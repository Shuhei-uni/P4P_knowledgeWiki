#!/usr/bin/env python3
"""Rebuild a reference Fluent setup onto another mesh with matching named selections.

This script is intended for the geothermal separator workflow in this repo:

1. Connect to an already-running Fluent gRPC session.
2. Load a reference case/data pair that already contains the desired setup.
3. Snapshot the reproducible setup state from that reference session.
4. Load a target mesh that exposes the same logical named selections.
5. Reapply the setup and save a case-only output.

Initialization, iteration, and autosave are started from Fluent after this
script returns; Python does not own the long solve.

It assumes the target mesh uses the same logical boundary roles as setup `07`:
`liquid inlet`, `steam inlet`, `wall`, `bottom`, and `outlet` / `steamoutlet`.
The actual zone names can differ; the script resolves common aliases and remaps
the reference setup onto the target names.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_chdir, safe_get_state, try_action, write_json_snapshot  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import (  # noqa: E402
    deep_replace_names,
    detect_cell_zone_name,
    detect_role_name,
    names_from_boundary_state,
    pick_first_named_object,
    print_header,
    require_remote_input,
    summarize_boundary_state,
)


ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "liquid_inlet": (
        "inlet_liquid_outer",
        "liquidinlet",
        "liquid_inlet",
        "liquid inlet",
        "liquid",
    ),
    "steam_inlet": (
        "inlet_steam_inner",
        "steaminlet",
        "steam_inlet",
        "steam inlet",
        "steam",
    ),
    "outlet": (
        "steamoutlet",
        "steam_outlet",
        "steam outlet",
        "outlet",
    ),
    "wall": (
        "wall-fluid",
        "wallfluid",
        "wall",
    ),
    "bottom": (
        "bottom",
    ),
}

BOUNDARY_TYPE_ORDER = (
    "velocity_inlet",
    "mass_flow_inlet",
    "pressure_outlet",
    "wall",
    "interior",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Clone a reference Fluent setup from case/data onto a new mesh and "
            "save a case-only artifact."
        )
    )
    parser.add_argument("--source-case", required=True, help="Remote reference case file.")
    parser.add_argument(
        "--source-data",
        default="",
        help=(
            "Remote reference data file. If omitted, Fluent will try the default "
            "paired .dat.h5 name next to --source-case."
        ),
    )
    parser.add_argument("--target-mesh", required=True, help="Remote target mesh file.")
    parser.add_argument("--output-case", required=True, help="Remote output case-only file.")
    parser.add_argument(
        "--snapshot-json",
        default="",
        help="Optional local JSON file for the captured reference snapshot.",
    )
    return parser


def safe_scheme_eval(solver, expression: str, default: Any = None) -> Any:
    try:
        return solver.scheme.eval(expression)
    except Exception:
        return default


def read_reference_case_data(solver, case_file: str, data_file: str) -> None:
    print_header("Load Reference Case/Data")
    require_remote_input(solver, case_file, "source case")
    if data_file:
        require_remote_input(solver, data_file, "source data")
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    try_action("read_reference_case", lambda: solver.settings.file.read_case(file_name=case_file), critical=True)
    if data_file:
        try_action("read_reference_data", lambda: solver.settings.file.read_data(file_name=data_file), critical=True)
    else:
        try_action(
            "read_reference_case_data_default_pair",
            lambda: solver.settings.file.read_case_data(file_name=case_file),
            critical=True,
        )


def capture_reference_snapshot(solver) -> dict[str, Any]:
    print_header("Capture Reference Snapshot")
    setup = solver.settings.setup
    solution = solver.settings.solution

    snapshot = {
        "general": {
            "solver": safe_get_state(setup.general.solver, "setup.general.solver"),
            "operating_conditions": safe_get_state(
                setup.general.operating_conditions,
                "setup.general.operating_conditions",
            ),
            "reference_values": safe_get_state(
                setup.general.reference_values,
                "setup.general.reference_values",
            ),
        },
        "models": safe_get_state(setup.models, "setup.models"),
        "phases": safe_get_state(setup.models.multiphase.phases, "setup.models.multiphase.phases"),
        "materials": safe_get_state(setup.materials, "setup.materials"),
        "boundary_conditions": safe_get_state(setup.boundary_conditions, "setup.boundary_conditions"),
        "cell_zone_conditions": safe_get_state(setup.cell_zone_conditions, "setup.cell_zone_conditions"),
        "solution": {
            "methods": safe_get_state(solution.methods, "solution.methods"),
            "controls": safe_get_state(solution.controls, "solution.controls"),
            "monitor": safe_get_state(solution.monitor, "solution.monitor"),
            "report_definitions": safe_get_state(
                solution.report_definitions,
                "solution.report_definitions",
            ),
            "initialization": safe_get_state(solution.initialization, "solution.initialization"),
        },
        "runtime": {
            "fluent_version": safe_scheme_eval(solver, "(cx-version)", default="unknown"),
            "iteration_count": safe_scheme_eval(solver, "(rpgetvar 'number-of-iterations)", default=None),
        },
    }

    boundary_state = snapshot["boundary_conditions"]
    if isinstance(boundary_state, Mapping):
        summarize_boundary_state(boundary_state)
    return snapshot


def build_name_replacements(
    source_snapshot: Mapping[str, Any],
    target_boundary_state: Mapping[str, Any],
    target_cell_zone_state: Mapping[str, Any],
) -> dict[str, str]:
    replacements: dict[str, str] = {}
    source_boundary_state = source_snapshot["boundary_conditions"]
    source_cell_zone_state = source_snapshot["cell_zone_conditions"]

    for role in ROLE_ALIASES:
        source_match = detect_role_name(source_boundary_state, role) if isinstance(source_boundary_state, Mapping) else None
        target_match = detect_role_name(target_boundary_state, role)
        if source_match and target_match:
            replacements[source_match[1]] = target_match[1]
            print(f"role_map[{role}]: {source_match[1]} -> {target_match[1]}")

    source_fluid = detect_cell_zone_name(source_cell_zone_state, ("fluid",))
    target_fluid = detect_cell_zone_name(target_cell_zone_state, ("fluid",))
    if not source_fluid and isinstance(source_cell_zone_state, Mapping):
        source_fluid = pick_first_named_object(source_cell_zone_state)
    if not target_fluid:
        target_fluid = pick_first_named_object(target_cell_zone_state)
    if source_fluid and target_fluid and source_fluid[1] != target_fluid[1]:
        replacements[source_fluid[1]] = target_fluid[1]
        print(f"cell_zone_map: {source_fluid[1]} -> {target_fluid[1]}")

    return replacements


def apply_general_settings(solver, general_state: Mapping[str, Any]) -> None:
    print_header("Apply General Settings")
    general = solver.settings.setup.general

    solver_state = general_state.get("solver")
    if isinstance(solver_state, Mapping):
        try_action("apply_general_solver_state", lambda: general.solver.set_state(solver_state))

    operating_conditions = general_state.get("operating_conditions")
    if isinstance(operating_conditions, Mapping):
        try_action(
            "apply_operating_conditions",
            lambda: general.operating_conditions.set_state(operating_conditions),
        )

    reference_values = general_state.get("reference_values")
    if isinstance(reference_values, Mapping):
        try_action(
            "apply_reference_values",
            lambda: general.reference_values.set_state(reference_values),
        )


def apply_models(solver, models_state: Mapping[str, Any]) -> None:
    print_header("Apply Models")
    models = solver.settings.setup.models

    multiphase_state = models_state.get("multiphase", {})
    multiphase_model = None
    if isinstance(multiphase_state, Mapping):
        multiphase_model = multiphase_state.get("model") or multiphase_state.get("models")
    if multiphase_model:
        try_action(
            "set_multiphase_model",
            lambda: setattr(models.multiphase, "model", multiphase_model),
            critical=True,
        )

    energy_state = models_state.get("energy", {})
    if isinstance(energy_state, Mapping) and "enabled" in energy_state:
        try_action("set_energy_enabled", lambda: setattr(models.energy, "enabled", energy_state["enabled"]))

    viscous_state = models_state.get("viscous", {})
    if isinstance(viscous_state, Mapping):
        if "model" in viscous_state:
            try_action("set_viscous_model", lambda: setattr(models.viscous, "model", viscous_state["model"]))
        if "k_epsilon_model" in viscous_state:
            try_action(
                "set_k_epsilon_variant",
                lambda: setattr(models.viscous, "k_epsilon_model", viscous_state["k_epsilon_model"]),
            )

    try_action("apply_full_models_state", lambda: models.set_state(models_state))


def apply_phase_assignments(solver, phases_state: Mapping[str, Any]) -> None:
    print_header("Apply Phase Assignments")
    if isinstance(phases_state, Mapping):
        try_action(
            "apply_multiphase_phases_state",
            lambda: solver.settings.setup.models.multiphase.phases.set_state(phases_state),
        )


def ensure_material_object(material_branch, material_name: str) -> None:
    try:
        existing = set(material_branch.get_object_names())
    except Exception:
        existing = set()
    if material_name not in existing:
        material_branch.create(name=material_name)


def apply_materials(solver, materials_state: Mapping[str, Any]) -> None:
    print_header("Apply Materials")
    materials = solver.settings.setup.materials

    for category in ("fluid", "solid", "inert_particle"):
        category_state = materials_state.get(category, {})
        if not isinstance(category_state, Mapping):
            continue
        category_obj = getattr(materials, category, None)
        if category_obj is None:
            continue
        for material_name, material_state in category_state.items():
            if not isinstance(material_state, Mapping):
                continue
            try_action(
                f"material_prepare_{category}.{material_name}",
                lambda name=material_name, obj=category_obj: ensure_material_object(obj, name),
            )
            try_action(
                f"material_apply_{category}.{material_name}",
                lambda name=material_name, state=material_state, obj=category_obj: obj[name].set_state(state),
            )


def convert_target_boundaries(
    solver,
    source_boundary_state: Mapping[str, Any],
    target_boundary_state: Mapping[str, Any],
) -> None:
    print_header("Convert Target Boundary Types")
    bc = solver.settings.setup.boundary_conditions

    for role in ("liquid_inlet", "steam_inlet", "outlet", "wall", "bottom"):
        source_match = detect_role_name(source_boundary_state, role)
        target_match = detect_role_name(target_boundary_state, role)
        if not source_match or not target_match:
            continue
        desired_type, target_name = source_match[0], target_match[1]
        current_type = target_match[0]
        if current_type == desired_type:
            print(f"{target_name}: already {current_type}")
            continue
        try_action(
            f"set_zone_type_{target_name}",
            lambda name=target_name, boundary_type=desired_type: bc.set_zone_type(
                zone_list=[name],
                new_type=boundary_type.replace("_", "-"),
            ),
        )


def apply_boundary_states(solver, boundary_state: Mapping[str, Any]) -> None:
    print_header("Apply Boundary States")
    bc = solver.settings.setup.boundary_conditions
    current_boundary_state = safe_get_state(bc, "boundary_conditions_current")

    for boundary_type in BOUNDARY_TYPE_ORDER:
        zone_map = boundary_state.get(boundary_type, {})
        if not isinstance(zone_map, Mapping):
            continue
        available_names = set(names_from_boundary_state(current_boundary_state, boundary_type))
        branch = getattr(bc, boundary_type, None)
        if branch is None:
            continue
        for zone_name, zone_state in zone_map.items():
            if zone_name == "settings" or not isinstance(zone_state, Mapping):
                continue
            if zone_name not in available_names:
                continue
            payload = deepcopy(zone_state)
            payload["name"] = zone_name
            try_action(
                f"apply_{boundary_type}_{zone_name}",
                lambda name=zone_name, state=payload, obj=branch: obj[name].set_state(state),
            )


def apply_cell_zone_conditions(solver, cell_zone_state: Mapping[str, Any]) -> None:
    print_header("Apply Cell Zone Conditions")
    try_action(
        "apply_cell_zone_conditions",
        lambda: solver.settings.setup.cell_zone_conditions.set_state(cell_zone_state),
    )


def apply_solution_state(solver, solution_state: Mapping[str, Any]) -> None:
    print_header("Apply Solution State")
    solution = solver.settings.solution
    for branch_name in ("methods", "controls", "monitor", "report_definitions"):
        branch_state = solution_state.get(branch_name)
        if not isinstance(branch_state, Mapping):
            continue
        branch = getattr(solution, branch_name, None)
        if branch is None:
            continue
        try_action(f"apply_solution_{branch_name}", lambda obj=branch, state=branch_state: obj.set_state(state))


def read_target_mesh(solver, mesh_file: str) -> None:
    print_header("Load Target Mesh")
    require_remote_input(solver, mesh_file, "target mesh")
    remote_chdir(solver, str(PureWindowsPath(mesh_file).parent))
    try_action("read_target_mesh", lambda: solver.settings.file.read_mesh(file_name=mesh_file), critical=True)


def write_case_only(solver, case_file: str, label: str) -> None:
    print_header(label)
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    try_action(f"write_case_{label}", lambda: solver.settings.file.write_case(file_name=case_file), critical=True)


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    solver = connect()
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")

    read_reference_case_data(solver, args.source_case, args.source_data)
    reference_snapshot = capture_reference_snapshot(solver)
    write_json_snapshot(args.snapshot_json, reference_snapshot)

    read_target_mesh(solver, args.target_mesh)

    target_boundary_state = safe_get_state(
        solver.settings.setup.boundary_conditions,
        "target_boundary_conditions",
    )
    target_cell_zone_state = safe_get_state(
        solver.settings.setup.cell_zone_conditions,
        "target_cell_zone_conditions",
    )
    if isinstance(target_boundary_state, Mapping):
        print_header("Target Boundary Summary")
        summarize_boundary_state(target_boundary_state)

    replacements = build_name_replacements(
        reference_snapshot,
        target_boundary_state if isinstance(target_boundary_state, Mapping) else {},
        target_cell_zone_state if isinstance(target_cell_zone_state, Mapping) else {},
    )
    remapped_snapshot = deep_replace_names(reference_snapshot, replacements)

    apply_general_settings(solver, remapped_snapshot["general"])
    apply_models(solver, remapped_snapshot["models"])
    apply_materials(solver, remapped_snapshot["materials"])
    apply_phase_assignments(solver, remapped_snapshot["phases"])
    apply_cell_zone_conditions(solver, remapped_snapshot["cell_zone_conditions"])

    current_target_boundary_state = safe_get_state(
        solver.settings.setup.boundary_conditions,
        "current_target_boundary_conditions",
    )
    convert_target_boundaries(
        solver,
        remapped_snapshot["boundary_conditions"],
        current_target_boundary_state if isinstance(current_target_boundary_state, Mapping) else {},
    )
    apply_boundary_states(solver, remapped_snapshot["boundary_conditions"])
    apply_solution_state(solver, remapped_snapshot["solution"])

    write_case_only(solver, args.output_case, "write_rebuilt_case_only")

    print("\nCase-only rebuild finished. Start initialization and the long run from Fluent with native autosave.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Inspect and build the setup-02d VOF-IC0 case from the supplied Fluent mesh.

This is intentionally a case-only builder: it never initializes, patches,
iterates, writes data, or configures a production timestep.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import probe_object  # noqa: E402
from pyansys_fluent.setup_io import load_target_mesh  # noqa: E402


DEFAULT_MESH = "brine-outlet-620kcells.msh.h5"
DEFAULT_OUTPUT = "VOF-IC0-P1120-preinit-20260814T000000Z.cas.h5"
DEFAULT_SNAPSHOT = PROJECT_ROOT / "output" / "02d_vof_ic0_mesh_inspection.json"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server-id", default="2")
    p.add_argument("--mesh", default=DEFAULT_MESH, help="Absolute or current-working-directory mesh path on the Fluent host.")
    p.add_argument("--snapshot-json", default=str(DEFAULT_SNAPSHOT))
    p.add_argument("--inspect-only", action="store_true", help="Load the requested mesh and capture only live state/probes.")
    p.add_argument("--probe-vof", action="store_true", help="Load mesh, apply only prerequisite models/materials/phase mapping, then capture live VOF branches. No case is saved.")
    p.add_argument("--apply", action="store_true", help="Build and reload-verify the no-patch case-only artifact.")
    p.add_argument("--verify-case", action="store_true", help="Reload and audit an already-written case-only artifact without changing its setup.")
    p.add_argument("--output-case", default=DEFAULT_OUTPUT, help="Reserved output path for the later validated case-only build.")
    return p


def _state(solver: Any, path: str, obj: Any) -> dict[str, Any]:
    return {"state": safe_get_state(obj, path), "probe": probe_object(obj).__dict__}


def capture(solver: Any, mesh: str) -> dict[str, Any]:
    setup = solver.settings.setup
    solution = solver.settings.solution
    return {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "fluent_version": solver.get_fluent_version(),
        "source_mesh": mesh,
        "file": _state(solver, "file", solver.settings.file),
        "general": _state(solver, "setup.general", setup.general),
        "models": _state(solver, "setup.models", setup.models),
        "multiphase": _state(solver, "setup.models.multiphase", setup.models.multiphase),
        "materials": _state(solver, "setup.materials", setup.materials),
        "boundary_conditions": _state(solver, "setup.boundary_conditions", setup.boundary_conditions),
        "cell_zone_conditions": _state(solver, "setup.cell_zone_conditions", setup.cell_zone_conditions),
        "solution_methods": _state(solver, "solution.methods", solution.methods),
        "solution_controls": _state(solver, "solution.controls", solution.controls),
        "run_calculation": _state(solver, "solution.run_calculation", solution.run_calculation),
        "initialization": _state(solver, "solution.initialization", solution.initialization),
    }


def prepare_vof_prerequisites(solver: Any) -> None:
    """Apply only dependency prerequisites and stop to expose version-specific VOF paths."""
    setup = solver.settings.setup
    general = setup.general
    general.solver.type = "pressure-based"
    # Fluent 2025 R2 represents the requested transient formulation by the
    # compatible first-order unsteady option. Explicit VOF cannot use the
    # second-order implicit temporal formulation.
    general.solver.time = "unsteady-1st-order"
    general.operating_conditions.gravity.enable = True
    general.operating_conditions.gravity.components = [0.0, -9.81, 0.0]
    general.operating_conditions.operating_pressure = 0.0

    models = setup.models
    models.energy.enabled = False
    models.discrete_phase.general_settings.interaction.enabled = False
    models.viscous.model = "k-epsilon"
    models.viscous.k_epsilon_model = "rng"

    fluid = setup.materials.fluid
    for name, density, viscosity in (
        ("water-vapor", 5.73, 15.188e-6),
        ("water-liquid", 881.77, 145.96e-6),
    ):
        if name not in set(fluid.get_object_names()):
            fluid.create(name=name)
        fluid[name].set_state(
            {
                "name": name,
                "chemical_formula": "",
                "density": {"option": "constant", "value": density},
                "viscosity": {"option": "constant", "value": viscosity},
            }
        )

    multiphase = setup.models.multiphase
    multiphase.model = "vof"

    # Model activation creates a fresh phase tree. Do not force phase count when
    # Fluent has already created the standard primary/secondary slots.
    state = safe_get_state(setup.models.multiphase, "multiphase_after_vof")
    phase_count = state.get("number_of_phases") if isinstance(state, dict) else None
    if isinstance(phase_count, dict) and phase_count.get("number_of_eulerian_phases") not in (None, 2):
        setup.models.multiphase.number_of_phases.number_of_eulerian_phases = 2

    # This project/release has a known working phase-material TUI sequence.
    for command in (
        "/define/phases/set-domain-properties/phase-domains/phase-1/material yes water-vapor",
        "/define/phases/set-domain-properties/phase-domains/phase-2/material yes water-liquid",
    ):
        solver.scheme.exec((f'(ti-menu-load-string "{command}")',))


def _set_nested_volume_fraction(state: dict[str, Any], *, inlet: str, liquid_fraction: float) -> dict[str, Any]:
    state["name"] = inlet
    mixture = state["phase"]["mixture"]
    mixture["momentum"]["velocity_magnitude"] = {"option": "value", "value": 27.118}
    mixture["momentum"]["initial_gauge_pressure"] = {"option": "value", "value": 1_140_000.0}
    state["phase"]["phase-2"]["multiphase"]["volume_fraction"] = {
        "option": "value",
        "value": liquid_fraction,
    }
    return state


def configure_boundaries_and_methods(solver: Any) -> None:
    bc = solver.settings.setup.boundary_conditions
    for inlet, fraction in (("liquid-inlet", 1.0), ("steam-inlet", 0.0)):
        obj = bc.velocity_inlet[inlet]
        state = safe_get_state(obj, f"velocity_inlet.{inlet}")
        if not isinstance(state, dict) or "phase" not in state:
            raise RuntimeError(f"VOF phase state unavailable at velocity inlet {inlet}: {state}")
        obj.set_state(_set_nested_volume_fraction(state, inlet=inlet, liquid_fraction=fraction))

    for outlet, liquid_backflow in (("brine-outlet", 1.0), ("steam-outlet", 0.0)):
        obj = bc.pressure_outlet[outlet]
        state = safe_get_state(obj, f"pressure_outlet.{outlet}")
        if not isinstance(state, dict) or "phase" not in state:
            raise RuntimeError(f"VOF phase state unavailable at pressure outlet {outlet}: {state}")
        state["name"] = outlet
        state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": 1_120_000.0}
        state["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"] = {
            "option": "value",
            "value": liquid_backflow,
        }
        obj.set_state(state)

    methods = solver.settings.solution.methods
    methods.spatial_discretization.discretization_scheme["pressure"] = "presto!"
    methods.spatial_discretization.discretization_scheme["mp"] = "geo-reconstruct"


def assert_case_contract(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    general = safe_get_state(setup.general, "general")
    models = safe_get_state(setup.models, "models")
    bcs = safe_get_state(setup.boundary_conditions, "boundary_conditions")
    methods = safe_get_state(solver.settings.solution.methods, "solution.methods")

    def value(obj: Any, *keys: str) -> Any:
        for key in keys:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(key)
        return obj

    required = {
        "pressure_based": value(general, "solver", "type") == "pressure-based",
        "unsteady_first_order": value(general, "solver", "time") == "unsteady-1st-order",
        "gravity": value(general, "operating_conditions", "gravity", "enable") is True,
        "operating_pressure_zero": value(general, "operating_conditions", "operating_pressure") == 0.0,
        "vof": value(models, "multiphase", "model") == "vof",
        "explicit": value(models, "multiphase", "vof_parameters", "vof_formulation") == "explicit",
        "sharp": value(models, "multiphase", "vof_parameters", "interface_modeling_options", "interface_type") == "sharp",
        "rng_ke": value(models, "viscous", "model") == "k-epsilon" and value(models, "viscous", "k_epsilon_model") == "rng",
        "geo_reconstruct": value(methods, "spatial_discretization", "discretization_scheme", "mp") == "geo-reconstruct",
        "presto": value(methods, "spatial_discretization", "discretization_scheme", "pressure") == "presto!",
    }
    for inlet, expected_fraction in (("liquid-inlet", 1.0), ("steam-inlet", 0.0)):
        base = value(bcs, "velocity_inlet", inlet, "phase")
        required[f"{inlet}_velocity"] = value(base, "mixture", "momentum", "velocity_magnitude", "value") == 27.118
        required[f"{inlet}_pressure"] = value(base, "mixture", "momentum", "initial_gauge_pressure", "value") == 1_140_000.0
        required[f"{inlet}_liquid_fraction"] = value(base, "phase-2", "multiphase", "volume_fraction", "value") == expected_fraction
    for outlet, expected_fraction in (("brine-outlet", 1.0), ("steam-outlet", 0.0)):
        base = value(bcs, "pressure_outlet", outlet, "phase")
        required[f"{outlet}_pressure"] = value(base, "mixture", "momentum", "gauge_pressure", "value") == 1_120_000.0
        required[f"{outlet}_liquid_backflow"] = value(base, "phase-2", "multiphase", "backflow_volume_fraction", "value") == expected_fraction
    failures = [name for name, ok in required.items() if not ok]
    if failures:
        raise RuntimeError(f"VOF-IC0 contract readback failed: {failures}")
    return {"checks": required, "general": general, "models": models, "boundaries": bcs, "methods": methods}


def main() -> int:
    args = parser().parse_args()
    solver = connect(server_id=args.server_id)
    if not remote_file_exists(solver, args.mesh):
        raise FileNotFoundError(f"Fluent cannot see the requested mesh: {args.mesh}")
    if sum(bool(mode) for mode in (args.inspect_only, args.probe_vof, args.apply, args.verify_case)) != 1:
        raise RuntimeError("Choose exactly one mode: --inspect-only, --probe-vof, --apply, or --verify-case.")
    if args.verify_case:
        if not remote_file_exists(solver, args.output_case):
            raise FileNotFoundError(f"Fluent cannot see the requested case-only artifact: {args.output_case}")
        solver.settings.file.read_case(file_name=args.output_case)
        contract = assert_case_contract(solver)
    else:
        load_target_mesh(solver, args.mesh)
        contract = None
    if args.probe_vof or args.apply:
        prepare_vof_prerequisites(solver)
    if args.apply:
        configure_boundaries_and_methods(solver)
        contract = assert_case_contract(solver)
        if remote_file_exists(solver, args.output_case):
            raise FileExistsError(f"Refusing to overwrite existing case-only artifact: {args.output_case}")
        solver.settings.file.write_case(file_name=args.output_case)
        if not remote_file_exists(solver, args.output_case):
            raise RuntimeError(f"Fluent did not expose the written case: {args.output_case}")
        solver.settings.file.read_case(file_name=args.output_case)
        contract = assert_case_contract(solver)
    payload = capture(solver, args.mesh)
    payload["case_only_contract"] = contract
    payload["output_case"] = args.output_case if args.apply else None
    payload["initialized"] = False
    payload["patched"] = False
    payload["iterated"] = False
    payload["data_written"] = False
    out = Path(args.snapshot_json).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"snapshot_json: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

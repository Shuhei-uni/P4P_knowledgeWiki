#!/usr/bin/env python3
"""
Set up a VOF + Eulerian Wall Film sensitivity case from an existing Fluent case/data.

This script is designed for Shuhei's remote Fluent layout:

Remote Windows project:
    C:\\Users\\syok443\\Documents\\Fluent Standalone Test 1

It:
- connects to an already-running Fluent gRPC session,
- verifies remote case/data paths,
- reads the existing case and explicit data file,
- inspects available boundary zones,
- enables VOF assumptions where PyFluent allows,
- enables Eulerian Wall Film where PyFluent/TUI allows,
- marks selected wall zones as Eulerian film walls,
- writes a new case file,
- does NOT run iterations.

Use:
    python scripts/setup_vof_ewf_from_existing_case.py --dry-run
    python scripts/setup_vof_ewf_from_existing_case.py --apply --film-walls wall wall-fluid --force
    python scripts/setup_vof_ewf_from_existing_case.py --apply --all-walls

Recommended first workflow:
    1. check_connection.py
    2. probe_remote_paths.py
    3. setup_vof_ewf_from_existing_case.py --dry-run
    4. inspect_case.py
    5. setup_vof_ewf_from_existing_case.py --apply --film-walls
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

# Allow importing check_connection.py from the same scripts folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Inspect only. Do not modify case.")
    mode.add_argument("--apply", action="store_true", help="Apply VOF + EWF setup and save new case.")

    parser.add_argument(
        "--film-walls",
        nargs="+",
        default=[],
        help="Specific wall boundary names to convert to Eulerian film walls.",
    )
    parser.add_argument(
        "--all-walls",
        action="store_true",
        help="Convert all wall zones to Eulerian film walls. Use only if that is intended.",
    )

    parser.add_argument(
        "--primary-phase",
        default="water-vapor",
        help="Primary phase assumption. Default: water-vapor.",
    )
    parser.add_argument(
        "--secondary-phase",
        default="water-liquid",
        help="Secondary phase assumption. Default: water-liquid.",
    )
    parser.add_argument(
        "--film-material",
        default="water-liquid",
        help="Wall-film material. Default: water-liquid.",
    )
    parser.add_argument(
        "--initial-film-height",
        default="0 [m]",
        help="Initial film height on film walls. Default: 0 [m].",
    )
    parser.add_argument(
        "--film-temperature",
        default="457 [K]",
        help="Assumed film temperature. Default around saturated water at ~11.2 bara.",
    )

    parser.add_argument(
        "--snapshot-json",
        default="",
        help="Optional local JSON path for dumped setup state.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Auto-answer prompts and overwrite conflicting settings where possible.",
    )

    return parser


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required .env value: {name}")
    return value


def quote_scheme_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', "\\\"")


def remote_file_exists(solver, path_text: str) -> bool:
    quoted = quote_scheme_string(path_text)
    return bool(solver.scheme.eval(f'(file-exists? "{quoted}")'))


def remote_chdir(solver, path_text: str) -> None:
    quoted = quote_scheme_string(path_text)
    solver.scheme.eval(f'(chdir "{quoted}")')


def safe_get_state(obj: Any, label: str) -> dict[str, Any]:
    try:
        state = obj.get_state()
        if isinstance(state, Mapping):
            return dict(state)
        return {"value": str(state)}
    except Exception as exc:
        return {"error": f"{label} unavailable: {exc}"}


def names_from_boundary_state(boundary_state: Mapping[str, Any], boundary_type: str) -> list[str]:
    section = boundary_state.get(boundary_type, {})
    if not isinstance(section, Mapping):
        return []
    return sorted(name for name in section.keys() if name != "settings")


def compact_print_list(title: str, values: list[str]) -> None:
    print(f"\n--- {title} ---")
    if not values:
        print("(none found)")
        return
    for value in values:
        print(f"- {value}")


def load_case_and_data(solver) -> None:
    case_file = env_required("FLUENT_REMOTE_CASE_FILE")
    data_file = env_required("FLUENT_REMOTE_DATA_FILE")

    print("\nChecking remote case/data paths...")
    if not remote_file_exists(solver, case_file):
        raise FileNotFoundError(f"Fluent cannot see case file: {case_file}")
    if not remote_file_exists(solver, data_file):
        raise FileNotFoundError(f"Fluent cannot see data file: {data_file}")

    case_dir = str(PureWindowsPath(case_file).parent)
    print(f"Changing Fluent working directory to: {case_dir}")
    remote_chdir(solver, case_dir)

    print("\nReading case file explicitly...")
    solver.settings.file.read_case(file_name=case_file)

    print("Reading data file explicitly...")
    solver.settings.file.read_data(file_name=data_file)

    print("Case/data loaded. No iterations were run.")


def inspect_current_setup(solver) -> dict[str, Any]:
    print("\nInspecting current setup...")

    setup = solver.settings.setup
    solution = solver.settings.solution

    boundary_state = safe_get_state(setup.boundary_conditions, "boundary_conditions")
    models_state = safe_get_state(setup.models, "models")
    materials_state = safe_get_state(setup.materials, "materials")
    cell_zone_state = safe_get_state(setup.cell_zone_conditions, "cell_zone_conditions")
    solution_state = safe_get_state(solution, "solution")

    velocity_inlets = names_from_boundary_state(boundary_state, "velocity_inlet")
    mass_flow_inlets = names_from_boundary_state(boundary_state, "mass_flow_inlet")
    pressure_outlets = names_from_boundary_state(boundary_state, "pressure_outlet")
    walls = names_from_boundary_state(boundary_state, "wall")

    compact_print_list("velocity inlets", velocity_inlets)
    compact_print_list("mass-flow inlets", mass_flow_inlets)
    compact_print_list("pressure outlets", pressure_outlets)
    compact_print_list("wall zones", walls)

    print("\n--- Current model summary ---")
    for key in ["multiphase", "viscous", "energy", "discrete_phase"]:
        print(f"{key}: {models_state.get(key, '(not found)')}")

    print("\n--- Material categories ---")
    for key, value in materials_state.items():
        if isinstance(value, Mapping):
            print(f"{key}: {', '.join(str(k) for k in value.keys())}")

    return {
        "boundary_conditions": boundary_state,
        "models": models_state,
        "materials": materials_state,
        "cell_zone_conditions": cell_zone_state,
        "solution": solution_state,
        "derived": {
            "velocity_inlets": velocity_inlets,
            "mass_flow_inlets": mass_flow_inlets,
            "pressure_outlets": pressure_outlets,
            "walls": walls,
        },
    }


def dump_snapshot(snapshot: Mapping[str, Any], snapshot_json: str) -> None:
    if not snapshot_json:
        return

    path = Path(snapshot_json).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    def fallback(obj):
        return str(obj)

    path.write_text(json.dumps(snapshot, indent=2, default=fallback), encoding="utf-8")
    print(f"\nWrote local setup snapshot to: {path}")


def try_action(label: str, func) -> bool:
    print(f"\n{label}")
    try:
        func()
        print("[OK]")
        return True
    except Exception as exc:
        print(f"[WARN] skipped/failed: {exc}")
        return False


def enable_gravity(solver) -> None:
    def via_settings():
        op = solver.settings.setup.general.operating_conditions
        op.gravity.enable = True
        op.gravity.components = [0.0, 0.0, -9.81]

    if not try_action("Enable gravity through settings API", via_settings):
        try_action(
            "Enable gravity through Scheme fallback",
            lambda: solver.scheme.eval("(rpsetvar 'gravity? #t)"),
        )


def enable_vof(solver, args: argparse.Namespace) -> None:
    """
    Attempts VOF setup using PyFluent settings/classes.

    Exact phase material assignment is version/case dependent, so this script
    reports warnings rather than hiding failures.
    """

    def via_solver_classes():
        from ansys.fluent.core.solver import Models

        models = Models(solver)
        models.multiphase.model = "vof"
        models.multiphase.vof_parameters.vof_formulation = "implicit"
        models.multiphase.vof_parameters.vof_cutoff = 1.0e-6
        models.multiphase.advanced_formulation.implicit_body_force = True

    try_action("Enable VOF through PyFluent Models API", via_solver_classes)

    # Phase renaming commands are version-sensitive.
    # If this fails, set phase names/materials manually in GUI and re-inspect.
    def rename_phases_tui():
        solver.tui.define.phases.set_domain_properties.change_phases_names(
            args.primary_phase,
            args.secondary_phase,
        )

    try_action(
        f"Try rename phases to {args.primary_phase}, {args.secondary_phase}",
        rename_phases_tui,
    )


def enable_ewf(solver, args: argparse.Namespace) -> None:
    """
    Enables Eulerian Wall Film as far as the current Fluent/PyFluent version allows.

    Some EWF options are interactive TUI prompts in Fluent. Those may need to be
    completed through the GUI once and then converted into a journal if this
    function warns.
    """

    ewf = solver.tui.define.models.eulerian_wallfilm

    try_action(
        "Enable Eulerian Wall Film model",
        lambda: ewf.enable_wallfilm_model("yes"),
    )

    try_action(
        "Enable/solve wall-film equation",
        lambda: ewf.solve_wallfilm_equation("yes"),
    )

    try_action(
        "Enable film/VOF transition messages",
        lambda: ewf.enable_film_vof_transition_message("yes"),
    )

    if args.force:
        if not try_action(
            f"Force set film material to {args.film_material}",
            lambda: ewf.film_material("yes", args.film_material),
        ):
            try_action(
                f"Set film material to {args.film_material}",
                lambda: ewf.film_material(args.film_material),
            )
    else:
        try_action(
            f"Set film material to {args.film_material}",
            lambda: ewf.film_material(args.film_material),
        )


def mark_film_walls(solver, wall_names: list[str], args: argparse.Namespace) -> None:
    print("\nMarking selected wall zones as Eulerian film walls...")

    for wall_name in wall_names:
        print(f"\nWall zone: {wall_name}")

        def via_wall_boundary_class():
            from ansys.fluent.core.solver import WallBoundary

            wall = WallBoundary(solver, name=wall_name)
            if args.force:
                try:
                    wall.wall_film.enabled = True
                except Exception:
                    pass
                try:
                    wall.wall_film.activate()
                except Exception:
                    pass
            wall.wall_film.eulerian_film_wall = True

            # 0 = boundary condition, 1 = initial condition.
            # For a dry-start film, initial condition is usually safest.
            wall.wall_film.film_condition_type = 1
            wall.wall_film.film_height = args.initial_film_height

            try:
                wall.wall_film.film_temperature = args.film_temperature
            except Exception:
                pass

            try:
                wall.wall_film.include_film_momentum_pressure = True
            except Exception:
                pass

        ok = try_action("Apply wall-film settings through WallBoundary API", via_wall_boundary_class)

        if not ok:
            print(
                "Manual fallback required in Fluent GUI: "
                "Boundary Conditions > selected wall > Wall Film > Eulerian Film Wall."
            )


def write_new_case(solver) -> None:
    output_case = env_required("FLUENT_REMOTE_OUTPUT_CASE")
    output_dir = str(PureWindowsPath(output_case).parent)

    print(f"\nWriting new setup case to: {output_case}")
    remote_chdir(solver, output_dir)
    solver.settings.file.write_case(file_name=output_case)
    print("Saved setup case. Original case/data were not overwritten.")


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    solver = connect()
    print(f"\nConnected to Fluent version: {solver.get_fluent_version()}")

    load_case_and_data(solver)
    snapshot = inspect_current_setup(solver)
    dump_snapshot(snapshot, args.snapshot_json)

    available_walls = snapshot["derived"]["walls"]

    if args.dry_run:
        print("\nDry run complete. No setup changes were applied.")
        print("Next: choose film wall names from the printed wall-zone list.")
        return 0

    if args.all_walls:
        film_walls = available_walls
        if not film_walls:
            raise RuntimeError("No wall zones found; cannot apply --all-walls.")
    else:
        film_walls = args.film_walls
        if not film_walls:
            raise RuntimeError(
                "No film walls supplied. Re-run with --film-walls "
                "or --all-walls after inspecting the wall-zone list."
            )

    missing = [name for name in film_walls if name not in available_walls]
    if missing:
        raise RuntimeError(
            "These requested film wall names were not found in the current case: "
            + ", ".join(missing)
        )

    enable_gravity(solver)
    enable_vof(solver, args)
    enable_ewf(solver, args)
    mark_film_walls(solver, film_walls, args)

    print("\nRe-inspecting after setup changes...")
    after_snapshot = inspect_current_setup(solver)
    dump_snapshot(
        after_snapshot,
        args.snapshot_json.replace(".json", "_after.json") if args.snapshot_json else "",
    )

    write_new_case(solver)

    print("\nFinished. No iterations were run.")
    print("Recommended next step: open the saved case in Fluent GUI and verify Models > Multiphase and Wall Film.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
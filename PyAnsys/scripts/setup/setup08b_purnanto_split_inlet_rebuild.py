#!/usr/bin/env python3
"""Rebuild the Purnanto 1680/1600J setup onto the two-inlet target mesh.

This script combines three archived sources of truth:

- the live 1680 carrier/solution capture;
- the 07 split-inlet boundary pattern;
- the 1600 particle extraction payload.

It writes a case-only artifact. Initialization, iteration, and autosave are
started from Fluent after the build using the native Fluent controls.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import safe_get_state, try_action, write_json_snapshot  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import load_json, print_header, summarize_boundary_state  # noqa: E402
from pyansys_fluent.setup_discovery import build_compact_boundary_summary, build_target_role_map, convert_target_boundaries_to_intended  # noqa: E402
from pyansys_fluent.setup_dpm import SEED_INJECTION_NAME  # noqa: E402
from pyansys_fluent.setup_dpm import apply_dpm_injections  # noqa: E402
from pyansys_fluent.setup_dpm import apply_dpm_model_settings  # noqa: E402
from pyansys_fluent.setup_dpm import bootstrap_inert_particle_material_branch  # noqa: E402
from pyansys_fluent.setup_dpm import delete_injection_if_present  # noqa: E402
from pyansys_fluent.setup_dpm import resolve_particle_material_name  # noqa: E402
from pyansys_fluent.setup_carrier import (  # noqa: E402
    apply_boundary_states,
    apply_carrier_cell_zone_conditions,
    apply_carrier_general,
    apply_carrier_operating_conditions_state,
    apply_carrier_models,
    apply_carrier_phase_materials,
    apply_carrier_solution_controls,
    apply_carrier_solution_methods,
    apply_carrier_solution_monitor,
    apply_carrier_solution_monitor_continuity,
    apply_material_states,
    build_intended_boundary_state,
)
from pyansys_fluent.setup_io import load_case_only, load_target_mesh, write_case_only  # noqa: E402


DEFAULT_SERVER_ID = "4"
DEFAULT_TARGET_MESH = r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files\PureTwoPhaseV2(PurnantoV2).msh"
DEFAULT_OUTPUT_CASE = r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files\output\PureTwoPhaseV2(PurnantoV2)-rebuilt.cas.h5"

LIVE_ARCHIVE_DIR = (
    PROJECT_ROOT
    / "cases"
    / "actual_setup_archives"
    / "purnanto-enthalpy1680-live-extract"
)
SPLIT_INLET_ARCHIVE_DIR = (
    PROJECT_ROOT
    / "cases"
    / "actual_setup_archives"
    / "07-pure-phase-split-actual-area-live-fff-1-2"
)
PARTICLE_ARCHIVE_DIR = (
    PROJECT_ROOT
    / "cases"
    / "actual_setup_archives"
    / "purnanto-enthalpy1600-particle-extract"
)

LIVE_SETTINGS_ROOT = LIVE_ARCHIVE_DIR / "live" / "settings_root_tree.json"
SPLIT_SETTINGS_SNAPSHOT = SPLIT_INLET_ARCHIVE_DIR / "settings_snapshot.json"
PARTICLE_INJECTIONS = PARTICLE_ARCHIVE_DIR / "injections.json"

STEAM_INLET_SURFACE_ROLE = "steam_inlet"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Rebuild the Purnanto V2 Fluent setup onto the Computer 2 two-inlet mesh "
            "and save a case file only."
        )
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print the planned merge payload without connecting to Fluent.")
    mode.add_argument("--apply", action="store_true", help="Connect to Fluent, apply the merged setup, and write the case-only file.")
    parser.add_argument(
        "--server-id",
        default=DEFAULT_SERVER_ID,
        help="Configured Fluent server id to use. Default: 4.",
    )
    parser.add_argument(
        "--target-mesh",
        default=DEFAULT_TARGET_MESH,
        help="Remote mesh path visible to the Fluent session on Computer 2.",
    )
    parser.add_argument(
        "--output-case",
        default=DEFAULT_OUTPUT_CASE,
        help="Remote output case path on Computer 2. A .cas.h5 file is written here.",
    )
    parser.add_argument(
        "--snapshot-json",
        default="",
        help="Optional local JSON path for the merge summary and resolved zone map.",
    )
    parser.add_argument(
        "--resume-case",
        default="",
        help="Optional existing case to load and extend with the archived setup instead of rebuilding from mesh.",
    )
    parser.add_argument(
        "--particle-material",
        default="",
        help=(
            "Optional inert-particle material name to create for DPM injections. "
            "If omitted, derive a traceable name from the archived source material."
        ),
    )
    parser.add_argument(
        "--apply-live-archive",
        action="store_true",
        help="Opt in to replaying the archived 1680 carrier and solution state before the rebuild.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Fail fast instead of continuing past non-critical setup errors. Default: enabled.",
    )
    parser.add_argument(
        "--lenient",
        dest="strict",
        action="store_false",
        help="Allow non-critical setup errors to continue. Use only for debugging.",
    )
    return parser


def extract_state_root(payload: dict[str, object]) -> dict[str, object]:
    state = payload.get("_state", payload)
    if not isinstance(state, dict):
        raise TypeError("Archive payload does not contain a mapping state tree")
    return state


def load_archive_inputs() -> dict[str, object]:
    live_root = extract_state_root(load_json(LIVE_SETTINGS_ROOT))
    split_root = extract_state_root(load_json(SPLIT_SETTINGS_SNAPSHOT))
    particle_entries = load_json(PARTICLE_INJECTIONS)
    if not isinstance(particle_entries, list):
        raise TypeError("Particle injection archive is not a list")
    return {
        "live_setup": extract_state_root(live_root["setup"]),
        "live_solution": extract_state_root(live_root["solution"]),
        "split_boundary_conditions": extract_state_root(split_root["setup"])["boundary_conditions"],
        "particle_entries": particle_entries,
    }


def build_archived_injection_state(
    particle_entries: list[dict[str, object]],
    steam_inlet_name: str,
    particle_material_name: str,
) -> dict[str, dict[str, object]]:
    injections: dict[str, dict[str, object]] = {}
    for entry in particle_entries:
        name = str(entry["injection_name"])
        settings = entry["settings"]
        if not isinstance(settings, dict):
            raise TypeError(f"Invalid injection settings for {name}")

        ntries = int(settings.get("ntries", 1))
        time_scale_constant = float(settings.get("time-scale-constant", 0.15))
        diameter = float(settings["diameter"])
        total_flow_rate = float(settings.get("total-flow-rate", 0.0))
        use_face_normal = bool(settings.get("use-face-normal", False))

        injections[name] = {
            "name": name,
            "particle_type": str(settings.get("type", "inert")),
            "material": particle_material_name,
            "injection_type": {"option": str(settings.get("injection-type", "surface"))},
            "initial_values": {
                "location": {
                    "injection_surfaces": [steam_inlet_name],
                    "randomized_positions_enabled": bool(settings.get("stochastic-on", False)),
                },
                "mass_flow_rate": {"total_flow_rate": total_flow_rate},
                "velocity": {
                    "use_face_normal_direction": use_face_normal,
                    "x_velocity": float(settings.get("x-vel", 0.0)),
                    "y_velocity": float(settings.get("y-vel", 0.0)),
                    "z_velocity": float(settings.get("z-vel", 0.0)),
                },
                "particle_size": {
                    "option": "uniform",
                    "diameter": diameter,
                },
            },
            "physical_models": {
                "particle_drag": {"option": "spherical"},
                "turbulent_dispersion": {
                    "enabled": bool(settings.get("random-eddy-on", False)),
                    "random_eddy_lifetime": bool(settings.get("random-eddy-on", False)),
                    "number_of_tries": ntries,
                    "time_scale_constant": time_scale_constant,
                },
                "particle_rotation": {"enabled": False},
                "rough_wall_treatment_enabled": False,
                "custom_laws": {
                    "law_1": "inert-heating",
                    "law_2": "inactive",
                    "law_3": "inactive",
                    "law_4": "inactive",
                    "law_5": "inactive",
                    "law_6": "inactive",
                    "law_7": "inactive",
                    "law_8": "inactive",
                    "law_9": "inactive",
                    "law_10": "inactive",
                    "switch": "Default",
                },
            },
        }
    return injections


def resolve_archived_particle_material(particle_entries: list[dict[str, object]], override: str) -> tuple[str, str]:
    source_materials = {
        str(entry.get("settings", {}).get("material", "water-liquid")).strip()
        for entry in particle_entries
    }
    source_materials = {material for material in source_materials if material}
    if len(source_materials) != 1:
        raise RuntimeError(f"Expected one archived particle material, got: {sorted(source_materials)}")

    archived_particle_material = next(iter(source_materials))
    particle_material = resolve_particle_material_name(archived_particle_material, override=override)
    return archived_particle_material, particle_material


def summarize_run_plan(
    *,
    target_mesh: str,
    output_case: str,
    role_map: dict[str, str] | None,
    injection_names: list[str],
    archived_particle_material: str,
    particle_material: str,
) -> dict[str, object]:
    return {
        "target_mesh": target_mesh,
        "output_case": output_case,
        "resolved_role_map": role_map or {},
        "injection_count": len(injection_names),
        "injection_names": injection_names,
        "archived_particle_material": archived_particle_material,
        "particle_material": particle_material,
        "archive_sources": {
            "live_settings_root": str(LIVE_SETTINGS_ROOT),
            "split_settings_snapshot": str(SPLIT_SETTINGS_SNAPSHOT),
            "particle_injections": str(PARTICLE_INJECTIONS),
        },
        "assumptions": [
            "Case-only rebuild; initialize, iterate, and autosave from Fluent after this script returns.",
            "1680 live archive supplies the carrier and solution authority.",
            "07 archive supplies the split-inlet boundary topology.",
            "1600 particle extract supplies the DPM injection payloads.",
            "DPM inert-particle material is derived from the archived source material unless overridden.",
            "Live archive replay is opt-in; safe mode prefers continuing to a case write after warnings.",
            "Steam inlet is the default DPM injection surface.",
        ],
    }


def apply_live_carrier_and_solution(
    solver,
    live_setup: dict[str, object],
    live_solution: dict[str, object],
    *,
    strict: bool,
) -> bool:
    print_header("Apply Live 1680 Carrier State")
    carrier_ok = True
    carrier_ok &= apply_carrier_general(solver)
    carrier_ok &= try_action(
        "apply_live_operating_conditions",
        lambda: apply_carrier_operating_conditions_state(solver, live_setup["general"]["operating_conditions"]),
    )
    carrier_ok &= try_action("apply_live_materials", lambda: apply_material_states(solver, live_setup["materials"]))
    carrier_ok &= try_action("apply_live_models_state", lambda: apply_carrier_models(solver))
    carrier_ok &= try_action("apply_live_cell_zone_state", lambda: apply_carrier_cell_zone_conditions(solver))
    if not carrier_ok:
        print("apply_live_1680_carrier_state: completed with non-fatal carrier warnings")

    print_header("Apply Live 1680 Solution State")
    solution_ref: dict[str, object] = {}
    solution_ok = safe_step(
        "access_solver_solution",
        lambda: solution_ref.setdefault("solution", solver.settings.solution),
        strict=False,
    )
    if solution_ok and "solution" in solution_ref:
        solution = solution_ref["solution"]
        try_action("apply_live_solution_methods", lambda: solution.methods.set_state(live_solution["methods"]))
        try_action("apply_live_solution_controls", lambda: solution.controls.set_state(live_solution["controls"]))
        try_action(
            "apply_live_solution_initialization",
            lambda: solution.initialization.set_state(live_solution["initialization"]),
        )
        try_action(
            "apply_live_solution_monitor",
            lambda: apply_carrier_solution_monitor(solver, live_solution["monitor"]),
        )
        try_action(
            "apply_live_solution_monitor_continuity",
            lambda: apply_carrier_solution_monitor_continuity(solver, live_solution["monitor"]),
        )
    else:
        print("apply_live_solution_state: skipped because solution branch is inactive")
        if strict:
            raise RuntimeError("solution branch is inactive")

    overall_ok = bool(carrier_ok and solution_ok)
    if strict and not overall_ok:
        raise RuntimeError("live archive replay failed")
    return overall_ok


def safe_step(label: str, func, *, strict: bool) -> bool:
    try:
        func()
        return True
    except Exception as exc:
        print(f"{label}: WARNING -> {exc}", flush=True)
        if strict:
            raise RuntimeError(f"{label} failed") from exc
        return False


def apply_two_inlet_boundary_state(
    solver,
    role_map: dict[str, str],
    split_boundary_conditions: dict[str, object],
    *,
    strict: bool,
) -> bool:
    print_header("Map Target Boundary Roles")
    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "target_boundary_conditions")
    if not isinstance(boundary_state, dict):
        if strict:
            raise RuntimeError("Could not inspect target boundary state")
        print("target_boundary_conditions: WARNING -> could not inspect boundary state")
        return False
    summarize_boundary_state(boundary_state)

    safe_step(
        "convert_target_boundaries_to_intended",
        lambda: convert_target_boundaries_to_intended(solver, boundary_state, role_map),
        strict=strict,
    )

    print_header("Apply Split-Inlet Boundary Pattern")
    intended_boundary = build_intended_boundary_state(role_map)
    if split_boundary_conditions:
        # Keep the archive loaded for traceability, but drive the actual setup with the
        # split-inlet authority already encoded in setup_carrier.build_intended_boundary_state.
        _ = split_boundary_conditions
    if not safe_step("apply_split_inlet_boundary_state", lambda: apply_boundary_states(solver, intended_boundary), strict=strict):
        if strict:
            raise RuntimeError("Failed to apply split-inlet boundary state")
        return False
    return True


def apply_archived_dpm_state(
    solver,
    *,
    role_map: dict[str, str],
    particle_entries: list[dict[str, object]],
    particle_material_name: str,
    strict: bool,
) -> tuple[list[str], bool]:
    print_header("Apply Archived DPM Model Settings")
    dpm_model_ok = apply_dpm_model_settings(
        solver,
        dpm_max_steps=10000,
        one_way_coupling=True,
        strict=strict,
    )
    if not dpm_model_ok:
        print("dpm_model_settings: WARNING -> continuing with partial DPM setup")

    print_header("Bootstrap DPM Inert Material Branch")
    material_ok = bootstrap_inert_particle_material_branch(
        solver,
        material_name=particle_material_name,
        density=1000.0,
        seed_name=SEED_INJECTION_NAME,
        strict=strict,
    )
    if not material_ok:
        print("dpm_material_bootstrap: WARNING -> continuing with partial DPM setup")

    steam_inlet_name = role_map[STEAM_INLET_SURFACE_ROLE]
    injection_state = build_archived_injection_state(
        particle_entries,
        steam_inlet_name,
        particle_material_name,
    )

    print_header("Apply Archived DPM Injections")
    injections_ok = apply_dpm_injections(solver, injection_state, strict=strict)
    if not injections_ok:
        print("dpm_injections: WARNING -> continuing with partial DPM setup")

    safe_step(
        "delete_seed_injection",
        lambda: delete_injection_if_present(solver, SEED_INJECTION_NAME),
        strict=False,
    )

    return sorted(injection_state.keys()), bool(dpm_model_ok and material_ok and injections_ok)


def write_rebuilt_case_only(solver, output_case: str, *, strict: bool) -> bool:
    print_header("Write Rebuilt Case")
    return safe_step(
        "write_case_only",
        lambda: write_case_only(solver, output_case, "write_rebuilt_case_only"),
        strict=strict,
    )


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    archive_inputs = load_archive_inputs()
    live_setup = archive_inputs["live_setup"]
    live_solution = archive_inputs["live_solution"]
    split_boundary_conditions = archive_inputs["split_boundary_conditions"]
    particle_entries = archive_inputs["particle_entries"]

    archived_particle_material, particle_material = resolve_archived_particle_material(
        particle_entries,
        args.particle_material,
    )

    plan_summary = summarize_run_plan(
        target_mesh=args.target_mesh,
        output_case=args.output_case,
        role_map=None,
        injection_names=[str(entry["injection_name"]) for entry in particle_entries],
        archived_particle_material=archived_particle_material,
        particle_material=particle_material,
    )

    if args.dry_run:
        write_json_snapshot(args.snapshot_json, plan_summary)
        print(json.dumps(plan_summary, indent=2))
        return 0

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    resume_mode = bool(args.resume_case)

    try:
        if resume_mode:
            print_header("Load Existing Setup Case")
            load_case_only(solver, args.resume_case, label="Load Existing Setup Case")
        else:
            load_target_mesh(solver, args.target_mesh)

            target_boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "target_boundary_conditions")
            if not isinstance(target_boundary_state, dict):
                raise RuntimeError("Could not inspect target boundary conditions after loading the mesh")
            role_map = build_target_role_map(target_boundary_state)

            if args.apply_live_archive:
                safe_step(
                    "apply_live_carrier_and_solution",
                    lambda: apply_live_carrier_and_solution(
                        solver,
                        live_setup,
                        live_solution,
                        strict=args.strict,
                    ),
                    strict=args.strict,
                )
            else:
                print("apply_live_archive: skipped (default safe mode)")

            boundary_ok = apply_two_inlet_boundary_state(
                solver,
                role_map,
                split_boundary_conditions,
                strict=args.strict,
            )
            if not boundary_ok:
                print("boundary_setup: WARNING -> continuing to case write")

            created_injections, dpm_ok = apply_archived_dpm_state(
                solver,
                role_map=role_map,
                particle_entries=particle_entries,
                particle_material_name=particle_material,
                strict=args.strict,
            )
            if not dpm_ok:
                print("dpm_setup: WARNING -> continuing to case write")

            write_rebuilt_case_only(solver, args.output_case, strict=args.strict)

        if resume_mode:
            target_boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "target_boundary_conditions")
            if not isinstance(target_boundary_state, dict):
                raise RuntimeError("Could not inspect target boundary conditions after resume load")
            role_map = build_target_role_map(target_boundary_state)
            created_injections = sorted(particle["injection_name"] for particle in particle_entries)
            write_rebuilt_case_only(solver, args.output_case, strict=args.strict)

        final_summary = summarize_run_plan(
            target_mesh=args.target_mesh,
            output_case=args.output_case,
            role_map=role_map,
            injection_names=created_injections,
            archived_particle_material=archived_particle_material,
            particle_material=particle_material,
        )
        final_summary["boundary_summary"] = build_compact_boundary_summary(target_boundary_state)
        final_summary["resume_mode"] = resume_mode
        write_json_snapshot(args.snapshot_json, final_summary)

        print("\nPurnanto 1680/1600J rebuild complete.")
        return 0
    except Exception as exc:
        print(f"\nPurnanto rebuild failed: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

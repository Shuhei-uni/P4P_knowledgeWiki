#!/usr/bin/env python3
"""Minimal DPM test setup for Fluent gRPC sessions.

This script is intentionally small:
- connect to one configured Fluent server;
- load the target mesh;
- resolve boundary roles dynamically;
- enable the DPM model;
- create one inert-particle material and one surface injection;
- write a case file without running iterations.

It is meant for probing the DPM setup path without touching the larger
setup08b rebuild flow.
"""

from __future__ import annotations

import argparse
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
from pyansys_fluent.setup_common import print_header  # noqa: E402
from pyansys_fluent.setup_discovery import build_target_role_map  # noqa: E402
from pyansys_fluent.setup_dpm import (  # noqa: E402
    SEED_INJECTION_NAME,
    apply_dpm_model_settings,
    apply_dpm_injections,
    bootstrap_inert_particle_material_branch,
    build_injection_state,
    delete_injection_if_present,
    resolve_particle_material_name,
)
from pyansys_fluent.setup_io import load_target_mesh  # noqa: E402
from pyansys_fluent.setup_io import write_case_only as write_remote_case_only  # noqa: E402


DEFAULT_SERVER_ID = "3"
DEFAULT_TARGET_MESH = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files"
    r"\PureTwoPhaseV2(PurnantoV2).msh"
)
DEFAULT_OUTPUT_CASE = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files\output"
    r"\PureTwoPhaseV2(PurnantoV2)-simple-dpm-test.cas.h5"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a minimal DPM setup test on a configured Fluent server.")
    parser.add_argument("--server-id", default=DEFAULT_SERVER_ID, help="Configured Fluent server id to use. Default: 3.")
    parser.add_argument("--target-mesh", default=DEFAULT_TARGET_MESH, help="Remote mesh path visible to the Fluent session.")
    parser.add_argument("--output-case", default=DEFAULT_OUTPUT_CASE, help="Remote case path to write at the end of the test.")
    parser.add_argument("--snapshot-json", default="", help="Optional local JSON path for a short run summary.")
    parser.add_argument("--particle-material", default="", help="Optional inert-particle material override.")
    parser.add_argument("--particle-density", type=float, default=1000.0, help="Density for the test inert-particle material.")
    parser.add_argument("--particle-mass-flow-rate", type=float, default=1e-6, help="Surface injection total flow rate.")
    parser.add_argument("--droplet-diameter-um", type=float, default=112.0, help="Single droplet diameter for the test injection.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop immediately when any DPM step fails.")
    return parser


def write_case_only(solver, output_case: str) -> bool:
    try:
        print_header("Write Case")
        write_remote_case_only(solver, output_case, "simple_dpm_test")
        return True
    except Exception as exc:
        print(f"write_case: FAILED -> {exc}", flush=True)
        return False


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()
    strict = args.fail_fast
    summary: dict[str, object] = {
        "target_mesh": args.target_mesh,
        "output_case": args.output_case,
        "strict": strict,
        "stages": {},
    }

    print_header("Connect")
    solver = connect(server_id=args.server_id)
    print(f"Connected to Fluent {solver.get_fluent_version()}")
    summary["fluent_version"] = solver.get_fluent_version()

    print_header("Load Mesh")
    load_target_mesh(solver, args.target_mesh)

    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "target_boundary_conditions")
    if not isinstance(boundary_state, dict):
        raise RuntimeError("Could not inspect boundary conditions after loading the mesh")
    role_map = build_target_role_map(boundary_state)
    summary["role_map"] = role_map

    archived_material = "water-liquid"
    particle_material = resolve_particle_material_name(archived_material, override=args.particle_material)
    summary["particle_material"] = particle_material

    print_header("Enable DPM")
    dpm_model_ok = apply_dpm_model_settings(solver, dpm_max_steps=5000, one_way_coupling=True, strict=strict)
    summary["stages"]["dpm_model_settings"] = dpm_model_ok
    if not dpm_model_ok:
        print("dpm_model_settings: WARNING -> continuing to case write", flush=True)
        if strict:
            raise RuntimeError("Failed to enable basic DPM settings")

    print_header("Bootstrap Material")
    material_ok = bootstrap_inert_particle_material_branch(
        solver,
        material_name=particle_material,
        density=args.particle_density,
        seed_name=SEED_INJECTION_NAME,
        strict=strict,
    )
    summary["stages"]["dpm_material_bootstrap"] = material_ok
    if not material_ok:
        print("dpm_material_bootstrap: WARNING -> continuing to case write", flush=True)
        if strict:
            raise RuntimeError("Failed to create the test inert-particle material")

    print_header("Build Injection")
    injection_state = build_injection_state(
        role_map,
        particle_material=particle_material,
        injection_surface_role="steam_inlet",
        droplet_diameters_um=(args.droplet_diameter_um,),
        particle_mass_flow_rate=args.particle_mass_flow_rate,
        enable_turbulent_dispersion=False,
        turbulent_dispersion_tries=1,
    )
    summary["injections"] = sorted(injection_state.keys())

    print_header("Prepare Probe Injection")
    for injection_name in sorted(injection_state.keys()):
        try_action(
            f"delete_existing_probe_injection_{injection_name}",
            lambda name=injection_name: delete_injection_if_present(solver, name),
            critical=False,
        )

    injections_ok = apply_dpm_injections(solver, injection_state, strict=strict)
    summary["stages"]["dpm_injections"] = injections_ok
    summary["dpm_state_after_injections"] = safe_get_state(
        solver.settings.setup.models.discrete_phase,
        "discrete_phase_after_injections",
    )
    if not injections_ok:
        print("dpm_injections: WARNING -> continuing to case write", flush=True)
        if strict:
            raise RuntimeError("Failed to create the test DPM injection")

    print_header("Cleanup")
    try_action("delete_seed_injection", lambda: delete_injection_if_present(solver, SEED_INJECTION_NAME), critical=False)

    if not write_case_only(solver, args.output_case):
        raise RuntimeError("Failed to write the test case")
    summary["stages"]["write_case"] = True

    summary["overall_dpm_ok"] = bool(dpm_model_ok and material_ok and injections_ok)
    write_json_snapshot(args.snapshot_json, summary)
    print("\nSimple DPM test complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

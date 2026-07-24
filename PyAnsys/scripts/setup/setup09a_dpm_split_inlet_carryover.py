#!/usr/bin/env python3
"""Build setup 09a from the setup 07 split-inlet carrier-field scaffold."""

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

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pyansys_fluent.connection import connect, env_suffix  # noqa: E402
from pyansys_fluent.run_persistence import RunPersistence  # noqa: E402
from pyansys_fluent.setup_dpm import um_to_microns_text  # noqa: E402
from pyansys_fluent.setup_io import dump_json_if_requested  # noqa: E402
from pyansys_fluent.setup_recipes import (  # noqa: E402
    CarrierRunConfig,
    CheckpointConfig,
    DpmConfig,
    require_setup09a_paths,
    run_setup09a_dpm_extension_recipe,
)
from pyansys_fluent.setup_run import RunInterrupted  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402


DEFAULT_DROPLET_DIAMETERS_UM = (5.0, 10.0, 14.2, 41.0)
DEFAULT_INJECTION_SURFACE_ROLE = "steam_inlet"
DEFAULT_WALL_DPM_MODE = "reflect"
DEFAULT_BOTTOM_DPM_MODE = "trap"
DEFAULT_OUTLET_DPM_MODE = "escape"
DEFAULT_PARTICLE_MASS_FLOW_RATE = 1e-6
DEFAULT_STREAMS_PER_INJECTION = 200
DEFAULT_CARRIER_ITERATIONS = 500
DEFAULT_SERVER_ID = "3"
DEFAULT_TARGET_MESH = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files"
    r"\PureTwoPhaseV2(PurnantoV2).msh"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare setup 09a as a setup 07 carrier-field rebuild plus one-way "
            "DPM carryover injections on a second Fluent gRPC session."
        )
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print the planned 09a payload without connecting to Fluent.")
    mode.add_argument("--apply", action="store_true", help="Connect to Fluent, stage a converged carrier field, then apply the 09a DPM extension.")
    parser.add_argument(
        "--server-id",
        default=DEFAULT_SERVER_ID,
        help="Configured local Fluent server id. Default: 3. Use FLUENT_SERVER_INFO_FILE3 or FLUENT_LOCAL_EXE3.",
    )
    parser.add_argument("--target-mesh", default=DEFAULT_TARGET_MESH, help="Remote mesh path visible to the target Fluent session.")
    parser.add_argument("--resume-case", default="", help="Optional remote converged setup 07 case file to resume from instead of rebuilding from mesh.")
    parser.add_argument("--resume-data", default="", help="Optional remote converged data file to resume from instead of rebuilding from mesh.")
    parser.add_argument("--resume-state-json", default="", help="Optional run-state JSON to resume from when no explicit resume pair is supplied.")
    parser.add_argument("--resume-latest", action="store_true", help="Resume from the latest autosave or numbered checkpoint matching the output paths.")
    parser.add_argument(
        "--carrier-iterations",
        type=int,
        default=DEFAULT_CARRIER_ITERATIONS,
        help="Iterations to run the setup 07 carrier field before enabling DPM when rebuilding from mesh. Default: 500.",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Build the mesh-based carrier setup and apply the 09a DPM/material/injection settings without initialization or any carrier iterations.",
    )
    parser.add_argument("--output-case", default="", help="Optional remote final 09a case path to write after DPM setup and any later iterations.")
    parser.add_argument("--output-data", default="", help="Optional remote final 09a data path to write with the output case.")
    parser.add_argument("--initialized-case", default="", help="Optional remote case path to write immediately after initialization.")
    parser.add_argument("--initialized-data", default="", help="Optional remote data path to write immediately after initialization.")
    parser.add_argument(
        "--injection-surface-role",
        choices=("steam_inlet", "liquid_inlet"),
        default=DEFAULT_INJECTION_SURFACE_ROLE,
        help="Which split inlet supplies the tracked droplets. Default: steam_inlet.",
    )
    parser.add_argument(
        "--droplet-diameters-um",
        nargs="+",
        type=float,
        default=list(DEFAULT_DROPLET_DIAMETERS_UM),
        help="DPM droplet diameters in micrometers. Default: 5 10 14.2 41.",
    )
    parser.add_argument("--particle-material", default="water-droplet", help="Inert particle material for DPM. Default: water-droplet.")
    parser.add_argument("--particle-density", type=float, default=881.77, help="Particle density for the inert particle material. Default: 881.77.")
    parser.add_argument("--streams-per-injection", type=int, default=DEFAULT_STREAMS_PER_INJECTION, help="Surface injection stream count. Default: 200.")
    parser.add_argument("--particle-mass-flow-rate", type=float, default=DEFAULT_PARTICLE_MASS_FLOW_RATE, help="DPM total flow rate per injection. Default: 1e-6.")
    parser.add_argument("--enable-turbulent-dispersion", action="store_true", help="Enable stochastic turbulent dispersion for each injection.")
    parser.add_argument("--turbulent-dispersion-tries", type=int, default=2, help="Number of stochastic tries when turbulent dispersion is enabled.")
    parser.add_argument("--dpm-max-steps", type=int, default=5000, help="DPM maximum tracking steps. Default: 5000.")
    parser.add_argument("--wall-dpm-mode", choices=("reflect", "trap"), default=DEFAULT_WALL_DPM_MODE, help="DPM fate on main walls. Default: reflect.")
    parser.add_argument("--bottom-dpm-mode", choices=("trap", "reflect"), default=DEFAULT_BOTTOM_DPM_MODE, help="DPM fate on bottom collection wall. Default: trap.")
    parser.add_argument("--outlet-dpm-mode", choices=("escape", "trap"), default=DEFAULT_OUTLET_DPM_MODE, help="DPM fate on the steam outlet. Default: escape.")
    parser.add_argument("--snapshot-json", default="", help="Optional local JSON path to dump the planned 09a payload.")
    parser.add_argument("--iterations", type=int, default=0, help="Optional iterations to run after the 09a DPM extension is applied. Default: 0.")
    parser.add_argument("--report-interval", type=int, default=100, help="Console progress interval during iterations. Default: 100.")
    parser.add_argument("--checkpoint-interval", type=int, default=1000, help="Overwrite a rolling autosave case/data checkpoint every N iterations. Default: 1000.")
    return parser


def connect_with_env_suffix(server_id: str | int = DEFAULT_SERVER_ID):
    load_dotenv()
    suffix = env_suffix(server_id)
    return connect(server_id=suffix or "1")


def build_dpm_plan(args: argparse.Namespace) -> dict[str, object]:
    droplet_sizes = [
        {
            "name": f"dpm-{um_to_microns_text(diameter_um)}um",
            "diameter_um": diameter_um,
            "diameter_m": diameter_um * 1e-6,
        }
        for diameter_um in args.droplet_diameters_um
    ]
    assumptions = [
        "Setup 09a inherits the setup 07 continuous-field definition.",
        "Tracked particles are injected from the steam-side split inlet by default.",
        "Steam outlet is treated as escape for carryover counting.",
        "Bottom is treated as trap for collected liquid unless later revised.",
        "Main separator walls are treated as reflect by default to avoid silently counting all wall hits as separation.",
        "DPM is one-way only. Continuous-phase feedback stays disabled.",
        (
            "When rebuilding from mesh, the setup 07 carrier field is iterated before DPM is applied."
            if args.carrier_iterations > 0
            else (
                "When rebuilding from mesh in setup-only mode, DPM is applied before initialization and before any carrier iterations."
                if args.setup_only
                else "A converged setup 07 case/data pair should be supplied before applying DPM."
            )
        ),
        "No post-DPM iterations are planned." if args.iterations <= 0 else "Additional iterations are requested after the 09a DPM extension is applied.",
    ]
    return {
        "setup_id": "09a",
        "lineage_parent": "07-pure-phase-split-actual-area",
        "target_mesh": args.target_mesh,
        "resume_case": args.resume_case,
        "resume_data": args.resume_data,
        "carrier_iterations": args.carrier_iterations,
        "output_case": args.output_case,
        "output_data": args.output_data,
        "initialized_case": args.initialized_case,
        "initialized_data": args.initialized_data,
        "iterations": args.iterations,
        "report_interval": args.report_interval,
        "checkpoint_interval": args.checkpoint_interval,
        "carrier_field": {
            "solver": "pressure-based",
            "time": "steady",
            "multiphase": "mixture",
            "turbulence": "RNG k-epsilon",
            "energy": "off",
            "surface_tension_best_effort": 0.0411,
        },
        "dpm": {
            "one_way_coupling": True,
            "unsteady_particle_tracking": False,
            "particle_material": args.particle_material,
            "particle_density": args.particle_density,
            "injection_surface_role": args.injection_surface_role,
            "streams_per_injection": args.streams_per_injection,
            "particle_mass_flow_rate": args.particle_mass_flow_rate,
            "enable_turbulent_dispersion": args.enable_turbulent_dispersion,
            "turbulent_dispersion_tries": args.turbulent_dispersion_tries,
            "max_tracking_steps": args.dpm_max_steps,
            "droplet_sizes": droplet_sizes,
            "boundary_fates": {
                "steam_outlet": args.outlet_dpm_mode,
                "main_walls": args.wall_dpm_mode,
                "bottom": args.bottom_dpm_mode,
            },
        },
        "assumptions": assumptions,
        "user_inputs_still_needed": [
            "Converged setup 07 case/data pair, or a remote .msh path plus carrier iterations",
            "Final case/data output path(s)",
            "Confirmation that droplets should be injected from the steam-side inlet",
            "Any alternative wall-fate interpretation for carryover accounting",
        ],
    }


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    plan = build_dpm_plan(args)
    dump_json_if_requested(args.snapshot_json, plan)
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    run_config = CarrierRunConfig(
        target_mesh=args.target_mesh,
        resume_case=args.resume_case,
        resume_data=args.resume_data,
        resume_state_json=args.resume_state_json,
        resume_latest=args.resume_latest,
        setup_only=args.setup_only,
        carrier_iterations=args.carrier_iterations,
    )
    checkpoint_config = CheckpointConfig(
        output_case=args.output_case,
        output_data=args.output_data,
        initialized_case=args.initialized_case,
        initialized_data=args.initialized_data,
        checkpoint_interval=args.checkpoint_interval,
        report_interval=args.report_interval,
    )
    dpm_config = DpmConfig(
        particle_material=args.particle_material,
        particle_density=args.particle_density,
        injection_surface_role=args.injection_surface_role,
        droplet_diameters_um=tuple(args.droplet_diameters_um),
        particle_mass_flow_rate=args.particle_mass_flow_rate,
        streams_per_injection=args.streams_per_injection,
        dpm_max_steps=args.dpm_max_steps,
        enable_turbulent_dispersion=args.enable_turbulent_dispersion,
        turbulent_dispersion_tries=args.turbulent_dispersion_tries,
        wall_dpm_mode=args.wall_dpm_mode,
        bottom_dpm_mode=args.bottom_dpm_mode,
        outlet_dpm_mode=args.outlet_dpm_mode,
        one_way_coupling=True,
    )
    require_setup09a_paths(run_config, checkpoint_config, args.iterations)

    solver = connect_with_env_suffix(args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")

    try:
        result = run_setup09a_dpm_extension_recipe(
            solver,
            run_config,
            checkpoint_config,
            dpm_config,
            post_dpm_iterations=args.iterations,
        )
    except RunInterrupted as exc:
        print_header("Interrupt Save")
        print(
            "Keyboard interrupt received. Saving current solver state so it can be resumed "
            f"from {args.output_case} and {args.output_data}."
        )
        persistence = RunPersistence(
            output_case=args.output_case,
            output_data=args.output_data,
            checkpoint_interval=args.checkpoint_interval,
            report_interval=args.report_interval,
        )
        persistence.record_interrupt(
            solver,
            completed_iterations=exc.completed_iterations,
            allow_case_only=False,
        )
        print(f"\nPaused run saved after approximately {exc.completed_iterations} completed iterations.")
        return 130

    payload = {
        "plan": plan,
        "role_map": result["role_map"],
        "final_boundary_summary": result["final_boundary_summary"],
        "created_injections": result["created_injections"],
    }
    print_header("09a Payload Summary")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

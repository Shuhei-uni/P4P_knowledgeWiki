#!/usr/bin/env python3
"""Build setup 09a as a case-only DPM artifact.

This script does not initialize, iterate, or write client-side checkpoints.
Run the prepared case from Fluent with native calculation-activity autosave.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pyansys_fluent.connection import connect, env_suffix  # noqa: E402
from pyansys_fluent.setup_dpm import um_to_microns_text  # noqa: E402
from pyansys_fluent.setup_io import dump_json_if_requested  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402
from pyansys_fluent.setup_recipes import (  # noqa: E402
    CarrierRunConfig,
    CheckpointConfig,
    DpmConfig,
    require_setup09a_paths,
    run_setup09a_dpm_extension_recipe,
)


DEFAULT_DROPLET_DIAMETERS_UM = (5.0, 10.0, 14.2, 41.0)
DEFAULT_INJECTION_SURFACE_ROLE = "steam_inlet"
DEFAULT_WALL_DPM_MODE = "reflect"
DEFAULT_BOTTOM_DPM_MODE = "trap"
DEFAULT_OUTLET_DPM_MODE = "escape"
DEFAULT_PARTICLE_MASS_FLOW_RATE = 1e-6
DEFAULT_STREAMS_PER_INJECTION = 200
DEFAULT_CARRIER_ITERATIONS = 0
DEFAULT_SERVER_ID = "3"
DEFAULT_TARGET_MESH = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(PurnantoV2)\Major Files"
    r"\PureTwoPhaseV2(PurnantoV2).msh"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare setup 09a as a case-only setup 07 carrier-field rebuild plus "
            "one-way DPM carryover injections."
        )
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print the planned 09a payload without connecting to Fluent.")
    mode.add_argument("--apply", action="store_true", help="Connect to Fluent, build the case-only carrier/DPM setup, and save it for a later Fluent-native run.")
    parser.add_argument(
        "--server-id",
        default=DEFAULT_SERVER_ID,
        help="Configured Fluent server id to use. Default: 3. Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3.",
    )
    parser.add_argument("--target-mesh", default=DEFAULT_TARGET_MESH, help="Remote mesh path visible to the target Fluent session.")
    parser.add_argument("--resume-case", default="", help="Optional remote case to load and extend instead of rebuilding from mesh. Fluent data/restart handling occurs outside this builder.")
    parser.add_argument(
        "--carrier-iterations",
        type=int,
        default=DEFAULT_CARRIER_ITERATIONS,
        help="Retired client-side carrier iterations; must remain 0. Run the carrier field from Fluent with native autosave.",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Build the mesh-based carrier setup and apply the 09a DPM/material/injection settings without initialization or any carrier iterations.",
    )
    parser.add_argument("--output-case", default="", help="Remote case path to write after the case-only DPM setup.")
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
            "When rebuilding from mesh, the case-only carrier and DPM setup is written before any Fluent-native initialization or iterations."
        ),
        "No Python post-DPM iterations are planned; start any solve from Fluent with native autosave.",
    ]
    return {
        "setup_id": "09a",
        "lineage_parent": "07-pure-phase-split-actual-area",
        "target_mesh": args.target_mesh,
        "resume_case": args.resume_case,
        "carrier_iterations": args.carrier_iterations,
        "output_case": args.output_case,
        "run_policy": "Fluent-native initialization, iteration, and autosave; no client-side Python loop",
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
            "A remote .msh path or an existing case-only setup case",
            "A remote case output path",
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
        setup_only=args.setup_only,
        carrier_iterations=args.carrier_iterations,
    )
    checkpoint_config = CheckpointConfig(
        output_case=args.output_case,
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
    require_setup09a_paths(run_config, checkpoint_config, 0)

    solver = connect_with_env_suffix(args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")

    result = run_setup09a_dpm_extension_recipe(
        solver,
        run_config,
        checkpoint_config,
        dpm_config,
        post_dpm_iterations=0,
    )

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

#!/usr/bin/env python3
"""Build setup 07 as a case-only Fluent artifact.

This compatibility entry point deliberately does not initialize, iterate, or
write client-side checkpoints. After the case is written, start the calculation
from Fluent with native autosave configured; see
``knowledge/fluent-settings/native_run_and_autosave.md``.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_recipes import (  # noqa: E402
    CarrierRunConfig,
    CheckpointConfig,
    require_setup07_paths,
    run_setup07_carrier_recipe,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Apply intended setup 07 to a target mesh and write a case-only artifact."
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured Fluent server id to use. Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3.",
    )
    parser.add_argument("--target-mesh", required=True, help="Remote target mesh file visible to Fluent.")
    parser.add_argument("--output-case", required=True, help="Remote case-only output path.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    run_config = CarrierRunConfig(target_mesh=args.target_mesh)
    checkpoint_config = CheckpointConfig(output_case=args.output_case)
    require_setup07_paths(run_config)

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    run_setup07_carrier_recipe(
        solver,
        run_config,
        checkpoint_config,
        iterations=0,
        skip_run=True,
    )
    print("\nSetup 07 case-only rebuild finished.")
    print("Start initialization and the long run from Fluent with native autosave.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Probe Fluent write-settings/read-settings transfer between a case and mesh.

This script intentionally mutates the connected Fluent session by loading a
case or mesh and applying settings. It does not initialize or run iterations.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path, PureWindowsPath

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.settings_transfer import (  # noqa: E402
    read_settings_file_onto_mesh,
    transfer_settings_to_mesh,
    write_settings_file,
)


DEFAULT_SERVER_ID = "2"
DEFAULT_SOURCE_CASE = r"C:\Users\syok443\Documents\Purnanto\enthalpy1680.cas"
DEFAULT_TARGET_MESH = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)"
    r"\TwoPhaseInlet(PurnantoExtended).msh"
)


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def default_settings_path(source_case_path: str) -> str:
    source = PureWindowsPath(source_case_path)
    return str(source.parent / f"{source.stem}-settings-transfer-{timestamp()}.set")


def default_output_case_path(mesh_path: str) -> str:
    mesh = PureWindowsPath(mesh_path)
    return str(mesh.parent / f"{mesh.stem}-settings-transfer-{timestamp()}.cas.h5")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Write Fluent settings from a case, read them onto a mesh, or run both as a transfer probe."
    )
    parser.add_argument(
        "--mode",
        choices=("transfer", "write", "read"),
        default="transfer",
        help="Operation to run. Default: transfer.",
    )
    parser.add_argument(
        "--server-id",
        default=DEFAULT_SERVER_ID,
        help="Configured Fluent server id to use. Default: 2.",
    )
    parser.add_argument(
        "--source-case",
        default=DEFAULT_SOURCE_CASE,
        help="Remote Fluent source case path for write/transfer modes.",
    )
    parser.add_argument(
        "--source-data",
        default="",
        help="Optional remote Fluent source data path to load after the source case.",
    )
    parser.add_argument(
        "--target-mesh",
        default=DEFAULT_TARGET_MESH,
        help="Remote Fluent target mesh path for read/transfer modes.",
    )
    parser.add_argument(
        "--settings-file",
        default="",
        help="Remote Fluent .set path. Defaults to a timestamped file beside the source case.",
    )
    parser.add_argument(
        "--output-case",
        default="",
        help="Optional remote Fluent case path to write after reading settings.",
    )
    parser.add_argument(
        "--write-output-case",
        action="store_true",
        help="Write a timestamped case beside the target mesh after read/transfer if --output-case is not set.",
    )
    parser.add_argument(
        "--summary-json",
        default="",
        help="Optional local JSON path for the probe summary.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirm that replacing the active Fluent session state is intentional.",
    )
    return parser


def dump_summary_if_requested(path_text: str, payload: object) -> None:
    if not path_text:
        return
    path = Path(path_text).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    print(f"summary_json: {path}", flush=True)


def main() -> int:
    args = build_parser().parse_args()
    if not args.yes:
        print("Refusing to run without --yes.")
        print("This probe loads case/mesh files and changes the active Fluent session state.")
        return 2

    settings_file = args.settings_file or default_settings_path(args.source_case)
    output_case = args.output_case
    if not output_case and args.write_output_case and args.mode in {"transfer", "read"}:
        output_case = default_output_case_path(args.target_mesh)

    print(f"server_id: {args.server_id}")
    print(f"mode: {args.mode}")
    print(f"source_case: {args.source_case}")
    if args.source_data:
        print(f"source_data: {args.source_data}")
    print(f"target_mesh: {args.target_mesh}")
    print(f"settings_file: {settings_file}")
    if output_case:
        print(f"output_case: {output_case}")

    solver = connect(server_id=args.server_id)
    print("\nConnected. Starting settings transfer probe.")

    if args.mode == "write":
        result = write_settings_file(
            solver,
            source_case_path=args.source_case,
            source_data_path=args.source_data or None,
            settings_path=settings_file,
        )
    elif args.mode == "read":
        result = read_settings_file_onto_mesh(
            solver,
            mesh_path=args.target_mesh,
            settings_path=settings_file,
            output_case_path=output_case or None,
        )
    else:
        result = transfer_settings_to_mesh(
            solver,
            source_case_path=args.source_case,
            source_data_path=args.source_data or None,
            mesh_path=args.target_mesh,
            settings_path=settings_file,
            output_case_path=output_case or None,
        )

    dump_summary_if_requested(args.summary_json, result)
    print("\nProbe completed. No iterations were run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Probe Fluent TUI particle-track XY export prompts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPTS = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SETUP_SCRIPTS))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Probe particle-track XY TUI command arguments.")
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--remote-output-dir", default=sweep.DEFAULT_REMOTE_OUTPUT_DIR)
    parser.add_argument("--local-output-dir", default=str(sweep.DEFAULT_LOCAL_OUTPUT_DIR / "ring_diagnostic"))
    parser.add_argument("--label", default="particle_xy_tui_probe")
    return parser


def ti_menu_capture(solver, command: str) -> str:
    escaped = quote_scheme_string(command)
    return sweep.capture_call(command, lambda: solver.scheme.exec((f'(ti-menu-load-string "{escaped}")',)))


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()
    output_dir = Path(args.local_output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    solver = connect(server_id=args.server_id)
    sweep.ensure_remote_directory_best_effort(solver, args.remote_output_dir)
    remote_xy = sweep.remote_join(args.remote_output_dir, f"{args.label}.xy")

    commands = [
        "/display/particle-tracks/plot-write-xy-plot ?",
        "/display/particle-tracks/plot-write-xy-plot",
        f"/display/particle-tracks/plot-write-xy-plot yes {remote_xy}",
        f"/display/particle-tracks/plot-write-xy-plot write {remote_xy}",
        f"/display/particle-tracks/plot-write-xy-plot file {remote_xy}",
        f"/display/particle-tracks/plot-write-xy-plot no yes {remote_xy}",
    ]

    results = []
    for command in commands:
        print(f"probe_command: {command}")
        text = ti_menu_capture(solver, command)
        exists = remote_file_exists(solver, remote_xy)
        file_text = sweep.remote_text_read_best_effort(solver, remote_xy) if exists else ""
        results.append(
            {
                "command": command,
                "output": text,
                "remote_xy": remote_xy,
                "remote_file_exists": exists,
                "remote_file_preview": file_text[:4000],
            }
        )

    local_json = output_dir / f"{args.label}.json"
    local_json.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"local_json: {local_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

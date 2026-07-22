#!/usr/bin/env python3
"""Run independent post-simulation checks against one live Fluent session.

The checks are deliberately read-only and can be selected individually:

    --check flux
    --check residual
    --check dpm

Use ``--check all`` for a complete pass.  Case/data loading is opt-in; the
default is to inspect the case/data already loaded in Fluent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
INSPECTION_DIR = PROJECT_ROOT / "scripts" / "inspection"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(INSPECTION_DIR))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import (  # noqa: E402
    calculate_carrier_metrics,
    capture_residual_history,
    capture_session_summary,
    extract_mass_flow_report,
    load_case_data_pair,
    plot_residual_history,
    write_json,
)
from run_dpm_particle_tracks import (  # noqa: E402
    format_dpm_console_report,
    run_dpm_particle_track_check,
    write_console_report,
    write_outputs as write_dpm_outputs,
)
from pyansys_fluent.setup_common import print_header, require_remote_input  # noqa: E402


CHECK_NAMES = ("flux", "residual", "dpm")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run independent read-only flux, residual, and DPM checks in Fluent."
    )
    parser.add_argument(
        "--check",
        dest="checks",
        action="append",
        choices=(*CHECK_NAMES, "all"),
        help="Check to run. Repeat for multiple checks. Default: all.",
    )
    parser.add_argument("--server-id", default="1")
    parser.add_argument(
        "--case-file",
        default="",
        help="Remote case path; required only with --load-case-data.",
    )
    parser.add_argument(
        "--data-file",
        default="",
        help="Remote data path; required only with --load-case-data.",
    )
    parser.add_argument(
        "--load-case-data",
        action="store_true",
        help="Explicitly load --case-file and --data-file before running checks.",
    )
    parser.add_argument(
        "--already-loaded",
        action="store_true",
        help="Compatibility alias for the default already-loaded-session behavior.",
    )
    parser.add_argument(
        "--load-mode",
        choices=("explicit", "paired"),
        default="explicit",
        help="Case/data loading mode when --load-case-data is used.",
    )
    parser.add_argument(
        "--run-label",
        default="active-session",
        help="Label used for generated output files.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output" / "post_simulation_analysis"),
    )

    parser.add_argument("--monitor-set", default="residual")
    parser.add_argument("--residual-timeout-seconds", type=float, default=10.0)
    parser.add_argument("--residual-poll-interval-seconds", type=float, default=0.5)
    parser.add_argument("--residual-settle-seconds", type=float, default=0.5)
    parser.add_argument("--residual-title", default="Scaled Residual History")

    parser.add_argument(
        "--dpm-injection",
        dest="dpm_injection_names",
        action="append",
        help="DPM injection name to select; repeat for multiple names.",
    )
    parser.add_argument(
        "--dpm-index",
        dest="dpm_injection_indices",
        action="append",
        type=int,
        help="Current live DPM injection index to select; repeat for multiple indices.",
    )
    parser.add_argument(
        "--dpm-order",
        choices=("live", "diameter-ascending", "diameter-descending"),
        default="diameter-ascending",
    )
    parser.add_argument("--dpm-inspect-only", action="store_true")
    parser.add_argument("--dpm-keep-going", action="store_true")
    parser.add_argument(
        "--dpm-detailed-output",
        action="store_true",
        help="Also write DPM JSON, CSV, and raw transcript artifacts; default is text summary only.",
    )
    return parser


def selected_checks(values: list[str] | None) -> list[str]:
    requested = values or ["all"]
    if "all" in requested:
        return list(CHECK_NAMES)
    return [name for name in CHECK_NAMES if name in requested]


def derive_run_label(args: argparse.Namespace) -> str:
    if args.run_label.strip() and args.run_label != "active-session":
        return args.run_label.strip()
    if args.data_file.strip():
        return PureWindowsPath(args.data_file).stem
    return "active-session"


def load_if_requested(solver: Any, args: argparse.Namespace) -> dict[str, Any]:
    if args.load_case_data and args.already_loaded:
        raise ValueError("Use either --load-case-data or --already-loaded, not both.")
    if not args.load_case_data:
        return {"mode": "already-loaded-session"}
    if not args.case_file.strip() or not args.data_file.strip():
        raise ValueError("--load-case-data requires both --case-file and --data-file.")
    require_remote_input(solver, args.case_file, "case file")
    require_remote_input(solver, args.data_file, "data file")
    return load_case_data_pair(
        solver,
        case_file=args.case_file,
        data_file=args.data_file,
        load_strategy=args.load_mode,
    )


def run_flux_check(solver: Any, *, run_label: str, output_dir: Path, load_summary: dict[str, Any]) -> Path:
    session_summary = capture_session_summary(solver)
    roles = session_summary["zone_discovery"]["roles"]
    zones: list[str] = []
    for value in (roles.get("liquid_inlet"), roles.get("steam_inlet")):
        if value and value not in zones:
            zones.append(value)
    for value in session_summary["zone_discovery"]["all_outlets"]:
        if value and value not in zones:
            zones.append(value)

    phase_map = session_summary["phase_domain_map"]
    fluxes = extract_mass_flow_report(
        solver,
        zones=zones,
        domains=(phase_map["vapor_domain"], phase_map["liquid_domain"]),
    )
    metrics = calculate_carrier_metrics(
        fluxes,
        roles,
        vapor_domain=phase_map["vapor_domain"],
        liquid_domain=phase_map["liquid_domain"],
    )
    payload = {
        "check": "flux",
        "run_label": run_label,
        "load": load_summary,
        "session": session_summary,
        "carrier_fluxes": fluxes,
        "carrier_metrics": metrics,
    }
    path = output_dir / f"{run_label}-flux-check.json"
    write_json(path, payload)
    return path


def run_residual_check(solver: Any, *, args: argparse.Namespace, run_label: str, output_dir: Path) -> tuple[Path, Path]:
    payload = capture_residual_history(
        solver,
        monitor_set=args.monitor_set,
        timeout=args.residual_timeout_seconds,
        interval=args.residual_poll_interval_seconds,
        settle_seconds=args.residual_settle_seconds,
    )
    json_path = output_dir / f"{run_label}-residual-check.json"
    plot_path = output_dir / f"{run_label}-residual-check.png"
    write_json(json_path, payload)
    plot_residual_history(payload, plot_path, title=args.residual_title)
    return json_path, plot_path


def main() -> int:
    args = build_parser().parse_args()
    checks = selected_checks(args.checks)
    run_label = derive_run_label(args)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("Connect")
    solver = connect(server_id=args.server_id)
    print(f"Connected to {solver.get_fluent_version()}", flush=True)
    load_summary = load_if_requested(solver, args)

    failures: list[str] = []
    for check in checks:
        try:
            print_header(f"{check.title()} Check")
            if check == "flux":
                path = run_flux_check(
                    solver,
                    run_label=run_label,
                    output_dir=output_dir,
                    load_summary=load_summary,
                )
                print(f"flux_json: {path}", flush=True)
            elif check == "residual":
                json_path, plot_path = run_residual_check(
                    solver,
                    args=args,
                    run_label=run_label,
                    output_dir=output_dir,
                )
                print(f"residual_json: {json_path}", flush=True)
                print(f"residual_plot: {plot_path}", flush=True)
            else:
                payload = run_dpm_particle_track_check(
                    solver,
                    case_file=args.case_file,
                    data_file=args.data_file,
                    load_case_data=False,
                    injection_names=args.dpm_injection_names or (),
                    injection_indices=args.dpm_injection_indices or (),
                    order=args.dpm_order,
                    inspect_only=args.dpm_inspect_only,
                    keep_going=args.dpm_keep_going,
                    run_label=run_label,
                )
                # The dispatcher loads at most once before the selected checks;
                # preserve that provenance in the DPM artifact.
                payload["load"] = load_summary
                payload["load_requested"] = args.load_case_data
                report_path = write_console_report(output_dir, f"{run_label}-dpm", payload)
                print(format_dpm_console_report(payload), end="", flush=True)
                print(f"dpm_report: {report_path}", flush=True)
                if args.dpm_detailed_output:
                    json_path, csv_path, transcript_path = write_dpm_outputs(
                        output_dir,
                        f"{run_label}-dpm",
                        payload,
                    )
                    print(f"dpm_json: {json_path}", flush=True)
                    print(f"dpm_csv: {csv_path}", flush=True)
                    print(f"dpm_transcript: {transcript_path}", flush=True)
                if not args.dpm_inspect_only and any(
                    item.get("status") != "ok" for item in payload.get("results", [])
                ):
                    failures.append("dpm")
        except Exception as exc:
            failures.append(check)
            print(f"{check} check failed: {type(exc).__name__}: {exc}", file=sys.stderr)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

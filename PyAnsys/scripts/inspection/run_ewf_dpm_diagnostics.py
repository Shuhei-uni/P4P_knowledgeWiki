#!/usr/bin/env python3
"""Audit and post-process Eulerian Wall Film plus DPM behavior in live Fluent.

Default mode is ``audit`` and does not intentionally mutate the case. Snapshot
modes create only namespaced report definitions; they never enable or disable
EWF, splash, stripping, separation, wall-film boundaries, or DPM interaction.

DPM mode captures Fluent's session transcript directly. Each injection must
produce a complete Summary block before the next command is submitted, and its
raw transcript plus partial CSV/JSON outputs are flushed immediately.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_reports import (  # noqa: E402
    configure_particle_track_summary,
    discover_live_injections,
    select_injections,
)
from pyansys_fluent.dpm_transcript import (  # noqa: E402
    SessionTranscriptCapture,
    track_one_injection_streamed,
)
from pyansys_fluent.ewf_diagnostics import (  # noqa: E402
    audit_ewf_dpm_settings,
    build_ewf_bookkeeping_target,
    create_and_compute_snapshot,
    extract_film_mass_flow,
    flatten_snapshot_reports,
    report_specs_as_dicts,
)
from pyansys_fluent.postprocess_live import (  # noqa: E402
    build_case_identity,
    load_case_data_pair,
)
from pyansys_fluent.setup_common import print_header, require_remote_input  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run read-mostly EWF/DPM diagnostics against an existing Fluent case/data state."
        )
    )
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--case-file", default="")
    parser.add_argument("--data-file", default="")
    parser.add_argument(
        "--load-case-data",
        action="store_true",
        help="Load --case-file and --data-file before analysis. Otherwise use the live session.",
    )
    parser.add_argument(
        "--load-mode",
        choices=("auto", "explicit", "paired"),
        default="explicit",
    )
    parser.add_argument(
        "--mode",
        choices=("audit", "snapshot", "dpm", "all"),
        default="audit",
        help="audit is non-mutating; snapshot creates namespaced diagnostic reports.",
    )
    parser.add_argument(
        "--film-wall",
        action="append",
        dest="film_walls",
        help="Active EWF wall name. Repeat for multiple walls. Auto-discovered when omitted.",
    )
    parser.add_argument(
        "--flux-boundary",
        action="append",
        dest="flux_boundaries",
        help="Boundary for Film Mass Flow Rate. Repeat as needed.",
    )
    parser.add_argument(
        "--injection",
        action="append",
        dest="injection_names",
        help="DPM injection name to track. Repeat as needed; all are used when omitted.",
    )
    parser.add_argument(
        "--index",
        action="append",
        type=int,
        dest="injection_indices",
        help="Live DPM injection index to track. Prefer names for stable automation.",
    )
    parser.add_argument(
        "--order",
        choices=("live", "diameter-ascending", "diameter-descending"),
        default="diameter-ascending",
    )
    parser.add_argument("--prefix", default="ewfdiag")
    parser.add_argument(
        "--object-policy",
        choices=("reuse", "replace", "fail"),
        default="reuse",
        help="How to handle existing report definitions owned by --prefix.",
    )
    parser.add_argument(
        "--create-history-files",
        action="store_true",
        help="Enable each report definition's Create Report File option for future iterations.",
    )
    parser.add_argument("--report-frequency", type=int, default=1)
    parser.add_argument("--tui-version", default="24.2")
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument(
        "--dpm-timeout-seconds",
        type=float,
        default=600.0,
        help="Maximum wait for one complete DPM Summary transcript block.",
    )
    parser.add_argument(
        "--transcript-quiet-seconds",
        type=float,
        default=1.0,
        help="Required no-output interval after the parsed Summary before continuing.",
    )
    parser.add_argument(
        "--echo-dpm-transcript",
        action="store_true",
        help="Echo the registered transcript callback to this Python terminal.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output" / "ewf_dpm_diagnostics"),
    )
    parser.add_argument("--run-label", default="")
    return parser


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        seen: set[str] = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    fieldnames.append(key)
                    seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def resolve_run_label(args: argparse.Namespace) -> str:
    if args.run_label.strip():
        return args.run_label.strip()
    if args.load_case_data and args.data_file:
        return PureWindowsPath(args.data_file).stem
    return datetime.now().strftime("ewf-dpm-%Y%m%d-%H%M%S")


def resolve_film_walls(
    args: argparse.Namespace,
    audit: dict[str, Any],
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    if args.film_walls:
        return list(dict.fromkeys(args.film_walls)), warnings
    discovered = [str(name) for name in audit.get("active_film_walls", [])]
    if discovered:
        return discovered, warnings
    wall_names = [
        str(item.get("name"))
        for item in audit.get("wall_zones", [])
        if item.get("name")
    ]
    if "wall" in wall_names:
        warnings.append(
            "Could not prove active film walls from the settings state; falling back to zone 'wall'."
        )
        return ["wall"], warnings
    warnings.append("No active EWF wall could be discovered. Supply --film-wall explicitly.")
    return [], warnings


def resolve_flux_boundaries(args: argparse.Namespace) -> list[str]:
    if args.flux_boundaries:
        return list(dict.fromkeys(args.flux_boundaries))
    return ["liquidinlet", "steaminlet", "steamoutlet"]


def dpm_summary_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        parsed = result.get("parsed", {})
        counts = parsed.get("counts", {})
        events = parsed.get("ewf_events", {})
        closure = result.get("closure", {})
        completion = result.get("completion", {})
        rows.append(
            {
                "index": result.get("index"),
                "injection": result.get("name"),
                "diameter_um": result.get("diameter_um"),
                "status": result.get("status"),
                "transcript_complete": completion.get("confirmed"),
                "completion_wait_seconds": completion.get("wait_seconds"),
                "tracked": counts.get("tracked"),
                "escaped": counts.get("escaped"),
                "trapped": counts.get("trapped"),
                "incomplete": counts.get("incomplete"),
                "aborted": counts.get("aborted"),
                "ewf_absorbed_events": events.get("absorbed"),
                "ewf_splashed_events_or_parcels": events.get("splashed"),
                "injected_kg_s": closure.get("injected_kg_s"),
                "terminal_sum_kg_s": closure.get("terminal_sum_kg_s"),
                "closure_residual_kg_s": closure.get("residual_kg_s"),
                "closure_relative_residual": closure.get("relative_residual"),
                "raw_output_path": result.get("raw_output_path"),
                "error": result.get("error"),
            }
        )
    return rows


def dpm_zone_rows(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        for fate in result.get("parsed", {}).get("fate_rows", []):
            elapsed = fate.get("elapsed_time_s", {})
            rows.append(
                {
                    "injection": result.get("name"),
                    "diameter_um": result.get("diameter_um"),
                    "fate": fate.get("fate"),
                    "zone": fate.get("zone"),
                    "zone_id": fate.get("zone_id"),
                    "count": fate.get("count"),
                    "elapsed_min_s": elapsed.get("min"),
                    "elapsed_max_s": elapsed.get("max"),
                    "elapsed_avg_s": elapsed.get("avg"),
                    "elapsed_std_dev_s": elapsed.get("std_dev"),
                    "row_type": "fate",
                }
            )
        for mass in result.get("parsed", {}).get("mass_transfer_rows", []):
            rows.append(
                {
                    "injection": result.get("name"),
                    "diameter_um": result.get("diameter_um"),
                    "fate": mass.get("fate"),
                    "zone": mass.get("zone"),
                    "zone_id": mass.get("zone_id"),
                    "initial_kg_s": mass.get("initial_kg_s"),
                    "final_kg_s": mass.get("final_kg_s"),
                    "change_kg_s": mass.get("change_kg_s"),
                    "row_type": "mass_transfer",
                }
            )
    return rows


def film_flux_rows(film_flux: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    parsed = film_flux.get("parsed", {})
    for zone, value in parsed.get("by_zone_kg_s", {}).items():
        rows.append(
            {
                "domain": film_flux.get("domain"),
                "zone": zone,
                "film_mass_flow_kg_s": value,
                "status": film_flux.get("status"),
            }
        )
    return rows


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-.")
    return cleaned or "injection"


def refresh_dpm_bookkeeping(payload: dict[str, Any]) -> None:
    payload["bookkeeping"]["dpm"] = [
        {"injection": result.get("name"), **result.get("closure", {})}
        for result in payload["dpm"]["results"]
    ]


def write_dpm_progress(output_root: Path, payload: dict[str, Any]) -> None:
    refresh_dpm_bookkeeping(payload)
    results = payload["dpm"]["results"]
    write_json(output_root / "dpm_progress.json", payload["dpm"])
    write_json(output_root / "bookkeeping.partial.json", payload["bookkeeping"])
    write_csv(output_root / "dpm_injection_summary.partial.csv", dpm_summary_rows(results))
    write_csv(output_root / "dpm_zone_summary.partial.csv", dpm_zone_rows(results))


def write_final_outputs(
    output_root: Path,
    payload: dict[str, Any],
    audit: dict[str, Any],
) -> None:
    write_json(
        output_root / "run_manifest.json",
        {
            key: payload.get(key)
            for key in (
                "created_at_utc",
                "mode",
                "fluent_version",
                "case_identity",
                "load",
                "report_prefix",
                "resolved_film_walls",
                "resolved_flux_boundaries",
                "warnings",
            )
        },
    )
    write_json(output_root / "model_audit.json", audit)
    write_json(output_root / "raw_results.json", payload)

    if payload.get("snapshot"):
        write_csv(
            output_root / "final_reports.csv",
            flatten_snapshot_reports(payload["snapshot"]),
        )
    if payload.get("film_flux"):
        write_csv(output_root / "film_flux.csv", film_flux_rows(payload["film_flux"]))
    if payload["dpm"]["results"]:
        results = payload["dpm"]["results"]
        write_csv(output_root / "dpm_injection_summary.csv", dpm_summary_rows(results))
        write_csv(output_root / "dpm_zone_summary.csv", dpm_zone_rows(results))
        transcript_parts: list[str] = []
        for result in results:
            transcript_parts.append(f"===== {result.get('name')} =====")
            transcript_parts.append(str(result.get("raw_output", "")))
        (output_root / "dpm_particle_track_transcript.txt").write_text(
            "\n".join(transcript_parts), encoding="utf-8"
        )
    write_json(output_root / "bookkeeping.json", payload["bookkeeping"])


def main() -> int:
    args = build_parser().parse_args()
    if args.report_frequency < 1:
        raise ValueError("--report-frequency must be at least 1")
    if args.dpm_timeout_seconds <= 0:
        raise ValueError("--dpm-timeout-seconds must be positive")
    if args.transcript_quiet_seconds < 0:
        raise ValueError("--transcript-quiet-seconds cannot be negative")
    if args.load_case_data and not (args.case_file and args.data_file):
        raise ValueError("--load-case-data requires both --case-file and --data-file")

    output_root = Path(args.output_dir).expanduser().resolve() / resolve_run_label(args)
    output_root.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "created_at_utc": iso_now(),
        "mode": args.mode,
        "load_requested": bool(args.load_case_data),
        "report_prefix": args.prefix,
        "report_specs": report_specs_as_dicts(),
        "warnings": [],
        "audit": {},
        "snapshot": {},
        "film_flux": {},
        "dpm": {
            "injections": [],
            "selected": [],
            "results": [],
            "transcript": {
                "capture": "solver.transcript.register_callback",
                "timeout_seconds": args.dpm_timeout_seconds,
                "quiet_seconds": args.transcript_quiet_seconds,
            },
        },
        "bookkeeping": {},
    }

    print_header("Connect")
    solver = connect(server_id=args.server_id)
    payload["fluent_version"] = str(solver.get_fluent_version())
    print(f"Connected to Fluent {payload['fluent_version']}", flush=True)

    if args.load_case_data:
        print_header("Load Explicit Case/Data")
        require_remote_input(solver, args.case_file, "case file")
        require_remote_input(solver, args.data_file, "data file")
        payload["load"] = load_case_data_pair(
            solver,
            case_file=args.case_file,
            data_file=args.data_file,
            load_strategy=args.load_mode,
        )
    else:
        payload["load"] = {"mode": "already-loaded-session"}
    payload["case_identity"] = build_case_identity(payload["load"])
    payload["warnings"].extend(payload["case_identity"].get("warnings", []))

    print_header("Audit EWF/DPM Settings")
    audit = audit_ewf_dpm_settings(solver)
    payload["audit"] = audit
    payload["warnings"].extend(audit.get("warnings", []))
    film_walls, wall_warnings = resolve_film_walls(args, audit)
    payload["warnings"].extend(wall_warnings)
    payload["resolved_film_walls"] = film_walls
    payload["resolved_flux_boundaries"] = resolve_flux_boundaries(args)

    if args.mode in {"snapshot", "all"}:
        if not film_walls:
            raise RuntimeError("Snapshot mode requires at least one resolved --film-wall")
        print_header("Create/Compute EWF Diagnostic Reports")
        snapshot = create_and_compute_snapshot(
            solver,
            surfaces=film_walls,
            prefix=args.prefix,
            object_policy=args.object_policy,
            create_history_files=args.create_history_files,
            frequency=args.report_frequency,
            mechanisms=audit.get("mechanisms", {}),
        )
        payload["snapshot"] = snapshot
        payload["warnings"].extend(snapshot.get("warnings", []))

        print_header("Film Mass Flow Rate")
        film_flux = extract_film_mass_flow(
            solver,
            zones=payload["resolved_flux_boundaries"],
            domain="mixture",
        )
        payload["film_flux"] = film_flux
        payload["bookkeeping"]["ewf"] = build_ewf_bookkeeping_target(
            snapshot, film_flux
        )

    if args.mode in {"dpm", "all"}:
        print_header("Discover Live DPM Injections")
        discovered = discover_live_injections(solver)
        selected = select_injections(
            discovered,
            requested_names=args.injection_names,
            requested_indices=args.injection_indices,
            order=args.order,
        )
        payload["dpm"]["injections"] = discovered
        payload["dpm"]["selected"] = [
            {"index": item["index"], "name": item["name"]} for item in selected
        ]

        live_transcript_path = output_root / "dpm_live_transcript.txt"
        raw_dir = output_root / "dpm_raw"
        with SessionTranscriptCapture(
            solver,
            stream_path=live_transcript_path,
            echo=args.echo_dpm_transcript,
        ) as collector:
            print_header("Configure DPM Summary")
            payload["dpm"]["configuration_commands"] = configure_particle_track_summary(
                solver,
                tui_version=args.tui_version,
            )
            collector.wait_until_quiet(quiet_seconds=0.25, timeout_seconds=5.0)

            print_header("Track DPM Injections")
            for item in selected:
                print(
                    f"Tracking index={item['index']} name={item['name']} "
                    f"diameter_um={item.get('diameter_um')}",
                    flush=True,
                )
                raw_path = raw_dir / (
                    f"{int(item['index']):02d}-{safe_filename(str(item['name']))}.txt"
                )
                result = track_one_injection_streamed(
                    solver,
                    item,
                    collector,
                    timeout_seconds=args.dpm_timeout_seconds,
                    quiet_seconds=args.transcript_quiet_seconds,
                    raw_output_path=raw_path,
                )
                payload["dpm"]["results"].append(result)
                write_dpm_progress(output_root, payload)
                print(
                    f"Completed name={item['name']} status={result['status']} "
                    f"confirmed={result.get('completion', {}).get('confirmed')} "
                    f"counts={result.get('parsed', {}).get('counts')}",
                    flush=True,
                )

                completion = result.get("completion", {})
                if not completion.get("safe_to_submit_next", False):
                    warning = (
                        f"Stopped after {item['name']}: command completion was not confirmed; "
                        "no further TUI command was submitted."
                    )
                    payload["warnings"].append(warning)
                    print(warning, flush=True)
                    break
                if result["status"] != "ok" and not args.keep_going:
                    break

        refresh_dpm_bookkeeping(payload)

    print_header("Write Outputs")
    write_final_outputs(output_root, payload, audit)
    print(f"output_dir: {output_root}", flush=True)

    failed_reports = [
        report
        for report in payload.get("snapshot", {}).get("reports", [])
        if report.get("status") == "failed"
    ]
    failed_dpm = [
        result for result in payload["dpm"]["results"] if result.get("status") != "ok"
    ]
    return 1 if failed_reports or failed_dpm else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)

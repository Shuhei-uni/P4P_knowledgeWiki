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
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
INSPECTION_DIR = PROJECT_ROOT / "scripts" / "inspection"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(INSPECTION_DIR))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import (  # noqa: E402
    build_case_identity,
    calculate_carrier_metrics,
    capture_residual_history,
    capture_session_summary,
    extract_mass_flow_report,
    load_case_data_pair,
    plot_residual_history,
    write_json,
)
from pyansys_fluent.results_evidence import (  # noqa: E402
    render_results_evidence,
    update_results_evidence,
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
    parser.add_argument(
        "--results-md",
        default="",
        help=(
            "Optional Project experiment results.md to receive a bounded, "
            "machine-generated evidence block. Text outside the block is preserved."
        ),
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


def _read_json(path: Path) -> Mapping[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError(f"Expected a JSON object in {path}")
    return payload


def _format_value(value: Any) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _clean_text(value: Any) -> str:
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def _unique_text(values: Sequence[Any]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _clean_text(value)
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _build_flux_record(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    fluxes = payload.get("carrier_fluxes", {})
    metrics = payload.get("carrier_metrics", {})
    session = payload.get("session", {})
    if not isinstance(fluxes, Mapping):
        fluxes = {}
    if not isinstance(metrics, Mapping):
        metrics = {}
    if not isinstance(session, Mapping):
        session = {}

    warnings: list[str] = []
    for source in (
        session.get("warnings", []),
        fluxes.get("warnings", []),
        session.get("phase_domain_map", {}).get("warnings", [])
        if isinstance(session.get("phase_domain_map", {}), Mapping)
        else [],
        session.get("zone_discovery", {}).get("warnings", [])
        if isinstance(session.get("zone_discovery", {}), Mapping)
        else [],
    ):
        if isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
            warnings.extend(source)

    by_domain = fluxes.get("by_domain", {})
    signed_values: list[str] = []
    if isinstance(by_domain, Mapping):
        for domain, zone_values in by_domain.items():
            if not isinstance(zone_values, Mapping):
                continue
            for zone, value in zone_values.items():
                if value is not None:
                    signed_values.append(
                        f"{domain}/{zone}={_format_value(value)} kg/s"
                    )

    metric_specs = (
        ("liquid inlet mass flow", "m_liq_in", "kg/s"),
        ("vapor inlet mass flow", "m_vap_in", "kg/s"),
        ("steam-outlet liquid mass flow", "m_liq_steam_out", "kg/s"),
        ("steam-outlet vapor mass flow", "m_vap_steam_out", "kg/s"),
        ("phase-flux efficiency", "eta_phase", "dimensionless"),
        ("steam-outlet vapor fraction", "x_out", "dimensionless"),
        ("mass imbalance", "mass_imbalance_kg_s", "kg/s"),
        ("mass imbalance ratio", "mass_imbalance_ratio", "dimensionless"),
    )
    measurements = [
        f"{label}={_format_value(metrics.get(key))} {unit}"
        for label, key, unit in metric_specs
    ]
    if signed_values:
        measurements.append("signed Fluent fluxes: " + ", ".join(signed_values))

    zones = fluxes.get("zones", [])
    zone_items = (
        list(zones)
        if isinstance(zones, Sequence) and not isinstance(zones, (str, bytes))
        else []
    )
    domains = list(by_domain) if isinstance(by_domain, Mapping) else []
    zone_text = ", ".join(str(zone) for zone in zone_items) or "unavailable"
    domain_text = ", ".join(str(domain) for domain in domains) or "unavailable"
    available = bool(fluxes.get("available"))
    status = (
        "complete"
        if available and not warnings
        else "partial"
        if available
        else "unavailable"
    )
    missing = _unique_text(warnings)
    if not available:
        missing.insert(0, "The live mass-flow report did not return usable domain data.")

    notes = [
        "The by-domain values retain Fluent's signed zone orientation; carrier metrics above use absolute mass-flow magnitudes.",
    ]
    if metrics.get("mass_balance_scope"):
        notes.append(
            f"Mass-balance scope recorded by the extractor: {metrics.get('mass_balance_scope')}; {metrics.get('scope_reason', 'scope reason unavailable')}."
        )
    if metrics.get("mass_imbalance_note"):
        notes.append(f"Mass-balance note: {metrics.get('mass_imbalance_note')}")

    return {
        "name": "flux",
        "status": status,
        "scope": f"zones {zone_text}; domains {domain_text}",
        "coordinate": "single live snapshot; Fluent iteration/time unavailable",
        "horizon": "single live snapshot; no iteration/time window",
        "measurements": measurements,
        "artifacts": [path],
        "notes": notes,
        "numerical_state": (
            "Instantaneous signed mass-flow evidence was captured; no iteration or physical-time history was available for a stability assessment."
        ),
        "missing": missing,
        "observations": [
            f"The captured report scope contains {len(zone_items)} zone(s) and {len(domains)} domain(s).",
            "Derived metrics and signed source values are reported separately; no ranking or acceptance decision is made.",
        ],
    }


def _build_residual_record(
    json_path: Path,
    plot_path: Path,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    iterations = payload.get("iterations", [])
    series = payload.get("series", {})
    if not isinstance(iterations, Sequence) or isinstance(iterations, (str, bytes)):
        iterations = []
    if not isinstance(series, Mapping):
        series = {}

    point_count = len(iterations)
    first = iterations[0] if iterations else None
    last = iterations[-1] if iterations else None
    aligned_series = bool(series) and all(
        isinstance(values, Sequence)
        and not isinstance(values, (str, bytes))
        and len(values) == point_count
        for values in series.values()
    )
    valid = bool(iterations) and aligned_series
    measurements = [
        f"{point_count} monitor point(s)",
        "series: " + (", ".join(str(name) for name in series) or "unavailable"),
    ]
    for name, values in series.items():
        if isinstance(values, Sequence) and not isinstance(values, (str, bytes)) and values:
            measurements.append(
                f"last {name}={_format_value(values[-1])} scaled residual"
            )

    artifacts = [json_path]
    missing: list[str] = []
    if not valid:
        if iterations and series and not aligned_series:
            missing.append("Residual series lengths do not match the native iteration coordinate.")
        else:
            missing.append("The residual monitor did not provide a non-empty iteration/series history.")
    if not plot_path.exists():
        missing.append("The residual plot artifact was not written.")
    if plot_path.exists():
        artifacts.append(plot_path)

    status = (
        "complete"
        if valid and plot_path.exists()
        else "partial"
        if (iterations or series)
        else "unavailable"
    )

    return {
        "name": "residual",
        "status": status,
        "scope": f"monitor set {payload.get('monitor_set', 'unavailable')}",
        "coordinate": "Fluent monitor iteration",
        "horizon": f"iterations {_format_value(first)} → {_format_value(last)}" if valid else "unavailable",
        "measurements": measurements,
        "artifacts": artifacts,
        "notes": [
            "The x-axis is the native Fluent monitor iteration; no physical-time conversion or gap interpolation was applied.",
        ],
        "numerical_state": (
            "Scaled residual values are reported over the captured monitor window; this packet does not turn the endpoint into a convergence verdict."
        ),
        "missing": missing,
        "observations": [
            f"Captured {point_count} monitor point(s) on the native iteration coordinate.",
            "The named residual series and their final captured values are evidence, not an automatic solver-quality decision.",
        ],
    }


def _build_dpm_record(
    payload: Mapping[str, Any],
    artifacts: Sequence[Path],
    *,
    inspect_only: bool,
) -> dict[str, Any]:
    raw_discovered = payload.get("injections", [])
    selected = payload.get("selected_injections", [])
    results = payload.get("results", [])
    discovery_available = isinstance(raw_discovered, Sequence) and not isinstance(
        raw_discovered, (str, bytes)
    )
    discovered = list(raw_discovered) if discovery_available else []
    if not isinstance(selected, Sequence) or isinstance(selected, (str, bytes)):
        selected = []
    if not isinstance(results, Sequence) or isinstance(results, (str, bytes)):
        results = []

    result_statuses = [
        str(item.get("status", "unavailable")).lower()
        for item in results
        if isinstance(item, Mapping)
    ]
    if inspect_only:
        status = "complete" if discovery_available else "unavailable"
    elif result_statuses and all(value == "ok" for value in result_statuses):
        status = "complete"
    elif any(value == "ok" for value in result_statuses):
        status = "partial"
    elif result_statuses:
        status = "failed"
    else:
        status = "partial" if selected else "unavailable"

    selected_names = []
    for item in selected:
        if isinstance(item, Mapping):
            selected_names.append(str(item.get("name", "unnamed")))
    measurements = [
        f"{len(discovered)} live injection(s) discovered",
        "selected injections: " + (", ".join(selected_names) or "none"),
    ]
    missing: list[str] = []
    observations = [
        f"The report inventory contains {len(discovered)} live injection(s); {len(selected_names)} were selected.",
    ]
    for item in results:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("name", "unnamed"))
        item_status = str(item.get("status", "unavailable"))
        counts = item.get("counts", {})
        if not isinstance(counts, Mapping):
            counts = {}
        measurements.append(
            f"{name}: status={item_status}, tracked={_format_value(counts.get('tracked'))}, "
            f"escaped={_format_value(counts.get('escaped'))}, "
            f"trapped={_format_value(counts.get('trapped'))}, "
            f"incomplete={_format_value(counts.get('incomplete'))}"
        )
        observations.append(f"{name} returned extraction status {item_status}.")
        if item_status != "ok":
            detail = item.get("failure_category") or item.get("error") or "no failure detail"
            missing.append(f"{name}: {item_status}; {_clean_text(detail)}")

    if not inspect_only and not result_statuses:
        missing.append("No particle-track result was returned for the selected injections.")

    return {
        "name": "dpm",
        "status": status,
        "scope": "selected live injections; report boundaries as configured by the DPM check",
        "coordinate": "particle-track report; Fluent iteration/time unavailable",
        "horizon": "particle-track report; no iteration/time window",
        "measurements": measurements,
        "artifacts": list(artifacts),
        "notes": [
            "Particle counts describe the selected injection/report scope and are not full validated fate accounting.",
            "Raw transcript artifacts, when requested, remain debug evidence and are not copied into results.md.",
        ],
        "numerical_state": (
            "DPM inventory/track status and counts were captured without a solver iteration or physical-time history; no numerical convergence decision is made."
        ),
        "missing": missing,
        "observations": observations,
    }


def _failed_record(check: str, exc: Exception) -> dict[str, Any]:
    detail = f"{type(exc).__name__}: {_clean_text(exc)}"
    return {
        "name": check,
        "status": "failed",
        "scope": "selected check did not complete",
        "coordinate": "unavailable",
        "horizon": "unavailable",
        "measurements": [],
        "artifacts": [],
        "notes": [f"The check raised {detail}.", "No raw exception transcript was copied into results.md."],
        "numerical_state": "No numerical evidence was produced by this check.",
        "missing": [detail],
        "observations": [],
    }


def main() -> int:
    args = build_parser().parse_args()
    checks = selected_checks(args.checks)
    run_label = derive_run_label(args)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print_header("Connect")
    solver = connect(server_id=args.server_id)
    fluent_version = solver.get_fluent_version()
    print(f"Connected to {fluent_version}", flush=True)
    load_summary = load_if_requested(solver, args)

    failures: list[str] = []
    evidence_records: list[dict[str, Any]] = []
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
                evidence_records.append(_build_flux_record(path, _read_json(path)))
            elif check == "residual":
                json_path, plot_path = run_residual_check(
                    solver,
                    args=args,
                    run_label=run_label,
                    output_dir=output_dir,
                )
                print(f"residual_json: {json_path}", flush=True)
                print(f"residual_plot: {plot_path}", flush=True)
                evidence_records.append(
                    _build_residual_record(json_path, plot_path, _read_json(json_path))
                )
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
                dpm_artifacts = [report_path]
                if args.dpm_detailed_output:
                    json_path, csv_path, transcript_path = write_dpm_outputs(
                        output_dir,
                        f"{run_label}-dpm",
                        payload,
                    )
                    print(f"dpm_json: {json_path}", flush=True)
                    print(f"dpm_csv: {csv_path}", flush=True)
                    print(f"dpm_transcript: {transcript_path}", flush=True)
                    dpm_artifacts.extend([json_path, csv_path, transcript_path])
                evidence_records.append(
                    _build_dpm_record(
                        payload,
                        dpm_artifacts,
                        inspect_only=args.dpm_inspect_only,
                    )
                )
                if not args.dpm_inspect_only and any(
                    item.get("status") != "ok" for item in payload.get("results", [])
                ):
                    failures.append("dpm")
        except Exception as exc:
            failures.append(check)
            evidence_records.append(_failed_record(check, exc))
            print(f"{check} check failed: {type(exc).__name__}: {exc}", file=sys.stderr)

    if args.results_md.strip():
        results_path = Path(args.results_md).expanduser().resolve()
        try:
            generated_block = render_results_evidence(
                results_path=results_path,
                run_label=run_label,
                load_summary=load_summary,
                case_identity=build_case_identity(load_summary),
                fluent_version=fluent_version,
                records=evidence_records,
            )
            update_results_evidence(results_path, generated_block)
            print(f"results_md: {results_path}", flush=True)
        except Exception as exc:
            failures.append("results-md")
            print(
                f"results.md evidence handoff failed: {type(exc).__name__}: {exc}",
                file=sys.stderr,
            )

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

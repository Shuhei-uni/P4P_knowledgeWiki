#!/usr/bin/env python3
"""Read only the completed 03A Stage-3 fixed-3,000 endpoint pairs.

This reconnecting post-processing helper loads each explicitly named case/data
pair, queries phase-resolved boundary mass flows, and saves one JSON record per
checkpoint.  It does not iterate, alter solver settings, or create Fluent
report definitions.
"""

from __future__ import annotations

import argparse
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.ewf_reports import compute_report_definition  # noqa: E402
from pyansys_fluent.postprocess_live import (  # noqa: E402
    calculate_carrier_metrics,
    capture_session_summary,
    extract_mass_flow_report,
    load_case_data_pair,
    write_json,
)


RUN_STAMP = "20260820T013223Z"
REMOTE_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3"
CHECKPOINTS = (
    ("F05", "full-mixture-100pct-end"),
    ("F06", "full-mixture-100pct-end"),
    ("F11", "full-mixture-10pct-end"),
    ("F11", "full-mixture-20pct-end"),
    ("F11", "full-mixture-40pct-end"),
    ("F11", "full-mixture-80pct-end"),
    ("F11", "full-mixture-100pct-end"),
)
SCALAR_REPORTS = (
    "03a_stage3_inventory_y010_liquid_volume",
    "03a_stage3_inventory_y010_liquid_mass",
    "03a_stage3_inventory_y030_liquid_volume",
    "03a_stage3_inventory_y030_liquid_mass",
    "03a_stage3_inventory_total_liquid_volume",
    "03a_stage3_inventory_total_liquid_mass",
    "03a_stage3_brine_entry_static_pressure",
    "03a_stage3_brine_entry_total_pressure",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="2", help="Connection routing only.")
    parser.add_argument("--run-stamp", default=RUN_STAMP)
    parser.add_argument("--remote-root", default=REMOTE_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT
        / "output"
        / "03A-stage3"
        / "override-fixed3000-native-server2"
        / RUN_STAMP
        / "post_simulation_analysis",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="BRANCH:STAGE",
        help="Optional repeatable filter, for example F11:full-mixture-40pct-end.",
    )
    parser.add_argument(
        "--residual-only",
        action="store_true",
        help="Load each pair and inspect only its retained residual monitor history.",
    )
    return parser.parse_args()


def selected_checkpoints(filters: list[str]) -> tuple[tuple[str, str], ...]:
    if not filters:
        return CHECKPOINTS
    requested = {item.strip() for item in filters}
    selected = tuple(
        item for item in CHECKPOINTS if f"{item[0]}:{item[1]}" in requested
    )
    unknown = requested - {f"{branch}:{stage}" for branch, stage in selected}
    if unknown:
        raise ValueError(f"Unknown or unsupported completed checkpoint filter(s): {sorted(unknown)}")
    return selected


def checkpoint_paths(
    *, branch: str, stage: str, remote_root: str, run_stamp: str
) -> tuple[str, str, str]:
    root = PureWindowsPath(remote_root) / branch / f"run-{run_stamp}"
    stem = f"03A-stage3-{branch}-{stage}-{run_stamp}"
    return stem, str(root / f"{stem}.cas.h5"), str(root / f"{stem}.dat.h5")


def saved_residual_history(solver: Any) -> dict[str, Any]:
    """Read the residual monitor retained in the loaded data file, if present."""
    try:
        names = [str(name) for name in solver.monitors.get_monitor_set_names()]
    except Exception as exc:
        return {"available": False, "warnings": [f"monitor enumeration failed: {type(exc).__name__}: {exc}"]}
    if "residual" not in names:
        return {"available": False, "monitor_sets": names, "warnings": ["residual monitor is absent from this checkpoint."]}
    try:
        iterations, series = solver.monitors.get_monitor_set_data("residual")
    except Exception as exc:
        return {"available": False, "monitor_sets": names, "warnings": [f"residual monitor read failed: {type(exc).__name__}: {exc}"]}
    return {
        "available": bool(iterations),
        "monitor_set": "residual",
        "iterations": list(iterations),
        "series": {str(name): list(values) for name, values in series.items()},
        "point_count": len(iterations),
        "warnings": [],
    }


def extract_one(solver: Any, *, branch: str, stage: str, args: argparse.Namespace) -> dict[str, Any]:
    stem, case_file, data_file = checkpoint_paths(
        branch=branch,
        stage=stage,
        remote_root=args.remote_root,
        run_stamp=args.run_stamp,
    )
    load = load_case_data_pair(
        solver, case_file=case_file, data_file=data_file, load_strategy="paired"
    )
    session = capture_session_summary(solver)
    zone_discovery = session["zone_discovery"]
    roles = zone_discovery["roles"]
    zones = list(
        dict.fromkeys(
            value
            for value in (
                roles.get("liquid_inlet"),
                roles.get("steam_inlet"),
                *zone_discovery.get("all_outlets", []),
            )
            if value
        )
    )
    phase_map = session["phase_domain_map"]
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
    scalar_reports = {
        name: compute_report_definition(solver, name) for name in SCALAR_REPORTS
    }
    residual_history = saved_residual_history(solver)
    return {
        "branch": branch,
        "checkpoint": stem,
        "case_data_identity": load,
        "phase_domain_map": phase_map,
        "zone_discovery": zone_discovery,
        "carrier_fluxes": fluxes,
        "carrier_metrics": metrics,
        "existing_scalar_reports": scalar_reports,
        "residual_history": residual_history,
        "readback_scope": (
            "explicit paired case/data load; read-only flux reporting; "
            "existing scalar report definitions recomputed; no iterations or new report definitions created"
        ),
    }


def extract_residual_only(solver: Any, *, branch: str, stage: str, args: argparse.Namespace) -> dict[str, Any]:
    stem, case_file, data_file = checkpoint_paths(
        branch=branch,
        stage=stage,
        remote_root=args.remote_root,
        run_stamp=args.run_stamp,
    )
    return {
        "branch": branch,
        "checkpoint": stem,
        "case_data_identity": load_case_data_pair(
            solver, case_file=case_file, data_file=data_file, load_strategy="paired"
        ),
        "residual_history": saved_residual_history(solver),
        "readback_scope": "explicit paired case/data load; residual-monitor inspection only; no iterations or report definitions created",
    }


def main() -> int:
    args = parse_args()
    args.output_dir = args.output_dir.expanduser().resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    solver = connect(server_id=args.server_id, start_transcript=False)
    summary: list[dict[str, Any]] = []
    for branch, stage in selected_checkpoints(args.only):
        record = (
            extract_residual_only(solver, branch=branch, stage=stage, args=args)
            if args.residual_only
            else extract_one(solver, branch=branch, stage=stage, args=args)
        )
        suffix = "residual-probe" if args.residual_only else "readback"
        output = args.output_dir / f"{branch}-{stage}-{suffix}.json"
        write_json(output, record)
        summary.append({"branch": branch, "stage": stage, "output": str(output)})
        print(f"Verified readback: {branch} {stage}", flush=True)
    write_json(args.output_dir / "endpoint-readback-index.json", {"checkpoints": summary})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

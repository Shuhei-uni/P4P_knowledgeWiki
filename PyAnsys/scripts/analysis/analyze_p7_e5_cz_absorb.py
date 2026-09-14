#!/usr/bin/env python3
"""Plot-led evidence extraction for the Phase-07 E5-CZ-ABSORB family.

The absorber is a numerical liquid-only sink in the lower cell zone.  This
analyzer keeps the controller readbacks, local liquid inventories, phase
routing, and solver residuals separate so a completed iteration horizon is not
mistaken for a numerically qualified flow solution.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_records(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    raw = payload.get("reports", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw, dict):
        raise ValueError(f"unexpected reports payload in {path}")
    records: dict[str, dict[str, Any]] = {}
    for key, record in raw.items():
        label = str(record.get("report_definition") or key).removesuffix("-rfile")
        records[label] = record
    return records


def values(records: dict[str, dict[str, Any]], name: str, field: str = "values") -> np.ndarray:
    if name not in records:
        raise KeyError(f"missing report {name}")
    return np.asarray(records[name][field], dtype=float)


def parse_residuals(text: str) -> dict[str, Any]:
    header_re = re.compile(r"^\s*iter\s+(.+?)\s+time/iter\s*$", re.I)
    number_re = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
    columns: list[str] | None = None
    iterations: list[int] = []
    series: dict[str, list[float]] = {}
    for line in text.splitlines():
        header = header_re.match(line)
        if header:
            next_columns = header.group(1).split()
            if columns is None:
                columns = next_columns
                series = {name: [] for name in columns}
            continue
        if columns is None:
            continue
        tokens = line.split()
        if (
            len(tokens) < len(columns) + 1
            or not tokens[0].isdigit()
            or not all(number_re.match(value) for value in tokens[1 : len(columns) + 1])
        ):
            continue
        iteration = int(tokens[0])
        if iterations and iteration == iterations[-1]:
            continue
        if iterations and iteration < iterations[-1]:
            continue
        iterations.append(iteration)
        for name, raw in zip(columns, tokens[1 : len(columns) + 1]):
            series[name].append(float(raw))
    if not iterations:
        raise RuntimeError("no residual rows captured")
    return {
        "iterations": iterations,
        "series": series,
        "point_count": len(iterations),
        "curve_count": len(series),
        "source": "PyFluent transcript callback",
    }


def load_residuals(json_path: Path, transcript_path: Path) -> dict[str, Any]:
    if json_path.exists():
        return load_json(json_path)
    return parse_residuals(transcript_path.read_text(encoding="utf-8", errors="replace"))


def late_stats(x: np.ndarray, y: np.ndarray, count: int = 100) -> dict[str, Any]:
    yy = y[-min(count, len(y)) :]
    xx = x[-len(yy) :]
    slope, _ = np.polyfit(xx, yy, 1) if len(yy) >= 2 else (float("nan"), float("nan"))
    return {
        "points": int(len(yy)),
        "window": [float(xx[0]), float(xx[-1])] if len(xx) else [],
        "start": float(yy[0]) if len(yy) else None,
        "end": float(yy[-1]) if len(yy) else None,
        "minimum": float(np.min(yy)) if len(yy) else None,
        "maximum": float(np.max(yy)) if len(yy) else None,
        "mean": float(np.mean(yy)) if len(yy) else None,
        "range": float(np.ptp(yy)) if len(yy) else None,
        "slope_per_native_iteration": float(slope),
    }


def controller_events(manifest: dict[str, Any], native_start: float) -> list[dict[str, Any]]:
    events = [e for e in manifest.get("events", []) if e.get("event") == "controller_update"]
    out = []
    for event in events:
        item = dict(event)
        item["native_iteration_plot"] = float(event.get("native_iteration") or native_start)
        out.append(item)
    return out


def routing(records: dict[str, dict[str, Any]]) -> dict[str, np.ndarray]:
    def raw(phase: str, surface: str) -> np.ndarray:
        return values(records, f"e0-flux-{phase}-{surface}")

    phase2_in = raw("phase2", "liquidinlet") + raw("phase2", "steaminlet")
    phase2_out = -(raw("phase2", "steamoutlet") + raw("phase2", "bottom"))
    phase1_in = raw("phase1", "liquidinlet") + raw("phase1", "steaminlet")
    phase1_out = -(raw("phase1", "steamoutlet") + raw("phase1", "bottom"))
    mixture_in = raw("mixture", "liquidinlet") + raw("mixture", "steaminlet")
    mixture_out = -(raw("mixture", "steamoutlet") + raw("mixture", "bottom"))
    return {
        "phase2_in": phase2_in,
        "phase2_out": phase2_out,
        "phase2_net": phase2_in - phase2_out,
        "phase1_in": phase1_in,
        "phase1_out": phase1_out,
        "phase1_net": phase1_in - phase1_out,
        "mixture_in": mixture_in,
        "mixture_out": mixture_out,
        "mixture_net": mixture_in - mixture_out,
        "bottom_phase1_raw": raw("phase1", "bottom"),
        "bottom_phase2_raw": raw("phase2", "bottom"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--reports", required=True, type=Path)
    parser.add_argument("--residuals", required=True, type=Path)
    parser.add_argument("--residual-transcript", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_json(args.manifest)
    records = load_records(args.reports)
    x = values(records, "e0-liquid-mass-total", "iterations")
    total = values(records, "e0-liquid-mass-total")
    lower = values(records, "absorb-lower-liquid-mass")
    adjacent = values(records, "absorb-adjacent-liquid-mass")
    broad = values(records, "absorb-broad-liquid-mass")
    lower_volume = values(records, "absorb-lower-liquid-volume")
    residuals = load_residuals(args.residuals, args.residual_transcript)
    rx = np.asarray(residuals["iterations"], dtype=float)
    route = routing(records)
    events = controller_events(manifest, float(x[0]))
    target = float(manifest.get("M_L_target_kg", float("nan")))
    cap = float(manifest.get("source_cap_kg_s", float("nan")))

    # F1: total, lower, adjacent, and broad inventories show whether the sink
    # affects only the intended lower zone or changes the wider inventory.
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, constrained_layout=True)
    axes[0].plot(x, total, color="#1d4ed8", lw=1.1, label="total liquid mass")
    axes[0].set_ylabel("Total liquid [kg]")
    axes[0].grid(alpha=0.25)
    axes[0].legend(fontsize=8)
    axes[1].plot(x, lower, color="#dc2626", lw=1.1, label="lower y≤0.10 m")
    axes[1].plot(x, adjacent, color="#d97706", lw=1.0, label="adjacent y=0.10–0.30 m")
    axes[1].plot(x, broad, color="#7c3aed", lw=1.0, label="broad y≤0.50 m")
    if np.isfinite(target):
        axes[1].axhline(target, color="#334155", ls="--", lw=0.9, label="controller target")
    axes[1].set(xlabel="Native solver iteration", ylabel="Zone liquid [kg]")
    axes[1].grid(alpha=0.25)
    axes[1].legend(fontsize=8, ncol=2)
    fig.suptitle(f"{manifest.get('setup_id', args.manifest.stem)} F1 — liquid inventory and spatial selectivity")
    f1 = args.output_dir / "F1-liquid-inventory-and-selectivity.png"
    fig.savefig(f1, dpi=190)
    plt.close(fig)

    # F2: controller command, target error, and saturation.  Native solver
    # coordinates are used for the event markers; active iteration remains in
    # the summary as the lifecycle coordinate.
    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, constrained_layout=True)
    if events:
        ex = np.asarray([e["native_iteration_plot"] for e in events])
        em = np.asarray([e.get("M_L_kg", np.nan) for e in events])
        ec = np.asarray([e.get("clamped_command_kg_s", np.nan) for e in events])
        ee = np.asarray([e.get("normalized_error", np.nan) for e in events])
        sat = np.asarray([bool(e.get("saturated")) for e in events])
        axes[0].plot(ex, em, "o-", color="#dc2626", label="lower liquid mass")
        axes[0].axhline(target, color="#334155", ls="--", label="target")
        axes[0].set_ylabel("Lower liquid [kg]")
        axes[0].legend(fontsize=8)
        axes[1].plot(ex, ec, "o-", color="#2563eb", label="command [kg/s]")
        if np.isfinite(cap):
            axes[1].axhline(cap, color="#dc2626", ls="--", label="cap")
        axes[1].plot(ex, ee, "s-", color="#7c3aed", label="normalized error")
        if np.any(sat):
            axes[1].scatter(ex[sat], ec[sat], color="#f59e0b", zorder=4, label="saturated update")
    axes[1].set(xlabel="Native solver iteration", ylabel="Command / error")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8)
    fig.suptitle(f"{manifest.get('setup_id', args.manifest.stem)} F2 — lower-zone absorber controller")
    f2 = args.output_dir / "F2-controller-command-and-saturation.png"
    fig.savefig(f2, dpi=190)
    plt.close(fig)

    # F3: phase routing and numerical adequacy.  The phase-2 bottom flux is
    # kept explicit because bottom phase loss is a distinct possible failure
    # mode from volumetric absorption.
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True, constrained_layout=True)
    axes[0, 0].plot(x, route["phase2_in"], label="phase-2 inflow")
    axes[0, 0].plot(x, route["phase2_out"], label="phase-2 outflow")
    axes[0, 0].plot(x, route["phase2_net"], label="phase-2 net")
    axes[0, 0].set_title("Liquid-phase routing", loc="left")
    axes[0, 0].set_ylabel("kg/s")
    axes[0, 1].plot(x, route["phase1_in"], label="phase-1 inflow")
    axes[0, 1].plot(x, route["phase1_out"], label="phase-1 outflow")
    axes[0, 1].plot(x, route["phase1_net"], label="phase-1 net")
    axes[0, 1].set_title("Vapor-phase routing", loc="left")
    axes[1, 0].plot(x, route["mixture_net"], color="#7c3aed", label="mixture net")
    axes[1, 0].plot(x, route["bottom_phase2_raw"], color="#dc2626", label="raw bottom phase-2")
    axes[1, 0].plot(x, route["bottom_phase1_raw"], color="#d97706", label="raw bottom phase-1")
    axes[1, 0].set_title("Closure and bottom-phase routing", loc="left")
    axes[1, 0].set_ylabel("kg/s")
    for ax in axes[0, :].tolist() + [axes[1, 0]]:
        ax.grid(alpha=0.2)
        ax.legend(fontsize=7)
    for name, series in residuals["series"].items():
        axes[1, 1].semilogy(rx, np.asarray(series, dtype=float), lw=0.75, label=name)
    axes[1, 1].set_title("Residual histories", loc="left")
    axes[1, 1].set_xlabel("Native solver iteration")
    axes[1, 1].set_ylabel("Scaled residual")
    axes[1, 1].grid(alpha=0.2, which="both")
    axes[1, 1].legend(fontsize=7, ncol=2)
    fig.suptitle(f"{manifest.get('setup_id', args.manifest.stem)} F3 — phase routing and numerical adequacy")
    f3 = args.output_dir / "F3-phase-routing-and-numerical-adequacy.png"
    fig.savefig(f3, dpi=190)
    plt.close(fig)

    late_count = min(100, len(x))
    residual_late = {
        name: late_stats(rx, np.asarray(series, dtype=float), min(100, len(rx)))
        for name, series in residuals["series"].items()
    }
    source_errors = [
        float(e.get("source_audit", {}).get("absolute_error_kg_s", np.nan))
        for e in events
        if isinstance(e.get("source_audit"), dict)
    ]
    active_values = [int(e["active_iteration"]) for e in events if e.get("active_iteration") is not None]
    summary = {
        "setup_id": manifest.get("setup_id"),
        "run_id": manifest.get("run_id"),
        "manifest_status": manifest.get("status"),
        "error": manifest.get("error"),
        "requested_active_iterations": manifest.get("requested_active_iterations"),
        "achieved_controller_horizon_active_iterations": max(active_values, default=0),
        "native_report_extent": [int(x[0]), int(x[-1])],
        "report_count": len(records),
        "report_points_each": sorted({int(r.get("points", 0)) for r in records.values()}),
        "residual_points": int(residuals["point_count"]),
        "target_M_L_kg": target,
        "source_cap_kg_s": cap,
        "inventory": {
            "total_liquid_mass": late_stats(x, total, late_count),
            "lower_liquid_mass": late_stats(x, lower, late_count),
            "adjacent_liquid_mass": late_stats(x, adjacent, late_count),
            "broad_liquid_mass": late_stats(x, broad, late_count),
            "lower_liquid_volume": late_stats(x, lower_volume, late_count),
        },
        "controller": {
            "updates": len(events),
            "saturated_updates": int(sum(bool(e.get("saturated")) for e in events)),
            "max_command_kg_s": float(max((e.get("clamped_command_kg_s", 0.0) for e in events), default=0.0)),
            "source_audit_max_abs_error_kg_s": float(max(source_errors, default=float("nan"))),
            "direct_phase1_source_off_all_updates": bool(all(e.get("direct_phase1_source_off") for e in events)),
        },
        "routing_late": {name: late_stats(x, series, late_count) for name, series in route.items()},
        "residuals_late": residual_late,
        "figures": {"F1": str(f1), "F2": str(f2), "F3": str(f3)},
        "claim_limits": [
            "This is a numerical discovery result, not a physically qualified separator prediction.",
            "A completed horizon does not imply converged flow when residuals or closure are poor.",
            "Volumetric phase-2 source audit does not by itself prove that the absorber represents a real brine pool.",
        ],
    }
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Create matched-window evidence plots and summary tables for Phase 7.2A Family R."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import re
import statistics
from typing import Any

import matplotlib.pyplot as plt


CASES = ("R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7")
ROUGHNESS = {"R0": 0.0, "R1": 5e-5, "R2": 2e-4, "R3": 5e-4, "R4": 1e-3, "R5": 2e-3, "R6": 4e-3, "R7": 8e-3}
COLORS = {"R0": "#333333", "R1": "#0072B2", "R2": "#E69F00", "R3": "#D55E00", "R4": "#009E73", "R5": "#CC79A7", "R6": "#56B4E9", "R7": "#A6761D"}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def series(histories: dict[str, Any], name: str) -> tuple[list[int], list[float]]:
    record = histories[name]
    iterations = [int(value) for value in record["iterations"]]
    values = [float(value) for value in record["values"]]
    if len(iterations) != 3001 or len(values) != 3001:
        raise RuntimeError(f"{name}: expected 3001 matched points, got {len(iterations)}/{len(values)}")
    offsets = [value - iterations[0] for value in iterations]
    if offsets != list(range(3001)):
        raise RuntimeError(f"{name}: native iteration coordinate is not contiguous 0..3000")
    return offsets, values


def stats(values: list[float], tail: int = 500) -> dict[str, float]:
    finite = [value for value in values if math.isfinite(value)]
    window = finite[-tail:]
    slope = (window[-1] - window[0]) / (len(window) - 1)
    return {
        "final": finite[-1],
        f"mean_last_{tail}": statistics.fmean(window),
        f"stdev_last_{tail}": statistics.stdev(window),
        f"slope_last_{tail}_per_iteration": slope,
        "minimum": min(finite),
        "maximum": max(finite),
    }


def residuals(path: Path) -> dict[str, list[float]]:
    columns = {name: [] for name in ("offset", "continuity", "x-velocity", "y-velocity", "z-velocity", "k", "epsilon", "vf-phase-2")}
    pattern = re.compile(
        r"^\s*(\d+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+"
        r"([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)"
    )
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        iteration = int(match.group(1))
        if iteration < 5586 or iteration > 8586:
            continue
        columns["offset"].append(iteration - 5586)
        for name, value in zip(tuple(columns)[1:], match.groups()[1:]):
            columns[name].append(float(value))
    if len(columns["offset"]) != 3001:
        raise RuntimeError(f"{path}: expected 3001 residual rows, got {len(columns['offset'])}")
    return columns


def finish_figure(fig: Any, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r0-root", type=Path, required=True)
    parser.add_argument("--r123-root", type=Path, required=True)
    parser.add_argument("--r45-root", type=Path, required=True)
    parser.add_argument("--r67-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    roots = {
        "R0": args.r0_root / "R0",
        **{case: args.r123_root / case for case in ("R1", "R2", "R3")},
        **{case: args.r45_root / case for case in ("R4", "R5")},
        **{case: args.r67_root / case for case in ("R6", "R7")},
    }
    manifests = {case: load(root / "run-manifest.json") for case, root in roots.items()}
    histories = {case: load(root / "report-histories.json") for case, root in roots.items()}
    for case in CASES:
        manifest = manifests[case]
        if manifest.get("status") != "COMPLETE" or manifest.get("terminal_native_iteration_before_save") != 8586:
            raise RuntimeError(f"{case}: incomplete or wrong terminal coordinate")
        if any(manifest["native_solve_event_flags"].get(key) for key in ("amg", "fpe", "nonfinite", "fatal")):
            raise RuntimeError(f"{case}: fatal solver-health event in manifest")

    metrics: dict[str, Any] = {"matched_window": {"parent_iteration": 5586, "terminal_iteration": 8586, "points": 3001}, "cases": {}}
    report_names = (
        "v2-flux-phase2-steamoutlet",
        "v2-flux-phase1-steamoutlet",
        "v2-flux-mixture-steamoutlet",
        "v2-flux-phase2-liquidinlet",
        "v2-flux-phase1-steaminlet",
        "v2-total-liquid-mass",
        "v2-lower-liquid-mass",
        "v2-applied-absorber",
        "v2-command",
        "v2-command-error",
        "family-r-outer-wall-liquid-y-velocity",
    )
    for case in CASES:
        metrics["cases"][case] = {
            "roughness_height_m": ROUGHNESS[case],
            "roughness_constant": 0.5,
            "reports": {name: stats(series(histories[case], name)[1]) for name in report_names},
            "closure_summary": manifests[case]["closure_summary"],
            "solver_events": manifests[case]["native_solve_event_flags"],
            "final_hashes": manifests[case]["final_hashes"],
        }
    baseline = metrics["cases"]["R0"]["reports"]["v2-flux-phase2-steamoutlet"]["mean_last_500"]
    for case in CASES:
        value = metrics["cases"][case]["reports"]["v2-flux-phase2-steamoutlet"]["mean_last_500"]
        metrics["cases"][case]["phase2_outlet_tail500_delta_from_R0_kg_s"] = value - baseline
        metrics["cases"][case]["phase2_outlet_tail500_magnitude_change_from_R0_percent"] = (abs(value) / abs(baseline) - 1.0) * 100.0
    dump(args.output / "metrics.json", metrics)

    with (args.output / "tail-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("case", "k_s_m", "phase2_outlet_mean_last_500_kg_s", "magnitude_change_from_R0_percent", "wall_y_velocity_mean_last_500_m_s", "total_liquid_mass_slope_last_500_kg_per_iter"))
        for case in CASES:
            reports = metrics["cases"][case]["reports"]
            writer.writerow((case, ROUGHNESS[case], reports["v2-flux-phase2-steamoutlet"]["mean_last_500"], metrics["cases"][case]["phase2_outlet_tail500_magnitude_change_from_R0_percent"], reports["family-r-outer-wall-liquid-y-velocity"]["mean_last_500"], reports["v2-total-liquid-mass"]["slope_last_500_per_iteration"]))

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    for case in CASES:
        x, y = series(histories[case], "v2-flux-phase2-steamoutlet")
        ax.plot(x, y, color=COLORS[case], lw=1.1, label=f"{case}: $k_s$={ROUGHNESS[case]:g} m")
    ax.axvspan(2501, 3000, color="#999999", alpha=0.12, label="tail-500 statistic")
    ax.set(xlabel="Child native iteration offset", ylabel="Phase-2 steamoutlet mass flux (kg/s)", title="Family R liquid carryover response (Fluent sign retained)")
    ax.grid(alpha=0.25); ax.legend(ncol=3, fontsize=8)
    finish_figure(fig, args.output / "01-phase2-steamoutlet-carryover.png")

    fig, axes = plt.subplots(2, 1, figsize=(8.2, 7.0), sharex=True)
    for case in CASES:
        for ax, name in zip(axes, ("v2-total-liquid-mass", "v2-lower-liquid-mass")):
            x, y = series(histories[case], name); ax.plot(x, y, color=COLORS[case], lw=1.0, label=case)
    axes[0].set_ylabel("Total liquid mass (kg)"); axes[1].set_ylabel("Lower-zone liquid mass (kg)")
    axes[1].set_xlabel("Child native iteration offset")
    for ax in axes: ax.grid(alpha=0.25); ax.legend(ncol=8, fontsize=8)
    fig.suptitle("Family R liquid inventories")
    finish_figure(fig, args.output / "02-liquid-inventories.png")

    fig, axes = plt.subplots(2, 1, figsize=(8.2, 7.0), sharex=True)
    for case in CASES:
        x, y = series(histories[case], "family-r-outer-wall-liquid-y-velocity")
        axes[0].plot(x, y, color=COLORS[case], lw=1.0, label=case)
        x, y = series(histories[case], "v2-command-error")
        axes[1].plot(x, y, color=COLORS[case], lw=1.0, label=case)
    axes[0].axhline(0, color="black", lw=0.7); axes[0].set_ylabel("Outer-wall liquid $v_y$ (m/s)\n(+ upward, − downward)")
    axes[1].axhline(0, color="black", lw=0.7); axes[1].set_ylabel("Absorber command error (kg/s)"); axes[1].set_xlabel("Child native iteration offset")
    for ax in axes: ax.grid(alpha=0.25); ax.legend(ncol=8, fontsize=8)
    fig.suptitle("Wall-routing response and absorber tracking")
    finish_figure(fig, args.output / "03-wall-velocity-and-absorber-error.png")

    fig, axes = plt.subplots(2, 1, figsize=(8.2, 7.0), sharex=True)
    for case in CASES:
        x, phase1 = series(histories[case], "v2-flux-phase1-steamoutlet")
        axes[0].plot(x, phase1, color=COLORS[case], lw=1.0, label=case)
        _, command = series(histories[case], "v2-command")
        _, applied = series(histories[case], "v2-applied-absorber")
        axes[1].plot(x, command, color=COLORS[case], lw=0.7, ls="--")
        axes[1].plot(x, [-value for value in applied], color=COLORS[case], lw=1.0, label=case)
    axes[0].set_ylabel("Phase-1 steamoutlet flux (kg/s)")
    axes[1].set_ylabel("Command / applied removal magnitude (kg/s)")
    axes[1].set_xlabel("Child native iteration offset")
    axes[1].text(0.02, 0.04, "Dashed = command; solid = applied magnitude", transform=axes[1].transAxes, fontsize=8)
    for ax in axes: ax.grid(alpha=0.25); ax.legend(ncol=8, fontsize=8)
    fig.suptitle("Vapor routing and absorber response")
    finish_figure(fig, args.output / "04-vapor-and-absorber.png")

    fig, axes = plt.subplots(4, 2, figsize=(10.2, 13.0), sharex=True, sharey=True)
    for ax, case in zip(axes.flat, CASES):
        data = residuals(roots[case] / "transcript-native-solve.txt")
        for name in ("continuity", "x-velocity", "y-velocity", "z-velocity", "k", "epsilon", "vf-phase-2"):
            ax.semilogy(data["offset"], data[name], lw=0.75, label=name)
        ax.set_title(case); ax.grid(alpha=0.2)
    axes[3, 0].set_xlabel("Child native iteration offset"); axes[3, 1].set_xlabel("Child native iteration offset")
    for ax in axes[:, 0]: ax.set_ylabel("Scaled residual")
    handles, labels = axes[0, 0].get_legend_handles_labels(); fig.legend(handles, labels, ncol=4, loc="lower center", fontsize=8)
    fig.suptitle("Family R solver residual histories")
    fig.subplots_adjust(bottom=0.13)
    fig.savefig(args.output / "05-residual-histories.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

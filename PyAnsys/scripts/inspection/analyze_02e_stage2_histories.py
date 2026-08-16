#!/usr/bin/env python3
"""Analyze recovered native Fluent report histories for Setup 02e Stage 2.

The script is deliberately offline and read-only with respect to Fluent.  It
parses the native report-history files and native transcripts copied from the
remote Fluent host, then writes the evidence summary and figures used by the
Stage 2 report.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "output" / "02e_stage2_recovered_20260816"
OUTPUT_DIR = INPUT_DIR
REPORT_DIR = PROJECT_ROOT.parent / "Setups" / "reports" / "02e"
TRANSCRIPT_DIR = INPUT_DIR / "transcripts"
LIQUID_DENSITY = 881.77
INITIAL_Y010_MASS = 4224.25373425353
INITIAL_Y010_VOLUME = 4.790652589965104
RESIDUAL_COLUMNS = ["continuity", "x-velocity", "y-velocity", "z-velocity", "k", "epsilon", "vf-phase-2"]

RUNS: dict[str, dict[str, Any]] = {
    "02e-PO-S2-A": {"family": "PO", "control": "1.175 MPa gauge", "suffix": 0, "status": "FAILED_FPE", "n": 453},
    "02e-PO-S2-B": {"family": "PO", "control": "1.190 MPa gauge", "suffix": 1, "status": "FAILED_FPE", "n": 415},
    "02e-OV-S2-A": {"family": "OV", "control": "K=3", "suffix": 2, "status": "COMPLETE_500", "n": 500},
    "02e-OV-S2-B": {"family": "OV", "control": "K=7", "suffix": 3, "status": "COMPLETE_500", "n": 500},
}

REPORT_STEMS = {
    "y010_mass": "inventory_y010_liquid_mass",
    "y030_mass": "inventory_y030_liquid_mass",
    "total_liquid_volume": "inventory_total_liquid_volume",
    "liquid_in": "flux_phase2_liquid_inlet",
    "liquid_brine": "flux_phase2_brine_outlet",
    "liquid_steam": "flux_phase2_steam_outlet",
    "vapour_in": "flux_phase1_steam_inlet",
    "vapour_brine": "flux_phase1_brine_outlet",
    "vapour_steam": "flux_phase1_steam_outlet",
}


def report_path(stem: str, suffix: int) -> Path:
    base = INPUT_DIR / f"02e_stage2_y010_{stem}-rfile"
    return base.with_suffix(".out") if suffix == 0 else Path(f"{base}_{suffix}_1.out")


def read_history(stem: str, suffix: int) -> tuple[np.ndarray, np.ndarray] | None:
    path = report_path(stem, suffix)
    if not path.exists():
        return None
    iterations: list[float] = []
    values: list[float] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            iteration = float(parts[0])
            value = float(parts[1].strip("()"))
        except ValueError:
            continue
        if np.isfinite(iteration) and np.isfinite(value):
            iterations.append(iteration)
            values.append(value)
    return (np.asarray(iterations), np.asarray(values)) if iterations else None


def window_indices(iterations: np.ndarray, status: str) -> tuple[np.ndarray, str]:
    if status == "COMPLETE_500":
        mask = (iterations >= 401) & (iterations <= 500)
        return mask, "401–500"
    count = min(20, len(iterations))
    mask = np.zeros(len(iterations), dtype=bool)
    mask[-count:] = True
    return mask, f"last {count} valid ({int(iterations[-count])}–{int(iterations[-1])})"


def trend_label(x: np.ndarray, y: np.ndarray) -> str:
    if len(y) < 2:
        return "INSUFFICIENT_HISTORY"
    slope = float(np.polyfit(x, y, 1)[0])
    span = float(np.max(y) - np.min(y))
    net = float(y[-1] - y[0])
    scale = max(float(np.mean(np.abs(y))), 1.0)
    if abs(net) <= max(0.02 * scale, 0.10 * span):
        return "APPROXIMATELY_BOUNDED"
    if slope < 0:
        return "DECREASING"
    if slope > 0:
        return "INCREASING"
    return "NON_MONOTONIC"


def stats(iterations: np.ndarray, values: np.ndarray, status: str) -> dict[str, Any]:
    mask, label = window_indices(iterations, status)
    x, y = iterations[mask], values[mask]
    return {
        "basis": label,
        "count": int(len(y)),
        "first_iteration": int(iterations[0]),
        "last_iteration": int(iterations[-1]),
        "first_value": float(values[0]),
        "last_value": float(values[-1]),
        "window_mean": float(np.mean(y)),
        "window_min": float(np.min(y)),
        "window_max": float(np.max(y)),
        "window_slope_per_iteration": float(np.polyfit(x, y, 1)[0]) if len(y) >= 2 else None,
        "window_trend": trend_label(x, y),
    }


def outward_positive(values: np.ndarray, role: str) -> np.ndarray:
    return values if role.endswith("_in") else -values


def read_residual_history(case_id: str) -> tuple[np.ndarray, np.ndarray] | None:
    candidates = sorted(TRANSCRIPT_DIR.glob(f"{case_id}-*.trn"))
    if not candidates:
        return None
    iterations: list[float] = []
    residuals: list[list[float]] = []
    for line in candidates[0].read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            iteration = float(parts[0])
            values = [float(value) for value in parts[1:8]]
        except ValueError:
            continue
        if np.isfinite(iteration) and all(np.isfinite(value) and value >= 0.0 for value in values):
            iterations.append(iteration)
            residuals.append(values)
    return (np.asarray(iterations), np.asarray(residuals)) if iterations else None


def inventory_figure(histories: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]], quantity: str, filename: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    divisor = LIQUID_DENSITY if quantity == "volume" else 1.0
    ylabel = "Liquid inventory (m³, mass / 881.77 kg·m⁻³)" if quantity == "volume" else "Liquid inventory (kg)"
    baseline = INITIAL_Y010_VOLUME if quantity == "volume" else INITIAL_Y010_MASS
    for ax, family in zip(axes, ("PO", "OV")):
        for case_id, meta in RUNS.items():
            if meta["family"] != family:
                continue
            h = histories[case_id]
            style = "-" if meta["status"] == "COMPLETE_500" else "--"
            for key, marker, alpha in (("y010_mass", "o", 1.0), ("y030_mass", "s", 0.65)):
                if key not in h:
                    continue
                x, y = h[key]
                ax.plot(x, y / divisor, style, linewidth=1.2, alpha=alpha, label=f"{case_id} {key[:4].upper()}")
                ax.plot(x[-1], y[-1] / divisor, marker, markersize=4, alpha=alpha)
        ax.axhline(baseline, color="black", linewidth=0.8, alpha=0.45, label="Y010 parent baseline")
        ax.set_title(f"{family} — recovered liquid inventories")
        ax.set_xlabel("Iteration")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=7, ncol=2)
    fig.suptitle("Setup 02e Stage 2: Y010 and Y030 liquid inventory histories")
    for destination in (OUTPUT_DIR / filename, REPORT_DIR / filename):
        fig.savefig(destination, dpi=180)
    plt.close(fig)


def residual_figure(residual_histories: dict[str, tuple[np.ndarray, np.ndarray] | None], filename: str) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for ax, case_id in zip(axes.flat, RUNS):
        history = residual_histories[case_id]
        meta = RUNS[case_id]
        if history is None:
            ax.text(0.5, 0.5, "Residual history unavailable", ha="center", va="center", transform=ax.transAxes)
            ax.set_title(case_id)
            continue
        iterations, values = history
        for index, label in enumerate(RESIDUAL_COLUMNS):
            ax.semilogy(iterations, np.maximum(values[:, index], np.finfo(float).tiny), label=label, color=colors[index])
        ax.set_title(f"{case_id} — {meta['status']}, n={int(iterations[-1])}")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Fluent scaled residual")
        ax.grid(True, which="both", alpha=0.25)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=9, bbox_to_anchor=(0.5, 0.01))
    fig.suptitle("Setup 02e Stage 2: native Fluent scaled residual histories", y=0.985)
    fig.subplots_adjust(left=0.06, right=0.985, top=0.90, bottom=0.12, wspace=0.28, hspace=0.40)
    for destination in (OUTPUT_DIR / filename, REPORT_DIR / filename):
        fig.savefig(destination, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "source": str(INPUT_DIR),
        "analysis": "offline native Fluent report-history extraction",
        "liquid_density_kg_per_m3": LIQUID_DENSITY,
        "initial_y010_liquid_mass_kg": INITIAL_Y010_MASS,
        "initial_y010_liquid_volume_m3": INITIAL_Y010_VOLUME,
        "total_domain_liquid_history": "native volume-integral report included",
        "runs": {},
    }
    histories: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {}
    residual_histories = {case_id: read_residual_history(case_id) for case_id in RUNS}
    csv_rows: list[dict[str, Any]] = []

    for case_id, meta in RUNS.items():
        case: dict[str, Any] = dict(meta)
        case["histories_available"], case["inventory"], case["fluxes"] = {}, {}, {}
        residual_history = residual_histories[case_id]
        case["residual_history_available"] = residual_history is not None
        case["residual_first_iteration"] = int(residual_history[0][0]) if residual_history is not None else None
        case["residual_last_iteration"] = int(residual_history[0][-1]) if residual_history is not None else None
        case_histories: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        for key, stem in REPORT_STEMS.items():
            history = read_history(stem, meta["suffix"])
            case["histories_available"][key] = history is not None
            if history is not None:
                case_histories[key] = history

        for key in ("y010_mass", "y030_mass"):
            history = case_histories.get(key)
            if history is None:
                case["inventory"][key] = None
                continue
            iterations, values = history
            result = stats(iterations, values, meta["status"])
            for source, target in (("first_value", "first_mass_kg"), ("last_value", "last_mass_kg"), ("window_mean", "window_mean_mass_kg"), ("window_min", "window_min_mass_kg"), ("window_max", "window_max_mass_kg")):
                result[target] = result.pop(source)
            for source, target in (("first_mass_kg", "first_volume_m3"), ("last_mass_kg", "last_volume_m3"), ("window_mean_mass_kg", "window_mean_volume_m3"), ("window_min_mass_kg", "window_min_volume_m3"), ("window_max_mass_kg", "window_max_volume_m3")):
                result[target] = result[source] / LIQUID_DENSITY
            result["delta_from_parent_mass_kg"] = result["last_mass_kg"] - INITIAL_Y010_MASS
            result["delta_from_parent_volume_m3"] = result["last_volume_m3"] - INITIAL_Y010_VOLUME
            result["percent_from_parent"] = 100.0 * result["delta_from_parent_mass_kg"] / INITIAL_Y010_MASS
            case["inventory"][key] = result

        total_history = case_histories.get("total_liquid_volume")
        case["inventory"]["total_liquid_volume"] = stats(*total_history, meta["status"]) if total_history is not None else None

        for key in ("liquid_in", "liquid_brine", "liquid_steam", "vapour_in", "vapour_brine", "vapour_steam"):
            history = case_histories.get(key)
            if history is None:
                case["fluxes"][key] = None
                continue
            iterations, native_values = history
            values = outward_positive(native_values, key)
            mask, label = window_indices(iterations, meta["status"])
            selected = values[mask] if meta["status"] == "COMPLETE_500" else values[-1:]
            case["fluxes"][key] = {
                "basis": label if meta["status"] == "COMPLETE_500" else "last valid point",
                "native_last": float(native_values[-1]),
                "outward_positive_last": float(values[-1]),
                "outward_positive_mean": float(np.mean(selected)),
                "outward_positive_min": float(np.min(selected)),
                "outward_positive_max": float(np.max(selected)),
            }

        flux = case["fluxes"]
        case["liquid_balance_L"] = (
            flux["liquid_in"]["outward_positive_mean"] - flux["liquid_brine"]["outward_positive_mean"] - flux["liquid_steam"]["outward_positive_mean"]
            if all(flux.get(key) is not None for key in ("liquid_in", "liquid_brine", "liquid_steam")) else None
        )
        case["vapour_brine_fraction"] = flux["vapour_brine"]["outward_positive_mean"] / flux["vapour_in"]["outward_positive_mean"] if flux.get("vapour_in") and flux.get("vapour_brine") else None
        case["liquid_steam_fraction"] = flux["liquid_steam"]["outward_positive_mean"] / flux["liquid_in"]["outward_positive_mean"] if flux.get("liquid_in") and flux.get("liquid_steam") else None
        summary["runs"][case_id] = case
        histories[case_id] = case_histories
        y010, y030 = case["inventory"].get("y010_mass") or {}, case["inventory"].get("y030_mass") or {}
        total, li, lb, ls, vb = (case["inventory"].get("total_liquid_volume") or {}, flux.get("liquid_in") or {}, flux.get("liquid_brine") or {}, flux.get("liquid_steam") or {}, flux.get("vapour_brine") or {})
        csv_rows.append({
            "case": case_id, "family": meta["family"], "control": meta["control"], "status": meta["status"], "iterations": meta["n"],
            "y010_last_mass_kg": y010.get("last_mass_kg"), "y010_last_volume_m3": y010.get("last_volume_m3"), "y010_delta_volume_m3": y010.get("delta_from_parent_volume_m3"), "y010_trend": y010.get("window_trend"),
            "y030_last_mass_kg": y030.get("last_mass_kg"), "y030_last_volume_m3": y030.get("last_volume_m3"), "y030_delta_volume_m3": y030.get("delta_from_parent_volume_m3"), "y030_trend": y030.get("window_trend"),
            "total_liquid_last_volume_m3": total.get("last_value"), "total_liquid_window_mean_volume_m3": total.get("window_mean"), "total_liquid_trend": total.get("window_trend"),
            "liquid_in_kg_s": li.get("outward_positive_mean"), "liquid_brine_kg_s": lb.get("outward_positive_mean"), "liquid_steam_kg_s": ls.get("outward_positive_mean"), "vapour_brine_kg_s": vb.get("outward_positive_mean"),
            "liquid_balance_L_kg_s": case["liquid_balance_L"], "vapour_brine_fraction": case["vapour_brine_fraction"], "liquid_steam_fraction": case["liquid_steam_fraction"],
        })

    (OUTPUT_DIR / "02e_stage2_inventory_flux_summary_20260816.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (OUTPUT_DIR / "02e_stage2_inventory_flux_summary_20260816.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0])); writer.writeheader(); writer.writerows(csv_rows)
    inventory_figure(histories, "volume", "02e_stage2_inventory_histories_20260816.png")
    inventory_figure(histories, "mass", "02e_stage2_mass_inventory_histories_20260816.png")
    residual_figure(residual_histories, "02e_stage2_scaled_residuals_20260816.png")
    print(f"Wrote {OUTPUT_DIR / '02e_stage2_inventory_flux_summary_20260816.json'}")
    print(f"Wrote {OUTPUT_DIR / '02e_stage2_inventory_flux_summary_20260816.csv'}")
    for row in csv_rows:
        print(row["case"], row["status"], row["iterations"], row["y010_last_volume_m3"], row["y030_last_volume_m3"], row["total_liquid_last_volume_m3"], row["liquid_balance_L_kg_s"])


if __name__ == "__main__":
    main()

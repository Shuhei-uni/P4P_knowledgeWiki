#!/usr/bin/env python3
"""Analyze recovered native Fluent report histories for Setup 02e Stage 1.

This is an offline, read-only analysis. It does not connect to Fluent, load a
case, run a solver command, or write to the Student host. The input files are
the small native report-history ``.out`` files copied from the Student host.
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
INPUT_DIR = PROJECT_ROOT / "output" / "02e_stage1_recovered_reports_20260816"
OUTPUT_DIR = INPUT_DIR
LIQUID_DENSITY = 881.77
INITIAL_Y010_MASS = 4224.25373425353
INITIAL_Y010_VOLUME = 4.790652589965104


RUNS: dict[str, dict[str, Any]] = {
    "PO-P1": {"family": "PO", "control": "1.160 MPa", "suffix": 0, "status": "COMPLETE_500", "n": 500},
    "PO-P2": {"family": "PO", "control": "1.200 MPa", "suffix": 1, "status": "FAILED_FPE", "n": 335},
    "PO-P3": {"family": "PO", "control": "1.240 MPa", "suffix": 2, "status": "FAILED_FPE", "n": 226},
    "OV-P1": {"family": "OV", "control": "K=0", "suffix": 3, "status": "COMPLETE_500", "n": 500},
    "OV-P2": {"family": "OV", "control": "K=10", "suffix": 4, "status": "FAILED_FPE", "n": 448},
    "OV-P3": {"family": "OV", "control": "K=100", "suffix": 5, "status": "FAILED_FPE", "n": 457},
    "MF-P1": {"family": "MF", "control": "58.4235 kg/s", "suffix": 6, "status": "FAILED_FPE", "n": 33},
    "MF-P2": {"family": "MF", "control": "116.847 kg/s", "suffix": 7, "status": "FAILED_FPE", "n": 9},
    # The recovered native MF-P3 transcript and report history terminate at 254.
    "MF-P3": {"family": "MF", "control": "233.694 kg/s", "suffix": 8, "status": "FAILED_FPE", "n": 254},
    # The original EF-P1 report history was not created/preserved. Its known
    # native outcome remains an FPE at 254 from the execution record.
    "EF-P1": {"family": "EF", "control": "-50 kPa", "suffix": None, "status": "FAILED_FPE", "n": 254},
    "EF-P2": {"family": "EF", "control": "0 kPa", "suffix": 9, "status": "COMPLETE_500", "n": 500},
    "EF-P3": {"family": "EF", "control": "+50 kPa", "suffix": 10, "status": "COMPLETE_500", "n": 500},
}


REPORT_STEMS = {
    "y010_mass": "inventory_y010_liquid_mass",
    "y030_mass": "inventory_y030_liquid_mass",
    "liquid_in": "flux_phase2_liquid_inlet",
    "liquid_brine": "flux_phase2_brine_outlet",
    "liquid_steam": "flux_phase2_steam_outlet",
    "vapour_in": "flux_phase1_steam_inlet",
    "vapour_brine": "flux_phase1_brine_outlet",
    "vapour_steam": "flux_phase1_steam_outlet",
}


def report_path(stem: str, suffix: int) -> Path:
    base = INPUT_DIR / f"02e_y010_{stem}-rfile"
    return base.with_suffix(".out") if suffix == 0 else Path(f"{base}_{suffix}_1.out")


def read_history(stem: str, suffix: int | None) -> tuple[np.ndarray, np.ndarray] | None:
    if suffix is None:
        return None
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
    if not iterations:
        return None
    return np.asarray(iterations), np.asarray(values)


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
    x = iterations[mask]
    y = values[mask]
    slope = float(np.polyfit(x, y, 1)[0]) if len(y) >= 2 else None
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
        "window_slope_per_iteration": slope,
        "window_trend": trend_label(x, y),
    }


def outward_positive(values: np.ndarray, role: str) -> np.ndarray:
    # Fluent's native flux report is negative for outward flow on the outlet
    # surfaces. The inlet report is retained as positive inflow.
    return values if role.endswith("_in") else -values


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "source": str(INPUT_DIR),
        "analysis": "offline native Fluent report-history extraction",
        "liquid_density_kg_per_m3": LIQUID_DENSITY,
        "initial_y010_liquid_mass_kg": INITIAL_Y010_MASS,
        "initial_y010_liquid_volume_m3": INITIAL_Y010_VOLUME,
        "total_domain_liquid_history": "unavailable: no total-domain report file was created",
        "runs": {},
    }

    csv_rows: list[dict[str, Any]] = []
    histories: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {}

    for case_id, meta in RUNS.items():
        case: dict[str, Any] = dict(meta)
        case["histories_available"] = {}
        case["inventory"] = {}
        case["fluxes"] = {}
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
            for name, mass_name in (
                ("first_value", "first_mass_kg"),
                ("last_value", "last_mass_kg"),
                ("window_mean", "window_mean_mass_kg"),
                ("window_min", "window_min_mass_kg"),
                ("window_max", "window_max_mass_kg"),
            ):
                result[mass_name] = result.pop(name)
            result["first_volume_m3"] = result["first_mass_kg"] / LIQUID_DENSITY
            result["last_volume_m3"] = result["last_mass_kg"] / LIQUID_DENSITY
            result["window_mean_volume_m3"] = result["window_mean_mass_kg"] / LIQUID_DENSITY
            result["window_min_volume_m3"] = result["window_min_mass_kg"] / LIQUID_DENSITY
            result["window_max_volume_m3"] = result["window_max_mass_kg"] / LIQUID_DENSITY
            result["delta_from_parent_mass_kg"] = result["last_mass_kg"] - INITIAL_Y010_MASS
            result["delta_from_parent_volume_m3"] = result["last_volume_m3"] - INITIAL_Y010_VOLUME
            result["percent_from_parent"] = 100.0 * result["delta_from_parent_mass_kg"] / INITIAL_Y010_MASS
            case["inventory"][key] = result

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
        if all(flux.get(key) is not None for key in ("liquid_in", "liquid_brine", "liquid_steam")):
            case["liquid_balance_L"] = (
                flux["liquid_in"]["outward_positive_mean"]
                - flux["liquid_brine"]["outward_positive_mean"]
                - flux["liquid_steam"]["outward_positive_mean"]
            )
        else:
            case["liquid_balance_L"] = None
        if flux.get("vapour_in") and flux.get("vapour_brine"):
            case["vapour_brine_fraction"] = flux["vapour_brine"]["outward_positive_mean"] / flux["vapour_in"]["outward_positive_mean"]
        else:
            case["vapour_brine_fraction"] = None
        if flux.get("liquid_in") and flux.get("liquid_steam"):
            case["liquid_steam_fraction"] = flux["liquid_steam"]["outward_positive_mean"] / flux["liquid_in"]["outward_positive_mean"]
        else:
            case["liquid_steam_fraction"] = None

        summary["runs"][case_id] = case
        y010 = case["inventory"].get("y010_mass") or {}
        y030 = case["inventory"].get("y030_mass") or {}
        liquid_in = case["fluxes"].get("liquid_in") or {}
        liquid_brine = case["fluxes"].get("liquid_brine") or {}
        liquid_steam = case["fluxes"].get("liquid_steam") or {}
        vapour_brine = case["fluxes"].get("vapour_brine") or {}
        csv_rows.append({
            "case": case_id,
            "family": meta["family"],
            "control": meta["control"],
            "status": meta["status"],
            "iterations": meta["n"],
            "y010_last_mass_kg": y010.get("last_mass_kg"),
            "y010_last_volume_m3": y010.get("last_volume_m3"),
            "y010_delta_volume_m3": y010.get("delta_from_parent_volume_m3"),
            "y010_trend": y010.get("window_trend"),
            "y030_last_mass_kg": y030.get("last_mass_kg"),
            "y030_last_volume_m3": y030.get("last_volume_m3"),
            "y030_delta_volume_m3": y030.get("delta_from_parent_volume_m3"),
            "y030_trend": y030.get("window_trend"),
            "liquid_in_kg_s": liquid_in.get("outward_positive_mean"),
            "liquid_brine_kg_s": liquid_brine.get("outward_positive_mean"),
            "liquid_steam_kg_s": liquid_steam.get("outward_positive_mean"),
            "vapour_brine_kg_s": vapour_brine.get("outward_positive_mean"),
            "liquid_balance_L_kg_s": case["liquid_balance_L"],
            "vapour_brine_fraction": case["vapour_brine_fraction"],
            "liquid_steam_fraction": case["liquid_steam_fraction"],
        })
        histories[case_id] = case_histories

    (OUTPUT_DIR / "02e_stage1_inventory_flux_summary_20260816.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    with (OUTPUT_DIR / "02e_stage1_inventory_flux_summary_20260816.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0]))
        writer.writeheader()
        writer.writerows(csv_rows)

    # Four compact family panels: Y010 and Y030 liquid volumes, with terminal
    # markers for failed runs and a distinct legend for missing EF-P1 history.
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    families = ["PO", "OV", "MF", "EF"]
    for ax, family in zip(axes.flat, families):
        for case_id, meta in RUNS.items():
            if meta["family"] != family:
                continue
            h = histories[case_id]
            if "y010_mass" not in h or "y030_mass" not in h:
                ax.plot([], [], "--", label=f"{case_id}: history unavailable")
                continue
            x, y010 = h["y010_mass"]
            _, y030 = h["y030_mass"]
            line_style = "-" if meta["status"] == "COMPLETE_500" else "--"
            ax.plot(x, y010 / LIQUID_DENSITY, line_style, linewidth=1.2, label=f"{case_id} Y010")
            ax.plot(x, y030 / LIQUID_DENSITY, line_style, linewidth=1.2, alpha=0.65, label=f"{case_id} Y030")
            ax.plot(x[-1], y010[-1] / LIQUID_DENSITY, "o", markersize=4)
            ax.plot(x[-1], y030[-1] / LIQUID_DENSITY, "s", markersize=4, alpha=0.65)
        ax.axhline(INITIAL_Y010_VOLUME, color="black", linewidth=0.8, alpha=0.45, label="Y010 parent baseline")
        ax.set_title(f"{family} — recovered liquid inventories")
        ax.set_xlabel("Iteration")
        ax.set_ylabel("Liquid inventory (m³, mass / 881.77 kg·m⁻³)")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=7, ncol=2)
    fig.suptitle("Setup 02e Stage 1: Y010 and Y030 liquid inventory histories")
    fig.savefig(OUTPUT_DIR / "02e_stage1_inventory_histories_20260816.png", dpi=180)
    plt.close(fig)

    print(f"Wrote {OUTPUT_DIR / '02e_stage1_inventory_flux_summary_20260816.json'}")
    print(f"Wrote {OUTPUT_DIR / '02e_stage1_inventory_flux_summary_20260816.csv'}")
    print(f"Wrote {OUTPUT_DIR / '02e_stage1_inventory_histories_20260816.png'}")
    print("case,status,n,y010_last_m3,y030_last_m3,L_kg_s,y010_trend,y030_trend")
    for row in csv_rows:
        print(
            row["case"], row["status"], row["iterations"],
            row["y010_last_volume_m3"], row["y030_last_volume_m3"],
            row["liquid_balance_L_kg_s"], row["y010_trend"], row["y030_trend"],
        )


if __name__ == "__main__":
    main()

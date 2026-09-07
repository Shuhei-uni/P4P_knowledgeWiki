#!/usr/bin/env python3
"""Extract and plot setup-07e pressure-outlet reversed-flow face counts.

The Fluent transcript reports the number of pressure-outlet faces with reversed
flow after each iteration.  This is a useful recirculation/stability diagnostic
but is not a backflow mass rate and is not an acceptance metric by itself.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)
OUTPUT_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
LOG_PATH = RUN_DIR / "controller.log"
RESIDUAL_PATH = RUN_DIR / "residual_history.csv"
MANIFEST_PATH = RUN_DIR / "qualification_manifest.json"

ITERATION_RE = re.compile(r"^\s*(\d+)\s+[+\-.0-9Ee]+\s+[+\-.0-9Ee]+")
REVERSED_RE = re.compile(
    r"Reversed flow on\s+(\d+)\s+faces of pressure-outlet\s+(\d+)\."
)

ORANGE = "#D97706"
BLUE = "#1769AA"
INK = "#1F2933"
MID = "#5B6570"
GRID = "#D9DEE3"


def set_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "axes.edgecolor": MID,
            "axes.labelcolor": INK,
            "xtick.color": "#374047",
            "ytick.color": "#374047",
            "text.color": INK,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
        }
    )


def style_axis(axis: plt.Axes) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.spines[["left", "bottom"]].set_color("#626B73")
    axis.grid(axis="y", color=GRID, linewidth=0.8)
    axis.set_axisbelow(True)


def extract_reversed_flow() -> pd.DataFrame:
    current_iteration: int | None = None
    rows: list[dict[str, int]] = []
    with LOG_PATH.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            iteration_match = ITERATION_RE.match(line)
            if iteration_match:
                current_iteration = int(iteration_match.group(1))
                continue
            reversed_match = REVERSED_RE.search(line)
            if reversed_match and current_iteration is not None:
                rows.append(
                    {
                        "iteration": current_iteration,
                        "reversed_faces": int(reversed_match.group(1)),
                        "pressure_outlet_zone_id": int(reversed_match.group(2)),
                    }
                )
    if not rows:
        raise RuntimeError(f"No reversed-flow records found in {LOG_PATH}")
    return (
        pd.DataFrame(rows)
        .drop_duplicates("iteration", keep="last")
        .sort_values("iteration")
        .reset_index(drop=True)
    )


def build_figure(reversed_flow: pd.DataFrame, residual: pd.DataFrame, status: str) -> dict[str, str]:
    latest_common_iteration = min(
        int(reversed_flow["iteration"].max()), int(residual["iteration"].max())
    )
    reversed_flow = reversed_flow[
        reversed_flow["iteration"] <= latest_common_iteration
    ].copy()
    residual = residual[residual["iteration"] <= latest_common_iteration].copy()
    joined = reversed_flow.merge(
        residual[["iteration", "continuity"]], on="iteration", how="left"
    )
    joined["reversed_faces_25_iteration_mean"] = (
        joined["reversed_faces"].rolling(25, min_periods=5).mean()
    )

    figure, axes = plt.subplots(2, 1, figsize=(11.6, 7.8), sharex=True)
    figure.suptitle(
        "Setup 07e pressure-outlet recirculation diagnostic",
        fontsize=16,
        fontweight="semibold",
        y=0.982,
    )
    figure.text(
        0.5,
        0.942,
        f"Latest common iteration {latest_common_iteration} • controller status: {status} • DPM off",
        ha="center",
        fontsize=10,
        color=MID,
    )

    axes[0].plot(
        joined["iteration"],
        joined["reversed_faces"],
        color=ORANGE,
        linewidth=0.9,
        alpha=0.45,
        label="per-iteration count",
    )
    axes[0].plot(
        joined["iteration"],
        joined["reversed_faces_25_iteration_mean"],
        color=ORANGE,
        linewidth=2.2,
        label="25-iteration moving mean",
    )
    axes[0].set_title("Pressure-outlet faces reporting reversed flow", fontweight="semibold")
    axes[0].set_ylabel("Faces")
    axes[0].legend(frameon=False, fontsize=8.5, loc="best")
    style_axis(axes[0])

    axes[1].plot(
        joined["iteration"],
        joined["continuity"],
        color=BLUE,
        linewidth=1.3,
        label="continuity residual",
    )
    axes[1].axhline(1e-3, color=INK, linestyle=":", linewidth=1.2, label="1e-3 gate")
    axes[1].set_yscale("log")
    axes[1].set_title("Continuity residual over the same iterations", fontweight="semibold")
    axes[1].set_xlabel("Total solver iteration")
    axes[1].set_ylabel("Scaled residual")
    axes[1].legend(frameon=False, fontsize=8.5, loc="best")
    style_axis(axes[1])

    figure.subplots_adjust(left=0.09, right=0.985, bottom=0.13, top=0.87, hspace=0.30)
    figure.text(
        0.01,
        0.012,
        "Face count indicates outlet recirculation topology only; it is not backflow mass rate and does not replace phase-flow, monitor or residual gates.",
        fontsize=8,
        color="#6B7280",
    )

    png = OUTPUT_DIR / "17_setup07e_pressure_outlet_reversed_flow.png"
    svg = OUTPUT_DIR / "17_setup07e_pressure_outlet_reversed_flow.svg"
    figure.savefig(png, dpi=240)
    figure.savefig(svg)
    plt.close(figure)
    return {"png": str(png), "svg": str(svg)}


def update_manifest(
    artifact: dict[str, str], csv_path: Path, summary_path: Path
) -> None:
    path = OUTPUT_DIR / "visual_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    manifest.setdefault("artifacts", {})["setup07e_pressure_outlet_reversed_flow"] = artifact
    manifest.setdefault("data_exports", [])
    for export in (csv_path, summary_path):
        if str(export) not in manifest["data_exports"]:
            manifest["data_exports"].append(str(export))
    manifest.setdefault("source_files", [])
    if str(LOG_PATH) not in manifest["source_files"]:
        manifest["source_files"].append(str(LOG_PATH))
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    set_style()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    reversed_flow = extract_reversed_flow()
    residual = pd.read_csv(RESIDUAL_PATH)
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    csv_path = OUTPUT_DIR / "setup07e_pressure_outlet_reversed_flow.csv"
    reversed_flow.to_csv(csv_path, index=False)
    first_iteration = int(reversed_flow["iteration"].min())
    last_iteration = int(reversed_flow["iteration"].max())
    summary = {
        "source": str(LOG_PATH),
        "controller_status": str(manifest.get("status", "unknown")),
        "row_count": int(len(reversed_flow)),
        "first_iteration": first_iteration,
        "last_iteration": last_iteration,
        "missing_iterations_within_recorded_span": int(
            last_iteration - first_iteration + 1 - len(reversed_flow)
        ),
        "pressure_outlet_zone_ids": sorted(
            int(value) for value in reversed_flow["pressure_outlet_zone_id"].unique()
        ),
        "minimum_reversed_faces": int(reversed_flow["reversed_faces"].min()),
        "maximum_reversed_faces": int(reversed_flow["reversed_faces"].max()),
        "mean_reversed_faces": float(reversed_flow["reversed_faces"].mean()),
        "latest_common_residual_iteration": int(
            min(last_iteration, int(residual["iteration"].max()))
        ),
        "interpretation_limit": (
            "Reversed pressure-outlet face count is a topology diagnostic, not "
            "backflow mass rate and not an independent convergence gate."
        ),
    }
    summary_path = OUTPUT_DIR / "setup07e_pressure_outlet_reversed_flow_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    artifact = build_figure(reversed_flow, residual, str(manifest.get("status", "unknown")))
    update_manifest(artifact, csv_path, summary_path)
    print(OUTPUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

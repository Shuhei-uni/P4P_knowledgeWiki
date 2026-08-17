#!/usr/bin/env python3
"""Build the compact local Stage-2 screening overview.

This script is intentionally read-only with respect to Fluent.  It consumes
the branch summary and post-processing JSON files already written by the
branch-scoped analysis workflow.  Missing or provisional phases remain visible
in the output metadata and are not filled by interpolation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import math
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PYANSYS_ROOT = REPOSITORY_ROOT / "PyAnsys"
STAGE1_POST = PYANSYS_ROOT / "output/post_simulation_analysis"
INITIAL_POST = PYANSYS_ROOT / "output/03a_stage2/20260817T125355Z/run/post_simulation_analysis"
EXTENSION_POST = PYANSYS_ROOT / "output/03a_stage2/20260817T132736Z/extension-700/post_simulation_analysis"
BRANCH_SUMMARY_DIR = PYANSYS_ROOT / "output/03a_stage2/20260817T132736Z/report"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def points(payload: dict[str, Any], minimum_iteration: float = -math.inf) -> dict[str, list[tuple[float, float]]]:
    x_values = [number(value) for value in payload.get("iterations", [])]
    series = payload.get("series", {})
    result: dict[str, list[tuple[float, float]]] = {}
    for name, values in series.items():
        selected: list[tuple[float, float]] = []
        for x_value, value in zip(x_values, values):
            y_value = number(value)
            if x_value is not None and y_value is not None and x_value > minimum_iteration and y_value > 0:
                selected.append((x_value, y_value))
        result[str(name)] = selected
    return result


def merge(chunks: list[dict[str, list[tuple[float, float]]]]) -> dict[str, list[tuple[float, float]]]:
    names = sorted({name for chunk in chunks for name in chunk})
    result: dict[str, list[tuple[float, float]]] = {}
    for name in names:
        by_iteration: dict[float, float] = {}
        for chunk in chunks:
            for x_value, y_value in chunk.get(name, []):
                by_iteration[x_value] = y_value
        result[name] = sorted(by_iteration.items())
    return result


def residual_sources(branch: str) -> list[tuple[str, Path, float]]:
    stage1 = STAGE1_POST / "03a_08b_parity_full_geometry_iter1000_20260817T110345Z-residual-check.json"
    if branch == "N5":
        return [
            ("Stage 1", stage1, -math.inf),
            ("N5 standard", INITIAL_POST / "N5-standard-bootstrap-residual-check.json", 1000.0),
            ("N5 RNG return", INITIAL_POST / "N5-rng-return-residual-check.json", 1500.0),
            ("N5 +700", EXTENSION_POST / "N5-extension-700-residual-check.json", 1800.0),
        ]
    return [
        ("Stage 1", stage1, -math.inf),
        (f"{branch} +300", INITIAL_POST / f"{branch}-initial-screen-residual-check.json", 1000.0),
        (f"{branch} +700", EXTENSION_POST / f"{branch}-extension-700-residual-check.json", 1300.0),
    ]


def flux_source(branch: str) -> tuple[str, Path]:
    if branch == "N1":
        return "N1 +700", EXTENSION_POST / "N1-extension-700-flux-check.json"
    if branch == "N3":
        return "N3 +700", EXTENSION_POST / "N3-extension-700-flux-check.json"
    if branch == "N4":
        return "N4 +700 snapshot", EXTENSION_POST / "N4-extension-700-flux-check.json"
    return "N5 RNG +300", INITIAL_POST / "N5-rng-return-flux-check.json"


def build_residual_overview(output: Path) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    branches = ("N1", "N3", "N4", "N5")
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), sharex=False, sharey=False, constrained_layout=True)
    records: list[dict[str, Any]] = []
    for axis, branch in zip(axes.ravel(), branches):
        chunks: list[dict[str, list[tuple[float, float]]]] = []
        branch_record: dict[str, Any] = {"branch": branch, "phases": []}
        for label, path, minimum_iteration in residual_sources(branch):
            if not path.exists():
                chunks.append({})
                branch_record["phases"].append({"label": label, "source": str(path), "status": "missing_local_artifact"})
                continue
            selected = points(read_json(path), minimum_iteration)
            chunks.append(selected)
            all_iterations = [x_value for values in selected.values() for x_value, _ in values]
            branch_record["phases"].append({
                "label": label,
                "source": str(path),
                "status": "available" if all_iterations else "no_points_in_phase",
                "first_iteration": min(all_iterations) if all_iterations else None,
                "last_iteration": max(all_iterations) if all_iterations else None,
            })
        merged = merge(chunks)
        for name, values in merged.items():
            if values:
                x_values, y_values = zip(*values)
                axis.plot(x_values, y_values, linewidth=1.0, label=name)
        axis.axvline(1000, color="0.35", linestyle="--", linewidth=0.8)
        axis.axvline(2000 if branch != "N5" else 2500, color="0.35", linestyle="--", linewidth=0.8)
        if branch == "N5":
            axis.axvline(1500, color="0.5", linestyle=":", linewidth=0.8)
            axis.axvline(1800, color="0.5", linestyle=":", linewidth=0.8)
        else:
            axis.axvline(1300, color="0.5", linestyle=":", linewidth=0.8)
        axis.set_yscale("log")
        axis.set_xlabel("Fluent native iteration")
        axis.set_ylabel("Fluent scaled residual")
        axis.set_title(f"{branch} — direct recorded history")
        axis.grid(True, which="major", linestyle="-", alpha=0.23)
        axis.grid(True, which="minor", linestyle=":", alpha=0.15)
        if branch in {"N4", "N5"}:
            axis.text(
                0.02,
                0.04,
                "endpoint residual evidence pending/incomplete",
                transform=axis.transAxes,
                fontsize=8,
                bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "0.6"},
            )
        records.append(branch_record)
    handles, labels = axes.ravel()[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return {"figure": str(output), "branches": records}


def build_flux_overview(output: Path) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    stage1_path = STAGE1_POST / "03a_08b_parity_full_geometry_iter1000_20260817T110345Z-flux-check.json"
    sources: list[tuple[str, Path]] = [("Stage 1", stage1_path)]
    sources.extend(flux_source(branch) for branch in ("N1", "N3", "N4", "N5"))
    metrics: dict[str, dict[str, float | None]] = {}
    for label, path in sources:
        if not path.exists():
            metrics[label] = {}
            continue
        metrics[label] = read_json(path).get("carrier_metrics", {})

    labels = [label for label, _ in sources]
    keys = [
        ("m_liq_steam_out", "liquid → steam outlet"),
        ("m_vap_steam_out", "vapour → steam outlet"),
        ("m_liq_out", "total liquid outlet"),
        ("m_vap_out", "total vapour outlet"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    x_values = np.arange(len(labels))
    for axis, (key, title) in zip(axes.ravel(), keys):
        y_values = [number(metrics[label].get(key)) if metrics.get(label) else math.nan for label in labels]
        axis.bar(x_values, y_values, color=["#4c78a8", "#f58518", "#54a24b", "#e45756", "#b279a2"])
        axis.set_title(title)
        axis.set_ylabel("Mass flow (kg/s)")
        axis.set_xticks(x_values, labels, rotation=25, ha="right")
        axis.grid(axis="y", linestyle=":", alpha=0.35)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return {"figure": str(output), "labels": labels, "metrics": metrics}


def build_balance_overview(output: Path) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    stage1_path = STAGE1_POST / "03a_08b_parity_full_geometry_iter1000_20260817T110345Z-flux-check.json"
    sources: list[tuple[str, Path]] = [("Stage 1", stage1_path)]
    sources.extend(flux_source(branch) for branch in ("N1", "N3", "N4", "N5"))
    labels: list[str] = []
    values: list[float] = []
    for label, path in sources:
        labels.append(label)
        payload = read_json(path) if path.exists() else {}
        value = number(payload.get("carrier_metrics", {}).get("mass_imbalance_ratio"))
        values.append(math.nan if value is None else value * 100.0)

    fig, axis = plt.subplots(figsize=(11, 6), constrained_layout=True)
    bars = axis.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b", "#e45756", "#b279a2"])
    axis.axhline(values[0], color="0.3", linestyle="--", linewidth=1.0, label="Stage-1 reference")
    axis.set_ylabel("Diagnostic mass imbalance (%)")
    axis.set_title("03A Stage-2 compact mass-balance comparison")
    axis.tick_params(axis="x", rotation=25)
    axis.grid(axis="y", linestyle=":", alpha=0.35)
    for bar, value in zip(bars, values):
        if math.isfinite(value):
            axis.text(bar.get_x() + bar.get_width() / 2, value, f"{value:.2f}%", ha="center", va="bottom", fontsize=9)
    axis.legend(frameon=False)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return {"figure": str(output), "labels": labels, "mass_imbalance_percent": values}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    payload = {
        "residual_overview": build_residual_overview(output_dir / "stage2-full-scaled-residual-overview.png"),
        "flux_overview": build_flux_overview(output_dir / "stage2-phase-flux-overview.png"),
        "balance_overview": build_balance_overview(output_dir / "stage2-mass-balance-overview.png"),
        "inventory_history_status": "No temporal liquid-inventory histories are currently available in the branch monitor artifacts.",
        "interpretation_status": "provisional pending N4 and N5 endpoint verification",
    }
    summary_path = output_dir / "stage2-overview.json"
    summary_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    print(f"overview_json: {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

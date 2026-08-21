#!/usr/bin/env python3
"""Build branch-by-branch Stage-3 evidence packages and plots.

This is an offline, read-only companion to
``build_03a_stage3_native_queue_analysis.py``.  Each selected queue branch gets
its own evidence directory and a consistent plot set.  The script never
connects to Fluent, changes a setting, fills a missing history, or treats an
endpoint sequence as a continuous monitor history.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import build_03a_stage3_native_queue_analysis as base


REPORT_ROOT = base.REPORT_ROOT
DEFAULT_CHECKPOINT_CSV = base.DEFAULT_CHECKPOINT_CSV
DEFAULT_RUN_DIR = base.DEFAULT_RUN_DIR
DEFAULT_READBACK_DIR = base.DEFAULT_READBACK_DIR
DEFAULT_EVIDENCE_DIR = REPORT_ROOT / "evidence" / "03a-stage3-native-queue"
DEFAULT_PLOT_DIR = REPORT_ROOT / "plots" / "03a-stage3" / "native-queue"
DEFAULT_ARTIFACT_MANIFEST = base.DEFAULT_ARTIFACT_MANIFEST
BRANCH_ORDER = base.BRANCH_ORDER


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint-csv", type=Path, default=DEFAULT_CHECKPOINT_CSV)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--readback-dir", type=Path, default=DEFAULT_READBACK_DIR)
    parser.add_argument("--evidence-dir", type=Path, default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--plot-dir", type=Path, default=DEFAULT_PLOT_DIR)
    parser.add_argument("--artifact-manifest", type=Path, default=DEFAULT_ARTIFACT_MANIFEST)
    parser.add_argument("--no-plots", action="store_true")
    return parser


def configure_plotting() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "legend.fontsize": 8,
            "figure.dpi": 120,
        }
    )
    return plt


def save_figure(figure: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=180, bbox_inches="tight")
    figure.clf()
    import matplotlib.pyplot as plt

    plt.close(figure)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows({column: row.get(column) for column in columns} for row in rows)


def finite(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def branch_rows(rows: list[dict[str, Any]], branch: str) -> list[dict[str, Any]]:
    return [row for row in rows if row["branch"] == branch]


def branch_stages(residual_status: dict[str, Any], branch: str) -> list[dict[str, Any]]:
    return [stage for stage in residual_status.get("stages", []) if stage.get("branch") == branch]


def branch_points(residual_status: dict[str, Any], branch: str) -> list[dict[str, Any]]:
    return [
        {
            "stage": stage.get("stage"),
            "equations": stage.get("endpoint_residual_point", {}),
        }
        for stage in branch_stages(residual_status, branch)
        if stage.get("endpoint_residual_point_available")
    ]


def endpoint_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "status": "unavailable",
            "basis": "no valid full-Mixture endpoint row in the selected evidence bundle",
        }
    final = rows[-1]
    return {
        "status": "endpoint_only",
        "basis": "last available endpoint row; not a late-window metric",
        "load_percent": final.get("load_percent"),
        "iteration": final.get("iteration"),
        "mass_imbalance_signed_pct": final.get("mass_imbalance_signed_pct"),
        "mass_imbalance_abs_pct": final.get("mass_imbalance_abs_pct"),
        "liquid_inventory_total_kg": final.get("liquid_inventory_total_kg"),
        "brine_entry_static_pressure_margin_kpa": final.get("brine_entry_static_pressure_margin_kpa"),
    }


def late_window_metrics(
    residual_status: dict[str, Any], report_history: dict[str, Any], branch: str
) -> dict[str, Any]:
    if report_history.get("status") == "found_unmapped_local_artifacts":
        reason = (
            "Local Stage-3-named report files were found, but their run/branch lineage "
            "does not map to this server-2 queue; endpoint points cannot be promoted to "
            "late-window statistics. Continuous residual history is also unavailable."
        )
    else:
        reason = (
            "Continuous residual and native report-file histories are unavailable; "
            "endpoint points cannot be promoted to late-window statistics."
        )
    return {
        "status": "unavailable",
        "branch": branch,
        "reason": reason,
        "residual_history_status": residual_status.get("history_status"),
        "report_history_status": report_history.get("status"),
        "metrics": {
            "residual_median": None,
            "residual_p95": None,
            "mass_imbalance_median_abs_pct": None,
            "mass_imbalance_p95_abs_pct": None,
            "inventory_slope_kg_per_iteration": None,
            "inventory_std_kg": None,
        },
    }


def status_message(axis: Any, title: str, message: str) -> None:
    axis.set_title(title)
    axis.text(
        0.5,
        0.5,
        message,
        ha="center",
        va="center",
        transform=axis.transAxes,
        wrap=True,
    )
    axis.set_xticks([])
    axis.set_yticks([])
    axis.grid(False)


def x_values(rows: list[dict[str, Any]]) -> list[float]:
    return [float(row["iteration"]) for row in rows]


def add_load_labels(axis: Any, rows: list[dict[str, Any]]) -> None:
    if len({row["load_percent"] for row in rows}) < 2:
        return
    for row in rows:
        axis.axvline(row["iteration"], color="#64748b", alpha=0.14)
        axis.text(
            row["iteration"],
            0.98,
            f"{row['load_percent']}%",
            transform=axis.get_xaxis_transform(),
            rotation=90,
            va="top",
            ha="right",
            fontsize=7,
            color="#475569",
        )


def plot_residuals(
    branch: str,
    stages: list[dict[str, Any]],
    points: list[dict[str, Any]],
    plot_path: Path,
) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(2, 1, figsize=(8.8, 6.2), gridspec_kw={"height_ratios": [1.0, 1.3]})
    labels = [str(stage.get("stage")) for stage in stages] or ["no submitted stage record"]
    values: list[list[int]] = []
    texts: list[list[str]] = []
    for stage in stages:
        export = bool(stage.get("native_export_exists"))
        monitor = bool(stage.get("retained_residual_monitor_available"))
        point = bool(stage.get("endpoint_residual_point_available"))
        values.append([int(export), int(monitor), int(point)])
        texts.append(
            [
                "available" if export else ("missing" if stage.get("native_export_status") == "missing" else "not probed"),
                "available" if monitor else "absent",
                "point" if point else "none",
            ]
        )
    if not values:
        values = [[0, 0, 0]]
        texts = [["none", "none", "none"]]
    image = axes[0].imshow(values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    axes[0].set_xticks(range(3), ["native export", "retained monitor", "endpoint point"])
    axes[0].set_yticks(range(len(labels)), labels)
    axes[0].set_title(f"{branch} — residual evidence availability")
    for row_index, row_text in enumerate(texts):
        for column_index, text in enumerate(row_text):
            axes[0].text(column_index, row_index, text, ha="center", va="center", fontsize=8)
    axes[0].set_xlabel("No continuous residual series is available for this branch")
    figure.colorbar(image, ax=axes[0], fraction=0.025, pad=0.02, ticks=[0, 1], label="evidence present")

    if points:
        point = points[-1]
        equation_names = list(base.EXPECTED_RESIDUALS)
        values_for_plot = [finite(point["equations"].get(name)) for name in equation_names]
        pairs = [(name, value) for name, value in zip(equation_names, values_for_plot) if value is not None and value > 0]
        if pairs:
            names, numeric = zip(*pairs)
            axes[1].barh(list(names), list(numeric), color="#2563eb")
            axes[1].set_xscale("log")
            axes[1].set_xlabel("Residual value (single endpoint point; log scale)")
            axes[1].set_title(f"{branch} — available endpoint residual point at {point['stage']}")
            axes[1].grid(axis="x", alpha=0.25)
        else:
            status_message(axes[1], f"{branch} — endpoint residual point", "No finite positive residual values available")
    else:
        status_message(
            axes[1],
            f"{branch} — residual history unavailable",
            "No continuous history or retained endpoint residual point was recovered.",
        )
    figure.suptitle(f"{branch} — all residual evidence", y=0.998)
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    save_figure(figure, plot_path)


def plot_physical(branch: str, rows: list[dict[str, Any]], plot_path: Path) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(3, 1, figsize=(8.8, 8.2), sharex=True)
    if not rows:
        for axis, title in zip(
            axes,
            ("mass inlet/outlet", "relative mass imbalance", "total liquid inventory"),
        ):
            status_message(axis, f"{branch} — {title}", "No valid full-Mixture endpoint row was recovered.")
    else:
        x = x_values(rows)
        axes[0].plot(x, [row["total_inlet_kg_s"] for row in rows], marker="o", label="total inlet", color="#2563eb")
        axes[0].plot(x, [row["total_outlet_kg_s"] for row in rows], marker="s", label="total outlet", color="#111827")
        axes[0].set_ylabel("Mass flow (kg/s)")
        axes[0].set_title("Mass inlet and outlet")
        axes[0].legend(loc="best")
        axes[0].grid(True, alpha=0.25)

        axes[1].axhline(0.0, color="#111827", linewidth=0.8)
        axes[1].plot(x, [row["mass_imbalance_signed_pct"] for row in rows], marker="o", color="#dc2626")
        axes[1].set_ylabel("Relative imbalance (%)")
        axes[1].set_title("Signed total mass imbalance")
        axes[1].grid(True, alpha=0.25)

        axes[2].plot(x, [row["liquid_inventory_total_kg"] for row in rows], marker="o", color="#16a34a")
        axes[2].set_ylabel("Liquid inventory (kg)")
        axes[2].set_title("Total liquid inventory")
        axes[2].grid(True, alpha=0.25)
        add_load_labels(axes[0], rows)
        add_load_labels(axes[1], rows)
        add_load_labels(axes[2], rows)
        axes[2].set_xlabel("Cumulative native iterations; markers are endpoints only")
    figure.suptitle(f"{branch} — mass closure and liquid inventory", y=0.998)
    figure.tight_layout(rect=(0, 0, 1, 0.97))
    save_figure(figure, plot_path)


def plot_phase_routing(branch: str, rows: list[dict[str, Any]], plot_path: Path) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(2, 1, figsize=(8.8, 6.8), sharex=True)
    if not rows:
        for axis, title in zip(axes, ("brine outlet routing", "steam outlet routing")):
            status_message(axis, f"{branch} — {title}", "No valid full-Mixture endpoint row was recovered.")
    else:
        x = x_values(rows)
        for axis, series, title in (
            (
                axes[0],
                (("liquid_to_brine_fraction_pct", "liquid → brine", "#2563eb"), ("vapour_to_brine_fraction_pct", "vapour → brine", "#dc2626")),
                "Brine outlet routing",
            ),
            (
                axes[1],
                (("liquid_to_steam_fraction_pct", "liquid → steam", "#16a34a"), ("vapour_to_steam_fraction_pct", "vapour → steam", "#9333ea")),
                "Steam outlet routing",
            ),
        ):
            for key, label, color in series:
                axis.plot(x, [row[key] for row in rows], marker="o", label=label, color=color)
            axis.set_ylabel("Routing fraction (%)")
            axis.set_title(title)
            axis.grid(True, alpha=0.25)
            axis.legend(loc="best")
            add_load_labels(axis, rows)
        axes[1].set_xlabel("Cumulative native iterations; markers are endpoints only")
    figure.suptitle(f"{branch} — phase routing", y=0.998)
    figure.text(0.5, 0.005, "Routing fractions are diagnostic and are not capped at 100%.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    save_figure(figure, plot_path)


def plot_liquid_distribution(branch: str, rows: list[dict[str, Any]], plot_path: Path) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(2, 1, figsize=(8.8, 6.8), sharex=True)
    if not rows:
        for axis, title in zip(axes, ("liquid inventory", "Y010/Y030 distribution")):
            status_message(axis, f"{branch} — {title}", "No valid full-Mixture endpoint row was recovered.")
    else:
        x = x_values(rows)
        for key, label, color in (
            ("liquid_inventory_total_kg", "total liquid", "#111827"),
            ("liquid_inventory_y030_kg", "Y030", "#2563eb"),
            ("liquid_inventory_y010_kg", "Y010", "#dc2626"),
        ):
            axes[0].plot(x, [row[key] for row in rows], marker="o", label=label, color=color)
        axes[0].set_ylabel("Liquid mass (kg)")
        axes[0].set_title("Total and diagnostic-region liquid inventory")
        axes[0].legend(loc="best")
        axes[0].grid(True, alpha=0.25)
        for key, label, color in (
            ("liquid_inventory_y030_kg", "Y030 / total", "#2563eb"),
            ("liquid_inventory_y010_kg", "Y010 / total", "#dc2626"),
        ):
            axes[1].plot(
                x,
                [100.0 * row[key] / row["liquid_inventory_total_kg"] for row in rows],
                marker="o",
                label=label,
                color=color,
            )
        axes[1].set_ylabel("Inventory share (%)")
        axes[1].set_title("Diagnostic-region share of total liquid")
        axes[1].legend(loc="best")
        axes[1].grid(True, alpha=0.25)
        add_load_labels(axes[0], rows)
        add_load_labels(axes[1], rows)
        axes[1].set_xlabel("Cumulative native iterations; markers are endpoints only")
    figure.suptitle(f"{branch} — liquid distribution", y=0.998)
    figure.text(0.5, 0.005, "Y010/Y030 are diagnostic registers, not a validated free-surface measure.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    save_figure(figure, plot_path)


def plot_brine_hydraulics(branch: str, rows: list[dict[str, Any]], plot_path: Path) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(2, 1, figsize=(8.8, 6.8), sharex=True)
    if not rows:
        for axis, title in zip(axes, ("pressure margin", "brine flow")):
            status_message(axis, f"{branch} — {title}", "No valid full-Mixture endpoint row was recovered.")
    else:
        x = x_values(rows)
        for key, label, color in (
            ("brine_entry_static_pressure_margin_kpa", "static margin", "#2563eb"),
            ("brine_entry_total_pressure_margin_kpa", "total-pressure margin", "#dc2626"),
        ):
            axes[0].plot(x, [row[key] for row in rows], marker="o", label=label, color=color)
        axes[0].axhline(0.0, color="#111827", linewidth=0.8)
        axes[0].set_ylabel("Pressure margin (kPa)")
        axes[0].set_title("Brine-entry pressure relative to the 1.120 MPa gauge reference")
        axes[0].legend(loc="best")
        axes[0].grid(True, alpha=0.25)
        for key, label, color in (
            ("total_brine_outlet_kg_s", "total brine outlet", "#111827"),
            ("liquid_to_brine_kg_s", "liquid → brine", "#16a34a"),
        ):
            axes[1].plot(x, [row[key] for row in rows], marker="o", label=label, color=color)
        axes[1].set_ylabel("Flow (kg/s)")
        axes[1].set_title("Brine outlet flow")
        axes[1].legend(loc="best")
        axes[1].grid(True, alpha=0.25)
        add_load_labels(axes[0], rows)
        add_load_labels(axes[1], rows)
        axes[1].set_xlabel("Cumulative native iterations; markers are endpoints only")
    figure.suptitle(f"{branch} — brine-entry pressure and flow", y=0.998)
    figure.text(0.5, 0.005, "Endpoint associations are not physical-time causality.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    save_figure(figure, plot_path)


def plot_cross_plots(branch: str, rows: list[dict[str, Any]], plot_path: Path) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(2, 2, figsize=(8.8, 7.0))
    pairs = (
        ("mass_imbalance_abs_pct", "liquid_inventory_total_kg", "Absolute imbalance (%)", "Liquid inventory (kg)"),
        ("brine_entry_static_pressure_margin_kpa", "total_brine_outlet_kg_s", "Static margin (kPa)", "Brine outlet (kg/s)"),
        ("liquid_inventory_total_kg", "liquid_to_brine_kg_s", "Liquid inventory (kg)", "Liquid → brine (kg/s)"),
        ("mass_imbalance_abs_pct", "total_outlet_kg_s", "Absolute imbalance (%)", "Total outlet (kg/s)"),
    )
    if len(rows) < 2:
        for axis, pair in zip(axes.flat, pairs):
            status_message(
                axis,
                f"{pair[2]} vs {pair[3]}",
                "Not calculable: fewer than two endpoint states and no continuous history.",
            )
    else:
        for axis, (x_key, y_key, x_label, y_label) in zip(axes.flat, pairs):
            axis.scatter([row[x_key] for row in rows], [row[y_key] for row in rows], color="#2563eb", s=42)
            for row in rows:
                axis.annotate(str(row["load_percent"]) + "%", (row[x_key], row[y_key]), fontsize=7, xytext=(3, 3), textcoords="offset points")
            axis.set_xlabel(x_label)
            axis.set_ylabel(y_label)
            axis.grid(True, alpha=0.25)
    figure.suptitle(f"{branch} — branch-specific cross-plots", y=0.998)
    figure.text(0.5, 0.005, "Associations among endpoint states are not causal or convergence histories.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    save_figure(figure, plot_path)


def plot_ramp_response(branch: str, rows: list[dict[str, Any]], plot_path: Path) -> None:
    plt = configure_plotting()
    figure, axes = plt.subplots(2, 2, figsize=(8.8, 6.8))
    is_ramp = len(rows) > 1 and len({row["load_percent"] for row in rows}) > 1
    if not is_ramp:
        for axis in axes.flat:
            status_message(axis, f"{branch} — ramp response", "Not applicable: this branch has no multi-load ramp in the selected queue.")
    else:
        metrics = (
            ("mass_imbalance_abs_pct", "Absolute imbalance (%)"),
            ("liquid_inventory_total_kg", "Total liquid inventory (kg)"),
            ("brine_entry_static_pressure_margin_kpa", "Static pressure margin (kPa)"),
            ("total_outlet_kg_s", "Total outlet flow (kg/s)"),
        )
        for axis, (key, label) in zip(axes.flat, metrics):
            axis.plot([row["load_percent"] for row in rows], [row[key] for row in rows], marker="o", color="#2563eb")
            axis.set_xlabel("Imposed inlet loading (%)")
            axis.set_ylabel(label)
            axis.set_xticks([10, 20, 40, 80, 100])
            axis.grid(True, alpha=0.25)
    figure.suptitle(f"{branch} — ramp-response summary", y=0.998)
    figure.text(0.5, 0.005, "Ramp points are confirmed stage endpoints; no interpolation is applied.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.97))
    save_figure(figure, plot_path)


def branch_plot_paths(branch: str, plot_root: Path) -> dict[str, Path]:
    branch_dir = plot_root / branch
    return {
        "residuals": branch_dir / "01-residuals.png",
        "physical": branch_dir / "02-mass-imbalance-inventory.png",
        "phase_routing": branch_dir / "03-phase-routing.png",
        "liquid_distribution": branch_dir / "04-liquid-distribution.png",
        "brine_hydraulics": branch_dir / "05-brine-pressure-flow.png",
        "cross_plots": branch_dir / "06-cross-plots.png",
        "ramp_response": branch_dir / "07-ramp-response.png",
    }


def build_branch_package(
    branch: str,
    rows: list[dict[str, Any]],
    residual_status: dict[str, Any],
    report_history: dict[str, Any],
    evidence_root: Path,
    plot_root: Path,
    no_plots: bool,
) -> dict[str, Any]:
    stages = branch_stages(residual_status, branch)
    points = branch_points(residual_status, branch)
    metrics = late_window_metrics(residual_status, report_history, branch)
    package_dir = evidence_root / "branches" / branch
    branch_csv_columns = [
        "branch",
        "run_stamp",
        "iteration",
        "load_percent",
        "momentum_urf",
        "evidence_status",
        "total_inlet_kg_s",
        "total_outlet_kg_s",
        "mass_imbalance_signed_pct",
        "mass_imbalance_abs_pct",
        "liquid_inventory_total_kg",
        "liquid_inventory_y030_kg",
        "liquid_inventory_y010_kg",
        "brine_entry_static_pressure_margin_kpa",
        "brine_entry_total_pressure_margin_kpa",
        "liquid_to_brine_fraction_pct",
        "liquid_to_steam_fraction_pct",
        "vapour_to_brine_fraction_pct",
        "vapour_to_steam_fraction_pct",
    ]
    write_csv(package_dir / "branch-checkpoints.csv", rows, branch_csv_columns)
    write_csv(
        package_dir / "branch-residual-points.csv",
        [
            {
                "branch": branch,
                "stage": point["stage"],
                "equation": equation,
                "value": value,
            }
            for point in points
            for equation, value in sorted(point["equations"].items())
        ],
        ["branch", "stage", "equation", "value"],
    )
    write_json(package_dir / "branch-residual-evidence.json", {"branch": branch, "stages": stages, "points": points})
    write_json(package_dir / "branch-late-window-metrics.json", metrics)
    write_json(package_dir / "branch-report-history-evidence.json", report_history)

    paths = branch_plot_paths(branch, plot_root)
    if not no_plots:
        plot_residuals(branch, stages, points, paths["residuals"])
        plot_physical(branch, rows, paths["physical"])
        plot_phase_routing(branch, rows, paths["phase_routing"])
        plot_liquid_distribution(branch, rows, paths["liquid_distribution"])
        plot_brine_hydraulics(branch, rows, paths["brine_hydraulics"])
        plot_cross_plots(branch, rows, paths["cross_plots"])
        plot_ramp_response(branch, rows, paths["ramp_response"])

    package = {
        "kind": "03a_stage3_branch_analysis_package",
        "branch": branch,
        "branch_metadata": base.BRANCH_META[branch],
        "checkpoint_count": len(rows),
        "residual_stage_count": len(stages),
        "residual_point_count": len(points),
        "residual_history_status": residual_status.get("history_status"),
        "report_history_status": report_history.get("status"),
        "late_window_metrics": metrics,
        "endpoint_metrics": endpoint_metrics(rows),
        "artifacts": {
            "checkpoints_csv": base.relative_path(package_dir / "branch-checkpoints.csv"),
            "residual_points_csv": base.relative_path(package_dir / "branch-residual-points.csv"),
            "residual_evidence_json": base.relative_path(package_dir / "branch-residual-evidence.json"),
            "late_window_metrics_json": base.relative_path(package_dir / "branch-late-window-metrics.json"),
            "report_history_json": base.relative_path(package_dir / "branch-report-history-evidence.json"),
            "plots": {name: base.relative_path(path) for name, path in paths.items()},
        },
    }
    write_json(package_dir / "branch-analysis.json", package)
    return package


def build_cross_branch_summary(packages: list[dict[str, Any]], path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for package in packages:
        late = package["late_window_metrics"]
        endpoint = package["endpoint_metrics"]
        rows.append(
            {
                "branch": package["branch"],
                "terminal_status": package["branch_metadata"]["status"],
                "full_mixture_100pct_iterations": package["branch_metadata"]["full_mixture_100pct_iterations"],
                "residual_history_status": package["residual_history_status"],
                "report_history_status": package["report_history_status"],
                "late_window_metrics_status": late["status"],
                "late_window_mass_imbalance_median_abs_pct": late["metrics"]["mass_imbalance_median_abs_pct"],
                "late_window_mass_imbalance_p95_abs_pct": late["metrics"]["mass_imbalance_p95_abs_pct"],
                "late_window_inventory_slope_kg_per_iteration": late["metrics"]["inventory_slope_kg_per_iteration"],
                "endpoint_abs_imbalance_pct": endpoint.get("mass_imbalance_abs_pct"),
                "endpoint_liquid_inventory_kg": endpoint.get("liquid_inventory_total_kg"),
                "endpoint_basis": endpoint.get("basis"),
                "evidence_strength": "partial",
            }
        )
    write_csv(
        path,
        rows,
        [
            "branch",
            "terminal_status",
            "full_mixture_100pct_iterations",
            "residual_history_status",
            "report_history_status",
            "late_window_metrics_status",
            "late_window_mass_imbalance_median_abs_pct",
            "late_window_mass_imbalance_p95_abs_pct",
            "late_window_inventory_slope_kg_per_iteration",
            "endpoint_abs_imbalance_pct",
            "endpoint_liquid_inventory_kg",
            "endpoint_basis",
            "evidence_strength",
        ],
    )


def main() -> int:
    args = build_parser().parse_args()
    checkpoint_csv = args.checkpoint_csv.expanduser().resolve()
    run_dir = args.run_dir.expanduser().resolve()
    evidence_root = args.evidence_dir.expanduser().resolve()
    plot_root = args.plot_dir.expanduser().resolve()
    artifact_manifest = args.artifact_manifest.expanduser().resolve()

    rows = base.load_checkpoint_rows(checkpoint_csv)
    residual_status = base.load_residual_status(run_dir)
    report_history = base.report_history_status(run_dir, artifact_manifest)
    packages = [
        build_branch_package(
            branch,
            branch_rows(rows, branch),
            residual_status,
            report_history,
            evidence_root,
            plot_root,
            args.no_plots,
        )
        for branch in BRANCH_ORDER
    ]
    summary_csv = evidence_root / "03a-stage3-native-queue-cross-branch-summary.csv"
    build_cross_branch_summary(packages, summary_csv)
    package_index = {
        "kind": "03a_stage3_native_queue_branch_package_index",
        "scope": {
            "branches": list(BRANCH_ORDER),
            "analysis_mode": "offline read-only branch-by-branch endpoint analysis",
            "interpretation_status": "pending user direction",
        },
        "late_window_summary_status": "unavailable",
        "late_window_summary_reason": (
            "No continuous residual history is available, and the locally discovered "
            "Stage-3-named report files cannot be mapped to the server-2 queue; the "
            "cross-branch table exposes null late-window metrics and retains endpoint "
            "values separately as endpoint-only context."
        ),
        "artifact_discovery_manifest": base.relative_path(artifact_manifest),
        "artifact_discovery_status": report_history.get("artifact_discovery_status"),
        "discovered_stage3_out_file_count": report_history.get("discovered_stage3_out_file_count", 0),
        "branches": packages,
        "cross_branch_summary_csv": base.relative_path(summary_csv),
    }
    index_path = evidence_root / "03a-stage3-native-queue-branch-packages.json"
    write_json(index_path, package_index)
    print(
        json.dumps(
            {
                "branch_package_index": base.relative_path(index_path),
                "cross_branch_summary": base.relative_path(summary_csv),
                "branches": list(BRANCH_ORDER),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

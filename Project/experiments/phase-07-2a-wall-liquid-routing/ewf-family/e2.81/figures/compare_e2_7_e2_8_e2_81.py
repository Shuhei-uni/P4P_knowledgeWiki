#!/usr/bin/env python3
"""Create compact, source-backed E2.7/E2.8/E2.81 comparison figures."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


ROOT = Path(__file__).resolve().parents[6]
FAMILY = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family"
FIGURES = FAMILY / "e2.81/figures"
OUTPUT = ROOT / "PyAnsys/output"
E27_MONITORS = (
    Path.home()
    / "Documents/FluentRuns/Phase72A/FamilyE/E2.7/20260923T071523Z/monitors"
)
E281_FIRST_ATTEMPT = (
    Path.home()
    / "Documents/FluentRuns/Phase72A/FamilyE/E2.81-fast-time-20260926T052048Z/monitors"
)
E281_RECOVERY = (
    OUTPUT
    / "phase72a_ewf_direct_e281_20260926T052048Z/continuation_N8586_to_N13586"
    / "recovery_from_N10000_to_N13586/monitors"
)

RUNS = {
    "E2.7": {
        "color": "#1f77b4",
        "history": OUTPUT
        / "phase72a_ewf_direct_e281_20260926T052048Z/e27-matched-thickness-area.json",
    },
    "E2.8": {
        "color": "#ff7f0e",
        "history": OUTPUT
        / "phase72a_ewf_direct_e28_20260926T010700Z/e28-per-iteration-history.csv",
    },
    "E2.81": {
        "color": "#2ca02c",
        "history": OUTPUT
        / "phase72a_ewf_direct_e281_20260926T052048Z/e281-per-iteration-history.csv",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def read_fluent_report(path: Path) -> dict[int, float]:
    """Read numeric iteration/value rows from a Fluent .out report file."""
    values: dict[int, float] = {}
    row_pattern = re.compile(
        r"^\s*(\d+)\s+([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][-+]?\d+)?)"
    )
    with path.open(encoding="utf-8-sig", errors="replace") as stream:
        for line in stream:
            match = row_pattern.match(line)
            if match:
                values[int(match.group(1))] = float(match.group(2))
    return values


def report_path(directory: Path, stem: str) -> Path:
    path = directory / f"{stem}.out"
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def build_trajectory() -> dict[str, dict[str, dict[int, float]]]:
    fields = {
        "film_mass": {},
        "max_thickness": {},
        "mean_speed": {},
    }

    # E2.7 native 5586–8586 segment. The historical monitor files append
    # later duplicate/recovery activity; retain only the original 3,001 rows.
    e27_prefix = "P72A-E2.7-p72a-e2.7-ewf-"
    e27_core = {
        "film_mass": read_fluent_report(
            E27_MONITORS / f"{e27_prefix}film-mass-total.out"
        ),
        "max_thickness": read_fluent_report(
            E27_MONITORS / f"{e27_prefix}thickness-max.out"
        ),
        "mean_speed": read_fluent_report(
            E27_MONITORS / f"{e27_prefix}velocity-mag-awavg.out"
        ),
    }
    for metric, source in e27_core.items():
        fields[metric]["E2.7"] = {
            iteration: value * (1000.0 if metric == "max_thickness" else 1.0)
            for iteration, value in source.items()
            if 5586 <= iteration <= 8586
        }

    # E2.7's independent continuation has aligned per-iteration data through
    # 13586. Its monitor values are stitched after the shared N8586 endpoint.
    e27_cont_path = FAMILY / "figures/E2.7-CONT5000-requested-histories.csv"
    e27_cont = read_csv(e27_cont_path)
    e27_columns = {
        "film_mass": "ewf_film_mass_kg",
        "max_thickness": "ewf_maximum_film_thickness_mm",
        "mean_speed": "ewf_velocity_area_weighted_average_m_s",
    }
    for metric, column in e27_columns.items():
        fields[metric]["E2.7"].update(
            {
                int(row["native_iteration"]): float(row[column])
                for row in e27_cont
                if int(row["native_iteration"]) > 8586 and row[column]
            }
        )

    # The E2.8 and E2.81 analysis extracts cover the common native 5586–8586
    # horizon. Thickness is converted from Fluent metres to millimetres.
    for experiment, filename, prefix in (
        (
            "E2.8",
            "phase72a_ewf_direct_e28_20260926T010700Z/e28-per-iteration-history.csv",
            "p72a-e2.8-ewf-",
        ),
        (
            "E2.81",
            "phase72a_ewf_direct_e281_20260926T052048Z/e281-per-iteration-history.csv",
            "p72a-e2.81-ewf-",
        ),
    ):
        rows = read_csv(OUTPUT / filename)
        for metric, suffix in (
            ("film_mass", "film-mass-total"),
            ("max_thickness", "thickness-max"),
            ("mean_speed", "velocity-mag-awavg"),
        ):
            factor = 1000.0 if metric == "max_thickness" else 1.0
            fields[metric][experiment] = {
                int(row["native_iteration"]): float(row[f"{prefix}{suffix}"]) * factor
                for row in rows
                if row.get(f"{prefix}{suffix}")
            }

    # E2.81's first continuation disconnected at N10272. Keep that recorded
    # path only through N9999, then use the recovered N10000 checkpoint onward.
    e281_stem = "p72a-e2.81-ewf-"
    e281_first = {
        "film_mass": read_fluent_report(
            report_path(E281_FIRST_ATTEMPT, f"{e281_stem}film-mass-total")
        ),
        "max_thickness": read_fluent_report(
            report_path(E281_FIRST_ATTEMPT, f"{e281_stem}thickness-max")
        ),
        "mean_speed": read_fluent_report(
            report_path(E281_FIRST_ATTEMPT, f"{e281_stem}velocity-mag-awavg")
        ),
    }
    e281_recovered = {
        "film_mass": read_fluent_report(
            report_path(E281_RECOVERY, f"{e281_stem}film-mass-total")
        ),
        "max_thickness": read_fluent_report(
            report_path(E281_RECOVERY, f"{e281_stem}thickness-max")
        ),
        "mean_speed": read_fluent_report(
            report_path(E281_RECOVERY, f"{e281_stem}velocity-mag-awavg")
        ),
    }
    for metric in fields:
        selected = fields[metric]["E2.81"]
        factor = 1000.0 if metric == "max_thickness" else 1.0
        selected.update(
            {
                iteration: value * factor
                for iteration, value in e281_first[metric].items()
                if 8586 < iteration < 10000
            }
        )
        selected.update(
            {
                iteration: value * factor
                for iteration, value in e281_recovered[metric].items()
                if iteration >= 10000
            }
        )

    expected = {
        "E2.7": (5586, 13586),
        "E2.8": (5586, 8586),
        "E2.81": (5586, 13586),
    }
    for metric in fields:
        for experiment, (first, last) in expected.items():
            iterations = sorted(fields[metric][experiment])
            if not iterations or iterations[0] != first or iterations[-1] != last:
                raise ValueError(
                    f"{experiment} {metric} coverage is "
                    f"{iterations[0] if iterations else None}–"
                    f"{iterations[-1] if iterations else None}, expected {first}–{last}"
                )
            if iterations != list(range(first, last + 1)):
                raise ValueError(f"{experiment} {metric} has coordinate gaps or duplicates")
    return fields


def plot_trajectories(fields: dict[str, dict[str, dict[int, float]]]) -> Path:
    fig, axes = plt.subplots(3, 1, figsize=(11.5, 9.2), sharex=True)
    metric_specs = (
        ("film_mass", "Total EWF film mass", "kg"),
        ("max_thickness", "Maximum film thickness", "mm"),
        ("mean_speed", "Area-weighted film speed", "m/s"),
    )

    for ax, (metric, title, unit) in zip(axes, metric_specs):
        for experiment, cfg in RUNS.items():
            values = fields[metric][experiment]
            color = cfg["color"]
            iterations = sorted(values)
            common = [i for i in iterations if i <= 8586]
            ax.plot(
                common,
                [values[i] for i in common],
                color=color,
                linewidth=1.4,
            )
            continuation = [i for i in iterations if i > 8586]
            if continuation:
                ax.plot(
                    continuation,
                    [values[i] for i in continuation],
                    color=color,
                    linewidth=1.6,
                    linestyle="--",
                )
        ax.axvline(8586, color="#555555", linewidth=0.9, linestyle=":")
        ax.axvline(10000, color="#777777", linewidth=0.9, linestyle="-.")
        ax.set_ylabel(f"{title}\n({unit})")
        ax.grid(True, alpha=0.25)
        ax.set_xlim(5586, 13586)

    axes[-1].set_xlabel("Native Fluent iteration")
    axes[0].set_title(
        "E2.7, E2.8 and E2.81: matched EWF response histories",
        loc="left",
        fontsize=14,
        weight="bold",
    )
    legend = [
        Line2D([0], [0], color=cfg["color"], lw=1.7, label=name)
        for name, cfg in RUNS.items()
    ] + [
        Line2D([0], [0], color="#555555", lw=1.5, linestyle=":", label="Common 3000-iteration horizon"),
        Line2D([0], [0], color="#444444", lw=1.5, linestyle="--", label="Continuation"),
    ]
    fig.legend(handles=legend, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.53, 0.965))
    fig.subplots_adjust(top=0.89, bottom=0.18, hspace=0.22, left=0.12, right=0.98)
    fig.text(
        0.12,
        0.065,
        "Dashed lines are continuations; E2.8 ends at N8586. E2.81 uses the first attempt through N9999, then the recovered N10000 checkpoint path (272 iterations replayed).",
        fontsize=7.8,
        color="#444444",
    )
    fig.text(
        0.12,
        0.03,
        "E2.7 continuation has a recorded copied-start hash mismatch. Raw monitor peaks are retained.",
        fontsize=7.8,
        color="#444444",
    )
    path = FIGURES / "E2.7-E2.8-E2.81-film-trajectories.png"
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)
    return path


def plot_threshold_areas() -> Path:
    e27_path = OUTPUT / "phase72a_ewf_direct_e281_20260926T052048Z/e27-matched-thickness-area.json"
    e27 = json.loads(e27_path.read_text(encoding="utf-8"))["measurements"]
    threshold_keys = [
        ("0.01", "0.01"),
        ("0.05", "0.05"),
        ("0.10", "0.1"),
        ("0.25", "0.25"),
        ("0.50", "0.5"),
    ]
    labels = [label for label, _ in threshold_keys]
    e27_values = [e27[f"area_at_or_above_{key}_mm_m2"] for _, key in threshold_keys]

    values_by_run = {"E2.7": e27_values}
    for experiment, folder in (
        ("E2.8", "phase72a_ewf_direct_e28_20260926T010700Z"),
        ("E2.81", "phase72a_ewf_direct_e281_20260926T052048Z"),
    ):
        path = OUTPUT / folder / "checkpoint-area/checkpoint-thickness-area.csv"
        rows = read_csv(path)
        row = next(r for r in rows if int(r["native_iteration"]) == 8586)
        values_by_run[experiment] = [
            float(row[f"area_at_or_above_{key}_mm_m2"]) for _, key in threshold_keys
        ]

    fig, ax = plt.subplots(figsize=(8.6, 5.4))
    x_positions = list(range(len(labels)))
    for experiment, cfg in RUNS.items():
        ax.plot(
            x_positions,
            values_by_run[experiment],
            color=cfg["color"],
            marker="o",
            markersize=5,
            linewidth=1.8,
            label=experiment,
        )
    ax.set_xticks(x_positions, [f"≥ {label}" for label in labels])
    ax.set_xlabel("Film thickness threshold (mm)")
    ax.set_ylabel("Active wall area at or above threshold (m²)")
    ax.set_title(
        "Reconstructed wall area by film thickness at native N8586",
        loc="left",
        fontsize=13,
        weight="bold",
    )
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, ncol=3, loc="upper right")
    ax.set_ylim(bottom=0)
    fig.text(
        0.12,
        0.015,
        "All three use the same 3,463-face wall-area reconstruction; these threshold areas are distinct from Fluent's Film Coverage integral.",
        fontsize=8.2,
        color="#444444",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    path = FIGURES / "E2.7-E2.8-E2.81-wet-area-by-thickness.png"
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)
    return path


def build_plot_suite_data() -> dict[str, dict[str, dict[int, float]]]:
    """Collect E2.8-style response and health fields with native coordinates."""
    metrics = (
        "film_mass",
        "max_thickness",
        "mean_thickness",
        "mean_speed",
        "coverage",
        "courant",
        "film_time",
        "timestep",
        "outflow",
        "h_residual",
        "u_residual",
        "v_residual",
    )
    data = {metric: {name: {} for name in RUNS} for metric in metrics}
    e27_prefix = "P72A-E2.7-p72a-e2.7-ewf-"
    e27_sources = {
        "film_mass": ("film-mass-total", 1.0),
        "max_thickness": ("thickness-max", 1000.0),
        "mean_thickness": ("thickness-awavg", 1000.0),
        "mean_speed": ("velocity-mag-awavg", 1.0),
        "courant": ("courant-max", 1.0),
        "outflow": ("outflow-mass-total", 1.0),
    }
    for metric, (suffix, factor) in e27_sources.items():
        vals = read_fluent_report(E27_MONITORS / f"{e27_prefix}{suffix}.out")
        data[metric]["E2.7"].update(
            {it: value * factor for it, value in vals.items() if 5586 <= it <= 8586}
        )
    # E2.7's fixed 1e-5 s film step is recorded in its setup and was used
    # unchanged in its 5,000-iteration horizon extension.
    data["film_time"]["E2.7"].update(
        {it: (it - 5586) * 1e-5 for it in range(5586, 13587)}
    )
    data["timestep"]["E2.7"].update({it: 1e-5 for it in range(5586, 13587)})

    # E2.8/E2.81 all-iteration histories through their shared N8586 endpoint.
    for experiment, filename, prefix in (
        ("E2.8", "phase72a_ewf_direct_e28_20260926T010700Z/e28-per-iteration-history.csv", "p72a-e2.8-ewf-"),
        ("E2.81", "phase72a_ewf_direct_e281_20260926T052048Z/e281-per-iteration-history.csv", "p72a-e2.81-ewf-"),
    ):
        rows = read_csv(OUTPUT / filename)
        source_fields = {
            "film_mass": (f"{prefix}film-mass-total", 1.0),
            "max_thickness": (f"{prefix}thickness-max", 1000.0),
            "mean_thickness": (f"{prefix}thickness-awavg", 1000.0),
            "mean_speed": (f"{prefix}velocity-mag-awavg", 1.0),
            "coverage": (f"{prefix}wet-area", 1.0),
            "courant": (f"{prefix}courant-max", 1.0),
            "film_time": ("film_time_s", 1.0),
            "timestep": ("film_timestep_s", 1.0),
            "outflow": (f"{prefix}outflow-mass-total", 1.0),
            "h_residual": ("ewf_h_residual_max", 1.0),
            "u_residual": ("ewf_u_residual_max", 1.0),
            "v_residual": ("ewf_v_residual_max", 1.0),
        }
        for metric, (column, factor) in source_fields.items():
            data[metric][experiment] = {
                int(row["native_iteration"]): float(row[column]) * factor
                for row in rows
                if row.get(column, "") not in ("", "nan", "NaN")
            }

    # E2.7 5,000-step continuation has a deliberately smaller extracted set.
    e27_cont = read_csv(FAMILY / "figures/E2.7-CONT5000-requested-histories.csv")
    for metric, column in (
        ("film_mass", "ewf_film_mass_kg"),
        ("max_thickness", "ewf_maximum_film_thickness_mm"),
        ("mean_speed", "ewf_velocity_area_weighted_average_m_s"),
    ):
        data[metric]["E2.7"].update(
            {
                int(row["native_iteration"]): float(row[column])
                for row in e27_cont
                if int(row["native_iteration"]) > 8586 and row.get(column)
            }
        )
    e27_measures = json.loads(
        (OUTPUT / "phase72a_ewf_direct_e281_20260926T052048Z/e27-matched-thickness-area.json").read_text(encoding="utf-8")
    )["measurements"]
    data["coverage"]["E2.7"][8586] = e27_measures["wet_area_m2_film_coverage"]
    data["coverage"]["E2.7"][13586] = float(e27_cont[-1]["ewf_wetted_area_m2_at_native_13586"])

    # E2.81 continuation report files: retain its first attempt only before
    # the N10000 restart point, then use the recovered checkpoint trajectory.
    monitor_fields = {
        "film_mass": ("film-mass-total", 1.0),
        "max_thickness": ("thickness-max", 1000.0),
        "mean_thickness": ("thickness-awavg", 1000.0),
        "mean_speed": ("velocity-mag-awavg", 1.0),
        "coverage": ("wet-area", 1.0),
        "courant": ("courant-max", 1.0),
        "outflow": ("outflow-mass-total", 1.0),
    }
    for metric, (suffix, factor) in monitor_fields.items():
        for source, lower, upper in (
            (E281_FIRST_ATTEMPT, 8587, 9999),
            (E281_RECOVERY, 10000, 13586),
        ):
            vals = read_fluent_report(report_path(source, f"p72a-e2.81-ewf-{suffix}"))
            data[metric]["E2.81"].update(
                {it: val * factor for it, val in vals.items() if lower <= it <= upper}
            )

    # Continuation film-time and timestep readbacks are sparse; keep them as
    # isolated source points instead of drawing a made-up per-iteration curve.
    recovery_manifest = json.loads(
        (OUTPUT / "phase72a_ewf_direct_e281_20260926T052048Z/continuation_N8586_to_N13586/recovery_from_N10000_to_N13586/recovery-manifest.json").read_text(encoding="utf-8")
    )
    start = recovery_manifest["start_film_solution_state"]
    final = recovery_manifest["final_film_solution_state"]
    data["film_time"]["E2.81"].update({10000: start["film_elapsed_time"], 13586: final["film_elapsed_time"]})
    data["timestep"]["E2.81"].update({10000: start["film_timestep"], 13586: final["film_timestep"]})
    return data


def draw_native_series(ax, values: dict[int, float], color: str, label: str, *, marker: str | None = None) -> None:
    """Draw contiguous native-coordinate segments without bridging data gaps."""
    if not values:
        return
    items = sorted(values.items())
    segments: list[list[tuple[int, float]]] = [[items[0]]]
    for item in items[1:]:
        if item[0] != segments[-1][-1][0] + 1:
            segments.append([item])
        else:
            segments[-1].append(item)
    for segment in segments:
        x = [item[0] for item in segment]
        y = [item[1] for item in segment]
        linestyle = "--" if x[0] > 8586 else "-"
        ax.plot(x, y, color=color, linewidth=1.15, linestyle=linestyle, marker=marker, markersize=3, label=label if segment is segments[0] else None)


def plot_film_response(data: dict[str, dict[str, dict[int, float]]]) -> Path:
    specs = (
        ("film_mass", "Film mass", "kg"),
        ("max_thickness", "Maximum film thickness", "mm"),
        ("mean_thickness", "Area-weighted film thickness", "mm"),
        ("mean_speed", "Area-weighted film speed", "m/s"),
        ("coverage", "Film Coverage area", "m²"),
        ("courant", "Maximum film Courant", "-"),
        ("film_time", "Film elapsed time from N5586", "s"),
    )
    fig, axes = plt.subplots(4, 2, figsize=(12.5, 13.2), sharex=False)
    flat = list(axes.flat)
    for ax, (metric, title, unit) in zip(flat, specs):
        for experiment, config in RUNS.items():
            draw_native_series(ax, data[metric][experiment], config["color"], experiment, marker="o" if metric == "film_time" else None)
        ax.axvline(8586, color="#475569", linewidth=0.8, linestyle=":")
        if metric == "film_time" or metric == "timestep":
            ax.set_ylabel(f"{title}\n({unit})")
        else:
            ax.set_title(title, fontsize=10, loc="left")
            ax.set_ylabel(unit)
        ax.grid(True, alpha=0.22)
        ax.set_xlim(5586, 13586 if metric in ("film_mass", "max_thickness", "mean_speed", "coverage", "courant", "film_time") else 8586)
        ax.set_xlabel("Native iteration")
    flat[-1].axis("off")
    axes[0, 0].set_title("Film mass (kg)", fontsize=10, loc="left")
    axes[0, 1].set_title("Maximum film thickness (mm)", fontsize=10, loc="left")
    fig.suptitle("E2.7 / E2.8 / E2.81 film response", x=0.05, ha="left", fontsize=15, weight="bold")
    handles = [Line2D([0], [0], color=c["color"], lw=1.8, label=n) for n, c in RUNS.items()]
    handles += [Line2D([0], [0], color="#334155", lw=1.5, linestyle="--", label="Continuation after N8586")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.965))
    fig.text(0.07, 0.025, "E2.8 ends at N8586. E2.81 switches to its recovered N10000 checkpoint after the failed attempt; sparse time/timestep readbacks are shown as unconnected points.", fontsize=8, color="#444444")
    fig.tight_layout(rect=(0.04, 0.05, 0.98, 0.93), h_pad=1.5, w_pad=1.4)
    path = FIGURES / "E2.7-E2.8-E2.81-film-response.png"
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)
    return path


def plot_numerical_health(data: dict[str, dict[str, dict[int, float]]]) -> Path:
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.6))
    ax = axes[0, 0]
    for experiment in ("E2.8", "E2.81"):
        color = RUNS[experiment]["color"]
        for metric, label, style in (("h_residual", "h", "-"), ("u_residual", "u", "--"), ("v_residual", "v", ":")):
            vals = data[metric][experiment]
            pairs = [(it, value) for it, value in sorted(vals.items()) if value > 0]
            if pairs:
                ax.semilogy([p[0] for p in pairs], [p[1] for p in pairs], color=color, linestyle=style, linewidth=0.9, label=f"{experiment} {label}")
    ax.set_title("EWF sub-iteration residual maxima")
    ax.set_ylabel("Absolute residual")
    ax.set_xlabel("Native iteration")
    ax.grid(True, which="both", alpha=0.22)
    ax.legend(frameon=False, fontsize=8, ncol=2)

    ax = axes[0, 1]
    for experiment, config in RUNS.items():
        draw_native_series(ax, data["courant"][experiment], config["color"], experiment)
    ax.axhline(0.5, color=RUNS["E2.8"]["color"], linestyle=":", linewidth=1, label="E2.8 Co max")
    ax.axhline(0.4, color=RUNS["E2.81"]["color"], linestyle=":", linewidth=1, label="E2.81 Co max")
    ax.set_title("Maximum film Courant")
    ax.set_xlabel("Native iteration")
    ax.set_ylabel("Courant")
    ax.grid(True, alpha=0.22)

    ax = axes[1, 0]
    for experiment, config in RUNS.items():
        draw_native_series(ax, data["timestep"][experiment], config["color"], experiment, marker="o" if experiment == "E2.81" else None)
    ax.set_title("Adaptive film timestep")
    ax.set_xlabel("Native iteration")
    ax.set_ylabel("Timestep (s)")
    ax.grid(True, alpha=0.22)

    ax = axes[1, 1]
    for experiment, config in RUNS.items():
        draw_native_series(ax, data["outflow"][experiment], config["color"], experiment)
    ax.set_title("Cumulative film outflow monitor")
    ax.set_xlabel("Native iteration")
    ax.set_ylabel("Reported mass outflow (kg)")
    ax.grid(True, alpha=0.22)

    fig.suptitle("E2.7 / E2.8 / E2.81 numerical health and film transfer", x=0.05, ha="left", fontsize=14, weight="bold")
    handles = [Line2D([0], [0], color=c["color"], lw=1.8, label=n) for n, c in RUNS.items()]
    handles += [Line2D([0], [0], color="#334155", lw=1.5, linestyle="--", label="Continuation after N8586")]
    fig.legend(handles=handles, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 0.955))
    fig.text(0.08, 0.015, "E2.7 per-step EWF residuals and continuation CFL/outflow were not in its extracted report set; E2.81 continuation residuals and timestep are available only as sparse readbacks.", fontsize=7.8, color="#444444")
    fig.tight_layout(rect=(0.04, 0.05, 0.98, 0.91), h_pad=1.5, w_pad=1.4)
    path = FIGURES / "E2.7-E2.8-E2.81-ewf-numerical-health.png"
    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)
    return path


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fields = build_trajectory()
    suite = build_plot_suite_data()
    for metric, series in fields.items():
        for experiment, values in series.items():
            print(
                f"{experiment} {metric}: N{min(values)}–N{max(values)} "
                f"({len(values)} points), final={values[max(values)]:.8g}"
            )
    print(plot_film_response(suite))
    print(plot_threshold_areas())
    print(plot_numerical_health(suite))


if __name__ == "__main__":
    main()

"""Compare available Phase 7.2A EWF-family bulk and film liquid inventories."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter


ROOT = Path(__file__).resolve().parents[3]
FLUENT_RUNS = Path.home() / "Documents/FluentRuns/Phase72A/FamilyE"
OUTPUT = ROOT / "PyAnsys/output/phase72a_ewf_family_total_liquid_inventory_20260927"
START_ITERATION = 5586
END_ITERATION = 8586
OVERLAY_TOLERANCE_KG = 1e-10


def monitor_dir(case_dir: str, run_id: str, monitor_dirname: str = "monitors") -> Path:
    return FLUENT_RUNS / case_dir / run_id / monitor_dirname


CASE_SPECS: list[dict[str, Any]] = [
    {
        "case": "E0",
        "source_type": "monitor",
        "bulk_dir": monitor_dir("E0", "20260922T115500Z"),
        "film_dir": None,
        "status": "smooth no-film control",
        "color": "#596773",
    },
    {
        "case": "E1",
        "source_type": "monitor",
        "bulk_dir": monitor_dir("E1", "20260923T024000Z"),
        "film_dir": monitor_dir("E1", "20260923T024000Z"),
        "status": "basic EWF; film report remains zero",
        "color": "#5a9f86",
    },
    {
        "case": "E2 attempt 1",
        "source_type": "monitor",
        "bulk_dir": monitor_dir("E2", "20260923T031600Z"),
        "film_dir": monitor_dir("E2", "20260923T031600Z"),
        "status": "phase-accretion branch; cap/FPE block",
        "color": "#b84f4f",
        "blocked": True,
    },
    {
        "case": "E2 recovery attempt",
        "source_type": "monitor",
        "bulk_dir": monitor_dir("E2", "20260923T040000Z"),
        "film_dir": monitor_dir("E2", "20260923T040000Z"),
        "status": "phase-accretion recovery; cap/FPE block",
        "color": "#d17c66",
        "blocked": True,
    },
]

for case, run_id, color in [
    ("E2.1", "20260923T052000Z", "#a64f43"),
    ("E2.2", "20260923T053831Z", "#c05b3e"),
    ("E2.3", "20260923T055258Z", "#d46f37"),
    ("E2.4", "20260923T060500Z", "#b78136"),
    ("E2.5", "20260923T062200Z", "#9b8d38"),
    ("E2.6", "20260923T065114Z", "#7d8f3e"),
]:
    CASE_SPECS.append(
        {
            "case": case,
            "source_type": "monitor",
            "bulk_dir": monitor_dir(case, run_id),
            "film_dir": monitor_dir(case, run_id),
            "status": "phase-accretion numerical block; cap/FPE",
            "color": color,
            "blocked": True,
        }
    )

CASE_SPECS.extend(
    [
        {
            "case": "E2.7",
            "source_type": "monitor",
            "bulk_dir": monitor_dir("E2.7", "20260923T071523Z"),
            "film_dir": monitor_dir("E2.7", "20260923T071523Z"),
            "status": "phase-accretion baseline; matched horizon ends at N8586",
            "color": "#245ea8",
        },
        {
            "case": "E3",
            "source_type": "monitor",
            "bulk_dir": monitor_dir("E3", "20260923T032500Z"),
            "film_dir": monitor_dir("E3", "20260923T032500Z"),
            "status": "basic EWF plus selected roughness",
            "color": "#3e8f4b",
        },
    ]
)

RECENT_CASES = [
    (
        "E2.8",
        "phase72a_ewf_direct_e28_20260926T010700Z",
        "selected adaptive prefix plus fixed-step recovery from N7000",
        "#e17c24",
    ),
    (
        "E2.81",
        "phase72a_ewf_direct_e281_20260926T052048Z",
        "adaptive follow-up; numerical qualification unresolved",
        "#8e5bb7",
    ),
    (
        "E2.82",
        "phase72a_ewf_fixed_dt_e2.82_20260926T134145Z",
        "fixed dt 1.25e-5 s; late numerical excursion",
        "#168c9a",
    ),
    (
        "E2.83",
        "phase72a_ewf_fixed_dt_e2.83_20260926T144249Z",
        "fixed dt 1.50e-5 s; thickness cap/divergence",
        "#a75098",
    ),
    (
        "E2.84",
        "phase72a_ewf_fixed_dt_e2.84_20260926T154347Z",
        "fixed dt 1.75e-5 s; thickness cap/divergence",
        "#855b3e",
    ),
]
for case, output_dir, status, color in RECENT_CASES:
    CASE_SPECS.append(
        {
            "case": case,
            "source_type": "report_history_json",
            "history_path": ROOT / "PyAnsys/output" / output_dir / "report-histories.json",
            "status": status,
            "color": color,
            "blocked": case in {"E2.83", "E2.84"},
        }
    )


def read_monitor(directory: Path, report_suffix: str) -> tuple[dict[int, float], str]:
    matches = sorted(directory.glob(f"*{report_suffix}.out"))
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected one {report_suffix} report in {directory}; found {len(matches)}"
        )
    values: dict[int, float] = {}
    row_pattern = re.compile(r"^\s*(\d+)\s+([-+0-9.eE]+)\s*$")
    for line in matches[0].read_text(errors="replace").splitlines():
        match = row_pattern.match(line)
        if match:
            iteration = int(match.group(1))
            value = float(match.group(2))
            if iteration in values and values[iteration] != value:
                raise RuntimeError(f"Conflicting values at N{iteration} in {matches[0]}")
            values[iteration] = value
    return values, matches[0].relative_to(FLUENT_RUNS).as_posix()


def read_json_history(path: Path, report_name: str) -> tuple[dict[int, float], dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    report = raw[report_name]
    iterations = report["iterations"]
    values = report["values"]
    if len(iterations) != len(values) or len(set(iterations)) != len(iterations):
        raise RuntimeError(f"Invalid history alignment in {path}: {report_name}")
    return dict(zip(iterations, values, strict=True)), {
        "path": path.relative_to(ROOT).as_posix(),
        "report_name": report_name,
        "selected_trajectory_sources": sanitize_paths(
            report.get("selected_trajectory_sources")
        ),
        "local_file": sanitize_paths(report.get("local_file")),
    }


def clip(values: dict[int, float]) -> dict[int, float]:
    return {
        iteration: value
        for iteration, value in sorted(values.items())
        if START_ITERATION <= iteration <= END_ITERATION
    }


def load_cases() -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for spec in CASE_SPECS:
        if spec["source_type"] == "monitor":
            bulk, bulk_source = read_monitor(spec["bulk_dir"], "v2-total-liquid-mass")
            if spec["film_dir"] is None:
                film, film_source = {}, None
            else:
                film, film_source = read_monitor(spec["film_dir"], "ewf-film-mass-total")
        else:
            bulk, bulk_meta = read_json_history(
                spec["history_path"], "v2-total-liquid-mass"
            )
            film, film_meta = read_json_history(
                spec["history_path"],
                next(
                    key
                    for key in json.loads(spec["history_path"].read_text(encoding="utf-8"))
                    if "ewf-film-mass-total" in key
                ),
            )
            bulk_source = bulk_meta
            film_source = film_meta

        bulk = clip(bulk)
        film = clip(film)
        if not bulk:
            raise RuntimeError(f"{spec['case']} has no bulk history in the selected window")
        loaded[spec["case"]] = {
            **spec,
            "bulk": bulk,
            "film": film,
            "bulk_source": bulk_source,
            "film_source": film_source,
        }
    return loaded


def bulk_overlay_groups(data: dict[str, dict[str, Any]]) -> list[list[str]]:
    remaining = list(data)
    groups: list[list[str]] = []
    while remaining:
        case = remaining.pop(0)
        group = [case]
        for other in list(remaining):
            left = data[case]["bulk"]
            right = data[other]["bulk"]
            if set(left) == set(right) and all(
                abs(left[iteration] - right[iteration]) <= OVERLAY_TOLERANCE_KG
                for iteration in left
            ):
                group.append(other)
                remaining.remove(other)
        groups.append(group)
    return groups


def write_artifacts(data: dict[str, dict[str, Any]]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT / "ewf-family-liquid-inventory.csv"
    summary_path = OUTPUT / "ewf-family-liquid-inventory-summary.json"

    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(
            [
                "case",
                "native_iteration",
                "continuous_liquid_mass_kg",
                "ewf_film_mass_kg",
                "case_status",
                "bulk_source",
                "film_source",
            ]
        )
        for case, series in data.items():
            iterations = sorted(set(series["bulk"]) | set(series["film"]))
            for iteration in iterations:
                writer.writerow(
                    [
                        case,
                        iteration,
                        series["bulk"].get(iteration, ""),
                        series["film"].get(iteration, ""),
                        series["status"],
                        source_text(series["bulk_source"]),
                        source_text(series["film_source"]),
                    ]
                )

    colors = {case: series["color"] for case, series in data.items()}
    bulk_groups = bulk_overlay_groups(data)
    fig, axes = plt.subplots(2, 1, figsize=(15.5, 9.5), sharex=True)
    fig.subplots_adjust(left=0.085, right=0.74, bottom=0.13, top=0.91, hspace=0.12)

    for group in bulk_groups:
        representative = data[group[0]]
        axes[0].plot(
            list(representative["bulk"]),
            list(representative["bulk"].values()),
            color=colors[group[0]],
            linewidth=1.55 if not representative.get("blocked") else 1.1,
            linestyle="--" if representative.get("blocked") else "-",
            alpha=0.92,
        )

    for case, series in data.items():
        if not series["film"]:
            continue
        axes[1].plot(
            list(series["film"]),
            list(series["film"].values()),
            color=colors[case],
            linewidth=1.35 if not series.get("blocked") else 1.05,
            linestyle="--" if series.get("blocked") else "-",
            alpha=0.9,
        )

    axes[0].set_ylabel("Continuous-liquid inventory (kg)")
    axes[0].set_title(
        "Bulk phase report: v2-total-liquid-mass", loc="left", fontsize=11
    )
    axes[0].grid(alpha=0.24)
    axes[0].set_xlim(START_ITERATION, END_ITERATION)
    axes[1].set_ylabel("EWF film inventory (kg; symlog)")
    axes[1].set_title("Wall-film report: ewf-film-mass-total", loc="left", fontsize=11)
    axes[1].set_yscale("symlog", linthresh=0.1, linscale=0.75)
    axes[1].set_ylim(bottom=0)
    axes[1].set_yticks([0, 0.1, 1, 10, 100, 1000, 10000])
    axes[1].yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:g}"))
    axes[1].grid(alpha=0.24, which="both")
    axes[1].set_xlabel("Native Fluent iteration")

    fig.suptitle(
        "Phase 7.2A Family E — liquid inventory across available EWF cases",
        fontsize=15,
    )
    handles = [
        Line2D(
            [0],
            [0],
            color=series["color"],
            linewidth=1.45,
            linestyle="--" if series.get("blocked") else "-",
        )
        for series in data.values()
    ]
    labels = list(data)
    fig.legend(
        handles,
        labels,
        loc="center left",
        bbox_to_anchor=(0.755, 0.52),
        frameon=False,
        fontsize=8.4,
        ncol=1,
        title="Case (dashed = early numerical block)",
        title_fontsize=9,
    )
    fig.text(
        0.085,
        0.035,
        "Raw native points; no interpolation. E2.8: adaptive to N7000, then fixed-step recovery. "
        "E2.7/E2.82-2.84 bulk histories overlap within 1e-12 kg (one trace). E2.83/.84 film traces reach thousands of kg. E4 omitted (no history).",
        fontsize=8.4,
        color="#444444",
    )

    fig.savefig(OUTPUT / "ewf-family-liquid-inventory.svg")
    fig.savefig(OUTPUT / "ewf-family-liquid-inventory.png", dpi=180)
    plt.close(fig)

    overlay_groups = [group for group in bulk_groups if len(group) > 1]
    summary: dict[str, Any] = {
        "question": "Compare the available Phase 7.2A Family E liquid-inventory histories.",
        "window_native_iteration": [START_ITERATION, END_ITERATION],
        "alignment": "Native report iterations retained; no interpolation or resampling.",
        "definitions": {
            "continuous_liquid_mass_kg": "v2-total-liquid-mass; continuous-liquid inventory, excluding separately reported EWF film mass.",
            "ewf_film_mass_kg": "ewf-film-mass-total; Fluent EWF film inventory.",
        },
        "bulk_overlay_tolerance_kg": OVERLAY_TOLERANCE_KG,
        "bulk_overlay_groups_within_tolerance": overlay_groups,
        "excluded": {
            "E4": "No total-liquid-mass history was present in the accessible E4 run directory.",
        },
        "cases": {},
    }
    for case, series in data.items():
        summary["cases"][case] = {
            "status_or_lineage": series["status"],
            "bulk_points": len(series["bulk"]),
            "bulk_native_range": [min(series["bulk"]), max(series["bulk"])],
            "bulk_first_kg": next(iter(series["bulk"].values())),
            "bulk_last_kg": list(series["bulk"].values())[-1],
            "bulk_min_kg": min(series["bulk"].values()),
            "bulk_max_kg": max(series["bulk"].values()),
            "bulk_source": series["bulk_source"],
            "film_points": len(series["film"]),
            "film_native_range": [min(series["film"]), max(series["film"])]
            if series["film"]
            else None,
            "film_first_kg": next(iter(series["film"].values()))
            if series["film"]
            else None,
            "film_last_kg": list(series["film"].values())[-1]
            if series["film"]
            else None,
            "film_min_kg": min(series["film"].values()) if series["film"] else None,
            "film_max_kg": max(series["film"].values()) if series["film"] else None,
            "film_source": series["film_source"],
        }
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
    print(f"Bulk-history overlays (within {OVERLAY_TOLERANCE_KG:g} kg): {overlay_groups}")


def source_text(source: Any) -> str:
    if source is None:
        return "no EWF film report (EWF disabled)"
    if isinstance(source, str):
        return source
    if isinstance(source, dict):
        return json.dumps(source, sort_keys=True, separators=(",", ":"))
    return str(source)


def sanitize_paths(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_paths(item) for item in value]
    if isinstance(value, str):
        normalized = value.replace("\\", "/")
        prefix = FLUENT_RUNS.as_posix().rstrip("/") + "/"
        if normalized.lower().startswith(prefix.lower()):
            return "FluentRuns/Phase72A/FamilyE/" + normalized[len(prefix) :]
    return value


def main() -> None:
    write_artifacts(load_cases())


if __name__ == "__main__":
    main()

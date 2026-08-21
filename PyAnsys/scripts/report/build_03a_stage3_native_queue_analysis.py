#!/usr/bin/env python3
"""Build an offline Stage-3 analysis for the selected native queue branches.

The builder is deliberately evidence-first.  It reads the preserved checkpoint
CSV, the existing paired-readback JSON files, and the residual-export probe
manifest.  It never connects to Fluent, loads a case, changes a setting, or
fills a missing history.  Endpoint values are plotted as endpoint values; a
line through staged points is labelled as a guide to the eye rather than a
continuous monitor history.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = (
    PROJECT_ROOT
    / ".."
    / "Setups"
    / "reports"
    / "full-geometry"
    / "mixture"
    / "steady-liquid-outlet"
    / "03a"
).resolve()
DEFAULT_CHECKPOINT_CSV = REPORT_ROOT / "03a-stage3-results-20260821-checkpoints.csv"
DEFAULT_RUN_DIR = (
    PROJECT_ROOT
    / "output"
    / "03A-stage3"
    / "override-fixed3000-native-server2"
    / "20260820T013223Z"
)
DEFAULT_READBACK_DIR = DEFAULT_RUN_DIR / "post_simulation_analysis"
DEFAULT_EVIDENCE_DIR = REPORT_ROOT / "evidence" / "03a-stage3-native-queue"
DEFAULT_PLOT_DIR = REPORT_ROOT / "plots" / "03a-stage3" / "native-queue"
DEFAULT_ARTIFACT_MANIFEST = DEFAULT_EVIDENCE_DIR / "03a-stage3-local-artifact-discovery.json"

BRANCH_ORDER = ("F02", "F04", "F05", "F06", "F11")
EXPECTED_RESIDUALS = (
    "continuity",
    "x-velocity",
    "y-velocity",
    "z-velocity",
    "k",
    "epsilon",
    "vf-phase-2",
)
PRESSURE_REFERENCE_PA = 1_120_000.0

BRANCH_META: dict[str, dict[str, Any]] = {
    "F02": {
        "mixture_startup": "carrier-first",
        "inlet_schedule": "100% immediately",
        "momentum_urf": 0.7,
        "status": "PARTIAL",
        "native_iterations": 0,
        "full_mixture_100pct_iterations": 0,
        "terminal_note": "Carrier 100% native stage ended before its named endpoint pair.",
    },
    "F04": {
        "mixture_startup": "carrier-first",
        "inlet_schedule": "100% immediately",
        "momentum_urf": 0.5,
        "status": "PARTIAL",
        "native_iterations": 0,
        "full_mixture_100pct_iterations": 0,
        "terminal_note": "Carrier 100% native stage ended before its named endpoint pair.",
    },
    "F05": {
        "mixture_startup": "full Mixture immediately",
        "inlet_schedule": "100% immediately",
        "momentum_urf": 0.3,
        "status": "COMPLETED",
        "native_iterations": 3000,
        "full_mixture_100pct_iterations": 3000,
        "terminal_note": "One full-Mixture 100% native stage completed.",
    },
    "F06": {
        "mixture_startup": "carrier-first, then full Mixture",
        "inlet_schedule": "100% immediately",
        "momentum_urf": 0.3,
        "status": "COMPLETED",
        "native_iterations": 6000,
        "full_mixture_100pct_iterations": 3000,
        "terminal_note": "Carrier 100% stage and no-reinitialization full-Mixture 100% stage completed.",
    },
    "F11": {
        "mixture_startup": "full Mixture immediately",
        "inlet_schedule": "10 → 20 → 40 → 80 → 100%",
        "momentum_urf": 0.3,
        "status": "COMPLETED",
        "native_iterations": 15000,
        "full_mixture_100pct_iterations": 3000,
        "terminal_note": "Five 3,000-iteration full-Mixture loading stages completed.",
    },
}

NUMERIC_COLUMNS = (
    "iteration",
    "load_percent",
    "momentum_urf",
    "total_inlet_kg_s",
    "total_outlet_kg_s",
    "liquid_inlet_kg_s",
    "vapour_inlet_kg_s",
    "liquid_to_brine_kg_s",
    "liquid_to_steam_kg_s",
    "vapour_to_brine_kg_s",
    "vapour_to_steam_kg_s",
    "mass_imbalance_signed_pct",
    "mass_imbalance_abs_pct",
    "liquid_closure_pct",
    "vapour_closure_pct",
    "liquid_inventory_total_kg",
    "liquid_inventory_y030_kg",
    "liquid_inventory_y010_kg",
    "brine_entry_static_pressure_pa",
    "brine_entry_total_pressure_pa",
    "brine_entry_pressure_margin_pa",
)

CROSS_FIELDS = {
    "total_inlet_kg_s": "m_mix_in",
    "total_outlet_kg_s": "m_mix_out",
    "liquid_inlet_kg_s": "m_liq_in",
    "vapour_inlet_kg_s": "m_vap_in",
    "liquid_to_brine_kg_s": "m_liq_to_brine",
    "liquid_to_steam_kg_s": "m_liq_steam_out",
    "vapour_to_brine_kg_s": "m_vap_to_brine",
    "vapour_to_steam_kg_s": "m_vap_steam_out",
    "liquid_inventory_total_kg": "inventory_total",
    "liquid_inventory_y030_kg": "inventory_y030",
    "liquid_inventory_y010_kg": "inventory_y010",
    "brine_entry_static_pressure_pa": "pressure_static",
    "brine_entry_total_pressure_pa": "pressure_total",
}


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


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT.parent.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_checkpoint_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        source_rows = list(csv.DictReader(handle))

    rows: list[dict[str, Any]] = []
    for source in source_rows:
        branch = str(source.get("branch", ""))
        if branch not in BRANCH_ORDER or source.get("solver_state") != "full-mixture":
            continue
        row: dict[str, Any] = dict(source)
        for column in NUMERIC_COLUMNS:
            parsed = finite_float(source.get(column))
            if parsed is None:
                raise ValueError(f"Missing/non-finite {column} for {branch}")
            row[column] = int(parsed) if column in {"iteration", "load_percent"} else parsed

        liquid_in = row["liquid_inlet_kg_s"]
        vapour_in = row["vapour_inlet_kg_s"]
        row.update(
            {
                "total_brine_outlet_kg_s": row["liquid_to_brine_kg_s"]
                + row["vapour_to_brine_kg_s"],
                "total_steam_outlet_kg_s": row["liquid_to_steam_kg_s"]
                + row["vapour_to_steam_kg_s"],
                "liquid_to_brine_fraction_pct": (
                    100.0 * row["liquid_to_brine_kg_s"] / liquid_in if liquid_in else None
                ),
                "liquid_to_steam_fraction_pct": (
                    100.0 * row["liquid_to_steam_kg_s"] / liquid_in if liquid_in else None
                ),
                "vapour_to_brine_fraction_pct": (
                    100.0 * row["vapour_to_brine_kg_s"] / vapour_in if vapour_in else None
                ),
                "vapour_to_steam_fraction_pct": (
                    100.0 * row["vapour_to_steam_kg_s"] / vapour_in if vapour_in else None
                ),
                "brine_entry_static_pressure_margin_kpa": row[
                    "brine_entry_pressure_margin_pa"
                ]
                / 1000.0,
                "brine_entry_total_pressure_margin_kpa": (
                    row["brine_entry_total_pressure_pa"] - PRESSURE_REFERENCE_PA
                )
                / 1000.0,
                "full_mixture_stage_iterations": 3000,
            }
        )
        rows.append(row)

    rows.sort(key=lambda item: (BRANCH_ORDER.index(item["branch"]), item["iteration"]))
    return rows


def parsed_report_value(payload: dict[str, Any], name: str) -> float | None:
    try:
        value = payload["existing_scalar_reports"][name]["parsed"]["value"]
    except (KeyError, TypeError):
        return None
    return finite_float(value)


def readback_metrics(payload: dict[str, Any]) -> dict[str, float | None]:
    carrier = payload.get("carrier_metrics", {})
    by_domain = payload.get("carrier_fluxes", {}).get("by_domain", {})
    phase_1 = by_domain.get("phase-1", {})
    phase_2 = by_domain.get("phase-2", {})

    def number(mapping: dict[str, Any], key: str) -> float | None:
        return finite_float(mapping.get(key))

    def outlet_magnitude(mapping: dict[str, Any], key: str) -> float | None:
        value = number(mapping, key)
        return abs(value) if value is not None else None

    return {
        "m_mix_in": number(carrier, "m_mix_in"),
        "m_mix_out": number(carrier, "m_mix_out"),
        "m_liq_in": number(carrier, "m_liq_in"),
        "m_vap_in": number(carrier, "m_vap_in"),
        "m_liq_to_brine": outlet_magnitude(phase_2, "brineoutlet"),
        "m_liq_steam_out": outlet_magnitude(phase_2, "steamoutlet"),
        "m_vap_to_brine": outlet_magnitude(phase_1, "brineoutlet"),
        "m_vap_steam_out": outlet_magnitude(phase_1, "steamoutlet"),
        "inventory_total": parsed_report_value(
            payload, "03a_stage3_inventory_total_liquid_mass"
        ),
        "inventory_y030": parsed_report_value(
            payload, "03a_stage3_inventory_y030_liquid_mass"
        ),
        "inventory_y010": parsed_report_value(
            payload, "03a_stage3_inventory_y010_liquid_mass"
        ),
        "pressure_static": parsed_report_value(
            payload, "03a_stage3_brine_entry_static_pressure"
        ),
        "pressure_total": parsed_report_value(
            payload, "03a_stage3_brine_entry_total_pressure"
        ),
        "inventory_total_volume_m3": parsed_report_value(
            payload, "03a_stage3_inventory_total_liquid_volume"
        ),
    }


def checkpoint_key(branch: str, load_percent: int) -> tuple[str, int]:
    return branch, int(load_percent)


def load_readbacks(path: Path) -> dict[tuple[str, int], dict[str, Any]]:
    readbacks: dict[tuple[str, int], dict[str, Any]] = {}
    for file_path in sorted(path.glob("*-readback.json")):
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        branch = str(payload.get("branch", ""))
        checkpoint = str(payload.get("checkpoint", ""))
        match = re.search(r"-(\d+)pct-end", checkpoint)
        if branch not in BRANCH_ORDER or not match:
            continue
        payload["_file_name"] = file_path.name
        payload["_metrics"] = readback_metrics(payload)
        readbacks[checkpoint_key(branch, int(match.group(1)))] = payload
    return readbacks


def cross_validate(
    rows: Iterable[dict[str, Any]], readbacks: dict[tuple[str, int], dict[str, Any]]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for row in rows:
        key = checkpoint_key(row["branch"], row["load_percent"])
        payload = readbacks.get(key)
        if payload is None:
            results.append(
                {
                    "branch": row["branch"],
                    "load_percent": row["load_percent"],
                    "iteration": row["iteration"],
                    "status": "readback_not_found",
                    "max_abs_difference": None,
                    "differences_json": "{}",
                    "readback_file": None,
                }
            )
            continue

        metrics = payload["_metrics"]
        differences: dict[str, float | None] = {}
        for csv_name, json_name in CROSS_FIELDS.items():
            csv_value = finite_float(row.get(csv_name))
            json_value = finite_float(metrics.get(json_name))
            differences[csv_name] = (
                abs(csv_value - json_value)
                if csv_value is not None and json_value is not None
                else None
            )
        finite_differences = [value for value in differences.values() if value is not None]
        maximum = max(finite_differences) if finite_differences else None
        results.append(
            {
                "branch": row["branch"],
                "load_percent": row["load_percent"],
                "iteration": row["iteration"],
                "status": "within_rounding" if maximum is not None and maximum <= 1e-3 else "discrepancy",
                "max_abs_difference": maximum,
                "differences_json": json.dumps(differences, sort_keys=True),
                "readback_file": payload["_file_name"],
            }
        )
    return results


def load_event_residual_points(run_dir: Path) -> dict[tuple[str, str], dict[str, float]]:
    event_file = run_dir / "native-fixed-3000-events.jsonl"
    points: dict[tuple[str, str], dict[str, float]] = {}
    if not event_file.exists():
        return points
    for line in event_file.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("kind") != "native_pair_verified":
            continue
        branch = str(event.get("branch", ""))
        stage = str(event.get("stage", ""))
        residuals = event.get("snapshot", {}).get("residuals")
        if branch not in BRANCH_ORDER or not isinstance(residuals, dict) or not residuals:
            continue
        finite = {
            str(name): float(value)
            for name, value in residuals.items()
            if finite_float(value) is not None
        }
        if finite:
            points[(branch, stage)] = finite
    return points


def load_submitted_stages(run_dir: Path) -> list[dict[str, Any]]:
    """Recover every native stage submitted for the selected branches."""
    event_file = run_dir / "native-fixed-3000-events.jsonl"
    stages: dict[tuple[str, str], dict[str, Any]] = {}
    if not event_file.exists():
        return []
    for line in event_file.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("kind") != "native_stage_submit":
            continue
        branch = str(event.get("branch", ""))
        stage = str(event.get("stage", ""))
        if branch not in BRANCH_ORDER or not stage:
            continue
        key = (branch, stage)
        stages.setdefault(
            key,
            {
                "branch": branch,
                "stage": stage,
                "remote_file": event.get("residual_export"),
                "exists": False,
                "status": "not_probed",
            },
        )
    return list(stages.values())


def load_residual_status(run_dir: Path) -> dict[str, Any]:
    probe_dir = run_dir / "post_simulation_analysis" / "native_residual_exports"
    download_index_path = probe_dir / "download-index.json"
    download_payload: dict[str, Any] = {}
    if download_index_path.exists():
        download_payload = json.loads(download_index_path.read_text(encoding="utf-8"))

    event_points = load_event_residual_points(run_dir)
    stages_by_key = {
        (stage.get("branch"), stage.get("stage")): dict(stage)
        for stage in load_submitted_stages(run_dir)
    }
    for stage in download_payload.get("stages", []):
        key = (stage.get("branch"), stage.get("stage"))
        merged = stages_by_key.setdefault(key, {})
        merged.update(stage)
    stages = list(stages_by_key.values())

    def stage_sort_key(stage: dict[str, Any]) -> tuple[int, int, str]:
        name = str(stage.get("stage", ""))
        load_match = re.search(r"-(\d+)pct", name)
        load = int(load_match.group(1)) if load_match else -1
        carrier_first = 0 if name.startswith("carrier-") else 1
        return BRANCH_ORDER.index(stage.get("branch", "F02")), carrier_first, load

    stages.sort(key=stage_sort_key)
    statuses: list[dict[str, Any]] = []
    for stage in stages:
        branch = str(stage.get("branch", ""))
        stage_name = str(stage.get("stage", ""))
        probe_name = f"{branch}-{stage_name}-end-residual-probe.json"
        probe_path = run_dir / "post_simulation_analysis" / probe_name
        if not probe_path.exists():
            probe_name = f"{branch}-{stage_name}-residual-probe.json"
            probe_path = run_dir / "post_simulation_analysis" / probe_name
        retained_available = False
        retained_warning = "No retained residual monitor was found in the paired endpoint probe."
        if probe_path.exists():
            probe_payload = json.loads(probe_path.read_text(encoding="utf-8"))
            history = probe_payload.get("residual_history", {})
            retained_available = bool(history.get("available"))
            warnings = history.get("warnings") or []
            if warnings:
                retained_warning = "; ".join(str(item) for item in warnings)

        point = event_points.get((branch, stage_name), {})
        statuses.append(
            {
                "branch": branch,
                "stage": stage_name,
                "native_export_exists": bool(stage.get("exists")),
                "native_export_status": stage.get("status", "not_probed"),
                "retained_residual_monitor_available": retained_available,
                "retained_residual_monitor_note": retained_warning,
                "endpoint_residual_point_available": bool(point),
                "endpoint_residual_point": point,
                "probe_file": probe_name if probe_path.exists() else None,
            }
        )

    return {
        "kind": "03a_stage3_residual_evidence_status",
        "expected_equations": list(EXPECTED_RESIDUALS),
        "history_status": "unavailable",
        "history_status_reason": (
            "The supported native residual-export probe recorded every expected "
            "export as missing; paired endpoint probes found no retained residual "
            "monitor. One F05 endpoint retained instantaneous residual values only."
        ),
        "stages": statuses,
        "source_probe": relative_path(download_index_path),
    }


def report_history_status(run_dir: Path, artifact_manifest_path: Path | None = None) -> dict[str, Any]:
    """Describe the report-file history evidence without inventing history."""
    local_out_files = sorted(
        path.name
        for path in run_dir.rglob("*.out")
        if path.is_file()
    ) if run_dir.exists() else []
    manifest: dict[str, Any] | None = None
    if artifact_manifest_path is not None and artifact_manifest_path.exists():
        try:
            manifest = json.loads(artifact_manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            manifest = None

    if manifest is not None:
        observations = manifest.get("observations", {})
        stage3_count = observations.get("stage3_report_file_count", 0)
        stage3_unique = observations.get("stage3_report_canonical_name_count", 0)
        return {
            "kind": "03a_stage3_report_history_evidence_status",
            "status": "found_unmapped_local_artifacts",
            "continuous_history_status": "unavailable",
            "method": "PyAnsys/scripts/report/discover_03a_stage3_artifacts.py",
            "local_stage3_out_files": local_out_files,
            "discovered_stage3_out_file_count": stage3_count,
            "discovered_stage3_out_canonical_name_count": stage3_unique,
            "artifact_discovery_manifest": relative_path(artifact_manifest_path),
            "artifact_discovery_status": manifest.get("artifact_status"),
            "server2_fixed_queue_history_usable": bool(
                manifest.get("server2_fixed_queue_history_usable", False)
            ),
            "reason": (
                f"The recursive local artifact discovery found {stage3_count} Stage-3-named "
                f".out files ({stage3_unique} canonical report names), but their filenames "
                "do not carry the server-2 fixed-queue run stamp or branch token. They are "
                "discovery evidence only; no late-window history is attributed to F02/F04/"
                "F05/F06/F11."
            ),
            "requires": "positive run/branch lineage or read-only remote Fluent/report-file access; no rerun is implied",
        }

    return {
        "kind": "03a_stage3_report_history_evidence_status",
        "status": "unavailable",
        "continuous_history_status": "unavailable",
        "method": "PyAnsys/scripts/inspection/extract_report_plot_histories.py",
        "local_stage3_out_files": local_out_files,
        "reason": (
            "No Stage-3 native .out report histories are present in the local evidence "
            "bundle. The current read-only Fluent reachability check timed out, so the "
            "extractor could not inspect or recover the remote report files. Existing "
            "endpoint readbacks establish report-definition names and scalar values, "
            "not continuous history arrays."
        ),
        "requires": "remote Fluent/report-file access; no rerun is implied",
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_derived_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "branch",
        "run_stamp",
        "iteration",
        "load_percent",
        "momentum_urf",
        "evidence_status",
        "total_inlet_kg_s",
        "total_outlet_kg_s",
        "total_brine_outlet_kg_s",
        "total_steam_outlet_kg_s",
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
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})


def write_cross_validation_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "branch",
        "load_percent",
        "iteration",
        "status",
        "max_abs_difference",
        "readback_file",
        "differences_json",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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


def stage_markers(axis: Any, f11_rows: list[dict[str, Any]]) -> None:
    colors = {10: "#94a3b8", 20: "#64748b", 40: "#475569", 80: "#334155", 100: "#0f172a"}
    for row in f11_rows:
        x_value = row["iteration"]
        axis.axvline(x_value, color=colors.get(row["load_percent"], "#64748b"), alpha=0.16)
        axis.text(
            x_value,
            0.98,
            f"{row['load_percent']}%",
            transform=axis.get_xaxis_transform(),
            rotation=90,
            va="top",
            ha="right",
            fontsize=7,
            color=colors.get(row["load_percent"], "#64748b"),
        )


def plot_stage_lines(axis: Any, rows: list[dict[str, Any]], y_key: str, ylabel: str) -> None:
    f11_rows = [row for row in rows if row["branch"] == "F11"]
    final_rows = [row for row in rows if row["branch"] in {"F05", "F06"}]
    if f11_rows:
        axis.plot(
            [row["iteration"] for row in f11_rows],
            [row[y_key] for row in f11_rows],
            marker="o",
            color="#2563eb",
            label="F11 staged endpoints",
        )
        stage_markers(axis, f11_rows)
    for branch, color in (("F05", "#dc2626"), ("F06", "#16a34a")):
        branch_rows = [row for row in final_rows if row["branch"] == branch]
        if branch_rows:
            axis.scatter(
                [row["iteration"] for row in branch_rows],
                [row[y_key] for row in branch_rows],
                color=color,
                marker="D",
                s=42,
                label=branch,
                zorder=4,
            )
    axis.set_xlabel("Cumulative native iterations (endpoint checkpoints)")
    axis.set_ylabel(ylabel)
    axis.grid(True, alpha=0.25)


def build_figures(rows: list[dict[str, Any]], residual_status: dict[str, Any], plot_dir: Path) -> list[str]:
    plt = configure_plotting()
    plot_dir.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []

    # Figure 1 is an evidence-availability matrix, not a fabricated residual plot.
    stages = residual_status["stages"]
    labels = [f"{stage['branch']} {stage['stage']}" for stage in stages]
    values = []
    text_values = []
    for stage in stages:
        export_value = 1 if stage["native_export_exists"] else 0
        monitor_value = 1 if stage["retained_residual_monitor_available"] else 0
        point_value = 1 if stage["endpoint_residual_point_available"] else 0
        values.append([export_value, monitor_value, point_value])
        export_text = "available" if export_value else (
            "missing" if stage["native_export_status"] == "missing" else "not probed"
        )
        text_values.append(
            [
                export_text,
                "available" if monitor_value else "absent",
                "point" if point_value else "none",
            ]
        )
    figure, axis = plt.subplots(figsize=(8.6, max(3.2, 0.38 * len(labels) + 1.7)))
    image = axis.imshow(values, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    axis.set_xticks(range(3), ["native export", "retained monitor", "endpoint point"])
    axis.set_yticks(range(len(labels)), labels)
    axis.set_title("Figure 1 — residual evidence availability (not a residual history)")
    for row_index, row_text in enumerate(text_values):
        for column_index, text in enumerate(row_text):
            axis.text(column_index, row_index, text, ha="center", va="center", fontsize=8)
    axis.set_xlabel("No continuous residual series is available for plotting in this scope")
    figure.colorbar(image, ax=axis, fraction=0.025, pad=0.02, ticks=[0, 1], label="evidence present")
    figure.tight_layout()
    path = plot_dir / "figure-01-residual-evidence-status.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    # Figure 2 — primary physical convergence evidence.
    figure, axes = plt.subplots(3, 1, figsize=(9.4, 10.0), sharex=True)
    plot_stage_lines(axes[0], rows, "total_inlet_kg_s", "Mass flow (kg/s)")
    axes[0].plot([], [], color="#111827", label="total inlet/outlet")
    f11 = [row for row in rows if row["branch"] == "F11"]
    axes[0].plot(
        [row["iteration"] for row in f11],
        [row["total_outlet_kg_s"] for row in f11],
        marker="s",
        color="#111827",
        label="F11 total outlet",
    )
    for branch, color in (("F05", "#dc2626"), ("F06", "#16a34a")):
        subset = [row for row in rows if row["branch"] == branch]
        axes[0].scatter(
            [row["iteration"] for row in subset],
            [row["total_outlet_kg_s"] for row in subset],
            color=color,
            marker="s",
            s=36,
            zorder=4,
        )
    axes[0].legend(ncol=3, loc="upper left")
    plot_stage_lines(axes[1], rows, "mass_imbalance_signed_pct", "Signed mass imbalance (%)")
    axes[1].axhline(0.0, color="#111827", linewidth=0.8)
    plot_stage_lines(axes[2], rows, "liquid_inventory_total_kg", "Total liquid inventory (kg)")
    axes[2].legend(ncol=3, loc="upper right")
    axes[2].set_xlim(left=0)
    figure.suptitle("Figure 2 — primary physical endpoint evidence", y=0.995)
    figure.text(
        0.5,
        0.005,
        "Only confirmed endpoint measurements are shown; connecting lines are guides to the eye, not continuous histories.",
        ha="center",
        fontsize=8,
    )
    figure.tight_layout(rect=(0, 0.02, 1, 0.98))
    path = plot_dir / "figure-02-primary-physical-endpoints.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    # Figure 3 — phase routing.
    figure, axes = plt.subplots(2, 1, figsize=(9.4, 7.8), sharex=True)
    for axis, series, title in (
        (
            axes[0],
            (("liquid_to_brine_kg_s", "liquid → brine", "#2563eb"), ("vapour_to_brine_kg_s", "vapour → brine", "#dc2626")),
            "Brine outlet routing",
        ),
        (
            axes[1],
            (("liquid_to_steam_kg_s", "liquid → steam", "#16a34a"), ("vapour_to_steam_kg_s", "vapour → steam", "#9333ea")),
            "Steam outlet routing",
        ),
    ):
        for key, label, color in series:
            subset = [row for row in rows if row["branch"] == "F11"]
            axis.plot(
                [row["iteration"] for row in subset],
                [row[key] for row in subset],
                marker="o",
                color=color,
                label=f"F11 {label}",
            )
            for branch, marker in (("F05", "D"), ("F06", "s")):
                endpoint = [row for row in rows if row["branch"] == branch]
                axis.scatter(
                    [row["iteration"] for row in endpoint],
                    [row[key] for row in endpoint],
                    color=color,
                    marker=marker,
                    s=35,
                    alpha=0.8,
                )
        stage_markers(axis, f11)
        axis.set_ylabel("Flow (kg/s)")
        axis.set_title(title)
        axis.grid(True, alpha=0.25)
        axis.legend(ncol=2, loc="upper right")
    axes[1].set_xlabel("Cumulative native iterations (endpoint checkpoints)")
    figure.suptitle("Figure 3 — phase routing at selected endpoints", y=0.995)
    figure.text(0.5, 0.005, "Routing is diagnostic evidence, not the Stage-3 pass/fail metric.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.98))
    path = plot_dir / "figure-03-phase-routing-endpoints.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    # Figure 4 — liquid distribution.
    figure, axes = plt.subplots(2, 1, figsize=(9.4, 7.8), sharex=True)
    for key, label, color in (
        ("liquid_inventory_total_kg", "total liquid", "#111827"),
        ("liquid_inventory_y030_kg", "Y030", "#2563eb"),
        ("liquid_inventory_y010_kg", "Y010", "#dc2626"),
    ):
        subset = [row for row in rows if row["branch"] == "F11"]
        axes[0].plot([row["iteration"] for row in subset], [row[key] for row in subset], marker="o", label=f"F11 {label}", color=color)
        for branch, marker in (("F05", "D"), ("F06", "s")):
            endpoint = [row for row in rows if row["branch"] == branch]
            axes[0].scatter([row["iteration"] for row in endpoint], [row[key] for row in endpoint], color=color, marker=marker, s=35)
    axes[0].set_ylabel("Liquid mass (kg)")
    axes[0].set_title("Liquid inventory")
    axes[0].legend(ncol=3, loc="upper right")
    axes[0].grid(True, alpha=0.25)
    for key, label, color in (
        ("liquid_inventory_y030_kg", "Y030 / total", "#2563eb"),
        ("liquid_inventory_y010_kg", "Y010 / total", "#dc2626"),
    ):
        subset = [row for row in rows if row["branch"] == "F11"]
        axes[1].plot(
            [row["iteration"] for row in subset],
            [100.0 * row[key] / row["liquid_inventory_total_kg"] for row in subset],
            marker="o",
            label=f"F11 {label}",
            color=color,
        )
    axes[1].set_ylabel("Inventory share (%)")
    axes[1].set_xlabel("Cumulative native iterations (endpoint checkpoints)")
    axes[1].set_title("Distribution within the reported liquid inventory")
    axes[1].legend(loc="upper right")
    axes[1].grid(True, alpha=0.25)
    for axis in axes:
        stage_markers(axis, f11)
    figure.suptitle("Figure 4 — liquid inventory and distribution", y=0.995)
    figure.text(0.5, 0.005, "Zone inventories are endpoint measurements; geometric register volumes are constants and are not plotted.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.98))
    path = plot_dir / "figure-04-liquid-distribution-endpoints.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    # Figure 5 — pressure response.
    figure, axes = plt.subplots(2, 1, figsize=(9.4, 7.8), sharex=True)
    for key, label, color in (
        ("brine_entry_static_pressure_margin_kpa", "static margin", "#2563eb"),
        ("brine_entry_total_pressure_margin_kpa", "total-pressure margin", "#dc2626"),
    ):
        subset = [row for row in rows if row["branch"] == "F11"]
        axes[0].plot([row["iteration"] for row in subset], [row[key] for row in subset], marker="o", label=f"F11 {label}", color=color)
        for branch, marker in (("F05", "D"), ("F06", "s")):
            endpoint = [row for row in rows if row["branch"] == branch]
            axes[0].scatter([row["iteration"] for row in endpoint], [row[key] for row in endpoint], color=color, marker=marker, s=35)
    axes[0].axhline(0.0, color="#111827", linewidth=0.8)
    axes[0].set_ylabel("Pressure margin (kPa)")
    axes[0].set_title("Brine-entry pressure margins relative to 1.120 MPa gauge")
    axes[0].legend(ncol=2, loc="upper left")
    axes[0].grid(True, alpha=0.25)
    for key, label, color in (
        ("total_brine_outlet_kg_s", "total brine outlet", "#111827"),
        ("liquid_to_brine_kg_s", "liquid → brine", "#16a34a"),
    ):
        subset = [row for row in rows if row["branch"] == "F11"]
        axes[1].plot([row["iteration"] for row in subset], [row[key] for row in subset], marker="o", label=f"F11 {label}", color=color)
        for branch, marker in (("F05", "D"), ("F06", "s")):
            endpoint = [row for row in rows if row["branch"] == branch]
            axes[1].scatter([row["iteration"] for row in endpoint], [row[key] for row in endpoint], color=color, marker=marker, s=35)
    axes[1].set_ylabel("Flow (kg/s)")
    axes[1].set_xlabel("Cumulative native iterations (endpoint checkpoints)")
    axes[1].set_title("Brine outlet flow")
    axes[1].legend(ncol=2, loc="upper left")
    axes[1].grid(True, alpha=0.25)
    for axis in axes:
        stage_markers(axis, f11)
    figure.suptitle("Figure 5 — brine-entry hydraulic response", y=0.995)
    figure.text(0.5, 0.005, "The cross-plot interpretation is intentionally not treated as time-domain causality.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.98))
    path = plot_dir / "figure-05-brine-entry-response.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    # Figure 6 — deliberate F11 loading response.
    figure, axes = plt.subplots(2, 2, figsize=(10.0, 7.8))
    ramp_metrics = (
        ("mass_imbalance_abs_pct", "absolute mass imbalance (%)"),
        ("liquid_inventory_total_kg", "total liquid inventory (kg)"),
        ("brine_entry_static_pressure_margin_kpa", "static pressure margin (kPa)"),
        ("total_outlet_kg_s", "total outlet flow (kg/s)"),
    )
    for axis, (key, label) in zip(axes.flat, ramp_metrics):
        axis.plot([row["load_percent"] for row in f11], [row[key] for row in f11], marker="o", color="#2563eb")
        axis.set_xlabel("Imposed inlet loading (%)")
        axis.set_ylabel(label)
        axis.set_xticks([10, 20, 40, 80, 100])
        axis.grid(True, alpha=0.25)
    figure.suptitle("Figure 6 — F11 progressive-loading endpoint response", y=0.995)
    figure.text(0.5, 0.005, "Each point is the end of a confirmed 3,000-iteration loading stage; no interpolation is applied.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.02, 1, 0.98))
    path = plot_dir / "figure-06-progressive-loading-response.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    # Figure 7 — matched 100% endpoints.
    matched = [row for row in rows if row["branch"] in {"F05", "F06", "F11"} and row["load_percent"] == 100]
    matched.sort(key=lambda row: ("F05", "F06", "F11").index(row["branch"]))
    labels = [row["branch"] for row in matched]
    figure, axes = plt.subplots(1, 3, figsize=(10.0, 4.4))
    matched_metrics = (
        ("mass_imbalance_abs_pct", "absolute imbalance (%)"),
        ("liquid_inventory_total_kg", "total liquid inventory (kg)"),
        ("brine_entry_static_pressure_margin_kpa", "static margin (kPa)"),
    )
    colors = ["#dc2626", "#16a34a", "#2563eb"]
    for axis, (key, label) in zip(axes, matched_metrics):
        axis.bar(labels, [row[key] for row in matched], color=colors)
        axis.set_ylabel(label)
        axis.grid(axis="y", alpha=0.25)
        for index, row in enumerate(matched):
            axis.text(index, row[key], f"{row[key]:.3g}", ha="center", va="bottom", fontsize=8)
    figure.suptitle("Figure 7 — matched full-Mixture 100% endpoint comparison", y=0.995)
    figure.text(0.5, 0.005, "All three endpoints have 3,000 full-Mixture 100% iterations; residual-envelope comparison is unavailable.", ha="center", fontsize=8)
    figure.tight_layout(rect=(0, 0.04, 1, 0.96))
    path = plot_dir / "figure-07-matched-100pct-comparison.png"
    save_figure(figure, path)
    generated.append(relative_path(path))

    return generated


def main() -> int:
    args = build_parser().parse_args()
    checkpoint_csv = args.checkpoint_csv.expanduser().resolve()
    run_dir = args.run_dir.expanduser().resolve()
    readback_dir = args.readback_dir.expanduser().resolve()
    evidence_dir = args.evidence_dir.expanduser().resolve()
    plot_dir = args.plot_dir.expanduser().resolve()
    artifact_manifest = args.artifact_manifest.expanduser().resolve()

    rows = load_checkpoint_rows(checkpoint_csv)
    readbacks = load_readbacks(readback_dir)
    validation_rows = cross_validate(rows, readbacks)
    residual_status = load_residual_status(run_dir)

    derived_csv = evidence_dir / "03a-stage3-native-queue-checkpoints.csv"
    validation_csv = evidence_dir / "03a-stage3-native-queue-cross-validation.csv"
    residual_json = evidence_dir / "03a-stage3-native-queue-residual-evidence.json"
    report_history_json = evidence_dir / "03a-stage3-native-queue-report-history-evidence.json"
    summary_json = evidence_dir / "03a-stage3-native-queue-analysis.json"
    write_derived_csv(derived_csv, rows)
    write_cross_validation_csv(validation_csv, validation_rows)
    write_json(residual_json, residual_status)
    report_history = report_history_status(run_dir, artifact_manifest)
    write_json(report_history_json, report_history)

    figures = [] if args.no_plots else build_figures(rows, residual_status, plot_dir)
    summary = {
        "kind": "03a_stage3_native_queue_analysis",
        "scope": {
            "run_stamp": "20260820T013223Z",
            "branches": list(BRANCH_ORDER),
            "case_identity_basis": "explicit checkpoint case/data filenames plus immutable P0 SHA-256 recorded in the execution evidence",
            "analysis_mode": "offline read-only endpoint and checkpoint analysis",
            "interpretation_status": "pending user direction",
        },
        "branch_metadata": BRANCH_META,
        "checkpoint_count": len(rows),
        "readback_count": len(readbacks),
        "cross_validation": {
            "status_counts": {
                status: sum(1 for row in validation_rows if row["status"] == status)
                for status in sorted({row["status"] for row in validation_rows})
            },
            "tolerance": "max absolute difference <= 0.001 in source units; pressure values are rounded in the CSV",
        },
        "residual_history": {
            "status": residual_status["history_status"],
            "expected_equations": list(EXPECTED_RESIDUALS),
            "point_only_equations": sorted(
                {
                    equation
                    for stage in residual_status["stages"]
                    for equation in stage["endpoint_residual_point"]
                }
            ),
        },
        "report_history": report_history,
        "artifacts": {
            "source_checkpoint_csv": relative_path(checkpoint_csv),
            "derived_checkpoint_csv": relative_path(derived_csv),
            "cross_validation_csv": relative_path(validation_csv),
            "residual_evidence_json": relative_path(residual_json),
            "report_history_evidence_json": relative_path(report_history_json),
            "figures": figures,
        },
        "checkpoints": rows,
    }
    write_json(summary_json, summary)

    print(json.dumps({"summary": relative_path(summary_json), "figures": figures}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

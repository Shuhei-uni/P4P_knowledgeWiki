#!/usr/bin/env python3
"""Audit terminal setup-07 overnight evidence and emit JSON/Markdown results."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)
MEETING_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
WIKI_ROOT = PROJECT_ROOT.parent / "ResearchProject_wiki" / "wiki"
SETUP_REPORT = (
    PROJECT_ROOT.parent
    / "Setup report"
    / "07e-split-inlet-adaptive-mass-balance-sink-control.md"
)


@dataclass
class Check:
    name: str
    status: str
    evidence: str


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def dpm_enabled(state: dict[str, Any]) -> bool:
    return bool(state.get("dpm_interaction", {}).get("state", {}).get("enabled"))


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Setup 07 Overnight Completion Audit",
        "",
        f"Generated: `{report['generated_at']}`  ",
        f"Overall: `{report['overall']}`  ",
        f"Terminal manifest: `{report['terminal']}`",
        "",
        "| Check | Status | Evidence |",
        "|---|---|---|",
    ]
    for item in report["checks"]:
        evidence = str(item["evidence"]).replace("|", "\\|")
        lines.append(f"| {item['name']} | `{item['status']}` | {evidence} |")
    lines.extend(
        [
            "",
            "This audit verifies numerical evidence preservation and reporting safety. A",
            "passing audit does not validate a physical brine outlet, separator efficiency,",
            "mesh independence, a free surface or physical-time accumulation.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    checks: list[Check] = []

    def add(name: str, condition: bool, evidence: str, *, pending: bool = False) -> None:
        status = "pending" if pending else ("pass" if condition else "fail")
        checks.append(Check(name, status, evidence))

    manifest_path = RUN_DIR / "qualification_manifest.json"
    manifest = load_json(manifest_path)
    terminal = manifest.get("status") == "completed"
    add(
        "terminal controller status",
        terminal,
        f"status={manifest.get('status')}; stop={manifest.get('stop_reason', '')}",
        pending=not terminal,
    )
    add(
        "scientific classification",
        terminal
        and any(
            word in str(manifest.get("classification", "")).lower()
            for word in ("diagnostic", "accepted")
        ),
        str(manifest.get("classification")),
        pending=not terminal,
    )
    add(
        "final sink ramp zero",
        float(manifest.get("ramp_after_run", float("nan"))) == 0.0,
        f"ramp_after_run={manifest.get('ramp_after_run')}",
        pending=not terminal,
    )
    add(
        "final DPM off",
        manifest.get("dpm_after_run") is False,
        f"dpm_after_run={manifest.get('dpm_after_run')}",
        pending=not terminal,
    )

    checkpoints = manifest.get("checkpoints", {})
    required = ("start_ramp0", "ramp_complete", "r1_1000", "r1_2000", "final")
    checkpoint_ok = all(
        key in checkpoints
        and checkpoints[key].get("case")
        and checkpoints[key].get("data")
        for key in required
    )
    add(
        "non-overwriting checkpoint set",
        checkpoint_ok,
        f"recorded={sorted(checkpoints)}; required={list(required)}",
        pending=not terminal and not checkpoint_ok,
    )

    controller_log = RUN_DIR / "controller.log"
    log_text = controller_log.read_text(encoding="utf-8", errors="replace")
    checkpoint_markers = {
        "start_ramp0": "saved_pair_start_from_prepared07c_fresh_hybrid_tau0p020_ramp0: VERIFIED",
        "ramp_complete": "saved_pair_ramp_complete_cumulative1000_r0p75: VERIFIED",
        "r1_1000": "saved_pair_r1_iter1000_cumulative2000: VERIFIED",
        "r1_2000": "saved_pair_r1_iter2000_cumulative3000: VERIFIED",
    }
    verified = [key for key, marker in checkpoint_markers.items() if marker in log_text]
    add(
        "checkpoint write verification markers",
        all(key in verified for key in checkpoint_markers),
        f"verified={verified}",
        pending=not terminal and len(verified) < len(checkpoint_markers),
    )
    final_case = str(checkpoints.get("final", {}).get("case", ""))
    final_stem = Path(final_case.replace("\\", "/")).name.replace(".cas.h5", "")
    final_marker = f"saved_pair_{final_stem}: VERIFIED" if final_stem else ""
    add(
        "final checkpoint write verified",
        bool(final_marker and final_marker in log_text),
        final_marker or "final checkpoint not recorded",
        pending=not terminal,
    )

    history_counts: dict[str, int] = {}
    histories_ok = True
    for name in (
        "physical_monitor_history.csv",
        "mass_balance_history.csv",
        "residual_history.csv",
    ):
        path = RUN_DIR / name
        count = csv_rows(path) if path.exists() else 0
        history_counts[name] = count
        histories_ok &= count > 0
    add("non-empty histories", histories_ok, json.dumps(history_counts, sort_keys=True))

    final_analysis_path = RUN_DIR / "QUALIFICATION_RESULT.json"
    final_analysis = load_json(final_analysis_path) if final_analysis_path.exists() else {}
    add(
        "terminal machine-readable analysis",
        bool(final_analysis.get("final"))
        and final_analysis.get("controller_status") == "completed",
        str(final_analysis_path),
        pending=not terminal or not final_analysis_path.exists(),
    )

    figures = tuple(range(14, 28))
    missing_figures: list[str] = []
    for number in figures:
        matches_png = list(MEETING_DIR.glob(f"{number:02d}_*.png"))
        matches_svg = list(MEETING_DIR.glob(f"{number:02d}_*.svg"))
        if not matches_png or not matches_svg:
            missing_figures.append(f"{number:02d}")
    add(
        "meeting figures 14-27 PNG/SVG",
        not missing_figures,
        f"missing={missing_figures}",
        pending=not terminal and bool(missing_figures),
    )

    dynamic_figure_numbers = (14, 15, 17, 19, 20, 21, 22, 23, 26, 27)
    stale_dynamic_figures: list[str] = []
    if terminal and final_analysis_path.exists():
        analysis_mtime = final_analysis_path.stat().st_mtime
        for number in dynamic_figure_numbers:
            matches = list(MEETING_DIR.glob(f"{number:02d}_*.png")) + list(
                MEETING_DIR.glob(f"{number:02d}_*.svg")
            )
            if not matches or any(path.stat().st_mtime < analysis_mtime for path in matches):
                stale_dynamic_figures.append(f"{number:02d}")
    add(
        "terminal dynamic figures regenerated after final analysis",
        terminal and final_analysis_path.exists() and not stale_dynamic_figures,
        f"figures={list(dynamic_figure_numbers)}; stale={stale_dynamic_figures}",
        pending=not terminal or not final_analysis_path.exists(),
    )

    visual_manifest_path = MEETING_DIR / "visual_manifest.json"
    visual_manifest = load_json(visual_manifest_path)
    artifacts = visual_manifest.get("artifacts", {})
    add(
        "visual manifest terminal artifacts",
        "setup07c_setup07e_liquid_field_comparison" in artifacts
        and "setup07c_setup07e_pressure_field_comparison" in artifacts,
        f"artifact_count={len(artifacts)}",
        pending=not terminal,
    )

    graphics_path = MEETING_DIR / "fluent" / "fluent_graphics_manifest.json"
    graphics = load_json(graphics_path)
    sink07e = graphics.get("states", {}).get("sink07e", {})
    restore = graphics.get("restore", {})
    graphics_ok = bool(
        sink07e
        and not dpm_enabled(sink07e)
        and graphics.get("postprocessing_only") is True
        and graphics.get("no_iterations_run") is True
        and graphics.get("dpm_update_run") is False
        and restore.get("ok") is True
        and restore.get("state", {}).get("key") == "sink07e_ramp_reset_final"
    )
    add(
        "Fluent graphics provenance and safe restore",
        graphics_ok,
        (
            f"sink07e={bool(sink07e)}; postprocessing_only={graphics.get('postprocessing_only')}; "
            f"restore={restore.get('state', {}).get('key')}; restore_ok={restore.get('ok')}"
        ),
        pending=not terminal,
    )

    documents = (
        SETUP_REPORT,
        PROJECT_ROOT.parent / "Setup report" / "order-dictionary.md",
        WIKI_ROOT / "progress" / "current-status.md",
        WIKI_ROOT / "progress" / "experiments.md",
        WIKI_ROOT / "model" / "validation.md",
        WIKI_ROOT / "progress" / "blockers.md",
        WIKI_ROOT / "log.md",
        MEETING_DIR / "MEETING_BRIEF.md",
        MEETING_DIR / "CHART_MAP.md",
        MEETING_DIR / "OVERNIGHT_HANDOFF.md",
        MEETING_DIR / "PRELIMINARY_BRINE_OUTLET_SIZING.md",
        MEETING_DIR / "BRINE_OUTLET_BOUNDARY_CONDITION_DECISION.md",
    )
    missing_docs = [str(path) for path in documents if not path.exists() or path.stat().st_size == 0]
    add("required documentation exists", not missing_docs, f"missing={missing_docs}")

    detailed_terminal_documents = (
        SETUP_REPORT,
        WIKI_ROOT / "progress" / "current-status.md",
        WIKI_ROOT / "progress" / "experiments.md",
        WIKI_ROOT / "model" / "validation.md",
        WIKI_ROOT / "log.md",
        MEETING_DIR / "MEETING_BRIEF.md",
        MEETING_DIR / "OVERNIGHT_HANDOFF.md",
    )
    summary_terminal_documents = (
        PROJECT_ROOT.parent / "Setup report" / "order-dictionary.md",
        WIKI_ROOT / "progress" / "blockers.md",
    )
    endpoint = final_analysis.get("endpoint", {}) if isinstance(final_analysis, dict) else {}
    sink = endpoint.get("sink_magnitude_kgs") if isinstance(endpoint, dict) else None
    sink_tokens = (
        {f"{float(sink):.4f}", f"{float(sink):.5f}", f"{float(sink):.6f}"}
        if sink is not None
        else set()
    )
    stale_detailed: list[str] = []
    stale_summary: list[str] = []
    if terminal and sink_tokens:
        for path in detailed_terminal_documents:
            content = path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""
            if "07e" not in content.lower() or not any(token in content for token in sink_tokens):
                stale_detailed.append(str(path))
        for path in summary_terminal_documents:
            content = path.read_text(encoding="utf-8", errors="replace").lower() if path.exists() else ""
            if "07e" not in content or "completed" not in content:
                stale_summary.append(str(path))
    add(
        "terminal documentation reconciled to final 07e endpoint",
        terminal and bool(sink_tokens) and not stale_detailed and not stale_summary,
        (
            f"sink_tokens={sorted(sink_tokens)}; stale_detailed={stale_detailed}; "
            f"stale_summary={stale_summary}"
        ),
        pending=not terminal or not sink_tokens,
    )

    status_counts = {
        status: sum(item.status == status for item in checks)
        for status in ("pass", "pending", "fail")
    }
    overall = (
        "failed"
        if status_counts["fail"]
        else "pending"
        if status_counts["pending"]
        else "passed"
    )
    report = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "overall": overall,
        "terminal": terminal,
        "summary": status_counts,
        "checks": [asdict(item) for item in checks],
        "interpretation_limit": (
            "Evidence-preservation/reporting audit only; not physical brine-outlet, "
            "separator-efficiency, mesh-independence, free-surface or physical-time validation."
        ),
    }
    json_path = MEETING_DIR / "OVERNIGHT_COMPLETION_AUDIT.json"
    md_path = MEETING_DIR / "OVERNIGHT_COMPLETION_AUDIT.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    visual_manifest["completion_audit"] = {
        "json": str(json_path),
        "markdown": str(md_path),
        "overall": overall,
        "summary": status_counts,
    }
    visual_manifest_path.write_text(
        json.dumps(visual_manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(md_path)
    print(json.dumps(report["summary"], sort_keys=True))
    return 0 if overall == "passed" else (2 if overall == "pending" else 1)


if __name__ == "__main__":
    raise SystemExit(main())

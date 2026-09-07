#!/usr/bin/env python3
"""Build a concise setup-07 overnight handoff from machine-readable evidence."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MEETING_DIR = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811"
SETUP07D_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_strong_sink_sensitivity_20260810"
    / "mesh-900k_band0p140165_tau0p020_v1"
)
SETUP07E_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def setup07e_analysis() -> tuple[dict[str, Any], Path]:
    manifest = load_json(SETUP07E_DIR / "qualification_manifest.json")
    final_path = SETUP07E_DIR / "QUALIFICATION_RESULT.json"
    interim_path = SETUP07E_DIR / "INTERIM_ANALYSIS.json"
    if manifest.get("status") == "completed" and final_path.exists():
        return load_json(final_path), final_path
    return load_json(interim_path), interim_path


def format_drift(assessment: dict[str, Any], field: str) -> str:
    item = assessment.get("stability", {}).get(field)
    if not item:
        return "n/a"
    return f"{float(item['drift_percent']):.3f}%"


def render() -> str:
    d = load_json(SETUP07D_DIR / "qualification_manifest.json")
    e_manifest = load_json(SETUP07E_DIR / "qualification_manifest.json")
    e, e_path = setup07e_analysis()
    d_endpoint = d["latest_metrics"]
    d_window = d.get("latest_500_iteration_assessment", {})
    e_endpoint = e["endpoint"]
    control = e["control_statistics"]
    residual = e["residual_statistics"]
    parity = e["dry_band_lineage_parity"]
    status = str(e.get("controller_status", "unknown"))
    final = bool(e.get("final"))
    dpm_after = e.get("dpm_after_run")
    dpm_after_text = (
        str(dpm_after) if dpm_after is not None else "pending (run active)"
    )

    lines = [
        "# Setup 07 Overnight Handoff",
        "",
        f"Generated: `{datetime.now().astimezone().isoformat(timespec='seconds')}`  ",
        f"Setup 07e state: `{'terminal' if final else 'interim'} / {status}`  ",
        "Scientific classification: `Diagnostic / unresolved unless the complete gate set proves otherwise`",
        "",
        "## Decision in one sentence",
        "",
        "The completed closed-bottom and fixed-sink evidence still supports adding a resolved brine outlet before restarting mesh convergence, DPM or EWF; setup 07e tests whether numerical liquid closure alone can stabilize the field but cannot validate outlet hydraulics.",
        "",
        "## Completed setup 07d control",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Iterations, ramp / full strength | `{d['cumulative_iterations_completed']} / {d['r1_iterations_completed']}` |",
        f"| Liquid sink | `{float(d_endpoint['sink_magnitude_kgs']):.4f} kg/s` (`{100.0 * float(d_endpoint['sink_magnitude_kgs']) / 116.92:.2f}%` of inlet) |",
        f"| Corrected liquid imbalance | `{float(d_endpoint['liquid_imbalance_percent']):.4f}%` |",
        f"| Pressure drop | `{float(d_endpoint['pressure_drop_pa']) / 1000.0:.4f} kPa` |",
        f"| Domain / band liquid inventory | `{float(d_endpoint['domain_liquid_inventory_kg']):.4f} / {float(d_endpoint['bottom_layer_liquid_inventory_kg']):.5f} kg` |",
        f"| Continuity residual | `{float(d_window.get('residuals', {}).get('continuity', {}).get('last', float('nan'))):.6g}` |",
        f"| Final-500 pressure / sink / inventory drift | `{format_drift(d_window, 'pressure_drop_pa')} / {format_drift(d_window, 'integrated_liquid_sink_kgs')} / {format_drift(d_window, 'domain_liquid_inventory_kg')}` |",
        f"| Stop / classification | `{d.get('stop_reason')} / {d.get('classification')}` |",
        "",
        "Setup 07d preserved start, ramp-complete, R1=1000, R1=2000 and final case/data; final ramp was reset to zero and DPM was off.",
        "",
        "## Setup 07e adaptive numerical-control state",
        "",
        "| Quantity | Result |",
        "|---|---:|",
        f"| Total / full-strength iteration | `{e_endpoint['cumulative_iteration']} / {e_endpoint['r1_iteration']}` |",
        f"| Ramp / tau | `{e_endpoint['ramp']:.3g} / {e_endpoint['tau_s']:.6g} s` |",
        f"| Commanded / achieved sink | `{e_endpoint['commanded_sink_kgs']:.4f} / {e_endpoint['sink_magnitude_kgs']:.4f} kg/s` |",
        f"| Corrected liquid / source-inclusive mixture imbalance | `{e_endpoint['corrected_liquid_imbalance_percent']:.4f}% / {e_endpoint['mixture_source_inclusive_imbalance_percent']:.4f}%` |",
        f"| Pressure drop | `{e_endpoint['pressure_drop_kpa']:.4f} kPa` |",
        f"| Domain / band liquid inventory | `{e_endpoint['domain_liquid_inventory_kg']:.5f} / {e_endpoint['band_liquid_inventory_kg']:.6g} kg` |",
        f"| Vapor / liquid steam-outlet flow | `{e_endpoint['vapor_steamoutlet_kgs_out']:.5f} / {e_endpoint['liquid_steamoutlet_kgs_out']:.6g} kg/s out` |",
        f"| Feedback samples with liquid in band | `{control['rows_with_liquid_in_band']}` |",
        f"| Passing acceptance windows | `{e.get('stable_windows_observed', 0)}` |",
        f"| Checkpoints recorded | `{', '.join(e.get('checkpoint_keys', []))}` |",
        "",
        "### Residual evidence",
        "",
        f"Window: iterations `{residual['iteration_start']}-{residual['iteration_end']}` (`{residual['samples']}` samples).",
        "",
        "| Residual | Endpoint | Endpoint change across window |",
        "|---|---:|---:|",
    ]
    for name, item in residual["statistics"].items():
        change = item["endpoint_change_percent"]
        change_text = "n/a" if change is None else f"{change:+.3f}%"
        lines.append(f"| `{name}` | `{item['endpoint']:.6g}` | `{change_text}` |")
    lines.extend(
        [
            "",
            "### Controlled-lineage evidence",
            "",
            f"Exact dry-band saved iterations `{parity['matched_iterations']}` have all-field parity pass `{parity['all_fields_pass']}` against setup 07d. This verifies deterministic clean-start lineage only; it does not validate feedback or the sink surrogate.",
            "",
            "## Safety and interpretation",
            "",
            f"- DPM record: `{e.get('dpm')}`; final DPM readback: `{dpm_after_text}`.",
            "- Bottom remains a wall; the source is a liquid-only volumetric sink in the complete bottom-local band.",
            "- Steady iteration is not physical time; unclosed liquid rate is not a transient accumulation rate.",
            "- Steam quality and carryover remain trend-only without a resolved, conserved brine outlet.",
            "- No mesh-convergence, separator-efficiency, free-surface or physical outlet-hydraulics claim is permitted.",
            "",
            "## Meeting package",
            "",
            "- Open with `27_tuesday_brine_outlet_action_summary.png`; use figure 13 for the preceding fixed-sink evidence chain.",
            "- Use figure 16 for the inventory-limited fixed-sink mechanism.",
            "- Use figures 14/15 for adaptive-control and residual histories once terminally regenerated.",
            "- Use figure 17 only as an outlet-recirculation face-count diagnostic, not backflow mass rate.",
            "- Use figure 18 as clean-start lineage evidence, not physical validation.",
            "- Use figure 19 for local-band wetting/source onset and figure 20 for the three-strategy comparison.",
            "- Use figure 21 for common-basis liquid-pathway accounting; unclosed steady rate is not physical-time accumulation.",
            "- Use figures 24/25 for the continuity-only outlet-size envelope and official-guidance boundary-condition sequence.",
            "- Use figure 26 to explain why the adaptive source is capacity-limited at the minimum tau.",
            "- Use terminal figures 22/23 only after their matched Fluent export and ramp-zero restore checks pass.",
            "",
            "## Remaining actions",
            "",
        ]
    )
    if final:
        lines.extend(
            [
                "- Verify terminal case/data checkpoints, final ramp zero and DPM off against the manifest and Fluent readback.",
                "- Reconcile the terminal classification across setup report, experiments, current status, blockers, validation, ordering and repository log.",
                "- Complete the evidence checklist and delete the overnight automation at/after the morning cutoff.",
            ]
        )
    else:
        lines.extend(
            [
                "- Continue the single guarded controller; do not launch a duplicate.",
                "- Preserve ramp-complete, R1=1000, R1=2000 and final ramp-zero checkpoints as reached.",
                "- Rebuild this handoff from terminal JSON after the run completes.",
            ]
        )
    lines.extend(
        [
            "",
            "## Machine-readable sources",
            "",
            f"- Setup 07d manifest: `{SETUP07D_DIR / 'qualification_manifest.json'}`",
            f"- Setup 07e manifest: `{SETUP07E_DIR / 'qualification_manifest.json'}`",
            f"- Setup 07e analysis: `{e_path}`",
            f"- Visual manifest: `{MEETING_DIR / 'visual_manifest.json'}`",
            f"- Completion checklist: `{MEETING_DIR / 'OVERNIGHT_COMPLETION_CHECKLIST.md'}`",
            f"- Completion audit: `{MEETING_DIR / 'OVERNIGHT_COMPLETION_AUDIT.md'}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    MEETING_DIR.mkdir(parents=True, exist_ok=True)
    path = MEETING_DIR / "OVERNIGHT_HANDOFF.md"
    path.write_text(render(), encoding="utf-8")
    manifest_path = MEETING_DIR / "visual_manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    manifest["overnight_handoff"] = str(path)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

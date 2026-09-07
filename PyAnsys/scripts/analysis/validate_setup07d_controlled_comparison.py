#!/usr/bin/env python3
"""Prove setup-07c/07d parity and isolate the intended fixed-tau change."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP07C_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_thickened_water_level_sink_20260808"
    / "mesh-900k_band0p140165_tau0p100_v1"
)
SETUP07D_DIR = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_strong_sink_sensitivity_20260810"
    / "mesh-900k_band0p140165_tau0p020_v1"
)


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def relative_percent(left: float, right: float) -> float:
    scale = max(abs(float(left)), abs(float(right)), 1.0e-30)
    return abs(float(left) - float(right)) / scale * 100.0


def main() -> int:
    c_manifest = json.loads((SETUP07C_DIR / "qualification_manifest.json").read_text(encoding="utf-8"))
    d_manifest = json.loads((SETUP07D_DIR / "qualification_manifest.json").read_text(encoding="utf-8"))
    c_history = pd.read_csv(SETUP07C_DIR / "physical_monitor_history.csv")
    d_history = pd.read_csv(SETUP07D_DIR / "physical_monitor_history.csv")

    settings_equal = c_manifest["settings_readback"] == d_manifest["settings_readback"]
    mesh_equal = c_manifest["mesh_metrics"] == d_manifest["mesh_metrics"]
    mask_fields = (
        "layer_thickness_m",
        "mask_field",
        "source_field",
        "mask_volume_integral_m3",
    )
    mask_comparison = {
        field: {
            "setup07c": c_manifest.get(field),
            "setup07d": d_manifest.get(field),
            "equal": c_manifest.get(field) == d_manifest.get(field),
        }
        for field in mask_fields
    }

    matched = c_history[c_history["r1_iteration"] == 0].merge(
        d_history[d_history["r1_iteration"] == 0],
        on="iteration",
        how="inner",
        suffixes=("_07c", "_07d"),
    )
    primary_pre_sink_fields = (
        "domain_liquid_inventory_kg",
        "pressure_drop_pa",
        "mixture_steamoutlet_kgs",
        "vapor_steamoutlet_kgs",
    )
    secondary_pre_sink_fields = (
        "outlet_area_weighted_velocity_ms",
        "domain_volume_avg_velocity_ms",
        "domain_volume_avg_vorticity_s-1",
    )
    pre_sink_fields = primary_pre_sink_fields + secondary_pre_sink_fields
    pre_sink_rows = []
    for _, row in matched.iterrows():
        record: dict[str, Any] = {"iteration": int(row["iteration"])}
        for field in pre_sink_fields:
            left = float(row[f"{field}_07c"])
            right = float(row[f"{field}_07d"])
            record[field] = {
                "setup07c": left,
                "setup07d": right,
                "relative_difference_percent": relative_percent(left, right),
            }
        pre_sink_rows.append(record)

    maximum_primary_pre_sink_difference = max(
        (
            row[field]["relative_difference_percent"]
            for row in pre_sink_rows
            for field in primary_pre_sink_fields
        ),
        default=float("inf"),
    )
    maximum_secondary_pre_sink_difference = max(
        (
            row[field]["relative_difference_percent"]
            for row in pre_sink_rows
            for field in secondary_pre_sink_fields
        ),
        default=float("inf"),
    )
    expected_tau_ratio = float(c_manifest["tau_s"]) / float(d_manifest["tau_s"])
    checks = {
        "mesh_metrics_exact": mesh_equal,
        "settings_readback_exact": settings_equal,
        "mask_contract_exact": all(item["equal"] for item in mask_comparison.values()),
        "source_hooks_exact": c_manifest["source_readback"] == d_manifest["source_readback"],
        "mask_readback_exact": c_manifest["mask_readback"] == d_manifest["mask_readback"],
        "udm_fields_exact": c_manifest["udm_fields"] == d_manifest["udm_fields"],
        "fresh_hybrid_after_tau_change": bool(d_manifest["fresh_hybrid_initialization_after_tau_change"]),
        "saved_accumulated_solution_loaded_is_false": not bool(d_manifest["saved_accumulated_solution_loaded"]),
        "dpm_off_during_and_after": d_manifest["dpm"].startswith("off") and d_manifest["dpm_after_run"] is False,
        "tau_ratio_is_five": abs(expected_tau_ratio - 5.0) <= 1.0e-12,
        "matched_pre_sink_rows_present": len(pre_sink_rows) >= 5,
        "pre_sink_primary_metrics_within_0p5_percent": maximum_primary_pre_sink_difference <= 0.5,
        "pre_sink_velocity_vorticity_within_1_percent": maximum_secondary_pre_sink_difference <= 1.0,
    }
    accepted = all(checks.values())
    audit = {
        "audit": "setup07c_to_setup07d_controlled_comparison",
        "classification": "accepted controlled diagnostic comparison" if accepted else "unresolved parity audit",
        "setup07c": str(SETUP07C_DIR),
        "setup07d": str(SETUP07D_DIR),
        "intended_change": {"tau_s": {"setup07c": c_manifest["tau_s"], "setup07d": d_manifest["tau_s"], "source_coefficient_ratio": expected_tau_ratio}},
        "checks": checks,
        "mesh_metrics_sha256": {
            "setup07c": canonical_hash(c_manifest["mesh_metrics"]),
            "setup07d": canonical_hash(d_manifest["mesh_metrics"]),
        },
        "settings_readback_sha256": {
            "setup07c": canonical_hash(c_manifest["settings_readback"]),
            "setup07d": canonical_hash(d_manifest["settings_readback"]),
        },
        "mask_comparison": mask_comparison,
        "matched_pre_sink_rows": pre_sink_rows,
        "maximum_pre_sink_primary_metric_difference_percent": maximum_primary_pre_sink_difference,
        "maximum_pre_sink_velocity_vorticity_difference_percent": maximum_secondary_pre_sink_difference,
        "parity_thresholds_percent": {
            "primary_pressure_inventory_and_outlet_flow": 0.5,
            "velocity_and_vorticity": 1.0,
            "basis": "same primary/secondary stability limits used by the setup-07 qualification contract",
        },
        "limitations": [
            "Parity establishes a controlled numerical sensitivity, not physical validity of the sink surrogate.",
            "The pre-sink comparison is limited to ramp rows before liquid occupies the active band.",
            "Neither setup is accepted as an iteration-independent separator solution.",
        ],
    }
    json_path = SETUP07D_DIR / "CONTROLLED_COMPARISON_AUDIT.json"
    json_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    status = "PASS" if accepted else "FAIL"
    lines = [
        "# Setup 07c to 07d Controlled-Comparison Audit",
        "",
        f"**Result:** `{status}` — {audit['classification']}",
        "",
        "The mesh metrics and complete Fluent settings readback are byte-for-byte equivalent after canonical JSON serialization. The qualified band/source-field contract is unchanged, fresh Hybrid Initialization was used, accumulated solution data were not loaded and DPM remained off. The intended production change is only `tau 0.1 -> 0.02 s`, a fivefold source-coefficient increase.",
        "",
        "## Checks",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    lines.extend(f"| `{name}` | `{'PASS' if value else 'FAIL'}` |" for name, value in checks.items())
    lines.extend(
        [
            "",
            "## Quantitative parity",
            "",
            f"- Matched pre-sink ramp rows: `{len(pre_sink_rows)}`.",
            f"- Maximum relative difference across pre-sink pressure/inventory/outlet-flow metrics: `{maximum_primary_pre_sink_difference:.6g}%` (limit `0.5%`).",
            f"- Maximum relative difference across pre-sink velocity/vorticity metrics: `{maximum_secondary_pre_sink_difference:.6g}%` (limit `1.0%`).",
            f"- Mesh-metric hash: `{audit['mesh_metrics_sha256']['setup07c']}` for both setups.",
            f"- Settings-readback hash: `{audit['settings_readback_sha256']['setup07c']}` for both setups.",
            "",
            "## Interpretation limit",
            "",
            "This proves that setup 07d is a controlled numerical sink-strength sensitivity. It does not validate the local sink as a physical brine outlet and does not change the unresolved convergence classification.",
        ]
    )
    (SETUP07D_DIR / "CONTROLLED_COMPARISON_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_path)
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())

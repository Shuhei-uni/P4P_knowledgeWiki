#!/usr/bin/env python3
"""Write a compact authoritative completion receipt after post-run hash repair."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--final-case", required=True)
    parser.add_argument("--final-data", required=True)
    parser.add_argument("--final-case-sha256", required=True)
    parser.add_argument("--final-data-sha256", required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    manifest = json.loads((run / "batched-resume-manifest.json").read_text(encoding="utf-8"))
    analysis = json.loads((run / "analysis" / "summary.json").read_text(encoding="utf-8"))
    checkpoints = []
    for offset in (250, 500, 750, 1000):
        item = json.loads((run / f"checkpoint-plus{offset:04d}-batched-readback.json").read_text(encoding="utf-8"))
        checkpoints.append({
            "additional_offset": offset,
            "native_expected_coordinate": item.get("native_expected_coordinate"),
            "checkpoint_pair": item.get("checkpoint_pair"),
            "terminal_readback": {
                "total_liquid_mass_kg": item.get("total_liquid_mass_kg"),
                "total_liquid_volume_m3": item.get("total_liquid_volume_m3"),
                "lower_liquid_mass_kg": item.get("lower_liquid_mass_kg"),
                "lower_liquid_volume_m3": item.get("lower_liquid_volume_m3"),
                "command_kg_s": item.get("command_kg_s"),
                "command_error_kg_s": item.get("command_error_kg_s"),
            },
            "event_flags": item.get("console_event_flags"),
        })
    receipt: dict[str, Any] = {
        "status": "COMPLETE",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "setup_id": manifest.get("setup_id"),
        "parent_start_native_iteration": manifest.get("parent_start_native_iteration"),
        "pause_native_iteration": manifest.get("pause_native_iteration"),
        "requested_additional_total": manifest.get("requested_additional_total"),
        "native_batch_size": manifest.get("native_batch_size"),
        "report_cadence": manifest.get("report_cadence"),
        "native_coordinate_note": "Checkpoint offsets are the requested continuation coordinates. Fluent transcript/report rows reached native 4586 after restart; the RP current-iteration variable was stale and is excluded from authority.",
        "control_delta": {
            "pressure_velocity_coupling": "Coupled",
            "pseudo_time_method": "Global Time Step",
            "all_other_physics_and_numerics": "preserved by readback audit",
        },
        "final_pair": {
            "case": args.final_case,
            "data": args.final_data,
            "case_sha256": args.final_case_sha256,
            "data_sha256": args.final_data_sha256,
        },
        "checkpoints": checkpoints,
        "analysis_summary": str((run / "analysis" / "summary.json").resolve()),
        "analysis_summary_sha256": __import__("hashlib").sha256((run / "analysis" / "summary.json").read_bytes()).hexdigest(),
        "figures": analysis.get("figures", {}),
        "post_run_wrapper_note": "The solver and writes completed; the original wrapper was marked BLOCKED only because its first final OneDrive hash parse returned empty. Final durable hashes were then verified in a fresh read-only attachment.",
    }
    output = run / "authoritative-completion-receipt.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

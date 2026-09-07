#!/usr/bin/env python3
"""Run the 0.05%-feed flow sensitivity at the 0.1%-target pressure."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p1feed_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_server2_step90_targetpressure_for0p1_0p05feed_"
    "dt128em6_inner100_steps10_attempt1_20260825"
)
MEMBER = "feed_0p05_percent_dt128_inner100"
FRACTION = 0.0005


def rewrite(run_root: Path) -> None:
    campaign_path = run_root / "campaign_manifest.json"
    payload = json.loads(campaign_path.read_text(encoding="utf-8"))
    passed = bool(payload.get("comparison_gate", {}).get("passed"))
    payload.update(
        {
            "classification": (
                "accepted diagnostic / 0.05%-feed flow sensitivity"
                if passed
                else "diagnostic / unresolved 0.05%-feed flow sensitivity"
            ),
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": "relative to failed 0.1%-feed dt128us inner100 member: inlet fraction 0.001 -> 0.0005 only",
            "acceptance_limitation": "The fixed pressure was interpolated for 0.1% liquid drainage, not 0.05%; this isolates numerical feed loading and is not a constant-level result or plant boundary.",
        }
    )
    probe.write_json(campaign_path, payload)
    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8"))
    member.update(
        {
            "inlet_fraction": FRACTION,
            "time_step_size_s": 1.28e-4,
            "inner_iterations_per_step": 100,
            "classification": (
                "accepted diagnostic / 0.05%-feed flow-sensitivity member"
                if member.get("status") == "completed"
                and member.get("residual_gate", {}).get("passed")
                else member.get("classification")
            ),
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    result = source.main()
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    rewrite(run_root)
    return result


if __name__ == "__main__":
    raise SystemExit(main())

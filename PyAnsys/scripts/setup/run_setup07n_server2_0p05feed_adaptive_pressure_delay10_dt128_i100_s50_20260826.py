#!/usr/bin/env python3
"""Delay adaptive brine-pressure feedback until the accepted ten-step startup.

The first adaptive-pressure attempt reacted to the step-1 zero-drain startup
signal, lowered pressure by about 13 Pa before the short-run balance point, and
then developed a long oscillation.  This one-factor sensitivity holds the same
initial pressure through the first nine steps and makes its first identical
controller update after step 10.  It still cold-loads the clean server-2
step-90 parent and changes no physics, feed, timestep, gain or pressure bound.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_adaptive_pressure_dt128_i100_s40_20260826 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_0p05feed_adaptivep_delay10_g0p25_dp5_dt128_i100_s50_a1_20260826"
MEMBER = "feed_0p05_percent_adaptive_pressure_delay10_dt128_inner100"
PHYSICAL_STEPS = 50
CHECKPOINT_STEPS = {1, 5, 10, 20, 30, 40, 50}
CONTROL_FIRST_UPDATE_AFTER_STEP = 10


def rewrite_delay_evidence() -> None:
    run_root = source.probe.PROJECT_ROOT / "output" / source.probe.STUDY_ID / RUN_LABEL
    campaign_path = run_root / "campaign_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    passed = bool(campaign.get("controller_use_authorized"))
    classification = (
        "accepted diagnostic / delayed adaptive-pressure 0.05%-feed flow balance"
        if passed
        else "diagnostic / unresolved delayed adaptive-pressure 0.05%-feed flow balance"
    )
    campaign.update(
        {
            "classification": classification,
            "eligible_parent": False,
            "one_factor_change": (
                "relative to the completed immediate-feedback adaptive-pressure "
                "diagnostic: first controller update moves from additional step 1 "
                "to additional step 10 only; the longer budget observes the response"
            ),
            "controller_startup_rationale": (
                "The fixed-pressure short diagnostic was balanced at step 10. Holding "
                "the controller until that clock avoids reacting to the step-1 "
                "zero-drain startup measurement."
            ),
        }
    )
    source.probe.write_json(campaign_path, campaign)
    member_path = run_root / MEMBER / "member_manifest.json"
    if member_path.exists():
        member = json.loads(member_path.read_text(encoding="utf-8"))
        member.update({"classification": classification + " member", "eligible_parent": False})
        source.probe.write_json(member_path, member)


def main() -> int:
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.PHYSICAL_STEPS = PHYSICAL_STEPS
    source.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
    source.CONTROL_FIRST_UPDATE_AFTER_STEP = CONTROL_FIRST_UPDATE_AFTER_STEP
    try:
        return source.main()
    finally:
        rewrite_delay_evidence()


if __name__ == "__main__":
    raise SystemExit(main())

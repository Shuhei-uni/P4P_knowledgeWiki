#!/usr/bin/env python3
"""Run a lower-gain delayed pressure controller from clean server-2 step 90.

The completed gain-0.25 delayed controller crossed the balanced point but then
overshot into an equal-size opposite imbalance.  This bounded one-factor
sensitivity changes only the proportional gain from 0.25 to 0.05.  It keeps
the clean checksum-bound parent, 0.05% feed, ten-step activation delay,
pressure bracket, timestep, inner-iteration budget, models and safety gates.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_adaptive_pressure_delay10_dt128_i100_s50_20260826 as delayed  # noqa: E402


RUN_LABEL = "b620_07n_s2_0p05_apd10_g05_dt128_i100_s100_a4_20260826"
MEMBER = "f0p05_apd10g05"
PHYSICAL_STEPS = 100
CHECKPOINT_STEPS = {1, 5, 10, 20, 30, 40, 50, 75, 100}
PROPORTIONAL_GAIN = 0.05


def rewrite_gain_evidence() -> None:
    run_root = (
        delayed.source.probe.PROJECT_ROOT
        / "output"
        / delayed.source.probe.STUDY_ID
        / RUN_LABEL
    )
    campaign_path = run_root / "campaign_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    passed = bool(campaign.get("controller_use_authorized"))
    classification = (
        "accepted diagnostic / lower-gain delayed adaptive-pressure 0.05%-feed flow balance"
        if passed
        else "diagnostic / unresolved lower-gain delayed adaptive-pressure 0.05%-feed flow balance"
    )
    campaign.update(
        {
            "classification": classification,
            "eligible_parent": False,
            "one_factor_change": (
                "relative to completed delayed adaptive-pressure attempt3: proportional "
                "gain 0.25 -> 0.05 only; clean parent, feed, activation delay, pressure "
                "bounds, timestep, inner iterations, models and gates are unchanged"
            ),
            "controller_gain_sensitivity_rationale": (
                "Gain 0.25 crossed the balance point and overshot to a comparable "
                "opposite imbalance. The fivefold reduction tests damping without "
                "changing the physical boundary interpretation."
            ),
        }
    )
    delayed.source.probe.write_json(campaign_path, campaign)
    member_path = run_root / MEMBER / "member_manifest.json"
    if member_path.exists():
        member = json.loads(member_path.read_text(encoding="utf-8"))
        member.update(
            {
                "classification": classification + " member",
                "eligible_parent": False,
            }
        )
        delayed.source.probe.write_json(member_path, member)


def main() -> int:
    delayed.RUN_LABEL = RUN_LABEL
    delayed.MEMBER = MEMBER
    delayed.PHYSICAL_STEPS = PHYSICAL_STEPS
    delayed.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
    delayed.CONTROL_FIRST_UPDATE_AFTER_STEP = 10
    delayed.source.PROPORTIONAL_GAIN = PROPORTIONAL_GAIN
    try:
        return delayed.main()
    finally:
        rewrite_gain_evidence()


if __name__ == "__main__":
    raise SystemExit(main())

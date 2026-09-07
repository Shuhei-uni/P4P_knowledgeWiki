#!/usr/bin/env python3
"""Long-hold the accepted calibrated 0.05%-feed pressure-step treatment.

This independently cold-loads the checksum-bound clean server-2 step-90
parent and repeats the accepted +23.218830875 Pa command after step 10.  The
only change from the accepted 36-step diagnostic is the requested budget of
70 physical steps.  Every saved field remains ineligible as a parent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_pressure_step23p219_after10_s36_20260828 as source  # noqa: E402


RUN_LABEL = "b620_07n_s2_0p05_pstep23p219_after10_s70_a1_20260828"
MEMBER = "f0p05_pstep23p219_after10_s70"
PHYSICAL_STEPS = 70
CHECKPOINT_STEPS = {1, 5, 10, 11, 20, 30, 36, 45, 55, 70}


def rewrite_long_hold() -> None:
    root = source.source.controller.probe.PROJECT_ROOT / "output" / source.source.controller.probe.STUDY_ID / RUN_LABEL
    campaign_path = root / "campaign_manifest.json"
    member_path = root / MEMBER / "member_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    member = json.loads(member_path.read_text(encoding="utf-8")) if member_path.exists() else {}
    balance = source.tail_balance_gate(member) if member else {"passed": False}
    completed = member.get("status") == "completed"
    residual = bool(member.get("residual_gate", {}).get("passed"))
    passed = completed and residual and bool(balance.get("passed"))
    classification = (
        "accepted diagnostic / calibrated pressure-step 0.05%-feed long hold"
        if passed
        else "diagnostic / unresolved calibrated pressure-step 0.05%-feed long hold"
    )
    campaign.update(
        {
            "classification": classification,
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": (
                "relative to the accepted calibrated 36-step diagnostic: requested physical "
                "budget 36 -> 70 only; both independently cold-load the same checksum-bound "
                "clean step-90 parent"
            ),
            "sustained_phase_mass_balance_gate": balance,
            "acceptance_limitation": (
                "Passing establishes persistence only for this low-feed numerical treatment. "
                "It is not plant-pressure validation or constant-level control."
            ),
        }
    )
    source.source.controller.probe.write_json(campaign_path, campaign)
    if member:
        member.update(
            {
                "classification": classification + " member",
                "eligible_parent": False,
                "sustained_phase_mass_balance_gate": balance,
            }
        )
        source.source.controller.probe.write_json(member_path, member)


def main() -> int:
    root = source.source.controller.probe.PROJECT_ROOT / "output" / source.source.controller.probe.STUDY_ID / RUN_LABEL
    if root.exists():
        raise FileExistsError(f"refusing to reuse output root: {root}")
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.PHYSICAL_STEPS = PHYSICAL_STEPS
    source.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
    try:
        return source.main()
    finally:
        rewrite_long_hold()


if __name__ == "__main__":
    raise SystemExit(main())

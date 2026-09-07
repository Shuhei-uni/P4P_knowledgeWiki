#!/usr/bin/env python3
"""Create the longer fixed-pressure half of a matched response experiment.

The prior 36-step +5 Pa response had the correct sign but no plateau.  This
runner independently cold-loads the checksum-bound clean server-2 step-90
parent and reproduces the 0.05%-feed baseline for 70 physical steps.  Its
history is the fixed-pressure reference for a separate +5 Pa step run; no
saved field is an eligible parent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_p1122264_0p05feed_dt128_i100_s100_20260826 as source  # noqa: E402


RUN_LABEL = "b620_07n_s2_0p05_fixed70_matched_a1_20260828"
MEMBER = "f0p05_fixed70_matched"
PHYSICAL_STEPS = 70
CHECKPOINT_STEPS = {1, 5, 10, 20, 30, 36, 45, 55, 70}


def rewrite_matched_reference() -> None:
    root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    campaign_path = root / "campaign_manifest.json"
    member_path = root / MEMBER / "member_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    completed = False
    if member_path.exists():
        member = json.loads(member_path.read_text(encoding="utf-8"))
        completed = member.get("status") == "completed"
        member.update(
            {
                "classification": (
                    "accepted diagnostic / completed fixed-pressure response reference"
                    if completed
                    else "diagnostic / unresolved fixed-pressure response reference"
                ),
                "eligible_parent": False,
                "matched_response_role": "fixed-pressure 70-step reference",
            }
        )
        probe.write_json(member_path, member)
    campaign.update(
        {
            "classification": (
                "accepted diagnostic / completed fixed-pressure response reference"
                if completed
                else "diagnostic / unresolved fixed-pressure response reference"
            ),
            "eligible_parent": False,
            "controller_use_authorized": False,
            "matched_response_role": "fixed-pressure 70-step reference",
            "one_factor_change": (
                "relative to the stopped 36-step fixed history: requested budget 36 -> 70; "
                "both independently cold-load the same checksum-bound clean step-90 parent"
            ),
            "next_action": (
                "after completion, independently cold-load clean step 90 and reproduce the "
                "same 70-step schedule with one +5 Pa command after step 10"
            ),
            "acceptance_limitation": (
                "Completion supplies only a matched numerical response reference. It does "
                "not validate plant pressure, downstream resistance, operating level or control."
            ),
        }
    )
    probe.write_json(campaign_path, campaign)


def main() -> int:
    root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if root.exists():
        raise FileExistsError(f"refusing to reuse output root: {root}")
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.PHYSICAL_STEPS = PHYSICAL_STEPS
    source.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
    try:
        return source.main()
    finally:
        rewrite_matched_reference()


if __name__ == "__main__":
    raise SystemExit(main())

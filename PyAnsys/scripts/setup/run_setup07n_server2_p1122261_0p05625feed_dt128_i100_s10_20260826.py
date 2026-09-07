#!/usr/bin/env python3
"""Retarget the 0.05625%-feed diagnostic to its interpolated drain pressure.

This is an independent one-factor pressure sensitivity.  It cold-loads the
same checksum-bound clean server-2 step-90 parent used by the prior feed-load
screen, keeps the inlet fraction, timestep and inner-iteration cap fixed, and
changes only the diagnostic brine pressure.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_p1122261_0p05625feed_dt128_i100_s10_a1_20260826"
MEMBER = "feed_0p05625_percent_retargetpressure_dt128_inner100"
FRACTION = 0.0005625
TARGET_PRESSURE_PA = 1_122_261.011


def rewrite_retarget_evidence() -> None:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    campaign_path = run_root / "campaign_manifest.json"
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    member_result = campaign["members"][MEMBER]
    passed = bool(member_result.get("residual_gate", {}).get("passed")) and bool(
        campaign.get("comparison_gate", {}).get("passed")
    )
    classification = (
        "accepted diagnostic / 0.05625%-feed pressure retarget"
        if passed
        else "diagnostic / unresolved 0.05625%-feed pressure retarget"
    )
    campaign.update(
        {
            "classification": classification,
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "independent_cold_load": True,
            "one_factor_change": (
                "relative to the completed p1122263.621 0.05625%-feed diagnostic: "
                "brine pressure 1122263.6212370484 -> 1122261.011 Pa only"
            ),
            "pressure_interpolation": {
                "pressure_pa": TARGET_PRESSURE_PA,
                "target_outward_liquid_kgs": 116.92 * FRACTION,
                "basis": (
                    "CFD response interpolation using the completed 0.05625%-feed "
                    "liquid-flow mismatch at 1122263.6212370484 Pa"
                ),
                "plant_boundary_validated": False,
            },
            "acceptance_limitation": (
                "This is a bounded numerical pressure retarget, not a plant "
                "boundary or validated constant-level controller."
            ),
        }
    )
    probe.write_json(campaign_path, campaign)

    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8"))
    member.update(
        {
            "inlet_fraction": FRACTION,
            "requested_brine_pressure_pa": TARGET_PRESSURE_PA,
            "classification": classification + " member",
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    source.TARGET_PRESSURE_PA = TARGET_PRESSURE_PA
    source.TARGET_LIQUID_DRAIN_KGS = 116.92 * FRACTION
    result = source.main()
    rewrite_retarget_evidence()
    return result


if __name__ == "__main__":
    raise SystemExit(main())

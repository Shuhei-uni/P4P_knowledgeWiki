#!/usr/bin/env python3
"""Long-hold the accepted 0.05%-feed drainage setup from clean step 90.

This runner does not continue the short accepted endpoint.  It independently
cold-loads the checksum-bound server-2 closed-pool step-90 parent, applies the
same 0.05% inlet rates and CFD-derived brine pressure as the accepted ten-step
diagnostic, and advances 100 guarded physical steps at ``dt=128 us`` with 100
inner iterations.  Every saved field remains ineligible as a general parent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_p1122264_0p05feed_dt128_i100_s100_a1_20260826"
MEMBER = "feed_0p05_percent_targetpressure_dt128_inner100_longhold"
FRACTION = 0.0005
TARGET_PRESSURE_PA = 1_122_263.6212370484
PHYSICAL_STEPS = 100
CHECKPOINT_STEPS = {1, 5, 10, 25, 50, 100}


def rewrite_long_hold_evidence() -> None:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    campaign_path = run_root / "campaign_manifest.json"
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    member_result = campaign["members"][MEMBER]
    passed = bool(member_result.get("residual_gate", {}).get("passed")) and bool(
        campaign.get("comparison_gate", {}).get("passed")
    )
    campaign.update(
        {
            "classification": (
                "accepted diagnostic / independent 0.05%-feed long hold"
                if passed
                else "diagnostic / unresolved independent 0.05%-feed long hold"
            ),
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "independent_cold_load": True,
            "one_factor_change": (
                "relative to the accepted short 0.05%-feed diagnostic: requested "
                "physical-step budget 10 -> 100 only; both branches cold-load the "
                "same checksum-bound closed-pool step-90 parent"
            ),
            "pressure_interpolation": {
                "pressure_pa": TARGET_PRESSURE_PA,
                "target_outward_liquid_kgs": 116.92 * FRACTION,
                "basis": "CFD-interpolated low-feed drainage pressure",
                "plant_boundary_validated": False,
            },
            "acceptance_limitation": (
                "This tests persistence of the low-feed numerical drainage state. "
                "It does not validate plant pressure, operating level, drainage "
                "capacity, full-flow operation, mesh independence or level control."
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
            "requested_physical_steps": PHYSICAL_STEPS,
            "classification": (
                "accepted diagnostic / independent 0.05%-feed long-hold member"
                if passed
                else "diagnostic / unresolved independent 0.05%-feed long-hold member"
            ),
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")

    original_probe_main = probe.main

    def long_hold_probe_main() -> int:
        # The source runner has already installed the exact parent, boundary,
        # inlet and monitoring contract when it delegates here.
        probe.PHYSICAL_STEPS = PHYSICAL_STEPS
        probe.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
        return original_probe_main()

    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    source.TARGET_PRESSURE_PA = TARGET_PRESSURE_PA
    source.TARGET_LIQUID_DRAIN_KGS = 116.92 * FRACTION
    probe.main = long_hold_probe_main
    result = source.main()
    rewrite_long_hold_evidence()
    return result


if __name__ == "__main__":
    raise SystemExit(main())

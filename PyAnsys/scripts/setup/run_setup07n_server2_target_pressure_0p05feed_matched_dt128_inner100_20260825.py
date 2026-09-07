#!/usr/bin/env python3
"""Run 0.05% feed at its independently interpolated drainage pressure.

This is a pressure-only sensitivity from the completed fixed-pressure 0.05%
feed diagnostic.  It always cold-loads the checksum-bound server-2 step-90
parent through the existing guarded runner.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p05feed_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_server2_step90_targetpressure_for0p05_0p05feed_"
    "dt128em6_inner100_steps10_attempt1_20260825"
)
MEMBER = "feed_0p05_percent_targetpressure_dt128_inner100"
FRACTION = 0.0005
TARGET_PRESSURE_PA = 1_122_246.4660643323
TARGET_LIQUID_DRAIN_KGS = 116.92 * FRACTION
PHASE_NET_TOLERANCE_KGS = 0.005


def rewrite(run_root: Path) -> None:
    campaign_path = run_root / "campaign_manifest.json"
    payload = json.loads(campaign_path.read_text(encoding="utf-8"))
    result = payload["members"][MEMBER]
    endpoint = result["endpoint"]
    liquid_net = abs(float(endpoint["liquid_net_kgs"]))
    vapor_net = abs(float(endpoint["vapor_net_kgs"]))
    numerical_and_physical = bool(result.get("residual_gate", {}).get("passed")) and bool(
        payload.get("comparison_gate", {}).get("passed")
    )
    phase_balance_passed = (
        liquid_net <= PHASE_NET_TOLERANCE_KGS
        and vapor_net <= PHASE_NET_TOLERANCE_KGS
    )
    passed = numerical_and_physical and phase_balance_passed
    payload.update(
        {
            "classification": (
                "accepted diagnostic / matched 0.05%-feed pressure-drainage"
                if passed
                else "diagnostic / unresolved matched 0.05%-feed pressure-drainage"
            ),
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": (
                "relative to the accepted fixed-pressure 0.05%-feed diagnostic: "
                "brine pressure 1122207.446241885 -> 1122246.4660643323 Pa only"
            ),
            "pressure_interpolation": {
                "pressure_pa": TARGET_PRESSURE_PA,
                "target_outward_liquid_kgs": TARGET_LIQUID_DRAIN_KGS,
                "basis": (
                    "linear interpolation of accepted server-2 zero-feed "
                    "low/centre/high response bracket"
                ),
                "plant_boundary_validated": False,
            },
            "phase_mass_balance_gate": {
                "tolerance_kgs": PHASE_NET_TOLERANCE_KGS,
                "liquid_net_abs_kgs": liquid_net,
                "vapor_net_abs_kgs": vapor_net,
                "passed": phase_balance_passed,
            },
            "acceptance_limitation": (
                "The pressure is CFD-interpolated, not a plant boundary. This is "
                "a bounded constant-inventory diagnostic, not plant validation."
            ),
        }
    )
    probe.write_json(campaign_path, payload)

    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8"))
    member.update(
        {
            "inlet_fraction": FRACTION,
            "requested_brine_pressure_pa": TARGET_PRESSURE_PA,
            "target_liquid_drain_kgs": TARGET_LIQUID_DRAIN_KGS,
            "phase_mass_balance_gate": payload["phase_mass_balance_gate"],
            "classification": (
                "accepted diagnostic / matched 0.05%-feed pressure-drainage member"
                if passed
                else "diagnostic / unresolved matched 0.05%-feed pressure-drainage member"
            ),
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    # The imported source mutates only process-local module constants and then
    # delegates to the create-first, checksum/readback-gated runner.
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    source.source.base.TARGET_PRESSURE_PA = TARGET_PRESSURE_PA
    result = source.main()
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    rewrite(run_root)
    return result


if __name__ == "__main__":
    raise SystemExit(main())

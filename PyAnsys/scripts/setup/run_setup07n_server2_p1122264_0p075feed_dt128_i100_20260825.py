#!/usr/bin/env python3
"""Bracket the stable inlet-load limit with 0.075% feed at fixed pressure."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_p1122264_0p075feed_dt128_i100_s10_a1_20260825"
MEMBER = "feed_0p075_percent_fixedpressure_dt128_inner100"
FRACTION = 0.00075
PRESSURE_PA = 1_122_263.6212370484


def rewrite_flow_sensitivity() -> None:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    path = run_root / "campaign_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = payload["members"][MEMBER]
    numerical_and_physical = bool(result.get("residual_gate", {}).get("passed")) and bool(
        payload.get("comparison_gate", {}).get("passed")
    )
    payload.update(
        {
            "classification": (
                "accepted diagnostic / 0.075%-feed load sensitivity"
                if numerical_and_physical
                else "diagnostic / unresolved 0.075%-feed load sensitivity"
            ),
            "eligible_parent": False,
            "controller_use_authorized": numerical_and_physical,
            "one_factor_change": (
                "relative to accepted p1122263.621 0.05%-feed diagnostic: inlet "
                "fraction 0.0005 -> 0.00075 only"
            ),
            "acceptance_limitation": (
                "Pressure remains matched to 0.05% drainage, so this isolates inlet "
                "loading and is not a constant-level or plant-boundary result."
            ),
        }
    )
    probe.write_json(path, payload)

    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8"))
    member.update(
        {
            "inlet_fraction": FRACTION,
            "classification": (
                "accepted diagnostic / 0.075%-feed load-sensitivity member"
                if numerical_and_physical
                else "diagnostic / unresolved 0.075%-feed load-sensitivity member"
            ),
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    source.TARGET_PRESSURE_PA = PRESSURE_PA
    source.TARGET_LIQUID_DRAIN_KGS = 116.92 * FRACTION
    result = source.main()
    rewrite_flow_sensitivity()
    return result


if __name__ == "__main__":
    raise SystemExit(main())

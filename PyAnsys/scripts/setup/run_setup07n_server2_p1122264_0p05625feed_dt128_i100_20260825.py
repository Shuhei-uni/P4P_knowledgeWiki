#!/usr/bin/env python3
"""Bisect the 0.05%-pass/0.0625%-fail feed-load bracket at 0.05625%."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_p1122264_0p0625feed_dt128_i100_20260825 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_p1122264_0p05625feed_dt128_i100_s10_a1_20260825"
MEMBER = "feed_0p05625_percent_fixedpressure_dt128_inner100"
FRACTION = 0.0005625


def rewrite() -> None:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    path = run_root / "campaign_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = payload["members"][MEMBER]
    passed = bool(result.get("residual_gate", {}).get("passed")) and bool(
        payload.get("comparison_gate", {}).get("passed")
    )
    label = "accepted diagnostic" if passed else "diagnostic / unresolved"
    payload.update(
        {
            "classification": f"{label} / 0.05625%-feed load sensitivity",
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": (
                "relative to accepted p1122263.621 0.05%-feed diagnostic: inlet "
                "fraction 0.0005 -> 0.0005625 only; midpoint of 0.05%-pass and "
                "terminal 0.0625%-fail bracket"
            ),
            "acceptance_limitation": (
                "Pressure remains matched to 0.05% drainage; this is a numerical "
                "load sensitivity, not a constant-level or plant-boundary result."
            ),
        }
    )
    probe.write_json(path, payload)
    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8"))
    member.update(
        {
            "inlet_fraction": FRACTION,
            "classification": f"{label} / 0.05625%-feed load-sensitivity member",
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    result = source.main()
    rewrite()
    return result


if __name__ == "__main__":
    raise SystemExit(main())

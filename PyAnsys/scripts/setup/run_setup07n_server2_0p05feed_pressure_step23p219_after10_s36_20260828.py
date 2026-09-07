#!/usr/bin/env python3
"""Test one evidence-calibrated pressure step for sustained 0.05% balance.

The +5 Pa response and matched fixed history had nearly linear, opposing
liquid-net slopes over steps 12--36.  Their least-squares slope ratio predicts
that a +23.218830875 Pa command after step 10 should cancel the background
drainage drift.  This independently cold-loads clean server-2 step 90 and
changes only that pressure-step amplitude relative to the completed +5 Pa
diagnostic.  It is a numerical mass-flow sensitivity, not level control.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_pressure_step_plus5_after10_hold36_20260827 as source  # noqa: E402


RUN_LABEL = "b620_07n_s2_0p05_pstep23p219_after10_s36_a1_20260828"
MEMBER = "f0p05_pstep23p219_after10_s36"
PRESSURE_CHANGE_PA = 23.218830875309216
PHYSICAL_STEPS = 36
CHECKPOINT_STEPS = {1, 5, 10, 11, 15, 20, 25, 30, 36}
BALANCE_TOLERANCE_KG_S = 0.005
BALANCE_TAIL_STEPS = 10


def tail_balance_gate(member: Mapping[str, Any]) -> dict[str, Any]:
    rows = [step["metrics"] for step in member.get("steps", [])]
    tail = rows[-BALANCE_TAIL_STEPS:]
    keys = ("liquid_net_kgs", "vapor_net_kgs", "mixture_net_kgs")
    maxima = {
        key: max((abs(float(row[key])) for row in tail), default=math.inf)
        for key in keys
    }
    return {
        "required_tail_steps": BALANCE_TAIL_STEPS,
        "tolerance_kg_s": BALANCE_TOLERANCE_KG_S,
        "tail_additional_steps": [int(row["additional_step"]) for row in tail],
        "maximum_absolute_tail_imbalance_kg_s": maxima,
        "passed": len(tail) == BALANCE_TAIL_STEPS
        and all(value <= BALANCE_TOLERANCE_KG_S for value in maxima.values()),
    }


def rewrite_calibrated_step() -> None:
    root = source.controller.probe.PROJECT_ROOT / "output" / source.controller.probe.STUDY_ID / RUN_LABEL
    campaign_path = root / "campaign_manifest.json"
    member_path = root / MEMBER / "member_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    member = json.loads(member_path.read_text(encoding="utf-8")) if member_path.exists() else {}
    balance = tail_balance_gate(member) if member else {"passed": False}
    completed = member.get("status") == "completed"
    residual = bool(member.get("residual_gate", {}).get("passed"))
    passed = completed and residual and bool(balance.get("passed"))
    classification = (
        "accepted diagnostic / calibrated pressure-step 0.05%-feed balance"
        if passed
        else "diagnostic / unresolved calibrated pressure-step 0.05%-feed balance"
    )
    campaign.update(
        {
            "classification": classification,
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": (
                "relative to the completed 36-step +5 Pa response: pressure-step amplitude "
                "+5 -> +23.218830875 Pa only; parent, command epoch, feeds, timestep, inner "
                "iterations, physical budget and physics are unchanged"
            ),
            "pressure_step_calibration": {
                "fixed_liquid_net_slope_kg_s_per_step": -0.0019402065095384616,
                "plus5_delta_slope_kg_s_per_step": 0.0004178088293846154,
                "calculation": "-fixed_slope / plus5_delta_slope * 5 Pa",
                "command_after_additional_step": 10,
                "pressure_change_pa": PRESSURE_CHANGE_PA,
                "pressure_after_pa": source.INITIAL_PRESSURE_PA + PRESSURE_CHANGE_PA,
                "plant_boundary_validated": False,
            },
            "sustained_phase_mass_balance_gate": balance,
            "acceptance_limitation": (
                "Passing would establish only a bounded numerical liquid-flow-balance "
                "sensitivity. Reported inventory precision cannot validate constant level."
            ),
        }
    )
    source.controller.probe.write_json(campaign_path, campaign)
    if member:
        member.update(
            {
                "classification": classification + " member",
                "eligible_parent": False,
                "sustained_phase_mass_balance_gate": balance,
            }
        )
        source.controller.probe.write_json(member_path, member)


def main() -> int:
    root = source.controller.probe.PROJECT_ROOT / "output" / source.controller.probe.STUDY_ID / RUN_LABEL
    if root.exists():
        raise FileExistsError(f"refusing to reuse output root: {root}")
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.PRESSURE_CHANGE_PA = PRESSURE_CHANGE_PA
    source.FINAL_PRESSURE_PA = source.INITIAL_PRESSURE_PA + PRESSURE_CHANGE_PA
    source.PHYSICAL_STEPS = PHYSICAL_STEPS
    source.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
    source.controller.MAX_PRESSURE_CHANGE_PA = PRESSURE_CHANGE_PA
    try:
        return source.main()
    finally:
        rewrite_calibrated_step()


if __name__ == "__main__":
    raise SystemExit(main())

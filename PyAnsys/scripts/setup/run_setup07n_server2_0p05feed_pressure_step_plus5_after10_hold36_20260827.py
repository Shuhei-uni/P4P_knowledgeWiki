#!/usr/bin/env python3
"""Measure the delayed 0.05%-feed drainage response to one +5 Pa step.

This diagnostic independently cold-loads the checksum-bound clean server-2
step-90 parent, holds the established 0.05%-feed pressure for ten physical
steps, raises only the brine pressure by 5 Pa, and then holds it fixed through
additional step 36.  It compares the response with the existing independent
fixed-pressure history.  It is an open-loop response identification, not a
level controller and never an eligible parent.
"""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_adaptive_pressure_dt128_i100_s40_20260826 as controller  # noqa: E402


RUN_LABEL = "b620_07n_s2_0p05_pstepplus5_after10_hold36_a2_20260827"
MEMBER = "f0p05_pstepplus5_after10_hold36"
PHYSICAL_STEPS = 36
CHECKPOINT_STEPS = {1, 5, 10, 11, 15, 20, 25, 30, 36}
ACTUATION_AFTER_STEP = 10
PRESSURE_CHANGE_PA = 5.0
INITIAL_PRESSURE_PA = 1_122_263.6212370484
FINAL_PRESSURE_PA = INITIAL_PRESSURE_PA + PRESSURE_CHANGE_PA
DELTA_ONSET_THRESHOLD_KG_S = 5.0e-4
SETTLE_RELATIVE_TOLERANCE = 0.05
SETTLE_ABSOLUTE_FLOOR_KG_S = 5.0e-4

REFERENCE_HISTORY = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07n_s2_p1122264_0p05feed_dt128_i100_s100_a1_20260826"
    / "feed_0p05_percent_targetpressure_dt128_inner100_longhold"
    / "physical_history.csv"
)


def read_csv_by_step(path: Path) -> dict[int, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            int(row["additional_step"]): row
            for row in csv.DictReader(stream)
        }


def response_analysis(member: Mapping[str, Any]) -> dict[str, Any]:
    reference = read_csv_by_step(REFERENCE_HISTORY)
    observed = {
        int(step["metrics"]["additional_step"]): step["metrics"]
        for step in member.get("steps", [])
    }
    rows: list[dict[str, Any]] = []
    for step in range(1, PHYSICAL_STEPS + 1):
        if step not in reference or step not in observed:
            continue
        observed_net = float(observed[step]["liquid_net_kgs"])
        reference_net = float(reference[step]["liquid_net_kgs"])
        rows.append(
            {
                "additional_step": step,
                "sample_role": "pre_step" if step <= ACTUATION_AFTER_STEP else "post_step",
                "fixed_pressure_liquid_net_kg_s": reference_net,
                "pressure_step_liquid_net_kg_s": observed_net,
                "delta_liquid_net_kg_s": observed_net - reference_net,
                "pressure_used_pa": observed[step].get("controller_pressure_used_pa"),
            }
        )

    post = [row for row in rows if row["additional_step"] > ACTUATION_AFTER_STEP]
    onset_step: int | None = None
    for index in range(max(0, len(post) - 2)):
        window = post[index : index + 3]
        if len(window) == 3 and all(
            float(row["delta_liquid_net_kg_s"]) >= DELTA_ONSET_THRESHOLD_KG_S
            for row in window
        ):
            onset_step = int(window[0]["additional_step"])
            break

    final_five = post[-5:]
    final_mean = (
        sum(float(row["delta_liquid_net_kg_s"]) for row in final_five) / 5.0
        if len(final_five) == 5
        else math.nan
    )
    tolerance = max(
        SETTLE_ABSOLUTE_FLOOR_KG_S,
        SETTLE_RELATIVE_TOLERANCE * abs(final_mean) if math.isfinite(final_mean) else math.inf,
    )
    settled_step: int | None = None
    for index in range(max(0, len(post) - 4)):
        window = post[index : index + 5]
        values = [float(row["delta_liquid_net_kg_s"]) for row in window]
        within_final_band = all(abs(value - final_mean) <= tolerance for value in values)
        five_step_change = abs(values[-1] - values[0])
        negligible_slope = five_step_change <= tolerance
        if len(window) == 5 and within_final_band and negligible_slope:
            settled_step = int(window[0]["additional_step"])
            break

    response_sign_passed = onset_step is not None
    plateau_passed = settled_step is not None
    return {
        "reference_history": str(REFERENCE_HISTORY),
        "actuation_after_additional_step": ACTUATION_AFTER_STEP,
        "pressure_before_pa": INITIAL_PRESSURE_PA,
        "pressure_after_pa": FINAL_PRESSURE_PA,
        "pressure_change_pa": PRESSURE_CHANGE_PA,
        "delta_definition": "pressure-step liquid_net minus matched fixed-pressure liquid_net",
        "expected_sign": "positive; higher brine pressure reduces liquid drainage",
        "response_onset_rule": (
            "first of three consecutive post-actuation steps with delta >= 0.0005 kg/s"
        ),
        "response_onset_additional_step": onset_step,
        "response_delay_steps": (
            onset_step - ACTUATION_AFTER_STEP if onset_step is not None else None
        ),
        "response_delay_seconds": (
            (onset_step - ACTUATION_AFTER_STEP) * 1.28e-4
            if onset_step is not None
            else None
        ),
        "final_five_delta_mean_kg_s": final_mean,
        "settling_band_kg_s": tolerance,
        "settled_window_start_additional_step": settled_step,
        "response_sign_passed": response_sign_passed,
        "plateau_passed": plateau_passed,
        "passed": response_sign_passed and plateau_passed,
        "rows": rows,
    }


def rewrite_response_evidence() -> None:
    run_root = controller.probe.PROJECT_ROOT / "output" / controller.probe.STUDY_ID / RUN_LABEL
    campaign_path = run_root / "campaign_manifest.json"
    member_path = run_root / MEMBER / "member_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    member = json.loads(member_path.read_text(encoding="utf-8")) if member_path.exists() else {}
    analysis = response_analysis(member) if member else {"passed": False, "rows": []}
    completed = member.get("status") == "completed"
    residual = bool(member.get("residual_gate", {}).get("passed"))
    physical_gates = all(
        not step.get("gate_failures") for step in member.get("steps", [])
    )
    accepted = completed and residual and physical_gates and bool(analysis.get("passed"))
    classification = (
        "accepted diagnostic / open-loop 0.05%-feed +5 Pa response identification"
        if accepted
        else "diagnostic / unresolved open-loop 0.05%-feed +5 Pa response identification"
    )
    campaign.pop("adaptive_pressure_controller", None)
    campaign.update(
        {
            "status": "completed" if completed else campaign.get("status"),
            "classification": classification,
            "eligible_parent": False,
            "controller_use_authorized": accepted,
            "one_factor_change": (
                "relative to the matched fixed-pressure 0.05%-feed history: one +5 Pa "
                "brine-pressure command is applied after fully monitoring additional step 10; "
                "parent, feeds, timestep, inner iterations and physics are unchanged"
            ),
            "response_identification": analysis,
            "pressure_step_checkpoint_semantics": (
                "the step-10 field advanced at pressure_before_pa; its saved case is prepared "
                "with pressure_after_pa for step 11. Every row records controller_pressure_used_pa."
            ),
            "next_action_if_unsettled": (
                "run a longer independently cold-loaded matched fixed/+5 Pa identification; "
                "do not tune another controller from an unconfirmed plateau"
            ),
            "acceptance_limitation": (
                "This can identify a numerical drainage response delay only. It does not "
                "validate plant pressure, downstream resistance, operating level or level control."
            ),
        }
    )
    controller.probe.write_json(campaign_path, campaign)
    if member:
        member.update(
            {
                "classification": classification + " member",
                "eligible_parent": False,
                "response_identification": analysis,
            }
        )
        controller.probe.write_json(member_path, member)
        controller.probe.write_csv(
            run_root / MEMBER / "matched_pressure_response_history.csv",
            analysis.get("rows", []),
        )


def main() -> int:
    run_root = controller.probe.PROJECT_ROOT / "output" / controller.probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")
    if not REFERENCE_HISTORY.exists():
        raise FileNotFoundError(f"missing fixed-pressure reference: {REFERENCE_HISTORY}")

    controller.RUN_LABEL = RUN_LABEL
    controller.MEMBER = MEMBER
    controller.PHYSICAL_STEPS = PHYSICAL_STEPS
    controller.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
    controller.CONTROL_FIRST_UPDATE_AFTER_STEP = ACTUATION_AFTER_STEP
    controller.CONTROL_POLICY = "forced_pressure_step"
    controller.FORCED_PRESSURE_CHANGE_BY_STEP = {ACTUATION_AFTER_STEP: PRESSURE_CHANGE_PA}
    controller.INITIAL_PRESSURE_PA = INITIAL_PRESSURE_PA
    try:
        return controller.main()
    finally:
        rewrite_response_evidence()


if __name__ == "__main__":
    raise SystemExit(main())

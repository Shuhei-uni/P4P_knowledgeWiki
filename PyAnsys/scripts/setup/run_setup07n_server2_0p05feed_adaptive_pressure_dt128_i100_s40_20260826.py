#!/usr/bin/env python3
"""Run a bounded adaptive-pressure 0.05%-feed drainage diagnostic.

The fixed-pressure long hold showed that an initially balanced brine pressure
did not keep drainage matched to liquid feed as the transient evolved.  This
runner independently cold-loads the checksum-bound server-2 step-90 parent and
changes only the brine pressure treatment: after each fully monitored step, a
damped, bracket-limited proportional update uses the liquid phase imbalance to
set the pressure for the next step.  It is a numerical flow-balance controller,
not a plant pressure or validated liquid-level controller.
"""

from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_0p05feed_adaptivep_g0p25_dp5_dt128_i100_s40_a1_20260826"
MEMBER = "feed_0p05_percent_adaptive_pressure_dt128_inner100"
FRACTION = 0.0005
LIQUID_FEED_KG_S = 116.92 * FRACTION
VAPOR_FEED_KG_S = 80.69 * FRACTION
INITIAL_PRESSURE_PA = 1_122_263.6212370484
PRESSURE_MIN_PA = 1_122_154.344427
PRESSURE_MAX_PA = 1_122_544.655573
HYDRAULIC_SLOPE_KG_S_PER_PA = 0.0014982128654954865
PROPORTIONAL_GAIN = 0.25
MAX_PRESSURE_CHANGE_PA = 5.0
PHYSICAL_STEPS = 40
CHECKPOINT_STEPS = {1, 5, 10, 20, 40}
CONTROL_FIRST_UPDATE_AFTER_STEP = 1
CONTROL_POLICY = "proportional_every_step"
FORCED_PRESSURE_CHANGE_BY_STEP: dict[int, float] = {}
FINAL_BALANCE_TOLERANCE_KG_S = 0.005
SUSTAINED_BALANCE_STEPS = 5
GROSS_BALANCE_LIMIT_KG_S = 0.10


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def set_existing_brine_pressure(solver: Any, pressure_pa: float) -> dict[str, Any]:
    """Change only the existing brine pressure value and prove its readback."""

    outlets = solver.settings.setup.boundary_conditions.pressure_outlet
    if "brineoutlet" not in outlets.get_object_names():
        raise RuntimeError("adaptive pressure update requires an existing brine pressure outlet")
    outlet = outlets["brineoutlet"]
    requested = copy.deepcopy(dict(outlet.get_state()))
    gauge = nested(requested, "phase", "mixture", "momentum", "gauge_pressure")
    if not isinstance(gauge, dict):
        raise RuntimeError("brine pressure outlet lacks the mixture gauge-pressure branch")
    gauge.update({"option": "value", "value": float(pressure_pa)})
    outlet.set_state(requested)
    # A boundary mutation can invalidate Settings handles.  Reacquire both
    # the collection and object before proving the pressure readback.
    outlets = solver.settings.setup.boundary_conditions.pressure_outlet
    outlet = outlets["brineoutlet"]
    readback = outlet.get_state()
    actual = nested(readback, "phase", "mixture", "momentum", "gauge_pressure", "value")
    if actual is None or not math.isclose(
        float(actual), pressure_pa, rel_tol=0.0, abs_tol=1.0e-5
    ):
        raise RuntimeError(
            f"adaptive brine pressure readback mismatch: requested={pressure_pa}, actual={actual}"
        )
    return {"requested_pressure_pa": pressure_pa, "actual_pressure_pa": float(actual)}


def sustained_balance_gate(result: Mapping[str, Any]) -> dict[str, Any]:
    rows = [step["metrics"] for step in result.get("steps", [])]
    tail = rows[-SUSTAINED_BALANCE_STEPS:]
    phase_keys = ("liquid_net_kgs", "vapor_net_kgs", "mixture_net_kgs")
    maxima = {
        key: max((abs(float(row[key])) for row in tail), default=math.inf)
        for key in phase_keys
    }
    passed = len(tail) == SUSTAINED_BALANCE_STEPS and all(
        value <= FINAL_BALANCE_TOLERANCE_KG_S for value in maxima.values()
    )
    return {
        "required_tail_steps": SUSTAINED_BALANCE_STEPS,
        "tolerance_kg_s": FINAL_BALANCE_TOLERANCE_KG_S,
        "tail_additional_steps": [int(row["additional_step"]) for row in tail],
        "maximum_absolute_tail_imbalance_kg_s": maxima,
        "passed": passed,
    }


def rewrite_adaptive_evidence() -> None:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    campaign_path = run_root / "campaign_manifest.json"
    if not campaign_path.exists():
        return
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8")) if member_path.exists() else {}
    balance = sustained_balance_gate(member) if member else {"passed": False}
    residual = bool(member.get("residual_gate", {}).get("passed"))
    completed = member.get("status") == "completed"
    passed = completed and residual and bool(balance.get("passed"))
    classification = (
        "accepted diagnostic / adaptive-pressure 0.05%-feed flow balance"
        if passed
        else "diagnostic / unresolved adaptive-pressure 0.05%-feed flow balance"
    )
    campaign.update(
        {
            "status": "completed" if completed else campaign.get("status"),
            "classification": classification,
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": (
                "relative to the stopped fixed-pressure 0.05%-feed long hold: "
                "bounded adaptive brine pressure replaces fixed brine pressure; "
                "parent, feed, timestep, inner iterations and all physics are unchanged"
            ),
            "adaptive_pressure_controller": {
                "type": "damped proportional liquid-flow-balance diagnostic",
                "initial_pressure_pa": INITIAL_PRESSURE_PA,
                "pressure_bounds_pa": [PRESSURE_MIN_PA, PRESSURE_MAX_PA],
                "hydraulic_slope_kg_s_per_pa": HYDRAULIC_SLOPE_KG_S_PER_PA,
                "slope_source": "accepted server-2 zero-feed pressure-response bracket",
                "proportional_gain": PROPORTIONAL_GAIN,
                "maximum_pressure_change_per_step_pa": MAX_PRESSURE_CHANGE_PA,
                "first_update_after_additional_step": CONTROL_FIRST_UPDATE_AFTER_STEP,
                "control_error": "liquid inlet plus signed liquid brine-outlet flow",
                "update": "delta_p = -gain * liquid_net / slope, clipped to bounds",
                "plant_boundary_validated": False,
                "operating_level_validated": False,
            },
            "sustained_phase_mass_balance_gate": balance,
            "acceptance_limitation": (
                "Passing would establish only bounded numerical flow balance with an "
                "emergent liquid seal. It does not validate plant pressure, downstream "
                "resistance, operating level, full-flow drainage or level control."
            ),
        }
    )
    probe.write_json(campaign_path, campaign)
    if member:
        member.update(
            {
                "classification": classification + " member",
                "eligible_parent": False,
                "inlet_fraction": FRACTION,
                "liquid_feed_kg_s": LIQUID_FEED_KG_S,
                "vapor_feed_kg_s": VAPOR_FEED_KG_S,
                "sustained_phase_mass_balance_gate": balance,
            }
        )
        probe.write_json(member_path, member)


def main() -> int:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")

    state: dict[str, Any] = {
        "solver": None,
        "pressure_pa": INITIAL_PRESSURE_PA,
        "pending_pressure_pa": None,
        "pending_step": None,
        "installed_settings_gate": None,
    }
    base_row_gate = probe.row_gate
    base_settings_gate = probe.open_settings_gate
    original_probe_main = probe.main

    def adaptive_row_gate(row: Mapping[str, Any], transcript_text: str) -> list[str]:
        failures = list(base_row_gate(row, transcript_text))
        current_pressure = float(state["pressure_pa"])
        liquid_net = float(row["liquid_net_kgs"])
        total_net = float(row["mixture_net_kgs"])
        step = int(row["additional_step"])
        controller_active = step >= CONTROL_FIRST_UPDATE_AFTER_STEP
        if CONTROL_POLICY == "proportional_every_step":
            update_due = controller_active
            raw_delta = (
                -PROPORTIONAL_GAIN * liquid_net / HYDRAULIC_SLOPE_KG_S_PER_PA
                if update_due
                else 0.0
            )
        elif CONTROL_POLICY == "forced_pressure_step":
            update_due = step in FORCED_PRESSURE_CHANGE_BY_STEP
            raw_delta = float(FORCED_PRESSURE_CHANGE_BY_STEP.get(step, 0.0))
        else:
            raise RuntimeError(f"unknown controller policy: {CONTROL_POLICY}")
        clipped_delta = max(
            -MAX_PRESSURE_CHANGE_PA, min(MAX_PRESSURE_CHANGE_PA, raw_delta)
        )
        requested = max(
            PRESSURE_MIN_PA, min(PRESSURE_MAX_PA, current_pressure + clipped_delta)
        )
        row.update(
            {
                "controller_active": controller_active,
                "controller_policy": CONTROL_POLICY,
                "controller_update_due": update_due,
                "controller_pressure_used_pa": current_pressure,
                "controller_liquid_balance_error_kg_s": liquid_net,
                "controller_raw_pressure_change_pa": raw_delta,
                "controller_clipped_pressure_change_pa": requested - current_pressure,
                "controller_next_pressure_pa": requested,
                "controller_pressure_at_lower_bound": math.isclose(
                    requested, PRESSURE_MIN_PA, rel_tol=0.0, abs_tol=1.0e-9
                ),
                "controller_pressure_at_upper_bound": math.isclose(
                    requested, PRESSURE_MAX_PA, rel_tol=0.0, abs_tol=1.0e-9
                ),
            }
        )
        if abs(liquid_net) > GROSS_BALANCE_LIMIT_KG_S:
            failures.append(
                f"gross liquid phase imbalance exceeds {GROSS_BALANCE_LIMIT_KG_S} kg/s: {liquid_net}"
            )
        if abs(total_net) > GROSS_BALANCE_LIMIT_KG_S:
            failures.append(
                f"gross total imbalance exceeds {GROSS_BALANCE_LIMIT_KG_S} kg/s: {total_net}"
            )
        if update_due and step < PHYSICAL_STEPS:
            state["pending_pressure_pa"] = requested
            state["pending_step"] = step
        else:
            state["pending_pressure_pa"] = None
            state["pending_step"] = None
        return sorted(set(failures))

    def adaptive_settings_gate(solver: Any, _requested_pressure_pa: float) -> dict[str, Any]:
        current_pressure = float(state["pressure_pa"])
        installed_gate = state.get("installed_settings_gate") or base_settings_gate
        before = installed_gate(solver, current_pressure)
        before_passed = bool(before.get("passed"))
        controller: dict[str, Any] = {
            "pressure_before_pa": current_pressure,
            "pre_update_settings_passed": before_passed,
            "pending_from_additional_step": state.get("pending_step"),
        }
        pending = state.get("pending_pressure_pa")
        if pending is not None:
            controller["pressure_update_readback"] = set_existing_brine_pressure(
                solver, float(pending)
            )
            state["pressure_pa"] = float(pending)
            state["pending_pressure_pa"] = None
            state["pending_step"] = None
            after = installed_gate(solver, float(state["pressure_pa"]))
            after_passed = bool(after.get("passed"))
            controller["pressure_after_pa"] = float(state["pressure_pa"])
            controller["post_update_settings_passed"] = after_passed
            result = after
            passed = before_passed and after_passed
        else:
            result = before
            passed = before_passed
        result["controller"] = controller
        result["passed"] = passed
        return result

    def adaptive_probe_main() -> int:
        probe.PHYSICAL_STEPS = PHYSICAL_STEPS
        probe.CHECKPOINT_STEPS = set(CHECKPOINT_STEPS)
        probe.row_gate = adaptive_row_gate
        # The nested feed runner installs its exact non-zero inlet gate before
        # it delegates here. Preserve and wrap that gate so every pressure
        # update continues to prove both phase inlet rates.
        state["installed_settings_gate"] = probe.open_settings_gate
        probe.open_settings_gate = adaptive_settings_gate
        return original_probe_main()

    def adaptive_comparison(results: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
        result = results[MEMBER]
        endpoint = result["endpoint"]
        balance = sustained_balance_gate(result)
        residual = bool(result.get("residual_gate", {}).get("passed"))
        seal = (
            float(endpoint["brine_face_liquid_vf_min"]) >= 0.99
            and abs(float(endpoint["vapor_brineoutlet_kgs"])) <= 1.0e-3
            and abs(float(endpoint["liquid_steamoutlet_kgs"])) <= 1.0e-3
        )
        return {
            "inlet_fraction": FRACTION,
            "time_step_size_s": 1.28e-4,
            "inner_iterations_per_step": 100,
            "physical_steps": PHYSICAL_STEPS,
            "endpoint_pressure_used_pa": endpoint.get("controller_pressure_used_pa"),
            "endpoint_next_pressure_pa": endpoint.get("controller_next_pressure_pa"),
            "endpoint_liquid_net_kg_s": endpoint["liquid_net_kgs"],
            "endpoint_vapor_net_kg_s": endpoint["vapor_net_kgs"],
            "endpoint_total_net_kg_s": endpoint["mixture_net_kgs"],
            "residual_gate_passed": residual,
            "steam_seal_passed": seal,
            "sustained_phase_mass_balance_gate": balance,
            "passed": residual and seal and bool(balance["passed"]),
        }

    # The nested source runner installs the exact clean step-90 parent and the
    # accepted feed/readback package.  These assignments alter only the new
    # process and preserve every prior branch.
    source.RUN_LABEL = RUN_LABEL
    source.MEMBER = MEMBER
    source.FRACTION = FRACTION
    source.TARGET_PRESSURE_PA = INITIAL_PRESSURE_PA
    source.TARGET_LIQUID_DRAIN_KGS = LIQUID_FEED_KG_S
    source.source.source.comparison = adaptive_comparison
    probe.main = adaptive_probe_main
    try:
        return source.main()
    finally:
        rewrite_adaptive_evidence()


if __name__ == "__main__":
    raise SystemExit(main())

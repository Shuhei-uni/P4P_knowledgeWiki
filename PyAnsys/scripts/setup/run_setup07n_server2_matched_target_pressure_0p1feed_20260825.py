#!/usr/bin/env python3
"""Run matched zero-feed and 0.1%-feed drainage members at one pressure.

Both members cold-load the exact clean server-2 step-90 closed-pool parent,
open the brine outlet at the linear pressure-bracket estimate for 0.11692 kg/s
outward liquid drainage, and retain ``dt=2.56e-4 s`` with 20 inner iterations.
Only inlet fraction differs between the independently loaded members.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_server2_step90_matched_targetpressure_zero_vs_0p1feed_"
    "dt256em6_inner20_steps10_attempt1_20260825"
)
PARENT_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_server2_independent_"
    "dt256em6_attempt1_20260824_additional_step10"
)
PARENT_CASE = probe.REMOTE_ROOT + rf"\{PARENT_LABEL}.cas.h5"
PARENT_DATA = probe.REMOTE_ROOT + rf"\{PARENT_LABEL}.dat.h5"
PARENT_CASE_SHA256 = "763fae763ce43c36505c7dc06986082f361e257c93afc778b5583a41dd15fd22"
PARENT_DATA_SHA256 = "9513a957ae42e59db076466754a226c44b7bfdfa7f8a69b40e44139fa2bae6b7"
INITIAL_TIME_STEP = 90
INITIAL_FLOW_TIME_S = 0.005110000000000003
TARGET_PRESSURE_PA = 1_122_207.446241885
TARGET_LIQUID_OUTWARD_KG_S = 0.11692
MEMBER_FRACTIONS = {"zero_feed": 0.0, "feed_0p1_percent": 0.001}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("2",), default="2")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def fraction_gate(solver: Any, fraction: float) -> dict[str, Any]:
    expected = {
        "liquidinlet": {"phase-1": 0.0, "phase-2": 116.92 * fraction},
        "steaminlet": {"phase-1": 80.69 * fraction, "phase-2": 0.0},
    }
    inlets = solver.settings.setup.boundary_conditions.mass_flow_inlet
    states: dict[str, Any] = {}
    readback: dict[str, Any] = {}
    passed = True
    for zone, phase_values in expected.items():
        state = inlets[zone].get_state()
        states[zone] = state
        readback[zone] = {}
        for phase, target in phase_values.items():
            actual = nested(
                state, "phase", phase, "momentum", "mass_flow_rate", "value"
            )
            readback[zone][phase] = actual
            passed = passed and actual is not None and math.isclose(
                float(actual), target, rel_tol=0.0, abs_tol=1.0e-8
            )
    return {
        "fraction": fraction,
        "expected": expected,
        "readback": readback,
        "states": states,
        "passed": passed,
    }


def comparison(results: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    zero = results["zero_feed"]["endpoint"]
    feed = results["feed_0p1_percent"]["endpoint"]
    all_residual = all(
        bool(result["residual_gate"]["passed"]) for result in results.values()
    )
    seal = all(
        float(result["endpoint"]["brine_face_liquid_vf_min"]) >= 0.99
        and abs(float(result["endpoint"]["vapor_brineoutlet_kgs"])) <= 1.0e-3
        and abs(float(result["endpoint"]["liquid_steamoutlet_kgs"])) <= 1.0e-3
        for result in results.values()
    )
    physical = all(
        abs(float(result["endpoint"][f"{phase}_storage_closure_residual_kg_s"]))
        <= 5.0
        for result in results.values()
        for phase in ("liquid", "vapor")
    )
    feed_liquid_balance = abs(float(feed["liquid_net_kgs"])) <= 0.05
    inventory_bounded = abs(float(feed["liquid_inventory_change_from_parent_kg"])) <= 0.01
    passed = all_residual and seal and physical and feed_liquid_balance and inventory_bounded
    return {
        "pressure_pa": TARGET_PRESSURE_PA,
        "pressure_basis": "linear interpolation of accepted zero-feed pressure-response bracket to -0.11692 kg/s liquid",
        "zero_feed_liquid_brineoutlet_kgs": zero["liquid_brineoutlet_kgs"],
        "feed_liquid_brineoutlet_kgs": feed["liquid_brineoutlet_kgs"],
        "feed_liquid_inlet_kgs": feed["liquid_liquidinlet_kgs"],
        "feed_liquid_net_kgs": feed["liquid_net_kgs"],
        "all_member_residual_gates_passed": all_residual,
        "steam_seal_passed": seal,
        "phase_storage_closure_passed": physical,
        "feed_liquid_net_within_0p05_kgs": feed_liquid_balance,
        "feed_inventory_change_within_0p01_kg": inventory_bounded,
        "passed": passed,
    }


def rewrite_final_evidence(run_root: Path) -> None:
    campaign_path = run_root / "campaign_manifest.json"
    campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
    passed = bool(campaign.get("comparison_gate", {}).get("passed"))
    campaign.update(
        {
            "classification": (
                "accepted diagnostic / matched target-pressure 0.1%-feed drainage"
                if passed
                else "diagnostic / unresolved matched target-pressure 0.1%-feed drainage"
            ),
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": "matched independently cold-loaded members; inlet fraction 0 versus 0.001 only",
            "acceptance_limitation": "The pressure is interpolated from a CFD zero-feed response and is not a plant boundary. Passing establishes only bounded low-feed drainage and an emergent liquid seal.",
        }
    )
    probe.write_json(campaign_path, campaign)
    for member, fraction in MEMBER_FRACTIONS.items():
        path = run_root / member / "member_manifest.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload.update(
            {
                "inlet_fraction": fraction,
                "classification": (
                    "accepted diagnostic / matched target-pressure member"
                    if payload.get("status") == "completed"
                    and payload.get("residual_gate", {}).get("passed")
                    else payload.get("classification")
                ),
                "eligible_parent": False,
            }
        )
        probe.write_json(path, payload)


def main() -> int:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")

    probe.parser = parser
    probe.RUN_LABEL = RUN_LABEL
    probe.PARENT_LABEL = PARENT_LABEL
    probe.PARENT_CASE = PARENT_CASE
    probe.PARENT_DATA = PARENT_DATA
    probe.PARENT_CASE_SHA256 = PARENT_CASE_SHA256
    probe.PARENT_DATA_SHA256 = PARENT_DATA_SHA256
    probe.INITIAL_TIME_STEP = INITIAL_TIME_STEP
    probe.INITIAL_FLOW_TIME_S = INITIAL_FLOW_TIME_S
    probe.TIME_STEP_SIZE_S = 2.56e-4
    probe.INNER_ITERATIONS = 20
    probe.PHYSICAL_STEPS = 10
    probe.CHECKPOINT_STEPS = {1, 5, 10}
    probe.CENTRE_PRESSURE_PA = TARGET_PRESSURE_PA
    probe.PRESSURE_MEMBERS = tuple(
        (member, TARGET_PRESSURE_PA) for member in MEMBER_FRACTIONS
    )
    probe.LOCAL_ROOT = run_root
    probe.GLOBAL_WRITER_LOCK = (
        probe.PROJECT_ROOT
        / "output"
        / probe.STUDY_ID
        / "setup07n_server2_independent_writer.lock"
    )
    probe.sweep.remote_delete_best_effort = lambda _solver, _path: True

    original_run_member = probe.run_member
    original_open = probe.opening07m.open_brine_pressure_outlet
    original_gate = probe.open_settings_gate
    current = {"member": ""}

    def run_member(solver: Any, member: str, pressure_pa: float, inventory: float):
        current["member"] = member
        return original_run_member(solver, member, pressure_pa, inventory)

    def open_and_set_fraction(solver: Any, pressure_pa: float):
        result = original_open(solver, pressure_pa)
        probe.opening07m.set_inlet_fraction(
            solver, MEMBER_FRACTIONS[current["member"]]
        )
        return result

    def matched_gate(solver: Any, pressure_pa: float):
        result = original_gate(solver, pressure_pa)
        result["inlets"] = fraction_gate(
            solver, MEMBER_FRACTIONS[current["member"]]
        )
        result["passed"] = all(
            bool(result[key].get("passed"))
            for key in ("boundary", "methods", "dpm", "sources", "ewf", "inlets")
        )
        return result

    probe.run_member = run_member
    probe.opening07m.open_brine_pressure_outlet = open_and_set_fraction
    probe.open_settings_gate = matched_gate
    probe.comparison_gate = comparison
    sys.argv = [sys.argv[0], "--server-id", "2", "--tcp-timeout-seconds", "5.0"]
    result = probe.main()
    rewrite_final_evidence(run_root)
    return result


if __name__ == "__main__":
    raise SystemExit(main())

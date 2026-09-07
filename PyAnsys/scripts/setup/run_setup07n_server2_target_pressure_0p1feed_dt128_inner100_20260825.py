#!/usr/bin/env python3
"""Repeat 0.1%-feed target-pressure drainage at dt=128 us, inner=100."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_matched_target_pressure_0p1feed_20260825 as base  # noqa: E402
import run_setup07n_server2_target_pressure_0p1feed_inner100_20260825 as inner100  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_server2_step90_targetpressure_0p1feed_"
    "dt128em6_inner100_steps10_attempt1_20260825"
)
MEMBER = "feed_0p1_percent_dt128_inner100"
FRACTION = 0.001


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("2",), default="2")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def comparison(results):
    result = results[MEMBER]
    endpoint = result["endpoint"]
    residual = bool(result["residual_gate"]["passed"])
    seal = (
        float(endpoint["brine_face_liquid_vf_min"]) >= 0.99
        and abs(float(endpoint["vapor_brineoutlet_kgs"])) <= 1.0e-3
        and abs(float(endpoint["liquid_steamoutlet_kgs"])) <= 1.0e-3
    )
    storage = all(
        abs(float(endpoint[f"{phase}_storage_closure_residual_kg_s"])) <= 5.0
        for phase in ("liquid", "vapor")
    )
    inventory = abs(float(endpoint["liquid_inventory_change_from_parent_kg"])) <= 0.01
    return {
        "pressure_pa": base.TARGET_PRESSURE_PA,
        "inlet_fraction": FRACTION,
        "time_step_size_s": 1.28e-4,
        "liquid_inlet_kgs": endpoint["liquid_liquidinlet_kgs"],
        "liquid_brineoutlet_kgs": endpoint["liquid_brineoutlet_kgs"],
        "liquid_net_kgs": endpoint["liquid_net_kgs"],
        "residual_gate_passed": residual,
        "steam_seal_passed": seal,
        "storage_closure_passed": storage,
        "inventory_gate_passed": inventory,
        "passed": residual and seal and storage and inventory,
    }


def rewrite(run_root: Path) -> None:
    campaign_path = run_root / "campaign_manifest.json"
    payload = json.loads(campaign_path.read_text(encoding="utf-8"))
    passed = bool(payload.get("comparison_gate", {}).get("passed"))
    payload.update(
        {
            "classification": (
                "accepted diagnostic / 0.1%-feed target-pressure drainage dt128us"
                if passed
                else "diagnostic / unresolved 0.1%-feed target-pressure drainage dt128us"
            ),
            "eligible_parent": False,
            "controller_use_authorized": passed,
            "one_factor_change": "relative to failed dt256us inner100 member: timestep 256 us -> 128 us only",
            "acceptance_limitation": "The outlet pressure is CFD-interpolated, not a plant boundary. This is a bounded low-feed timestep sensitivity.",
        }
    )
    probe.write_json(campaign_path, payload)
    member_path = run_root / MEMBER / "member_manifest.json"
    member = json.loads(member_path.read_text(encoding="utf-8"))
    member.update(
        {
            "inlet_fraction": FRACTION,
            "time_step_size_s": 1.28e-4,
            "inner_iterations_per_step": 100,
            "classification": (
                "accepted diagnostic / 0.1%-feed target-pressure member dt128us"
                if member.get("status") == "completed"
                and member.get("residual_gate", {}).get("passed")
                else member.get("classification")
            ),
            "eligible_parent": False,
        }
    )
    probe.write_json(member_path, member)


def main() -> int:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")
    probe.parser = parser
    probe.RUN_LABEL = RUN_LABEL
    probe.PARENT_LABEL = base.PARENT_LABEL
    probe.PARENT_CASE = base.PARENT_CASE
    probe.PARENT_DATA = base.PARENT_DATA
    probe.PARENT_CASE_SHA256 = base.PARENT_CASE_SHA256
    probe.PARENT_DATA_SHA256 = base.PARENT_DATA_SHA256
    probe.INITIAL_TIME_STEP = base.INITIAL_TIME_STEP
    probe.INITIAL_FLOW_TIME_S = base.INITIAL_FLOW_TIME_S
    probe.TIME_STEP_SIZE_S = 1.28e-4
    probe.INNER_ITERATIONS = 100
    probe.PHYSICAL_STEPS = 10
    probe.CHECKPOINT_STEPS = {1, 5, 10}
    probe.CENTRE_PRESSURE_PA = base.TARGET_PRESSURE_PA
    probe.PRESSURE_MEMBERS = ((MEMBER, base.TARGET_PRESSURE_PA),)
    probe.LOCAL_ROOT = run_root
    probe.GLOBAL_WRITER_LOCK = (
        probe.PROJECT_ROOT / "output" / probe.STUDY_ID / "setup07n_server2_independent_writer.lock"
    )
    probe.sweep.remote_delete_best_effort = lambda _solver, _path: True
    original_open = probe.opening07m.open_brine_pressure_outlet
    original_gate = probe.open_settings_gate

    def open_and_set_fraction(solver: Any, pressure_pa: float):
        result = original_open(solver, pressure_pa)
        probe.opening07m.set_inlet_fraction(solver, FRACTION)
        return result

    def feed_gate(solver: Any, pressure_pa: float):
        result = original_gate(solver, pressure_pa)
        result["inlets"] = base.fraction_gate(solver, FRACTION)
        result["passed"] = all(
            bool(result[key].get("passed"))
            for key in ("boundary", "methods", "dpm", "sources", "ewf", "inlets")
        )
        return result

    probe.opening07m.open_brine_pressure_outlet = open_and_set_fraction
    probe.open_settings_gate = feed_gate
    probe.comparison_gate = comparison
    sys.argv = [sys.argv[0], "--server-id", "2", "--tcp-timeout-seconds", "5.0"]
    result = probe.main()
    rewrite(run_root)
    return result


if __name__ == "__main__":
    raise SystemExit(main())

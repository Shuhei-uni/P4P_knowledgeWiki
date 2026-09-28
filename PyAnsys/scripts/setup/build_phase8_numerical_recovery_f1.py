#!/usr/bin/env python3
"""Build matched F1 Coupled/Global Time Step recovery child."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state
from build_phase8_purnanto_parity_pilots import F1_CHILD, F1_PARENT, TARGET_LIQUID, TARGET_SPEED, TARGET_VAPOR, pair
from run_phase8_parity_carrier import dump, load_pair, require, save_pair

CHILD = F1_CHILD.parents[2] / "NumericalRecovery" / "F1" / "F1-26p81-coupled-gts"
RECEIPT = ROOT / "output" / f"phase8_numerical_recovery_f1_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"


def inspect(solver, speed: float = TARGET_SPEED):
    settings = solver.settings
    methods = safe_get_state(settings.solution.methods, "methods")
    bc = safe_get_state(settings.setup.boundary_conditions, "boundaries")
    cells = safe_get_state(settings.setup.cell_zone_conditions, "cells")
    models = safe_get_state(settings.setup.models, "models")
    inlets = bc["mass_flow_inlet"]
    feeds = {zone: {phase: float(inlets[zone]["phase"][phase]["momentum"]["mass_flow_rate"]["value"])
                    for phase in ("phase-1", "phase-2")} for zone in ("liquidinlet", "steaminlet")}
    ratio = speed / TARGET_SPEED
    assert abs(sum(feeds[z]["phase-1"] for z in feeds) - TARGET_VAPOR * ratio) < 1e-5
    assert abs(sum(feeds[z]["phase-2"] for z in feeds) - TARGET_LIQUID * ratio) < 1e-5
    assert all(feeds[z]["phase-1"] > 0 and feeds[z]["phase-2"] > 0 for z in feeds)
    assert models["multiphase"]["model"] == "mixture"
    assert not models["discrete_phase"].get("injections", {})
    for zone in cells["fluid"].values():
        for phase in ("mixture", "phase-1", "phase-2"):
            assert not zone["phase"][phase]["sources"]["enable"]
    assert "bottom" in bc["wall"]
    return {"methods": methods, "feeds_kg_s": feeds,
            "inlet_turbulence": {z: inlets[z]["phase"]["mixture"]["turbulence"] for z in feeds},
            "outlet_turbulence": bc["pressure_outlet"]["steamoutlet"]["phase"]["mixture"]["turbulence"],
            "no_cell_sources": True, "no_injections": True, "closed_bottom": True}


def main():
    require(all(p.is_file() for p in pair(F1_PARENT)), "Original F1 numerical source missing")
    require(all(p.is_file() for p in pair(F1_CHILD)), "Parity F1 physical source missing")
    require(not any(p.exists() for p in pair(CHILD)), "Recovery child already exists")
    receipt = {"status": "BUILDING", "source_numerical_pair": [str(p) for p in pair(F1_PARENT)],
               "source_physical_pair": [str(p) for p in pair(F1_CHILD)],
               "controlled_delta": "Restore Phase 7.2A coupled/global-time-step numerical stack while retaining common 0.724 m inlet/backflow turbulence scale and mixed feed"}
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                           ui_mode="gui", start_timeout=240, cleanup_on_exit=True, start_transcript=True)
    try:
        load_pair(solver, F1_PARENT)
        source = inspect(solver)
        receipt["original_numerics"] = source["methods"]
        load_pair(solver, F1_CHILD)
        receipt["parity_before"] = inspect(solver)
        methods = solver.settings.solution.methods
        methods.p_v_coupling.flow_scheme = source["methods"]["p_v_coupling"]["flow_scheme"]
        methods.pseudo_time_method.set_state(source["methods"]["pseudo_time_method"])
        methods.spatial_discretization.discretization_scheme.set_state(
            source["methods"]["spatial_discretization"]["discretization_scheme"])
        after = inspect(solver)
        require(after["methods"]["p_v_coupling"] == source["methods"]["p_v_coupling"], "Coupling readback mismatch")
        require(after["methods"]["pseudo_time_method"] == source["methods"]["pseudo_time_method"], "Pseudo-time readback mismatch")
        require(after["methods"]["spatial_discretization"]["discretization_scheme"] == source["methods"]["spatial_discretization"]["discretization_scheme"], "Discretization readback mismatch")
        require(after["inlet_turbulence"] == receipt["parity_before"]["inlet_turbulence"], "Inlet turbulence changed")
        require(after["outlet_turbulence"] == receipt["parity_before"]["outlet_turbulence"], "Outlet turbulence changed")
        solver.settings.solution.initialization.hybrid_initialize()
        solver.settings.mesh.check()
        receipt["before_save"] = inspect(solver)
        receipt["child_pair"] = save_pair(solver, CHILD)
        load_pair(solver, CHILD)
        receipt["after_reopen"] = inspect(solver)
        require(receipt["after_reopen"] == receipt["before_save"], "Recovery case setting drift after reopen")
        receipt["status"] = "CASE_DATA_VERIFIED"
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(RECEIPT, receipt)
        if receipt["status"] == "CASE_DATA_VERIFIED":
            solver.exit()
    print(json.dumps({"status": receipt["status"], "receipt": str(RECEIPT), "child_pair": receipt["child_pair"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()

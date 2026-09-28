#!/usr/bin/env python3
"""Derive the 26.81 m/s split-inlet F2 base from verified F1."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.stage4_native import ensure_remote_directory
from build_phase8_f1_from_p72a_e0 import (
    AREA, DATA as F1_DATA, CHILD as F1_CASE, RHO_L, RHO_V,
    REFERENCE_LIQUID, REFERENCE_VAPOR, SPEED, require,
)

REMOTE_ROOT = r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F2"
CASE = REMOTE_ROOT + r"\F2-split-26p81-base.cas.h5"
DATA = REMOTE_ROOT + r"\F2-split-26p81-base.dat.h5"


def state_without_inlets(solver):
    settings = solver.settings
    bc = safe_get_state(settings.setup.boundary_conditions, "boundary")
    bc.pop("mass_flow_inlet", None)
    return {
        "models": safe_get_state(settings.setup.models, "models"),
        "general_solver": safe_get_state(settings.setup.general.solver, "solver"),
        "operating_conditions": safe_get_state(settings.setup.general.operating_conditions, "operating"),
        "materials": safe_get_state(settings.setup.materials, "materials"),
        "cells": safe_get_state(settings.setup.cell_zone_conditions, "cells"),
        "other_boundaries": bc,
        "methods": safe_get_state(settings.solution.methods, "methods"),
        "controls": safe_get_state(settings.solution.controls, "controls"),
    }


def inlet_audit(solver, vapor, liquid):
    inlet = safe_get_state(solver.settings.setup.boundary_conditions.mass_flow_inlet, "inlet")
    target = {
        "liquidinlet": {"phase-1": 0.0, "phase-2": liquid},
        "steaminlet": {"phase-1": vapor, "phase-2": 0.0},
    }
    readback = {}
    for zone, phases in target.items():
        readback[zone] = {}
        for phase, expected in phases.items():
            actual = float(inlet[zone]["phase"][phase]["momentum"]["mass_flow_rate"]["value"])
            require(abs(actual - expected) < 1e-5, f"{zone}/{phase}: {actual} != {expected}")
            readback[zone][phase] = actual
    return readback


def main():
    solver = connect("student", start_transcript=True, tcp_timeout_seconds=5)
    for path in (F1_CASE, F1_DATA):
        require(remote_file_exists(solver, path), f"F1 parent missing: {path}")
    require(not solver.settings.solution.run_calculation.iterating(), "solver is iterating")
    solver.settings.file.read_case(file_name=F1_CASE)
    solver.settings.file.read_data(file_name=F1_DATA)
    fixed_parent = state_without_inlets(solver)
    area_total = sum(AREA.values())
    multiplier = SPEED * area_total / (REFERENCE_VAPOR / RHO_V + REFERENCE_LIQUID / RHO_L)
    vapor = REFERENCE_VAPOR * multiplier
    liquid = REFERENCE_LIQUID * multiplier
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
    for zone, phase, value in (
        ("liquidinlet", "phase-1", 0.0),
        ("liquidinlet", "phase-2", liquid),
        ("steaminlet", "phase-1", vapor),
        ("steaminlet", "phase-2", 0.0),
    ):
        inlet[zone].phase[phase].momentum.mass_flow_rate.value = value
    before = inlet_audit(solver, vapor, liquid)
    require(state_without_inlets(solver) == fixed_parent, "non-inlet setup drift before save")
    solver.settings.mesh.check()
    solver.settings.solution.initialization.hybrid_initialize()
    ensure_remote_directory(solver, REMOTE_ROOT)
    require(not remote_file_exists(solver, CASE) and not remote_file_exists(solver, DATA), "F2 artifact exists")
    solver.settings.file.write_case(file_name=CASE)
    solver.settings.file.write_data(file_name=DATA)
    require(remote_file_exists(solver, CASE) and remote_file_exists(solver, DATA), "F2 pair missing")
    solver.settings.file.read_case(file_name=CASE)
    solver.settings.file.read_data(file_name=DATA)
    after = inlet_audit(solver, vapor, liquid)
    require(state_without_inlets(solver) == fixed_parent, "non-inlet setup drift after reopen")
    receipt = {"status": "PREPARED", "parent_case": F1_CASE, "parent_data": F1_DATA,
               "child_case": CASE, "child_data": DATA, "controlled_delta": "split pure-phase inlet",
               "target_speed_m_s": SPEED, "target_mass_kg_s": {"vapor": vapor, "liquid": liquid},
               "before_save_inlets": before, "after_reopen_inlets": after,
               "other_settings_match_F1": True, "initialization": "fresh hybrid",
               "report_definitions": "Phase 8 common reports pending"}
    out = ROOT / "output" / "phase8_f2_base_20260926.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()

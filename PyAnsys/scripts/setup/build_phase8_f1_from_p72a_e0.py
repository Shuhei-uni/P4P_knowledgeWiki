#!/usr/bin/env python3
"""Build Phase 8 F1's 26.81 m/s mixed-inlet carrier from P72A E0.

The exact parent is copied on the Fluent host to a path without spaces before
loading. The child is a case/data pair after fresh Hybrid initialization; no
Phase 7 data field or DPM injection is inherited.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state, quote_scheme_string
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_text_read

SOURCE = r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\E0\20260922T115500Z\P72A-E0-prepared.cas.h5"
PARENT_COPY = r"C:\Users\Public\phase8-p72a-e0-parent.cas.h5"
ROOT_REMOTE = r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F1"
CHILD = ROOT_REMOTE + r"\F1-mixed-26p81-base.cas.h5"
DATA = ROOT_REMOTE + r"\F1-mixed-26p81-base.dat.h5"
AREA = {"liquidinlet": 0.0048899165, "steaminlet": 0.51928608}
SPEED = 26.81
RHO_V = 5.797433853149414
RHO_L = 881.2108764648438
REFERENCE_VAPOR = 80.69
REFERENCE_LIQUID = 116.92


def require(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def same_audit(a, b) -> bool:
    for key in a:
        if key not in b:
            return False
        if key in {"readback_mass_kg_s", "target_mass_kg_s"}:
            if any(not math.isclose(a[key][phase], b[key][phase], rel_tol=1e-12, abs_tol=1e-9)
                   for phase in ("phase-1", "phase-2")):
                return False
        elif key == "nominal_speed_m_s":
            if not math.isclose(a[key], b[key], rel_tol=1e-12, abs_tol=1e-9):
                return False
        elif a[key] != b[key]:
            return False
    return True


def remote_sha256(solver, path: str, label: str) -> str:
    remote_chdir(solver, str(PureWindowsPath(path).parent))
    scratch = rf"C:\Users\Public\phase8-{label}-sha256.txt"
    cmd = f'cmd /c certutil -hashfile "{PureWindowsPath(path).name}" SHA256 > {scratch}'
    result = solver.scheme.eval(f'(system "{quote_scheme_string(cmd)}")')
    require(result == 0, f"hash command failed for {label}: {result}")
    matches = re.findall(r"(?im)^\s*([0-9a-f]{64})\s*$", remote_text_read(solver, scratch))
    require(len(matches) == 1, f"missing hash for {label}")
    return matches[0]


def audit(solver):
    models = safe_get_state(solver.settings.setup.models, "models")
    bc = safe_get_state(solver.settings.setup.boundary_conditions, "boundaries")
    cells = safe_get_state(solver.settings.setup.cell_zone_conditions, "cells")
    methods = safe_get_state(solver.settings.solution.methods, "methods")
    fluids = cells.get("fluid", {})
    require(set(fluids) == {"separator-purnanto", "p71a-v2-virtual-outlet"}, f"fluid zones {list(fluids)}")
    for name, state in fluids.items():
        for phase in ("mixture", "phase-1", "phase-2"):
            require(not state["phase"][phase]["sources"]["enable"], f"source enabled: {name}/{phase}")
    require(models["multiphase"]["model"] == "mixture", "Mixture model missing")
    require(models["viscous"]["k_epsilon_model"] == "rng", "RNG turbulence missing")
    dpm = models["discrete_phase"]
    require(not dpm["general_settings"]["interaction"]["enabled"], "DPM interaction on")
    require(not dpm["physical_models"]["erosion_accretion_enabled"], "film/accretion on")
    require(not dpm.get("injections", {}), "inherited DPM injections remain")
    require(methods["p_v_coupling"]["flow_scheme"] == "Coupled", "solver scheme drift")
    require(methods["pseudo_time_method"]["formulation"]["coupled_solver"] == "global-time-step", "pseudo time drift")
    inlet = bc["mass_flow_inlet"]
    area_total = sum(AREA.values())
    q_reference = REFERENCE_VAPOR / RHO_V + REFERENCE_LIQUID / RHO_L
    multiplier = SPEED * area_total / q_reference
    targets = {"phase-1": REFERENCE_VAPOR * multiplier, "phase-2": REFERENCE_LIQUID * multiplier}
    actual = {}
    for phase in targets:
        actual[phase] = 0.0
        for name, area in AREA.items():
            state = inlet[name]["phase"][phase]["momentum"]["mass_flow_rate"]
            value = float(state["value"])
            expected = targets[phase] * area / area_total
            require(abs(value - expected) < 1e-5, f"inlet {name}/{phase}: {value} != {expected}")
            actual[phase] += value
        require(abs(actual[phase] - targets[phase]) < 1e-5, f"total {phase} feed mismatch")
    for name in bc["wall"]:
        roughness = bc["wall"][name]["phase"]["mixture"]["turbulence"]["roughness_height"]["value"]
        require(abs(float(roughness)) < 1e-15, f"roughness on {name}")
    require("bottom" in bc["wall"] and "steamoutlet" in bc["pressure_outlet"], "boundary topology drift")
    return {"fluid_zones": list(fluids), "source_enabled": False, "DPM_interaction": False,
            "film": False, "injections": [], "flow_scheme": "Coupled", "pseudo_time": "global-time-step",
            "area_m2": AREA, "target_mass_kg_s": targets, "readback_mass_kg_s": actual,
            "nominal_speed_m_s": sum(actual[p] / rho for p, rho in (("phase-1", RHO_V), ("phase-2", RHO_L))) / area_total,
            "wall_zones": list(bc["wall"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--finalize-existing", action="store_true",
                        help="Finish the already saved case after an interrupted build; never overwrite it")
    args = parser.parse_args()
    solver = connect("student", start_transcript=True, tcp_timeout_seconds=5)
    if args.finalize_existing:
        require(remote_file_exists(solver, CHILD), "existing F1 child missing")
        require(not remote_file_exists(solver, DATA), "F1 data already exists; refusing overwrite")
        solver.settings.file.read_case(file_name=CHILD)
        pre_save = audit(solver)
        solver.settings.mesh.check()
        solver.settings.solution.initialization.hybrid_initialize()
        solver.settings.file.write_data(file_name=DATA)
        require(remote_file_exists(solver, DATA), "F1 initialized data not saved")
        solver.settings.file.read_case(file_name=CHILD)
        solver.settings.file.read_data(file_name=DATA)
        post_save = audit(solver)
        require(same_audit(pre_save, post_save), "save/reopen F1 audit mismatch")
        receipt = {"status": "PREPARED", "parent": SOURCE, "parent_copy": PARENT_COPY,
                   "child": CHILD, "data": DATA, "fluent_version": str(solver.get_fluent_version()),
                   "pre_save": pre_save, "post_reopen": post_save,
                   "initialization": "fresh hybrid; Phase 7.2A data not inherited",
                   "report_definitions": "Phase 7 reports removed; Phase 8 common reports pending"}
        local = ROOT / "output" / "phase8_f1_base_20260926.json"
        local.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2), flush=True)
        return
    require(remote_file_exists(solver, SOURCE), "Phase 7.2A E0 parent missing")
    if not remote_file_exists(solver, PARENT_COPY):
        remote_chdir(solver, str(PureWindowsPath(SOURCE).parent))
        cmd = f'cmd /c copy "{PureWindowsPath(SOURCE).name}" {PARENT_COPY}'
        require(solver.scheme.eval(f'(system "{quote_scheme_string(cmd)}")') == 0,
                "no-space parent copy failed")
    require(remote_file_exists(solver, PARENT_COPY), "no-space parent copy missing")
    require(remote_sha256(solver, SOURCE, "source") == remote_sha256(solver, PARENT_COPY, "parent-copy"),
            "no-space parent copy differs from source")
    require(not solver.settings.solution.run_calculation.iterating(), "solver is iterating")
    solver.settings.file.read_case(file_name=PARENT_COPY)
    require(solver.settings.setup.models.is_active(), "parent failed to load")
    before = safe_get_state(solver.settings.setup.cell_zone_conditions, "parent zones")
    require(set(before.get("fluid", {})) == {"separator-purnanto", "p71a-v2-virtual-outlet"}, "wrong parent topology")
    print("parent loaded", flush=True)

    # Dependency order: remove reports referencing the absorber, then remove
    # injections, disable sources, and finally change inlet phase commands.
    monitor = solver.settings.solution.monitor
    for branch_name in ("report_files", "report_plots"):
        branch = getattr(monitor, branch_name)
        names = list(branch.get_object_names())
        if names:
            branch.delete(name_list=names)
    definitions = solver.settings.solution.report_definitions
    for branch_name in ("flux", "surface", "volume", "single_valued_expression"):
        branch = getattr(definitions, branch_name)
        names = list(branch.get_object_names())
        if names:
            branch.delete(name_list=names)
    dpm = solver.settings.setup.models.discrete_phase
    names = list(dpm.injections.get_object_names())
    if names:
        dpm.injections.delete(name_list=names)
    dpm.general_settings.interaction.enabled = False
    dpm.physical_models.erosion_accretion_enabled = False
    cells = solver.settings.setup.cell_zone_conditions.fluid
    for name in cells.get_object_names():
        for phase in ("mixture", "phase-1", "phase-2"):
            cells[name].phase[phase].sources.enable = False
    expressions = solver.settings.setup.named_expressions
    names = [name for name in expressions.get_object_names() if name.startswith("P71V2")]
    if names:
        expressions.delete(name_list=names)

    area_total = sum(AREA.values())
    multiplier = SPEED * area_total / (REFERENCE_VAPOR / RHO_V + REFERENCE_LIQUID / RHO_L)
    targets = {"phase-1": REFERENCE_VAPOR * multiplier, "phase-2": REFERENCE_LIQUID * multiplier}
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
    for name, area in AREA.items():
        for phase, target in targets.items():
            inlet[name].phase[phase].momentum.mass_flow_rate.value = target * area / area_total
    pre_save = audit(solver)
    solver.settings.mesh.check()
    # Fresh field: the Phase 7.2A flow solution is not F1 initial data.
    solver.settings.solution.initialization.hybrid_initialize()
    ensure_remote_directory(solver, ROOT_REMOTE)
    require(not remote_file_exists(solver, CHILD), "refusing to overwrite existing F1 base")
    solver.settings.file.write_case(file_name=CHILD)
    require(remote_file_exists(solver, CHILD), "F1 case not saved")
    require(not remote_file_exists(solver, DATA), "refusing to overwrite existing F1 data")
    solver.settings.file.write_data(file_name=DATA)
    require(remote_file_exists(solver, DATA), "F1 data not saved")
    solver.settings.file.read_case(file_name=CHILD)
    solver.settings.file.read_data(file_name=DATA)
    post_save = audit(solver)
    require(same_audit(pre_save, post_save), "save/reopen F1 audit mismatch")
    receipt = {"status": "PREPARED", "parent": SOURCE, "parent_copy": PARENT_COPY,
               "child": CHILD, "data": DATA, "fluent_version": str(solver.get_fluent_version()),
               "pre_save": pre_save, "post_reopen": post_save,
               "initialization": "fresh hybrid; Phase 7.2A data not inherited",
               "report_definitions": "Phase 7 reports removed; Phase 8 common reports pending"}
    local = ROOT / "output" / "phase8_f1_base_20260926.json"
    local.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()

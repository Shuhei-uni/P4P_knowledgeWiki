#!/usr/bin/env python3
"""Build Purnanto-parity F1/F2 children from the retained Phase 8 base pairs.

This preserves the 60k Phase 8 geometry and 26.81 m/s design feed while
restoring the saved historical 00a numerical and turbulence-length-scale
choices that can be represented on this mesh.  It creates paired children
and never overwrites the existing Phase 8 bases.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
from datetime import datetime, timezone
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state

RUNS = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8")
F1_PARENT = RUNS / "F1" / "F1-mixed-26p81-base"
F1_CHILD = RUNS / "PurnantoParity" / "F1" / "F1-purnanto-parity-26p81"
F2_CHILD = RUNS / "PurnantoParity" / "F2" / "F2-purnanto-parity-26p81"
OUT = ROOT / "output" / f"phase8_purnanto_parity_pilots_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
AREA = {"liquidinlet": 0.0048899165, "steaminlet": 0.51928608}
TARGET_SPEED = 26.81
TARGET_VAPOR = 80.70292372
TARGET_LIQUID = 116.93872650
INLETS = tuple(AREA)
FLUID_ZONES = ("separator-purnanto", "p71a-v2-virtual-outlet")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def pair(base: Path) -> tuple[Path, Path]:
    return base.with_suffix(".cas.h5"), base.with_suffix(".dat.h5")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_new(base: Path) -> None:
    case, data = pair(base)
    if case.exists() or data.exists():
        raise FileExistsError(f"Refusing to overwrite existing child pair: {case}, {data}")
    base.parent.mkdir(parents=True, exist_ok=True)


def load_pair(solver: Any, base: Path) -> None:
    case, data = pair(base)
    require(case.is_file() and data.is_file(), f"Missing paired Fluent source: {case} / {data}")
    solver.settings.file.read_case(file_name=str(case))
    solver.settings.file.read_data(file_name=str(data))


def audit(solver: Any, *, exact_flows: bool) -> dict[str, Any]:
    settings = solver.settings
    methods = safe_get_state(settings.solution.methods, "solution methods")
    models = safe_get_state(settings.setup.models, "models")
    boundaries = safe_get_state(settings.setup.boundary_conditions, "boundaries")
    cells = safe_get_state(settings.setup.cell_zone_conditions, "cell zones")
    fluid = cells.get("fluid", {})
    require(set(fluid) == set(FLUID_ZONES), f"Fluid-zone set changed: {sorted(fluid)}")
    for zone, state in fluid.items():
        for phase in ("mixture", "phase-1", "phase-2"):
            require(not state["phase"][phase]["sources"]["enable"], f"Active cell source: {zone}/{phase}")
    require(models["multiphase"]["model"] == "mixture", "Mixture model changed")
    require(models["viscous"]["k_epsilon_model"] == "rng", "RNG k-epsilon changed")
    dpm = models["discrete_phase"]
    require(not dpm["general_settings"]["interaction"]["enabled"], "DPM interaction is active")
    require(not dpm["physical_models"]["erosion_accretion_enabled"], "DPM erosion/accretion is active")
    require(not dpm.get("injections", {}), "Unexpected DPM injections in carrier base")

    require(methods["p_v_coupling"]["flow_scheme"] == "SIMPLE", "SIMPLE readback failed")
    require(methods["spatial_discretization"]["gradient_scheme"] == "green-gauss-node-based", "Gradient scheme drift")
    discretization = methods["spatial_discretization"]["discretization_scheme"]
    expected_discretization = {"pressure": "presto!", "mom": "second-order-upwind", "mp": "quick", "k": "second-order-upwind", "epsilon": "second-order-upwind"}
    require(all(discretization.get(k) == v for k, v in expected_discretization.items()), f"Discretization readback failed: {discretization}")
    pseudo = methods["pseudo_time_method"]["formulation"]
    expected_off = "segregated_solver" if "segregated_solver" in pseudo else "coupled_solver"
    require(pseudo.get(expected_off) == "off", f"Pseudo-time-off readback failed: {pseudo}")

    require(set(boundaries.get("mass_flow_inlet", {})) == set(INLETS), "Inlet zone set changed")
    flow_readback: dict[str, dict[str, float]] = {}
    for name in INLETS:
        mixture = boundaries["mass_flow_inlet"][name]["phase"]["mixture"]
        turbulence = mixture["turbulence"]
        require(math.isclose(float(turbulence["turbulent_intensity"]), 0.0211, rel_tol=0, abs_tol=2e-7), f"Inlet intensity drift: {name}")
        require(math.isclose(float(turbulence["hydraulic_diameter"]), 0.724, rel_tol=0, abs_tol=2e-9), f"Inlet diameter drift: {name}")
        flow_readback[name] = {}
        for phase in ("phase-1", "phase-2"):
            flow_readback[name][phase] = float(boundaries["mass_flow_inlet"][name]["phase"][phase]["momentum"]["mass_flow_rate"]["value"])

    outlet = boundaries.get("pressure_outlet", {}).get("steamoutlet")
    require(outlet is not None, "steamoutlet pressure boundary is missing")
    outlet_turbulence = outlet["phase"]["mixture"]["turbulence"]
    require(math.isclose(float(outlet_turbulence["backflow_turbulent_intensity"]), 0.021525, rel_tol=0, abs_tol=2e-7), "Outlet backflow intensity drift")
    require(math.isclose(float(outlet_turbulence["backflow_hydraulic_diameter"]), 0.724, rel_tol=0, abs_tol=2e-9), "Outlet backflow diameter drift")
    require("bottom" in boundaries["wall"], "Closed lower boundary is missing")

    sums = {
        phase: sum(flow_readback[zone][phase] for zone in INLETS)
        for phase in ("phase-1", "phase-2")
    }
    if exact_flows:
        require(math.isclose(sums["phase-1"], TARGET_VAPOR, rel_tol=0, abs_tol=1e-5), f"Total vapor feed mismatch: {sums}")
        require(math.isclose(sums["phase-2"], TARGET_LIQUID, rel_tol=0, abs_tol=1e-5), f"Total liquid feed mismatch: {sums}")
    return {
        "flow_scheme": methods["p_v_coupling"]["flow_scheme"],
        "pseudo_time_formulation": pseudo,
        "spatial_discretization": discretization,
        "inlet_flows_kg_s_by_zone": flow_readback,
        "summed_phase_flows_kg_s": sums,
        "inlet_turbulence": {name: boundaries["mass_flow_inlet"][name]["phase"]["mixture"]["turbulence"] for name in INLETS},
        "outlet_turbulence": outlet_turbulence,
        "fluid_zones": sorted(fluid),
        "all_cell_sources_off": True,
        "mixture_RNG": True,
        "DPM_interaction_off_and_no_injections": True,
        "closed_bottom": True,
    }


def configure_purnanto_parity(solver: Any) -> dict[str, Any]:
    methods = solver.settings.solution.methods
    methods.p_v_coupling.flow_scheme = "SIMPLE"
    methods.spatial_discretization.gradient_scheme = "green-gauss-node-based"
    methods.spatial_discretization.discretization_scheme.set_state(
        {"pressure": "presto!", "mom": "second-order-upwind", "k": "second-order-upwind", "epsilon": "second-order-upwind", "mp": "quick"}
    )
    methods.pseudo_time_method.set_state({"formulation": {"segregated_solver": "off"}})
    for zone in INLETS:
        turbulence = solver.settings.setup.boundary_conditions.mass_flow_inlet[zone].phase["mixture"].turbulence
        turbulence.turbulent_intensity = 0.0211
        turbulence.hydraulic_diameter = 0.724
    outlet_turbulence = solver.settings.setup.boundary_conditions.pressure_outlet["steamoutlet"].phase["mixture"].turbulence
    outlet_turbulence.backflow_turbulent_intensity = 0.021525
    outlet_turbulence.backflow_hydraulic_diameter = 0.724
    solver.settings.solution.methods.high_order_term_relaxation.enable = False
    return audit(solver, exact_flows=True)


def build_f1(solver: Any) -> dict[str, Any]:
    ensure_new(F1_CHILD)
    load_pair(solver, F1_PARENT)
    before = audit_source_f1(solver)
    changed = configure_purnanto_parity(solver)
    solver.settings.mesh.check()
    case, data = pair(F1_CHILD)
    solver.settings.file.write_case(file_name=str(case))
    solver.settings.file.write_data(file_name=str(data))
    require(case.is_file() and data.is_file(), "F1 parity case/data write failed")
    solver.settings.file.read_case(file_name=str(case))
    solver.settings.file.read_data(file_name=str(data))
    after = audit(solver, exact_flows=True)
    return {"parent_case": str(pair(F1_PARENT)[0]), "parent_data": str(pair(F1_PARENT)[1]),
            "case": str(case), "data": str(data), "controlled_delta": "Purnanto 00a SIMPLE and boundary turbulence scales",
            "source_audit": before, "before_save": changed, "after_reopen": after,
            "case_sha256": sha256(case), "data_sha256": sha256(data), "nominal_speed_m_s": TARGET_SPEED,
            "initialization": "retained fresh Hybrid field from the verified Phase 8 F1 base; no iterations"}


def audit_source_f1(solver: Any) -> dict[str, Any]:
    state = safe_get_state(solver.settings.solution.methods, "source solution methods")
    return {"source_flow_scheme": state["p_v_coupling"]["flow_scheme"],
            "source_pseudo_time": state["pseudo_time_method"],
            "source_discretization": state["spatial_discretization"]["discretization_scheme"]}


def build_f2(solver: Any) -> dict[str, Any]:
    ensure_new(F2_CHILD)
    load_pair(solver, F1_CHILD)
    liquid_zone = solver.settings.setup.boundary_conditions.mass_flow_inlet["liquidinlet"]
    steam_zone = solver.settings.setup.boundary_conditions.mass_flow_inlet["steaminlet"]
    liquid_zone.phase["phase-1"].momentum.mass_flow_rate.value = 0.0
    liquid_zone.phase["phase-2"].momentum.mass_flow_rate.value = TARGET_LIQUID
    steam_zone.phase["phase-1"].momentum.mass_flow_rate.value = TARGET_VAPOR
    steam_zone.phase["phase-2"].momentum.mass_flow_rate.value = 0.0
    before_init = audit(solver, exact_flows=False)
    require(math.isclose(before_init["inlet_flows_kg_s_by_zone"]["liquidinlet"]["phase-2"], TARGET_LIQUID, abs_tol=1e-5), "F2 liquid split command failed")
    require(math.isclose(before_init["inlet_flows_kg_s_by_zone"]["steaminlet"]["phase-1"], TARGET_VAPOR, abs_tol=1e-5), "F2 vapor split command failed")
    solver.settings.solution.initialization.hybrid_initialize()
    solver.settings.mesh.check()
    case, data = pair(F2_CHILD)
    solver.settings.file.write_case(file_name=str(case))
    solver.settings.file.write_data(file_name=str(data))
    require(case.is_file() and data.is_file(), "F2 parity case/data write failed")
    solver.settings.file.read_case(file_name=str(case))
    solver.settings.file.read_data(file_name=str(data))
    after = audit(solver, exact_flows=False)
    require(math.isclose(after["summed_phase_flows_kg_s"]["phase-1"], TARGET_VAPOR, abs_tol=1e-5), "F2 vapor total mismatch after reopen")
    require(math.isclose(after["summed_phase_flows_kg_s"]["phase-2"], TARGET_LIQUID, abs_tol=1e-5), "F2 liquid total mismatch after reopen")
    require(after["inlet_flows_kg_s_by_zone"]["liquidinlet"]["phase-1"] == 0.0 and after["inlet_flows_kg_s_by_zone"]["steaminlet"]["phase-2"] == 0.0, "F2 inlet phase split mismatch")
    return {"parent_case": str(pair(F1_CHILD)[0]), "parent_data": str(pair(F1_CHILD)[1]),
            "case": str(case), "data": str(data), "controlled_delta": "split pure-phase inlet on the Purnanto-parity carrier stack",
            "before_save": before_init, "after_reopen": after,
            "case_sha256": sha256(case), "data_sha256": sha256(data), "nominal_speed_m_s": TARGET_SPEED,
            "initialization": "fresh Hybrid after the split inlet was applied; no iterations"}


def main() -> int:
    require(ROOT.joinpath(".venv").exists(), "Expected PyAnsys repository root")
    require(all(path.is_file() for path in pair(F1_PARENT)), "Verified Phase 8 F1 parent pair is incomplete")
    require(not OUT.exists(), f"Refusing to overwrite receipt: {OUT}")
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                           ui_mode="gui", start_timeout=240, cleanup_on_exit=False, start_transcript=True)
    receipt: dict[str, Any] = {"status": "BUILDING", "fluent_version": str(solver.get_fluent_version()),
                               "student_limit": "one million cells; source mesh is the 60,964-cell Phase 8 partition",
                               "families": {}}
    try:
        receipt["families"]["F1"] = build_f1(solver)
        receipt["families"]["F2"] = build_f2(solver)
        receipt["status"] = "CASE_DATA_VERIFIED"
    except Exception as exc:
        receipt["status"] = "BLOCKED_BUILD_FAILURE"
        receipt["error"] = repr(exc)
        raise
    finally:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(receipt, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, default=str), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

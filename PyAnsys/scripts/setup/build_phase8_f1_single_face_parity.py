#!/usr/bin/env python3
"""Make a separately named, genuinely one-face Purnanto-style F1 child."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state
from build_phase8_purnanto_parity_pilots import AREA, TARGET_LIQUID, TARGET_VAPOR
from run_phase8_parity_carrier import dump, load_pair, pair, require, save_pair, sha256

SOURCE_RECEIPT = ROOT / "output" / "phase8_purnanto_parity_pilots_20260928T110152Z.json"
OUTPUT_ROOT = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\PurnantoParity\F1SingleFace")
EXPECTED_AREA = sum(AREA.values())


def area(solver, zone: str) -> float:
    branch = solver.settings.solution.report_definitions.surface
    name = "p8-single-face-area-check"
    if name not in branch.get_object_names():
        branch.create(name=name)
    report = branch[name]
    report.report_type = "surface-area"
    report.surface_names = [zone]
    report.per_selection = False
    report.create_report_file = False
    report.create_report_plot = False
    result = solver.settings.solution.report_definitions.compute(report_defs=[name])
    return float(result[0][name][0])


def inspect(solver) -> dict:
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
    names = set(inlet.get_object_names())
    require(len(names) == 1, f"Expected one inlet face zone, found {names}")
    zone = names.pop()
    values = {phase: float(inlet[zone].phase[phase].momentum.mass_flow_rate.value())
              for phase in ("phase-1", "phase-2")}
    require(abs(values["phase-1"] - TARGET_VAPOR) < 1e-5 and
            abs(values["phase-2"] - TARGET_LIQUID) < 1e-5,
            f"Merged inlet phase feeds changed: {values}")
    measured_area = area(solver, zone)
    require(abs(measured_area - EXPECTED_AREA) < 1e-6,
            f"Merged inlet area {measured_area} differs from {EXPECTED_AREA}")
    turbulence = safe_get_state(inlet[zone].phase["mixture"].turbulence,
                                "merged inlet turbulence")
    require(abs(float(turbulence["hydraulic_diameter"]) - 0.724) < 1e-8,
            f"Merged inlet hydraulic diameter changed: {turbulence}")
    return {"inlet_zone": zone, "inlet_area_m2": measured_area,
            "phase_flows_kg_s": values, "turbulence": turbulence,
            "flow_scheme": solver.settings.solution.methods.p_v_coupling.flow_scheme(),
            "pseudo_time": safe_get_state(solver.settings.solution.methods.pseudo_time_method.formulation,
                                           "single-face pseudo-time"),
            "spatial_discretization": safe_get_state(
                solver.settings.solution.methods.spatial_discretization.discretization_scheme,
                "single-face discretization")}


def main() -> None:
    receipt = json.loads(SOURCE_RECEIPT.read_text(encoding="utf-8"))
    source = receipt["families"]["F1"]
    source_base = Path(str(source["case"]).removesuffix(".cas.h5"))
    for kind, path in zip(("case", "data"), pair(source_base)):
        require(path.is_file() and sha256(path) == source[f"{kind}_sha256"],
                f"F1 parity source {kind} changed")
    label = f"F1-single-face-parity-26p81-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    child = OUTPUT_ROOT / label
    output = ROOT / "output" / "phase8-single-face" / label / "build.json"
    require(not output.exists() and not any(path.exists() for path in pair(child)),
            "Single-face child collision")
    result = {"status": "BUILDING", "source_receipt": str(SOURCE_RECEIPT),
              "source_case_sha256": source["case_sha256"],
              "source_data_sha256": source["data_sha256"],
              "child_base": str(child), "claim_limit":
              "Separate true one-face SIMPLE setup; two-face matched F1/F2 evidence remains distinct."}
    dump(output, result)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double",
                           processor_count=4, ui_mode="gui", start_timeout=240,
                           cleanup_on_exit=True, start_transcript=True)
    try:
        load_pair(solver, source_base)
        inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
        result["before_merge"] = {
            zone: safe_get_state(inlet[zone], f"source {zone}")
            for zone in ("liquidinlet", "steaminlet")}
        result["before_areas_m2"] = {
            zone: area(solver, zone) for zone in ("liquidinlet", "steaminlet")}
        require(abs(sum(result["before_areas_m2"].values()) - EXPECTED_AREA) < 1e-6,
                "Source inlet areas changed")
        # The command requires matching boundary type and condition. Match the
        # smaller zone to the larger one, then restore the *total* feeds on the
        # surviving face; initialize afresh because the temporary feed is artificial.
        inlet["liquidinlet"].set_state(result["before_merge"]["steaminlet"])
        solver.settings.mesh.modify_zones.merge_zones(
            zone_names=["liquidinlet", "steaminlet"])
        names = set(inlet.get_object_names())
        require(len(names) == 1, f"Merge did not produce one inlet: {names}")
        zone = names.pop()
        inlet[zone].phase["phase-1"].momentum.mass_flow_rate.value = TARGET_VAPOR
        inlet[zone].phase["phase-2"].momentum.mass_flow_rate.value = TARGET_LIQUID
        inlet[zone].phase["mixture"].turbulence.hydraulic_diameter = 0.724
        inlet[zone].phase["mixture"].turbulence.turbulent_intensity = 0.0211
        solver.settings.solution.initialization.hybrid_initialize()
        solver.settings.mesh.check()
        result["configured"] = inspect(solver)
        result["child_pair"] = save_pair(solver, child)
        load_pair(solver, child)
        result["reopened"] = inspect(solver)
        result["status"] = "CASE_DATA_VERIFIED"
    except Exception as exc:
        result["status"] = "BLOCKED"
        result["error"] = repr(exc)
        raise
    finally:
        dump(output, result)
        if result["status"] == "CASE_DATA_VERIFIED":
            solver.exit()
    print(json.dumps({"status": result["status"], "receipt": str(output)}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build a seven-bin Phase 8 DPM child from a qualified F1/F2 carrier."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup"),
                str(ROOT / "scripts" / "inspection")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state
from pyansys_fluent.dependency_workflow import safe_child_names

from build_09cV2_student_velocity_adaptation import (
    DPM_MATERIAL, STEAM_VELOCITY_M_S, object_names, set_leaf_readback,
    set_state_readback,
)
from build_09cV3_mass_flow_from_09cV2 import FINE_MIST_BINS
from run_dpm_particle_tracks import run_dpm_particle_track_check
from run_phase8_parity_carrier import dump, load_pair, pair, require, save_pair, sha256

LIQUID_FEED = 116.93872650
VAPOR_FEED = 80.70292372
REFERENCE_SPEED = 26.81
OUTPUT_ROOT = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\DPM")


def inspect(solver, *, fraction: float, allocated: bool,
            speed: float = REFERENCE_SPEED) -> dict:
    settings = solver.settings.setup
    boundary = safe_get_state(settings.boundary_conditions, "boundaries")
    models = safe_get_state(settings.models, "models")
    dpm = models["discrete_phase"]
    injections = dpm.get("injections", {})
    feeds = {zone: {phase: float(boundary["mass_flow_inlet"][zone]["phase"][phase]["momentum"]["mass_flow_rate"]["value"])
                    for phase in ("phase-1", "phase-2")} for zone in ("liquidinlet", "steaminlet")}
    vapor = sum(p["phase-1"] for p in feeds.values())
    liquid = sum(p["phase-2"] for p in feeds.values())
    scale = speed / REFERENCE_SPEED
    target_liquid = LIQUID_FEED * scale * (1 - fraction) if allocated else LIQUID_FEED * scale
    require(abs(vapor - VAPOR_FEED * scale) < 1e-5, f"Vapor feed drift: {vapor}")
    require(abs(liquid - target_liquid) < 1e-5, f"Liquid feed drift: {liquid}")
    require(len(injections) == 7, f"Expected seven injections, got {list(injections)}")
    flows = {name: float(payload["initial_values"]["mass_flow_rate"]["total_flow_rate"])
             for name, payload in injections.items()}
    require(abs(sum(flows.values()) - LIQUID_FEED * scale * fraction) < 1e-7,
            f"DPM flow drift: {sum(flows.values())}")
    for name, payload in injections.items():
        require(payload["particle_type"] == "inert", f"{name} is not an inert droplet")
        require(payload["material"] == DPM_MATERIAL, f"{name} material changed")
        require(payload["injection_type"]["option"] == "surface", f"{name} type changed")
        require(payload["initial_values"]["location"]["injection_surfaces"] == ["steaminlet"],
                f"{name} release surface changed")
        actual_velocity = float(payload["initial_values"]["velocity"]["x_velocity"])
        expected_velocity = STEAM_VELOCITY_M_S * scale
        require(abs(actual_velocity - expected_velocity) < 1e-6,
                f"{name} release velocity changed: {actual_velocity}")
    interaction = dpm["general_settings"]["interaction"]
    require(bool(interaction["enabled"]) is allocated, "Interaction mode mismatch")
    walls = {name: payload.get("phase", {}).get("mixture", {}).get("discrete_phase", {}).get("bc_type")
             for name, payload in boundary["wall"].items()}
    require(walls["bottom"] == "trap", "Bottom DPM fate changed")
    require(walls["wall"] == "reflect", "Main wall DPM fate changed")
    return {"feeds_kg_s": feeds, "dpm_flows_kg_s": flows, "dpm_total_kg_s": sum(flows.values()),
            "interaction": interaction, "tracking": dpm["tracking"], "injections": injections,
            "wall_fates": walls, "methods": safe_get_state(solver.settings.solution.methods, "methods")}


def ensure_material(solver) -> dict:
    materials = solver.settings.setup.materials
    fluids = safe_get_state(materials.fluid, "fluid materials")
    source = next((name for name in ("water-liquid-at-psep", "water-liquid") if name in fluids), None)
    require(source is not None, f"No recorded liquid material among {list(fluids)}")
    density = float(fluids[source]["density"]["value"])
    inert = materials.inert_particle
    created = False
    if DPM_MATERIAL not in object_names(inert):
        inert.create(name=DPM_MATERIAL)
        created = True
    set_state_readback(inert[DPM_MATERIAL],
                       {"name": DPM_MATERIAL, "chemical_formula": "",
                        "density": {"option": "value", "value": density}},
                       "DPM material")
    return {"source_liquid": source, "density_kg_m3": density, "created": created,
            "readback": safe_get_state(inert[DPM_MATERIAL], "DPM material")}


def configure(solver, *, fraction: float, allocated: bool,
              source_interval: int = 1, speed: float = REFERENCE_SPEED) -> dict:
    setup = solver.settings.setup
    before = safe_get_state(setup.boundary_conditions, "parent boundaries")
    require(abs(sum(float(before["mass_flow_inlet"][z]["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"])
                    for z in ("liquidinlet", "steaminlet")) - LIQUID_FEED * speed / REFERENCE_SPEED) < 1e-5,
            "Parent liquid feed does not match the qualified speed point")
    require(not safe_get_state(setup.models.discrete_phase.injections, "parent injections"),
            "Parent already has DPM injections")
    # In Fluent 2025 R2 the inert-particle material branch is inactive until
    # an injection exists, even while the DPM settings tree is readable.
    for name, *_ in FINE_MIST_BINS:
        setup.models.discrete_phase.injections.create(name=name)
    material = ensure_material(solver)
    if allocated:
        set_leaf_readback(
            setup.boundary_conditions.mass_flow_inlet["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate.value,
            LIQUID_FEED * speed / REFERENCE_SPEED * (1 - fraction), "allocated Eulerian liquid feed")
    dpm = setup.models.discrete_phase
    set_leaf_readback(dpm.general_settings.interaction.enabled, allocated, "continuous-phase interaction")
    if allocated:
        set_leaf_readback(dpm.general_settings.interaction.update_sources_every_iteration,
                          source_interval == 1, "update DPM sources every iteration")
        set_leaf_readback(dpm.general_settings.interaction.iteration_interval, source_interval,
                          "DPM source interval")
    set_leaf_readback(dpm.tracking.max_num_steps, 50000, "maximum DPM steps")
    set_state_readback(dpm.tracking.step_size_controls,
                       {"option": "step-length-factor", "step_length_factor": 5},
                       "DPM step-length control")
    bc = setup.boundary_conditions
    set_leaf_readback(bc.wall["bottom"].phase["mixture"].discrete_phase.bc_type, "trap", "bottom fate")
    set_leaf_readback(bc.wall["wall"].phase["mixture"].discrete_phase.bc_type, "reflect", "main-wall fate")
    for zone in ("liquidinlet", "steaminlet"):
        set_leaf_readback(bc.mass_flow_inlet[zone].phase["mixture"].discrete_phase.bc_type,
                          "escape", f"{zone} fate")
    set_leaf_readback(bc.pressure_outlet["steamoutlet"].phase["mixture"].discrete_phase.bc_type,
                      "escape", "outlet fate")
    injections = dpm.injections
    total = LIQUID_FEED * speed / REFERENCE_SPEED * fraction
    share_sum = sum(float(item[3]) for item in FINE_MIST_BINS)
    for name, _interval, diameter_um, share_pct, _old_flow in FINE_MIST_BINS:
        injection = setup.models.discrete_phase.injections[name]
        set_leaf_readback(injection.particle_type, "inert", f"{name} type")
        injection = setup.models.discrete_phase.injections[name]
        set_leaf_readback(injection.material, DPM_MATERIAL, f"{name} material")
        injection = setup.models.discrete_phase.injections[name]
        set_leaf_readback(injection.injection_type.option, "surface", f"{name} injection type")
        injection = setup.models.discrete_phase.injections[name]
        location = safe_get_state(injection.initial_values.location, f"{name} original location")
        location.update({"injection_surfaces": ["steaminlet"],
                         "randomized_positions_enabled": False, "number_of_streams": 100})
        set_state_readback(injection.initial_values.location, location,
                           f"{name} location")
        injection = setup.models.discrete_phase.injections[name]
        mass_flow = injection.initial_values.mass_flow_rate
        if "scale_by_area" in safe_child_names(mass_flow):
            set_leaf_readback(mass_flow.scale_by_area, False, f"{name} scale by area")
        injection = setup.models.discrete_phase.injections[name]
        set_leaf_readback(injection.initial_values.mass_flow_rate.total_flow_rate,
                          total * share_pct / share_sum, f"{name} parcel weight")
        injection = setup.models.discrete_phase.injections[name]
        set_state_readback(injection.initial_values.velocity,
                           {"use_face_normal_direction": False,
                            "x_velocity": STEAM_VELOCITY_M_S * speed / REFERENCE_SPEED,
                            "y_velocity": 0.0, "z_velocity": 0.0},
                           f"{name} initial velocity")
        injection = setup.models.discrete_phase.injections[name]
        set_state_readback(injection.initial_values.particle_size,
                           {"option": "uniform", "diameter": diameter_um * 1e-6},
                           f"{name} diameter")
        injection = setup.models.discrete_phase.injections[name]
        set_leaf_readback(injection.physical_models.particle_drag.option, "spherical", f"{name} drag")
        set_leaf_readback(injection.physical_models.particle_rotation.enabled, False, f"{name} rotation")
        set_leaf_readback(injection.physical_models.turbulent_dispersion.enabled, False,
                          f"{name} turbulent dispersion")
    return {"material": material, "target_dpm_kg_s": total,
            "bin_share_sum_pct": share_sum, "configured": inspect(solver, fraction=fraction,
                                                                      allocated=allocated, speed=speed)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-manifest", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--family", choices=("F1", "F2"), required=True)
    parser.add_argument("--mode", choices=("diagnostic", "allocated"), required=True)
    parser.add_argument("--fraction", type=float, default=0.05)
    parser.add_argument("--source-interval", type=int, default=1,
                        help="Coupled DPM source update interval in carrier iterations")
    args = parser.parse_args()
    require(0 < args.fraction < 1, "DPM fraction must be between zero and one")
    if args.mode == "diagnostic":
        require(args.fraction == 0.05, "F1/F2 diagnostic parcel basis is fixed at 5%")
    else:
        require(args.family == "F2", "Allocated two-way DPM belongs to F3/F4")
        require(1 <= args.source_interval <= 100, "Source interval must be 1..100")
    parent = json.loads(args.parent_manifest.read_text(encoding="utf-8"))
    assessment = json.loads(args.assessment.read_text(encoding="utf-8"))
    require(parent["status"] == "COMPLETE" and assessment["developed_for_diagnostic_dpm"],
            "Parent carrier has not passed its declared development gate")
    require(parent["family"] == args.family, "Parent family mismatch")
    speed = float(parent["speed_m_s"])
    for kind in ("case", "data"):
        path = Path(parent["checkpoints"][-1][kind])
        require(path.is_file(), f"Parent final {kind} missing")
        require(sha256(path) == parent["checkpoints"][-1][f"{kind}_sha256"],
                f"Parent final {kind} hash changed")
    source_base = Path(parent["paths"]["final"]) / "final"
    interval_label = f"-upd{args.source_interval}" if args.mode == "allocated" and args.source_interval != 1 else ""
    label = (f"{args.family}-{args.mode}-{int(args.fraction*1000):03d}permil-{str(speed).replace('.', 'p')}"
             f"{interval_label}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    child = OUTPUT_ROOT / ("F3" if args.mode == "allocated" else args.family) / label
    require(not any(path.exists() for path in pair(child)), "Refusing to overwrite DPM child")
    receipt_path = ROOT / "output" / "phase8-dpm" / label / "build.json"
    receipt = {"status": "BUILDING", "family": args.family, "mode": args.mode,
               "fraction": args.fraction, "speed_m_s": speed,
               "injection_velocity_rule": "reference 27.118 m/s times nominal-speed/reference-speed ratio",
               "parent_manifest": str(args.parent_manifest),
               "source_interval": args.source_interval,
               "parent_assessment": str(args.assessment), "child_base": str(child),
               "parent_case_sha256": parent["checkpoints"][-1]["case_sha256"]}
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                           ui_mode="gui", start_timeout=240, cleanup_on_exit=True, start_transcript=True)
    try:
        load_pair(solver, source_base)
        receipt["parent_methods"] = safe_get_state(solver.settings.solution.methods, "parent methods")
        receipt["parent_dpm_general"] = safe_get_state(
            solver.settings.setup.models.discrete_phase.general_settings, "parent DPM general")
        receipt["parent_dpm_tracking"] = safe_get_state(
            solver.settings.setup.models.discrete_phase.tracking, "parent DPM tracking")
        receipt["parent_materials"] = {
            "fluid": safe_get_state(solver.settings.setup.materials.fluid, "parent fluid materials")}
        receipt["parent_wall_names"] = object_names(solver.settings.setup.boundary_conditions.wall)
        dump(receipt_path, receipt)
        receipt["configuration"] = configure(solver, fraction=args.fraction,
                                              allocated=args.mode == "allocated",
                                              source_interval=args.source_interval,
                                              speed=speed)
        receipt["child_pair"] = save_pair(solver, child)
        load_pair(solver, child)
        receipt["reopened"] = inspect(solver, fraction=args.fraction,
                                       allocated=args.mode == "allocated", speed=speed)
        if args.mode == "allocated":
            interaction = receipt["reopened"]["interaction"]
            require(interaction["iteration_interval"] == args.source_interval and
                    interaction["update_sources_every_iteration"] is (args.source_interval == 1),
                    "Coupled DPM source cadence changed after reopen")
        require(receipt["reopened"]["methods"] == receipt["parent_methods"],
                "DPM build changed carrier numerics")
        receipt["status"] = "CASE_DATA_VERIFIED"
        dump(receipt_path, receipt)
        if args.mode == "diagnostic":
            try:
                receipt["particle_tracks"] = run_dpm_particle_track_check(
                    solver, run_label=label, order="diameter-ascending", keep_going=True,
                    zone_summaries=True)
                receipt["tracking_status"] = "COMPLETE" if all(
                    item.get("status") == "ok" for item in receipt["particle_tracks"]["results"]
                ) else "PARTIAL"
            except Exception as exc:
                receipt["tracking_status"] = "BLOCKED"
                receipt["tracking_error"] = repr(exc)
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(receipt_path, receipt)
        if receipt["status"] == "CASE_DATA_VERIFIED":
            solver.exit()
    print(json.dumps({"status": receipt["status"], "receipt": str(receipt_path)}, indent=2))


if __name__ == "__main__":
    main()

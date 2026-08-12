#!/usr/bin/env python3
"""Build the Student-session 09cV2 velocity-inlet adaptation.

The loaded Student case is intentionally not treated as an exact historical
09c parent: it has velocity inlets, two anthracite placeholders, no verified
``water-liquid-at-psep`` source material, and DPM interaction disabled.

This script makes the documented 5% screening derivative as a case-only
artifact. It does not initialize, iterate, read data, or write a ``.dat.h5``.
Every mutation is followed by a live readback, and the saved case is reloaded
and audited before the script succeeds.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state, write_json_snapshot  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import safe_allowed_values, safe_child_names  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


DEFAULT_SERVER_ID = "student"
DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\base files"
DEFAULT_OUTPUT_CASE = "09cV2-fDPM-05pct-velocity-inlet-adaptation.cas.h5"
DEFAULT_BACKUP_CASE = "09cV2-student-prebuild-source-20260804.cas.h5"
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "output" / "09cV2_student_velocity_inlet_adaptation_20260804.json"

LIQUID_REFERENCE_KG_S = 116.920
VAPOR_REFERENCE_KG_S = 80.690
DPM_FRACTION = 0.05
DPM_TOTAL_KG_S = LIQUID_REFERENCE_KG_S * DPM_FRACTION
EULERIAN_LIQUID_REFERENCE_KG_S = LIQUID_REFERENCE_KG_S - DPM_TOTAL_KG_S

SOURCE_LIQUID_VELOCITY_M_S = 27.118
ADAPTED_LIQUID_VELOCITY_M_S = SOURCE_LIQUID_VELOCITY_M_S * (1.0 - DPM_FRACTION)
STEAM_VELOCITY_M_S = 27.118

FILM_MATERIAL = "water-liquid-at-psep"
DPM_MATERIAL = "water-liquid-at-psep-dpm"

# These are the documented rounded 09c parent weights.  Normalizing them to
# the exact 5% total makes the allocation close exactly while preserving the
# documented relative six-bin basis.
HISTORICAL_BINS = (
    ("5um", 5.63, 0.19),
    ("28um", 28.14, 0.78),
    ("56um", 56.27, 0.97),
    ("112um", 112.54, 1.95),
    ("168um", 168.81, 1.95),
    ("348um", 348.88, 23.38),
)
PARENT_WEIGHT_TOTAL_KG_S = sum(weight for _, _, weight in HISTORICAL_BINS)
INJECTIONS = tuple(
    (f"{FILM_MATERIAL}-{label}", diameter_um, DPM_TOTAL_KG_S * weight / PARENT_WEIGHT_TOTAL_KG_S)
    for label, diameter_um, weight in HISTORICAL_BINS
)
TARGET_INJECTION_NAMES = {name for name, _, _ in INJECTIONS}
PLACEHOLDER_NAMES = {"injection-0", "injection-1"}


class UnknownSetup(RuntimeError):
    """A required live Fluent fact or readback is unknown."""


def fail(message: str) -> None:
    raise UnknownSetup(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def remote_case_path(value: str) -> str:
    """Resolve relative case names into the Student host's active case folder."""
    path = PureWindowsPath(value)
    if path.is_absolute():
        return str(path)
    return str(PureWindowsPath(DEFAULT_REMOTE_DIR) / path)


def as_float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        fail(f"{label} is not numeric: {value!r}")
        raise exc


def close(actual: Any, expected: float, label: str, *, tolerance: float = 1.0e-9) -> float:
    actual_float = as_float(actual, label)
    require(abs(actual_float - expected) <= tolerance, f"{label} readback mismatch: {actual_float} != {expected}")
    return actual_float


def object_names(branch: Any) -> list[str]:
    try:
        return sorted(str(name) for name in branch.get_object_names())
    except Exception as exc:
        fail(f"Could not read object names: {type(exc).__name__}: {exc}")
        return []


def state(obj: Any, label: str) -> Any:
    value = safe_get_state(obj, label)
    if isinstance(value, Mapping) and "_capture_error" in value:
        fail(str(value["_capture_error"]))
    return value


def state_value(payload: Any, *keys: str) -> Any:
    current = payload
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def set_state_readback(obj: Any, value: Any, label: str) -> Any:
    try:
        obj.set_state(value)
        return obj.get_state()
    except Exception as exc:
        fail(f"Could not set/read back {label}: {type(exc).__name__}: {exc}")
        return None


def set_leaf_readback(obj: Any, value: Any, label: str) -> Any:
    return set_state_readback(obj, value, label)


def read_source_audit(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    bc = setup.boundary_conditions

    velocity_inlets = object_names(bc.velocity_inlet)
    require(set(velocity_inlets) == {"liquidinlet", "steaminlet"}, f"Unexpected velocity inlets: {velocity_inlets}")
    require(object_names(bc.mass_flow_inlet) == [], "Mass-flow inlet branch is unexpectedly active")

    liquid_state = state(bc.velocity_inlet["liquidinlet"], "source liquidinlet")
    steam_state = state(bc.velocity_inlet["steaminlet"], "source steaminlet")
    liquid_phase = state_value(liquid_state, "phase", "water-liquid")
    steam_phase = state_value(steam_state, "phase", "water-vapor")
    require(isinstance(liquid_phase, Mapping), "liquidinlet water-liquid phase is unavailable")
    require(isinstance(steam_phase, Mapping), "steaminlet water-vapor phase is unavailable")
    require(
        state_value(liquid_phase, "multiphase", "volume_fraction", "value") == 1,
        "liquidinlet is not pure water-liquid",
    )
    source_liquid_velocity = close(
        state_value(liquid_phase, "momentum", "velocity_magnitude", "value"),
        SOURCE_LIQUID_VELOCITY_M_S,
        "source liquidinlet water-liquid velocity",
    )
    source_steam_velocity = close(
        state_value(steam_phase, "momentum", "velocity_magnitude", "value"),
        STEAM_VELOCITY_M_S,
        "source steaminlet water-vapor velocity",
    )

    model_state = state(setup.models, "source models")
    require(state_value(model_state, "multiphase", "model") == "mixture", "Loaded case is not Mixture")
    require(state_value(model_state, "energy", "enabled") is False, "Energy is not off in the loaded case")
    viscous = state_value(model_state, "viscous")
    require(state_value(viscous, "model") == "k-epsilon", "Loaded case is not k-epsilon")
    require(state_value(viscous, "k_epsilon_model") == "rng", "Loaded case is not RNG k-epsilon")

    dpm = setup.models.discrete_phase
    interaction = dpm.general_settings.interaction
    interaction_state = state(interaction, "source DPM interaction")
    require(state_value(interaction_state, "enabled") is False, "Loaded DPM interaction is already enabled")
    injection_state = state(dpm.injections, "source injections")
    require(isinstance(injection_state, Mapping), "Loaded DPM injections are unavailable")
    require(set(injection_state) == PLACEHOLDER_NAMES, f"Unexpected source injections: {sorted(injection_state)}")
    for name, payload in injection_state.items():
        require(payload.get("material") == "anthracite", f"{name} is not the expected anthracite placeholder")
        close(
            state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"),
            1.0e-20,
            f"{name} placeholder flow",
            tolerance=1.0e-30,
        )
        require(
            state_value(payload, "initial_values", "location", "injection_surfaces") == ["steaminlet"],
            f"{name} is not on steaminlet",
        )

    materials = state(setup.materials.fluid, "source fluid materials")
    require(isinstance(materials, Mapping), "Fluid material state is unavailable")
    require("water-liquid" in materials, "water-liquid is not available for the fallback copy")
    require(FILM_MATERIAL not in materials, f"Unexpected existing {FILM_MATERIAL} material in source case")
    inert_materials = state(setup.materials.inert_particle, "source inert materials")
    require(isinstance(inert_materials, Mapping), "Inert-particle material state is unavailable")
    require(DPM_MATERIAL not in inert_materials, f"Unexpected existing {DPM_MATERIAL} material in source case")

    return {
        "velocity_inlets": velocity_inlets,
        "mass_flow_inlets": [],
        "source_liquid_velocity_m_s": source_liquid_velocity,
        "source_steam_velocity_m_s": source_steam_velocity,
        "model_state": model_state,
        "dpm_interaction": interaction_state,
        "source_injections": injection_state,
        "source_fluid_materials": materials,
        "source_inert_materials": inert_materials,
    }


def prepare_materials(solver: Any) -> dict[str, Any]:
    materials = solver.settings.setup.materials
    fluid = materials.fluid
    fluid_names = set(object_names(fluid))
    require("water-liquid" in fluid_names, "water-liquid is unavailable for material fallback")

    created_film_material = False
    if FILM_MATERIAL not in fluid_names:
        try:
            fluid.make_a_copy(from_="water-liquid", to=FILM_MATERIAL)
            created_film_material = True
        except Exception as exc:
            fail(f"Could not create fallback fluid material {FILM_MATERIAL}: {type(exc).__name__}: {exc}")

    require(FILM_MATERIAL in set(object_names(fluid)), f"Fallback film material {FILM_MATERIAL} was not created")
    film_state = state(fluid[FILM_MATERIAL], f"{FILM_MATERIAL} fallback material")
    source_state = state(fluid["water-liquid"], "water-liquid source material")
    film_density = close(
        state_value(film_state, "density", "value"),
        as_float(state_value(source_state, "density", "value"), "water-liquid density"),
        f"{FILM_MATERIAL} density",
    )
    film_viscosity = as_float(state_value(film_state, "viscosity", "value"), f"{FILM_MATERIAL} viscosity")

    inert = materials.inert_particle
    inert_names = set(object_names(inert))
    created_dpm_material = False
    if DPM_MATERIAL not in inert_names:
        try:
            inert.create(name=DPM_MATERIAL)
            created_dpm_material = True
        except Exception as exc:
            fail(f"Could not create DPM material {DPM_MATERIAL}: {type(exc).__name__}: {exc}")
    require(DPM_MATERIAL in set(object_names(inert)), f"DPM material {DPM_MATERIAL} is unavailable")
    dpm_state = set_state_readback(
        inert[DPM_MATERIAL],
        {
            "name": DPM_MATERIAL,
            "chemical_formula": "",
            "density": {"option": "value", "value": film_density},
        },
        f"{DPM_MATERIAL} state",
    )
    close(
        state_value(dpm_state, "density", "value"),
        film_density,
        f"{DPM_MATERIAL} density",
    )

    return {
        "created_film_material": created_film_material,
        "created_dpm_material": created_dpm_material,
        "film_material": film_state,
        "film_density_kg_m3": film_density,
        "film_viscosity_pa_s": film_viscosity,
        "dpm_material": dpm_state,
        "material_basis": (
            "Fallback: water-liquid-at-psep was created as a copy of the live water-liquid material; "
            "water-liquid-at-psep-dpm uses the copied density. This is not a provenance-verified historical EWF material pair."
        ),
    }


def apply_velocity_partition(solver: Any) -> dict[str, Any]:
    inlet = solver.settings.setup.boundary_conditions.velocity_inlet["liquidinlet"]
    phase = inlet.phase["water-liquid"]
    velocity = phase.momentum.velocity_magnitude
    readback = set_state_readback(
        velocity,
        {"option": "value", "value": ADAPTED_LIQUID_VELOCITY_M_S},
        "liquidinlet water-liquid velocity",
    )
    close(
        state_value(readback, "value"),
        ADAPTED_LIQUID_VELOCITY_M_S,
        "adapted liquidinlet water-liquid velocity",
    )

    steam_state = state(
        solver.settings.setup.boundary_conditions.velocity_inlet["steaminlet"],
        "adapted steaminlet",
    )
    close(
        state_value(steam_state, "phase", "water-vapor", "momentum", "velocity_magnitude", "value"),
        STEAM_VELOCITY_M_S,
        "preserved steaminlet water-vapor velocity",
    )
    return {
        "source_liquid_velocity_m_s": SOURCE_LIQUID_VELOCITY_M_S,
        "adapted_liquid_velocity_m_s": ADAPTED_LIQUID_VELOCITY_M_S,
        "preserved_steam_velocity_m_s": STEAM_VELOCITY_M_S,
        "partition_basis": "velocity-inlet scaling assumption; mass-flow report branch is inactive",
        "target_eulerian_liquid_reference_kg_s": EULERIAN_LIQUID_REFERENCE_KG_S,
    }


def apply_global_dpm_state(solver: Any) -> dict[str, Any]:
    dpm = solver.settings.setup.models.discrete_phase
    interaction = dpm.general_settings.interaction

    set_leaf_readback(interaction.enabled, True, "DPM interaction enabled")
    interaction = solver.settings.setup.models.discrete_phase.general_settings.interaction
    set_leaf_readback(
        interaction.update_sources_every_iteration,
        True,
        "DPM update sources every flow iteration",
    )
    set_leaf_readback(interaction.iteration_interval, 1, "DPM iteration interval")

    tracking = solver.settings.setup.models.discrete_phase.tracking
    set_leaf_readback(tracking.max_num_steps, 50000, "DPM maximum number of steps")
    set_state_readback(
        tracking.step_size_controls,
        {"option": "step-length-factor", "step_length_factor": 5},
        "DPM step-size controls",
    )

    interaction = solver.settings.setup.models.discrete_phase.general_settings.interaction
    return {
        "interaction": state(interaction, "DPM interaction after") ,
        "max_num_steps": state(tracking.max_num_steps, "DPM max steps after"),
        "step_size_controls": state(tracking.step_size_controls, "DPM step controls after"),
    }


def apply_wall_fates(solver: Any) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions

    def set_wall(name: str, expected: str) -> Any:
        leaf = bc.wall[name].phase["mixture"].discrete_phase.bc_type
        allowed = safe_allowed_values(leaf)
        require(not allowed or expected in allowed, f"{name} DPM wall fate {expected!r} is not allowed: {allowed}")
        set_leaf_readback(leaf, expected, f"{name} DPM wall fate")
        return state(leaf, f"{name} DPM wall fate after")

    bottom = set_wall("bottom", "trap")
    wall_fluid = set_wall("wall-fluid", "reflect")
    inlet_liquid = state(bc.velocity_inlet["liquidinlet"].phase["mixture"].discrete_phase.bc_type, "liquidinlet DPM fate")
    inlet_steam = state(bc.velocity_inlet["steaminlet"].phase["mixture"].discrete_phase.bc_type, "steaminlet DPM fate")
    outlet = state(bc.pressure_outlet["steamoutlet"].phase["mixture"].discrete_phase.bc_type, "steamoutlet DPM fate")
    require(inlet_liquid == "escape", f"liquidinlet DPM fate is not escape: {inlet_liquid!r}")
    require(inlet_steam == "escape", f"steaminlet DPM fate is not escape: {inlet_steam!r}")
    require(outlet == "escape", f"steamoutlet DPM fate is not escape: {outlet!r}")
    return {
        "liquidinlet": inlet_liquid,
        "steaminlet": inlet_steam,
        "steamoutlet": outlet,
        "bottom": bottom,
        "wall-fluid": wall_fluid,
    }


def set_location(injection: Any, name: str) -> dict[str, Any]:
    location = injection.initial_values.location
    existing = location.get_state()
    desired = dict(existing) if isinstance(existing, Mapping) else {}
    desired["injection_surfaces"] = ["steaminlet"]
    desired["randomized_positions_enabled"] = False
    desired["number_of_streams"] = 100
    try:
        readback = location.set_state(desired)
        readback = location.get_state()
        strategy = "location.set_state"
    except Exception:
        surfaces = location.injection_surfaces
        allowed = safe_allowed_values(surfaces)
        require("steaminlet" in allowed, f"steaminlet is not an allowed surface for {name}: {allowed}")
        surfaces.set_state(["steaminlet"])
        location.randomized_positions_enabled.set_state(False)
        location.number_of_streams.set_state(100)
        readback = location.get_state()
        strategy = "location.injection_surfaces.set_state"
    require(
        state_value(readback, "injection_surfaces") == ["steaminlet"],
        f"{name} surface readback mismatch: {readback!r}",
    )
    require(
        state_value(readback, "randomized_positions_enabled") is False,
        f"{name} randomized-position readback mismatch: {readback!r}",
    )
    return {"strategy": strategy, "readback": readback}


def configure_injection(solver: Any, name: str, diameter_um: float, flow_kg_s: float) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    injection = branch[name]

    set_leaf_readback(injection.particle_type, "inert", f"{name} particle type")
    injection = branch[name]
    set_leaf_readback(injection.material, DPM_MATERIAL, f"{name} material")
    injection = branch[name]
    set_leaf_readback(injection.injection_type.option, "surface", f"{name} injection type")
    injection = branch[name]
    location = set_location(injection, name)

    injection = branch[name]
    mass_flow = injection.initial_values.mass_flow_rate
    if "scale_by_area" in safe_child_names(mass_flow):
        set_leaf_readback(mass_flow.scale_by_area, False, f"{name} scale by area")
    set_leaf_readback(mass_flow.total_flow_rate, flow_kg_s, f"{name} total flow rate")

    injection = branch[name]
    set_state_readback(
        injection.initial_values.velocity,
        {
            "use_face_normal_direction": False,
            "x_velocity": STEAM_VELOCITY_M_S,
            "y_velocity": 0.0,
            "z_velocity": 0.0,
        },
        f"{name} velocity",
    )
    set_state_readback(
        injection.initial_values.particle_size,
        {"option": "uniform", "diameter": diameter_um * 1.0e-6},
        f"{name} particle size",
    )

    injection = branch[name]
    set_leaf_readback(injection.physical_models.particle_drag.option, "spherical", f"{name} drag law")
    set_leaf_readback(injection.physical_models.particle_rotation.enabled, False, f"{name} particle rotation")
    dispersion = injection.physical_models.turbulent_dispersion
    set_leaf_readback(dispersion.enabled, False, f"{name} turbulent dispersion")

    final = state(branch[name], f"{name} final injection")
    require(final.get("particle_type") == "inert", f"{name} final particle type mismatch: {final!r}")
    require(final.get("material") == DPM_MATERIAL, f"{name} final material mismatch: {final!r}")
    require(state_value(final, "injection_type", "option") == "surface", f"{name} final injection type mismatch")
    require(state_value(final, "initial_values", "location", "injection_surfaces") == ["steaminlet"], f"{name} final surface mismatch")
    close(state_value(final, "initial_values", "mass_flow_rate", "total_flow_rate"), flow_kg_s, f"{name} final flow")
    close(state_value(final, "initial_values", "particle_size", "diameter"), diameter_um * 1.0e-6, f"{name} final diameter", tolerance=1.0e-14)
    require(state_value(final, "physical_models", "turbulent_dispersion", "enabled") is False, f"{name} stochastic dispersion remains enabled")
    require(state_value(final, "physical_models", "particle_rotation", "enabled") is False, f"{name} particle rotation remains enabled")
    require(state_value(final, "physical_models", "particle_drag", "option") == "spherical", f"{name} drag law mismatch")

    return {
        "name": name,
        "diameter_um": diameter_um,
        "flow_kg_s": flow_kg_s,
        "location": location,
        "readback": final,
    }


def create_injections(solver: Any) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    existing = set(object_names(branch))
    require(not (existing & TARGET_INJECTION_NAMES), f"Target injections already exist: {sorted(existing & TARGET_INJECTION_NAMES)}")

    built: dict[str, Any] = {}
    for name, diameter_um, flow_kg_s in INJECTIONS:
        branch.create(name=name)
        branch = solver.settings.setup.models.discrete_phase.injections
        require(name in set(object_names(branch)), f"Injection creation readback failed: {name}")
        built[name] = configure_injection(solver, name, diameter_um, flow_kg_s)

    final_names = set(object_names(solver.settings.setup.models.discrete_phase.injections))
    require(TARGET_INJECTION_NAMES <= final_names, "Not all target injections are present after configuration")
    total = sum(as_float(item["flow_kg_s"], f"{name} flow") for name, item in built.items())
    close(total, DPM_TOTAL_KG_S, "configured DPM total", tolerance=1.0e-12)
    return {"injections": built, "configured_total_kg_s": total}


def remove_placeholders(solver: Any) -> list[str]:
    branch = solver.settings.setup.models.discrete_phase.injections
    for name in sorted(PLACEHOLDER_NAMES):
        require(name in set(object_names(branch)), f"Expected placeholder is missing before removal: {name}")
        try:
            branch.__delitem__(name)
        except Exception:
            branch.delete(name_list=[name])
        branch = solver.settings.setup.models.discrete_phase.injections
    remaining = object_names(branch)
    require(set(remaining) == TARGET_INJECTION_NAMES, f"Final injection list is not the six target bins: {remaining}")
    return remaining


def final_audit(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    models = state(setup.models, "final models")
    require(state_value(models, "multiphase", "model") == "mixture", "Final case is not Mixture")
    require(state_value(models, "energy", "enabled") is False, "Final case unexpectedly enabled Energy")

    liquid_state = state(setup.boundary_conditions.velocity_inlet["liquidinlet"], "final liquidinlet")
    steam_state = state(setup.boundary_conditions.velocity_inlet["steaminlet"], "final steaminlet")
    liquid_velocity = close(
        state_value(liquid_state, "phase", "water-liquid", "momentum", "velocity_magnitude", "value"),
        ADAPTED_LIQUID_VELOCITY_M_S,
        "final liquid velocity",
    )
    steam_velocity = close(
        state_value(steam_state, "phase", "water-vapor", "momentum", "velocity_magnitude", "value"),
        STEAM_VELOCITY_M_S,
        "final steam velocity",
    )

    interaction = setup.models.discrete_phase.general_settings.interaction
    interaction_state = state(interaction, "final DPM interaction")
    require(state_value(interaction_state, "enabled") is True, f"Final DPM interaction is not enabled: {interaction_state!r}")
    update_sources = state(interaction.update_sources_every_iteration, "final DPM source update")
    iteration_interval = state(interaction.iteration_interval, "final DPM interval")
    require(update_sources is True, f"Final DPM source-update setting is not true: {update_sources!r}")
    close(iteration_interval, 1, "final DPM iteration interval", tolerance=0.0)

    injections = state(setup.models.discrete_phase.injections, "final injections")
    require(isinstance(injections, Mapping), "Final DPM injection state is unavailable")
    require(set(injections) == TARGET_INJECTION_NAMES, f"Final DPM injection names mismatch: {sorted(injections)}")
    flows = {
        name: as_float(state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"), f"{name} flow")
        for name, payload in injections.items()
    }
    close(sum(flows.values()), DPM_TOTAL_KG_S, "final DPM total", tolerance=1.0e-12)

    walls = apply_wall_fates(solver)
    materials = state(setup.materials.inert_particle, "final inert materials")
    require(DPM_MATERIAL in materials, f"Final DPM material is absent: {sorted(materials)}")
    film_materials = state(setup.materials.fluid, "final fluid materials")
    require(FILM_MATERIAL in film_materials, f"Final fallback film material is absent: {sorted(film_materials)}")

    return {
        "models": models,
        "liquid_velocity_m_s": liquid_velocity,
        "steam_velocity_m_s": steam_velocity,
        "dpm_interaction": interaction_state,
        "dpm_update_sources_every_iteration": update_sources,
        "dpm_iteration_interval": iteration_interval,
        "injections": injections,
        "dpm_flows_kg_s": flows,
        "dpm_total_kg_s": sum(flows.values()),
        "wall_fates": walls,
        "fluid_material_names": sorted(film_materials),
        "inert_material_names": sorted(materials),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", default=DEFAULT_SERVER_ID)
    parser.add_argument("--output-case", default=DEFAULT_OUTPUT_CASE)
    parser.add_argument("--backup-case", default=DEFAULT_BACKUP_CASE)
    parser.add_argument("--summary-json", default=str(DEFAULT_SUMMARY_JSON))
    args = parser.parse_args()
    require(str(args.server_id).strip().lower() == DEFAULT_SERVER_ID, "This adaptation is restricted to the student endpoint")

    output_case = remote_case_path(args.output_case)
    backup_case = remote_case_path(args.backup_case)

    solver = connect(server_id=args.server_id)
    require(not remote_file_exists(solver, output_case), f"Refusing to overwrite existing output case: {output_case}")
    require(not remote_file_exists(solver, backup_case), f"Refusing to overwrite existing backup case: {backup_case}")

    summary: dict[str, Any] = {
        "setup_id": "09cV2",
        "artifact_role": "velocity-inlet adaptation of 09cV2 historical 5% allocation point",
        "case_identity_status_before_build": "unavailable",
        "source_case_filename_before_build": None,
        "output_case": output_case,
        "backup_case": backup_case,
        "fluent_version": solver.get_fluent_version(),
        "dpm_fraction": DPM_FRACTION,
        "liquid_reference_kg_s": LIQUID_REFERENCE_KG_S,
        "vapor_reference_kg_s": VAPOR_REFERENCE_KG_S,
        "dpm_total_target_kg_s": DPM_TOTAL_KG_S,
        "eulerian_liquid_reference_target_kg_s": EULERIAN_LIQUID_REFERENCE_KG_S,
        "historical_bin_basis": [
            {"name": name, "diameter_um": diameter_um, "parent_weight_kg_s": weight}
            for name, diameter_um, weight in HISTORICAL_BINS
        ],
        "notes": [
            "The active source case was velocity-inlet based, not the documented mass-flow 09c parent.",
            "The liquid allocation is represented by scaling liquidinlet water-liquid velocity from 27.118 to 25.7621 m/s; exact mass-flow closure was unavailable because the live flux-report branch is inactive.",
            "water-liquid-at-psep and water-liquid-at-psep-dpm are fallback copies based on the live water-liquid density, not provenance-verified historical EWF materials.",
            "Case-only build: no initialization, iterations, data read, or .dat.h5 write.",
            "The resulting artifact must be labelled diagnostic and velocity-inlet adaptation, not exact historical 09cV2 recreation.",
        ],
    }

    backup_written = False
    try:
        summary["source_readback"] = read_source_audit(solver)
        write_case_only(solver, backup_case, "write pre-build recovery case")
        require(remote_file_exists(solver, backup_case), "Pre-build recovery case was not visible after write")
        backup_written = True

        summary["partition"] = apply_velocity_partition(solver)
        summary["materials"] = prepare_materials(solver)
        summary["dpm_global"] = apply_global_dpm_state(solver)
        summary["wall_fates_before_injection_cleanup"] = apply_wall_fates(solver)
        summary["injection_build"] = create_injections(solver)
        summary["removed_placeholders"] = remove_placeholders(solver)
        summary["pre_save_audit"] = final_audit(solver)

        write_case_only(solver, output_case, "write 09cV2 Student velocity adaptation")
        require(remote_file_exists(solver, output_case), "Output case was not visible after write")

        load_case_only(solver, output_case, label="Reload saved 09cV2 Student velocity adaptation")
        summary["post_save_audit"] = final_audit(solver)
        summary["case_identity_status_after_build"] = "verified by explicit output-case reload"
        summary["status"] = "complete"
    except Exception as exc:
        summary["status"] = "failed"
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        if backup_written:
            try:
                load_case_only(solver, backup_case, label="Restore pre-build case after failed mutation")
                summary["restored_prebuild_case"] = True
            except Exception as restore_exc:
                summary["restored_prebuild_case"] = False
                summary["restore_failure"] = f"{type(restore_exc).__name__}: {restore_exc}"
        output = Path(args.summary_json).expanduser().resolve()
        write_json_snapshot(str(output), summary)
        raise

    output = Path(args.summary_json).expanduser().resolve()
    write_json_snapshot(str(output), summary)
    print(f"output_case: {output_case}")
    print(f"backup_case: {backup_case}")
    print(f"summary_json: {output}")
    print("09cV2 Student velocity-inlet adaptation case-only build complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UnknownSetup as exc:
        print(f"UNKNOWN_SETUP_STOP: {exc}", file=sys.stderr)
        raise SystemExit(2)

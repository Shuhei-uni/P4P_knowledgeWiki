#!/usr/bin/env python3
"""Build the mass-flow 09cV3 fine-mist child from the server-1 09cV2 case.

The source case is the explicitly named mass-flow parent
``09cV2-fDPM-05pct-10678.cas.h5``.  This builder is intentionally separate
from the Student velocity-inlet adaptation builder: the two cases have
different inlet topologies and wall-zone names.

Only the active DPM injection population is changed.  The six legacy bins are
removed from the copied child and replaced with the documented seven-bin
5--100 um fine-mist prior.  Carrier boundaries, phase flows, materials,
global DPM controls, wall fates, and inherited injection properties are
read back before and after the change.

This is a setup-only workflow.  It writes ``.cas.h5`` files only; it does not
initialize, iterate, read data, or write ``.dat.h5`` files.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    safe_get_state,
    write_json_snapshot,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import safe_allowed_values, safe_child_names  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


DEFAULT_SERVER_ID = "1"
DEFAULT_REMOTE_DIR = r"C:\Users\syok443\P4P simulation"
DEFAULT_SOURCE_CASE = "09cV2-fDPM-05pct-10678.cas.h5"
DEFAULT_OUTPUT_CASE = "09cV3-fDPM-05pct-finemist-5to100um.cas.h5"
DEFAULT_BACKUP_CASE = "09cV3-server1-prebuild-from-09cV2-20260804.cas.h5"
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "output" / "09cV3_mass_flow_from_09cV2_20260804.json"
DEFAULT_VERIFICATION_JSON = PROJECT_ROOT / "output" / "09cV3_mass_flow_verification_20260804.json"

LIQUID_REFERENCE_KG_S = 116.920
EULERIAN_LIQUID_KG_S = 111.074
DPM_TOTAL_KG_S = 5.846
VAPOR_KG_S = 80.690
INHERITED_DPM_MATERIAL = "water-liquid-at-psep-dpm"
INHERITED_FILM_MATERIAL = "water-liquid-at-psep"
VAPOR_MATERIAL = "water-vapor-at-psep"

LEGACY_INJECTION_NAMES = (
    "water-liquid-at-psep-5um",
    "water-liquid-at-psep-28um",
    "water-liquid-at-psep-56um",
    "water-liquid-at-psep-112um",
    "water-liquid-at-psep-168um",
    "water-liquid-at-psep-348um",
)
LEGACY_INJECTION_KEYS = {name.casefold() for name in LEGACY_INJECTION_NAMES}

# These are the exact setup inputs from the 09cV3 definition.  The PSD is an
# assumed engineering prior, not measured separator-inlet data.
FINE_MIST_BINS = (
    ("09cV3-finemist-07um", "5-10", 7.07, 6.998, 0.409128),
    ("09cV3-finemist-14um", "10-20", 14.14, 19.931, 1.165149),
    ("09cV3-finemist-24um", "20-30", 24.49, 21.680, 1.267410),
    ("09cV3-finemist-35um", "30-40", 34.64, 18.688, 1.092501),
    ("09cV3-finemist-49um", "40-60", 48.99, 22.738, 1.329262),
    ("09cV3-finemist-69um", "60-80", 69.28, 8.016, 0.468606),
    ("09cV3-finemist-89um", "80-100", 89.44, 1.949, 0.113944),
)
TARGET_INJECTION_NAMES = {item[0] for item in FINE_MIST_BINS}
TARGET_INJECTION_KEYS = {name.casefold() for name in TARGET_INJECTION_NAMES}
EXPECTED_FINE_MIST_FLOW_KG_S = sum(item[4] for item in FINE_MIST_BINS)


class UnknownSetup(RuntimeError):
    """A required live Fluent fact or readback is unknown."""


def fail(message: str) -> None:
    raise UnknownSetup(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def remote_case_path(value: str) -> str:
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


def close(actual: Any, expected: float, label: str, *, tolerance: float = 1.0e-10) -> float:
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


def active_state(obj: Any) -> bool | None:
    try:
        return bool(obj.is_active())
    except Exception:
        return None


def casefolded_object_map(payload: Mapping[str, Any]) -> dict[str, tuple[str, Any]]:
    return {str(name).casefold(): (str(name), value) for name, value in payload.items()}


def compare_physical_model_subset(actual: Any, expected: Any, label: str) -> None:
    checks = (
        (("particle_drag", "option"),),
        (("particle_rotation", "enabled"),),
        (("turbulent_dispersion", "enabled"),),
        (("rough_wall_treatment_enabled",),),
        (("custom_laws", "enabled"),),
    )
    for (path,) in checks:
        expected_value = state_value(expected, *path)
        if expected_value is None:
            continue
        actual_value = state_value(actual, *path)
        require(actual_value == expected_value, f"{label} {'.'.join(path)} changed: {actual_value!r} != {expected_value!r}")


def boundary_fates(solver: Any) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    fates = {
        "liquidinlet": state(
            bc.mass_flow_inlet["liquidinlet"].phase["mixture"].discrete_phase.bc_type,
            "liquidinlet DPM fate",
        ),
        "steaminlet": state(
            bc.mass_flow_inlet["steaminlet"].phase["mixture"].discrete_phase.bc_type,
            "steaminlet DPM fate",
        ),
        "steamoutlet": state(
            bc.pressure_outlet["steamoutlet"].phase["mixture"].discrete_phase.bc_type,
            "steamoutlet DPM fate",
        ),
        "bottom": state(
            bc.wall["bottom"].phase["mixture"].discrete_phase.bc_type,
            "bottom DPM fate",
        ),
        "wall": state(
            bc.wall["wall"].phase["mixture"].discrete_phase.bc_type,
            "wall DPM fate",
        ),
    }
    require(
        fates == {
            "liquidinlet": "escape",
            "steaminlet": "escape",
            "steamoutlet": "escape",
            "bottom": "trap",
            "wall": "reflect",
        },
        f"Unexpected mass-flow parent wall fates: {fates!r}",
    )
    return fates


def read_parent_audit(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    bc = setup.boundary_conditions
    models = state(setup.models, "parent models")
    boundaries = state(bc, "parent boundary conditions")
    materials = state(setup.materials, "parent materials")

    mass_flow_inlets = object_names(bc.mass_flow_inlet)
    velocity_inlets = object_names(bc.velocity_inlet)
    require(set(mass_flow_inlets) == {"liquidinlet", "steaminlet"}, f"Unexpected mass-flow inlets: {mass_flow_inlets}")
    require(not velocity_inlets, f"Unexpected velocity-inlet branch contents: {velocity_inlets}")

    liquid_state = state(bc.mass_flow_inlet["liquidinlet"], "parent liquidinlet")
    steam_state = state(bc.mass_flow_inlet["steaminlet"], "parent steaminlet")
    liquid_flow = close(
        state_value(liquid_state, "phase", "phase-2", "momentum", "mass_flow_rate", "value"),
        EULERIAN_LIQUID_KG_S,
        "parent Eulerian liquid flow",
    )
    vapor_flow = close(
        state_value(steam_state, "phase", "phase-1", "momentum", "mass_flow_rate", "value"),
        VAPOR_KG_S,
        "parent vapor flow",
    )

    require(state_value(models, "multiphase", "model") == "mixture", "Parent is not Mixture")
    require(state_value(models, "multiphase", "phases", "phase-1", "material") == VAPOR_MATERIAL, "Parent vapor material changed")
    require(state_value(models, "multiphase", "phases", "phase-2", "material") == INHERITED_FILM_MATERIAL, "Parent liquid material changed")
    require(state_value(models, "energy", "enabled") is False, "Parent Energy is not off")
    require(state_value(models, "viscous", "model") == "k-epsilon", "Parent is not k-epsilon")
    require(state_value(models, "viscous", "k_epsilon_model") == "rng", "Parent is not RNG k-epsilon")

    dpm = setup.models.discrete_phase
    interaction = state(dpm.general_settings.interaction, "parent DPM interaction")
    require(state_value(interaction, "enabled") is True, "Parent DPM interaction is not enabled")
    require(state_value(interaction, "update_sources_every_iteration") is True, "Parent DPM sources are not updated every iteration")
    close(state_value(interaction, "iteration_interval"), 1, "parent DPM iteration interval", tolerance=0.0)

    injections = state(dpm.injections, "parent injections")
    require(isinstance(injections, Mapping), "Parent DPM injection state is unavailable")
    require(set(injections) == set(LEGACY_INJECTION_NAMES), f"Parent injection names mismatch: {sorted(injections)}")
    legacy_total = 0.0
    for name, payload in injections.items():
        require(payload.get("particle_type") == "inert", f"Parent {name} particle type is not inert")
        require(payload.get("material") == INHERITED_DPM_MATERIAL, f"Parent {name} material mismatch")
        require(state_value(payload, "injection_type", "option") == "surface", f"Parent {name} is not a surface injection")
        require(state_value(payload, "initial_values", "location", "injection_surfaces") == ["steaminlet"], f"Parent {name} is not on steaminlet")
        legacy_total += as_float(
            state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"),
            f"Parent {name} flow",
        )
    close(legacy_total, DPM_TOTAL_KG_S, "parent six-bin DPM total", tolerance=1.0e-12)

    exemplar_name = LEGACY_INJECTION_NAMES[0]
    exemplar = injections[exemplar_name]
    exemplar_location = state_value(exemplar, "initial_values", "location")
    exemplar_velocity = state_value(exemplar, "initial_values", "velocity")
    exemplar_physical_models = state_value(exemplar, "physical_models")
    require(isinstance(exemplar_location, Mapping), "Parent exemplar location is unavailable")
    require(isinstance(exemplar_velocity, Mapping), "Parent exemplar velocity is unavailable")
    require(isinstance(exemplar_physical_models, Mapping), "Parent exemplar physical models are unavailable")

    fluid_materials = state(setup.materials.fluid, "parent fluid materials")
    inert_materials = state(setup.materials.inert_particle, "parent inert materials")
    require(INHERITED_FILM_MATERIAL in fluid_materials, f"Parent material is absent: {INHERITED_FILM_MATERIAL}")
    require(INHERITED_DPM_MATERIAL in inert_materials, f"Parent material is absent: {INHERITED_DPM_MATERIAL}")

    fates = boundary_fates(solver)
    model_children = safe_child_names(setup.models)
    return {
        "mass_flow_inlets": mass_flow_inlets,
        "velocity_inlets": velocity_inlets,
        "liquid_flow_kg_s": liquid_flow,
        "vapor_flow_kg_s": vapor_flow,
        "models": models,
        "boundaries": boundaries,
        "materials": materials,
        "dpm_interaction": interaction,
        "legacy_injections": injections,
        "legacy_total_kg_s": legacy_total,
        "exemplar_name": exemplar_name,
        "exemplar_location": exemplar_location,
        "exemplar_velocity": exemplar_velocity,
        "exemplar_physical_models": exemplar_physical_models,
        "fluid_material_names": sorted(fluid_materials),
        "inert_material_names": sorted(inert_materials),
        "wall_fates": fates,
        "model_children": model_children,
        "ewf_note": "No EWF setting is intentionally changed by this PSD-only child build.",
    }


def set_state_readback(obj: Any, value: Any, label: str) -> Any:
    try:
        obj.set_state(value)
        return obj.get_state()
    except Exception as exc:
        fail(f"Could not set/read back {label}: {type(exc).__name__}: {exc}")
        return None


def set_leaf_readback(obj: Any, value: Any, label: str) -> Any:
    return set_state_readback(obj, value, label)


def set_location(injection: Any, name: str, inherited_location: Mapping[str, Any]) -> dict[str, Any]:
    location = injection.initial_values.location
    desired = deepcopy(dict(inherited_location))
    desired["injection_surfaces"] = ["steaminlet"]
    desired["randomized_positions_enabled"] = False
    try:
        readback = set_state_readback(location, desired, f"{name} location")
        strategy = "inherited location state"
    except UnknownSetup:
        surfaces = location.injection_surfaces
        allowed = safe_allowed_values(surfaces)
        require("steaminlet" in allowed, f"steaminlet is not an allowed surface for {name}: {allowed}")
        set_leaf_readback(surfaces, ["steaminlet"], f"{name} injection surface")
        set_leaf_readback(location.randomized_positions_enabled, False, f"{name} randomized positions")
        readback = state(location, f"{name} location fallback")
        strategy = "surface leaf fallback"
    require(state_value(readback, "injection_surfaces") == ["steaminlet"], f"{name} surface readback mismatch: {readback!r}")
    require(state_value(readback, "randomized_positions_enabled") is False, f"{name} randomized-position readback mismatch")
    return {"strategy": strategy, "readback": readback}


def configure_injection(
    solver: Any,
    name: str,
    interval_um: str,
    diameter_um: float,
    share_pct: float,
    flow_kg_s: float,
    parent_audit: Mapping[str, Any],
) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    inherited_location = parent_audit["exemplar_location"]
    inherited_velocity = parent_audit["exemplar_velocity"]
    inherited_physical_models = parent_audit["exemplar_physical_models"]

    injection = branch[name]
    set_leaf_readback(injection.particle_type, "inert", f"{name} particle type")
    injection = branch[name]
    set_leaf_readback(injection.material, INHERITED_DPM_MATERIAL, f"{name} material")
    injection = branch[name]
    set_leaf_readback(injection.injection_type.option, "surface", f"{name} injection type")
    injection = branch[name]
    location_readback = set_location(injection, name, inherited_location)

    injection = branch[name]
    mass_flow = injection.initial_values.mass_flow_rate
    if "scale_by_area" in safe_child_names(mass_flow):
        set_leaf_readback(mass_flow.scale_by_area, False, f"{name} scale by area")
    set_leaf_readback(mass_flow.total_flow_rate, flow_kg_s, f"{name} total flow rate")

    injection = branch[name]
    set_state_readback(injection.initial_values.velocity, deepcopy(dict(inherited_velocity)), f"{name} inherited velocity")
    set_state_readback(
        injection.initial_values.particle_size,
        {"option": "uniform", "diameter": diameter_um * 1.0e-6},
        f"{name} particle size",
    )

    injection = branch[name]
    physical_strategy = "full inherited physical-model state"
    try:
        physical_readback = set_state_readback(
            injection.physical_models,
            deepcopy(dict(inherited_physical_models)),
            f"{name} physical models",
        )
    except UnknownSetup:
        physical_strategy = "inherited physical-model leaf fallback"
        injection = branch[name]
        set_leaf_readback(
            injection.physical_models.particle_drag.option,
            state_value(inherited_physical_models, "particle_drag", "option"),
            f"{name} drag law",
        )
        injection = branch[name]
        set_state_readback(
            injection.physical_models.turbulent_dispersion,
            deepcopy(dict(state_value(inherited_physical_models, "turbulent_dispersion") or {})),
            f"{name} turbulent dispersion",
        )
        injection = branch[name]
        set_state_readback(
            injection.physical_models.particle_rotation,
            deepcopy(dict(state_value(inherited_physical_models, "particle_rotation") or {})),
            f"{name} particle rotation",
        )
        injection = branch[name]
        set_leaf_readback(
            injection.physical_models.rough_wall_treatment_enabled,
            state_value(inherited_physical_models, "rough_wall_treatment_enabled"),
            f"{name} rough-wall treatment",
        )
        injection = branch[name]
        set_state_readback(
            injection.physical_models.custom_laws,
            deepcopy(dict(state_value(inherited_physical_models, "custom_laws") or {})),
            f"{name} custom laws",
        )
        physical_readback = state(injection.physical_models, f"{name} physical models fallback")

    final = state(branch[name], f"{name} final injection")
    require(final.get("particle_type") == "inert", f"{name} particle type mismatch")
    require(final.get("material") == INHERITED_DPM_MATERIAL, f"{name} material mismatch")
    require(state_value(final, "injection_type", "option") == "surface", f"{name} injection type mismatch")
    require(state_value(final, "initial_values", "location", "injection_surfaces") == ["steaminlet"], f"{name} surface mismatch")
    close(state_value(final, "initial_values", "mass_flow_rate", "total_flow_rate"), flow_kg_s, f"{name} final flow", tolerance=1.0e-12)
    close(state_value(final, "initial_values", "particle_size", "diameter"), diameter_um * 1.0e-6, f"{name} final diameter", tolerance=1.0e-14)
    for component in ("x_velocity", "y_velocity", "z_velocity"):
        close(
            state_value(final, "initial_values", "velocity", component),
            as_float(state_value(inherited_velocity, component), f"parent {component}"),
            f"{name} inherited {component}",
            tolerance=1.0e-12,
        )
    compare_physical_model_subset(state_value(final, "physical_models"), inherited_physical_models, f"{name} physical models")

    return {
        "name": name,
        "interval_um": interval_um,
        "diameter_um": diameter_um,
        "mass_share_pct": share_pct,
        "flow_kg_s": flow_kg_s,
        "active": active_state(branch[name]),
        "location": location_readback,
        "physical_model_strategy": physical_strategy,
        "readback": final,
        "physical_readback": physical_readback,
    }


def create_fine_mist_injections(solver: Any, parent_audit: Mapping[str, Any]) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    existing = {name.casefold() for name in object_names(branch)}
    require(not (existing & TARGET_INJECTION_KEYS), f"Fine-mist target injections already exist: {sorted(existing & TARGET_INJECTION_KEYS)}")

    built: dict[str, Any] = {}
    for name, interval_um, diameter_um, share_pct, flow_kg_s in FINE_MIST_BINS:
        branch.create(name=name)
        branch = solver.settings.setup.models.discrete_phase.injections
        require(name in object_names(branch), f"Injection creation readback failed: {name}")
        built[name] = configure_injection(solver, name, interval_um, diameter_um, share_pct, flow_kg_s, parent_audit)

    total = sum(as_float(item["flow_kg_s"], f"{name} flow") for name, item in built.items())
    close(total, DPM_TOTAL_KG_S, "configured fine-mist DPM total", tolerance=1.0e-12)
    return {"injections": built, "configured_total_kg_s": total}


def remove_legacy_injections(solver: Any, parent_audit: Mapping[str, Any]) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    removed: dict[str, Any] = {}
    for name in LEGACY_INJECTION_NAMES:
        require(name in object_names(branch), f"Expected legacy injection is missing before removal: {name}")
        removed[name] = {
            "action": "removed from copied child injection branch",
            "active_before": active_state(branch[name]),
            "readback_before": parent_audit["legacy_injections"][name],
        }
        try:
            branch.__delitem__(name)
        except Exception:
            branch.delete(name_list=[name])
        branch = solver.settings.setup.models.discrete_phase.injections
        require(name not in object_names(branch), f"Legacy injection removal readback failed: {name}")
    return removed


def final_audit(solver: Any, parent_audit: Mapping[str, Any]) -> dict[str, Any]:
    setup = solver.settings.setup
    models = state(setup.models, "final models")
    boundaries = state(setup.boundary_conditions, "final boundary conditions")
    materials = state(setup.materials, "final materials")

    require(boundaries == parent_audit["boundaries"], "Carrier boundary conditions changed during PSD substitution")
    require(materials == parent_audit["materials"], "Materials changed during PSD substitution")
    require(state_value(models, "multiphase", "model") == "mixture", "Final multiphase model changed")
    require(state_value(models, "energy", "enabled") is False, "Final Energy unexpectedly enabled")
    require(state_value(models, "viscous", "model") == "k-epsilon", "Final viscous model changed")
    require(state_value(models, "viscous", "k_epsilon_model") == "rng", "Final turbulence model changed")

    interaction = state(setup.models.discrete_phase.general_settings.interaction, "final DPM interaction")
    require(state_value(interaction, "enabled") is True, "Final DPM interaction is not enabled")
    require(state_value(interaction, "update_sources_every_iteration") is True, "Final DPM source update is not per iteration")
    close(state_value(interaction, "iteration_interval"), 1, "final DPM iteration interval", tolerance=0.0)

    injections = state(setup.models.discrete_phase.injections, "final fine-mist injections")
    require(isinstance(injections, Mapping), "Final DPM injection state is unavailable")
    injection_map = casefolded_object_map(injections)
    require(set(injection_map) == TARGET_INJECTION_KEYS, f"Final injection names mismatch: {sorted(injections)}")
    require(not (set(injection_map) & LEGACY_INJECTION_KEYS), "A legacy injection remains in the final child")

    records: dict[str, Any] = {}
    flows: dict[str, float] = {}
    for name, interval_um, diameter_um, share_pct, expected_flow in FINE_MIST_BINS:
        actual_name, payload = injection_map[name.casefold()]
        flow = close(state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"), expected_flow, f"{name} final flow", tolerance=1.0e-12)
        diameter = close(state_value(payload, "initial_values", "particle_size", "diameter"), diameter_um * 1.0e-6, f"{name} final diameter", tolerance=1.0e-14)
        require(payload.get("particle_type") == "inert", f"{name} final particle type changed")
        require(payload.get("material") == INHERITED_DPM_MATERIAL, f"{name} final material changed")
        require(state_value(payload, "injection_type", "option") == "surface", f"{name} final injection type changed")
        require(state_value(payload, "initial_values", "location", "injection_surfaces") == ["steaminlet"], f"{name} final surface changed")
        compare_physical_model_subset(state_value(payload, "physical_models"), parent_audit["exemplar_physical_models"], f"{name} final physical models")
        flows[name] = flow
        records[name] = {
            "interval_um": interval_um,
            "diameter_um": diameter,
            "mass_share_pct": share_pct,
            "flow_kg_s": flow,
            "fluent_case_name": actual_name,
            "active": active_state(setup.models.discrete_phase.injections[actual_name]),
        }

    total = close(sum(flows.values()), DPM_TOTAL_KG_S, "final fine-mist DPM total", tolerance=1.0e-12)
    require(abs(EULERIAN_LIQUID_KG_S + total - LIQUID_REFERENCE_KG_S) <= 1.0e-12, "Input liquid accounting does not close")
    fates = boundary_fates(solver)
    require(fates == parent_audit["wall_fates"], f"Boundary DPM fates changed from parent: {fates!r}")

    return {
        "models": models,
        "mass_flow_inlets": object_names(setup.boundary_conditions.mass_flow_inlet),
        "liquid_flow_kg_s": close(
            state_value(boundaries, "mass_flow_inlet", "liquidinlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value"),
            EULERIAN_LIQUID_KG_S,
            "final Eulerian liquid flow",
        ),
        "vapor_flow_kg_s": close(
            state_value(boundaries, "mass_flow_inlet", "steaminlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value"),
            VAPOR_KG_S,
            "final vapor flow",
        ),
        "dpm_interaction": interaction,
        "injections": records,
        "dpm_flows_kg_s": flows,
        "dpm_total_kg_s": total,
        "input_liquid_accounting": {
            "eulerian_liquid_kg_s": EULERIAN_LIQUID_KG_S,
            "dpm_total_kg_s": total,
            "total_liquid_reference_kg_s": LIQUID_REFERENCE_KG_S,
            "closed": True,
        },
        "wall_fates": fates,
        "active_injection_count": len(injections),
        "iterations_performed_by_this_script": 0,
        "data_file_read_by_this_script": False,
        "data_file_written_by_this_script": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and verify the mass-flow 09cV3 fine-mist child.")
    parser.add_argument("--server-id", default=DEFAULT_SERVER_ID)
    parser.add_argument("--source-case", default=DEFAULT_SOURCE_CASE)
    parser.add_argument("--output-case", default=DEFAULT_OUTPUT_CASE)
    parser.add_argument("--backup-case", default=DEFAULT_BACKUP_CASE)
    parser.add_argument("--summary-json", default=str(DEFAULT_SUMMARY_JSON))
    parser.add_argument("--verification-json", default=str(DEFAULT_VERIFICATION_JSON))
    parser.add_argument(
        "--reuse-existing-output",
        action="store_true",
        help="Strictly verify an already-written child without mutating or overwriting it.",
    )
    args = parser.parse_args()
    require(str(args.server_id).strip().lower() == DEFAULT_SERVER_ID, "This builder is restricted to server ID 1")

    source_case = remote_case_path(args.source_case)
    output_case = remote_case_path(args.output_case)
    backup_case = remote_case_path(args.backup_case)
    solver = connect(server_id=args.server_id)

    require(remote_file_exists(solver, source_case), f"Source 09cV2 case does not exist: {source_case}")
    output_exists = remote_file_exists(solver, output_case)
    backup_exists = remote_file_exists(solver, backup_case)
    if not args.reuse_existing_output:
        require(not output_exists, f"Refusing to overwrite existing 09cV3 output: {output_case}")
        require(not backup_exists, f"Refusing to overwrite existing recovery case: {backup_case}")
    else:
        require(output_exists, f"Requested reuse but 09cV3 output does not exist: {output_case}")

    summary: dict[str, Any] = {
        "setup_id": "09cV3",
        "parent_setup_id": "09cV2",
        "artifact_role": "fine-mist PSD child of the explicitly named mass-flow 09cV2 case",
        "case_identity_status": "verified by explicit full-path source and output reload",
        "source_case": source_case,
        "output_case": output_case,
        "backup_case": backup_case,
        "reuse_existing_output": bool(args.reuse_existing_output),
        "fluent_version": solver.get_fluent_version(),
        "dpm_fraction": 0.05,
        "liquid_reference_kg_s": LIQUID_REFERENCE_KG_S,
        "eulerian_liquid_kg_s": EULERIAN_LIQUID_KG_S,
        "vapor_kg_s": VAPOR_KG_S,
        "dpm_total_target_kg_s": DPM_TOTAL_KG_S,
        "psd_basis": "Assumed, medium-risk engineering prior; truncated/renormalised Rosin-Rammler fine-mist distribution",
        "fine_mist_bins": [
            {"name": name, "interval_um": interval, "diameter_um": diameter, "mass_share_pct": share, "flow_kg_s": flow}
            for name, interval, diameter, share, flow in FINE_MIST_BINS
        ],
        "fine_mist_flow_table_sum_kg_s": EXPECTED_FINE_MIST_FLOW_KG_S,
        "notes": [
            "This source uses mass_flow_inlet.liquidinlet and mass_flow_inlet.steaminlet; it is not the Student velocity-inlet adaptation.",
            "Only the active DPM injection population is changed; carrier boundaries, phase flows, materials, global DPM controls, wall fates, and inherited injection properties are read back.",
            "The fine-mist PSD is an assumed engineering prior, not measured inlet data.",
            "Case-only build: no initialization, flow iterations, data read, or .dat.h5 write.",
        ],
    }

    if args.reuse_existing_output:
        try:
            load_case_only(solver, source_case, label="Load explicit mass-flow 09cV2 parent for existing 09cV3 audit")
            parent_audit = read_parent_audit(solver)
            summary["parent_readback"] = parent_audit
            load_case_only(solver, output_case, label="Load existing mass-flow 09cV3 child for strict audit")
            summary["post_save_audit"] = final_audit(solver, parent_audit)
            summary["status"] = "complete"
            summary["verification_status"] = "verified-existing-output"
        except Exception as exc:
            summary["status"] = "failed"
            summary["verification_status"] = "failed"
            summary["failure"] = f"{type(exc).__name__}: {exc}"
            write_json_snapshot(str(Path(args.summary_json).expanduser().resolve()), summary)
            write_json_snapshot(str(Path(args.verification_json).expanduser().resolve()), summary)
            raise
        write_json_snapshot(str(Path(args.summary_json).expanduser().resolve()), summary)
        write_json_snapshot(str(Path(args.verification_json).expanduser().resolve()), summary)
        print(f"source_case: {source_case}")
        print(f"output_case: {output_case}")
        print(f"backup_case: {backup_case}")
        print("Existing mass-flow 09cV3 child passed strict case-only verification.")
        return 0

    backup_written = False
    try:
        load_case_only(solver, source_case, label="Load explicit mass-flow 09cV2 parent for 09cV3 build")
        parent_audit = read_parent_audit(solver)
        summary["parent_readback"] = parent_audit

        write_case_only(solver, backup_case, "Write mass-flow 09cV3 pre-build recovery case")
        require(remote_file_exists(solver, backup_case), "09cV3 recovery case was not visible after write")
        backup_written = True

        summary["fine_mist_build"] = create_fine_mist_injections(solver, parent_audit)
        summary["legacy_injections_removed"] = remove_legacy_injections(solver, parent_audit)
        summary["pre_save_audit"] = final_audit(solver, parent_audit)

        write_case_only(solver, output_case, "Write mass-flow 09cV3 fine-mist case-only child")
        require(remote_file_exists(solver, output_case), "09cV3 output case was not visible after write")

        load_case_only(solver, output_case, label="Reload saved mass-flow 09cV3 fine-mist child")
        summary["post_save_audit"] = final_audit(solver, parent_audit)
        summary["status"] = "complete"
        summary["verification_status"] = "verified"
    except Exception as exc:
        summary["status"] = "failed"
        summary["verification_status"] = "failed"
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        if backup_written:
            try:
                load_case_only(solver, backup_case, label="Restore mass-flow 09cV2 parent after failed build")
                summary["restored_prebuild_case"] = True
            except Exception as restore_exc:
                summary["restored_prebuild_case"] = False
                summary["restore_failure"] = f"{type(restore_exc).__name__}: {restore_exc}"
        write_json_snapshot(str(Path(args.summary_json).expanduser().resolve()), summary)
        write_json_snapshot(str(Path(args.verification_json).expanduser().resolve()), summary)
        raise

    write_json_snapshot(str(Path(args.summary_json).expanduser().resolve()), summary)
    write_json_snapshot(str(Path(args.verification_json).expanduser().resolve()), summary)
    print(f"source_case: {source_case}")
    print(f"output_case: {output_case}")
    print(f"backup_case: {backup_case}")
    print(f"summary_json: {Path(args.summary_json).expanduser().resolve()}")
    print(f"verification_json: {Path(args.verification_json).expanduser().resolve()}")
    print("Mass-flow 09cV3 case-only build and strict reload verification complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UnknownSetup as exc:
        print(f"UNKNOWN_SETUP_STOP: {exc}", file=sys.stderr)
        raise SystemExit(2)

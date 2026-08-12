#!/usr/bin/env python3
"""Build the Student-session 09cV3 fine-mist PSD child from 09cV2.

The parent is the explicitly named Student velocity-inlet adaptation created
for 09cV2.  This script changes only the DPM injection population: the
legacy six-bin payload is replaced by the documented seven-bin 5--100 um
fine-mist prior.  The parent is never overwritten.

This is deliberately a case-only setup build.  It does not initialize,
iterate, read a data file, or write a ``.dat.h5``.  The child is reloaded by
full remote path and audited before the script reports success.
"""

from __future__ import annotations

import argparse
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
DEFAULT_SOURCE_CASE = "09cV2-fDPM-05pct-velocity-inlet-adaptation.cas.h5"
DEFAULT_OUTPUT_CASE = "09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5"
DEFAULT_BACKUP_CASE = "09cV3-student-prebuild-from-09cV2-20260804.cas.h5"
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "output" / "09cV3_student_finemist_from_09cV2_20260804.json"
DEFAULT_VERIFICATION_JSON = PROJECT_ROOT / "output" / "09cV3_student_finemist_verification_20260804.json"

LIQUID_REFERENCE_KG_S = 116.920
EULERIAN_LIQUID_REFERENCE_KG_S = 111.074
DPM_TOTAL_KG_S = 5.846
VAPOR_REFERENCE_KG_S = 80.690

PARENT_LIQUID_VELOCITY_M_S = 25.7621
PARENT_STEAM_VELOCITY_M_S = 27.118
INHERITED_DPM_MATERIAL = "water-liquid-at-psep-dpm"
INHERITED_FILM_MATERIAL = "water-liquid-at-psep"

LEGACY_INJECTION_NAMES = (
    "water-liquid-at-psep-5um",
    "water-liquid-at-psep-28um",
    "water-liquid-at-psep-56um",
    "water-liquid-at-psep-112um",
    "water-liquid-at-psep-168um",
    "water-liquid-at-psep-348um",
)

# The tabulated flows are the exact setup inputs.  The displayed mass shares
# are rounded, so they are intentionally not recomputed here.
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
LEGACY_INJECTION_KEYS = {name.casefold() for name in LEGACY_INJECTION_NAMES}
EXPECTED_FINE_MIST_FLOW_TOTAL = sum(item[4] for item in FINE_MIST_BINS)


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


def active_state(obj: Any) -> bool | None:
    try:
        return bool(obj.is_active())
    except Exception:
        return None


def casefolded_object_map(payload: Mapping[str, Any]) -> dict[str, tuple[str, Any]]:
    return {str(name).casefold(): (str(name), value) for name, value in payload.items()}


def compare_required_physical_models(actual: Any, expected: Any, label: str) -> None:
    for path, expected_value in (
        (("particle_drag", "option"), state_value(expected, "particle_drag", "option")),
        (("particle_rotation", "enabled"), state_value(expected, "particle_rotation", "enabled")),
        (("turbulent_dispersion", "enabled"), state_value(expected, "turbulent_dispersion", "enabled")),
        (("rough_wall_treatment_enabled",), state_value(expected, "rough_wall_treatment_enabled")),
        (("custom_laws", "enabled"), state_value(expected, "custom_laws", "enabled")),
    ):
        if expected_value is None:
            continue
        actual_value = state_value(actual, *path)
        require(actual_value == expected_value, f"{label} {'.'.join(path)} changed: {actual_value!r} != {expected_value!r}")


def read_wall_fates(solver: Any) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    fates = {
        "bottom": state(bc.wall["bottom"].phase["mixture"].discrete_phase.bc_type, "bottom DPM fate"),
        "wall-fluid": state(bc.wall["wall-fluid"].phase["mixture"].discrete_phase.bc_type, "wall-fluid DPM fate"),
        "liquidinlet": state(
            bc.velocity_inlet["liquidinlet"].phase["mixture"].discrete_phase.bc_type,
            "liquidinlet DPM fate",
        ),
        "steaminlet": state(
            bc.velocity_inlet["steaminlet"].phase["mixture"].discrete_phase.bc_type,
            "steaminlet DPM fate",
        ),
        "steamoutlet": state(
            bc.pressure_outlet["steamoutlet"].phase["mixture"].discrete_phase.bc_type,
            "steamoutlet DPM fate",
        ),
    }
    require(fates == {"bottom": "trap", "wall-fluid": "reflect", "liquidinlet": "escape", "steaminlet": "escape", "steamoutlet": "escape"}, f"Unexpected parent wall fates: {fates!r}")
    return fates


def read_parent_audit(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    bc = setup.boundary_conditions

    velocity_inlets = object_names(bc.velocity_inlet)
    require(set(velocity_inlets) == {"liquidinlet", "steaminlet"}, f"Unexpected parent velocity inlets: {velocity_inlets}")
    require(object_names(bc.mass_flow_inlet) == [], "Parent unexpectedly exposes an active mass-flow inlet branch")

    liquid_state = state(bc.velocity_inlet["liquidinlet"], "parent liquidinlet")
    steam_state = state(bc.velocity_inlet["steaminlet"], "parent steaminlet")
    liquid_phase = state_value(liquid_state, "phase", "water-liquid")
    steam_liquid_phase = state_value(steam_state, "phase", "water-liquid")
    steam_phase = state_value(steam_state, "phase", "water-vapor")
    require(isinstance(liquid_phase, Mapping), "Parent liquidinlet water-liquid phase is unavailable")
    require(isinstance(steam_liquid_phase, Mapping), "Parent steaminlet water-liquid phase is unavailable")
    require(isinstance(steam_phase, Mapping), "Parent steaminlet water-vapor phase is unavailable")
    require(state_value(liquid_phase, "multiphase", "volume_fraction", "value") == 1, "Parent liquidinlet is not pure water-liquid")
    # In this split velocity-inlet adaptation Fluent stores the steam-side
    # phase fraction as water-liquid = 0 and leaves the water-vapor fraction
    # leaf inactive/empty.  Preserve that observed parent topology rather
    # than imposing a pure-vapor leaf that is not active in the case.
    require(state_value(steam_liquid_phase, "multiphase", "volume_fraction", "value") == 0, "Parent steaminlet water-liquid fraction is not zero")
    liquid_velocity = close(
        state_value(liquid_phase, "momentum", "velocity_magnitude", "value"),
        PARENT_LIQUID_VELOCITY_M_S,
        "parent liquidinlet water-liquid velocity",
    )
    steam_velocity = close(
        state_value(steam_phase, "momentum", "velocity_magnitude", "value"),
        PARENT_STEAM_VELOCITY_M_S,
        "parent steaminlet water-vapor velocity",
    )

    model_state = state(setup.models, "parent models")
    require(state_value(model_state, "multiphase", "model") == "mixture", "Parent is not Mixture")
    require(state_value(model_state, "energy", "enabled") is False, "Parent Energy is not off")
    require(state_value(model_state, "viscous", "model") == "k-epsilon", "Parent is not k-epsilon")
    require(state_value(model_state, "viscous", "k_epsilon_model") == "rng", "Parent is not RNG k-epsilon")

    dpm = setup.models.discrete_phase
    interaction = dpm.general_settings.interaction
    interaction_state = state(interaction, "parent DPM interaction")
    require(state_value(interaction_state, "enabled") is True, "Parent DPM interaction is not enabled")
    require(state_value(interaction_state, "update_sources_every_iteration") is True, "Parent DPM source updates are not per iteration")
    close(state_value(interaction_state, "iteration_interval"), 1, "parent DPM iteration interval", tolerance=0.0)

    injections = state(dpm.injections, "parent injections")
    require(isinstance(injections, Mapping), "Parent DPM injection state is unavailable")
    require(set(injections) == set(LEGACY_INJECTION_NAMES), f"Parent injection names mismatch: {sorted(injections)}")
    legacy_total = 0.0
    for name, payload in injections.items():
        require(payload.get("particle_type") == "inert", f"Parent {name} particle type is not inert")
        require(payload.get("material") == INHERITED_DPM_MATERIAL, f"Parent {name} material mismatch")
        require(state_value(payload, "injection_type", "option") == "surface", f"Parent {name} is not a surface injection")
        require(state_value(payload, "initial_values", "location", "injection_surfaces") == ["steaminlet"], f"Parent {name} is not on steaminlet")
        legacy_total += as_float(state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"), f"Parent {name} flow")
    close(legacy_total, DPM_TOTAL_KG_S, "parent six-bin DPM total", tolerance=1.0e-12)

    exemplar_name = LEGACY_INJECTION_NAMES[0]
    exemplar = injections[exemplar_name]
    exemplar_location = state_value(exemplar, "initial_values", "location")
    exemplar_velocity = state_value(exemplar, "initial_values", "velocity")
    exemplar_physical_models = state_value(exemplar, "physical_models")
    require(isinstance(exemplar_location, Mapping), "Parent exemplar location state is unavailable")
    require(isinstance(exemplar_velocity, Mapping), "Parent exemplar velocity state is unavailable")
    require(isinstance(exemplar_physical_models, Mapping), "Parent exemplar physical-model state is unavailable")

    fluid_materials = state(setup.materials.fluid, "parent fluid materials")
    inert_materials = state(setup.materials.inert_particle, "parent inert-particle materials")
    require(INHERITED_FILM_MATERIAL in fluid_materials, f"Parent fallback film material {INHERITED_FILM_MATERIAL} is absent")
    require(INHERITED_DPM_MATERIAL in inert_materials, f"Parent DPM material {INHERITED_DPM_MATERIAL} is absent")

    wall_fates = read_wall_fates(solver)
    model_children = safe_child_names(setup.models)
    ewf_evidence = {
        "model_children": model_children,
        "wall_film_branch_present_in_model_children": any(str(name).lower() in {"wall_film", "ewf", "film"} for name in model_children),
        "interpretation": "EWF was not activated in the 09cV2 velocity-inlet adaptation; no EWF setting is changed by this child build.",
    }

    return {
        "velocity_inlets": velocity_inlets,
        "mass_flow_inlets": [],
        "liquid_velocity_m_s": liquid_velocity,
        "steam_velocity_m_s": steam_velocity,
        "models": model_state,
        "dpm_interaction": interaction_state,
        "legacy_injections": injections,
        "legacy_total_kg_s": legacy_total,
        "exemplar_name": exemplar_name,
        "exemplar_location": exemplar_location,
        "exemplar_velocity": exemplar_velocity,
        "exemplar_physical_models": exemplar_physical_models,
        "fluid_material_names": sorted(fluid_materials),
        "inert_material_names": sorted(inert_materials),
        "wall_fates": wall_fates,
        "ewf": ewf_evidence,
    }


def set_location(injection: Any, name: str, inherited_location: Mapping[str, Any]) -> dict[str, Any]:
    location = injection.initial_values.location
    desired = dict(inherited_location)
    desired["injection_surfaces"] = ["steaminlet"]
    desired["randomized_positions_enabled"] = False
    try:
        location.set_state(desired)
        readback = location.get_state()
        strategy = "inherited location state"
    except Exception:
        surfaces = location.injection_surfaces
        allowed = safe_allowed_values(surfaces)
        require("steaminlet" in allowed, f"steaminlet is not an allowed surface for {name}: {allowed}")
        surfaces.set_state(["steaminlet"])
        location.randomized_positions_enabled.set_state(False)
        readback = location.get_state()
        strategy = "surface leaf fallback"
    require(state_value(readback, "injection_surfaces") == ["steaminlet"], f"{name} surface readback mismatch: {readback!r}")
    require(state_value(readback, "randomized_positions_enabled") is False, f"{name} randomized-position readback mismatch: {readback!r}")
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
    injection = branch[name]
    inherited_location = parent_audit["exemplar_location"]
    inherited_velocity = parent_audit["exemplar_velocity"]
    inherited_physical_models = parent_audit["exemplar_physical_models"]

    set_leaf_readback(injection.particle_type, "inert", f"{name} particle type")
    injection = branch[name]
    set_leaf_readback(injection.material, INHERITED_DPM_MATERIAL, f"{name} material")
    injection = branch[name]
    set_leaf_readback(injection.injection_type.option, "surface", f"{name} injection type")
    injection = branch[name]
    location = set_location(injection, name, inherited_location)

    injection = branch[name]
    mass_flow = injection.initial_values.mass_flow_rate
    if "scale_by_area" in safe_child_names(mass_flow):
        set_leaf_readback(mass_flow.scale_by_area, False, f"{name} scale by area")
    set_leaf_readback(mass_flow.total_flow_rate, flow_kg_s, f"{name} total flow rate")

    injection = branch[name]
    set_state_readback(injection.initial_values.velocity, dict(inherited_velocity), f"{name} inherited velocity")
    set_state_readback(
        injection.initial_values.particle_size,
        {"option": "uniform", "diameter": diameter_um * 1.0e-6},
        f"{name} particle size",
    )

    injection = branch[name]
    physical_strategy = "full inherited physical-model state"
    try:
        physical_readback = set_state_readback(injection.physical_models, dict(inherited_physical_models), f"{name} physical models")
    except UnknownSetup:
        physical_strategy = "inherited physical-model leaf fallback"
        injection = branch[name]
        set_leaf_readback(
            injection.physical_models.particle_drag.option,
            state_value(inherited_physical_models, "particle_drag", "option"),
            f"{name} drag law",
        )
        injection = branch[name]
        set_leaf_readback(
            injection.physical_models.particle_rotation.enabled,
            state_value(inherited_physical_models, "particle_rotation", "enabled"),
            f"{name} particle rotation",
        )
        injection = branch[name]
        dispersion = injection.physical_models.turbulent_dispersion
        set_leaf_readback(
            dispersion.enabled,
            state_value(inherited_physical_models, "turbulent_dispersion", "enabled"),
            f"{name} turbulent dispersion",
        )
        injection = branch[name]
        physical_readback = state(injection.physical_models, f"{name} physical models after fallback")

    final = state(branch[name], f"{name} final injection")
    require(final.get("particle_type") == "inert", f"{name} particle type mismatch: {final!r}")
    require(final.get("material") == INHERITED_DPM_MATERIAL, f"{name} material mismatch: {final!r}")
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
    compare_required_physical_models(state_value(final, "physical_models"), inherited_physical_models, f"{name} physical models")

    return {
        "name": name,
        "interval_um": interval_um,
        "diameter_um": diameter_um,
        "mass_share_pct": share_pct,
        "flow_kg_s": flow_kg_s,
        "active": active_state(branch[name]),
        "location": location,
        "physical_model_strategy": physical_strategy,
        "readback": final,
        "physical_readback": physical_readback,
    }


def create_fine_mist_injections(solver: Any, parent_audit: Mapping[str, Any]) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    existing = set(object_names(branch))
    require(not (existing & TARGET_INJECTION_NAMES), f"Fine-mist target injections already exist: {sorted(existing & TARGET_INJECTION_NAMES)}")

    built: dict[str, Any] = {}
    for name, interval_um, diameter_um, share_pct, flow_kg_s in FINE_MIST_BINS:
        branch.create(name=name)
        branch = solver.settings.setup.models.discrete_phase.injections
        require(name in set(object_names(branch)), f"Injection creation readback failed: {name}")
        built[name] = configure_injection(solver, name, interval_um, diameter_um, share_pct, flow_kg_s, parent_audit)

    final_names = set(object_names(solver.settings.setup.models.discrete_phase.injections))
    require(TARGET_INJECTION_NAMES <= final_names, f"Not all fine-mist injections are present: {sorted(final_names)}")
    total = sum(as_float(item["flow_kg_s"], f"{name} flow") for name, item in built.items())
    close(total, DPM_TOTAL_KG_S, "configured fine-mist DPM total", tolerance=1.0e-12)
    return {"injections": built, "configured_total_kg_s": total}


def remove_legacy_injections(solver: Any, parent_audit: Mapping[str, Any]) -> dict[str, Any]:
    branch = solver.settings.setup.models.discrete_phase.injections
    removed: dict[str, Any] = {}
    for name in LEGACY_INJECTION_NAMES:
        require(name in set(object_names(branch)), f"Expected legacy injection is missing before deactivation: {name}")
        removed[name] = {
            "action": "removed from active injection branch in copied child",
            "active_before": active_state(branch[name]),
            "readback_before": parent_audit["legacy_injections"][name],
        }
        try:
            branch.__delitem__(name)
        except Exception:
            branch.delete(name_list=[name])
        branch = solver.settings.setup.models.discrete_phase.injections
        require(name not in set(object_names(branch)), f"Legacy injection removal readback failed: {name}")
    return removed


def final_audit(solver: Any, parent_audit: Mapping[str, Any]) -> dict[str, Any]:
    setup = solver.settings.setup
    bc = setup.boundary_conditions
    models = state(setup.models, "final models")
    require(state_value(models, "multiphase", "model") == state_value(parent_audit["models"], "multiphase", "model") == "mixture", "Final multiphase model changed")
    require(state_value(models, "energy", "enabled") is False, "Final Energy unexpectedly enabled")
    require(state_value(models, "viscous", "model") == "k-epsilon", "Final viscous model changed")
    require(state_value(models, "viscous", "k_epsilon_model") == "rng", "Final turbulence model changed")

    liquid_state = state(bc.velocity_inlet["liquidinlet"], "final liquidinlet")
    steam_state = state(bc.velocity_inlet["steaminlet"], "final steaminlet")
    liquid_velocity = close(state_value(liquid_state, "phase", "water-liquid", "momentum", "velocity_magnitude", "value"), PARENT_LIQUID_VELOCITY_M_S, "final liquid velocity")
    steam_velocity = close(state_value(steam_state, "phase", "water-vapor", "momentum", "velocity_magnitude", "value"), PARENT_STEAM_VELOCITY_M_S, "final steam velocity")

    interaction = setup.models.discrete_phase.general_settings.interaction
    interaction_state = state(interaction, "final DPM interaction")
    require(state_value(interaction_state, "enabled") is True, "Final DPM interaction is not enabled")
    require(state_value(interaction_state, "update_sources_every_iteration") is True, "Final DPM source update is not per iteration")
    close(state_value(interaction_state, "iteration_interval"), 1, "final DPM iteration interval", tolerance=0.0)

    injections = state(setup.models.discrete_phase.injections, "final fine-mist injections")
    require(isinstance(injections, Mapping), "Final DPM injection state is unavailable")
    injection_map = casefolded_object_map(injections)
    # Fluent 2025 R2 lowercases object names when the case is serialized.  The
    # requested setup identities retain their documented spelling in the
    # audit records, while the live saved-case comparison is case-insensitive.
    require(set(injection_map) == TARGET_INJECTION_KEYS, f"Final injection names mismatch after Fluent canonicalization: {sorted(injections)}")
    require(not (set(injection_map) & LEGACY_INJECTION_KEYS), "A legacy injection remains active")

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
        compare_required_physical_models(state_value(payload, "physical_models"), parent_audit["exemplar_physical_models"], f"{name} final physical models")
        flows[name] = flow
        records[name] = {
            "interval_um": interval_um,
            "diameter_um": diameter,
            "mass_share_pct": share_pct,
            "flow_kg_s": flow,
            "fluent_case_name": actual_name,
            "active": active_state(setup.models.discrete_phase.injections[actual_name]),
            "payload": payload,
        }
    total = close(sum(flows.values()), DPM_TOTAL_KG_S, "final fine-mist DPM total", tolerance=1.0e-12)
    require(abs(EULERIAN_LIQUID_REFERENCE_KG_S + total - LIQUID_REFERENCE_KG_S) <= 1.0e-12, "Input liquid accounting does not close")

    fluid_materials = state(setup.materials.fluid, "final fluid materials")
    inert_materials = state(setup.materials.inert_particle, "final inert materials")
    require(INHERITED_FILM_MATERIAL in fluid_materials, "Final fallback film material is absent")
    require(INHERITED_DPM_MATERIAL in inert_materials, "Final DPM material is absent")
    walls = read_wall_fates(solver)
    require(walls == parent_audit["wall_fates"], f"Wall fates changed from parent: {walls!r}")

    return {
        "models": models,
        "liquid_velocity_m_s": liquid_velocity,
        "steam_velocity_m_s": steam_velocity,
        "dpm_interaction": interaction_state,
        "injections": records,
        "dpm_flows_kg_s": flows,
        "dpm_total_kg_s": total,
        "input_liquid_accounting": {
            "eulerian_liquid_reference_kg_s": EULERIAN_LIQUID_REFERENCE_KG_S,
            "dpm_total_kg_s": total,
            "total_liquid_reference_kg_s": LIQUID_REFERENCE_KG_S,
            "closed": True,
        },
        "wall_fates": walls,
        "fluid_material_names": sorted(fluid_materials),
        "inert_material_names": sorted(inert_materials),
        "legacy_injections_present": sorted(set(injection_map) & LEGACY_INJECTION_KEYS),
        "active_injection_count": len(injections),
        "iterations_performed_by_this_script": 0,
        "data_file_read_by_this_script": False,
        "data_file_written_by_this_script": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
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
    require(str(args.server_id).strip().lower() == DEFAULT_SERVER_ID, "This build is restricted to the student endpoint")

    source_case = remote_case_path(args.source_case)
    output_case = remote_case_path(args.output_case)
    backup_case = remote_case_path(args.backup_case)
    solver = connect(server_id=args.server_id)

    require(remote_file_exists(solver, source_case), f"Source 09cV2 case does not exist: {source_case}")
    output_exists = remote_file_exists(solver, output_case)
    backup_exists = remote_file_exists(solver, backup_case)
    if not args.reuse_existing_output:
        require(not output_exists, f"Refusing to overwrite existing 09cV3 output: {output_case}")
        require(not backup_exists, f"Refusing to overwrite existing 09cV3 recovery: {backup_case}")
    else:
        require(output_exists, f"Requested reuse but 09cV3 output does not exist: {output_case}")

    summary: dict[str, Any] = {
        "setup_id": "09cV3",
        "parent_setup_id": "09cV2",
        "artifact_role": "fine-mist PSD child of the Student velocity-inlet 09cV2 adaptation",
        "case_identity_status": "verified by explicit full-path source and output reload",
        "source_case": source_case,
        "output_case": output_case,
        "backup_case": backup_case,
        "reuse_existing_output": bool(args.reuse_existing_output),
        "fluent_version": solver.get_fluent_version(),
        "dpm_fraction": 0.05,
        "liquid_reference_kg_s": LIQUID_REFERENCE_KG_S,
        "eulerian_liquid_reference_kg_s": EULERIAN_LIQUID_REFERENCE_KG_S,
        "dpm_total_target_kg_s": DPM_TOTAL_KG_S,
        "vapor_reference_kg_s": VAPOR_REFERENCE_KG_S,
        "psd_basis": "Assumed, medium-risk engineering prior; truncated/renormalised Rosin-Rammler fine-mist distribution",
        "fine_mist_bins": [
            {"name": name, "interval_um": interval, "diameter_um": diameter, "mass_share_pct": share, "flow_kg_s": flow}
            for name, interval, diameter, share, flow in FINE_MIST_BINS
        ],
        "fine_mist_flow_table_sum_kg_s": EXPECTED_FINE_MIST_FLOW_TOTAL,
        "notes": [
            "The parent was explicitly loaded from the Student velocity-inlet adaptation output, not inferred from server ID or the current session label.",
            "Only the active DPM injection population is changed: six legacy injections are removed from the copied child branch and seven fine-mist surface injections are created on steaminlet.",
            "All non-PSD injection settings are inherited from the parent exemplar and read back after each new injection is configured.",
            "The liquid allocation remains the parent velocity-inlet adaptation assumption; the live session does not expose an independent mass-flow report for 111.074 kg/s.",
            "The fine-mist PSD is an assumed engineering prior, not measured inlet data.",
            "Case-only build: no initialization, flow iterations, data read, or .dat.h5 write.",
        ],
    }

    if args.reuse_existing_output:
        try:
            load_case_only(solver, source_case, label="Load explicit 09cV2 parent for existing 09cV3 audit")
            parent_audit = read_parent_audit(solver)
            summary["parent_readback"] = parent_audit
            load_case_only(solver, output_case, label="Load existing 09cV3 child for strict audit")
            summary["post_save_audit"] = final_audit(solver, parent_audit)
            summary["status"] = "complete"
            summary["verification_status"] = "verified-existing-output"
            summary["build_reused_existing_output"] = True
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
        print(f"summary_json: {Path(args.summary_json).expanduser().resolve()}")
        print(f"verification_json: {Path(args.verification_json).expanduser().resolve()}")
        print("Existing 09cV3 Student fine-mist child passed strict case-only verification.")
        return 0

    backup_written = False
    try:
        load_case_only(solver, source_case, label="Load explicit 09cV2 parent for 09cV3 build")
        parent_audit = read_parent_audit(solver)
        summary["parent_readback"] = parent_audit

        write_case_only(solver, backup_case, "Write 09cV3 pre-build recovery case")
        require(remote_file_exists(solver, backup_case), "09cV3 pre-build recovery case was not visible after write")
        backup_written = True

        summary["fine_mist_build"] = create_fine_mist_injections(solver, parent_audit)
        summary["legacy_injections_deactivated"] = remove_legacy_injections(solver, parent_audit)
        summary["pre_save_audit"] = final_audit(solver, parent_audit)

        write_case_only(solver, output_case, "Write 09cV3 fine-mist case-only child")
        require(remote_file_exists(solver, output_case), "09cV3 output case was not visible after write")

        load_case_only(solver, output_case, label="Reload saved 09cV3 fine-mist child")
        post_parent_reference = dict(parent_audit)
        summary["post_save_audit"] = final_audit(solver, post_parent_reference)
        summary["status"] = "complete"
        summary["verification_status"] = "verified"
    except Exception as exc:
        summary["status"] = "failed"
        summary["verification_status"] = "failed"
        summary["failure"] = f"{type(exc).__name__}: {exc}"
        if backup_written:
            try:
                load_case_only(solver, backup_case, label="Restore 09cV2 parent after failed 09cV3 build")
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
    print("09cV3 Student fine-mist case-only build and strict reload verification complete.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UnknownSetup as exc:
        print(f"UNKNOWN_SETUP_STOP: {exc}", file=sys.stderr)
        raise SystemExit(2)

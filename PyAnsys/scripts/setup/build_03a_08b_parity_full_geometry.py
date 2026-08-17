#!/usr/bin/env python3
"""Build and reload-verify the current 03A carrier-only case.

The case is reconstructed from the audited 00a/08b continuous-phase record,
the 07 split-inlet representation, and the current Full-geomV2 mesh.  This
script deliberately stops at a case-only save: Fluent-native initialization,
iterations, data writes, DPM tracking, and EWF operations are separate work.

The saved 08b case on Student uses mass-flow inlets, while the current 03A
contract explicitly requires pure-phase velocity inlets.  That is recorded as
an intentional project-side representation difference in the manifest; the
audited carrier values remain the source authority.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, load_target_mesh, write_case_only  # noqa: E402
from pyansys_fluent.setup_common import normalize_name  # noqa: E402


EXACT_MESH_NAME = "Full-geomV2-231kcells.msh.h5"
DEFAULT_MESH = rf"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\{EXACT_MESH_NAME}"
DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
STEAM_OUTLET_PRESSURE_PA = 1_120_000.0
INLET_REFERENCE_PRESSURE_PA = 1_140_000.0
INLET_VELOCITY_M_S = 27.118
INLET_INTENSITY = 0.0211
STEAM_OUTLET_BACKFLOW_INTENSITY = 0.021525
STEAM_OUTLET_DH_M = 0.724
BRINE_OUTLET_BACKFLOW_INTENSITY = 0.0261
BRINE_OUTLET_DH_M = 0.508
LIQUID_DH_M = 0.01338
STEAM_DH_M = 0.72061
VAPOUR_DENSITY = 5.7974339
VAPOUR_VISCOSITY = 1.52062e-5
LIQUID_DENSITY = 881.21088
LIQUID_VISCOSITY = 1.45544e-4

SOURCE_AUTHORITY = {
    "target_setup": "Setups/full-geometry/mixture/steady-liquid-outlet/03a-08b-parity-full-geometry-baseline.md",
    "carrier_authority": "Setups/past/archived/00a-purnanto-setup-5000-live-audit.md",
    "parity_lineage": "Setups/past/reported/08b-purnanto-parity-split-inlet-rebuild.md",
    "split_representation": "Setups/past/archived/08a-steam-outlet-extension-student-trial.md",
    "surviving_machine_extract": "PyAnsys/cases/actual_setup_archives/purnanto-enthalpy1520-live-extract/live/bundle.json",
    "missing_machine_extract": "PyAnsys/cases/actual_setup_archives/purnanto-enthalpy1680-live-extract/live/settings_root_tree.json",
    "excluded_parent": "FG-MIX-T01-S1-C1375 (explicitly excluded by 03A)",
}


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def state_or_empty(obj: Any, label: str) -> dict[str, Any]:
    state = safe_get_state(obj, label)
    return dict(state) if isinstance(state, Mapping) else {}


def object_names(obj: Any) -> list[str]:
    try:
        return sorted(str(name) for name in obj.get_object_names())
    except Exception:
        return []


def zone_names(boundary_state: Mapping[str, Any], boundary_type: str) -> list[str]:
    branch = boundary_state.get(boundary_type, {})
    if not isinstance(branch, Mapping):
        return []
    return sorted(str(name) for name in branch if str(name) != "settings")


def find_named_zone(boundary_state: Mapping[str, Any], boundary_type: str, aliases: tuple[str, ...]) -> str:
    aliases_normalized = {normalize_name(alias) for alias in aliases}
    for name in zone_names(boundary_state, boundary_type):
        if normalize_name(name) in aliases_normalized:
            return name
    raise RuntimeError(
        f"Required {boundary_type} zone was not found for aliases {aliases}; "
        f"available={zone_names(boundary_state, boundary_type)}"
    )


def resolve_zones(solver: Any) -> tuple[dict[str, str], dict[str, Any], dict[str, Any]]:
    boundaries = state_or_empty(solver.settings.setup.boundary_conditions, "03A boundary topology")
    cell_zones = state_or_empty(solver.settings.setup.cell_zone_conditions, "03A cell-zone topology")
    zones = {
        "liquid_inlet": find_named_zone(boundaries, "velocity_inlet", ("liquidinlet", "liquid-inlet")),
        "steam_inlet": find_named_zone(boundaries, "velocity_inlet", ("steaminlet", "steam-inlet")),
        "steam_outlet": find_named_zone(boundaries, "pressure_outlet", ("steamoutlet", "steam-outlet")),
        "brine_outlet": find_named_zone(boundaries, "pressure_outlet", ("brineoutlet", "brine-outlet")),
    }
    walls = zone_names(boundaries, "wall")
    if not walls:
        raise RuntimeError("03A requires at least one physical wall zone")
    zones["wall_zones"] = walls
    return zones, boundaries, cell_zones


def set_leaf(mapping: dict[str, Any], keys: tuple[str, ...], value: Any) -> None:
    cursor = mapping
    for key in keys[:-1]:
        child = cursor.get(key)
        if not isinstance(child, dict):
            child = {}
            cursor[key] = child
        cursor = child
    cursor[keys[-1]] = value


def existing_or_default(mapping: Mapping[str, Any], candidates: tuple[str, ...], default: str) -> str:
    for candidate in candidates:
        if candidate in mapping:
            return candidate
    return default


def set_general(solver: Any) -> None:
    general = solver.settings.setup.general
    setattr(general.solver, "type", "pressure-based")
    setattr(general.solver, "time", "steady")
    setattr(general.solver, "velocity_formulation", "absolute")
    setattr(general.operating_conditions.gravity, "enable", True)
    setattr(general.operating_conditions.gravity, "components", [0.0, -9.81, 0.0])
    setattr(general.operating_conditions, "operating_pressure", 0.0)
    # These leaves are inactive on a fresh single-phase mesh.  They are
    # applied again after Mixture activation in set_operating_conditions.
    try:
        setattr(general.operating_conditions.operating_density, "method", "mixture-averaged")
    except Exception as exc:
        print(f"operating_density: deferred until Mixture activation ({exc})", flush=True)
    try:
        general.operating_conditions.operating_temperature.set_state(298.15)
    except Exception as exc:
        print(f"operating_temperature: deferred until Mixture activation ({exc})", flush=True)
    try:
        setattr(general.operating_conditions, "reference_pressure_method", "Connected and disconnected fluid zones")
    except Exception as exc:
        print(f"reference_pressure_method: not exposed ({exc})", flush=True)


def set_operating_conditions(solver: Any) -> dict[str, Any]:
    """Set Mixture-dependent operating leaves and record API limitations."""
    general = solver.settings.setup.general
    limitations: list[str] = []
    try:
        setattr(general.operating_conditions.operating_density, "method", "mixture-averaged")
    except Exception as exc:
        limitations.append(f"operating_density: {type(exc).__name__}: {exc}")
    try:
        general.operating_conditions.operating_temperature.set_state(298.15)
    except Exception as exc:
        limitations.append(f"operating_temperature: {type(exc).__name__}: {exc}")
    state = state_or_empty(general, "operating conditions readback")
    readback = {
        "operating_density_method": nested(state, "operating_conditions", "operating_density", "method"),
        "operating_temperature": nested(state, "operating_conditions", "operating_temperature"),
        "limitations": limitations,
    }
    if readback["operating_density_method"] != "mixture-averaged":
        readback["limitations"].append(
            f"operating_density readback is {readback['operating_density_method']!r}, expected 'mixture-averaged'"
        )
    if readback["operating_temperature"] is None:
        readback["limitations"].append("operating_temperature is not exposed by the current Student settings tree")
    return readback


def ensure_material(material_branch: Any, name: str, state: dict[str, Any]) -> None:
    if name not in set(object_names(material_branch)):
        material_branch.create(name=name)
    material_branch[name].set_state(state)


def set_materials(solver: Any) -> None:
    fluid = solver.settings.setup.materials.fluid
    ensure_material(
        fluid,
        "water-vapor-at-psep",
        {
            "name": "water-vapor-at-psep",
            "chemical_formula": "h2o-sep",
            "density": {"option": "constant", "value": VAPOUR_DENSITY},
            "viscosity": {"option": "constant", "value": VAPOUR_VISCOSITY},
        },
    )
    ensure_material(
        fluid,
        "water-liquid-at-psep",
        {
            "name": "water-liquid-at-psep",
            "chemical_formula": "h2o-psep",
            "density": {"option": "constant", "value": LIQUID_DENSITY},
            "viscosity": {"option": "constant", "value": LIQUID_VISCOSITY},
        },
    )


def set_models(solver: Any) -> None:
    models = solver.settings.setup.models
    multiphase = models.multiphase
    mp_state = state_or_empty(multiphase, "multiphase before activation")
    if "model" in mp_state or hasattr(multiphase, "model"):
        setattr(multiphase, "model", "mixture")
    elif "models" in mp_state or hasattr(multiphase, "models"):
        setattr(multiphase, "models", "mixture")
    else:
        raise RuntimeError(f"Mixture model setter is not exposed: {mp_state}")

    # Model activation can replace the settings object, so reacquire it.
    multiphase = solver.settings.setup.models.multiphase
    number = multiphase.number_of_phases
    number_state = safe_get_state(number, "number of phases")
    activated_state = state_or_empty(multiphase, "multiphase after activation")
    activated_phases = activated_state.get("phases", {})
    already_two_phases = isinstance(activated_phases, Mapping) and all(
        phase_name in activated_phases for phase_name in ("phase-1", "phase-2")
    )
    if not already_two_phases and number_state != 2 and not (isinstance(number_state, Mapping) and 2 in number_state.values()):
        attempts = (
            lambda: number.set_state(2),
            lambda: setattr(number, "number_of_eulerian_phases", 2),
            lambda: setattr(multiphase, "number_of_phases", 2),
        )
        for attempt in attempts:
            try:
                attempt()
                break
            except Exception:
                continue
        else:
            raise RuntimeError("Could not set Mixture phase count to two")

    models = solver.settings.setup.models
    models.energy.enabled = False
    models.viscous.model = "k-epsilon"
    models.viscous.k_epsilon_model = "rng"
    models.viscous.rng_options.differential_viscosity_model = True
    models.viscous.rng_options.swirl_dominated_flow = True
    models.viscous.near_wall_treatment.wall_treatment = "standard-wall-fn"


def set_phase_materials(solver: Any) -> None:
    vapor = "water-vapor-at-psep"
    liquid = "water-liquid-at-psep"
    models = solver.settings.setup.models
    assigned = False

    # Fluent 2025 R2 exposes phase material assignment beneath Mixture after
    # activation.  Keep this path first because it is the live model state.
    try:
        phases = models.multiphase.phases
        phases["phase-1"].set_state({"material": vapor})
        phases["phase-2"].set_state({"material": liquid})
        assigned = True
    except Exception as exc:
        print(f"multiphase phase-material path: unavailable ({exc})", flush=True)

    # The surviving Purnanto extraction also records the same assignment in
    # species.model.phase_material even with species transport off.
    try:
        species_model = models.species.model
        current = state_or_empty(species_model, "phase material mapping")
        current.update({"option": "off", "phase_material": {"phase-1": vapor, "phase-2": liquid}})
        species_model.set_state(current)
        assigned = True
    except Exception as exc:
        print(f"species phase-material path: unavailable ({exc})", flush=True)

    if not assigned:
        # Last-resort TUI path retained for the known 2025 R2 phase menu.
        for index, material in ((1, vapor), (2, liquid)):
            command = f"/define/phases/set-domain-properties/phase-domains/phase-{index}/material yes {material}"
            solver.scheme.exec((f'(ti-menu-load-string "{command}")',))

    state = state_or_empty(solver.settings.setup.models, "phase material readback")
    serialized = json.dumps(state, sort_keys=True, default=str)
    if vapor not in serialized or liquid not in serialized:
        raise RuntimeError(f"Phase material readback does not contain the audited psep materials: {state}")


def boundary_state(solver: Any, boundary_type: str, name: str) -> dict[str, Any]:
    branch = getattr(solver.settings.setup.boundary_conditions, boundary_type)
    return state_or_empty(branch[name], f"{boundary_type}.{name}")


def set_velocity_inlet(solver: Any, name: str, *, liquid: bool, hydraulic_diameter: float) -> None:
    before = boundary_state(solver, "velocity_inlet", name)
    mixture = nested(before, "phase", "mixture") or {}
    mixture_momentum = mixture.get("momentum", {}) if isinstance(mixture, Mapping) else {}
    pressure_key = existing_or_default(
        mixture_momentum if isinstance(mixture_momentum, Mapping) else {},
        ("initial_gauge_pressure", "supersonic_gauge_pressure"),
        "initial_gauge_pressure",
    )
    pressure = {pressure_key: {"option": "value", "value": INLET_REFERENCE_PRESSURE_PA}}
    if "supersonic_gauge_pressure" in mixture_momentum:
        pressure["supersonic_gauge_pressure"] = {"option": "value", "value": INLET_REFERENCE_PRESSURE_PA}
    first_payload: dict[str, Any] = {
        "phase": {
            "mixture": {
                "momentum": {
                    **pressure,
                },
                "turbulence": {
                    "turbulence_specification": "Intensity and Hydraulic Diameter",
                },
            }
        }
    }
    obj = solver.settings.setup.boundary_conditions.velocity_inlet[name]
    obj.set_state(first_payload)

    # Changing the turbulence specification activates the hydraulic-diameter
    # child in Fluent; reacquire the zone before setting that now-live leaf.
    payload: dict[str, Any] = {
        "phase": {
            "mixture": {
                "turbulence": {
                    "turbulent_intensity": INLET_INTENSITY,
                    "hydraulic_diameter": hydraulic_diameter,
                }
            }
        }
    }
    for phase in ("phase-1", "phase-2"):
        existing_momentum = nested(before, "phase", phase, "momentum") or {}
        velocity_key = existing_or_default(
            existing_momentum if isinstance(existing_momentum, Mapping) else {},
            ("velocity_magnitude", "velocity"),
            "velocity",
        )
        payload["phase"][phase] = {
            "momentum": {
                "velocity_specification_method": "Magnitude, Normal to Boundary",
                "reference_frame": "Absolute",
                velocity_key: {"option": "value", "value": INLET_VELOCITY_M_S},
            }
        }
    payload["phase"]["phase-2"]["multiphase"] = {
        "volume_fraction": {"option": "value", "value": 1.0 if liquid else 0.0}
    }
    obj.set_state(payload)
    after = boundary_state(solver, "velocity_inlet", name)
    actual_velocity = get_velocity(after, "phase-2")
    actual_vf = nested(after, "phase", "phase-2", "multiphase", "volume_fraction", "value")
    if actual_velocity is None or abs(float(actual_velocity) - INLET_VELOCITY_M_S) > 1e-9:
        raise RuntimeError(f"Velocity readback failed for {name}: {after}")
    if actual_vf is None or abs(float(actual_vf) - (1.0 if liquid else 0.0)) > 1e-9:
        raise RuntimeError(f"Phase-2 volume-fraction readback failed for {name}: {after}")


def set_pressure_outlet(solver: Any, name: str, *, liquid_backflow: float, intensity: float, hydraulic_diameter: float) -> None:
    first_payload = {
        "phase": {
            "mixture": {
                "momentum": {
                    "gauge_pressure": {"option": "value", "value": STEAM_OUTLET_PRESSURE_PA},
                    "pressure_profile_multiplier": 1.0,
                    "backflow_dir_spec_method": "Normal to Boundary",
                    "backflow_pressure_spec": "Total Pressure",
                    "radial_equ_pressure_distribution": False,
                },
                "turbulence": {
                    "turbulence_specification": "Intensity and Hydraulic Diameter",
                },
            },
        }
    }
    obj = solver.settings.setup.boundary_conditions.pressure_outlet[name]
    obj.set_state(first_payload)
    payload = {
        "phase": {
            "mixture": {
                "turbulence": {
                    "backflow_turbulent_intensity": intensity,
                    "backflow_hydraulic_diameter": hydraulic_diameter,
                },
            },
            "phase-2": {
                "multiphase": {
                    "volume_frac_spec_method": "Backflow Volume Fraction",
                    "backflow_volume_fraction": {"option": "value", "value": liquid_backflow},
                }
            },
        }
    }
    obj = solver.settings.setup.boundary_conditions.pressure_outlet[name]
    obj.set_state(payload)
    after = boundary_state(solver, "pressure_outlet", name)
    pressure = nested(after, "phase", "mixture", "momentum", "gauge_pressure", "value")
    vf = nested(after, "phase", "phase-2", "multiphase", "backflow_volume_fraction", "value")
    if pressure is None or abs(float(pressure) - STEAM_OUTLET_PRESSURE_PA) > 1e-6:
        raise RuntimeError(f"Pressure readback failed for {name}: {after}")
    if vf is None or abs(float(vf) - liquid_backflow) > 1e-9:
        raise RuntimeError(f"Backflow phase-fraction readback failed for {name}: {after}")


def set_walls(solver: Any, wall_names: list[str]) -> None:
    branch = solver.settings.setup.boundary_conditions.wall
    payload = {
        "phase": {
            "mixture": {
                "momentum": {"wall_motion": "Stationary Wall", "shear_condition": "No Slip"},
                "turbulence": {
                    "roughness_height": {"option": "value", "value": 0.0},
                    "roughness_const": {"option": "value", "value": 0.5},
                },
            }
        }
    }
    for name in wall_names:
        branch[name].set_state(payload)


def get_velocity(state: Mapping[str, Any], phase: str) -> Any:
    momentum = nested(state, "phase", phase, "momentum") or {}
    for key in ("velocity_magnitude", "velocity"):
        value = nested(momentum, key, "value")
        if value is not None:
            return value
    return None


def apply_boundaries(solver: Any, zones: Mapping[str, str]) -> None:
    set_velocity_inlet(solver, zones["liquid_inlet"], liquid=True, hydraulic_diameter=LIQUID_DH_M)
    set_velocity_inlet(solver, zones["steam_inlet"], liquid=False, hydraulic_diameter=STEAM_DH_M)
    set_pressure_outlet(
        solver,
        zones["steam_outlet"],
        liquid_backflow=0.0,
        intensity=STEAM_OUTLET_BACKFLOW_INTENSITY,
        hydraulic_diameter=STEAM_OUTLET_DH_M,
    )
    set_pressure_outlet(
        solver,
        zones["brine_outlet"],
        liquid_backflow=1.0,
        intensity=BRINE_OUTLET_BACKFLOW_INTENSITY,
        hydraulic_diameter=BRINE_OUTLET_DH_M,
    )
    set_walls(solver, list(zones["wall_zones"]))


def apply_solution(solver: Any) -> None:
    methods = solver.settings.solution.methods
    methods.set_state(
        {
            "p_v_coupling": {"flow_scheme": "SIMPLE", "solve_n_phase": False},
            "gradient_scheme": "green-gauss-node-based",
            "discretization_scheme": {
                "pressure": "presto!",
                "mom": "second-order-upwind",
                "k": "second-order-upwind",
                "epsilon": "second-order-upwind",
                "mp": "quick",
            },
            "pseudo_time_method": {"formulation": {"segregated_solver": "off"}},
            "high_order_term_relaxation": {"enable": False},
        }
    )
    solver.settings.solution.controls.set_state(
        {
            "under_relaxation": {
                "pressure": 0.3,
                "mom": 0.7,
                "density": 1.0,
                "body-force": 1.0,
                "drift": 0.1,
                "mp": 0.4,
                "k": 0.8,
                "epsilon": 0.8,
                "turb-viscosity": 1.0,
            },
            "equations": {"drift": True, "flow": True, "ke": True, "mp": True},
            "limits": {
                "min_pressure": 1,
                "max_pressure": 5.0e10,
                "min_tke": 1e-14,
                "min_epsilon": 1e-20,
                "max_turb_visc_ratio": 100000.0,
                "min_vol_frac_for_matrix_sol": 1e-8,
            },
        }
    )
    residual = solver.settings.solution.monitor.residual
    residual.set_state(
        {
            "equations": {
                "continuity": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-4},
                "x-velocity": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-3},
                "y-velocity": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-3},
                "z-velocity": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-3},
                "vf-phase-2": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-3},
                "k": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-3},
                "epsilon": {"monitor": True, "check_convergence": True, "absolute_criteria": 1e-3},
            }
        }
    )
    solver.settings.solution.initialization.set_state(
        {
            "initialization_type": "hybrid",
            "reference_frame": "relative",
            "patch": {"vof_smooth_options": {"patch_reconstructed_interface": False}},
        }
    )


def apply_dpm_guard(solver: Any) -> dict[str, Any]:
    dpm = solver.settings.setup.models.discrete_phase
    state = state_or_empty(dpm, "DPM guard")
    interaction = nested(state, "general_settings", "interaction", "enabled")
    try:
        dpm.general_settings.interaction.enabled = False
    except Exception as exc:
        print(f"DPM interaction setter: unavailable ({exc})", flush=True)
    after = state_or_empty(dpm, "DPM guard readback")
    injections = after.get("injections", {})
    names = sorted(str(name) for name in injections) if isinstance(injections, Mapping) else []
    if names:
        raise RuntimeError(f"03A requires no active DPM injections, found {names}")
    return {"interaction_before": interaction, "interaction_after": nested(after, "general_settings", "interaction", "enabled"), "injection_names": names}


def capture_interaction(solver: Any) -> dict[str, Any]:
    mp = solver.settings.setup.models.multiphase
    result: dict[str, Any] = {"multiphase_state": state_or_empty(mp, "Mixture interaction parent")}
    unresolved: list[str] = []
    for attr in ("phase_interaction", "vof_parameters", "advanced_formulation", "liquid_surface_tension", "bubble_number_density"):
        try:
            obj = getattr(mp, attr)
            entry: dict[str, Any] = {"state": safe_get_state(obj, attr)}
            try:
                entry["child_names"] = list(obj.child_names)
            except Exception as exc:
                entry["child_names_error"] = f"{type(exc).__name__}: {exc}"
            result[attr] = entry
            if isinstance(entry["state"], Mapping) and "_capture_error" in entry["state"]:
                unresolved.append(attr)
        except Exception as exc:
            result[attr] = {"error": f"{type(exc).__name__}: {exc}"}
            unresolved.append(attr)
    # These are the exact fields that the target requires to be positively
    # read back if the current Fluent model tree exposes them.
    phase_interaction = result.get("phase_interaction", {})
    phase_state = phase_interaction.get("state", {}) if isinstance(phase_interaction, Mapping) else {}
    surface_entry = result.get("liquid_surface_tension", {})
    surface_state = surface_entry.get("state", {}) if isinstance(surface_entry, Mapping) else {}
    surface_json = json.dumps(surface_state, default=str).lower()
    result["required_field_status"] = {
        "secondary_diameter": "exposed" if "diameter" in json.dumps(phase_state, default=str).lower() else "not-exposed",
        "slip_relation": "exposed" if "slip" in json.dumps(phase_state, default=str).lower() else "not-exposed",
        "drag_interfacial_options": "exposed" if any(token in json.dumps(phase_state, default=str).lower() for token in ("drag", "interfacial")) else "not-exposed",
        "surface_tension": "exposed" if "_capture_error" not in surface_json and "surface" in surface_json else "not-exposed-or-inactive",
    }
    result["readback_status"] = "READ_BACK" if not unresolved else "MODEL_TREE_LIMITATION"
    result["unresolved_branches"] = unresolved
    return result


def compact_contract(solver: Any, zones: Mapping[str, str], dpm_guard: dict[str, Any]) -> dict[str, Any]:
    models = state_or_empty(solver.settings.setup.models, "model contract")
    general = state_or_empty(solver.settings.setup.general, "general contract")
    materials = state_or_empty(solver.settings.setup.materials.fluid, "material contract")
    boundaries = state_or_empty(solver.settings.setup.boundary_conditions, "boundary contract")
    methods = state_or_empty(solver.settings.solution.methods, "methods contract")
    controls = state_or_empty(solver.settings.solution.controls, "controls contract")
    initialization = state_or_empty(solver.settings.solution.initialization, "initialization contract")

    def material_value(name: str, field: str) -> Any:
        return nested(materials, name, field, "value")

    def inlet_contract(name: str) -> dict[str, Any]:
        state = nested(boundaries, "velocity_inlet", name) or {}
        return {
            "initial_gauge_pressure": nested(state, "phase", "mixture", "momentum", "initial_gauge_pressure", "value")
            or nested(state, "phase", "mixture", "momentum", "supersonic_gauge_pressure", "value"),
            "velocity": get_velocity(state, "phase-2"),
            "volume_fraction": nested(state, "phase", "phase-2", "multiphase", "volume_fraction", "value"),
            "turbulence_specification": nested(state, "phase", "mixture", "turbulence", "turbulence_specification"),
            "turbulent_intensity": nested(state, "phase", "mixture", "turbulence", "turbulent_intensity"),
            "hydraulic_diameter": nested(state, "phase", "mixture", "turbulence", "hydraulic_diameter"),
        }

    def outlet_contract(name: str) -> dict[str, Any]:
        state = nested(boundaries, "pressure_outlet", name) or {}
        return {
            "gauge_pressure": nested(state, "phase", "mixture", "momentum", "gauge_pressure", "value"),
            "backflow_direction": nested(state, "phase", "mixture", "momentum", "backflow_dir_spec_method"),
            "backflow_pressure": nested(state, "phase", "mixture", "momentum", "backflow_pressure_spec"),
            "backflow_volume_fraction": nested(state, "phase", "phase-2", "multiphase", "backflow_volume_fraction", "value"),
            "turbulent_intensity": nested(state, "phase", "mixture", "turbulence", "backflow_turbulent_intensity"),
            "hydraulic_diameter": nested(state, "phase", "mixture", "turbulence", "backflow_hydraulic_diameter"),
        }

    return {
        "zones": dict(zones),
        "general": {
            "solver_type": nested(general, "solver", "type"),
            "solver_time": nested(general, "solver", "time"),
            "velocity_formulation": nested(general, "solver", "velocity_formulation"),
            "gravity": nested(general, "operating_conditions", "gravity"),
            "operating_pressure": nested(general, "operating_conditions", "operating_pressure"),
            "operating_density_method": nested(general, "operating_conditions", "operating_density", "method"),
            "operating_temperature": nested(general, "operating_conditions", "operating_temperature"),
        },
        "models": {
            "multiphase": nested(models, "multiphase", "model") or nested(models, "multiphase", "models"),
            "phase_count": nested(models, "multiphase", "number_of_phases")
            or (2 if isinstance(nested(models, "multiphase", "phases"), Mapping) and all(
                phase_name in nested(models, "multiphase", "phases") for phase_name in ("phase-1", "phase-2")
            ) else None),
            "phase_materials": {
                "phase-1": nested(models, "multiphase", "phases", "phase-1", "material") or nested(models, "species", "model", "phase_material", "phase-1"),
                "phase-2": nested(models, "multiphase", "phases", "phase-2", "material") or nested(models, "species", "model", "phase_material", "phase-2"),
            },
            "energy": nested(models, "energy", "enabled"),
            "viscous": nested(models, "viscous", "model"),
            "k_epsilon": nested(models, "viscous", "k_epsilon_model"),
            "differential_viscosity": nested(models, "viscous", "rng_options", "differential_viscosity_model") or nested(models, "viscous", "rng", "differential_viscosity_model"),
            "swirl": nested(models, "viscous", "rng_options", "swirl_dominated_flow") or nested(models, "viscous", "rng", "swirl_dominated_flow"),
            "wall_treatment": nested(models, "viscous", "near_wall_treatment", "wall_treatment"),
        },
        "materials": {
            "water-vapor-at-psep": {"density": material_value("water-vapor-at-psep", "density"), "viscosity": material_value("water-vapor-at-psep", "viscosity")},
            "water-liquid-at-psep": {"density": material_value("water-liquid-at-psep", "density"), "viscosity": material_value("water-liquid-at-psep", "viscosity")},
        },
        "boundaries": {
            "liquid_inlet": inlet_contract(zones["liquid_inlet"]),
            "steam_inlet": inlet_contract(zones["steam_inlet"]),
            "steam_outlet": outlet_contract(zones["steam_outlet"]),
            "brine_outlet": outlet_contract(zones["brine_outlet"]),
        },
        "methods": {
            "flow_scheme": nested(methods, "p_v_coupling", "flow_scheme"),
            "gradient_scheme": nested(methods, "gradient_scheme") or nested(methods, "spatial_discretization", "gradient_scheme"),
            "pressure": nested(methods, "discretization_scheme", "pressure") or nested(methods, "spatial_discretization", "discretization_scheme", "pressure"),
            "mom": nested(methods, "discretization_scheme", "mom") or nested(methods, "spatial_discretization", "discretization_scheme", "mom"),
            "mp": nested(methods, "discretization_scheme", "mp") or nested(methods, "spatial_discretization", "discretization_scheme", "mp"),
            "k": nested(methods, "discretization_scheme", "k") or nested(methods, "spatial_discretization", "discretization_scheme", "k"),
            "epsilon": nested(methods, "discretization_scheme", "epsilon") or nested(methods, "spatial_discretization", "discretization_scheme", "epsilon"),
            "pseudo_time": nested(methods, "pseudo_time_method"),
            "high_order_term_relaxation": nested(methods, "high_order_term_relaxation", "enable"),
        },
        "controls": {
            "under_relaxation": nested(controls, "under_relaxation"),
        },
        "initialization": {
            "initialization_type": nested(initialization, "initialization_type"),
            "reference_frame": nested(initialization, "reference_frame"),
            "patch_reconstructed_interface": nested(initialization, "patch", "vof_smooth_options", "patch_reconstructed_interface"),
        },
        "dpm": dpm_guard,
    }


def validate_contract(contract: Mapping[str, Any]) -> None:
    models = contract["models"]
    if models["multiphase"] != "mixture" or models["energy"] is not False or models["viscous"] != "k-epsilon" or models["k_epsilon"] != "rng":
        raise RuntimeError(f"Carrier model contract mismatch: {models}")
    if models["phase_materials"] != {"phase-1": "water-vapor-at-psep", "phase-2": "water-liquid-at-psep"}:
        raise RuntimeError(f"Phase material contract mismatch: {models['phase_materials']}")
    if contract["general"]["solver_type"] != "pressure-based" or contract["general"]["solver_time"] != "steady":
        raise RuntimeError(f"General solver contract mismatch: {contract['general']}")
    if contract["general"]["operating_density_method"] != "mixture-averaged":
        raise RuntimeError(f"Operating-density contract mismatch: {contract['general']}")
    if contract["methods"]["flow_scheme"] != "SIMPLE" or contract["methods"]["gradient_scheme"] != "green-gauss-node-based":
        raise RuntimeError(f"Solution method contract mismatch: {contract['methods']}")
    if contract["methods"]["high_order_term_relaxation"] not in (False, None):
        raise RuntimeError("Rhie-Chow high-order-term relaxation is not disabled")
    if contract["initialization"]["initialization_type"] != "hybrid" or contract["initialization"]["patch_reconstructed_interface"] not in (False, None):
        raise RuntimeError(f"Initialization contract mismatch: {contract['initialization']}")
    if contract["dpm"].get("injection_names"):
        raise RuntimeError(f"DPM injections are active: {contract['dpm']}")
    for name in ("water-vapor-at-psep", "water-liquid-at-psep"):
        if contract["materials"][name]["density"] is None or contract["materials"][name]["viscosity"] is None:
            raise RuntimeError(f"Material readback incomplete for {name}: {contract['materials'][name]}")


def normalized_contract(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): normalized_contract(v) for k, v in value.items()}
    if isinstance(value, list):
        return [normalized_contract(v) for v in value]
    if isinstance(value, float):
        return round(value, 10)
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Print the traced build plan without connecting to Fluent")
    mode.add_argument("--apply", action="store_true", help="Build, save, reload, and verify the case-only artifact")
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--mesh", default=DEFAULT_MESH)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--output-case", default="", help="Explicit unique remote .cas.h5 output path")
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--snapshot-json", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if PureWindowsPath(args.mesh).name != EXACT_MESH_NAME:
        raise ValueError(f"03A is locked to {EXACT_MESH_NAME}; got {args.mesh}")
    output_case = args.output_case or str(PureWindowsPath(args.remote_dir) / f"03A-08b-parity-full-geometry-steady-preinit-{args.stamp}.cas.h5")
    plan = {
        "setup_id": "03A",
        "purpose": "08b/audited-Purnanto carrier on current full geometry with brine outlet",
        "mesh": args.mesh,
        "output_case": output_case,
        "source_authority": SOURCE_AUTHORITY,
        "intentional_difference": "03A explicitly uses split pure-phase Velocity Inlets; saved 08b artifact readback used Mass-Flow Inlets.",
        "case_only_policy": "No initialization, iteration, DPM injection, EWF operation, data write, or solver shutdown.",
    }
    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not solver.is_active():
        raise RuntimeError("Fluent session is not active")
    if not remote_file_exists(solver, args.mesh):
        raise FileNotFoundError(f"Target mesh is not visible on Fluent host: {args.mesh}")
    if remote_file_exists(solver, output_case):
        raise FileExistsError(f"Refusing to overwrite existing case: {output_case}")

    load_target_mesh(solver, args.mesh)
    try:
        solver.tui.mesh.check()
        mesh_check = "Fluent mesh check issued; counts/quality remain in the remote transcript"
    except Exception as exc:
        mesh_check = f"mesh check unavailable: {type(exc).__name__}: {exc}"
    zones, target_boundaries, target_cell_zones = resolve_zones(solver)

    set_general(solver)
    set_materials(solver)
    set_models(solver)
    operating_condition_readback = set_operating_conditions(solver)
    set_phase_materials(solver)
    apply_boundaries(solver, zones)
    apply_solution(solver)
    dpm_guard = apply_dpm_guard(solver)
    interaction = capture_interaction(solver)
    contract = compact_contract(solver, zones, dpm_guard)
    validate_contract(contract)

    write_case_only(solver, output_case, "Write 03A case-only pre-initialization artifact")
    if not remote_file_exists(solver, output_case):
        raise RuntimeError(f"Fluent did not expose the written case: {output_case}")
    load_case_only(solver, output_case, label="Reload and verify 03A case-only artifact")
    reloaded_dpm_guard = apply_dpm_guard(solver)
    reloaded = compact_contract(solver, zones, reloaded_dpm_guard)
    validate_contract(reloaded)
    if normalized_contract(reloaded) != normalized_contract(contract):
        raise RuntimeError("Reloaded 03A contract differs from the pre-save contract")

    payload = {
        **plan,
        "status": "CASE_ONLY_VERIFIED",
        "server_id": args.server_id,
        "fluent_version": str(solver.get_fluent_version()),
        "mesh_check": mesh_check,
        "boundary_topology_after_mesh": target_boundaries,
        "cell_zone_topology_after_mesh": target_cell_zones,
        "zones": zones,
        "operating_condition_readback": operating_condition_readback,
        "authority_requested_readback": {
            "authority": {
                "carrier": "00a audited Purnanto / surviving 1520 machine extract",
                "split_inlets": "07/08b project representation",
                "brine_outlet": "03A requested 1.120 MPa pressure outlet",
            },
            "requested": contract,
            "readback": reloaded,
        },
        "mixture_interaction_readback": interaction,
        "mesh_geometry_gate": {
            "status": "PENDING_NATIVE_PREFLIGHT",
            "note": "Actual boundary areas, wetted perimeters, hydraulic diameters, node/cell counts, and quality metrics must be recorded from this loaded mesh before any run; provisional Dh values were used where the target provides them.",
            "expected_cell_count": 231376,
            "expected_inlet_areas_m2": {"liquid": 0.0048896, "steam": 0.5192864, "total": 0.524176},
        },
        "post_reload": {"case_file": output_case, "status": "FULL_PATH_RELOAD_VERIFIED"},
    }
    snapshot = Path(args.snapshot_json).expanduser().resolve()
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    print(f"snapshot_json: {snapshot}", flush=True)
    print("CASE_ONLY_VERIFIED; no initialization, iteration, data write, DPM injection, EWF action, or solver shutdown was issued.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

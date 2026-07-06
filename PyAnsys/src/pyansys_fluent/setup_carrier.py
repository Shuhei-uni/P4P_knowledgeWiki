#!/usr/bin/env python3
"""Carrier-field setup helpers shared by setup07 and setup09a."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import Any

from pyansys_fluent.common import safe_get_state, try_action
from pyansys_fluent.setup_common import (
    deep_replace_names,
    load_json,
    names_from_boundary_state,
    print_header,
)
from pyansys_fluent.setup_discovery import BOUNDARY_TYPE_ORDER, build_name_replacements_from_fallback


ARCHIVE_DIR = (
    Path(__file__).resolve().parents[2]
    / "cases"
    / "actual_setup_archives"
    / "07-pure-phase-split-actual-area-live-fff-1-2"
)
FALLBACK_SETTINGS = ARCHIVE_DIR / "settings_snapshot.json"


def load_setup07_fallback_settings() -> dict[str, Any]:
    return load_json(FALLBACK_SETTINGS)


def apply_branch_with_fallback(
    label: str,
    intended_func,
    fallback_func,
) -> None:
    print_header(label)
    if intended_func():
        print(f"{label}: intended settings applied")
        return
    print(f"{label}: intended settings failed, applying fallback")
    if not fallback_func():
        raise RuntimeError(f"{label} failed for both intended and fallback settings")


def ensure_material_object(material_branch, material_name: str) -> None:
    try:
        existing = set(material_branch.get_object_names())
    except Exception:
        existing = set()
    if material_name not in existing:
        material_branch.create(name=material_name)


def apply_material_states(solver, materials_state: Mapping[str, Any]) -> bool:
    materials = solver.settings.setup.materials
    ok = True
    for category in ("fluid", "solid", "inert_particle"):
        category_state = materials_state.get(category, {})
        if not isinstance(category_state, Mapping):
            continue
        category_obj = getattr(materials, category, None)
        if category_obj is None:
            continue
        for material_name, material_state in category_state.items():
            if not isinstance(material_state, Mapping):
                continue
            ok &= try_action(
                f"material_prepare_{category}.{material_name}",
                lambda name=material_name, obj=category_obj: ensure_material_object(obj, name),
            )
            ok &= try_action(
                f"material_apply_{category}.{material_name}",
                lambda name=material_name, state=material_state, obj=category_obj: obj[name].set_state(state),
            )
    return ok


def apply_boundary_states(solver, boundary_state: Mapping[str, Any]) -> bool:
    bc = solver.settings.setup.boundary_conditions
    current_boundary_state = safe_get_state(bc, "boundary_conditions_current")
    ok = True
    for boundary_type in BOUNDARY_TYPE_ORDER:
        zone_map = boundary_state.get(boundary_type, {})
        if not isinstance(zone_map, Mapping):
            continue
        available_names = set(names_from_boundary_state(current_boundary_state, boundary_type))
        branch = getattr(bc, boundary_type, None)
        if branch is None:
            continue
        for zone_name, zone_state in zone_map.items():
            if zone_name == "settings" or not isinstance(zone_state, Mapping):
                continue
            if zone_name not in available_names:
                continue
            payload = deepcopy(zone_state)
            payload["name"] = zone_name
            phase_map = payload.get("phase")
            if isinstance(phase_map, Mapping):
                for phase_state in phase_map.values():
                    if isinstance(phase_state, Mapping):
                        phase_state.pop("dpm", None)
            ok &= try_action(
                f"apply_{boundary_type}_{zone_name}",
                lambda name=zone_name, state=payload, obj=branch: obj[name].set_state(state),
            )
    return ok


def build_intended_materials() -> dict[str, Any]:
    return {
        "fluid": {
            "water-liquid": {
                "name": "water-liquid",
                "chemical_formula": "",
                "density": {"option": "constant", "value": 881.77},
                "viscosity": {"option": "constant", "value": 145.96e-6},
            },
            "water-vapor": {
                "name": "water-vapor",
                "chemical_formula": "",
                "density": {"option": "constant", "value": 5.73},
                "viscosity": {"option": "constant", "value": 15.188e-6},
            },
        }
    }


def build_intended_boundary_state(role_map: Mapping[str, str]) -> dict[str, Any]:
    liquid_inlet = role_map["liquid_inlet"]
    steam_inlet = role_map["steam_inlet"]
    outlet = role_map["outlet"]
    wall = role_map["wall"]
    bottom = role_map["bottom"]
    return {
        "velocity_inlet": {
            liquid_inlet: {
                "name": liquid_inlet,
                "phase": {
                    "mixture": {
                        "momentum": {"initial_gauge_pressure": {"option": "value", "value": 1140000}},
                        "turbulence": {
                            "turbulence_specification": "Intensity and Hydraulic Diameter",
                            "turbulent_intensity": 0.0210999999,
                            "hydraulic_diameter": 0.01338,
                        },
                    },
                    "phase-1": {
                        "momentum": {
                            "velocity_specification_method": "Magnitude, Normal to Boundary",
                            "reference_frame": "Absolute",
                            "velocity": {"option": "value", "value": 27.118},
                        },
                    },
                    "phase-2": {
                        "momentum": {
                            "velocity_specification_method": "Magnitude, Normal to Boundary",
                            "reference_frame": "Absolute",
                            "velocity": {"option": "value", "value": 27.118},
                        },
                        "multiphase": {"volume_fraction": {"option": "value", "value": 1.0}},
                    },
                },
            },
            steam_inlet: {
                "name": steam_inlet,
                "phase": {
                    "mixture": {
                        "momentum": {"initial_gauge_pressure": {"option": "value", "value": 1140000}},
                        "turbulence": {
                            "turbulence_specification": "Intensity and Hydraulic Diameter",
                            "turbulent_intensity": 0.0210999999,
                            "hydraulic_diameter": 0.72061,
                        },
                    },
                    "phase-1": {
                        "momentum": {
                            "velocity_specification_method": "Magnitude, Normal to Boundary",
                            "reference_frame": "Absolute",
                            "velocity": {"option": "value", "value": 27.118},
                        },
                    },
                    "phase-2": {
                        "momentum": {
                            "velocity_specification_method": "Magnitude, Normal to Boundary",
                            "reference_frame": "Absolute",
                            "velocity": {"option": "value", "value": 27.118},
                        },
                        "multiphase": {"volume_fraction": {"option": "value", "value": 0.0}},
                    },
                },
            },
        },
        "pressure_outlet": {
            outlet: {
                "name": outlet,
                "phase": {
                    "mixture": {
                        "momentum": {
                            "gauge_pressure": {"option": "value", "value": 1120000},
                            "pressure_profile_multiplier": 1,
                            "backflow_dir_spec_method": "Normal to Boundary",
                            "backflow_pressure_spec": "Total Pressure",
                            "radial_equ_pressure_distribution": False,
                        },
                        "turbulence": {
                            "turbulence_specification": "Intensity and Hydraulic Diameter",
                            "backflow_turbulent_intensity": 0.0215249995,
                            "backflow_hydraulic_diameter": 0.724,
                        },
                    },
                    "phase-2": {
                        "multiphase": {
                            "volume_frac_spec_method": "Backflow Volume Fraction",
                            "backflow_volume_fraction": {"option": "value", "value": 0.0},
                        }
                    },
                },
            }
        },
        "wall": {
            **{
                name: {
                    "name": name,
                    "phase": {
                        "mixture": {
                            "momentum": {"wall_motion": "Stationary Wall", "shear_condition": "No Slip"},
                            "turbulence": {
                                "roughness_height": {"option": "value", "value": 0.0},
                                "roughness_const": {"option": "value", "value": 0.5},
                            },
                        }
                    },
                }
                for name in {wall, bottom}
            },
        },
    }


def apply_carrier_general(solver) -> bool:
    general = solver.settings.setup.general
    ok = True
    ok &= try_action("set_solver_type", lambda: setattr(general.solver, "type", "pressure-based"))
    ok &= try_action("set_solver_time", lambda: setattr(general.solver, "time", "steady"))
    ok &= try_action("set_velocity_formulation", lambda: setattr(general.solver, "velocity_formulation", "absolute"))
    ok &= try_action("set_gravity_enable", lambda: setattr(general.operating_conditions.gravity, "enable", True))
    ok &= try_action("set_gravity_components", lambda: setattr(general.operating_conditions.gravity, "components", [0.0, -9.81, 0.0]))
    ok &= try_action("set_operating_pressure", lambda: setattr(general.operating_conditions, "operating_pressure", 0))
    ok &= try_action(
        "set_operating_density_method",
        lambda: setattr(general.operating_conditions.operating_density, "method", "mixture-averaged"),
    )
    ok &= try_action(
        "set_operating_temperature",
        lambda: general.operating_conditions.operating_temperature.set_state(298.15),
    )
    ok &= try_action(
        "set_reference_pressure_method",
        lambda: setattr(
            general.operating_conditions,
            "reference_pressure_method",
            "Connected and disconnected fluid zones",
        ),
    )
    return ok


def apply_carrier_operating_conditions_state(solver, operating_conditions_state: Mapping[str, Any]) -> bool:
    """Replay the archived operating conditions payload as a single state update."""
    if not isinstance(operating_conditions_state, Mapping):
        return False
    general = solver.settings.setup.general
    return try_action(
        "apply_live_operating_conditions_state",
        lambda: general.operating_conditions.set_state(dict(operating_conditions_state)),
    )


def apply_carrier_solution_monitor(solver, monitor_state: Mapping[str, Any]) -> bool:
    """Replay the residual monitor state with narrower, version-tolerant setters."""
    monitor = solver.settings.solution.monitor
    residual = monitor.residual
    ok = True

    if not isinstance(monitor_state, Mapping):
        return False

    residual_state = monitor_state.get("residual")
    if not isinstance(residual_state, Mapping):
        return False

    ok &= try_action("apply_live_solution_monitor_residual", lambda: residual.set_state(residual_state))

    options_state = residual_state.get("options")
    if isinstance(options_state, Mapping):
        ok &= try_action(
            "apply_live_solution_monitor_residual_options",
            lambda: residual.options.set_state(options_state),
        )

    equations_state = residual_state.get("equations")
    if isinstance(equations_state, Mapping):
        for equation_name, equation_state in equations_state.items():
            if not isinstance(equation_state, Mapping):
                continue
            equation_obj = getattr(residual.equations, equation_name, None)
            if equation_obj is None:
                continue
            ok &= try_action(
                f"apply_live_solution_monitor_residual_{equation_name}",
                lambda obj=equation_obj, state=equation_state: obj.set_state(state),
            )

    axes_state = residual_state.get("axes")
    if isinstance(axes_state, Mapping):
        ok &= try_action(
            "apply_live_solution_monitor_residual_axes",
            lambda: residual.axes.set_state(axes_state),
        )

    return ok


def apply_carrier_solution_monitor_continuity(solver, monitor_state: Mapping[str, Any]) -> bool:
    """Restore the archived continuity residual threshold with a direct leaf setter."""
    if not isinstance(monitor_state, Mapping):
        return False

    residual_state = monitor_state.get("residual")
    if not isinstance(residual_state, Mapping):
        return False

    equations_state = residual_state.get("equations")
    if not isinstance(equations_state, Mapping):
        return False

    continuity_state = equations_state.get("continuity")
    if not isinstance(continuity_state, Mapping):
        return False

    residual = solver.settings.solution.monitor.residual
    return try_action(
        "apply_live_solution_monitor_continuity",
        lambda: residual.equations.continuity.set_state(dict(continuity_state)),
    )


def apply_carrier_models(solver) -> bool:
    models = solver.settings.setup.models
    ok = True
    multiphase = models.multiphase
    if hasattr(multiphase, "model"):
        ok &= try_action("set_multiphase_model", lambda: setattr(multiphase, "model", "mixture"))
    else:
        ok &= try_action("set_multiphase_models", lambda: setattr(multiphase, "models", "mixture"))

    multiphase_state = safe_get_state(multiphase, "multiphase_after_model")
    desired_phase_count_already_present = False
    if isinstance(multiphase_state, Mapping):
        phase_count_state = multiphase_state.get("number_of_phases")
        if isinstance(phase_count_state, Mapping):
            desired_phase_count_already_present = phase_count_state.get("number_of_eulerian_phases") == 2
        elif phase_count_state == 2:
            desired_phase_count_already_present = True

    if desired_phase_count_already_present:
        print("set_number_of_phases: SKIPPED -> model activation already exposed two phases")
    else:
        if hasattr(multiphase.number_of_phases, "number_of_eulerian_phases"):
            ok &= try_action(
                "set_number_of_phases",
                lambda: setattr(multiphase.number_of_phases, "number_of_eulerian_phases", 2),
            )
        else:
            ok &= try_action("set_number_of_phases_scalar", lambda: setattr(multiphase, "number_of_phases", 2))
    ok &= try_action("set_energy_off", lambda: setattr(models.energy, "enabled", False))
    ok &= try_action("set_viscous_model", lambda: setattr(models.viscous, "model", "k-epsilon"))
    ok &= try_action("set_k_epsilon_rng", lambda: setattr(models.viscous, "k_epsilon_model", "rng"))
    ok &= try_action(
        "set_rng_differential_viscosity",
        lambda: setattr(models.viscous.rng_options, "differential_viscosity_model", True),
    )
    ok &= try_action(
        "set_rng_swirl_dominated_flow",
        lambda: setattr(models.viscous.rng_options, "swirl_dominated_flow", True),
    )
    ok &= try_action(
        "set_standard_wall_function",
        lambda: setattr(models.viscous.near_wall_treatment, "wall_treatment", "standard-wall-fn"),
    )
    ok &= try_action(
        "disable_discrete_phase_interaction",
        lambda: setattr(models.discrete_phase.general_settings.interaction, "enabled", False),
    )
    return ok


def apply_carrier_phase_materials(solver) -> bool:
    ok = True
    commands = [
        '/define/phases/set-domain-properties/phase-domains/phase-1/material yes water-vapor',
        '/define/phases/set-domain-properties/phase-domains/phase-2/material yes water-liquid',
    ]
    for index, command in enumerate(commands, start=1):
        ok &= try_action(
            f"apply_phase_material_mapping_tui_{index}",
            lambda cmd=command: solver.scheme.exec((f'(ti-menu-load-string "{cmd}")',)),
        )
    try:
        state = solver.settings.setup.models.species.model.get_state()
        print(f"phase_material_state: {state}")
    except Exception as exc:
        print(f"phase_material_state: FAILED -> {exc}")
    return ok


def apply_surface_tension_best_effort(solver) -> bool:
    ok = True
    commands = [
        (
            "set_surface_tension_coeff_phase_pair_constant",
            "/define/phases/set-domain-properties/interaction-domain/forces/surface-tension/"
            "sfc-tension-coeff yes constant 0.0411",
        ),
        (
            "enable_surface_tension_modeling",
            "/define/phases/set-domain-properties/interaction-domain/forces/surface-tension/"
            "sfc-modeling yes",
        ),
        (
            "set_surface_tension_model_type_csf",
            "/define/phases/set-domain-properties/interaction-domain/forces/surface-tension/"
            "sfc-model-type continuum-surface-force",
        ),
    ]
    for label, command in commands:
        ok &= try_action(label, lambda cmd=command: solver.scheme.exec((f'(ti-menu-load-string "{cmd}")',)))
    return ok


def disable_dpm_after_setup(solver) -> bool:
    models = solver.settings.setup.models
    ok = True
    ok &= try_action(
        "disable_discrete_phase_interaction_postsetup",
        lambda: setattr(models.discrete_phase.general_settings.interaction, "enabled", False),
    )
    ok &= try_action(
        "set_dpm_contour_plotting_none",
        lambda: setattr(models.discrete_phase.general_settings, "contour_plotting", "none"),
    )
    return ok


def apply_carrier_cell_zone_conditions(solver) -> bool:
    zone_state = {
        "fluid": {
            "fluid": {
                "name": "fluid",
                "phase": {
                    "mixture": {
                        "general": {"laminar": False},
                        "porous_zone": {"porous": False},
                        "fan_zone": {"fan_zone": False},
                        "sources": {"enable": False},
                        "fixed_values": {"enable": False},
                    }
                },
            }
        }
    }
    return try_action(
        "apply_intended_cell_zone_conditions",
        lambda: solver.settings.setup.cell_zone_conditions.set_state(zone_state),
    )


def apply_carrier_solution_methods(solver) -> bool:
    methods = solver.settings.solution.methods
    state = {
        "p_v_coupling": {"flow_scheme": "SIMPLE", "solve_n_phase": False},
        "gradient_scheme": "green-gauss-node-based",
        "discretization_scheme": {
            "pressure": "presto!",
            "mom": "second-order-upwind",
            "k": "second-order-upwind",
            "epsilon": "second-order-upwind",
            "mp": "quick",
        },
        "pseudo_time_method": {"formulation": {"coupled_solver": "off"}},
    }
    return try_action("apply_intended_solution_methods", lambda: methods.set_state(state))


def apply_carrier_solution_controls(solver) -> bool:
    controls = solver.settings.solution.controls
    state = {
        "under_relaxation": {
            "body-force": 1.0,
            "density": 1.0,
            "drift": 0.1,
            "epsilon": 0.8,
            "k": 0.8,
            "mp": 0.4,
            "turb-viscosity": 1.0,
        },
        "equations": {"drift": True, "flow": True, "ke": True, "mp": True},
        "limits": {
            "min_pressure": 1,
            "max_pressure": 5.0e10,
            "min_tke": 1e-14,
            "min_epsilon": 1e-20,
            "max_turb_visc_ratio": 100000.0,
            "min_vol_frac_for_matrix_sol": 1e-08,
        },
    }
    return try_action("apply_intended_solution_controls", lambda: controls.set_state(state))


def apply_carrier_initialization_settings(solver) -> bool:
    init = solver.settings.solution.initialization
    ok = True
    ok &= try_action("set_initialization_type", lambda: setattr(init, "initialization_type", "hybrid"))
    ok &= try_action("set_initialization_reference_frame", lambda: setattr(init, "reference_frame", "relative"))
    return ok


def prepare_setup07_fallback_payloads(
    fallback_settings: Mapping[str, Any],
    target_boundary_state: Mapping[str, Any],
) -> dict[str, Any]:
    fallback_boundary = fallback_settings["setup"]["boundary_conditions"]
    fallback_cell_zones = fallback_settings["setup"]["cell_zone_conditions"]
    replacements = build_name_replacements_from_fallback(fallback_boundary, target_boundary_state)
    return {
        "fallback_general": fallback_settings["setup"]["general"],
        "fallback_models": fallback_settings["setup"]["models"],
        "fallback_materials": fallback_settings["setup"]["materials"],
        "fallback_boundary": deep_replace_names(fallback_boundary, replacements),
        "fallback_cell_zones": deep_replace_names(fallback_cell_zones, {"fluid": "fluid"}),
        "fallback_solution": fallback_settings["solution"],
        "fallback_initialization": fallback_settings["solution_initialization_detail"]["_state"],
    }

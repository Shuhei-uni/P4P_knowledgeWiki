#!/usr/bin/env python3
"""Rebuild intended setup 07 on a new mesh, with live-archive fallback.

Strategy:
1. Connect to the already-running Fluent gRPC session.
2. Read a target mesh with matching logical named selections.
3. Apply the intended inherited setup for setup 07.
4. If an intended settings block fails, fall back to the archived actual-live block.
5. Hybrid initialize, iterate, checkpoint, and write final case/data.

This script prioritizes getting a runnable case over perfect parity.

Use `--server-id` to choose which configured Fluent gRPC server to use:
- `1` -> `FLUENT_IP` / `FLUENT_PORT` / `FLUENT_PASSWORD`
- `2` -> `FLUENT_IP2` / `FLUENT_PORT2` / `FLUENT_PASSWORD2`
- `3` -> `FLUENT_IP3` / `FLUENT_PORT3` / `FLUENT_PASSWORD3`
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path, PureWindowsPath
from typing import Any

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from pyansys_fluent.common import remote_chdir, safe_get_state, try_action  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import (  # noqa: E402
    deep_replace_names,
    detect_role_name,
    load_json,
    names_from_boundary_state,
    print_header,
    require_remote_input,
    summarize_boundary_state,
)


ARCHIVE_DIR = (
    Path(__file__).resolve().parents[2]
    / "cases"
    / "actual_setup_archives"
    / "07-pure-phase-split-actual-area-live-fff-1-2"
)
FALLBACK_SETTINGS = ARCHIVE_DIR / "settings_snapshot.json"

ROLE_ALIASES: dict[str, tuple[str, ...]] = {
    "liquid_inlet": (
        "inlet_liquid_outer",
        "liquidinlet",
        "liquid_inlet",
        "liquid inlet",
        "liquid",
    ),
    "steam_inlet": (
        "inlet_steam_inner",
        "steaminlet",
        "steam_inlet",
        "steam inlet",
        "steam",
    ),
    "outlet": (
        "steamoutlet",
        "steam_outlet",
        "steam outlet",
        "outlet",
    ),
    "wall": (
        "wall-fluid",
        "wallfluid",
        "wall",
    ),
    "bottom": ("bottom",),
}

BOUNDARY_TYPE_ORDER = (
    "velocity_inlet",
    "mass_flow_inlet",
    "pressure_outlet",
    "wall",
    "interior",
)


class RunInterrupted(Exception):
    def __init__(self, completed_iterations: int):
        super().__init__(f"Run interrupted after approximately {completed_iterations} iterations")
        self.completed_iterations = completed_iterations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Apply intended setup 07 to a target mesh, fall back to archived "
            "actual settings when necessary, then initialize and run."
        )
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured Fluent server id to use. Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3.",
    )
    parser.add_argument("--target-mesh", default="", help="Remote target mesh file.")
    parser.add_argument("--output-case", required=True, help="Remote final case file.")
    parser.add_argument("--output-data", required=True, help="Remote final data file.")
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Iterations after initialization. Default: 100.",
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=100,
        help="Console progress interval. Default: 100.",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=1000,
        help="Overwrite a rolling autosave case/data checkpoint every N iterations. Default: 1000.",
    )
    parser.add_argument(
        "--initialized-case",
        default="",
        help="Optional remote case file to write immediately after initialization.",
    )
    parser.add_argument(
        "--initialized-data",
        default="",
        help="Optional remote data file to write immediately after initialization.",
    )
    parser.add_argument(
        "--skip-run",
        action="store_true",
        help="Apply setup and initialize, but do not iterate.",
    )
    parser.add_argument(
        "--resume-case",
        default="",
        help="Optional remote case file to resume from instead of rebuilding from mesh.",
    )
    parser.add_argument(
        "--resume-data",
        default="",
        help="Optional remote data file to resume from instead of rebuilding from mesh.",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    has_resume = bool(args.resume_case or args.resume_data)
    if has_resume and not (args.resume_case and args.resume_data):
        raise ValueError("Both --resume-case and --resume-data are required for resume mode")
    if not has_resume and not args.target_mesh:
        raise ValueError("--target-mesh is required unless --resume-case/--resume-data are provided")


def build_target_role_map(boundary_state: Mapping[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for role in ROLE_ALIASES:
        match = detect_role_name(boundary_state, ROLE_ALIASES, role)
        if not match:
            if role == "bottom":
                if "wall" in mapping:
                    mapping["bottom"] = mapping["wall"]
                    print(f"role_map[bottom] = {mapping['bottom']} (fallback to wall)")
                    continue
            raise RuntimeError(f"Could not detect target boundary for role: {role}")
        mapping[role] = match[1]
        print(f"role_map[{role}] = {match[1]}")
    return mapping


def load_fallback_settings() -> dict[str, Any]:
    return load_json(FALLBACK_SETTINGS)


def build_name_replacements_from_fallback(
    fallback_boundary_state: Mapping[str, Any],
    target_boundary_state: Mapping[str, Any],
) -> dict[str, str]:
    replacements: dict[str, str] = {"fluid": "fluid"}
    for role in ROLE_ALIASES:
        source_match = detect_role_name(fallback_boundary_state, role)
        target_match = detect_role_name(target_boundary_state, role)
        if source_match and target_match:
            replacements[source_match[1]] = target_match[1]
    return replacements


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


def convert_target_boundaries_to_intended(
    solver,
    target_boundary_state: Mapping[str, Any],
    role_map: Mapping[str, str],
) -> bool:
    bc = solver.settings.setup.boundary_conditions
    desired = {
        role_map["liquid_inlet"]: "velocity_inlet",
        role_map["steam_inlet"]: "velocity_inlet",
        role_map["outlet"]: "pressure_outlet",
        role_map["wall"]: "wall",
        role_map["bottom"]: "wall",
    }
    ok = True
    for zone_name, desired_type in desired.items():
        current_type = None
        for boundary_type, zones in target_boundary_state.items():
            if isinstance(zones, Mapping) and zone_name in zones:
                current_type = boundary_type
                break
        if current_type == desired_type:
            continue
        ok &= try_action(
            f"set_zone_type_{zone_name}",
            lambda name=zone_name, new_type=desired_type: bc.set_zone_type(
                zone_list=[name], new_type=new_type.replace("_", "-")
            ),
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


def apply_intended_general(solver) -> bool:
    general = solver.settings.setup.general
    ok = True
    ok &= try_action("set_solver_type", lambda: setattr(general.solver, "type", "pressure-based"))
    ok &= try_action("set_solver_time", lambda: setattr(general.solver, "time", "steady"))
    ok &= try_action("set_velocity_formulation", lambda: setattr(general.solver, "velocity_formulation", "absolute"))
    ok &= try_action("set_gravity_enable", lambda: setattr(general.operating_conditions.gravity, "enable", True))
    ok &= try_action("set_gravity_components", lambda: setattr(general.operating_conditions.gravity, "components", [0.0, -9.81, 0.0]))
    ok &= try_action("set_operating_pressure", lambda: setattr(general.operating_conditions, "operating_pressure", 0))
    return ok


def apply_intended_models(solver) -> bool:
    models = solver.settings.setup.models
    ok = True
    ok &= try_action("set_multiphase_model", lambda: setattr(models.multiphase, "model", "mixture"))

    multiphase_state = safe_get_state(models.multiphase, "multiphase_after_model")
    desired_phase_count_already_present = False
    if isinstance(multiphase_state, Mapping):
        phase_count_state = multiphase_state.get("number_of_phases", {})
        if isinstance(phase_count_state, Mapping):
            desired_phase_count_already_present = (
                phase_count_state.get("number_of_eulerian_phases") == 2
            )

    if desired_phase_count_already_present:
        print("set_number_of_phases: SKIPPED -> model activation already exposed two phases")
    else:
        ok &= try_action(
            "set_number_of_phases",
            lambda: setattr(models.multiphase.number_of_phases, "number_of_eulerian_phases", 2),
        )
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


def apply_intended_phase_materials(solver) -> bool:
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

    # This Fluent build does not expose the newer settings-tree phase_interaction
    # branch for the Mixture model, but the TUI surface-tension path is live.
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
        ok &= try_action(
            label,
            lambda cmd=command: solver.scheme.exec((f'(ti-menu-load-string "{cmd}")',)),
        )

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


def apply_intended_cell_zone_conditions(solver) -> bool:
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


def apply_intended_solution_methods(solver) -> bool:
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


def apply_intended_solution_controls(solver) -> bool:
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


def apply_intended_initialization(solver) -> bool:
    init = solver.settings.solution.initialization
    ok = True
    ok &= try_action("set_initialization_type", lambda: setattr(init, "initialization_type", "hybrid"))
    ok &= try_action("set_initialization_reference_frame", lambda: setattr(init, "reference_frame", "relative"))
    return ok


def initialize_target_case(solver) -> None:
    print_header("Initialize Target Case")
    if try_action("hybrid_initialize_settings_api", lambda: solver.settings.solution.initialization.hybrid_initialize()):
        return
    if try_action("hybrid_initialize_tui", lambda: solver.tui.solve.initialize.hyb_initialization()):
        return
    raise RuntimeError("Failed to initialize target case")


def load_target_mesh(solver, mesh_path: str) -> None:
    print_header("Load Target Mesh")
    require_remote_input(solver, mesh_path, "target mesh")
    remote_chdir(solver, str(PureWindowsPath(mesh_path).parent))
    if not try_action("read_target_mesh", lambda: solver.settings.file.read_mesh(file_name=mesh_path)):
        raise RuntimeError("Could not read target mesh")


def load_resume_case_data(solver, case_path: str, data_path: str) -> None:
    print_header("Load Resume Case/Data")
    require_remote_input(solver, case_path, "resume case")
    require_remote_input(solver, data_path, "resume data")
    remote_chdir(solver, str(PureWindowsPath(case_path).parent))
    if not try_action("read_resume_case", lambda: solver.settings.file.read_case(file_name=case_path)):
        raise RuntimeError("Could not read resume case")
    if not try_action("read_resume_data", lambda: solver.settings.file.read_data(file_name=data_path)):
        raise RuntimeError("Could not read resume data")


def checkpoint_paths(path_text: str, iteration: int) -> str:
    if path_text.endswith(".cas.h5"):
        return path_text[:-7] + f"-iter{iteration}.cas.h5"
    if path_text.endswith(".dat.h5"):
        return path_text[:-7] + f"-iter{iteration}.dat.h5"
    return path_text + f"-iter{iteration}"


def rolling_autosave_path(path_text: str) -> str:
    if path_text.endswith(".cas.h5"):
        return path_text[:-7] + "-autosave.cas.h5"
    if path_text.endswith(".dat.h5"):
        return path_text[:-7] + "-autosave.dat.h5"
    return path_text + "-autosave"


def write_case_data_pair(solver, case_file: str, data_file: str, label: str) -> None:
    print_header(label)
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    if not try_action(f"write_case_{label}", lambda: solver.settings.file.write_case(file_name=case_file)):
        raise RuntimeError(f"Could not write case for {label}")
    if not try_action(f"write_data_{label}", lambda: solver.settings.file.write_data(file_name=data_file)):
        raise RuntimeError(f"Could not write data for {label}")


def iterate_target_case(
    solver,
    iterations: int,
    report_interval: int,
    checkpoint_interval: int,
    output_case: str,
    output_data: str,
) -> int:
    print_header("Run Target Case")
    if iterations <= 0:
        print("iterate: SKIPPED")
        return

    chunk = max(1, report_interval)
    checkpoint_step = max(0, checkpoint_interval)
    completed = 0
    while completed < iterations:
        step = min(chunk, iterations - completed)
        try:
            ran = try_action(
                f"iterate_{completed + step}",
                lambda step=step: solver.settings.solution.run_calculation.iterate(iter_count=step),
            )
        except KeyboardInterrupt as exc:
            raise RunInterrupted(completed) from exc
        if not ran:
            try:
                ran = try_action(
                    f"iterate_tui_{completed + step}",
                    lambda step=step: solver.tui.solve.iterate(step),
                )
            except KeyboardInterrupt as exc:
                raise RunInterrupted(completed) from exc
        if not ran:
            raise RuntimeError(f"Iteration failed at step {completed + step}")
        completed += step
        print(f"progress: {completed}/{iterations}")
        if checkpoint_step > 0 and completed < iterations and completed % checkpoint_step == 0:
            write_case_data_pair(
                solver,
                rolling_autosave_path(output_case),
                rolling_autosave_path(output_data),
                f"autosave_{completed}",
            )
    return completed


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()
    validate_args(args)

    fallback_settings = load_fallback_settings()
    fallback_general = fallback_settings["setup"]["general"]
    fallback_models = fallback_settings["setup"]["models"]
    fallback_materials = fallback_settings["setup"]["materials"]
    fallback_boundary = fallback_settings["setup"]["boundary_conditions"]
    fallback_cell_zones = fallback_settings["setup"]["cell_zone_conditions"]
    fallback_solution = fallback_settings["solution"]

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")

    if args.resume_case and args.resume_data:
        load_resume_case_data(solver, args.resume_case, args.resume_data)
    else:
        load_target_mesh(solver, args.target_mesh)

        target_boundary_state = safe_get_state(
            solver.settings.setup.boundary_conditions,
            "target_boundary_conditions",
        )
        if not isinstance(target_boundary_state, Mapping):
            raise RuntimeError("Could not inspect target boundary state")
        print_header("Target Boundary Summary")
        summarize_boundary_state(target_boundary_state)
        role_map = build_target_role_map(target_boundary_state)

        replacements = build_name_replacements_from_fallback(fallback_boundary, target_boundary_state)
        remapped_fallback_boundary = deep_replace_names(fallback_boundary, replacements)
        remapped_fallback_cell_zones = deep_replace_names(fallback_cell_zones, {"fluid": "fluid"})

        intended_boundary = build_intended_boundary_state(role_map)
        intended_materials = build_intended_materials()

        apply_branch_with_fallback(
            "General Settings",
            lambda: apply_intended_general(solver),
            lambda: try_action(
                "apply_fallback_general",
                lambda: solver.settings.setup.general.set_state(fallback_general),
            ),
        )
        apply_branch_with_fallback(
            "Models",
            lambda: apply_intended_models(solver),
            lambda: try_action(
                "apply_fallback_models",
                lambda: solver.settings.setup.models.set_state(fallback_models),
            ),
        )
        apply_branch_with_fallback(
            "Materials",
            lambda: apply_material_states(solver, intended_materials),
            lambda: apply_material_states(solver, fallback_materials),
        )
        apply_branch_with_fallback(
            "Phase Material Assignment",
            lambda: apply_intended_phase_materials(solver),
            lambda: True,
        )
        print_header("Surface Tension")
        if not apply_surface_tension_best_effort(solver):
            print("surface_tension: still not writable through API, manual Fluent check may be needed")
        apply_branch_with_fallback(
            "Cell Zone Conditions",
            lambda: apply_intended_cell_zone_conditions(solver),
            lambda: try_action(
                "apply_fallback_cell_zones",
                lambda: solver.settings.setup.cell_zone_conditions.set_state(remapped_fallback_cell_zones),
            ),
        )
        apply_branch_with_fallback(
            "Boundary Type Conversion",
            lambda: convert_target_boundaries_to_intended(solver, target_boundary_state, role_map),
            lambda: True,
        )
        apply_branch_with_fallback(
            "Boundary Conditions",
            lambda: apply_boundary_states(solver, intended_boundary),
            lambda: apply_boundary_states(solver, remapped_fallback_boundary),
        )
        apply_branch_with_fallback(
            "Solution Methods",
            lambda: apply_intended_solution_methods(solver),
            lambda: try_action(
                "apply_fallback_solution_methods",
                lambda: solver.settings.solution.methods.set_state(fallback_solution["methods"]),
            ),
        )
        apply_branch_with_fallback(
            "Solution Controls",
            lambda: apply_intended_solution_controls(solver),
            lambda: try_action(
                "apply_fallback_solution_controls",
                lambda: solver.settings.solution.controls.set_state(fallback_solution["controls"]),
            ),
        )
        apply_branch_with_fallback(
            "Initialization Settings",
            lambda: apply_intended_initialization(solver),
            lambda: try_action(
                "apply_fallback_initialization",
                lambda: solver.settings.solution.initialization.set_state(
                    fallback_settings["solution_initialization_detail"]["_state"]
                ),
            ),
        )

        print_header("Disable DPM For This Run")
        disable_dpm_after_setup(solver)

        initialize_target_case(solver)

        if args.initialized_case and args.initialized_data:
            write_case_data_pair(
                solver,
                args.initialized_case,
                args.initialized_data,
                "write_initialized_case_data",
            )

    run_iterations = 0 if args.skip_run else args.iterations
    try:
        iterate_target_case(
            solver,
            run_iterations,
            args.report_interval,
            args.checkpoint_interval,
            args.output_case,
            args.output_data,
        )
    except RunInterrupted as exc:
        print_header("Interrupt Save")
        print(
            "Keyboard interrupt received. Saving current solver state so it can be resumed "
            f"from {args.output_case} and {args.output_data}."
        )
        write_case_data_pair(solver, args.output_case, args.output_data, "write_interrupt_case_data")
        print(f"\nPaused run saved after approximately {exc.completed_iterations} completed iterations.")
        return 130
    write_case_data_pair(solver, args.output_case, args.output_data, "write_final_case_data")

    print("\nSetup 07 rebuild finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

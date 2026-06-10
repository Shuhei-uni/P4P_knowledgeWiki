#!/usr/bin/env python3
"""Build setup 09a from the setup 07 split-inlet carrier-field scaffold.

This script is intentionally safe by default:
- `--dry-run` only prints the planned 09a payload.
- `--apply` connects to a second Fluent gRPC session and either:
  - loads a converged setup 07 case/data pair, then adds DPM, or
  - rebuilds setup 07 on a target mesh, initializes it, runs the carrier field,
    then adds DPM.
- The intended 09a workflow is post-convergence droplet tracking on top of the
  setup 07 carrier field, not DPM configuration before the carrier field exists.

Connection source for this script:
- FLUENT_SERVER_INFO_FILE{N}, or
- FLUENT_IP{N} + FLUENT_PORT{N} + FLUENT_PASSWORD{N}

Expected follow-up from the user:
- provide either a converged setup 07 case/data pair or a target `.msh` plus
  a carrier-iteration budget
- confirm output case/data path(s)
- confirm whether the default steam-inlet droplet-injection assumption is kept
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from setup07_rebuild_run import (  # noqa: E402
    apply_boundary_states,
    apply_intended_cell_zone_conditions,
    apply_intended_general,
    apply_intended_initialization,
    apply_intended_models,
    apply_intended_phase_materials,
    apply_intended_solution_controls,
    apply_intended_solution_methods,
    apply_material_states,
    apply_surface_tension_best_effort,
    build_intended_boundary_state,
    build_intended_materials,
    build_target_role_map,
    convert_target_boundaries_to_intended,
    initialize_target_case,
    iterate_target_case,
    load_resume_case_data,
    RunInterrupted,
    write_case_data_pair,
)
from pyansys_fluent.common import bool_env, remote_chdir, remote_file_exists, safe_get_state, try_action  # noqa: E402
from pyansys_fluent.connection import connect, env_suffix  # noqa: E402
from pyansys_fluent.setup_common import names_from_boundary_state, print_header, require_remote_input, summarize_boundary_state  # noqa: E402

DEFAULT_DROPLET_DIAMETERS_UM = (5.0, 10.0, 14.2, 41.0)
DEFAULT_INJECTION_SURFACE_ROLE = "steam_inlet"
DEFAULT_WALL_DPM_MODE = "reflect"
DEFAULT_BOTTOM_DPM_MODE = "trap"
DEFAULT_OUTLET_DPM_MODE = "escape"
DEFAULT_PARTICLE_MASS_FLOW_RATE = 1e-6
DEFAULT_STREAMS_PER_INJECTION = 200
SEED_INJECTION_NAME = "__codex_seed_default_injection__"
DEFAULT_CARRIER_ITERATIONS = 500


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare setup 09a as a setup 07 carrier-field rebuild plus one-way "
            "DPM carryover injections on a second Fluent gRPC session."
        )
    )

    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned 09a payload without connecting to Fluent.",
    )
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Connect to Fluent, stage a converged carrier field, then apply the 09a DPM extension.",
    )
    parser.add_argument(
        "--server-id",
        default="2",
        help="Configured Fluent server id to use. Default: 2. Use 1 for FLUENT_IP, 2 for FLUENT_IP2, 3 for FLUENT_IP3.",
    )

    parser.add_argument(
        "--target-mesh",
        default="",
        help="Remote mesh path visible to the second Fluent session.",
    )
    parser.add_argument(
        "--resume-case",
        default="",
        help="Optional remote converged setup 07 case file to resume from instead of rebuilding from mesh.",
    )
    parser.add_argument(
        "--resume-data",
        default="",
        help="Optional remote converged data file to resume from instead of rebuilding from mesh.",
    )
    parser.add_argument(
        "--carrier-iterations",
        type=int,
        default=DEFAULT_CARRIER_ITERATIONS,
        help=(
            "Iterations to run the setup 07 carrier field before enabling DPM "
            "when rebuilding from mesh. Default: 500."
        ),
    )
    parser.add_argument(
        "--output-case",
        default="",
        help="Optional remote final 09a case path to write after DPM setup and any later iterations.",
    )
    parser.add_argument(
        "--output-data",
        default="",
        help="Optional remote final 09a data path to write with the output case.",
    )
    parser.add_argument(
        "--initialized-case",
        default="",
        help="Optional remote case path to write immediately after initialization.",
    )
    parser.add_argument(
        "--initialized-data",
        default="",
        help="Optional remote data path to write immediately after initialization.",
    )
    parser.add_argument(
        "--injection-surface-role",
        choices=("steam_inlet", "liquid_inlet"),
        default=DEFAULT_INJECTION_SURFACE_ROLE,
        help="Which split inlet supplies the tracked droplets. Default: steam_inlet.",
    )
    parser.add_argument(
        "--droplet-diameters-um",
        nargs="+",
        type=float,
        default=list(DEFAULT_DROPLET_DIAMETERS_UM),
        help="DPM droplet diameters in micrometers. Default: 5 10 14.2 41.",
    )
    parser.add_argument(
        "--particle-material",
        default="water-droplet",
        help="Inert particle material for DPM. Default: water-droplet.",
    )
    parser.add_argument(
        "--particle-density",
        type=float,
        default=881.77,
        help="Particle density for the inert particle material. Default: 881.77.",
    )
    parser.add_argument(
        "--streams-per-injection",
        type=int,
        default=DEFAULT_STREAMS_PER_INJECTION,
        help="Surface injection stream count. Default: 200.",
    )
    parser.add_argument(
        "--particle-mass-flow-rate",
        type=float,
        default=DEFAULT_PARTICLE_MASS_FLOW_RATE,
        help="DPM total flow rate per injection. Default: 1e-6.",
    )
    parser.add_argument(
        "--enable-turbulent-dispersion",
        action="store_true",
        help="Enable stochastic turbulent dispersion for each injection.",
    )
    parser.add_argument(
        "--turbulent-dispersion-tries",
        type=int,
        default=2,
        help="Number of stochastic tries when turbulent dispersion is enabled.",
    )
    parser.add_argument(
        "--dpm-max-steps",
        type=int,
        default=5000,
        help="DPM maximum tracking steps. Default: 5000.",
    )
    parser.add_argument(
        "--wall-dpm-mode",
        choices=("reflect", "trap"),
        default=DEFAULT_WALL_DPM_MODE,
        help="DPM fate on main walls. Default: reflect.",
    )
    parser.add_argument(
        "--bottom-dpm-mode",
        choices=("trap", "reflect"),
        default=DEFAULT_BOTTOM_DPM_MODE,
        help="DPM fate on bottom collection wall. Default: trap.",
    )
    parser.add_argument(
        "--outlet-dpm-mode",
        choices=("escape", "trap"),
        default=DEFAULT_OUTLET_DPM_MODE,
        help="DPM fate on the steam outlet. Default: escape.",
    )
    parser.add_argument(
        "--snapshot-json",
        default="",
        help="Optional local JSON path to dump the planned 09a payload.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=0,
        help="Optional iterations to run after the 09a DPM extension is applied. Default: 0.",
    )
    parser.add_argument(
        "--report-interval",
        type=int,
        default=100,
        help="Console progress interval during iterations. Default: 100.",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=1000,
        help="Overwrite a rolling autosave case/data checkpoint every N iterations. Default: 1000.",
    )
    return parser


def connect_with_env_suffix(server_id: str | int = "2"):
    load_dotenv()
    suffix = env_suffix(server_id)
    return connect(server_id=suffix or "1")


def um_to_microns_text(value_um: float) -> str:
    if value_um.is_integer():
        return f"{int(value_um)}"
    return f"{value_um:g}"


def dump_json_if_requested(path_text: str, payload: Mapping[str, Any]) -> None:
    if not path_text:
        return
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"snapshot_json: wrote {path}")


def require_apply_paths(args: argparse.Namespace) -> None:
    has_resume = bool(args.resume_case or args.resume_data)
    if has_resume and not (args.resume_case and args.resume_data):
        raise RuntimeError("Both --resume-case and --resume-data are required for resume mode.")
    if not has_resume and not args.target_mesh:
        raise RuntimeError("--target-mesh is required with --apply unless resume files are provided.")
    if not has_resume and args.carrier_iterations <= 0:
        raise RuntimeError(
            "09a is defined as a post-convergence DPM extension of setup 07. "
            "Provide --resume-case/--resume-data or a positive --carrier-iterations value."
        )
    if bool(args.output_case) ^ bool(args.output_data):
        raise RuntimeError("--output-case and --output-data must be provided together.")
    if bool(args.initialized_case) ^ bool(args.initialized_data):
        raise RuntimeError(
            "--initialized-case and --initialized-data must be provided together."
        )
    if not has_resume and args.carrier_iterations > 0 and not (args.output_case and args.output_data):
        raise RuntimeError(
            "--output-case and --output-data are required when rebuilding from mesh so "
            "carrier-field checkpoints and the final 09a case have a destination."
        )


def build_dpm_plan(args: argparse.Namespace) -> dict[str, Any]:
    droplet_sizes = [
        {
            "name": f"dpm-{um_to_microns_text(diameter_um)}um",
            "diameter_um": diameter_um,
            "diameter_m": diameter_um * 1e-6,
        }
        for diameter_um in args.droplet_diameters_um
    ]

    assumptions = [
        "Setup 09a inherits the setup 07 continuous-field definition.",
        "Tracked particles are injected from the steam-side split inlet by default.",
        "Steam outlet is treated as escape for carryover counting.",
        "Bottom is treated as trap for collected liquid unless later revised.",
        "Main separator walls are treated as reflect by default to avoid silently counting all wall hits as separation.",
        "DPM is one-way only. Continuous-phase feedback stays disabled.",
        (
            "When rebuilding from mesh, the setup 07 carrier field is iterated before DPM is applied."
            if args.carrier_iterations > 0
            else "A converged setup 07 case/data pair should be supplied before applying DPM."
        ),
        (
            "No post-DPM iterations are planned."
            if args.iterations <= 0
            else "Additional iterations are requested after the 09a DPM extension is applied."
        ),
    ]

    return {
        "setup_id": "09a",
        "lineage_parent": "07-pure-phase-split-actual-area",
        "target_mesh": args.target_mesh,
        "resume_case": args.resume_case,
        "resume_data": args.resume_data,
        "carrier_iterations": args.carrier_iterations,
        "output_case": args.output_case,
        "output_data": args.output_data,
        "initialized_case": args.initialized_case,
        "initialized_data": args.initialized_data,
        "iterations": args.iterations,
        "report_interval": args.report_interval,
        "checkpoint_interval": args.checkpoint_interval,
        "carrier_field": {
            "solver": "pressure-based",
            "time": "steady",
            "multiphase": "mixture",
            "turbulence": "RNG k-epsilon",
            "energy": "off",
            "surface_tension_best_effort": 0.0411,
        },
        "dpm": {
            "one_way_coupling": True,
            "unsteady_particle_tracking": False,
            "particle_material": args.particle_material,
            "particle_density": args.particle_density,
            "injection_surface_role": args.injection_surface_role,
            "streams_per_injection": args.streams_per_injection,
            "particle_mass_flow_rate": args.particle_mass_flow_rate,
            "enable_turbulent_dispersion": args.enable_turbulent_dispersion,
            "turbulent_dispersion_tries": args.turbulent_dispersion_tries,
            "max_tracking_steps": args.dpm_max_steps,
            "droplet_sizes": droplet_sizes,
            "boundary_fates": {
                "steam_outlet": args.outlet_dpm_mode,
                "main_walls": args.wall_dpm_mode,
                "bottom": args.bottom_dpm_mode,
            },
        },
        "assumptions": assumptions,
        "user_inputs_still_needed": [
            "Converged setup 07 case/data pair, or a remote .msh path plus carrier iterations",
            "Final case/data output path(s)",
            "Confirmation that droplets should be injected from the steam-side inlet",
            "Any alternative wall-fate interpretation for carryover accounting",
        ],
    }


def ensure_inert_particle_material(
    solver,
    material_name: str,
    density: float,
) -> bool:
    materials = solver.settings.setup.materials
    inert_branch = getattr(materials, "inert_particle", None)
    if inert_branch is None:
        print("inert_particle branch is unavailable in this Fluent build/state.")
        return False

    try:
        existing = set(inert_branch.get_object_names())
    except Exception as exc:
        print(f"inert_particle_names: FAILED -> {exc}")
        existing = set()

    if material_name in existing:
        return True

    ok = True
    ok &= try_action(
        f"material_prepare_inert_particle.{material_name}",
        lambda: inert_branch.create(name=material_name),
    )

    try:
        existing = set(inert_branch.get_object_names())
    except Exception as exc:
        print(f"inert_particle_names_postcreate: FAILED -> {exc}")
        existing = set()

    if material_name not in existing:
        try:
            inert_branch.set_state(
                {
                    material_name: {
                        "name": material_name,
                        "chemical_formula": "",
                        "density": {"option": "constant", "value": density},
                    }
                }
            )
            ok = True
        except Exception as exc:
            print(f"material_setstate_inert_particle.{material_name}: FAILED -> {exc}")

    try:
        existing = set(inert_branch.get_object_names())
    except Exception as exc:
        print(f"inert_particle_names_postsetstate: FAILED -> {exc}")
        existing = set()

    if material_name not in existing:
        print(
            f"inert particle material '{material_name}' is still unavailable after "
            "manual creation attempts."
        )
        return False

    ok &= try_action(
        f"material_apply_inert_particle.{material_name}",
        lambda: inert_branch[material_name].set_state(
            {
                "name": material_name,
                "chemical_formula": "",
                "density": {"option": "constant", "value": density},
            }
        ),
    )
    return ok


def ensure_seed_injection_for_inert_materials(solver, seed_name: str = SEED_INJECTION_NAME) -> bool:
    branch = solver.settings.setup.models.discrete_phase.injections
    try:
        names = set(branch.get_object_names())
    except Exception:
        names = set()
    if seed_name in names:
        return True
    return try_action(
        f"create_seed_injection_{seed_name}",
        lambda: branch.create(name=seed_name),
    )


def enable_dpm_model_best_effort(solver) -> bool:
    dpm = solver.settings.setup.models.discrete_phase
    try:
        # In this 2026 R1 Student path, the DPM branch is already live enough to
        # create injections once the carrier setup exists.
        dpm.injections.get_object_names()
        print("enable_dpm_model_precheck: OK -> discrete_phase branch already active")
        return True
    except Exception:
        pass

    ok = False
    ok |= try_action(
        "enable_dpm_model_attr_enabled",
        lambda: setattr(dpm, "enabled", True),
    )
    ok |= try_action(
        "enable_dpm_model_attr_model",
        lambda: setattr(dpm, "model", True),
    )
    ok |= try_action(
        "enable_dpm_model_tui_best_effort",
        lambda: solver.scheme.exec(
            ('(ti-menu-load-string "/define/models/dpm yes")',)
        ),
    )
    return ok


def delete_injection_if_present(solver, injection_name: str) -> bool:
    branch = solver.settings.setup.models.discrete_phase.injections
    try:
        names = set(branch.get_object_names())
    except Exception:
        names = set()
    if injection_name not in names:
        return True
    if try_action(
        f"delete_injection_{injection_name}_delitem",
        lambda: branch.__delitem__(injection_name),
    ):
        return True
    return try_action(
        f"delete_injection_{injection_name}_delete",
        lambda: branch.delete(name_list=[injection_name]),
    )


def zone_name_for_role(role_map: Mapping[str, str], role: str) -> str:
    zone_name = role_map.get(role, "").strip()
    if not zone_name:
        raise RuntimeError(f"Role map does not contain required role: {role}")
    return zone_name


def build_dpm_boundary_patch(
    role_map: Mapping[str, str],
    wall_mode: str,
    bottom_mode: str,
    outlet_mode: str,
) -> dict[str, Any]:
    liquid_inlet = zone_name_for_role(role_map, "liquid_inlet")
    steam_inlet = zone_name_for_role(role_map, "steam_inlet")
    outlet = zone_name_for_role(role_map, "outlet")
    wall = zone_name_for_role(role_map, "wall")
    bottom = zone_name_for_role(role_map, "bottom")

    main_wall_dpm = {"discrete_phase_bc_type": wall_mode}
    if wall_mode == "reflect":
        main_wall_dpm.update(
            {
                "normal_coefficient": {
                    "option": "polynomial",
                    "function_of": "angle",
                    "polynomial": {"function_of": "angle", "coefficients": [1.0]},
                },
                "tangential_coefficient": {
                    "option": "polynomial",
                    "function_of": "angle",
                    "polynomial": {"function_of": "angle", "coefficients": [1.0]},
                },
            }
        )

    return {
        "velocity_inlet": {
            liquid_inlet: {
                "name": liquid_inlet,
                "phase": {"mixture": {"dpm": {"discrete_phase_bc_type": "escape"}}},
            },
            steam_inlet: {
                "name": steam_inlet,
                "phase": {"mixture": {"dpm": {"discrete_phase_bc_type": "escape"}}},
            },
        },
        "pressure_outlet": {
            outlet: {
                "name": outlet,
                "phase": {"mixture": {"dpm": {"discrete_phase_bc_type": outlet_mode}}},
            }
        },
        "wall": {
            wall: {
                "name": wall,
                "phase": {"mixture": {"dpm": main_wall_dpm}},
            },
            bottom: {
                "name": bottom,
                "phase": {
                    "mixture": {"dpm": {"discrete_phase_bc_type": bottom_mode}}
                },
            },
        },
    }


def build_injection_state(
    role_map: Mapping[str, str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    injection_surface = zone_name_for_role(role_map, args.injection_surface_role)
    injections: dict[str, Any] = {}
    for diameter_um in args.droplet_diameters_um:
        name = f"dpm-{um_to_microns_text(diameter_um)}um"
        injections[name] = {
            "name": name,
            "particle_type": "inert",
            "material": args.particle_material,
            "injection_type": {"option": "surface"},
            "initial_values": {
                "reference_frame": "global",
                "location": {
                    "injection_surfaces": [injection_surface],
                    "randomized_positions_enabled": False,
                },
                "mass_flow_rate": {"total_flow_rate": args.particle_mass_flow_rate},
                "velocity": {
                    "use_face_normal_direction": True,
                    "x_velocity": 0.0,
                    "y_velocity": 0.0,
                    "z_velocity": 0.0,
                },
                "particle_size": {
                    "option": "uniform",
                    "diameter": diameter_um * 1e-6,
                },
            },
            "physical_models": {
                "particle_drag": {"option": "spherical"},
                "turbulent_dispersion": {
                    "enabled": args.enable_turbulent_dispersion,
                    "random_eddy_lifetime": False,
                    "number_of_tries": args.turbulent_dispersion_tries,
                    "time_scale_constant": 0.15,
                },
                "particle_rotation": {
                    "enabled": False,
                },
                "rough_wall_treatment_enabled": False,
                "custom_laws": {
                    "law_1": "inert-heating",
                    "law_2": "inactive",
                    "law_3": "inactive",
                    "law_4": "inactive",
                    "law_5": "inactive",
                    "law_6": "inactive",
                    "law_7": "inactive",
                    "law_8": "inactive",
                    "law_9": "inactive",
                    "law_10": "inactive",
                    "switch": "Default",
                },
            },
        }
    return injections


def apply_dpm_model_settings(solver, args: argparse.Namespace) -> bool:
    dpm = solver.settings.setup.models.discrete_phase
    ok = True
    ok &= enable_dpm_model_best_effort(solver)
    ok &= try_action(
        "set_dpm_interaction_with_continuous_phase_off",
        lambda: setattr(solver.settings.setup.models.discrete_phase.general_settings.interaction, "enabled", False),
    )
    ok &= try_action(
        "set_dpm_contour_plotting_none",
        lambda: setattr(dpm.general_settings, "contour_plotting", "none"),
    )
    ok &= try_action(
        "set_dpm_max_steps",
        lambda: setattr(dpm.tracking, "max_num_steps", args.dpm_max_steps),
    )
    try_action(
        "set_dpm_high_order_tracking_best_effort",
        lambda: setattr(dpm.numerics, "high_res_tracking", True),
    )
    try_action(
        "set_dpm_pressure_gradient_force_off_best_effort",
        lambda: setattr(dpm.physical_models, "pressure_gradient_force", False),
    )
    try_action(
        "set_dpm_virtual_mass_force_off_best_effort",
        lambda: setattr(dpm.physical_models, "virtual_mass_force", False),
    )
    try_action(
        "set_dpm_unsteady_tracking_off_best_effort",
        lambda: setattr(dpm.particle_treatment, "unsteady_tracking", False),
    )
    try_action(
        "set_dpm_interaction_iteration_interval_best_effort",
        lambda: setattr(dpm.general_settings.interaction, "iteration_interval", 10),
    )
    return ok


def apply_dpm_injections(solver, injection_state: Mapping[str, Any]) -> bool:
    branch = solver.settings.setup.models.discrete_phase.injections
    ok = True
    for name, payload in injection_state.items():
        ok &= try_action(
            f"create_injection_{name}",
            lambda injection_name=name: branch.create(name=injection_name),
        )
        ok &= apply_single_dpm_injection(
            branch=branch,
            injection_name=name,
            state=payload,
        )
    return ok


def reacquire_injection(branch, injection_name: str):
    return branch[injection_name]


def apply_single_dpm_injection(branch, injection_name: str, state: Mapping[str, Any]) -> bool:
    ok = True
    injection = reacquire_injection(branch, injection_name)

    particle_type = state.get("particle_type")
    if particle_type is not None:
        ok &= try_action(
            f"{injection_name}_particle_type",
            lambda value=particle_type: setattr(injection, "particle_type", value),
        )
        injection = reacquire_injection(branch, injection_name)

    material = state.get("material")
    if material is not None:
        ok &= try_action(
            f"{injection_name}_material",
            lambda value=material: setattr(injection, "material", value),
        )
        injection = reacquire_injection(branch, injection_name)

    injection_type = state.get("injection_type", {})
    if isinstance(injection_type, Mapping):
        option = injection_type.get("option")
        if option is not None:
            ok &= try_action(
                f"{injection_name}_injection_type",
                lambda value=option: setattr(injection.injection_type, "option", value),
            )
            injection = reacquire_injection(branch, injection_name)

    initial_values = state.get("initial_values", {})
    if isinstance(initial_values, Mapping):
        reference_frame = initial_values.get("reference_frame")
        if reference_frame is not None:
            ok &= try_action(
                f"{injection_name}_reference_frame",
                lambda value=reference_frame: setattr(injection.initial_values, "reference_frame", value),
            )

        location = initial_values.get("location", {})
        if isinstance(location, Mapping):
            ok &= try_action(
                f"{injection_name}_location",
                lambda value=dict(location): injection.initial_values.location.set_state(value),
            )

        mass_flow_rate = initial_values.get("mass_flow_rate", {})
        if isinstance(mass_flow_rate, Mapping):
            ok &= try_action(
                f"{injection_name}_mass_flow_rate",
                lambda value=dict(mass_flow_rate): injection.initial_values.mass_flow_rate.set_state(value),
            )

        velocity = initial_values.get("velocity", {})
        if isinstance(velocity, Mapping):
            ok &= try_action(
                f"{injection_name}_velocity",
                lambda value=dict(velocity): injection.initial_values.velocity.set_state(value),
            )

        particle_size = initial_values.get("particle_size", {})
        if isinstance(particle_size, Mapping):
            ok &= try_action(
                f"{injection_name}_particle_size",
                lambda value=dict(particle_size): injection.initial_values.particle_size.set_state(value),
            )

        angular_velocity = initial_values.get("angular_velocity", {})
        if isinstance(angular_velocity, Mapping) and angular_velocity:
            ok &= try_action(
                f"{injection_name}_angular_velocity",
                lambda value=dict(angular_velocity): injection.initial_values.angular_velocity.set_state(value),
            )

    physical_models = state.get("physical_models", {})
    if isinstance(physical_models, Mapping):
        particle_drag = physical_models.get("particle_drag", {})
        if isinstance(particle_drag, Mapping):
            option = particle_drag.get("option")
            if option is not None:
                ok &= try_action(
                    f"{injection_name}_particle_drag",
                    lambda value=option: setattr(injection.physical_models.particle_drag, "option", value),
                )

        turbulent_dispersion = physical_models.get("turbulent_dispersion", {})
        if isinstance(turbulent_dispersion, Mapping):
            ok &= try_action(
                f"{injection_name}_turbulent_dispersion",
                lambda value=dict(turbulent_dispersion): injection.physical_models.turbulent_dispersion.set_state(value),
            )

        particle_rotation = physical_models.get("particle_rotation", {})
        if isinstance(particle_rotation, Mapping):
            ok &= try_action(
                f"{injection_name}_particle_rotation",
                lambda value=dict(particle_rotation): injection.physical_models.particle_rotation.set_state(value),
            )

        rough_wall_treatment_enabled = physical_models.get("rough_wall_treatment_enabled")
        if rough_wall_treatment_enabled is not None:
            ok &= try_action(
                f"{injection_name}_rough_wall_treatment",
                lambda value=rough_wall_treatment_enabled: setattr(
                    injection.physical_models,
                    "rough_wall_treatment_enabled",
                    value,
                ),
            )

        custom_laws = physical_models.get("custom_laws", {})
        if isinstance(custom_laws, Mapping):
            ok &= try_action(
                f"{injection_name}_custom_laws",
                lambda value=dict(custom_laws): injection.physical_models.custom_laws.set_state(value),
            )

    return ok


def build_compact_boundary_summary(boundary_state: Mapping[str, Any]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    for boundary_type in ("velocity_inlet", "mass_flow_inlet", "pressure_outlet", "wall", "interior"):
        names = names_from_boundary_state(boundary_state, boundary_type)
        if names:
            summary[boundary_type] = names
    return summary


def load_target_mesh(solver, mesh_path: str) -> None:
    print_header("Load Target Mesh")
    require_remote_input(solver, mesh_path, "target mesh")
    remote_chdir(solver, str(PureWindowsPath(mesh_path).parent))
    if not try_action(
        "read_target_mesh",
        lambda: solver.settings.file.read_mesh(file_name=mesh_path),
    ):
        raise RuntimeError("Could not read target mesh")


def rebuild_setup07_carrier_field(
    solver,
    role_map: Mapping[str, str],
) -> None:
    target_boundary_state = safe_get_state(
        solver.settings.setup.boundary_conditions,
        "target_boundary_conditions",
    )
    if not isinstance(target_boundary_state, Mapping):
        raise RuntimeError("Could not inspect target boundary state")

    if not convert_target_boundaries_to_intended(solver, target_boundary_state, role_map):
        raise RuntimeError("Could not convert target boundaries to intended types")

    if not apply_intended_general(solver):
        raise RuntimeError("Failed to apply setup 07 general settings")
    if not apply_intended_models(solver):
        raise RuntimeError("Failed to apply setup 07 model settings")
    if not apply_material_states(solver, build_intended_materials()):
        raise RuntimeError("Failed to apply setup 07 fluid materials")
    if not apply_intended_phase_materials(solver):
        raise RuntimeError("Failed to map setup 07 phase materials")
    apply_surface_tension_best_effort(solver)
    if not apply_intended_cell_zone_conditions(solver):
        raise RuntimeError("Failed to apply setup 07 cell-zone conditions")
    if not apply_boundary_states(solver, build_intended_boundary_state(role_map)):
        raise RuntimeError("Failed to apply setup 07 boundary conditions")
    if not apply_intended_solution_methods(solver):
        raise RuntimeError("Failed to apply setup 07 solution methods")
    if not apply_intended_solution_controls(solver):
        raise RuntimeError("Failed to apply setup 07 solution controls")
    if not apply_intended_initialization(solver):
        raise RuntimeError("Failed to set setup 07 initialization options")


def apply_09a_dpm_extension(
    solver,
    role_map: Mapping[str, str],
    args: argparse.Namespace,
) -> Mapping[str, Any]:
    print_header("Apply 09a DPM Materials")
    ensure_seed_injection_for_inert_materials(solver)
    if not ensure_inert_particle_material(
        solver,
        material_name=args.particle_material,
        density=args.particle_density,
    ):
        print(
            "dpm_materials: SKIPPED after failure. "
            "Manual Fluent cleanup may still be required."
        )

    print_header("Apply 09a DPM Model Settings")
    if not apply_dpm_model_settings(solver, args):
        print(
            "dpm_model_settings: PARTIAL/FAILED. Continuing so the case can still be saved."
        )

    print_header("Apply 09a DPM Boundary Fates")
    boundary_patch = build_dpm_boundary_patch(
        role_map=role_map,
        wall_mode=args.wall_dpm_mode,
        bottom_mode=args.bottom_dpm_mode,
        outlet_mode=args.outlet_dpm_mode,
    )
    if not apply_boundary_states(solver, boundary_patch):
        print(
            "dpm_boundary_fates: PARTIAL/FAILED. Continuing so the case can still be saved."
        )

    print_header("Apply 09a DPM Injections")
    injections = build_injection_state(role_map, args)
    if not apply_dpm_injections(solver, injections):
        print(
            "dpm_injections: PARTIAL/FAILED. Continuing so the case can still be saved."
        )
    delete_injection_if_present(solver, SEED_INJECTION_NAME)
    return injections


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    plan = build_dpm_plan(args)
    dump_json_if_requested(args.snapshot_json, plan)

    if args.dry_run:
        print(json.dumps(plan, indent=2))
        return 0

    require_apply_paths(args)

    solver = connect_with_env_suffix(args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")

    role_map: Mapping[str, str]
    injections: Mapping[str, Any] = {}
    if args.resume_case and args.resume_data:
        load_resume_case_data(solver, args.resume_case, args.resume_data)
        boundary_state = safe_get_state(
            solver.settings.setup.boundary_conditions,
            "resume_boundary_conditions",
        )
        if not isinstance(boundary_state, Mapping):
            raise RuntimeError("Could not inspect resumed boundary state")
        print_header("Resume Boundary Summary")
        summarize_boundary_state(boundary_state)
        role_map = build_target_role_map(boundary_state)
        injections = apply_09a_dpm_extension(solver, role_map, args)
    else:
        load_target_mesh(solver, args.target_mesh)

        boundary_state = safe_get_state(
            solver.settings.setup.boundary_conditions,
            "target_boundary_conditions",
        )
        if not isinstance(boundary_state, Mapping):
            raise RuntimeError("Could not inspect target boundary state")

        print_header("Target Boundary Summary")
        summarize_boundary_state(boundary_state)
        role_map = build_target_role_map(boundary_state)

        rebuild_setup07_carrier_field(solver, role_map)
        initialize_target_case(solver)

        if args.initialized_case and args.initialized_data:
            write_case_data_pair(
                solver,
                args.initialized_case,
                args.initialized_data,
                "initialized",
            )

        if args.carrier_iterations > 0:
            iterate_target_case(
                solver,
                args.carrier_iterations,
                args.report_interval,
                args.checkpoint_interval,
                args.output_case,
                args.output_data,
            )

        injections = apply_09a_dpm_extension(solver, role_map, args)

    try:
        if args.iterations > 0:
            if not (args.output_case and args.output_data):
                raise RuntimeError(
                    "--output-case and --output-data are required when --iterations > 0 "
                    "so interrupt/final saves have a destination."
                )
            iterate_target_case(
                solver,
                args.iterations,
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
        write_case_data_pair(
            solver,
            args.output_case,
            args.output_data,
            "write_interrupt_case_data",
        )
        print(f"\nPaused run saved after approximately {exc.completed_iterations} completed iterations.")
        return 130

    if args.output_case and args.output_data:
        write_case_data_pair(
            solver,
            args.output_case,
            args.output_data,
            "final",
        )

    final_boundary_state = safe_get_state(
        solver.settings.setup.boundary_conditions,
        "final_boundary_conditions",
    )
    payload = {
        "plan": plan,
        "role_map": dict(role_map),
        "final_boundary_summary": (
            build_compact_boundary_summary(final_boundary_state)
            if isinstance(final_boundary_state, Mapping)
            else {}
        ),
        "created_injections": sorted(injections.keys()),
    }
    print_header("09a Payload Summary")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

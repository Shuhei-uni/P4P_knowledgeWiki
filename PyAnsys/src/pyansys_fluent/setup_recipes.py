#!/usr/bin/env python3
"""Recipe-level orchestration for setup07 and setup09a."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping
from typing import Any

from pyansys_fluent.common import safe_get_state, try_action
from pyansys_fluent.run_persistence import RunPersistence, discover_latest_resume_source
from pyansys_fluent.setup_common import print_header, summarize_boundary_state
from pyansys_fluent.setup_io import load_resume_case_data, load_target_mesh, write_case_data_pair
from pyansys_fluent.setup_run import RunInterrupted, initialize_case, iterate_case
from pyansys_fluent.setup_discovery import (
    build_compact_boundary_summary,
    build_target_role_map,
    convert_target_boundaries_to_intended,
)
from pyansys_fluent.setup_carrier import (
    apply_boundary_states,
    apply_branch_with_fallback,
    apply_carrier_cell_zone_conditions,
    apply_carrier_general,
    apply_carrier_initialization_settings,
    apply_carrier_models,
    apply_carrier_phase_materials,
    apply_carrier_solution_controls,
    apply_carrier_solution_methods,
    apply_material_states,
    apply_surface_tension_best_effort,
    build_intended_boundary_state,
    build_intended_materials,
    disable_dpm_after_setup,
    load_setup07_fallback_settings,
    prepare_setup07_fallback_payloads,
)
from pyansys_fluent.setup_dpm import (
    SEED_INJECTION_NAME,
    apply_dpm_injections,
    apply_dpm_model_settings,
    build_dpm_boundary_patch,
    build_injection_state,
    delete_injection_if_present,
    ensure_inert_particle_material,
    ensure_seed_injection_for_inert_materials,
)


@dataclass(frozen=True)
class CheckpointConfig:
    output_case: str
    output_data: str = ""
    initialized_case: str = ""
    initialized_data: str = ""
    checkpoint_interval: int = 1000
    report_interval: int = 100
    state_json: str = ""
    keep_history: bool = True


@dataclass(frozen=True)
class CarrierRunConfig:
    target_mesh: str = ""
    resume_case: str = ""
    resume_data: str = ""
    resume_state_json: str = ""
    resume_latest: bool = False
    setup_only: bool = False
    carrier_iterations: int = 0


@dataclass(frozen=True)
class DpmConfig:
    particle_material: str
    particle_density: float
    injection_surface_role: str
    droplet_diameters_um: tuple[float, ...]
    particle_mass_flow_rate: float
    streams_per_injection: int
    dpm_max_steps: int
    enable_turbulent_dispersion: bool
    turbulent_dispersion_tries: int
    wall_dpm_mode: str
    bottom_dpm_mode: str
    outlet_dpm_mode: str
    one_way_coupling: bool = True


def require_setup07_paths(run_config: CarrierRunConfig) -> None:
    has_resume = bool(run_config.resume_case or run_config.resume_data or run_config.resume_state_json or run_config.resume_latest)
    if has_resume and not (run_config.resume_case and run_config.resume_data):
        if not (run_config.resume_state_json or run_config.resume_latest):
            raise ValueError("Both --resume-case and --resume-data are required for resume mode")
    if not has_resume and not run_config.target_mesh:
        raise ValueError("--target-mesh is required unless --resume-case/--resume-data are provided")


def require_setup09a_paths(
    run_config: CarrierRunConfig,
    checkpoint_config: CheckpointConfig,
    post_dpm_iterations: int,
) -> None:
    has_resume = bool(run_config.resume_case or run_config.resume_data or run_config.resume_state_json or run_config.resume_latest)
    if has_resume and not (run_config.resume_case and run_config.resume_data):
        if not (run_config.resume_state_json or run_config.resume_latest):
            raise RuntimeError("Both --resume-case and --resume-data are required for resume mode.")
    if not has_resume and not run_config.target_mesh:
        raise RuntimeError("--target-mesh is required with --apply unless resume files are provided.")
    if not has_resume and not run_config.setup_only and run_config.carrier_iterations <= 0:
        raise RuntimeError(
            "09a is defined as a post-convergence DPM extension of setup 07. "
            "Provide --resume-case/--resume-data, a positive --carrier-iterations value, or use --setup-only."
        )
    if bool(checkpoint_config.output_case) ^ bool(checkpoint_config.output_data):
        raise RuntimeError("--output-case and --output-data must be provided together.")
    if bool(checkpoint_config.initialized_case) ^ bool(checkpoint_config.initialized_data):
        raise RuntimeError("--initialized-case and --initialized-data must be provided together.")
    if not has_resume and (run_config.setup_only or run_config.carrier_iterations > 0) and not (
        checkpoint_config.output_case and checkpoint_config.output_data
    ):
        raise RuntimeError(
            "--output-case and --output-data are required when rebuilding from mesh so "
            "mesh-based checkpoints and the final 09a case have a destination."
        )
    if post_dpm_iterations > 0 and not (checkpoint_config.output_case and checkpoint_config.output_data):
        raise RuntimeError(
            "--output-case and --output-data are required when --iterations > 0 "
            "so interrupt/final saves have a destination."
        )


def apply_setup07_carrier_from_mesh(solver) -> dict[str, str]:
    target_boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "target_boundary_conditions")
    if not isinstance(target_boundary_state, Mapping):
        raise RuntimeError("Could not inspect target boundary state")
    print_header("Target Boundary Summary")
    summarize_boundary_state(target_boundary_state)
    role_map = build_target_role_map(target_boundary_state)

    fallback_settings = load_setup07_fallback_settings()
    fallback_payloads = prepare_setup07_fallback_payloads(fallback_settings, target_boundary_state)

    intended_boundary = build_intended_boundary_state(role_map)
    intended_materials = build_intended_materials()

    apply_branch_with_fallback(
        "General Settings",
        lambda: apply_carrier_general(solver),
        lambda: try_action("apply_fallback_general", lambda: solver.settings.setup.general.set_state(fallback_payloads["fallback_general"])),
    )
    apply_branch_with_fallback(
        "Models",
        lambda: apply_carrier_models(solver),
        lambda: try_action("apply_fallback_models", lambda: solver.settings.setup.models.set_state(fallback_payloads["fallback_models"])),
    )
    apply_branch_with_fallback(
        "Materials",
        lambda: apply_material_states(solver, intended_materials),
        lambda: apply_material_states(solver, fallback_payloads["fallback_materials"]),
    )
    apply_branch_with_fallback("Phase Material Assignment", lambda: apply_carrier_phase_materials(solver), lambda: True)
    print_header("Surface Tension")
    if not apply_surface_tension_best_effort(solver):
        print("surface_tension: still not writable through API, manual Fluent check may be needed")
    apply_branch_with_fallback(
        "Cell Zone Conditions",
        lambda: apply_carrier_cell_zone_conditions(solver),
        lambda: try_action(
            "apply_fallback_cell_zones",
            lambda: solver.settings.setup.cell_zone_conditions.set_state(fallback_payloads["fallback_cell_zones"]),
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
        lambda: apply_boundary_states(solver, fallback_payloads["fallback_boundary"]),
    )
    apply_branch_with_fallback(
        "Solution Methods",
        lambda: apply_carrier_solution_methods(solver),
        lambda: try_action(
            "apply_fallback_solution_methods",
            lambda: solver.settings.solution.methods.set_state(fallback_payloads["fallback_solution"]["methods"]),
        ),
    )
    apply_branch_with_fallback(
        "Solution Controls",
        lambda: apply_carrier_solution_controls(solver),
        lambda: try_action(
            "apply_fallback_solution_controls",
            lambda: solver.settings.solution.controls.set_state(fallback_payloads["fallback_solution"]["controls"]),
        ),
    )
    apply_branch_with_fallback(
        "Initialization Settings",
        lambda: apply_carrier_initialization_settings(solver),
        lambda: try_action(
            "apply_fallback_initialization",
            lambda: solver.settings.solution.initialization.set_state(fallback_payloads["fallback_initialization"]),
        ),
    )
    print_header("Disable DPM For This Run")
    disable_dpm_after_setup(solver)
    return role_map


def run_setup07_carrier_recipe(
    solver,
    run_config: CarrierRunConfig,
    checkpoint_config: CheckpointConfig,
    *,
    iterations: int,
    skip_run: bool,
) -> dict[str, Any]:
    require_setup07_paths(run_config)
    role_map: dict[str, str] | None = None
    persistence = RunPersistence(
        output_case=checkpoint_config.output_case,
        output_data=checkpoint_config.output_data,
        checkpoint_interval=checkpoint_config.checkpoint_interval,
        report_interval=checkpoint_config.report_interval,
        state_json=checkpoint_config.state_json,
        keep_history=checkpoint_config.keep_history,
    )

    resume_mode = bool(
        run_config.resume_case
        or run_config.resume_data
        or run_config.resume_state_json
        or run_config.resume_latest
    )
    if resume_mode:
        resume_source = discover_latest_resume_source(
            checkpoint_config.output_case,
            checkpoint_config.output_data,
            resume_case=run_config.resume_case,
            resume_data=run_config.resume_data,
            resume_state_json=run_config.resume_state_json or checkpoint_config.state_json,
        )
        if not resume_source.is_available:
            raise RuntimeError("Resume mode was requested but no usable case/data pair was found.")
        load_resume_case_data(solver, resume_source.case_path, resume_source.data_path)
        completed_before_this_run = resume_source.completed_iterations
    else:
        completed_before_this_run = 0
        load_target_mesh(solver, run_config.target_mesh)
        role_map = apply_setup07_carrier_from_mesh(solver)
        initialize_case(solver)
        if checkpoint_config.initialized_case and checkpoint_config.initialized_data:
            write_case_data_pair(
                solver,
                checkpoint_config.initialized_case,
                checkpoint_config.initialized_data,
                "write_initialized_case_data",
            )

    run_iterations = 0 if skip_run else iterations
    iterate_case(
        solver,
        run_iterations,
        checkpoint_config.report_interval,
        checkpoint_config.checkpoint_interval,
        checkpoint_config.output_case,
        checkpoint_config.output_data,
        starting_completed_iterations=completed_before_this_run,
        persistence=persistence,
    )
    persistence.record_final(
        solver,
        completed_iterations=completed_before_this_run + run_iterations,
        total_iterations=completed_before_this_run + iterations,
        allow_case_only=False,
    )
    return {"role_map": role_map or {}}


def apply_09a_dpm_extension_recipe(
    solver,
    role_map: Mapping[str, str],
    dpm_config: DpmConfig,
) -> Mapping[str, Any]:
    print_header("Apply 09a DPM Materials")
    ensure_seed_injection_for_inert_materials(solver)
    if not ensure_inert_particle_material(
        solver,
        material_name=dpm_config.particle_material,
        density=dpm_config.particle_density,
    ):
        print("dpm_materials: SKIPPED after failure. Manual Fluent cleanup may still be required.")

    print_header("Apply 09a DPM Model Settings")
    if not apply_dpm_model_settings(
        solver,
        dpm_max_steps=dpm_config.dpm_max_steps,
        one_way_coupling=dpm_config.one_way_coupling,
    ):
        print("dpm_model_settings: PARTIAL/FAILED. Continuing so the case can still be saved.")

    print_header("Apply 09a DPM Boundary Fates")
    boundary_patch = build_dpm_boundary_patch(
        role_map=role_map,
        wall_mode=dpm_config.wall_dpm_mode,
        bottom_mode=dpm_config.bottom_dpm_mode,
        outlet_mode=dpm_config.outlet_dpm_mode,
    )
    if not apply_boundary_states(solver, boundary_patch):
        print("dpm_boundary_fates: PARTIAL/FAILED. Continuing so the case can still be saved.")

    print_header("Apply 09a DPM Injections")
    injections = build_injection_state(
        role_map,
        particle_material=dpm_config.particle_material,
        injection_surface_role=dpm_config.injection_surface_role,
        droplet_diameters_um=dpm_config.droplet_diameters_um,
        particle_mass_flow_rate=dpm_config.particle_mass_flow_rate,
        enable_turbulent_dispersion=dpm_config.enable_turbulent_dispersion,
        turbulent_dispersion_tries=dpm_config.turbulent_dispersion_tries,
    )
    if not apply_dpm_injections(solver, injections):
        print("dpm_injections: PARTIAL/FAILED. Continuing so the case can still be saved.")
    delete_injection_if_present(solver, SEED_INJECTION_NAME)
    return injections


def run_setup09a_dpm_extension_recipe(
    solver,
    run_config: CarrierRunConfig,
    checkpoint_config: CheckpointConfig,
    dpm_config: DpmConfig,
    *,
    post_dpm_iterations: int,
) -> dict[str, Any]:
    require_setup09a_paths(run_config, checkpoint_config, post_dpm_iterations)
    injections: Mapping[str, Any] = {}
    persistence = RunPersistence(
        output_case=checkpoint_config.output_case,
        output_data=checkpoint_config.output_data,
        checkpoint_interval=checkpoint_config.checkpoint_interval,
        report_interval=checkpoint_config.report_interval,
        state_json=checkpoint_config.state_json,
        keep_history=checkpoint_config.keep_history,
    )

    resume_mode = bool(
        run_config.resume_case
        or run_config.resume_data
        or run_config.resume_state_json
        or run_config.resume_latest
    )
    if resume_mode:
        resume_source = discover_latest_resume_source(
            checkpoint_config.output_case,
            checkpoint_config.output_data,
            resume_case=run_config.resume_case,
            resume_data=run_config.resume_data,
            resume_state_json=run_config.resume_state_json or checkpoint_config.state_json,
        )
        if not resume_source.is_available:
            raise RuntimeError("Resume mode was requested but no usable case/data pair was found.")
        load_resume_case_data(solver, resume_source.case_path, resume_source.data_path)
        completed_before_this_run = resume_source.completed_iterations
        boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "resume_boundary_conditions")
        if not isinstance(boundary_state, Mapping):
            raise RuntimeError("Could not inspect resumed boundary state")
        print_header("Resume Boundary Summary")
        summarize_boundary_state(boundary_state)
        role_map = build_target_role_map(boundary_state)
        injections = apply_09a_dpm_extension_recipe(solver, role_map, dpm_config)
    else:
        completed_before_this_run = 0
        load_target_mesh(solver, run_config.target_mesh)
        role_map = apply_setup07_carrier_from_mesh(solver)
        if run_config.setup_only:
            print_header("Skip Initialization And Carrier Iterations")
            print("setup_only: carrier field will not be initialized or iterated before DPM.", flush=True)
        else:
            initialize_case(solver)
            if checkpoint_config.initialized_case and checkpoint_config.initialized_data:
                write_case_data_pair(
                    solver,
                    checkpoint_config.initialized_case,
                    checkpoint_config.initialized_data,
                    "write_initialized_case_data",
                )
            if run_config.carrier_iterations > 0:
                iterate_case(
                    solver,
                    run_config.carrier_iterations,
                    checkpoint_config.report_interval,
                    checkpoint_config.checkpoint_interval,
                    checkpoint_config.output_case,
                    checkpoint_config.output_data,
                    starting_completed_iterations=completed_before_this_run,
                    persistence=persistence,
                )
        injections = apply_09a_dpm_extension_recipe(solver, role_map, dpm_config)

    if post_dpm_iterations > 0:
        iterate_case(
            solver,
            post_dpm_iterations,
            checkpoint_config.report_interval,
            checkpoint_config.checkpoint_interval,
            checkpoint_config.output_case,
            checkpoint_config.output_data,
            starting_completed_iterations=completed_before_this_run,
            persistence=persistence,
        )

    if checkpoint_config.output_case and checkpoint_config.output_data:
        if run_config.setup_only:
            persistence.record_case_only(
                solver,
                completed_iterations=completed_before_this_run + post_dpm_iterations,
                total_iterations=completed_before_this_run + post_dpm_iterations,
            )
        else:
            persistence.record_final(
                solver,
                completed_iterations=completed_before_this_run + post_dpm_iterations,
                total_iterations=completed_before_this_run + post_dpm_iterations,
                allow_case_only=False,
            )

    final_boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "final_boundary_conditions")
    return {
        "role_map": dict(role_map),
        "final_boundary_summary": build_compact_boundary_summary(final_boundary_state) if isinstance(final_boundary_state, Mapping) else {},
        "created_injections": sorted(injections.keys()),
    }

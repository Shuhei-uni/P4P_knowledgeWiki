#!/usr/bin/env python3
"""Discrete phase model helpers for setup09a-style extensions."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence
from typing import Any

from pyansys_fluent.common import try_action
from pyansys_fluent.dependency_workflow import (
    classify_failure,
    safe_allowed_values,
    safe_child_names,
    safe_command_names,
)


SEED_INJECTION_NAME = "__codex_seed_default_injection__"


@dataclass(frozen=True)
class InjectionSurfaceBindResult:
    success: bool
    strategy_name: str = ""
    readback: Any = None
    category: str = "unknown"
    error_log: list[str] = field(default_factory=list)
    probe: dict[str, Any] = field(default_factory=dict)


def um_to_microns_text(value_um: float) -> str:
    if value_um.is_integer():
        return f"{int(value_um)}"
    return f"{value_um:g}"


def resolve_particle_material_name(source_material: str, override: str = "") -> str:
    override = override.strip()
    if override:
        return override

    source_material = source_material.strip()
    if not source_material:
        raise ValueError("source_material must be non-empty when no override is provided")

    return f"dpm-{source_material}"


def ensure_inert_particle_material(
    solver,
    material_name: str,
    density: float,
    *,
    strict: bool = False,
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

    ok = try_action(
        f"material_prepare_inert_particle.{material_name}",
        lambda: inert_branch.create(name=material_name),
        critical=strict,
    )

    try:
        existing = set(inert_branch.get_object_names())
    except Exception as exc:
        print(f"inert_particle_names_postcreate: FAILED -> {exc}")
        existing = set()

    if material_name not in existing:
        print(
            f"inert particle material '{material_name}' is still unavailable after create()."
        )
        return False

    return bool(ok and try_action(
        f"material_apply_inert_particle.{material_name}",
        lambda: inert_branch[material_name].set_state(
            {
                "name": material_name,
                "chemical_formula": "",
                "density": {"option": "constant", "value": density},
            }
        ),
        critical=strict,
    ))


def ensure_seed_injection_for_inert_materials(
    solver,
    seed_name: str = SEED_INJECTION_NAME,
    *,
    strict: bool = False,
) -> bool:
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
        critical=strict,
    )


def bootstrap_inert_particle_material_branch(
    solver,
    *,
    material_name: str,
    density: float,
    seed_name: str = SEED_INJECTION_NAME,
    strict: bool = False,
) -> bool:
    ok = True
    ok &= ensure_seed_injection_for_inert_materials(solver, seed_name=seed_name, strict=strict)
    ok &= ensure_inert_particle_material(
        solver,
        material_name=material_name,
        density=density,
        strict=strict,
    )
    return ok


def enable_dpm_model_best_effort(solver, *, strict: bool = False) -> bool:
    dpm = solver.settings.setup.models.discrete_phase
    try:
        dpm.injections.get_object_names()
        print("enable_dpm_model_precheck: OK -> discrete_phase branch already active")
        return True
    except Exception:
        pass

    return try_action(
        "enable_dpm_model_attr_enabled",
        lambda: setattr(dpm, "enabled", True),
        critical=strict,
    )


def delete_injection_if_present(solver, injection_name: str) -> bool:
    branch = solver.settings.setup.models.discrete_phase.injections
    try:
        names = set(branch.get_object_names())
    except Exception:
        names = set()
    if injection_name not in names:
        return True
    if try_action(f"delete_injection_{injection_name}_delitem", lambda: branch.__delitem__(injection_name)):
        return True
    return try_action(f"delete_injection_{injection_name}_delete", lambda: branch.delete(name_list=[injection_name]))


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
                "phase": {"mixture": {"dpm": {"discrete_phase_bc_type": bottom_mode}}},
            },
        },
    }


def build_injection_state(
    role_map: Mapping[str, str],
    *,
    particle_material: str,
    injection_surface_role: str,
    droplet_diameters_um: tuple[float, ...],
    particle_mass_flow_rate: float,
    enable_turbulent_dispersion: bool,
    turbulent_dispersion_tries: int,
) -> dict[str, Any]:
    injection_surface = zone_name_for_role(role_map, injection_surface_role)
    injections: dict[str, Any] = {}
    for diameter_um in droplet_diameters_um:
        name = f"dpm-{um_to_microns_text(diameter_um)}um"
        injections[name] = {
            "name": name,
            "injection_type": {"option": "surface"},
            "initial_values": {
                "reference_frame": "global",
                "location": {
                    "injection_surfaces": [injection_surface],
                    "randomized_positions_enabled": False,
                },
                "mass_flow_rate": {"total_flow_rate": particle_mass_flow_rate},
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
                    "enabled": enable_turbulent_dispersion,
                    "random_eddy_lifetime": False,
                    "number_of_tries": turbulent_dispersion_tries,
                    "time_scale_constant": 0.15,
                },
                "particle_rotation": {"enabled": False},
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
            "particle_type": "inert",
            "material": particle_material,
        }
    return injections


def apply_dpm_model_settings(
    solver,
    *,
    dpm_max_steps: int,
    one_way_coupling: bool = True,
    strict: bool = False,
) -> bool:
    dpm = solver.settings.setup.models.discrete_phase
    required_ok = True
    required_ok &= enable_dpm_model_best_effort(solver, strict=strict)
    if one_way_coupling:
        required_ok &= try_action(
            "set_dpm_interaction_with_continuous_phase_off",
            lambda: setattr(dpm.general_settings.interaction, "enabled", False),
            critical=strict,
        )
    required_ok &= try_action(
        "set_dpm_contour_plotting_none",
        lambda: setattr(dpm.general_settings, "contour_plotting", "none"),
        critical=strict,
    )
    required_ok &= try_action(
        "set_dpm_max_steps",
        lambda: setattr(dpm.tracking, "max_num_steps", dpm_max_steps),
        critical=strict,
    )
    required_ok &= try_action(
        "set_dpm_step_size_controls",
        lambda: dpm.tracking.step_size_controls.set_state(
            {"option": "step-length-factor", "step_length_factor": 5}
        ),
        critical=strict,
    )

    # Optional force settings. These are version/build dependent, so they should
    # not make the whole DPM setup fail.
    physical_models = getattr(dpm, "physical_models", None)
    if physical_models is None:
        print("DPM physical_models branch unavailable; skipping optional particle force settings.")
        return required_ok

    # Older/archive-style path.
    particle_forces = getattr(physical_models, "particle_forces", None)
    if particle_forces is not None:
        try_action(
            "set_dpm_pressure_force_best_effort",
            lambda: setattr(particle_forces, "pressure_force_enabled", True),
            critical=strict,
        )

        virtual_mass_force = getattr(particle_forces, "virtual_mass_force", None)
        if virtual_mass_force is not None:
            try_action(
                "set_dpm_virtual_mass_force_best_effort_particle_forces",
                lambda: virtual_mass_force.set_state(
                    {"enabled": True, "virtual_mass_factor": 0.5}
                ),
                critical=strict,
            )
    else:
        print("DPM particle_forces branch unavailable; skipping pressure-force setting.")

    # Fluent 2024 R2 appears to expose virtual_mass_force directly here.
    direct_virtual_mass_force = getattr(physical_models, "virtual_mass_force", None)
    if direct_virtual_mass_force is not None:
        try_action(
            "set_dpm_virtual_mass_force_best_effort_direct",
            lambda: direct_virtual_mass_force.set_state(
                {"enabled": True, "virtual_mass_factor": 0.5}
            ),
            critical=strict,
        )
    else:
        print("DPM virtual_mass_force branch unavailable; skipping virtual-mass setting.")

    return required_ok


def reacquire_injection(branch, injection_name: str):
    return branch[injection_name]


def get_named_object_names(branch: Any) -> list[str]:
    """Return names from a PyFluent named-object branch across API versions."""
    for attr in ("get_object_names", "list", "object_names"):
        try:
            value = getattr(branch, attr)
            names = value() if callable(value) else value
            if isinstance(names, (list, tuple, set)):
                return [str(name) for name in names]
        except Exception:
            pass
    return []


def capture_surface_bind_probe(injection: Any, *, injection_name: str) -> dict[str, Any]:
    """Capture the live location/surface branch without making probe failures fatal."""
    probe: dict[str, Any] = {
        "injection_name": injection_name,
        "injection_type_state": None,
        "location_state": None,
        "location_child_names": [],
        "location_command_names": [],
        "surface_leaf_present": False,
        "surface_leaf_state": None,
        "surface_leaf_allowed_values": [],
        "surface_leaf_child_names": [],
        "surface_leaf_command_names": [],
        "errors": [],
    }

    try:
        probe["injection_type_state"] = injection.injection_type.get_state()
    except Exception as exc:
        probe["errors"].append(f"injection_type_state: {type(exc).__name__}: {exc}")

    try:
        location = injection.initial_values.location
    except Exception as exc:
        probe["errors"].append(f"location_lookup: {type(exc).__name__}: {exc}")
        return probe

    try:
        probe["location_state"] = location.get_state()
    except Exception as exc:
        probe["errors"].append(f"location_state: {type(exc).__name__}: {exc}")

    probe["location_child_names"] = safe_child_names(location)
    probe["location_command_names"] = safe_command_names(location)

    try:
        surf_leaf = getattr(location, "injection_surfaces")
    except Exception as exc:
        probe["errors"].append(f"injection_surfaces_lookup: {type(exc).__name__}: {exc}")
        return probe

    if surf_leaf is None:
        probe["errors"].append("injection_surfaces_lookup: leaf unavailable")
        return probe

    probe["surface_leaf_present"] = True
    try:
        probe["surface_leaf_state"] = surf_leaf.get_state()
    except Exception as exc:
        probe["errors"].append(f"surface_leaf_state: {type(exc).__name__}: {exc}")

    probe["surface_leaf_allowed_values"] = safe_allowed_values(surf_leaf)
    probe["surface_leaf_child_names"] = safe_child_names(surf_leaf)
    probe["surface_leaf_command_names"] = safe_command_names(surf_leaf)
    return probe


def read_injection_surface_state(injection) -> Any:
    try:
        return injection.initial_values.location.get_state()
    except Exception as exc:
        return {"readback_error": str(exc)}


def inspect_injection_surface_leaf(injection, *, injection_name: str) -> tuple[bool, list[str]]:
    error_log: list[str] = []

    try:
        location = injection.initial_values.location
    except Exception as exc:
        print(f"{injection_name}_location: unavailable -> {exc}", flush=True)
        return False, [f"{injection_name}_location_lookup: {exc}"]

    try:
        location_active = bool(location.is_active())
    except Exception as exc:
        location_active = False
        error_log.append(f"{injection_name}_location_is_active: {exc}")

    try:
        surf_leaf = getattr(location, "injection_surfaces", None)
    except Exception as exc:
        surf_leaf = None
        error_log.append(f"{injection_name}_surface_leaf_lookup: {exc}")
    if surf_leaf is None:
        print(f"{injection_name}_surface_leaf: unavailable", flush=True)
        return False, error_log

    try:
        surf_active = bool(surf_leaf.is_active())
    except Exception as exc:
        surf_active = False
        error_log.append(f"{injection_name}_surface_leaf_is_active: {exc}")

    try:
        allowed = list(surf_leaf.allowed_values())
    except Exception as exc:
        allowed = []
        error_log.append(f"{injection_name}_surface_leaf_allowed_values: {exc}")

    print(f"{injection_name}_location_active: {location_active}", flush=True)
    print(f"{injection_name}_surface_leaf_active: {surf_active}", flush=True)
    print(f"{injection_name}_surface_allowed_values: {allowed}", flush=True)
    return bool(location_active and surf_active), error_log


def escape_scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def try_location_object_binding(
    injection,
    *,
    injection_name: str,
    surface_name: str,
    randomized_positions_enabled: bool | None = None,
) -> tuple[bool, dict[str, Any] | None, list[str]]:
    error_log: list[str] = []

    try:
        current_state = injection.initial_values.location.get_state()
    except Exception as exc:
        current_state = {}
        error_log.append(f"{injection_name}_location_state_read_failed: {exc}")

    if isinstance(current_state, Mapping):
        desired_state: dict[str, Any] = dict(current_state)
    else:
        desired_state = {}

    desired_state["injection_surfaces"] = [surface_name]
    if randomized_positions_enabled is None:
        desired_state.setdefault("randomized_positions_enabled", False)
    else:
        desired_state["randomized_positions_enabled"] = randomized_positions_enabled

    if not try_action(
        f"{injection_name}_location_set_state",
        lambda: injection.initial_values.location.set_state(desired_state),
    ):
        error_log.append(f"{injection_name}_location_set_state failed")
        return False, None, error_log

    try:
        readback = injection.initial_values.location.get_state()
    except Exception as exc:
        readback = None
        error_log.append(f"{injection_name}_location_state_readback_failed: {exc}")

    surfaces = readback.get("injection_surfaces") if isinstance(readback, Mapping) else None
    if surfaces in (False, None, []):
        error_log.append(
            f"{injection_name}_location_readback_missing_surface: requested={surface_name!r} readback={readback!r}"
        )
        return False, readback, error_log
    if isinstance(surfaces, Sequence) and not isinstance(surfaces, (str, bytes)) and surface_name not in surfaces:
        error_log.append(
            f"{injection_name}_location_readback_mismatch: requested={surface_name!r} readback={surfaces!r}"
        )
        return False, readback, error_log
    if isinstance(surfaces, str) and surfaces != surface_name:
        error_log.append(
            f"{injection_name}_location_readback_mismatch: requested={surface_name!r} readback={surfaces!r}"
        )
        return False, readback, error_log

    return True, readback, error_log


def bind_surface_injection_location_or_fail(
    solver,
    branch,
    injection_name: str,
    surface_name: str,
    *,
    strict: bool = False,
) -> InjectionSurfaceBindResult:
    injection = reacquire_injection(branch, injection_name)
    error_log: list[str] = []
    probe: dict[str, Any] = {}

    print(f"{injection_name}_set_injection_type_surface: starting", flush=True)
    if not try_action(
        f"{injection_name}_injection_type_surface",
        lambda: setattr(injection.injection_type, "option", "surface"),
    ):
        message = f"{injection_name}_injection_type_surface failed"
        return InjectionSurfaceBindResult(
            success=False,
            category=classify_failure(message),
            error_log=[message],
            probe=capture_surface_bind_probe(injection, injection_name=injection_name),
        )

    injection = reacquire_injection(branch, injection_name)
    leaf_active, inspect_errors = inspect_injection_surface_leaf(injection, injection_name=injection_name)
    error_log.extend(inspect_errors)
    probe = capture_surface_bind_probe(injection, injection_name=injection_name)

    try:
        location = injection.initial_values.location
        surf_leaf = getattr(location, "injection_surfaces")
    except Exception as exc:
        error_log.append(f"{injection_name}_surface_leaf_lookup_failed: {exc}")
        return InjectionSurfaceBindResult(
            success=False,
            category=classify_failure(exc),
            error_log=error_log,
            probe=probe,
        )

    if not leaf_active:
        print(f"{injection_name}_surface_bind: WARNING -> surface leaf is not active", flush=True)

    try:
        allowed = list(surf_leaf.allowed_values())
    except Exception as exc:
        allowed = []
        error_log.append(f"{injection_name}_surface_allowed_values_failed: {exc}")

    if allowed and surface_name not in allowed:
        message = f"{surface_name!r} is not an allowed DPM injection surface. Allowed values: {allowed}"
        if strict:
            raise RuntimeError(message)
        error_log.append(message)
        return InjectionSurfaceBindResult(
            success=False,
            category="invalid value/format issue",
            readback={"allowed_values": allowed},
            error_log=error_log,
            probe=probe,
        )

    location_bind_ok, location_readback, location_errors = try_location_object_binding(
        injection,
        injection_name=injection_name,
        surface_name=surface_name,
    )
    error_log.extend(location_errors)
    if location_bind_ok:
        print(f"{injection_name}_location_set_state_readback: {location_readback}", flush=True)
        return InjectionSurfaceBindResult(
            success=True,
            strategy_name="location_set_state",
            readback={"location": location_readback},
            category="unknown",
            error_log=error_log,
            probe=capture_surface_bind_probe(reacquire_injection(branch, injection_name), injection_name=injection_name),
        )

    if strict:
        return InjectionSurfaceBindResult(
            success=False,
            category=classify_failure("; ".join(error_log)),
            readback=location_readback,
            error_log=error_log,
            probe=capture_surface_bind_probe(injection, injection_name=injection_name),
        )

    set_strategies = [
        (
            "surface_leaf_set_list",
            lambda: surf_leaf.set_state([surface_name]),
        ),
        (
            "surface_leaf_set_scalar",
            lambda: surf_leaf.set_state(surface_name),
        ),
        (
            "surface_leaf_set_value_list",
            lambda: setattr(surf_leaf, "value", [surface_name]),
        ),
        (
            "surface_leaf_set_value_scalar",
            lambda: setattr(surf_leaf, "value", surface_name),
        ),
    ]

    setter_ok = False
    for strategy_name, setter in set_strategies:
        label = f"{injection_name}_{strategy_name}"
        if try_action(label, setter):
            setter_ok = True
            break
        error_log.append(f"{label} failed")

    if not setter_ok:
        return InjectionSurfaceBindResult(
            success=False,
            category="PyFluent wrapper limitation",
            error_log=error_log,
            probe=capture_surface_bind_probe(injection, injection_name=injection_name),
        )

    injection = reacquire_injection(branch, injection_name)
    leaf_readback = None
    try:
        leaf_readback = injection.initial_values.location.injection_surfaces.get_state()
    except Exception as exc:
        leaf_readback = {"readback_error": str(exc)}
        error_log.append(f"{injection_name}_surface_leaf_readback: {exc}")

    try:
        location_readback = injection.initial_values.location.get_state()
    except Exception as exc:
        location_readback = {"readback_error": str(exc)}
        error_log.append(f"{injection_name}_location_readback: {exc}")

    print(f"{injection_name}_surface_leaf_readback: {leaf_readback}", flush=True)
    print(f"{injection_name}_location_readback: {location_readback}", flush=True)

    surfaces = location_readback.get("injection_surfaces") if isinstance(location_readback, Mapping) else None
    if not leaf_readback or surfaces in (False, None, []):
        error_log.append(
            f"{injection_name}_surface_bind_readback_missing_surface: requested={surface_name!r} readback={location_readback!r}"
        )
        return InjectionSurfaceBindResult(
            success=False,
            category="PyFluent wrapper limitation",
            readback={"leaf": leaf_readback, "location": location_readback},
            error_log=error_log,
            probe=capture_surface_bind_probe(injection, injection_name=injection_name),
        )

    return InjectionSurfaceBindResult(
        success=True,
        strategy_name="surface_leaf",
        readback={"leaf": leaf_readback, "location": location_readback},
        category="unknown",
        error_log=error_log,
        probe=capture_surface_bind_probe(injection, injection_name=injection_name),
    )


def apply_single_dpm_injection(
    solver,
    branch,
    injection_name: str,
    state: Mapping[str, Any],
    *,
    strict: bool = False,
) -> bool:
    ok = True
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
            injection = reacquire_injection(branch, injection_name)
            injection_surface = location.get("injection_surfaces")
            randomize = bool(location.get("randomized_positions_enabled", False))
            surface_names: list[str] = []
            if isinstance(injection_surface, str) and injection_surface.strip():
                surface_names = [injection_surface.strip()]
            elif isinstance(injection_surface, Sequence) and not isinstance(injection_surface, (str, bytes)):
                surface_names = [str(surface).strip() for surface in injection_surface if str(surface).strip()]

            if surface_names:
                bind_result = bind_surface_injection_location_or_fail(
                    solver=solver,
                    branch=branch,
                    injection_name=injection_name,
                    surface_name=surface_names[0],
                    strict=strict,
                )
                if not bind_result.success:
                    ok = False
                    if strict:
                        return False
                    print(
                        f"{injection_name}_location_bind: WARNING -> injection surface was not bound. "
                        f"category={bind_result.category}; continuing in non-strict mode.",
                        flush=True,
                    )
                    if bind_result.readback is not None:
                        print(f"{injection_name}_location_bind_readback: {bind_result.readback}", flush=True)
                    if bind_result.error_log:
                        print(f"{injection_name}_location_bind_errors: {bind_result.error_log}", flush=True)
            ok &= try_action(
                f"{injection_name}_randomized_positions_enabled",
                lambda value=randomize: setattr(
                    injection.initial_values.location,
                    "randomized_positions_enabled",
                    value,
                ),
            )

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

    for label, payload in (
        ("mass_flow_rate", initial_values.get("mass_flow_rate", {})),
        ("velocity", initial_values.get("velocity", {})),
        ("particle_size", initial_values.get("particle_size", {})),
        ("angular_velocity", initial_values.get("angular_velocity", {})),
    ):
        if isinstance(payload, Mapping) and payload:
            ok &= try_action(
                f"{injection_name}_{label}",
                lambda name=label, value=dict(payload): getattr(injection.initial_values, name).set_state(value),
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

        for label, payload in (
            ("turbulent_dispersion", physical_models.get("turbulent_dispersion", {})),
            ("particle_rotation", physical_models.get("particle_rotation", {})),
            ("custom_laws", physical_models.get("custom_laws", {})),
        ):
            if isinstance(payload, Mapping):
                ok &= try_action(
                    f"{injection_name}_{label}",
                    lambda name=label, value=dict(payload): getattr(injection.physical_models, name).set_state(value),
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

    return ok


def apply_dpm_injections(solver, injection_state: Mapping[str, Any], *, strict: bool = False) -> bool:
    branch = solver.settings.setup.models.discrete_phase.injections
    ok = True
    for name, payload in injection_state.items():
        existing_names = set(get_named_object_names(branch))
        if name in existing_names:
            print(f"create_injection_{name}: SKIPPED -> already exists", flush=True)
        else:
            created = try_action(
                f"create_injection_{name}",
                lambda injection_name=name: branch.create(name=injection_name),
                critical=strict,
            )
            ok &= created
            if not created and strict:
                return False
        ok &= apply_single_dpm_injection(
            solver=solver,
            branch=branch,
            injection_name=name,
            state=payload,
            strict=strict,
        )
        if not ok and strict:
            return False
    return ok

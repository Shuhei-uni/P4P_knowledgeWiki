#!/usr/bin/env python3
"""Read-only EWF/DPM configuration audit."""

from __future__ import annotations

from typing import Any

from pyansys_fluent.dependency_workflow import safe_object_names
from pyansys_fluent.ewf_core import (
    as_bool,
    child_by_alias,
    find_values_by_key,
    first_scalar_match,
    get_state,
)


def audit_ewf_dpm_settings(solver: Any) -> dict[str, Any]:
    warnings: list[str] = []
    try:
        models = solver.settings.setup.models
        models_state = get_state(models, "setup.models", warnings)
    except Exception as exc:
        models_state = None
        warnings.append(f"setup.models unavailable: {type(exc).__name__}: {exc}")

    try:
        boundaries = solver.settings.setup.boundary_conditions
        boundaries_state = get_state(boundaries, "setup.boundary_conditions", warnings)
    except Exception as exc:
        boundaries_state = None
        boundaries = None
        warnings.append(f"boundary_conditions unavailable: {type(exc).__name__}: {exc}")

    ewf_state = None
    dpm_state = None
    try:
        ewf_state = get_state(
            solver.settings.setup.models.eulerian_wall_film,
            "setup.models.eulerian_wall_film",
            warnings,
        )
    except Exception as exc:
        warnings.append(f"EWF branch unavailable: {type(exc).__name__}: {exc}")
    try:
        dpm_state = get_state(
            solver.settings.setup.models.discrete_phase,
            "setup.models.discrete_phase",
            warnings,
        )
    except Exception as exc:
        warnings.append(f"DPM branch unavailable: {type(exc).__name__}: {exc}")

    source = ewf_state if ewf_state is not None else models_state
    mechanisms = {
        "ewf_enabled": as_bool(
            first_scalar_match(source, ("enabled", "eulerian_wall_film", "eulerian_film_model"))
        ),
        "dpm_coupling": as_bool(first_scalar_match(source, ("dpm_coupling", "dpm-coupling"))),
        "particle_splashing": as_bool(
            first_scalar_match(source, ("particle_splashing", "particle-splashing"))
        ),
        "edge_separation": as_bool(
            first_scalar_match(source, ("edge_separation", "edge-separation"))
        ),
        "particle_stripping": as_bool(
            first_scalar_match(source, ("particle_stripping", "particle-stripping"))
        ),
        "solve_momentum": as_bool(
            first_scalar_match(source, ("solve_momentum", "solve-momentum"))
        ),
        "film_material": first_scalar_match(source, ("film_material", "film-material")),
        "max_courant_number": first_scalar_match(
            source, ("max_courant_number", "maximum_courant_number", "max-courant-number")
        ),
        "dpm_per_film_steps": first_scalar_match(
            source, ("dpm_per_film_steps", "dpm-per-film-steps")
        ),
        "dpm_relaxation_factor": first_scalar_match(
            source, ("relaxation_factor", "dpm_relaxation_factor")
        ),
    }

    wall_zones: list[dict[str, Any]] = []
    active_film_walls: list[str] = []
    if boundaries is not None:
        wall_branch, _ = child_by_alias(boundaries, ("wall",))
        if wall_branch is not None:
            for name in safe_object_names(wall_branch):
                try:
                    state = get_state(wall_branch[name], f"wall.{name}", warnings)
                except Exception as exc:
                    state = None
                    warnings.append(f"wall {name} unavailable: {type(exc).__name__}: {exc}")
                enabled_value = first_scalar_match(
                    state,
                    (
                        "eulerian_film_wall",
                        "eulerian_wall_film",
                        "eulerian-film-wall",
                        "wall_film_enabled",
                    ),
                )
                enabled = as_bool(enabled_value)
                if enabled is True:
                    active_film_walls.append(str(name))
                wall_zones.append(
                    {
                        "name": str(name),
                        "eulerian_film_wall": enabled,
                        "impingement_model": first_scalar_match(
                            state, ("impingement_model", "impingement-model")
                        ),
                        "dpm_wall_splash": as_bool(
                            first_scalar_match(state, ("dpm_wall_splash", "dpm-wall-splash"))
                        ),
                        "number_of_splashed_particles": first_scalar_match(
                            state,
                            ("number_of_splashed_particles", "number-of-splashed-particles"),
                        ),
                        "allow_boundary_separation": as_bool(
                            first_scalar_match(
                                state,
                                ("allow_boundary_separation", "allow-boundary-separation"),
                            )
                        ),
                        "state": state,
                    }
                )

    udf_matches = find_values_by_key(
        dpm_state,
        (
            "impingement_model",
            "film_regime",
            "splashing_distribution",
            "body_force",
            "scalar_update",
            "source",
            "dpm_time_step",
        ),
    )

    return {
        "mechanisms": mechanisms,
        "active_film_walls": active_film_walls,
        "wall_zones": wall_zones,
        "dpm_udf_matches": udf_matches,
        "raw_states": {
            "eulerian_wall_film": ewf_state,
            "discrete_phase": dpm_state,
            "models": models_state,
            "boundary_conditions": boundaries_state,
        },
        "warnings": warnings,
    }

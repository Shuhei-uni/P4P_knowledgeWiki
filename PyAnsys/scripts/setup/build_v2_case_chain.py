#!/usr/bin/env python3
"""Build the provisional 09cV2 -> 010V2d case-only chain on Fluent server 3.

This script intentionally does not initialize, iterate, read data, or write data.
It uses the already-loaded 09c case in the live Fluent session and saves only
case files. Any missing path, unsupported option, or readback mismatch raises
``UnknownSetup`` and stops the chain immediately.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import safe_allowed_values, safe_child_names  # noqa: E402
from pyansys_fluent.setup_dpm import ensure_inert_particle_material  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


LIQUID_TOTAL = 116.92
VAPOR_TOTAL = 80.69
DPM_FRACTION = 0.05
DPM_TOTAL = LIQUID_TOTAL * DPM_FRACTION
EULERIAN_LIQUID = LIQUID_TOTAL - DPM_TOTAL
FILM_MATERIAL = "water-liquid-at-psep"
DPM_MATERIAL = "water-liquid-at-psep-dpm"
SERVER_ID = "3"

CASE_NAMES = {
    "09cV2": "09cV2-fDPM-05pct.cas.h5",
    "010V2": "010V2-ewf-deposition-control.cas.h5",
    "010V2a": "010V2a-ewf-splash.cas.h5",
    "010V2b": "010V2b-ewf-edge-separation.cas.h5",
    "010V2c": "010V2c-ewf-particle-stripping.cas.h5",
    "010V2d": "010V2d-ewf-combined.cas.h5",
}

INJECTION_LABELS = {
    "injection-5-micron": "5um",
    "injection-28-micron": "28um",
    "injection-56-micron": "56um",
    "injection-112-micron": "112um",
    "injection-168-micron": "168um",
    "injection-348-micron": "348um",
}


class UnknownSetup(RuntimeError):
    """A required live Fluent fact or readback is unknown."""


def fail(message: str) -> None:
    raise UnknownSetup(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def state_value(state: dict[str, Any], *keys: str) -> Any:
    current: Any = state
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def finite_float(value: Any, label: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        fail(f"{label} is not numeric: {value!r}")
        raise exc


def object_names(branch: Any) -> list[str]:
    try:
        return sorted(str(name) for name in branch.get_object_names())
    except Exception as exc:
        fail(f"Could not read object names for {branch}: {type(exc).__name__}: {exc}")
        return []


def read_injections(solver: Any) -> dict[str, dict[str, Any]]:
    state = safe_get_state(solver.settings.setup.models.discrete_phase.injections, "injections")
    require(isinstance(state, dict), "DPM injection state is unavailable")
    return state


def read_source_state(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    model_state = safe_get_state(setup.models, "models")
    require(state_value(model_state, "multiphase", "models") == "mixture", "Loaded case is not Mixture")
    require(state_value(model_state, "multiphase", "number_of_phases") == 2, "Loaded case does not expose two phases")

    dpm_state = state_value(model_state, "discrete_phase")
    require(isinstance(dpm_state, dict), "Loaded case has no readable DPM state")
    interaction = state_value(dpm_state, "general_settings", "interaction")
    require(state_value(interaction, "enabled") is True, "09c source DPM interaction is not enabled")
    require(state_value(interaction, "update_sources_every_iteration") is True, "09c source DPM source update is not every iteration")
    require(int(state_value(interaction, "iteration_interval")) == 1, "09c source DPM iteration interval is not 1")

    boundary_state = safe_get_state(setup.boundary_conditions.mass_flow_inlet, "mass_flow_inlet")
    liquid_flow = state_value(boundary_state, "liquidinlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value")
    vapor_flow = state_value(boundary_state, "steaminlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value")
    require(abs(finite_float(liquid_flow, "liquidinlet flow") - LIQUID_TOTAL) < 1e-8, "09c liquid inlet is not 116.92 kg/s")
    require(abs(finite_float(vapor_flow, "steaminlet flow") - VAPOR_TOTAL) < 1e-8, "09c vapor inlet is not 80.69 kg/s")

    injections = read_injections(solver)
    require(set(injections) == set(INJECTION_LABELS), f"Unexpected 09c injection names: {sorted(injections)}")
    total = 0.0
    for name, payload in injections.items():
        surfaces = state_value(payload, "initial_values", "location", "injection_surfaces")
        require(surfaces == ["steaminlet"], f"{name} is not bound to steaminlet: {surfaces!r}")
        flow = finite_float(state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"), f"{name} flow")
        total += flow
    require(abs(total - 29.22) < 1e-8, f"09c DPM total is {total}, expected 29.22 kg/s")

    material_state = safe_get_state(setup.materials, "materials")
    fluid = state_value(material_state, "fluid", FILM_MATERIAL)
    require(isinstance(fluid, dict), f"Film fluid material {FILM_MATERIAL!r} is unavailable")
    density = finite_float(state_value(fluid, "density", "value"), f"{FILM_MATERIAL} density")

    return {
        "model_state": model_state,
        "boundary_state": boundary_state,
        "injections": injections,
        "source_dpm_total": total,
        "film_density": density,
    }


def check_targets_absent(solver: Any, *, allow_existing_09cV2: bool = False) -> None:
    targets = [
        name
        for key, name in CASE_NAMES.items()
        if not (allow_existing_09cV2 and key == "09cV2")
    ]
    existing = [name for name in targets if remote_file_exists(solver, name)]
    require(not existing, f"Refusing to overwrite existing remote case files: {existing}")


def set_readback(obj: Any, label: str, value: Any, expected: Any | None = None) -> Any:
    try:
        setter = getattr(obj, "set_state", None)
        if callable(setter):
            setter(value)
        else:
            setattr(obj, label, value)
        actual = obj.get_state()
    except Exception as exc:
        fail(f"Could not set {label}: {type(exc).__name__}: {exc}")
    if expected is not None and str(actual) != str(expected):
        fail(f"Readback mismatch for {label}: expected {expected!r}, got {actual!r}")
    return actual


def set_state_readback(obj: Any, label: str, value: Any) -> Any:
    try:
        obj.set_state(value)
        return obj.get_state()
    except Exception as exc:
        fail(f"Could not set/read back {label}: {type(exc).__name__}: {exc}")
        return None


def rename_injections_and_scale(solver: Any, source: dict[str, Any]) -> dict[str, Any]:
    setup = solver.settings.setup
    inlet = setup.boundary_conditions.mass_flow_inlet["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate
    set_state_readback(inlet, "liquidinlet.phase-2.mass_flow_rate", {"option": "value", "value": EULERIAN_LIQUID})
    liquid_readback = inlet.get_state()
    require(abs(finite_float(state_value(liquid_readback, "value"), "09cV2 liquid flow") - EULERIAN_LIQUID) < 1e-8, "09cV2 Eulerian liquid flow readback mismatch")

    material_ok = ensure_inert_particle_material(
        solver,
        material_name=DPM_MATERIAL,
        density=source["film_density"],
        strict=True,
    )
    require(material_ok, f"Could not create/read back DPM material {DPM_MATERIAL}")

    branch = setup.models.discrete_phase.injections
    source_total = source["source_dpm_total"]
    ratio = DPM_TOTAL / source_total
    old_names = sorted(source["injections"])
    new_names: list[str] = []

    for old_name in old_names:
        payload = source["injections"][old_name]
        old_flow = finite_float(state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"), f"{old_name} source flow")
        new_name = f"{FILM_MATERIAL}-{INJECTION_LABELS[old_name]}"
        require(new_name not in object_names(branch), f"Target injection name already exists: {new_name}")

        branch.rename(new=new_name, old=old_name)
        branch = setup.models.discrete_phase.injections
        require(new_name in object_names(branch), f"Injection rename readback failed: {old_name} -> {new_name}")
        injection = branch[new_name]

        set_readback(injection.material, "material", DPM_MATERIAL, DPM_MATERIAL)
        flow_leaf = injection.initial_values.mass_flow_rate
        new_flow = old_flow * ratio
        set_state_readback(flow_leaf, f"{new_name}.total_flow_rate", {"scale_by_area": False, "total_flow_rate": new_flow})
        flow_state = flow_leaf.get_state()
        actual_flow = finite_float(state_value(flow_state, "total_flow_rate"), f"{new_name} readback flow")
        require(abs(actual_flow - new_flow) < 1e-8, f"Flow readback mismatch for {new_name}: {actual_flow} vs {new_flow}")
        new_names.append(new_name)

    final_state = read_injections(solver)
    final_total = sum(
        finite_float(state_value(payload, "initial_values", "mass_flow_rate", "total_flow_rate"), f"{name} final flow")
        for name, payload in final_state.items()
    )
    require(abs(final_total - DPM_TOTAL) < 1e-8, f"09cV2 DPM total is {final_total}, expected {DPM_TOTAL}")
    require(set(final_state) == set(new_names), f"09cV2 injection names do not match target names: {sorted(final_state)}")
    return {"injection_state": final_state, "liquid_flow": liquid_readback, "dpm_total": final_total}


def enable_ewf_and_wall(solver: Any) -> dict[str, Any]:
    interaction = solver.settings.setup.models.discrete_phase.general_settings.interaction
    set_readback(interaction.enabled, "enabled", False, False)

    ewf_tui = solver.tui.define.models.eulerian_wallfilm
    required_commands = {"enable_wallfilm_model", "solve_wallfilm_equation"}
    available = set(dir(ewf_tui))
    require(required_commands <= available, f"Unknown EWF TUI commands; available names do not contain {sorted(required_commands)}")

    try:
        ewf_tui.enable_wallfilm_model("yes")
        ewf_tui.solve_wallfilm_equation("yes")
    except Exception as exc:
        fail(f"EWF activation failed: {type(exc).__name__}: {exc}")

    try:
        wallfilm_enabled = solver.scheme.eval("(sg-wallfilm?)")
    except Exception as exc:
        fail(f"EWF activation readback is unavailable: {type(exc).__name__}: {exc}")
    require(wallfilm_enabled is True, f"EWF activation readback was not true: {wallfilm_enabled!r}")

    film_material_command = getattr(ewf_tui, "film_material", None)
    require(film_material_command is not None, "EWF film_material command is unavailable")
    try:
        film_material_command("yes", FILM_MATERIAL)
    except Exception:
        try:
            film_material_command(FILM_MATERIAL)
        except Exception as exc:
            fail(f"EWF film material command failed: {type(exc).__name__}: {exc}")

    setup = solver.settings.setup
    wall_film = setup.boundary_conditions.wall["wall"].phase["mixture"].wall_film
    state = safe_get_state(wall_film, "wall_film")
    require(isinstance(state, dict), "EWF wall-film state is unavailable after activation")
    required = {
        "eulerian_film_wall",
        "film_condition_type",
        "film_height",
        "enable_flow_momentum_coupling",
        "enable_dpm_wall_splash",
    }
    missing = sorted(required - set(state))
    require(not missing, f"Unknown EWF wall-film children: missing {missing}; available {sorted(state)}")

    set_readback(wall_film.eulerian_film_wall, "eulerian_film_wall", True, True)
    set_readback(wall_film.film_condition_type, "film_condition_type", "film-wall-initial", "film-wall-initial")
    set_state_readback(wall_film.film_height, "film_height", {"option": "value", "value": 0})
    set_readback(wall_film.enable_flow_momentum_coupling, "enable_flow_momentum_coupling", False, False)
    set_readback(wall_film.enable_dpm_wall_splash, "enable_dpm_wall_splash", False, False)

    dpm_wall = setup.boundary_conditions.wall["wall"].phase["mixture"].dpm.discrete_phase_bc_type
    allowed = safe_allowed_values(dpm_wall)
    require("wall-film" in allowed or not allowed, f"wall-film DPM fate is not an available/readable option: {allowed}")
    set_readback(dpm_wall, "wall DPM discrete_phase_bc_type", "wall-film", "wall-film")

    solver_time = setup.general.solver.time
    set_readback(solver_time, "solver time", "transient", "transient")

    methods = solver.settings.solution.methods
    transient = methods.transient_formulation
    transient_allowed = safe_allowed_values(transient)
    transient_state = safe_get_state(transient, "transient_formulation")
    if transient_allowed:
        candidates = ["first-order-implicit", "first-order", "first-order-implicit-transient"]
        selected = next((item for item in candidates if item in transient_allowed), None)
        require(selected is not None, f"No first-order transient option is available: {transient_allowed}")
    else:
        require(isinstance(transient_state, dict), "Transient formulation state is unavailable after switching to transient")
        selected = "first-order-implicit"
    transient_readback = set_state_readback(transient, "transient formulation", {"option": selected})
    require("first-order" in str(transient_readback).lower(), f"Transient formulation did not read back as first-order: {transient_readback!r}")

    run_calc = solver.settings.solution.run_calculation
    run_children = set(safe_child_names(run_calc))
    timestep_field = next((name for name in ("time_step_size", "time_step") if name in run_children), None)
    require(timestep_field is not None, f"Unknown transient timestep path; run-calculation children: {sorted(run_children)}")
    timestep = getattr(run_calc, timestep_field)
    set_readback(timestep, timestep_field, 1.0e-5, 1.0e-5)

    return {
        "wallfilm_enabled": wallfilm_enabled,
        "wall_film": safe_get_state(setup.boundary_conditions.wall["wall"].phase["mixture"].wall_film, "wall_film_after"),
        "dpm_interaction": safe_get_state(interaction, "interaction_after"),
        "solver": safe_get_state(setup.general.solver, "solver_after"),
        "transient_formulation": transient_readback,
        "run_calculation": safe_get_state(run_calc, "run_calculation_after"),
    }


def load_branch(solver: Any, case_name: str) -> None:
    load_case_only(solver, case_name, label=f"Load {case_name}")


def set_wall_feature(solver: Any, feature: str, value: Any) -> dict[str, Any]:
    wall_film = solver.settings.setup.boundary_conditions.wall["wall"].phase["mixture"].wall_film
    state = safe_get_state(wall_film, f"wall_film_before_{feature}")
    require(isinstance(state, dict) and feature in state, f"Unknown EWF wall feature {feature!r}; available {sorted(state) if isinstance(state, dict) else state}")
    leaf = getattr(wall_film, feature)
    set_readback(leaf, feature, value, value)
    return safe_get_state(wall_film, f"wall_film_after_{feature}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", default=SERVER_ID)
    parser.add_argument("--summary-json", default="PyAnsys/output/v2_case_build_20260721.json")
    parser.add_argument(
        "--resume-09cV2",
        action="store_true",
        help="Reuse the already-written 09cV2 case and continue with the downstream branches.",
    )
    args = parser.parse_args()
    require(str(args.server_id) == SERVER_ID, "This build script is restricted to Fluent server 3")

    solver = connect(server_id=SERVER_ID)
    summary: dict[str, Any] = {"server_id": SERVER_ID, "fluent_version": solver.get_fluent_version(), "cases": {}}

    check_targets_absent(solver, allow_existing_09cV2=args.resume_09cV2)
    if args.resume_09cV2:
        require(remote_file_exists(solver, CASE_NAMES["09cV2"]), "--resume-09cV2 requested but the case is unavailable")
        load_branch(solver, CASE_NAMES["09cV2"])
        summary["cases"]["09cV2"] = {"existing_case_reused": True}
    else:
        source = read_source_state(solver)
        summary["source_readback"] = source

        v2 = rename_injections_and_scale(solver, source)
        write_case_only(solver, CASE_NAMES["09cV2"], "write_09cV2_case_only")
        require(remote_file_exists(solver, CASE_NAMES["09cV2"]), "09cV2 case was not visible after write")
        summary["cases"]["09cV2"] = v2

    load_branch(solver, CASE_NAMES["09cV2"])
    ewf_state = enable_ewf_and_wall(solver)
    write_case_only(solver, CASE_NAMES["010V2"], "write_010V2_case_only")
    require(remote_file_exists(solver, CASE_NAMES["010V2"]), "010V2 case was not visible after write")
    summary["cases"]["010V2"] = ewf_state

    load_branch(solver, CASE_NAMES["010V2"])
    summary["cases"]["010V2a"] = set_wall_feature(solver, "enable_dpm_wall_splash", True)
    write_case_only(solver, CASE_NAMES["010V2a"], "write_010V2a_case_only")
    require(remote_file_exists(solver, CASE_NAMES["010V2a"]), "010V2a case was not visible after write")

    load_branch(solver, CASE_NAMES["010V2"])
    summary["cases"]["010V2b"] = set_wall_feature(solver, "enable_edge_separation", True)
    write_case_only(solver, CASE_NAMES["010V2b"], "write_010V2b_case_only")
    require(remote_file_exists(solver, CASE_NAMES["010V2b"]), "010V2b case was not visible after write")

    load_branch(solver, CASE_NAMES["010V2"])
    summary["cases"]["010V2c"] = set_wall_feature(solver, "enable_particle_stripping", True)
    write_case_only(solver, CASE_NAMES["010V2c"], "write_010V2c_case_only")
    require(remote_file_exists(solver, CASE_NAMES["010V2c"]), "010V2c case was not visible after write")

    load_branch(solver, CASE_NAMES["010V2"])
    set_wall_feature(solver, "enable_dpm_wall_splash", True)
    set_wall_feature(solver, "enable_edge_separation", True)
    summary["cases"]["010V2d"] = set_wall_feature(solver, "enable_particle_stripping", True)
    write_case_only(solver, CASE_NAMES["010V2d"], "write_010V2d_case_only")
    require(remote_file_exists(solver, CASE_NAMES["010V2d"]), "010V2d case was not visible after write")

    summary["notes"] = [
        "Case-only build: no initialization, iterations, solver advance, or .dat.h5 writes.",
        "The source was the already-loaded 09c case on server 3.",
        "The five-percent DPM allocation was selected explicitly by the user.",
    ]
    output = Path(args.summary_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"summary_json: {output}")
    print("V2 case-only chain complete; no initialization or iteration was performed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except UnknownSetup as exc:
        print(f"UNKNOWN_SETUP_STOP: {exc}", file=sys.stderr)
        raise SystemExit(2)

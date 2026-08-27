#!/usr/bin/env python3
"""Build the independent 03A Stage-2 stabilization children.

Each child is loaded from the immutable Stage-1 1,000-iteration case/data
pair, instrumented with the common residual/flux/inventory monitor package,
and given exactly one Stage-2 numerical delta:

* N1: k/epsilon under-relaxation damping;
* N3: first-order k/epsilon transport;
* N4: first-order momentum/k/epsilon startup;
* N5: standard-k-epsilon bootstrap.

This script never initializes, patches, iterates, or owns a run loop.  Fluent
case/data writes are the only solver-side mutations after each branch is
prepared.  The resulting paired files are independent inputs for a separately
selected Fluent-native continuation; the former campaign-specific runner is
retired and recoverable from Git history.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_resume_case_data  # noqa: E402
import build_02e_y010_campaign as y010  # noqa: E402
import build_03a_08b_parity_full_geometry as stage1  # noqa: E402


DEFAULT_PARENT_CASE = (
    r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z-"
    r"iter1000-20260817T110345Z.cas.h5"
)
DEFAULT_PARENT_DATA = DEFAULT_PARENT_CASE[:-7] + ".dat.h5"
DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
EXPECTED_MESH = "Full-geomV2-231kcells.msh.h5"
MONITOR_PREFIX = "03a_stage2"
RESIDUAL_HISTORY_SIZE = 800


BRANCHES: tuple[dict[str, Any], ...] = (
    {
        "case_id": "03A-S2-N1",
        "branch": "N1",
        "description": "reduced turbulence under-relaxation damping",
        "k_epsilon_model": "rng",
        "momentum_scheme": "second-order-upwind",
        "k_scheme": "second-order-upwind",
        "epsilon_scheme": "second-order-upwind",
        "k_urf": 0.5,
        "epsilon_urf": 0.5,
        "initial_iterations": 300,
        "n5_bootstrap": False,
    },
    {
        "case_id": "03A-S2-N3",
        "branch": "N3",
        "description": "first-order turbulence transport",
        "k_epsilon_model": "rng",
        "momentum_scheme": "second-order-upwind",
        "k_scheme": "first-order-upwind",
        "epsilon_scheme": "first-order-upwind",
        "k_urf": 0.8,
        "epsilon_urf": 0.8,
        "initial_iterations": 300,
        "n5_bootstrap": False,
    },
    {
        "case_id": "03A-S2-N4",
        "branch": "N4",
        "description": "first-order momentum plus turbulence startup",
        "k_epsilon_model": "rng",
        "momentum_scheme": "first-order-upwind",
        "k_scheme": "first-order-upwind",
        "epsilon_scheme": "first-order-upwind",
        "k_urf": 0.8,
        "epsilon_urf": 0.8,
        "initial_iterations": 300,
        "n5_bootstrap": False,
    },
    {
        "case_id": "03A-S2-N5",
        "branch": "N5",
        "description": "standard-k-epsilon bootstrap before RNG return",
        "k_epsilon_model": "standard",
        "momentum_scheme": "second-order-upwind",
        "k_scheme": "second-order-upwind",
        "epsilon_scheme": "second-order-upwind",
        "k_urf": 0.8,
        "epsilon_urf": 0.8,
        "initial_iterations": 500,
        "n5_bootstrap": True,
    },
)


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def ensure_absent(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError("Refusing to overwrite Stage-2 artifacts: " + ", ".join(existing))


def resolve_fluid_zone(solver: Any) -> str:
    state = safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones")
    fluid = state.get("fluid", {}) if isinstance(state, Mapping) else {}
    names = [str(name) for name in fluid if str(name) != "settings"]
    if len(names) != 1:
        raise RuntimeError(f"Expected one fluid cell zone; found {names}")
    return names[0]


def set_optional(obj: Any, attribute: str, value: Any) -> None:
    try:
        setattr(obj, attribute, value)
    except Exception:
        # Fluent 2025 R2 exposes a slightly different editable subset of
        # report-history toggles depending on the loaded case.  The monitor
        # definition remains useful when an optional toggle is read-only.
        pass


def replace_named_report(branch: Any, name: str) -> Any:
    names = {str(item) for item in branch.get_object_names()}
    if name in names:
        deleted = False
        for kwargs in ({"name_list": [name]}, {"names": [name]}, {"name": name}):
            try:
                branch.delete(**kwargs)
                deleted = True
                break
            except Exception:
                continue
        if not deleted:
            branch.delete(name)
    branch.create(name=name)
    return branch[name]


def create_register(solver: Any, name: str, max_point: list[float]) -> dict[str, Any]:
    """Create a diagnostic box only; this function never patches it."""
    registers = solver.settings.solution.cell_registers
    if name in set(registers.get_object_names()):
        registers.delete(name_list=name)
    registers = solver.settings.solution.cell_registers
    registers.create(name=name)
    register = solver.settings.solution.cell_registers[name]
    register.set_state(
        {
            "name": name,
            "type": {
                "option": "hexahedron",
                "hexahedron": {
                    "min_point": y010.Y010_MIN,
                    "max_point": max_point,
                    "inside": True,
                },
            },
        }
    )
    state = solver.settings.solution.cell_registers[name].get_state()
    box = state.get("type", {}).get("hexahedron", {})
    if (
        state.get("type", {}).get("option") != "hexahedron"
        or box.get("min_point") != y010.Y010_MIN
        or box.get("max_point") != max_point
    ):
        raise RuntimeError(f"Cell-register readback mismatch for {name}: {state}")
    return state


def configure_monitor_package(solver: Any, zones: Mapping[str, str], fluid_zone: str) -> dict[str, Any]:
    """Create branch-local native report definitions for the required history."""
    root = solver.settings.solution.report_definitions
    flux = root.flux
    volume = root.volume
    surfaces = {
        "liquid_inlet": zones["liquid_inlet"],
        "steam_inlet": zones["steam_inlet"],
        "brine_outlet": zones["brine_outlet"],
        "steam_outlet": zones["steam_outlet"],
    }
    definitions: list[dict[str, Any]] = []

    # Keep mixture and phase-separated fluxes.  The phase-separated histories
    # are the auditable fallback when Fluent's mixture flux report is inactive.
    for phase in ("mixture", "phase-1", "phase-2"):
        for role, surface in surfaces.items():
            name = f"{MONITOR_PREFIX}_flux_{phase.replace('-', '')}_{role}"
            report = replace_named_report(flux, name)
            report.report_type = "flux-massflow"
            report.boundaries = [surface]
            set_optional(report, "per_selection", False)
            set_optional(report, "average_over", 1)
            set_optional(report, "retain_instantaneous_values", True)
            report.phase = phase
            set_optional(report, "create_report_file", True)
            set_optional(report, "create_report_plot", True)
            definitions.append(
                {
                    "name": name,
                    "kind": "flux",
                    "phase": phase,
                    "surface": surface,
                    "state": report.get_state(),
                }
            )

    volume_definitions = (
        ("y010_geometric_volume", y010.Y010_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y010_liquid_volume", y010.Y010_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y010_liquid_mass", y010.Y010_REGISTER, "volume-mass", None, "phase-2"),
        ("y030_geometric_volume", y010.Y030_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y030_liquid_volume", y010.Y030_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y030_liquid_mass", y010.Y030_REGISTER, "volume-mass", None, "phase-2"),
        ("total_liquid_volume", fluid_zone, "volume-integral", "phase-2-vof", "mixture"),
        ("total_liquid_mass", fluid_zone, "volume-mass", None, "phase-2"),
    )
    for suffix, cell_zone, report_type, field, phase in volume_definitions:
        name = f"{MONITOR_PREFIX}_inventory_{suffix}"
        report = replace_named_report(volume, name)
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = [cell_zone]
        if field is not None:
            report.field = field
        set_optional(report, "per_selection", False)
        set_optional(report, "average_over", 1)
        set_optional(report, "retain_instantaneous_values", True)
        report.phase = phase
        set_optional(report, "create_report_file", True)
        set_optional(report, "create_report_plot", True)
        definitions.append(
            {
                "name": name,
                "kind": "volume",
                "report_type": report_type,
                "field": field,
                "cell_zone": cell_zone,
                "phase": phase,
                "state": report.get_state(),
            }
        )

    return {
        "prefix": MONITOR_PREFIX,
        "fluid_zone": fluid_zone,
        "definition_count": len(definitions),
        "definitions": definitions,
        "registers_are_diagnostic_only": True,
    }


def configure_residual_history(solver: Any) -> dict[str, Any]:
    residual = solver.settings.solution.monitor.residual
    state = safe_get_state(residual, "Stage-2 residual monitor before update")
    equations = state.get("equations", {}) if isinstance(state, Mapping) else {}
    for name in equations:
        try:
            residual.equations[name].check_convergence = False
        except Exception:
            try:
                residual.equations[name].set_state({"check_convergence": False})
            except Exception:
                pass
    try:
        residual.options.n_save = RESIDUAL_HISTORY_SIZE
    except Exception:
        pass
    try:
        residual.options.n_display = RESIDUAL_HISTORY_SIZE
    except Exception:
        pass
    final_state = safe_get_state(residual, "Stage-2 residual monitor after update")
    return {
        "requested_history_size": RESIDUAL_HISTORY_SIZE,
        "state": final_state,
        "convergence_checks_disabled_for_fixed_budget": True,
    }


def configure_branch_settings(solver: Any, branch: Mapping[str, Any]) -> dict[str, Any]:
    """Apply one numerical delta after the parent pair has been loaded."""
    models = solver.settings.setup.models
    viscous = models.viscous
    # The model change is deliberately done before reading/setting model child
    # options.  Reacquire the live object after the parent switch.
    viscous.model = "k-epsilon"
    viscous = solver.settings.setup.models.viscous
    viscous.k_epsilon_model = branch["k_epsilon_model"]
    viscous = solver.settings.setup.models.viscous
    if branch["k_epsilon_model"] == "rng":
        try:
            viscous.rng_options.differential_viscosity_model = True
            viscous.rng_options.swirl_dominated_flow = True
        except Exception as exc:
            raise RuntimeError(f"RNG options could not be read/applied: {exc}") from exc
    try:
        viscous.near_wall_treatment.wall_treatment = "standard-wall-fn"
    except Exception:
        pass

    methods = solver.settings.solution.methods
    method_payload = {
        "pressure": "presto!",
        "mom": branch["momentum_scheme"],
        "k": branch["k_scheme"],
        "epsilon": branch["epsilon_scheme"],
        "mp": "quick",
    }
    # The reloaded Student tree exposes the discretization object below
    # spatial_discretization.  Keep the existing root-level setter only as a
    # compatibility fallback for cases whose serialization uses the shorter
    # layout; readback below decides whether the branch actually applied.
    try:
        methods.p_v_coupling.flow_scheme = "SIMPLE"
        methods.spatial_discretization.gradient_scheme = "green-gauss-node-based"
        methods.spatial_discretization.discretization_scheme.set_state(method_payload)
        methods.pseudo_time_method.set_state({"formulation": {"segregated_solver": "off"}})
        methods.high_order_term_relaxation.enable = False
    except Exception:
        methods = solver.settings.solution.methods
        methods.set_state(
            {
                "p_v_coupling": {"flow_scheme": "SIMPLE", "solve_n_phase": False},
                "gradient_scheme": "green-gauss-node-based",
                "discretization_scheme": method_payload,
                "pseudo_time_method": {"formulation": {"segregated_solver": "off"}},
                "high_order_term_relaxation": {"enable": False},
            }
        )
    controls = solver.settings.solution.controls
    controls.under_relaxation.set_state(
        {
            "pressure": 0.3,
            "mom": 0.7,
            "density": 1.0,
            "body-force": 1.0,
            "drift": 0.1,
            "mp": 0.4,
            "k": branch["k_urf"],
            "epsilon": branch["epsilon_urf"],
            "turb-viscosity": 1.0,
        }
    )
    residual = configure_residual_history(solver)
    models_state = safe_get_state(solver.settings.setup.models, "Stage-2 model readback")
    methods_state = safe_get_state(solver.settings.solution.methods, "Stage-2 method readback")
    controls_state = safe_get_state(solver.settings.solution.controls, "Stage-2 controls readback")
    readback = {
        "model": nested(models_state, "viscous", "model"),
        "k_epsilon_model": nested(models_state, "viscous", "k_epsilon_model"),
        "differential_viscosity": nested(models_state, "viscous", "rng_options", "differential_viscosity_model")
        or nested(models_state, "viscous", "rng", "differential_viscosity_model"),
        "swirl_dominated_flow": nested(models_state, "viscous", "rng_options", "swirl_dominated_flow")
        or nested(models_state, "viscous", "rng", "swirl_dominated_flow"),
        "methods": methods_state,
        "under_relaxation": controls_state.get("under_relaxation", {})
        if isinstance(controls_state, Mapping)
        else {},
        "residual": residual,
    }
    expected = {
        "model": "k-epsilon",
        "k_epsilon_model": branch["k_epsilon_model"],
        "momentum": branch["momentum_scheme"],
        "k": branch["k_scheme"],
        "epsilon": branch["epsilon_scheme"],
        "k_urf": branch["k_urf"],
        "epsilon_urf": branch["epsilon_urf"],
    }
    actual_momentum = nested(methods_state, "discretization_scheme", "mom") or nested(
        methods_state, "spatial_discretization", "discretization_scheme", "mom"
    )
    actual_k = nested(methods_state, "discretization_scheme", "k") or nested(
        methods_state, "spatial_discretization", "discretization_scheme", "k"
    )
    actual_epsilon = nested(methods_state, "discretization_scheme", "epsilon") or nested(
        methods_state, "spatial_discretization", "discretization_scheme", "epsilon"
    )
    if (
        readback["model"] != expected["model"]
        or readback["k_epsilon_model"] != expected["k_epsilon_model"]
        or actual_momentum != expected["momentum"]
        or actual_k != expected["k"]
        or actual_epsilon != expected["epsilon"]
        or float(readback["under_relaxation"].get("k")) != expected["k_urf"]
        or float(readback["under_relaxation"].get("epsilon")) != expected["epsilon_urf"]
    ):
        raise RuntimeError(
            f"Stage-2 branch readback mismatch: expected={expected}, "
            f"actual={{'model': {readback['model']!r}, 'k_epsilon_model': {readback['k_epsilon_model']!r}, "
            f"'mom': {actual_momentum!r}, 'k': {actual_k!r}, 'epsilon': {actual_epsilon!r}, "
            f"'k_urf': {readback['under_relaxation'].get('k')!r}, "
            f"'epsilon_urf': {readback['under_relaxation'].get('epsilon')!r}}}"
        )
    return {"expected": expected, "readback": readback}


def resolve_zones(solver: Any) -> dict[str, str]:
    state = safe_get_state(solver.settings.setup.boundary_conditions, "Stage-2 boundaries")
    return {
        "liquid_inlet": stage1.find_named_zone(state, "velocity_inlet", ("liquidinlet", "liquid-inlet")),
        "steam_inlet": stage1.find_named_zone(state, "velocity_inlet", ("steaminlet", "steam-inlet")),
        "steam_outlet": stage1.find_named_zone(state, "pressure_outlet", ("steamoutlet", "steam-outlet")),
        "brine_outlet": stage1.find_named_zone(state, "pressure_outlet", ("brineoutlet", "brine-outlet")),
    }


def validate_parent_contract(contract: Mapping[str, Any]) -> None:
    """Validate the Stage-1 carrier while preserving its inherited init flag.

    The executed Stage-1 endpoint can read back
    ``patch_reconstructed_interface=True`` even though no liquid patch was
    issued.  That flag is retained as inherited state; it is not treated as a
    Stage-2 patch command or silently rewritten.
    """
    models = contract["models"]
    general = contract["general"]
    methods = contract["methods"]
    if models["multiphase"] != "mixture" or models["energy"] is not False:
        raise RuntimeError(f"Stage-1 parent carrier mismatch: {models}")
    if models["viscous"] != "k-epsilon" or models["k_epsilon"] != "rng":
        raise RuntimeError(f"Stage-1 parent turbulence mismatch: {models}")
    if models["phase_materials"] != {
        "phase-1": "water-vapor-at-psep",
        "phase-2": "water-liquid-at-psep",
    }:
        raise RuntimeError(f"Stage-1 parent phase-material mismatch: {models}")
    if general["solver_type"] != "pressure-based" or general["solver_time"] != "steady":
        raise RuntimeError(f"Stage-1 parent solver mismatch: {general}")
    if general["operating_density_method"] != "mixture-averaged":
        raise RuntimeError(f"Stage-1 parent operating-density mismatch: {general}")
    if methods["flow_scheme"] != "SIMPLE" or methods["gradient_scheme"] != "green-gauss-node-based":
        raise RuntimeError(f"Stage-1 parent solution-method mismatch: {methods}")
    if methods["high_order_term_relaxation"] not in (False, None):
        raise RuntimeError(f"Stage-1 parent high-order relaxation is active: {methods}")
    if contract["dpm"].get("injection_names"):
        raise RuntimeError(f"Stage-1 parent has active DPM injections: {contract['dpm']}")
    for name in ("water-vapor-at-psep", "water-liquid-at-psep"):
        material = contract["materials"][name]
        if material["density"] is None or material["viscosity"] is None:
            raise RuntimeError(f"Stage-1 parent material readback incomplete: {contract['materials']}")


def build_child(
    solver: Any,
    *,
    parent_case: str,
    parent_data: str,
    remote_dir: str,
    stamp: str,
    branch: Mapping[str, Any],
) -> dict[str, Any]:
    stem = f"03A-08b-parity-full-geometry-Stage2-{branch['branch']}-from-iter1000-{stamp}"
    pre_run_case = str(PureWindowsPath(remote_dir) / f"{stem}-pre-run.cas.h5")
    pre_run_data = str(PureWindowsPath(remote_dir) / f"{stem}-pre-run.dat.h5")
    ensure_absent(solver, [pre_run_case, pre_run_data])

    load_resume_case_data(solver, parent_case, parent_data)
    zones = resolve_zones(solver)
    parent_models = safe_get_state(solver.settings.setup.models, "Stage-1 parent models")
    parent_methods = safe_get_state(solver.settings.solution.methods, "Stage-1 parent methods")
    parent_controls = safe_get_state(solver.settings.solution.controls, "Stage-1 parent controls")
    parent_boundaries = safe_get_state(
        solver.settings.setup.boundary_conditions,
        "Stage-1 parent boundaries",
    )
    parent_general = safe_get_state(solver.settings.setup.general, "Stage-1 parent general")
    parent_contract = stage1.compact_contract(
        solver,
        zones,
        {"interaction_before": None, "interaction_after": None, "injection_names": []},
    )
    validate_parent_contract(parent_contract)
    parent_case_identity = {
        "case": parent_case,
        "data": parent_data,
        "mesh_basename": PureWindowsPath(parent_case).name,
        "parent_is_explicit_case_data_pair": True,
    }
    if "water-vapor-at-psep" not in json.dumps(parent_models, default=str) or "water-liquid-at-psep" not in json.dumps(parent_models, default=str):
        raise RuntimeError("Stage-1 parent phase-material readback does not contain the audited psep materials")
    if nested(parent_models, "multiphase", "model") != "mixture":
        raise RuntimeError(f"Stage-1 parent is not Mixture: {parent_models}")
    if nested(parent_models, "viscous", "k_epsilon_model") != "rng":
        raise RuntimeError(f"Stage-1 parent is not RNG k-epsilon: {parent_models}")
    if nested(parent_methods, "p_v_coupling", "flow_scheme") != "SIMPLE":
        raise RuntimeError(f"Stage-1 parent is not SIMPLE: {parent_methods}")
    if float(nested(parent_controls, "under_relaxation", "k")) != 0.8 or float(nested(parent_controls, "under_relaxation", "epsilon")) != 0.8:
        raise RuntimeError(f"Stage-1 parent turbulence URFs are not 0.8: {parent_controls}")
    if nested(parent_general, "solver", "time") != "steady":
        raise RuntimeError(f"Stage-1 parent is not steady: {parent_general}")
    for outlet in ("steam_outlet", "brine_outlet"):
        if nested(parent_contract, "boundaries", outlet, "gauge_pressure") != 1_120_000.0:
            raise RuntimeError(f"Stage-1 parent {outlet} pressure is not 1.120 MPa: {parent_contract}")
    for inlet in ("liquid_inlet", "steam_inlet"):
        if nested(parent_contract, "boundaries", inlet, "velocity") != 27.118:
            raise RuntimeError(f"Stage-1 parent {inlet} velocity mismatch: {parent_contract}")

    # These registers and report definitions are instrumentation only.  No
    # initialize/patch operation is called, and the parent field is retained.
    registers = {
        y010.Y010_REGISTER: create_register(solver, y010.Y010_REGISTER, y010.Y010_MAX),
        y010.Y030_REGISTER: create_register(solver, y010.Y030_REGISTER, y010.Y030_MAX),
    }
    fluid_zone = resolve_fluid_zone(solver)
    monitor_package = configure_monitor_package(solver, zones, fluid_zone)
    branch_settings = configure_branch_settings(solver, branch)

    solver.settings.file.write_case(file_name=pre_run_case)
    solver.settings.file.write_data(file_name=pre_run_data)
    if not all(remote_file_exists(solver, path) for path in (pre_run_case, pre_run_data)):
        raise RuntimeError(f"Stage-2 pre-run pair was not written: {pre_run_case}, {pre_run_data}")

    load_resume_case_data(solver, pre_run_case, pre_run_data)
    reload_branch = configure_branch_settings(solver, branch)
    child_dpm = safe_get_state(solver.settings.setup.models.discrete_phase, "Stage-2 child DPM")
    child_injections = nested(child_dpm, "injections")
    child_contract = stage1.compact_contract(
        solver,
        zones,
        {
            "interaction_before": nested(child_dpm, "general_settings", "interaction", "enabled"),
            "interaction_after": nested(child_dpm, "general_settings", "interaction", "enabled"),
            "injection_names": sorted(str(name) for name in child_injections) if isinstance(child_injections, Mapping) else [],
        },
    )
    if branch["k_epsilon_model"] != "standard":
        validate_parent_contract(child_contract)
    frozen_parent = {
        "general": parent_contract["general"],
        "materials": parent_contract["materials"],
        "boundaries": parent_contract["boundaries"],
        "models": {key: value for key, value in parent_contract["models"].items() if key not in {"k_epsilon", "differential_viscosity", "swirl"}},
        "methods": {key: value for key, value in parent_contract["methods"].items() if key not in {"mom", "k", "epsilon"}},
        "controls": {key: value for key, value in parent_contract["controls"].get("under_relaxation", {}).items() if key not in {"k", "epsilon"}},
    }
    frozen_child = {
        "general": child_contract["general"],
        "materials": child_contract["materials"],
        "boundaries": child_contract["boundaries"],
        "models": {key: value for key, value in child_contract["models"].items() if key not in {"k_epsilon", "differential_viscosity", "swirl"}},
        "methods": {key: value for key, value in child_contract["methods"].items() if key not in {"mom", "k", "epsilon"}},
        "controls": {key: value for key, value in child_contract["controls"].get("under_relaxation", {}).items() if key not in {"k", "epsilon"}},
    }
    if json.dumps(frozen_parent, sort_keys=True, default=str) != json.dumps(frozen_child, sort_keys=True, default=str):
        raise RuntimeError("Stage-2 child changed a frozen physical/numerical context outside its declared branch delta")
    reload_registers = {
        name: safe_get_state(solver.settings.solution.cell_registers[name], f"{name} reload")
        for name in registers
    }
    if not all(name in set(solver.settings.solution.cell_registers.get_object_names()) for name in registers):
        raise RuntimeError(f"Diagnostic registers did not survive reload: {reload_registers}")

    return {
        "case_id": branch["case_id"],
        "branch": branch["branch"],
        "description": branch["description"],
        "source_parent_case": parent_case,
        "source_parent_data": parent_data,
        "source_parent": parent_case_identity,
        "parent_contract": parent_contract,
        "child_contract_reload": child_contract,
        "frozen_context_verified": True,
        "pre_run_case": pre_run_case,
        "pre_run_data": pre_run_data,
        "mesh_basename_expected": EXPECTED_MESH,
        "zones": zones,
        "fluid_zone": fluid_zone,
        "registers": registers,
        "registers_reload": reload_registers,
        "monitor_package": monitor_package,
        "branch_definition": dict(branch),
        "branch_settings": branch_settings,
        "branch_settings_reload": reload_branch,
        "native_iterations_initial": branch["initial_iterations"],
        "n5_bootstrap": branch["n5_bootstrap"],
        "initialization": "none; inherited Stage-1 iter1000 field",
        "liquid_patch": False,
        "fluent_version": str(solver.get_fluent_version()),
        "status": "CASE_DATA_VERIFIED",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--parent-case", default=DEFAULT_PARENT_CASE)
    parser.add_argument("--parent-data", default=DEFAULT_PARENT_DATA)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--snapshot-json", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if PureWindowsPath(args.parent_case).suffixes[-2:] != [".cas", ".h5"]:
        raise ValueError(f"Parent case is not .cas.h5: {args.parent_case}")
    if PureWindowsPath(args.parent_data).suffixes[-2:] != [".dat", ".h5"]:
        raise ValueError(f"Parent data is not .dat.h5: {args.parent_data}")
    if PureWindowsPath(args.parent_case) != PureWindowsPath(DEFAULT_PARENT_CASE) or PureWindowsPath(args.parent_data) != PureWindowsPath(DEFAULT_PARENT_DATA):
        raise ValueError(
            "Stage-2 is locked to the verified Stage-1 iter1000 pair; "
            f"expected {DEFAULT_PARENT_CASE} and {DEFAULT_PARENT_DATA}"
        )

    solver = connect(server_id=args.server_id)
    fluent_version = str(solver.get_fluent_version())
    if "2025 R2" not in fluent_version:
        raise RuntimeError(f"Expected Fluent 2025 R2, got {fluent_version!r}")
    if not solver.is_active():
        raise RuntimeError("Student Fluent session is not active")
    for path in (args.parent_case, args.parent_data):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"Stage-1 parent member is not visible through Fluent gRPC: {path}")

    children = [
        build_child(
            solver,
            parent_case=args.parent_case,
            parent_data=args.parent_data,
            remote_dir=args.remote_dir,
            stamp=args.stamp,
            branch=branch,
        )
        for branch in BRANCHES
    ]
    payload = {
        "setup_id": "03A",
        "stage": "Stage 2",
        "purpose": "steady numerical-stabilization screen from the immutable Stage-1 iter1000 case/data pair",
        "transport": "Fluent gRPC",
        "transport": "Fluent gRPC",
        "fluent_version": fluent_version,
        "mesh": EXPECTED_MESH,
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "parent_policy": "Every child independently read the same Stage-1 case/data pair; no child was derived from another child.",
        "stage2_cases": [dict(branch) for branch in BRANCHES],
        "native_iteration_policy": {
            "N1_N3_N4": "300 initial additional steady iterations unless Fluent fails earlier; return-to-authority is a separate qualification decision.",
            "N5": "500 standard-k-epsilon bootstrap iterations unless Fluent fails earlier, then a separate 300-iteration RNG return check after gRPC readback/restoration.",
        },
        "initialization": "none",
        "liquid_patch": False,
        "children": children,
        "status": "CASE_DATA_VERIFIED",
    }
    output = args.snapshot_json.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    print(f"snapshot_json: {output}", flush=True)
    print("CASE_DATA_VERIFIED; no initialization, patch, iteration, or solver shutdown was issued.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

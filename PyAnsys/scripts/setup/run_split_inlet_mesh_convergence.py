#!/usr/bin/env python3
"""Preflight and run the five-grid split-inlet carrier mesh study in Fluent."""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import math
import re
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import (  # noqa: E402
    quote_scheme_string,
    remote_chdir,
    remote_file_exists,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402
from pyansys_fluent.mesh_convergence import (  # noqa: E402
    monitor_stability,
    named_zones,
    normalize_zone_name,
    parse_mesh_check,
    parse_mesh_quality,
    parse_mesh_size,
    parse_named_report_rows,
    parse_net_report_value,
    resolve_zone_roles,
)
from pyansys_fluent.setup_common import require_remote_input  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


STUDY_ID = "split_inlet_mesh_convergence_20260801"
REMOTE_STUDY_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_MESH_ROOT = r"C:\Users\qtra338\Documents\Mesh study\Meshes"
SETTINGS_FILE = r"C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set"
TEMPLATE_CASE = r"C:\Users\qtra338\Documents\Mesh study\partial_solution_diagnostic_20260801.cas.h5"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID
MESH_NAMES = (
    "mesh-300k",
    "mesh-600k",
    "mesh-900k",
    "mesh-1600k",
    "mesh-1900k",
    "mesh-2000k",
    "mesh-2300k",
)
MESH_FILES = {name: rf"{REMOTE_MESH_ROOT}\{name}.msh" for name in MESH_NAMES}
LEGACY_STAGE2 = rf"{REMOTE_MESH_ROOT}\mesh-stage2.msh"
ITERATIONS = 3000
BLOCK = 250
CHECKPOINTS = {1000, 2000, 3000}
TOTAL_INLET = 116.92 + 80.69

FACE_ALIASES: dict[str, tuple[str, ...]] = {
    "liquidinlet": ("liquid-inlet", "liquid_inlet", "inlet-liquid", "inlet_liquid"),
    "steaminlet": ("steam-inlet", "steam_inlet", "inlet-steam", "inlet_steam"),
    "steamoutlet": ("steam-outlet", "steam_outlet", "outlet", "outlet-steam"),
    "bottom": ("bottom-wall", "bottom_wall"),
    "wall-fluid": ("wall_fluid", "wallfluid", "wall-smooth_spiral_separator"),
}
CELL_ALIASES: dict[str, tuple[str, ...]] = {"fluid": ("fluid-domain", "fluid_domain")}
EXPECTED_CATEGORIES = {
    "liquidinlet": "mass_flow_inlet",
    "steaminlet": "mass_flow_inlet",
    "steamoutlet": "pressure_outlet",
    "bottom": "wall",
    "wall-fluid": "wall",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight-only", action="store_true")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--mesh-filter", action="append", default=[])
    parser.add_argument("--skip-preflight-all", action="store_true")
    parser.add_argument("--minimum-free-gb", type=float, default=80.0)
    parser.add_argument("--allow-low-disk", action="store_true")
    return parser


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def ensure_remote_directory(solver: Any, path: str) -> None:
    if sweep.ensure_remote_directory_best_effort(solver, path):
        return
    raise RuntimeError(f"requires manual GUI cleanup: could not create remote directory {path}")


def remote_command_capture(solver: Any, command: str, scratch: str) -> str:
    sweep.remote_delete_best_effort(solver, scratch)
    wrapped = f'cmd /c {command} > "{scratch}" 2>&1'
    solver.scheme.eval(f'(system "{quote_scheme_string(wrapped)}")')
    text = sweep.remote_text_read_best_effort(solver, scratch)
    if not text:
        raise RuntimeError(f"requires TUI fallback: remote command produced no output: {command}")
    return text


def remote_file_sha256(solver: Any, path: str, scratch: str) -> str:
    text = remote_command_capture(solver, f'certutil -hashfile "{path}" SHA256', scratch)
    matches = re.findall(r"\b[0-9a-fA-F]{64}\b", text.replace(" ", ""))
    if not matches:
        raise RuntimeError(f"Could not parse SHA256 for {path}: {text[:500]}")
    return matches[0].lower()


def remote_free_bytes(solver: Any, scratch: str) -> int:
    command = "wmic logicaldisk where \"DeviceID='C:'\" get FreeSpace /value"
    text = remote_command_capture(solver, command, scratch)
    match = re.search(r"FreeSpace=(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    powershell = 'powershell -NoProfile -Command "(Get-PSDrive -Name C).Free"'
    text = remote_command_capture(solver, powershell, scratch)
    match = re.search(r"(?:^|\s)(\d{8,})(?:\s|$)", text)
    if not match:
        raise RuntimeError(f"Could not parse remote free disk space: {text[:500]}")
    return int(match.group(1))


def capture_fluent(label: str, func: Callable[[], Any], *, required: bool = True) -> str:
    text = sweep.capture_call(label, func, required=required)
    return text


def call_and_drain(func: Callable[[], Any], delay_seconds: float = 1.0) -> Any:
    """Keep stdout capture open briefly for Fluent's asynchronous console stream."""
    result = func()
    time.sleep(delay_seconds)
    return result


def read_mesh(solver: Any, path: str) -> str:
    require_remote_input(solver, path, "mesh")
    remote_chdir(solver, str(PureWindowsPath(path).parent))
    return capture_fluent("read_mesh", lambda: solver.settings.file.read_mesh(file_name=path))


def load_template_and_replace_mesh(solver: Any, mesh_path: str) -> str:
    """Load the verified case-only setup, replace its mesh, and discard stale handles."""
    require_remote_input(solver, TEMPLATE_CASE, "mesh-study template case")
    require_remote_input(solver, mesh_path, "replacement mesh")
    read_text = capture_fluent(
        "read_template_case",
        lambda: call_and_drain(
            lambda: solver.settings.file.read_case(file_name=TEMPLATE_CASE),
            delay_seconds=2.0,
        ),
    )
    replace_text = capture_fluent(
        "replace_mesh",
        lambda: call_and_drain(
            lambda: solver.settings.mesh.replace(file_name=mesh_path, zones=True),
            delay_seconds=2.0,
        ),
    )
    lowered = (read_text + replace_text).lower()
    if "error:" in lowered or "failed" in lowered:
        raise RuntimeError("requires TUI fallback: case-template mesh replacement reported an error")
    return read_text + replace_text


def apply_settings(solver: Any, path: str) -> str:
    require_remote_input(solver, path, "settings file")
    attempts: tuple[tuple[str, Callable[[], Any]], ...] = (
        ("read_settings_file_name", lambda: solver.settings.file.read_settings(file_name=path)),
        ("read_settings_file_name_1", lambda: solver.settings.file.read_settings(file_name_1=path)),
        ("tui_read_settings", lambda: solver.tui.file.read_settings(path)),
    )
    failures: list[str] = []
    for label, call in attempts:
        text = capture_fluent(label, lambda call=call: call_and_drain(call), required=False)
        lowered = text.lower()
        rejected = any(
            token in lowered
            for token in (
                "failed",
                "error:",
                "empty filename",
                "unknown keyword",
            )
        )
        if not rejected:
            return text
        failures.append(text)
    raise RuntimeError("requires TUI fallback: all read-settings calls failed\n" + "\n".join(failures))


def collect_mesh_reports(solver: Any) -> tuple[dict[str, Any], str]:
    size_text = capture_fluent(
        "mesh_size_info", lambda: call_and_drain(lambda: solver.settings.mesh.size_info())
    )
    check_text = capture_fluent(
        "mesh_check", lambda: call_and_drain(lambda: solver.settings.mesh.check())
    )
    quality_text = capture_fluent(
        "mesh_quality", lambda: call_and_drain(lambda: solver.settings.mesh.quality())
    )
    metrics = parse_mesh_size(size_text)
    metrics.update(parse_mesh_check(check_text))
    metrics.update(parse_mesh_quality(quality_text))
    metrics["characteristic_size_m"] = (
        metrics["domain_volume_m3"] / metrics["cells"]
    ) ** (1.0 / 3.0)
    return metrics, size_text + check_text + quality_text


def current_zone_mapping(solver: Any, *, allow_rename: bool) -> dict[str, Any]:
    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "boundary_conditions")
    cell_state = safe_get_state(solver.settings.setup.cell_zone_conditions, "cell_zone_conditions")
    if not isinstance(boundary_state, Mapping) or not isinstance(cell_state, Mapping):
        raise RuntimeError("path/version issue: could not inspect Fluent zones")
    face_available = named_zones(boundary_state)
    cell_available = named_zones(cell_state)
    faces = resolve_zone_roles(face_available, FACE_ALIASES)
    cells = resolve_zone_roles(cell_available, CELL_ALIASES)
    renames: list[dict[str, str]] = []
    if allow_rename:
        for canonical, item in faces.items():
            actual = item["name"]
            if actual == canonical:
                continue
            if normalize_zone_name(actual) != normalize_zone_name(canonical):
                raise RuntimeError(
                    f"invalid value/format issue: refusing non-normalized zone rename {actual!r} -> {canonical!r}"
                )
            solver.settings.setup.boundary_conditions.set_zone_name(
                zonename=actual,
                newname=canonical,
            )
            renames.append({"from": actual, "to": canonical})
        if renames:
            boundary_state = safe_get_state(
                solver.settings.setup.boundary_conditions,
                "boundary_conditions_after_rename",
            )
            faces = resolve_zone_roles(named_zones(boundary_state), FACE_ALIASES)
    if cells["fluid"]["name"] != "fluid":
        raise RuntimeError(
            "requires manual GUI cleanup: fluid cell zone is not canonically named and the "
            "2024 R2 cell-zone settings branch has no safe rename command"
        )
    return {
        "face_roles": faces,
        "cell_roles": cells,
        "renames": renames,
        "available_face_zones": face_available,
        "available_cell_zones": cell_available,
    }


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def capture_settings(solver: Any, remote_dir: str) -> dict[str, Any]:
    phase_names: list[str]
    phase_materials: dict[str, Any]
    phase_identity_method = "settings phase material object"
    try:
        phases = solver.settings.setup.models.multiphase.phases
        phase_names = sorted(str(name) for name in phases.get_object_names())
        phase_materials = {
            name: sweep.scalar_setting_state(phases[name].material)
            for name in phase_names
        }
        phase_densities: dict[str, float] = {}
    except AttributeError:
        # Fluent 2024 R2 can hide the phase-material named-object branch after
        # a fresh case read. Density reports are also inactive until the case
        # has been initialized, so phase identity is verified separately after
        # hybrid initialization rather than inferred here.
        phase_identity_method = "deferred until initialized density readback"
        phase_names = ["phase-1", "phase-2"]
        phase_materials = {"phase-1": None, "phase-2": None}
        phase_densities = {}
    branches = {
        "general": solver.settings.setup.general,
        "energy": solver.settings.setup.models.energy,
        "multiphase": solver.settings.setup.models.multiphase,
        "viscous": solver.settings.setup.models.viscous,
        "dpm_interaction": solver.settings.setup.models.discrete_phase.general_settings.interaction,
        "materials": solver.settings.setup.materials,
        "boundary_conditions": solver.settings.setup.boundary_conditions,
        "cell_zone_conditions": solver.settings.setup.cell_zone_conditions,
        "methods": solver.settings.solution.methods,
        "controls": solver.settings.solution.controls,
        "initialization": solver.settings.solution.initialization,
        "residual": solver.settings.solution.monitor.residual,
    }
    return {
        **{name: safe_get_state(branch, name) for name, branch in branches.items()},
        "phase_names": phase_names,
        "phase_materials": phase_materials,
        "phase_densities_kg_m3": phase_densities,
        "phase_identity_method": phase_identity_method,
    }


def critical_fingerprint(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "general": snapshot["general"],
        "energy": snapshot["energy"],
        "multiphase": snapshot["multiphase"],
        "viscous": snapshot["viscous"],
        "dpm_interaction": snapshot["dpm_interaction"],
        "materials": snapshot["materials"],
        "phase_names": snapshot["phase_names"],
        "phase_materials": snapshot["phase_materials"],
        "phase_densities_kg_m3": snapshot["phase_densities_kg_m3"],
        "phase_identity_method": snapshot["phase_identity_method"],
        "boundary_conditions": snapshot["boundary_conditions"],
        "cell_zone_conditions": snapshot["cell_zone_conditions"],
        "methods": snapshot["methods"],
        "controls": snapshot["controls"],
        "initialization": snapshot["initialization"],
        "residual": snapshot["residual"],
    }


def fingerprint_sha256(fingerprint: Mapping[str, Any]) -> str:
    encoded = json.dumps(fingerprint, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def validate_settings(
    snapshot: Mapping[str, Any],
    mesh_metrics: Mapping[str, Any],
    *,
    require_phase_identity: bool = True,
) -> list[str]:
    errors: list[str] = []

    def expect(path: tuple[str, ...], expected: Any, *, tolerance: float = 0.0) -> None:
        actual = nested(snapshot, *path)
        if tolerance and isinstance(expected, (int, float)) and actual is not None:
            passed = math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)
        else:
            passed = actual == expected
        if not passed:
            errors.append(f"{'.'.join(path)} expected={expected!r} actual={actual!r}")

    expect(("general", "solver", "type"), "pressure-based")
    expect(("general", "solver", "time"), "steady")
    expect(("general", "solver", "velocity_formulation"), "absolute")
    expect(("general", "operating_conditions", "operating_pressure"), 0.0, tolerance=1e-9)
    expect(("general", "operating_conditions", "gravity", "enable"), True)
    expect(("general", "operating_conditions", "gravity", "components"), [0, -9.81, 0])
    expect(("energy", "enabled"), False)
    expect(("multiphase", "models"), "mixture")
    expect(("multiphase", "number_of_phases"), 2)
    if require_phase_identity:
        expect(("phase_materials", "phase-1"), "water-vapor-at-psep")
        expect(("phase_materials", "phase-2"), "water-liquid-at-psep")
        expect(("phase_densities_kg_m3", "phase-1"), 5.797433853149414, tolerance=1e-5)
        expect(("phase_densities_kg_m3", "phase-2"), 881.2108764648438, tolerance=1e-5)
    expect(("viscous", "model"), "k-epsilon")
    expect(("viscous", "k_epsilon_model"), "rng")
    expect(("viscous", "rng_options", "differential_viscosity_model"), True)
    expect(("viscous", "rng_options", "swirl_dominated_flow"), True)
    expect(("viscous", "near_wall_treatment", "wall_treatment"), "standard-wall-fn")
    expect(("dpm_interaction", "enabled"), False)
    expect(("methods", "p_v_coupling", "flow_scheme"), "SIMPLE")
    expect(("methods", "gradient_scheme"), "green-gauss-node-based")
    for field, expected in {
        "pressure": "presto!",
        "mom": "second-order-upwind",
        "epsilon": "second-order-upwind",
        "k": "first-order-upwind",
        "mp": "quick",
    }.items():
        expect(("methods", "discretization_scheme", field), expected)
    for field, expected in {
        "pressure": 0.3,
        "mom": 0.7,
        "k": 0.8,
        "epsilon": 0.8,
        "mp": 0.4,
        "drift": 0.1,
    }.items():
        expect(("controls", "under_relaxation", field), expected, tolerance=1e-6)
    bc = snapshot["boundary_conditions"]
    for role, category in EXPECTED_CATEGORIES.items():
        if nested(bc, category, role) is None:
            errors.append(f"boundary role {role!r} is not in expected category {category!r}")
    expect(("boundary_conditions", "mass_flow_inlet", "liquidinlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value"), 0.0, tolerance=1e-8)
    expect(("boundary_conditions", "mass_flow_inlet", "liquidinlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value"), 116.92, tolerance=1e-8)
    expect(("boundary_conditions", "mass_flow_inlet", "steaminlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value"), 80.69, tolerance=1e-8)
    expect(("boundary_conditions", "mass_flow_inlet", "steaminlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value"), 0.0, tolerance=1e-8)
    expect(("boundary_conditions", "pressure_outlet", "steamoutlet", "phase", "mixture", "momentum", "gauge_pressure", "value"), 1120000.0, tolerance=1e-6)
    expect(("boundary_conditions", "pressure_outlet", "steamoutlet", "phase", "phase-2", "multiphase", "backflow_volume_fraction", "value"), 0.0, tolerance=1e-8)
    if int(mesh_metrics.get("partitions", -1)) != 16:
        errors.append(f"processor/partition count expected=16 actual={mesh_metrics.get('partitions')}")
    return errors


def report_file_text(
    solver: Any,
    remote_dir: str,
    label: str,
    call: Callable[[str], Any],
) -> str:
    # A unique name keeps retries idempotent even when Fluent/Windows retains
    # a previous report file or an earlier run ended before cleanup.
    path = remote_join(remote_dir, f"_{label}_{time.time_ns()}_scratch.txt")
    call(path)
    text = sweep.remote_text_read_best_effort(solver, path)
    if not text:
        raise RuntimeError(f"requires TUI fallback: report {label} produced no readable file")
    sweep.remote_delete_best_effort(solver, path)
    return text


def surface_scalar(
    solver: Any,
    remote_dir: str,
    label: str,
    surfaces: Sequence[str],
    field: str,
    *,
    average: str = "area",
) -> dict[str, float]:
    report = solver.settings.results.report.surface_integrals
    command = report.area_weighted_avg if average == "area" else report.mass_weighted_avg
    text = report_file_text(
        solver,
        remote_dir,
        label,
        lambda path: command(
            surface_names=list(surfaces),
            report_of=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    rows = parse_named_report_rows(text, surfaces)
    missing = [surface for surface in surfaces if surface not in rows]
    if missing:
        raise RuntimeError(f"Could not parse surface report {label}; missing rows: {missing}")
    try:
        net_value = parse_net_report_value(text)
    except ValueError:
        # Fluent 2024 R2 omits the redundant Net row for a report scoped to
        # exactly one surface. In that case the named row is the net value.
        if len(surfaces) != 1:
            raise
        net_value = rows[surfaces[0]]
    return rows | {"Net": net_value}


def surface_areas(solver: Any, remote_dir: str, surfaces: Sequence[str]) -> dict[str, float]:
    report = solver.settings.results.report.surface_integrals
    text = report_file_text(
        solver,
        remote_dir,
        "surface_areas",
        lambda path: report.area(
            surface_names=list(surfaces),
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    return parse_named_report_rows(text, surfaces) | {"Net": parse_net_report_value(text)}


def volume_scalar(solver: Any, remote_dir: str, label: str, field: str) -> float:
    report = solver.settings.results.report.volume_integrals
    text = report_file_text(
        solver,
        remote_dir,
        label,
        lambda path: report.volume_average(
            cell_zones=["fluid"],
            cell_function=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    rows = parse_named_report_rows(text, ["fluid"])
    if "fluid" not in rows:
        raise RuntimeError(f"Could not parse volume report {label}")
    return rows["fluid"]


def verify_initialized_phase_identity(solver: Any, remote_dir: str) -> dict[str, Any]:
    """Read phase density fields after initialization and match them to materials."""
    phase_densities = {
        "phase-1": volume_scalar(solver, remote_dir, "phase_1_density", "phase-1-density"),
        "phase-2": volume_scalar(solver, remote_dir, "phase_2_density", "phase-2-density"),
    }
    materials_state = safe_get_state(solver.settings.setup.materials, "materials_for_phase_match")
    fluids = nested(materials_state, "fluid") or {}
    phase_materials: dict[str, Any] = {}
    for phase_name, density in phase_densities.items():
        matches = []
        for material_name, material in fluids.items():
            material_density = nested(material, "density", "value")
            if material_density is not None and math.isclose(
                float(material_density), float(density), rel_tol=0.0, abs_tol=1e-5
            ):
                matches.append(str(material_name))
        phase_materials[phase_name] = matches[0] if len(matches) == 1 else matches
    return {
        "phase_names": ["phase-1", "phase-2"],
        "phase_materials": phase_materials,
        "phase_densities_kg_m3": phase_densities,
        "phase_identity_method": "initialized density fields matched to material database",
    }


def mass_flows(solver: Any, remote_dir: str, domain: str) -> dict[str, float]:
    zones = ["liquidinlet", "steaminlet", "steamoutlet"]
    report = solver.settings.results.report.fluxes
    text = report_file_text(
        solver,
        remote_dir,
        f"mass_flow_{domain}",
        lambda path: report.mass_flow(
            domain=domain,
            zones=zones,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    rows = parse_named_report_rows(text, zones)
    rows["Net"] = parse_net_report_value(text)
    return rows


def geometry_signature(solver: Any, remote_dir: str) -> dict[str, Any]:
    surfaces = ["liquidinlet", "steaminlet", "steamoutlet", "bottom", "wall-fluid"]
    signature: dict[str, Any] = {"areas_m2": surface_areas(solver, remote_dir, surfaces)}
    for field, key in (
        ("x-coordinate", "centroid_x_m"),
        ("y-coordinate", "centroid_y_m"),
        ("z-coordinate", "centroid_z_m"),
    ):
        signature[key] = surface_scalar(
            solver,
            remote_dir,
            f"geometry_{key}",
            ["liquidinlet", "steaminlet", "steamoutlet"],
            field,
        )
    return signature


def collect_physical_metrics(solver: Any, remote_dir: str, iteration: int) -> dict[str, Any]:
    mixture = mass_flows(solver, remote_dir, "mixture")
    vapor = mass_flows(solver, remote_dir, "phase-1")
    liquid = mass_flows(solver, remote_dir, "phase-2")
    inlet_pressure = surface_scalar(
        solver,
        remote_dir,
        "pressure_inlet",
        ["liquidinlet", "steaminlet"],
        "pressure",
        average="mass",
    )["Net"]
    outlet_pressure = surface_scalar(
        solver,
        remote_dir,
        "pressure_outlet",
        ["steamoutlet"],
        "pressure",
        average="mass",
    )["Net"]
    outlet_velocity = surface_scalar(
        solver,
        remote_dir,
        "outlet_velocity",
        ["steamoutlet"],
        "velocity-magnitude",
    )["Net"]
    volume_velocity = volume_scalar(solver, remote_dir, "volume_velocity", "velocity-magnitude")
    volume_vorticity = volume_scalar(solver, remote_dir, "volume_vorticity", "vorticity-mag")
    vapor_out = abs(vapor["steamoutlet"])
    liquid_out = abs(liquid["steamoutlet"])
    quality = 100.0 * vapor_out / (vapor_out + liquid_out) if vapor_out + liquid_out else math.nan
    return {
        "iteration": iteration,
        "mixture_liquidinlet_kgs": mixture["liquidinlet"],
        "mixture_steaminlet_kgs": mixture["steaminlet"],
        "mixture_steamoutlet_kgs": mixture["steamoutlet"],
        "mixture_net_kgs": mixture["Net"],
        "mixture_imbalance_percent": abs(mixture["Net"]) / TOTAL_INLET * 100.0,
        "vapor_liquidinlet_kgs": vapor["liquidinlet"],
        "vapor_steaminlet_kgs": vapor["steaminlet"],
        "vapor_steamoutlet_kgs": vapor["steamoutlet"],
        "vapor_net_kgs": vapor["Net"],
        "vapor_imbalance_percent": abs(vapor["Net"]) / 80.69 * 100.0,
        "liquid_liquidinlet_kgs": liquid["liquidinlet"],
        "liquid_steaminlet_kgs": liquid["steaminlet"],
        "liquid_steamoutlet_kgs": liquid["steamoutlet"],
        "liquid_net_kgs": liquid["Net"],
        "liquid_imbalance_percent": abs(liquid["Net"]) / 116.92 * 100.0,
        "carrier_outlet_quality_percent_trend_only": quality,
        "inlet_mass_weighted_pressure_pa": inlet_pressure,
        "outlet_mass_weighted_pressure_pa": outlet_pressure,
        "pressure_drop_pa": inlet_pressure - outlet_pressure,
        "outlet_area_weighted_velocity_ms": outlet_velocity,
        "domain_volume_avg_velocity_ms": volume_velocity,
        "domain_volume_avg_vorticity_s-1": volume_vorticity,
    }


def preflight_one(
    solver: Any,
    mesh_name: str,
    mesh_path: str,
    baseline_hash: str | None,
) -> tuple[dict[str, Any], str]:
    local_dir = LOCAL_ROOT / mesh_name.replace("-", "_")
    remote_dir = remote_join(REMOTE_STUDY_ROOT, mesh_name.replace("-", "_"))
    local_dir.mkdir(parents=True, exist_ok=True)
    ensure_remote_directory(solver, remote_dir)
    transcript = remote_join(remote_dir, f"{mesh_name}_transcript.trn")
    try:
        solver.settings.file.start_transcript(file_name=transcript)
    except Exception as exc:
        print(f"start_transcript: diagnostic failure -> {type(exc).__name__}: {exc}")

    started = time.time()
    try:
        mesh_load_text = read_mesh(solver, mesh_path)
        zones_before = current_zone_mapping(solver, allow_rename=True)
        mesh_metrics, quality_text = collect_mesh_reports(solver)
        template_replace_text = load_template_and_replace_mesh(solver, mesh_path)
        zones_after_replace = current_zone_mapping(solver, allow_rename=True)
        settings_text = apply_settings(solver, SETTINGS_FILE)
        zones_after = current_zone_mapping(solver, allow_rename=False)
        snapshot = capture_settings(solver, remote_dir)
        errors = validate_settings(snapshot, mesh_metrics, require_phase_identity=False)
        warning_names = re.findall(r"no zone with name\s+([^\s\)]+)", settings_text, re.IGNORECASE)
        critical_warning_names = [
            name for name in warning_names if normalize_zone_name(name) in {normalize_zone_name(role) for role in FACE_ALIASES}
        ]
        if critical_warning_names:
            errors.append(f"read-settings reported missing required zones: {critical_warning_names}")
        if errors:
            raise RuntimeError("pre-initialization validation failed: " + "; ".join(errors))
        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        snapshot.update(verify_initialized_phase_identity(solver, remote_dir))
        errors = validate_settings(snapshot, mesh_metrics, require_phase_identity=True)
        geometry = geometry_signature(solver, remote_dir)
        fingerprint = critical_fingerprint(snapshot)
        current_hash = fingerprint_sha256(fingerprint)
        if baseline_hash is not None and current_hash != baseline_hash:
            errors.append(
                f"critical settings fingerprint mismatch: baseline={baseline_hash} current={current_hash}"
            )
        payload = {
            "study_id": STUDY_ID,
            "mesh_name": mesh_name,
            "mesh_file": mesh_path,
            "settings_file": SETTINGS_FILE,
            "status": "accepted" if not errors else "unresolved",
            "started_epoch": started,
            "completed_epoch": time.time(),
            "fluent_version": str(solver.get_fluent_version()),
            "mesh_metrics": mesh_metrics,
            "geometry_signature": geometry,
            "zone_mapping_before_settings": zones_before,
            "zone_mapping_after_template_replace": zones_after_replace,
            "zone_mapping_after_settings": zones_after,
            "settings_import_no_zone_warnings": warning_names,
            "settings_import_text": settings_text,
            "template_replace_text": template_replace_text,
            "template_case": TEMPLATE_CASE,
            "critical_fingerprint_sha256": current_hash,
            "validation_errors": errors,
            "limitations": [
                "bottom is a wall and steamoutlet is the only carrier outlet",
                "carrier quality/liquid carryover is trend-only, not validated separator efficiency",
                "settings file is the 07a execution authority and differs from archived FFF.1-2 numerics/BC family",
            ],
        }
        write_json(local_dir / f"{mesh_name}_preflight.json", payload)
        write_json(local_dir / f"{mesh_name}_settings_readback.json", snapshot)
        (local_dir / f"{mesh_name}_mesh_quality.txt").write_text(quality_text, encoding="utf-8")
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(remote_dir, f"{mesh_name}_preflight.json"),
            json.dumps(payload, indent=2, default=str),
        )
        if errors:
            raise RuntimeError("preflight validation failed: " + "; ".join(errors))
        return payload, current_hash
    except Exception as exc:
        failure = {
            "study_id": STUDY_ID,
            "mesh_name": mesh_name,
            "status": "unresolved",
            "failure_category": classify_failure(exc),
            "error": f"{type(exc).__name__}: {exc}",
            "completed_epoch": time.time(),
        }
        write_json(local_dir / f"{mesh_name}_preflight_failure.json", failure)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


def monitor_snapshot(solver: Any) -> dict[str, dict[str, Any]]:
    return sweep.monitor_iteration_snapshot(solver)


def monitor_point_count(snapshot: Mapping[str, Mapping[str, Any]]) -> int:
    residual = snapshot.get("residual")
    if residual:
        return int(residual.get("points", 0))
    return max((int(value.get("points", 0)) for value in snapshot.values()), default=0)


def require_point_advance(
    solver: Any,
    before: Mapping[str, Mapping[str, Any]],
    requested: int,
    timeout_seconds: float = 30.0,
) -> dict[str, dict[str, Any]]:
    before_points = monitor_point_count(before)
    deadline = time.monotonic() + timeout_seconds
    after: dict[str, dict[str, Any]] = {}
    while time.monotonic() < deadline:
        after = monitor_snapshot(solver)
        if monitor_point_count(after) >= before_points + requested:
            return after
        time.sleep(0.5)
    raise RuntimeError(
        "Fluent monitor history did not prove the full iteration block: "
        f"before_points={before_points}, requested={requested}, after={after}"
    )


def save_pair(solver: Any, remote_dir: str, mesh_name: str, label: str) -> dict[str, str]:
    case_file = remote_join(remote_dir, f"{mesh_name}_{label}.cas.h5")
    data_file = remote_join(remote_dir, f"{mesh_name}_{label}.dat.h5")
    sweep.write_case_data_pair(solver, case_file, data_file, label)
    return {"case": case_file, "data": data_file}


def formal_run_one(
    solver: Any,
    preflight: Mapping[str, Any],
    baseline_hash: str,
) -> dict[str, Any]:
    mesh_name = str(preflight["mesh_name"])
    mesh_path = str(preflight["mesh_file"])
    local_dir = LOCAL_ROOT / mesh_name.replace("-", "_")
    remote_dir = remote_join(REMOTE_STUDY_ROOT, mesh_name.replace("-", "_"))
    transcript = remote_join(remote_dir, f"{mesh_name}_production_transcript.trn")
    result: dict[str, Any] = {
        "mesh_name": mesh_name,
        "status": "running",
        "iterations_requested": ITERATIONS,
        "block_size": BLOCK,
        "checkpoints": {},
        "iteration_evidence": [],
        "started_epoch": time.time(),
    }
    try:
        try:
            solver.settings.file.start_transcript(file_name=transcript)
        except Exception as exc:
            print(f"start_transcript: diagnostic failure -> {type(exc).__name__}: {exc}")
        load_template_and_replace_mesh(solver, mesh_path)
        current_zone_mapping(solver, allow_rename=True)
        mesh_metrics, quality_text = collect_mesh_reports(solver)
        apply_settings(solver, SETTINGS_FILE)
        current_zone_mapping(solver, allow_rename=False)
        snapshot = capture_settings(solver, remote_dir)
        errors = validate_settings(snapshot, mesh_metrics, require_phase_identity=False)
        if errors:
            raise RuntimeError("production pre-initialization readback failed: " + "; ".join(errors))

        sweep.configure_residual_history(solver, 4000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        snapshot.update(verify_initialized_phase_identity(solver, remote_dir))
        errors = validate_settings(snapshot, mesh_metrics, require_phase_identity=True)
        current_hash = fingerprint_sha256(critical_fingerprint(snapshot))
        if current_hash != baseline_hash:
            errors.append(f"settings fingerprint mismatch: {current_hash} != {baseline_hash}")
        if errors:
            raise RuntimeError("production initialized readback failed: " + "; ".join(errors))
        result["checkpoints"]["initialized"] = save_pair(
            solver, remote_dir, mesh_name, "initialized"
        )
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        initial_monitor = monitor_snapshot(solver)
        result["initial_monitor_snapshot"] = initial_monitor

        physical_rows: list[dict[str, Any]] = []
        completed = 0
        while completed < ITERATIONS:
            before = monitor_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=BLOCK)
            after = require_point_advance(solver, before, BLOCK)
            completed += BLOCK
            evidence = {
                "block_end": completed,
                "requested": BLOCK,
                "before": before,
                "after": after,
            }
            result["iteration_evidence"].append(evidence)
            metrics = collect_physical_metrics(solver, remote_dir, completed)
            physical_rows.append(metrics)
            write_csv(local_dir / f"{mesh_name}_physical_monitor_history.csv", physical_rows)
            residual_rows = [
                row
                for row in sweep.monitor_history_rows(solver)
                if 0 < float(row["iteration"]) <= completed
            ]
            sweep.write_monitor_history_csv(
                local_dir / f"{mesh_name}_residual_history.csv",
                residual_rows,
            )
            if completed in CHECKPOINTS:
                label = f"iter{completed}_final" if completed == ITERATIONS else f"checkpoint_{completed}"
                result["checkpoints"][str(completed)] = save_pair(
                    solver, remote_dir, mesh_name, label
                )
            result["iterations_completed"] = completed
            write_json(local_dir / f"{mesh_name}_run_manifest.json", result)
            print(f"{mesh_name}: completed {completed}/{ITERATIONS}", flush=True)

        final_metrics = physical_rows[-1]
        primary_fields = [
            "pressure_drop_pa",
            "vapor_steamoutlet_kgs",
            "liquid_steamoutlet_kgs",
            "carrier_outlet_quality_percent_trend_only",
        ]
        secondary_fields = [
            "outlet_area_weighted_velocity_ms",
            "domain_volume_avg_velocity_ms",
            "domain_volume_avg_vorticity_s-1",
        ]
        stability = monitor_stability(physical_rows, primary_fields + secondary_fields)
        balance_pass = all(
            final_metrics[field] <= 0.5
            for field in (
                "mixture_imbalance_percent",
                "vapor_imbalance_percent",
                "liquid_imbalance_percent",
            )
        )
        primary_stable = all(stability[field]["drift_percent"] <= 0.5 for field in primary_fields)
        secondary_stable = all(stability[field]["drift_percent"] <= 1.0 for field in secondary_fields)
        classification = "accepted" if balance_pass and primary_stable and secondary_stable else "unresolved"
        metrics_payload = {
            "study_id": STUDY_ID,
            "mesh_name": mesh_name,
            "classification": classification,
            "mesh_metrics": mesh_metrics,
            "final_metrics": final_metrics,
            "monitor_stability_2500_3000": stability,
            "acceptance": {
                "phase_and_mixture_balance_pass": balance_pass,
                "primary_monitor_stability_pass": primary_stable,
                "secondary_monitor_stability_pass": secondary_stable,
            },
            "quality_metric_text_file": f"{mesh_name}_mesh_quality.txt",
            "carrier_quality_scope": "trend-only; bottom is a wall and steamoutlet is the only carrier outlet",
        }
        write_json(local_dir / f"{mesh_name}_metrics.json", metrics_payload)
        write_csv(local_dir / f"{mesh_name}_mass_balance_history.csv", physical_rows)
        write_csv(local_dir / f"{mesh_name}_surface_metrics.csv", [final_metrics])
        (local_dir / f"{mesh_name}_mesh_quality.txt").write_text(quality_text, encoding="utf-8")
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(remote_dir, f"{mesh_name}_metrics.json"),
            json.dumps(metrics_payload, indent=2, default=str),
        )
        result.update(
            {
                "status": "completed",
                "classification": classification,
                "iterations_completed": ITERATIONS,
                "final_checkpoint_is_3000_checkpoint": True,
                "metrics": metrics_payload,
                "completed_epoch": time.time(),
            }
        )
        write_json(local_dir / f"{mesh_name}_run_manifest.json", result)
        return result
    except Exception as exc:
        result.update(
            {
                "status": "failed",
                "classification": "unresolved",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        write_json(local_dir / f"{mesh_name}_run_manifest.json", result)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


def select_meshes(filters: Sequence[str]) -> list[str]:
    if not filters:
        return list(MESH_NAMES)
    normalized = {value.strip().lower().replace(".msh", "") for value in filters}
    selected = [name for name in MESH_NAMES if name.lower() in normalized]
    missing = normalized - {name.lower() for name in selected}
    if missing:
        raise ValueError(f"Unknown mesh filter(s): {sorted(missing)}")
    return selected


def write_preflight_matrix(rows: Sequence[Mapping[str, Any]]) -> None:
    matrix: list[dict[str, Any]] = []
    for row in rows:
        metrics = row["mesh_metrics"]
        geometry = row["geometry_signature"]
        matrix.append(
            {
                "mesh_name": row["mesh_name"],
                "status": row["status"],
                "cells": metrics["cells"],
                "faces": metrics["faces"],
                "nodes": metrics["nodes"],
                "partitions": metrics["partitions"],
                "domain_volume_m3": metrics["domain_volume_m3"],
                "characteristic_size_m": metrics["characteristic_size_m"],
                "minimum_orthogonal_quality": metrics["minimum_orthogonal_quality"],
                "maximum_aspect_ratio": metrics["maximum_aspect_ratio"],
                "liquidinlet_area_m2": geometry["areas_m2"].get("liquidinlet"),
                "steaminlet_area_m2": geometry["areas_m2"].get("steaminlet"),
                "steamoutlet_area_m2": geometry["areas_m2"].get("steamoutlet"),
                "settings_fingerprint": row["critical_fingerprint_sha256"],
            }
        )
    write_csv(LOCAL_ROOT / "mesh_matrix.csv", matrix)


def main() -> int:
    load_dotenv()
    args = build_parser().parse_args()
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    selected = select_meshes(args.mesh_filter)
    solver = connect(server_id=args.server_id)
    print(f"connected_fluent_version: {solver.get_fluent_version()}")
    ensure_remote_directory(solver, REMOTE_STUDY_ROOT)
    for mesh_name in selected:
        require_remote_input(solver, MESH_FILES[mesh_name], mesh_name)
    require_remote_input(solver, SETTINGS_FILE, "mesh-study settings")
    require_remote_input(solver, TEMPLATE_CASE, "mesh-study template case")
    require_remote_input(solver, LEGACY_STAGE2, "legacy stage2 mesh")

    scratch = remote_join(REMOTE_STUDY_ROOT, "_remote_preflight.txt")
    free_bytes = remote_free_bytes(solver, scratch)
    free_gb = free_bytes / 1_000_000_000.0
    alias_hash = remote_file_sha256(solver, MESH_FILES["mesh-600k"], scratch)
    stage2_hash = remote_file_sha256(solver, LEGACY_STAGE2, scratch)
    environment = {
        "study_id": STUDY_ID,
        "fluent_version": str(solver.get_fluent_version()),
        "remote_free_bytes": free_bytes,
        "remote_free_gb_decimal": free_gb,
        "minimum_free_gb_required": args.minimum_free_gb,
        "mesh_stage2_sha256": stage2_hash,
        "mesh_600k_sha256": alias_hash,
        "mesh_stage2_matches_mesh_600k": stage2_hash == alias_hash,
        "selected_meshes": selected,
    }
    write_json(LOCAL_ROOT / "environment_preflight.json", environment)
    if free_gb < args.minimum_free_gb and not args.allow_low_disk:
        raise RuntimeError(
            f"Remote C: free space {free_gb:.2f} GB is below required {args.minimum_free_gb:.2f} GB"
        )

    preflight_rows: list[dict[str, Any]] = []
    baseline_hash: str | None = None
    preflight_manifest_path = LOCAL_ROOT / "preflight_manifest.json"
    if not args.skip_preflight_all or args.preflight_only:
        existing_by_name: dict[str, dict[str, Any]] = {}
        if args.mesh_filter and preflight_manifest_path.exists():
            existing_manifest = json.loads(preflight_manifest_path.read_text(encoding="utf-8"))
            baseline_hash = str(existing_manifest["baseline_settings_fingerprint"])
            existing_by_name = {
                str(row["mesh_name"]): row for row in existing_manifest.get("meshes", [])
            }
        for mesh_name in selected:
            print(f"\n=== PREFLIGHT {mesh_name} ===", flush=True)
            payload, current_hash = preflight_one(
                solver,
                mesh_name,
                MESH_FILES[mesh_name],
                baseline_hash,
            )
            if baseline_hash is None:
                baseline_hash = current_hash
            preflight_rows.append(payload)
            existing_by_name[mesh_name] = payload
        merged_rows = [
            existing_by_name[name] for name in MESH_NAMES if name in existing_by_name
        ]
        write_preflight_matrix(merged_rows)
        write_json(
            preflight_manifest_path,
            {
                "environment": environment,
                "status": "accepted" if len(merged_rows) == len(MESH_NAMES) else "partial",
                "baseline_settings_fingerprint": baseline_hash,
                "meshes": merged_rows,
            },
        )
    else:
        manifest = json.loads(preflight_manifest_path.read_text(encoding="utf-8"))
        baseline_hash = str(manifest["baseline_settings_fingerprint"])
        by_name = {row["mesh_name"]: row for row in manifest["meshes"]}
        missing = [name for name in selected if name not in by_name]
        if missing:
            raise RuntimeError(f"Meshes lack accepted preflight records: {', '.join(missing)}")
        preflight_rows = [by_name[name] for name in selected]

    if args.preflight_only:
        print("preflight_all: ACCEPTED")
        return 0
    assert baseline_hash is not None
    study_manifest: dict[str, Any] = {
        "study_id": STUDY_ID,
        "status": "running",
        "environment": environment,
        "baseline_settings_fingerprint": baseline_hash,
        "runs": [],
        "started_epoch": time.time(),
    }
    write_json(LOCAL_ROOT / "study_manifest.json", study_manifest)
    for preflight in preflight_rows:
        print(f"\n=== PRODUCTION {preflight['mesh_name']} ===", flush=True)
        run = formal_run_one(solver, preflight, baseline_hash)
        study_manifest["runs"].append(run)
        write_json(LOCAL_ROOT / "study_manifest.json", study_manifest)
    study_manifest.update({"status": "completed", "completed_epoch": time.time()})
    write_json(LOCAL_ROOT / "study_manifest.json", study_manifest)
    print("mesh_study: COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

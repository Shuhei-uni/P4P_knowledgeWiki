#!/usr/bin/env python3
"""Build and verify the Setup 02e Y010 parent and independent children.

This module deliberately stops at case/data preparation.  Fluent-native
journals own all 500-iteration calculations; this script never calls a solve
iteration command.
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


DEFAULT_MESH = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\Full-geomV2-231kcells.msh.h5"
DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
DEFAULT_SNAPSHOT = PROJECT_ROOT / "output" / "02e_y010_campaign_build.json"

Y010_REGISTER = "codex_y010_pool_below_y_0p10m"
Y030_REGISTER = "codex_y030_monitor_below_y_0p30m"
MONITOR_PREFIX = "02e_y010"
Y010_MIN = [-2.067034, -1.484584, -1.469893]
Y010_MAX = [1.066098, 0.100000, 2.000000]
Y030_MAX = [1.066098, 0.300000, 2.000000]
EXPECTED_Y010 = {
    "selected_cells": 33315,
    "geometric_volume_m3": 4.829410214,
    "liquid_volume_m3": 4.790652590,
    "liquid_mass_kg": 4224.253734,
}
LIQUID_DENSITY = 881.77
STEAM_PRESSURE = 1_120_000.0
INLET_PRESSURE = 1_140_000.0
INLET_VELOCITY = 27.118

STAGE1 = {
    "PO": (
        ("02e-PO-P1", "po-p1160", 1_160_000.0),
        ("02e-PO-P2", "po-p1200", 1_200_000.0),
        ("02e-PO-P3", "po-p1240", 1_240_000.0),
    ),
    "OV": (
        ("02e-OV-P1", "ov-k0", 0.0),
        ("02e-OV-P2", "ov-k10", 10.0),
        ("02e-OV-P3", "ov-k100", 100.0),
    ),
    "MF": (
        ("02e-MF-P1", "mf-liquid58p4235-vapour0", 58.4235),
        ("02e-MF-P2", "mf-liquid116p847-vapour0", 116.847),
        ("02e-MF-P3", "mf-liquid233p694-vapour0", 233.694),
    ),
    "EF": (
        ("02e-EF-P1", "ef-jumpm50kpa", -50_000.0),
        ("02e-EF-P2", "ef-jump0", 0.0),
        ("02e-EF-P3", "ef-jumpp50kpa", 50_000.0),
    ),
}


def norm(value: object) -> str:
    return str(value).replace("-", "").replace("_", "").casefold()


def resolve_name(mapping: Mapping[str, Any], aliases: tuple[str, ...], role: str) -> str:
    names = [str(name) for name in mapping if str(name) != "settings"]
    for alias in aliases:
        for name in names:
            if norm(name) == norm(alias):
                return name
    raise RuntimeError(f"Could not resolve {role}; available names={sorted(names)}")


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def remote_path(remote_dir: str, filename: str) -> str:
    return str(PureWindowsPath(remote_dir) / filename)


def ensure_absent(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError("Refusing to overwrite existing artifacts: " + ", ".join(existing))


def resolve_zones(solver: Any) -> dict[str, str]:
    state = solver.settings.setup.boundary_conditions.get_state()
    return {
        "liquid_inlet": resolve_name(state.get("velocity_inlet", {}), ("liquid-inlet", "liquidinlet"), "liquid inlet"),
        "steam_inlet": resolve_name(state.get("velocity_inlet", {}), ("steam-inlet", "steaminlet"), "steam inlet"),
        "brine_outlet": resolve_name(state.get("pressure_outlet", {}), ("brine-outlet", "brineoutlet"), "brine outlet"),
        "steam_outlet": resolve_name(state.get("pressure_outlet", {}), ("steam-outlet", "steamoutlet"), "steam outlet"),
    }


def ensure_materials_and_models(solver: Any) -> None:
    setup = solver.settings.setup
    general = setup.general
    general.solver.type = "pressure-based"
    general.solver.time = "steady"
    general.operating_conditions.operating_pressure = 0.0
    general.operating_conditions.gravity.enable = True
    general.operating_conditions.gravity.components = [0.0, -9.81, 0.0]

    models = setup.models
    models.energy.enabled = False
    models.viscous.model = "k-epsilon"
    models.viscous.k_epsilon_model = "rng"
    multiphase = models.multiphase
    multiphase.model = "mixture"
    multiphase = solver.settings.setup.models.multiphase

    fluid = setup.materials.fluid
    material_states = {
        "water-vapor": {
            "name": "water-vapor",
            "chemical_formula": "",
            "density": {"option": "constant", "value": 5.73},
            "viscosity": {"option": "constant", "value": 15.188e-6},
        },
        "water-liquid": {
            "name": "water-liquid",
            "chemical_formula": "",
            "density": {"option": "constant", "value": LIQUID_DENSITY},
            "viscosity": {"option": "constant", "value": 145.96e-6},
        },
    }
    for name, state in material_states.items():
        if name not in set(fluid.get_object_names()):
            fluid.create(name=name)
        fluid[name].set_state(state)

    multiphase = solver.settings.setup.models.multiphase
    phase_state = safe_get_state(multiphase, "multiphase_after_model")
    phase_map = phase_state.get("phases", {}) if isinstance(phase_state, Mapping) else {}
    if "phase-1" not in phase_map or "phase-2" not in phase_map:
        number = getattr(multiphase, "number_of_phases", None)
        if number is not None and hasattr(number, "number_of_eulerian_phases"):
            number.number_of_eulerian_phases = 2
        elif number is not None:
            setattr(multiphase, "number_of_phases", 2)
        multiphase = solver.settings.setup.models.multiphase
    # Material assignment must follow model activation and phase-tree refresh.
    multiphase.phases["phase-1"].material = "water-vapor"
    multiphase.phases["phase-2"].material = "water-liquid"
    multiphase = solver.settings.setup.models.multiphase
    final_state = safe_get_state(multiphase, "multiphase_final")
    if nested(final_state, "model") != "mixture":
        raise RuntimeError(f"Mixture model readback failed: {final_state}")
    if nested(final_state, "phases", "phase-1", "material") != "water-vapor":
        raise RuntimeError(f"Phase-1 material readback failed: {final_state}")
    if nested(final_state, "phases", "phase-2", "material") != "water-liquid":
        raise RuntimeError(f"Phase-2 material readback failed: {final_state}")

    # DPM/EWF are intentionally absent from the experiment.  The Student build
    # exposes the DPM branch even when inactive; only the interaction switch is
    # touched, and only after the carrier model is active.
    try:
        models.discrete_phase.general_settings.interaction.enabled = False
    except Exception:
        pass


def configure_frozen_boundaries(solver: Any, zones: Mapping[str, str]) -> None:
    bc = solver.settings.setup.boundary_conditions
    for role, fraction in (("liquid_inlet", 1.0), ("steam_inlet", 0.0)):
        name = zones[role]
        obj = bc.velocity_inlet[name]
        state = safe_get_state(obj, f"velocity_inlet.{name}")
        state["name"] = name
        state["phase"]["mixture"]["momentum"]["initial_gauge_pressure"] = {"option": "value", "value": INLET_PRESSURE}
        for phase in ("phase-1", "phase-2"):
            state["phase"][phase]["momentum"]["velocity_specification_method"] = "Magnitude, Normal to Boundary"
            state["phase"][phase]["momentum"]["reference_frame"] = "Absolute"
            state["phase"][phase]["momentum"]["velocity_magnitude"] = {"option": "value", "value": INLET_VELOCITY}
        state["phase"]["phase-2"]["multiphase"]["volume_fraction"] = {"option": "value", "value": fraction}
        obj.set_state(state)

    for role, pressure, fraction in (
        ("brine_outlet", STEAM_PRESSURE, 1.0),
        ("steam_outlet", STEAM_PRESSURE, 0.0),
    ):
        name = zones[role]
        obj = bc.pressure_outlet[name]
        state = safe_get_state(obj, f"pressure_outlet.{name}")
        state["name"] = name
        state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": pressure}
        state["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"] = {"option": "value", "value": fraction}
        obj.set_state(state)


def configure_solution(solver: Any) -> None:
    methods = solver.settings.solution.methods
    methods.p_v_coupling.flow_scheme = "SIMPLE"
    methods.spatial_discretization.gradient_scheme = "least-square-cell-based"
    methods.spatial_discretization.discretization_scheme.set_state(
        {
            "pressure": "presto!",
            "mom": "second-order-upwind",
            "mp": "quick",
            "k": "second-order-upwind",
            "epsilon": "second-order-upwind",
        }
    )
    controls = solver.settings.solution.controls
    controls.under_relaxation.set_state(
        {
            "body-force": 1.0,
            "density": 1.0,
            "drift": 0.1,
            "epsilon": 0.8,
            "k": 0.8,
            "mom": 0.7,
            "mp": 0.5,
            "pressure": 0.3,
            "turb-viscosity": 1.0,
        }
    )
    residual = solver.settings.solution.monitor.residual
    state = safe_get_state(residual, "residual")
    equations = state.get("equations", {}) if isinstance(state, Mapping) else {}
    for equation_name in equations:
        equation = getattr(residual.equations, equation_name, None)
        if equation is not None:
            try:
                equation.check_convergence = False
            except Exception:
                try:
                    equation.set_state({"check_convergence": False})
                except Exception:
                    pass
    try:
        residual.options.n_save = 600
    except Exception:
        pass


def create_register(solver: Any, name: str, max_point: list[float]) -> dict[str, Any]:
    registers = solver.settings.solution.cell_registers
    if name in set(registers.get_object_names()):
        old = registers[name].get_state()
        registers.delete(name_list=name)
        if old.get("type", {}).get("option") == "hexahedron":
            pass
    registers = solver.settings.solution.cell_registers
    registers.create(name=name)
    register = solver.settings.solution.cell_registers[name]
    register.set_state(
        {
            "name": name,
            "type": {"option": "hexahedron", "hexahedron": {"min_point": Y010_MIN, "max_point": max_point, "inside": True}},
        }
    )
    state = solver.settings.solution.cell_registers[name].get_state()
    box = state.get("type", {}).get("hexahedron", {})
    if state.get("type", {}).get("option") != "hexahedron" or box.get("min_point") != Y010_MIN or box.get("max_point") != max_point:
        raise RuntimeError(f"Register readback mismatch for {name}: {state}")
    return state


def inventory_queries(solver: Any, register_name: str) -> dict[str, Any]:
    reports = solver.settings.results.report.volume_integrals
    payload: dict[str, Any] = {"available": False, "register": register_name, "values": {}, "warnings": []}
    try:
        geom = reports.get_volume(
            cell_zones=[register_name],
            locations={"geometry": [register_name]},
            cell_function="cell-volume",
            current_domain="mixture",
        )
        payload["values"]["geometric_volume_m3"] = geom
        payload["available"] = True
    except Exception as exc:
        payload["warnings"].append(f"geometric volume query failed: {type(exc).__name__}: {exc}")
    for key, field in (("liquid_volume_m3", "phase-2-vof"),):
        try:
            value = reports.compute_volume_integral(
                cell_zones=[register_name],
                locations={"geometry": [register_name]},
                cell_function=field,
                current_domain="mixture",
            )
            payload["values"][key] = value
        except Exception as exc:
            payload["warnings"].append(f"{key} query failed: {type(exc).__name__}: {exc}")
    liquid_volume = payload["values"].get("liquid_volume_m3")
    if isinstance(liquid_volume, Mapping) and "Net" in liquid_volume:
        payload["values"]["liquid_mass_kg"] = float(liquid_volume["Net"]) * LIQUID_DENSITY
    elif isinstance(liquid_volume, (int, float)):
        payload["values"]["liquid_mass_kg"] = float(liquid_volume) * LIQUID_DENSITY
    return payload


def _replace_named_report(branch: Any, name: str) -> Any:
    """Create a report definition with a deterministic name."""
    names = set(str(item) for item in branch.get_object_names())
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
            try:
                branch.delete(name)
                deleted = True
            except Exception as exc:
                raise RuntimeError(f"Could not replace report definition {name}") from exc
    branch.create(name=name)
    return branch[name]


def _set_optional(obj: Any, attribute: str, value: Any) -> None:
    try:
        setattr(obj, attribute, value)
    except Exception:
        # Fluent exposes a slightly different editable subset for report
        # definitions by report type/version.  The definition itself remains
        # valid when an optional history toggle is not writable.
        pass


def configure_monitor_package(solver: Any, zones: Mapping[str, str]) -> dict[str, Any]:
    """Create native report-definition monitors shared by every child case.

    Flux reports are separate by phase and boundary so the sign convention is
    auditable after each native run.  Volume-integral reports preserve the
    Y010/Y030 inventory histories, while the endpoint inventory query remains
    the authoritative scalar readback used by the build verifier.
    """
    root = solver.settings.solution.report_definitions
    flux = root.flux
    volume = root.volume
    # Remove only probes created during live API discovery, plus our own
    # deterministic names when rebuilding an instrumented parent.
    for branch, names in ((flux, ("codex_probe_flux",)), (volume, ("codex_probe_volume",))):
        for name in names:
            if name in set(str(item) for item in branch.get_object_names()):
                try:
                    branch.delete(name_list=[name])
                except Exception:
                    branch.delete(name)

    definitions: list[dict[str, Any]] = []
    surfaces = {
        "liquid_inlet": zones["liquid_inlet"],
        "steam_inlet": zones["steam_inlet"],
        "brine_outlet": zones["brine_outlet"],
        "steam_outlet": zones["steam_outlet"],
    }
    for phase in ("mixture", "phase-1", "phase-2"):
        for role, surface in surfaces.items():
            name = f"{MONITOR_PREFIX}_flux_{phase.replace('-', '')}_{role}"
            report = _replace_named_report(flux, name)
            report.report_type = "flux-massflow"
            report.boundaries = [surface]
            _set_optional(report, "per_selection", False)
            _set_optional(report, "average_over", 1)
            _set_optional(report, "retain_instantaneous_values", True)
            report.phase = phase
            _set_optional(report, "create_report_file", True)
            _set_optional(report, "create_report_plot", True)
            definitions.append({"name": name, "kind": "flux", "phase": phase, "surface": surface, "state": report.get_state()})

    volumes = (
        ("y010_geometric_volume", Y010_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y010_liquid_volume", Y010_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y010_liquid_mass", Y010_REGISTER, "volume-mass", None, "phase-2"),
        ("y030_geometric_volume", Y030_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y030_liquid_volume", Y030_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y030_liquid_mass", Y030_REGISTER, "volume-mass", None, "phase-2"),
    )
    for suffix, register, report_type, field, phase in volumes:
        name = f"{MONITOR_PREFIX}_inventory_{suffix}"
        report = _replace_named_report(volume, name)
        report.report_type = report_type
        if field is not None:
            report = volume[name]
            report.field = field
        report = volume[name]
        report.cell_zones = [register]
        _set_optional(report, "per_selection", False)
        _set_optional(report, "average_over", 1)
        _set_optional(report, "retain_instantaneous_values", True)
        report.phase = phase
        _set_optional(report, "create_report_file", True)
        _set_optional(report, "create_report_plot", True)
        definitions.append({"name": name, "kind": "volume", "register": register, "report_type": report_type, "field": field, "phase": phase, "state": report.get_state()})
    return {"count": len(definitions), "definitions": definitions}


def build_parent(solver: Any, mesh: str, parent_case: str, parent_data: str, zones: dict[str, str]) -> dict[str, Any]:
    ensure_materials_and_models(solver)
    configure_frozen_boundaries(solver, zones)
    configure_solution(solver)
    solver.settings.solution.initialization.hybrid_initialize()
    create_register(solver, Y010_REGISTER, Y010_MAX)
    solver.settings.solution.initialization.patch.calculate_patch(
        domain="phase-2", registers=[Y010_REGISTER], variable="mp", value=1.0
    )
    # Keep a monitoring-only Y030 register in the parent; it is never patched.
    create_register(solver, Y030_REGISTER, Y030_MAX)
    inventory = inventory_queries(solver, Y010_REGISTER)
    monitors = configure_monitor_package(solver, zones)
    solver.settings.file.write_case(file_name=parent_case)
    solver.settings.file.write_data(file_name=parent_data)
    if not remote_file_exists(solver, parent_case) or not remote_file_exists(solver, parent_data):
        raise RuntimeError("Y010 parent pair was not visible after write")
    solver.settings.file.read_case_data(file_name=parent_case)
    return {
        "mesh": mesh,
        "parent_case": parent_case,
        "parent_data": parent_data,
        "zones": zones,
        "models": safe_get_state(solver.settings.setup.models, "models"),
        "boundaries": safe_get_state(solver.settings.setup.boundary_conditions, "boundaries"),
        "methods": safe_get_state(solver.settings.solution.methods, "methods"),
        "registers": {Y010_REGISTER: solver.settings.solution.cell_registers[Y010_REGISTER].get_state(), Y030_REGISTER: solver.settings.solution.cell_registers[Y030_REGISTER].get_state()},
        "inventory": inventory,
        "monitors": monitors,
        "expected_inventory_reference": EXPECTED_Y010,
        "fluent_version": solver.get_fluent_version(),
        "initialized": True,
        "patched": True,
        "iterations": 0,
    }


def set_pressure_outlet(solver: Any, zone: str, pressure: float) -> None:
    obj = solver.settings.setup.boundary_conditions.pressure_outlet[zone]
    state = safe_get_state(obj, f"pressure_outlet.{zone}")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": pressure}
    obj.set_state(state)
    actual = nested(solver.settings.setup.boundary_conditions.pressure_outlet[zone].get_state(), "phase", "mixture", "momentum", "gauge_pressure", "value")
    if float(actual) != float(pressure):
        raise RuntimeError(f"Pressure readback mismatch for {zone}: requested={pressure} actual={actual}")


def set_outlet_vent(solver: Any, zone: str, k: float) -> None:
    bc = solver.settings.setup.boundary_conditions
    bc.set_zone_type(zone_list=[zone], new_type="outlet-vent")
    bc = solver.settings.setup.boundary_conditions
    obj = bc.outlet_vent[zone]
    state = safe_get_state(obj, f"outlet_vent.{zone}")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": STEAM_PRESSURE}
    obj.set_state(state)
    # Fluent 2025 R2 exposes the resistance branch under mixture momentum.
    # Changing option rebuilds its children, so reacquire before setting value.
    momentum = solver.settings.setup.boundary_conditions.outlet_vent[zone].phase["mixture"].momentum
    momentum.loss_coefficient.option = "constant"
    momentum = solver.settings.setup.boundary_conditions.outlet_vent[zone].phase["mixture"].momentum
    momentum.loss_coefficient.value = k
    after = safe_get_state(solver.settings.setup.boundary_conditions.outlet_vent[zone], f"outlet_vent.{zone}.after")
    actual = nested(after, "phase", "mixture", "momentum", "loss_coefficient", "value")
    if actual is None:
        raise RuntimeError(f"Outlet Vent K readback unavailable: {after}")
    if abs(float(actual) - k) > 1e-12:
        raise RuntimeError(f"Outlet Vent K readback mismatch: requested={k} actual={actual}")


def set_mass_flow_outlet(solver: Any, zone: str, target: float) -> None:
    bc = solver.settings.setup.boundary_conditions
    bc.set_zone_type(zone_list=[zone], new_type="mass-flow-outlet")
    bc = solver.settings.setup.boundary_conditions
    obj = bc.mass_flow_outlet[zone]
    state = safe_get_state(obj, f"mass_flow_outlet.{zone}")
    # The live 2025 R2 branch uses phase-specific mass-flow rate leaves.
    for phase in ("phase-1", "phase-2"):
        momentum = state["phase"][phase].setdefault("momentum", {})
        momentum["mass_flow_specification"] = "Mass Flow Rate"
        momentum["mass_flow_rate"] = {"option": "value", "value": 0.0 if phase == "phase-1" else target}
    obj.set_state(state)
    after = safe_get_state(bc.mass_flow_outlet[zone], f"mass_flow_outlet.{zone}.after")
    actual = nested(after, "phase", "phase-2", "momentum", "mass_flow_rate", "value")
    if actual is None or abs(float(actual) - target) > 1e-9:
        raise RuntimeError(f"Mass-Flow Outlet liquid target readback mismatch: requested={target} actual={actual}")


def set_exhaust_fan(solver: Any, zone: str, jump: float) -> None:
    bc = solver.settings.setup.boundary_conditions
    bc.set_zone_type(zone_list=[zone], new_type="exhaust-fan")
    bc = solver.settings.setup.boundary_conditions
    obj = bc.exhaust_fan[zone]
    state = safe_get_state(obj, f"exhaust_fan.{zone}")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": STEAM_PRESSURE}
    obj.set_state(state)
    momentum = solver.settings.setup.boundary_conditions.exhaust_fan[zone].phase["mixture"].momentum
    momentum.pressure_jump.option = "constant"
    momentum = solver.settings.setup.boundary_conditions.exhaust_fan[zone].phase["mixture"].momentum
    momentum.pressure_jump.value = jump
    after = safe_get_state(solver.settings.setup.boundary_conditions.exhaust_fan[zone], f"exhaust_fan.{zone}.after")
    actual = nested(after, "phase", "mixture", "momentum", "pressure_jump", "value")
    if actual is None or abs(float(actual) - jump) > 1e-9:
        raise RuntimeError(f"Exhaust Fan pressure-jump readback mismatch: requested={jump} actual={actual}")


def build_children(
    solver: Any,
    parent_case: str,
    remote_dir: str,
    stamp: str,
    zones: dict[str, str],
    family: str | None = None,
    case_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    families = [family] if family else list(STAGE1)
    for selected_family in families:
        for case_id, suffix, control in STAGE1[selected_family]:
            if case_ids is not None and case_id not in case_ids:
                continue
            filename = f"{case_id}-{suffix}-y010-pre-run-{stamp}.cas.h5"
            output = remote_path(remote_dir, filename)
            data_output = output[:-7] + ".dat.h5"
            ensure_absent(solver, [output, data_output])
            solver.settings.file.read_case_data(file_name=parent_case)
            # Reacquire after every case load, then mutate only the requested outlet.
            live_zones = resolve_zones(solver)
            if live_zones != zones:
                raise RuntimeError(f"Zone map changed after parent reload: {live_zones} vs {zones}")
            if selected_family == "PO":
                set_pressure_outlet(solver, zones["brine_outlet"], control)
            elif selected_family == "OV":
                set_outlet_vent(solver, zones["brine_outlet"], control)
            elif selected_family == "MF":
                set_mass_flow_outlet(solver, zones["brine_outlet"], control)
            elif selected_family == "EF":
                set_exhaust_fan(solver, zones["brine_outlet"], control)
            else:
                raise ValueError(selected_family)
            solver.settings.file.write_case(file_name=output)
            solver.settings.file.write_data(file_name=data_output)
            if not remote_file_exists(solver, output) or not remote_file_exists(solver, data_output):
                raise RuntimeError(f"Paired child not visible after write: {output}, {data_output}")
            records.append({"case_id": case_id, "family": selected_family, "control": control, "pre_run_case": output, "pre_run_data": data_output, "fluent_version": solver.get_fluent_version()})
    return records


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("parent", "stage1"), required=True)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--mesh", default=DEFAULT_MESH)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--snapshot-json", default=str(DEFAULT_SNAPSHOT))
    parser.add_argument("--parent-case", default="")
    parser.add_argument("--parent-data", default="")
    parser.add_argument("--family", choices=tuple(STAGE1), default=None)
    parser.add_argument("--case-id", action="append", default=None, help="Build only this Stage-1 case ID; repeat for a selected subset.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    solver = connect(server_id=args.server_id)
    if not remote_file_exists(solver, args.mesh):
        raise FileNotFoundError(f"Production mesh not visible on {args.server_id}: {args.mesh}")
    if args.mode == "parent":
        parent_case = args.parent_case or remote_path(args.remote_dir, f"02e-Y010-parent-initialized-{args.stamp}.cas.h5")
        parent_data = args.parent_data or remote_path(args.remote_dir, f"02e-Y010-parent-initialized-{args.stamp}.dat.h5")
        ensure_absent(solver, [parent_case, parent_data])
        solver.settings.file.read_mesh(file_name=args.mesh)
        zones = resolve_zones(solver)
        payload = build_parent(solver, args.mesh, parent_case, parent_data, zones)
    else:
        if not args.parent_case:
            raise ValueError("--parent-case is required in stage1 mode")
        solver.settings.file.read_case_data(file_name=args.parent_case)
        zones = resolve_zones(solver)
        selected_case_ids = set(args.case_id) if args.case_id else None
        valid_case_ids = {case_id for cases in STAGE1.values() for case_id, _, _ in cases}
        if selected_case_ids is not None:
            unknown = selected_case_ids - valid_case_ids
            if unknown:
                raise ValueError(f"Unknown Stage-1 case IDs: {sorted(unknown)}")
            if args.family:
                family_case_ids = {case_id for case_id, _, _ in STAGE1[args.family]}
                outside = selected_case_ids - family_case_ids
                if outside:
                    raise ValueError(f"Case IDs outside --family={args.family}: {sorted(outside)}")
        records = build_children(solver, args.parent_case, args.remote_dir, args.stamp, zones, args.family, selected_case_ids)
        if not records:
            raise ValueError("No Stage-1 children selected for building")
        payload = {"mode": "stage1", "parent_case": args.parent_case, "zones": zones, "children": records, "fluent_version": solver.get_fluent_version()}
    output = Path(args.snapshot_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"snapshot_json: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

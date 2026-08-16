#!/usr/bin/env python3
"""Build 02d VOF IC0, IC1, and IC2-Y030 cases from the currently loaded mesh.

The script intentionally does not read a mesh or an existing case.  It uses the
mesh already loaded in the named Student Fluent session, applies the documented
02d VOF setup contract, and writes:

* IC0: a pre-initialization case-only artifact;
* IC1: a Hybrid-Initialized case/data pair with the five-cell brine-outlet
  boundary-distance patch;
* IC2-Y030: an independently rebuilt case/data pair from IC1 with a liquid pool
  patch below ``y = +0.30 m``.

No calculation iteration, timestep, native autosave, or production run is
started.  IC1 and IC2 data files are required to preserve their patched fields.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
DEFAULT_Y_CUT = 0.30
DEFAULT_IC1_DISTANCE = 5

# Read-only mesh check immediately before this build reported these bounds for
# the loaded Full-geomV2 mesh.  The values are recorded in the output snapshot
# and are used only to define the reproducible IC2 pool register.
LOADED_MESH_BOUNDS = {
    "min_point": [-2.067034, -1.484584, -1.469893],
    "max_point": [1.066492, 6.993813, 2.0],
    "observed_max_y": 6.993813,
}


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server-id", default="student")
    p.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    p.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    p.add_argument("--y-cut", type=float, default=DEFAULT_Y_CUT)
    p.add_argument("--ic1-distance", type=int, default=DEFAULT_IC1_DISTANCE)
    p.add_argument(
        "--snapshot-json",
        default=str(PROJECT_ROOT / "output" / "02d_vof_loaded_mesh_ic0_ic1_ic2_build.json"),
    )
    return p


def find_zone(mapping: Mapping[str, Any], aliases: tuple[str, ...], role: str) -> str:
    names = {str(name): name for name in mapping}
    lowered = {name.lower(): name for name in names}
    for alias in aliases:
        if alias in names:
            return alias
        if alias.lower() in lowered:
            return str(lowered[alias.lower()])
    raise RuntimeError(f"Could not resolve {role} zone from {sorted(names)}")


def resolve_zones(solver: Any) -> dict[str, str]:
    state = solver.settings.setup.boundary_conditions.get_state()
    return {
        "liquid_inlet": find_zone(
            state.get("velocity_inlet", {}),
            ("liquid-inlet", "liquidinlet"),
            "liquid inlet",
        ),
        "steam_inlet": find_zone(
            state.get("velocity_inlet", {}),
            ("steam-inlet", "steaminlet"),
            "steam inlet",
        ),
        "brine_outlet": find_zone(
            state.get("pressure_outlet", {}),
            ("brine-outlet", "brineoutlet"),
            "brine outlet",
        ),
        "steam_outlet": find_zone(
            state.get("pressure_outlet", {}),
            ("steam-outlet", "steamoutlet"),
            "steam outlet",
        ),
    }


def require_one_fluid_zone(solver: Any) -> str:
    state = solver.settings.setup.cell_zone_conditions.get_state()
    zones = state.get("fluid", {}) if isinstance(state, Mapping) else {}
    names = [str(name) for name in zones if str(name) != "settings"]
    if len(names) != 1:
        raise RuntimeError(f"Expected exactly one loaded fluid cell zone, found {names}")
    return names[0]


def ensure_absent(solver: Any, paths: list[str]) -> None:
    for path in paths:
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")


def configure_materials_and_models(solver: Any) -> None:
    setup = solver.settings.setup
    general = setup.general
    general.solver.type = "pressure-based"
    general.solver.time = "unsteady-1st-order"
    general.operating_conditions.gravity.enable = True
    general.operating_conditions.gravity.components = [0.0, -9.81, 0.0]
    general.operating_conditions.operating_pressure = 0.0

    models = setup.models
    models.energy.enabled = False
    models.discrete_phase.general_settings.interaction.enabled = False
    models.viscous.model = "k-epsilon"
    models.viscous.k_epsilon_model = "rng"

    fluid = setup.materials.fluid
    for name, density, viscosity in (
        ("water-vapor", 5.73, 15.188e-6),
        ("water-liquid", 881.77, 145.96e-6),
    ):
        if name not in set(fluid.get_object_names()):
            fluid.create(name=name)
        fluid[name].set_state(
            {
                "name": name,
                "chemical_formula": "",
                "density": {"option": "constant", "value": density},
                "viscosity": {"option": "constant", "value": viscosity},
            }
        )

    multiphase = setup.models.multiphase
    multiphase.model = "vof"
    multiphase = solver.settings.setup.models.multiphase
    state = safe_get_state(multiphase, "multiphase_after_vof")
    phase_count = state.get("number_of_phases") if isinstance(state, Mapping) else None
    if isinstance(phase_count, Mapping) and phase_count.get("number_of_eulerian_phases") not in (None, 2):
        multiphase.number_of_phases.number_of_eulerian_phases = 2

    # This is the known working 2025 R2 phase-material sequence for the VOF
    # model.  It must follow model activation and precede phase BC mutation.
    for command in (
        "/define/phases/set-domain-properties/phase-domains/phase-1/material yes water-vapor",
        "/define/phases/set-domain-properties/phase-domains/phase-2/material yes water-liquid",
    ):
        solver.scheme.exec((f'(ti-menu-load-string "{command}")',))

    # Reacquire after phase-material assignment, then enforce/read back the
    # model-specific parent and children.
    multiphase = solver.settings.setup.models.multiphase
    state = safe_get_state(multiphase, "multiphase_configured")
    parameters = state.get("vof_parameters", {}) if isinstance(state, Mapping) else {}
    if parameters.get("vof_formulation") != "explicit":
        multiphase.vof_parameters.vof_formulation = "explicit"
    interface = parameters.get("interface_modeling_options", {})
    if interface.get("interface_type") != "sharp":
        multiphase.vof_parameters.interface_modeling_options.interface_type = "sharp"


def phase_state_for_inlet(obj: Any, name: str, liquid_fraction: float) -> dict[str, Any]:
    state = safe_get_state(obj, f"velocity_inlet.{name}")
    if not isinstance(state, dict) or "phase" not in state:
        raise RuntimeError(f"VOF phase state unavailable at velocity inlet {name}: {state}")
    state["name"] = name
    state["phase"]["mixture"]["momentum"]["velocity_magnitude"] = {
        "option": "value",
        "value": 27.118,
    }
    state["phase"]["mixture"]["momentum"]["initial_gauge_pressure"] = {
        "option": "value",
        "value": 1_140_000.0,
    }
    state["phase"]["phase-2"]["multiphase"]["volume_fraction"] = {
        "option": "value",
        "value": liquid_fraction,
    }
    return state


def configure_boundaries_and_methods(solver: Any, zones: Mapping[str, str]) -> None:
    bc = solver.settings.setup.boundary_conditions
    for role, fraction in (("liquid_inlet", 1.0), ("steam_inlet", 0.0)):
        name = zones[role]
        obj = bc.velocity_inlet[name]
        obj.set_state(phase_state_for_inlet(obj, name, fraction))

    for role, liquid_backflow in (("brine_outlet", 1.0), ("steam_outlet", 0.0)):
        name = zones[role]
        obj = bc.pressure_outlet[name]
        state = safe_get_state(obj, f"pressure_outlet.{name}")
        if not isinstance(state, dict) or "phase" not in state:
            raise RuntimeError(f"VOF phase state unavailable at pressure outlet {name}: {state}")
        state["name"] = name
        state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {
            "option": "value",
            "value": 1_120_000.0,
        }
        state["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"] = {
            "option": "value",
            "value": liquid_backflow,
        }
        obj.set_state(state)

    methods = solver.settings.solution.methods
    methods.spatial_discretization.discretization_scheme["pressure"] = "presto!"
    methods.spatial_discretization.discretization_scheme["mp"] = "geo-reconstruct"


def nested_value(obj: Mapping[str, Any], *keys: str) -> Any:
    value: Any = obj
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def assert_contract(solver: Any, zones: Mapping[str, str]) -> dict[str, Any]:
    setup = solver.settings.setup
    general = safe_get_state(setup.general, "general")
    models = safe_get_state(setup.models, "models")
    bcs = safe_get_state(setup.boundary_conditions, "boundary_conditions")
    methods = safe_get_state(solver.settings.solution.methods, "solution.methods")
    required = {
        "pressure_based": nested_value(general, "solver", "type") == "pressure-based",
        "unsteady_first_order": nested_value(general, "solver", "time") == "unsteady-1st-order",
        "gravity": nested_value(general, "operating_conditions", "gravity", "enable") is True,
        "gravity_components": nested_value(general, "operating_conditions", "gravity", "components")
        == [0.0, -9.81, 0.0],
        "operating_pressure_zero": nested_value(general, "operating_conditions", "operating_pressure") == 0.0,
        "vof": nested_value(models, "multiphase", "model") == "vof",
        "two_phases": nested_value(models, "multiphase", "number_of_phases", "number_of_eulerian_phases") == 2,
        "explicit": nested_value(models, "multiphase", "vof_parameters", "vof_formulation") == "explicit",
        "sharp": nested_value(
            models,
            "multiphase",
            "vof_parameters",
            "interface_modeling_options",
            "interface_type",
        )
        == "sharp",
        "primary_vapor": nested_value(models, "multiphase", "phases", "phase-1", "material") == "water-vapor",
        "secondary_liquid": nested_value(models, "multiphase", "phases", "phase-2", "material") == "water-liquid",
        "rng_ke": nested_value(models, "viscous", "model") == "k-epsilon"
        and nested_value(models, "viscous", "k_epsilon_model") == "rng",
        "geo_reconstruct": nested_value(methods, "spatial_discretization", "discretization_scheme", "mp")
        == "geo-reconstruct",
        "presto": nested_value(methods, "spatial_discretization", "discretization_scheme", "pressure") == "presto!",
    }
    for role, expected_fraction in (("liquid_inlet", 1.0), ("steam_inlet", 0.0)):
        name = zones[role]
        base = nested_value(bcs, "velocity_inlet", name, "phase")
        required[f"{role}_velocity"] = nested_value(base, "mixture", "momentum", "velocity_magnitude", "value") == 27.118
        required[f"{role}_pressure"] = nested_value(base, "mixture", "momentum", "initial_gauge_pressure", "value") == 1_140_000.0
        required[f"{role}_liquid_fraction"] = nested_value(base, "phase-2", "multiphase", "volume_fraction", "value") == expected_fraction
    for role, expected_fraction in (("brine_outlet", 1.0), ("steam_outlet", 0.0)):
        name = zones[role]
        base = nested_value(bcs, "pressure_outlet", name, "phase")
        required[f"{role}_pressure"] = nested_value(base, "mixture", "momentum", "gauge_pressure", "value") == 1_120_000.0
        required[f"{role}_liquid_backflow"] = nested_value(
            base, "phase-2", "multiphase", "backflow_volume_fraction", "value"
        ) == expected_fraction
    failures = [name for name, ok in required.items() if not ok]
    if failures:
        raise RuntimeError(f"02d VOF contract readback failed: {failures}")
    return {"checks": required, "general": general, "models": models, "boundaries": bcs, "methods": methods}


def configure_register_boundary(solver: Any, name: str, boundary: str, distance: int) -> dict[str, Any]:
    registers = solver.settings.solution.cell_registers
    if name in registers.get_object_names():
        registers.delete(name_list=name)
    registers.create(name=name)
    registers[name].set_state(
        {
            "name": name,
            "type": {
                "option": "boundary",
                "boundary": {
                    "distance_option": {"option": "cell-distance", "cell_distance": distance},
                    "boundary_list": [boundary],
                },
            },
        }
    )
    state = safe_get_state(registers[name], name)
    boundary_state = state.get("type", {}).get("boundary", {}) if isinstance(state, Mapping) else {}
    if (
        state.get("type", {}).get("option") != "boundary"
        or boundary_state.get("boundary_list") != [boundary]
        or boundary_state.get("distance_option", {}).get("cell_distance") != distance
    ):
        raise RuntimeError(f"IC1 register readback mismatch: {state}")
    return state


def configure_register_pool(solver: Any, name: str, y_cut: float) -> dict[str, Any]:
    registers = solver.settings.solution.cell_registers
    if name in registers.get_object_names():
        registers.delete(name_list=name)
    registers.create(name=name)
    min_point = list(LOADED_MESH_BOUNDS["min_point"])
    max_point = list(LOADED_MESH_BOUNDS["max_point"])
    max_point[1] = y_cut
    registers[name].set_state(
        {
            "name": name,
            "type": {
                "option": "hexahedron",
                "hexahedron": {"min_point": min_point, "max_point": max_point, "inside": True},
            },
        }
    )
    state = safe_get_state(registers[name], name)
    hexahedron = state.get("type", {}).get("hexahedron", {}) if isinstance(state, Mapping) else {}
    readback_max = hexahedron.get("max_point", [])
    if state.get("type", {}).get("option") != "hexahedron" or len(readback_max) < 2 or readback_max[1] != y_cut:
        raise RuntimeError(f"IC2 register readback mismatch: {state}")
    return state


def patch_phase_two_liquid(solver: Any, register: str) -> None:
    solver.settings.solution.initialization.patch.calculate_patch(
        domain="phase-2", registers=[register], variable="mp", value=1.0
    )


def write_case(solver: Any, path: str) -> None:
    solver.settings.file.write_case(file_name=path)
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent did not expose written case: {path}")


def write_pair(solver: Any, case: str, data: str) -> None:
    write_case(solver, case)
    solver.settings.file.write_data(file_name=data)
    if not remote_file_exists(solver, data):
        raise RuntimeError(f"Fluent did not expose written data: {data}")


def main() -> int:
    args = parser().parse_args()
    if args.ic1_distance <= 0:
        raise ValueError("--ic1-distance must be positive")
    if not 0.0 < args.y_cut < LOADED_MESH_BOUNDS["observed_max_y"]:
        raise ValueError(f"--y-cut must be between 0 and {LOADED_MESH_BOUNDS['observed_max_y']}")

    root = args.remote_dir.rstrip("\\/")
    ic0_case = rf"{root}\VOF-IC0-P1120-loadedmesh-preinit-{args.stamp}.cas.h5"
    ic1_case = rf"{root}\VOF-IC1-P1120-loadedmesh-patch-platform-{args.stamp}.cas.h5"
    ic1_data = rf"{root}\VOF-IC1-P1120-loadedmesh-patch-platform-{args.stamp}.dat.h5"
    ic2_case = rf"{root}\VOF-IC2-Y030-P1120-loadedmesh-patch-platform-{args.stamp}.cas.h5"
    ic2_data = rf"{root}\VOF-IC2-Y030-P1120-loadedmesh-patch-platform-{args.stamp}.dat.h5"
    targets = [ic0_case, ic1_case, ic1_data, ic2_case, ic2_data]

    solver = connect(server_id=args.server_id)
    zones = resolve_zones(solver)
    fluid_zone = require_one_fluid_zone(solver)
    ensure_absent(solver, targets)

    # No mesh read: the loaded mesh is the only geometry input for this build.
    solver.tui.mesh.check()
    configure_materials_and_models(solver)
    configure_boundaries_and_methods(solver, zones)
    contract = assert_contract(solver, zones)
    write_case(solver, ic0_case)

    # IC1 is created from the clean IC0 setup, then saved as a paired field
    # checkpoint because the patch is part of the requested case definition.
    solver.settings.solution.initialization.hybrid_initialize()
    ic1_register = f"vof_ic1_brine_outlet_{args.ic1_distance}cells_loadedmesh"
    ic1_register_state = configure_register_boundary(
        solver, ic1_register, zones["brine_outlet"], args.ic1_distance
    )
    patch_phase_two_liquid(solver, ic1_register)
    write_pair(solver, ic1_case, ic1_data)

    # Rebuild one independent IC2 sibling from the saved IC1 field, not from
    # an in-memory patch state or another pool height.
    solver.settings.file.read_case(file_name=ic1_case)
    solver.settings.file.read_data(file_name=ic1_data)
    ic2_register = "vof_ic2_pool_below_y_0p30m_loadedmesh"
    ic2_register_state = configure_register_pool(solver, ic2_register, args.y_cut)
    patch_phase_two_liquid(solver, ic2_register)
    write_pair(solver, ic2_case, ic2_data)

    # Reload all three artifacts for readback.  End on IC2 so the live session
    # contains the requested final sibling and its patched field.
    solver.settings.file.read_case(file_name=ic0_case)
    ic0_contract = assert_contract(solver, zones)
    solver.settings.file.read_case(file_name=ic1_case)
    solver.settings.file.read_data(file_name=ic1_data)
    ic1_contract = assert_contract(solver, zones)
    solver.settings.file.read_case(file_name=ic2_case)
    solver.settings.file.read_data(file_name=ic2_data)
    ic2_contract = assert_contract(solver, zones)

    payload = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "fluent_version": solver.get_fluent_version(),
        "mesh_source": "currently loaded Fluent mesh; no mesh file was read",
        "mesh_case_identity": "unavailable from live Fluent filename state",
        "loaded_fluid_cell_zone": fluid_zone,
        "loaded_boundary_zones": zones,
        "loaded_mesh_bounds_used_for_ic2_register": LOADED_MESH_BOUNDS,
        "ic1_distance_cells": args.ic1_distance,
        "ic2_y_cut_m": args.y_cut,
        "ic1_register": {"name": ic1_register, "state": ic1_register_state},
        "ic2_register": {"name": ic2_register, "state": ic2_register_state},
        "artifacts": {
            "ic0_case": ic0_case,
            "ic1_case": ic1_case,
            "ic1_data": ic1_data,
            "ic2_case": ic2_case,
            "ic2_data": ic2_data,
        },
        "reload_readback": {"ic0": ic0_contract, "ic1": ic1_contract, "ic2": ic2_contract},
        "initialized": {"ic0": False, "ic1": True, "ic2": True},
        "patched": {"ic0": False, "ic1": True, "ic2": True},
        "iterated": False,
        "live_session_ends_on": "IC2-Y030 case/data",
    }
    snapshot = Path(args.snapshot_json).expanduser().resolve()
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    snapshot.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"snapshot_json: {snapshot}")
    print("fluent_left_open: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

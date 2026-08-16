#!/usr/bin/env python3
"""Build the exact-mesh Stage-1 pressure candidates for FG-MIX-T01.

This builder creates one fresh, unpatched steady Mixture parent directly from
the production mesh and then creates three independent case-only children.
Only the brine-outlet pressure differs between children.  Fluent owns Hybrid
Initialization, the 1,000-iteration native solves, and paired endpoint saves
in the separate run workflow.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402
import build_02e_y010_campaign as frozen_02c  # noqa: E402


EXACT_MESH_NAME = "Full-geomV2-231kcells.msh.h5"
DEFAULT_MESH = rf"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\{EXACT_MESH_NAME}"
DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
STEAM_PRESSURE_PA = 1_120_000.0
INLET_PRESSURE_PA = 1_140_000.0
INLET_VELOCITY_M_S = 27.118
RUN_ITERATIONS = 1_000

CANDIDATES = (
    ("FG-MIX-T01-S1-C136", "brine-p1136kpa", 1_136_000.0),
    ("FG-MIX-T01-S1-C1375", "brine-p1137p5kpa", 1_137_500.0),
    ("FG-MIX-T01-S1-C139", "brine-p1139kpa", 1_139_000.0),
)


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def require_exact_mesh(mesh: str) -> None:
    if PureWindowsPath(mesh).name != EXACT_MESH_NAME:
        raise ValueError(
            f"This Stage-1 candidate workflow is locked to {EXACT_MESH_NAME!r}; got {mesh!r}"
        )


def pressure_value(state: dict[str, Any]) -> float:
    return float(state["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])


def read_contract(solver: Any, zones: dict[str, str]) -> dict[str, Any]:
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "boundary contract")
    models = safe_get_state(solver.settings.setup.models, "model contract")
    pressure_outlets = boundaries["pressure_outlet"]
    velocity_inlets = boundaries["velocity_inlet"]
    brine = pressure_outlets[zones["brine_outlet"]]
    steam = pressure_outlets[zones["steam_outlet"]]
    liquid = velocity_inlets[zones["liquid_inlet"]]
    vapour = velocity_inlets[zones["steam_inlet"]]
    return {
        "mesh_name": EXACT_MESH_NAME,
        "zones": zones,
        "models": {
            "multiphase": nested(models, "multiphase", "model"),
            "viscous": nested(models, "viscous", "model"),
            "k_epsilon_model": nested(models, "viscous", "k_epsilon_model"),
            "energy_enabled": nested(models, "energy", "enabled"),
        },
        "pressures_pa": {
            "brine_outlet": pressure_value(brine),
            "steam_outlet": pressure_value(steam),
            "liquid_inlet_initial": float(
                nested(liquid, "phase", "mixture", "momentum", "initial_gauge_pressure", "value")
            ),
            "steam_inlet_initial": float(
                nested(vapour, "phase", "mixture", "momentum", "initial_gauge_pressure", "value")
            ),
        },
        "inlet_velocity_m_s": {
            "liquid": float(nested(liquid, "phase", "phase-2", "momentum", "velocity_magnitude", "value")),
            "steam": float(nested(vapour, "phase", "phase-1", "momentum", "velocity_magnitude", "value")),
        },
        "inlet_liquid_volume_fraction": float(
            nested(liquid, "phase", "phase-2", "multiphase", "volume_fraction", "value")
        ),
        "inlet_steam_liquid_volume_fraction": float(
            nested(vapour, "phase", "phase-2", "multiphase", "volume_fraction", "value")
        ),
        "brine_backflow_liquid_volume_fraction": float(
            nested(brine, "phase", "phase-2", "multiphase", "backflow_volume_fraction", "value")
        ),
        "steam_backflow_liquid_volume_fraction": float(
            nested(steam, "phase", "phase-2", "multiphase", "backflow_volume_fraction", "value")
        ),
    }


def validate_common_contract(contract: dict[str, Any]) -> None:
    if contract["models"] != {
        "multiphase": "mixture",
        "viscous": "k-epsilon",
        "k_epsilon_model": "rng",
        "energy_enabled": False,
    }:
        raise RuntimeError(f"Unexpected Stage-1 model contract: {contract['models']}")
    if contract["pressures_pa"]["steam_outlet"] != STEAM_PRESSURE_PA:
        raise RuntimeError("Steam outlet is not the frozen 1.120 MPa gauge pressure")
    for key in ("liquid_inlet_initial", "steam_inlet_initial"):
        if contract["pressures_pa"][key] != INLET_PRESSURE_PA:
            raise RuntimeError(f"{key} is not the frozen 1.140 MPa gauge pressure")
    if contract["inlet_velocity_m_s"] != {"liquid": INLET_VELOCITY_M_S, "steam": INLET_VELOCITY_M_S}:
        raise RuntimeError(f"Split-inlet velocity contract changed: {contract['inlet_velocity_m_s']}")
    if contract["inlet_liquid_volume_fraction"] != 1.0 or contract["inlet_steam_liquid_volume_fraction"] != 0.0:
        raise RuntimeError("Split-inlet phase fractions are not liquid-dominant / vapour-dominant")
    if contract["brine_backflow_liquid_volume_fraction"] != 1.0:
        raise RuntimeError("Brine backflow liquid volume fraction is not 1.0")
    if contract["steam_backflow_liquid_volume_fraction"] != 0.0:
        raise RuntimeError("Steam-outlet backflow liquid volume fraction is not 0.0")


def set_brine_pressure(solver: Any, zone: str, requested_pa: float) -> dict[str, Any]:
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet[zone]
    before = outlet.get_state()
    if pressure_value(before) == requested_pa:
        raise RuntimeError(f"Parent already has candidate pressure {requested_pa} Pa")
    outlet.set_state(
        {
            "phase": {
                "mixture": {
                    "momentum": {
                        "gauge_pressure": {"option": "value", "value": requested_pa}
                    }
                }
            }
        }
    )
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet[zone]
    after = outlet.get_state()
    actual = pressure_value(after)
    if actual != requested_pa:
        raise RuntimeError(f"Brine pressure readback mismatch: requested={requested_pa}, actual={actual}")
    return {"before": before, "after": after}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--mesh", default=DEFAULT_MESH)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument(
        "--stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="UTC artifact stamp used to make all remote filenames unique",
    )
    parser.add_argument("--snapshot-json", required=True)
    args = parser.parse_args()
    require_exact_mesh(args.mesh)

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not remote_file_exists(solver, args.mesh):
        raise FileNotFoundError(f"Exact production mesh is not visible on {args.server_id}: {args.mesh}")

    remote_dir = PureWindowsPath(args.remote_dir)
    parent_case = str(remote_dir / f"FG-MIX-T01-S1-steady-parent-unpatched-{args.stamp}.cas.h5")
    if remote_file_exists(solver, parent_case):
        raise FileExistsError(f"Refusing to overwrite parent artifact: {parent_case}")

    # Read the exact mesh and configure the prescribed 02c Mixture contract.
    solver.settings.file.read_mesh(file_name=args.mesh)
    zones = frozen_02c.resolve_zones(solver)
    frozen_02c.ensure_materials_and_models(solver)
    frozen_02c.configure_frozen_boundaries(solver, zones)
    frozen_02c.configure_solution(solver)
    parent_contract = read_contract(solver, zones)
    validate_common_contract(parent_contract)

    # This is intentionally a case-only, uninitialized parent.  No Y010
    # register, phase patch, Hybrid Initialization, or solve is issued here.
    write_case_only(solver, parent_case, "Write FG-MIX-T01 Stage-1 unpatched parent")
    if not remote_file_exists(solver, parent_case):
        raise RuntimeError(f"Parent case was not visible after write: {parent_case}")

    children: list[dict[str, Any]] = []
    for case_id, suffix, pressure_pa in CANDIDATES:
        child_case = str(
            remote_dir
            / f"{case_id}-{suffix}-unpatched-preinit-{args.stamp}.cas.h5"
        )
        if remote_file_exists(solver, child_case):
            raise FileExistsError(f"Refusing to overwrite candidate artifact: {child_case}")
        load_case_only(solver, parent_case, label=f"Reload exact-mesh parent for {case_id}")
        reloaded_parent = read_contract(solver, zones)
        if reloaded_parent != parent_contract:
            raise RuntimeError(f"Parent readback changed before {case_id}: {reloaded_parent}")
        pressure_audit = set_brine_pressure(solver, zones["brine_outlet"], pressure_pa)
        write_case_only(solver, child_case, f"Write {case_id} case-only child")
        if not remote_file_exists(solver, child_case):
            raise RuntimeError(f"Child case was not visible after write: {child_case}")
        load_case_only(solver, child_case, label=f"Reload and verify {case_id}")
        child_contract = read_contract(solver, zones)
        expected = deepcopy(parent_contract)
        expected["pressures_pa"]["brine_outlet"] = pressure_pa
        if child_contract != expected:
            raise RuntimeError(
                f"{case_id} differs outside brine pressure: expected={expected}, got={child_contract}"
            )
        children.append(
            {
                "case_id": case_id,
                "pressure_pa": pressure_pa,
                "delta_vs_steam_pa": pressure_pa - STEAM_PRESSURE_PA,
                "case_file": child_case,
                "status": "CASE_ONLY_VERIFIED",
                "pressure_readback": pressure_audit,
                "contract": child_contract,
            }
        )

    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S1",
        "purpose": "three pressure candidates for a quick 1,000-iteration steady parent screen",
        "status": "CASE_ONLY_VERIFIED",
        "server_id": args.server_id,
        "fluent_version": str(solver.get_fluent_version()),
        "mesh": args.mesh,
        "mesh_identity_rule": f"basename must equal {EXACT_MESH_NAME}",
        "parent_case": parent_case,
        "parent_initialization": "uninitialized; no Y010 patch",
        "native_iterations_per_candidate": RUN_ITERATIONS,
        "steam_outlet_pressure_pa": STEAM_PRESSURE_PA,
        "parent_contract": parent_contract,
        "children": children,
        "run_policy": "Fluent-native Hybrid Initialization, 1,000 steady iterations, and paired case/data endpoint write are separate.",
    }
    output = Path(args.snapshot_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    print(f"snapshot_json: {output}", flush=True)
    print("No initialization, iteration, or data write was issued.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

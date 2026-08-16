#!/usr/bin/env python3
"""Build the single current 02c-H Student case at 1.140 MPa.

The selected Student parent is an explicitly named, pre-initialization
surrogate. This script changes only the brine-outlet gauge pressure and stops
after a case-only write plus reload/readback verification. Fluent owns Hybrid
Initialization, iteration, and case/data checkpointing in the separate native
run workflow.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


DEFAULT_PARENT = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\02c-C-brine-p1125kpa-unprimed-preinit-20260815T231711Z.cas.h5"
DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case"
REQUESTED_PRESSURE_PA = 1_140_000
STEAM_PRESSURE_PA = 1_120_000
EXPECTED_INLET_REFERENCE_PA = 1_140_000
EXPECTED_VELOCITY = 27.118


def pressure_value(state: dict[str, Any]) -> float:
    return float(state["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])


def initial_pressure_value(state: dict[str, Any]) -> float:
    return float(state["phase"]["mixture"]["momentum"]["initial_gauge_pressure"]["value"])


def find_zone(mapping: dict[str, Any], expected: str) -> str:
    normalized = expected.replace("-", "").casefold()
    for name in mapping:
        if str(name).replace("-", "").casefold() == normalized:
            return str(name)
    raise RuntimeError(f"Required zone {expected!r} is unavailable; found {sorted(mapping)}")


def velocity_value(state: dict[str, Any], phase: str) -> float:
    return float(state["phase"][phase]["momentum"]["velocity_magnitude"]["value"])


def volume_fraction_value(state: dict[str, Any]) -> float:
    return float(state["phase"]["phase-2"]["multiphase"]["volume_fraction"]["value"])


def compact_contract(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions.get_state()
    models = solver.settings.setup.models.get_state()
    outlet_vents = boundaries.get("outlet_vent", {})
    pressure_outlets = boundaries.get("pressure_outlet", {})
    velocity_inlets = boundaries.get("velocity_inlet", {})
    if not isinstance(outlet_vents, dict) or not isinstance(pressure_outlets, dict) or not isinstance(velocity_inlets, dict):
        raise RuntimeError("Required boundary branches are unavailable")

    if "brineoutlet" in {str(name).replace("-", "").casefold() for name in outlet_vents}:
        brine_boundary_type = "outlet_vent"
        brine_name = find_zone(outlet_vents, "brineoutlet")
    else:
        brine_boundary_type = "pressure_outlet"
        brine_name = find_zone(pressure_outlets, "brineoutlet")
    steam_name = find_zone(pressure_outlets, "steamoutlet")
    liquid_name = find_zone(velocity_inlets, "liquidinlet")
    inlet_steam_name = find_zone(velocity_inlets, "steaminlet")
    brine = (outlet_vents if brine_boundary_type == "outlet_vent" else pressure_outlets)[brine_name]
    steam = pressure_outlets[steam_name]
    liquid_inlet = velocity_inlets[liquid_name]
    steam_inlet = velocity_inlets[inlet_steam_name]

    multiphase = models.get("multiphase", {})
    viscous = models.get("viscous", {})
    if multiphase.get("model") != "mixture":
        raise RuntimeError(f"Student parent is not Mixture: {multiphase.get('model')!r}")
    if viscous.get("model") != "k-epsilon" or viscous.get("k_epsilon_model") != "rng":
        raise RuntimeError("Student parent is not RNG k-epsilon")
    if models.get("energy", {}).get("enabled") is not False:
        raise RuntimeError("Student parent Energy state is not off")

    return {
        "zone_names": {
            "brine_outlet": brine_name,
            "steam_outlet": steam_name,
            "liquid_inlet": liquid_name,
            "steam_inlet": inlet_steam_name,
        },
        "boundary_types": {"brine_outlet": brine_boundary_type, "steam_outlet": "pressure_outlet"},
        "brine_pressure_pa": pressure_value(brine),
        "steam_pressure_pa": pressure_value(steam),
        "inlet_reference_pa": {
            "liquid": initial_pressure_value(liquid_inlet),
            "steam": initial_pressure_value(steam_inlet),
        },
        "inlet_velocity_m_s": {
            "liquid": velocity_value(liquid_inlet, "phase-2"),
            "steam": velocity_value(steam_inlet, "phase-1"),
        },
        "inlet_volume_fraction_phase_2": {
            "liquid": float(liquid_inlet["phase"]["phase-2"]["multiphase"]["volume_fraction"]["value"]),
            "steam": float(steam_inlet["phase"]["phase-2"]["multiphase"]["volume_fraction"]["value"]),
        },
        "brine_backflow_volume_fraction_phase_2": float(
            brine["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"]["value"]
        ),
        "steam_backflow_volume_fraction_phase_2": float(
            steam["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"]["value"]
        ),
        "models": {
            "multiphase": multiphase.get("model"),
            "viscous": viscous.get("model"),
            "k_epsilon_model": viscous.get("k_epsilon_model"),
            "energy_enabled": models.get("energy", {}).get("enabled"),
        },
    }


def set_brine_pressure(solver: Any, brine_name: str, boundary_type: str) -> dict[str, Any]:
    branch = solver.settings.setup.boundary_conditions.outlet_vent if boundary_type == "outlet_vent" else solver.settings.setup.boundary_conditions.pressure_outlet
    outlet = branch[brine_name]
    before = outlet.get_state()
    if pressure_value(before) == REQUESTED_PRESSURE_PA:
        raise RuntimeError("Selected parent already has the requested H pressure")
    outlet.set_state(
        {"phase": {"mixture": {"momentum": {"gauge_pressure": {"option": "value", "value": REQUESTED_PRESSURE_PA}}}}}
    )
    branch = solver.settings.setup.boundary_conditions.outlet_vent if boundary_type == "outlet_vent" else solver.settings.setup.boundary_conditions.pressure_outlet
    outlet = branch[brine_name]
    after = outlet.get_state()
    if pressure_value(after) != REQUESTED_PRESSURE_PA:
        raise RuntimeError(f"Brine-pressure readback mismatch: {pressure_value(after)}")
    return {"before": before, "after": after}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--parent-case", default=DEFAULT_PARENT)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--stamp", required=True, help="UTC artifact stamp, e.g. 20260816T120000Z")
    parser.add_argument("--output-json", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    solver = connect(args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not remote_file_exists(solver, args.parent_case):
        raise FileNotFoundError(f"Student parent is not visible: {args.parent_case}")

    load_case_only(solver, args.parent_case, label="Load explicit Student 02c pre-initialization parent")
    parent_contract = compact_contract(solver)
    if parent_contract["steam_pressure_pa"] != STEAM_PRESSURE_PA:
        raise RuntimeError("Student parent steam outlet is not 1.120 MPa")
    if any(value != EXPECTED_INLET_REFERENCE_PA for value in parent_contract["inlet_reference_pa"].values()):
        raise RuntimeError("Student parent inlet reference is not 1.140 MPa on both inlets")
    if any(value != EXPECTED_VELOCITY for value in parent_contract["inlet_velocity_m_s"].values()):
        raise RuntimeError("Student parent split-inlet velocity is not 27.118 m/s")

    pressure_audit = set_brine_pressure(
        solver,
        parent_contract["zone_names"]["brine_outlet"],
        parent_contract["boundary_types"]["brine_outlet"],
    )
    output_case = str(
        PureWindowsPath(args.remote_dir)
        / f"02c-H-brine-p1140kpa-unprimed-student-preinit-{args.stamp}.cas.h5"
    )
    if remote_file_exists(solver, output_case):
        raise FileExistsError(f"Refusing to overwrite existing Student child: {output_case}")
    write_case_only(solver, output_case, label="Write 02c-H Student case-only child")
    if not remote_file_exists(solver, output_case):
        raise RuntimeError(f"Student child was not visible after write: {output_case}")

    load_case_only(solver, output_case, label="Reload and verify 02c-H Student case-only child")
    child_contract = compact_contract(solver)
    expected = deepcopy(parent_contract)
    expected["brine_pressure_pa"] = REQUESTED_PRESSURE_PA
    if child_contract != expected:
        raise RuntimeError(
            "Reloaded Student child differs outside the requested brine pressure; "
            f"expected={json.dumps(expected, sort_keys=True)}, got={json.dumps(child_contract, sort_keys=True)}"
        )

    manifest = {
        "case_id": "02c-H",
        "status": "CASE_ONLY_VERIFIED",
        "server_id": args.server_id,
        "fluent_version": str(solver.get_fluent_version()),
        "parent_case": args.parent_case,
        "child_case": output_case,
        "pressure_pa": REQUESTED_PRESSURE_PA,
        "steam_pressure_pa": STEAM_PRESSURE_PA,
        "parent_contract": parent_contract,
        "pressure_readback": pressure_audit,
        "child_contract": child_contract,
        "lineage_note": "Student mesh-derived surrogate parent; not certified as server-2 exact 02c mesh parity.",
        "run_policy": "Fluent-native Hybrid Initialization, 500 steady iterations, and paired case/data write are separate.",
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"CASE_ONLY_VERIFIED: {output_case}", flush=True)
    print(f"manifest: {args.output_json}", flush=True)
    print("No initialization, iteration, or data write was issued.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

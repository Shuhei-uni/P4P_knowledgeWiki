#!/usr/bin/env python3
"""Build isolated, case-only 02c positive-backpressure screen children.

This script intentionally stops before initialization or iteration.  It uses
the existing Fluent gRPC session only to make and verify setup children.  Each
child starts by reloading the same frozen pre-initialization parent, so no
solved field from another pressure point can contaminate the comparison.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


PARENT_CASE = r"C:\Users\syok443\P4P simulation\brine outlet\02c-B-brine-p1120kpa-unprimed-preinit-20260812T043007Z.cas.h5"
REMOTE_DIR = str(PureWindowsPath(PARENT_CASE).parent)
STEAM_PRESSURE_PA = 1_120_000
JOBS = (
    ("02c-D", "brine-p1122p5kpa-unprimed", 1_122_500),
    ("02c-E", "brine-p1127p5kpa-unprimed", 1_127_500),
    ("02c-F", "brine-p1130kpa-unprimed", 1_130_000),
    ("02c-G", "brine-p1135kpa-unprimed", 1_135_000),
)


def pressure_value(state: dict[str, Any]) -> float:
    return float(state["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])


def require_parent_contract(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions.get_state()
    if not {"brine-outlet", "steam-outlet"}.issubset(boundaries.get("pressure_outlet", {})):
        raise RuntimeError("Parent does not expose both brine-outlet and steam-outlet as pressure outlets")
    if not {"liquid-inlet", "steam-inlet"}.issubset(boundaries.get("velocity_inlet", {})):
        raise RuntimeError("Parent does not expose the expected split velocity-inlet topology")

    models = solver.settings.setup.models.get_state()
    multiphase = models.get("multiphase", {})
    if multiphase.get("model") != "mixture":
        raise RuntimeError(f"Parent multiphase model is not Mixture: {multiphase.get('model')!r}")
    viscous = models.get("viscous", {})
    if viscous.get("model") != "k-epsilon" or viscous.get("k_epsilon_model") != "rng":
        raise RuntimeError("Parent turbulence model is not RNG k-epsilon")

    brine = boundaries["pressure_outlet"]["brine-outlet"]
    steam = boundaries["pressure_outlet"]["steam-outlet"]
    if pressure_value(steam) != STEAM_PRESSURE_PA:
        raise RuntimeError(f"Steam outlet differs from frozen {STEAM_PRESSURE_PA} Pa: {pressure_value(steam)}")
    return {"boundaries": boundaries, "models": models}


def set_brine_pressure(solver: Any, requested_pa: int) -> dict[str, Any]:
    # The 2025 R2 live parent has this exact multiphase state shape. Reacquire
    # after setting, because Fluent settings handles may be stale after a write.
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet["brine-outlet"]
    before = outlet.get_state()
    if pressure_value(before) == requested_pa:
        raise RuntimeError("Frozen parent unexpectedly already has the requested child pressure")
    outlet.set_state({
        "phase": {"mixture": {"momentum": {"gauge_pressure": {"option": "value", "value": requested_pa}}}}
    })
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet["brine-outlet"]
    after = outlet.get_state()
    actual = pressure_value(after)
    if actual != requested_pa:
        raise RuntimeError(f"Brine pressure readback mismatch: requested {requested_pa}, got {actual}")
    return {"before": before, "after": after}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--stamp", required=True, help="UTC timestamp, e.g. 20260812T120000Z")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument(
        "--case-id",
        action="append",
        choices=[job[0] for job in JOBS],
        help="Build only this case (repeatable). Defaults to every pending case.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    solver = connect(args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not solver.is_active():
        raise RuntimeError("Fluent session is not active")
    if not remote_file_exists(solver, PARENT_CASE):
        raise FileNotFoundError(f"Frozen 02c parent is not visible on Fluent host: {PARENT_CASE}")

    manifest: dict[str, Any] = {
        "queue_id": "02c-positive-backpressure-screen",
        "purpose": "case-only preparation; Fluent-native runs are separate",
        "fluent_version": str(solver.get_fluent_version()),
        "parent_case": PARENT_CASE,
        "jobs": {},
    }
    selected = set(args.case_id or [job[0] for job in JOBS])
    for case_id, suffix, pressure_pa in JOBS:
        if case_id not in selected:
            continue
        load_case_only(solver, PARENT_CASE, label=f"Load frozen parent for {case_id}")
        parent_audit = require_parent_contract(solver)
        pressure_audit = set_brine_pressure(solver, pressure_pa)
        child = str(PureWindowsPath(REMOTE_DIR) / f"{case_id}-{suffix}-preinit-{args.stamp}.cas.h5")
        if remote_file_exists(solver, child):
            raise FileExistsError(f"Refusing to overwrite existing child: {child}")
        write_case_only(solver, child, label=f"Write {case_id} pre-initialization case")
        if not remote_file_exists(solver, child):
            raise RuntimeError(f"Fluent did not expose the written child: {child}")
        load_case_only(solver, child, label=f"Reload and verify {case_id}")
        child_audit = require_parent_contract(solver)
        child_brine = child_audit["boundaries"]["pressure_outlet"]["brine-outlet"]
        if pressure_value(child_brine) != pressure_pa:
            raise RuntimeError(f"{case_id} reload lost brine-pressure value")
        manifest["jobs"][case_id] = {
            "status": "CASE_ONLY_VERIFIED",
            "pressure_pa": pressure_pa,
            "delta_vs_steam_pa": pressure_pa - STEAM_PRESSURE_PA,
            "case_file": child,
            "parent_contract": parent_audit,
            "pressure_readback": pressure_audit,
            "child_contract": child_audit,
        }
        print(f"{case_id}: CASE_ONLY_VERIFIED -> {child}", flush=True)

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"manifest: {args.output_json}")
    print("No initialization, iteration, data write, or Fluent shutdown was issued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

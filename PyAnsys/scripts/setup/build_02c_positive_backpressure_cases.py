#!/usr/bin/env python3
"""Build isolated, case-only 02c positive-backpressure screen children.

This script intentionally stops before initialization or iteration.  It uses
the existing Fluent gRPC session only to make and verify setup children.  Each
child starts by reloading the same frozen pre-initialization parent, so no
solved field from another pressure point can contaminate the comparison.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
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
# Coarse upper sweep requested after D--G: offsets are above the nominal
# 1.140 MPa inlet reference/initial gauge pressure, not above the steam outlet.
# The steam outlet remains fixed at 1.120 MPa for every child.
ABOVE_INLET_JOBS = (
    ("02c-H20", "brine-p1160kpa-unprimed", 1_160_000),
    ("02c-H25", "brine-p1165kpa-unprimed", 1_165_000),
    ("02c-H30", "brine-p1170kpa-unprimed", 1_170_000),
    ("02c-H35", "brine-p1175kpa-unprimed", 1_175_000),
    ("02c-H40", "brine-p1180kpa-unprimed", 1_180_000),
    ("02c-H45", "brine-p1185kpa-unprimed", 1_185_000),
    ("02c-H50", "brine-p1190kpa-unprimed", 1_190_000),
)
# A separate broad screen.  The I lineage deliberately remains distinct from
# H20--H50, including at the overlapping 1.160 and 1.180 MPa points, so an
# already-built or already-submitted H artifact can never be overwritten or
# silently treated as an I child.
ABOVE_INLET_COARSE_JOBS = (
    ("02c-I20", "brine-p1160kpa-unprimed-coarse130", 1_160_000),
    ("02c-I40", "brine-p1180kpa-unprimed-coarse130", 1_180_000),
    ("02c-I60", "brine-p1200kpa-unprimed-coarse130", 1_200_000),
    ("02c-I80", "brine-p1220kpa-unprimed-coarse130", 1_220_000),
    ("02c-I100", "brine-p1240kpa-unprimed-coarse130", 1_240_000),
    ("02c-I120", "brine-p1260kpa-unprimed-coarse130", 1_260_000),
    ("02c-I140", "brine-p1280kpa-unprimed-coarse130", 1_280_000),
    ("02c-I160", "brine-p1300kpa-unprimed-coarse130", 1_300_000),
)


def pressure_value(state: dict[str, Any]) -> float:
    return float(state["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])


def find_zone_name(zones: dict[str, Any], expected: str) -> str:
    normalized = expected.replace("-", "").casefold()
    for name in zones:
        if str(name).replace("-", "").casefold() == normalized:
            return str(name)
    raise RuntimeError(f"Required zone {expected!r} is unavailable; found {sorted(zones)}")


def require_parent_contract(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions.get_state()
    pressure_outlets = boundaries.get("pressure_outlet", {})
    velocity_inlets = boundaries.get("velocity_inlet", {})
    if not isinstance(pressure_outlets, dict) or not isinstance(velocity_inlets, dict):
        raise RuntimeError("Parent boundary-state branches are unavailable")
    zone_names = {
        "brine_outlet": find_zone_name(pressure_outlets, "brine-outlet"),
        "steam_outlet": find_zone_name(pressure_outlets, "steam-outlet"),
        "liquid_inlet": find_zone_name(velocity_inlets, "liquid-inlet"),
        "steam_inlet": find_zone_name(velocity_inlets, "steam-inlet"),
    }

    models = solver.settings.setup.models.get_state()
    multiphase = models.get("multiphase", {})
    if multiphase.get("model") != "mixture":
        raise RuntimeError(f"Parent multiphase model is not Mixture: {multiphase.get('model')!r}")
    viscous = models.get("viscous", {})
    if viscous.get("model") != "k-epsilon" or viscous.get("k_epsilon_model") != "rng":
        raise RuntimeError("Parent turbulence model is not RNG k-epsilon")

    brine = pressure_outlets[zone_names["brine_outlet"]]
    steam = pressure_outlets[zone_names["steam_outlet"]]
    if pressure_value(steam) != STEAM_PRESSURE_PA:
        raise RuntimeError(f"Steam outlet differs from frozen {STEAM_PRESSURE_PA} Pa: {pressure_value(steam)}")
    return {"boundaries": boundaries, "models": models, "zone_names": zone_names}


def set_brine_pressure(solver: Any, requested_pa: int, brine_outlet: str) -> dict[str, Any]:
    # The 2025 R2 live parent has this exact multiphase state shape. Reacquire
    # after setting, because Fluent settings handles may be stale after a write.
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet[brine_outlet]
    before = outlet.get_state()
    if pressure_value(before) == requested_pa:
        raise RuntimeError("Frozen parent unexpectedly already has the requested child pressure")
    outlet.set_state({
        "phase": {"mixture": {"momentum": {"gauge_pressure": {"option": "value", "value": requested_pa}}}}
    })
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet[brine_outlet]
    after = outlet.get_state()
    actual = pressure_value(after)
    if actual != requested_pa:
        raise RuntimeError(f"Brine pressure readback mismatch: requested {requested_pa}, got {actual}")
    return {"before": before, "after": after}


def require_child_contract_matches_parent(
    parent_audit: dict[str, Any],
    child_audit: dict[str, Any],
    requested_pa: int,
) -> None:
    """Require every recorded parent boundary/model value to survive the child write.

    The requested brine gauge pressure is the only permitted difference in the
    audited contract.  This remains intentionally scoped to the records the
    builder already checks live; all other case settings are inherited by
    loading the immutable parent before each one-field mutation.
    """

    expected = deepcopy(parent_audit)
    expected["boundaries"]["pressure_outlet"][expected["zone_names"]["brine_outlet"]]["phase"]["mixture"]["momentum"]["gauge_pressure"][
        "value"
    ] = requested_pa
    if child_audit != expected:
        raise RuntimeError(
            "Reloaded child differs from the frozen parent outside the requested "
            "brine-outlet gauge-pressure change"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument(
        "--parent-case",
        default=PARENT_CASE,
        help="Absolute remote pre-initialization parent case. Defaults to the verified 02c-B parent.",
    )
    parser.add_argument(
        "--artifact-tag",
        default="",
        help="Optional safe filename tag, for example student-smoke.",
    )
    parser.add_argument("--stamp", required=True, help="UTC timestamp, e.g. 20260812T120000Z")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument(
        "--case-id",
        action="append",
        choices=[job[0] for job in (*JOBS, *ABOVE_INLET_JOBS, *ABOVE_INLET_COARSE_JOBS)],
        help="Build only this case (repeatable). Defaults to every pending case.",
    )
    parser.add_argument(
        "--matrix",
        choices=("positive-d-to-g", "above-inlet-20-to-50", "above-inlet-20-to-130-coarse"),
        default="positive-d-to-g",
        help="Select the named 02c pressure matrix to build.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    solver = connect(args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not solver.is_active():
        raise RuntimeError("Fluent session is not active")
    parent_case = args.parent_case
    remote_dir = str(PureWindowsPath(parent_case).parent)
    if not remote_file_exists(solver, parent_case):
        raise FileNotFoundError(f"Selected pre-initialization parent is not visible on Fluent host: {parent_case}")

    manifest: dict[str, Any] = {
        "queue_id": {
            "positive-d-to-g": "02c-positive-backpressure-screen",
            "above-inlet-20-to-50": "02c-above-inlet-20-to-50-screen",
            "above-inlet-20-to-130-coarse": "02c-above-inlet-20-to-130-coarse-screen",
        }[args.matrix],
        "purpose": "case-only preparation; Fluent-native runs are separate",
        "fluent_version": str(solver.get_fluent_version()),
        "parent_case": parent_case,
        "jobs": {},
    }
    matrix_jobs = {
        "positive-d-to-g": JOBS,
        "above-inlet-20-to-50": ABOVE_INLET_JOBS,
        "above-inlet-20-to-130-coarse": ABOVE_INLET_COARSE_JOBS,
    }[args.matrix]
    selected = set(args.case_id or [job[0] for job in matrix_jobs])
    for case_id, suffix, pressure_pa in matrix_jobs:
        if case_id not in selected:
            continue
        load_case_only(solver, parent_case, label=f"Load frozen parent for {case_id}")
        parent_audit = require_parent_contract(solver)
        pressure_audit = set_brine_pressure(solver, pressure_pa, parent_audit["zone_names"]["brine_outlet"])
        artifact_suffix = f"{suffix}-{args.artifact_tag.strip()}" if args.artifact_tag.strip() else suffix
        child = str(PureWindowsPath(remote_dir) / f"{case_id}-{artifact_suffix}-preinit-{args.stamp}.cas.h5")
        if remote_file_exists(solver, child):
            raise FileExistsError(f"Refusing to overwrite existing child: {child}")
        write_case_only(solver, child, label=f"Write {case_id} pre-initialization case")
        if not remote_file_exists(solver, child):
            raise RuntimeError(f"Fluent did not expose the written child: {child}")
        load_case_only(solver, child, label=f"Reload and verify {case_id}")
        child_audit = require_parent_contract(solver)
        child_brine = child_audit["boundaries"]["pressure_outlet"][child_audit["zone_names"]["brine_outlet"]]
        if pressure_value(child_brine) != pressure_pa:
            raise RuntimeError(f"{case_id} reload lost brine-pressure value")
        require_child_contract_matches_parent(parent_audit, child_audit, pressure_pa)
        manifest["jobs"][case_id] = {
            "status": "CASE_ONLY_VERIFIED",
            "pressure_pa": pressure_pa,
            "artifact_suffix": artifact_suffix,
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

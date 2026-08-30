#!/usr/bin/env python3
"""Build, prove, and run one bounded Phase-06 Stage-01 discovery child.

This is an attached discovery runner. Its local manifest is an operational
record, not Project scientific evidence: it is written at launch and updated
at every material boundary so an interrupted RPC cannot look like a completed
solve.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import sys
import time
import traceback
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import ensure_remote_directory, redirect_report_files


PARENT_CASE = r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\P5\F11\F11.cas.h5"
PARENT_DATA = r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\P5\F11\F11.dat.h5"
POOL_MASS_REPORT_FILES = (
    "03a_stage3_inventory_y010_liquid_mass-rfile",
    "03a_stage3_inventory_y030_liquid_mass-rfile",
)


def get_at(value: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def clock(solver: Any) -> int:
    return int(solver.scheme.eval("(rpgetvar 'current-iteration)"))


def prove_quiescent(solver: Any, samples: int = 3, delay_seconds: float = 2.0) -> dict[str, Any]:
    """Bounded read-only ownership preflight when client reporting is unavailable."""
    run_calculation = solver.settings.solution.run_calculation
    if run_calculation.iterating():
        raise RuntimeError("Fluent reports iterating=true before this discovery run; remote solve must be reconciled first")
    coordinates: list[int] = []
    for index in range(samples):
        coordinates.append(clock(solver))
        if index + 1 < samples:
            time.sleep(delay_seconds)
    solver.settings.solution.controls.equations.get_state()
    if len(set(coordinates)) != 1:
        raise RuntimeError(f"Fluent is not quiescent before mutation: iterations={coordinates}")
    return {
        "iteration_samples": coordinates,
        "status": "QUIESCENT",
        "limitation": "Fluent 2025 R2 returned no connected-client text through this endpoint; no known local runner owns this server.",
    }


def write_status(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically update the deliberately mutable operational manifest."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def event(payload: dict[str, Any], name: str, **details: Any) -> None:
    payload.setdefault("events", []).append({"epoch": time.time(), "event": name, **details})
    print(json.dumps(payload["events"][-1], default=str), flush=True)


def parent_audit(solver: Any) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "models")
    bc = safe_get_state(solver.settings.setup.boundary_conditions, "bc")
    if get_at(models, "multiphase", "model") != "mixture":
        raise RuntimeError("F11 parent is not Mixture")
    if get_at(models, "viscous", "k_epsilon_model") != "rng":
        raise RuntimeError("F11 parent is not RNG k-epsilon")
    if "brineoutlet" not in bc.get("pressure_outlet", {}):
        raise RuntimeError("F11 brine outlet missing")
    return {"models": models, "brine": bc["pressure_outlet"]["brineoutlet"], "iteration": clock(solver)}


def set_outlet(solver: Any, lane: str, loss: float) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    if lane == "reference":
        return safe_get_state(bc.pressure_outlet["brineoutlet"], "reference")
    if lane != "vent":
        raise ValueError(lane)
    baseline = safe_get_state(bc.pressure_outlet["brineoutlet"], "pressure")
    pressure = float(get_at(baseline, "phase", "mixture", "momentum", "gauge_pressure", "value"))
    bc.set_zone_type(zone_list=["brineoutlet"], new_type="outlet-vent")
    obj = solver.settings.setup.boundary_conditions.outlet_vent["brineoutlet"]
    state = safe_get_state(obj, "vent")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": pressure}
    obj.set_state(state)
    momentum = solver.settings.setup.boundary_conditions.outlet_vent["brineoutlet"].phase["mixture"].momentum
    momentum.loss_coefficient.option = "constant"
    momentum.loss_coefficient.value = loss
    after = safe_get_state(solver.settings.setup.boundary_conditions.outlet_vent["brineoutlet"], "vent-after")
    actual_loss = float(get_at(after, "phase", "mixture", "momentum", "loss_coefficient", "value"))
    if abs(actual_loss - loss) > 1e-12:
        raise RuntimeError("vent loss readback mismatch")
    return after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--lane", choices=("reference", "vent"), required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--loss", type=float, default=10.0)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    if args.iterations <= 0:
        raise ValueError("--iterations must be positive")
    manifest = args.manifest.expanduser().resolve()
    if manifest.exists():
        raise FileExistsError(f"Refusing to overwrite operational manifest: {manifest}")
    payload: dict[str, Any] = {
        "status": "RUNNING", "lane": args.lane, "server_id": str(args.server_id),
        "parent_case": PARENT_CASE, "parent_data": PARENT_DATA, "run_root": args.run_root,
        "requested_smoke_iterations": 50, "requested_discovery_iterations": args.iterations, "events": [],
    }
    write_status(manifest, payload)
    event(payload, "runner_started")
    write_status(manifest, payload)
    try:
        event(payload, "connect_started")
        write_status(manifest, payload)
        solver = connect(server_id=args.server_id, start_transcript=False)
        event(payload, "connected", fluent_version=str(solver.get_fluent_version()))
        payload["ownership_preflight"] = prove_quiescent(solver)
        if not all(remote_file_exists(solver, path) for path in (PARENT_CASE, PARENT_DATA)):
            raise RuntimeError("canonical F11 pair missing")
        ensure_remote_directory(solver, args.run_root)
        solver.scheme.eval(f'(chdir "{quote_scheme_string(args.run_root)}")')
        event(payload, "loading_parent")
        write_status(manifest, payload)
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        payload["before"] = parent_audit(solver)
        payload["outlet"] = set_outlet(solver, args.lane, args.loss)
        payload["monitor_files"] = redirect_report_files(solver, str(PureWindowsPath(args.run_root) / "monitors"))
        missing_pool_files = [name for name in POOL_MASS_REPORT_FILES if name not in payload["monitor_files"]]
        if missing_pool_files:
            raise RuntimeError(f"Inherited lower-region liquid-mass report files are unavailable: {missing_pool_files}")
        prepared_case = str(PureWindowsPath(args.run_root) / "prepared.cas.h5")
        prepared_data = prepared_case[:-7] + ".dat.h5"
        final_case = str(PureWindowsPath(args.run_root) / "final.cas.h5")
        final_data = final_case[:-7] + ".dat.h5"
        if any(remote_file_exists(solver, path) for path in (prepared_case, prepared_data, final_case, final_data)):
            raise FileExistsError("refusing existing Phase-06 output paths")
        event(payload, "writing_prepared_pair", case=prepared_case, data=prepared_data)
        write_status(manifest, payload)
        solver.settings.file.write_case(file_name=prepared_case)
        solver.settings.file.write_data(file_name=prepared_data)
        if not all(remote_file_exists(solver, path) for path in (prepared_case, prepared_data)):
            raise RuntimeError("prepared paired save failed")
        event(payload, "reloading_prepared_pair")
        write_status(manifest, payload)
        solver.settings.file.read_case(file_name=prepared_case)
        solver.settings.file.read_data(file_name=prepared_data)
        payload["reopened_outlet"] = set_outlet(solver, "reference", args.loss) if args.lane == "reference" else safe_get_state(solver.settings.setup.boundary_conditions.outlet_vent["brineoutlet"], "reopened vent")
        start = clock(solver)
        payload["start_iteration"] = start
        event(payload, "smoke_started", start_iteration=start, incremental_iterations=50)
        write_status(manifest, payload)
        solver.settings.solution.run_calculation.iterate(iter_count=50)
        smoke = clock(solver)
        payload["smoke_iteration"] = smoke
        pool_paths = [payload["monitor_files"][name] for name in POOL_MASS_REPORT_FILES]
        missing_smoke_histories = [path for path in pool_paths if not remote_file_exists(solver, path)]
        if missing_smoke_histories:
            raise RuntimeError(f"smoke run did not write required pool histories: {missing_smoke_histories}")
        event(payload, "discovery_started", start_iteration=smoke, incremental_iterations=args.iterations)
        write_status(manifest, payload)
        solver.settings.solution.run_calculation.iterate(iter_count=args.iterations)
        final_iteration = clock(solver)
        payload["final_iteration"] = final_iteration
        missing_final_histories = [path for path in pool_paths if not remote_file_exists(solver, path)]
        if missing_final_histories:
            raise RuntimeError(f"discovery run did not retain required pool histories: {missing_final_histories}")
        event(payload, "writing_final_pair", case=final_case, data=final_data)
        write_status(manifest, payload)
        solver.settings.file.write_case(file_name=final_case)
        solver.settings.file.write_data(file_name=final_data)
        if not all(remote_file_exists(solver, path) for path in (final_case, final_data)):
            raise RuntimeError("final paired save failed")
        payload.update({"prepared_case": prepared_case, "prepared_data": prepared_data, "final_case": final_case, "final_data": final_data, "status": "COMPLETE"})
        event(payload, "runner_complete")
        write_status(manifest, payload)
        print(json.dumps(payload, indent=2, default=str))
        return 0
    except Exception as exc:
        payload.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
        event(payload, "runner_blocked", error=payload["error"])
        write_status(manifest, payload)
        print(json.dumps(payload, indent=2, default=str), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

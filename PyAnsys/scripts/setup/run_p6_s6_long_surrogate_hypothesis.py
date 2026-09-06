#!/usr/bin/env python3
"""Run the approved long-horizon Phase-06 numerical-surrogate hypothesis test.

The solver path is Python/PyFluent only: this runner does not invoke a Fluent
TUI, journal, or GUI execution fallback.  The outer handoff job verifies the
remote final pair and wakes the originating Codex thread on either terminal
state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import sys
import traceback
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.postprocess_live import capture_residual_history
from pyansys_fluent.stage4_native import (
    configure_autosave,
    configure_residual_history,
    ensure_remote_directory,
    redirect_report_files,
)
from extract_report_plot_histories import parse_report_forms, read_remote_forms
from run_p6_s1_discovery import (
    PARENT_CASE,
    PARENT_DATA,
    POOL_MASS_REPORT_FILES,
    clock,
    event,
    parent_audit,
    prove_quiescent,
    write_status,
)

TARGET_KG = 200.0
P_MIN = 1_115_000.0
P_MAX = 1_137_500.0
START_PRESSURE_PA = 1_120_000.0
PROXY_REPORT_FILE = "03a_stage3_inventory_y010_liquid_mass-rfile"


def data_path(case_path: str) -> str:
    if not case_path.endswith(".cas.h5"):
        raise ValueError(f"Expected .cas.h5 path, got {case_path!r}")
    return case_path[:-7] + ".dat.h5"


def write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite evidence: {path}")
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def set_pressure(solver: Any, value_pa: float) -> float:
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"]
    state = safe_get_state(outlet, "P6-S6 brine pressure before update")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {
        "option": "value",
        "value": value_pa,
    }
    outlet.set_state(state)
    after = safe_get_state(
        solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"],
        "P6-S6 brine pressure readback",
    )
    return float(after["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])


def latest_proxy(solver: Any, report_path: str) -> tuple[int, float]:
    history = parse_report_forms(read_remote_forms(solver, report_path))
    return int(history["iterations"][-1]), float(history["values"][-1])


def set_working_directory(solver: Any, path: str) -> None:
    """Make Fluent's relative report-file destination explicit and auditable."""
    solver.scheme.eval(f'(chdir "{quote_scheme_string(path)}")')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--residual-history", type=Path, required=True)
    parser.add_argument("--chunks", type=int, default=100)
    parser.add_argument("--chunk-iterations", type=int, default=100)
    parser.add_argument(
        "--solver-call-iterations",
        type=int,
        default=50,
        help="Iterations per individual PyFluent RPC; feedback remains at chunk-iterations.",
    )
    parser.add_argument("--gain-pa-per-kg", type=float, default=2000.0)
    parser.add_argument("--max-step-pa", type=float, default=5000.0)
    parser.add_argument("--checkpoint-every-chunks", type=int, default=50)
    args = parser.parse_args()
    if min(
        args.chunks,
        args.chunk_iterations,
        args.solver_call_iterations,
        args.checkpoint_every_chunks,
    ) <= 0:
        raise ValueError("chunk, solver-call, and checkpoint counts must be positive")
    if args.chunk_iterations % args.solver_call_iterations:
        raise ValueError(
            "chunk-iterations must be an exact multiple of solver-call-iterations"
        )

    manifest = args.manifest.expanduser().resolve()
    residual_history = args.residual_history.expanduser().resolve()
    if manifest.exists() or residual_history.exists():
        raise FileExistsError("Refusing to overwrite an existing P6-S6 evidence artifact")

    total_iterations = args.chunks * args.chunk_iterations
    prepared_case = str(PureWindowsPath(args.run_root) / "prepared.cas.h5")
    final_case = str(PureWindowsPath(args.run_root) / "final.cas.h5")
    checkpoint_root = str(PureWindowsPath(args.run_root) / "checkpoints")
    monitor_root = str(PureWindowsPath(args.run_root) / "monitors")
    payload: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": "P6-S6-H",
        "mode": "hypothesis-test",
        "server_id": str(args.server_id),
        "run_root": args.run_root,
        "parent_case": PARENT_CASE,
        "parent_data": PARENT_DATA,
        "target_proxy_kg": TARGET_KG,
        "pressure_bounds_pa": [P_MIN, P_MAX],
        "starting_pressure_pa": START_PRESSURE_PA,
        "chunks_requested": args.chunks,
        "chunk_iterations": args.chunk_iterations,
        "solver_call_iterations": args.solver_call_iterations,
        "total_incremental_iterations": total_iterations,
        "gain_pa_per_kg": args.gain_pa_per_kg,
        "max_step_pa": args.max_step_pa,
        "chunks": [],
        "events": [],
    }
    write_status(manifest, payload)
    event(payload, "runner_started")
    write_status(manifest, payload)
    try:
        solver = connect(server_id=args.server_id, start_transcript=False)
        payload["ownership_preflight"] = prove_quiescent(solver)
        if not all(remote_file_exists(solver, path) for path in (PARENT_CASE, PARENT_DATA)):
            raise RuntimeError("The canonical F11 parent pair is absent")
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, checkpoint_root)
        protected = (prepared_case, data_path(prepared_case), final_case, data_path(final_case))
        if any(remote_file_exists(solver, path) for path in protected):
            raise FileExistsError("Refusing to reuse P6-S6 remote prepared/final paths")

        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        payload["parent_readback"] = parent_audit(solver)
        payload["initial_pressure_readback_pa"] = set_pressure(solver, START_PRESSURE_PA)
        set_working_directory(solver, monitor_root)
        payload["fluent_working_dir"] = monitor_root
        payload["monitor_files"] = redirect_report_files(solver, monitor_root)
        missing_reports = [name for name in POOL_MASS_REPORT_FILES if name not in payload["monitor_files"]]
        if missing_reports:
            raise RuntimeError(f"Required lower-region report files are absent: {missing_reports}")
        payload["residual_monitor_readback"] = configure_residual_history(
            solver, total_iterations + 1000
        )
        payload["autosave_readback"] = configure_autosave(
            solver,
            checkpoint_root,
            data_frequency=args.chunk_iterations * args.checkpoint_every_chunks,
        )
        solver.settings.file.write_case(file_name=prepared_case)
        solver.settings.file.write_data(file_name=data_path(prepared_case))
        if not all(remote_file_exists(solver, path) for path in (prepared_case, data_path(prepared_case))):
            raise RuntimeError("Prepared paired save failed")
        solver.settings.file.read_case(file_name=prepared_case)
        solver.settings.file.read_data(file_name=data_path(prepared_case))
        set_working_directory(solver, monitor_root)
        payload["prepared_reload_readback"] = parent_audit(solver)
        payload["prepared_pressure_readback_pa"] = set_pressure(solver, START_PRESSURE_PA)
        reopened_files: dict[str, Any] = {}
        reopened_reports = solver.settings.solution.monitor.report_files
        for name, expected_path in payload["monitor_files"].items():
            state = safe_get_state(reopened_reports[name], f"P6-S6 reloaded report {name}")
            actual_path = state.get("file_name") if isinstance(state, Mapping) else None
            expected_name = PureWindowsPath(expected_path).name
            actual_windows = PureWindowsPath(actual_path) if isinstance(actual_path, str) else None
            relative_to_working_dir = bool(
                actual_windows is not None
                and not actual_windows.is_absolute()
                and str(actual_windows.parent) in (".", "")
                and actual_windows.name == expected_name
            )
            if actual_path != expected_path and not relative_to_working_dir:
                raise RuntimeError(
                    f"Report path did not survive save/reopen for {name}: "
                    f"{actual_path!r} != {expected_path!r}"
                )
            reopened_files[name] = {
                "configured": actual_path,
                "resolved": str(PureWindowsPath(monitor_root) / expected_name),
            }
        payload["reopened_monitor_files"] = reopened_files

        inherited_rp_iteration = clock(solver)
        event(
            payload,
            "smoke_started",
            inherited_rp_iteration=inherited_rp_iteration,
            incremental_iterations=50,
        )
        write_status(manifest, payload)
        solver.settings.solution.run_calculation.iterate(iter_count=50)
        missing_smoke = [
            path for path in payload["monitor_files"].values() if not remote_file_exists(solver, path)
        ]
        if missing_smoke:
            raise RuntimeError(f"Smoke run did not write redirected histories: {missing_smoke}")
        smoke_report_iteration, _ = latest_proxy(
            solver, payload["monitor_files"][PROXY_REPORT_FILE]
        )
        payload["inherited_rp_iteration"] = inherited_rp_iteration
        payload["smoke_report_iteration"] = smoke_report_iteration
        pressure = START_PRESSURE_PA
        previous_report_iteration = smoke_report_iteration

        for chunk in range(1, args.chunks + 1):
            event(
                payload,
                "chunk_started",
                chunk=chunk,
                report_iteration_before=previous_report_iteration,
                pressure_before_pa=pressure,
            )
            write_status(manifest, payload)
            call_iteration = previous_report_iteration
            for solver_call in range(
                1, args.chunk_iterations // args.solver_call_iterations + 1
            ):
                event(
                    payload,
                    "chunk_solver_call_started",
                    chunk=chunk,
                    solver_call=solver_call,
                    report_iteration_before=call_iteration,
                    incremental_iterations=args.solver_call_iterations,
                )
                write_status(manifest, payload)
                solver.settings.solution.run_calculation.iterate(
                    iter_count=args.solver_call_iterations
                )
                call_iteration_after, _ = latest_proxy(
                    solver, payload["monitor_files"][PROXY_REPORT_FILE]
                )
                if call_iteration_after != call_iteration + args.solver_call_iterations:
                    raise RuntimeError(
                        f"Chunk {chunk} solver call {solver_call} report coordinate mismatch: "
                        f"{call_iteration} -> {call_iteration_after}, expected "
                        f"+{args.solver_call_iterations}"
                    )
                event(
                    payload,
                    "chunk_solver_call_complete",
                    chunk=chunk,
                    solver_call=solver_call,
                    report_iteration_after=call_iteration_after,
                )
                call_iteration = call_iteration_after
            report_iteration, proxy_mass = latest_proxy(
                solver, payload["monitor_files"][PROXY_REPORT_FILE]
            )
            if report_iteration != previous_report_iteration + args.chunk_iterations:
                raise RuntimeError(
                    f"Chunk {chunk} report coordinate mismatch: {previous_report_iteration} -> "
                    f"{report_iteration}, expected +{args.chunk_iterations}"
                )
            error_kg = proxy_mass - TARGET_KG
            step_pa = max(
                -args.max_step_pa,
                min(args.max_step_pa, -args.gain_pa_per_kg * error_kg),
            )
            requested_pressure = max(P_MIN, min(P_MAX, pressure + step_pa))
            readback_pressure = set_pressure(solver, requested_pressure)
            payload["chunks"].append(
                {
                    "chunk": chunk,
                    "report_iteration_before": previous_report_iteration,
                    "report_iteration_after": report_iteration,
                    "report_iteration": report_iteration,
                    "proxy_mass_kg": proxy_mass,
                    "error_kg": error_kg,
                    "pressure_before_pa": pressure,
                    "requested_pressure_after_pa": requested_pressure,
                    "pressure_after_pa": readback_pressure,
                }
            )
            pressure = readback_pressure
            previous_report_iteration = report_iteration
            if chunk % args.checkpoint_every_chunks == 0:
                checkpoint_case = str(
                    PureWindowsPath(checkpoint_root) / f"checkpoint-chunk-{chunk:03d}.cas.h5"
                )
                solver.settings.file.write_case(file_name=checkpoint_case)
                solver.settings.file.write_data(file_name=data_path(checkpoint_case))
                if not all(
                    remote_file_exists(solver, path)
                    for path in (checkpoint_case, data_path(checkpoint_case))
                ):
                    raise RuntimeError(f"Checkpoint pair missing after chunk {chunk}")
                payload.setdefault("checkpoints", []).append(
                    {"chunk": chunk, "case": checkpoint_case, "data": data_path(checkpoint_case)}
                )
            write_status(manifest, payload)

        expected_final_report = smoke_report_iteration + total_iterations
        if previous_report_iteration != expected_final_report:
            raise RuntimeError(
                f"Final report coordinate {previous_report_iteration} does not equal expected "
                f"{expected_final_report}"
            )
        residuals = capture_residual_history(solver, timeout=20.0, settle_seconds=1.0)
        if int(residuals.get("point_count", 0)) < total_iterations:
            raise RuntimeError(
                "Residual capture is shorter than the planned long horizon: "
                f"{residuals.get('point_count')} < {total_iterations}"
            )
        write_new_json(residual_history, residuals)
        solver.settings.file.write_case(file_name=final_case)
        solver.settings.file.write_data(file_name=data_path(final_case))
        if not all(remote_file_exists(solver, path) for path in (final_case, data_path(final_case))):
            raise RuntimeError("Final paired save failed")
        payload.update(
            {
                "status": "COMPLETE",
                "final_report_iteration": previous_report_iteration,
                "final_case": final_case,
                "final_data": data_path(final_case),
                "residual_history": str(residual_history),
            }
        )
        event(payload, "runner_complete")
        write_status(manifest, payload)
        return 0
    except Exception as exc:
        payload.update(
            {
                "status": "BLOCKED",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }
        )
        event(payload, "runner_blocked", error=payload["error"])
        write_status(manifest, payload)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the user-authorized fixed-3000 Stage-3 override queue.

This is intentionally separate from the authoritative adaptive Stage-3
runner.  The user explicitly requested a fixed 3000-iteration block per
stage, with no gate pauses, while retaining independent local lineage,
prescribed branch transitions, and the existing physical setup.

The script writes only branch artifacts under the Fluent-machine Documents
tree and an execution journal/evidence stream under the local repository
output directory.  It never writes to the immutable OneDrive P0 directory.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
import time
import traceback
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402


P0_REMOTE = (
    r"C:\Users\syok443\OneDrive - The University of Auckland"
    r"\2026 Sem 2\700\Full geom\03A-stage3"
    r"\03A-stage3-P0-monitor-ready-preinit.cas.h5"
)
F11_RESUME_CASE = (
    r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11"
    r"\run-20260818T053845Z"
    r"\03A-stage3-F11-stage-10pct-end-iter00750.cas.h5"
)
F11_RESUME_DATA = (
    r"C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11"
    r"\run-20260818T053845Z"
    r"\03A-stage3-F11-stage-10pct-end-iter00750.dat.h5"
)

INLET_ZONES = ("liquidinlet", "steaminlet")
INLET_PHASES = ("phase-1", "phase-2")
P0_SHA256 = "8b9489d745a9539bfa36ffdca0fe224331fce749c331f08f6b0fc1ad6f386301"


def windows_path(root: str, name: str) -> str:
    return str(PureWindowsPath(root) / name)


class RunJournal:
    def __init__(self, output_dir: Path, stamp: str) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = output_dir / "fixed-3000-events.jsonl"
        self.plan_path = output_dir / "fixed-3000-execution-plan.jou"
        self.stamp = stamp
        self._write_plan()

    def _write_plan(self) -> None:
        plan = """; USER-AUTHORIZED 03A STAGE-3 FIXED-3000 OVERRIDE
; This journal records the requested fixed-block schedule.
; Gate pauses are intentionally disabled by explicit user override.
; P0 lineage remains independent for every branch.
;
; F02: B/U0.7 carrier 3000 -> full Mixture 3000
; F04: B/U0.5 carrier 3000 -> full Mixture 3000
; F11: resume 10% at iter750 -> +2250 to iter3000
;      20% 3000 -> 40% 3000 -> 80% 3000 -> 100% 3000
; F06: B/U0.3 carrier 3000 -> full Mixture 3000
; F05: A/U0.3 full Mixture 3000
;
; The 10% F11 increment is 2250 because the verified current iteration is
; 750 and the requested fixed stage total is 3000.
"""
        self.plan_path.write_text(plan, encoding="utf-8")

    def event(self, kind: str, **fields: Any) -> None:
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind,
            **fields,
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")
            handle.flush()
        print(json.dumps(payload, default=str), flush=True)


def state_readback(solver: Any) -> dict[str, Any]:
    equations = safe_get_state(
        solver.settings.solution.controls.equations,
        "fixed-3000 equations",
    )
    urf = safe_get_state(
        solver.settings.solution.controls.under_relaxation,
        "fixed-3000 under-relaxation",
    )
    velocities: dict[str, dict[str, Any]] = {}
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        velocities[zone] = {}
        for phase in INLET_PHASES:
            try:
                velocities[zone][phase] = (
                    bc[zone]
                    .phase[phase]
                    .momentum.velocity_magnitude.get_state()
                )
            except Exception as exc:
                velocities[zone][phase] = {"error": repr(exc)}
    return {
        "equations": equations,
        "under_relaxation": urf,
        "inlet_velocity_states": velocities,
    }


def configure_autosave(solver: Any, root: str) -> dict[str, Any]:
    state = {
        "case_frequency": "each-time",
        "data_frequency": 250,
        "root_name": windows_path(root, "03A-stage3-autosave-%i"),
        "retain_most_recent_files": True,
        "max_files": 2,
        "append_file_name_with": {
            "file_suffix_type": "time-step",
            "file_decimal_digit": 6,
        },
    }
    solver.settings.file.auto_save.set_state(state)
    return solver.settings.file.auto_save.get_state()


def set_all_inlet_velocities(solver: Any, velocity: float) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            bc[zone].phase[phase].momentum.velocity_magnitude.set_state(
                {"option": "value", "value": velocity}
            )
            bc = solver.settings.setup.boundary_conditions.velocity_inlet
    return state_readback(solver)["inlet_velocity_states"]


def set_equation_mode(solver: Any, *, full_mixture: bool) -> dict[str, Any]:
    solver.settings.solution.controls.equations.set_state(
        {"mp": full_mixture, "drift": full_mixture}
    )
    return safe_get_state(
        solver.settings.solution.controls.equations,
        "equation-mode readback",
    )


def set_branch_settings(
    solver: Any,
    *,
    momentum_urf: float,
    velocity: float,
    full_mixture: bool,
) -> dict[str, Any]:
    solver.settings.solution.controls.under_relaxation.set_state(
        {"mom": momentum_urf}
    )
    set_equation_mode(solver, full_mixture=full_mixture)
    set_all_inlet_velocities(solver, velocity)
    return state_readback(solver)


def write_case(solver: Any, path: str) -> None:
    solver.settings.file.write_case(file_name=path)
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent did not expose written case: {path}")


def write_pair(solver: Any, case_path: str, data_path: str) -> None:
    write_case(solver, case_path)
    solver.settings.file.write_data(file_name=data_path)
    if not remote_file_exists(solver, data_path):
        raise RuntimeError(f"Fluent did not expose written data: {data_path}")


def read_case_data(solver: Any, case_path: str, data_path: str | None = None) -> None:
    solver.settings.file.read_case(file_name=case_path)
    if data_path is not None:
        solver.settings.file.read_data(file_name=data_path)


def prepare_from_p0(
    solver: Any,
    journal: RunJournal,
    *,
    branch: str,
    root: str,
    momentum_urf: float,
    velocity: float,
    full_mixture: bool,
) -> tuple[Any, dict[str, Any]]:
    local_p0 = windows_path(root, f"03A-stage3-{branch}-P0-local.cas.h5")
    preinit = windows_path(
        root,
        f"03A-stage3-{branch}-preinit-override.cas.h5",
    )
    journal.event("load_p0", branch=branch, p0=P0_REMOTE)
    read_case_data(solver, P0_REMOTE)
    write_case(solver, local_p0)
    read_case_data(solver, local_p0)
    autosave = configure_autosave(solver, root)
    settings = set_branch_settings(
        solver,
        momentum_urf=momentum_urf,
        velocity=velocity,
        full_mixture=full_mixture,
    )
    write_case(solver, preinit)
    read_case_data(solver, preinit)
    autosave = configure_autosave(solver, root)
    settings = set_branch_settings(
        solver,
        momentum_urf=momentum_urf,
        velocity=velocity,
        full_mixture=full_mixture,
    )
    journal.event(
        "preinit_verified",
        branch=branch,
        local_p0=local_p0,
        preinit=preinit,
        p0_sha256=P0_SHA256,
        autosave=autosave,
        settings=settings,
    )
    solver.settings.solution.initialization.hybrid_initialize()
    start_case = windows_path(root, f"03A-stage3-{branch}-start-iter000.cas.h5")
    start_data = windows_path(root, f"03A-stage3-{branch}-start-iter000.dat.h5")
    write_pair(solver, start_case, start_data)
    journal.event(
        "hybrid_initialized_once",
        branch=branch,
        start_case=start_case,
        start_data=start_data,
    )
    return solver, settings


def latest_iteration(solver: Any) -> tuple[int | None, dict[str, Any]]:
    snapshot = collect_snapshot(solver, monitor_sets=("residual",))
    value = snapshot.get("progress", {}).get("iteration")
    try:
        iteration = int(float(value)) if value is not None else None
    except (TypeError, ValueError):
        iteration = None
    return iteration, snapshot


def wait_for_target(
    solver: Any,
    journal: RunJournal,
    *,
    branch: str,
    stage: str,
    target_iteration: int,
    timeout_seconds: float = 900.0,
) -> tuple[Any, int]:
    deadline = time.monotonic() + timeout_seconds
    best = -1
    last_progress = time.monotonic()
    probe = solver
    last_snapshot: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            current, snapshot = latest_iteration(probe)
            last_snapshot = snapshot
            if current is not None:
                if current > best:
                    best = current
                    last_progress = time.monotonic()
                    journal.event(
                        "progress",
                        branch=branch,
                        stage=stage,
                        observed_iteration=current,
                        target_iteration=target_iteration,
                    )
                if current >= target_iteration:
                    return probe, current
            if time.monotonic() - last_progress > 180.0:
                raise RuntimeError(
                    f"NO_PROGRESS before target {target_iteration}; "
                    f"best observed iteration {best}; last snapshot={last_snapshot}"
                )
        except RuntimeError:
            raise
        except Exception as exc:
            journal.event(
                "reconnect",
                branch=branch,
                stage=stage,
                reason=repr(exc),
            )
            try:
                probe = connect(server_id="2")
            except Exception as reconnect_exc:
                journal.event(
                    "reconnect_failed",
                    branch=branch,
                    stage=stage,
                    error=repr(reconnect_exc),
                )
        time.sleep(2.0)
    raise RuntimeError(
        f"TIMEOUT before target {target_iteration}; "
        f"best observed iteration {best}; last snapshot={last_snapshot}"
    )


def run_fixed_block(
    solver: Any,
    journal: RunJournal,
    *,
    branch: str,
    stage: str,
    additional_iterations: int,
    target_iteration: int,
) -> Any:
    journal.event(
        "fixed_block_start",
        branch=branch,
        stage=stage,
        additional_iterations=additional_iterations,
        target_iteration=target_iteration,
    )
    command_error: str | None = None
    try:
        solver.settings.solution.run_calculation.iterate(
            iter_count=additional_iterations
        )
    except Exception as exc:
        command_error = repr(exc)
        journal.event(
            "solve_client_error",
            branch=branch,
            stage=stage,
            additional_iterations=additional_iterations,
            error=command_error,
        )
    solver, observed = wait_for_target(
        solver,
        journal,
        branch=branch,
        stage=stage,
        target_iteration=target_iteration,
    )
    journal.event(
        "fixed_block_complete",
        branch=branch,
        stage=stage,
        target_iteration=target_iteration,
        observed_iteration=observed,
        client_error=command_error,
    )
    return solver


def transition(
    solver: Any,
    journal: RunJournal,
    *,
    branch: str,
    from_stage: str,
    to_stage: str,
    velocity: float,
    momentum_urf: float,
    checkpoint_case: str,
    checkpoint_data: str,
) -> Any:
    before = state_readback(solver)
    write_pair(solver, checkpoint_case, checkpoint_data)
    after_settings = set_branch_settings(
        solver,
        momentum_urf=momentum_urf,
        velocity=velocity,
        full_mixture=True,
    )
    transition_case = checkpoint_case.replace(
        ".cas.h5", f"-after-{to_stage}.cas.h5"
    )
    transition_data = checkpoint_data.replace(
        ".dat.h5", f"-after-{to_stage}.dat.h5"
    )
    write_pair(solver, transition_case, transition_data)
    journal.event(
        "transition",
        branch=branch,
        from_stage=from_stage,
        to_stage=to_stage,
        settings_before=before,
        settings_after=after_settings,
        checkpoint_before_transition={
            "case": checkpoint_case,
            "data": checkpoint_data,
        },
        transition_checkpoint={
            "case": transition_case,
            "data": transition_data,
        },
        no_reinitialization=True,
    )
    return solver


def run_schedule_b(
    journal: RunJournal,
    *,
    branch: str,
    momentum_urf: float,
    stamp: str,
) -> None:
    root = rf"C:\Users\syok443\Documents\FluentRuns\03A-stage3\{branch}\run-{stamp}"
    solver = connect(server_id="2")
    solver, _ = prepare_from_p0(
        solver,
        journal,
        branch=branch,
        root=root,
        momentum_urf=momentum_urf,
        velocity=27.118,
        full_mixture=False,
    )
    solver = run_fixed_block(
        solver,
        journal,
        branch=branch,
        stage="carrier-100pct",
        additional_iterations=3000,
        target_iteration=3000,
    )
    carrier_case = windows_path(root, f"03A-stage3-{branch}-carrier-end-iter003000.cas.h5")
    carrier_data = windows_path(root, f"03A-stage3-{branch}-carrier-end-iter003000.dat.h5")
    write_pair(solver, carrier_case, carrier_data)
    solver = transition(
        solver,
        journal,
        branch=branch,
        from_stage="carrier-100pct",
        to_stage="full-mixture-100pct",
        velocity=27.118,
        momentum_urf=momentum_urf,
        checkpoint_case=carrier_case,
        checkpoint_data=carrier_data,
    )
    solver = run_fixed_block(
        solver,
        journal,
        branch=branch,
        stage="full-mixture-100pct",
        additional_iterations=3000,
        target_iteration=6000,
    )
    final_case = windows_path(root, f"03A-stage3-{branch}-final-iter006000.cas.h5")
    final_data = windows_path(root, f"03A-stage3-{branch}-final-iter006000.dat.h5")
    write_pair(solver, final_case, final_data)
    journal.event("branch_complete", branch=branch, final_case=final_case, final_data=final_data)


def run_f11(journal: RunJournal, *, stamp: str) -> None:
    branch = "F11"
    root = rf"C:\Users\syok443\Documents\FluentRuns\03A-stage3\{branch}\run-{stamp}"
    solver = connect(server_id="2")
    if not remote_file_exists(solver, F11_RESUME_CASE) or not remote_file_exists(
        solver, F11_RESUME_DATA
    ):
        raise FileNotFoundError("F11 verified iteration-750 resume pair is unavailable")
    read_case_data(solver, F11_RESUME_CASE, F11_RESUME_DATA)
    configure_autosave(solver, root)
    settings = state_readback(solver)
    journal.event(
        "resume_f11",
        branch=branch,
        resume_case=F11_RESUME_CASE,
        resume_data=F11_RESUME_DATA,
        settings=settings,
        current_verified_iteration=750,
        no_reinitialization=True,
    )
    stages = (
        ("10pct", 27.118, 2250, 3000),
        ("20pct", 5.4236, 3000, 6000),
        ("40pct", 10.8472, 3000, 9000),
        ("80pct", 21.6944, 3000, 12000),
        ("100pct", 27.118, 3000, 15000),
    )
    previous_stage = "resume-10pct-iter000750"
    for stage, velocity, additional, target in stages:
        solver = run_fixed_block(
            solver,
            journal,
            branch=branch,
            stage=stage,
            additional_iterations=additional,
            target_iteration=target,
        )
        end_case = windows_path(root, f"03A-stage3-F11-{stage}-end-iter{target:06d}.cas.h5")
        end_data = windows_path(root, f"03A-stage3-F11-{stage}-end-iter{target:06d}.dat.h5")
        write_pair(solver, end_case, end_data)
        journal.event(
            "stage_checkpoint",
            branch=branch,
            stage=stage,
            iteration=target,
            case=end_case,
            data=end_data,
        )
        if stage != "100pct":
            next_stage = stages[stages.index((stage, velocity, additional, target)) + 1][0]
            next_velocity = stages[stages.index((stage, velocity, additional, target)) + 1][1]
            solver = transition(
                solver,
                journal,
                branch=branch,
                from_stage=stage,
                to_stage=next_stage,
                velocity=next_velocity,
                momentum_urf=0.3,
                checkpoint_case=end_case,
                checkpoint_data=end_data,
            )
        previous_stage = stage
    journal.event("branch_complete", branch=branch, final_stage=previous_stage)


def run_f05(journal: RunJournal, *, stamp: str) -> None:
    branch = "F05"
    root = rf"C:\Users\syok443\Documents\FluentRuns\03A-stage3\{branch}\run-{stamp}"
    solver = connect(server_id="2")
    solver, _ = prepare_from_p0(
        solver,
        journal,
        branch=branch,
        root=root,
        momentum_urf=0.3,
        velocity=27.118,
        full_mixture=True,
    )
    solver = run_fixed_block(
        solver,
        journal,
        branch=branch,
        stage="full-mixture-100pct",
        additional_iterations=3000,
        target_iteration=3000,
    )
    final_case = windows_path(root, "03A-stage3-F05-final-iter003000.cas.h5")
    final_data = windows_path(root, "03A-stage3-F05-final-iter003000.dat.h5")
    write_pair(solver, final_case, final_data)
    journal.event("branch_complete", branch=branch, final_case=final_case, final_data=final_data)


def run_branch_guarded(journal: RunJournal, branch_id: str, function: Any, **kwargs: Any) -> None:
    journal.event("branch_start", branch=branch_id)
    try:
        function(journal, **kwargs)
    except Exception as exc:
        journal.event(
            "branch_failure",
            branch=branch_id,
            classification="NUMERICAL_OR_EXECUTION_FAILURE",
            error=repr(exc),
            traceback=traceback.format_exc(),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="2")
    parser.add_argument(
        "--stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    parser.add_argument(
        "--output-dir",
        default="PyAnsys/output/03A-stage3/override-fixed3000",
    )
    args = parser.parse_args()
    journal = RunJournal(Path(args.output_dir), args.stamp)
    journal.event(
        "queue_start",
        server_id=args.server_id,
        queue=("F02", "F04", "F11", "F06", "F05"),
        policy="user-authorized-fixed-3000-per-stage",
        p0_sha256=P0_SHA256,
    )
    run_branch_guarded(
        journal,
        "F02",
        run_schedule_b,
        branch="F02",
        momentum_urf=0.7,
        stamp=args.stamp,
    )
    run_branch_guarded(
        journal,
        "F04",
        run_schedule_b,
        branch="F04",
        momentum_urf=0.5,
        stamp=args.stamp,
    )
    run_branch_guarded(journal, "F11", run_f11, stamp=args.stamp)
    run_branch_guarded(
        journal,
        "F06",
        run_schedule_b,
        branch="F06",
        momentum_urf=0.3,
        stamp=args.stamp,
    )
    run_branch_guarded(journal, "F05", run_f05, stamp=args.stamp)
    journal.event("queue_complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

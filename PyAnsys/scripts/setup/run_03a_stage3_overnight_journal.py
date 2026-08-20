#!/usr/bin/env python3
"""Run the user-authorized unattended Stage-3 fixed-block sequence on Fluent 1.

Every branch starts independently from the released immutable P0. The solve
work is issued as native Fluent journals, one blocking 3000-iteration block per
scientific stage. This Python process only hands journals to Fluent, applies
the prescribed loading transitions, verifies the resulting state, and skips a
branch after an execution or numerical error. It never calls Fluent
exit/shutdown and never uses one branch's developed field as another branch's
starting field.
"""

from __future__ import annotations

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


SERVER_ID = "1"
P0_REMOTE = (
    r"C:\Users\syok443\OneDrive - The University of Auckland"
    r"\2026 Sem 2\700\Full geom\03A-stage3"
    r"\03A-stage3-P0-monitor-ready-preinit.cas.h5"
)
P0_SHA256 = "8b9489d745a9539bfa36ffdca0fe224331fce749c331f08f6b0fc1ad6f386301"
REMOTE_QUEUE_ROOT = r"C:\Users\syok443\Documents\FluentRuns\03A-stage3"
INLET_ZONES = ("liquidinlet", "steaminlet")
INLET_PHASES = ("phase-1", "phase-2")
VELOCITY_10 = 2.7118
VELOCITY_20 = 5.4236
VELOCITY_40 = 10.8472
VELOCITY_80 = 21.6944
VELOCITY_100 = 27.118


def win(root: str, name: str) -> str:
    return str(PureWindowsPath(root) / name)


def data_path(case_path: str) -> str:
    return case_path.replace(".cas.h5", ".dat.h5")


def scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


class EventLog:
    def __init__(self, path: Path, stamp: str) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.stamp = stamp

    def emit(self, kind: str, **fields: Any) -> None:
        payload = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "kind": kind,
            "stamp": self.stamp,
            **fields,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")
            handle.flush()
        print(json.dumps(payload, default=str), flush=True)


def write_remote_journal(solver: Any, remote_path: str, journal: str) -> None:
    body = " ".join(
        f'(display "{scheme_string(line)}") (newline)'
        for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{scheme_string(remote_path)}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_path):
        raise RuntimeError(f"Fluent did not expose native journal: {remote_path}")


def ensure_remote_directory(solver: Any, path: str) -> None:
    command = f'cmd /c if not exist "{path}" md "{path}"'
    result = solver.scheme.eval(f'(system "{scheme_string(command)}")')
    if result not in (0, None):
        raise RuntimeError(f"Could not create/verify Fluent-machine directory: {path}; result={result!r}")
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent-machine directory is unavailable: {path}")


def state_readback(solver: Any) -> dict[str, Any]:
    equations = safe_get_state(
        solver.settings.solution.controls.equations,
        "equations",
    )
    urf = safe_get_state(
        solver.settings.solution.controls.under_relaxation,
        "under-relaxation",
    )
    inlet_states: dict[str, Any] = {}
    invariant_states: dict[str, Any] = {}
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        inlet_states[zone] = safe_get_state(bc[zone], f"{zone} state")
        state = inlet_states[zone]
        phase_state = state.get("phase", {}) if isinstance(state, dict) else {}
        mixture = phase_state.get("mixture", {}) if isinstance(phase_state, dict) else {}
        turbulence = mixture.get("turbulence", {}) if isinstance(mixture, dict) else {}
        invariant_states[zone] = {
            "turbulent_intensity": turbulence.get("turbulent_intensity"),
            "hydraulic_diameter": turbulence.get("hydraulic_diameter"),
        }
    return {
        "equations": equations,
        "under_relaxation": urf,
        "inlet_states": inlet_states,
        "inlet_invariants": invariant_states,
    }


def equation_value(equations: Any, key: str) -> bool | None:
    if isinstance(equations, dict):
        value = equations.get(key)
        if isinstance(value, bool):
            return value
        for child in equations.values():
            result = equation_value(child, key)
            if result is not None:
                return result
    return None


def urf_value(urf: Any) -> float | None:
    if isinstance(urf, dict):
        value = urf.get("mom")
        if isinstance(value, (int, float)):
            return float(value)
        for child in urf.values():
            result = urf_value(child)
            if result is not None:
                return result
    return None


def velocity_values(readback: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for zone, state in readback["inlet_states"].items():
        result[zone] = {}
        phase_state = state.get("phase", {}) if isinstance(state, dict) else {}
        for phase in INLET_PHASES:
            phase_item = phase_state.get(phase, {}) if isinstance(phase_state, dict) else {}
            momentum = phase_item.get("momentum", {}) if isinstance(phase_item, dict) else {}
            result[zone][phase] = momentum.get("velocity_magnitude", {})
    return result


def configure_autosave(solver: Any, root: str) -> dict[str, Any]:
    solver.settings.file.auto_save.set_state(
        {
            "case_frequency": "each-time",
            "data_frequency": 250,
            "root_name": win(root, "F-autosave-%i"),
            "retain_most_recent_files": True,
            "max_files": 2,
            "append_file_name_with": {
                "file_suffix_type": "time-step",
                "file_decimal_digit": 6,
            },
        }
    )
    return safe_get_state(solver.settings.file.auto_save, "autosave")


def set_equations(solver: Any, full_mixture: bool) -> None:
    equations = solver.settings.solution.controls.equations
    equations["mp"].set_state(full_mixture)
    equations = solver.settings.solution.controls.equations
    equations["drift"].set_state(full_mixture)


def set_inlet_velocities(solver: Any, velocity: float) -> None:
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            bc[zone].phase[phase].momentum.velocity_magnitude.set_state(
                {"option": "value", "value": velocity}
            )
            bc = solver.settings.setup.boundary_conditions.velocity_inlet


def set_branch_settings(
    solver: Any,
    *,
    momentum_urf: float,
    velocity: float,
    full_mixture: bool,
) -> dict[str, Any]:
    solver.settings.solution.controls.under_relaxation["mom"].set_state(momentum_urf)
    set_equations(solver, full_mixture)
    set_inlet_velocities(solver, velocity)
    return state_readback(solver)


def write_case(solver: Any, path: str) -> None:
    solver.settings.file.write_case(file_name=path)
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Missing Fluent case after write: {path}")


def write_pair(solver: Any, case_path: str, data_file: str | None = None) -> None:
    data_file = data_file or data_path(case_path)
    write_case(solver, case_path)
    solver.settings.file.write_data(file_name=data_file)
    if not remote_file_exists(solver, data_file):
        raise RuntimeError(f"Missing Fluent data after write: {data_file}")


def read_case(solver: Any, path: str) -> None:
    solver.settings.file.read_case(file_name=path)


def stop_native_transcript_if_active(solver: Any) -> None:
    """Release a dangling native transcript before the next stage journal."""
    try:
        solver.tui.file.stop_transcript()
    except Exception:
        pass


def classify_branch_error(exc: Exception) -> str:
    """Keep transport loss distinct from a genuine hard numerical failure."""
    message = f"{type(exc).__name__}: {exc}".lower()
    if any(
        marker in message
        for marker in (
            "stream removed",
            "failed to connect",
            "connect() timed out",
            "deadline exceeded",
            "unavailable",
            "can't assign requested address",
        )
    ):
        return "TRANSPORT_FAILURE"
    if any(
        marker in message
        for marker in (
            "floating point",
            "fpe",
            "non-finite",
            "amg divergence",
            "unrecoverable amg",
        )
    ):
        return "NUMERICAL_FAILURE"
    return "EXECUTION_ERROR"


def wait_for_iteration(solver: Any, expected: int, *, attempts: int = 12) -> int | None:
    latest: int | None = None
    for _ in range(attempts):
        try:
            snapshot = collect_snapshot(solver, monitor_sets=("residual",))
            value = snapshot.get("progress", {}).get("iteration")
            if value is not None:
                latest = max(latest or int(value), int(value))
                if latest >= expected:
                    return latest
        except Exception:
            pass
        time.sleep(5)
    return latest


def native_journal(
    *,
    root: str,
    label: str,
    iterations: int,
    checkpoint_case: str,
    residual_path: str,
    transcript_path: str,
) -> str:
    journal = f"""; 03A Stage-3 overnight native journal
; branch-stage: {label}
; fixed native iterations: {iterations}
; branch errors are handled by the supervising client; no rescue settings.
/file/confirm-overwrite? no
/file/start-transcript \"{transcript_path}\"
/solve/monitors/residual/print? no
/solve/monitors/residual/plot? yes
/solve/monitors/residual/n-save 250
/solve/iterate {iterations}
/file/write-case-data \"{checkpoint_case}\"
/plot/residuals-set/plot-to-file \"{residual_path}\"
/plot/residuals
/plot/residuals-set/end-plot-to-file
/file/stop-transcript
"""
    return journal


def run_native_stage(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    root: str,
    iterations: int,
    expected_iteration: int | None,
    stamp: str,
) -> tuple[Any, str]:
    stem = f"{branch}-{stage}-iter{expected_iteration or 0:06d}-{stamp}"
    case_path = win(root, stem + ".cas.h5")
    residual_path = win(root, stem + "-residuals.out")
    transcript_path = win(root, stem + ".trn")
    journal_path = win(root, stem + ".jou")
    journal = native_journal(
        root=root,
        label=f"{branch}/{stage}",
        iterations=iterations,
        checkpoint_case=case_path,
        residual_path=residual_path,
        transcript_path=transcript_path,
    )
    write_remote_journal(solver, journal_path, journal)
    events.emit(
        "native_journal_handoff",
        branch=branch,
        stage=stage,
        iterations=iterations,
        expected_iteration=expected_iteration,
        journal=journal_path,
        transcript=transcript_path,
    )
    solver.settings.file.read_journal(file_name_list=[journal_path])
    observed = wait_for_iteration(solver, expected_iteration) if expected_iteration else None
    pair_ok = remote_file_exists(solver, case_path) and remote_file_exists(
        solver, data_path(case_path)
    )
    if not pair_ok:
        raise RuntimeError(f"Native stage did not leave a complete pair: {case_path}")
    if (
        expected_iteration is not None
        and observed is not None
        and expected_iteration - observed > 10
    ):
        raise RuntimeError(
            f"Native stage stopped before expected iteration {expected_iteration}; observed {observed}"
        )
    events.emit(
        "native_stage_complete",
        branch=branch,
        stage=stage,
        expected_iteration=expected_iteration,
        observed_iteration=observed,
        case=case_path,
        data=data_path(case_path),
    )
    return solver, case_path


def verify_transition(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    velocity: float,
    momentum_urf: float,
    full_mixture: bool,
) -> None:
    if equation_value(after["equations"], "mp") is not full_mixture:
        raise RuntimeError("mp equation state failed transition verification")
    if equation_value(after["equations"], "drift") is not full_mixture:
        raise RuntimeError("drift equation state failed transition verification")
    actual_urf = urf_value(after["under_relaxation"])
    if actual_urf is None or abs(actual_urf - momentum_urf) > 1e-9:
        raise RuntimeError(f"Momentum URF changed unexpectedly: {actual_urf!r}")
    values = velocity_values(after)
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            value = values[zone][phase]
            actual = value.get("value") if isinstance(value, dict) else None
            if actual is None or abs(float(actual) - velocity) > 1e-8:
                raise RuntimeError(f"Velocity transition failed for {zone}/{phase}: {value!r}")
    if before["inlet_invariants"] != after["inlet_invariants"]:
        raise RuntimeError("Turbulence intensity or hydraulic diameter changed")


def transition(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    from_stage: str,
    to_stage: str,
    root: str,
    velocity: float,
    momentum_urf: float,
    stamp: str,
) -> Any:
    before = state_readback(solver)
    checkpoint = win(root, f"{branch}-{from_stage}-pre-transition-{stamp}.cas.h5")
    write_pair(solver, checkpoint)
    after_settings = set_branch_settings(
        solver,
        momentum_urf=momentum_urf,
        velocity=velocity,
        full_mixture=True,
    )
    verify_transition(
        before,
        after_settings,
        velocity=velocity,
        momentum_urf=momentum_urf,
        full_mixture=True,
    )
    transition_case = win(root, f"{branch}-{to_stage}-transition-{stamp}.cas.h5")
    write_pair(solver, transition_case)
    events.emit(
        "transition_verified",
        branch=branch,
        from_stage=from_stage,
        to_stage=to_stage,
        reason="USER_FIXED_ITERATION_OVERRIDE",
        checkpoint_before=checkpoint,
        checkpoint_after=transition_case,
        settings_before=before,
        settings_after=after_settings,
        no_reinitialization=True,
    )
    return solver


def prepare_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    root: str,
    momentum_urf: float,
    stamp: str,
) -> Any:
    if not remote_file_exists(solver, P0_REMOTE):
        raise FileNotFoundError(f"Released P0 is unavailable: {P0_REMOTE}")
    ensure_remote_directory(solver, root)
    local_p0 = win(root, f"{branch}-P0-local-{stamp}.cas.h5")
    urf_tag = str(momentum_urf).replace(".", "p")
    preinit = win(root, f"{branch}-D-M1-S1-U{urf_tag}-preinit-{stamp}.cas.h5")
    events.emit("p0_release_verified", branch=branch, p0=P0_REMOTE, p0_sha256=P0_SHA256)
    read_case(solver, P0_REMOTE)
    write_case(solver, local_p0)
    read_case(solver, local_p0)
    before = state_readback(solver)
    settings = set_branch_settings(
        solver,
        momentum_urf=momentum_urf,
        velocity=VELOCITY_10,
        full_mixture=False,
    )
    if before["inlet_invariants"] != settings["inlet_invariants"]:
        raise RuntimeError("P0-to-branch setup changed turbulence invariants")
    write_case(solver, preinit)
    read_case(solver, preinit)
    configure_autosave(solver, root)
    settings = state_readback(solver)
    events.emit(
        "preinit_verified",
        branch=branch,
        local_p0=local_p0,
        preinit=preinit,
        settings=settings,
        p0_sha256=P0_SHA256,
    )
    solver.settings.solution.initialization.hybrid_initialize()
    start = win(root, f"{branch}-hybrid-initialized-iter000000-{stamp}.cas.h5")
    write_pair(solver, start)
    events.emit(
        "hybrid_initialized_once",
        branch=branch,
        start_case=start,
        start_data=data_path(start),
    )
    return solver


def run_from_scratch_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    momentum_urf: float,
    stamp: str,
) -> Any:
    """Run one complete F## branch from pristine P0 through 100% loading.

    The stage calls are intentionally explicit. Each call blocks on one native
    Fluent journal before the next transition is considered.
    """
    root = win(REMOTE_QUEUE_ROOT, branch)
    solver = prepare_branch(
        solver,
        events,
        branch=branch,
        root=root,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    solver, _ = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="carrier-10pct",
        root=root,
        iterations=3000,
        expected_iteration=3000,
        stamp=stamp,
    )
    solver = transition(
        solver,
        events,
        branch=branch,
        from_stage="carrier-10pct",
        to_stage="full-mixture-10pct",
        root=root,
        velocity=VELOCITY_10,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    solver, _ = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="full-mixture-10pct",
        root=root,
        iterations=3000,
        expected_iteration=6000,
        stamp=stamp,
    )
    solver = transition(
        solver,
        events,
        branch=branch,
        from_stage="full-mixture-10pct",
        to_stage="full-mixture-20pct",
        root=root,
        velocity=VELOCITY_20,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    solver, _ = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="full-mixture-20pct",
        root=root,
        iterations=3000,
        expected_iteration=9000,
        stamp=stamp,
    )
    solver = transition(
        solver,
        events,
        branch=branch,
        from_stage="full-mixture-20pct",
        to_stage="full-mixture-40pct",
        root=root,
        velocity=VELOCITY_40,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    solver, _ = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="full-mixture-40pct",
        root=root,
        iterations=3000,
        expected_iteration=12000,
        stamp=stamp,
    )
    solver = transition(
        solver,
        events,
        branch=branch,
        from_stage="full-mixture-40pct",
        to_stage="full-mixture-80pct",
        root=root,
        velocity=VELOCITY_80,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    solver, _ = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="full-mixture-80pct",
        root=root,
        iterations=3000,
        expected_iteration=15000,
        stamp=stamp,
    )
    solver = transition(
        solver,
        events,
        branch=branch,
        from_stage="full-mixture-80pct",
        to_stage="full-mixture-100pct",
        root=root,
        velocity=VELOCITY_100,
        momentum_urf=momentum_urf,
        stamp=stamp,
    )
    solver, _ = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="full-mixture-100pct",
        root=root,
        iterations=3000,
        expected_iteration=18000,
        stamp=stamp,
    )
    events.emit("branch_complete", branch=branch, final_stage="full-mixture-100pct")
    return solver


def guarded_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    runner: Any,
    stamp: str,
) -> Any:
    events.emit("branch_start", branch=branch)
    try:
        solver = runner(solver, events, stamp=stamp)
        return solver
    except Exception as exc:
        events.emit(
            "branch_skipped_after_error",
            branch=branch,
            classification=classify_branch_error(exc),
            error=repr(exc),
            traceback=traceback.format_exc(),
        )
        try:
            solver = connect(server_id=SERVER_ID, start_transcript=False)
            stop_native_transcript_if_active(solver)
            return solver
        except Exception as reconnect_error:
            events.emit(
                "fluent_reconnect_failed_after_branch_error",
                branch=branch,
                error=repr(reconnect_error),
            )
            raise


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output" / "03a_stage3" / "overnight" / stamp
    events = EventLog(output_dir / "overnight-events.jsonl", stamp)
    events.emit(
        "queue_start",
        server_id=SERVER_ID,
        queue=("F08", "F10", "F12"),
        policy="user-authorized-fixed-3000-per-stage; all-branches-from-pristine-P0",
        p0_sha256=P0_SHA256,
    )
    solver = connect(server_id=SERVER_ID, start_transcript=False)
    if not solver.is_active():
        raise RuntimeError("Fluent server 1 is not active")
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Unexpected Fluent version: {solver.get_fluent_version()!r}")
    stop_native_transcript_if_active(solver)
    solver = guarded_branch(
        solver,
        events,
        branch="F08",
        runner=lambda s, e, stamp: run_from_scratch_branch(
            s, e, branch="F08", momentum_urf=0.7, stamp=stamp
        ),
        stamp=stamp,
    )
    solver = guarded_branch(
        solver,
        events,
        branch="F10",
        runner=lambda s, e, stamp: run_from_scratch_branch(
            s, e, branch="F10", momentum_urf=0.5, stamp=stamp
        ),
        stamp=stamp,
    )
    solver = guarded_branch(
        solver,
        events,
        branch="F12",
        runner=lambda s, e, stamp: run_from_scratch_branch(
            s, e, branch="F12", momentum_urf=0.3, stamp=stamp
        ),
        stamp=stamp,
    )
    events.emit("queue_complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

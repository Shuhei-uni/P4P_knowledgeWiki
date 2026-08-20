#!/usr/bin/env python3
"""Hand the user-authorized overnight Stage-3 journal sequence to Fluent 3.

This runner is deliberately an execution supervisor, not a new experiment
definition.  It writes native Fluent journals to the Fluent machine and hands
them to the already-running session one stage at a time.  The user override
replaces the adaptive gate pauses with fixed blocks:

* the active F07 10% state receives exactly 2,150 more iterations;
* every subsequent F07/F09 loading state receives 3,000 iterations;
* the non-ramping F03 control receives 5,000 iterations;
* F01 is already a preserved numerical failure and is not retried;
* an error skips the affected branch and the queue proceeds independently.

All case/data files, journals, transcripts, and autosaves remain on the
Fluent machine under C:\\Temp\\03A-stage3-<branch>.  The repository receives
only the local execution event log and manifest.  The script never writes to
the shared OneDrive P0 directory and never exits Fluent.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
import time
import traceback
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402


SERVER_ID = "3"
P0_REMOTE = (
    r"C:\Users\syok443\OneDrive - The University of Auckland"
    r"\2026 Sem 2\700\Full geom\03A-stage3"
    r"\03A-stage3-P0-monitor-ready-preinit.cas.h5"
)
P0_SHA256 = "8b9489d745a9539bfa36ffdca0fe224331fce749c331f08f6b0fc1ad6f386301"
BRANCH_ROOTS = {
    # F07 was prepared before the overnight handoff and already has its
    # validated 10%-at-iteration-1000 checkpoint in this directory.
    "F07": r"C:\Temp\03A-stage3-F07",
    "F03": r"C:\Temp\03A-stage3-F03",
    "F09": r"C:\Temp\03A-stage3-F09",
}
F07_RESUME_CASE = r"C:\Temp\03A-stage3-F07\F07-10pct-1000.cas.h5"
F07_RESUME_DATA = r"C:\Temp\03A-stage3-F07\F07-10pct-1000.dat.h5"
INLET_ZONES = ("liquidinlet", "steaminlet")
INLET_PHASES = ("phase-1", "phase-2")
VELOCITIES = {
    "10pct": 2.7118,
    "20pct": 5.4236,
    "40pct": 10.8472,
    "80pct": 21.6944,
    "100pct": 27.118,
}
PAIR_WAIT_SECONDS = 4 * 60 * 60
SKIP_RECONNECT_ATTEMPTS = 3
SKIP_RECONNECT_DELAY_SECONDS = 15.0


def win(root: str, name: str) -> str:
    return str(PureWindowsPath(root) / name)


def branch_root(branch: str) -> str:
    try:
        return BRANCH_ROOTS[branch]
    except KeyError as exc:
        raise ValueError(f"No approved local root for branch {branch!r}") from exc


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


class TerminalNativeStageError(RuntimeError):
    """A Fluent-native journal returned a terminal solver/journal error.

    This deliberately excludes a client transport loss: Fluent may still be
    solving after a dropped gRPC client, so an uncertain block must be observed
    through its native endpoint before any branch decision is made.
    """

    def __init__(self, *, branch: str, stage: str, journal_error: Exception) -> None:
        self.branch = branch
        self.stage = stage
        self.journal_error = repr(journal_error)
        super().__init__(
            f"Native journal terminated in {branch}/{stage}: {self.journal_error}"
        )


def write_remote_text(solver: Any, remote_path: str, text_value: str) -> None:
    """Write a native journal using Fluent's own Scheme file service."""
    body = " ".join(
        f'(display "{scheme_string(line)}") (newline)'
        for line in text_value.splitlines()
    )
    expression = (
        f'(with-output-to-file "{scheme_string(remote_path)}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_path):
        raise RuntimeError(f"Fluent did not expose journal after write: {remote_path}")


def ensure_remote_directory(solver: Any, path: str) -> None:
    command = f'cmd /c if not exist "{path}" md "{path}"'
    result = solver.scheme.eval(f'(system "{scheme_string(command)}")')
    if result not in (0, None):
        raise RuntimeError(f"Could not create/verify Fluent directory {path}: {result!r}")
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent-machine directory is unavailable: {path}")


def stop_active_transcript(solver: Any) -> None:
    """Close an inherited transcript before a stage journal starts its own."""
    try:
        solver.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    except Exception:
        # A missing transcript is harmless; the native journal will start the
        # stage transcript and any actual journal failure remains visible.
        pass


def readback(solver: Any) -> dict[str, Any]:
    """Read branch identity controls and all inlet settings used by the override."""
    equations = safe_get_state(
        solver.settings.solution.controls.equations,
        "Stage-3 equations",
    )
    urf = safe_get_state(
        solver.settings.solution.controls.under_relaxation,
        "Stage-3 under-relaxation",
    )
    inlet_states: dict[str, Any] = {}
    invariants: dict[str, Any] = {}
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        inlet_states[zone] = safe_get_state(bc[zone], f"{zone} state")
        state = inlet_states[zone]
        phase_state = state.get("phase", {}) if isinstance(state, dict) else {}
        mixture = phase_state.get("mixture", {}) if isinstance(phase_state, dict) else {}
        turbulence = mixture.get("turbulence", {}) if isinstance(mixture, dict) else {}
        invariants[zone] = {
            "turbulent_intensity": turbulence.get("turbulent_intensity"),
            "hydraulic_diameter": mixture.get("hydraulic_diameter"),
        }
    return {
        "equations": equations,
        "under_relaxation": urf,
        "inlet_states": inlet_states,
        "inlet_invariants": invariants,
    }


def nested_value(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = nested_value(child, key)
            if found is not None:
                return found
    return None


def velocity_values(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for zone, zone_state in state["inlet_states"].items():
        result[zone] = {}
        phase_state = zone_state.get("phase", {}) if isinstance(zone_state, dict) else {}
        for phase in INLET_PHASES:
            phase_item = phase_state.get(phase, {}) if isinstance(phase_state, dict) else {}
            momentum = phase_item.get("momentum", {}) if isinstance(phase_item, dict) else {}
            result[zone][phase] = momentum.get("velocity_magnitude", {})
    return result


def configure_autosave(solver: Any, root: str) -> dict[str, Any]:
    state = {
        "case_frequency": "if-case-is-modified",
        "data_frequency": 250,
        "root_name": win(root, f"{PureWindowsPath(root).name}-autosave"),
        "retain_most_recent_files": True,
        "max_files": 5,
        "append_file_name_with": {
            "file_suffix_type": "time-step",
            "file_decimal_digit": 6,
        },
    }
    solver.settings.file.auto_save.set_state(state)
    return safe_get_state(solver.settings.file.auto_save, "Stage-3 autosave")


def set_equations(solver: Any, full_mixture: bool) -> None:
    equations = solver.settings.solution.controls.equations
    equations["mp"].set_state(full_mixture)
    equations["drift"].set_state(full_mixture)


def set_velocities(solver: Any, velocity: float) -> None:
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            bc[zone].phase[phase].momentum.velocity_magnitude.set_state(
                {"option": "value", "value": velocity}
            )


def set_stage_controls(solver: Any, *, momentum_urf: float, velocity: float) -> dict[str, Any]:
    solver.settings.solution.controls.under_relaxation["mom"].set_state(momentum_urf)
    set_equations(solver, True)
    set_velocities(solver, velocity)
    return readback(solver)


def write_case(solver: Any, path: str) -> None:
    solver.settings.file.write_case(file_name=path)
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Missing Fluent case after write: {path}")


def write_pair(solver: Any, case_path: str) -> None:
    data_file = data_path(case_path)
    write_case(solver, case_path)
    solver.settings.file.write_data(file_name=data_file)
    if not remote_file_exists(solver, data_file):
        raise RuntimeError(f"Missing Fluent data after write: {data_file}")


def wait_for_iteration(solver: Any, expected: int, *, attempts: int = 18) -> int | None:
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


def snapshot_summary(solver: Any) -> dict[str, Any]:
    """Capture bounded read-only evidence without treating it as case identity."""
    try:
        snapshot = collect_snapshot(solver, monitor_sets=("residual",))
        return {
            "health": snapshot.get("health"),
            "iteration": snapshot.get("progress", {}).get("iteration"),
            "residuals": snapshot.get("monitors", {}).get("residual", {}).get("last_values"),
            "read_errors": snapshot.get("read_errors"),
        }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def reconnect(events: EventLog, *, reason: str, attempts: int = 3) -> Any:
    """Reconnect only; this function never reloads or reissues a solve."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            solver = connect(server_id=SERVER_ID)
            if not solver.is_active():
                raise RuntimeError("Fluent handoff returned an inactive session")
            events.emit("reconnected", reason=reason, reconnect_attempt=attempt)
            return solver
        except Exception as exc:
            last_error = exc
            events.emit(
                "reconnect_pending",
                reason=reason,
                reconnect_attempt=attempt,
                max_attempts=attempts,
                error=repr(exc),
                no_solve_issued=True,
            )
            if attempt < attempts:
                time.sleep(SKIP_RECONNECT_DELAY_SECONDS)
    raise RuntimeError(f"Could not reconnect after {attempts} attempts: {reason}") from last_error


def wait_for_pair(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    case_path: str,
    timeout_seconds: float = PAIR_WAIT_SECONDS,
) -> Any:
    """Observe a native endpoint without ever repeating the submitted solve block."""
    data_file = data_path(case_path)
    deadline = time.monotonic() + timeout_seconds
    probe = solver
    partial_logged = False
    while time.monotonic() < deadline:
        try:
            case_exists = remote_file_exists(probe, case_path)
            data_exists = remote_file_exists(probe, data_file)
            if case_exists and data_exists:
                events.emit(
                    "native_pair_verified",
                    branch=branch,
                    stage=stage,
                    case=case_path,
                    data=data_file,
                    snapshot=snapshot_summary(probe),
                )
                return probe
            if (case_exists or data_exists) and not partial_logged:
                events.emit(
                    "partial_native_pair_observed",
                    branch=branch,
                    stage=stage,
                    case_exists=case_exists,
                    data_exists=data_exists,
                )
                partial_logged = True
        except Exception as exc:
            events.emit(
                "transport_observation_error",
                branch=branch,
                stage=stage,
                error=repr(exc),
                no_solve_issued=True,
            )
            try:
                probe = reconnect(events, reason=f"pair_wait:{branch}:{stage}")
            except Exception as reconnect_error:
                events.emit(
                    "pair_wait_reconnect_unavailable",
                    branch=branch,
                    stage=stage,
                    error=repr(reconnect_error),
                    no_solve_issued=True,
                )
        time.sleep(10.0)
    raise TimeoutError(
        f"Timed out waiting for native paired endpoint {case_path} and {data_file}"
    )


def is_terminal_native_error(exc: Exception) -> bool:
    """Separate a Fluent-returned journal stop from an uncertain transport loss."""
    text = str(exc).lower()
    transport_markers = (
        "stream removed", "recvmsg", "no route to host", "failed to connect",
        "connection reset", "deadline exceeded", "grpc", "transport", "timed out",
    )
    if any(marker in text for marker in transport_markers):
        return False
    return "error object" in text or any(
        marker in text
        for marker in (
            "floating-point", "floating point", "fpe", "amg", "non-finite",
            "nonfinite", "solver termination",
        )
    )


def is_hard_numerical_failure(exc: Exception) -> bool:
    text = " ".join((str(exc), getattr(exc, "journal_error", ""))).lower()
    return any(
        marker in text
        for marker in (
            "floating-point", "floating point", "fpe", "amg", "non-finite",
            "nonfinite", "solver termination",
        )
    )


def native_stage_journal(
    *,
    iterations: int,
    checkpoint_case: str,
    transcript_path: str,
) -> str:
    return f"""; USER-AUTHORIZED 03A Stage-3 fixed-block journal
; The adaptive gate is overridden by the user for this unattended run.
; Native solve block: {iterations} iterations
; Local checkpoint pair: {checkpoint_case} / {data_path(checkpoint_case)}
/file/start-transcript \"{transcript_path}\"
/solve/monitors/residual/print? yes
/solve/monitors/residual/plot? yes
/solve/monitors/residual/n-save 12000
/solve/iterate {iterations}
/file/write-case-data \"{checkpoint_case}\"
/file/stop-transcript
"""


def run_native_stage(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    root: str,
    iterations: int,
    expected_iteration: int,
) -> Any:
    stamp = events.stamp
    stem = f"{branch}-{stage}-end-iter{expected_iteration:06d}-{stamp}"
    checkpoint_case = win(root, stem + ".cas.h5")
    transcript_path = win(root, stem + ".trn")
    journal_path = win(root, stem + ".jou")
    journal = native_stage_journal(
        iterations=iterations,
        checkpoint_case=checkpoint_case,
        transcript_path=transcript_path,
    )
    # The initial F07 preparation left its long transcript open.  Fluent
    # rejects a second /file/start-transcript until the inherited one is
    # closed, so close it explicitly before handing over this native journal.
    stop_active_transcript(solver)
    write_remote_text(solver, journal_path, journal)
    events.emit(
        "journal_handoff",
        branch=branch,
        stage=stage,
        iterations=iterations,
        expected_iteration=expected_iteration,
        journal=journal_path,
        transcript=transcript_path,
        checkpoint_case=checkpoint_case,
        checkpoint_data=data_path(checkpoint_case),
    )
    native_error: str | None = None
    try:
        solver.settings.file.read_journal(file_name_list=[journal_path])
    except Exception as exc:
        native_error = repr(exc)
        events.emit(
            "native_stage_client_error",
            branch=branch,
            stage=stage,
            error=native_error,
            note="No solve is repeated; transport loss is reconciled against the native endpoint.",
        )
        if is_terminal_native_error(exc):
            events.emit(
                "native_stage_terminal_error",
                branch=branch,
                stage=stage,
                error=native_error,
                numerical_marker=is_hard_numerical_failure(exc),
            )
            raise TerminalNativeStageError(
                branch=branch, stage=stage, journal_error=exc
            ) from exc
        try:
            solver = reconnect(events, reason=f"native_stage_error:{branch}:{stage}")
        except Exception as reconnect_error:
            events.emit(
                "native_stage_reconnect_unavailable",
                branch=branch,
                stage=stage,
                error=repr(reconnect_error),
                no_solve_issued=True,
            )
    solver = wait_for_pair(
        solver,
        events,
        branch=branch,
        stage=stage,
        case_path=checkpoint_case,
    )
    observed = wait_for_iteration(solver, expected_iteration)
    if observed is not None and observed < expected_iteration:
        raise RuntimeError(
            f"Stage stopped before expected iteration {expected_iteration}; observed {observed}"
        )
    events.emit(
        "stage_complete",
        branch=branch,
        stage=stage,
        iterations=iterations,
        expected_iteration=expected_iteration,
        observed_iteration=observed,
        checkpoint_case=checkpoint_case,
        checkpoint_data=data_path(checkpoint_case),
        native_client_error=native_error,
    )
    return solver


def verify_stage_state(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    velocity: float,
    momentum_urf: float,
) -> None:
    if nested_value(after["equations"], "mp") is not True:
        raise RuntimeError("Full Mixture equation is not active after transition")
    if nested_value(after["equations"], "drift") is not True:
        raise RuntimeError("Drift/slip equation is not active after transition")
    actual_urf = nested_value(after["under_relaxation"], "mom")
    if actual_urf is None or abs(float(actual_urf) - momentum_urf) > 1e-9:
        raise RuntimeError(f"Momentum URF changed unexpectedly: {actual_urf!r}")
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            item = velocity_values(after)[zone][phase]
            actual = item.get("value") if isinstance(item, dict) else None
            if actual is None or abs(float(actual) - velocity) > 1e-8:
                raise RuntimeError(f"Velocity transition failed for {zone}/{phase}: {item!r}")
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
) -> Any:
    before = readback(solver)
    before_case = win(root, f"{branch}-{from_stage}-pre-transition-{events.stamp}.cas.h5")
    write_pair(solver, before_case)
    after = set_stage_controls(solver, momentum_urf=momentum_urf, velocity=velocity)
    verify_stage_state(before, after, velocity=velocity, momentum_urf=momentum_urf)
    after_case = win(root, f"{branch}-{to_stage}-transition-{events.stamp}.cas.h5")
    write_pair(solver, after_case)
    events.emit(
        "transition_verified",
        branch=branch,
        from_stage=from_stage,
        to_stage=to_stage,
        reason="USER_FIXED_ITERATION_OVERRIDE",
        checkpoint_before=before_case,
        checkpoint_after=after_case,
        settings_before=before,
        settings_after=after,
        no_reinitialization=True,
    )
    return solver


def prepare_new_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    momentum_urf: float,
    initial_velocity: float,
) -> Any:
    root = branch_root(branch)
    ensure_remote_directory(solver, root)
    local_p0 = win(root, f"{branch}-P0-local-{events.stamp}.cas.h5")
    preinit = win(root, f"{branch}-A-preinit-{events.stamp}.cas.h5")
    events.emit(
        "p0_lineage_start",
        branch=branch,
        p0=P0_REMOTE,
        p0_sha256=P0_SHA256,
        local_root=root,
    )
    if not remote_file_exists(solver, P0_REMOTE):
        raise FileNotFoundError(f"Released P0 is unavailable: {P0_REMOTE}")
    solver.settings.file.read_case(file_name=P0_REMOTE)
    write_case(solver, local_p0)
    solver.settings.file.read_case(file_name=local_p0)
    before = readback(solver)
    after = set_stage_controls(
        solver,
        momentum_urf=momentum_urf,
        velocity=initial_velocity,
    )
    if before["inlet_invariants"] != after["inlet_invariants"]:
        raise RuntimeError("P0-derived branch changed turbulence invariants")
    write_case(solver, preinit)
    solver.settings.file.read_case(file_name=preinit)
    autosave = configure_autosave(solver, root)
    settings = readback(solver)
    events.emit(
        "preinit_verified",
        branch=branch,
        local_p0=local_p0,
        preinit=preinit,
        settings=settings,
        autosave=autosave,
        p0_sha256=P0_SHA256,
    )
    solver.settings.solution.initialization.hybrid_initialize()
    initialized = win(root, f"{branch}-hybrid-initialized-{events.stamp}.cas.h5")
    write_pair(solver, initialized)
    events.emit(
        "hybrid_initialized_once",
        branch=branch,
        case=initialized,
        data=data_path(initialized),
    )
    return solver


def resume_f07(solver: Any, events: EventLog) -> Any:
    """Restore the validated F07 10%/iteration-1000 pair after any handoff."""
    root = branch_root("F07")
    ensure_remote_directory(solver, root)
    if not remote_file_exists(solver, F07_RESUME_CASE):
        raise FileNotFoundError(f"Missing F07 resume case: {F07_RESUME_CASE}")
    if not remote_file_exists(solver, F07_RESUME_DATA):
        raise FileNotFoundError(f"Missing F07 resume data: {F07_RESUME_DATA}")
    solver.settings.file.read_case(file_name=F07_RESUME_CASE)
    solver.settings.file.read_data(file_name=F07_RESUME_DATA)
    autosave = configure_autosave(solver, root)
    settings = readback(solver)
    events.emit(
        "f07_resume_pair_loaded",
        branch="F07",
        stage="10pct",
        iteration=1000,
        case=F07_RESUME_CASE,
        data=F07_RESUME_DATA,
        settings=settings,
        autosave=autosave,
        no_reinitialization=True,
    )
    return solver


def run_staged_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    momentum_urf: float,
    current_stage: str | None = None,
) -> Any:
    root = branch_root(branch)
    if current_stage is not None:
        # F07 is already loaded and verified at 10%/iteration 1000 when this
        # script is handed to the session.  The user explicitly requested
        # another 2,150 iterations for this active stage.
        settings = readback(solver)
        actual_urf = nested_value(settings["under_relaxation"], "mom")
        if actual_urf is None or abs(float(actual_urf) - momentum_urf) > 1e-9:
            raise RuntimeError(f"{branch} active momentum URF mismatch: {actual_urf!r}")
        if nested_value(settings["equations"], "mp") is not True:
            raise RuntimeError(f"{branch} active state is not full Mixture")
        actual_velocities = velocity_values(settings)
        for zone in INLET_ZONES:
            for phase in INLET_PHASES:
                value = actual_velocities[zone][phase]
                actual = value.get("value") if isinstance(value, dict) else None
                if actual is None or abs(float(actual) - VELOCITIES["10pct"]) > 1e-8:
                    raise RuntimeError(f"{branch} active velocity mismatch: {zone}/{phase}: {value!r}")
        observed_iteration = wait_for_iteration(solver, 1000)
        if observed_iteration is not None and observed_iteration < 1000:
            raise RuntimeError(
                f"{branch} active iteration is below the verified resume point: {observed_iteration!r}"
            )
        # The named case/data pair is the released F07 iteration-1000 recovery
        # state. Monitor history can be unavailable immediately after a reload,
        # so lack of streamed history is not grounds to skip this branch.
        current_iteration = observed_iteration or 1000
        events.emit(
            "active_stage_verified",
            branch=branch,
            stage=current_stage,
            current_iteration=current_iteration,
            iteration_evidence=(
                "residual_monitor" if observed_iteration is not None else "named_resume_case_data_pair"
            ),
            settings=settings,
            instruction="run another 2150 iterations",
        )
        solver = run_native_stage(
            solver,
            events,
            branch=branch,
            stage="10pct-resume-plus-2150",
            root=root,
            iterations=2150,
            expected_iteration=3150,
        )
        previous_stage = "10pct-resume-plus-2150"
        cumulative = 3150
        remaining = (
            ("20pct", VELOCITIES["20pct"]),
            ("40pct", VELOCITIES["40pct"]),
            ("80pct", VELOCITIES["80pct"]),
            ("100pct", VELOCITIES["100pct"]),
        )
    else:
        previous_stage = "10pct"
        cumulative = 0
        remaining = (
            ("10pct", VELOCITIES["10pct"]),
            ("20pct", VELOCITIES["20pct"]),
            ("40pct", VELOCITIES["40pct"]),
            ("80pct", VELOCITIES["80pct"]),
            ("100pct", VELOCITIES["100pct"]),
        )

    if current_stage is None:
        solver = run_native_stage(
            solver,
            events,
            branch=branch,
            stage="10pct",
            root=root,
            iterations=3000,
            expected_iteration=3000,
        )
        remaining = remaining[1:]
        cumulative = 3000

    for index, (stage, velocity) in enumerate(remaining):
        solver = transition(
            solver,
            events,
            branch=branch,
            from_stage=previous_stage,
            to_stage=stage,
            root=root,
            velocity=velocity,
            momentum_urf=momentum_urf,
        )
        cumulative += 3000
        solver = run_native_stage(
            solver,
            events,
            branch=branch,
            stage=stage,
            root=root,
            iterations=3000,
            expected_iteration=cumulative,
        )
        previous_stage = stage
    events.emit(
        "branch_complete",
        branch=branch,
        final_stage=previous_stage,
        final_iteration=cumulative,
        policy="fixed-3000-per-staged-state; active-stage-plus-2150",
    )
    return solver


def run_nonramping_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    momentum_urf: float,
) -> Any:
    root = branch_root(branch)
    solver = prepare_new_branch(
        solver,
        events,
        branch=branch,
        momentum_urf=momentum_urf,
        initial_velocity=VELOCITIES["100pct"],
    )
    solver = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="100pct-final-5000",
        root=root,
        iterations=5000,
        expected_iteration=5000,
    )
    events.emit(
        "branch_complete",
        branch=branch,
        final_stage="100pct-final-5000",
        final_iteration=5000,
        policy="user-fixed-5000-nonramping-case",
    )
    return solver


def guarded_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    runner: Callable[[Any, EventLog], Any],
) -> tuple[Any, bool, bool]:
    events.emit("branch_start", branch=branch)
    try:
        return runner(solver, events), True, True
    except Exception as exc:
        hard_numerical = is_hard_numerical_failure(exc)
        terminal_native_stage = isinstance(exc, TerminalNativeStageError)
        unresolved_transport = isinstance(exc, TimeoutError) or (
            "timed out waiting for native paired endpoint" in str(exc).lower()
        )
        if hard_numerical:
            classification = "NUMERICAL_FAILURE"
        elif terminal_native_stage:
            classification = "TERMINAL_NATIVE_STAGE_FAILURE"
        else:
            classification = "EXECUTION_OR_TRANSPORT_FAILURE"
        events.emit(
            "branch_failure",
            branch=branch,
            classification=classification,
            error=repr(exc),
            traceback=traceback.format_exc(),
        )
        if unresolved_transport:
            events.emit(
                "queue_blocked",
                branch=branch,
                reason="Transport loss left native-stage completion uncertain; no next branch started",
            )
            return solver, False, False
        if not terminal_native_stage:
            events.emit(
                "queue_blocked",
                branch=branch,
                reason="Setup or verification error requires review; no next branch started",
            )
            return solver, False, False
        try:
            replacement = reconnect(
                events,
                reason=f"after_terminal_stage_skip:{branch}",
                attempts=SKIP_RECONNECT_ATTEMPTS,
            )
            events.emit(
                "branch_skipped_after_terminal_error",
                branch=branch,
                numerical_failure=hard_numerical,
                next_branch_policy="LOAD_PRISTINE_P0_INDEPENDENTLY",
            )
            return replacement, False, True
        except Exception as reconnect_error:
            events.emit(
                "queue_blocked",
                branch=branch,
                reason="Terminal Fluent error could not be followed by a safe reconnect",
                error=repr(reconnect_error),
            )
            return solver, False, False


def connect_with_transport_backoff(events: EventLog, *, attempts: int = 40) -> Any:
    """Reconnect to the same Fluent process without issuing any solve call."""
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            solver = connect(server_id=SERVER_ID)
            if not solver.is_active():
                raise RuntimeError("Fluent server 3 handshake returned an inactive session")
            if "2025 R2" not in str(solver.get_fluent_version()):
                raise RuntimeError(f"Unexpected Fluent version: {solver.get_fluent_version()!r}")
            events.emit(
                "fluent_session_verified",
                server_id=SERVER_ID,
                version=str(solver.get_fluent_version()),
                transport_attempt=attempt,
            )
            return solver
        except Exception as exc:
            last_error = exc
            events.emit(
                "transport_reconnect_pending",
                server_id=SERVER_ID,
                transport_attempt=attempt,
                max_attempts=attempts,
                error=repr(exc),
                no_solve_issued=True,
            )
            if attempt < attempts:
                time.sleep(30)
    raise RuntimeError(
        f"Fluent server 3 did not recover after {attempts} transport attempts"
    ) from last_error


def write_plan(path: Path) -> None:
    path.write_text(
        """; USER-AUTHORIZED 03A STAGE-3 OVERNIGHT FIXED-BLOCK PLAN
; Fluent session server: 3
; Shared P0 is read-only; all outputs are local under C:\\Temp.
;
; F01: already preserved NUMERICAL_FAILURE at iteration 5704; no retry.
; F07: current 10pct iteration 1000 -> +2150 to 3150, then
;      20pct 3000, 40pct 3000, 80pct 3000, 100pct 3000.
; F03: independent P0-derived A state, 100pct, 5000 iterations.
; F09: independent P0-derived C state, 10/20/40/80/100pct, 3000 each.
; Any branch error is logged, that branch is skipped, and the next branch
; starts independently from its own P0-derived local state.
""",
        encoding="utf-8",
    )


def main() -> int:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = PROJECT_ROOT / "output" / "03a_stage3" / "overnight" / stamp
    output_dir.mkdir(parents=True, exist_ok=True)
    events = EventLog(output_dir / "overnight-events.jsonl", stamp)
    plan_path = output_dir / "F01-F07-F03-F09-user-override.plan.jou"
    write_plan(plan_path)
    events.emit(
        "queue_start",
        server_id=SERVER_ID,
        queue=("F01", "F07", "F03", "F09"),
        policy="user-authorized-fixed-block-override",
        p0_sha256=P0_SHA256,
        plan=str(plan_path),
    )
    events.emit(
        "branch_skipped_prior_error",
        branch="F01",
        classification="NUMERICAL_FAILURE_ALREADY_PRESERVED",
        last_valid_iteration=5500,
        failure_iteration=5704,
        reason="No automatic retry of the already failed canonical control",
    )

    solver = connect_with_transport_backoff(events)

    solver, _f07_ok, can_continue = guarded_branch(
        solver,
        events,
        branch="F07",
        runner=lambda s, e: run_staged_branch(
            resume_f07(s, e),
            e,
            branch="F07",
            momentum_urf=0.7,
            current_stage="10pct",
        ),
    )
    if not can_continue:
        return 2
    solver, _f03_ok, can_continue = guarded_branch(
        solver,
        events,
        branch="F03",
        runner=lambda s, e: run_nonramping_branch(
            s,
            e,
            branch="F03",
            momentum_urf=0.5,
        ),
    )
    if not can_continue:
        return 2
    solver, _f09_ok, can_continue = guarded_branch(
        solver,
        events,
        branch="F09",
        runner=lambda s, e: run_staged_branch(
            prepare_new_branch(
                s,
                e,
                branch="F09",
                momentum_urf=0.5,
                initial_velocity=VELOCITIES["10pct"],
            ),
            e,
            branch="F09",
            momentum_urf=0.5,
        ),
    )
    if not can_continue:
        return 2
    events.emit("queue_complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

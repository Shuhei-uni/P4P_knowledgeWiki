#!/usr/bin/env python3
"""Restart the user-authorized fixed-3000 Stage-3 queue on Fluent server 2.

The scientific override is explicit: every prescribed Stage-3 state receives
exactly one native Fluent solve of 3,000 iterations.  Fluent owns each solve,
the native transcript, and the native autosave/checkpoint timing.  Python only
prepares independent branch state, submits one native journal per stage, waits
for the named paired endpoint, and performs the prescribed state transition.

This is intentionally separate from the adaptive production runner.  It does
not evaluate stage3-gate-v1 because the user explicitly replaced that decision
rule with a fixed-3,000-iterations-per-stage override.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
import time
import traceback
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.native_run_monitor import collect_snapshot  # noqa: E402


SERVER_ID = "2"
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
STAGE_ITERATIONS = 3000
PAIR_WAIT_SECONDS = 4 * 60 * 60
SKIP_RECONNECT_ATTEMPTS = 3
SKIP_RECONNECT_DELAY_SECONDS = 15.0
IDLE_PREFLIGHT_WINDOW_SECONDS = 5.0


def win(root: str, name: str) -> str:
    return str(PureWindowsPath(root) / name)


def data_path(case_path: str) -> str:
    if not case_path.endswith(".cas.h5"):
        raise ValueError(f"Expected .cas.h5 path, got {case_path!r}")
    return case_path[:-7] + ".dat.h5"


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


class RunLedger:
    """Small restart index for one fixed-3000 queue invocation.

    The ledger is deliberately not a recovery artifact: Fluent's paired
    case/data endpoints remain authoritative.  It records which endpoint the
    next supervisor process must verify before it can continue, so a laptop
    restart never replays an uncertain native solve block.
    """

    filename = "native-fixed-3000-resume-state.json"
    schema_version = 1

    def __init__(self, run_dir: Path, state: dict[str, Any]) -> None:
        self.run_dir = run_dir
        self.path = run_dir / self.filename
        self.state = state

    @classmethod
    def create(cls, run_dir: Path, *, stamp: str) -> "RunLedger":
        ledger = cls(
            run_dir,
            {
                "schema_version": cls.schema_version,
                "stamp": stamp,
                "queue": ["F02", "F04", "F11", "F06", "F05"],
                "branches": {},
            },
        )
        ledger._write()
        return ledger

    @classmethod
    def load(cls, run_dir: Path) -> "RunLedger":
        path = run_dir / cls.filename
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Resume ledger is missing: {path}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Resume ledger is not valid JSON: {path}") from exc
        if not isinstance(state, dict) or state.get("schema_version") != cls.schema_version:
            raise RuntimeError(f"Unsupported resume ledger: {path}")
        if not isinstance(state.get("stamp"), str) or not state["stamp"]:
            raise RuntimeError(f"Resume ledger has no run stamp: {path}")
        if not isinstance(state.get("branches"), dict):
            raise RuntimeError(f"Resume ledger has invalid branch state: {path}")
        return cls(run_dir, state)

    @property
    def stamp(self) -> str:
        return str(self.state["stamp"])

    def _branch(self, branch: str) -> dict[str, Any]:
        branches = self.state["branches"]
        return branches.setdefault(branch, {"stages": {}, "transitions": {}})

    def _write(self) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self.state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def branch_prepared(self, branch: str, *, root: str, start_case: str) -> None:
        item = self._branch(branch)
        item["prepared"] = {"root": root, "start_case": start_case, "status": "complete"}
        self._write()

    def stage_submitted(self, branch: str, stage: str, *, case_path: str) -> None:
        self._branch(branch)["stages"][stage] = {
            "case_path": case_path,
            "status": "submitted",
        }
        self._write()

    def stage_complete(self, branch: str, stage: str, *, case_path: str) -> None:
        self._branch(branch)["stages"][stage] = {
            "case_path": case_path,
            "status": "complete",
        }
        self._write()

    def transition_complete(self, branch: str, stage: str, *, case_path: str) -> None:
        self._branch(branch)["transitions"][stage] = {
            "case_path": case_path,
            "status": "complete",
        }
        self._write()

    def branch_skipped(
        self,
        branch: str,
        *,
        stage: str,
        reason: str,
        numerical_failure: bool,
    ) -> None:
        item = self._branch(branch)
        item["status"] = "skipped"
        item["skip"] = {
            "stage": stage,
            "reason": reason,
            "numerical_failure": numerical_failure,
            "status": "complete",
        }
        self._write()

    def stage(self, branch: str, stage: str) -> dict[str, Any] | None:
        value = self._branch(branch)["stages"].get(stage)
        return value if isinstance(value, dict) else None

    def prepared(self, branch: str) -> dict[str, Any] | None:
        value = self._branch(branch).get("prepared")
        return value if isinstance(value, dict) else None

    def transition(self, branch: str, stage: str) -> dict[str, Any] | None:
        value = self._branch(branch)["transitions"].get(stage)
        return value if isinstance(value, dict) else None

    def branch_status(self, branch: str) -> str | None:
        value = self._branch(branch).get("status")
        return value if isinstance(value, str) else None


class TerminalNativeStageError(RuntimeError):
    """A native stage journal stopped and Fluent returned control.

    This is deliberately distinct from a transport timeout.  The branch must
    not be repeated, because Fluent may already have advanced some iterations;
    after a successful reconnect the independently seeded next branch may run.
    """

    def __init__(self, *, branch: str, stage: str, journal_error: Exception) -> None:
        self.branch = branch
        self.stage = stage
        self.journal_error = repr(journal_error)
        super().__init__(
            f"Native journal terminated in {branch}/{stage}: {self.journal_error}"
        )


class QueuePaused(RuntimeError):
    """A cooperative pause was requested before submitting another stage."""


def write_remote_journal(solver: Any, remote_path: str, journal: str) -> None:
    """Write literal journal lines on the Fluent computer.

    Fluent 2025 R2 preserved literal ``\\n`` in an earlier implementation, so
    each line is emitted with an explicit Scheme ``display``/``newline`` pair.
    """

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
    """Create the run directory before any Fluent file write."""

    command = f'cmd /c if not exist "{path}" md "{path}"'
    result = solver.scheme.eval(f'(system "{scheme_string(command)}")')
    if result not in (0, None):
        raise RuntimeError(
            f"Could not create/verify Fluent-machine directory: {path}; result={result!r}"
        )
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent-machine directory is unavailable: {path}")


def state_readback(solver: Any) -> dict[str, Any]:
    """Read the live equation, URF, inlet, and turbulence-invariant state."""

    equations = safe_get_state(
        solver.settings.solution.controls.equations,
        "Stage-3 equations",
    )
    under_relaxation = safe_get_state(
        solver.settings.solution.controls.under_relaxation,
        "Stage-3 under-relaxation",
    )
    inlet_velocities: dict[str, dict[str, Any]] = {}
    inlet_invariants: dict[str, dict[str, Any]] = {}
    bc = solver.settings.setup.boundary_conditions.velocity_inlet
    for zone in INLET_ZONES:
        inlet_velocities[zone] = {}
        for phase in INLET_PHASES:
            inlet_velocities[zone][phase] = safe_get_state(
                bc[zone].phase[phase].momentum.velocity_magnitude,
                f"{zone}.{phase}.velocity_magnitude",
            )
        zone_state = safe_get_state(bc[zone], f"{zone} boundary")
        phase_state = zone_state.get("phase", {}) if isinstance(zone_state, dict) else {}
        mixture = phase_state.get("mixture", {}) if isinstance(phase_state, dict) else {}
        turbulence = mixture.get("turbulence", {}) if isinstance(mixture, dict) else {}
        inlet_invariants[zone] = {
            "turbulent_intensity": turbulence.get("turbulent_intensity"),
            "hydraulic_diameter": turbulence.get("hydraulic_diameter"),
        }
    return {
        "equations": equations,
        "under_relaxation": under_relaxation,
        "inlet_velocities": inlet_velocities,
        "inlet_invariants": inlet_invariants,
    }


def equation_value(equations: Any, key: str) -> bool | None:
    if isinstance(equations, dict):
        value = equations.get(key)
        if isinstance(value, bool):
            return value
        for child in equations.values():
            found = equation_value(child, key)
            if found is not None:
                return found
    return None


def momentum_urf_value(value: Any) -> float | None:
    if isinstance(value, dict):
        candidate = value.get("mom")
        if isinstance(candidate, (int, float)):
            return float(candidate)
        for child in value.values():
            found = momentum_urf_value(child)
            if found is not None:
                return found
    return None


def velocity_value(value: Any) -> float | None:
    if isinstance(value, dict):
        candidate = value.get("value")
        if isinstance(candidate, (int, float)):
            return float(candidate)
        for child in value.values():
            found = velocity_value(child)
            if found is not None:
                return found
    return None


def verify_settings(
    settings: dict[str, Any],
    *,
    full_mixture: bool,
    velocity: float,
    momentum_urf: float,
    invariants_before: dict[str, Any] | None = None,
) -> None:
    if equation_value(settings["equations"], "mp") is not full_mixture:
        raise RuntimeError(f"mp equation readback mismatch: {settings['equations']!r}")
    if equation_value(settings["equations"], "drift") is not full_mixture:
        raise RuntimeError(f"drift equation readback mismatch: {settings['equations']!r}")
    actual_urf = momentum_urf_value(settings["under_relaxation"])
    if actual_urf is None or abs(actual_urf - momentum_urf) > 1e-9:
        raise RuntimeError(f"Momentum URF readback mismatch: {actual_urf!r} != {momentum_urf}")
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            actual = velocity_value(settings["inlet_velocities"][zone][phase])
            if actual is None or abs(actual - velocity) > 1e-8:
                raise RuntimeError(
                    f"Velocity readback mismatch for {zone}/{phase}: {actual!r} != {velocity}"
                )
    if invariants_before is not None and settings["inlet_invariants"] != invariants_before:
        raise RuntimeError("Turbulence intensity or hydraulic diameter changed")


def set_branch_settings(
    solver: Any,
    *,
    full_mixture: bool,
    velocity: float,
    momentum_urf: float,
) -> dict[str, Any]:
    # These are live-verified 2025 R2 paths.  The equations object is reacquired
    # for the single dependency-sensitive update, and the boundary object is
    # reacquired for every phase write.
    solver.settings.solution.controls.under_relaxation.set_state({"mom": momentum_urf})
    solver.settings.solution.controls.equations.set_state(
        {"mp": full_mixture, "drift": full_mixture}
    )
    for zone in INLET_ZONES:
        for phase in INLET_PHASES:
            bc = solver.settings.setup.boundary_conditions.velocity_inlet
            bc[zone].phase[phase].momentum.velocity_magnitude.set_state(
                {"option": "value", "value": velocity}
            )
    return state_readback(solver)


def configure_autosave(solver: Any, root: str) -> dict[str, Any]:
    state = {
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
    solver.settings.file.auto_save.set_state(state)
    return safe_get_state(solver.settings.file.auto_save, "native autosave")


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


def read_case(solver: Any, path: str) -> None:
    solver.settings.file.read_case(file_name=path)


def restore_pair(solver: Any, case_path: str) -> None:
    """Restore a verified native endpoint before continuing orchestration."""

    data_file = data_path(case_path)
    if not remote_file_exists(solver, case_path) or not remote_file_exists(solver, data_file):
        raise RuntimeError(f"Cannot restore incomplete native endpoint: {case_path}")
    solver.settings.file.read_case_data(file_name=case_path)


def render_native_stage_journal(
    *,
    branch: str,
    stage: str,
    iterations: int,
    checkpoint_case: str,
    transcript: str,
    residual_export: str,
) -> str:
    return "\n".join(
        [
            "; USER-AUTHORIZED 03A Stage-3 fixed-3000 native stage",
            f"; branch: {branch}",
            f"; stage: {stage}",
            f"; native iterations: {iterations}",
            "; Fluent owns solve, transcript, endpoint write, and autosave.",
            "/file/confirm-overwrite? no",
            f'/file/start-transcript "{transcript}"',
            "/solve/monitors/residual/print? yes",
            "/solve/monitors/residual/plot? no",
            "/solve/monitors/residual/n-save 6000",
            f"/solve/iterate {iterations}",
            f'/file/write-case-data "{checkpoint_case}"',
            f'/plot/residuals-set/plot-to-file "{residual_export}"',
            "/file/stop-transcript",
            "; Fluent-native stage journal finished; Fluent remains open.",
            "",
        ]
    )


def reconnect(events: EventLog, *, reason: str) -> Any:
    events.emit("reconnect_attempt", reason=reason)
    solver = connect(server_id=SERVER_ID)
    events.emit("reconnected", reason=reason)
    return solver


def stop_active_transcript(solver: Any) -> None:
    """Close an inherited native transcript before starting a new stage."""

    try:
        solver.scheme.eval('(ti-menu-load-string "/file/stop-transcript")')
    except Exception:
        # Fluent may have no active native transcript.  That is harmless; the
        # new stage journal owns its own uniquely named transcript.
        pass


def snapshot_summary(solver: Any) -> dict[str, Any]:
    try:
        snapshot = collect_snapshot(solver, monitor_sets=("residual",))
        return {
            "timestamp_utc": snapshot.get("timestamp_utc"),
            "health": snapshot.get("health"),
            "iteration": snapshot.get("progress", {}).get("iteration"),
            "highest_iteration": snapshot.get("monitors", {})
            .get("residual", {})
            .get("highest_iteration"),
            "residuals": snapshot.get("monitors", {})
            .get("residual", {})
            .get("last_values"),
            "read_errors": snapshot.get("read_errors"),
        }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def idle_preflight(solver: Any, events: EventLog) -> dict[str, Any]:
    """Require a healthy, observably quiescent Fluent session before mutation."""

    first = collect_snapshot(solver, monitor_sets=("residual",))
    time.sleep(IDLE_PREFLIGHT_WINDOW_SECONDS)
    second = collect_snapshot(solver, monitor_sets=("residual",))

    for label, snapshot in (("first", first), ("second", second)):
        health_text = " ".join(str(value) for value in snapshot.get("health", {}).values()).upper()
        if "SERVING" not in health_text:
            raise RuntimeError(
                f"Fluent idle preflight failed: {label} health is not SERVING: "
                f"{snapshot.get('health')!r}"
            )

    first_iteration = first.get("progress", {}).get("iteration")
    second_iteration = second.get("progress", {}).get("iteration")
    first_flow_time = first.get("runtime", {}).get("flow_time")
    second_flow_time = second.get("runtime", {}).get("flow_time")
    comparable = False
    if first_iteration is not None and second_iteration is not None:
        comparable = True
        if second_iteration != first_iteration:
            raise RuntimeError(
                "Fluent idle preflight failed: iteration changed from "
                f"{first_iteration!r} to {second_iteration!r}"
            )
    if first_flow_time is not None and second_flow_time is not None:
        comparable = True
        if second_flow_time != first_flow_time:
            raise RuntimeError(
                "Fluent idle preflight failed: flow time changed from "
                f"{first_flow_time!r} to {second_flow_time!r}"
            )
    if not comparable:
        raise RuntimeError(
            "Fluent idle preflight failed: no comparable iteration or flow-time "
            "readback was available"
        )

    result = {
        "window_seconds": IDLE_PREFLIGHT_WINDOW_SECONDS,
        "first": first,
        "second": second,
        "observed_quiescent": True,
    }
    events.emit(
        "server_idle_preflight_passed",
        window_seconds=IDLE_PREFLIGHT_WINDOW_SECONDS,
        iteration=second_iteration,
        flow_time=second_flow_time,
    )
    return result


def wait_for_pair(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    case_path: str,
    timeout_seconds: float = PAIR_WAIT_SECONDS,
) -> Any:
    """Wait read-only for the native journal's durable pair.

    This loop never issues a solve, save, reload, or retry.  If the client RPC
    failed while Fluent continued natively, the pair is the authoritative
    completion proof and prevents an uncertain block from being repeated.
    """

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
            )
            try:
                probe = reconnect(events, reason=f"pair_wait:{branch}:{stage}")
            except Exception as reconnect_error:
                events.emit(
                    "reconnect_failed",
                    branch=branch,
                    stage=stage,
                    error=repr(reconnect_error),
                )
        time.sleep(10.0)
    raise TimeoutError(
        f"Timed out waiting for native paired endpoint {case_path} and {data_file}"
    )


def is_terminal_native_error(exc: Exception) -> bool:
    """Identify a Fluent journal error that has returned control to the client.

    A bare ``Error Object: ()`` is the error shape observed from this Fluent
    2025 R2 session when a native journal aborts.  It is distinct from a gRPC
    transport loss, for which Fluent may still be solving and the paired
    endpoint must be awaited before any next-branch action.
    """

    text = str(exc).lower()
    transport_markers = (
        "stream removed",
        "recvmsg",
        "no route to host",
        "failed to connect to all addresses",
        "connection reset",
        "grpc",
        "transport",
        "timed out waiting for native paired endpoint",
    )
    if any(marker in text for marker in transport_markers):
        return False
    return "error object" in text or any(
        marker in text
        for marker in (
            "invalid path",
            "unknown command",
            "inactive",
            "floating-point",
            "floating point",
            "fpe",
            "amg",
            "non-finite",
            "nonfinite",
            "solver termination",
        )
    )


def run_native_stage(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    stage: str,
    root: str,
    stamp: str,
    ledger: RunLedger,
) -> Any:
    case_path = win(root, f"03A-stage3-{branch}-{stage}-end-{stamp}.cas.h5")
    transcript = win(root, f"03A-stage3-{branch}-{stage}-{stamp}.trn")
    residual_export = win(root, f"03A-stage3-{branch}-{stage}-{stamp}-residuals.out")
    remote_journal = win(root, f"03A-stage3-{branch}-{stage}-{stamp}.jou")
    local_journal = ledger.run_dir / f"{branch}-{stage}.jou"
    journal = render_native_stage_journal(
        branch=branch,
        stage=stage,
        iterations=STAGE_ITERATIONS,
        checkpoint_case=case_path,
        transcript=transcript,
        residual_export=residual_export,
    )
    recorded = ledger.stage(branch, stage)
    if recorded is not None:
        if recorded.get("case_path") != case_path:
            raise RuntimeError(f"Resume ledger endpoint mismatch for {branch}/{stage}")
        if recorded.get("status") == "complete":
            restore_pair(solver, case_path)
            events.emit("stage_restored", branch=branch, stage=stage, case=case_path)
            return solver
        if recorded.get("status") == "submitted":
            events.emit("stage_resume_reconcile", branch=branch, stage=stage, case=case_path)
            solver = wait_for_pair(solver, events, branch=branch, stage=stage, case_path=case_path)
            ledger.stage_complete(branch, stage, case_path=case_path)
            restore_pair(solver, case_path)
            return solver
        raise RuntimeError(f"Unsupported resume stage state: {recorded!r}")
    pause_file = ledger.run_dir / "PAUSE"
    if pause_file.exists():
        raise QueuePaused(
            f"Queue pause requested by {pause_file}; no new native stage was submitted"
        )
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    # Persist intent before any remote execution.  A restart may wait for this
    # endpoint but must never submit the same 3,000-iteration block twice.
    ledger.stage_submitted(branch, stage, case_path=case_path)
    stop_active_transcript(solver)
    write_remote_journal(solver, remote_journal, journal)
    events.emit(
        "native_stage_submit",
        branch=branch,
        stage=stage,
        iterations=STAGE_ITERATIONS,
        journal=remote_journal,
        local_journal=str(local_journal),
        checkpoint_case=case_path,
        checkpoint_data=data_path(case_path),
        transcript=transcript,
        residual_export=residual_export,
    )
    native_error: str | None = None
    try:
        solver.settings.file.read_journal(file_name_list=[remote_journal])
    except Exception as exc:
        native_error = repr(exc)
        events.emit(
            "native_stage_client_error",
            branch=branch,
            stage=stage,
            error=native_error,
            note="Fluent-native journal may still be running; waiting for paired endpoint without repeating it.",
        )
        if is_terminal_native_error(exc):
            events.emit(
                "native_stage_terminal_error",
                branch=branch,
                stage=stage,
                error=native_error,
                note="Stage returned a Fluent journal error; skip the remainder of this branch.",
            )
            raise TerminalNativeStageError(
                branch=branch,
                stage=stage,
                journal_error=exc,
            ) from exc
        try:
            solver = reconnect(events, reason=f"native_stage_error:{branch}:{stage}")
        except Exception as reconnect_error:
            events.emit(
                "native_stage_reconnect_unavailable",
                branch=branch,
                stage=stage,
                error=repr(reconnect_error),
            )
    solver = wait_for_pair(
        solver,
        events,
        branch=branch,
        stage=stage,
        case_path=case_path,
    )
    ledger.stage_complete(branch, stage, case_path=case_path)
    restore_pair(solver, case_path)
    events.emit(
        "stage_complete",
        branch=branch,
        stage=stage,
        iterations=STAGE_ITERATIONS,
        policy="USER_FIXED_3000_PER_STAGE",
        native_client_error=native_error,
        case=case_path,
        data=data_path(case_path),
    )
    return solver


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
    full_mixture: bool,
    stamp: str,
    ledger: RunLedger,
) -> Any:
    transition_case = win(root, f"03A-stage3-{branch}-{to_stage}-transition-{stamp}.cas.h5")
    recorded = ledger.transition(branch, to_stage)
    if recorded is not None:
        if recorded.get("case_path") != transition_case or recorded.get("status") != "complete":
            raise RuntimeError(f"Unsupported resume transition state for {branch}/{to_stage}: {recorded!r}")
        restore_pair(solver, transition_case)
        events.emit("transition_restored", branch=branch, to_stage=to_stage, checkpoint_after=transition_case)
        return solver
    before = state_readback(solver)
    pre_case = win(root, f"03A-stage3-{branch}-{from_stage}-pre-transition-{stamp}.cas.h5")
    write_pair(solver, pre_case)
    after = set_branch_settings(
        solver,
        full_mixture=full_mixture,
        velocity=velocity,
        momentum_urf=momentum_urf,
    )
    verify_settings(
        after,
        full_mixture=full_mixture,
        velocity=velocity,
        momentum_urf=momentum_urf,
        invariants_before=before["inlet_invariants"],
    )
    write_pair(solver, transition_case)
    ledger.transition_complete(branch, to_stage, case_path=transition_case)
    events.emit(
        "transition_complete",
        branch=branch,
        from_stage=from_stage,
        to_stage=to_stage,
        reason="USER_FIXED_3000_PER_STAGE",
        checkpoint_before=pre_case,
        checkpoint_before_data=data_path(pre_case),
        checkpoint_after=transition_case,
        checkpoint_after_data=data_path(transition_case),
        settings_before=before,
        settings_after=after,
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
    velocity: float,
    full_mixture: bool,
    startup_label: str,
    stamp: str,
    ledger: RunLedger,
) -> Any:
    if not remote_file_exists(solver, P0_REMOTE):
        raise FileNotFoundError(f"Released P0 is unavailable: {P0_REMOTE}")
    ensure_remote_directory(solver, root)
    local_p0 = win(root, f"03A-stage3-{branch}-P0-local-{stamp}.cas.h5")
    preinit = win(root, f"03A-stage3-{branch}-{startup_label}-preinit-{stamp}.cas.h5")
    prepared = ledger.prepared(branch)
    if prepared is not None:
        start_case = win(root, f"03A-stage3-{branch}-hybrid-initialized-iter000000-{stamp}.cas.h5")
        if prepared.get("root") != root or prepared.get("start_case") != start_case:
            raise RuntimeError(f"Resume ledger preparation mismatch for {branch}")
        restore_pair(solver, start_case)
        configure_autosave(solver, root)
        events.emit("branch_preparation_restored", branch=branch, start_case=start_case)
        return solver
    events.emit(
        "p0_release_verified",
        branch=branch,
        p0=P0_REMOTE,
        p0_sha256=P0_SHA256,
        local_root=root,
    )
    read_case(solver, P0_REMOTE)
    write_case(solver, local_p0)
    read_case(solver, local_p0)
    parent_state = state_readback(solver)
    settings = set_branch_settings(
        solver,
        full_mixture=full_mixture,
        velocity=velocity,
        momentum_urf=momentum_urf,
    )
    verify_settings(
        settings,
        full_mixture=full_mixture,
        velocity=velocity,
        momentum_urf=momentum_urf,
        invariants_before=parent_state["inlet_invariants"],
    )
    write_case(solver, preinit)
    read_case(solver, preinit)
    settings = state_readback(solver)
    verify_settings(
        settings,
        full_mixture=full_mixture,
        velocity=velocity,
        momentum_urf=momentum_urf,
        invariants_before=parent_state["inlet_invariants"],
    )
    autosave = configure_autosave(solver, root)
    events.emit(
        "preinit_verified",
        branch=branch,
        startup_label=startup_label,
        local_p0=local_p0,
        preinit=preinit,
        settings=settings,
        autosave=autosave,
        hybrid_initialize_count_before=0,
    )
    solver.settings.solution.initialization.hybrid_initialize()
    start_case = win(root, f"03A-stage3-{branch}-hybrid-initialized-iter000000-{stamp}.cas.h5")
    write_pair(solver, start_case)
    ledger.branch_prepared(branch, root=root, start_case=start_case)
    events.emit(
        "hybrid_initialized_once",
        branch=branch,
        start_case=start_case,
        start_data=data_path(start_case),
        settings=state_readback(solver),
    )
    return solver


def run_schedule_b(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    momentum_urf: float,
    stamp: str,
    ledger: RunLedger,
) -> Any:
    # The run directory is created before any P0-derived local write.
    root = win(REMOTE_QUEUE_ROOT, f"{branch}\\run-{stamp}")
    solver = prepare_branch(
        solver,
        events,
        branch=branch,
        root=root,
        momentum_urf=momentum_urf,
        velocity=VELOCITY_100,
        full_mixture=False,
        startup_label="B-M1-S0",
        stamp=stamp,
        ledger=ledger,
    )
    solver = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="carrier-100pct",
        root=root,
        stamp=stamp,
        ledger=ledger,
    )
    solver = transition(
        solver,
        events,
        branch=branch,
        from_stage="carrier-100pct",
        to_stage="full-mixture-100pct",
        root=root,
        velocity=VELOCITY_100,
        momentum_urf=momentum_urf,
        full_mixture=True,
        stamp=stamp,
        ledger=ledger,
    )
    solver = run_native_stage(
        solver,
        events,
        branch=branch,
        stage="full-mixture-100pct",
        root=root,
        stamp=stamp,
        ledger=ledger,
    )
    events.emit("branch_complete", branch=branch, final_stage="full-mixture-100pct")
    return solver


def run_f11(
    solver: Any,
    events: EventLog,
    *,
    stamp: str,
    ledger: RunLedger,
) -> Any:
    branch = "F11"
    root = win(REMOTE_QUEUE_ROOT, f"{branch}\\run-{stamp}")
    solver = prepare_branch(
        solver,
        events,
        branch=branch,
        root=root,
        momentum_urf=0.3,
        velocity=VELOCITY_10,
        full_mixture=True,
        startup_label="C-M0-S1",
        stamp=stamp,
        ledger=ledger,
    )
    solver = run_native_stage(solver, events, branch=branch, stage="full-mixture-10pct", root=root, stamp=stamp, ledger=ledger)
    solver = transition(
        solver, events, branch=branch, from_stage="full-mixture-10pct", to_stage="full-mixture-20pct",
        root=root, velocity=VELOCITY_20, momentum_urf=0.3, full_mixture=True, stamp=stamp, ledger=ledger,
    )
    solver = run_native_stage(solver, events, branch=branch, stage="full-mixture-20pct", root=root, stamp=stamp, ledger=ledger)
    solver = transition(
        solver, events, branch=branch, from_stage="full-mixture-20pct", to_stage="full-mixture-40pct",
        root=root, velocity=VELOCITY_40, momentum_urf=0.3, full_mixture=True, stamp=stamp, ledger=ledger,
    )
    solver = run_native_stage(solver, events, branch=branch, stage="full-mixture-40pct", root=root, stamp=stamp, ledger=ledger)
    solver = transition(
        solver, events, branch=branch, from_stage="full-mixture-40pct", to_stage="full-mixture-80pct",
        root=root, velocity=VELOCITY_80, momentum_urf=0.3, full_mixture=True, stamp=stamp, ledger=ledger,
    )
    solver = run_native_stage(solver, events, branch=branch, stage="full-mixture-80pct", root=root, stamp=stamp, ledger=ledger)
    solver = transition(
        solver, events, branch=branch, from_stage="full-mixture-80pct", to_stage="full-mixture-100pct",
        root=root, velocity=VELOCITY_100, momentum_urf=0.3, full_mixture=True, stamp=stamp, ledger=ledger,
    )
    solver = run_native_stage(solver, events, branch=branch, stage="full-mixture-100pct", root=root, stamp=stamp, ledger=ledger)
    events.emit("branch_complete", branch=branch, final_stage="full-mixture-100pct")
    return solver


def run_f05(
    solver: Any,
    events: EventLog,
    *,
    stamp: str,
    ledger: RunLedger,
) -> Any:
    branch = "F05"
    root = win(REMOTE_QUEUE_ROOT, f"{branch}\\run-{stamp}")
    solver = prepare_branch(
        solver, events, branch=branch, root=root, momentum_urf=0.3,
        velocity=VELOCITY_100, full_mixture=True, startup_label="A-M0-S0", stamp=stamp, ledger=ledger,
    )
    solver = run_native_stage(solver, events, branch=branch, stage="full-mixture-100pct", root=root, stamp=stamp, ledger=ledger)
    events.emit("branch_complete", branch=branch, final_stage="full-mixture-100pct")
    return solver


def is_hard_numerical_failure(exc: Exception) -> bool:
    text = " ".join(
        (
            str(exc),
            exc.journal_error if isinstance(exc, TerminalNativeStageError) else "",
        )
    ).lower()
    return any(
        token in text
        for token in (
            "floating-point",
            "floating point",
            "fpe",
            "amg",
            "non-finite",
            "nonfinite",
            "solver termination",
        )
    )


def guarded_branch(
    solver: Any,
    events: EventLog,
    *,
    branch: str,
    runner: Callable[..., Any],
    stamp: str,
    ledger: RunLedger | None = None,
) -> tuple[Any, bool, bool]:
    events.emit("branch_start", branch=branch)
    if ledger is not None and ledger.branch_status(branch) == "skipped":
        events.emit(
            "branch_resume_skipped",
            branch=branch,
            reason="persisted_terminal_native_stage_failure",
        )
        return solver, False, True
    try:
        return runner(solver, events, stamp=stamp), True, True
    except Exception as exc:
        if isinstance(exc, QueuePaused):
            events.emit("queue_paused", branch=branch, reason=str(exc))
            return solver, False, False
        hard = is_hard_numerical_failure(exc)
        terminal_native_stage = isinstance(exc, TerminalNativeStageError)
        unresolved_transport = isinstance(exc, TimeoutError) or (
            "timed out waiting for native paired endpoint" in str(exc).lower()
        )
        if hard:
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
            note=(
                "No uncertain native stage is repeated. A terminal native stage is "
                "eligible for branch skip only after Fluent reconnects."
            ),
        )
        if unresolved_transport:
            events.emit(
                "queue_blocked",
                after_branch=branch,
                reason="Could not establish a durable endpoint or safe Fluent idle state after transport loss",
            )
            return solver, False, False

        # Only a Fluent-returned terminal stage (including an FPE-like solver
        # termination) is eligible for automatic branch skipping.  Setup,
        # path, or verification errors need operator review rather than silently
        # changing the experiment by moving on to a different branch.
        if not terminal_native_stage:
            events.emit(
                "queue_blocked",
                after_branch=branch,
                reason="Non-terminal setup/execution failure requires review; next branch was not started",
            )
            return solver, False, False

        reconnect_error: Exception | None = None
        for attempt in range(1, SKIP_RECONNECT_ATTEMPTS + 1):
            try:
                solver = reconnect(
                    events,
                    reason=f"after_terminal_stage_skip:{branch}:attempt-{attempt}",
                )
                if ledger is not None:
                    ledger.branch_skipped(
                        branch,
                        stage=exc.stage,
                        reason="TERMINAL_NATIVE_STAGE_FAILURE",
                        numerical_failure=hard,
                    )
                events.emit(
                    "branch_skipped",
                    branch=branch,
                    reason="TERMINAL_NATIVE_STAGE",
                    numerical_failure=hard,
                    next_branch_policy="LOAD_PRISTINE_P0_INDEPENDENTLY",
                    reconnect_attempt=attempt,
                )
                return solver, False, True
            except Exception as caught:
                reconnect_error = caught
                events.emit(
                    "reconnect_failed",
                    branch=branch,
                    attempt=attempt,
                    error=repr(caught),
                )
                if attempt < SKIP_RECONNECT_ATTEMPTS:
                    time.sleep(SKIP_RECONNECT_DELAY_SECONDS)
        events.emit(
            "queue_blocked",
            branch=branch,
            reason="Terminal native stage could not reconnect to Fluent; do not start the next branch",
            numerical_failure=hard,
            error=repr(reconnect_error),
        )
        return solver, False, False


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or safely resume the fixed-3000 Stage-3 queue.")
    parser.add_argument(
        "--resume-run-dir",
        type=Path,
        help="Existing local campaign directory containing native-fixed-3000-resume-state.json.",
    )
    args = parser.parse_args()
    if args.resume_run_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output_dir = PROJECT_ROOT / "output" / "03A-stage3" / "override-fixed3000-native-server2" / stamp
        ledger = RunLedger.create(output_dir, stamp=stamp)
        resumed = False
    else:
        output_dir = args.resume_run_dir.expanduser().resolve()
        ledger = RunLedger.load(output_dir)
        stamp = ledger.stamp
        resumed = True
    events = EventLog(output_dir / "native-fixed-3000-events.jsonl", stamp)
    plan_path = output_dir / "native-fixed-3000-queue-plan.jou"
    if not resumed:
        plan_path.write_text(
        "\n".join(
            [
                "; USER-AUTHORIZED 03A Stage-3 fixed-3000 restart plan",
                "; Queue: F02 -> F04 -> F11 -> F06 -> F05",
                "; Fluent-native stage journals are generated and submitted one at a time.",
                "; Every stage writes a named paired case/data endpoint before transition.",
                "; F02: carrier-100pct 3000 -> full-mixture-100pct 3000",
                "; F04: carrier-100pct 3000 -> full-mixture-100pct 3000",
                "; F11: full-mixture 10/20/40/80/100pct, 3000 each",
                "; F06: carrier-100pct 3000 -> full-mixture-100pct 3000",
                "; F05: full-mixture-100pct 3000",
                "; Gate decisions are disabled only by the explicit user fixed-3000 override.",
                "; P0 remains read-only; all run artifacts remain under local Fluent storage.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    events.emit(
        "queue_start",
        server_id=SERVER_ID,
        queue=("F02", "F04", "F11", "F06", "F05"),
        policy="USER_FIXED_3000_PER_STAGE_NATIVE_FLUENT",
        p0=P0_REMOTE,
        p0_sha256=P0_SHA256,
        plan=str(plan_path),
        resumed=resumed,
    )
    solver = connect(server_id=SERVER_ID)
    if not solver.is_active():
        raise RuntimeError("Fluent server 2 is not active")
    version = str(solver.get_fluent_version())
    if "2025 R2" not in version:
        raise RuntimeError(f"Unexpected Fluent version: {version!r}")
    idle_state = idle_preflight(solver, events)
    events.emit(
        "server_preflight",
        fluent_version=version,
        initial_snapshot=idle_state["first"],
        final_snapshot=idle_state["second"],
    )

    outcomes: list[tuple[str, bool]] = []

    solver, ok, can_continue = guarded_branch(
        solver, events, branch="F02", runner=lambda s, e, stamp: run_schedule_b(s, e, branch="F02", momentum_urf=0.7, stamp=stamp, ledger=ledger), stamp=stamp, ledger=ledger
    )
    outcomes.append(("F02", ok))
    if not can_continue:
        return 2
    solver, ok, can_continue = guarded_branch(
        solver, events, branch="F04", runner=lambda s, e, stamp: run_schedule_b(s, e, branch="F04", momentum_urf=0.5, stamp=stamp, ledger=ledger), stamp=stamp, ledger=ledger
    )
    outcomes.append(("F04", ok))
    if not can_continue:
        return 2
    solver, ok, can_continue = guarded_branch(solver, events, branch="F11", runner=lambda s, e, stamp: run_f11(s, e, stamp=stamp, ledger=ledger), stamp=stamp, ledger=ledger)
    outcomes.append(("F11", ok))
    if not can_continue:
        return 2
    solver, ok, can_continue = guarded_branch(
        solver, events, branch="F06", runner=lambda s, e, stamp: run_schedule_b(s, e, branch="F06", momentum_urf=0.3, stamp=stamp, ledger=ledger), stamp=stamp, ledger=ledger
    )
    outcomes.append(("F06", ok))
    if not can_continue:
        return 2
    solver, ok, can_continue = guarded_branch(solver, events, branch="F05", runner=lambda s, e, stamp: run_f05(s, e, stamp=stamp, ledger=ledger), stamp=stamp, ledger=ledger)
    outcomes.append(("F05", ok))
    if not can_continue:
        return 2
    completed = [branch for branch, success in outcomes if success]
    skipped = [branch for branch, success in outcomes if not success]
    if skipped:
        events.emit(
            "queue_finished_with_skips",
            completed_branches=completed,
            skipped_branches=skipped,
            all_branches_visited=True,
        )
        return 3
    events.emit("queue_complete", all_branches_terminal=True, all_branches_successful=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

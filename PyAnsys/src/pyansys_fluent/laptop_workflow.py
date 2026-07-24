"""Laptop-owned control state from a Markdown plan to result artifacts.

This module deliberately does not parse setup intent or issue Fluent setup
commands.  The agent reads the Markdown plan, works directly through PyFluent
or TUI, and records only proved progress here.  The only host-side handoff is a
strict :class:`RunRequest`.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

from pyansys_fluent.agent_ledger import AgentLedger
from pyansys_fluent.bridge import (
    ConnectionDocumentError,
    read_latest_connection,
)
from pyansys_fluent.run_worker import RunRequest, submit_run_request


WORKFLOW_SCHEMA_VERSION = 1
ANALYSIS_SCHEMA_VERSION = 1
RESULT_SCHEMA_VERSION = 1
_FORBIDDEN_KEY_PARTS = ("password", "secret", "credential")


class LaptopWorkflowError(RuntimeError):
    """Raised when a workflow transition is unsafe or out of order."""


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_no_credential_fields(value: Any, *, location: str = "workflow") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if any(part in key_text for part in _FORBIDDEN_KEY_PARTS):
                raise ValueError(
                    f"{location} must not contain credential field {key!r}"
                )
            _assert_no_credential_fields(child, location=f"{location}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_no_credential_fields(
                child, location=f"{location}[{index}]"
            )


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _assert_no_credential_fields(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        try:
            os.chmod(temporary, 0o600)
        except OSError:
            pass
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(dict(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    _assert_no_credential_fields(payload)
    return payload


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.close(descriptor)
        except OSError:
            pass
        temporary.unlink(missing_ok=True)
        raise


class LaptopWorkflow:
    """Persistent laptop-side state machine with explicit verification gates."""

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).expanduser().resolve()
        self.state_path = self.workspace / "workflow.json"
        self.ledger_path = self.workspace / "ledger.json"
        self.analysis_path = self.workspace / "analysis_manifest.json"
        self.results_dir = self.workspace / "results"
        self.ledger = AgentLedger(self.ledger_path)

    def create(
        self,
        *,
        job_id: str,
        setup_plan_path: str | Path,
        connection_generation: int | None = None,
        analysis_tasks: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Register an arbitrary Markdown plan without interpreting its content."""

        if self.state_path.exists():
            raise FileExistsError(
                f"Laptop workflow already exists: {self.state_path}"
            )
        job_id = job_id.strip()
        if not job_id:
            raise ValueError("job_id must be non-empty")
        plan = Path(setup_plan_path).expanduser().resolve()
        if not plan.is_file():
            raise FileNotFoundError(f"Setup plan does not exist: {plan}")
        if plan.suffix.lower() not in {".md", ".mdx"}:
            raise ValueError("setup_plan_path must be Markdown")
        self.workspace.mkdir(parents=True, exist_ok=True)
        now = _utc_now()
        self.ledger.create(
            job_id=job_id,
            phase="case_build",
            setup_plan_path=str(plan),
            connection_generation=connection_generation,
            analysis_manifest_path=str(self.analysis_path),
        )
        analysis = {
            "schema_version": ANALYSIS_SCHEMA_VERSION,
            "job_id": job_id,
            "status": "pending",
            "tasks": {},
            "created_at": now,
            "updated_at": now,
        }
        _atomic_write_json(self.analysis_path, analysis)
        state = {
            "schema_version": WORKFLOW_SCHEMA_VERSION,
            "job_id": job_id,
            "setup_plan_path": str(plan),
            "setup_plan_sha256": _sha256(plan),
            "status": "case_build",
            "ledger_path": str(self.ledger_path),
            "analysis_manifest_path": str(self.analysis_path),
            "active_request": None,
            "receipt_history": [],
            "pending_checkpoint": None,
            "accepted_run_checkpoint": None,
            "human_review_reason": None,
            "result_manifest_path": None,
            "created_at": now,
            "updated_at": now,
        }
        self._write_state(state)
        if analysis_tasks:
            self.add_analysis_tasks(analysis_tasks)
        return self.read()

    def read(self) -> dict[str, Any]:
        state = _read_json(self.state_path)
        if state.get("schema_version") != WORKFLOW_SCHEMA_VERSION:
            raise ValueError("Unsupported laptop workflow schema_version")
        return state

    def observe_connection_generation(self, generation: int) -> dict[str, Any]:
        """Record a newly verified laptop connection without caching its secret."""

        self.ledger.observe_connection_generation(generation)
        return self.read()

    def start_step(
        self, step: str, *, safe_to_retry: bool = False
    ) -> dict[str, Any]:
        self._require_status("case_build")
        self.assert_plan_unchanged()
        self.ledger.start_step(step, safe_to_retry=safe_to_retry)
        return self.read()

    def complete_step(self, step: str) -> dict[str, Any]:
        self._require_status("case_build")
        self.assert_plan_unchanged()
        self.ledger.complete_step(step)
        return self.read()

    def accept_case_checkpoint(self, case_path: str) -> dict[str, Any]:
        """Record a setup case only after the agent has read it back."""

        self._require_status("case_build")
        self.assert_plan_unchanged()
        self.ledger.accept_checkpoint(case_path)
        return self.read()

    def mark_case_ready(self) -> dict[str, Any]:
        self._require_status("case_build")
        self.assert_plan_unchanged()
        ledger = self.ledger.read()
        if ledger.get("current_step") is not None:
            raise LaptopWorkflowError("A setup step is still active")
        if not ledger.get("latest_case_checkpoint"):
            raise LaptopWorkflowError(
                "No agent-accepted case checkpoint is recorded"
            )
        self.ledger.set_phase("run", status="case_ready")
        state = self.read()
        state["status"] = "case_ready"
        self._write_state(state)
        return self.read()

    def record_setup_connection_loss(self, *, generation: int) -> dict[str, Any]:
        """Record loss during direct laptop-controlled case construction."""

        self._require_status("case_build")
        ledger = self.ledger.connection_lost(generation=generation)
        state = self.read()
        state["status"] = "setup_recovery_required"
        state["pending_checkpoint"] = (
            {
                "case_path": ledger["latest_case_checkpoint"],
                "data_path": ledger["latest_data_checkpoint"],
                "interrupted_step": ledger["current_step"],
                "safe_to_retry": ledger["current_step_safe_to_retry"],
            }
            if ledger.get("latest_case_checkpoint")
            else None
        )
        self._write_state(state)
        return self.read()

    def verify_setup_recovery(self, *, generation: int) -> dict[str, Any]:
        """Continue case building after the agent proves the restored case."""

        self._require_status("setup_recovery_required")
        state = self.read()
        pending = state.get("pending_checkpoint")
        if not pending:
            raise LaptopWorkflowError(
                "No accepted setup checkpoint is available for recovery"
            )
        if pending.get("interrupted_step") and not pending.get("safe_to_retry"):
            raise LaptopWorkflowError(
                "Interrupted setup step is not explicitly safe to retry; "
                "require human review"
            )
        self.ledger.recovered(
            generation=generation,
            restored_state_verified=True,
        )
        state["status"] = "case_build"
        state["pending_checkpoint"] = None
        self._write_state(state)
        return self.read()

    def submit(
        self,
        request: RunRequest,
        *,
        bridge_dir: str | Path,
        max_connection_age_seconds: float = 45.0,
    ) -> Path:
        """Submit an explicit initialize or resume request after authority checks."""

        state = self.read()
        ledger = self.ledger.read()
        self.assert_plan_unchanged()
        if state.get("active_request") is not None:
            raise LaptopWorkflowError("Another run request is still active")
        if request.mode == "initialize":
            self._require_status("case_ready", state=state)
            if request.source_case != ledger.get("latest_case_checkpoint"):
                raise LaptopWorkflowError(
                    "Initialize source_case is not the agent-accepted case"
                )
            current_generation = ledger.get("connection_generation")
            if (
                current_generation is not None
                and request.expected_generation < current_generation
            ):
                raise LaptopWorkflowError(
                    "Initialize request uses an older Fluent generation"
                )
        else:
            self._require_status("recovery_verified", state=state)
            accepted = state.get("accepted_run_checkpoint") or {}
            if (
                request.source_case != accepted.get("case_path")
                or request.source_data != accepted.get("data_path")
                or request.completed_iterations != accepted.get("iteration")
            ):
                raise LaptopWorkflowError(
                    "Resume request does not match the explicitly verified pair"
                )
            if request.expected_generation != accepted.get(
                "verified_generation"
            ):
                raise LaptopWorkflowError(
                    "Resume request generation is not the verified generation"
                )
        bridge = Path(bridge_dir).expanduser()
        if not bridge.is_absolute():
            raise ValueError("FLUENT_BRIDGE_DIR must be an absolute path")
        try:
            connection = read_latest_connection(
                bridge,
                max_age_seconds=max_connection_age_seconds,
                min_generation=request.expected_generation,
            )
        except (OSError, json.JSONDecodeError, ConnectionDocumentError) as exc:
            raise LaptopWorkflowError(
                "No fresh running Fluent connection matches the request"
            ) from exc
        if connection["generation"] != request.expected_generation:
            raise LaptopWorkflowError(
                "Run request is pinned to a stale Fluent generation"
            )
        destination = submit_run_request(bridge, request)
        state["status"] = "run_requested"
        state["active_request"] = request.to_dict()
        self._write_state(state)
        self.ledger.observe_connection_generation(
            request.expected_generation
        )
        self.ledger.set_phase("run", status="run_requested")
        return destination

    def ingest_receipt(self, receipt_path: str | Path) -> dict[str, Any]:
        """Record a worker receipt without scientifically accepting its files."""

        state = self.read()
        self._require_status("run_requested", state=state)
        receipt_file = Path(receipt_path).expanduser().resolve()
        receipt = _read_json(receipt_file)
        active = state.get("active_request") or {}
        if receipt.get("job_id") != active.get("job_id"):
            raise LaptopWorkflowError("Receipt job_id does not match active request")
        if receipt.get("generation") != active.get("expected_generation"):
            raise LaptopWorkflowError(
                "Receipt generation does not match active request"
            )
        status = receipt.get("status")
        if status not in {"completed", "interrupted", "failed"}:
            raise LaptopWorkflowError(f"Unsupported receipt status: {status!r}")
        receipt_record = {
            "path": str(receipt_file),
            "sha256": _sha256(receipt_file),
            "job_id": receipt["job_id"],
            "generation": receipt["generation"],
            "status": status,
            "completed_iterations": receipt.get("completed_iterations"),
        }
        state["receipt_history"].append(receipt_record)
        state["active_request"] = None
        state["pending_checkpoint"] = deepcopy(receipt.get("last_checkpoint"))
        if status == "interrupted":
            state["status"] = "recovery_required"
            self.ledger.connection_lost(generation=int(receipt["generation"]))
        elif status == "completed":
            if not state["pending_checkpoint"]:
                raise LaptopWorkflowError(
                    "Completed receipt has no final case/data pair"
                )
            if receipt.get("final_data_path") != state[
                "pending_checkpoint"
            ].get("data_path"):
                raise LaptopWorkflowError(
                    "Completed receipt final_data_path does not match its pair"
                )
            state["status"] = "run_completed_pending_verification"
            self.ledger.set_phase(
                "run", status="run_completed_pending_verification"
            )
        else:
            state["status"] = "run_failed"
            self.ledger.set_phase("run", status="run_failed")
        self._write_state(state)
        return self.read()

    def verify_pending_checkpoint(
        self,
        *,
        case_path: str,
        data_path: str,
        generation: int,
    ) -> dict[str, Any]:
        """Accept a pair only after the agent loads and inspects it in Fluent."""

        state = self.read()
        if state["status"] not in {
            "recovery_required",
            "run_completed_pending_verification",
        }:
            raise LaptopWorkflowError(
                "There is no pending run checkpoint to verify"
            )
        pending = state.get("pending_checkpoint") or {}
        if (
            case_path != pending.get("case_path")
            or data_path != pending.get("data_path")
        ):
            raise LaptopWorkflowError(
                "Verified paths do not match the pending worker checkpoint"
            )
        if not pending.get("file_verified"):
            raise LaptopWorkflowError("Worker did not file-verify the pair")
        accepted = deepcopy(pending)
        accepted["verified_generation"] = generation
        accepted["agent_state_verified"] = True
        state["accepted_run_checkpoint"] = accepted
        state["pending_checkpoint"] = None
        if state["status"] == "recovery_required":
            self.ledger.recovered(
                generation=generation,
                restored_state_verified=True,
            )
            self.ledger.accept_checkpoint(case_path, data_path=data_path)
            self.ledger.set_phase("run", status="recovery_verified")
            state["status"] = "recovery_verified"
        else:
            ledger_generation = self.ledger.read().get("connection_generation")
            if ledger_generation is not None and generation < ledger_generation:
                raise LaptopWorkflowError(
                    "Verification generation cannot move backwards"
                )
            expected_generation = state["receipt_history"][-1]["generation"]
            if generation < expected_generation:
                raise LaptopWorkflowError(
                    "Completed run cannot be verified on an older generation"
                )
            self.ledger.observe_connection_generation(generation)
            self.ledger.accept_checkpoint(case_path, data_path=data_path)
            self.ledger.set_phase("analysis", status="analysis_ready")
            state["status"] = "analysis_ready"
        self._write_state(state)
        return self.read()

    def require_human_review(
        self, *, generation: int, reason: str
    ) -> dict[str, Any]:
        """Stop automatic transitions when restored state cannot be proved."""

        reason = reason.strip()
        if not reason:
            raise ValueError("human-review reason must be non-empty")
        state = self.read()
        if state["status"] in {"recovery_required", "setup_recovery_required"}:
            self.ledger.recovered(
                generation=generation,
                restored_state_verified=False,
            )
        elif state["status"] == "run_completed_pending_verification":
            self.ledger.observe_connection_generation(generation)
            self.ledger.set_phase("review", status="human_review")
        else:
            raise LaptopWorkflowError(
                "Human review can be required only for pending setup or run recovery"
            )
        state["status"] = "human_review"
        state["human_review_reason"] = reason
        self._write_state(state)
        return self.read()

    def add_analysis_tasks(self, names: Sequence[str]) -> dict[str, Any]:
        analysis = self.read_analysis()
        for raw_name in names:
            name = raw_name.strip()
            if not name:
                raise ValueError("analysis task names must be non-empty")
            if name in analysis["tasks"]:
                raise ValueError(f"Analysis task already exists: {name}")
            analysis["tasks"][name] = {
                "status": "pending",
                "artifacts": [],
                "notes": None,
                "updated_at": _utc_now(),
            }
        analysis["updated_at"] = _utc_now()
        _atomic_write_json(self.analysis_path, analysis)
        return self.read_analysis()

    def read_analysis(self) -> dict[str, Any]:
        analysis = _read_json(self.analysis_path)
        if analysis.get("schema_version") != ANALYSIS_SCHEMA_VERSION:
            raise ValueError("Unsupported analysis manifest schema_version")
        return analysis

    def start_analysis_task(self, name: str) -> dict[str, Any]:
        self._require_status("analysis_ready")
        analysis = self.read_analysis()
        task = self._analysis_task(analysis, name)
        if task["status"] not in {"pending", "interrupted", "failed"}:
            raise LaptopWorkflowError(
                f"Analysis task {name!r} cannot start from {task['status']!r}"
            )
        task["status"] = "running"
        task["updated_at"] = _utc_now()
        analysis["status"] = "running"
        analysis["updated_at"] = _utc_now()
        _atomic_write_json(self.analysis_path, analysis)
        return analysis

    def complete_analysis_task(
        self,
        name: str,
        *,
        artifacts: Sequence[str | Path],
        notes: str | None = None,
    ) -> dict[str, Any]:
        self._require_status("analysis_ready")
        analysis = self.read_analysis()
        task = self._analysis_task(analysis, name)
        if task["status"] != "running":
            raise LaptopWorkflowError(
                f"Analysis task {name!r} is not running"
            )
        if not artifacts:
            raise ValueError("At least one analysis artifact is required")
        records: list[dict[str, Any]] = []
        for artifact_value in artifacts:
            artifact = Path(artifact_value).expanduser().resolve()
            if not artifact.is_file():
                raise FileNotFoundError(f"Analysis artifact not found: {artifact}")
            records.append(
                {
                    "path": str(artifact),
                    "sha256": _sha256(artifact),
                    "size_bytes": artifact.stat().st_size,
                }
            )
        task.update(
            status="complete",
            artifacts=records,
            notes=notes,
            updated_at=_utc_now(),
        )
        statuses = {item["status"] for item in analysis["tasks"].values()}
        analysis["status"] = (
            "complete" if statuses and statuses == {"complete"} else "running"
        )
        analysis["updated_at"] = _utc_now()
        _atomic_write_json(self.analysis_path, analysis)
        return analysis

    def mark_analysis_task(
        self, name: str, *, status: str, notes: str
    ) -> dict[str, Any]:
        self._require_status("analysis_ready")
        if status not in {"interrupted", "failed"}:
            raise ValueError("status must be 'interrupted' or 'failed'")
        analysis = self.read_analysis()
        task = self._analysis_task(analysis, name)
        task.update(status=status, notes=notes, updated_at=_utc_now())
        analysis["status"] = status
        analysis["updated_at"] = _utc_now()
        _atomic_write_json(self.analysis_path, analysis)
        return analysis

    def finalize(self) -> tuple[Path, Path]:
        """Write the traceable result manifest after all explicit tasks finish."""

        self._require_status("analysis_ready")
        self.assert_plan_unchanged()
        state = self.read()
        analysis = self.read_analysis()
        tasks = analysis.get("tasks", {})
        if not tasks or any(task["status"] != "complete" for task in tasks.values()):
            raise LaptopWorkflowError(
                "Every explicit analysis task must be complete before finalization"
            )
        accepted = state.get("accepted_run_checkpoint")
        if not accepted:
            raise LaptopWorkflowError("No agent-verified final run pair exists")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.results_dir / "result_manifest.json"
        summary_path = self.results_dir / "result-summary.md"
        manifest = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "job_id": state["job_id"],
            "setup_plan": {
                "path": state["setup_plan_path"],
                "sha256": state["setup_plan_sha256"],
            },
            "final_checkpoint": accepted,
            "receipt_history": deepcopy(state["receipt_history"]),
            "analysis": analysis,
            "created_at": _utc_now(),
        }
        _atomic_write_json(manifest_path, manifest)
        lines = [
            f"# Result Package — {state['job_id']}",
            "",
            f"- Setup plan: `{state['setup_plan_path']}`",
            f"- Setup plan SHA-256: `{state['setup_plan_sha256']}`",
            f"- Final case: `{accepted['case_path']}`",
            f"- Final data: `{accepted['data_path']}`",
            f"- Completed iterations: `{accepted.get('iteration')}`",
            "",
            "## Analysis artifacts",
            "",
        ]
        for name, task in analysis["tasks"].items():
            lines.append(f"### {name}")
            lines.append("")
            for artifact in task["artifacts"]:
                lines.append(
                    f"- `{artifact['path']}` — SHA-256 `{artifact['sha256']}`"
                )
            if task.get("notes"):
                lines.append(f"- Notes: {task['notes']}")
            lines.append("")
        _atomic_write_text(summary_path, "\n".join(lines))
        state["status"] = "complete"
        state["result_manifest_path"] = str(manifest_path)
        self._write_state(state)
        self.ledger.set_phase("result", status="complete")
        return manifest_path, summary_path

    def assert_plan_unchanged(self) -> None:
        """Fail closed when the registered setup Markdown changes mid-workflow."""

        state = self.read()
        plan = Path(state["setup_plan_path"])
        if not plan.is_file() or _sha256(plan) != state["setup_plan_sha256"]:
            raise LaptopWorkflowError(
                "Setup plan changed after workflow creation; start a new "
                "workflow or restore the registered plan"
            )

    def _require_status(
        self, expected: str, *, state: Mapping[str, Any] | None = None
    ) -> None:
        current = dict(state) if state is not None else self.read()
        if current.get("status") != expected:
            raise LaptopWorkflowError(
                f"Workflow status is {current.get('status')!r}; "
                f"expected {expected!r}"
            )

    @staticmethod
    def _analysis_task(
        analysis: Mapping[str, Any], name: str
    ) -> dict[str, Any]:
        tasks = analysis.get("tasks")
        if not isinstance(tasks, dict) or name not in tasks:
            raise KeyError(f"Unknown analysis task: {name}")
        return tasks[name]

    def _write_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _utc_now()
        _atomic_write_json(self.state_path, state)

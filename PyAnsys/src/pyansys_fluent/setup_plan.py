"""Contracts for Git-synchronised, agent-authored Fluent build scripts.

Markdown is a request and an audit record.  It is intentionally *not* a DSL
that attempts to recreate a Fluent case.  For every plan, the planning agent
commits a case-specific Python build script.  That script contains the
ordered, live-validated PyFluent/TUI operations needed for the one case.

The local Fluent-PC runner pins the source case and script hashes, invokes the
script locally, and commits a small evidence record.  Fluent credentials and
case/data artifacts never leave that PC.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pyansys_fluent.autonomy.common import (
    ContractValidationError,
    canonical_digest,
    reject_unknown,
    require_absolute_path,
    require_mapping,
    require_schema_version,
    require_sha256,
    require_string,
)


SETUP_PLAN_SCHEMA_VERSION = 2


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _front_matter(markdown: str) -> dict[str, Any]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContractValidationError(
            "Setup plan must begin with a YAML front-matter delimiter (---)"
        )
    try:
        closing = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ContractValidationError(
            "Setup plan front matter is missing its closing delimiter"
        ) from exc
    try:
        import yaml
    except ModuleNotFoundError as exc:  # pragma: no cover - dependency contract
        raise RuntimeError("PyYAML is required to read Markdown setup plans") from exc
    payload = yaml.safe_load("\n".join(lines[1:closing]))
    return dict(require_mapping(payload, "setup plan front matter"))


@dataclass(frozen=True)
class MarkdownSetupPlan:
    """Pinned inputs for one agent-authored Fluent build script."""

    plan_id: str
    parent_case_path: str
    parent_case_sha256: str
    output_case_path: str
    build_script_path: str
    build_script_sha256: str
    schema_version: int = SETUP_PLAN_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            SETUP_PLAN_SCHEMA_VERSION,
            "MarkdownSetupPlan",
        )
        require_string(self.plan_id, "plan_id")
        require_absolute_path(self.parent_case_path, "parent_case_path")
        require_sha256(self.parent_case_sha256, "parent_case_sha256")
        require_absolute_path(self.output_case_path, "output_case_path")
        require_string(self.build_script_path, "build_script_path")
        require_sha256(self.build_script_sha256, "build_script_sha256")
        script_path = Path(self.build_script_path)
        if script_path.is_absolute() or ".." in script_path.parts:
            raise ContractValidationError(
                "build_script_path must be a repository-relative path without '..'"
            )
        if script_path.suffix != ".py":
            raise ContractValidationError("build_script_path must name a .py file")
        if not self.parent_case_path.lower().endswith(".cas.h5"):
            raise ContractValidationError("parent_case_path must end with .cas.h5")
        if not self.output_case_path.lower().endswith(".cas.h5"):
            raise ContractValidationError("output_case_path must end with .cas.h5")
        if self.parent_case_path == self.output_case_path:
            raise ContractValidationError(
                "output_case_path must differ from parent_case_path"
            )

    @property
    def digest(self) -> str:
        return canonical_digest(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "plan_id": self.plan_id,
            "parent_case_path": self.parent_case_path,
            "parent_case_sha256": self.parent_case_sha256,
            "output_case_path": self.output_case_path,
            "build_script_path": self.build_script_path,
            "build_script_sha256": self.build_script_sha256,
        }

    @classmethod
    def from_markdown(cls, markdown: str) -> "MarkdownSetupPlan":
        data = _front_matter(markdown)
        reject_unknown(
            data,
            {
                "schema_version",
                "plan_id",
                "parent_case_path",
                "parent_case_sha256",
                "output_case_path",
                "build_script_path",
                "build_script_sha256",
            },
            "MarkdownSetupPlan",
        )
        plan = cls(
            schema_version=data.get("schema_version"),
            plan_id=data.get("plan_id"),
            parent_case_path=data.get("parent_case_path"),
            parent_case_sha256=data.get("parent_case_sha256"),
            output_case_path=data.get("output_case_path"),
            build_script_path=data.get("build_script_path"),
            build_script_sha256=data.get("build_script_sha256"),
        )
        plan.validate()
        return plan

    @classmethod
    def from_path(cls, path: Path) -> "MarkdownSetupPlan":
        return cls.from_markdown(path.read_text(encoding="utf-8"))


def capture_parent_identity(case_path: str) -> dict[str, Any]:
    """Return local source identity before the agent pins it into a plan."""

    path = Path(case_path)
    if not path.is_absolute() or not path.is_file():
        raise FileNotFoundError(f"Parent case is not a local file: {case_path}")
    return {
        "path": str(path.resolve()),
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _tracked_build_script(plan: MarkdownSetupPlan, project_root: Path) -> Path:
    script = (project_root / plan.build_script_path).resolve()
    try:
        script.relative_to(project_root.resolve())
    except ValueError as exc:  # Defense in depth after plan validation.
        raise RuntimeError("Build script resolves outside the repository") from exc
    if not script.is_file():
        raise FileNotFoundError(f"Pinned build script is missing: {script}")
    observed_sha = _sha256(script)
    if observed_sha != plan.build_script_sha256:
        raise RuntimeError(
            "Build script SHA-256 mismatch: plan is pinned to "
            f"{plan.build_script_sha256}, observed {observed_sha}"
        )
    return script


def _compact_process_output(text: str, limit: int = 4000) -> str:
    return text if len(text) <= limit else text[-limit:] + "\n[truncated]"


def execute_pinned_build_script(
    plan: MarkdownSetupPlan,
    *,
    project_root: Path,
    server_id: str,
) -> dict[str, Any]:
    """Invoke the plan's case-specific build script on the Fluent PC.

    Build scripts have one stable CLI contract: ``--server-id``,
    ``--source-case``, ``--output-case``, and ``--summary-json``.  The script,
    not Markdown, contains the step-by-step Fluent TUI/PyFluent sequence.
    """

    plan.validate()
    parent_identity_before = capture_parent_identity(plan.parent_case_path)
    if parent_identity_before["sha256"] != plan.parent_case_sha256:
        raise RuntimeError(
            "Parent case SHA-256 mismatch: plan is pinned to "
            f"{plan.parent_case_sha256}, observed {parent_identity_before['sha256']}"
        )
    output_path = Path(plan.output_case_path)
    if output_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite an existing output case: {output_path}"
        )
    script = _tracked_build_script(plan, project_root)

    with tempfile.TemporaryDirectory(prefix="fluent-build-") as temporary:
        detail_path = Path(temporary) / "build-script-evidence.json"
        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--server-id",
                str(server_id),
                "--source-case",
                plan.parent_case_path,
                "--output-case",
                plan.output_case_path,
                "--summary-json",
                str(detail_path),
            ],
            cwd=project_root,
            text=True,
            capture_output=True,
            check=False,
        )
        detail: Any = None
        if detail_path.is_file():
            try:
                import json

                detail = json.loads(detail_path.read_text(encoding="utf-8"))
            except Exception as exc:
                detail = {"_evidence_read_error": f"{type(exc).__name__}: {exc}"}

    parent_identity_after = capture_parent_identity(plan.parent_case_path)
    if parent_identity_after["sha256"] != plan.parent_case_sha256:
        raise RuntimeError("Parent case changed during build-script execution")
    if completed.returncode != 0:
        raise RuntimeError(
            "Build script failed with exit code "
            f"{completed.returncode}: {_compact_process_output(completed.stderr)}"
        )
    if not output_path.is_file():
        raise RuntimeError(
            "Build script reported success but the expected output case is missing: "
            f"{output_path}"
        )
    return {
        "status": "success",
        "plan_id": plan.plan_id,
        "plan_digest": plan.digest,
        "build_script": {
            "path": plan.build_script_path,
            "sha256": plan.build_script_sha256,
        },
        "parent_identity_before": parent_identity_before,
        "parent_identity_after": parent_identity_after,
        "output_case_path": plan.output_case_path,
        "build_script_evidence": detail,
        "build_script_stdout": _compact_process_output(completed.stdout),
    }

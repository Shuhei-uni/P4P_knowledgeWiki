"""Markdown setup-plan contracts and the first local Fluent execution recipe.

Plans are exchanged through Git, but Fluent execution stays on the Windows
computer that owns the case files and the local gRPC server.  This module
deliberately supports named recipes only; Markdown can never contain arbitrary
Python, a TUI command, or a generated Fluent path.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pyansys_fluent.autonomy.common import (
    ContractValidationError,
    canonical_digest,
    reject_unknown,
    require_absolute_path,
    require_bool,
    require_mapping,
    require_positive_int,
    require_schema_version,
    require_sha256,
    require_string,
)
from pyansys_fluent.common import remote_file_exists, safe_get_state, try_action
from pyansys_fluent.setup_io import load_case_only, write_case_only


SETUP_PLAN_SCHEMA_VERSION = 1
TWO_WAY_DPM_INTERACTION = "dpm_two_way_interaction"
SUPPORTED_RECIPES = frozenset({TWO_WAY_DPM_INTERACTION})


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
            index for index, line in enumerate(lines[1:], start=1)
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
    """A pinned, named recipe request authored in Markdown front matter."""

    plan_id: str
    recipe_id: str
    parent_case_path: str
    parent_case_sha256: str
    output_case_path: str
    expected_parent_interaction: dict[str, Any]
    update_sources_every_iteration: bool
    iteration_interval: int
    schema_version: int = SETUP_PLAN_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            SETUP_PLAN_SCHEMA_VERSION,
            "MarkdownSetupPlan",
        )
        require_string(self.plan_id, "plan_id")
        if self.recipe_id not in SUPPORTED_RECIPES:
            raise ContractValidationError(
                f"Unsupported setup recipe: {self.recipe_id!r}"
            )
        require_absolute_path(self.parent_case_path, "parent_case_path")
        require_sha256(self.parent_case_sha256, "parent_case_sha256")
        require_absolute_path(self.output_case_path, "output_case_path")
        if not self.parent_case_path.lower().endswith(".cas.h5"):
            raise ContractValidationError("parent_case_path must end with .cas.h5")
        if not self.output_case_path.lower().endswith(".cas.h5"):
            raise ContractValidationError("output_case_path must end with .cas.h5")
        if self.parent_case_path == self.output_case_path:
            raise ContractValidationError(
                "output_case_path must differ from parent_case_path"
            )
        expected = require_mapping(
            self.expected_parent_interaction,
            "expected_parent_interaction",
        )
        reject_unknown(
            expected,
            {
                "enabled",
                "update_sources_every_iteration",
                "iteration_interval",
            },
            "expected_parent_interaction",
        )
        if not expected:
            raise ContractValidationError(
                "expected_parent_interaction must declare at least one precondition"
            )
        for field_name, value in expected.items():
            if field_name == "iteration_interval":
                require_positive_int(value, field_name)
            else:
                require_bool(value, field_name)
        require_bool(
            self.update_sources_every_iteration,
            "update_sources_every_iteration",
        )
        require_positive_int(self.iteration_interval, "iteration_interval")

    @property
    def digest(self) -> str:
        return canonical_digest(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "plan_id": self.plan_id,
            "recipe_id": self.recipe_id,
            "parent_case_path": self.parent_case_path,
            "parent_case_sha256": self.parent_case_sha256,
            "output_case_path": self.output_case_path,
            "expected_parent_interaction": dict(self.expected_parent_interaction),
            "update_sources_every_iteration": self.update_sources_every_iteration,
            "iteration_interval": self.iteration_interval,
        }

    @classmethod
    def from_markdown(cls, markdown: str) -> "MarkdownSetupPlan":
        data = _front_matter(markdown)
        reject_unknown(
            data,
            {
                "schema_version",
                "plan_id",
                "recipe_id",
                "parent_case_path",
                "parent_case_sha256",
                "output_case_path",
                "expected_parent_interaction",
                "update_sources_every_iteration",
                "iteration_interval",
            },
            "MarkdownSetupPlan",
        )
        plan = cls(
            schema_version=data.get("schema_version"),
            plan_id=data.get("plan_id"),
            recipe_id=data.get("recipe_id"),
            parent_case_path=data.get("parent_case_path"),
            parent_case_sha256=data.get("parent_case_sha256"),
            output_case_path=data.get("output_case_path"),
            expected_parent_interaction=data.get("expected_parent_interaction"),
            update_sources_every_iteration=data.get(
                "update_sources_every_iteration"
            ),
            iteration_interval=data.get("iteration_interval"),
        )
        plan.validate()
        return plan

    @classmethod
    def from_path(cls, path: Path) -> "MarkdownSetupPlan":
        return cls.from_markdown(path.read_text(encoding="utf-8"))


def capture_parent_identity(case_path: str) -> dict[str, Any]:
    """Return local source identity before an agent pins it into a plan."""

    path = Path(case_path)
    if not path.is_absolute() or not path.is_file():
        raise FileNotFoundError(f"Parent case is not a local file: {case_path}")
    return {
        "path": str(path.resolve()),
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _injection_names(branch: Any) -> list[str]:
    try:
        names = branch.get_object_names()
    except Exception as exc:
        raise RuntimeError("Could not inspect inherited DPM injections") from exc
    return sorted(str(name) for name in names)


def _require_interaction_preconditions(
    actual: Any,
    expected: dict[str, Any],
) -> None:
    if not isinstance(actual, dict):
        raise RuntimeError(f"Could not capture DPM interaction state: {actual}")
    mismatches = {
        key: {"expected": value, "actual": actual.get(key)}
        for key, value in expected.items()
        if actual.get(key) != value
    }
    if mismatches:
        raise RuntimeError(
            "Parent DPM interaction precondition mismatch: "
            f"{mismatches}"
        )


def execute_markdown_setup_plan(
    solver: Any,
    plan: MarkdownSetupPlan,
) -> dict[str, Any]:
    """Apply the plan's named recipe and return evidence for the Git outbox."""

    plan.validate()
    parent_identity = capture_parent_identity(plan.parent_case_path)
    if parent_identity["sha256"] != plan.parent_case_sha256:
        raise RuntimeError(
            "Parent case SHA-256 mismatch: plan is pinned to "
            f"{plan.parent_case_sha256}, observed {parent_identity['sha256']}"
        )

    if not remote_file_exists(solver, plan.parent_case_path):
        raise FileNotFoundError(
            f"Fluent cannot see parent case: {plan.parent_case_path}"
        )
    output_path = Path(plan.output_case_path)
    if output_path.exists():
        raise FileExistsError(
            f"Refusing to overwrite an existing output case: {output_path}"
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    load_case_only(solver, plan.parent_case_path, label="Load Markdown Plan Parent")

    dpm = solver.settings.setup.models.discrete_phase
    interaction = dpm.general_settings.interaction
    before_interaction = safe_get_state(interaction, "plan.parent.interaction")
    before_injections = _injection_names(dpm.injections)
    if not before_injections:
        raise RuntimeError("Parent case has no active DPM injections")
    _require_interaction_preconditions(
        before_interaction,
        plan.expected_parent_interaction,
    )

    if plan.recipe_id != TWO_WAY_DPM_INTERACTION:  # validate() guards this.
        raise ContractValidationError(f"Unsupported recipe: {plan.recipe_id}")
    if not try_action(
        "set_dpm_interaction_enabled_true",
        lambda: setattr(interaction, "enabled", True),
    ):
        raise RuntimeError("Could not enable DPM continuous-phase interaction")
    if not try_action(
        "set_dpm_update_sources_every_iteration",
        lambda: setattr(
            interaction,
            "update_sources_every_iteration",
            plan.update_sources_every_iteration,
        ),
    ):
        raise RuntimeError("Could not set DPM source-update mode")
    if not try_action(
        "set_dpm_iteration_interval",
        lambda: setattr(interaction, "iteration_interval", plan.iteration_interval),
    ):
        raise RuntimeError("Could not set DPM iteration interval")

    after_interaction = safe_get_state(interaction, "plan.output.interaction")
    after_injections = _injection_names(dpm.injections)
    _require_interaction_preconditions(
        after_interaction,
        {
            "enabled": True,
            "update_sources_every_iteration": plan.update_sources_every_iteration,
            "iteration_interval": plan.iteration_interval,
        },
    )
    if after_injections != before_injections:
        raise RuntimeError(
            "Inherited DPM injection inventory changed unexpectedly: "
            f"before={before_injections}, after={after_injections}"
        )

    write_case_only(solver, plan.output_case_path, "markdown_setup_plan")
    if not remote_file_exists(solver, plan.output_case_path):
        raise RuntimeError(
            f"Fluent wrote no visible output case: {plan.output_case_path}"
        )
    if _sha256(Path(plan.parent_case_path)) != plan.parent_case_sha256:
        raise RuntimeError("Parent case changed during setup-plan execution")

    return {
        "status": "success",
        "plan_id": plan.plan_id,
        "plan_digest": plan.digest,
        "recipe_id": plan.recipe_id,
        "parent_identity": parent_identity,
        "output_case_path": plan.output_case_path,
        "fluent_version": solver.get_fluent_version(),
        "before_interaction": before_interaction,
        "after_interaction": after_interaction,
        "injection_names": after_injections,
    }

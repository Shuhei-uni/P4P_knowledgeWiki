"""Phase 3 declarative setup contracts and an offline-only plan compiler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .capability import CapabilityFingerprint, CapabilityRegistry
from .common import (
    ContractValidationError,
    reject_unknown,
    require_absolute_path,
    require_bool,
    require_choice,
    require_json_value,
    require_mapping,
    require_positive_int,
    require_schema_version,
    require_sha256,
    require_string,
    require_string_sequence,
)


SETUP_SCHEMA_VERSION = 1
SETUP_STAGES = (
    "mesh",
    "materials",
    "models",
    "phases",
    "boundaries",
    "numerics",
    "dpm",
    "ewf",
    "final",
)


@dataclass(frozen=True)
class ControlledChange:
    """One semantic setting change explicitly owned by an experiment."""

    semantic_id: str
    stage: str
    requested_value: Any
    expected_parent_value: Any = None

    def validate(self) -> None:
        require_string(self.semantic_id, "semantic_id")
        require_choice(self.stage, set(SETUP_STAGES), "stage")
        require_json_value(self.requested_value, "requested_value")
        require_json_value(
            self.expected_parent_value,
            "expected_parent_value",
        )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "semantic_id": self.semantic_id,
            "stage": self.stage,
            "requested_value": require_json_value(self.requested_value),
            "expected_parent_value": require_json_value(
                self.expected_parent_value
            ),
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "ControlledChange":
        data = require_mapping(payload, "ControlledChange")
        reject_unknown(
            data,
            {
                "semantic_id",
                "stage",
                "requested_value",
                "expected_parent_value",
            },
            "ControlledChange",
        )
        change = cls(
            semantic_id=data.get("semantic_id"),
            stage=data.get("stage"),
            requested_value=data.get("requested_value"),
            expected_parent_value=data.get("expected_parent_value"),
        )
        change.validate()
        return change


@dataclass(frozen=True)
class RunPolicy:
    """Future Phase 4 run policy, separate from setup mutation."""

    total_iterations: int
    chunk_iterations: int
    checkpoint_interval: int
    initialization: str = "hybrid"
    resume_enabled: bool = True
    checkpoint_reopen_required: bool = True

    def validate(self) -> None:
        require_positive_int(self.total_iterations, "total_iterations")
        require_positive_int(self.chunk_iterations, "chunk_iterations")
        require_positive_int(
            self.checkpoint_interval,
            "checkpoint_interval",
        )
        if self.chunk_iterations > self.total_iterations:
            raise ContractValidationError(
                "chunk_iterations cannot exceed total_iterations"
            )
        if self.checkpoint_interval % self.chunk_iterations != 0:
            raise ContractValidationError(
                "checkpoint_interval must be a multiple of chunk_iterations"
            )
        require_choice(
            self.initialization,
            {"hybrid"},
            "initialization",
        )
        require_bool(self.resume_enabled, "resume_enabled")
        require_bool(
            self.checkpoint_reopen_required,
            "checkpoint_reopen_required",
        )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "total_iterations": self.total_iterations,
            "chunk_iterations": self.chunk_iterations,
            "checkpoint_interval": self.checkpoint_interval,
            "initialization": self.initialization,
            "resume_enabled": self.resume_enabled,
            "checkpoint_reopen_required": (
                self.checkpoint_reopen_required
            ),
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "RunPolicy":
        data = require_mapping(payload, "RunPolicy")
        reject_unknown(
            data,
            {
                "total_iterations",
                "chunk_iterations",
                "checkpoint_interval",
                "initialization",
                "resume_enabled",
                "checkpoint_reopen_required",
            },
            "RunPolicy",
        )
        policy = cls(
            total_iterations=data.get("total_iterations"),
            chunk_iterations=data.get("chunk_iterations"),
            checkpoint_interval=data.get("checkpoint_interval"),
            initialization=data.get("initialization", "hybrid"),
            resume_enabled=data.get("resume_enabled", True),
            checkpoint_reopen_required=data.get(
                "checkpoint_reopen_required",
                True,
            ),
        )
        policy.validate()
        return policy


@dataclass(frozen=True)
class SetupSpec:
    """Declarative experiment input; it contains no executable Fluent path."""

    setup_id: str
    experiment_id: str
    parent_case_path: str
    parent_case_sha256: str
    required_fingerprint_digest: str
    controlled_changes: tuple[ControlledChange, ...]
    preserve_semantic_ids: tuple[str, ...]
    run_policy: RunPolicy
    analysis_contract_id: str
    schema_version: int = SETUP_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            SETUP_SCHEMA_VERSION,
            "SetupSpec",
        )
        require_string(self.setup_id, "setup_id")
        require_string(self.experiment_id, "experiment_id")
        require_absolute_path(self.parent_case_path, "parent_case_path")
        require_sha256(self.parent_case_sha256, "parent_case_sha256")
        require_sha256(
            self.required_fingerprint_digest,
            "required_fingerprint_digest",
        )
        if not self.controlled_changes:
            raise ContractValidationError(
                "controlled_changes must contain at least one change"
            )
        controlled_ids: list[str] = []
        for change in self.controlled_changes:
            if not isinstance(change, ControlledChange):
                raise ContractValidationError(
                    "controlled_changes must contain ControlledChange objects"
                )
            change.validate()
            controlled_ids.append(change.semantic_id)
        if len(controlled_ids) != len(set(controlled_ids)):
            raise ContractValidationError(
                "controlled_changes cannot repeat a semantic_id"
            )
        preserved = require_string_sequence(
            self.preserve_semantic_ids,
            "preserve_semantic_ids",
        )
        overlap = set(controlled_ids) & set(preserved)
        if overlap:
            raise ContractValidationError(
                "A semantic setting cannot be both controlled and preserved: "
                f"{sorted(overlap)}"
            )
        if not isinstance(self.run_policy, RunPolicy):
            raise ContractValidationError(
                "run_policy must be a RunPolicy"
            )
        self.run_policy.validate()
        require_string(self.analysis_contract_id, "analysis_contract_id")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "setup_id": self.setup_id,
            "experiment_id": self.experiment_id,
            "parent_case_path": self.parent_case_path,
            "parent_case_sha256": self.parent_case_sha256,
            "required_fingerprint_digest": (
                self.required_fingerprint_digest
            ),
            "controlled_changes": [
                change.to_dict() for change in self.controlled_changes
            ],
            "preserve_semantic_ids": list(self.preserve_semantic_ids),
            "run_policy": self.run_policy.to_dict(),
            "analysis_contract_id": self.analysis_contract_id,
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "SetupSpec":
        data = require_mapping(payload, "SetupSpec")
        reject_unknown(
            data,
            {
                "schema_version",
                "setup_id",
                "experiment_id",
                "parent_case_path",
                "parent_case_sha256",
                "required_fingerprint_digest",
                "controlled_changes",
                "preserve_semantic_ids",
                "run_policy",
                "analysis_contract_id",
            },
            "SetupSpec",
        )
        changes = data.get("controlled_changes")
        if not isinstance(changes, list):
            raise ContractValidationError(
                "controlled_changes must be an array"
            )
        preserved = require_string_sequence(
            data.get("preserve_semantic_ids", ()),
            "preserve_semantic_ids",
        )
        spec = cls(
            schema_version=data.get("schema_version"),
            setup_id=data.get("setup_id"),
            experiment_id=data.get("experiment_id"),
            parent_case_path=data.get("parent_case_path"),
            parent_case_sha256=data.get("parent_case_sha256"),
            required_fingerprint_digest=data.get(
                "required_fingerprint_digest"
            ),
            controlled_changes=tuple(
                ControlledChange.from_dict(item) for item in changes
            ),
            preserve_semantic_ids=preserved,
            run_policy=RunPolicy.from_dict(data.get("run_policy")),
            analysis_contract_id=data.get("analysis_contract_id"),
        )
        spec.validate()
        return spec


@dataclass(frozen=True)
class CompiledSetupStep:
    sequence: int
    stage: str
    semantic_id: str
    recipe_id: str
    requested_value: Any
    readback_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "stage": self.stage,
            "semantic_id": self.semantic_id,
            "recipe_id": self.recipe_id,
            "requested_value": require_json_value(self.requested_value),
            "readback_required": self.readback_required,
        }


@dataclass(frozen=True)
class CompiledSetupPlan:
    setup_id: str
    fingerprint_digest: str
    steps: tuple[CompiledSetupStep, ...]
    preserved_semantic_ids: tuple[str, ...]
    requires_fresh_session_reopen: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "setup_id": self.setup_id,
            "fingerprint_digest": self.fingerprint_digest,
            "steps": [step.to_dict() for step in self.steps],
            "preserved_semantic_ids": list(self.preserved_semantic_ids),
            "requires_fresh_session_reopen": (
                self.requires_fresh_session_reopen
            ),
        }


class SetupCompiler:
    """Compile a SetupSpec to a deterministic plan without executing it."""

    def compile(
        self,
        spec: SetupSpec,
        fingerprint: CapabilityFingerprint,
        registry: CapabilityRegistry,
    ) -> CompiledSetupPlan:
        spec.validate()
        fingerprint.validate()
        if spec.required_fingerprint_digest != fingerprint.digest:
            raise ContractValidationError(
                "SetupSpec requires a different capability fingerprint"
            )
        stage_index = {
            stage: index for index, stage in enumerate(SETUP_STAGES)
        }
        ordered = sorted(
            spec.controlled_changes,
            key=lambda change: (
                stage_index[change.stage],
                change.semantic_id,
            ),
        )
        steps: list[CompiledSetupStep] = []
        for sequence, change in enumerate(ordered, start=1):
            recipe = registry.resolve(change.semantic_id, fingerprint)
            steps.append(
                CompiledSetupStep(
                    sequence=sequence,
                    stage=change.stage,
                    semantic_id=change.semantic_id,
                    recipe_id=recipe.recipe_id,
                    requested_value=change.requested_value,
                )
            )
        return CompiledSetupPlan(
            setup_id=spec.setup_id,
            fingerprint_digest=fingerprint.digest,
            steps=tuple(steps),
            preserved_semantic_ids=spec.preserve_semantic_ids,
        )

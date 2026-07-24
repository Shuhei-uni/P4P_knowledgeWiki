"""Phase 6 bounded next-action records and deterministic dry-run gating."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .analysis import AnalysisManifest
from .common import (
    ContractValidationError,
    reject_unknown,
    require_bool,
    require_choice,
    require_mapping,
    require_schema_version,
    require_string,
    require_string_sequence,
)


DECISION_SCHEMA_VERSION = 1
NEXT_ACTIONS = frozenset(
    {
        "NEXT_EXPERIMENT",
        "CONTINUE_ITERATIONS",
        "RERUN_FROM_CHECKPOINT",
        "REPAIR_SETUP",
        "INCREASE_ANALYSIS_BUDGET",
        "CAPABILITY_RESEARCH_REQUIRED",
        "HUMAN_REVIEW_REQUIRED",
        "STOP_PROJECT_BRANCH",
    }
)
RUN_OUTCOMES = frozenset(
    {"completed", "nonconverged", "interrupted", "failed"}
)


@dataclass(frozen=True)
class DecisionContext:
    capability_ready: bool
    setup_verified: bool
    run_outcome: str
    analysis_manifest: AnalysisManifest
    evidence_adequate: bool
    evidence_refs: tuple[str, ...]
    human_review_reasons: tuple[str, ...] = ()
    stop_requested: bool = False

    def validate(self) -> None:
        require_bool(self.capability_ready, "capability_ready")
        require_bool(self.setup_verified, "setup_verified")
        require_choice(self.run_outcome, RUN_OUTCOMES, "run_outcome")
        if not isinstance(self.analysis_manifest, AnalysisManifest):
            raise ContractValidationError(
                "analysis_manifest must be an AnalysisManifest"
            )
        self.analysis_manifest.validate()
        require_bool(self.evidence_adequate, "evidence_adequate")
        require_string_sequence(self.evidence_refs, "evidence_refs")
        require_string_sequence(
            self.human_review_reasons,
            "human_review_reasons",
        )
        require_bool(self.stop_requested, "stop_requested")


@dataclass(frozen=True)
class DecisionRecord:
    action: str
    rationale: str
    evidence_refs: tuple[str, ...]
    approval_required: bool
    schema_version: int = DECISION_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            DECISION_SCHEMA_VERSION,
            "DecisionRecord",
        )
        require_choice(self.action, NEXT_ACTIONS, "action")
        require_string(self.rationale, "rationale")
        require_string_sequence(self.evidence_refs, "evidence_refs")
        require_bool(self.approval_required, "approval_required")
        if self.action == "NEXT_EXPERIMENT" and not self.approval_required:
            raise ContractValidationError(
                "Scaffolded NEXT_EXPERIMENT decisions require approval"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "action": self.action,
            "rationale": self.rationale,
            "evidence_refs": list(self.evidence_refs),
            "approval_required": self.approval_required,
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "DecisionRecord":
        data = require_mapping(payload, "DecisionRecord")
        reject_unknown(
            data,
            {
                "schema_version",
                "action",
                "rationale",
                "evidence_refs",
                "approval_required",
            },
            "DecisionRecord",
        )
        evidence_refs = require_string_sequence(
            data.get("evidence_refs", ()),
            "evidence_refs",
        )
        record = cls(
            schema_version=data.get("schema_version"),
            action=data.get("action"),
            rationale=data.get("rationale"),
            evidence_refs=evidence_refs,
            approval_required=data.get("approval_required"),
        )
        record.validate()
        return record


def evaluate_next_action(context: DecisionContext) -> DecisionRecord:
    """Choose one bounded action without proposing or executing a setup."""

    context.validate()
    if context.stop_requested:
        action = "STOP_PROJECT_BRANCH"
        rationale = "A project-level stop was explicitly requested."
    elif context.human_review_reasons:
        action = "HUMAN_REVIEW_REQUIRED"
        rationale = (
            "Human review blockers remain: "
            + "; ".join(context.human_review_reasons)
        )
    elif not context.capability_ready:
        action = "CAPABILITY_RESEARCH_REQUIRED"
        rationale = (
            "The requested setting strategy is not verified for the current "
            "capability fingerprint."
        )
    elif not context.setup_verified:
        action = "REPAIR_SETUP"
        rationale = (
            "The setup has not passed controlled-diff and reopen verification."
        )
    elif context.run_outcome in {"interrupted", "failed"}:
        action = "RERUN_FROM_CHECKPOINT"
        rationale = (
            "The run did not reach a terminal numerical result and should "
            "resume from verified state."
        )
    elif context.run_outcome == "nonconverged":
        action = "CONTINUE_ITERATIONS"
        rationale = (
            "The setup is verified but the numerical result is not converged."
        )
    elif not context.analysis_manifest.safe_for_interpretation:
        action = "INCREASE_ANALYSIS_BUDGET"
        rationale = (
            "Required analysis evidence is incomplete: "
            + "; ".join(context.analysis_manifest.blocking_reasons)
        )
    elif not context.evidence_adequate:
        action = "HUMAN_REVIEW_REQUIRED"
        rationale = (
            "The analysis is complete but evidence is not adequate for an "
            "automatic experiment decision."
        )
    else:
        action = "NEXT_EXPERIMENT"
        rationale = (
            "Capabilities, setup, run, analysis, and evidence gates passed."
        )

    record = DecisionRecord(
        action=action,
        rationale=rationale,
        evidence_refs=context.evidence_refs,
        approval_required=action in {
            "NEXT_EXPERIMENT",
            "REPAIR_SETUP",
            "STOP_PROJECT_BRANCH",
        },
    )
    record.validate()
    return record

"""Phase 5 analysis contracts and deterministic completeness gating."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .common import (
    ContractValidationError,
    reject_unknown,
    require_choice,
    require_json_value,
    require_mapping,
    require_schema_version,
    require_string,
    require_string_sequence,
)


ANALYSIS_SCHEMA_VERSION = 1
APPLICABILITY = frozenset({"required", "optional", "not_applicable"})
RESULT_STATUSES = frozenset(
    {"complete", "incomplete", "failed", "not_applicable"}
)


@dataclass(frozen=True)
class AnalysisRequirement:
    analysis_id: str
    applicability: str
    completion_predicates: tuple[str, ...] = ()
    reason: str | None = None

    def validate(self) -> None:
        require_string(self.analysis_id, "analysis_id")
        require_choice(
            self.applicability,
            APPLICABILITY,
            "applicability",
        )
        predicates = require_string_sequence(
            self.completion_predicates,
            "completion_predicates",
        )
        if self.applicability == "required" and not predicates:
            raise ContractValidationError(
                "required analysis needs at least one completion predicate"
            )
        if self.applicability == "not_applicable":
            if self.reason is None:
                raise ContractValidationError(
                    "not_applicable analysis requires a reason"
                )
            require_string(self.reason, "reason")
            if predicates:
                raise ContractValidationError(
                    "not_applicable analysis cannot have completion predicates"
                )
        elif self.reason is not None:
            require_string(self.reason, "reason")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "analysis_id": self.analysis_id,
            "applicability": self.applicability,
            "completion_predicates": list(self.completion_predicates),
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "AnalysisRequirement":
        data = require_mapping(payload, "AnalysisRequirement")
        reject_unknown(
            data,
            {
                "analysis_id",
                "applicability",
                "completion_predicates",
                "reason",
            },
            "AnalysisRequirement",
        )
        predicates = require_string_sequence(
            data.get("completion_predicates", ()),
            "completion_predicates",
        )
        requirement = cls(
            analysis_id=data.get("analysis_id"),
            applicability=data.get("applicability"),
            completion_predicates=predicates,
            reason=data.get("reason"),
        )
        requirement.validate()
        return requirement


@dataclass(frozen=True)
class AnalysisContract:
    contract_id: str
    experiment_question: str
    requirements: tuple[AnalysisRequirement, ...]
    schema_version: int = ANALYSIS_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            ANALYSIS_SCHEMA_VERSION,
            "AnalysisContract",
        )
        require_string(self.contract_id, "contract_id")
        require_string(self.experiment_question, "experiment_question")
        if not self.requirements:
            raise ContractValidationError(
                "AnalysisContract requires at least one analysis"
            )
        identifiers: list[str] = []
        for requirement in self.requirements:
            if not isinstance(requirement, AnalysisRequirement):
                raise ContractValidationError(
                    "requirements must contain AnalysisRequirement objects"
                )
            requirement.validate()
            identifiers.append(requirement.analysis_id)
        if len(identifiers) != len(set(identifiers)):
            raise ContractValidationError(
                "requirements cannot repeat an analysis_id"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "experiment_question": self.experiment_question,
            "requirements": [
                requirement.to_dict()
                for requirement in self.requirements
            ],
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "AnalysisContract":
        data = require_mapping(payload, "AnalysisContract")
        reject_unknown(
            data,
            {
                "schema_version",
                "contract_id",
                "experiment_question",
                "requirements",
            },
            "AnalysisContract",
        )
        requirements = data.get("requirements")
        if not isinstance(requirements, list):
            raise ContractValidationError("requirements must be an array")
        contract = cls(
            schema_version=data.get("schema_version"),
            contract_id=data.get("contract_id"),
            experiment_question=data.get("experiment_question"),
            requirements=tuple(
                AnalysisRequirement.from_dict(item)
                for item in requirements
            ),
        )
        contract.validate()
        return contract


@dataclass(frozen=True)
class AnalysisResult:
    analysis_id: str
    status: str
    satisfied_predicates: tuple[str, ...] = ()
    artifact_paths: tuple[str, ...] = ()
    blocking_reasons: tuple[str, ...] = ()
    evidence: Any = None

    def validate(self) -> None:
        require_string(self.analysis_id, "analysis_id")
        require_choice(self.status, RESULT_STATUSES, "status")
        require_string_sequence(
            self.satisfied_predicates,
            "satisfied_predicates",
        )
        require_string_sequence(self.artifact_paths, "artifact_paths")
        require_string_sequence(
            self.blocking_reasons,
            "blocking_reasons",
        )
        require_json_value(self.evidence, "evidence")
        if self.status in {"incomplete", "failed"} and not self.blocking_reasons:
            raise ContractValidationError(
                f"{self.status} analysis requires a blocking reason"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "analysis_id": self.analysis_id,
            "status": self.status,
            "satisfied_predicates": list(self.satisfied_predicates),
            "artifact_paths": list(self.artifact_paths),
            "blocking_reasons": list(self.blocking_reasons),
            "evidence": require_json_value(self.evidence),
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "AnalysisResult":
        data = require_mapping(payload, "AnalysisResult")
        reject_unknown(
            data,
            {
                "analysis_id",
                "status",
                "satisfied_predicates",
                "artifact_paths",
                "blocking_reasons",
                "evidence",
            },
            "AnalysisResult",
        )
        satisfied = require_string_sequence(
            data.get("satisfied_predicates", ()),
            "satisfied_predicates",
        )
        artifacts = require_string_sequence(
            data.get("artifact_paths", ()),
            "artifact_paths",
        )
        blockers = require_string_sequence(
            data.get("blocking_reasons", ()),
            "blocking_reasons",
        )
        result = cls(
            analysis_id=data.get("analysis_id"),
            status=data.get("status"),
            satisfied_predicates=satisfied,
            artifact_paths=artifacts,
            blocking_reasons=blockers,
            evidence=data.get("evidence"),
        )
        result.validate()
        return result


@dataclass(frozen=True)
class AnalysisManifest:
    contract_id: str
    results: tuple[AnalysisResult, ...]
    safe_for_interpretation: bool
    blocking_reasons: tuple[str, ...]
    schema_version: int = ANALYSIS_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            ANALYSIS_SCHEMA_VERSION,
            "AnalysisManifest",
        )
        require_string(self.contract_id, "contract_id")
        identifiers: list[str] = []
        for result in self.results:
            if not isinstance(result, AnalysisResult):
                raise ContractValidationError(
                    "results must contain AnalysisResult objects"
                )
            result.validate()
            identifiers.append(result.analysis_id)
        if len(identifiers) != len(set(identifiers)):
            raise ContractValidationError(
                "results cannot repeat an analysis_id"
            )
        if not isinstance(self.safe_for_interpretation, bool):
            raise ContractValidationError(
                "safe_for_interpretation must be a boolean"
            )
        require_string_sequence(
            self.blocking_reasons,
            "blocking_reasons",
        )
        if self.safe_for_interpretation and self.blocking_reasons:
            raise ContractValidationError(
                "safe manifest cannot contain blocking reasons"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "contract_id": self.contract_id,
            "results": [result.to_dict() for result in self.results],
            "safe_for_interpretation": self.safe_for_interpretation,
            "blocking_reasons": list(self.blocking_reasons),
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "AnalysisManifest":
        data = require_mapping(payload, "AnalysisManifest")
        reject_unknown(
            data,
            {
                "schema_version",
                "contract_id",
                "results",
                "safe_for_interpretation",
                "blocking_reasons",
            },
            "AnalysisManifest",
        )
        results = data.get("results")
        if not isinstance(results, list):
            raise ContractValidationError("results must be an array")
        blockers = require_string_sequence(
            data.get("blocking_reasons", ()),
            "blocking_reasons",
        )
        manifest = cls(
            schema_version=data.get("schema_version"),
            contract_id=data.get("contract_id"),
            results=tuple(
                AnalysisResult.from_dict(item) for item in results
            ),
            safe_for_interpretation=data.get(
                "safe_for_interpretation"
            ),
            blocking_reasons=blockers,
        )
        manifest.validate()
        return manifest


def build_analysis_manifest(
    contract: AnalysisContract,
    supplied_results: tuple[AnalysisResult, ...],
) -> AnalysisManifest:
    """Normalize results and block interpretation on any required gap."""

    contract.validate()
    by_id: dict[str, AnalysisResult] = {}
    for result in supplied_results:
        result.validate()
        if result.analysis_id in by_id:
            raise ContractValidationError(
                f"Duplicate result for {result.analysis_id}"
            )
        by_id[result.analysis_id] = result

    contract_ids = {
        requirement.analysis_id for requirement in contract.requirements
    }
    extra = set(by_id) - contract_ids
    if extra:
        raise ContractValidationError(
            f"Results are not declared by the contract: {sorted(extra)}"
        )

    normalized: list[AnalysisResult] = []
    blockers: list[str] = []
    for requirement in contract.requirements:
        result = by_id.get(requirement.analysis_id)
        if requirement.applicability == "not_applicable":
            if result is not None and result.status != "not_applicable":
                raise ContractValidationError(
                    f"{requirement.analysis_id} must be not_applicable"
                )
            normalized.append(
                result
                or AnalysisResult(
                    analysis_id=requirement.analysis_id,
                    status="not_applicable",
                    blocking_reasons=(),
                    evidence={"reason": requirement.reason},
                )
            )
            continue

        if result is None:
            result = AnalysisResult(
                analysis_id=requirement.analysis_id,
                status="incomplete",
                blocking_reasons=("result was not supplied",),
            )
        normalized.append(result)

        if requirement.applicability != "required":
            continue
        missing_predicates = set(requirement.completion_predicates) - set(
            result.satisfied_predicates
        )
        if result.status != "complete":
            blockers.append(
                f"{result.analysis_id}: required status is {result.status}"
            )
        if missing_predicates:
            blockers.append(
                f"{result.analysis_id}: missing predicates "
                f"{sorted(missing_predicates)}"
            )
        blockers.extend(
            f"{result.analysis_id}: {reason}"
            for reason in result.blocking_reasons
        )

    manifest = AnalysisManifest(
        contract_id=contract.contract_id,
        results=tuple(normalized),
        safe_for_interpretation=not blockers,
        blocking_reasons=tuple(blockers),
    )
    manifest.validate()
    return manifest


class AnalysisPlugin(Protocol):
    """Interface implemented later by carrier, DPM, and EWF adapters."""

    analysis_id: str

    def execute(self, context: Any) -> AnalysisResult:
        """Produce one structured result without interpreting the experiment."""


class AnalysisDispatcher:
    """Run injected plugins and build one contract-gated manifest."""

    def __init__(self, plugins: tuple[AnalysisPlugin, ...] = ()):
        self._plugins: dict[str, AnalysisPlugin] = {}
        for plugin in plugins:
            analysis_id = require_string(
                getattr(plugin, "analysis_id", None),
                "plugin.analysis_id",
            )
            if analysis_id in self._plugins:
                raise ContractValidationError(
                    f"Duplicate analysis plugin for {analysis_id}"
                )
            self._plugins[analysis_id] = plugin

    def execute(
        self,
        contract: AnalysisContract,
        context: Any,
    ) -> AnalysisManifest:
        contract.validate()
        results: list[AnalysisResult] = []
        for requirement in contract.requirements:
            if requirement.applicability == "not_applicable":
                continue
            plugin = self._plugins.get(requirement.analysis_id)
            if plugin is None:
                results.append(
                    AnalysisResult(
                        analysis_id=requirement.analysis_id,
                        status="incomplete",
                        blocking_reasons=("analysis plugin is not registered",),
                    )
                )
                continue
            try:
                result = plugin.execute(context)
                result.validate()
                if result.analysis_id != requirement.analysis_id:
                    raise ContractValidationError(
                        "Plugin returned result for "
                        f"{result.analysis_id}, expected "
                        f"{requirement.analysis_id}"
                    )
            except Exception as exc:
                result = AnalysisResult(
                    analysis_id=requirement.analysis_id,
                    status="failed",
                    blocking_reasons=(
                        f"{type(exc).__name__}: {exc}",
                    ),
                )
            results.append(result)
        return build_analysis_manifest(contract, tuple(results))

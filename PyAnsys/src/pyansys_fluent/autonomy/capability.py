"""Phase 2 capability fingerprints, observations, and verified recipes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .common import (
    ContractValidationError,
    canonical_digest,
    reject_unknown,
    require_bool,
    require_choice,
    require_json_value,
    require_mapping,
    require_non_negative_int,
    require_schema_version,
    require_sha256,
    require_string,
    require_string_sequence,
)


CAPABILITY_SCHEMA_VERSION = 1
CAPABILITY_STRATEGIES = frozenset(
    {"settings_api", "tui", "python_journal"}
)


@dataclass(frozen=True)
class CapabilityFingerprint:
    """Exact Fluent/PyFluent and case-state identity for recipe reuse."""

    fluent_version: str
    pyfluent_version: str
    solver_mode: str
    dimension: int
    precision: str
    active_models: tuple[str, ...]
    phase_count: int
    boundary_types: tuple[tuple[str, str], ...]
    source_case_sha256: str | None = None
    schema_version: int = CAPABILITY_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            CAPABILITY_SCHEMA_VERSION,
            "CapabilityFingerprint",
        )
        require_string(self.fluent_version, "fluent_version")
        require_string(self.pyfluent_version, "pyfluent_version")
        require_choice(
            self.solver_mode,
            {"solution", "meshing", "pre_post"},
            "solver_mode",
        )
        if self.dimension not in {2, 3}:
            raise ContractValidationError("dimension must be 2 or 3")
        require_choice(
            self.precision,
            {"single", "double"},
            "precision",
        )
        require_string_sequence(self.active_models, "active_models")
        require_non_negative_int(self.phase_count, "phase_count")
        names: list[str] = []
        for index, pair in enumerate(self.boundary_types):
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ContractValidationError(
                    f"boundary_types[{index}] must be a name/type pair"
                )
            names.append(
                require_string(pair[0], f"boundary_types[{index}].name")
            )
            require_string(pair[1], f"boundary_types[{index}].type")
        if len(names) != len(set(names)):
            raise ContractValidationError(
                "boundary_types cannot contain duplicate names"
            )
        if self.source_case_sha256 is not None:
            require_sha256(self.source_case_sha256, "source_case_sha256")

    @property
    def digest(self) -> str:
        return canonical_digest(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "fluent_version": self.fluent_version,
            "pyfluent_version": self.pyfluent_version,
            "solver_mode": self.solver_mode,
            "dimension": self.dimension,
            "precision": self.precision,
            "active_models": list(self.active_models),
            "phase_count": self.phase_count,
            "boundary_types": {
                name: boundary_type
                for name, boundary_type in self.boundary_types
            },
            "source_case_sha256": self.source_case_sha256,
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "CapabilityFingerprint":
        data = require_mapping(payload, "CapabilityFingerprint")
        reject_unknown(
            data,
            {
                "schema_version",
                "fluent_version",
                "pyfluent_version",
                "solver_mode",
                "dimension",
                "precision",
                "active_models",
                "phase_count",
                "boundary_types",
                "source_case_sha256",
            },
            "CapabilityFingerprint",
        )
        boundaries = require_mapping(
            data.get("boundary_types"),
            "boundary_types",
        )
        active_models = require_string_sequence(
            data.get("active_models"),
            "active_models",
        )
        fingerprint = cls(
            schema_version=data.get("schema_version"),
            fluent_version=data.get("fluent_version"),
            pyfluent_version=data.get("pyfluent_version"),
            solver_mode=data.get("solver_mode"),
            dimension=data.get("dimension"),
            precision=data.get("precision"),
            active_models=active_models,
            phase_count=data.get("phase_count"),
            boundary_types=tuple(
                sorted(
                    (
                        require_string(name, "boundary name"),
                        require_string(value, f"boundary_types.{name}"),
                    )
                    for name, value in boundaries.items()
                )
            ),
            source_case_sha256=data.get("source_case_sha256"),
        )
        fingerprint.validate()
        return fingerprint


@dataclass(frozen=True)
class CapabilityObservation:
    """One read-only live observation of a semantic Fluent setting."""

    semantic_id: str
    path: str
    active: bool
    read_only: bool | None
    active_children: tuple[str, ...] = ()
    active_commands: tuple[str, ...] = ()
    active_queries: tuple[str, ...] = ()
    allowed_values: tuple[Any, ...] = ()
    compact_state: Any = None
    errors: tuple[str, ...] = ()
    schema_version: int = CAPABILITY_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            CAPABILITY_SCHEMA_VERSION,
            "CapabilityObservation",
        )
        require_string(self.semantic_id, "semantic_id")
        require_string(self.path, "path")
        require_bool(self.active, "active")
        if self.read_only is not None:
            require_bool(self.read_only, "read_only")
        require_string_sequence(self.active_children, "active_children")
        require_string_sequence(self.active_commands, "active_commands")
        require_string_sequence(self.active_queries, "active_queries")
        for index, value in enumerate(self.allowed_values):
            require_json_value(value, f"allowed_values[{index}]")
        require_json_value(self.compact_state, "compact_state")
        require_string_sequence(self.errors, "errors")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "semantic_id": self.semantic_id,
            "path": self.path,
            "active": self.active,
            "read_only": self.read_only,
            "active_children": list(self.active_children),
            "active_commands": list(self.active_commands),
            "active_queries": list(self.active_queries),
            "allowed_values": [
                require_json_value(value) for value in self.allowed_values
            ],
            "compact_state": require_json_value(self.compact_state),
            "errors": list(self.errors),
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "CapabilityObservation":
        data = require_mapping(payload, "CapabilityObservation")
        reject_unknown(
            data,
            {
                "schema_version",
                "semantic_id",
                "path",
                "active",
                "read_only",
                "active_children",
                "active_commands",
                "active_queries",
                "allowed_values",
                "compact_state",
                "errors",
            },
            "CapabilityObservation",
        )
        active_children = require_string_sequence(
            data.get("active_children", ()),
            "active_children",
        )
        active_commands = require_string_sequence(
            data.get("active_commands", ()),
            "active_commands",
        )
        active_queries = require_string_sequence(
            data.get("active_queries", ()),
            "active_queries",
        )
        errors = require_string_sequence(
            data.get("errors", ()),
            "errors",
        )
        allowed_values = data.get("allowed_values", ())
        if (
            isinstance(allowed_values, (str, bytes))
            or not isinstance(allowed_values, (list, tuple))
        ):
            raise ContractValidationError(
                "allowed_values must be an array"
            )
        observation = cls(
            schema_version=data.get("schema_version"),
            semantic_id=data.get("semantic_id"),
            path=data.get("path"),
            active=data.get("active"),
            read_only=data.get("read_only"),
            active_children=active_children,
            active_commands=active_commands,
            active_queries=active_queries,
            allowed_values=tuple(allowed_values),
            compact_state=data.get("compact_state"),
            errors=errors,
        )
        observation.validate()
        return observation


@dataclass(frozen=True)
class CapabilityRecipe:
    """One fingerprint-pinned, readback-required setting strategy."""

    recipe_id: str
    semantic_id: str
    strategy: str
    target: str
    readback_target: str
    fingerprint_digest: str
    verified: bool
    invalidation_reason: str | None = None
    schema_version: int = CAPABILITY_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            CAPABILITY_SCHEMA_VERSION,
            "CapabilityRecipe",
        )
        require_string(self.recipe_id, "recipe_id")
        require_string(self.semantic_id, "semantic_id")
        require_choice(self.strategy, CAPABILITY_STRATEGIES, "strategy")
        require_string(self.target, "target")
        require_string(self.readback_target, "readback_target")
        require_sha256(self.fingerprint_digest, "fingerprint_digest")
        require_bool(self.verified, "verified")
        if self.invalidation_reason is not None:
            require_string(self.invalidation_reason, "invalidation_reason")
        if self.verified and self.invalidation_reason is not None:
            raise ContractValidationError(
                "verified recipe cannot have an invalidation_reason"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "recipe_id": self.recipe_id,
            "semantic_id": self.semantic_id,
            "strategy": self.strategy,
            "target": self.target,
            "readback_target": self.readback_target,
            "fingerprint_digest": self.fingerprint_digest,
            "verified": self.verified,
            "invalidation_reason": self.invalidation_reason,
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "CapabilityRecipe":
        data = require_mapping(payload, "CapabilityRecipe")
        reject_unknown(
            data,
            {
                "schema_version",
                "recipe_id",
                "semantic_id",
                "strategy",
                "target",
                "readback_target",
                "fingerprint_digest",
                "verified",
                "invalidation_reason",
            },
            "CapabilityRecipe",
        )
        recipe = cls(
            schema_version=data.get("schema_version"),
            recipe_id=data.get("recipe_id"),
            semantic_id=data.get("semantic_id"),
            strategy=data.get("strategy"),
            target=data.get("target"),
            readback_target=data.get("readback_target"),
            fingerprint_digest=data.get("fingerprint_digest"),
            verified=data.get("verified"),
            invalidation_reason=data.get("invalidation_reason"),
        )
        recipe.validate()
        return recipe


class CapabilityRegistry:
    """In-memory scaffold for safe recipe resolution and invalidation."""

    def __init__(self, recipes: tuple[CapabilityRecipe, ...] = ()):
        self._recipes: dict[str, CapabilityRecipe] = {}
        for recipe in recipes:
            recipe.validate()
            if recipe.semantic_id in self._recipes:
                raise ContractValidationError(
                    f"Duplicate capability recipe for {recipe.semantic_id}"
                )
            self._recipes[recipe.semantic_id] = recipe

    def resolve(
        self,
        semantic_id: str,
        fingerprint: CapabilityFingerprint,
    ) -> CapabilityRecipe:
        fingerprint.validate()
        recipe = self._recipes.get(semantic_id)
        if recipe is None:
            raise ContractValidationError(
                f"No capability recipe for {semantic_id}"
            )
        if not recipe.verified:
            raise ContractValidationError(
                f"Capability recipe {recipe.recipe_id} is not verified"
            )
        if recipe.fingerprint_digest != fingerprint.digest:
            raise ContractValidationError(
                f"Capability fingerprint mismatch for {semantic_id}"
            )
        return recipe

    def invalidate(self, semantic_id: str, reason: str) -> CapabilityRecipe:
        recipe = self._recipes.get(semantic_id)
        if recipe is None:
            raise ContractValidationError(
                f"No capability recipe for {semantic_id}"
            )
        invalidated = CapabilityRecipe(
            recipe_id=recipe.recipe_id,
            semantic_id=recipe.semantic_id,
            strategy=recipe.strategy,
            target=recipe.target,
            readback_target=recipe.readback_target,
            fingerprint_digest=recipe.fingerprint_digest,
            verified=False,
            invalidation_reason=require_string(reason, "reason"),
        )
        invalidated.validate()
        self._recipes[semantic_id] = invalidated
        return invalidated


@dataclass(frozen=True)
class CapabilityProbeSnapshot:
    """Serializable output expected from a future read-only live adapter."""

    fingerprint: CapabilityFingerprint
    observations: tuple[CapabilityObservation, ...]
    schema_version: int = CAPABILITY_SCHEMA_VERSION

    def validate(self) -> None:
        require_schema_version(
            self.schema_version,
            CAPABILITY_SCHEMA_VERSION,
            "CapabilityProbeSnapshot",
        )
        if not isinstance(self.fingerprint, CapabilityFingerprint):
            raise ContractValidationError(
                "fingerprint must be a CapabilityFingerprint"
            )
        self.fingerprint.validate()
        identifiers: list[str] = []
        for observation in self.observations:
            if not isinstance(observation, CapabilityObservation):
                raise ContractValidationError(
                    "observations must contain CapabilityObservation objects"
                )
            observation.validate()
            identifiers.append(observation.semantic_id)
        if len(identifiers) != len(set(identifiers)):
            raise ContractValidationError(
                "observations cannot repeat a semantic_id"
            )

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": self.schema_version,
            "fingerprint": self.fingerprint.to_dict(),
            "observations": [
                observation.to_dict()
                for observation in self.observations
            ],
        }

    @classmethod
    def from_dict(cls, payload: Any) -> "CapabilityProbeSnapshot":
        data = require_mapping(payload, "CapabilityProbeSnapshot")
        reject_unknown(
            data,
            {"schema_version", "fingerprint", "observations"},
            "CapabilityProbeSnapshot",
        )
        observations = data.get("observations")
        if not isinstance(observations, list):
            raise ContractValidationError(
                "observations must be an array"
            )
        snapshot = cls(
            schema_version=data.get("schema_version"),
            fingerprint=CapabilityFingerprint.from_dict(
                data.get("fingerprint")
            ),
            observations=tuple(
                CapabilityObservation.from_dict(item)
                for item in observations
            ),
        )
        snapshot.validate()
        return snapshot


class ReadOnlyCapabilityBackend(Protocol):
    """Interface a future Fluent adapter must implement."""

    def capture_fingerprint(self) -> CapabilityFingerprint:
        """Return exact version and case-state identity."""

    def observe(self, semantic_id: str) -> CapabilityObservation:
        """Read one semantic setting without mutation."""


class CapabilityProbe:
    """Collect deterministic observations through an injected backend."""

    def __init__(self, backend: ReadOnlyCapabilityBackend):
        self.backend = backend

    def capture(
        self,
        semantic_ids: tuple[str, ...],
    ) -> CapabilityProbeSnapshot:
        identifiers = require_string_sequence(
            semantic_ids,
            "semantic_ids",
        )
        if not identifiers:
            raise ContractValidationError(
                "semantic_ids must contain at least one target"
            )
        fingerprint = self.backend.capture_fingerprint()
        fingerprint.validate()
        observations: list[CapabilityObservation] = []
        for semantic_id in identifiers:
            observation = self.backend.observe(semantic_id)
            observation.validate()
            if observation.semantic_id != semantic_id:
                raise ContractValidationError(
                    "Backend returned observation for "
                    f"{observation.semantic_id}, expected {semantic_id}"
                )
            observations.append(observation)
        snapshot = CapabilityProbeSnapshot(
            fingerprint=fingerprint,
            observations=tuple(observations),
        )
        snapshot.validate()
        return snapshot

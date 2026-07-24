"""Shared validation helpers for versioned autonomy contracts."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any


class ContractValidationError(ValueError):
    """Raised when an offline autonomy contract is unsafe or malformed."""


def require_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractValidationError(f"{field_name} must be an object")
    return value


def reject_unknown(
    payload: Mapping[str, Any],
    allowed: set[str],
    model_name: str,
) -> None:
    unknown = set(payload) - allowed
    if unknown:
        raise ContractValidationError(
            f"{model_name} contains unknown fields: {sorted(unknown)}"
        )


def require_schema_version(
    value: Any,
    expected: int,
    model_name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContractValidationError(
            f"{model_name}.schema_version must be an integer"
        )
    if value != expected:
        raise ContractValidationError(
            f"Unsupported {model_name} schema_version {value}; expected {expected}"
        )
    return value


def require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def require_string_sequence(value: Any, field_name: str) -> tuple[str, ...]:
    if (
        isinstance(value, (str, bytes))
        or not isinstance(value, Sequence)
    ):
        raise ContractValidationError(f"{field_name} must be an array")
    result = tuple(
        require_string(item, f"{field_name}[{index}]")
        for index, item in enumerate(value)
    )
    if len(result) != len(set(result)):
        raise ContractValidationError(f"{field_name} cannot contain duplicates")
    return result


def require_choice(
    value: Any,
    choices: set[str] | frozenset[str],
    field_name: str,
) -> str:
    normalized = require_string(value, field_name)
    if normalized not in choices:
        raise ContractValidationError(
            f"{field_name} must be one of {sorted(choices)}"
        )
    return normalized


def require_positive_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ContractValidationError(f"{field_name} must be a positive integer")
    return value


def require_non_negative_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ContractValidationError(
            f"{field_name} must be a non-negative integer"
        )
    return value


def require_bool(value: Any, field_name: str) -> bool:
    if not isinstance(value, bool):
        raise ContractValidationError(f"{field_name} must be a boolean")
    return value


def require_sha256(value: Any, field_name: str) -> str:
    normalized = require_string(value, field_name).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized):
        raise ContractValidationError(
            f"{field_name} must contain exactly 64 hexadecimal characters"
        )
    return normalized


def require_absolute_path(value: Any, field_name: str) -> str:
    normalized = require_string(value, field_name)
    if not (
        Path(normalized).is_absolute()
        or PureWindowsPath(normalized).is_absolute()
    ):
        raise ContractValidationError(f"{field_name} must be an absolute path")
    return normalized


def require_json_value(value: Any, field_name: str = "value") -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): require_json_value(item, f"{field_name}.{key}")
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            require_json_value(item, f"{field_name}[{index}]")
            for index, item in enumerate(value)
        ]
    raise ContractValidationError(f"{field_name} must be JSON-serializable")


def canonical_digest(payload: Mapping[str, Any]) -> str:
    document = json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(document).hexdigest()

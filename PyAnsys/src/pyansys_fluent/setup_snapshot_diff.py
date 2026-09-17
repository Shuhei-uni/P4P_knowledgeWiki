"""Compare captured setup evidence without loading cases into a live workspace."""
from __future__ import annotations

from collections.abc import Mapping
from fnmatch import fnmatchcase
from typing import Any

from pyansys_fluent.dependency_workflow import values_equal


def diff_values(left: Any, right: Any, path: str = "") -> list[dict]:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        rows = []
        for key in sorted(set(left) | set(right), key=str):
            child = f"{path}.{key}" if path else str(key)
            if key not in left:
                rows.append({"path": child, "base_missing": True, "candidate": right[key]})
            elif key not in right:
                rows.append({"path": child, "base": left[key], "candidate_missing": True})
            else:
                rows.extend(diff_values(left[key], right[key], child))
        return rows
    return [] if values_equal(left, right) else [{"path": path, "base": left, "candidate": right}]


def _has_missing_evidence(value: Any) -> bool:
    if value is None or (isinstance(value, str) and value == "<large_state_omitted>"):
        return True
    if isinstance(value, Mapping):
        if value.get("error") or value.get("status") == "error" or value.get("ok") is False or value.get("inactive") is True or value.get("skipped"):
            return True
        return any(_has_missing_evidence(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_has_missing_evidence(item) for item in value)
    return False


def compare_snapshots(base: dict, candidate: dict, allowed_changes: list[str]) -> dict:
    """A matching capture is not proof of artifact identity or experiment readiness."""
    for snapshot in (base, candidate):
        if snapshot.get("schema") != "p4p.mcp-inspection.v1" or snapshot.get("status") != "OBSERVED" or snapshot.get("errors"):
            raise ValueError("Both inputs must be successful MCP inspection captures.")
        state = snapshot.get("results", {}).get("get_state")
        if not isinstance(state, dict) or not state or set(state) != set(snapshot.get("paths", [])) or _has_missing_evidence(state):
            raise ValueError("Snapshot contains missing/failed state; an unknown value cannot prove an invariant.")
    if not base.get("paths") or set(base["paths"]) != set(candidate.get("paths", [])):
        raise ValueError("Snapshot scopes differ; capture the same required paths before comparing.")
    differences = diff_values(base["results"]["get_state"], candidate["results"]["get_state"])
    for row in differences:
        row["classification"] = "declared-change" if any(fnmatchcase(row["path"], pattern) for pattern in allowed_changes) else "requires-review"
    return {"status": "BLOCKED" if any(r["classification"] == "requires-review" for r in differences) else "WITHIN_DECLARED_DIFF_SCOPE",
            "paths": base["paths"], "differences": differences,
            "claim_limit": "Captured-path comparison only. Verify artifact identity, expected new values, save/reopen, smoke and evidence streams separately."}

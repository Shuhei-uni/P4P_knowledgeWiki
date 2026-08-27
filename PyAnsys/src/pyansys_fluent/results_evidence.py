"""Bounded machine-evidence handoff for selected Project experiment results.

This module deliberately owns only the small bridge from an analysis run to an
existing ``results.md`` file.  It does not define a universal result schema,
interpret a run, or manage generated artifacts.  Callers provide a short list
of evidence records and the writer replaces only its own marker block.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


BEGIN_MARKER = "<!-- BEGIN CODEX GENERATED EVIDENCE: post-simulation-analysis -->"
END_MARKER = "<!-- END CODEX GENERATED EVIDENCE: post-simulation-analysis -->"
_ALLOWED_STATUSES = frozenset(
    {
        "complete",
        "partial",
        "unavailable",
        "failed",
        "not applicable",
        "requires rerun",
        "blocked",
    }
)


def _inline(value: Any) -> str:
    """Return a single-line value safe to place inside Markdown code spans."""
    if value is None or value == "":
        return "unavailable"
    return str(value).replace("`", "'").replace("\n", " ").replace("\r", " ")


def _table_value(value: Any) -> str:
    return _inline(value).replace("|", "\\|")


def _relative_artifact_link(results_path: Path, artifact: Any) -> str:
    target = Path(str(artifact)).expanduser()
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    else:
        target = target.resolve()
    relative = os.path.relpath(target, start=results_path.parent.resolve())
    return Path(relative).as_posix()


def _artifact_links(results_path: Path, artifacts: Any) -> str:
    if not isinstance(artifacts, Sequence) or isinstance(artifacts, (str, bytes)):
        return "unavailable"

    links: list[str] = []
    for artifact in artifacts:
        if artifact is None or str(artifact).strip() == "":
            continue
        target = Path(str(artifact))
        label = target.name or str(target)
        links.append(
            f"[{_table_value(label)}]({_relative_artifact_link(results_path, artifact)})"
        )
    return ", ".join(links) or "unavailable"


def _record_status(record: Mapping[str, Any]) -> str:
    value = str(record.get("status", "unavailable")).strip().lower()
    return value if value in _ALLOWED_STATUSES else "unavailable"


def _record_lines(record: Mapping[str, Any], key: str) -> list[str]:
    values = record.get(key, [])
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, Sequence):
        return []
    return [_inline(value) for value in values if _inline(value).strip()]


def _case_identity_lines(case_identity: Mapping[str, Any]) -> list[str]:
    status = _inline(case_identity.get("status", "unavailable"))
    lines = [f"- Case/data identity: `{status}`"]
    basis = case_identity.get("basis")
    if basis:
        lines.append(f"  - Basis: {_inline(basis)}")
    case_file = case_identity.get("case_file")
    data_file = case_identity.get("data_file")
    if case_file or data_file:
        lines.extend(
            [
                f"  - Case: `{_inline(case_file)}`",
                f"  - Data: `{_inline(data_file)}`",
            ]
        )
    warnings = case_identity.get("warnings", [])
    if isinstance(warnings, str) or not isinstance(warnings, Sequence):
        warnings = []
    for warning in warnings:
        lines.append(f"  - Identity limitation: {_inline(warning)}")
    return lines


def render_results_evidence(
    *,
    results_path: Path,
    run_label: str,
    load_summary: Mapping[str, Any],
    case_identity: Mapping[str, Any],
    fluent_version: Any,
    records: Sequence[Mapping[str, Any]],
) -> str:
    """Render a bounded evidence block for an existing Project ``results.md``.

    ``records`` is intentionally a caller-owned list rather than a framework
    object.  Each record may provide ``name``, ``status``, ``scope``,
    ``coordinate``, ``horizon``, ``measurements``, ``artifacts``, ``notes``,
    ``numerical_state``, ``missing``, and ``observations``.  Unknown fields are
    ignored so the handoff stays small and task-specific.
    """
    normalized_records = list(records)
    requested = ", ".join(
        f"`{_inline(record.get('name', 'unnamed'))}`" for record in normalized_records
    ) or "none"

    lines = [
        BEGIN_MARKER,
        "## Automated evidence handoff",
        "",
        "### What ran",
        f"- Run label: `{_inline(run_label)}`",
        f"- Selected checks: {requested}",
        f"- Case/data action: `{_inline(load_summary.get('mode', 'unavailable'))}`",
        "",
        "### Run identity / horizon",
        *_case_identity_lines(case_identity),
        f"- Fluent version: `{_inline(fluent_version)}`",
    ]

    for record in normalized_records:
        name = _inline(record.get("name", "unnamed"))
        coordinate = _inline(record.get("coordinate"))
        horizon = _inline(record.get("horizon"))
        lines.append(f"- `{name}` coordinate: `{coordinate}`; horizon: `{horizon}`")

    lines.extend(["", "### Plots and measured values"])
    lines.extend(
        [
            "| Check | Extraction status | Scope / coordinate | Measured values | Artifacts |",
            "|---|---|---|---|---|",
        ]
    )
    for record in normalized_records:
        name = _table_value(record.get("name", "unnamed"))
        status = _table_value(_record_status(record))
        scope = _table_value(
            f"{_inline(record.get('scope'))}; {_inline(record.get('coordinate'))}"
        )
        measurements = "; ".join(_record_lines(record, "measurements")) or "unavailable"
        artifacts = _artifact_links(results_path, record.get("artifacts", []))
        lines.append(
            f"| `{name}` | `{status}` | {scope} | {_table_value(measurements)} | {artifacts} |"
        )

    for record in normalized_records:
        name = _inline(record.get("name", "unnamed"))
        for note in _record_lines(record, "notes"):
            lines.append(f"- `{name}` evidence note: {note}")

    lines.extend(["", "### Numerical state"])
    lines.append(
        "- Extraction status is separate from scientific adequacy; this packet does not declare convergence, validation, or parent eligibility."
    )
    for record in normalized_records:
        name = _inline(record.get("name", "unnamed"))
        numerical_state = _inline(record.get("numerical_state"))
        lines.append(f"- `{name}`: {numerical_state}")

    lines.extend(["", "### Missing/incomplete evidence"])
    missing_any = False
    if case_identity.get("status") != "verified":
        lines.append("- Case/data identity is unavailable or not verified by this pass.")
        missing_any = True
    for record in normalized_records:
        name = _inline(record.get("name", "unnamed"))
        missing = _record_lines(record, "missing")
        if _record_status(record) != "complete" and not missing:
            missing = ["The selected check did not produce complete evidence."]
        for item in missing:
            lines.append(f"- `{name}`: {item}")
            missing_any = True
    if not missing_any:
        lines.append("- No extraction gaps were reported by the selected checks.")

    lines.extend(["", "### Neutral observations"])
    for record in normalized_records:
        name = _inline(record.get("name", "unnamed"))
        observations = _record_lines(record, "observations")
        if not observations:
            observations = [
                f"Extraction status is `{_record_status(record)}` for the reported scope."
            ]
        for observation in observations:
            lines.append(f"- `{name}`: {observation}")
    lines.append(
        "- This generated block records evidence only. It does not choose a preferred case or model, assign a scientific finding, or select the next experiment."
    )

    lines.extend([END_MARKER, ""])
    return "\n".join(lines)


def update_results_evidence(path: Path, generated_block: str) -> Path:
    """Append or replace only the generator-owned marker block in ``path``."""
    path = Path(path)
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as handle:
            existing = handle.read()
    else:
        existing = ""

    block = generated_block.rstrip("\r\n") + "\n"
    begin_index = existing.find(BEGIN_MARKER)
    end_index = existing.find(END_MARKER)

    if begin_index >= 0:
        if end_index < begin_index + len(BEGIN_MARKER):
            raise ValueError("Generated evidence has a begin marker without a later end marker.")
        replacement_end = end_index + len(END_MARKER)
        updated = existing[:begin_index] + block.rstrip("\n") + existing[replacement_end:]
    elif end_index >= 0:
        raise ValueError("Generated evidence has an end marker without a begin marker.")
    else:
        separator = ""
        if existing:
            if not existing.endswith(("\n", "\r")):
                separator += "\n"
            if not existing.endswith(("\n\n", "\r\n\r\n")):
                separator += "\n"
        updated = existing + separator + block

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return path

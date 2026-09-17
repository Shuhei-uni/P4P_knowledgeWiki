#!/usr/bin/env python3
"""Reset and redirect the Phase 7.1A evaluation report files.

Run this on the Windows Fluent/Codex host immediately before each autoresearch
experiment.  It reuses the already-proven Phase 7 report definitions, removes
stale .out histories from the experiment monitor directory, and points each
required Fluent Report File object at one deterministic filename.

This script changes monitor file destinations only.  It does not initialize,
iterate, change physics/numerics, or alter report definitions.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


INVENTORY_REPORTS = (
    "e0-liquid-mass-total",
    "e0-liquid-volume-total",
    "absorb-lower-liquid-mass",
    "absorb-lower-liquid-volume",
    "absorb-adjacent-liquid-mass",
    "absorb-broad-liquid-mass",
)
FLUX_REPORTS = tuple(
    f"e0-flux-{phase}-{surface}"
    for phase in ("mixture", "phase1", "phase2")
    for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")
)
REQUIRED_REPORT_DEFINITIONS = INVENTORY_REPORTS + FLUX_REPORTS


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def report_definition_map(solver: Any) -> dict[str, str]:
    """Map scientific report definition names to Fluent Report File objects."""
    branch = solver.settings.solution.monitor.report_files
    result: dict[str, str] = {}
    for object_name in (str(item) for item in branch.get_object_names()):
        state = safe_get_state(branch[object_name], f"report file {object_name}")
        if not isinstance(state, Mapping):
            continue
        definitions = state.get("report_defs", [])
        if isinstance(definitions, str):
            definitions = [definitions]
        if isinstance(definitions, list):
            for definition in definitions:
                if isinstance(definition, str):
                    result[definition.removesuffix("-rfile")] = object_name
        if object_name.endswith("-rfile"):
            result.setdefault(object_name.removesuffix("-rfile"), object_name)
    return result


def clear_old_outputs(report_dir: Path) -> list[str]:
    """Delete only files owned by this evaluation contract."""
    deleted: list[str] = []
    for logical_name in REQUIRED_REPORT_DEFINITIONS:
        # Fluent can create numbered siblings such as *_1_1.out after a prior
        # file collision.  Remove those as well so one experiment starts from
        # one unambiguous history.
        for path in report_dir.glob(f"{logical_name}*.out"):
            if path.is_file():
                path.unlink()
                deleted.append(str(path))
    for name in ("evaluation.json", "report-contract.json"):
        path = report_dir / name
        if path.exists() and path.is_file():
            path.unlink()
            deleted.append(str(path))
    return deleted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--server-id", default="1")
    args = parser.parse_args()

    report_dir = args.report_dir.expanduser().resolve()
    report_dir.mkdir(parents=True, exist_ok=True)
    deleted = clear_old_outputs(report_dir)

    solver = connect(server_id=args.server_id, start_transcript=False)
    branch = solver.settings.solution.monitor.report_files
    mapping = report_definition_map(solver)
    missing = [name for name in REQUIRED_REPORT_DEFINITIONS if name not in mapping]
    if missing:
        raise RuntimeError(
            "Phase 7.1A evaluation contract is incomplete; missing report definitions: "
            + ", ".join(missing)
        )

    redirected: dict[str, dict[str, str]] = {}
    for logical_name in REQUIRED_REPORT_DEFINITIONS:
        object_name = mapping[logical_name]
        destination = report_dir / f"{logical_name}.out"
        report_file = branch[object_name]
        report_file.file_name = str(destination)
        state = safe_get_state(report_file, f"redirected report file {object_name}")
        actual = state.get("file_name") if isinstance(state, Mapping) else None
        if not isinstance(actual, str) or Path(actual).name.casefold() != destination.name.casefold():
            raise RuntimeError(
                f"report redirect readback mismatch for {logical_name}: "
                f"requested={destination}; actual={actual!r}"
            )
        redirected[logical_name] = {
            "fluent_object": object_name,
            "file": str(destination),
        }

    contract = {
        "kind": "p71a-autoresearch-report-contract",
        "status": "READY",
        "server_id": args.server_id,
        "report_dir": str(report_dir),
        "deleted_stale_files": deleted,
        "required_report_count": len(REQUIRED_REPORT_DEFINITIONS),
        "reports": redirected,
        "note": (
            "Monitor destinations were reset only. Physics, numerics, initialization, "
            "report definitions, and solver state were not changed."
        ),
    }
    write_json(report_dir / "report-contract.json", contract)
    print(json.dumps(contract, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

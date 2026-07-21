#!/usr/bin/env python3
"""Read-only comparison of two Fluent case setup states.

The script loads each remote case without reading data, captures the main
setup trees, and reports changed paths.  It is intended for checking that a
derived branch changes only the settings expected by its setup definition.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_chdir, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import require_remote_input  # noqa: E402


SNAPSHOT_OBJECTS = {
    "models": lambda solver: solver.settings.setup.models,
    "boundary_conditions": lambda solver: solver.settings.setup.boundary_conditions,
    "materials": lambda solver: solver.settings.setup.materials,
    "cell_zone_conditions": lambda solver: solver.settings.setup.cell_zone_conditions,
    "solution": lambda solver: solver.settings.solution,
}

EXPECTED_PATH_TOKENS = (
    "eulerian_wall_film",
    "wall_film",
    "wallfilm",
    "film",
    "particle_splash",
    "splash",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--base-case", required=True)
    parser.add_argument("--candidate-case", required=True)
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output" / "case_setup_diff"),
    )
    return parser.parse_args()


def load_case(solver: Any, case_file: str) -> None:
    require_remote_input(solver, case_file, "case file")
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    solver.settings.file.read_case(file_name=case_file)


def capture_case(solver: Any, case_file: str) -> dict[str, Any]:
    load_case(solver, case_file)
    captured: dict[str, Any] = {
        "case_file": case_file,
        "fluent_version": solver.get_fluent_version(),
    }
    for name, getter in SNAPSHOT_OBJECTS.items():
        captured[name] = safe_get_state(getter(solver), f"{name} for {case_file}")
    return captured


def leaf_equal(left: Any, right: Any) -> bool:
    return json.dumps(left, sort_keys=True, default=str) == json.dumps(
        right, sort_keys=True, default=str
    )


def diff_values(left: Any, right: Any, path: str) -> list[dict[str, Any]]:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        rows: list[dict[str, Any]] = []
        keys = sorted(set(left) | set(right), key=str)
        for key in keys:
            child_path = f"{path}.{key}" if path else str(key)
            if key not in left:
                rows.append({"path": child_path, "base": "<missing>", "candidate": right[key]})
            elif key not in right:
                rows.append({"path": child_path, "base": left[key], "candidate": "<missing>"})
            else:
                rows.extend(diff_values(left[key], right[key], child_path))
        return rows
    if isinstance(left, list) and isinstance(right, list):
        if leaf_equal(left, right):
            return []
        return [{"path": path, "base": left, "candidate": right}]
    if leaf_equal(left, right):
        return []
    return [{"path": path, "base": left, "candidate": right}]


def classify(path: str) -> str:
    normalized = path.lower().replace("-", "_")
    if any(token in normalized for token in EXPECTED_PATH_TOKENS):
        return "expected-10a-area"
    return "requires-review"


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Read-Only Fluent Setup Difference Audit",
        "",
        f"- Server id: `{payload['server_id']}`",
        f"- Base case: `{payload['base_case']}`",
        f"- Candidate case: `{payload['candidate_case']}`",
        "- Data files: none loaded; this is a case-setup comparison only.",
        "",
        "## Difference Summary",
        "",
        f"- Total changed paths: `{len(payload['differences'])}`",
        f"- Paths in expected 10a/EWF area: `{payload['expected_change_count']}`",
        f"- Paths requiring review: `{payload['review_change_count']}`",
        "",
        "| Classification | Path | Base value | Candidate value |",
        "|---|---|---|---|",
    ]
    for row in payload["differences"]:
        base = json.dumps(row["base"], default=str).replace("|", "\\|")
        candidate = json.dumps(row["candidate"], default=str).replace("|", "\\|")
        lines.append(f"| `{row['classification']}` | `{row['path']}` | `{base}` | `{candidate}` |")
    if not payload["differences"]:
        lines.append("| none | none | — | — |")
    lines.extend(
        [
            "",
            "Interpretation: `expected-10a-area` identifies paths associated with EWF/film/splash controls. "
            "All `requires-review` paths must be checked against the 10a setup definition before treating the branch as clean.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    solver = connect(server_id=args.server_id)
    base = capture_case(solver, args.base_case)
    candidate = capture_case(solver, args.candidate_case)

    differences: list[dict[str, Any]] = []
    for tree_name in SNAPSHOT_OBJECTS:
        for row in diff_values(base.get(tree_name), candidate.get(tree_name), tree_name):
            row["classification"] = classify(row["path"])
            differences.append(row)

    payload = {
        "server_id": str(args.server_id),
        "base_case": args.base_case,
        "candidate_case": args.candidate_case,
        "base_snapshot": base,
        "candidate_snapshot": candidate,
        "differences": differences,
        "expected_change_count": sum(
            row["classification"] == "expected-10a-area" for row in differences
        ),
        "review_change_count": sum(
            row["classification"] == "requires-review" for row in differences
        ),
    }
    json_path = output_dir / "10a-base-case-diff.json"
    markdown_path = output_dir / "10a-base-case-diff.md"
    json_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")
    print(f"snapshot_json: {json_path}")
    print(f"summary_markdown: {markdown_path}")
    print(f"changed_paths: {len(differences)}")
    print(f"expected_10a_paths: {payload['expected_change_count']}")
    print(f"review_paths: {payload['review_change_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

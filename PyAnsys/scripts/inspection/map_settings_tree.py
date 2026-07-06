#!/usr/bin/env python3
"""Probe-first Fluent settings tree mapper.

Default use case:
1. connect to a live Fluent session
2. optionally load a case/data pair before probing
3. optionally activate DPM if the requested root lives under `setup.models.discrete_phase`
4. capture the live settings tree
5. compare it against an archived seed tree when provided

The script is intentionally generic. DPM is the first supported root, but the
same mapper works for other Fluent settings branches as long as the requested
root is reachable in the live session.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.extraction import load_remote_case_data  # noqa: E402
from pyansys_fluent.setup_common import load_json, print_header  # noqa: E402
from pyansys_fluent.setup_dpm import enable_dpm_model_best_effort  # noqa: E402
from pyansys_fluent.settings_tree_mapper import capture_settings_tree, compare_tree_shapes  # noqa: E402


DEFAULT_SEED_JSON = (
    PROJECT_ROOT
    / "cases"
    / "actual_setup_archives"
    / "07-pure-phase-split-actual-area-live-fff-1-2"
    / "models_tree_detailed.json"
)
DEFAULT_ROOT_PATH = "setup.models.discrete_phase"
DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "output" / "settings_tree_maps" / "dpm_tree.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a live Fluent settings tree with optional archive comparison.")
    parser.add_argument("--server-id", default="3", help="Configured Fluent server id. Default: 3.")
    parser.add_argument("--case-path", default="", help="Optional remote .cas.h5 to load before probing.")
    parser.add_argument("--data-path", default="", help="Optional remote .dat.h5 to load before probing.")
    parser.add_argument("--root-path", default=DEFAULT_ROOT_PATH, help=f"Live settings root to map. Default: {DEFAULT_ROOT_PATH}.")
    parser.add_argument("--seed-json", default=str(DEFAULT_SEED_JSON), help="Optional local seed JSON to compare against.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="Optional local JSON path for the mapped tree.")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum recursion depth for the live capture.")
    parser.add_argument("--no-state", action="store_true", help="Skip state readback and capture only the tree shape.")
    parser.add_argument("--skip-dpm-activation", action="store_true", help="Do not attempt to enable DPM before probing the DPM root.")
    return parser


def split_path(path_text: str) -> list[str]:
    return [part for part in path_text.split(".") if part]


def resolve_path(root: Any, path_parts: list[str]) -> Any:
    obj = root
    for part in path_parts:
        obj = getattr(obj, part)
    return obj


def normalize_seed_path(path_parts: list[str]) -> list[str]:
    if len(path_parts) >= 2 and path_parts[0] == "setup" and path_parts[1] == "models":
        return path_parts[2:]
    return path_parts


def resolve_seed_subtree(seed_tree: Any, path_parts: list[str]) -> Any:
    if not path_parts:
        return seed_tree

    node = seed_tree
    for part in path_parts:
        if isinstance(node, dict):
            if part in node:
                node = node[part]
                continue
            children = node.get("children")
            if isinstance(children, dict) and part in children:
                node = children[part]
                continue
        raise KeyError(f"Seed tree does not contain path: {'.'.join(path_parts)}")
    return node


def main() -> int:
    args = build_parser().parse_args()
    root_parts = split_path(args.root_path)
    if not root_parts:
        raise ValueError("--root-path must not be empty")

    solver = connect(server_id=args.server_id)
    print(f"Connected to Fluent {solver.get_fluent_version()}")

    if args.case_path:
        if args.data_path:
            load_remote_case_data(solver, args.case_path, args.data_path, [])
        else:
            solver.settings.file.read_case(file_name=args.case_path)
            print(f"Loaded case: {args.case_path}")

    if not args.skip_dpm_activation and "discrete_phase" in root_parts:
        print_header("DPM Preflight")
        enable_dpm_model_best_effort(solver)

    live_root = resolve_path(solver, root_parts)
    seed_tree = None
    if args.seed_json:
        seed_tree = load_json(Path(args.seed_json))
        seed_path = normalize_seed_path(root_parts)
        if seed_path:
            try:
                seed_tree = resolve_seed_subtree(seed_tree, seed_path)
            except KeyError as exc:
                print(f"seed_tree: unavailable ({exc})")
                seed_tree = None

    print_header("Tree Capture")
    live_tree = capture_settings_tree(
        live_root,
        args.root_path,
        max_depth=args.max_depth,
        include_state=not args.no_state,
        seed_tree=seed_tree,
    )

    comparison = compare_tree_shapes(live_tree, seed_tree, args.root_path) if seed_tree is not None else {
        "missing_children": [],
        "extra_children": [],
        "missing_objects": [],
        "extra_objects": [],
    }
    summary = {
        "root_path": args.root_path,
        "seed_json": args.seed_json or "",
        "comparison": comparison,
        "live_tree_meta": live_tree.get("_meta", {}),
    }
    payload = {
        "summary": summary,
        "live_tree": live_tree,
        "seed_tree": seed_tree,
    }

    output_path = Path(args.output_json).expanduser()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"wrote_json: {output_path}")
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

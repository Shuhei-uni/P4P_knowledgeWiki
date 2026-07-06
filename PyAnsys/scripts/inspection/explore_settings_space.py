#!/usr/bin/env python3
"""Generic recursive explorer for visible Fluent settings space.

This script is meant for the "no past record" case:
- connect to a live Fluent session
- optionally load a mesh
- choose a live root such as `setup`, `setup.models`, or `setup.boundary_conditions`
- recurse through whatever Fluent exposes via child/object names
- optionally compare the capture to an archived seed tree

It does not try to invent unknown parents. It only explores what the current
session exposes, which is the safest possible baseline for a build-sensitive
Fluent tree.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import ansys.fluent.core as pyfluent

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import load_json  # noqa: E402
from pyansys_fluent.setup_io import load_target_mesh  # noqa: E402
from pyansys_fluent.settings_tree_mapper import capture_settings_tree, compare_tree_shapes  # noqa: E402


DEFAULT_OUTPUT_JSON = PROJECT_ROOT / "output" / "settings_tree_maps" / "explore_settings_space.json"
DEFAULT_ROOT_PATH = "setup"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Recursively explore visible Fluent settings paths.")
    parser.add_argument("--server-id", default="3", help="Configured Fluent server id. Default: 3.")
    parser.add_argument("--fluent-exe", default="", help="Optional local Fluent executable to launch instead of using .env connection details.")
    parser.add_argument("--processor-count", type=int, default=2, help="Processor count for local launch. Default: 2.")
    parser.add_argument("--start-timeout", type=int, default=120, help="Seconds to wait for local server-info. Default: 120.")
    parser.add_argument("--mesh", default="", help="Optional remote .msh file to load before probing.")
    parser.add_argument("--root-path", default=DEFAULT_ROOT_PATH, help=f"Live settings root to map. Default: {DEFAULT_ROOT_PATH}.")
    parser.add_argument("--seed-json", default="", help="Optional local seed JSON to compare against.")
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON), help="Optional local JSON path for the mapped tree.")
    parser.add_argument("--max-depth", type=int, default=5, help="Maximum recursion depth for the live capture.")
    parser.add_argument("--no-state", action="store_true", help="Skip state readback and capture only tree shape.")
    parser.add_argument("--no-adaptive", action="store_true", help="Disable parent-activation heuristics and alias-aware rescans.")
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


def start_local_fluent(
    fluent_exe: Path,
    output_dir: Path,
    processor_count: int,
    timeout: int,
) -> tuple[subprocess.Popen[str], Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    server_info = output_dir / "server_info_explore_settings_space.txt"
    if server_info.exists():
        server_info.unlink()
    process = subprocess.Popen(
        [str(fluent_exe), "3ddp", f"-t{processor_count}", "-g", f"-sifile={server_info}"],
        stdin=subprocess.PIPE,
        stdout=(output_dir / "fluent_stdout.log").open("w", encoding="utf-8", errors="replace"),
        stderr=(output_dir / "fluent_stderr.log").open("w", encoding="utf-8", errors="replace"),
        cwd=str(output_dir),
        text=True,
    )
    deadline = time.time() + timeout
    while time.time() < deadline:
        if server_info.exists() and server_info.stat().st_size > 0:
            return process, server_info
        if process.poll() is not None:
            raise RuntimeError(f"Fluent exited early with code {process.returncode}")
        time.sleep(2)
    raise TimeoutError(f"Timed out waiting for server-info file: {server_info}")


def main() -> int:
    args = build_parser().parse_args()
    root_parts = split_path(args.root_path)
    if not root_parts:
        raise ValueError("--root-path must not be empty")

    local_process = None
    if args.fluent_exe:
        local_process, server_info = start_local_fluent(
            Path(args.fluent_exe),
            PROJECT_ROOT / "output" / "settings_tree_maps" / "explore_settings_space_local",
            args.processor_count,
            args.start_timeout,
        )
        solver = pyfluent.connect_to_fluent(
            server_info_file_name=str(server_info),
            allow_remote_host=False,
            cleanup_on_exit=False,
            start_transcript=True,
        )
    else:
        solver = connect(server_id=args.server_id)
        server_info = None
    print(f"Connected to Fluent {solver.get_fluent_version()}")

    if args.mesh:
        load_target_mesh(solver, args.mesh)

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

    live_tree = capture_settings_tree(
        live_root,
        args.root_path,
        max_depth=args.max_depth,
        include_state=not args.no_state,
        seed_tree=seed_tree,
        activate_parents=not args.no_adaptive,
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
        "activation_attempts": live_tree.get("_activation_attempts", []),
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
    solver.exit()
    if local_process is not None and local_process.poll() is None:
        local_process.terminate()
        local_process.wait(timeout=20)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

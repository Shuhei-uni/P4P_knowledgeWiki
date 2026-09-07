#!/usr/bin/env python3
"""Print selected Fluent TUI tree attributes for discovery."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def public_attrs(obj: Any) -> list[str]:
    return sorted(name for name in dir(obj) if not name.startswith("_"))


def descend(root: Any, path: str) -> Any:
    obj = root
    for part in [p for p in path.split(".") if p]:
        obj = getattr(obj, part)
    return obj


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="define.models")
    args = parser.parse_args()

    load_dotenv()
    solver = connect()
    obj = descend(solver.tui, args.path)
    payload = {
        "path": args.path,
        "attrs": public_attrs(obj),
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

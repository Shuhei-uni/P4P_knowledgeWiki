#!/usr/bin/env python3
"""List Fluent TUI zone-management commands without changing the loaded case."""

from __future__ import annotations

import sys
import inspect
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def public_names(value: object) -> list[str]:
    return sorted(name for name in dir(value) if not name.startswith("_"))


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    solver = connect(server_id="1")
    for label, branch in (
        ("mesh.modify_zones", solver.tui.mesh.modify_zones),
        ("define.boundary_conditions", solver.tui.define.boundary_conditions),
    ):
        print(f"[{label}]")
        for name in public_names(branch):
            print(name)
    for label, command in (
        ("mesh.modify_zones.zone_name", solver.tui.mesh.modify_zones.zone_name),
        (
            "define.boundary_conditions.rename_zone",
            solver.tui.define.boundary_conditions.rename_zone,
        ),
        ("define.boundary_conditions.zone_type", solver.tui.define.boundary_conditions.zone_type),
    ):
        print(f"[{label} signature]")
        try:
            print(inspect.signature(command))
        except Exception as exc:
            print(f"unavailable: {type(exc).__name__}: {exc}")
        print(getattr(command, "__doc__", ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

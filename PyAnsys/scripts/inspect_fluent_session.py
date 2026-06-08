#!/usr/bin/env python3
"""Inspect a connected Fluent session without intentionally modifying the case.

Run after scripts/check_connection.py succeeds.

The exact object model can vary by Fluent/PyFluent version, so this script uses
try/except and prints whatever it can find.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow importing check_connection.py from the same folder.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_connection import connect  # noqa: E402


def try_print(label: str, func):
    print(f"\n--- {label} ---")
    try:
        value = func()
        print(value)
    except Exception as exc:
        print(f"Could not retrieve {label}: {exc}")


def main() -> int:
    solver = connect()
    print("\nConnected. Inspecting session...")

    try_print("Fluent version", lambda: solver.get_fluent_version())

    # TUI fallback probes are often more stable across versions.
    try_print("Working directory", lambda: solver.tui.file.show_configuration())

    # Common settings API probes. These may need adjustment for your Fluent version/case.
    try_print("Setup object", lambda: solver.settings.setup)
    try_print("Boundary conditions object", lambda: solver.settings.setup.boundary_conditions)
    try_print("Models object", lambda: solver.settings.setup.models)
    try_print("Materials object", lambda: solver.settings.setup.materials)

    print("\nInspection finished. This script did not intentionally modify the case.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

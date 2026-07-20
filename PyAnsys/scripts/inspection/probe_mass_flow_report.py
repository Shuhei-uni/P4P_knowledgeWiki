#!/usr/bin/env python3
"""Probe Fluent mass-flow report selectors on the currently loaded case."""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", default="1")
    args = parser.parse_args()

    solver = connect(server_id=args.server_id)
    command = solver.settings.results.report.fluxes.mass_flow
    zones = ["liquidinlet", "steaminlet", "steamoutlet"]
    selectors = [
        {"domain": "phase-1", "zones": zones},
        {"domain": "phase-2", "zones": zones},
        {"domain": "mixture", "physics": ["phase-1"], "zones": zones},
        {"domain": "mixture", "physics": ["phase-2"], "zones": zones},
    ]
    for selector in selectors:
        buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer):
                command(**selector)
            print(f"SELECTOR {selector}")
            print(buffer.getvalue().rstrip())
        except Exception as exc:
            print(f"SELECTOR {selector} ERROR {type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

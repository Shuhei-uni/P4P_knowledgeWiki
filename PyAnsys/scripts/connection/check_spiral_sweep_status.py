#!/usr/bin/env python3
"""Report the local status of the 2026-07-25 spiral-inlet enthalpy sweep."""

from __future__ import annotations

import sys
from pathlib import Path

import check_sweep_status


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SPIRAL_OUTPUT_DIR = PROJECT_ROOT / "output" / "spiral_enthalpy_sweep_20260725"


def add_default_output_dir(argv: list[str]) -> list[str]:
    if any(argument == "--output-dir" or argument.startswith("--output-dir=") for argument in argv):
        return argv
    return [*argv, "--output-dir", str(SPIRAL_OUTPUT_DIR)]


if __name__ == "__main__":
    sys.argv = add_default_output_dir(sys.argv)
    raise SystemExit(check_sweep_status.main())

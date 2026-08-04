#!/usr/bin/env python3
"""Run the six-case Purnanto sweep using the spiral-inlet Fluent baseline."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parents[1]

import run_purnanto_enthalpy_sweep as sweep


SPIRAL_INJECTION_NAMES = (
    "injection-5-micron",
    "injection-28-micron",
    "injection-56-micron",
    "injection-112-micron",
    "injection-168-micron",
    "injection-348-micron",
    "injection-562-micron",
    "injection-844-micron",
    "injection-1631-micron",
)

DEFAULTS = {
    "--base-case": r"C:\Users\qtra338\Documents\baseline_spiral_inlet.cas.h5",
    "--harwell-csv": str(REPO_ROOT / "Code" / "spiral_harwell_results.csv"),
    "--remote-output-dir": r"C:\Users\qtra338\Documents\spiral_enthalpy_sweep_20260725",
    "--local-output-dir": str(PROJECT_ROOT / "output" / "spiral_enthalpy_sweep_20260725"),
    "--inlet-name": "inlet",
    "--outlet-name": "outlet",
    "--particle-material": "liquid-water",
    "--injection-surface": "inlet",
    "--injection-names": ",".join(SPIRAL_INJECTION_NAMES),
    "--dpm-velocity-mode": "face-normal",
}


def apply_defaults(argv: list[str]) -> list[str]:
    result = list(argv)
    present = {argument.split("=", 1)[0] for argument in result if argument.startswith("--")}
    for option, value in DEFAULTS.items():
        if option not in present:
            result.extend((option, value))
    return result


if __name__ == "__main__":
    sys.argv = apply_defaults(sys.argv)
    raise SystemExit(sweep.main())

#!/usr/bin/env python3
"""Retry the zero-step matched 0.05%-feed run under a new evidence label."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


source.RUN_LABEL = (
    "brine620k_07n_server2_step90_targetpressure_for0p05_0p05feed_"
    "dt128em6_inner100_steps10_attempt2_20260825"
)


if __name__ == "__main__":
    raise SystemExit(source.main())

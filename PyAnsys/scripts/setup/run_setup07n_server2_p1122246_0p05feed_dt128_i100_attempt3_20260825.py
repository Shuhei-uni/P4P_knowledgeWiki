#!/usr/bin/env python3
"""Retry matched 0.05%-feed drainage with a Windows-safe short label."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


source.RUN_LABEL = "brine620k_07n_s2_p1122246_0p05feed_dt128_i100_s10_a3_20260825"


if __name__ == "__main__":
    raise SystemExit(source.main())

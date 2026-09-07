#!/usr/bin/env python3
"""Retry delayed feedback with short evidence names after path-hash failures."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_adaptive_pressure_delay10_dt128_i100_s50_20260826 as source  # noqa: E402


source.RUN_LABEL = "b620_07n_s2_0p05_apd10_g25_dt128_i100_s50_a3_20260826"
source.MEMBER = "f0p05_apd10"


if __name__ == "__main__":
    raise SystemExit(source.main())

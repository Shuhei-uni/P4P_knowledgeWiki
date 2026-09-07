#!/usr/bin/env python3
"""Retry the stopped delayed-controller diagnostic under fresh evidence paths.

Attempt 1 stopped after one fully monitored step because its remote checkpoint
hash command returned no output.  This wrapper changes only the attempt label;
the clean parent, controller, feed, timestep, budget and gates are identical.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_server2_0p05feed_adaptive_pressure_delay10_dt128_i100_s50_20260826 as source  # noqa: E402


source.RUN_LABEL = (
    "brine620k_07n_s2_0p05feed_adaptivep_delay10_g0p25_dp5_"
    "dt128_i100_s50_a2_20260826"
)


if __name__ == "__main__":
    raise SystemExit(source.main())

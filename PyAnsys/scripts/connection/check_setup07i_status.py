#!/usr/bin/env python3
"""Report setup-07i WFGC sensitivity status and Fluent health read-only."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_setup07h_status as base  # noqa: E402


base.RUN_ROOT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_resolved_brine_outlet_20260813"
    / "brine620k_07i_pool_y0_equal_psep_wfgc_v1"
)
base.SETUP_LABEL = "07i"


if __name__ == "__main__":
    raise SystemExit(base.main())

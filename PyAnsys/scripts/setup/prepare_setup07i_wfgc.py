#!/usr/bin/env python3
"""Prepare the clean setup-07i WFGC-only sensitivity."""

from __future__ import annotations

from pathlib import Path

import prepare_setup07h_brine_pool as base


base.RUN_LABEL = "brine620k_07i_pool_y0_equal_psep_wfgc_v1"
base.LOCAL_ROOT = (
    base.PROJECT_ROOT
    / "output"
    / base.STUDY_ID
    / base.RUN_LABEL
)
base.ENABLE_WFGC = True


if __name__ == "__main__":
    raise SystemExit(base.main())

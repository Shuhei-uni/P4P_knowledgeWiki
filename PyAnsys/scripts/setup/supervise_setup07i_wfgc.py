#!/usr/bin/env python3
"""Run exactly one supervised setup-07i WFGC sensitivity."""

from __future__ import annotations

import supervise_setup07h_brine_pool as base


base.RUN_LABEL = "brine620k_07i_pool_y0_equal_psep_wfgc_v1"
base.RUN_ROOT = (
    base.PROJECT_ROOT
    / "output"
    / base.STUDY_ID
    / base.RUN_LABEL
)
base.SUPERVISOR_MANIFEST = base.RUN_ROOT / "supervisor_manifest.json"
base.READINESS_LOG = base.RUN_ROOT / "supervisor_readiness.log"
base.PREPARATION_MANIFEST = base.RUN_ROOT / "preparation_manifest.json"
base.QUALIFICATION_MANIFEST = base.RUN_ROOT / "qualification_manifest.json"
base.SETUP_LABEL = "07i"
base.STATUS_SCRIPT = "scripts/connection/check_setup07i_status.py"
base.PREPARATION_SCRIPT = "scripts/setup/prepare_setup07i_wfgc.py"
base.QUALIFICATION_SCRIPT = "scripts/setup/run_setup07i_wfgc_qualification.py"
base.READINESS_REQUIRED = False
base.PREPARATION_IDLE_TIMEOUT_SECONDS = 600.0


if __name__ == "__main__":
    raise SystemExit(base.main())

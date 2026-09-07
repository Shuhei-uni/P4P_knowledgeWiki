#!/usr/bin/env python3
"""Run the guarded setup-07i WFGC-only sensitivity."""

from __future__ import annotations

import prepare_setup07i_wfgc as prepare
import run_setup07h_brine_pool_qualification as base


base.STUDY_ID = prepare.base.STUDY_ID
base.RUN_LABEL = prepare.base.RUN_LABEL
base.REMOTE_ROOT = prepare.base.REMOTE_ROOT
base.LOCAL_ROOT = prepare.base.LOCAL_ROOT
base.PREPARATION_MANIFEST = base.LOCAL_ROOT / "preparation_manifest.json"
base.REQUIRE_WFGC = True
base.ENABLE_GROSS_PHYSICAL_GATE = True


if __name__ == "__main__":
    raise SystemExit(base.main())

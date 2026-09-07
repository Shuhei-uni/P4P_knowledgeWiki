#!/usr/bin/env python3
"""Run setup-07k using the guarded setup-07j transient qualification engine."""

from __future__ import annotations

import prepare_setup07k_transient_vof_massflow_outlet as prepare07k
import run_setup07j_transient_vof_qualification as engine


engine.prepare07j = prepare07k
engine.STUDY_ID = prepare07k.STUDY_ID
engine.RUN_LABEL = prepare07k.RUN_LABEL
engine.REMOTE_ROOT = prepare07k.REMOTE_ROOT
engine.LOCAL_ROOT = prepare07k.LOCAL_ROOT
engine.PREPARATION_MANIFEST = prepare07k.LOCAL_ROOT / "preparation_manifest.json"
engine.TIME_STEP_SIZE_S = prepare07k.TIME_STEP_SIZE_S
engine.MAX_ITERATIONS_PER_TIME_STEP = prepare07k.MAX_ITERATIONS_PER_TIME_STEP


if __name__ == "__main__":
    raise SystemExit(engine.main())

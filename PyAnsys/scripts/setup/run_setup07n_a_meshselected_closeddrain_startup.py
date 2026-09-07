#!/usr/bin/env python3
"""Run the fresh setup-07n mesh-selected closed-drain startup lineage."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402


RUN_LABEL = "brine620k_07n_a_closeddrain_meshselected_startup_attempt1_20260822"

pilot.RUN_LABEL = RUN_LABEL
pilot.LOCAL_ROOT = pilot.PROJECT_ROOT / "output" / pilot.STUDY_ID / RUN_LABEL
pilot.STAGE0_MANIFEST = (
    pilot.PROJECT_ROOT
    / "output"
    / pilot.STUDY_ID
    / "brine620k_07n_stage0_geometry_v1"
    / "brine620k_07n_stage0_pool_selection_plateau_attempt4_20260822.json"
)
pilot.EXPECTED_STAGE0_SHA256 = (
    "d3e1b4b559420feb1c19c0054d21a075b27300324189c59976b01f0ccdbaced5"
)
pilot.TARGET_LEVEL_Y_M = 0.01645836558472365
pilot.REGISTER_NAME = "setup07n_a_meshselected_startup_attempt1_pool"
pilot.CANDIDATE_MODE = "mesh-selection-plateau"
pilot.CANDIDATE_BASIS = (
    "center of the exact whole-cell threshold plateau that selects 98,473 cells"
)
pilot.CANDIDATE_LIMITATION = (
    "CFD-defined diagnostic level; not a measured plant water level and not a "
    "direct volume-cell vertex-height measurement"
)
pilot.RUN_CLASSIFICATION = "diagnostic / unresolved mesh-selected closed-drain startup"
pilot.FINAL_CLASSIFICATION = (
    "diagnostic / unresolved mesh-selected closed-drain bounded startup"
)
pilot.GRAVITY_TIME_SCALE_NOTE = (
    "10 us is only a guarded startup; local gravity scale is about 0.0428 s"
)
pilot.ACCEPTANCE_LIMITATION = (
    "Ten microseconds proves the fresh mesh-selected time-zero lineage and guarded "
    "startup only; it is not a physically relaxed pool or an open-drain result."
)
pilot.ELIGIBILITY_SCOPE = (
    "same mesh-selected closed-drain diagnostic lineage, conservative dt extension only"
)


if __name__ == "__main__":
    raise SystemExit(pilot.main())

#!/usr/bin/env python3
"""Extend the mesh-selected closed-drain lineage at dt=2e-6 s."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


RUN_LABEL = "brine620k_07n_a_closeddrain_meshselected_dt2em6_extension_attempt1_20260822"
PARENT_LABEL = "brine620k_07n_a_closeddrain_meshselected_startup_attempt1_20260822"

extension.RUN_LABEL = RUN_LABEL
extension.LOCAL_ROOT = extension.PROJECT_ROOT / "output" / extension.STUDY_ID / RUN_LABEL
extension.PARENT_LABEL = PARENT_LABEL
extension.PARENT_CASE = (
    extension.REMOTE_ROOT + rf"\{PARENT_LABEL}_checkpoint_step10.cas.h5"
)
extension.PARENT_DATA = (
    extension.REMOTE_ROOT + rf"\{PARENT_LABEL}_checkpoint_step10.dat.h5"
)
extension.EXPECTED_PARENT_CASE_SHA256 = (
    "53418365ec234cf323b66a9d7046d1591de545adb4cb029724e724132d6cc5b1"
)
extension.EXPECTED_PARENT_DATA_SHA256 = (
    "73565aee2d3ab049bcc7b415c8bbc00ec3599ef597b9a1b5f860da97bb61a7a1"
)
extension.INITIAL_TIME_STEP = 10
extension.INITIAL_FLOW_TIME_S = 1.0e-5
extension.TIME_STEP_SIZE_S = 2.0e-6
extension.INNER_ITERATIONS = 20
extension.ADDITIONAL_STEPS = 10
extension.CHECKPOINT_ADDITIONAL_STEPS = {1, 5, 10}
extension.RUN_CLASSIFICATION = (
    "diagnostic / unresolved mesh-selected closed-drain dt extension"
)
extension.FINAL_CLASSIFICATION = (
    "diagnostic / unresolved mesh-selected closed-drain dt2em6 startup"
)
extension.ONE_FACTOR_CHANGE = "physical dt 1e-6 s -> 2e-6 s"
extension.UNCHANGED_CONTRACT = (
    "mesh-selected startup step-10 field; zero feed; brine wall; steam pressure "
    "outlet; transient explicit VOF; PISO/PRESTO/Geo-Reconstruct/WFGC; RNG "
    "k-epsilon; Energy off; DPM zero/off; EWF off; no sources/sinks"
)
extension.PARENT_ELIGIBILITY_SCOPE = (
    "same mesh-selected closed-drain diagnostic lineage only"
)
extension.ACCEPTANCE_LIMITATION = (
    "30 us cumulative time remains startup-only; closed drain and CFD-defined "
    "diagnostic level do not establish constant-level operation"
)
extension.NEXT_ELIGIBILITY_SCOPE = (
    "same mesh-selected closed-drain diagnostic lineage, next conservative 2x dt only"
)
extension.SAVE_TAG = "07n_a_meshselected_dt2em6"
extension.PRINT_LABEL = "07n-a mesh-selected dt2e-6 extension"


if __name__ == "__main__":
    raise SystemExit(extension.main())

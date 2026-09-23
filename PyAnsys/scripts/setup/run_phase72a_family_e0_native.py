#!/usr/bin/env python3
"""Run the Phase 7.2A Family E0 no-film control on the student endpoint."""

from pathlib import PureWindowsPath

import run_phase72a_family_r_native as native


native.SERVER_ID = "student"
native.FAMILY_ID = "P72A-Family-E"
native.FAMILY_LABEL = "E0-smooth-EWF-off-control"
native.SETUP_ID_PREFIX = "P72A-FAMILY-E"
native.PARENT_CASE = (
    "C:/Users/Shuhei Yokkaichi/Documents/FluentRuns/Phase72A/FamilyE/"
    "parent-transfer-20260922T115133Z/"
    "P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-"
    "full-loading-plus1000.cas.h5"
)
native.PARENT_DATA = native.PARENT_CASE.replace(".cas.h5", ".dat.h5")
native.REMOTE_LOCAL_ROOT = PureWindowsPath(
    r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE"
)
native.REMOTE_FINAL_ROOT = PureWindowsPath(
    r"C:\Users\Shuhei Yokkaichi\Documents\OneDrive - The University of Auckland"
    r"\P4P-Fluent-Artifacts\Phase72A\FamilyE"
)
native.CASES = (("E0", 0.0, 0.5),)


if __name__ == "__main__":
    raise SystemExit(native.main())

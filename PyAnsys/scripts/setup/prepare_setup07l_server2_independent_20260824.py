#!/usr/bin/env python3
"""Prepare a unique, independent setup-07l isolation carrier on server 2."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from inspect_setup07n_mesh_geometry import exclusive_writer_lock  # noqa: E402
import prepare_setup07j_transient_vof as source07j  # noqa: E402

source07j.RUN_LABEL = "brine620k_07j_transient_vof_independent_attempt2_20260824"

import prepare_setup07l_hydrostatic_rest as preparation  # noqa: E402

preparation.RUN_LABEL = "brine620k_07l_hydrostatic_rest_independent_attempt2_20260824"
LOCK_PATH = (
    PROJECT_ROOT
    / "output"
    / preparation.STUDY_ID
    / "setup07n_server2_independent_writer.lock"
)


if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--server-id", "2"]
    with exclusive_writer_lock(LOCK_PATH):
        raise SystemExit(preparation.main())

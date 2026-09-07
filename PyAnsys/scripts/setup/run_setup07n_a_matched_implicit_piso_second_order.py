#!/usr/bin/env python3
"""Run the matched implicit-VOF/PISO second-order-time sensitivity."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_matched_implicit_piso as implicit  # noqa: E402


implicit.RUN_LABEL = (
    "brine620k_07n_a_closeddrain_matchedwindow_implicit_piso_"
    "compressive_secondorder_dt256em6_steps20_attempt1_20260823"
)
implicit.TARGET_TRANSIENT_FORMULATION = "unsteady-2nd-order"
implicit.RUN_CLASSIFICATION = (
    "diagnostic / unresolved matched-window implicit-VOF second-order-time sensitivity"
)
implicit.FINAL_CLASSIFICATION = implicit.RUN_CLASSIFICATION
implicit.ONE_FACTOR_CHANGE = (
    "implicit-VOF transient formulation first-order -> second-order at fixed "
    "dt=2.56e-4 s, 20 inner iterations, PISO/PRESTO/Compressive and identical "
    "closed-pool physics"
)
implicit.UNCHANGED_CONTRACT = (
    "exact accepted explicit step-940 field; zero feed; closed brine wall; "
    "steam pressure outlet; implicit VOF; PISO/PRESTO/Compressive/WFGC; RNG "
    "k-epsilon; Energy off; DPM zero/off; EWF off; no sources/sinks; no "
    "initialization"
)
implicit.ACCEPTANCE_LIMITATION = (
    "The endpoint is a closed-pool temporal-order diagnostic only. It does "
    "not select a solver, validate drainage or plant conditions, or establish "
    "time-step or mesh independence."
)
implicit.PRINT_LABEL = "07n-a implicit VOF/PISO second-order matched window"


if __name__ == "__main__":
    raise SystemExit(implicit.main())

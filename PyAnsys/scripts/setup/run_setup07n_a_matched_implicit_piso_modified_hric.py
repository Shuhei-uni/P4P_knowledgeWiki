#!/usr/bin/env python3
"""Run the matched implicit-VOF/PISO Modified-HRIC sensitivity."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_matched_implicit_piso as implicit  # noqa: E402


implicit.RUN_LABEL = (
    "brine620k_07n_a_closeddrain_matchedwindow_implicit_piso_"
    "modifiedhric_secondorder_dt256em6_steps20_attempt1_20260823"
)
implicit.TARGET_TRANSIENT_FORMULATION = "unsteady-2nd-order"
implicit.TARGET_VOF_SCHEME = "modified-hric"
implicit.RUN_CLASSIFICATION = (
    "diagnostic / unresolved matched-window implicit-VOF Modified-HRIC sensitivity"
)
implicit.FINAL_CLASSIFICATION = implicit.RUN_CLASSIFICATION
implicit.ONE_FACTOR_CHANGE = (
    "implicit-VOF interface discretization Compressive -> Modified-HRIC at "
    "fixed second-order time, dt=2.56e-4 s, 20 inner iterations, PISO/PRESTO "
    "and identical closed-pool physics"
)
implicit.UNCHANGED_CONTRACT = (
    "exact accepted explicit step-940 field; zero feed; closed brine wall; "
    "steam pressure outlet; implicit VOF; PISO/PRESTO/WFGC; second-order "
    "transient; RNG k-epsilon; Energy off; DPM zero/off; EWF off; no "
    "sources/sinks; no initialization"
)
implicit.ACCEPTANCE_LIMITATION = (
    "The endpoint is a closed-pool interface-discretization diagnostic only. "
    "It does not select a solver, validate drainage or plant conditions, or "
    "establish time-step or mesh independence."
)
implicit.PRINT_LABEL = "07n-a implicit VOF/PISO Modified-HRIC matched window"


if __name__ == "__main__":
    raise SystemExit(implicit.main())

#!/usr/bin/env python3
"""Run a matched closed-wall control from the clean server-2 setup-07n step 90.

This thin wrapper deliberately keeps the parent timestep, inner-iteration cap,
physics and boundaries unchanged.  It supplies the background relaxation
trajectory for the independent server-2 open-drain pressure comparison.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_a_server2_independent_step90_closed_control_"
    "dt256em6_steps10_attempt1_20260825"
)
PARENT_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_server2_independent_"
    "dt256em6_attempt1_20260824_additional_step10"
)
PARENT_CASE = extension.REMOTE_ROOT + rf"\{PARENT_LABEL}.cas.h5"
PARENT_DATA = extension.REMOTE_ROOT + rf"\{PARENT_LABEL}.dat.h5"
PARENT_CASE_SHA256 = (
    "763fae763ce43c36505c7dc06986082f361e257c93afc778b5583a41dd15fd22"
)
PARENT_DATA_SHA256 = (
    "9513a957ae42e59db076466754a226c44b7bfdfa7f8a69b40e44139fa2bae6b7"
)
INITIAL_TIME_STEP = 90
INITIAL_FLOW_TIME_S = 0.005110000000000003
TIME_STEP_SIZE_S = 2.56e-4


def server2_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("2",), default="2")
    parser.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return parser


def main() -> int:
    run_root = extension.PROJECT_ROOT / "output" / extension.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")

    extension.parser = server2_parser
    extension.RUN_LABEL = RUN_LABEL
    extension.PARENT_LABEL = PARENT_LABEL
    extension.PARENT_CASE = PARENT_CASE
    extension.PARENT_DATA = PARENT_DATA
    extension.EXPECTED_PARENT_CASE_SHA256 = PARENT_CASE_SHA256
    extension.EXPECTED_PARENT_DATA_SHA256 = PARENT_DATA_SHA256
    extension.INITIAL_TIME_STEP = INITIAL_TIME_STEP
    extension.INITIAL_FLOW_TIME_S = INITIAL_FLOW_TIME_S
    extension.TIME_STEP_SIZE_S = TIME_STEP_SIZE_S
    extension.INNER_ITERATIONS = 20
    extension.ADDITIONAL_STEPS = 10
    extension.CHECKPOINT_ADDITIONAL_STEPS = {1, 5, 10}
    extension.LOCAL_ROOT = run_root
    extension.GLOBAL_WRITER_LOCK = (
        extension.PROJECT_ROOT
        / "output"
        / extension.STUDY_ID
        / "setup07n_server2_independent_writer.lock"
    )
    extension.RUN_CLASSIFICATION = (
        "diagnostic / unresolved independent server-2 matched closed-wall control"
    )
    extension.FINAL_CLASSIFICATION = (
        "accepted diagnostic / independent server-2 matched closed-wall background control"
    )
    extension.ONE_FACTOR_CHANGE = (
        "none: matched same-dt, same-inner closed-wall continuation for background drift"
    )
    extension.UNCHANGED_CONTRACT = (
        "checksum-bound independent server-2 step-90 field; zero feed; brine wall; "
        "steam pressure outlet; transient explicit VOF; PISO/PRESTO/"
        "Geo-Reconstruct/WFGC; RNG k-epsilon; Energy off; DPM zero/off; "
        "EWF off; no sources/sinks"
    )
    extension.PARENT_ELIGIBILITY_SCOPE = (
        "independent server-2 diagnostic branching only; never server-1 lineage"
    )
    extension.ACCEPTANCE_LIMITATION = (
        "This is a matched closed-wall background control, not drainage, level "
        "control, operating mass balance or a server-1 lineage result."
    )
    extension.NEXT_ELIGIBILITY_SCOPE = (
        "comparison evidence only; endpoint is not an automatic parent"
    )
    extension.SAVE_TAG = "07n_a_server2_step90_closed_control"
    extension.PRINT_LABEL = "07n-a server2 matched closed control"

    sys.argv = [
        sys.argv[0],
        "--server-id",
        "2",
        "--tcp-timeout-seconds",
        "5.0",
    ]
    return extension.main()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the independent server-2 setup-07n zero-feed pressure-response bracket."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_c_server2_independent_step90_zero_feed_pressure_bracket_"
    "dt256em6_steps10_attempt2_20260825"
)
PARENT_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_server2_independent_"
    "dt256em6_attempt1_20260824_additional_step10"
)
PARENT_CASE = probe.REMOTE_ROOT + rf"\{PARENT_LABEL}.cas.h5"
PARENT_DATA = probe.REMOTE_ROOT + rf"\{PARENT_LABEL}.dat.h5"
PARENT_CASE_SHA256 = (
    "763fae763ce43c36505c7dc06986082f361e257c93afc778b5583a41dd15fd22"
)
PARENT_DATA_SHA256 = (
    "9513a957ae42e59db076466754a226c44b7bfdfa7f8a69b40e44139fa2bae6b7"
)
INITIAL_TIME_STEP = 90
INITIAL_FLOW_TIME_S = 0.005110000000000003
CENTRE_PRESSURE_PA = 1_122_349.5


def server2_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("2",), default="2")
    parser.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return parser


def main() -> int:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")

    probe.parser = server2_parser
    probe.RUN_LABEL = RUN_LABEL
    probe.PARENT_LABEL = PARENT_LABEL
    probe.PARENT_CASE = PARENT_CASE
    probe.PARENT_DATA = PARENT_DATA
    probe.PARENT_CASE_SHA256 = PARENT_CASE_SHA256
    probe.PARENT_DATA_SHA256 = PARENT_DATA_SHA256
    probe.INITIAL_TIME_STEP = INITIAL_TIME_STEP
    probe.INITIAL_FLOW_TIME_S = INITIAL_FLOW_TIME_S
    probe.TIME_STEP_SIZE_S = 2.56e-4
    probe.INNER_ITERATIONS = 20
    probe.PHYSICAL_STEPS = 10
    probe.CHECKPOINT_STEPS = {1, 5, 10}
    probe.CENTRE_PRESSURE_PA = CENTRE_PRESSURE_PA
    probe.PRESSURE_MEMBERS = (
        ("centre", CENTRE_PRESSURE_PA),
        ("low", CENTRE_PRESSURE_PA - probe.PRESSURE_HALF_WIDTH_PA),
        ("high", CENTRE_PRESSURE_PA + probe.PRESSURE_HALF_WIDTH_PA),
    )
    probe.LOCAL_ROOT = run_root
    probe.GLOBAL_WRITER_LOCK = (
        probe.PROJECT_ROOT
        / "output"
        / probe.STUDY_ID
        / "setup07n_server2_independent_writer.lock"
    )
    # Scratch report paths contain a nanosecond suffix, so they cannot collide.
    # The immediately preceding closed-control attempt stalled only in the
    # optional post-read scratch-file deletion verification.  Retain those
    # unique remote scratch files for this campaign instead of issuing the
    # non-physical cleanup RPC; all physical reports and gates remain active.
    probe.sweep.remote_delete_best_effort = lambda _solver, _path: True

    sys.argv = [
        sys.argv[0],
        "--server-id",
        "2",
        "--tcp-timeout-seconds",
        "5.0",
    ]
    return probe.main()


if __name__ == "__main__":
    raise SystemExit(main())

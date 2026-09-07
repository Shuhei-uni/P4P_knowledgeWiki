#!/usr/bin/env python3
"""Continue the independent server-2 whole-cell pool at dt=2e-6 s.

This is a one-factor time-step extension of the checksum-bound independent
server-2 startup.  It is not part of the authoritative server-1 lineage.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_server2_independent_"
    "dt2em6_attempt1_20260824"
)
PARENT_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_"
    "server2_independent_startup_attempt2_20260824"
)


def server2_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("2",), default="2")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


extension.parser = server2_parser
extension.RUN_LABEL = RUN_LABEL
extension.PARENT_LABEL = PARENT_LABEL
extension.PARENT_CASE = extension.REMOTE_ROOT + rf"\{PARENT_LABEL}_checkpoint_step10.cas.h5"
extension.PARENT_DATA = extension.REMOTE_ROOT + rf"\{PARENT_LABEL}_checkpoint_step10.dat.h5"
extension.EXPECTED_PARENT_CASE_SHA256 = (
    "ed6eefafbefe6296ece5a702c26a7f243d8cb046884bd70d56c02a50f6addbaf"
)
extension.EXPECTED_PARENT_DATA_SHA256 = (
    "844f0ca3ef6600150b7b0d2cb9e65484a11b0c5341c4b2b1b7e3ec0a2c2ba65b"
)
extension.LOCAL_ROOT = extension.PROJECT_ROOT / "output" / extension.STUDY_ID / RUN_LABEL
extension.GLOBAL_WRITER_LOCK = (
    extension.PROJECT_ROOT
    / "output"
    / extension.STUDY_ID
    / "setup07n_server2_independent_writer.lock"
)
extension.RUN_CLASSIFICATION = (
    "diagnostic / unresolved independent server-2 whole-cell dt extension"
)
extension.FINAL_CLASSIFICATION = (
    "diagnostic / unresolved independent server-2 whole-cell dt2em6 startup"
)
extension.ONE_FACTOR_CHANGE = "physical dt 1e-6 s -> 2e-6 s"
extension.UNCHANGED_CONTRACT = (
    "independent server-2 step-10 field; accepted exact whole-cell pool; zero feed; "
    "brine wall; steam pressure outlet; transient explicit VOF; "
    "PISO/PRESTO/Geo-Reconstruct/WFGC; RNG k-epsilon; Energy off; "
    "DPM zero/off; EWF off; no sources/sinks"
)
extension.PARENT_ELIGIBILITY_SCOPE = (
    "same independent server-2 closed-pool reconstruction only"
)
extension.ACCEPTANCE_LIMITATION = (
    "30 us cumulative time remains guarded startup; the branch is an independent "
    "server-2 reconstruction and is ineligible for the server-1 lineage"
)
extension.NEXT_ELIGIBILITY_SCOPE = (
    "same independent server-2 closed-pool reconstruction, next conservative 2x dt only"
)
extension.SAVE_TAG = "07n_a_server2_independent_dt2em6"
extension.PRINT_LABEL = "07n-a server2 independent dt2e-6"


if __name__ == "__main__":
    sys.argv = [
        sys.argv[0],
        "--server-id",
        "2",
        "--tcp-timeout-seconds",
        "5",
    ]
    raise SystemExit(extension.main())

#!/usr/bin/env python3
"""Reconstruct the whole-cell 07n pool for an independent server-2 startup.

This branch is intentionally non-authoritative. It uses the same mesh,
settings and accepted whole-cell pool definition but does not possess the
checksum-bound server-1 step-940 data field. Its outputs may support an
independent sensitivity only and must never be substituted into the server-1
lineage without a separate equivalence adjudication.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_a_closeddrain_meshselected_"
    "server2_independent_startup_attempt2_20260824"
)
SOURCE_07L_LABEL = (
    "brine620k_07l_hydrostatic_rest_independent_attempt2_20260824_server2"
)


def server2_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("2",), default="2")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


pilot.parser = server2_parser
pilot.RUN_LABEL = RUN_LABEL
pilot.LOCAL_ROOT = pilot.PROJECT_ROOT / "output" / pilot.STUDY_ID / RUN_LABEL
pilot.GLOBAL_WRITER_LOCK = (
    pilot.PROJECT_ROOT
    / "output"
    / pilot.STUDY_ID
    / "setup07n_server2_independent_writer.lock"
)
pilot.REMOTE_CARRIER_CASE = (
    pilot.REMOTE_ROOT + rf"\{SOURCE_07L_LABEL}_initialized_t0.cas.h5"
)
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
pilot.REGISTER_NAME = "setup07n_a_server2_independent_attempt2_pool"
pilot.CANDIDATE_MODE = "mesh-selection-plateau"
pilot.CANDIDATE_BASIS = (
    "accepted exact whole-cell threshold plateau selecting 98,473 cells"
)
pilot.CANDIDATE_LIMITATION = (
    "independent server-2 reconstruction; not the checksum-bound server-1 "
    "step-940 field and not a measured plant level"
)
pilot.RUN_CLASSIFICATION = (
    "diagnostic / unresolved independent server-2 whole-cell startup"
)
pilot.FINAL_CLASSIFICATION = (
    "diagnostic / unresolved independent server-2 bounded startup"
)
pilot.GRAVITY_TIME_SCALE_NOTE = (
    "10 us is guarded startup only; local gravity scale is about 0.0428 s"
)
pilot.ACCEPTANCE_LIMITATION = (
    "This reconstructs only an independent server-2 startup. It is not "
    "physically relaxed, open-draining, or eligible for the server-1 lineage."
)
pilot.ELIGIBILITY_SCOPE = (
    "same independent server-2 closed-pool reconstruction only"
)


if __name__ == "__main__":
    sys.argv = [
        sys.argv[0],
        "--server-id",
        "2",
        "--tcp-timeout-seconds",
        "5",
    ]
    raise SystemExit(pilot.main())

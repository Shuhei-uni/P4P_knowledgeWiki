#!/usr/bin/env python3
"""Run the bounded matched-window implicit-VOF/PISO setup-07n-a comparison.

The runner cold-loads the checksum-bound accepted explicit step-940 parent,
changes only the VOF formulation to implicit (which Fluent 2024 R2
automatically pairs with Compressive volume-fraction discretization), and
advances 20 guarded physical steps at the parent's dt and inner-iteration cap.
Every output is diagnostic/unresolved and ineligible as a continuation parent
until the explicit/implicit endpoint comparison is separately adjudicated.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_a_closeddrain_matchedwindow_implicit_piso_"
    "compressive_dt256em6_steps20_attempt1_20260823"
)
PARENT_STEM = (
    extension.REMOTE_ROOT
    + r"\brine620k_07n_a_closeddrain_meshselected_dt256em6_"
    r"hold100_stage8_attempt1_20260823_additional_step100"
)
PARENT_CASE_SHA256 = (
    "03383ac0e1674b7a2acd47fc65ca84033c907f960bc3a4ace912e4902ce6c7c9"
)
PARENT_DATA_SHA256 = (
    "a5963dfada0754dd24685b699a65ac341d90b9ce0c3dda11879863eb9ff0772a"
)
TARGET_TRANSIENT_FORMULATION = "unsteady-1st-order"
TARGET_VOF_SCHEME = "compressive"
RUN_CLASSIFICATION = (
    "diagnostic / unresolved matched-window implicit-VOF/PISO comparison"
)
FINAL_CLASSIFICATION = RUN_CLASSIFICATION
ONE_FACTOR_CHANGE = (
    "VOF formulation explicit -> implicit at fixed dt=2.56e-4 s and 20 "
    "inner iterations; Fluent's automatic Geo-Reconstruct -> Compressive "
    "switch is the required formulation-linked discretization change"
)
UNCHANGED_CONTRACT = (
    "exact accepted explicit step-940 field; zero feed; closed brine wall; "
    "steam pressure outlet; PISO/PRESTO/WFGC; first-order transient; RNG "
    "k-epsilon; Energy off; DPM zero/off; EWF off; no sources/sinks; no "
    "initialization"
)
ACCEPTANCE_LIMITATION = (
    "The endpoint is a closed-pool solver/formulation diagnostic only. It "
    "does not validate constant-level drainage, the plant brine pressure, "
    "or mesh/time-step independence, and it is nonpromotable until a "
    "separate matched comparison is adjudicated."
)
PRINT_LABEL = "07n-a implicit VOF/PISO matched window"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def main() -> int:
    args = parser().parse_args()
    extension.RUN_LABEL = RUN_LABEL
    extension.LOCAL_ROOT = (
        extension.PROJECT_ROOT / "output" / extension.STUDY_ID / RUN_LABEL
    )
    extension.PARENT_LABEL = Path(PARENT_STEM.replace("\\", "/")).name
    extension.PARENT_CASE = PARENT_STEM + ".cas.h5"
    extension.PARENT_DATA = PARENT_STEM + ".dat.h5"
    extension.EXPECTED_PARENT_CASE_SHA256 = PARENT_CASE_SHA256
    extension.EXPECTED_PARENT_DATA_SHA256 = PARENT_DATA_SHA256
    extension.INITIAL_TIME_STEP = 940
    extension.INITIAL_FLOW_TIME_S = 0.2227100000000037
    extension.TIME_STEP_SIZE_S = 2.56e-4
    extension.INNER_ITERATIONS = 20
    extension.ADDITIONAL_STEPS = 20
    extension.CHECKPOINT_ADDITIONAL_STEPS = {1, 5, 10, 20}
    extension.VOF_FORMULATION = "implicit"
    extension.EXPECTED_VOF_SCHEME = TARGET_VOF_SCHEME
    extension.EXPECTED_TRANSIENT_FORMULATION = TARGET_TRANSIENT_FORMULATION
    extension.COURANT_FIELD = "cell-convective-courant-number"
    extension.ENDPOINT_ELIGIBILITY_ALLOWED = False
    extension.RUN_CLASSIFICATION = RUN_CLASSIFICATION
    extension.FINAL_CLASSIFICATION = FINAL_CLASSIFICATION
    extension.ONE_FACTOR_CHANGE = ONE_FACTOR_CHANGE
    extension.UNCHANGED_CONTRACT = UNCHANGED_CONTRACT
    extension.PARENT_ELIGIBILITY_SCOPE = (
        "accepted explicit closed-pool diagnostic comparisons only"
    )
    extension.ACCEPTANCE_LIMITATION = ACCEPTANCE_LIMITATION
    extension.NEXT_ELIGIBILITY_SCOPE = (
        "none; endpoint comparison and adjudication required before reuse"
    )
    extension.SAVE_TAG = "07n_a_matched_implicit_piso"
    extension.PRINT_LABEL = PRINT_LABEL

    sys.argv = [
        sys.argv[0],
        "--server-id",
        args.server_id,
        "--tcp-timeout-seconds",
        str(args.tcp_timeout_seconds),
    ]
    return extension.main()


if __name__ == "__main__":
    raise SystemExit(main())

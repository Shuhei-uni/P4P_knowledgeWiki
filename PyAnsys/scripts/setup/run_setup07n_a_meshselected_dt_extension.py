#!/usr/bin/env python3
"""Run one checksum-bound guarded one-factor stage of the mesh-selected 07n-a lineage.

The scheduler permits an unchanged hold, one conservative 2x increase, or a
matched half-/quarter-/eighth-dt sensitivity. At unchanged dt it may instead
test a larger inner-iteration cap. Every branch remains diagnostic/unresolved
until its endpoint is compared and adjudicated outside this runner.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--run-label", required=True)
    result.add_argument(
        "--parent-stem",
        required=True,
        help="Exact remote parent path without .cas.h5/.dat.h5 suffix",
    )
    result.add_argument("--parent-case-sha256", required=True)
    result.add_argument("--parent-data-sha256", required=True)
    result.add_argument("--initial-time-step", type=int, required=True)
    result.add_argument("--initial-flow-time-s", type=float, required=True)
    result.add_argument("--old-dt-s", type=float, required=True)
    result.add_argument("--new-dt-s", type=float, required=True)
    result.add_argument("--inner-iterations", type=int, default=20)
    result.add_argument("--additional-steps", type=int, default=10)
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def main() -> int:
    args = parser().parse_args()
    if args.additional_steps < 1:
        raise ValueError("additional steps must be positive")
    if not (args.old_dt_s > 0.0 and args.new_dt_s > 0.0):
        raise ValueError("time steps must be positive")
    if args.inner_iterations not in (20, 40, 100, 200):
        raise ValueError("inner iterations must be one of 20, 40, 100 or 200")
    ratio = args.new_dt_s / args.old_dt_s
    if min(
        abs(ratio - 0.125),
        abs(ratio - 0.25),
        abs(ratio - 0.5),
        abs(ratio - 1.0),
        abs(ratio - 2.0),
    ) > 1.0e-12:
        raise ValueError(
            "this guarded scheduler permits a same-dt hold, one 2x dt change, "
            "or a matched half-/quarter-/eighth-dt sensitivity"
        )
    if args.inner_iterations != 20 and abs(ratio - 1.0) > 1.0e-12:
        raise ValueError(
            "inner-iteration sensitivity must keep physical dt unchanged"
        )
    if not args.parent_stem.startswith(extension.REMOTE_ROOT + "\\"):
        raise ValueError("parent stem must be inside the authoritative remote study root")

    extension.RUN_LABEL = args.run_label
    extension.LOCAL_ROOT = (
        extension.PROJECT_ROOT / "output" / extension.STUDY_ID / args.run_label
    )
    extension.PARENT_LABEL = Path(args.parent_stem.replace("\\", "/")).name
    extension.PARENT_CASE = args.parent_stem + ".cas.h5"
    extension.PARENT_DATA = args.parent_stem + ".dat.h5"
    extension.EXPECTED_PARENT_CASE_SHA256 = args.parent_case_sha256
    extension.EXPECTED_PARENT_DATA_SHA256 = args.parent_data_sha256
    extension.INITIAL_TIME_STEP = args.initial_time_step
    extension.INITIAL_FLOW_TIME_S = args.initial_flow_time_s
    extension.TIME_STEP_SIZE_S = args.new_dt_s
    extension.INNER_ITERATIONS = args.inner_iterations
    extension.ADDITIONAL_STEPS = args.additional_steps
    checkpoints = {1, args.additional_steps}
    if args.additional_steps >= 5:
        checkpoints.add(5)
    if args.additional_steps >= 10:
        checkpoints.add(10)
    if args.additional_steps >= 40:
        checkpoints.update(
            {
                args.additional_steps // 4,
                args.additional_steps // 2,
                3 * args.additional_steps // 4,
            }
        )
    extension.CHECKPOINT_ADDITIONAL_STEPS = checkpoints
    extension.RUN_CLASSIFICATION = (
        "diagnostic / unresolved mesh-selected closed-drain one-factor extension"
    )
    extension.FINAL_CLASSIFICATION = (
        "diagnostic / unresolved mesh-selected closed-drain bounded dt stage"
    )
    if args.inner_iterations != 20:
        extension.ONE_FACTOR_CHANGE = (
            f"inner iterations per physical step 20 -> {args.inner_iterations} "
            f"at fixed dt {args.new_dt_s:.12g} s"
        )
    elif abs(ratio - 1.0) <= 1.0e-12:
        extension.ONE_FACTOR_CHANGE = f"same-dt hold at {args.new_dt_s:.12g} s"
    else:
        extension.ONE_FACTOR_CHANGE = (
            f"physical dt {args.old_dt_s:.12g} s -> {args.new_dt_s:.12g} s"
        )
    extension.UNCHANGED_CONTRACT = (
        "mesh-selected closed-drain parent; zero feed; brine wall; steam pressure "
        "outlet; transient explicit VOF; PISO/PRESTO/Geo-Reconstruct/WFGC; RNG "
        "k-epsilon; Energy off; DPM zero/off; EWF off; no sources/sinks"
    )
    extension.PARENT_ELIGIBILITY_SCOPE = (
        "same mesh-selected closed-drain diagnostic lineage only"
    )
    final_time = args.initial_flow_time_s + args.additional_steps * args.new_dt_s
    extension.ACCEPTANCE_LIMITATION = (
        f"Cumulative physical time {final_time:.12g} s remains a closed-drain "
        "diagnostic; it does not establish constant-level open-drain operation"
    )
    if args.inner_iterations != 20:
        extension.NEXT_ELIGIBILITY_SCOPE = (
            "matched inner-iteration diagnostic endpoint only; do not continue or "
            "promote before comparison adjudication"
        )
    elif abs(ratio - 1.0) <= 1.0e-12:
        extension.NEXT_ELIGIBILITY_SCOPE = (
            "same mesh-selected closed-drain diagnostic lineage, continued same-dt "
            "hold or matched sensitivity only"
        )
    elif abs(ratio - 2.0) <= 1.0e-12:
        extension.NEXT_ELIGIBILITY_SCOPE = (
            "same mesh-selected closed-drain diagnostic lineage, next conservative "
            "2x dt only"
        )
    elif abs(ratio - 0.5) <= 1.0e-12:
        extension.NEXT_ELIGIBILITY_SCOPE = (
            "matched half-dt diagnostic endpoint only; do not continue or promote "
            "before comparison adjudication"
        )
    elif abs(ratio - 0.25) <= 1.0e-12:
        extension.NEXT_ELIGIBILITY_SCOPE = (
            "matched quarter-dt diagnostic endpoint only; do not continue or "
            "promote before comparison adjudication"
        )
    else:
        extension.NEXT_ELIGIBILITY_SCOPE = (
            "matched eighth-dt diagnostic endpoint only; do not continue or "
            "promote before comparison adjudication"
        )
    extension.SAVE_TAG = "07n_a_meshselected_onefactor"
    extension.PRINT_LABEL = (
        f"07n-a mesh-selected dt={args.new_dt_s:.12g} s, "
        f"inner={args.inner_iterations}"
    )

    sys.argv = [
        sys.argv[0],
        "--server-id",
        "1",
        "--tcp-timeout-seconds",
        str(args.tcp_timeout_seconds),
    ]
    return extension.main()


if __name__ == "__main__":
    raise SystemExit(main())

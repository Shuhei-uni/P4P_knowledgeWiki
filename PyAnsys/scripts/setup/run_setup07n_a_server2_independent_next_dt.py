#!/usr/bin/env python3
"""Advance one checksum-bound 2x-dt stage in the independent server-2 lineage."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--parent-manifest", type=Path, required=True)
    result.add_argument("--run-label", required=True)
    result.add_argument("--time-step-size-s", type=float, required=True)
    result.add_argument("--stage-tag", required=True)
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def server2_parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("2",), default="2")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def load_parent(path: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.resolve().read_text(encoding="utf-8"))
    if payload.get("status") != "completed":
        raise RuntimeError(f"parent is not completed: {payload.get('status')!r}")
    if payload.get("next_dt_extension_eligible") is not True:
        raise RuntimeError("parent did not pass its next-dt eligibility gates")
    endpoint = payload.get("checkpoints", {}).get("10")
    if not isinstance(endpoint, dict) or endpoint.get("eligible_parent") is not True:
        raise RuntimeError("parent additional-step-10 checkpoint is not eligible")
    steps = payload.get("steps")
    if not isinstance(steps, list) or not steps:
        raise RuntimeError("parent has no physical-step evidence")
    final = steps[-1].get("metrics")
    if not isinstance(final, dict):
        raise RuntimeError("parent final physical metrics are missing")
    if steps[-1].get("gate_failures"):
        raise RuntimeError("parent endpoint has gate failures")
    return payload, endpoint, final


def main() -> int:
    args = build_parser().parse_args()
    parent_payload, endpoint, final = load_parent(args.parent_manifest)
    parent_dt = float(parent_payload["time_step_size_s"])
    if not math.isclose(
        args.time_step_size_s,
        2.0 * parent_dt,
        rel_tol=0.0,
        abs_tol=max(1.0e-15, parent_dt * 1.0e-12),
    ):
        raise RuntimeError(
            f"next dt must be exactly 2x parent dt: parent={parent_dt:g}, "
            f"requested={args.time_step_size_s:g}"
        )
    run_root = extension.PROJECT_ROOT / "output" / extension.STUDY_ID / args.run_label
    if run_root.exists():
        raise FileExistsError(f"refusing to reuse output root: {run_root}")

    extension.parser = server2_parser
    extension.RUN_LABEL = args.run_label
    extension.PARENT_LABEL = str(parent_payload.get("run_label", "unknown"))
    extension.PARENT_CASE = endpoint["case"]["path"]
    extension.PARENT_DATA = endpoint["data"]["path"]
    extension.EXPECTED_PARENT_CASE_SHA256 = endpoint["case"]["sha256"]
    extension.EXPECTED_PARENT_DATA_SHA256 = endpoint["data"]["sha256"]
    extension.INITIAL_TIME_STEP = int(final["time_step"])
    extension.INITIAL_FLOW_TIME_S = float(final["flow_time_s"])
    extension.TIME_STEP_SIZE_S = float(args.time_step_size_s)
    extension.LOCAL_ROOT = run_root
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
        "diagnostic / unresolved independent server-2 whole-cell "
        f"dt={args.time_step_size_s:g} s relaxation"
    )
    extension.ONE_FACTOR_CHANGE = (
        f"physical dt {parent_dt:g} s -> {args.time_step_size_s:g} s"
    )
    extension.UNCHANGED_CONTRACT = (
        "checksum-bound independent server-2 whole-cell field; zero feed; brine wall; "
        "steam pressure outlet; transient explicit VOF; PISO/PRESTO/"
        "Geo-Reconstruct/WFGC; RNG k-epsilon; Energy off; DPM zero/off; "
        "EWF off; no sources/sinks"
    )
    extension.PARENT_ELIGIBILITY_SCOPE = str(endpoint.get("eligibility_scope"))
    target_time = extension.INITIAL_FLOW_TIME_S + 10.0 * args.time_step_size_s
    extension.ACCEPTANCE_LIMITATION = (
        f"Cumulative flow time {target_time:g} s remains an independent closed-pool "
        "relaxation diagnostic and is ineligible for the server-1 lineage"
    )
    extension.NEXT_ELIGIBILITY_SCOPE = (
        "same independent server-2 closed-pool reconstruction, next conservative 2x dt only"
    )
    extension.SAVE_TAG = args.stage_tag
    extension.PRINT_LABEL = f"07n-a server2 independent {args.stage_tag}"

    sys.argv = [
        sys.argv[0],
        "--server-id",
        "2",
        "--tcp-timeout-seconds",
        str(args.tcp_timeout_seconds),
    ]
    return extension.main()


if __name__ == "__main__":
    raise SystemExit(main())

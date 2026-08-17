#!/usr/bin/env python3
"""Read back one completed 03A Stage-2 +700 endpoint.

This verifier is deliberately branch-scoped so a reconnect can be performed
and recorded one case at a time.  It does not issue solver iterations.  The
endpoint is classified as verified only after the paired case/data files can
be loaded and read-only evidence is captured from Fluent.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_DIR = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SETUP_DIR))

from pyansys_fluent.common import remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import write_json  # noqa: E402
import run_03a_stage2_stabilization as base  # noqa: E402


DEFAULT_REMOTE_DIR = base.DEFAULT_REMOTE_DIR
BRANCHES = ("N1", "N3", "N4", "N5")
EXPECTED_FINAL_ITERATION = {
    "N1": 2000,
    "N3": 2000,
    "N4": 2000,
    "N5": 2500,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--branch", choices=BRANCHES, required=True)
    parser.add_argument("--stamp", required=True)
    parser.add_argument(
        "--remote-dir",
        default=DEFAULT_REMOTE_DIR,
        help="Remote Fluent directory containing the Stage-2 endpoint files.",
    )
    parser.add_argument(
        "--extension-dir",
        required=True,
        type=Path,
        help="Existing extension campaign directory containing the branch journal.",
    )
    return parser


def remote_artifact_state(solver: Any, paths: dict[str, str]) -> dict[str, bool | None]:
    state: dict[str, bool | None] = {}
    for name, path in paths.items():
        try:
            state[name] = bool(remote_file_exists(solver, path))
        except Exception:
            state[name] = None
    return state


def endpoint_paths(branch: str, remote_dir: str, stamp: str) -> dict[str, str]:
    if branch == "N5":
        stem = f"03A-S2-N5-from-rng-return-plus700-{stamp}"
    else:
        stem = f"03A-S2-{branch}-from-initial-screen-plus700-{stamp}"
    root = PureWindowsPath(remote_dir)
    return {
        "endpoint_case": str(root / f"{stem}.cas.h5"),
        "endpoint_data": str(root / f"{stem}.dat.h5"),
        "transcript": str(root / f"{stem}.trn"),
        "residual_file": str(root / f"{stem}-residuals.out"),
        "remote_journal": str(root / f"{stem}.jou"),
    }


def as_number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> int:
    args = build_parser().parse_args()
    branch = args.branch
    extension_dir = args.extension_dir.expanduser().resolve()
    output_dir = extension_dir / "post_simulation_analysis" / f"reconnect-{args.stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = endpoint_paths(branch, args.remote_dir, args.stamp)
    local_journal = extension_dir / (
        f"03A-S2-{branch}-from-rng-return-plus700-{args.stamp}.jou"
        if branch == "N5"
        else f"03A-S2-{branch}-from-initial-screen-plus700-{args.stamp}.jou"
    )

    solver = connect(server_id=args.server_id)
    fluent_version = str(solver.get_fluent_version())
    if "2025 R2" not in fluent_version:
        raise RuntimeError(f"Expected Fluent 2025 R2, got {fluent_version!r}")
    if not solver.is_active():
        raise RuntimeError("Student Fluent session is not active")

    artifacts = remote_artifact_state(solver, paths)
    pair_present = artifacts.get("endpoint_case") is True and artifacts.get("endpoint_data") is True
    record: dict[str, Any] = {
        "branch": branch,
        "phase": "extension-700",
        "verification_stamp": args.stamp,
        "fluent_version": fluent_version,
        "expected_final_iteration": EXPECTED_FINAL_ITERATION[branch],
        "local_journal": str(local_journal),
        "remote_artifacts": artifacts,
        "endpoint_paths": paths,
        "status": "NOT_VERIFIED",
        "verification_basis": [],
        "warnings": [],
    }

    if not pair_present:
        record["status"] = "ENDPOINT_PAIR_MISSING"
        record["warnings"].append(
            "The paired endpoint case/data files were not both visible after reconnect; no case was loaded."
        )
    else:
        try:
            evidence = base.collect_endpoint_evidence(
                solver,
                branch=branch,
                phase="extension-700",
                endpoint_case=paths["endpoint_case"],
                endpoint_data=paths["endpoint_data"],
                output_dir=output_dir,
            )
            residual = evidence.get("residual_history", {})
            iterations = residual.get("iterations", []) if isinstance(residual, dict) else []
            last_iteration = as_number(iterations[-1]) if iterations else None
            record["status"] = "RUN_COMPLETED_ENDPOINT_VERIFIED"
            record["verification_basis"] = [
                "paired endpoint case/data files visible after reconnect",
                "paired case/data load completed",
                "read-only endpoint residual, flux, monitor, and settings evidence captured",
            ]
            record["last_residual_iteration"] = last_iteration
            record["evidence"] = evidence
            if last_iteration is not None and last_iteration != EXPECTED_FINAL_ITERATION[branch]:
                record["status"] = "ENDPOINT_VERIFIED_ITERATION_MISMATCH"
                record["warnings"].append(
                    f"Residual history ended at iteration {last_iteration:g}; expected "
                    f"{EXPECTED_FINAL_ITERATION[branch]} for {branch}."
                )
        except Exception as exc:
            record["status"] = "ENDPOINT_PRESENT_READBACK_FAILED"
            record["warnings"].append(f"{type(exc).__name__}: {exc}")

    verification_json = extension_dir / f"{branch}-extension-700-reconnect-{args.stamp}.json"
    write_json(verification_json, record)
    print(json.dumps(record, indent=2, default=str), flush=True)
    print(f"verification_json: {verification_json}", flush=True)
    return 0 if record["status"] == "RUN_COMPLETED_ENDPOINT_VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())

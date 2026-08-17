#!/usr/bin/env python3
"""Extend each verified 03A Stage-2 endpoint by 700 Fluent-native iterations.

The extension is deliberately a separate campaign from the initial Stage-2
screen.  N1/N3/N4 continue from their verified ``initial-screen`` endpoint;
N5 continues from its verified ``rng-return`` endpoint.  Fluent owns one
native ``/solve/iterate 700`` command per branch.  Python only prepares and
submits the journals, records artifact/failure state, and performs read-only
endpoint analysis afterward.

This script must be run only after ``run_03a_stage2_stabilization.py`` has
finished.  It refuses to infer an endpoint from a partial or failed phase.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SETUP_DIR))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import write_json  # noqa: E402
import run_03a_stage2_stabilization as base  # noqa: E402


EXTENSION_ITERATIONS = 700
BRANCHES = ("N1", "N3", "N4", "N5")
INITIAL_PHASE_BY_BRANCH = {
    "N1": "initial-screen",
    "N3": "initial-screen",
    "N4": "initial-screen",
    "N5": "rng-return",
}


def completed_source_phase(campaign: Mapping[str, Any], branch: str) -> dict[str, Any] | None:
    phase_name = INITIAL_PHASE_BY_BRANCH[branch]
    candidates = [
        phase
        for phase in campaign.get("phases", [])
        if phase.get("branch") == branch
        and phase.get("phase") == phase_name
        and phase.get("status") == "RUN_COMPLETED_ENDPOINT_VERIFIED"
    ]
    if len(candidates) != 1:
        return None
    phase = dict(candidates[0])
    artifacts = phase.get("expected_artifacts", {})
    if not isinstance(artifacts, Mapping):
        return None
    if not artifacts.get("endpoint_case") or not artifacts.get("endpoint_data"):
        return None
    return phase


def prepare_extension_artifacts(
    solver: Any,
    *,
    source_phase: Mapping[str, Any],
    parent_case: str,
    remote_dir: str,
    stamp: str,
    output_dir: Path,
) -> dict[str, Any]:
    branch = str(source_phase["branch"])
    source_phase_name = str(source_phase["phase"])
    input_case = str(source_phase["expected_artifacts"]["endpoint_case"])
    input_data = str(source_phase["expected_artifacts"]["endpoint_data"])
    stem = f"03A-S2-{branch}-from-{source_phase_name}-plus700-{stamp}"
    endpoint_case = str(PureWindowsPath(remote_dir) / f"{stem}.cas.h5")
    endpoint_data = str(PureWindowsPath(remote_dir) / f"{stem}.dat.h5")
    transcript = str(PureWindowsPath(remote_dir) / f"{stem}.trn")
    residual_file = str(PureWindowsPath(remote_dir) / f"{stem}-residuals.out")
    remote_journal = str(PureWindowsPath(remote_dir) / f"{stem}.jou")
    local_journal = output_dir / f"{stem}.jou"
    base.ensure_absent(
        solver,
        [endpoint_case, endpoint_data, transcript, residual_file, remote_journal],
    )
    journal = base.render_branch_journal(
        branch=branch,
        phase="extension-700",
        parent_case=parent_case,
        input_case=input_case,
        input_data=input_data,
        iterations=EXTENSION_ITERATIONS,
        endpoint_case=endpoint_case,
        transcript=transcript,
        residual_file=residual_file,
    )
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    base.write_remote_journal(solver, remote_journal, journal)
    return {
        "branch": branch,
        "phase": "extension-700",
        "source_phase": source_phase_name,
        "source_endpoint_case": input_case,
        "source_endpoint_data": input_data,
        "iterations_requested": EXTENSION_ITERATIONS,
        "input_case": input_case,
        "input_data": input_data,
        "endpoint_case": endpoint_case,
        "endpoint_data": endpoint_data,
        "transcript": transcript,
        "residual_file": residual_file,
        "remote_journal": remote_journal,
        "local_journal": str(local_journal),
        "journal": journal,
        "artifacts": {
            "endpoint_case": endpoint_case,
            "endpoint_data": endpoint_data,
            "transcript": transcript,
            "residual_file": residual_file,
            "remote_journal": remote_journal,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--base-campaign", required=True, type=Path)
    parser.add_argument("--stage2-manifest", required=True, type=Path)
    parser.add_argument("--remote-dir", default=base.DEFAULT_REMOTE_DIR)
    parser.add_argument(
        "--stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest-json", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    base_campaign_path = args.base_campaign.expanduser().resolve()
    stage2_path = args.stage2_manifest.expanduser().resolve()
    base_campaign = json.loads(base_campaign_path.read_text(encoding="utf-8"))
    stage2 = json.loads(stage2_path.read_text(encoding="utf-8"))
    if stage2.get("setup_id") != "03A" or len(stage2.get("children", [])) != 4:
        raise ValueError("Expected the verified 03A four-child Stage-2 manifest")
    if base_campaign.get("status") != "RUNS_ATTEMPTED":
        raise ValueError(
            "The initial Stage-2 campaign is not terminal; wait for all current journals to finish. "
            f"Observed status={base_campaign.get('status')!r}"
        )

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = args.manifest_json.expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    campaign: dict[str, Any] = {
        "setup_id": "03A",
        "stage": "Stage 2 extension",
        "purpose": "700 additional steady iterations from each verified Stage-2 endpoint",
        "transport": "Fluent gRPC",
        "base_campaign": str(base_campaign_path),
        "stage2_manifest": str(stage2_path),
        "parent_case": stage2.get("parent_case"),
        "parent_data": stage2.get("parent_data"),
        "extension_iterations": EXTENSION_ITERATIONS,
        "lineage_policy": (
            "N1/N3/N4 continue from their verified 300-iteration initial-screen endpoint; "
            "N5 continues from its verified 300-iteration RNG-return endpoint."
        ),
        "phases": [],
        "status": "PLANNED",
        "interpretation_status": "pending user direction",
    }
    write_json(manifest_path, campaign)

    solver = connect(server_id=args.server_id)
    fluent_version = str(solver.get_fluent_version())
    if "2025 R2" not in fluent_version:
        raise RuntimeError(f"Expected Fluent 2025 R2, got {fluent_version!r}")
    if not solver.is_active():
        raise RuntimeError("Student Fluent session is not active")

    campaign["fluent_version"] = fluent_version
    campaign["status"] = "SUBMITTING_NATIVE_RUNS"
    write_json(manifest_path, campaign)
    for branch in BRANCHES:
        source_phase = completed_source_phase(base_campaign, branch)
        if source_phase is None:
            record = {
                "branch": branch,
                "phase": "extension-700",
                "source_phase": INITIAL_PHASE_BY_BRANCH[branch],
                "status": "NOT_ATTEMPTED",
                "failure": {
                    "category": "source_endpoint_not_verified",
                    "exception": (
                        "The required source phase did not have exactly one "
                        "RUN_COMPLETED_ENDPOINT_VERIFIED endpoint pair."
                    ),
                },
            }
            campaign["phases"].append(record)
            write_json(output_dir / f"{branch}-extension-700-run.json", record)
            write_json(manifest_path, campaign)
            continue
        try:
            artifacts = prepare_extension_artifacts(
                solver,
                source_phase=source_phase,
                parent_case=str(stage2["parent_case"]),
                remote_dir=args.remote_dir,
                stamp=args.stamp,
                output_dir=output_dir,
            )
            base.submit_phase(
                solver,
                child={},
                phase_artifacts=artifacts,
                output_dir=output_dir,
                campaign_payload=campaign,
            )
        except Exception as exc:
            record = {
                "branch": branch,
                "phase": "extension-700",
                "source_phase": source_phase["phase"],
                "status": "FAILED_PREPARATION",
                "failure": {
                    "category": base.infer_failure_category(f"{type(exc).__name__}: {exc}"),
                    "exception": f"{type(exc).__name__}: {exc}",
                },
            }
            campaign["phases"].append(record)
            write_json(output_dir / f"{branch}-extension-700-run.json", record)
            write_json(manifest_path, campaign)

    campaign["status"] = "RUNS_ATTEMPTED"
    campaign["cumulative_iteration_accounting"] = {
        "N1": "300 initial-screen + 700 extension = 1000 additional iterations from Stage-1 iter1000",
        "N3": "300 initial-screen + 700 extension = 1000 additional iterations from Stage-1 iter1000",
        "N4": "300 initial-screen + 700 extension = 1000 additional iterations from Stage-1 iter1000",
        "N5": (
            "500 standard bootstrap + 300 RNG return + 700 extension; the extension itself is "
            "700 from the verified 300-iteration RNG-return endpoint."
        ),
    }
    write_json(manifest_path, campaign)
    print(json.dumps(campaign, indent=2, default=str), flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    print("RUNS_ATTEMPTED; Fluent remains open; no solver shutdown was issued.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

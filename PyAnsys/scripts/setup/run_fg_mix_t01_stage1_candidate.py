#!/usr/bin/env python3
"""Submit one FG-MIX-T01 Stage-1 candidate as a Fluent-native run.

The selected case-only child is read independently, Hybrid Initialized, and
run for 1,000 steady iterations by Fluent.  Python only prepares/submits the
journal and records the expected remote artifacts; it does not loop over
iterations or own checkpoint timing.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


RUN_ITERATIONS = 1_000


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def render_journal(
    *,
    case_file: str,
    endpoint_case: str,
    endpoint_data: str,
    residual_file: str,
    transcript: str,
) -> str:
    return "\n".join(
        [
            "; FG-MIX-T01 Stage-1 native candidate run",
            "; Fluent owns initialization, the 1,000 iterations, and paired checkpoint write.",
            "/file/confirm-overwrite? no",
            f'/file/start-transcript "{posix(transcript)}"',
            "/solve/monitors/residual/print? yes",
            "/solve/monitors/residual/plot? yes",
            "/solve/monitors/residual/n-save 1200",
            f'/file/read-case "{posix(case_file)}"',
            "/solve/initialize/hyb-initialization",
            f"/solve/iterate {RUN_ITERATIONS}",
            f'/file/write-case-data "{posix(endpoint_case)}"',
            f'/plot/residuals-set/plot-to-file "{posix(residual_file)}"',
            "/plot/residuals",
            "/plot/residuals-set/end-plot-to-file",
            "/file/stop-transcript",
            "; Native candidate run finished; Fluent remains open.",
            "",
        ]
    )


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)'
        for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(remote_journal))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Remote journal was not created: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--build-snapshot", required=True, type=Path)
    parser.add_argument("--case-id", required=True)
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="UTC stamp for endpoint and journal artifacts",
    )
    parser.add_argument("--local-journal", required=True, type=Path)
    args = parser.parse_args()

    snapshot = json.loads(args.build_snapshot.expanduser().resolve().read_text(encoding="utf-8"))
    children = [child for child in snapshot["children"] if child["case_id"] == args.case_id]
    if len(children) != 1:
        raise ValueError(f"Expected one child for {args.case_id!r}; found {len(children)}")
    child = children[0]
    case_file = str(child["case_file"])
    source = PureWindowsPath(case_file)
    stem = source.name[:-7]
    output_stem = f"{stem}-iter1000-{args.run_stamp}"
    endpoint_case = str(source.parent / f"{output_stem}.cas.h5")
    endpoint_data = str(source.parent / f"{output_stem}.dat.h5")
    residual_file = str(source.parent / f"{output_stem}-residuals.out")
    transcript = str(source.parent / f"{output_stem}.trn")
    remote_journal = str(source.parent / f"{output_stem}.jou")

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if not remote_file_exists(solver, case_file):
        raise FileNotFoundError(f"Candidate input case is not visible: {case_file}")
    for path in (endpoint_case, endpoint_data, residual_file, transcript, remote_journal):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite run artifact: {path}")

    journal = render_journal(
        case_file=case_file,
        endpoint_case=endpoint_case,
        endpoint_data=endpoint_data,
        residual_file=residual_file,
        transcript=transcript,
    )
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, remote_journal, journal)

    manifest = {
        "campaign": "FG-MIX-T01",
        "stage": "S1",
        "case_id": args.case_id,
        "pressure_pa": child["pressure_pa"],
        "mesh": snapshot["mesh"],
        "server_id": args.server_id,
        "fluent_version": str(solver.get_fluent_version()),
        "preinit_case": case_file,
        "remote_journal": remote_journal,
        "local_journal": str(local_journal),
        "transcript": transcript,
        "residual_file": residual_file,
        "endpoint_case": endpoint_case,
        "endpoint_data": endpoint_data,
        "native_iterations_requested": RUN_ITERATIONS,
        "status": "SUBMITTED_NATIVE_RUN",
    }
    manifest_path = local_journal.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, default=str), flush=True)
    solver.settings.file.read_journal(file_name_list=[remote_journal])
    print(f"native_journal_submitted: {remote_journal}", flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

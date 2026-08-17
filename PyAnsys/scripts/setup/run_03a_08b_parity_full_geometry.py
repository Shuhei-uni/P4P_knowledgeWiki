#!/usr/bin/env python3
"""Submit the 03A case-only artifact to Fluent for a native 1,000-iteration run.

All Student interaction is through the existing Fluent gRPC session.  Python
only prepares the native journal, submits it, and records the expected remote
artifacts; Fluent owns Hybrid Initialization, the steady iterations, and the
paired case/data checkpoint write.
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
    residual_file: str,
    transcript: str,
) -> str:
    return "\n".join(
        [
            "; 03A 08b-parity full-geometry native steady checkpoint",
            "; Fluent owns Hybrid Initialization, 1,000 iterations, and the paired write.",
            "; Python does not loop over iterations or perform client-side checkpointing.",
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
            "; 03A native checkpoint complete; Fluent remains open.",
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
        raise RuntimeError(f"Fluent did not expose the native journal: {remote_journal}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument(
        "--case-file",
        default=r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\03A-08b-parity-full-geometry-steady-preinit-20260817T103746Z.cas.h5",
    )
    parser.add_argument("--run-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--local-journal", required=True, type=Path)
    args = parser.parse_args()

    source = PureWindowsPath(args.case_file)
    if source.suffixes[-2:] != [".cas", ".h5"]:
        raise ValueError(f"Expected a .cas.h5 input case, got {args.case_file!r}")
    stem = source.name[:-7]
    output_stem = f"{stem}-iter1000-{args.run_stamp}"
    endpoint_case = str(source.parent / f"{output_stem}.cas.h5")
    endpoint_data = str(source.parent / f"{output_stem}.dat.h5")
    residual_file = str(source.parent / f"{output_stem}-residuals.out")
    transcript = str(source.parent / f"{output_stem}.trn")
    remote_journal = str(source.parent / f"{output_stem}.jou")

    solver = connect(server_id=args.server_id)
    fluent_version = str(solver.get_fluent_version())
    if "2025 R2" not in fluent_version:
        raise RuntimeError(f"Expected Fluent 2025 R2, got {fluent_version!r}")
    if not solver.is_active():
        raise RuntimeError("Student Fluent session is not active")
    if not remote_file_exists(solver, str(source)):
        raise FileNotFoundError(f"03A input case is not visible through Fluent: {source}")
    for path in (endpoint_case, endpoint_data, residual_file, transcript, remote_journal):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite existing run artifact: {path}")

    journal = render_journal(
        case_file=str(source),
        endpoint_case=endpoint_case,
        residual_file=residual_file,
        transcript=transcript,
    )
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, remote_journal, journal)

    manifest = {
        "setup_id": "03A",
        "transport": "Fluent gRPC",
        "server_id": args.server_id,
        "fluent_version": fluent_version,
        "preinit_case": str(source),
        "remote_journal": remote_journal,
        "local_journal": str(local_journal),
        "transcript": transcript,
        "residual_file": residual_file,
        "endpoint_case": endpoint_case,
        "endpoint_data": endpoint_data,
        "native_iterations_requested": RUN_ITERATIONS,
        "initialization": "Hybrid Initialization",
        "liquid_patch": False,
        "dpm_ewf": False,
        "status": "SUBMITTED_NATIVE_RUN",
        "qualification": "diagnostic checkpoint; iteration count alone does not qualify steady state",
    }
    manifest_path = local_journal.with_suffix(".json")
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2), flush=True)
    solver.settings.file.read_journal(file_name_list=[remote_journal])
    print(f"native_journal_submitted: {remote_journal}", flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    print("fluent_left_open: true", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

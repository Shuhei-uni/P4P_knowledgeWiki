#!/usr/bin/env python3
"""Submit one already-prepared Stage-3 pressure case to Fluent.

This intentionally submits only one pressure level. A failed native journal
must not prevent the next independent pressure case from being attempted.
Fluent owns the 200 transient timesteps and endpoint write.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
from pathlib import PureWindowsPath
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


TRANSIENT_STEPS = 200
TIME_STEP_S = 2.5e-4
RESIDUAL_HISTORY_SIZE = 1_200


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def render_journal(child: dict[str, Any]) -> str:
    return "\n".join(
        [
            "; FG-MIX-T01 Stage-3 independent pressure case",
            f"; Branch: {child['branch']}; brine outlet: {child['pressure_mpa']:.3f} MPa gauge",
            "; Fluent owns 200 transient timesteps and paired endpoint write.",
            "/file/confirm-overwrite? no",
            f'/file/read-case "{posix(child["prepared_case"])}"',
            f'/file/read-data "{posix(child["prepared_data"])}"',
            f"/solve/set/transient-controls/time-step-size {TIME_STEP_S}",
            f"/solve/monitors/residual/n-save {RESIDUAL_HISTORY_SIZE}",
            "/solve/monitors/residual/print? yes",
            f'/file/start-transcript "{posix(child["transcript"])}"',
            f"/solve/iterate {TRANSIENT_STEPS}",
            f'/file/write-case-data "{posix(child["endpoint_case"])}"',
            f'/plot/residuals-set/plot-to-file "{posix(child["residual_file"])}"',
            "/plot/residuals",
            "/plot/residuals-set/end-plot-to-file",
            "/file/stop-transcript",
            "; Independent pressure case submitted; Fluent remains open.",
            "",
        ]
    )


def write_remote_journal(solver: Any, path: str, body_text: str) -> None:
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)'
        for line in body_text.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(path))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Remote journal was not created: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--pressure-manifest", required=True, type=Path)
    parser.add_argument("--pressure-mpa", required=True, type=float)
    parser.add_argument("--branch", choices=("INIT-S", "INIT-H"), default="INIT-S")
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    parser.add_argument("--local-journal", required=True, type=Path)
    parser.add_argument("--manifest-json", required=True, type=Path)
    args = parser.parse_args()

    pressure_manifest_path = args.pressure_manifest.expanduser().resolve()
    pressure_manifest = json.loads(pressure_manifest_path.read_text(encoding="utf-8"))
    matches = [
        child
        for child in pressure_manifest["children"]
        if child["branch"] == args.branch
        and abs(float(child["pressure_mpa"]) - args.pressure_mpa) < 1.0e-9
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one prepared {args.branch} child at {args.pressure_mpa:.3f} MPa; found {len(matches)}"
        )
    child = dict(matches[0])
    for key in ("prepared_case", "prepared_data"):
        if not isinstance(child.get(key), str):
            raise ValueError(f"Missing prepared artifact field: {key}")

    source = PureWindowsPath(child["prepared_case"])
    stem = source.name.removesuffix("-start.cas.h5")
    child["endpoint_case"] = str(source.parent / f"{stem}.cas.h5")
    child["endpoint_data"] = str(source.parent / f"{stem}.dat.h5")
    child["transcript"] = str(source.parent / f"{stem}.trn")
    child["residual_file"] = str(source.parent / f"{stem}-residuals.out")
    child["remote_journal"] = str(source.parent / f"{stem}-{args.run_stamp}.jou")

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    for key in ("prepared_case", "prepared_data"):
        if not remote_file_exists(solver, child[key]):
            raise FileNotFoundError(f"Prepared input is missing: {child[key]}")
    for key in ("endpoint_case", "endpoint_data", "transcript", "residual_file", "remote_journal"):
        if remote_file_exists(solver, child[key]):
            raise FileExistsError(f"Refusing to overwrite existing artifact: {child[key]}")

    journal = render_journal(child)
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, child["remote_journal"], journal)

    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S3",
        "purpose": "independent shortened brine-outlet pressure case",
        "branch": args.branch,
        "pressure_mpa": args.pressure_mpa,
        "pressure_pa": args.pressure_mpa * 1_000_000.0,
        "native_transient_steps": TRANSIENT_STEPS,
        "time_step_s": TIME_STEP_S,
        "physical_horizon_s": TRANSIENT_STEPS * TIME_STEP_S,
        "prepared_case": child["prepared_case"],
        "prepared_data": child["prepared_data"],
        "endpoint_case": child["endpoint_case"],
        "endpoint_data": child["endpoint_data"],
        "transcript": child["transcript"],
        "residual_file": child["residual_file"],
        "remote_journal": child["remote_journal"],
        "local_journal": str(local_journal),
        "source_pressure_manifest": str(pressure_manifest_path),
        "status": "SUBMITTED_NATIVE_RUN",
        "fluent_version": str(solver.get_fluent_version()),
    }
    manifest_path = args.manifest_json.expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    solver.settings.file.read_journal(file_name_list=[child["remote_journal"]])
    print(f"native_journal_submitted: {child['remote_journal']}", flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

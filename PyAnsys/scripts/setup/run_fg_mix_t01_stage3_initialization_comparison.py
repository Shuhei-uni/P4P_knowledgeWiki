#!/usr/bin/env python3
"""Submit the FG-MIX-T01 Stage-3 INIT-S versus INIT-H comparison.

Each saved Stage-2 or monitor-ready pair is independently reloaded and
advanced by Fluent for 1,000 transient timesteps at 2.5e-4 s, giving a common
physical horizon of 0.25 s. The start-state initialization and Y010 patch are
not repeated.
Python prepares and submits one Fluent-native journal; Fluent owns all
transient stepping and paired endpoint writes.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_resume_case_data  # noqa: E402


REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
EXACT_MESH_NAME = "Full-geomV2-231kcells.msh.h5"
STAGE2_STAMP = "20260816T112833Z"
TIME_STEP_S = 2.5e-4
TIME_STEPS = 1_000
PHYSICAL_HORIZON_S = TIME_STEP_S * TIME_STEPS
RESIDUAL_HISTORY_SIZE = 5_000


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def case_stem(branch: str) -> str:
    return f"FG-MIX-T01-S3-{branch}-TPO1-0p25s-{RUN_STAMP}"


def render_journal(children: list[dict[str, Any]]) -> str:
    lines = [
        "; FG-MIX-T01 Stage-3 native initialization comparison",
        "; Same physical horizon: 1000 steps x 2.5e-4 s = 0.25 s.",
        "; Start states already contain their branch-specific initialization and one Y010 patch.",
        "; Do not reinitialize or repatch either branch.",
        "/file/confirm-overwrite? no",
    ]
    for child in children:
        branch = child["branch"]
        lines.extend(
            [
                f"; BEGIN {branch}",
                f'/file/read-case "{posix(child["case_file"])}"',
                f'/file/read-data "{posix(child["data_file"])}"',
                "; Reassert the fixed timestep after the data read.",
                f"/solve/set/transient-controls/time-step-size {TIME_STEP_S}",
                f"/solve/monitors/residual/n-save {RESIDUAL_HISTORY_SIZE}",
                "/solve/monitors/residual/print? yes",
                f'/file/start-transcript "{posix(child["transcript"])}"',
                f"/solve/iterate {TIME_STEPS}",
                f'/file/write-case-data "{posix(child["endpoint_case"])}"',
                f'/plot/residuals-set/plot-to-file "{posix(child["residual_file"])}"',
                "/plot/residuals",
                "/plot/residuals-set/end-plot-to-file",
                "/file/stop-transcript",
                f"; END {branch}",
            ]
        )
    lines.extend(["; Stage-3 native comparison submitted; Fluent remains open.", ""])
    return "\n".join(lines)


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(remote_journal))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Remote Stage-3 journal was not created: {remote_journal}")


def verify_start_state(solver: Any, child: dict[str, Any]) -> dict[str, Any]:
    case_file = child["case_file"]
    data_file = child["data_file"]
    case_name = PureWindowsPath(case_file).name
    if f"-{child['branch']}-TPO1-" not in case_name:
        raise RuntimeError(f"Unexpected Stage-2/monitor-repair case identity for {child['branch']}: {case_file}")
    load_resume_case_data(solver, case_file, data_file)
    solver_state = safe_get_state(solver.settings.setup.general.solver, "solver")
    transient = safe_get_state(solver.settings.solution.run_calculation.transient_controls, "transient")
    models = safe_get_state(solver.settings.setup.models.multiphase, "multiphase")
    boundary = safe_get_state(
        solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"],
        "brine outlet",
    )
    pressure = nested(boundary, "phase", "mixture", "momentum", "gauge_pressure", "value")
    registers = solver.settings.solution.cell_registers.get_object_names()
    if solver_state.get("time") != "unsteady-2nd-order-bounded":
        raise RuntimeError(f"{child['branch']} is not a bounded second-order transient start: {solver_state}")
    if abs(float(transient.get("time_step_size")) - TIME_STEP_S) > 1.0e-15:
        raise RuntimeError(f"{child['branch']} timestep mismatch: {transient}")
    if transient.get("flow_time") != 0:
        raise RuntimeError(f"{child['branch']} does not start at flow time 0: {transient}")
    if float(pressure) != 1_200_000.0:
        raise RuntimeError(f"{child['branch']} T-PO-1 pressure mismatch: {pressure}")
    if models.get("model") != "mixture":
        raise RuntimeError(f"{child['branch']} multiphase model mismatch: {models}")
    if "codex_y010_pool_below_y_0p10m" not in set(registers):
        raise RuntimeError(f"{child['branch']} Y010 register is missing: {registers}")
    return {
        "solver": solver_state,
        "transient_controls": transient,
        "multiphase_model": models.get("model"),
        "brine_pressure_pa": pressure,
        "registers": sorted(str(name) for name in registers),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--stage2-manifest", required=True, type=Path)
    parser.add_argument(
        "--run-stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        help="UTC stamp used for Stage-3 endpoint, transcript, residual, and journal names",
    )
    parser.add_argument("--local-journal", required=True, type=Path)
    parser.add_argument("--manifest-json", required=True, type=Path)
    args = parser.parse_args()

    global RUN_STAMP
    RUN_STAMP = args.run_stamp
    stage2 = json.loads(args.stage2_manifest.expanduser().resolve().read_text(encoding="utf-8"))
    source_candidate = stage2.get("source_candidate", "FG-MIX-T01-S1-C1375")
    if source_candidate != "FG-MIX-T01-S1-C1375":
        raise ValueError(f"Stage-2/monitor manifest is not based on C1375: {source_candidate}")
    if PureWindowsPath(stage2["mesh"]).name != EXACT_MESH_NAME:
        raise ValueError(f"Stage-2 manifest is not locked to {EXACT_MESH_NAME}: {stage2['mesh']}")
    if len(stage2.get("children", [])) != 2:
        raise ValueError("Expected exactly INIT-S and INIT-H Stage-2 children")

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")

    children: list[dict[str, Any]] = []
    start_readbacks: dict[str, Any] = {}
    for source in sorted(stage2["children"], key=lambda item: item["branch"]):
        branch = source["branch"]
        stem = case_stem(branch)
        endpoint_case = str(PureWindowsPath(REMOTE_DIR) / f"{stem}.cas.h5")
        endpoint_data = str(PureWindowsPath(REMOTE_DIR) / f"{stem}.dat.h5")
        transcript = str(PureWindowsPath(REMOTE_DIR) / f"{stem}.trn")
        residual_file = str(PureWindowsPath(REMOTE_DIR) / f"{stem}-residuals.out")
        child = {
            "branch": branch,
            "case_file": source["case_file"],
            "data_file": source["data_file"],
            "endpoint_case": endpoint_case,
            "endpoint_data": endpoint_data,
            "transcript": transcript,
            "residual_file": residual_file,
        }
        for path in (child["case_file"], child["data_file"]):
            if not remote_file_exists(solver, path):
                raise FileNotFoundError(f"Missing Stage-2 source for {branch}: {path}")
        for path in (endpoint_case, endpoint_data, transcript, residual_file):
            if remote_file_exists(solver, path):
                raise FileExistsError(f"Refusing to overwrite Stage-3 artifact: {path}")
        start_readbacks[branch] = verify_start_state(solver, child)
        children.append(child)

    remote_journal = str(PureWindowsPath(REMOTE_DIR) / f"FG-MIX-T01-S3-INIT-S-INIT-H-0p25s-{RUN_STAMP}.jou")
    if remote_file_exists(solver, remote_journal):
        raise FileExistsError(f"Refusing to overwrite Stage-3 journal: {remote_journal}")
    journal = render_journal(children)
    local_journal = args.local_journal.expanduser().resolve()
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, remote_journal, journal)

    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S3",
        "comparison": "INIT-S versus INIT-H",
        "source_stage2_manifest": str(args.stage2_manifest.expanduser().resolve()),
        "mesh": stage2["mesh"],
        "mesh_readback": {"cells": 231376, "nodes": 697078},
        "time_step_s": TIME_STEP_S,
        "native_transient_steps": TIME_STEPS,
        "physical_horizon_s": PHYSICAL_HORIZON_S,
        "max_iter_per_time_step": 20,
        "stage2_equivalence_gate": stage2.get("equivalence_gate", {}),
        "start_readbacks": start_readbacks,
        "remote_journal": remote_journal,
        "local_journal": str(local_journal),
        "children": children,
        "status": "SUBMITTED_NATIVE_RUN",
        "fluent_version": str(solver.get_fluent_version()),
    }
    manifest_path = args.manifest_json.expanduser().resolve()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    solver.settings.file.read_journal(file_name_list=[remote_journal])
    print(f"native_journal_submitted: {remote_journal}", flush=True)
    print(f"manifest_json: {manifest_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

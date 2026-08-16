#!/usr/bin/env python3
"""Prepare Stage-3 start-state copies with a total-liquid-mass report.

This is a case-only monitor repair.  It reloads each saved Stage-2 startup
pair, adds one total-domain phase-2 ``volume-mass`` report definition, and
writes a new paired input without initialization, patching, or timestepping.
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

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_io import load_resume_case_data  # noqa: E402
import build_02e_y010_campaign as y010  # noqa: E402


REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
MONITOR_NAME = "fg_mix_t01_s3_total_liquid_mass"
MESH_NAME = "Full-geomV2-231kcells.msh.h5"


def set_optional(obj: Any, attribute: str, value: Any) -> None:
    try:
        setattr(obj, attribute, value)
    except Exception:
        pass


def resolve_fluid_zone(solver: Any) -> str:
    state = safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones")
    names = [
        str(name)
        for name in state.get("fluid", {})
        if str(name) != "settings"
    ]
    if len(names) != 1:
        raise RuntimeError(f"Expected one fluid zone, found {names}")
    return names[0]


def ensure_absent(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError("Refusing to overwrite monitor-repair artifacts: " + ", ".join(existing))


def prepare_child(solver: Any, source: dict[str, Any], remote_dir: str, stamp: str) -> dict[str, Any]:
    branch = source["branch"]
    stem = f"FG-MIX-T01-S3-{branch}-TPO1-0p25s-massmon-start-{stamp}"
    case_file = str(PureWindowsPath(remote_dir) / f"{stem}.cas.h5")
    data_file = str(PureWindowsPath(remote_dir) / f"{stem}.dat.h5")
    ensure_absent(solver, [case_file, data_file])

    load_resume_case_data(solver, source["case_file"], source["data_file"])
    solver_state = safe_get_state(solver.settings.setup.general.solver, "solver")
    transient = safe_get_state(solver.settings.solution.run_calculation.transient_controls, "transient")
    if solver_state.get("time") != "unsteady-2nd-order-bounded":
        raise RuntimeError(f"{branch} is not a transient start: {solver_state}")
    if transient.get("flow_time") != 0:
        raise RuntimeError(f"{branch} does not start at flow time 0: {transient}")

    fluid_zone = resolve_fluid_zone(solver)
    volume = solver.settings.solution.report_definitions.volume
    report = y010._replace_named_report(volume, MONITOR_NAME)
    report.report_type = "volume-mass"
    report = volume[MONITOR_NAME]
    report.cell_zones = [fluid_zone]
    report.phase = "phase-2"
    set_optional(report, "per_selection", False)
    set_optional(report, "average_over", 1)
    set_optional(report, "retain_instantaneous_values", True)
    set_optional(report, "create_report_file", True)
    set_optional(report, "create_report_plot", True)
    report_state = report.get_state()
    if report_state.get("report_type") != "volume-mass":
        raise RuntimeError(f"Total-liquid-mass report type readback failed: {report_state}")
    if report_state.get("cell_zones") != [fluid_zone]:
        raise RuntimeError(f"Total-liquid-mass cell-zone readback failed: {report_state}")
    if report_state.get("phase") != "phase-2":
        raise RuntimeError(f"Total-liquid-mass phase readback failed: {report_state}")
    if report_state.get("create_report_file") is not True:
        raise RuntimeError(f"Total-liquid-mass report file output is not active: {report_state}")

    solver.settings.file.write_case(file_name=case_file)
    solver.settings.file.write_data(file_name=data_file)
    ensure_present = [case_file, data_file]
    if not all(remote_file_exists(solver, path) for path in ensure_present):
        raise RuntimeError(f"Monitor-repair pair was not written: {ensure_present}")

    load_resume_case_data(solver, case_file, data_file)
    reload_report = solver.settings.solution.report_definitions.volume[MONITOR_NAME].get_state()
    if reload_report.get("create_report_file") is not True:
        raise RuntimeError(f"Total-liquid-mass report did not survive reload: {reload_report}")
    return {
        "branch": branch,
        "source_case": source["case_file"],
        "source_data": source["data_file"],
        "case_file": case_file,
        "data_file": data_file,
        "fluid_zone": fluid_zone,
        "total_liquid_mass_report": MONITOR_NAME,
        "report_state": reload_report,
        "timestep_run": False,
        "status": "CASE_DATA_VERIFIED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--stage2-manifest", required=True, type=Path)
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--snapshot-json", required=True, type=Path)
    args = parser.parse_args()

    stage2 = json.loads(args.stage2_manifest.expanduser().resolve().read_text(encoding="utf-8"))
    if stage2.get("source_candidate") != "FG-MIX-T01-S1-C1375":
        raise ValueError("Stage-2 manifest is not based on C1375")
    if PureWindowsPath(stage2["mesh"]).name != MESH_NAME:
        raise ValueError(f"Stage-2 mesh is not {MESH_NAME}")

    solver = connect(server_id=args.server_id)
    records = [
        prepare_child(solver, source, REMOTE_DIR, args.stamp)
        for source in sorted(stage2["children"], key=lambda item: item["branch"])
    ]
    payload = {
        "campaign": "FG-MIX-T01",
        "stage": "S3",
        "purpose": "monitor-repaired Stage-3 start-state copies with total-domain liquid mass history",
        "source_stage2_manifest": str(args.stage2_manifest.expanduser().resolve()),
        "mesh": stage2["mesh"],
        "mesh_readback": {"cells": 231376, "nodes": 697078},
        "total_liquid_mass_definition": {
            "name": MONITOR_NAME,
            "report_type": "volume-mass",
            "phase": "phase-2",
            "cell_zone": "simple-spiral-separator--brine-outlet-",
            "create_report_file": True,
        },
        "runs_submitted": False,
        "children": records,
        "status": "CASE_DATA_VERIFIED",
        "fluent_version": str(solver.get_fluent_version()),
    }
    output = args.snapshot_json.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str))
    print(f"snapshot_json: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

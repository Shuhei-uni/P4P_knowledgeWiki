#!/usr/bin/env python3
"""Prepare (but do not run) the P71A thin-outer cold-start ramp baseline."""
from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import data_path, ensure_remote_directory
from run_p7_e5_cz import LOWER_ZONE, PARENT_ZONE, configure_sources, fluid_names, read_source_tree

OUTER_RING = "bottom-bottom-band1-thin-outer-separator-purnanto"
FULL_COMMAND_KG_S = 116.92
RAMP_ITERATIONS = 100
UPDATE_INTERVAL = 10


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def audit(solver: Any) -> dict[str, Any]:
    zones = fluid_names(solver)
    require(set(zones) == {PARENT_ZONE, LOWER_ZONE}, f"unexpected fluid zones: {zones}")
    source = read_source_tree(solver)
    mass = source[LOWER_ZONE]["phase-2"].get("terms", {}).get("mass", [])
    value = float(mass[0]["value"]) if mass else None
    require(value is not None and abs(value) < 1e-12, f"initial ramp source is not zero: {source}")
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "boundaries")
    outer = boundaries.get("pressure_outlet", {}).get(OUTER_RING, {})
    pressure = outer.get("phase", {}).get("mixture", {}).get("momentum", {}).get("gauge_pressure", {}).get("value")
    require(abs(float(pressure) - 1_120_000.0) < 1e-9, f"outer pressure changed: {pressure}")
    return {"fluid_zones": zones, "source_tree": source, "outer_ring": outer}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--server-id", default="1")
    p.add_argument("--parent-case", required=True)
    p.add_argument("--parent-data", required=True)
    p.add_argument("--run-root", required=True)
    p.add_argument("--manifest", required=True, type=Path)
    a = p.parse_args()
    root = PureWindowsPath(a.run_root)
    output_case = str(root / "P71A-thin-outer-ramp-baseline-active000.cas.h5")
    payload: dict[str, Any] = {
        "status": "RUNNING", "setup_id": "P71A-BB-THIN-OUTER-PO-P1120-RAMP",
        "parent_case": a.parent_case, "parent_data": a.parent_data,
        "ramp_baseline_case": output_case, "ramp_baseline_data": data_path(output_case),
        "full_absorber_command_kg_s": FULL_COMMAND_KG_S,
        "initial_absorber_command_kg_s": 0.0,
        "ramp_iterations": RAMP_ITERATIONS, "update_interval": UPDATE_INTERVAL,
        "iterations_run": 0,
    }
    write_json(a.manifest, payload)
    try:
        s = connect(server_id=a.server_id, start_transcript=False)
        ensure_remote_directory(s, a.run_root)
        for path in (a.parent_case, a.parent_data):
            require(remote_file_exists(s, path), f"parent artifact is absent: {path}")
        for path in (output_case, data_path(output_case)):
            require(not remote_file_exists(s, path), f"refusing to overwrite: {path}")
        remote_chdir(s, str(PureWindowsPath(a.parent_case).parent))
        s.settings.file.read_case(file_name=a.parent_case)
        s.settings.file.read_data(file_name=a.parent_data)
        payload["parent_readback"] = {"fluid_zones": fluid_names(s), "source_tree": read_source_tree(s)}
        # Cold-start state: the runner will calculate -command/V at every
        # 10-iteration boundary.  At active iteration 0 command is exactly 0.
        configure_sources(s, 0.0, {"x": 0.0, "y": 0.0, "z": 0.0})
        payload["pre_save_audit"] = audit(s)
        remote_chdir(s, a.run_root)
        s.settings.file.write_case(file_name=output_case)
        s.settings.file.write_data(file_name=data_path(output_case))
        require(remote_file_exists(s, output_case) and remote_file_exists(s, data_path(output_case)), "ramp baseline pair missing")
        s.settings.file.read_case(file_name=output_case)
        s.settings.file.read_data(file_name=data_path(output_case))
        payload["post_reopen_audit"] = audit(s)
        payload["status"] = "COMPLETE"
        write_json(a.manifest, payload)
        print(json.dumps({"status": payload["status"], "ramp_baseline_case": output_case, "iterations_run": 0}, indent=2))
        return 0
    except Exception as exc:
        payload["status"] = "BLOCKED"; payload["error"] = f"{type(exc).__name__}: {exc}"; payload["traceback"] = traceback.format_exc()
        write_json(a.manifest, payload)
        print(json.dumps({"status": payload["status"], "error": payload["error"]}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

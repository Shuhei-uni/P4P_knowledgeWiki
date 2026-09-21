#!/usr/bin/env python3
"""Create/reopen the corrected C8 thin-ring P0 pressure baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import data_path, ensure_remote_directory, remote_file_sha256
from build_p71a_baseline_v2_virtual_outlet import OUTLET_ZONE, expression_definitions, source_state

OUTER = "bottom-bottom-band1-thin-outer-separator-purnanto"
RINGS = ("bottom", "bottom-thin-inner-separator-purnanto", "bottom-thick-inner-separator-purnanto", "bottom-thick-outer-separator-purnanto", OUTER)
PRESSURE = 1_120_000.0


def require(ok: bool, msg: str) -> None:
    if not ok: raise RuntimeError(msg)


def save_pair(s: Any, case: str, scratch: str) -> dict[str, str]:
    data = data_path(case); require(not remote_file_exists(s, case) and not remote_file_exists(s, data), f"refusing overwrite: {case}")
    s.settings.file.write_case(file_name=case); s.settings.file.write_data(file_name=data)
    require(remote_file_exists(s, case) and remote_file_exists(s, data), "pressure baseline pair missing")
    return {"case": case, "data": data, "case_sha256": remote_file_sha256(s, case, str(PureWindowsPath(scratch) / "pressure-case.sha256.txt")), "data_sha256": remote_file_sha256(s, data, str(PureWindowsPath(scratch) / "pressure-data.sha256.txt"))}


def narrow_audit(s: Any) -> dict[str, Any]:
    bc = safe_get_state(s.settings.setup.boundary_conditions, "C8 v2 pressure baseline boundaries")
    require(OUTER in bc.get("pressure_outlet", {}), "thin outer ring is not a pressure outlet")
    require(all(name in bc.get("wall", {}) for name in RINGS[:-1]), "inner bottom bands are not walls")
    out = bc["pressure_outlet"][OUTER]
    p = out["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"]
    vf = out["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"]["value"]
    require(abs(float(p) - PRESSURE) < 1e-9 and abs(float(vf)) < 1e-12, f"pressure readback mismatch: p={p}, vf={vf}")
    expr = s.settings.setup.named_expressions
    defs = {name: expr[name].definition() for name in expression_definitions()}
    require(defs == expression_definitions(), "v2 expressions differ after pressure baseline reload")
    src = source_state(s)
    require(src[OUTLET_ZONE]["phase-2"]["enable"] is True and src[OUTLET_ZONE]["phase-1"]["enable"] is False, "v2 source scopes changed")
    return {"boundary": out, "pressure_pa": float(p), "phase2_backflow_volume_fraction": float(vf), "source_state": src, "expression_definitions": defs}


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--server-id", default="3"); ap.add_argument("--all-wall-case", required=True); ap.add_argument("--pressure-case", required=True); ap.add_argument("--run-root", required=True); ap.add_argument("--manifest", required=True, type=Path)
    a = ap.parse_args(); result: dict[str, Any] = {"status": "RUNNING", "setup_id": "C8-V2-THIN-RING-PRESSURE-BASELINE-P1120", "server_id": a.server_id, "all_wall_case": a.all_wall_case, "all_wall_data": data_path(a.all_wall_case), "pressure_case": a.pressure_case, "pressure_data": data_path(a.pressure_case), "pressure_pa": PRESSURE}
    a.manifest.parent.mkdir(parents=True, exist_ok=True); a.manifest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    try:
        s = connect(a.server_id, start_transcript=False, tcp_timeout_seconds=120); require(not s.settings.solution.run_calculation.iterating(), "Server 3 is iterating")
        ensure_remote_directory(s, a.run_root); require(remote_file_exists(s, a.all_wall_case) and remote_file_exists(s, data_path(a.all_wall_case)), "all-wall v2 baseline missing")
        s.settings.file.read_case(file_name=a.all_wall_case); s.settings.file.read_data(file_name=data_path(a.all_wall_case))
        bc = s.settings.setup.boundary_conditions; state = safe_get_state(bc, "all-wall pressure baseline input")
        require(all(name in state.get("wall", {}) for name in RINGS), "source baseline is not all-wall")
        bc.set_zone_type(zone_list=[OUTER], new_type="pressure-outlet"); out = bc.pressure_outlet[OUTER]; out.phase["mixture"].momentum.gauge_pressure = PRESSURE; out.phase["mixture"].momentum.backflow_dir_spec_method = "Normal to Boundary"; out.phase["mixture"].momentum.backflow_pressure_spec = "Total Pressure"; out.phase["phase-2"].multiphase.backflow_volume_fraction = 0.0
        result["pre_save_audit"] = narrow_audit(s); result["pair"] = save_pair(s, a.pressure_case, a.run_root)
        s.settings.file.read_case(file_name=a.pressure_case); s.settings.file.read_data(file_name=data_path(a.pressure_case)); result["post_reopen_audit"] = narrow_audit(s); result["status"] = "COMPLETE"; a.manifest.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"); print(json.dumps({"status": result["status"], "pair": result["pair"], "pressure_pa": PRESSURE}, indent=2)); return 0
    except Exception as exc:
        result.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}"}); a.manifest.write_text(json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8"); print(json.dumps(result, indent=2), file=sys.stderr); return 1


if __name__ == "__main__": raise SystemExit(main())

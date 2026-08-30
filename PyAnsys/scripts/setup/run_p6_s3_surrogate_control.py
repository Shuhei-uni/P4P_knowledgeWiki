#!/usr/bin/env python3
"""Run the Phase-06 simplified quasi-steady liquid-inventory controller."""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import ensure_remote_directory, redirect_report_files
from extract_report_plot_histories import parse_report_forms, read_remote_forms
from run_p6_s1_discovery import PARENT_CASE, PARENT_DATA, prove_quiescent, write_status, event

TARGET_KG = 200.0
P_MIN, P_MAX = 1_115_000.0, 1_137_500.0
GAIN_PA_PER_KG, MAX_STEP_PA = 500.0, 2_000.0
REPORT_FILE = "03a_stage3_inventory_y010_liquid_mass-rfile"

def set_pressure(solver, pressure: float) -> float:
    obj = solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"]
    state = safe_get_state(obj, "brine pressure outlet")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option":"value", "value": pressure}
    obj.set_state(state)
    after = safe_get_state(solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"], "brine pressure readback")
    return float(after["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])

def latest_proxy(solver, path: str) -> tuple[int, float]:
    data = parse_report_forms(read_remote_forms(solver, path))
    return int(data["iterations"][-1]), float(data["values"][-1])

def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--server-id",required=True); p.add_argument("--run-root",required=True); p.add_argument("--manifest",type=Path,required=True); p.add_argument("--chunks",type=int,default=5); p.add_argument("--chunk-iterations",type=int,default=100); p.add_argument("--gain-pa-per-kg",type=float,default=GAIN_PA_PER_KG); p.add_argument("--max-step-pa",type=float,default=MAX_STEP_PA); a=p.parse_args()
    if a.manifest.exists(): raise FileExistsError(a.manifest)
    payload={"status":"RUNNING","setup_id":"P6-S3-C","server_id":a.server_id,"run_root":a.run_root,"target_proxy_kg":TARGET_KG,"pressure_bounds_pa":[P_MIN,P_MAX],"chunks":[],"events":[]}; write_status(a.manifest,payload); event(payload,"runner_started"); write_status(a.manifest,payload)
    try:
        s=connect(server_id=a.server_id,start_transcript=False); payload["ownership_preflight"]=prove_quiescent(s)
        if not all(remote_file_exists(s,x) for x in (PARENT_CASE,PARENT_DATA)): raise RuntimeError("F11 pair absent")
        ensure_remote_directory(s,a.run_root); s.scheme.eval(f'(chdir "{quote_scheme_string(a.run_root)}")')
        s.settings.file.read_case(file_name=PARENT_CASE); s.settings.file.read_data(file_name=PARENT_DATA)
        if safe_get_state(s.settings.setup.models,"models")["multiphase"]["model"]!="mixture": raise RuntimeError("unexpected parent model")
        monitor=redirect_report_files(s,str(PureWindowsPath(a.run_root)/"monitors")); proxy_path=monitor[REPORT_FILE]
        pressure=set_pressure(s,1_120_000.0); prepared=str(PureWindowsPath(a.run_root)/"prepared.cas.h5"); final=str(PureWindowsPath(a.run_root)/"final.cas.h5")
        s.settings.file.write_case(file_name=prepared); s.settings.file.write_data(file_name=prepared[:-7]+".dat.h5"); s.settings.file.read_case(file_name=prepared); s.settings.file.read_data(file_name=prepared[:-7]+".dat.h5")
        for n in range(a.chunks):
            event(payload,"chunk_started",chunk=n+1,pressure_pa=pressure); write_status(a.manifest,payload); s.settings.solution.run_calculation.iterate(iter_count=a.chunk_iterations)
            it,mass=latest_proxy(s,proxy_path); error=mass-TARGET_KG; step=max(-a.max_step_pa,min(a.max_step_pa,-a.gain_pa_per_kg*error)); next_p=max(P_MIN,min(P_MAX,pressure+step)); actual=set_pressure(s,next_p)
            payload["chunks"].append({"chunk":n+1,"native_iteration":it,"proxy_mass_kg":mass,"error_kg":error,"pressure_before_pa":pressure,"requested_pressure_after_pa":next_p,"readback_pressure_after_pa":actual}); pressure=actual; write_status(a.manifest,payload)
        s.settings.file.write_case(file_name=final); s.settings.file.write_data(file_name=final[:-7]+".dat.h5")
        if not all(remote_file_exists(s,x) for x in (final,final[:-7]+".dat.h5")): raise RuntimeError("final pair missing")
        payload.update({"status":"COMPLETE","final_case":final,"final_data":final[:-7]+".dat.h5","monitor_files":monitor}); event(payload,"runner_complete"); write_status(a.manifest,payload); return 0
    except Exception as e:
        payload.update({"status":"BLOCKED","error":f"{type(e).__name__}: {e}","traceback":traceback.format_exc()}); event(payload,"runner_blocked",error=payload["error"]); write_status(a.manifest,payload); raise
if __name__=="__main__": main()

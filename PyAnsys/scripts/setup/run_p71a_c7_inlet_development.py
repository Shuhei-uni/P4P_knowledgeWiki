#!/usr/bin/env python3
"""Execute one C7 all-wall, two-inlet development case on Server 1.

The prepared 237k parent is never mutated on disk.  Each child reopens that
same paired parent, applies only its declared simultaneous inlet schedule, and
keeps the recreated phase-2 absorber at its verified -116.92 kg/s integral.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms
from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import (configure_autosave, configure_residual_history, data_path,
    ensure_remote_directory, remote_file_sha256, scientific_readback)
from run_p7_e5_cz import LOWER_ZONE, PARENT_ZONE, configure_sources, read_source_tree, try_integrated_source_reports
from run_p7_e0_ref_discovery import configure_reports as configure_flux_reports
from run_p7_e5_cz_absorb import configure_inventory_reports
from run_p7_e5_cz_absorb_cold import configure_total_inventory_reports
from run_p7_treatment_screen import parse_residuals

LIQUID_BASE, VAPOR_BASE = 116.92, 80.69
HORIZON, RAMP, UPDATE = 5000, 2000, 10
RINGS = ("bottom", "bottom-thin-inner-separator-purnanto", "bottom-thick-inner-separator-purnanto",
         "bottom-thick-outer-separator-purnanto", "bottom-bottom-band1-thin-outer-separator-purnanto")
STARTS = {"C7-R0": 1.0, "C7-R25": .25, "C7-R50": .50, "C7-R75": .75,
          "C8-D0": .25}
REQUIRED_REPORTS = {
    "e0-liquid-mass-total", "e0-liquid-volume-total", "absorb-lower-liquid-mass",
    "absorb-lower-liquid-volume", "absorb-adjacent-liquid-mass", "absorb-broad-liquid-mass",
}
REQUIRED_REPORTS.update(
    f"e0-flux-{phase}-{surface}"
    for phase in ("mixture", "phase1", "phase2")
    for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")
)

def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    tmp.replace(path)

def require(ok: bool, msg: str) -> None:
    if not ok: raise RuntimeError(msg)

def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if isinstance(value, (list, tuple)) and isinstance(key, int):
            value = value[key] if -len(value) <= key < len(value) else None
            continue
        if not isinstance(value, Mapping): return None
        value = value.get(key)
    return value

def flow_multiplier(start: float, active: int) -> float:
    return 1.0 if start == 1.0 else start + (1.0 - start) * min(active / RAMP, 1.0)

def set_inlets(solver: Any, start: float, active: int) -> dict[str, Any]:
    f = flow_multiplier(start, active)
    bc = solver.settings.setup.boundary_conditions.mass_flow_inlet
    bc["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate = LIQUID_BASE * f
    bc["steaminlet"].phase["phase-1"].momentum.mass_flow_rate = VAPOR_BASE * f
    state = safe_get_state(solver.settings.setup.boundary_conditions, "C7 inlet schedule readback")
    liquid = nested(state, "mass_flow_inlet", "liquidinlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value")
    vapor = nested(state, "mass_flow_inlet", "steaminlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value")
    require(liquid is not None and abs(float(liquid) - LIQUID_BASE * f) < 1e-8, f"liquid ramp readback mismatch: {liquid}")
    require(vapor is not None and abs(float(vapor) - VAPOR_BASE * f) < 1e-8, f"vapor ramp readback mismatch: {vapor}")
    return {"active_iteration": active, "multiplier": f, "liquid_phase2_command_kg_s": float(liquid), "vapor_phase1_command_kg_s": float(vapor)}

def set_absorber(solver: Any, start: float, active: int) -> dict[str, Any]:
    """Keep the liquid sink no stronger than the simultaneously ramped input."""
    f = flow_multiplier(start, active)
    raw = solver.settings.results.report.volume_integrals.get_volume(
        cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]},
        cell_function="cell-volume", current_domain="mixture")
    volume = float(raw.get("Net", raw) if isinstance(raw, Mapping) else raw)
    require(math.isfinite(volume) and volume > 0, f"invalid C7 lower-zone volume: {volume}")
    source = configure_sources(solver, -LIQUID_BASE * f / volume, {"x": 0.0, "y": 0.0, "z": 0.0})
    tree = read_source_tree(solver)
    actual = float(nested(tree, LOWER_ZONE, "phase-2", "terms", "mass", 0, "value"))
    require(abs(actual * volume + LIQUID_BASE * f) < 1e-6,
            f"C7 absorber schedule mismatch: density={actual}, volume={volume}, f={f}")
    return {"active_iteration": active, "multiplier": f, "target_integrated_phase2_sink_kg_s": -LIQUID_BASE*f,
            "source_density_kg_m3_s": actual, "lower_volume_m3": volume, "source_readback": source}

def audit(solver: Any, expected_f: float | None = None) -> dict[str, Any]:
    b = safe_get_state(solver.settings.setup.boundary_conditions, "C7 boundary audit")
    walls = set((b.get("wall") or {}) if isinstance(b, Mapping) else {})
    require(set(RINGS).issubset(walls), f"all five C7 bottom bands are not walls: {sorted(walls)}")
    pressure = set((b.get("pressure_outlet") or {}) if isinstance(b, Mapping) else {})
    require(pressure <= {"settings", "steamoutlet"}, f"C7 has unauthorized pressure outlet: {sorted(pressure)}")
    source = read_source_tree(solver)
    mass = nested(source, LOWER_ZONE, "phase-2", "terms", "mass", 0, "value")
    require(mass is not None, "C7 phase-2 lower absorber source absent")
    volume = solver.settings.results.report.volume_integrals.get_volume(cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]}, cell_function="cell-volume", current_domain="mixture")
    volume = float(volume.get("Net", volume) if isinstance(volume, Mapping) else volume)
    multiplier = 1.0 if expected_f is None else expected_f
    require(math.isfinite(volume) and volume > 0 and abs(float(mass) * volume + LIQUID_BASE * multiplier) < 1e-6,
            f"absorber integral does not match C7 multiplier {multiplier}: density={mass}, volume={volume}")
    result = {"bottom_wall_bands": list(RINGS), "lower_volume_m3": volume,
              "phase2_source_density_kg_m3_s": float(mass), "integrated_phase2_source_kg_s": float(mass)*volume,
              "source_tree": source, "boundaries": b}
    result["absorber_multiplier"] = multiplier
    return result

def save_pair(solver: Any, case: str) -> None:
    dat = data_path(case)
    require(not remote_file_exists(solver, case) and not remote_file_exists(solver, dat), f"refusing to overwrite checkpoint {case}")
    solver.settings.file.write_case(file_name=case); solver.settings.file.write_data(file_name=dat)
    require(remote_file_exists(solver, case) and remote_file_exists(solver, dat), f"checkpoint pair absent: {case}")

def configure_c7_report_files(solver: Any, monitor_root: str, case: str) -> dict[str, str]:
    """Bind fresh monitor paths without editing inherited read-only reports.

    Prepared C7 pairs already carry the complete 18-definition evidence
    package.  Fluent 2025 R2 can expose those definitions as read-only after a
    case/data reload, so recreating them or toggling optional properties emits
    API errors and can leave the runner stuck in preflight.  Reuse the proven
    definitions and only remove generic stale report-file objects before
    rebinding the existing one-definition report files.
    """
    ensure_remote_directory(solver, monitor_root)
    files = solver.settings.solution.monitor.report_files
    mapping: dict[str, str] = {}
    stale: list[str] = []
    for name in list(files.get_object_names()):
        state = safe_get_state(files[name], f"C7 report-file {name}")
        defs = state.get("report_defs") if isinstance(state, Mapping) else None
        if not isinstance(defs, list) or len(defs) != 1 or defs[0] not in REQUIRED_REPORTS:
            stale.append(name)
            continue
        definition = str(defs[0])
        mapping[definition] = str(name)
    if stale:
        files.delete(name_list=stale)
    # A genuinely uninstrumented parent is outside the normal C7 path.  Keep a
    # deterministic fallback for it, but do not touch the valid inherited
    # package used by the prepared local parent.
    missing_defs = REQUIRED_REPORTS - set(mapping)
    if missing_defs:
        configure_flux_reports(solver)
        configure_total_inventory_reports(solver)
        configure_inventory_reports(solver)
        mapping = {}
        for name in list(files.get_object_names()):
            state = safe_get_state(files[name], f"C7 report-file {name}")
            defs = state.get("report_defs") if isinstance(state, Mapping) else None
            if isinstance(defs, list) and len(defs) == 1 and defs[0] in REQUIRED_REPORTS:
                mapping[str(defs[0])] = str(name)
    for definition, name in mapping.items():
        path = str(PureWindowsPath(monitor_root) / f"{case}-{definition}.out")
        require(not remote_file_exists(solver, path), f"refusing to overwrite monitor {path}")
        files[name].file_name = path
        reread = safe_get_state(files[name], f"C7 report-file binding {name}")
        actual = reread.get("file_name") if isinstance(reread, Mapping) else None
        require(PureWindowsPath(str(actual)).name == PureWindowsPath(path).name,
                f"monitor path mismatch for {definition}: {actual!r}")
        mapping[definition] = path
    missing = REQUIRED_REPORTS - set(mapping)
    require(not missing, f"C7 report-file bindings incomplete: {sorted(missing)}")
    return mapping

def paths(checkpoint_root: str, final_root: str, case: str, stamp: str) -> dict[str, str]:
    """Keep working pairs on the selected Fluent host's local disk; publish only final pair."""
    p = PureWindowsPath(checkpoint_root) / case / stamp
    final = PureWindowsPath(final_root) / case / stamp
    out={"prepared":str(p/f"{case}-prepared.cas.h5"),"active000":str(p/f"{case}-active000.cas.h5"),"monitors":str(p/"monitors"),"scratch":str(p/"scratch"),"final_root":str(final)}
    out.update({f"active{i}":str(p/f"{case}-active{i}.cas.h5") for i in (1000,2000,3000,4000)})
    out["active5000"] = str(final / f"{case}-active5000.cas.h5")
    return out

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--case", choices=STARTS, required=True); ap.add_argument("--parent-case", required=True); ap.add_argument("--parent-data", required=True); ap.add_argument("--checkpoint-root", required=True); ap.add_argument("--final-root", required=True); ap.add_argument("--local-dir", required=True,type=Path); ap.add_argument("--server-id",default="1"); ap.add_argument("--stamp",default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")); ap.add_argument("--parent-identity-receipt", required=True, help="Local receipt describing the exact prepared parent; never infer a receipt from another server or run."); ap.add_argument("--family-label", default="P71A-INLET-DEVELOPMENT-RAMP"); ap.add_argument("--start-active", type=int, default=0); a=ap.parse_args()
    require(0 <= a.start_active < HORIZON and a.start_active % UPDATE == 0, "start-active must be a valid C7 schedule coordinate")
    local=a.local_dir.resolve(); local.mkdir(parents=True,exist_ok=False)
    man=local/"run-manifest.json"; start=STARTS[a.case]; p=paths(a.checkpoint_root,a.final_root,a.case,a.stamp)
    m={"status":"RUNNING","setup_id":a.case,"family":a.family_label,"server_id":a.server_id,"parent_case":a.parent_case,"parent_data":a.parent_data,"checkpoint_root_local_disk":a.checkpoint_root,"final_root_onedrive":a.final_root,"requested_active_iterations":HORIZON,"start_active_iteration":a.start_active,"inlet_start_multiplier":start,"ramp_active_iterations":0 if start==1 else RAMP,"hold_active_iterations":HORIZON if start==1 else HORIZON-RAMP,"absorber_target_kg_s":-LIQUID_BASE,"artifacts":p,"events":[]}; dump(man,m)
    capture=None
    try:
        # Case/data reloads and ten-iteration blocks can legitimately exceed
        # a five-second RPC window on the remote Server-3 filesystem.  Keep a
        # bounded but practical timeout so a normal long read is not mistaken
        # for a disconnected solver stream.
        s=connect(a.server_id,start_transcript=True,tcp_timeout_seconds=120); require("2025 R2" in str(s.get_fluent_version()),"unexpected Fluent version")
        ensure_remote_directory(s,str(PureWindowsPath(a.checkpoint_root)/a.case/a.stamp)); ensure_remote_directory(s,p["monitors"]); ensure_remote_directory(s,p["scratch"]); ensure_remote_directory(s,p["final_root"])
        require(remote_file_exists(s,a.parent_case) and remote_file_exists(s,a.parent_data),"C7 all-wall parent pair missing")
        # This exact parent pair must have its own supplied identity receipt.
        # Do not infer identity from another server or another C7-equivalent
        # run, and do not serialize every child behind a second multi-gigabyte
        # parent-data hash when the caller already holds a durable receipt.
        m["parent_identity"]={"case":a.parent_case,"data":a.parent_data,
                              "sha256_receipt":a.parent_identity_receipt}
        s.settings.file.read_case(file_name=a.parent_case); s.settings.file.read_data(file_name=a.parent_data)
        # A continuation parent carries the schedule state at
        # ``start_active``.  The untouched prepared parent is the one
        # exception: it intentionally contains the base absorber source, and
        # a reduced-flow case applies its synchronized initial multiplier
        # immediately after loading it.  Audit the prepared parent at base
        # flow, then audit the applied initial schedule below.
        parent_multiplier = 1.0 if a.start_active == 0 else flow_multiplier(start, a.start_active)
        m["parent_readback"]=audit(s, parent_multiplier)
        report_paths=configure_c7_report_files(s,p["monitors"],a.case)
        m["report_paths"]=report_paths; m["residual_configuration"]=configure_residual_history(s,HORIZON+200); m["autosave_configuration"]={"mode":"manual paired saves", "checkpoint_locations":"local Fluent host disk", "final_location":"OneDrive"}
        initial_f = flow_multiplier(start, a.start_active)
        m["initial_inlet_schedule"] = set_inlets(s,start,a.start_active)
        m["initial_absorber_schedule"] = set_absorber(s,start,a.start_active)
        save_pair(s,p["prepared"]); s.settings.file.read_case(file_name=p["prepared"]); s.settings.file.read_data(file_name=data_path(p["prepared"])); m["prepared_reopen"]=audit(s,initial_f)
        if a.start_active == 0: save_pair(s,p["active000"])
        capture=SessionTranscriptCapture(s,stream_path=local/"transcript.txt",echo=False); capture.start(); marker=capture.mark(); active=a.start_active
        while active<HORIZON:
            block=min(UPDATE,HORIZON-active); before=capture.mark(); s.settings.solution.run_calculation.iterate(iter_count=block); active+=block; text=capture.text_since(before)
            if re.search(r"floating point exception|Divergence detected in AMG solver|fatal error",text,re.I):
                m.update({"last_valid_active_iteration":active-block,"failure_console_tail":text[-16000:]}); dump(man,m); raise RuntimeError(f"solver failure in block ending at C7 active {active}")
            event=set_inlets(s,start,active); event["event"]="inlet_ramp_update"
            event["absorber_schedule"] = set_absorber(s,start,active)
            m["events"].append(event)
            if active in (1000,2000,3000,4000,5000): save_pair(s,p[f"active{active}"]); event["checkpoint_case"]=p[f"active{active}"]
            if active==a.start_active+50: require(all(remote_file_exists(s,x) for x in report_paths.values()),"C7 monitor files did not appear during 50-iteration smoke")
            if active%100==0: dump(man,m)
        expected_points = HORIZON - a.start_active
        residuals=parse_residuals(capture.text_since(marker)); require(residuals["point_count"]>=expected_points,f"short residual evidence: {residuals['point_count']}"); dump(local/"residuals.json",residuals)
        reports={}
        for name,path in report_paths.items():
            require(remote_file_exists(s,path),f"missing report {name}"); h=parse_report_forms(read_remote_forms(s,path)); require(h["points"]>=expected_points,f"short report {name}: {h['points']}"); h.update({"monitor_name":name,"remote_file":path}); reports[name]=h
        dump(local/"reports.json",{"reports":reports}); s.settings.file.read_case(file_name=p["active5000"]); s.settings.file.read_data(file_name=data_path(p["active5000"])); m["terminal_readback"]=audit(s); m["integrated_source_reports"]=try_integrated_source_reports(s); m["final_sha256"]={"case":remote_file_sha256(s,p["active5000"],str(PureWindowsPath(p["scratch"])/"final-case.sha256.txt")),"data":remote_file_sha256(s,data_path(p["active5000"]),str(PureWindowsPath(p["scratch"])/"final-data.sha256.txt"))}; m.update({"achieved_active_iterations":active,"residuals":residuals,"status":"COMPLETE"}); dump(man,m); return 0
    except Exception as exc:
        m.update({"status":"BLOCKED","error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()}); dump(man,m); return 1
    finally:
        if capture: capture.close()

if __name__ == "__main__": raise SystemExit(main())

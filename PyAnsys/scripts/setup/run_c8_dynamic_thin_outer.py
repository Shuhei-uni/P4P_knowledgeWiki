#!/usr/bin/env python3
"""Run one independent Server-3 C8 delayed thin-outer-ring pressure case.

Each invocation reads the immutable C8-D0 pair afresh, rebuilds its own
instrumentation, and changes no boundary except the named outer ring after the
recorded persistence trigger.  Local checkpoints are deliberately separate
from the OneDrive terminal pair.
"""
from __future__ import annotations

import argparse, json, re, sys, traceback
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_residual_history, data_path, ensure_remote_directory
from run_p71a_c7_inlet_development import audit as audit_all_wall
from run_p71a_c7_inlet_development import configure_c7_report_files, save_pair
from run_p7_e0_ref_discovery import replace_named, set_optional
from run_p7_e5_cz_absorb import configure_inventory_reports
from run_p7_e5_cz_absorb_cold import configure_total_inventory_reports
from run_p7_treatment_screen import parse_residuals

OUTER = "bottom-bottom-band1-thin-outer-separator-purnanto"
RINGS = ("bottom", "bottom-thin-inner-separator-purnanto", "bottom-thick-inner-separator-purnanto", "bottom-thick-outer-separator-purnanto", OUTER)
HORIZON, STEP, PERSISTENCE = 5000, 10, 20
PRESSURES = {"C8-P0": 1_120_000.0, "C8-P10": 1_110_000.0, "C8-P30": 1_090_000.0, "C8-P60": 1_060_000.0}
BASE = {"e0-liquid-mass-total", "e0-liquid-volume-total", "absorb-lower-liquid-mass", "absorb-lower-liquid-volume", "absorb-adjacent-liquid-mass", "absorb-broad-liquid-mass"}
BASE |= {f"e0-flux-{phase}-{surface}" for phase in ("mixture", "phase1", "phase2") for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")}
RING_REPORTS = {f"c8-ring-flux-{phase}" for phase in ("mixture", "phase1", "phase2")}
REQUIRED = BASE | RING_REPORTS

def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    tmp.replace(path)

def require(ok: bool, msg: str) -> None:
    if not ok: raise RuntimeError(msg)

def paths(root: str, final_root: str, case: str, stamp: str) -> dict[str, str]:
    local = PureWindowsPath(root) / case / stamp; final = PureWindowsPath(final_root) / case / stamp
    out = {"local_root": str(local), "monitor_root": str(local / "monitors"), "scratch": str(local / "scratch"), "prepared": str(local / f"{case}-prepared.cas.h5"), "active000": str(local / f"{case}-active000.cas.h5"), "pre_switch": str(local / f"{case}-pre-switch.cas.h5"), "post_switch": str(local / f"{case}-post-switch.cas.h5"), "final_root": str(final)}
    out.update({f"active{i}": str(local / f"{case}-active{i}.cas.h5") for i in (1000,2000,3000,4000)})
    out["active5000"] = str(final / f"{case}-active5000.cas.h5")
    return out

def ring_reports(solver: Any) -> None:
    flux = solver.settings.solution.report_definitions.flux
    for phase in ("mixture", "phase-1", "phase-2"):
        name = f"c8-ring-flux-{phase.replace('-', '')}"
        report = replace_named(flux, name); report.report_type = "flux-massflow"; report = flux[name]
        report.boundaries = [OUTER]; report.phase = phase
        for key, value in (("per_selection", False), ("average_over", 1), ("retain_instantaneous_values", True), ("create_report_file", True), ("create_report_plot", True)): set_optional(report, key, value)
        state = safe_get_state(report, f"C8 ring report {name}")
        require(state.get("report_type") == "flux-massflow" and state.get("boundaries") == [OUTER] and state.get("phase") == phase, f"ring report readback mismatch: {name}")

def bind_reports(solver: Any, root: str, case: str) -> dict[str, str]:
    # The inherited generic files are removed first.  The base helper creates
    # one fresh file per base definition; then we attach the three ring files.
    mapping = configure_c7_report_files(solver, root, case)
    # The base reset deletes every inherited report-file object, including the
    # automatically created ring files.  Recreate the ring definitions only
    # after that reset so Fluent creates three fresh, bindable C8 files.
    ring_reports(solver)
    files = solver.settings.solution.monitor.report_files
    for name in files.get_object_names():
        state = safe_get_state(files[name], f"C8 report file {name}")
        defs = state.get("report_defs") if isinstance(state, Mapping) else None
        if not isinstance(defs, list) or len(defs) != 1 or defs[0] not in RING_REPORTS: continue
        definition = str(defs[0]); file_name = str(PureWindowsPath(root) / f"{case}-{definition}.out")
        require(not remote_file_exists(solver, file_name), f"refusing monitor overwrite: {file_name}")
        files[name].file_name = file_name
        after = safe_get_state(files[name], f"C8 report binding {name}")
        require(PureWindowsPath(str(after.get("file_name"))).name == PureWindowsPath(file_name).name, f"ring monitor binding failed: {definition}")
        mapping[definition] = file_name
    require(set(mapping) == REQUIRED, f"C8 report package incomplete: {sorted(REQUIRED-set(mapping))}")
    return mapping

def lower_value(solver: Any, path: str) -> float:
    history = parse_report_forms(read_remote_forms(solver, path))
    values = history.get("values") or []
    require(values, "lower-liquid monitor has no samples")
    return float(values[-1])

def wall_audit(solver: Any) -> dict[str, Any]:
    return audit_all_wall(solver, 1.0)

def open_ring(solver: Any, pressure: float) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    bc.set_zone_type(zone_list=[OUTER], new_type="pressure-outlet")
    outlet = bc.pressure_outlet[OUTER]
    state = safe_get_state(outlet, "C8 outer pressure outlet before set")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option":"value", "value":pressure}
    state["phase"]["mixture"]["momentum"]["backflow_dir_spec_method"] = "Normal to Boundary"
    state["phase"]["mixture"]["momentum"]["backflow_pressure_spec"] = "Total Pressure"
    state["phase"]["phase-2"]["multiphase"]["backflow_volume_fraction"] = {"option":"value", "value":0.0}
    outlet.set_state(state)
    boundaries = safe_get_state(bc, "C8 switch readback")
    outer = boundaries.get("pressure_outlet", {}).get(OUTER, {})
    actual = outer.get("phase", {}).get("mixture", {}).get("momentum", {}).get("gauge_pressure", {}).get("value")
    vf = outer.get("phase", {}).get("phase-2", {}).get("multiphase", {}).get("backflow_volume_fraction", {}).get("value")
    require(actual is not None and abs(float(actual)-pressure) < 1e-6 and vf is not None and abs(float(vf)) < 1e-12, f"C8 outlet readback failed: {outer}")
    require(all(name in boundaries.get("wall", {}) for name in RINGS[:-1]), "C8 switch changed a retained bottom wall")
    return {"pressure_pa": float(actual), "phase2_backflow_volume_fraction": float(vf), "boundary": outer}

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--case", choices=PRESSURES, required=True); ap.add_argument("--parent-case", required=True); ap.add_argument("--parent-data", required=True); ap.add_argument("--checkpoint-root", required=True); ap.add_argument("--final-root", required=True); ap.add_argument("--local-dir", required=True, type=Path); ap.add_argument("--server-id", default="3"); ap.add_argument("--stamp", required=True); ap.add_argument("--threshold-kg", required=True, type=float); ap.add_argument("--trigger-receipt", required=True, type=Path); a=ap.parse_args()
    local=a.local_dir.resolve(); local.mkdir(parents=True, exist_ok=False); man=local/"run-manifest.json"; p=paths(a.checkpoint_root,a.final_root,a.case,a.stamp)
    m: dict[str, Any] = {"status":"RUNNING", "setup_id":a.case, "family":"P71A-INDEPENDENT-C8-DYNAMIC-THIN-OUTER", "server_id":a.server_id, "parent_case":a.parent_case, "parent_data":a.parent_data, "trigger_receipt":str(a.trigger_receipt), "threshold_kg":a.threshold_kg, "persistence_samples":PERSISTENCE, "cadence_active_iterations":STEP, "pressure_pa":PRESSURES[a.case], "artifacts":p, "events":[]}; dump(man,m); cap=None
    try:
        receipt=json.loads(a.trigger_receipt.read_text(encoding="utf-8")); require(abs(float(receipt["threshold_kg"])-a.threshold_kg)<1e-10, "trigger receipt threshold mismatch")
        s=connect(a.server_id,start_transcript=True,tcp_timeout_seconds=120); require("2025 R2" in str(s.get_fluent_version()), "unexpected Fluent version")
        for directory in (p["local_root"],p["monitor_root"],p["scratch"],p["final_root"]): ensure_remote_directory(s,directory)
        require(remote_file_exists(s,a.parent_case) and remote_file_exists(s,a.parent_data), "C8-D0 parent pair missing")
        s.settings.file.read_case(file_name=a.parent_case); s.settings.file.read_data(file_name=a.parent_data); m["parent_readback"]=wall_audit(s)
        ring_reports(s); configure_total_inventory_reports(s); configure_inventory_reports(s); report_paths=bind_reports(s,p["monitor_root"],a.case); m["report_paths"]=report_paths; m["residual_configuration"]=configure_residual_history(s,HORIZON+200)
        save_pair(s,p["prepared"]); s.settings.file.read_case(file_name=p["prepared"]); s.settings.file.read_data(file_name=data_path(p["prepared"])); m["prepared_reopen"]=wall_audit(s); save_pair(s,p["active000"])
        cap=SessionTranscriptCapture(s,stream_path=local/"transcript.txt",echo=False); cap.start(); marker=cap.mark(); streak=0; switched=False
        for active in range(STEP,HORIZON+1,STEP):
            before=cap.mark(); s.settings.solution.run_calculation.iterate(iter_count=STEP); text=cap.text_since(before)
            if re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I): m.update({"last_valid_active_iteration":active-STEP,"failure_console_tail":text[-16000:]}); raise RuntimeError(f"solver failure at active {active}")
            lower=lower_value(s,report_paths["absorb-lower-liquid-mass"]); streak = streak+1 if lower >= a.threshold_kg else 0
            event={"active_iteration":active,"lower_liquid_mass_kg":lower,"trigger_streak_samples":streak,"ring_state":"pressure-outlet" if switched else "wall"}
            if not switched and streak >= PERSISTENCE:
                save_pair(s,p["pre_switch"]); event["pre_switch_case"]=p["pre_switch"]; event["switch_readback"]=open_ring(s,PRESSURES[a.case]); save_pair(s,p["post_switch"]); event["post_switch_case"]=p["post_switch"]; switched=True; event["switch_active_iteration"]=active; m["switch_active_iteration"]=active
            if active in (1000,2000,3000,4000,5000): save_pair(s,p[f"active{active}"]); event["checkpoint_case"]=p[f"active{active}"]
            if active == 50: require(all(remote_file_exists(s,x) for x in report_paths.values()), "C8 monitor smoke failed")
            m["events"].append(event)
            if active % 100 == 0: dump(man,m)
        residuals=parse_residuals(cap.text_since(marker)); require(residuals["point_count"] >= HORIZON, "short residual history")
        reports={}
        for name,path in report_paths.items():
            h=parse_report_forms(read_remote_forms(s,path)); require(h["points"] >= HORIZON, f"short report: {name}"); h.update({"monitor_name":name,"remote_file":path}); reports[name]=h
        dump(local/"residuals.json",residuals); dump(local/"reports.json",{"reports":reports})
        m.update({"achieved_active_iterations":HORIZON,"switched":switched,"status":"COMPLETE","residuals":residuals}); dump(man,m); return 0
    except Exception as exc:
        m.update({"status":"BLOCKED","error":f"{type(exc).__name__}: {exc}","traceback":traceback.format_exc()}); dump(man,m); return 1
    finally:
        if cap: cap.close()

if __name__ == "__main__": raise SystemExit(main())

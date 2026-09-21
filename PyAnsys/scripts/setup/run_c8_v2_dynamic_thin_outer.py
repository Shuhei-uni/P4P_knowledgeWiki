#!/usr/bin/env python3
"""Run one corrected C8 pressure child with the Phase 7.1A v2 absorber."""
from __future__ import annotations

import argparse
from collections.abc import Mapping
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_residual_history, data_path, ensure_remote_directory
from build_p71a_baseline_v2_virtual_outlet import OUTLET_ZONE, expression_definitions, source_state
from run_c8_dynamic_thin_outer import (BASE, HORIZON, PERSISTENCE, PRESSURES, REQUIRED, RINGS, STEP, bind_reports, dump, lower_value, open_ring, parse_residuals, paths, save_pair)


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def v2_wall_audit(solver: Any) -> dict[str, Any]:
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "C8 v2 child all-wall boundaries")
    require(all(name in boundaries.get("wall", {}) for name in RINGS), "v2 child parent is not all-wall")
    expr = solver.settings.setup.named_expressions
    defs = {name: expr[name].definition() for name in expression_definitions()}
    require(defs == expression_definitions(), "v2 child expression definitions differ")
    sources = source_state(solver)
    require(sources[OUTLET_ZONE]["phase-2"]["enable"] is True, "v2 phase-2 source disabled")
    require(sources[OUTLET_ZONE]["phase-1"]["enable"] is False, "v2 phase-1 source enabled")
    require(sources[OUTLET_ZONE]["mixture"]["enable"] is True, "v2 mixture source disabled")
    command = float(expr["P71V2Command"].get_value())
    require(math.isfinite(command) and command > 0, f"invalid v2 command: {command}")
    return {"boundaries": boundaries, "definitions": defs, "source_state": sources, "command_kg_s": command}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", choices=PRESSURES, required=True)
    ap.add_argument("--parent-case", required=True)
    ap.add_argument("--parent-data", required=True)
    ap.add_argument("--checkpoint-root", required=True)
    ap.add_argument("--final-root", required=True)
    ap.add_argument("--local-dir", required=True, type=Path)
    ap.add_argument("--server-id", default="3")
    ap.add_argument("--stamp", required=True)
    ap.add_argument("--threshold-kg", required=True, type=float)
    ap.add_argument("--trigger-receipt", required=True, type=Path)
    args = ap.parse_args()
    receipt = json.loads(args.trigger_receipt.read_text(encoding="utf-8"))
    require(abs(float(receipt["threshold_kg"]) - args.threshold_kg) < 1e-10, "trigger receipt threshold mismatch")
    local = args.local_dir.resolve(); local.mkdir(parents=True, exist_ok=False)
    p = paths(args.checkpoint_root, args.final_root, args.case, args.stamp)
    manifest: dict[str, Any] = {"status": "RUNNING", "setup_id": args.case, "family": "P71A-C8-V2-DYNAMIC-THIN-OUTER", "server_id": args.server_id, "parent_case": args.parent_case, "parent_data": args.parent_data, "trigger_receipt": str(args.trigger_receipt), "threshold_kg": args.threshold_kg, "persistence_samples": PERSISTENCE, "cadence_active_iterations": STEP, "pressure_pa": PRESSURES[args.case], "artifacts": p, "events": [], "absorber": "P71A v2 throughput-controlled phase-2 virtual outlet"}
    dump(local / "run-manifest.json", manifest)
    capture = None
    try:
        s = connect(args.server_id, start_transcript=True, tcp_timeout_seconds=120)
        require("2025 R2" in str(s.get_fluent_version()), "unexpected Fluent version")
        for directory in (p["local_root"], p["monitor_root"], p["scratch"], p["final_root"]): ensure_remote_directory(s, directory)
        require(remote_file_exists(s, args.parent_case) and remote_file_exists(s, args.parent_data), "corrected v2 all-wall parent missing")
        s.settings.file.read_case(file_name=args.parent_case); s.settings.file.read_data(file_name=args.parent_data)
        manifest["parent_readback"] = v2_wall_audit(s)
        report_paths = bind_reports(s, p["monitor_root"], args.case); manifest["report_paths"] = report_paths; manifest["residual_configuration"] = configure_residual_history(s, HORIZON + 200)
        save_pair(s, p["prepared"]); s.settings.file.read_case(file_name=p["prepared"]); s.settings.file.read_data(file_name=data_path(p["prepared"]))
        manifest["prepared_reopen"] = v2_wall_audit(s); save_pair(s, p["active000"])
        capture = SessionTranscriptCapture(s, stream_path=local / "transcript.txt", echo=False); capture.start(); marker = capture.mark(); streak = 0; switched = False
        for active in range(STEP, HORIZON + 1, STEP):
            before = capture.mark(); s.settings.solution.run_calculation.iterate(iter_count=STEP); text = capture.text_since(before)
            if re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I):
                manifest.update({"last_valid_active_iteration": active - STEP, "failure_console_tail": text[-16000:]}); dump(local / "run-manifest.json", manifest); raise RuntimeError(f"solver failure at active {active}")
            lower = lower_value(s, report_paths["absorb-lower-liquid-mass"]); streak = streak + 1 if lower >= args.threshold_kg else 0
            event = {"active_iteration": active, "lower_liquid_mass_kg": lower, "trigger_streak_samples": streak, "ring_state": "pressure-outlet" if switched else "wall"}
            if not switched and streak >= PERSISTENCE:
                save_pair(s, p["pre_switch"]); event["pre_switch_case"] = p["pre_switch"]; event["switch_readback"] = open_ring(s, PRESSURES[args.case]); save_pair(s, p["post_switch"]); switched = True; event["switch_active_iteration"] = active; manifest["switch_active_iteration"] = active
            if active in (1000, 2000, 3000, 4000, 5000): save_pair(s, p[f"active{active}"]); event["checkpoint_case"] = p[f"active{active}"]
            if active == 50: require(all(remote_file_exists(s, x) for x in report_paths.values()), "v2 C8 monitor smoke failed")
            manifest["events"].append(event)
            if active % 100 == 0: dump(local / "run-manifest.json", manifest)
        residuals = parse_residuals(capture.text_since(marker)); require(residuals["point_count"] >= HORIZON, "short v2 child residual history")
        reports = {}
        for name, path in report_paths.items():
            h = parse_report_forms(read_remote_forms(s, path)); require(h["points"] >= HORIZON, f"short v2 child report {name}: {h['points']}"); h.update({"monitor_name": name, "remote_file": path}); reports[name] = h
        (local / "residuals.json").write_text(json.dumps(residuals, indent=2, default=str) + "\n", encoding="utf-8")
        (local / "reports.json").write_text(json.dumps({"reports": reports}, indent=2, default=str) + "\n", encoding="utf-8")
        manifest.update({"achieved_active_iterations": HORIZON, "switched": switched, "residuals": residuals, "status": "COMPLETE" if switched else "BLOCKED_NO_TRIGGER"}); dump(local / "run-manifest.json", manifest)
        return 0 if switched else 1
    except Exception as exc:
        manifest.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}); dump(local / "run-manifest.json", manifest); return 1
    finally:
        if capture: capture.close()


if __name__ == "__main__": raise SystemExit(main())

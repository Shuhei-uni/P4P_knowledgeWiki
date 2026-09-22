#!/usr/bin/env python3
"""Run the corrected all-wall C8-D0 development parent on Server 3.

This is the v2 absorber replacement screen used to derive a fresh lower-liquid
trigger.  The thin outer ring and all other bottom bands remain walls for the
whole 5,000-iteration horizon.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from datetime import datetime, timezone
import json
import math
from pathlib import Path, PureWindowsPath
import re
import statistics
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]

from extract_report_plot_histories import parse_report_forms, read_remote_forms
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_residual_history, data_path, ensure_remote_directory, remote_file_sha256
from build_p71a_baseline_v2_virtual_outlet import OUTLET_ZONE, SOURCE_HOOKS, expression_definitions, source_state
from run_c8_dynamic_thin_outer import (BASE, REQUIRED, RINGS, bind_reports, dump, parse_residuals, save_pair)

HORIZON, BATCH, PERSISTENCE = 5000, 1000, 20


def require(ok: bool, msg: str) -> None:
    if not ok:
        raise RuntimeError(msg)


def v2_audit(solver: Any) -> dict[str, Any]:
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "C8 v2 all-wall boundaries")
    require(all(name in boundaries.get("wall", {}) for name in RINGS), "corrected C8-D0 is not all-wall")
    expr = solver.settings.setup.named_expressions
    defs = {name: expr[name].definition() for name in expression_definitions()}
    require(defs == expression_definitions(), "v2 expression definitions differ from baseline")
    sources = source_state(solver)
    require(sources[OUTLET_ZONE]["phase-2"]["enable"] is True, "v2 liquid source disabled")
    require(sources[OUTLET_ZONE]["phase-1"]["enable"] is False, "v2 vapor source enabled")
    require(sources[OUTLET_ZONE]["mixture"]["enable"] is True, "v2 mixture momentum/turbulence source disabled")
    command = float(expr["P71V2Command"].get_value())
    require(math.isfinite(command) and command > 0, f"invalid v2 command: {command}")
    return {"boundaries": boundaries, "definitions": defs, "source_state": sources, "command_kg_s": command}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--server-id", default="3")
    ap.add_argument("--parent-case", required=True)
    ap.add_argument("--parent-data", required=True)
    ap.add_argument("--checkpoint-root", required=True)
    ap.add_argument("--final-root", required=True)
    ap.add_argument("--local-dir", required=True, type=Path)
    ap.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    ap.add_argument("--trigger-receipt", required=True, type=Path)
    args = ap.parse_args()
    local = args.local_dir.resolve(); local.mkdir(parents=True, exist_ok=False)
    case = "C8-D0-V2"
    work = PureWindowsPath(args.checkpoint_root) / case / args.stamp
    final = PureWindowsPath(args.final_root) / case / args.stamp
    paths = {"prepared": str(work / f"{case}-prepared.cas.h5"), "active000": str(work / f"{case}-active000.cas.h5"), "monitor_root": str(work / "monitors"), "scratch": str(work / "scratch"), "final_root": str(final), "active5000": str(final / f"{case}-active5000.cas.h5")}
    for active in (1000, 2000, 3000, 4000): paths[f"active{active}"] = str(work / f"{case}-active{active}.cas.h5")
    manifest: dict[str, Any] = {"status": "RUNNING", "setup_id": case, "family": "P71A-C8-V2-ALL-WALL-DEVELOPMENT", "server_id": args.server_id, "parent_case": args.parent_case, "parent_data": args.parent_data, "checkpoint_root": args.checkpoint_root, "final_root": args.final_root, "artifacts": paths, "requested_active_iterations": HORIZON, "events": []}
    dump(local / "run-manifest.json", manifest)
    capture = None
    try:
        s = connect(args.server_id, start_transcript=True, tcp_timeout_seconds=120)
        require("2025 R2" in str(s.get_fluent_version()), "unexpected Fluent version")
        for directory in (str(work), paths["monitor_root"], paths["scratch"], paths["final_root"]): ensure_remote_directory(s, directory)
        require(remote_file_exists(s, args.parent_case) and remote_file_exists(s, args.parent_data), "v2 all-wall parent pair missing")
        s.settings.file.read_case(file_name=args.parent_case); s.settings.file.read_data(file_name=args.parent_data)
        manifest["parent_readback"] = v2_audit(s)
        report_paths = bind_reports(s, paths["monitor_root"], case)
        manifest["report_paths"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(s, HORIZON + 200)
        save_pair(s, paths["prepared"]); s.settings.file.read_case(file_name=paths["prepared"]); s.settings.file.read_data(file_name=data_path(paths["prepared"]))
        manifest["prepared_reopen"] = v2_audit(s); save_pair(s, paths["active000"])
        capture = SessionTranscriptCapture(s, stream_path=local / "transcript.txt", echo=False); capture.start(); marker = capture.mark(); active = 0
        while active < HORIZON:
            before = capture.mark(); s.settings.solution.run_calculation.iterate(iter_count=min(BATCH, HORIZON - active)); active += min(BATCH, HORIZON - active); text = capture.text_since(before)
            if re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I):
                manifest["last_valid_active_iteration"] = active - STEP; manifest["failure_console_tail"] = text[-16000:]; dump(local / "run-manifest.json", manifest); raise RuntimeError(f"solver failure at active {active}")
            lower_path = report_paths["absorb-lower-liquid-mass"]
            lower = float((parse_report_forms(read_remote_forms(s, lower_path)).get("values") or [float("nan")])[-1])
            require(math.isfinite(lower), f"nonfinite lower liquid mass at active {active}")
            event = {"active_iteration": active, "lower_liquid_mass_kg": lower, "ring_state": "wall"}
            if active in (1000, 2000, 3000, 4000, 5000): save_pair(s, paths[f"active{active}"]); event["checkpoint_case"] = paths[f"active{active}"]
            manifest["events"].append(event)
            if active % 100 == 0: dump(local / "run-manifest.json", manifest)
        residuals = parse_residuals(capture.text_since(marker)); require(residuals["point_count"] >= HORIZON, "short v2 residual history")
        reports = {}
        for name, path in report_paths.items():
            history = parse_report_forms(read_remote_forms(s, path)); require(history["points"] >= HORIZON, f"short v2 report {name}: {history['points']}"); history.update({"monitor_name": name, "remote_file": path}); reports[name] = history
        (local / "residuals.json").write_text(json.dumps(residuals, indent=2, default=str) + "\n", encoding="utf-8")
        (local / "reports.json").write_text(json.dumps({"reports": reports}, indent=2, default=str) + "\n", encoding="utf-8")
        values = reports["absorb-lower-liquid-mass"]["values"]
        late = [float(v) for v in values[-100:]]
        median = statistics.median(late); threshold = 0.8 * median
        receipt = {"status": "COMPLETE", "family": "corrected Server-3 C8 v2", "parent_run_manifest": str(local / "run-manifest.json"), "parent_case": paths["active5000"], "parent_data": data_path(paths["active5000"]), "metric": "absorb-lower-liquid-mass", "window_active_iterations": [4000, 5000], "late_median_kg": median, "threshold_fraction_of_median": 0.8, "threshold_kg": threshold, "cadence_active_iterations": STEP, "persistence_samples": PERSISTENCE, "persistence_active_iterations": PERSISTENCE * STEP, "open_condition": f"Each of {PERSISTENCE} consecutive sampled lower-liquid-mass values is >= threshold_kg.", "source": "C8-D0-V2 reports.json"}
        args.trigger_receipt.parent.mkdir(parents=True, exist_ok=True); args.trigger_receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        manifest.update({"achieved_active_iterations": HORIZON, "residuals": residuals, "trigger_receipt": str(args.trigger_receipt), "trigger_values": {"late_median_kg": median, "threshold_kg": threshold}, "status": "COMPLETE"})
        dump(local / "run-manifest.json", manifest); return 0
    except (Exception, KeyboardInterrupt) as exc:
        manifest.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()}); dump(local / "run-manifest.json", manifest); return 1
    finally:
        if capture: capture.close()


if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""Resume the paused R0 control in large native solver batches."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "inspection"), str(ROOT / "scripts" / "setup")]
from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import data_path, remote_file_sha256  # noqa: E402
from run_p71a_v2_inlet_loading import applied_absorber, compute_report, expression_value  # noqa: E402
from run_p7_e0_ref_discovery import parse_residuals  # noqa: E402


HORIZON = 1000
CHECKPOINTS = (250, 500, 750, 1000)
CASE_ID = "P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME"


def dump(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def event_flags(text: str) -> dict[str, bool]:
    return {
        "amg": bool(re.search(r"AMG|divergence detected in AMG", text, re.I)),
        "fpe": bool(re.search(r"floating point exception|FPE", text, re.I)),
        "nonfinite": bool(re.search(r"non.?finite|NaN|Inf", text, re.I)),
        "fatal": bool(re.search(r"fatal error|segmentation violation|node failure", text, re.I)),
        "reverse_flow": bool(re.search(r"reverse flow|reversed flow", text, re.I)),
        "turbulent_viscosity": bool(re.search(r"turbulent viscosity|viscosity limited|limiting", text, re.I)),
    }


def save_pair(solver: Any, case: str) -> dict[str, Any]:
    data = data_path(case)
    require(not remote_file_exists(solver, case) and not remote_file_exists(solver, data), f"refusing overwrite: {case}")
    solver.settings.file.write_case(file_name=case)
    solver.settings.file.write_data(file_name=data)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return {
        "case": case,
        "data": data,
        "case_sha256": remote_file_sha256(solver, case, case + f".{stamp}.case.sha256.txt"),
        "data_sha256": remote_file_sha256(solver, data, data + f".{stamp}.data.sha256.txt"),
    }


def histories(solver: Any, report_paths: dict[str, str]) -> dict[str, Any]:
    result = {}
    for name, path in report_paths.items():
        if remote_file_exists(solver, path):
            try:
                result[name] = parse_report_forms(read_remote_forms(solver, path))
            except Exception as exc:
                result[name] = {"remote_file": path, "parse_error": f"{type(exc).__name__}: {exc}"}
        else:
            result[name] = {"remote_file": path, "missing": True}
    return result


def readback(solver: Any) -> dict[str, Any]:
    methods = safe_get_state(solver.settings.solution.methods, "methods")
    return {
        "methods": methods,
        "general": safe_get_state(solver.settings.setup.general, "general"),
        "models": safe_get_state(solver.settings.setup.models, "models"),
        "controls": safe_get_state(solver.settings.solution.controls, "controls"),
        "boundaries": safe_get_state(solver.settings.setup.boundary_conditions, "boundaries"),
        "cell_zones": safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones"),
        "report_files": safe_get_state(solver.settings.solution.monitor.report_files, "report files"),
        "fluid_zones": list(solver.settings.setup.cell_zone_conditions.fluid.get_object_names()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-dir", type=Path, required=True)
    parser.add_argument("--pause-case", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--final-root", required=True)
    parser.add_argument("--parent-start-native", type=int, required=True)
    parser.add_argument("--pause-native", type=int, required=True)
    parser.add_argument("--batch", type=int, default=100)
    parser.add_argument("--case-id", default=CASE_ID, help="Artifact stem for this continuation; defaults to the original R0 setup ID.")
    args = parser.parse_args()
    require(args.batch >= 50, "batch must be a larger native batch (>=50)")
    local = args.local_dir.resolve()
    transcript_path = local / "transcript-batched-resume.txt"
    manifest_path = local / "batched-resume-manifest.json"
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": args.case_id,
        "resume_from_pause_case": args.pause_case,
        "parent_start_native_iteration": args.parent_start_native,
        "pause_native_iteration": args.pause_native,
        "already_completed_additional": args.pause_native - args.parent_start_native,
        "requested_additional_total": HORIZON,
        "remaining_iterations": HORIZON - (args.pause_native - args.parent_start_native),
        "native_batch_size": args.batch,
        "report_cadence": "native every iteration; solver calls in larger batches",
        "events": [],
    }
    dump(manifest_path, manifest)
    solver = None
    capture = None
    try:
        solver = connect(server_id="1", start_transcript=True, tcp_timeout_seconds=10)
        require(not bool(solver.settings.solution.run_calculation.iterating()), "Fluent is still iterating")
        solver.settings.file.read_case(file_name=args.pause_case)
        solver.settings.file.read_data(file_name=data_path(args.pause_case))
        rb = readback(solver)
        methods = rb["methods"]
        require(methods.get("p_v_coupling", {}).get("flow_scheme") == "Coupled", f"coupling readback: {methods}")
        require(methods.get("pseudo_time_method", {}).get("formulation", {}).get("coupled_solver") == "global-time-step", f"pseudo-time readback: {methods}")
        require(rb["general"].get("solver", {}).get("time") == "steady", "resume is not steady")
        report_state = rb["report_files"]
        report_paths = {}
        for key, state in report_state.items():
            if isinstance(state, dict) and state.get("active") and state.get("file_name") and state.get("report_defs"):
                report_paths[state["report_defs"][0]] = state["file_name"]
        require(len(report_paths) >= 10, f"child report package not restored: {len(report_paths)}")
        manifest["reopen_readback"] = rb
        manifest["report_paths"] = report_paths
        capture = SessionTranscriptCapture(solver, stream_path=transcript_path, echo=False)
        capture.start()
        marker = capture.mark()
        completed = args.pause_native - args.parent_start_native
        remaining = HORIZON - completed
        # First land exactly on +250, then use large calls thereafter.
        while remaining > 0:
            next_checkpoint = min((x for x in CHECKPOINTS if x > completed), default=HORIZON)
            to_checkpoint = next_checkpoint - completed
            block = min(remaining, to_checkpoint if to_checkpoint < args.batch else args.batch)
            before = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=block)
            completed += block
            remaining -= block
            console = capture.text_since(before)
            flags = event_flags(console)
            event = {
                "additional_offset": completed,
                "native_expected_coordinate": args.parent_start_native + completed,
                "requested_batch": block,
                "console_event_flags": flags,
                "command_kg_s": expression_value(solver, "P71V2Command"),
                "named_removal_kg_s": expression_value(solver, "P71V2Removal"),
                "command_error_kg_s": expression_value(solver, "P71V2CommandError"),
                "applied_phase2_source_kg_s_signed": applied_absorber(solver),
                "available_liquid_volume_m3": expression_value(solver, "P71V2AvailableVolume"),
                "total_liquid_mass_kg": compute_report(solver, "v2-total-liquid-mass"),
                "total_liquid_volume_m3": compute_report(solver, "v2-total-liquid-volume"),
                "lower_liquid_mass_kg": compute_report(solver, "v2-lower-liquid-mass"),
                "lower_liquid_volume_m3": compute_report(solver, "v2-lower-liquid-volume"),
                "console_tail": console[-3000:],
            }
            manifest["events"].append(event)
            if flags["amg"] or flags["fpe"] or flags["nonfinite"] or flags["fatal"]:
                manifest["status"] = "BLOCKED"
                manifest["first_event"] = event
                dump(manifest_path, manifest)
                raise RuntimeError(f"solver event in batch ending at additional offset {completed}")
            if completed in CHECKPOINTS:
                checkpoint_case = str(PureWindowsPath(args.run_root) / f"{args.case_id}-plus{completed:04d}.cas.h5")
                event["checkpoint_pair"] = save_pair(solver, checkpoint_case)
                event["readback"] = readback(solver)
                event["report_histories"] = histories(solver, report_paths)
                dump(local / f"checkpoint-plus{completed:04d}-batched-readback.json", event)
            if completed % 100 == 0 or completed in CHECKPOINTS:
                dump(manifest_path, manifest)

        transcript = capture.text_since(marker)
        residuals = parse_residuals(transcript)
        dump(local / "residuals-batched-resume.json", residuals)
        report_histories = histories(solver, report_paths)
        dump(local / "report-histories-batched.json", report_histories)
        final_case = str(PureWindowsPath(args.final_root) / f"{args.case_id}-full-loading-plus1000.cas.h5")
        final_pair = save_pair(solver, final_case)
        manifest["final_pair"] = final_pair
        manifest["residuals"] = {"points": residuals.get("point_count"), "path": str(local / "residuals-batched-resume.json")}
        manifest["report_histories_path"] = str(local / "report-histories-batched.json")
        manifest["terminal_readback_before_reopen"] = readback(solver)
        solver.settings.file.read_case(file_name=final_pair["case"])
        solver.settings.file.read_data(file_name=final_pair["data"])
        manifest["terminal_readback_after_reopen"] = readback(solver)
        manifest["status"] = "COMPLETE"
        manifest["achieved_additional_total"] = completed
        dump(manifest_path, manifest)
        print(json.dumps(manifest, indent=2, default=str, allow_nan=True))
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        dump(manifest_path, manifest)
        print(json.dumps(manifest, indent=2, default=str, allow_nan=True), file=sys.stderr)
        return 1
    finally:
        if capture is not None:
            capture.close()


if __name__ == "__main__":
    raise SystemExit(main())

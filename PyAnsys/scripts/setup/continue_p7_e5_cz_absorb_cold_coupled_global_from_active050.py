#!/usr/bin/env python3
"""Continue the server-3 Coupled absorber branch from active 50 to 10000.

The existing branch stopped after its 50-iteration smoke checkpoint because
Fluent 2025 R2 named the absorber report-file objects ``report-file-N`` rather
than ``<definition>-rfile``.  This continuation resolves report paths from
their report definitions, preserves the live active-50 state, performs the
five required source-ramp transitions to active 100, and then makes one
continuous 9,900-iteration solver call at the final absorber command.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import base_invariants, density_from_case, fluid_names, read_source_tree, zone_inventory  # noqa: E402
from run_p7_e5_cz_absorb_cold import schedule_update  # noqa: E402
from run_p7_treatment_screen import data_path, parse_residuals, save_pair  # noqa: E402


CANDIDATE = "P7-E5-CZ-ABSORB-COLD-COUPLED-GLOBAL-PSEUDO-10K"
PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
START_ACTIVE = 50
RAMP_END = 100
FINAL_ACTIVE = 10_000
FINAL_COMMAND_KG_S = 116.92
RAMP_POINTS = (60, 70, 80, 90, 100)
REQUIRED_REPORT_KEYS = {
    "e0-liquid-mass-total-rfile",
    "e0-liquid-volume-total-rfile",
    "absorb-lower-liquid-mass-rfile",
    "absorb-lower-liquid-volume-rfile",
    "absorb-adjacent-liquid-mass-rfile",
    "absorb-broad-liquid-mass-rfile",
}
REQUIRED_REPORT_KEYS.update(
    f"e0-flux-{phase}-{surface}-rfile"
    for phase in ("mixture", "phase1", "phase2")
    for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def normalize_remote_path(value: str) -> str:
    return value.replace("\\\\", "\\")


def fatal_console(text: str) -> bool:
    return bool(re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I))


def resolve_report_paths(solver: Any) -> dict[str, str]:
    """Resolve logical report keys through Fluent's actual report-file objects."""
    reports = solver.settings.solution.monitor.report_files
    definition_to_path: dict[str, str] = {}
    for object_name in (str(item) for item in reports.get_object_names()):
        state = safe_get_state(reports[object_name], object_name)
        if not isinstance(state, Mapping):
            continue
        path = state.get("file_name")
        if not isinstance(path, str) or not path.strip():
            continue
        definitions = state.get("report_defs")
        if isinstance(definitions, list):
            for definition in definitions:
                if isinstance(definition, str):
                    definition_to_path[definition] = path
        if object_name.endswith("-rfile"):
            definition_to_path.setdefault(object_name[:-6], path)
    resolved: dict[str, str] = {}
    missing: list[str] = []
    for key in sorted(REQUIRED_REPORT_KEYS):
        definition = key[:-6]
        path = definition_to_path.get(definition)
        if path is None or not remote_file_exists(solver, path):
            missing.append(key)
        else:
            resolved[key] = path
    if missing:
        raise RuntimeError(f"required report definitions could not be resolved to existing files: {missing}")
    return resolved


def latest_report(solver: Any, path: str) -> tuple[int, float, int]:
    parsed = parse_report_forms(read_remote_forms(solver, path))
    iterations = parsed.get("iterations", [])
    values = parsed.get("values", [])
    if not iterations or not values:
        raise RuntimeError(f"report has no samples: {path}")
    return int(iterations[-1]), float(values[-1]), int(parsed["points"])


def build_paths(run_root: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "active050": str(root / f"{CANDIDATE}-active050.cas.h5"),
        "active100": str(root / f"{CANDIDATE}-active100.cas.h5"),
        "final": str(root / f"{CANDIDATE}-active10000.cas.h5"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="3")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite active-50 continuation evidence")
    args.run_root = normalize_remote_path(args.run_root)
    paths = build_paths(args.run_root)
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "mode": "attached-continuation-from-active050",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP3", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP3', 'unknown')}",
        "starting_active_iteration": START_ACTIVE,
        "ramp_end_active_iteration": RAMP_END,
        "final_active_iteration": FINAL_ACTIVE,
        "continuous_final_call": {"iter_count": FINAL_ACTIVE - RAMP_END, "call_count": 1, "batching": "none"},
        "absorber_command_kg_s_at_start": 58.46,
        "absorber_command_kg_s_final": FINAL_COMMAND_KG_S,
        "run_root": args.run_root,
        "artifact_paths": paths,
        "prior_manifest": "PyAnsys/output/phase07_solver_path_recreate/P7-E5-CZ-ABSORB-COLD-COUPLED-GLOBAL-PSEUDO-10K-server3-S3-10K-20260915T015808Z-manifest.json",
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        for key in ("active100", "final"):
            if remote_file_exists(solver, paths[key]) or remote_file_exists(solver, data_path(paths[key])):
                raise FileExistsError(f"refusing to overwrite continuation artifact: {paths[key]}")
        if not remote_file_exists(solver, paths["active050"]) or not remote_file_exists(solver, data_path(paths["active050"])):
            raise FileNotFoundError(f"active-050 paired checkpoint is not visible: {paths['active050']}")

        zones = fluid_names(solver)
        if set(zones) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"active-050 live topology mismatch: {zones}")
        methods = solver.settings.solution.methods.get_state()
        if methods.get("p_v_coupling", {}).get("flow_scheme") != "Coupled":
            raise RuntimeError(f"active-050 coupling mismatch: {methods.get('p_v_coupling')}")
        if methods.get("pseudo_time_method", {}).get("formulation", {}).get("coupled_solver") != "global-time-step":
            raise RuntimeError(f"active-050 global-time-step mismatch: {methods.get('pseudo_time_method')}")
        density = density_from_case(solver)
        inventory = zone_inventory(solver, density)
        source_tree = read_source_tree(solver)
        source_value = source_tree[LOWER_ZONE]["phase-2"]["terms"]["mass"][0]["value"]
        start_command = -float(source_value) * inventory["geometric_volume_m3"]
        if abs(start_command - 58.46) > 1.0e-6:
            raise RuntimeError(f"active-050 source command mismatch: {start_command}")

        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()
        report_paths = resolve_report_paths(solver)
        report_iteration, report_value, report_points = latest_report(solver, report_paths["e0-liquid-mass-total-rfile"])
        if report_iteration != START_ACTIVE:
            raise RuntimeError(f"active-050 report readback mismatch: {report_iteration}")
        manifest["active050_readback"] = {
            "fluid_zones": zones,
            "base_invariants": base_invariants(solver),
            "solver_path": {"p_v_coupling": methods.get("p_v_coupling"), "pseudo_time_method": methods.get("pseudo_time_method")},
            "source_mass_kg_m3_s": source_value,
            "source_command_kg_s": start_command,
            "report_iteration": report_iteration,
            "report_points": report_points,
            "report_value": report_value,
            "report_paths": report_paths,
        }
        write_json(args.manifest, manifest)

        marker = capture.mark()
        active = START_ACTIVE
        for target_active in RAMP_POINTS:
            previous_active = active
            event = schedule_update(solver, target_active, density, manifest)
            solver.settings.solution.run_calculation.iterate(iter_count=target_active - active)
            active = target_active
            console = capture.text_since(marker)
            if fatal_console(console):
                manifest["last_valid_active_iteration"] = previous_active
                manifest["terminal_solver_diagnostics"] = {"active_iteration": active, "console_tail": console[-12000:]}
                write_json(args.manifest, manifest)
                raise RuntimeError(f"fatal/divergence diagnostic during ramp block ending at active {active}")
            native_iteration, _, points = latest_report(solver, report_paths["e0-liquid-mass-total-rfile"])
            event["completed_active_iteration"] = active
            event["native_iteration"] = native_iteration
            event["report_points"] = points
            event["console_tail"] = console[-3000:]
            write_json(args.manifest, manifest)

        save_pair(solver, paths["active100"])
        manifest["events"].append({"event": "active100_saved", "case": paths["active100"], "data": data_path(paths["active100"])})
        write_json(args.manifest, manifest)

        marker = capture.mark()
        solver.settings.solution.run_calculation.iterate(iter_count=FINAL_ACTIVE - RAMP_END)
        console = capture.text_since(marker)
        manifest["continuous_final_call_result"] = {
            "iter_count": FINAL_ACTIVE - RAMP_END,
            "call_count": 1,
            "fatal_or_divergence_detected": fatal_console(console),
            "console_tail": console[-12000:],
        }
        if fatal_console(console):
            write_json(args.manifest, manifest)
            raise RuntimeError("fatal/divergence diagnostic detected during the continuous final solve call")

        save_pair(solver, paths["final"])
        manifest["events"].append({"event": "active10000_saved", "case": paths["final"], "data": data_path(paths["final"])})
        residuals = parse_residuals(console)
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        final_report = latest_report(solver, report_paths["e0-liquid-mass-total-rfile"])
        manifest["final_readback"] = {
            "fluid_zones": fluid_names(solver),
            "source_tree": read_source_tree(solver),
            "solver_path": solver.settings.solution.methods.get_state(),
            "total_liquid_report": {"iteration": final_report[0], "value": final_report[1], "points": final_report[2]},
            "artifact_pairs": {
                "active100": {"case": remote_file_exists(solver, paths["active100"]), "data": remote_file_exists(solver, data_path(paths["active100"]))},
                "active10000": {"case": remote_file_exists(solver, paths["final"]), "data": remote_file_exists(solver, data_path(paths["final"]))},
            },
        }
        if final_report[0] != FINAL_ACTIVE:
            raise RuntimeError(f"final report iteration mismatch: {final_report[0]}")
        manifest["status"] = "COMPLETE"
        write_json(args.manifest, manifest)
        capture.close()
        print(json.dumps(manifest, indent=2, default=str))
        return 0
    except Exception as exc:
        if capture is not None:
            capture.close()
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        write_json(args.manifest, manifest)
        print(json.dumps(manifest, indent=2, default=str), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

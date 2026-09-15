#!/usr/bin/env python3
"""Prepare the Phase-07 C3C4 child from the exact active-1000 parent.

The script preserves the currently loaded server-1 state, loads the paired
active-1000 absorber parent, applies only the declared Coupled + steady Global
Time Step solver-path delta, and proves the prepared child by save/reopen.  It
does not run iterations; the setup remains ready for the required smoke gate.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import base_invariants, fluid_names, read_source_tree  # noqa: E402
from run_p7_e5_cz_absorb import configure_inventory_reports, redirect_all_reports  # noqa: E402
from run_p7_e5_cz_absorb_cold_coupled_10k import configure_coupled_global_pseudo  # noqa: E402
from run_p7_treatment_screen import data_path, save_pair  # noqa: E402


PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
PARENT_ARTIFACT_ACTIVE_ITERATION = 1000
EXPECTED_MASS_SOURCE = -379.23778869844955
REPORT_STEM = "S1-C3-10K"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def normalize_remote_path(value: str) -> str:
    return value.replace("\\\\", "\\")


def source_mass_value(source_tree: dict[str, Any]) -> float | None:
    lower = source_tree.get(LOWER_ZONE, {})
    phase2 = lower.get("phase-2", {}) if isinstance(lower, dict) else {}
    terms = phase2.get("terms", {}) if isinstance(phase2, dict) else {}
    entries = terms.get("mass", []) if isinstance(terms, dict) else []
    if isinstance(entries, dict):
        entries = [entries]
    for entry in entries:
        if isinstance(entry, dict) and entry.get("option") == "value":
            try:
                return float(entry["value"])
            except (KeyError, TypeError, ValueError):
                return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--recovery-case", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()

    if args.manifest.exists():
        raise FileExistsError("refusing to overwrite C3C4 preparation evidence")
    args.parent_case = normalize_remote_path(args.parent_case)
    args.parent_data = normalize_remote_path(args.parent_data)
    args.run_root = normalize_remote_path(args.run_root)
    args.recovery_case = normalize_remote_path(args.recovery_case)

    root = PureWindowsPath(args.run_root)
    prepared_case = str(root / "S1-C3C4-COUPLED-GLOBAL-PSEUDO-TIME-prepared.cas.h5")
    recovery_data = data_path(args.recovery_case)
    paths = {
        "prepared_case": prepared_case,
        "prepared_data": data_path(prepared_case),
        "recovery_case": args.recovery_case,
        "recovery_data": recovery_data,
        "monitor_root": str(root / "monitors"),
    }
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": "C3C4-COUPLED-GLOBAL-PSEUDO-TIME",
        "mode": "prepare-from-exact-active1000-parent",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP1", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP1', 'unknown')}",
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "run_root": args.run_root,
        "artifact_paths": paths,
        "controlled_delta": "SIMPLE -> Coupled; pseudo-time off -> Coupled-compatible steady Global Time Step",
        "iterations_run": 0,
        "next_gate": "50-iteration smoke, then attached 500-iteration discovery per setup.md",
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        for path in (prepared_case, data_path(prepared_case), args.recovery_case, recovery_data):
            if remote_file_exists(solver, path):
                raise FileExistsError(f"refusing to overwrite existing artifact: {path}")
        if not remote_file_exists(solver, args.parent_case) or not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"active-1000 parent pair is not visible: {args.parent_case}; {args.parent_data}")

        capture_path = args.manifest.with_name(args.manifest.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        # Preserve the currently loaded state before replacing it with the
        # exact active-1000 parent required by the project setup.
        save_pair(solver, args.recovery_case)
        manifest["current_state_recovery"] = {
            "case": args.recovery_case,
            "data": recovery_data,
        }

        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        parent_zones = fluid_names(solver)
        parent_sources = read_source_tree(solver)
        parent_mass_source = source_mass_value(parent_sources)
        parent_methods = solver.settings.solution.methods.get_state()
        if set(parent_zones) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"active-1000 parent topology mismatch: {parent_zones}")
        if parent_mass_source is None or abs(parent_mass_source - EXPECTED_MASS_SOURCE) > 1.0e-8:
            raise RuntimeError(f"active-1000 parent absorber source mismatch: {parent_mass_source}")
        if parent_methods.get("p_v_coupling", {}).get("flow_scheme") != "SIMPLE":
            raise RuntimeError(f"active-1000 parent coupling mismatch: {parent_methods.get('p_v_coupling')}")
        if parent_methods.get("pseudo_time_method", {}).get("formulation", {}).get("segregated_solver") != "off":
            raise RuntimeError(f"active-1000 parent pseudo-time mismatch: {parent_methods.get('pseudo_time_method')}")
        manifest["parent_readback"] = {
            "fluid_zones": parent_zones,
            "parent_artifact_active_iteration": PARENT_ARTIFACT_ACTIVE_ITERATION,
            "base_invariants": base_invariants(solver),
            "source_tree": parent_sources,
            "source_mass_kg_m3_s": parent_mass_source,
            "solver_path": {
                "p_v_coupling": parent_methods.get("p_v_coupling"),
                "pseudo_time_method": parent_methods.get("pseudo_time_method"),
            },
        }

        manifest["solver_path_readback_before_save"] = configure_coupled_global_pseudo(solver)
        manifest["monitor_definitions"] = configure_inventory_reports(solver)
        manifest["report_files"] = redirect_all_reports(solver, paths["monitor_root"], REPORT_STEM)
        manifest["residual_configuration"] = configure_residual_history(solver, 800)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=100)
        write_json(args.manifest, manifest)

        save_pair(solver, prepared_case)
        solver.settings.file.read_case(file_name=prepared_case)
        solver.settings.file.read_data(file_name=data_path(prepared_case))
        reopened_methods = solver.settings.solution.methods.get_state()
        reopened_sources = read_source_tree(solver)
        reopened_path = configure_coupled_global_pseudo(solver)
        reopened_zones = fluid_names(solver)
        if set(reopened_zones) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"prepared child topology mismatch after reopen: {reopened_zones}")
        if source_mass_value(reopened_sources) is None or abs(source_mass_value(reopened_sources) - EXPECTED_MASS_SOURCE) > 1.0e-8:
            raise RuntimeError(f"prepared child absorber source changed after reopen: {source_mass_value(reopened_sources)}")
        manifest["prepared_reopen_readback"] = {
            "fluid_zones": reopened_zones,
            "parent_artifact_active_iteration": PARENT_ARTIFACT_ACTIVE_ITERATION,
            "base_invariants": base_invariants(solver),
            "source_tree": reopened_sources,
            "solver_path": reopened_path,
            "coupling": reopened_methods.get("p_v_coupling"),
            "pseudo_time": reopened_methods.get("pseudo_time_method"),
        }
        manifest["prepared_pair_verified"] = {
            "case": prepared_case,
            "data": data_path(prepared_case),
            "case_exists": remote_file_exists(solver, prepared_case),
            "data_exists": remote_file_exists(solver, data_path(prepared_case)),
        }
        manifest["transcript"] = str(capture_path)
        manifest["status"] = "PREPARED"
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

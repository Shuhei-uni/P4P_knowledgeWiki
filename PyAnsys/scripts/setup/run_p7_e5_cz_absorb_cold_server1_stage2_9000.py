#!/usr/bin/env python3
"""Run the server-1 absorber control from active 1000 to active 10000.

The stage-2 solve is deliberately one Fluent iterate call with
``iter_count=9000``.  The absorber command is already at its final value, so
there is no schedule update that would justify smaller batches.
"""

from __future__ import annotations

import argparse
import json
import os
import re
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
from pyansys_fluent.stage4_native import ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import base_invariants, fluid_names, read_source_tree  # noqa: E402
from run_p7_treatment_screen import data_path, parse_residuals, save_pair  # noqa: E402


PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
FINAL_COMMAND_KG_S = 116.92
EXPECTED_MASS_SOURCE = -379.23778869844955
START_ACTIVE = 1000
ADDITIONAL_ITERATIONS = 9000
FINAL_ACTIVE = 10000


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


def fatal_console(text: str) -> bool:
    return bool(re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite server-1 stage-2 evidence")
    args.run_root = normalize_remote_path(args.run_root)
    root = PureWindowsPath(args.run_root)
    paths = {
        "active1000": str(root / "S1-SIMPLE-10K-active1000.cas.h5"),
        "active10000": str(root / "S1-SIMPLE-10K-active10000.cas.h5"),
    }
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": "P7-E5-CZ-ABSORB-COLD-SIMPLE-STAGE2-10K",
        "mode": "attached-single-call-stage2",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP1", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP1', 'unknown')}",
        "starting_active_iteration": START_ACTIVE,
        "additional_iterations": ADDITIONAL_ITERATIONS,
        "expected_final_active_iteration": FINAL_ACTIVE,
        "iterate_call": {"iter_count": ADDITIONAL_ITERATIONS, "call_count": 1, "batching": "none"},
        "solver_path": "original SIMPLE control; steady pseudo-time off",
        "absorber_command_kg_s": FINAL_COMMAND_KG_S,
        "artifact_paths": paths,
        "source_manifest": "PyAnsys/output/phase07_solver_path_recreate/P7-E5-CZ-ABSORB-COLD-RECREATED-LIVE-RESUME2-server1-20260915T000111Z-active-run3-manifest.json",
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        for case_path in paths.values():
            if remote_file_exists(solver, case_path) or remote_file_exists(solver, data_path(case_path)):
                raise FileExistsError(f"refusing to overwrite stage-2 artifact: {case_path}")

        zones = fluid_names(solver)
        if set(zones) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"server-1 topology mismatch at stage-2 start: {zones}")
        methods = solver.settings.solution.methods.get_state()
        coupling = methods.get("p_v_coupling", {}) if isinstance(methods, dict) else {}
        pseudo = methods.get("pseudo_time_method", {}) if isinstance(methods, dict) else {}
        if coupling.get("flow_scheme") != "SIMPLE" or pseudo.get("formulation", {}).get("segregated_solver") != "off":
            raise RuntimeError(f"server-1 solver-path mismatch at stage-2 start: coupling={coupling}; pseudo={pseudo}")
        source_tree = read_source_tree(solver)
        mass_source = source_mass_value(source_tree)
        if mass_source is None or abs(mass_source - EXPECTED_MASS_SOURCE) > 1.0e-8:
            raise RuntimeError(f"server-1 absorber command mismatch at stage-2 start: {mass_source}")
        manifest["stage2_start_readback"] = {
            "fluid_zones": zones,
            "base_invariants": base_invariants(solver),
            "solver_path": {"p_v_coupling": coupling, "pseudo_time_method": pseudo},
            "source_mass_kg_m3_s": mass_source,
            "source_tree": source_tree,
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "stage-2 start runtime state"),
        }

        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()
        save_pair(solver, paths["active1000"])
        manifest["active1000_saved"] = True
        write_json(args.manifest, manifest)

        marker = capture.mark()
        # This is intentionally a single solver call: the final absorber
        # command is fixed, so no per-10-iteration controller work is needed.
        solver.settings.solution.run_calculation.iterate(iter_count=ADDITIONAL_ITERATIONS)
        console = capture.text_since(marker)
        manifest["post_solve_diagnostics"] = {
            "fatal_or_divergence_detected": fatal_console(console),
            "console_tail": console[-12000:],
        }
        if fatal_console(console):
            raise RuntimeError("fatal/divergence diagnostic detected during the single 9000-iteration solve call")

        save_pair(solver, paths["active10000"])
        residuals = parse_residuals(console)
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["active10000_saved"] = True
        manifest["final_live_readback"] = {
            "fluid_zones": fluid_names(solver),
            "source_tree": read_source_tree(solver),
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "stage-2 final runtime state"),
        }
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

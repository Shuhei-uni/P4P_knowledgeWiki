#!/usr/bin/env python3
"""Resume the Phase-07 cold-start absorber from a verified split checkpoint.

The initial reconstruction runner intentionally saves a paired checkpoint after
the native lower-zone split.  This continuation runner is used when that save
completed but the client disconnected before report setup or iteration began.
It does not repeat the mesh operation, change the original solver settings, or
load an evolved case.  It prepares a fresh child directory, proves the split
state, and runs the original 1000-active-iteration absorber discovery path.
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import base_invariants, density_from_case, fluid_names, read_source_tree  # noqa: E402
from run_p7_e5_cz_absorb import configure_inventory_reports, redirect_all_reports  # noqa: E402
from run_p7_e5_cz_absorb_cold import (  # noqa: E402
    CANDIDATE,
    FAMILY,
    HORIZON,
    REQUIRED_REPORT_NAMES,
    build_paths,
    data_path,
    run_discovery,
)
from run_p7_treatment_screen import parse_residuals, save_pair  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--split-case", required=True)
    parser.add_argument("--split-data", required=True)
    parser.add_argument("--use-live-state", action="store_true")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local continuation evidence")

    paths = build_paths(args.run_root)
    remote_artifacts = [path for key, path in paths.items() if key != "monitor_root"]
    remote_artifacts += [data_path(path) for path in remote_artifacts]
    manifest: dict[str, object] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "run_id": args.manifest.stem,
        "family": FAMILY,
        "mode": "attached-discovery-resume",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP1", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP1', 'unknown')}",
        "reference_setup_id": "P7-E0-REF",
        "continuation_source_case": args.split_case,
        "continuation_source_data": args.split_data,
        "run_root": args.run_root,
        "final_absorber_rate_kg_s": 116.92,
        "ramp_iterations": 100,
        "update_interval_active_iterations": 10,
        "requested_active_iterations": HORIZON,
        "artifact_paths": paths,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        existing = [path for path in remote_artifacts if remote_file_exists(solver, path)]
        if existing:
            raise FileExistsError(f"refusing to overwrite remote continuation artifacts: {existing}")
        if not args.use_live_state and (not remote_file_exists(solver, args.split_case) or not remote_file_exists(solver, args.split_data)):
            raise FileNotFoundError(f"verified split checkpoint is not visible: {args.split_case}; {args.split_data}")

        remote_chdir(solver, str(PureWindowsPath(args.split_case).parent))
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        if not args.use_live_state:
            solver.settings.file.read_case(file_name=args.split_case)
            solver.settings.file.read_data(file_name=args.split_data)
        names = fluid_names(solver)
        if set(names) != {"separator-purnanto", "p7-e5-lower-y010"}:
            raise RuntimeError(f"split checkpoint topology mismatch: {names}")
        source_tree = read_source_tree(solver)
        if any(source_tree[zone][phase].get("enable") is not False for zone in source_tree for phase in ("phase-1", "phase-2", "mixture")):
            raise RuntimeError(f"split checkpoint is not source-off: {source_tree}")
        density = density_from_case(solver)
        manifest["split_checkpoint_readback"] = {
            "fluid_zones": names,
            "base_invariants": base_invariants(solver),
            "source_tree": source_tree,
            "liquid_density_kg_m3": density,
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "split checkpoint runtime state"),
            "claim": "E0-style initialized field after verified lower-zone split, before absorber iterations",
        }
        manifest["events"].append({"event": "split_checkpoint_reopened", "case": args.split_case})  # type: ignore[union-attr]

        manifest["monitor_definitions"] = configure_inventory_reports(solver)
        manifest["report_files"] = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE)
        manifest["residual_configuration"] = configure_residual_history(solver, 1200)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=100)
        manifest["source_contract"] = {
            "parent_zone": "separator-purnanto",
            "lower_zone": "p7-e5-lower-y010",
            "phase2_mass_only": True,
            "direct_phase1_mass_source": "off",
            "mixture_momentum_components": ["x", "y", "z"],
            "patch_reset_route": "excluded",
            "outlet_change": "excluded",
        }
        write_json(args.manifest, manifest)

        solver.settings.file.write_case(file_name=paths["prepared"])
        solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]) or not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("prepared continuation pair was not saved")
        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        if set(fluid_names(solver)) != {"separator-purnanto", "p7-e5-lower-y010"}:
            raise RuntimeError(f"prepared save/reopen topology mismatch: {fluid_names(solver)}")
        manifest["prepared_reopen"] = {
            "fluid_zones": fluid_names(solver),
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
        }
        report_paths = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE)
        manifest["report_files_after_reopen"] = report_paths
        write_json(args.manifest, manifest)

        run_discovery(solver, paths, report_paths, capture, manifest, args.manifest, density)
        residuals = manifest.pop("residuals")
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["final_case"] = paths["final"]
        manifest["final_data"] = data_path(paths["final"])
        solver.settings.file.read_case(file_name=paths["final"])
        solver.settings.file.read_data(file_name=data_path(paths["final"]))
        manifest["final_readback"] = {
            "fluid_zones": fluid_names(solver),
            "source_tree": read_source_tree(solver),
            "base_invariants": base_invariants(solver),
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "final runtime state"),
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

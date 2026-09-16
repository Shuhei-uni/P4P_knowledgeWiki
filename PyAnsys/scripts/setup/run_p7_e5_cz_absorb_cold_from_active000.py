#!/usr/bin/env python3
"""Run the original cold-start absorber path from a saved active-000 state.

This continuation is used after the prepared and active-000 case/data pair
have already been proven.  It verifies the live Fluent state, reuses the
active-000 pair without rewriting it, then runs the original 1000-iteration
absorber ramp/hold and saves the declared checkpoints.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path, PureWindowsPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from run_p7_e5_cz import base_invariants, density_from_case, fluid_names, read_source_tree  # noqa: E402
from run_p7_e5_cz_absorb import redirect_all_reports  # noqa: E402
from run_p7_e5_cz_absorb_cold import (  # noqa: E402
    CANDIDATE,
    FAMILY,
    HORIZON,
    build_paths,
    data_path,
    run_discovery,
)
from run_p7_treatment_screen import latest_report_value  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def _term_value(source_state: object, term_name: str) -> float | None:
    if not isinstance(source_state, dict):
        return None
    terms = source_state.get("terms")
    if not isinstance(terms, dict):
        return None
    values = terms.get(term_name)
    if not isinstance(values, list) or not values:
        return None
    item = values[0]
    if not isinstance(item, dict) or item.get("option") != "value":
        return None
    try:
        return float(item.get("value"))
    except (TypeError, ValueError):
        return None


def _verify_zero_source_state(source_tree: dict[str, object]) -> None:
    parent = source_tree["separator-purnanto"]
    lower = source_tree["p7-e5-lower-y010"]
    if not isinstance(parent, dict) or not isinstance(lower, dict):
        raise RuntimeError(f"unexpected source tree shape: {source_tree}")
    if any(isinstance(parent.get(phase), dict) and parent[phase].get("enable") is not False for phase in ("phase-1", "phase-2", "mixture")):
        raise RuntimeError(f"parent source state is not off: {source_tree}")
    if not isinstance(lower.get("phase-1"), dict) or lower["phase-1"].get("enable") is not False:
        raise RuntimeError(f"lower phase-1 source state is not off: {source_tree}")
    lower_phase2 = lower.get("phase-2")
    lower_mixture = lower.get("mixture")
    if not isinstance(lower_phase2, dict) or not isinstance(lower_mixture, dict):
        raise RuntimeError(f"lower source state is incomplete: {source_tree}")
    mass = _term_value(lower_phase2, "mass")
    momenta = [_term_value(lower_mixture, component) for component in ("x-momentum", "y-momentum", "z-momentum")]
    if mass is None or abs(mass) > 1e-15 or any(value is None or abs(value) > 1e-15 for value in momenta):
        raise RuntimeError(f"active-000 source values are not zero: {source_tree}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    parser.add_argument("--start-active", type=int, default=0)
    args = parser.parse_args()

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite active-000 continuation evidence")
    paths = build_paths(args.run_root)
    start_key = "child_start" if args.start_active == 0 else "smoke"
    required_start = [paths["prepared"], data_path(paths["prepared"]), paths[start_key], data_path(paths[start_key])]
    later_keys = ("smoke", "checkpoint100", "checkpoint250", "checkpoint500", "checkpoint750", "final")
    if args.start_active > 0:
        later_keys = ("checkpoint100", "checkpoint250", "checkpoint500", "checkpoint750", "final")
    later_artifacts = [paths[key] for key in later_keys]
    later_artifacts += [data_path(path) for path in later_artifacts]
    manifest: dict[str, object] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "run_id": args.manifest.stem,
        "family": FAMILY,
        "mode": "attached-discovery-from-active000",
        "server_id": args.server_id,
        "server_ip": os.getenv("FLUENT_IP1", "unknown"),
        "server_ref": f"server-{args.server_id}@{os.getenv('FLUENT_IP1', 'unknown')}",
        "reference_setup_id": "P7-E0-REF",
        "run_root": args.run_root,
        "start_active_iteration": args.start_active,
        "requested_active_iterations": HORIZON,
        "artifact_paths": paths,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        for path in required_start:
            if not remote_file_exists(solver, path):
                raise FileNotFoundError(f"required active-000 artifact is missing: {path}")
        existing_later = [path for path in later_artifacts if remote_file_exists(solver, path)]
        if existing_later:
            raise FileExistsError(f"refusing to overwrite later run artifacts: {existing_later}")

        names = fluid_names(solver)
        if args.start_active not in (0, 50):
            raise RuntimeError(f"unsupported continuation start: {args.start_active}")
        if set(names) != {"separator-purnanto", "p7-e5-lower-y010"}:
            raise RuntimeError(f"live active-000 topology mismatch: {names}")
        source_tree = read_source_tree(solver)
        if args.start_active == 0:
            _verify_zero_source_state(source_tree)
        else:
            parent = source_tree["separator-purnanto"]
            lower = source_tree["p7-e5-lower-y010"]
            if any(parent[phase].get("enable") is not False for phase in ("phase-1", "phase-2", "mixture")) or lower["phase-1"].get("enable") is not False or lower["phase-2"].get("enable") is not True or lower["mixture"].get("enable") is not True:
                raise RuntimeError(f"live active-50 source state is inconsistent: {source_tree}")
        run_state = safe_get_state(solver.settings.solution.run_calculation, "active runtime state")
        if args.start_active == 0:
            if not isinstance(run_state, dict) or int(run_state.get("iter_count", -1)) != 0:
                raise RuntimeError(f"live active-000 iteration-control readback mismatch: {run_state}")
        else:
            report_state = solver.settings.solution.monitor.report_files["e0-liquid-mass-total-rfile"].get_state()
            report_path = report_state.get("file_name") if isinstance(report_state, dict) else None
            if not isinstance(report_path, str) or not remote_file_exists(solver, report_path):
                raise RuntimeError(f"active-{args.start_active:03d} mass report is not readable: {report_state}")
            native_iteration, _ = latest_report_value(solver, report_path)
            if native_iteration != args.start_active:
                raise RuntimeError(f"live active-{args.start_active:03d} report readback mismatch: {native_iteration}")
        methods = safe_get_state(solver.settings.solution.methods, "active-000 methods")
        if not isinstance(methods, dict) or methods.get("p_v_coupling", {}).get("flow_scheme") != "SIMPLE" or methods.get("pseudo_time_method", {}).get("formulation", {}).get("segregated_solver") != "off":
            raise RuntimeError(f"live active-000 solver method mismatch: {methods}")
        density = density_from_case(solver)
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()
        manifest["active000_readback"] = {
            "fluid_zones": names,
            "base_invariants": base_invariants(solver),
            "source_tree": source_tree,
            "runtime_state": run_state,
            "methods": methods,
            "liquid_density_kg_m3": density,
            "case": paths[start_key],
            "data": data_path(paths[start_key]),
        }
        report_paths = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE + ("-CONT50" if args.start_active else ""))
        manifest["report_files"] = report_paths
        manifest["events"].append({"event": "active000_verified_and_reused", "active_iteration": 0})  # type: ignore[union-attr]
        write_json(args.manifest, manifest)

        run_discovery(solver, paths, report_paths, capture, manifest, args.manifest, density, save_initial=False, start_active=args.start_active)
        residuals = manifest.pop("residuals")
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["final_case"] = paths["final"]
        manifest["final_data"] = data_path(paths["final"])
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

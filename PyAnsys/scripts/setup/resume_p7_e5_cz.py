#!/usr/bin/env python3
"""Continue an E5-CZ discovery child from a paired active-250 checkpoint.

This is an execution-recovery path, not a new scientific setup.  It is used
when Fluent loses its session after the lower-zone child has already been
proven and a paired active-250 case/data checkpoint is available.  The
checkpoint already contains the split topology and the source command for the
next 50-iteration block; the continuation therefore does not rebuild the
mesh or reset the source.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import traceback
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_file_exists, remote_chdir  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    ensure_remote_directory,
)
from run_p7_e5_cz import (  # noqa: E402
    DELTA_M_REF_DEFAULT,
    GAINS,
    LIQUID_INLET_KG_S,
    LOWER_ZONE,
    MAX_COMMAND_KG_S,
    M_STAR_DEFAULT,
    PARENT_ZONE,
    base_invariants,
    build_paths,
    configure_sources,
    data_path,
    density_from_case,
    fluid_names,
    lower_volume_and_velocity,
    read_source_tree,
    try_integrated_source_reports,
    zone_inventory,
)
from run_p7_treatment_screen import (  # noqa: E402
    latest_report_value,
    parse_residuals,
    redirect_reports,
    save_pair,
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def continuation_paths(run_root: str, candidate: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    paths = build_paths(run_root, candidate)
    paths["resume_start"] = str(root / f"{candidate}-resume-start-active250.cas.h5")
    paths["active300"] = str(root / f"{candidate}-resume-active300.cas.h5")
    paths["active350"] = str(root / f"{candidate}-resume-active350.cas.h5")
    paths["active400"] = str(root / f"{candidate}-resume-active400.cas.h5")
    paths["active450"] = str(root / f"{candidate}-resume-active450.cas.h5")
    return paths


def save_checkpoint(solver: Any, path: str) -> None:
    save_pair(solver, path)


def run_continuation(
    solver: Any,
    *,
    paths: dict[str, str],
    report_paths: dict[str, str],
    capture: SessionTranscriptCapture,
    manifest: dict[str, Any],
    manifest_path: Path,
    candidate: str,
    start_active: int,
    end_active: int,
    gain: float,
    m_star: float,
    delta_m_ref: float,
    density_kg_m3: float,
) -> dict[str, Any]:
    mass_report = report_paths["e0-liquid-mass-total-rfile"]
    marker = capture.mark()
    active = start_active
    commands: list[dict[str, Any]] = []
    while active < end_active:
        block = min(50, end_active - active)
        solver.settings.solution.run_calculation.iterate(iter_count=block)
        active += block
        recent_console = capture.text_since(marker)
        if re.search(r"floating point exception|Divergence detected in AMG solver", recent_console, re.I):
            manifest["terminal_solver_diagnostics"] = {
                "active_iteration": active,
                "native_iteration_hint": 500 + active,
                "last_console_tail": recent_console[-12000:],
            }
            manifest["last_valid_active_iteration"] = active - block
            write_json(manifest_path, manifest)
            raise RuntimeError(f"Fluent solver divergence/floating-point exception during resume block ending at {active}")

        native_iteration, current_mass = latest_report_value(solver, mass_report)
        normalized_error = max(0.0, (current_mass - m_star) / delta_m_ref)
        requested = min(MAX_COMMAND_KG_S, max(0.0, gain * LIQUID_INLET_KG_S * normalized_error))
        inventory = zone_inventory(solver, density_kg_m3)
        basis = inventory["velocity_basis_m_s"]
        source = configure_sources(solver, -requested / inventory["geometric_volume_m3"], basis)
        integrated = try_integrated_source_reports(solver)
        command = {
            "event": "controller_update",
            "active_iteration": active,
            "native_iteration": native_iteration,
            "Mcurrent_kg": current_mass,
            "Mstar_kg": m_star,
            "DeltaMref_kg": delta_m_ref,
            "normalized_error": normalized_error,
            "gain": gain,
            "requested_command_kg_s": requested,
            "clamped_command_kg_s": requested,
            "saturated": requested >= MAX_COMMAND_KG_S,
            "lower_inventory": inventory,
            "source": source,
            "integrated_source_reports": integrated,
            "analytical_integrated_phase2_source_kg_s": -requested,
        }
        commands.append(command)
        manifest["events"].append(command)
        write_json(manifest_path, manifest)
        if active in (300, 350, 400, 450):
            save_checkpoint(solver, paths[f"active{active}"])
        elif active == end_active:
            save_checkpoint(solver, paths["final"])

    residuals = parse_residuals(capture.text_since(marker))
    expected_points = end_active - start_active
    if residuals["point_count"] < expected_points:
        raise RuntimeError(
            f"E5-CZ resume residual history too short: {residuals['point_count']} < {expected_points}"
        )
    if not all(remote_file_exists(solver, path) for path in report_paths.values()):
        raise RuntimeError("one or more E5-CZ resume report files did not appear")
    manifest["controller_updates"] = commands
    manifest["residuals"] = residuals
    return residuals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--candidate", required=True, choices=("P7-E5-CZ-G050",))
    parser.add_argument("--resume-case", required=True)
    parser.add_argument("--resume-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--residual-history", type=Path, required=True)
    parser.add_argument("--anchor-manifest", type=Path)
    parser.add_argument("--start-active", type=int, default=250)
    parser.add_argument("--end-active", type=int, default=500)
    parser.add_argument("--m-star", type=float, default=M_STAR_DEFAULT)
    parser.add_argument("--delta-m-ref", type=float, default=DELTA_M_REF_DEFAULT)
    args = parser.parse_args()
    if not 0 <= args.start_active < args.end_active <= 500 or args.start_active % 50 or args.end_active % 50:
        raise ValueError("resume range must be 50-aligned and satisfy 0 <= start < end <= 500")
    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local E5-CZ continuation evidence")

    gain = GAINS[args.candidate]
    paths = continuation_paths(args.run_root, args.candidate)
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": args.candidate,
        "run_id": args.manifest.stem,
        "family": "E5-CZ",
        "mode": "attached-discovery-recovery-continuation",
        "server_id": args.server_id,
        "resume_case": args.resume_case,
        "resume_data": args.resume_data,
        "run_root": args.run_root,
        "gain": gain,
        "requested_active_iterations": args.end_active,
        "resume_start_active_iteration": args.start_active,
        "requested_final_active_iteration": args.end_active,
        "controller_update_interval": 50,
        "m_star_kg": args.m_star,
        "delta_m_ref_kg": args.delta_m_ref,
        "anchor_manifest": str(args.anchor_manifest) if args.anchor_manifest else None,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        artifact_paths = [paths["resume_start"], paths["active300"], paths["active350"], paths["active400"], paths["active450"], paths["final"]]
        artifact_paths += [data_path(path) for path in artifact_paths]
        existing = [path for path in artifact_paths if remote_file_exists(solver, path)]
        if existing:
            raise FileExistsError(f"refusing to overwrite remote E5-CZ continuation artifacts: {existing}")
        if not remote_file_exists(solver, args.resume_case) or not remote_file_exists(solver, args.resume_data):
            raise FileNotFoundError(f"resume pair is not visible: {args.resume_case}, {args.resume_data}")
        remote_chdir(solver, str(PureWindowsPath(args.resume_case).parent))
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        solver.settings.file.read_case(file_name=args.resume_case)
        solver.settings.file.read_data(file_name=args.resume_data)
        zones = fluid_names(solver)
        if zones != [LOWER_ZONE, PARENT_ZONE]:
            raise RuntimeError(f"resume checkpoint zone mismatch: {zones}")
        manifest["resume_readback"] = {
            "fluid_zones": zones,
            "parent_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
        }
        density = density_from_case(solver)
        manifest["liquid_density_kg_m3"] = density
        manifest["resume_inventory"] = zone_inventory(solver, density)
        write_json(args.manifest, manifest)

        report_paths = redirect_reports(solver, paths["monitor_root"], f"{args.candidate}-resume")
        manifest["report_files"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(solver, args.end_active - args.start_active + 50)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=50)
        save_pair(solver, paths["resume_start"])
        manifest["events"].append({"event": "resume_start_saved", "active_iteration": args.start_active, "case": paths["resume_start"]})
        write_json(args.manifest, manifest)

        run_continuation(
            solver,
            paths=paths,
            report_paths=report_paths,
            capture=capture,
            manifest=manifest,
            manifest_path=args.manifest,
            candidate=args.candidate,
            start_active=args.start_active,
            end_active=args.end_active,
            gain=gain,
            m_star=float(args.m_star),
            delta_m_ref=float(args.delta_m_ref),
            density_kg_m3=float(density),
        )
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
            "parent_invariants": base_invariants(solver),
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

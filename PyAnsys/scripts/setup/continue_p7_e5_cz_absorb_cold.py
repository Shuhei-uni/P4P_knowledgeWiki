#!/usr/bin/env python3
"""Continue the verified cold-start E5 absorber case to total active 5000.

This is an attached discovery-extension runner.  It loads the durable
active-1000 case/data pair, keeps the existing split topology and fixed
116.92 kg/s lower-zone phase-2 absorber, and performs only 4,000 additional
iterations.  It does not add an outlet, reset fields, remesh, resplit, or
change the absorber schedule.
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

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    ensure_remote_directory,
)
from run_p7_e5_cz_absorb import (  # noqa: E402
    LIQUID_INLET_KG_S,
    LOWER_ZONE,
    PARENT_ZONE,
    redirect_all_reports,
    source_audit,
    source_invariant_summary,
)
from run_p7_e5_cz import (  # noqa: E402
    base_invariants,
    configure_sources,
    data_path,
    density_from_case,
    fluid_names,
    read_source_tree,
    try_integrated_source_reports,
    zone_inventory,
)
from run_p7_treatment_screen import latest_report_value, parse_residuals, save_pair  # noqa: E402


CANDIDATE = "P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000"
FAMILY = "E5-CZ-ABSORB-COLD-CONT5000"
PARENT_ACTIVE = 1000
TARGET_ACTIVE = 5000
ADDITIONAL_ITERATIONS = TARGET_ACTIVE - PARENT_ACTIVE
UPDATE_INTERVAL = 10
CHECKPOINT_TOTALS = (1050, 1100, 1250, 1500, 2000, 3000, 4000, 5000)
REQUIRED_REPORT_NAMES = {
    "e0-liquid-mass-total-rfile",
    "e0-liquid-volume-total-rfile",
    "absorb-lower-liquid-mass-rfile",
    "absorb-lower-liquid-volume-rfile",
    "absorb-adjacent-liquid-mass-rfile",
    "absorb-broad-liquid-mass-rfile",
}
REQUIRED_REPORT_NAMES.update(
    f"e0-flux-{phase}-{surface}-rfile"
    for phase in ("mixture", "phase1", "phase2")
    for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def continuation_paths(run_root: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "prepared": str(root / f"{CANDIDATE}-prepared.cas.h5"),
        "child_start": str(root / f"{CANDIDATE}-active1000.cas.h5"),
        "smoke": str(root / f"{CANDIDATE}-active1050.cas.h5"),
        "checkpoint1100": str(root / f"{CANDIDATE}-active1100.cas.h5"),
        "checkpoint1250": str(root / f"{CANDIDATE}-active1250.cas.h5"),
        "checkpoint1500": str(root / f"{CANDIDATE}-active1500.cas.h5"),
        "checkpoint2000": str(root / f"{CANDIDATE}-active2000.cas.h5"),
        "checkpoint3000": str(root / f"{CANDIDATE}-active3000.cas.h5"),
        "checkpoint4000": str(root / f"{CANDIDATE}-active4000.cas.h5"),
        "final": str(root / f"{CANDIDATE}-active5000.cas.h5"),
        "monitor_root": str(root / "monitors"),
    }


def fatal_console(text: str) -> bool:
    return bool(re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I))


def fixed_source_update(
    solver: Any,
    total_active: int,
    density_kg_m3: float,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    inventory = zone_inventory(solver, density_kg_m3)
    source = configure_sources(
        solver,
        -LIQUID_INLET_KG_S / inventory["geometric_volume_m3"],
        inventory["velocity_basis_m_s"],
    )
    integrated = try_integrated_source_reports(solver)
    audit = source_audit(integrated, LIQUID_INLET_KG_S)
    invariants = source_invariant_summary(solver)
    event = {
        "event": "continuation_source_update",
        "total_active_iteration": total_active,
        "additional_active_iteration": total_active - PARENT_ACTIVE,
        "native_iteration": None,
        "command_kg_s": LIQUID_INLET_KG_S,
        "lower_inventory": inventory,
        "source": source,
        "source_audit": audit,
        "source_invariants": invariants,
        "direct_phase1_source_off": invariants["phase1_direct_mass_source_off"],
    }
    manifest["events"].append(event)
    return event


def run_continuation(
    solver: Any,
    paths: Mapping[str, str],
    report_paths: Mapping[str, str],
    capture: SessionTranscriptCapture,
    manifest: dict[str, Any],
    manifest_path: Path,
    density_kg_m3: float,
) -> dict[str, Any]:
    mass_report = report_paths["e0-liquid-mass-total-rfile"]
    initial = fixed_source_update(solver, PARENT_ACTIVE, density_kg_m3, manifest)
    manifest["initial_source_update"] = initial
    save_pair(solver, paths["child_start"])
    manifest["events"].append({"event": "continuation_start_saved", "total_active_iteration": PARENT_ACTIVE, "case": paths["child_start"]})
    write_json(manifest_path, manifest)

    marker = capture.mark()
    additional = 0
    while additional < ADDITIONAL_ITERATIONS:
        block = min(UPDATE_INTERVAL, ADDITIONAL_ITERATIONS - additional)
        solver.settings.solution.run_calculation.iterate(iter_count=block)
        additional += block
        total_active = PARENT_ACTIVE + additional
        console = capture.text_since(marker)
        if fatal_console(console):
            manifest["last_valid_total_active_iteration"] = total_active - block
            manifest["terminal_solver_diagnostics"] = {
                "total_active_iteration": total_active,
                "additional_active_iteration": additional,
                "console_tail": console[-16000:],
            }
            write_json(manifest_path, manifest)
            raise RuntimeError(f"solver divergence/fatal diagnostic during continuation block ending at total active {total_active}")

        native_iteration, total_mass = latest_report_value(solver, mass_report)
        event = fixed_source_update(solver, total_active, density_kg_m3, manifest)
        event["native_iteration"] = native_iteration
        event["total_liquid_mass_kg"] = total_mass
        event["warnings"] = {
            "floating_point_or_fatal_matches": len(re.findall(r"floating point exception|fatal error", console, re.I)),
            "divergence_matches": len(re.findall(r"Divergence detected in AMG solver", console, re.I)),
            "console_tail": console[-6000:],
        }
        write_json(manifest_path, manifest)

        if total_active == 1050:
            save_pair(solver, paths["smoke"])
            missing = [
                name
                for name in sorted(REQUIRED_REPORT_NAMES)
                if name not in report_paths or not remote_file_exists(solver, report_paths[name])
            ]
            if missing:
                raise RuntimeError(f"required continuation report files missing at smoke: {missing}")
            manifest["smoke"] = {
                "total_active_iteration": total_active,
                "additional_iterations": additional,
                "case": paths["smoke"],
                "source_audit": event["source_audit"],
            }
            write_json(manifest_path, manifest)

        checkpoint_key = {
            1100: "checkpoint1100",
            1250: "checkpoint1250",
            1500: "checkpoint1500",
            2000: "checkpoint2000",
            3000: "checkpoint3000",
            4000: "checkpoint4000",
            5000: "final",
        }.get(total_active)
        if checkpoint_key is not None:
            save_pair(solver, paths[checkpoint_key])

    residuals = parse_residuals(capture.text_since(marker))
    if residuals["point_count"] < ADDITIONAL_ITERATIONS:
        raise RuntimeError(
            f"continuation residual history too short: {residuals['point_count']} < {ADDITIONAL_ITERATIONS}"
        )
    histories: dict[str, Any] = {}
    for name in sorted(REQUIRED_REPORT_NAMES):
        path = report_paths[name]
        if not remote_file_exists(solver, path):
            raise RuntimeError(f"required continuation report is missing: {path}")
        from extract_report_plot_histories import parse_report_forms, read_remote_forms

        history = parse_report_forms(read_remote_forms(solver, path))
        if history["points"] < ADDITIONAL_ITERATIONS:
            raise RuntimeError(f"continuation report history too short for {name}: {history['points']}")
        histories[name] = {
            "points": history["points"],
            "first_iteration": history["iterations"][0],
            "last_iteration": history["iterations"][-1],
        }
    manifest["report_history_summary"] = histories
    manifest["residuals"] = residuals
    manifest["achieved_additional_iterations"] = ADDITIONAL_ITERATIONS
    manifest["achieved_total_active_iteration"] = TARGET_ACTIVE
    return residuals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()
    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local continuation evidence")

    paths = continuation_paths(args.run_root)
    remote_artifacts = [path for key, path in paths.items() if key != "monitor_root"]
    remote_artifacts += [data_path(path) for path in remote_artifacts]
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "run_id": args.manifest.stem,
        "family": FAMILY,
        "mode": "attached-discovery-extension",
        "server_id": args.server_id,
        "server_ip": os.getenv("STUDENT_IP", "unknown"),
        "server_ref": f"student@{os.getenv('STUDENT_IP', 'unknown')}",
        "parent_setup_id": "P7-E5-CZ-ABSORB-COLD-RAMP11692",
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "run_root": args.run_root,
        "parent_active_iteration": PARENT_ACTIVE,
        "additional_iterations": ADDITIONAL_ITERATIONS,
        "requested_total_active_iteration": TARGET_ACTIVE,
        "fixed_absorber_rate_kg_s": LIQUID_INLET_KG_S,
        "update_interval_additional_iterations": UPDATE_INTERVAL,
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
        if not remote_file_exists(solver, args.parent_case) or not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"exact active-1000 parent pair is not visible: {args.parent_case}; {args.parent_data}")

        remote_chdir(solver, str(PureWindowsPath(args.parent_case).parent))
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        zones = fluid_names(solver)
        if set(zones) != {LOWER_ZONE, PARENT_ZONE}:
            raise RuntimeError(f"continuation parent topology mismatch: {zones}")
        density = density_from_case(solver)
        parent_inventory = zone_inventory(solver, density)
        parent_source_tree = read_source_tree(solver)
        parent_source_invariants = source_invariant_summary(solver)
        manifest["parent_readback"] = {
            "fluid_zones": zones,
            "base_invariants": base_invariants(solver),
            "density_kg_m3": density,
            "lower_inventory": parent_inventory,
            "source_tree": parent_source_tree,
            "source_invariants": parent_source_invariants,
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "parent runtime state"),
            "parent_evidence": "durable active-1000 final pair from P7-E5-CZ-ABSORB-COLD-RAMP11692",
        }
        write_json(args.manifest, manifest)

        report_paths = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE)
        manifest["report_files"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(solver, ADDITIONAL_ITERATIONS + 100)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=100)

        # The parent source is already active.  Reassert the same fixed source
        # once and record the readback before the continuation child is saved.
        initial = fixed_source_update(solver, PARENT_ACTIVE, density, manifest)
        manifest["preparation_source_update"] = initial
        solver.settings.file.write_case(file_name=paths["prepared"])
        solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]) or not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("prepared continuation pair was not saved")
        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        reopened = fluid_names(solver)
        if set(reopened) != {LOWER_ZONE, PARENT_ZONE}:
            raise RuntimeError(f"prepared continuation topology mismatch after reopen: {reopened}")
        manifest["prepared_reopen"] = {
            "fluid_zones": reopened,
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
            "source_invariants": source_invariant_summary(solver),
        }
        # Fluent 2025 R2 can restore the inherited report paths on reopen.
        # Use the same child-local paths and refuse any pre-existing file.
        manifest["report_files_after_reopen"] = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE + "-reopen")
        # The report path changes after reopen are intentional only as a
        # file-local implementation repair; the first set remains the declared
        # continuation destination.  Use the post-reopen paths for the solve.
        report_paths = manifest["report_files_after_reopen"]
        manifest["report_files_used_for_solve"] = report_paths
        write_json(args.manifest, manifest)

        # Ensure the fixed source survives the prepared reopen and is audited
        # immediately before the first continuation block.
        final_pre_run = fixed_source_update(solver, PARENT_ACTIVE, density, manifest)
        manifest["pre_run_source_update"] = final_pre_run
        write_json(args.manifest, manifest)

        run_continuation(
            solver,
            paths=paths,
            report_paths=report_paths,
            capture=capture,
            manifest=manifest,
            manifest_path=args.manifest,
            density_kg_m3=density,
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
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
            "source_invariants": source_invariant_summary(solver),
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

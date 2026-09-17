#!/usr/bin/env python3
"""Run a cold-start inlet-matched cell-zone absorber discovery child.

The runner accepts either an initialized case/data parent or an explicitly
requested case-only Hybrid initialization. It preserves the supplied parent,
creates and proves the lower-zone split in a child, ramps a lower-zone phase-2
sink from zero to the liquid-inlet rate, and holds it for the declared
discovery horizon. It does not add an outlet, remesh, or use a UDF.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

import ansys.fluent.core as pyfluent

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import (  # noqa: E402
    base_invariants,
    configure_sources,
    data_path,
    density_from_case,
    disable_sources,
    fluid_names,
    read_source_tree,
    split_lower_zone,
    try_integrated_source_reports,
    zone_inventory,
)
from run_p7_e5_cz_absorb import (  # noqa: E402
    configure_inventory_reports,
    redirect_all_reports,
    source_audit,
    source_invariant_summary,
)
from run_p7_treatment_screen import latest_report_value, parse_residuals, save_pair  # noqa: E402


CANDIDATE = "P7-E5-CZ-ABSORB-COLD-RAMP11692"
FAMILY = "E5-CZ-ABSORB-COLD"
PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
LIQUID_INLET_KG_S = 116.92
RAMP_ITERATIONS = 100
UPDATE_INTERVAL = 10
HORIZON = 1000
CHECKPOINTS = (100, 250, 500, 750, 1000)
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


def save_case_only(solver: Any, case_path: str) -> None:
    """Preserve a valid pre-initialization recovery case without inventing data."""

    solver.settings.file.write_case(file_name=case_path)
    if not remote_file_exists(solver, case_path):
        raise RuntimeError(f"case-only recovery artifact was not saved: {case_path}")


def configure_total_inventory_reports(solver: Any) -> list[dict[str, Any]]:
    """Replace inherited total-liquid reports with the post-split full domain."""

    zones = [PARENT_ZONE, LOWER_ZONE]
    volume = solver.settings.solution.report_definitions.volume
    readbacks: list[dict[str, Any]] = []
    for name, report_type, field, phase in (
        ("e0-liquid-mass-total", "volume-mass", None, "phase-2"),
        ("e0-liquid-volume-total", "volume-integral", "phase-2-vof", "mixture"),
    ):
        names = set(str(item) for item in volume.get_object_names())
        if name in names:
            volume.delete(name_list=[name])
        volume.create(name=name)
        report = volume[name]
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = zones
        if field is not None:
            report.field = field
        if report_type != "volume-integral":
            report.phase = phase
        for key, value in (("per_selection", False), ("average_over", 1), ("create_report_file", True), ("create_report_plot", True)):
            try:
                setattr(report, key, value)
            except Exception:
                pass
        state = safe_get_state(report, f"post-split total-liquid report {name}")
        if not isinstance(state, Mapping) or state.get("report_type") != report_type or state.get("cell_zones") != zones:
            raise RuntimeError(f"post-split total-liquid report readback mismatch for {name}: {state}")
        if report_type != "volume-integral" and state.get("phase") != phase:
            raise RuntimeError(f"post-split total-liquid phase mismatch for {name}: {state}")
        if field is not None and state.get("field") != field:
            raise RuntimeError(f"post-split total-liquid field mismatch for {name}: {state}")
        readbacks.append({"name": name, "state": state})
    return readbacks


def build_paths(run_root: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "pre_split_recovery": str(root / f"{CANDIDATE}-pre-split-recovery.cas.h5"),
        "split_source_off": str(root / f"{CANDIDATE}-split-source-off.cas.h5"),
        "prepared": str(root / f"{CANDIDATE}-prepared.cas.h5"),
        "child_start": str(root / f"{CANDIDATE}-active000.cas.h5"),
        "smoke": str(root / f"{CANDIDATE}-active050.cas.h5"),
        "checkpoint100": str(root / f"{CANDIDATE}-active100.cas.h5"),
        "checkpoint250": str(root / f"{CANDIDATE}-active250.cas.h5"),
        "checkpoint500": str(root / f"{CANDIDATE}-active500.cas.h5"),
        "checkpoint750": str(root / f"{CANDIDATE}-active750.cas.h5"),
        "final": str(root / f"{CANDIDATE}-active1000.cas.h5"),
        "monitor_root": str(root / "monitors"),
    }


def command_for(active_iteration: int) -> float:
    return LIQUID_INLET_KG_S * min(float(active_iteration) / RAMP_ITERATIONS, 1.0)


def schedule_update(
    solver: Any,
    active_iteration: int,
    density_kg_m3: float,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    inventory = zone_inventory(solver, density_kg_m3)
    command = command_for(active_iteration)
    source = configure_sources(
        solver,
        -command / inventory["geometric_volume_m3"],
        inventory["velocity_basis_m_s"],
    )
    integrated = try_integrated_source_reports(solver)
    audit = source_audit(integrated, command)
    invariants = source_invariant_summary(solver)
    event = {
        "event": "ramp_update",
        "active_iteration": active_iteration,
        "command_kg_s": command,
        "ramp_fraction": min(float(active_iteration) / RAMP_ITERATIONS, 1.0),
        "target_command_kg_s": LIQUID_INLET_KG_S,
        "lower_inventory": inventory,
        "source": source,
        "source_audit": audit,
        "source_invariants": invariants,
        "direct_phase1_source_off": invariants["phase1_direct_mass_source_off"],
    }
    manifest["events"].append(event)
    return event


def fatal_console(text: str) -> bool:
    return bool(re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", text, re.I))


def run_discovery(
    solver: Any,
    paths: Mapping[str, str],
    report_paths: Mapping[str, str],
    capture: SessionTranscriptCapture,
    manifest: dict[str, Any],
    manifest_path: Path,
    density_kg_m3: float,
    save_initial: bool = True,
    start_active: int = 0,
) -> None:
    if start_active < 0 or start_active > HORIZON:
        raise ValueError(f"invalid start_active={start_active}; horizon={HORIZON}")
    if start_active:
        initial_event = schedule_update(solver, start_active, density_kg_m3, manifest)
        manifest["resume_schedule"] = initial_event
    else:
        initial_event = schedule_update(solver, 0, density_kg_m3, manifest)
        manifest["initial_schedule"] = initial_event
    if save_initial and start_active == 0:
        save_pair(solver, paths["child_start"])
        manifest["events"].append({"event": "child_start_saved", "active_iteration": 0, "case": paths["child_start"]})
    else:
        manifest["events"].append({"event": "child_start_reused", "active_iteration": start_active, "case": paths["child_start"]})
    write_json(manifest_path, manifest)

    active = start_active
    marker = capture.mark()
    while active < HORIZON:
        block = min(UPDATE_INTERVAL, HORIZON - active)
        solver.settings.solution.run_calculation.iterate(iter_count=block)
        active += block
        console = capture.text_since(marker)
        if fatal_console(console):
            manifest["last_valid_active_iteration"] = active - block
            manifest["terminal_solver_diagnostics"] = {
                "active_iteration": active,
                "console_tail": console[-16000:],
            }
            write_json(manifest_path, manifest)
            raise RuntimeError(f"solver divergence/fatal diagnostic during block ending at active {active}")

        native_iteration, total_mass = latest_report_value(solver, report_paths["e0-liquid-mass-total-rfile"])
        event = schedule_update(solver, active, density_kg_m3, manifest)
        event["native_iteration"] = native_iteration
        event["total_liquid_mass_kg"] = total_mass
        event["warnings"] = {
            "floating_point_or_fatal_matches": len(re.findall(r"floating point exception|fatal error", console, re.I)),
            "divergence_matches": len(re.findall(r"Divergence detected in AMG solver", console, re.I)),
            "console_tail": console[-6000:],
        }
        write_json(manifest_path, manifest)

        if active == 50:
            save_pair(solver, paths["smoke"])
            missing = [
                name
                for name in sorted(REQUIRED_REPORT_NAMES)
                if name not in report_paths or not remote_file_exists(solver, report_paths[name])
            ]
            if missing:
                raise RuntimeError(f"required cold-start absorber report files did not appear during smoke: {missing}")
            manifest["smoke"] = {"active_iterations": 50, "case": paths["smoke"], "source_audit": event["source_audit"]}
            write_json(manifest_path, manifest)
        if active in CHECKPOINTS:
            key = "final" if active == HORIZON else f"checkpoint{active}"
            save_pair(solver, paths[key])

    residuals = parse_residuals(capture.text_since(marker))
    required_points = HORIZON - start_active
    if residuals["point_count"] < required_points:
        raise RuntimeError(f"cold-start residual history too short: {residuals['point_count']} < {required_points}")

    histories: dict[str, Any] = {}
    for name in sorted(REQUIRED_REPORT_NAMES):
        path = report_paths[name]
        if not remote_file_exists(solver, path):
            raise RuntimeError(f"required cold-start absorber report is missing after run: {path}")
        history = parse_report_forms(read_remote_forms(solver, path))
        if history["points"] < required_points:
            raise RuntimeError(f"cold-start report history too short for {name}: {history['points']} < {required_points}")
        histories[name] = {
            "points": history["points"],
            "first_iteration": history["iterations"][0],
            "last_iteration": history["iterations"][-1],
        }
    manifest["report_history_summary"] = histories
    manifest["residuals"] = residuals
    manifest["requested_active_iterations"] = HORIZON
    manifest["achieved_active_iterations"] = HORIZON


def main() -> int:
    global CANDIDATE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--candidate", default=CANDIDATE)
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", help="Optional paired parent data file. Omit only for a case-only cold start.")
    parser.add_argument(
        "--initialize-parent",
        action="store_true",
        help="Hybrid-initialize a case-only parent after prepared-case save/reopen.",
    )
    parser.add_argument(
        "--server-info-file",
        type=Path,
        help="Connect directly to a preserved local Fluent session instead of a configured endpoint.",
    )
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()

    CANDIDATE = args.candidate

    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local cold-start absorber evidence")

    paths = build_paths(args.run_root)
    remote_artifacts = [path for key, path in paths.items() if key != "monitor_root"]
    remote_artifacts += [data_path(path) for path in remote_artifacts]
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": CANDIDATE,
        "run_id": args.manifest.stem,
        "family": FAMILY,
        "mode": "attached-discovery",
        "server_id": args.server_id,
        "server_ip": os.getenv("STUDENT_IP", "unknown"),
        "server_ref": f"student@{os.getenv('STUDENT_IP', 'unknown')}",
        "reference_setup_id": "P7-E0-REF",
        "parent_case": args.parent_case,
        "parent_data": args.parent_data or "",
        "run_root": args.run_root,
        "final_absorber_rate_kg_s": LIQUID_INLET_KG_S,
        "ramp_iterations": RAMP_ITERATIONS,
        "update_interval_active_iterations": UPDATE_INTERVAL,
        "requested_active_iterations": HORIZON,
        "artifact_paths": paths,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        if args.server_info_file:
            if not args.server_info_file.is_file():
                raise FileNotFoundError(f"local Fluent server-info file is unavailable: {args.server_info_file}")
            solver = pyfluent.connect_to_fluent(
                server_info_file_name=str(args.server_info_file),
                allow_remote_host=False,
                cleanup_on_exit=False,
                start_transcript=True,
            )
        else:
            solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        existing = [path for path in remote_artifacts if remote_file_exists(solver, path)]
        if existing:
            raise FileExistsError(f"refusing to overwrite remote cold-start artifacts: {existing}")
        if not remote_file_exists(solver, args.parent_case):
            raise FileNotFoundError(f"parent case is not visible: {args.parent_case}")
        if args.parent_data and not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"parent data is not visible: {args.parent_data}")
        if not args.parent_data and not args.initialize_parent:
            raise RuntimeError("a case-only parent requires --initialize-parent; do not infer an initialized field")

        remote_chdir(solver, str(PureWindowsPath(args.parent_case).parent))
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        solver.settings.file.read_case(file_name=args.parent_case)
        if args.parent_data:
            solver.settings.file.read_data(file_name=args.parent_data)
        names = fluid_names(solver)
        if names != [PARENT_ZONE]:
            raise RuntimeError(f"initialized E0 topology mismatch before split: {names}")
        manifest["initialized_parent_readback"] = {
            "fluid_zones": names,
            "base_invariants": base_invariants(solver),
            "runtime_state": safe_get_state(solver.settings.solution.run_calculation, "initialized runtime state"),
            "initialization_claim": (
                "initialized parent data read from the supplied pair"
                if args.parent_data
                else "case-only parent; hybrid initialization is required after prepared save/reopen"
            ),
        }
        density = density_from_case(solver)
        manifest["liquid_density_kg_m3"] = density
        if args.parent_data:
            save_pair(solver, paths["pre_split_recovery"])
        else:
            save_case_only(solver, paths["pre_split_recovery"])
        manifest["events"].append({"event": "pre_split_recovery_saved", "case": paths["pre_split_recovery"]})

        split = split_lower_zone(solver, capture, require_reference_mesh=False)
        manifest["mesh_split"] = split
        disable_sources(solver)
        manifest["split_source_off_readback"] = read_source_tree(solver)
        if args.parent_data:
            save_pair(solver, paths["split_source_off"])
        else:
            save_case_only(solver, paths["split_source_off"])
        manifest["events"].append({"event": "split_source_off_saved", "case": paths["split_source_off"]})

        manifest["total_inventory_definitions"] = configure_total_inventory_reports(solver)
        manifest["monitor_definitions"] = configure_inventory_reports(solver)
        manifest["report_files"] = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE)
        manifest["residual_configuration"] = configure_residual_history(solver, 1200)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=100)
        manifest["source_contract"] = {
            "parent_zone": PARENT_ZONE,
            "lower_zone": LOWER_ZONE,
            "phase2_mass_only": True,
            "direct_phase1_mass_source": "off",
            "mixture_momentum_components": ["x", "y", "z"],
            "patch_reset_route": "excluded",
            "outlet_change": "excluded",
        }
        write_json(args.manifest, manifest)

        solver.settings.file.write_case(file_name=paths["prepared"])
        if args.parent_data:
            solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]):
            raise RuntimeError("prepared cold-start case was not saved")
        if args.parent_data and not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("prepared cold-start data was not saved")
        solver.settings.file.read_case(file_name=paths["prepared"])
        if args.parent_data:
            solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        if set(fluid_names(solver)) != {PARENT_ZONE, LOWER_ZONE}:
            raise RuntimeError(f"prepared save/reopen topology mismatch: {fluid_names(solver)}")
        manifest["prepared_reopen"] = {
            "fluid_zones": fluid_names(solver),
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
        }
        manifest["report_files_after_reopen"] = redirect_all_reports(solver, paths["monitor_root"], CANDIDATE)
        if args.initialize_parent:
            solver.settings.solution.initialization.hybrid_initialize()
            manifest["initialization"] = {
                "method": "hybrid",
                "state_after_initialization": safe_get_state(
                    solver.settings.solution.initialization,
                    "hybrid initialization readback",
                ),
            }
        write_json(args.manifest, manifest)

        run_discovery(
            solver,
            paths,
            manifest["report_files_after_reopen"],
            capture,
            manifest,
            args.manifest,
            density,
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

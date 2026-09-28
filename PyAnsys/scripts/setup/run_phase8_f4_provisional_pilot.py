#!/usr/bin/env python3
"""Run a bounded provisional F4 EWF pilot with common and film reports."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup"),
                str(ROOT / "scripts" / "inspection")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.ewf_report_specs import REPORT_SPECS
from pyansys_fluent.ewf_reports import ensure_surface_report
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history
from build_phase8_f4_provisional_ewf import inspect as inspect_ewf
from run_phase8_f3_pilot import add_dpm_mass_source_report, reset_phase8_reports
from run_phase8_parity_carrier import (
    FAILURE_MARKER, ITERATION_ROW, RUN_ROOT, FINAL_ROOT,
    check_reports, configure_reports, dump, load_pair, require, save_pair, sha256,
)

FILM_KEYS = (
    "film_mass_total", "film_thickness_max", "film_thickness_area_average",
    "film_velocity_area_average", "film_courant_max",
    "film_secondary_phase_mass_total", "film_dpm_mass_source_total",
    "film_outflow_mass_total", "film_stripped_mass_total",
)
REQUIRED_FILM_KEYS = {"film_mass_total", "film_thickness_max",
                      "film_thickness_area_average", "film_velocity_area_average"}


def configure_film_reports(solver, monitor_root: Path, definitions: dict,
                           paths: dict) -> dict:
    by_key = {spec.key: spec for spec in REPORT_SPECS}
    available = {}
    unavailable = {}
    branch = solver.settings.solution.monitor.report_files
    for key in FILM_KEYS:
        spec = by_key[key]
        try:
            configured = ensure_surface_report(
                solver, spec, prefix="p8-ewf", surfaces=["wall"],
                object_policy="fail", create_history_file=False, frequency=10)
            name = f"p8-ewf-{spec.suffix}"
            state = solver.settings.solution.report_definitions.surface[name].get_state()
            path = monitor_root / f"{name}.out"
            require(not path.exists(), f"EWF report path exists: {path}")
            branch.create(name=f"{name}-rfile")
            branch[f"{name}-rfile"].set_state(
                {"file_name": str(path), "report_defs": [name],
                 "frequency": 10, "active": True})
            definitions[name] = {"kind": state["report_type"], "field": state.get("field"),
                                 "surface": "wall", "units": spec.expected_dimension,
                                 "state": state}
            paths[name] = str(path)
            available[key] = {"name": name, "configured": configured}
        except Exception as exc:
            name = f"p8-ewf-{spec.suffix}"
            surface = solver.settings.solution.report_definitions.surface
            if name in surface.get_object_names() and name not in definitions:
                surface.delete(name_list=[name])
            if key in REQUIRED_FILM_KEYS:
                raise
            unavailable[key] = repr(exc)
    return {"installed": available, "unavailable": unavailable}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("child_receipt", type=Path)
    parser.add_argument("--iterations", type=int, default=1000)
    args = parser.parse_args()
    require(args.iterations >= 1000 and args.iterations % 1000 == 0,
            "Use whole 1000-iteration blocks")
    child = json.loads(args.child_receipt.read_text(encoding="utf-8"))
    require(child["status"] == "CASE_DATA_VERIFIED" and
            child["basis"] == "Phase 7.2A E2.7 provisional" and
            child["reopened"]["film_wall"]["enable_dpm_wall_splash"] is True,
            "F4 child lacks the intended provisional EWF wall package")
    source = Path(child["child_base"])
    for kind in ("case", "data"):
        path = Path(child["child_pair"][kind])
        require(path.is_file() and sha256(path) == child["child_pair"][f"{kind}_sha256"],
                f"F4 source {kind} identity changed")
    label = f"F4-26p81-5pct-E27-provisional-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    local, final = RUN_ROOT / label, FINAL_ROOT / label
    manifest = ROOT / "output" / "phase8-ewf" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest.exists(),
            "F4 pilot collision")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    run = {"status": "RUNNING", "family": "F4", "variant": "provisional-E2.7-EWF",
           "speed_m_s": 26.81, "fraction": 0.05, "source_receipt": str(args.child_receipt),
           "source_case_sha256": child["child_pair"]["case_sha256"],
           "source_data_sha256": child["child_pair"]["data_sha256"],
           "source_interval": 100, "requested_additional_iterations": args.iterations,
           "paths": {"local": str(local), "final": str(final),
                     "transcript": str(local / "transcript.txt")},
           "checkpoints": [],
           "claim_limit": "Exploratory E2.7-based F4; F3 carrier gate failed and EWF transfer/fates require separate accounting."}
    dump(manifest, run)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double",
                           processor_count=4, ui_mode="gui", start_timeout=240,
                           cleanup_on_exit=True, start_transcript=True)
    capture = None
    try:
        load_pair(solver, source)
        run["source_readback"] = inspect_ewf(solver)
        run["autosave_configuration"] = configure_autosave(
            solver, str(local), data_frequency=1000)
        run["removed_inherited_report_definitions"] = reset_phase8_reports(solver)
        definitions, paths = configure_reports(solver, local / "monitors")
        run["dpm_source_reports"] = add_dpm_mass_source_report(
            solver, local / "monitors", definitions, paths)
        run["film_reports"] = configure_film_reports(
            solver, local / "monitors", definitions, paths)
        run["report_definitions"] = definitions
        run["report_paths"] = paths
        run["residual_configuration"] = configure_residual_history(
            solver, args.iterations + 200)
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        run["start_pair"] = save_pair(solver, local / "active000")
        load_pair(solver, local / "active000")
        run["start_reopen_readback"] = inspect_ewf(solver)
        check_reports(solver, definitions, paths)
        run["initial_report_compute"] = solver.settings.solution.report_definitions.compute(
            report_defs=list(definitions))
        require(len(run["initial_report_compute"]) == len(definitions),
                "F4 initial report computation incomplete")
        dump(manifest, run)
        for block in range(1, args.iterations // 1000 + 1):
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            output = capture.text_since(marker)
            rows = [int(value) for value in ITERATION_ROW.findall(output)]
            require(rows and set(range(rows[-1] - 999, rows[-1] + 1)).issubset(set(rows)),
                    f"F4 block {block} missing native iteration rows")
            require(not FAILURE_MARKER.search(output), f"F4 fatal event in block {block}")
            destination = (final / "final" if block * 1000 == args.iterations else
                           local / f"active{block*1000:04d}")
            run["checkpoints"].append({"additional_iterations": block * 1000,
                                       "native_iteration": rows[-1],
                                       **save_pair(solver, destination)})
            run["last_valid_native_iteration"] = rows[-1]
            dump(manifest, run)
        load_pair(solver, final / "final")
        run["final_reopen_readback"] = inspect_ewf(solver)
        check_reports(solver, definitions, paths)
        run["status"] = "COMPLETE"
    except Exception as exc:
        run["status"] = "BLOCKED"
        run["error"] = repr(exc)
        raise
    finally:
        dump(manifest, run)
        if capture is not None:
            capture.close()
        if run["status"] == "COMPLETE":
            solver.exit()
    print(json.dumps({"status": run["status"], "manifest": str(manifest)}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run a bounded F3 allocated, two-way DPM discovery from the verified child."""
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
from pyansys_fluent.common import safe_get_state
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history

from build_phase8_dpm_reference import inspect as audit_dpm
from run_dpm_particle_tracks import run_dpm_particle_track_check
from run_phase8_parity_carrier import (
    FAILURE_MARKER, ITERATION_ROW, RUN_ROOT, FINAL_ROOT, FLUID_ZONES,
    check_reports, configure_reports, dump, load_pair, require, save_pair, sha256,
)


def reset_phase8_reports(solver) -> dict:
    reports = solver.settings.solution.report_definitions
    removed = {}
    for kind in ("flux", "volume", "surface"):
        branch = getattr(reports, kind)
        names = [name for name in branch.get_object_names() if name.startswith("p8-")]
        if names:
            branch.delete(name_list=names)
        removed[kind] = names
    return removed


def add_dpm_mass_source_report(solver, monitor_root: Path, definitions: dict,
                               paths: dict) -> dict:
    """Sum available per-cell DPM mass and momentum exchange rates."""
    branch = solver.settings.solution.report_definitions.volume
    probe = branch["p8-volume-phase2-total"].field
    available = {str(value) for value in probe.allowed_values()}
    candidates = [str(value) for value in available
                  if "dpm" in str(value).lower() and "mass" in str(value).lower()
                  and "source" in str(value).lower()]
    if not candidates:
        return {"status": "UNAVAILABLE", "candidate_fields": []}
    require(len(candidates) == 1, f"Ambiguous DPM mass-source fields: {candidates}")
    specs = [("p8-dpm-mass-source-total", candidates[0], "kg/s")]
    specs.extend((f"p8-dpm-{axis}-mom-source-total", f"dpm-{axis}-mom-source", "N")
                 for axis in ("x", "y", "z") if f"dpm-{axis}-mom-source" in available)
    installed = {}
    files = solver.settings.solution.monitor.report_files
    for name, field, units in specs:
        if name in branch.get_object_names():
            state = safe_get_state(branch[name], name)
            require(state.get("report_type") == "volume-sum" and state.get("field") == field and
                    name in definitions and name in paths,
                    f"Existing DPM source report is not a valid Volume Sum: {name}")
            installed[name] = {"field": field, "units": units, "state": state,
                               "report_file": paths[name], "reused": True}
            continue
        branch.create(name=name)
        report = branch[name]
        report.report_type = "volume-sum"
        report.field = field
        report.cell_zones = list(FLUID_ZONES)
        report.phase = "mixture"
        report.per_selection = False
        report.average_over = 1
        report.create_report_file = False
        report.create_report_plot = False
        state = safe_get_state(report, name)
        require(state.get("field") == field and state.get("cell_zones") == list(FLUID_ZONES),
                f"DPM source report readback failed: {state}")
        output = monitor_root / f"{name}.out"
        require(not output.exists(), f"DPM source report file already exists: {output}")
        files.create(name=f"{name}-rfile")
        files[f"{name}-rfile"].set_state(
            {"file_name": str(output), "report_defs": [name], "frequency": 10, "active": True})
        definitions[name] = {"kind": "volume-sum", "phase": "mixture", "field": field,
                             "cell_zones": list(FLUID_ZONES), "units": units, "state": state}
        paths[name] = str(output)
        installed[name] = {"field": field, "units": units, "state": state,
                           "report_file": str(output)}
    return {"status": "INSTALLED", "candidate_fields": candidates,
            "definitions": installed,
            "unavailable_momentum_axes": [axis for axis in ("x", "y", "z")
                                          if f"dpm-{axis}-mom-source" not in available]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("child_receipt", type=Path)
    parser.add_argument("--iterations", type=int, default=1000)
    args = parser.parse_args()
    require(args.iterations >= 1000 and args.iterations % 1000 == 0,
            "Run in declared 1000-iteration blocks")
    source = json.loads(args.child_receipt.read_text(encoding="utf-8"))
    require(source["status"] == "CASE_DATA_VERIFIED" and source["mode"] == "allocated",
            "F3 source must be a verified allocated DPM child")
    require(source["family"] == "F2" and 0 < float(source["fraction"]) < 1,
            "F3 pilot requires a verified split-inlet allocated child")
    fraction = float(source["fraction"])
    speed = float(source["speed_m_s"])
    source_interval = int(source.get("source_interval", 1))
    source_base = Path(source["child_base"])
    for kind in ("case", "data"):
        source_file = Path(source["child_pair"][kind])
        require(source_file.is_file() and sha256(source_file) == source["child_pair"][f"{kind}_sha256"],
                f"F3 source {kind} identity changed")
    speed_label = str(speed).replace(".", "p")
    fraction_label = format(100 * fraction, ".15g").replace(".", "p")
    label = (f"F3-{speed_label}-{fraction_label}pct-coupled-upd{source_interval}-"
             f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    local, final = RUN_ROOT / label, FINAL_ROOT / label
    manifest = ROOT / "output" / "phase8-carrier" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest.exists(), "F3 run collision")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    receipt = {"status": "RUNNING", "family": "F3", "variant": "allocated-two-way-dpm",
               "speed_m_s": speed, "fraction": fraction, "source_receipt": str(args.child_receipt),
               "source_interval": source_interval,
               "source_case_sha256": source["child_pair"]["case_sha256"],
               "source_data_sha256": source["child_pair"]["data_sha256"],
               "requested_additional_iterations": args.iterations,
               "paths": {"local": str(local), "final": str(final),
                         "transcript": str(local / "transcript.txt")}, "checkpoints": [],
               "claim_limit": "Pilot only; DPM sources and incomplete tracks require separate accounting."}
    dump(manifest, receipt)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                           ui_mode="gui", start_timeout=240, cleanup_on_exit=True, start_transcript=True)
    capture = None
    try:
        load_pair(solver, source_base)
        receipt["source_readback"] = audit_dpm(solver, fraction=fraction, allocated=True,
                                                speed=speed)
        receipt["autosave_configuration"] = configure_autosave(solver, str(local), data_frequency=1000)
        receipt["removed_inherited_report_definitions"] = reset_phase8_reports(solver)
        definitions, report_paths = configure_reports(solver, local / "monitors")
        receipt["dpm_mass_source_report"] = add_dpm_mass_source_report(
            solver, local / "monitors", definitions, report_paths)
        receipt["report_definitions"] = definitions
        receipt["report_paths"] = report_paths
        receipt["residual_configuration"] = configure_residual_history(solver, args.iterations + 200)
        volume_field = solver.settings.solution.report_definitions.volume["p8-volume-phase2-total"].field
        receipt["candidate_dpm_volume_fields"] = [str(name) for name in volume_field.allowed_values()
                                                  if "dpm" in str(name).lower() or "particle" in str(name).lower()]
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        receipt["start_pair"] = save_pair(solver, local / "active000")
        load_pair(solver, local / "active000")
        receipt["start_reopen_readback"] = audit_dpm(solver, fraction=fraction, allocated=True,
                                                      speed=speed)
        check_reports(solver, definitions, report_paths)
        receipt["initial_report_compute"] = solver.settings.solution.report_definitions.compute(
            report_defs=list(definitions))
        require(len(receipt["initial_report_compute"]) == len(definitions),
                "F3 initial report computation incomplete")
        dump(manifest, receipt)
        last_coordinate = None
        for block in range(1, args.iterations // 1000 + 1):
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            block_text = capture.text_since(marker)
            rows = [int(value) for value in ITERATION_ROW.findall(block_text)]
            unique = sorted(set(rows))
            require(unique and set(range(unique[-1] - 999, unique[-1] + 1)).issubset(set(unique)),
                    f"F3 block {block} missing native iterations")
            require(not FAILURE_MARKER.search(block_text), f"F3 fatal event in block {block}")
            if last_coordinate is not None:
                require(unique[0] <= last_coordinate + 1 <= unique[-1],
                        "F3 native-coordinate discontinuity")
            last_coordinate = unique[-1]
            destination = final / "final" if block * 1000 == args.iterations else local / f"active{block*1000:04d}"
            receipt["checkpoints"].append({"additional_iterations": block * 1000,
                                           "native_iteration": last_coordinate,
                                           **save_pair(solver, destination)})
            receipt["last_valid_additional_iterations"] = block * 1000
            dump(manifest, receipt)
        load_pair(solver, final / "final")
        receipt["final_reopen_readback"] = audit_dpm(solver, fraction=fraction, allocated=True,
                                                      speed=speed)
        check_reports(solver, definitions, report_paths)
        receipt["achieved_additional_iterations"] = args.iterations
        try:
            receipt["particle_tracks"] = run_dpm_particle_track_check(
                solver, run_label=label, order="diameter-ascending", keep_going=True,
                zone_summaries=True)
            receipt["tracking_status"] = "COMPLETE" if all(
                item.get("status") == "ok" for item in receipt["particle_tracks"]["results"]
            ) else "PARTIAL"
        except Exception as exc:
            receipt["tracking_status"] = "BLOCKED"
            receipt["tracking_error"] = repr(exc)
        receipt["status"] = "COMPLETE"
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(manifest, receipt)
        if capture is not None:
            capture.close()
        if receipt["status"] == "COMPLETE":
            solver.exit()
    print(json.dumps({"status": receipt["status"], "manifest": str(manifest)}, indent=2))


if __name__ == "__main__":
    main()

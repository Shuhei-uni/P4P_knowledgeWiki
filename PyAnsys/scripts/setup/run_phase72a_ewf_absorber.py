#!/usr/bin/env python3
"""Build and run a preserved Phase 7.2A bulk-plus-EWF collector child."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
import traceback

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts/setup"), str(ROOT / "scripts/inspection")]
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.ewf_absorber import LOWER_FILM_WALL, configure, readback, ensure_reports
from pyansys_fluent.stage4_native import ensure_remote_directory, configure_autosave, remote_file_sha256
from run_phase72a_e27_server1_continuation import native_iteration, pair_save, validate_e27
from run_phase72a_stage2_e27_roughness import SOURCE_CASE, SOURCE_DATA, SOURCE_HASHES, dump
from run_phase72a_family_r_native import apply_roughness, wall_readback, OUTER_WALL_ZONES
from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType


def film_mass(solver):
    values = solver.settings.solution.report_definitions.compute(report_defs=["p72a-e2.7-ewf-film-mass-total"])
    return float(values[0]["p72a-e2.7-ewf-film-mass-total"][0])


def prepare_roughness_children(server_id: str, proof_path: Path, output_root: Path) -> dict:
    """Prepare matched R3/R4 source cases after the smooth native proof."""
    proof = json.loads(proof_path.read_text())
    if proof["status"] != "SOURCE_REMOVAL_VERIFIED":
        raise RuntimeError("Native EWF removal and restoration must be verified first")
    parent = proof["production_pair"]
    solver = connect(server_id, start_transcript=False)
    base = PureWindowsPath(parent["case"]).parent / "roughness-children"
    scratch = base / "scratch"
    ensure_remote_directory(solver, str(base))
    ensure_remote_directory(solver, str(scratch))
    for kind in ("case", "data"):
        if remote_file_sha256(solver, parent[kind], str(scratch / f"parent-{kind}.sha256.txt")) != parent[f"{kind}_sha256"]:
            raise RuntimeError(f"Verified source parent {kind} hash changed")
    output_root.mkdir(parents=True, exist_ok=False)
    path = output_root / "prepared-stage2.json"
    record = {"status": "PREPARING", "parent": parent, "source_proof": str(proof_path), "children": {}}
    dump(path, record)
    for case, height in (("R3", 5e-4), ("R4", 1e-3)):
        solver.settings.file.read_case(file_name=parent["case"])
        solver.settings.file.read_data(file_name=parent["data"])
        work = base / case
        monitor = work / "monitors"
        ensure_remote_directory(solver, str(work))
        ensure_remote_directory(solver, str(monitor))
        child = {"roughness": apply_roughness(solver, case, height, 0.5)}
        for name in solver.settings.solution.monitor.report_files.get_object_names():
            solver.settings.solution.monitor.report_files[name].file_name = str(monitor / f"{name}.out")
        child["upper_film_mass_kg"] = film_mass(solver)
        if abs(child["upper_film_mass_kg"] - proof["restored_upper_film_mass_kg"]) > 1e-8:
            raise RuntimeError("Roughness preparation changed inherited film inventory")
        child["collector"] = readback(solver)
        child["pair"] = pair_save(solver, work / "prepared.cas.h5", scratch, scratch_tag=case)
        solver.settings.file.read_case(file_name=child["pair"]["case"])
        solver.settings.file.read_data(file_name=child["pair"]["data"])
        child["reopen_collector"] = readback(solver)
        child["reopen_native_iteration"] = native_iteration(solver)
        child["reopen_e27"] = validate_e27(solver, max_thickness=1.0)
        child["reopen_roughness"] = wall_readback(solver)
        for name in OUTER_WALL_ZONES:
            state = child["reopen_roughness"]["settings"][name]
            if abs(float(state["roughness_height"]["value"]) - height) > 1e-12 or abs(float(state["roughness_const"]["value"]) - 0.5) > 1e-12:
                raise RuntimeError(f"Reopened {case} roughness mismatch on {name}")
        if child["reopen_native_iteration"] != 13586:
            raise RuntimeError("Roughness child lost the parent iteration coordinate")
        # apply_roughness itself records exact native per-wall readbacks.
        child["status"] = "PREPARED_REOPEN_VERIFIED"
        record["children"][case] = child
        dump(path, record)
    selected = record["children"]["R3"]["pair"]
    solver.settings.file.read_case(file_name=selected["case"])
    solver.settings.file.read_data(file_name=selected["data"])
    record["selected_server1_case"] = "R3"
    record["selected_readback"] = readback(solver)
    record["status"] = "PREPARED_R3_R4_REOPEN_VERIFIED"
    dump(path, record)
    return record


def audit_prepared_roughness_children(server_id: str, manifest_path: Path) -> dict:
    """Read persisted roughness as well as film hooks for both siblings."""
    record = json.loads(manifest_path.read_text())
    if record["status"] != "PREPARED_R3_R4_REOPEN_VERIFIED":
        raise RuntimeError("Both paired roughness artifacts must exist before this audit")
    solver = connect(server_id, start_transcript=False)
    for case, height in (("R4", 1e-3), ("R3", 5e-4)):
        child = record["children"][case]
        solver.settings.file.read_case(file_name=child["pair"]["case"])
        solver.settings.file.read_data(file_name=child["pair"]["data"])
        walls = wall_readback(solver)
        for name in OUTER_WALL_ZONES:
            state = walls["settings"][name]
            if abs(float(state["roughness_height"]["value"]) - height) > 1e-12 or abs(float(state["roughness_const"]["value"]) - 0.5) > 1e-12:
                raise RuntimeError(f"Persisted {case} roughness differs on {name}")
        if native_iteration(solver) != 13586 or abs(film_mass(solver) - 5.842478445133369) > 1e-8:
            raise RuntimeError("Persisted child altered the inherited native coordinate/inventory")
        child["final_reopen_audit"] = {"roughness": walls, "collector": readback(solver),
                                        "e27": validate_e27(solver, max_thickness=1.0)}
        dump(manifest_path, record)
    record["final_native_audit"] = "PASS_R3_R4"
    dump(manifest_path, record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=["1", "3"], required=True)
    parser.add_argument("--case", choices=["smooth", "R3", "R4"], default="smooth")
    parser.add_argument("--stamp", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=0)
    args = parser.parse_args()
    if args.iterations < 0 or args.iterations % 1000:
        parser.error("Scientific iterations must be whole 1000-iteration blocks")
    out = args.output_root.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = out / "run-manifest.json"
    work = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\EWFAbsorber") / args.case / args.stamp
    scratch = work / "scratch"
    manifest = {"status": "PREFLIGHT", "server_id": args.server_id, "case": args.case, "parent_case": str(SOURCE_CASE), "parent_data": str(SOURCE_DATA), "expected_parent_hashes": SOURCE_HASHES, "work_root": str(work), "requested_iterations": args.iterations}
    dump(manifest_path, manifest)
    capture = None
    try:
        solver = connect(args.server_id, start_transcript=False)
        ensure_remote_directory(solver, str(work))
        ensure_remote_directory(solver, str(scratch))
        manifest["preserved_endpoint"] = pair_save(solver, work / "previous-endpoint.cas.h5", scratch, scratch_tag="previous")
        dump(manifest_path, manifest)
        manifest["parent_hashes"] = {
            "case": remote_file_sha256(solver, str(SOURCE_CASE), str(scratch / "parent-case.sha256.txt")),
            "data": remote_file_sha256(solver, str(SOURCE_DATA), str(scratch / "parent-data.sha256.txt")),
        }
        if manifest["parent_hashes"] != SOURCE_HASHES:
            raise RuntimeError("Parent hashes do not match the recorded E2.7 pair")
        solver.settings.file.read_case(file_name=str(SOURCE_CASE))
        solver.settings.file.read_data(file_name=str(SOURCE_DATA))
        manifest["parent_readback"] = validate_e27(solver)
        if native_iteration(solver) != 13586:
            raise RuntimeError("Unexpected E2.7 parent coordinate")
        manifest["upper_film_mass_before"] = film_mass(solver)
        walls = solver.settings.setup.boundary_conditions.wall
        geometry = solver.fields.field_data.get_field_data(SurfaceFieldDataRequest(surfaces=[LOWER_FILM_WALL], data_types=[SurfaceDataType.FacesCentroid]))[LOWER_FILM_WALL]
        coordinates = np.asarray(geometry.face_centroids)
        if len(coordinates) != 34 or not np.all((coordinates[:, 1] >= 0) & (coordinates[:, 1] <= 0.1)):
            raise RuntimeError("Lower film wall is not inside the verified absorber band")
        manifest["lower_wall_geometry"] = {"faces": len(coordinates), "minimum": coordinates.min(axis=0).tolist(), "maximum": coordinates.max(axis=0).tolist()}
        lower = walls[LOWER_FILM_WALL].phase["mixture"].wall_film
        lower.eulerian_film_wall = True
        lower.film_condition_type = "film-wall-initial"
        lower.film_height.set_state({"option": "value", "value": 0.0})
        lower.enable_flow_momentum_coupling = False
        # Allocate the newly enabled film domain before expressions touch its
        # fields, then restore the exact parent bulk/upper-film data. The new
        # lower film starts dry; no hybrid bulk initialization is performed.
        manifest["status"] = "INITIALIZING_NEW_FILM_STORAGE"
        dump(manifest_path, manifest)
        solver.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        solver.settings.file.read_data(file_name=str(SOURCE_DATA))
        manifest["status"] = "BINDING_FILM_SOURCE"
        dump(manifest_path, manifest)
        manifest["collector_configuration"] = configure(solver)
        parameters = solver.rp_vars("wall-film/model-parameters")
        solver.rp_vars("wall-film/model-parameters", [(k, 1.0 if k == "thickness-limit" else v) for k, v in parameters])
        if args.case != "smooth":
            manifest["roughness"] = apply_roughness(solver, args.case, {"R3": 5e-4, "R4": 1e-3}[args.case], 0.5)
        manifest["upper_film_mass_after"] = film_mass(solver)
        if abs(manifest["upper_film_mass_after"] - manifest["upper_film_mass_before"]) > 1e-8:
            raise RuntimeError("Inherited upper film inventory changed during configuration")
        manifest["collector_readback"] = readback(solver)
        monitor = work / "monitors"
        ensure_remote_directory(solver, str(monitor))
        manifest["collector_reports"] = ensure_reports(solver, str(monitor))
        # Prepared artifacts must also be safe to resume interactively without
        # appending to inherited/OneDrive monitor files.
        files = solver.settings.solution.monitor.report_files
        for name in files.get_object_names():
            files[name].file_name = str(monitor / f"{name}.out")
            files[name].frequency = 1
            files[name].active = True
        manifest["prepared_pair"] = pair_save(solver, work / "prepared.cas.h5", scratch, scratch_tag="prepared")
        dump(manifest_path, manifest)
        solver.settings.file.read_case(file_name=manifest["prepared_pair"]["case"])
        solver.settings.file.read_data(file_name=manifest["prepared_pair"]["data"])
        manifest["reopen_readback"] = readback(solver)
        # Recover the parent clock without discarding the source-case delta.
        solver.settings.file.read_data(file_name=str(SOURCE_DATA))
        if native_iteration(solver) != 13586:
            raise RuntimeError("Prepared case plus parent data coordinate mismatch")
        manifest["reopen_e27"] = validate_e27(solver, max_thickness=1.0)
        manifest["status"] = "PREPARED_REOPEN_VERIFIED"
        dump(manifest_path, manifest)
        if not args.iterations:
            return 0
        # Preserve all inherited report definitions but write new local histories.
        files = solver.settings.solution.monitor.report_files
        monitor = work / "monitors"
        ensure_remote_directory(solver, str(monitor))
        for name in files.get_object_names():
            report = files[name]
            state = report.get_state()
            report.file_name = str(monitor / f"{state['report_defs'][0]}.out")
            report.frequency = 1
            report.active = True
        capture = SessionTranscriptCapture(solver, stream_path=out / "transcript-stream.txt", echo=False)
        capture.start()
        configure_autosave(solver, str(work), data_frequency=1000)
        manifest["status"] = "RUNNING"
        manifest["completed_blocks"] = []
        dump(manifest_path, manifest)
        for block in range(1, args.iterations // 1000 + 1):
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            coordinate = native_iteration(solver)
            if coordinate != 13586 + block * 1000:
                raise RuntimeError(f"Unexpected native coordinate {coordinate}")
            record = pair_save(solver, work / f"block{block}-N{coordinate}.cas.h5", scratch, scratch_tag=f"block{block}")
            record["collector"] = readback(solver)
            manifest["completed_blocks"].append(record)
            dump(manifest_path, manifest)
        manifest["final_pair"] = pair_save(solver, work / "final.cas.h5", scratch, scratch_tag="final")
        solver.settings.file.read_case(file_name=manifest["final_pair"]["case"])
        solver.settings.file.read_data(file_name=manifest["final_pair"]["data"])
        manifest["final_reopen_collector"] = readback(solver)
        manifest["status"] = "COMPLETE"
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        dump(manifest_path, manifest)
        return 0
    except Exception as exc:
        manifest["status"] = "BLOCKED_IMPLEMENTATION"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        dump(manifest_path, manifest)
        raise
    finally:
        if capture:
            capture.close()


if __name__ == "__main__":
    raise SystemExit(main())

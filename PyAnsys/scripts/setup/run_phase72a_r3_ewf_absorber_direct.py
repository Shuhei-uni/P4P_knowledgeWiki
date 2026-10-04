"""Run matched R3/E2.7 with the new collector in a caller-owned local REPL.

Launch and explicit shutdown belong to the direct-fluent-use skill/controller.
This worker never attaches to fleet servers, launches, or exits Fluent.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts/setup"), str(ROOT / "scripts/inspection")]
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.ewf_absorber import LOWER_FILM_WALL, configure, readback, ensure_reports
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history
from run_phase72a_e27_server1_continuation import native_iteration, validate_e27
from run_phase72a_ewf_absorber import film_mass
from run_phase72a_stage2_e27_roughness import SOURCE_HASHES, configure_coverage
from run_phase72a_family_r_native import apply_roughness, wall_readback, OUTER_WALL_ZONES

PARENT = Path(r"C:\Users\Shuhei Yokkaichi\OneDrive\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\FamilyE\E2.7-continuation-5000\20260923T102912Z\P72A-E2.7-CONT5000-final-N13586.cas.h5")
OLD = ROOT / "output/phase72a-stage2-cap1m/R3-recovery2-20261003/report-histories.json"


def dump(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")
    temp.replace(path)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_pair(solver, path, coordinate):
    data = Path(str(path).replace(".cas.h5", ".dat.h5"))
    if path.exists() or data.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    solver.settings.file.write_case(file_name=str(path))
    solver.settings.file.write_data(file_name=str(data))
    return {"case": str(path), "data": str(data), "native_iteration": coordinate,
            "case_sha256": sha(path), "data_sha256": sha(data)}


def file_history(path):
    rows = []
    for line in path.read_text().splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and re.fullmatch(r"\d+", parts[0]):
            rows.append((int(parts[0]), float(parts[1])))
    if not rows:
        raise RuntimeError(f"No native report rows in {path}")
    return {"points": len(rows), "iterations": [x for x, _ in rows], "values": [y for _, y in rows], "file": str(path)}


def validate_roughness(solver):
    state = wall_readback(solver)
    for name in OUTER_WALL_ZONES:
        values = state["settings"][name]
        if abs(float(values["roughness_height"]["value"]) - 5e-4) > 1e-12 or abs(float(values["roughness_const"]["value"]) - .5) > 1e-12:
            raise RuntimeError(f"R3 roughness mismatch on {name}")
    return state


def run_local_r3(solver, stamp):
    runtime = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse")
    work = runtime / "Phase72A-R3-E27-NewAbsorber" / stamp
    out = ROOT / "output/phase72a-r3-ewf-absorber-direct" / stamp
    work.mkdir(parents=True, exist_ok=False)
    out.mkdir(parents=True, exist_ok=False)
    monitor = work / "monitors"
    monitor.mkdir()
    manifest_path = out / "run-manifest.json"
    manifest = {"status": "PREFLIGHT", "execution": "direct-fluent-use", "fleet_server_access": False,
        "case": "R3+E2.7+shared_bulk_EWF_absorber", "parent_case": str(PARENT),
        "native_start": 13586, "requested_additional_iterations": 3000, "expected_terminal_iteration": 16586,
        "old_absorber_histories": str(OLD), "matched_cap_m": 1.0, "work_root": str(work),
        "completed_blocks": [], "started_utc": datetime.now(timezone.utc).isoformat()}
    dump(manifest_path, manifest)
    capture = SessionTranscriptCapture(solver, stream_path=out / "transcript-stream.txt", echo=False)
    capture.start()
    try:
        parent_data = Path(str(PARENT).replace(".cas.h5", ".dat.h5"))
        manifest["parent_hashes"] = {"case": sha(PARENT), "data": sha(parent_data)}
        if manifest["parent_hashes"] != SOURCE_HASHES:
            raise RuntimeError("E2.7 parent hash mismatch")
        parent_dir = work / "parent"
        parent_dir.mkdir()
        local_case = parent_dir / PARENT.name
        local_data = parent_dir / parent_data.name
        shutil.copy2(PARENT, local_case)
        shutil.copy2(parent_data, local_data)
        if sha(local_case) != SOURCE_HASHES["case"] or sha(local_data) != SOURCE_HASHES["data"]:
            raise RuntimeError("Local parent copy mismatch")
        solver.settings.file.read_case(file_name=str(local_case))
        solver.settings.file.read_data(file_name=str(local_data))
        if native_iteration(solver) != 13586:
            raise RuntimeError("Parent is not at N13586")
        manifest["parent_model_readback"] = validate_e27(solver)
        manifest["upper_film_mass_before"] = film_mass(solver)
        lower = solver.settings.setup.boundary_conditions.wall[LOWER_FILM_WALL].phase["mixture"].wall_film
        lower.eulerian_film_wall = True
        lower.film_condition_type = "film-wall-initial"
        lower.film_height.set_state({"option": "value", "value": 0.0})
        lower.enable_flow_momentum_coupling = False
        solver.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        solver.settings.file.read_data(file_name=str(local_data))
        manifest["collector_configuration"] = configure(solver)
        parameters = solver.rp_vars("wall-film/model-parameters")
        solver.rp_vars("wall-film/model-parameters", [(k, 1.0 if k == "thickness-limit" else v) for k, v in parameters])
        manifest["roughness"] = apply_roughness(solver, "R3", 5e-4, .5)
        manifest["collector_reports"] = ensure_reports(solver, str(monitor))
        manifest["coverage"] = configure_coverage(solver)
        # Add upper+lower totals so extending the film area cannot hide storage.
        root = solver.settings.solution.report_definitions.surface
        for suffix, template in {"film-mass-total": "p72a-e2.7-ewf-film-mass-total", "thickness-max": "p72a-e2.7-ewf-thickness-max"}.items():
            name = "p72a-collector-combined-" + suffix
            root.make_a_copy(from_=template, to=name)
            root[name].surface_names = ["wall", LOWER_FILM_WALL]
            files = solver.settings.solution.monitor.report_files
            # Native copying can create a report file automatically. Reuse it
            # rather than creating a second file for the same definition/path.
            file_name = name + "-rfile" if name + "-rfile" in files.get_object_names() else name
            if file_name not in files.get_object_names():
                files.create(name=file_name)
            files[file_name].report_defs = [name]
        files = solver.settings.solution.monitor.report_files
        coverage_file = "p72a-stage2-ewf-wetted-area-rfile"
        if coverage_file not in files.get_object_names():
            files.create(name=coverage_file)
        files[coverage_file].report_defs = ["p72a-stage2-ewf-wetted-area"]
        paths = {}
        for name in files.get_object_names():
            obj = files[name]
            definition = obj.report_defs()[0]
            path = monitor / f"{definition}.out"
            obj.file_name = str(path)
            obj.frequency_of = "iteration"
            obj.frequency = 1
            obj.active = True
            paths[definition] = path
        manifest["report_paths"] = paths
        manifest["residual_history"] = configure_residual_history(solver, 3001)
        manifest["autosave"] = configure_autosave(solver, str(work), data_frequency=1000)
        if abs(film_mass(solver) - manifest["upper_film_mass_before"]) > 1e-8:
            raise RuntimeError("Preparation changed the inherited upper film mass")
        manifest["prepared_pair"] = save_pair(solver, work / "prepared-N13586.cas.h5", 13586)
        dump(manifest_path, manifest)
        solver.settings.file.read_case(file_name=manifest["prepared_pair"]["case"])
        solver.settings.file.read_data(file_name=manifest["prepared_pair"]["data"])
        if native_iteration(solver) != 13586:
            solver.settings.file.read_data(file_name=str(local_data))
        if native_iteration(solver) != 13586:
            raise RuntimeError("Prepared child lost its starting coordinate")
        manifest["prepared_reopen"] = {"collector": readback(solver), "roughness": validate_roughness(solver), "e27": validate_e27(solver, max_thickness=1.0)}
        if abs(film_mass(solver) - manifest["upper_film_mass_before"]) > 1e-8:
            raise RuntimeError("Reopen changed the upper film mass")
        manifest["status"] = "RUNNING"
        dump(manifest_path, manifest)
        print(f"RUNNING: local R3+E2.7 new absorber, N13586 -> N16586. Manifest: {manifest_path}", flush=True)
        for block in range(1, 4):
            solver.tui.solve.iterate(1000)
            capture.wait_until_quiet(quiet_seconds=.25, timeout_seconds=5)
            history = file_history(paths["p72a-e2.7-ewf-thickness-max"])
            coordinate = history["iterations"][-1]
            if coordinate != 13586 + 1000 * block:
                raise RuntimeError(f"Block {block} stopped at native report N{coordinate}")
            checkpoint = save_pair(solver, work / f"block{block}-N{coordinate}.cas.h5", coordinate)
            checkpoint["expression_iteration"] = native_iteration(solver)
            checkpoint["collector"] = readback(solver)
            manifest["completed_blocks"].append(checkpoint)
            dump(manifest_path, manifest)
            print(f"CHECKPOINT VERIFIED: N{coordinate} ({block}/3 blocks)", flush=True)
        histories = {name: file_history(path) for name, path in paths.items()}
        for name, history in histories.items():
            if history["iterations"][-1] != 16586 or history["points"] < 3000:
                raise RuntimeError(f"Incomplete native report history: {name}")
        dump(out / "report-histories.json", histories)
        manifest["final_pair"] = save_pair(solver, work / "final-N16586.cas.h5", 16586)
        solver.settings.file.read_case(file_name=manifest["final_pair"]["case"])
        solver.settings.file.read_data(file_name=manifest["final_pair"]["data"])
        manifest["final_reopen"] = {"collector": readback(solver), "roughness": validate_roughness(solver), "e27": validate_e27(solver, max_thickness=1.0), "expression_iteration": native_iteration(solver)}
        manifest["native_terminal_iteration"] = 16586
        manifest["report_history_points"] = {k: v["points"] for k, v in histories.items()}
        manifest["status"] = "COMPLETE"
        manifest["finished_utc"] = datetime.now(timezone.utc).isoformat()
        dump(manifest_path, manifest)
        print(f"COMPLETE: 3000 native iterations and final pair reopened. Manifest: {manifest_path}", flush=True)
        return manifest
    except Exception as exc:
        manifest.update(status="IMPLEMENTATION_OR_RUN_FAILURE", error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc())
        dump(manifest_path, manifest)
        raise
    finally:
        capture.close()


def continue_repaired_local_r3(solver, stamp):
    """Continue the zero-iteration child after fixing only report duplication."""
    work = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\FluentDirectUse") / "Phase72A-R3-E27-NewAbsorber" / stamp
    out = ROOT / "output/phase72a-r3-ewf-absorber-direct" / stamp
    manifest_path = out / "run-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if manifest["status"] != "IMPLEMENTATION_OR_RUN_FAILURE" or manifest["completed_blocks"] or native_iteration(solver) != 13586:
        raise RuntimeError("This recovery requires the unchanged, zero-iteration child")
    shutil.copy2(manifest_path, out / "initial-setup-failure.json")
    manifest["initial_setup_error"] = manifest.pop("error")
    manifest["initial_setup_traceback"] = manifest.pop("traceback")
    manifest["repair"] = "Removed the two redundant combined-film report files; no solver/model change or iterations consumed"
    paths = {}
    seen = set()
    files = solver.settings.solution.monitor.report_files
    for name in files.get_object_names():
        obj = files[name]
        path = obj.file_name()
        if path in seen or not obj.active() or obj.frequency() != 1:
            raise RuntimeError("Report mapping remains duplicate/inactive")
        seen.add(path)
        paths[obj.report_defs()[0]] = Path(path)
    manifest["report_paths"] = paths
    manifest["prepared_pair_repaired"] = save_pair(solver, work / "run-input-N13586.cas.h5", 13586)
    solver.settings.file.read_case(file_name=manifest["prepared_pair_repaired"]["case"])
    solver.settings.file.read_data(file_name=manifest["prepared_pair_repaired"]["data"])
    if native_iteration(solver) != 13586:
        solver.settings.file.read_data(file_name=str(work / "parent" / PARENT.name.replace(".cas.h5", ".dat.h5")))
    if native_iteration(solver) != 13586 or abs(film_mass(solver) - manifest["upper_film_mass_before"]) > 1e-8:
        raise RuntimeError("Recovery changed the parent coordinate/inventory")
    manifest["repaired_reopen"] = {"collector": readback(solver), "roughness": validate_roughness(solver), "e27": validate_e27(solver, max_thickness=1.0)}
    capture = SessionTranscriptCapture(solver, stream_path=out / "transcript-repaired-solve.txt", echo=False)
    capture.start()
    try:
        manifest["status"] = "RUNNING"
        dump(manifest_path, manifest)
        print("RUNNING REPAIRED LOCAL CHILD: N13586 -> N16586", flush=True)
        for block in range(1, 4):
            solver.tui.solve.iterate(1000)
            capture.wait_until_quiet(quiet_seconds=.25, timeout_seconds=5)
            coordinate = file_history(paths["p72a-e2.7-ewf-thickness-max"])["iterations"][-1]
            if coordinate != 13586 + 1000 * block:
                raise RuntimeError(f"Block {block} stopped at native report N{coordinate}")
            checkpoint = save_pair(solver, work / f"block{block}-N{coordinate}.cas.h5", coordinate)
            checkpoint["expression_iteration"] = native_iteration(solver)
            checkpoint["collector"] = readback(solver)
            manifest["completed_blocks"].append(checkpoint)
            dump(manifest_path, manifest)
            print(f"CHECKPOINT VERIFIED: N{coordinate} ({block}/3)", flush=True)
        histories = {name: file_history(path) for name, path in paths.items()}
        if any(h["points"] < 3000 or h["iterations"][-1] != 16586 for h in histories.values()):
            raise RuntimeError("Native report histories are incomplete")
        dump(out / "report-histories.json", histories)
        manifest["final_pair"] = save_pair(solver, work / "final-N16586.cas.h5", 16586)
        solver.settings.file.read_case(file_name=manifest["final_pair"]["case"])
        solver.settings.file.read_data(file_name=manifest["final_pair"]["data"])
        manifest["final_reopen"] = {"collector": readback(solver), "roughness": validate_roughness(solver), "e27": validate_e27(solver, max_thickness=1.0), "expression_iteration": native_iteration(solver)}
        manifest.update(status="COMPLETE", native_terminal_iteration=16586,
                        report_history_points={k: v["points"] for k, v in histories.items()},
                        finished_utc=datetime.now(timezone.utc).isoformat())
        dump(manifest_path, manifest)
        print("COMPLETE: 3000 native iterations; final pair saved/reopened", flush=True)
        return manifest
    except Exception as exc:
        manifest.update(status="IMPLEMENTATION_OR_RUN_FAILURE", error=str(exc), traceback=traceback.format_exc())
        dump(manifest_path, manifest)
        raise
    finally:
        capture.close()

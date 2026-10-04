#!/usr/bin/env python3
"""Paired, isolated native film-source check, restoring the prepared separator."""
from __future__ import annotations

import argparse
import math
import re
from pathlib import Path, PureWindowsPath
import sys
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts/setup")]
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.ewf_absorber import LOWER_FILM_WALL, readback
from pyansys_fluent.ewf_reports import ensure_surface_report
from pyansys_fluent.ewf_report_specs import REPORT_SPECS
from pyansys_fluent.stage4_native import ensure_remote_directory
from run_phase72a_e27_server1_continuation import dump, pair_save, native_iteration
from run_phase72a_ewf_absorber import film_mass
import json


def qualify_saved_check(source_path: Path) -> Path:
    """Recover clock instrumentation only from complete native mass evidence."""
    record = json.loads(source_path.read_text())
    if record["status"] != "PROOF_FAILED" or "division by zero" not in record.get("error", ""):
        raise RuntimeError("Only a complete check with the stale-clock error can be recovered")
    if record.get("restored_native_iteration") != 13586 or abs(record["restored_upper_film_mass_kg"] - 5.842478445133369) > 1e-8:
        raise RuntimeError("Production restoration was not verified")
    transcript_path = source_path.parent / "transcript.txt"
    clocks = re.findall(r"Film time\s*=\s*([\d.eE+-]+)\s+with timestep\s*=\s*([\d.eE+-]+)", transcript_path.read_text())
    if len(clocks) != 20:
        raise RuntimeError(f"Expected exactly 20 native film updates; found {len(clocks)}")
    for index, arm in enumerate(("source_off", "source_on")):
        samples = record["arms"][arm]
        if len(samples) != 11:
            raise RuntimeError("Incomplete native mass arm")
        samples[0]["film_elapsed_time_s"] = 0.0
        for sample, (clock, dt) in zip(samples[1:], clocks[index * 10:(index + 1) * 10]):
            if not math.isclose(float(dt), 1e-5, rel_tol=1e-8):
                raise RuntimeError("Unexpected printed film timestep")
            sample["rp_film_elapsed_time_s"] = sample["film_elapsed_time_s"]
            sample["film_elapsed_time_s"] = float(clock)
    off, on = record["arms"]["source_off"], record["arms"]["source_on"]
    off_change = off[-1]["native_film_mass_kg"] - off[0]["native_film_mass_kg"]
    removed = on[0]["native_film_mass_kg"] - on[-1]["native_film_mass_kg"]
    fractions, errors, steps = [], [], []
    for a, b in zip(on, on[1:]):
        loss = a["native_film_mass_kg"] - b["native_film_mass_kg"]
        dt = b["film_elapsed_time_s"] - a["film_elapsed_time_s"]
        fractions.append(loss / a["native_film_mass_kg"])
        errors.append(loss / (a["collector"]["P71V3FilmRemoval"] * dt) - 1)
        steps.append(dt / 1e-5)
    if not math.isclose(off[0]["native_film_mass_kg"], on[0]["native_film_mass_kg"], rel_tol=1e-8):
        raise RuntimeError("Unequal starting native masses")
    if abs(off_change) > off[0]["native_film_mass_kg"] * 1e-5 or removed <= 0 or min(fractions) < 0 or max(fractions) > 0.0101 or max(abs(e) for e in errors) > 0.03 or any(not math.isclose(n, 1, abs_tol=1e-8) for n in steps):
        raise RuntimeError("Native source accounting/bounded depletion was not verified")
    record.update(status="SOURCE_REMOVAL_VERIFIED", original_implementation_error=record.pop("error"),
        original_implementation_traceback=record.pop("traceback"),
        raw_proof=str(source_path), clock_basis="Fluent printed film time; RP clock remained stale at zero",
        off_change_kg=off_change, on_removed_kg=removed,
        source_on_loss_fractions_per_bulk_iteration=fractions, source_integral_relative_errors=errors,
        physical_film_steps_per_bulk_iteration=steps)
    destination = source_path.parent / "source-proof-qualified.json"
    dump(destination, record)
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--build-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    build = json.loads(args.build_manifest.read_text())
    if build["status"] != "PREPARED_REOPEN_VERIFIED":
        raise RuntimeError("A saved/reopened prepared collector is required")
    prepared = build["prepared_pair"]
    work = PureWindowsPath(build["work_root"]) / "source-proof"
    scratch = work / "scratch"
    out = args.output_root.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest_path = out / "source-proof.json"
    record = {"status": "PREPARING", "prepared_pair": prepared, "seed_height_m": 1e-4,
              "bulk_iterations_requested_per_arm": 10, "arms": {}}
    dump(manifest_path, record)
    solver = connect(args.server_id, start_transcript=False)
    capture = SessionTranscriptCapture(solver, stream_path=out / "transcript.txt", echo=False)
    capture.start()
    try:
        ensure_remote_directory(solver, str(work))
        ensure_remote_directory(solver, str(scratch))
        solver.settings.file.read_case(file_name=prepared["case"])
        solver.settings.file.read_data(file_name=prepared["data"])
        monitor = PureWindowsPath(build["work_root"]) / "monitors"
        for name in solver.settings.solution.monitor.report_files.get_object_names():
            item = solver.settings.solution.monitor.report_files[name]
            item.file_name = str(monitor / f"{name}.out")
            item.frequency = 1
            item.active = True
        prepared = pair_save(solver, work / "production-prepared.cas.h5", scratch, scratch_tag="production")
        record["production_pair"] = prepared
        dump(manifest_path, record)
        parameters = dict(solver.rp_vars("wall-film/model-parameters"))
        record["original_parameters"] = parameters
        dump(manifest_path, record)
        # Preserve the production coupled solver. Zero initial velocity and
        # disabled film forcing suppress edge transport in this source test.
        changes = {"secondary-phase-mode": 0, "mom-gravity?": False, "mom-aero-drive?": False, "mom-wall-visc?": False}
        if any(key not in parameters for key in changes):
            raise RuntimeError("Isolated no-forcing film controls are unavailable")
        solver.rp_vars("wall-film/model-parameters", [(k, changes.get(k, v)) for k, v in parameters.items()])
        walls = solver.settings.setup.boundary_conditions.wall
        upper = walls["wall"].phase["mixture"].wall_film
        upper.film_condition_type = "film-wall-initial"
        upper.film_height.set_state({"option": "value", "value": 0.0})
        lower = walls[LOWER_FILM_WALL].phase["mixture"].wall_film
        lower.film_height.set_state({"option": "value", "value": 1e-4})
        # Initialization is confined to this disposable fixture. All production
        # bulk/upper-film data remain in the hash-recorded prepared pair.
        solver.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
        record["fixture_parameters"] = dict(solver.rp_vars("wall-film/model-parameters"))
        for key, value in changes.items():
            if record["fixture_parameters"].get(key) != value:
                raise RuntimeError(f"Fixture control did not persist: {key}")
        report = ensure_surface_report(solver, next(s for s in REPORT_SPECS if s.key == "film_mass_total"),
            prefix="p72a-collector-proof-lower", surfaces=[LOWER_FILM_WALL], object_policy="replace",
            create_history_file=False, frequency=1)
        report_name = report["name"]
        record["lower_mass_report"] = report
        # Disable bulk equation advancement to exclude accretion and transport.
        equations = solver.settings.solution.controls.equations
        record["bulk_equations_before"] = equations.get_state()
        for name in equations.get_object_names():
            equations[name] = False
        record["bulk_equations_fixture"] = equations.get_state()
        for name in solver.settings.solution.monitor.report_files.get_object_names():
            solver.settings.solution.monitor.report_files[name].active = False
        fixture = pair_save(solver, work / "seed.cas.h5", scratch, scratch_tag="seed")
        record["seed_pair"] = fixture
        dump(manifest_path, record)

        def snapshot():
            native = solver.settings.solution.report_definitions.compute(report_defs=[report_name])
            values = readback(solver)["values"]
            native_mass = float(native[0][report_name][0])
            if not math.isclose(native_mass, values["P71V3FilmInventory"], rel_tol=1e-5, abs_tol=1e-10):
                raise RuntimeError("Native mass and density-integrated thickness disagree")
            return {"native_film_mass_kg": native_mass, "collector": values,
                    "film_elapsed_time_s": float(dict(solver.rp_vars("wall-film/solution-state"))["film_elapsed_time"])}

        for arm, enabled in (("source_off", False), ("source_on", True)):
            solver.settings.file.read_case(file_name=fixture["case"])
            solver.settings.file.read_data(file_name=fixture["data"])
            solver.settings.setup.boundary_conditions.wall[LOWER_FILM_WALL].phase["mixture"].wall_film.enable_film_source_terms = enabled
            # Mass-hook readback is asserted separately for the source-on arm.
            if not enabled:
                # readback requires enabled hooks; sample the identical fields
                # through the native report and inventory expression directly.
                def snap_off():
                    native = solver.settings.solution.report_definitions.compute(report_defs=[report_name])
                    return {"native_film_mass_kg": float(native[0][report_name][0]),
                            "film_inventory_kg": float(solver.settings.setup.named_expressions["P71V3FilmInventory"].get_value()),
                            "film_elapsed_time_s": float(dict(solver.rp_vars("wall-film/solution-state"))["film_elapsed_time"])}
                sample = snap_off
            else:
                sample = snapshot
            snapshots = [sample()]
            record["arms"][arm] = snapshots
            dump(manifest_path, record)
            for _ in range(10):
                marker = capture.mark()
                solver.settings.solution.run_calculation.iterate(iter_count=1)
                observed = sample()
                capture.wait_until_quiet(quiet_seconds=0.1, timeout_seconds=5)
                clocks = re.findall(r"Film time\s*=\s*([\d.eE+-]+)\s+with timestep", capture.text_since(marker))
                if not clocks:
                    raise RuntimeError("No native printed film clock for this update")
                observed["rp_film_elapsed_time_s"] = observed["film_elapsed_time_s"]
                observed["film_elapsed_time_s"] = float(clocks[-1])
                snapshots.append(observed)
                dump(manifest_path, record)
        off = record["arms"]["source_off"]
        on = record["arms"]["source_on"]
        if not math.isclose(off[0]["native_film_mass_kg"], on[0]["native_film_mass_kg"], rel_tol=1e-8):
            raise RuntimeError("Paired arms did not start from identical native inventory")
        off_change = off[-1]["native_film_mass_kg"] - off[0]["native_film_mass_kg"]
        removed = on[0]["native_film_mass_kg"] - on[-1]["native_film_mass_kg"]
        if abs(off_change) > off[0]["native_film_mass_kg"] * 1e-5 or removed <= on[0]["native_film_mass_kg"] * 1e-4:
            raise RuntimeError("Source-off stability or source-on removal was not demonstrated")
        if any(s["native_film_mass_kg"] < 0 for s in on):
            raise RuntimeError("Negative film mass in source proof")
        step_losses = [(a["native_film_mass_kg"] - b["native_film_mass_kg"]) / a["native_film_mass_kg"] for a, b in zip(on, on[1:])]
        record["source_on_loss_fractions_per_bulk_iteration"] = step_losses
        record["physical_film_steps_per_bulk_iteration"] = [(b["film_elapsed_time_s"]-a["film_elapsed_time_s"])/parameters["timestep-max"] for a, b in zip(on, on[1:])]
        record["source_integral_relative_errors"] = [
            ((a["native_film_mass_kg"]-b["native_film_mass_kg"]) /
             (a["collector"]["P71V3FilmRemoval"] * (b["film_elapsed_time_s"]-a["film_elapsed_time_s"]))) - 1
            for a, b in zip(on, on[1:])]
        if max(step_losses) > 0.1001 or min(step_losses) < -1e-6:
            raise RuntimeError("Per-update film depletion bound was not demonstrated")
        if max(record["physical_film_steps_per_bulk_iteration"]) > int(parameters["film-per-flow-iters"]) + 1e-5:
            raise RuntimeError("Actual film advance exceeds the conservative update span")
        if max(abs(x) for x in record["source_integral_relative_errors"]) > 0.03:
            raise RuntimeError("Native loss does not match the source-integrated film time")
        record["off_change_kg"] = off_change
        record["on_removed_kg"] = removed
        record["status"] = "SOURCE_REMOVAL_PROVED_PENDING_RESTORE"
    except Exception as exc:
        record.update(status="PROOF_FAILED", error=str(exc), traceback=traceback.format_exc())
        raise
    finally:
        try:
            solver.settings.file.read_case(file_name=prepared["case"])
            solver.settings.file.read_data(file_name=prepared["data"])
            record["restored_production"] = readback(solver)
            record["restored_upper_film_mass_kg"] = film_mass(solver)
            record["restored_native_iteration"] = native_iteration(solver)
            if abs(record["restored_upper_film_mass_kg"] - build["upper_film_mass_before"]) > 1e-8:
                raise RuntimeError("Restored upper film inventory differs from the parent")
            if record["restored_native_iteration"] != 13586:
                raise RuntimeError("Restored parent coordinate differs")
            if record["status"] == "SOURCE_REMOVAL_PROVED_PENDING_RESTORE":
                record["status"] = "SOURCE_REMOVAL_VERIFIED"
        except Exception as exc:
            record.update(status="RESTORATION_FAILED", restoration_error=str(exc))
            raise
        finally:
            capture.close()
            dump(manifest_path, record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

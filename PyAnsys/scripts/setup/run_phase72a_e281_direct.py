#!/usr/bin/env python3
"""Build and run the Phase 7.2A E2.81 fast-time EWF child in a live solver REPL.

The caller must launch the pinned HOME-DESKTOP-SH Fluent 2025 R2 session using
the direct-fluent-use skill, then call ``run_e281(solver)`` in that same Python
process. This module never exits or replaces the Fluent session.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path, PureWindowsPath
import re
import shutil
import sys
import time
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [
    str(ROOT / "PyAnsys" / "src"),
    str(ROOT / "PyAnsys" / "scripts" / "inspection"),
]

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.ewf_report_specs import REPORT_SPECS, ReportSpec  # noqa: E402
from pyansys_fluent.ewf_reports import ensure_surface_report  # noqa: E402
from pyansys_fluent.stage4_native import configure_residual_history  # noqa: E402


PARENT_CASE = Path(
    r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\parent-transfer-20260922T115133Z\P71A-R0-SMOOTH-CONTROL-COUPLED-GLOBAL-TIME-PLUS1000-full-loading-plus1000.cas.h5"
)
PARENT_DATA = Path(str(PARENT_CASE).replace(".cas.h5", ".dat.h5"))
PARENT_CASE_SHA256 = "4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc"
PARENT_DATA_SHA256 = "b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72"
PARENT_ITERATION = 5586
HORIZON = 3000
BATCHES = [1000, 500, 100, 10, 10, 10, 10, 25, 25, 50, 50, 50, 50, 250, 250, 250, 250, 110]
FILM_MATERIAL = "water-liquid-at-psep"
EXPECTED_WALL_AREA_M2 = 53.4369522992766
EWF_REPORT_KEYS = {
    "film_courant_max",
    "film_mass_total",
    "film_thickness_max",
    "film_thickness_area_average",
    "film_outflow_mass_total",
    "film_velocity_area_average",
    "film_velocity_max",
    "film_x_velocity_area_average",
    "film_y_velocity_area_average",
    "film_z_velocity_area_average",
    "film_secondary_phase_mass_total",
    "film_secondary_phase_collection_area_average",
}
UNAVAILABLE_EWF_REPORT_KEYS = {
    "film_dpm_mass_source_total": "film-dpm-mass-source is not an allowed surface-report field in this Fluent 2025 R2 case",
    "film_stripped_mass_total": "film-stripped-mass is not an allowed surface-report field in this Fluent 2025 R2 case",
    "film_separated_mass_total": "film-separated-mass is not an allowed surface-report field in this Fluent 2025 R2 case",
}
ADDITIONAL_EWF_REPORT_SPECS = (
    ReportSpec("film_surface_velocity_area_average", "surface-velocity-mag-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-surface-velocity-mag",), (("film", "surface", "velocity", "mag"),), "m/s"),
    ReportSpec("film_surface_velocity_max", "surface-velocity-mag-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-surface-velocity-mag",), (("film", "surface", "velocity", "mag"),), "m/s"),
    ReportSpec("film_surface_x_velocity_area_average", "surface-x-velocity-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-surface-x-velocity",), (("film", "surface", "x", "velocity"),), "m/s"),
    ReportSpec("film_surface_y_velocity_area_average", "surface-y-velocity-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-surface-y-velocity",), (("film", "surface", "y", "velocity"),), "m/s"),
    ReportSpec("film_surface_z_velocity_area_average", "surface-z-velocity-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-surface-z-velocity",), (("film", "surface", "z", "velocity"),), "m/s"),
    ReportSpec("film_effective_pressure_area_average", "effective-pressure-awavg", ("surface-areaavg", "area-weighted-average"), (("area", "avg"), ("area", "weighted", "average")), ("film-effective-pressure",), (("film", "effective", "pressure"),), "Pa"),
    ReportSpec("film_effective_pressure_max", "effective-pressure-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-effective-pressure",), (("film", "effective", "pressure"),), "Pa"),
    ReportSpec("film_weber_number_max", "weber-number-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-weber-number",), (("film", "weber", "number"),), "dimensionless"),
    ReportSpec("film_strip_weber_number_max", "strip-weber-number-max", ("surface-facetmax", "facet-maximum", "facet-max"), (("facet", "max"),), ("film-strip-weber-number",), (("film", "strip", "weber", "number"),), "dimensionless"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, default=str, allow_nan=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def native_iteration(solver: Any) -> int:
    value = float(
        solver.settings.setup.named_expressions["P71V2Iteration"].get_value()
    )
    require(math.isfinite(value), f"nonfinite native iteration expression: {value!r}")
    return int(round(value))


def film_solution_state(solver: Any) -> dict[str, Any]:
    value = solver.rp_vars().get("wall-film/solution-state")
    require(isinstance(value, (list, tuple)), f"EWF solution state is unavailable: {value!r}")
    return dict(value)


def data_path(case_path: Path) -> Path:
    require(str(case_path).endswith(".cas.h5"), f"unexpected Fluent case path: {case_path}")
    return Path(str(case_path).replace(".cas.h5", ".dat.h5"))


def save_pair(solver: Any, case_path: Path) -> dict[str, Any]:
    case_path.parent.mkdir(parents=True, exist_ok=True)
    data = data_path(case_path)
    require(not case_path.exists(), f"refusing to overwrite case: {case_path}")
    require(not data.exists(), f"refusing to overwrite data: {data}")
    solver.settings.file.write_case(file_name=str(case_path))
    solver.settings.file.write_data(file_name=str(data))
    require(case_path.is_file() and case_path.stat().st_size > 0, f"case save missing: {case_path}")
    require(data.is_file() and data.stat().st_size > 0, f"data save missing: {data}")
    return {
        "case": str(case_path),
        "data": str(data),
        "native_iteration": native_iteration(solver),
        "case_sha256": sha256(case_path),
        "data_sha256": sha256(data),
        "case_bytes": case_path.stat().st_size,
        "data_bytes": data.stat().st_size,
    }


def copy_saved_pair(
    solver: Any,
    source_pair: dict[str, Any],
    destination_case_path: Path,
) -> dict[str, Any]:
    """Copy a saved local pair so local and shared endpoints are byte-identical."""
    require(
        native_iteration(solver) == int(source_pair["native_iteration"]),
        "solver moved after the source pair was saved",
    )
    destination_case_path.parent.mkdir(parents=True, exist_ok=True)
    destination_data_path = data_path(destination_case_path)
    require(not destination_case_path.exists(), f"refusing to overwrite case: {destination_case_path}")
    require(not destination_data_path.exists(), f"refusing to overwrite data: {destination_data_path}")
    shutil.copy2(source_pair["case"], destination_case_path)
    shutil.copy2(source_pair["data"], destination_data_path)
    copied = {
        "case": str(destination_case_path),
        "data": str(destination_data_path),
        "native_iteration": int(source_pair["native_iteration"]),
        "case_sha256": sha256(destination_case_path),
        "data_sha256": sha256(destination_data_path),
        "case_bytes": destination_case_path.stat().st_size,
        "data_bytes": destination_data_path.stat().st_size,
    }
    require(copied["case_sha256"] == source_pair["case_sha256"], "copied case hash differs from local source")
    require(copied["data_sha256"] == source_pair["data_sha256"], "copied data hash differs from local source")
    return copied


def create_report_file(
    solver: Any,
    *,
    definition: str,
    monitor_root: Path,
) -> str:
    files = solver.settings.solution.monitor.report_files
    name = f"{definition}-rfile"
    existing = {str(item) for item in files.get_object_names()}
    require(name not in existing, f"report file already exists: {name}")
    path = monitor_root / f"{definition}.out"
    report_file = files.create(name=name)
    report_file.set_state(
        {
            "file_name": str(path),
            "report_defs": [definition],
            "frequency_of": "iteration",
            "frequency": 1,
            "active": True,
            "print": False,
            "write_instantaneous_values": False,
        }
    )
    state = report_file.get_state()
    require(state.get("active") is True, f"report file is inactive: {name}: {state}")
    require(int(state.get("frequency", 0)) == 1, f"report file cadence mismatch: {name}: {state}")
    require(state.get("report_defs") == [definition], f"report definition mismatch: {name}: {state}")
    require(Path(str(state.get("file_name", ""))) == path, f"report path mismatch: {name}: {state}")
    return str(path)


def configure_fast_ewf(solver: Any) -> dict[str, Any]:
    ewf = solver.tui.define.models.eulerian_wallfilm
    ewf.enable_wallfilm_model("yes")
    solver.execute_tui(
        "/define/models/eulerian-wallfilm/film-material yes "
        f'"{FILM_MATERIAL}"\n'
    )
    ewf = solver.tui.define.models.eulerian_wallfilm
    parameters = solver.rp_vars().get("wall-film/model-parameters")
    require(isinstance(parameters, list), "EWF model parameters are unavailable")
    previous = dict(parameters)
    expected = {
        "solve-momentum?": True,
        "mom-equation?": True,
        "mom-gravity?": True,
        "mom-aero-drive?": True,
        "mom-pressure?": False,
        "solve-energy?": False,
        "solve-scalar?": False,
        "dpm-collection?": False,
        "dpm-splashing?": False,
        "film-stripping?": False,
        "film-separation?": False,
        "secondary-phase-mode": 1,
        "film-vof-coupling?": False,
        "time-scheme": 2,
        "mass-scheme": 0,
        "mom-scheme": 0,
        "thickness-limit": 0.3,
        "film-coupled-solution?": True,
        "ewf-adaptive?": True,
        "courant-number": 0.4,
        "adapt-init-dt": 1e-4,
        "adapt-tstp-inc": 1.5,
        "adapt-tstp-dec": 2.0,
        "timestep-max": 1e-5,
        "sub-iter-stop": 5e-4,
        "sub-iter-nums": 4,
        "sub-iter-interval": 1,
        "film-message?": True,
    }
    missing = set(expected) - set(previous)
    require(not missing, f"Fluent 2025 R2 is missing EWF controls: {sorted(missing)}")
    changed = [(key, expected.get(str(key), value)) for key, value in parameters]
    solver.rp_vars("wall-film/model-parameters", changed)
    actual = dict(solver.rp_vars().get("wall-film/model-parameters"))
    for key, target in expected.items():
        value = actual.get(key)
        if isinstance(target, float):
            require(
                value is not None and abs(float(value) - target) <= max(1e-12, abs(target) * 1e-9),
                f"EWF control {key} mismatch: expected {target!r}, got {value!r}",
            )
        else:
            require(value == target, f"EWF control {key} mismatch: expected {target!r}, got {value!r}")

    ewf.solve_wallfilm_equation("yes")
    wall = solver.settings.setup.boundary_conditions.wall
    film_wall = wall["wall"].phase["mixture"].wall_film
    film_wall.eulerian_film_wall = True
    film_wall = wall["wall"].phase["mixture"].wall_film
    film_wall.film_condition_type = "film-wall-boundary"
    film_wall.enable_flow_momentum_coupling = False
    bottom_film = wall["bottom"].phase["mixture"].wall_film
    bottom_state = bottom_film.get_state()
    require(bottom_state.get("eulerian_film_wall") is not True, "bottom unexpectedly became a film wall")
    dpm = solver.settings.setup.models.discrete_phase.get_state()
    require(
        dpm.get("physical_models", {}).get("erosion_accretion_enabled") is False,
        "DPM erosion/accretion must remain off",
    )
    ewf.initialize_wallfilm_model()
    wall_readback = film_wall.get_state()
    require(wall_readback.get("eulerian_film_wall") is True, "EWF wall readback failed")
    require(wall_readback.get("enable_flow_momentum_coupling") is False, "flow momentum coupling is not OFF")
    return {
        "model_parameters": actual,
        "film_wall": wall_readback,
        "bottom_wall_film": bottom_state,
        "dpm_erosion_accretion_enabled": dpm.get("physical_models", {}).get("erosion_accretion_enabled"),
    }


def ensure_coverage_report(solver: Any) -> dict[str, Any]:
    name = "p72a-e2.81-ewf-wet-area"
    branch = solver.settings.solution.report_definitions.surface
    names = {str(item) for item in branch.get_object_names()}
    require(name not in names, f"coverage report already exists: {name}")
    branch.create(name=name)
    report = branch[name]
    report.report_type = "surface-integral"
    report.field = "film-coverage"
    report.surface_names = ["wall"]
    report.per_selection = False
    report.average_over = 1
    report.create_report_file = False
    report.create_report_plot = False
    state = report.get_state()
    require(state.get("report_type") == "surface-integral", f"wrong wet-area report type: {state}")
    require(state.get("field") == "film-coverage", f"wrong wet-area field: {state}")
    require(state.get("surface_names") == ["wall"], f"wrong wet-area surface: {state}")
    initial = solver.settings.solution.report_definitions.compute(report_defs=[name])
    return {"name": name, "state": state, "initial_compute": initial}


def ensure_wall_area_report(solver: Any) -> dict[str, Any]:
    name = "p72a-e2.81-ewf-wall-area-check"
    branch = solver.settings.solution.report_definitions.surface
    names = {str(item) for item in branch.get_object_names()}
    require(name not in names, f"wall-area report already exists: {name}")
    branch.create(name=name)
    report = branch[name]
    report.report_type = "surface-area"
    report.surface_names = ["wall"]
    report.per_selection = False
    report.create_report_file = False
    report.create_report_plot = False
    result = solver.settings.solution.report_definitions.compute(report_defs=[name])
    try:
        value = float(result[0][name][0])
    except Exception as exc:
        raise RuntimeError(f"Could not read native wall-area report: {result!r}") from exc
    require(
        abs(value - EXPECTED_WALL_AREA_M2) <= 1e-9,
        f"native wall area mismatch: expected {EXPECTED_WALL_AREA_M2}, got {value}",
    )
    return {"name": name, "area_m2": value, "compute": result}


def _write_run_paths(path: Path, values: dict[str, str]) -> None:
    lines = ["experiment_id: E2.81", f"run_stamp: {json.dumps(values['stamp'])}"]
    for key in (
        "parent_case",
        "parent_data",
        "local_run_root",
        "local_checkpoint_root",
        "local_output_root",
        "onedrive_root",
    ):
        lines.append(f"{key}: {json.dumps(values[key])}")
    lines.append("parent_native_iteration: 5586")
    lines.append("requested_additional_iterations: 3000")
    lines.append("requested_checkpoint_frequency: 250")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def route_report_file_outputs(solver: Any, expected_paths: dict[str, str]) -> dict[str, dict[str, str]]:
    """Reapply local paths because Fluent restores new report files as relative names."""
    files = solver.settings.solution.monitor.report_files
    restored_paths: dict[str, str] = {}
    final_paths: dict[str, str] = {}
    for object_name in files.get_object_names():
        report_file = files[str(object_name)]
        state = report_file.get_state()
        definitions = state.get("report_defs") or []
        require(len(definitions) == 1, f"report-file mapping is not one-to-one: {object_name}: {state}")
        definition = str(definitions[0])
        expected_path = expected_paths.get(definition)
        require(expected_path is not None, f"unexpected report definition: {definition}")
        restored_paths[definition] = str(state.get("file_name", ""))
        state.update(
            {
                "file_name": expected_path,
                "frequency_of": "iteration",
                "frequency": 1,
                "active": True,
            }
        )
        report_file.set_state(state)
        readback = report_file.get_state()
        require(readback.get("active") is True, f"report is inactive after path routing: {object_name}")
        require(int(readback.get("frequency", 0)) == 1, f"report frequency mismatch after path routing: {object_name}")
        actual_path = str(readback.get("file_name", ""))
        require(
            PureWindowsPath(actual_path) == PureWindowsPath(expected_path),
            f"report path routing failed: {object_name}: {readback}",
        )
        final_paths[definition] = actual_path
    require(
        set(final_paths) == set(expected_paths),
        f"report-file set mismatch after path routing: missing={set(expected_paths) - set(final_paths)}, "
        f"extra={set(final_paths) - set(expected_paths)}",
    )
    return {"restored_paths": restored_paths, "routed_paths": final_paths}


def run_prepared_e281_batches(
    solver: Any,
    manifest: dict[str, Any],
    manifest_path: Path,
) -> dict[str, Any]:
    local_root = Path(manifest["local_run_root"])
    durable_root = Path(manifest["onedrive_root"])
    output_root = Path(manifest["local_output_root"])
    report_paths = dict(manifest["report_paths"])
    transcript_path = output_root / "transcript-native-solve.txt"
    capture: SessionTranscriptCapture | None = None
    try:
        capture = SessionTranscriptCapture(
            solver,
            stream_path=local_root / "transcript-stream.txt",
            echo=False,
        ).start()
        if not transcript_path.exists():
            transcript_path.write_text("", encoding="utf-8")
        manifest["status"] = "RUNNING"
        manifest["solve_batches"] = BATCHES
        if not manifest.get("solve_started_utc"):
            manifest["solve_started_utc"] = datetime.now(timezone.utc).isoformat()
        dump(manifest_path, manifest)

        completed_batches = len(manifest.get("batches", []))
        for batch_number, requested_iterations in enumerate(BATCHES, start=1):
            if batch_number <= completed_batches:
                continue
            expected = PARENT_ITERATION + sum(BATCHES[:batch_number])
            marker = capture.mark()
            batch_started = time.perf_counter()
            print(
                f"E2.81: starting native solve batch {batch_number}/{len(BATCHES)} "
                f"({requested_iterations} iterations), target {expected}",
                flush=True,
            )
            solver.execute_tui(f"/solve/iterate {requested_iterations}\n")
            capture.wait_until_quiet(quiet_seconds=1.0, timeout_seconds=30.0)
            segment = capture.text_since(marker)
            with transcript_path.open("a", encoding="utf-8") as handle:
                handle.write(segment)
            actual = native_iteration(solver)
            batch_record = {
                "batch": batch_number,
                "requested_iterations": requested_iterations,
                "expected_native_iteration": expected,
                "actual_native_iteration": actual,
                "elapsed_wall_seconds": time.perf_counter() - batch_started,
                "ewf_solution_state": film_solution_state(solver),
                "transcript_chars": len(segment),
            }
            manifest["batches"].append(batch_record)
            manifest["last_native_iteration"] = actual
            dump(manifest_path, manifest)
            print(
                f"E2.81: batch {batch_number}/{len(BATCHES)} ended at native {actual}; "
                f"film state {batch_record['ewf_solution_state']}",
                flush=True,
            )
            if actual != expected:
                recovery = save_pair(
                    solver,
                    local_root / f"P72A-E2.81-recovery-N{actual}.cas.h5",
                )
                manifest["recovery_pair"] = recovery
                manifest["status"] = "BLOCKED_SHORT_OF_REQUESTED_HORIZON"
                dump(manifest_path, manifest)
                return manifest

            if actual == 7196:
                checkpoint = save_pair(
                    solver,
                    local_root / f"P72A-E2.81-review-N{actual}.cas.h5",
                )
                manifest["risk_window_review_pair"] = checkpoint
                manifest["status"] = "PAUSED_FOR_REVIEW"
                manifest["pause_reason"] = "staged review immediately before the E2.8 divergence window"
                dump(manifest_path, manifest)
                return manifest

        capture.wait_until_quiet(quiet_seconds=1.0, timeout_seconds=30.0)
        capture.close()
        capture = None
        transcript = transcript_path.read_text(encoding="utf-8", errors="replace")
        manifest["transcript_lines"] = len(transcript.splitlines())
        manifest["ewf_residual_rows"] = len(
            re.findall(r"\bsub-iteration:\s*\d+\s+residual\s*-\s*h:", transcript, re.I)
        )
        manifest["event_flags"] = {
            "fpe": bool(re.search(r"floating point exception|floating-point exception|\bFPE\b", transcript, re.I)),
            "amg_divergence": bool(re.search(r"AMG solver.*(?:diverg|failed|failure)|divergence detected in AMG", transcript, re.I)),
            "nonfinite": bool(re.search(r"nan|infinity|nonfinite", transcript, re.I)),
            "fatal": bool(re.search(r"fatal error|aborted|unrecoverable", transcript, re.I)),
        }
        final_iteration = native_iteration(solver)
        require(final_iteration == PARENT_ITERATION + HORIZON, "final native iteration mismatch")
        manifest["local_final_pair"] = save_pair(
            solver,
            local_root / f"P72A-E2.81-final-N{final_iteration}.cas.h5",
        )
        manifest["durable_final_pair"] = copy_saved_pair(
            solver,
            manifest["local_final_pair"],
            durable_root / f"P72A-E2.81-final-N{final_iteration}.cas.h5",
        )

        histories: dict[str, Any] = {}
        for definition, path in report_paths.items():
            require(Path(path).is_file(), f"native report output missing: {path}")
            history = parse_report_forms(read_remote_forms(solver, path))
            history.update({"definition_name": definition, "local_file": path})
            histories[definition] = history
        dump(output_root / "report-histories.json", histories)
        point_counts = {name: int(record.get("points", 0)) for name, record in histories.items()}
        manifest["report_history_points"] = point_counts
        manifest["reports_complete_each_iteration"] = all(
            count >= HORIZON + 1 for count in point_counts.values()
        )
        manifest["achieved_additional_iterations"] = HORIZON
        manifest["terminal_native_iteration"] = final_iteration
        manifest["elapsed_wall_seconds"] = sum(
            float(batch["elapsed_wall_seconds"]) for batch in manifest["batches"]
        )
        manifest["elapsed_wall_measure"] = "sum_of_per_batch_wall_seconds"
        manifest["solve_finished_utc"] = datetime.now(timezone.utc).isoformat()
        manifest["status"] = "COMPLETE" if manifest["reports_complete_each_iteration"] else "COMPLETE_WITH_REPORT_GAP"
        dump(manifest_path, manifest)
        return manifest
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        try:
            actual = native_iteration(solver)
            manifest["last_native_iteration"] = actual
            recovery_path = local_root / f"P72A-E2.81-recovery-after-run-N{actual}.cas.h5"
            if not recovery_path.exists():
                manifest["recovery_pair"] = save_pair(solver, recovery_path)
        except Exception as recovery_error:
            manifest["recovery_error"] = f"{type(recovery_error).__name__}: {recovery_error}"
        dump(manifest_path, manifest)
        raise
    finally:
        if capture is not None:
            capture.close()


def resume_prepared_e281(solver: Any, manifest_file: str | Path) -> dict[str, Any]:
    """Resume a pre-solve E2.81 stop after verifying and routing its saved pair."""
    manifest_path = Path(manifest_file)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("status") == "BLOCKED", f"expected a blocked preflight manifest: {manifest.get('status')}")
    require(
        "report path did not persist after reopen" in str(manifest.get("error", "")),
        "this resume helper is scoped to the recorded report-path reopen stop",
    )
    require(native_iteration(solver) == PARENT_ITERATION, "live resumed solver is not at native 5586")
    local_start = manifest["local_start_pair"]
    durable_start = manifest["durable_start_pair"]
    require(sha256(Path(local_start["case"])) == local_start["case_sha256"], "local start case changed")
    require(sha256(Path(local_start["data"])) == local_start["data_sha256"], "local start data changed")
    require(sha256(Path(durable_start["case"])) == durable_start["case_sha256"], "shared start case changed")
    require(sha256(Path(durable_start["data"])) == durable_start["data_sha256"], "shared start data changed")
    require(local_start["case_sha256"] == durable_start["case_sha256"], "local/shared start cases differ")
    require(local_start["data_sha256"] == durable_start["data_sha256"], "local/shared start data differ")

    saved_parameters = dict(manifest["ewf_setup_readback"]["model_parameters"])
    live_parameters = dict(solver.rp_vars().get("wall-film/model-parameters"))
    for key, expected in saved_parameters.items():
        actual = live_parameters.get(key)
        if isinstance(expected, float):
            require(
                actual is not None and abs(float(actual) - expected) <= max(1e-12, abs(expected) * 1e-9),
                f"reopened EWF parameter changed: {key}: expected {expected}, got {actual}",
            )
        else:
            require(actual == expected, f"reopened EWF parameter changed: {key}: expected {expected}, got {actual}")
    wall = solver.settings.setup.boundary_conditions.wall
    reopened_film_wall = wall["wall"].phase["mixture"].wall_film.get_state()
    require(reopened_film_wall.get("eulerian_film_wall") is True, "reopened wall is not an EWF wall")
    require(reopened_film_wall.get("enable_flow_momentum_coupling") is False, "reopened flow momentum coupling changed")
    require(native_iteration(solver) == PARENT_ITERATION, "resume setup changed native iteration")

    route_readback = route_report_file_outputs(solver, dict(manifest["report_paths"]))
    autosave = solver.settings.file.auto_save
    autosave.set_state(manifest["autosave_readback"])
    autosave_readback = autosave.get_state()
    require(int(autosave_readback.get("data_frequency", 0)) == 250, "resumed checkpoint frequency mismatch")
    require(int(autosave_readback.get("max_files", 0)) == 20, "resumed checkpoint retention mismatch")
    residual_readback = configure_residual_history(solver, HORIZON + 1)

    manifest["preflight_recovery"] = {
        "previous_error": manifest.get("error"),
        "previous_traceback": manifest.get("traceback"),
        "resume_utc": datetime.now(timezone.utc).isoformat(),
        "native_iteration": native_iteration(solver),
        "local_durable_pair_hashes_match": True,
        "ewf_setup_readback": live_parameters,
        "film_wall_readback": reopened_film_wall,
        "report_path_routing_after_reopen": route_readback,
        "autosave_readback": autosave_readback,
        "residual_history_readback": residual_readback,
    }
    manifest.pop("error", None)
    manifest.pop("traceback", None)
    manifest["start_pair_reopen_gate"] = "PASS_AFTER_POST_REOPEN_PATH_ROUTING"
    manifest["status"] = "PREPARED_RECOVERED_PREFLIGHT"
    dump(manifest_path, manifest)
    return run_prepared_e281_batches(solver, manifest, manifest_path)


def resume_e281_after_review(solver: Any, manifest_file: str | Path) -> dict[str, Any]:
    """Continue a staged E2.81 run from the preserved native-7196 pair."""
    manifest_path = Path(manifest_file)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("status") == "PAUSED_FOR_REVIEW", f"unexpected staged status: {manifest.get('status')}")
    checkpoint = manifest["risk_window_review_pair"]
    require(native_iteration(solver) == 7196, "live solver is not at the staged native-7196 checkpoint")
    require(sha256(Path(checkpoint["case"])) == checkpoint["case_sha256"], "review case hash changed")
    require(sha256(Path(checkpoint["data"])) == checkpoint["data_sha256"], "review data hash changed")
    manifest["risk_window_review"] = {
        "native_iteration": native_iteration(solver),
        "reviewed_utc": datetime.now(timezone.utc).isoformat(),
        "solver_version": str(solver.get_fluent_version()),
        "film_solution_state": film_solution_state(solver),
    }
    manifest["status"] = "PREPARED_AFTER_STAGED_REVIEW"
    dump(manifest_path, manifest)
    return run_prepared_e281_batches(solver, manifest, manifest_path)


def run_e281(solver: Any) -> dict[str, Any]:
    require("2025 R2" in str(solver.get_fluent_version()), "E2.81 requires Fluent 2025 R2")
    require(PARENT_CASE.is_file() and PARENT_DATA.is_file(), "verified E2.81 parent pair is missing")
    case_hash, data_hash = sha256(PARENT_CASE), sha256(PARENT_DATA)
    require(case_hash == PARENT_CASE_SHA256, f"parent case hash mismatch: {case_hash}")
    require(data_hash == PARENT_DATA_SHA256, f"parent data hash mismatch: {data_hash}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    local_root = Path.home() / "Documents" / "FluentRuns" / "Phase72A" / "FamilyE" / f"E2.81-fast-time-{stamp}"
    checkpoint_root = local_root / "checkpoints"
    monitor_root = local_root / "monitors"
    output_root = ROOT / "PyAnsys" / "output" / f"phase72a_ewf_direct_e281_{stamp}"
    durable_root = (
        Path.home()
        / "Documents"
        / "OneDrive - The University of Auckland"
        / "P4P-Fluent-Artifacts"
        / "Phase72A"
        / "FamilyE"
        / "E2.81"
        / stamp
    )
    for directory in (checkpoint_root, monitor_root, output_root, durable_root):
        directory.mkdir(parents=True, exist_ok=False)
    manifest_path = output_root / "run-manifest.json"
    manifest: dict[str, Any] = {
        "status": "PREFLIGHT",
        "experiment": "E2.81",
        "run_stamp_utc": stamp,
        "fluent_version": str(solver.get_fluent_version()),
        "parent": {
            "case": str(PARENT_CASE),
            "data": str(PARENT_DATA),
            "case_sha256": case_hash,
            "data_sha256": data_hash,
            "native_iteration": PARENT_ITERATION,
        },
        "local_run_root": str(local_root),
        "local_checkpoint_root": str(checkpoint_root),
        "local_monitor_root": str(monitor_root),
        "local_output_root": str(output_root),
        "onedrive_root": str(durable_root),
        "requested_additional_iterations": HORIZON,
        "tui_batch_sizes": BATCHES,
        "monitor_frequency_native_iterations": 1,
        "checkpoint_data_frequency_native_iterations": 250,
        "report_histories": {},
        "batches": [],
        "unavailable_ewf_report_fields": UNAVAILABLE_EWF_REPORT_KEYS,
    }
    dump(manifest_path, manifest)
    _write_run_paths(
        ROOT / "Project" / "experiments" / "phase-07-2a-wall-liquid-routing" / "ewf-family" / "e2.81" / "run-paths.yaml",
        {
            "stamp": stamp,
            "parent_case": str(PARENT_CASE),
            "parent_data": str(PARENT_DATA),
            "local_run_root": str(local_root),
            "local_checkpoint_root": str(checkpoint_root),
            "local_output_root": str(output_root),
            "onedrive_root": str(durable_root),
        },
    )

    capture: SessionTranscriptCapture | None = None
    try:
        print(f"E2.81: loading exact native-{PARENT_ITERATION} parent {PARENT_CASE}", flush=True)
        solver.settings.file.read_case(file_name=str(PARENT_CASE))
        solver.settings.file.read_data(file_name=str(PARENT_DATA))
        require(native_iteration(solver) == PARENT_ITERATION, "loaded parent native iteration is not 5586")
        manifest["loaded_parent_native_iteration"] = native_iteration(solver)

        manifest["ewf_setup_readback"] = configure_fast_ewf(solver)
        manifest["coverage_report"] = ensure_coverage_report(solver)
        manifest["native_wall_area_check"] = ensure_wall_area_report(solver)

        report_paths: dict[str, str] = {}
        files = solver.settings.solution.monitor.report_files
        for name in list(files.get_object_names()):
            report_file = files[str(name)]
            state = report_file.get_state()
            definitions = state.get("report_defs") or []
            require(len(definitions) == 1, f"inherited report file is not one-to-one: {name}: {state}")
            definition = str(definitions[0])
            path = monitor_root / f"{definition}.out"
            state.update(
                {
                    "file_name": str(path),
                    "frequency_of": "iteration",
                    "frequency": 1,
                    "active": True,
                }
            )
            report_file.set_state(state)
            readback = report_file.get_state()
            require(readback.get("active") is True, f"inherited report is inactive: {name}")
            require(int(readback.get("frequency", 0)) == 1, f"inherited report frequency mismatch: {name}")
            require(
                PureWindowsPath(str(readback.get("file_name", ""))) == PureWindowsPath(str(path)),
                f"inherited report path mismatch: {name}: {readback}",
            )
            report_paths[definition] = str(path)

        definitions: list[str] = []
        selected_specs = [spec for spec in REPORT_SPECS if spec.key in EWF_REPORT_KEYS]
        selected_specs.extend(ADDITIONAL_EWF_REPORT_SPECS)
        for spec in selected_specs:
            configured = ensure_surface_report(
                solver,
                spec,
                prefix="p72a-e2.81-ewf",
                surfaces=["wall"],
                object_policy="replace",
                create_history_file=False,
                frequency=1,
            )
            definitions.append(str(configured["name"]))
        require(
            len(definitions) == len(EWF_REPORT_KEYS) + len(ADDITIONAL_EWF_REPORT_SPECS),
            "E2.81 EWF report-definition set is incomplete",
        )
        coverage_name = str(manifest["coverage_report"]["name"])
        for definition in [*definitions, coverage_name]:
            report_paths[definition] = create_report_file(
                solver,
                definition=definition,
                monitor_root=monitor_root,
            )

        autosave = solver.settings.file.auto_save
        autosave_state = autosave.get_state()
        autosave_state.update(
            {
                "case_frequency": "each-time",
                "data_frequency": 250,
                "root_name": str(checkpoint_root / "checkpoint-%i"),
                "retain_most_recent_files": True,
                "max_files": 20,
                "append_file_name_with": {
                    "file_suffix_type": "time-step",
                    "file_decimal_digit": 6,
                },
            }
        )
        autosave.set_state(autosave_state)
        autosave_readback = autosave.get_state()
        require(autosave_readback.get("data_frequency") == 250, "checkpoint data frequency mismatch")
        require(autosave_readback.get("max_files") == 20, "checkpoint retention mismatch")
        manifest["autosave_readback"] = autosave_readback
        manifest["native_residual_history"] = configure_residual_history(solver, HORIZON + 1)
        manifest["report_frequency_native_iterations"] = 1
        manifest["report_definition_names"] = definitions + [coverage_name]
        manifest["unavailable_ewf_report_fields"] = UNAVAILABLE_EWF_REPORT_KEYS
        manifest["report_paths"] = report_paths
        manifest["start_film_solution_state"] = film_solution_state(solver)
        manifest["start_native_iteration_before_save"] = native_iteration(solver)
        require(native_iteration(solver) == PARENT_ITERATION, "setup changed native iteration before save")
        manifest["instrumentation_gate"] = "PASS_READBACK_ALL_REPORTS_EVERY_ITERATION_COVERAGE_AND_AUTOSAVE"

        local_start = save_pair(
            solver,
            local_root / f"P72A-E2.81-start-N{PARENT_ITERATION}.cas.h5",
        )
        # Copy the Fluent-local save. Two independent HDF5 writes of this same
        # state have different bytes; this preserves exact pair identity.
        durable_start = copy_saved_pair(
            solver,
            local_start,
            durable_root / f"P72A-E2.81-start-N{PARENT_ITERATION}.cas.h5",
        )
        require(local_start["case_sha256"] == durable_start["case_sha256"], "start case copies differ")
        require(local_start["data_sha256"] == durable_start["data_sha256"], "start data copies differ")
        manifest["local_start_pair"] = local_start
        manifest["durable_start_pair"] = durable_start

        print("E2.81: reopening the instrumented start pair for readback", flush=True)
        solver.settings.file.read_case(file_name=local_start["case"])
        solver.settings.file.read_data(file_name=local_start["data"])
        require(native_iteration(solver) == PARENT_ITERATION, "instrumented reopen changed native iteration")
        manifest["reopen_ewf_solution_state"] = film_solution_state(solver)
        manifest["report_path_routing_after_reopen"] = route_report_file_outputs(solver, report_paths)
        manifest["start_pair_reopen_gate"] = "PASS"
        manifest["status"] = "PREPARED"
        dump(manifest_path, manifest)
        return run_prepared_e281_batches(solver, manifest, manifest_path)
    except Exception as exc:
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        try:
            actual = native_iteration(solver)
            manifest["last_native_iteration"] = actual
            recovery_path = local_root / f"P72A-E2.81-recovery-N{actual}.cas.h5"
            if not recovery_path.exists():
                manifest["recovery_pair"] = save_pair(solver, recovery_path)
        except Exception as recovery_error:
            manifest["recovery_error"] = f"{type(recovery_error).__name__}: {recovery_error}"
        dump(manifest_path, manifest)
        raise
    finally:
        if capture is not None:
            capture.close()

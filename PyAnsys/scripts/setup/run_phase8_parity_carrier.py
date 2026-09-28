#!/usr/bin/env python3
"""Run a Phase 8 F1/F2 carrier point with common native reports.

Each point starts independently from its verified 26.81 m/s parity child.
Intermediate checkpoints and monitor files stay on the Fluent machine; only
the final case/data pair is copied to the Phase 8 sharing directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history
from build_phase8_purnanto_parity_pilots import (
    AREA,
    F1_CHILD,
    F2_CHILD,
    TARGET_LIQUID,
    TARGET_SPEED,
    TARGET_VAPOR,
    audit as audit_parity,
    pair,
)

RUN_ROOT = Path(r"C:\Users\Public\FluentPhase8")
FINAL_ROOT = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\PurnantoParity\Runs")
PHASES = ("mixture", "phase-1", "phase-2")
BOUNDARIES = ("liquidinlet", "steaminlet", "steamoutlet")
FLUID_ZONES = ("separator-purnanto", "p71a-v2-virtual-outlet")
FAILURE_MARKER = re.compile(r"floating point exception|Divergence detected in AMG solver|fatal error|nonfinite", re.I)
ITERATION_ROW = re.compile(r"^\s*(\d+)\s+\d+\.\d+e[+-]\d+\s+\d+\.\d+e[+-]\d+", re.I | re.M)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def save_pair(solver: Any, base: Path) -> dict[str, str]:
    case, data = pair(base)
    require(not case.exists() and not data.exists(), f"Checkpoint already exists: {base}")
    base.parent.mkdir(parents=True, exist_ok=True)
    solver.settings.file.write_case(file_name=str(case))
    solver.settings.file.write_data(file_name=str(data))
    require(case.is_file() and data.is_file(), f"Incomplete checkpoint pair: {base}")
    return {"case": str(case), "data": str(data), "case_sha256": sha256(case), "data_sha256": sha256(data)}


def load_pair(solver: Any, base: Path) -> None:
    case, data = pair(base)
    require(case.is_file() and data.is_file(), f"Missing parent pair: {base}")
    solver.settings.file.read_case(file_name=str(case))
    solver.settings.file.read_data(file_name=str(data))


def native_iteration(solver: Any) -> int:
    errors: list[str] = []
    for expression in ("(%rpgetvar 'current-iteration)", "(rpgetvar 'current-iteration)"):
        try:
            return int(solver.scheme.eval(expression))
        except Exception as exc:
            errors.append(f"{expression}: {exc}")
    raise RuntimeError("Fluent native iteration is unavailable: " + "; ".join(errors))


def set_speed(solver: Any, family: str, speed: float) -> dict[str, Any]:
    ratio = speed / TARGET_SPEED
    inlet = solver.settings.setup.boundary_conditions.mass_flow_inlet
    if family == "F1":
        area_total = sum(AREA.values())
        for zone, area in AREA.items():
            inlet[zone].phase["phase-1"].momentum.mass_flow_rate.value = TARGET_VAPOR * ratio * area / area_total
            inlet[zone].phase["phase-2"].momentum.mass_flow_rate.value = TARGET_LIQUID * ratio * area / area_total
    elif family == "F2":
        inlet["liquidinlet"].phase["phase-1"].momentum.mass_flow_rate.value = 0.0
        inlet["liquidinlet"].phase["phase-2"].momentum.mass_flow_rate.value = TARGET_LIQUID * ratio
        inlet["steaminlet"].phase["phase-1"].momentum.mass_flow_rate.value = TARGET_VAPOR * ratio
        inlet["steaminlet"].phase["phase-2"].momentum.mass_flow_rate.value = 0.0
    else:
        raise ValueError(family)
    if not math.isclose(speed, TARGET_SPEED, rel_tol=0, abs_tol=1e-10):
        solver.settings.solution.initialization.hybrid_initialize()
    readback = audit_parity(solver, exact_flows=False)
    phase_flows = readback["summed_phase_flows_kg_s"]
    require(math.isclose(phase_flows["phase-1"], TARGET_VAPOR * ratio, rel_tol=0, abs_tol=1e-5), "Vapor feed readback mismatch")
    require(math.isclose(phase_flows["phase-2"], TARGET_LIQUID * ratio, rel_tol=0, abs_tol=1e-5), "Liquid feed readback mismatch")
    if family == "F2":
        faces = readback["inlet_flows_kg_s_by_zone"]
        require(faces["liquidinlet"]["phase-1"] == 0 and faces["steaminlet"]["phase-2"] == 0, "F2 pure-phase split changed")
    return readback


def configure_reports(solver: Any, monitor_root: Path,
                      boundaries: tuple[str, ...] = BOUNDARIES) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    definitions: dict[str, dict[str, Any]] = {}
    reports = solver.settings.solution.report_definitions
    flux = reports.flux
    for phase in PHASES:
        for boundary in boundaries:
            name = f"p8-flux-{phase.replace('-', '')}-{boundary}"
            require(name not in flux.get_object_names(), f"Inherited Phase 8 report: {name}")
            flux.create(name=name)
            report = flux[name]
            report.report_type = "flux-massflow"
            report = flux[name]
            report.boundaries = [boundary]
            report.phase = phase
            report.per_selection = False
            report.average_over = 1
            report.create_report_file = False
            report.create_report_plot = False
            state = safe_get_state(report, name)
            require(state.get("report_type") == "flux-massflow" and state.get("phase") == phase and state.get("boundaries") == [boundary], f"Flux definition failed: {name}: {state}")
            definitions[name] = {"kind": "flux-massflow", "phase": phase, "boundary": boundary, "units": "kg/s", "fluent_sign": "positive into domain", "state": state}

    volume = reports.volume
    volume_specs = (
        ("p8-mass-phase1-total", "volume-mass", None, list(FLUID_ZONES), "phase-1", "kg"),
        ("p8-mass-phase2-total", "volume-mass", None, list(FLUID_ZONES), "phase-2", "kg"),
        ("p8-mass-phase2-lower", "volume-mass", None, [FLUID_ZONES[1]], "phase-2", "kg"),
        ("p8-volume-phase2-total", "volume-integral", "phase-2-vof", list(FLUID_ZONES), "mixture", "m3"),
        ("p8-volume-phase2-lower", "volume-integral", "phase-2-vof", [FLUID_ZONES[1]], "mixture", "m3"),
    )
    for name, kind, field, zones, phase, units in volume_specs:
        require(name not in volume.get_object_names(), f"Inherited Phase 8 report: {name}")
        volume.create(name=name)
        report = volume[name]
        report.report_type = kind
        report = volume[name]
        report.cell_zones = zones
        if kind == "volume-mass":
            report.phase = phase
        if field is not None:
            report.field = field
        report.per_selection = False
        report.average_over = 1
        report.create_report_file = False
        report.create_report_plot = False
        state = safe_get_state(report, name)
        require(state.get("report_type") == kind and state.get("cell_zones") == zones and state.get("phase") == phase, f"Volume definition failed: {name}: {state}")
        definitions[name] = {"kind": kind, "phase": phase, "field": field, "cell_zones": zones, "units": units, "state": state}

    surface = reports.surface
    pressure_field: str | None = None
    for boundary in boundaries:
        name = f"p8-pressure-{boundary}"
        require(name not in surface.get_object_names(), f"Inherited Phase 8 report: {name}")
        surface.create(name=name)
        report = surface[name]
        report.report_type = "surface-areaavg"
        report = surface[name]
        if pressure_field is None:
            allowed = {str(value) for value in report.field.allowed_values()}
            pressure_field = next((candidate for candidate in ("pressure", "static-pressure") if candidate in allowed), None)
            require(pressure_field is not None, f"Live Fluent pressure field unavailable; names: {sorted(allowed)[:35]}")
        report.field = pressure_field
        report.surface_names = [boundary]
        report.per_surface = False
        report.average_over = 1
        report.create_report_file = False
        report.create_report_plot = False
        state = safe_get_state(report, name)
        require(state.get("report_type") == "surface-areaavg" and state.get("field") == pressure_field and state.get("surface_names") == [boundary], f"Pressure definition failed: {name}: {state}")
        definitions[name] = {"kind": "surface-areaavg", "phase": "mixture", "field": pressure_field, "surface": boundary, "units": "Pa", "state": state}

    monitor_root.mkdir(parents=True, exist_ok=True)
    report_files = solver.settings.solution.monitor.report_files
    inherited = list(report_files.get_object_names())
    if inherited:
        report_files.delete(name_list=inherited)
    paths: dict[str, str] = {}
    for definition in definitions:
        name = f"{definition}-rfile"
        output = monitor_root / f"{definition}.out"
        require(not output.exists(), f"Report file already exists: {output}")
        report_files.create(name=name)
        report_files[name].set_state({"file_name": str(output), "report_defs": [definition], "frequency": 10, "active": True})
        state = safe_get_state(report_files[name], name)
        require(state.get("report_defs") == [definition] and int(state.get("frequency", -1)) == 10 and bool(state.get("active")), f"Report file readback failed: {name}: {state}")
        paths[definition] = str(output)
    return definitions, paths


def check_reports(solver: Any, definitions: dict[str, dict[str, Any]], paths: dict[str, str]) -> None:
    branches = solver.settings.solution.report_definitions
    for name, definition in definitions.items():
        kind = definition["kind"]
        branch = branches.flux if kind == "flux-massflow" else branches.volume if kind in {"volume-mass", "volume-integral", "volume-sum"} else branches.surface
        state = safe_get_state(branch[name], f"reopened {name}")
        require(state.get("report_type") == kind, f"Report type changed after reopen: {name}")
        file_state = safe_get_state(solver.settings.solution.monitor.report_files[f"{name}-rfile"], f"reopened {name} report file")
        require(file_state.get("report_defs") == [name] and Path(str(file_state.get("file_name"))).name == Path(paths[name]).name, f"Report file changed after reopen: {name}")


def run_point(family: str, speed: float, horizon: int) -> dict[str, Any]:
    require(horizon >= 1000 and horizon % 1000 == 0, "Carrier horizon must be whole 1,000-iteration blocks")
    source = F1_CHILD if family == "F1" else F2_CHILD
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    label = f"{family}-{str(speed).replace('.', 'p')}-{stamp}"
    local = RUN_ROOT / label
    final = FINAL_ROOT / label
    manifest_path = ROOT / "output" / "phase8-carrier" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest_path.exists(), f"Run ID already exists: {label}")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    paths = {"local": str(local), "final": str(final), "monitors": str(local / "monitors"), "transcript": str(local / "transcript.txt")}
    receipt: dict[str, Any] = {"status": "RUNNING", "family": family, "speed_m_s": speed, "requested_active_iterations": horizon,
                               "source_case": str(pair(source)[0]), "source_data": str(pair(source)[1]),
                               "source_case_sha256": sha256(pair(source)[0]), "source_data_sha256": sha256(pair(source)[1]),
                               "paths": paths, "checkpoints": [], "report_cadence": 10,
                               "comparison_window_active_iterations": [horizon - 500, horizon],
                               "claim_limit": "closed-bottom discovery; steady iteration inventory slope is not physical storage rate"}
    dump(manifest_path, receipt)
    solver = None
    capture = None
    try:
        solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                               ui_mode="gui", start_timeout=240, cleanup_on_exit=True, start_transcript=True)
        receipt["fluent_version"] = str(solver.get_fluent_version())
        require("2025 R2" in receipt["fluent_version"], "Unexpected Fluent release")
        load_pair(solver, source)
        receipt["source_native_iteration"] = native_iteration(solver)
        receipt["feed_audit"] = set_speed(solver, family, speed)
        receipt["start_rp_current_iteration"] = native_iteration(solver)
        receipt["native_coordinate_note"] = "Fluent RP current-iteration can be stale; iteration rows in the transcript and report files govern active iteration counts."
        receipt["autosave_configuration"] = configure_autosave(solver, str(local), data_frequency=1000)
        definitions, report_paths = configure_reports(solver, local / "monitors")
        receipt["report_definitions"] = definitions
        receipt["report_paths"] = report_paths
        receipt["residual_configuration"] = configure_residual_history(solver, horizon + 200)
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        receipt["start_pair"] = save_pair(solver, local / "active000")
        load_pair(solver, local / "active000")
        receipt["start_reopen_audit"] = audit_parity(solver, exact_flows=False)
        check_reports(solver, definitions, report_paths)
        receipt["initial_report_compute"] = solver.settings.solution.report_definitions.compute(report_defs=list(definitions))
        require(len(receipt["initial_report_compute"]) == len(definitions), "Initial report computation incomplete")
        receipt["status"] = "READY_TO_RUN"
        dump(manifest_path, receipt)

        plan = [(50, 50), (950, 1000)] + [(1000, endpoint) for endpoint in range(2000, horizon + 1, 1000)]
        for count, endpoint in plan:
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=count)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            transcript = capture.text_since(marker)
            iteration_rows = [int(value) for value in ITERATION_ROW.findall(transcript)]
            expected_rows = set(range(endpoint - count + 1, endpoint + 1))
            require(iteration_rows and iteration_rows[-1] == endpoint and expected_rows.issubset(set(iteration_rows)),
                    f"Fluent iteration transcript incomplete at {endpoint}: last={iteration_rows[-1] if iteration_rows else None}, unique rows={len(set(iteration_rows))}")
            require(not FAILURE_MARKER.search(transcript), f"Fatal solver event in {endpoint} block")
            if endpoint == horizon:
                checkpoint = save_pair(solver, final / "final")
            else:
                checkpoint = save_pair(solver, local / f"active{endpoint:04d}")
            receipt["checkpoints"].append({"active_iteration": endpoint, "transcript_first_iteration": iteration_rows[0],
                                           "transcript_last_iteration": iteration_rows[-1], "transcript_rows": len(iteration_rows),
                                           "transcript_unique_rows": len(set(iteration_rows)), **checkpoint})
            receipt["last_valid_active_iteration"] = endpoint
            dump(manifest_path, receipt)
            if endpoint == 1000:
                missing = [name for name, path in report_paths.items() if not Path(path).is_file() or Path(path).stat().st_size == 0]
                require(not missing, f"Report instrumentation failed at first full block: {missing}")
        load_pair(solver, final / "final")
        receipt["final_reopen_audit"] = audit_parity(solver, exact_flows=False)
        check_reports(solver, definitions, report_paths)
        receipt["final_rp_current_iteration"] = native_iteration(solver)
        receipt["achieved_active_iterations"] = receipt["checkpoints"][-1]["active_iteration"]
        require(receipt["achieved_active_iterations"] == horizon, "Final pair did not reopen at requested horizon")
        receipt["report_file_bytes"] = {name: Path(path).stat().st_size for name, path in report_paths.items()}
        require(all(size > 0 for size in receipt["report_file_bytes"].values()), "One or more final report files are empty")
        receipt["status"] = "COMPLETE"
        dump(manifest_path, receipt)
        return {"manifest": str(manifest_path), "status": receipt["status"], "final_pair": receipt["checkpoints"][-1], "achieved_active_iterations": receipt["achieved_active_iterations"]}
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        dump(manifest_path, receipt)
        raise
    finally:
        if capture is not None:
            capture.close()
        if solver is not None and receipt["status"] == "COMPLETE":
            solver.exit()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=("F1", "F2"), required=True)
    parser.add_argument("--speed", type=float, default=26.81)
    parser.add_argument("--horizon", type=int, default=2000)
    args = parser.parse_args()
    result = run_point(args.family, args.speed, args.horizon)
    print(json.dumps(result, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

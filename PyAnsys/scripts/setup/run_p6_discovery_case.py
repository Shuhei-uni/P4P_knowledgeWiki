#!/usr/bin/env python3
"""Run one Phase-06 steady numerical-surrogate discovery case.

This is an attached discovery runner.  It proves the exact F11 parent,
redirects inherited report files, checks residual capture during the smoke,
then runs one 500-iteration screen and saves a matching final pair.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
import re
import sys
import time
import traceback
from collections.abc import Mapping
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import (
    configure_autosave,
    configure_residual_history,
    ensure_remote_directory,
    redirect_report_files,
)
from extract_report_plot_histories import parse_report_forms, read_remote_forms
from run_p6_s1_discovery import PARENT_CASE, PARENT_DATA, POOL_MASS_REPORT_FILES, clock, event, prove_quiescent, write_status

TARGET_KG = 200.0
P_MIN, P_MAX = 1_115_000.0, 1_137_500.0
PROXY_REPORT_FILE = "03a_stage3_inventory_y010_liquid_mass-rfile"


def data_path(case_path: str) -> str:
    if not case_path.endswith(".cas.h5"):
        raise ValueError(case_path)
    return case_path[:-7] + ".dat.h5"


def set_pressure(solver: Any, pressure: float) -> float:
    outlet = solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"]
    state = safe_get_state(outlet, "P6 discovery brine pressure")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": pressure}
    outlet.set_state(state)
    after = safe_get_state(solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"], "P6 discovery pressure readback")
    return float(after["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])


def latest_proxy(solver: Any, path: str) -> tuple[int, float]:
    history = parse_report_forms(read_remote_forms(solver, path))
    return int(history["iterations"][-1]), float(history["values"][-1])


def readback_report_paths(solver: Any, monitor_files: Mapping[str, str], monitor_root: str) -> dict[str, Any]:
    """Prove redirected report destinations after a full case/data reload."""
    reports = solver.settings.solution.monitor.report_files
    readback: dict[str, Any] = {}
    root = PureWindowsPath(monitor_root)
    for name, expected in monitor_files.items():
        state = safe_get_state(reports[name], f"P6 discovery reloaded report {name}")
        actual = state.get("file_name") if isinstance(state, Mapping) else None
        expected_name = PureWindowsPath(expected).name
        actual_path = PureWindowsPath(actual) if isinstance(actual, str) else None
        relative_ok = bool(
            actual_path is not None
            and not actual_path.is_absolute()
            and str(actual_path.parent) in (".", "")
            and actual_path.name == expected_name
        )
        if actual != expected and not relative_ok:
            raise RuntimeError(f"report path did not survive save/reopen for {name}: {actual!r} != {expected!r}")
        readback[name] = {"configured": actual, "resolved": str(root / expected_name)}
    return readback


def report_sample_counts(
    solver: Any,
    monitor_files: Mapping[str, str],
    *,
    expected_report_count: int,
    expected_samples_per_report: int,
) -> dict[str, int]:
    if len(monitor_files) != expected_report_count:
        raise RuntimeError(
            f"report package count mismatch: {len(monitor_files)} != {expected_report_count}"
        )
    counts: dict[str, int] = {}
    for name, path in monitor_files.items():
        parsed = parse_report_forms(read_remote_forms(solver, path))
        counts[name] = len(parsed.get("iterations", []))
        if counts[name] != expected_samples_per_report:
            raise RuntimeError(
                "report history sample-count mismatch: "
                f"{name} has {counts[name]}, expected {expected_samples_per_report}: {path}"
            )
    return counts


def set_vent(solver: Any, loss: float) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    baseline = safe_get_state(bc.pressure_outlet["brineoutlet"], "P6 discovery baseline pressure")
    pressure = float(baseline["phase"]["mixture"]["momentum"]["gauge_pressure"]["value"])
    bc.set_zone_type(zone_list=["brineoutlet"], new_type="outlet-vent")
    obj = bc.outlet_vent["brineoutlet"]
    state = safe_get_state(obj, "P6 discovery outlet vent")
    state["phase"]["mixture"]["momentum"]["gauge_pressure"] = {"option": "value", "value": pressure}
    obj.set_state(state)
    obj.phase["mixture"].momentum.loss_coefficient.option = "constant"
    obj.phase["mixture"].momentum.loss_coefficient.value = loss
    readback = safe_get_state(obj, "P6 discovery vent readback")
    actual = float(readback["phase"]["mixture"]["momentum"]["loss_coefficient"]["value"])
    if abs(actual - loss) > 1e-12:
        raise RuntimeError(f"vent loss readback mismatch: {actual} != {loss}")
    return readback


def set_eulerian(solver: Any, parent_phase_state: Mapping[str, Any]) -> dict[str, Any]:
    """Switch only the multiphase formulation for the capability-gated D06 lane.

    The live Settings API and the version-matched Fluent manual establish that
    ``eulerian`` is an available model value for this Fluent 2025 R2 parent.
    Reacquire the multiphase object after the dependency-sensitive model change
    and prove that the existing phase/material mapping remains intact.  The
    scientific campaign intentionally does not invent an interaction law here;
    any mandatory/default Eulerian state is recorded for downstream analysis.
    """
    multiphase = solver.settings.setup.models.multiphase
    allowed = multiphase.model.allowed_values()
    if "eulerian" not in allowed:
        raise RuntimeError(f"live Eulerian capability missing from allowed values: {allowed!r}")
    multiphase.model.set_state("eulerian")
    multiphase = solver.settings.setup.models.multiphase
    model = multiphase.model.get_state()
    phases = safe_get_state(multiphase, "P6 D06 phase mapping")
    if model != "eulerian":
        raise RuntimeError(f"Eulerian model readback mismatch: {model!r}")
    observed_phase_state = phases.get("phases", {}) if isinstance(phases, Mapping) else {}
    if observed_phase_state != parent_phase_state:
        raise RuntimeError(
            f"D06 phase/material mapping changed during Eulerian switch: "
            f"{observed_phase_state!r} != {parent_phase_state!r}"
        )
    # The D06R repair is deliberately narrow: official steady-Eulerian
    # guidance motivates Fluent's coupled pressure--velocity route, and its
    # exact 2025 R2 Settings state has been proven in a disposable save/reopen
    # child.  Do not invent an unverified pseudo-time or Courant override.
    coupling = solver.settings.solution.methods.p_v_coupling
    allowed_couplings = coupling.flow_scheme.allowed_values()
    if "Coupled" not in allowed_couplings:
        raise RuntimeError(
            "D06R required Eulerian Coupled scheme is unavailable: "
            f"{allowed_couplings!r}"
        )
    coupling.flow_scheme.set_state("Coupled")
    coupling = solver.settings.solution.methods.p_v_coupling
    coupling_state = safe_get_state(coupling, "P6 D06R coupled-scheme readback")
    if coupling_state.get("flow_scheme") != "Coupled":
        raise RuntimeError(f"D06R coupled-scheme readback mismatch: {coupling_state!r}")
    viscous = solver.settings.setup.models.viscous
    turbulence = safe_get_state(
        viscous.multiphase_turbulence,
        "P6 D06 multiphase turbulence readback",
    )
    # Fluent exposes phase-interaction as a dependency-sensitive branch.  In
    # this child it is inactive after the Eulerian switch; preserve that fact
    # explicitly rather than treating an unavailable branch as a silent pass.
    interaction_state = safe_get_state(
        multiphase.phase_interaction,
        "P6 D06 phase interaction readback",
    )
    # ``safe_get_state`` deliberately returns a capture-error mapping rather
    # than raising.  Classify that outcome explicitly: falsely calling this
    # branch ACTIVE would conceal a dependency state that matters for D06.
    if isinstance(interaction_state, Mapping) and "_capture_error" in interaction_state:
        interaction = {
            "status": "INACTIVE_OR_UNAVAILABLE",
            "error": str(interaction_state["_capture_error"]),
        }
    else:
        interaction = {"status": "ACTIVE", "state": interaction_state}
    return {
        "mode": "eulerian",
        "allowed_values": list(allowed),
        "model": model,
        "active_children": multiphase.get_active_child_names(),
        "phase_materials": observed_phase_state,
        "pressure_velocity_coupling": coupling_state,
        "multiphase_turbulence": turbulence,
        "phase_interaction": interaction,
        "state": phases,
    }


def read_eulerian_auxiliary_state(solver: Any) -> dict[str, Any]:
    """Read D06's turbulence and phase-interaction branches after reload."""
    viscous = solver.settings.setup.models.viscous
    turbulence = safe_get_state(
        viscous.multiphase_turbulence,
        "P6 D06 reloaded multiphase turbulence readback",
    )
    interaction_state = safe_get_state(
        solver.settings.setup.models.multiphase.phase_interaction,
        "P6 D06 reloaded phase interaction readback",
    )
    if isinstance(interaction_state, Mapping) and "_capture_error" in interaction_state:
        interaction = {
            "status": "INACTIVE_OR_UNAVAILABLE",
            "error": str(interaction_state["_capture_error"]),
        }
    else:
        interaction = {"status": "ACTIVE", "state": interaction_state}
    return {
        "multiphase_turbulence": turbulence,
        "phase_interaction": interaction,
        "pressure_velocity_coupling": safe_get_state(
            solver.settings.solution.methods.p_v_coupling,
            "P6 D06R reloaded coupled-scheme readback",
        ),
    }


def parse_native_residual_transcript(text: str) -> dict[str, Any]:
    """Parse Fluent's printed residual rows captured by the PyFluent transcript.

    Fluent 2025 R2 does not expose the ``residual`` monitor set through the
    PyFluent monitor-stream manager, but it does emit scaled residual rows
    through the supported transcript callback when residual printing is on.
    This parser uses those native iteration rows; no RP iteration value is
    used for progress or horizon proof.
    """
    header_re = re.compile(r"^\s*iter\s+(.+?)\s+time/iter\s*$", re.IGNORECASE)
    number_re = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
    columns: list[str] | None = None
    iterations: list[int] = []
    series: dict[str, list[float]] = {}
    raw_row_count = 0
    verified_duplicate_rows = 0
    for line in text.splitlines():
        header = header_re.match(line)
        if header:
            next_columns = header.group(1).split()
            if columns is None:
                columns = next_columns
                series = {name: [] for name in columns}
            elif next_columns != columns:
                raise RuntimeError(
                    "residual transcript changed column layout across repeated headers: "
                    f"{next_columns!r} != {columns!r}"
                )
            continue
        if columns is None:
            continue
        tokens = line.split()
        if len(tokens) < len(columns) + 1 or not tokens[0].isdigit():
            continue
        values = tokens[1 : len(columns) + 1]
        if not all(number_re.match(value) for value in values):
            continue
        iteration = int(tokens[0])
        numeric_values = [float(value) for value in values]
        raw_row_count += 1
        if iterations and iteration == iterations[-1]:
            if all(series[name][-1] == value for name, value in zip(columns, numeric_values)):
                verified_duplicate_rows += 1
                continue
            raise RuntimeError(
                f"residual transcript repeats native iteration {iteration} with different values"
            )
        if iterations and iteration < iterations[-1]:
            raise RuntimeError(
                f"residual transcript moves backwards in native iteration: {iterations[-1]} -> {iteration}"
            )
        iterations.append(iteration)
        for name, value in zip(columns, numeric_values):
            series[name].append(value)
    if not iterations or not series:
        raise RuntimeError("PyFluent transcript contained no native residual rows")
    misaligned = {name: len(values) for name, values in series.items() if len(values) != len(iterations)}
    if misaligned:
        raise RuntimeError(
            "residual transcript produced misaligned native histories: "
            f"iterations={len(iterations)}, series={misaligned}"
        )
    return {
        "monitor_set": "residual",
        "source": "solver.transcript.register_callback",
        "iterations": iterations,
        "series": series,
        "point_count": len(iterations),
        "curve_count": len(series),
        "raw_row_count": raw_row_count,
        "verified_duplicate_boundary_rows_removed": verified_duplicate_rows,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--server-id", required=True)
    p.add_argument("--case-id", required=True)
    p.add_argument("--mode", choices=("fixed", "vent", "feedback", "ramp", "eulerian"), required=True)
    p.add_argument("--run-root", required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--residual-history", type=Path, required=True)
    p.add_argument("--pressure", type=float, default=1_120_000.0)
    p.add_argument("--loss", type=float, default=1.0)
    p.add_argument("--gain-pa-per-kg", type=float, default=500.0)
    p.add_argument("--max-step-pa", type=float, default=2_000.0)
    p.add_argument("--deadband-kg", type=float, default=0.0)
    p.add_argument(
        "--pressure-sequence",
        default="",
        help="Comma-separated, per-chunk gauge pressures for --mode ramp; the first is the initial pressure.",
    )
    p.add_argument("--chunks", type=int, default=5)
    p.add_argument("--chunk-iterations", type=int, default=100)
    p.add_argument("--smoke-iterations", type=int, default=50)
    p.add_argument("--discovery-iterations", type=int, default=500)
    a = p.parse_args()
    if a.manifest.exists() or a.residual_history.exists():
        raise FileExistsError("refusing to overwrite discovery evidence")
    if a.discovery_iterations <= 0 or a.smoke_iterations <= 0:
        raise ValueError("iteration counts must be positive")
    if a.mode in ("feedback", "ramp") and a.chunks * a.chunk_iterations != a.discovery_iterations:
        raise ValueError(f"{a.mode} chunks*chunk-iterations must equal discovery-iterations")
    pressure_sequence: list[float] = []
    if a.mode == "ramp":
        try:
            pressure_sequence = [float(value.strip()) for value in a.pressure_sequence.split(",") if value.strip()]
        except ValueError as exc:
            raise ValueError(f"invalid --pressure-sequence: {a.pressure_sequence!r}") from exc
        if len(pressure_sequence) != a.chunks:
            raise ValueError(
                f"ramp needs exactly one pressure per chunk: {len(pressure_sequence)} != {a.chunks}"
            )
        if any(not (P_MIN <= value <= P_MAX) for value in pressure_sequence):
            raise ValueError(f"ramp pressure outside declared bracket {P_MIN}..{P_MAX}: {pressure_sequence!r}")
    manifest = a.manifest.expanduser().resolve()
    smoke_residual = a.residual_history.with_name(a.residual_history.stem + ".smoke.json")
    transcript_path = a.residual_history.with_name(a.residual_history.stem + ".transcript.txt")
    final_case = str(PureWindowsPath(a.run_root) / "final.cas.h5")
    prepared_case = str(PureWindowsPath(a.run_root) / "prepared.cas.h5")
    monitor_root = str(PureWindowsPath(a.run_root) / "monitors")
    payload: dict[str, Any] = {
        "status": "RUNNING", "phase_id": "phase-06-full-geometry-with-brine-pool",
        "setup_id": a.case_id, "mode": "discovery", "case_mode": a.mode,
        "server_id": str(a.server_id), "run_root": a.run_root,
        "parent_case": PARENT_CASE, "parent_data": PARENT_DATA,
        "requested_smoke_iterations": a.smoke_iterations,
        "requested_discovery_iterations": a.discovery_iterations,
        "events": [], "updates": [],
    }
    if a.mode == "ramp":
        payload["pressure_sequence_pa"] = pressure_sequence
    write_status(manifest, payload); event(payload, "runner_started"); write_status(manifest, payload)
    transcript_capture: SessionTranscriptCapture | None = None
    try:
        a.residual_history.parent.mkdir(parents=True, exist_ok=True)
        solver = connect(server_id=a.server_id, start_transcript=True)
        payload["ownership_preflight"] = prove_quiescent(solver)
        if not all(remote_file_exists(solver, x) for x in (PARENT_CASE, PARENT_DATA)):
            raise RuntimeError("canonical F11 parent pair absent")
        ensure_remote_directory(solver, a.run_root)
        ensure_remote_directory(solver, monitor_root)
        solver.scheme.eval(f'(chdir "{quote_scheme_string(monitor_root)}")')
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        models = safe_get_state(solver.settings.setup.models, "P6 discovery model readback")
        if models.get("multiphase", {}).get("model") != "mixture":
            raise RuntimeError("discovery runner currently requires the verified Mixture parent")
        payload["parent_readback"] = {"models": models, "iteration": clock(solver)}
        if a.mode == "eulerian":
            parent_phase_state = models.get("multiphase", {}).get("phases", {})
            payload["eulerian_readback"] = set_eulerian(solver, parent_phase_state)
        initial_pressure = pressure_sequence[0] if a.mode == "ramp" else a.pressure
        if a.mode == "vent":
            payload["outlet_readback"] = set_vent(solver, a.loss)
        else:
            actual_initial_pressure = set_pressure(solver, max(P_MIN, min(P_MAX, initial_pressure)))
            if a.mode == "ramp" and abs(actual_initial_pressure - pressure_sequence[0]) > 1e-6:
                raise RuntimeError(
                    "ramp initial-pressure readback mismatch: "
                    f"{actual_initial_pressure} != {pressure_sequence[0]}"
                )
            payload["outlet_readback"] = {"mode": "pressure", "pressure_pa": actual_initial_pressure}
        payload["monitor_files"] = redirect_report_files(solver, monitor_root)
        for name in POOL_MASS_REPORT_FILES:
            if name not in payload["monitor_files"]:
                raise RuntimeError(f"required pool report missing: {name}")
        payload["residual_config"] = configure_residual_history(solver, a.discovery_iterations + a.smoke_iterations + 100)
        # Redirect inherited autosave roots before any smoke solve.  The F11
        # parent can carry a server-local root that does not exist elsewhere;
        # a short discovery run must not fail at that inherited autosave event.
        payload["autosave_config"] = configure_autosave(
            solver,
            a.run_root,
            data_frequency=max(a.discovery_iterations + a.smoke_iterations + 1, 1_000),
        )
        if any(remote_file_exists(solver, path) for path in (prepared_case, data_path(prepared_case), final_case, data_path(final_case))):
            raise FileExistsError("discovery output path already exists")
        solver.settings.file.write_case(file_name=prepared_case)
        solver.settings.file.write_data(file_name=data_path(prepared_case))
        if not all(remote_file_exists(solver, path) for path in (prepared_case, data_path(prepared_case))):
            raise RuntimeError("prepared paired save failed")
        solver.settings.file.read_case(file_name=prepared_case)
        solver.settings.file.read_data(file_name=data_path(prepared_case))
        payload["prepared_reload_rp_iteration"] = clock(solver)
        payload["prepared_reload_model_readback"] = safe_get_state(solver.settings.setup.models, "P6 discovery reloaded models")
        if a.mode == "eulerian":
            payload["prepared_reload_eulerian_auxiliary_readback"] = read_eulerian_auxiliary_state(solver)
            if (
                payload["prepared_reload_eulerian_auxiliary_readback"]
                .get("pressure_velocity_coupling", {})
                .get("flow_scheme")
                != "Coupled"
            ):
                raise RuntimeError(
                    "D06R Coupled scheme did not survive prepared save/reopen: "
                    f"{payload['prepared_reload_eulerian_auxiliary_readback']!r}"
                )
        if a.mode == "vent":
            payload["prepared_reload_outlet_readback"] = safe_get_state(
                solver.settings.setup.boundary_conditions.outlet_vent["brineoutlet"],
                "P6 discovery reloaded outlet vent",
            )
        else:
            payload["prepared_reload_outlet_readback"] = safe_get_state(
                solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"],
                "P6 discovery reloaded pressure outlet",
            )
        payload["prepared_reload_report_readback"] = readback_report_paths(solver, payload["monitor_files"], monitor_root)
        payload["prepared_reload_residual_readback"] = safe_get_state(
            solver.settings.solution.monitor.residual,
            "P6 discovery reloaded residual monitor",
        )
        payload["prepared_reload_autosave_readback"] = safe_get_state(
            solver.settings.file.auto_save,
            "P6 discovery reloaded autosave",
        )
        if (
            payload["prepared_reload_autosave_readback"].get("root_name")
            != payload["autosave_config"].get("root_name")
        ):
            raise RuntimeError(
                "autosave root did not survive prepared save/reopen: "
                f"{payload['prepared_reload_autosave_readback']!r}"
            )
        transcript_capture = SessionTranscriptCapture(solver, stream_path=transcript_path)
        transcript_capture.start()
        smoke_marker = transcript_capture.mark()
        event(payload, "smoke_started", incremental_iterations=a.smoke_iterations); write_status(manifest, payload)
        solver.settings.solution.run_calculation.iterate(iter_count=a.smoke_iterations)
        missing_smoke = [path for path in payload["monitor_files"].values() if not remote_file_exists(solver, path)]
        if missing_smoke:
            raise RuntimeError(f"smoke did not write report histories: {missing_smoke}")
        smoke_residuals = parse_native_residual_transcript(transcript_capture.text_since(smoke_marker))
        if int(smoke_residuals.get("point_count", 0)) <= 0:
            raise RuntimeError("smoke residual monitor did not populate")
        smoke_residual.parent.mkdir(parents=True, exist_ok=True)
        smoke_residual.write_text(json.dumps(smoke_residuals, indent=2, default=str) + "\n", encoding="utf-8")
        smoke_history = parse_report_forms(read_remote_forms(solver, payload["monitor_files"][PROXY_REPORT_FILE]))
        smoke_coordinates = [int(value) for value in smoke_history["iterations"]]
        if len(smoke_coordinates) < 2 or smoke_coordinates[-1] - smoke_coordinates[0] != a.smoke_iterations:
            raise RuntimeError(
                f"smoke report coordinate span mismatch: {smoke_coordinates[:1]} -> {smoke_coordinates[-1:]}, expected span {a.smoke_iterations}"
            )
        report_start_iteration = smoke_coordinates[0]
        smoke_iteration = smoke_coordinates[-1]
        payload["report_iteration_start"] = report_start_iteration
        payload["smoke_report_iteration"] = smoke_iteration
        payload["rp_iteration_after_smoke"] = clock(solver)
        payload["smoke_residual_history"] = str(smoke_residual)
        report_path = payload["monitor_files"][PROXY_REPORT_FILE]
        previous_iteration, _ = latest_proxy(solver, report_path)
        if previous_iteration != smoke_iteration:
            raise RuntimeError(f"smoke proxy report coordinate mismatch: {previous_iteration} != solver {smoke_iteration}")
        pressure = float(payload["outlet_readback"].get("pressure_pa", initial_pressure)) if a.mode != "vent" else None
        for chunk in range(1, a.chunks + 1 if a.mode in ("feedback", "ramp") else 2):
            count = a.chunk_iterations if a.mode == "feedback" else a.discovery_iterations
            if a.mode == "ramp":
                count = a.chunk_iterations
            if chunk > 1 and a.mode not in ("feedback", "ramp"):
                break
            event(payload, "discovery_chunk_started", chunk=chunk, iteration_before=previous_iteration); write_status(manifest, payload)
            solver.settings.solution.run_calculation.iterate(iter_count=count)
            it, mass = latest_proxy(solver, report_path)
            if it != previous_iteration + count:
                raise RuntimeError(f"discovery native iteration mismatch: {previous_iteration} -> {it}, expected +{count}")
            update: dict[str, Any] = {"chunk": chunk, "report_iteration": it, "proxy_mass_kg": mass}
            if a.mode == "feedback" and pressure is not None:
                error = mass - TARGET_KG
                if abs(error) <= a.deadband_kg:
                    step = 0.0
                else:
                    step = max(-a.max_step_pa, min(a.max_step_pa, -a.gain_pa_per_kg * error))
                requested = max(P_MIN, min(P_MAX, pressure + step))
                actual = set_pressure(solver, requested)
                update.update({"error_kg": error, "pressure_before_pa": pressure, "requested_pressure_after_pa": requested, "pressure_after_pa": actual})
                pressure = actual
            elif a.mode == "ramp" and pressure is not None:
                update["pressure_before_pa"] = pressure
                if chunk < len(pressure_sequence):
                    requested = pressure_sequence[chunk]
                    actual = set_pressure(solver, requested)
                    if abs(actual - requested) > 1e-6:
                        raise RuntimeError(
                            f"ramp pressure readback mismatch after chunk {chunk}: {actual} != {requested}"
                        )
                    update.update({"requested_pressure_after_pa": requested, "pressure_after_pa": actual})
                    pressure = actual
                else:
                    update.update({"requested_pressure_after_pa": None, "pressure_after_pa": pressure})
            payload["updates"].append(update); previous_iteration = it; write_status(manifest, payload)
        residuals = parse_native_residual_transcript(transcript_capture.text_since(smoke_marker))
        if int(residuals.get("point_count", 0)) < a.discovery_iterations:
            raise RuntimeError(f"residual history too short: {residuals.get('point_count')} < {a.discovery_iterations}")
        a.residual_history.write_text(json.dumps(residuals, indent=2, default=str) + "\n", encoding="utf-8")
        transcript_capture.close()
        payload["residual_transcript"] = str(transcript_path)
        expected_samples_per_report = 1 + a.smoke_iterations + a.discovery_iterations
        payload["report_sample_counts"] = report_sample_counts(
            solver,
            payload["monitor_files"],
            expected_report_count=30,
            expected_samples_per_report=expected_samples_per_report,
        )
        payload["report_package_verification"] = {
            "status": "PASS",
            "expected_report_count": 30,
            "observed_report_count": len(payload["monitor_files"]),
            "expected_samples_per_report": expected_samples_per_report,
            "observed_sample_counts": payload["report_sample_counts"],
        }
        report_end_iteration = previous_iteration
        event(payload, "final_pair_started", case=final_case, data=data_path(final_case)); write_status(manifest, payload)
        solver.settings.file.write_case(file_name=final_case)
        solver.settings.file.write_data(file_name=data_path(final_case))
        if not all(remote_file_exists(solver, path) for path in (final_case, data_path(final_case))):
            raise RuntimeError("final paired save failed")
        solver.settings.file.read_case(file_name=final_case)
        solver.settings.file.read_data(file_name=data_path(final_case))
        payload["final_reopen_rp_iteration"] = clock(solver)
        payload["final_reopen_model_readback"] = safe_get_state(solver.settings.setup.models, "P6 discovery final model")
        if a.mode == "eulerian":
            payload["final_reopen_eulerian_auxiliary_readback"] = read_eulerian_auxiliary_state(solver)
            if (
                payload["final_reopen_eulerian_auxiliary_readback"]
                .get("pressure_velocity_coupling", {})
                .get("flow_scheme")
                != "Coupled"
            ):
                raise RuntimeError(
                    "D06R Coupled scheme did not survive final save/reopen: "
                    f"{payload['final_reopen_eulerian_auxiliary_readback']!r}"
                )
        if a.mode == "vent":
            payload["final_reopen_outlet_readback"] = safe_get_state(
                solver.settings.setup.boundary_conditions.outlet_vent["brineoutlet"],
                "P6 discovery final outlet vent",
            )
        else:
            payload["final_reopen_outlet_readback"] = safe_get_state(
                solver.settings.setup.boundary_conditions.pressure_outlet["brineoutlet"],
                "P6 discovery final pressure outlet",
            )
        final_report_iteration, _ = latest_proxy(solver, payload["monitor_files"][PROXY_REPORT_FILE])
        payload["final_reopen_report_iteration"] = final_report_iteration
        if final_report_iteration != report_end_iteration:
            raise RuntimeError(
                f"final report endpoint did not survive reopen: {final_report_iteration} != {report_end_iteration}"
            )
        payload["report_iteration_end"] = report_end_iteration
        payload["report_iteration_delta"] = report_end_iteration - report_start_iteration
        expected_delta = a.smoke_iterations + a.discovery_iterations
        if payload["report_iteration_delta"] != expected_delta:
            raise RuntimeError(
                f"final report delta mismatch: {payload['report_iteration_delta']} != expected {expected_delta}"
            )
        payload["terminal_verification"] = {
            "status": "PASS",
            "pair_exists": True,
            "pair_reopened": True,
            "requested_discovery_iterations": a.discovery_iterations,
            "report_iteration_start": payload["report_iteration_start"],
            "report_iteration_end": payload["report_iteration_end"],
            "report_iteration_delta": payload["report_iteration_delta"],
            "report_sample_counts": payload["report_sample_counts"],
            "report_package_verification": payload["report_package_verification"],
            "residual_history_points": int(residuals.get("point_count", 0)),
        }
        payload.update({"status": "COMPLETE", "final_report_iteration": payload["report_iteration_end"], "final_case": final_case, "final_data": data_path(final_case), "residual_history": str(a.residual_history)})
        event(payload, "runner_complete"); write_status(manifest, payload); print(json.dumps(payload, indent=2, default=str)); return 0
    except Exception as exc:
        if transcript_capture is not None:
            transcript_capture.close()
        payload.update({"status": "BLOCKED", "error": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()})
        event(payload, "runner_blocked", error=payload["error"]); write_status(manifest, payload); print(json.dumps(payload, indent=2, default=str), file=sys.stderr); return 1


if __name__ == "__main__":
    raise SystemExit(main())

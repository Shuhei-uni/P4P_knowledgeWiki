#!/usr/bin/env python3
"""Build, prove, and run the attached P7-E0-REF discovery experiment."""
from __future__ import annotations

import argparse
import json
import re
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))

from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.connection import connect
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import (
    configure_autosave,
    configure_residual_history,
    ensure_remote_directory,
)
from extract_report_plot_histories import parse_report_forms, read_remote_forms

SETUP_ID = "P7-E0-REF"
EXPECTED_DIAMETER_M = 0.875936
PHASES = ("mixture", "phase-1", "phase-2")
SURFACES = ("liquidinlet", "steaminlet", "steamoutlet", "bottom")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    tmp.replace(path)


def data_path(case_path: str) -> str:
    if not case_path.endswith(".cas.h5"):
        raise ValueError(case_path)
    return case_path[:-7] + ".dat.h5"


def set_optional(obj: Any, name: str, value: Any) -> None:
    try:
        setattr(obj, name, value)
    except Exception:
        pass


def replace_named(branch: Any, name: str) -> Any:
    names = set(branch.get_object_names())
    if name in names:
        branch.delete(name_list=[name])
    branch.create(name=name)
    return branch[name]


def configure_reports(solver: Any) -> list[dict[str, Any]]:
    definitions: list[dict[str, Any]] = []
    flux = solver.settings.solution.report_definitions.flux
    for phase in PHASES:
        for surface in SURFACES:
            name = f"e0-flux-{phase.replace('-', '')}-{surface}"
            report = replace_named(flux, name)
            report.report_type = "flux-massflow"
            report = flux[name]
            report.boundaries = [surface]
            report.phase = phase
            set_optional(report, "per_selection", False)
            set_optional(report, "average_over", 1)
            set_optional(report, "retain_instantaneous_values", True)
            set_optional(report, "create_report_file", True)
            set_optional(report, "create_report_plot", True)
            state = report.get_state()
            if state.get("report_type") != "flux-massflow" or state.get("boundaries") != [surface] or state.get("phase") != phase:
                raise RuntimeError(f"flux report readback mismatch for {name}: {state}")
            definitions.append({"name": name, "kind": "flux", "phase": phase, "surface": surface, "state": state})

    volume = solver.settings.solution.report_definitions.volume
    mass = replace_named(volume, "e0-liquid-mass-total")
    mass.report_type = "volume-mass"
    mass = volume["e0-liquid-mass-total"]
    mass.cell_zones = ["separator-purnanto"]
    mass.phase = "phase-2"
    for key, value in (("per_selection", False), ("average_over", 1), ("retain_instantaneous_values", True), ("create_report_file", True), ("create_report_plot", True)):
        set_optional(mass, key, value)
    mass_state = mass.get_state()
    if mass_state.get("report_type") != "volume-mass" or mass_state.get("cell_zones") != ["separator-purnanto"] or mass_state.get("phase") != "phase-2":
        raise RuntimeError(f"liquid mass report readback mismatch: {mass_state}")
    definitions.append({"name": "e0-liquid-mass-total", "kind": "volume-mass", "state": mass_state})

    liquid_volume = replace_named(volume, "e0-liquid-volume-total")
    liquid_volume.report_type = "volume-integral"
    liquid_volume = volume["e0-liquid-volume-total"]
    liquid_volume.cell_zones = ["separator-purnanto"]
    liquid_volume.field = "phase-2-vof"
    liquid_volume.phase = "mixture"
    for key, value in (("per_selection", False), ("average_over", 1), ("retain_instantaneous_values", True), ("create_report_file", True), ("create_report_plot", True)):
        set_optional(liquid_volume, key, value)
    volume_state = liquid_volume.get_state()
    if volume_state.get("report_type") != "volume-integral" or volume_state.get("field") != "phase-2-vof":
        raise RuntimeError(f"liquid volume report readback mismatch: {volume_state}")
    definitions.append({"name": "e0-liquid-volume-total", "kind": "volume-integral", "state": volume_state})
    return definitions


def existing_e0_reports(solver: Any) -> list[dict[str, Any]] | None:
    """Reuse the named E0 package already present in a shared initialized pair."""
    flux = solver.settings.solution.report_definitions.flux
    volume = solver.settings.solution.report_definitions.volume
    expected_flux = {
        f"e0-flux-{phase.replace('-', '')}-{surface}"
        for phase in PHASES
        for surface in SURFACES
    }
    if not expected_flux.issubset(set(str(name) for name in flux.get_object_names())):
        return None
    if not {"e0-liquid-mass-total", "e0-liquid-volume-total"}.issubset(
        set(str(name) for name in volume.get_object_names())
    ):
        return None
    definitions: list[dict[str, Any]] = []
    for phase in PHASES:
        for surface in SURFACES:
            name = f"e0-flux-{phase.replace('-', '')}-{surface}"
            state = safe_get_state(flux[name], f"existing E0 flux report {name}")
            definitions.append({"name": name, "kind": "flux", "phase": phase, "surface": surface, "state": state})
    for name, kind in (("e0-liquid-mass-total", "volume-mass"), ("e0-liquid-volume-total", "volume-integral")):
        definitions.append({"name": name, "kind": kind, "state": safe_get_state(volume[name], f"existing E0 volume report {name}")})
    return definitions


def redirect_e0_report_files(solver: Any, monitor_root: str) -> dict[str, str]:
    ensure_remote_directory(solver, monitor_root)
    reports = solver.settings.solution.monitor.report_files
    expected = {
        f"e0-flux-{phase.replace('-', '')}-{surface}-rfile"
        for phase in PHASES
        for surface in SURFACES
    }
    expected |= {"e0-liquid-mass-total-rfile", "e0-liquid-volume-total-rfile"}
    names = sorted(str(name) for name in reports.get_object_names())
    stale = sorted(set(names) - expected)
    if stale:
        # The shared initialized dependency pair can retain generic Fluent
        # report-file objects from an earlier instrumentation package. They
        # are not part of the approved E0 evidence contract; remove only
        # those unreferenced generic objects before enforcing the 14-file set.
        reports.delete(name_list=stale)
    names = sorted(str(name) for name in reports.get_object_names())
    if len(names) != 14:
        raise RuntimeError(f"expected exactly 14 E0 report-file objects, got {names}")
    paths: dict[str, str] = {}
    for name in names:
        path = str(PureWindowsPath(monitor_root) / f"{name}.out")
        if remote_file_exists(solver, path):
            raise FileExistsError(f"refusing to overwrite E0 monitor file: {path}")
        reports[name].file_name = path
        state = safe_get_state(reports[name], f"E0 report file {name}")
        actual = state.get("file_name") if isinstance(state, Mapping) else None
        if not isinstance(actual, str) or PureWindowsPath(actual).name != PureWindowsPath(path).name:
            raise RuntimeError(f"E0 report path readback mismatch for {name}: {actual!r}")
        paths[name] = path
    return paths


def verify_setup(solver: Any) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "P7 E0 models")
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "P7 E0 boundaries")
    cells = safe_get_state(solver.settings.setup.cell_zone_conditions, "P7 E0 cell zones")
    if models.get("multiphase", {}).get("model") != "mixture":
        raise RuntimeError("E0 requires Mixture")
    phases = models.get("multiphase", {}).get("phases", {})
    if phases.get("phase-1", {}).get("material") != "water-vapor-at-psep" or phases.get("phase-2", {}).get("material") != "water-liquid-at-psep":
        raise RuntimeError(f"phase/material mapping mismatch: {phases}")
    if models.get("viscous", {}).get("k_epsilon_model") != "rng":
        raise RuntimeError("E0 requires RNG k-epsilon")
    rng = models.get("viscous", {}).get("rng", {})
    if rng.get("differential_viscosity_model") is not True:
        raise RuntimeError(f"E0 requires parent RNG differential-viscosity option on: {rng}")
    if rng.get("swirl_dominated_flow") is not True:
        raise RuntimeError(f"E0 requires parent RNG swirl-dominated-flow option on: {rng}")
    if models.get("discrete_phase", {}).get("general_settings", {}).get("interaction", {}).get("enabled") is not False:
        raise RuntimeError("DPM carrier interaction is not proven off")
    required = {
        "mass_flow_inlet": {"liquidinlet", "steaminlet"},
        "pressure_outlet": {"steamoutlet"},
        "wall": {"bottom", "wall", "separator-purnanto:1"},
    }
    for kind, names in required.items():
        actual = set(boundaries.get(kind, {})) - {"settings"}
        if not names.issubset(actual):
            raise RuntimeError(f"boundary map mismatch for {kind}: {actual}")
    if "separator-purnanto" not in cells.get("fluid", {}):
        raise RuntimeError(f"fluid cell zone mismatch: {cells}")
    outlet = boundaries["pressure_outlet"]["steamoutlet"]
    diameter = float(outlet["phase"]["mixture"]["turbulence"]["backflow_hydraulic_diameter"])
    if abs(diameter - EXPECTED_DIAMETER_M) > 1e-12:
        raise RuntimeError(f"steamoutlet diameter mismatch: {diameter}")
    liq = float(boundaries["mass_flow_inlet"]["liquidinlet"]["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"])
    vap = float(boundaries["mass_flow_inlet"]["steaminlet"]["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"])
    if abs(liq - 116.92) > 1e-9 or abs(vap - 80.69) > 1e-9:
        raise RuntimeError(f"inlet target mismatch: liquid={liq}, vapor={vap}")
    return {"models": models, "boundaries": boundaries, "cell_zone_conditions": cells, "liquid_inlet_kg_s": liq, "vapor_inlet_kg_s": vap, "steamoutlet_diameter_m": diameter}


def parse_residuals(text: str) -> dict[str, Any]:
    header_re = re.compile(r"^\s*iter\s+(.+?)\s+time/iter\s*$", re.I)
    num_re = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
    columns = None; iterations: list[int] = []; series: dict[str, list[float]] = {}
    for line in text.splitlines():
        match = header_re.match(line)
        if match:
            next_columns = match.group(1).split()
            if columns is None:
                columns = next_columns; series = {name: [] for name in columns}
            elif next_columns != columns:
                raise RuntimeError("residual column layout changed")
            continue
        if columns is None:
            continue
        tokens = line.split()
        if len(tokens) < len(columns) + 1 or not tokens[0].isdigit() or not all(num_re.match(x) for x in tokens[1:len(columns)+1]):
            continue
        it = int(tokens[0]); values = [float(x) for x in tokens[1:len(columns)+1]]
        if iterations and it == iterations[-1]:
            continue
        if iterations and it < iterations[-1]:
            raise RuntimeError("residual native iteration moved backwards")
        iterations.append(it)
        for name, value in zip(columns, values): series[name].append(value)
    if not iterations:
        raise RuntimeError("no native residual rows captured")
    return {"iterations": iterations, "series": series, "point_count": len(iterations), "curve_count": len(series), "source": "PyFluent transcript callback"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--server-id", default="3")
    p.add_argument("--source-case", required=True)
    p.add_argument("--run-root", required=True)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--residual-history", required=True, type=Path)
    args = p.parse_args()
    if args.manifest.exists():
        prior = json.loads(args.manifest.read_text(encoding="utf-8"))
        if prior.get("status") != "BLOCKED" or prior.get("events"):
            raise FileExistsError("refusing to overwrite nonempty local E0 evidence")
    if args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local E0 residual evidence")
    root = PureWindowsPath(args.run_root)
    prepared = str(root / "prepared.cas.h5")
    initialized = str(root / "initialized.cas.h5")
    smoke = str(root / "smoke-iter0050.cas.h5")
    final = str(root / "final-iter2000.cas.h5")
    monitor_root = str(root / "monitors")
    transcript_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
    checkpoints = {500: str(root / "checkpoint-iter0500.cas.h5"), 1000: str(root / "checkpoint-iter1000.cas.h5"), 1500: str(root / "checkpoint-iter1500.cas.h5")}
    payload: dict[str, Any] = {"status": "RUNNING", "setup_id": SETUP_ID, "mode": "discovery", "server_id": args.server_id, "source_case": args.source_case, "run_root": args.run_root, "requested_iterations": 2000, "events": []}
    write_json(args.manifest, payload)
    capture = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root); ensure_remote_directory(solver, monitor_root)
        if not remote_file_exists(solver, args.source_case):
            raise FileNotFoundError(args.source_case)
        for path in (prepared, initialized, data_path(initialized), smoke, data_path(smoke), final, data_path(final), *checkpoints.values(), *(data_path(x) for x in checkpoints.values())):
            if remote_file_exists(solver, path):
                raise FileExistsError(f"refusing to overwrite E0 artifact: {path}")
        solver.settings.file.read_case(file_name=args.source_case)
        outlet = solver.settings.setup.boundary_conditions.pressure_outlet["steamoutlet"]
        outlet.phase["mixture"].turbulence.backflow_hydraulic_diameter = EXPECTED_DIAMETER_M
        reused = existing_e0_reports(solver)
        payload["instrumentation"] = reused if reused is not None else configure_reports(solver)
        payload["report_files"] = redirect_e0_report_files(solver, monitor_root)
        if len(payload["report_files"]) != 14:
            raise RuntimeError(f"expected 14 report files, got {len(payload['report_files'])}")
        payload["residual_configuration"] = configure_residual_history(solver, 2200)
        payload["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=500)
        capture = SessionTranscriptCapture(solver, stream_path=transcript_path); capture.start()
        solver.settings.mesh.check()
        payload["immediate_readback"] = verify_setup(solver)
        solver.settings.file.write_case(file_name=prepared)
        if not remote_file_exists(solver, prepared): raise RuntimeError("prepared case save failed")
        solver.settings.file.read_case(file_name=prepared)
        payload["post_reopen_readback"] = verify_setup(solver)
        init = solver.settings.solution.initialization
        init.initialization_type = "hybrid"
        init.reference_frame = "relative"
        init.hybrid_init_options.general_settings.iter_count = 10
        init.hybrid_initialize()
        solver.settings.file.write_case(file_name=initialized); solver.settings.file.write_data(file_name=data_path(initialized))
        if not remote_file_exists(solver, initialized) or not remote_file_exists(solver, data_path(initialized)):
            raise RuntimeError("initialized pair save failed")
        run_marker = capture.mark()
        completed = 0
        for count, endpoint in ((50, 50), (450, 500), (500, 1000), (500, 1500), (500, 2000)):
            solver.settings.solution.run_calculation.iterate(iter_count=count)
            completed = endpoint
            case_path = smoke if endpoint == 50 else checkpoints.get(endpoint, final)
            solver.settings.file.write_case(file_name=case_path); solver.settings.file.write_data(file_name=data_path(case_path))
            if not remote_file_exists(solver, case_path) or not remote_file_exists(solver, data_path(case_path)):
                raise RuntimeError(f"checkpoint pair missing at {endpoint}")
            payload["events"].append({"event": "checkpoint", "iteration": endpoint, "case": case_path, "data": data_path(case_path)})
            write_json(args.manifest, payload)
            if endpoint == 50:
                missing = [path for path in payload["report_files"].values() if not remote_file_exists(solver, path)]
                if missing: raise RuntimeError(f"smoke report files missing: {missing}")
                smoke_residuals = parse_residuals(capture.text_since(run_marker))
                if smoke_residuals["point_count"] < 50: raise RuntimeError("smoke residual history too short")
        residuals = parse_residuals(capture.text_since(run_marker))
        if residuals["point_count"] < 2000: raise RuntimeError(f"residual history too short: {residuals['point_count']}")
        write_json(args.residual_history, residuals)
        histories: dict[str, Any] = {}
        for name, path in payload["report_files"].items():
            parsed = parse_report_forms(read_remote_forms(solver, path))
            if len(parsed.get("iterations", [])) < 2000: raise RuntimeError(f"report history too short for {name}: {len(parsed.get('iterations', []))}")
            histories[name] = parsed
        history_path = args.residual_history.with_name(args.residual_history.stem.replace("-residuals", "-report-histories") + ".json")
        write_json(history_path, histories)
        solver.settings.file.read_case(file_name=final); solver.settings.file.read_data(file_name=data_path(final))
        payload["final_reopen_readback"] = verify_setup(solver)
        payload["status"] = "COMPLETE"; payload["completed_iterations"] = completed; payload["final_case"] = final; payload["final_data"] = data_path(final); payload["residual_history"] = str(args.residual_history); payload["report_histories"] = str(history_path); payload["transcript"] = str(transcript_path)
        write_json(args.manifest, payload)
        capture.close()
        print(json.dumps(payload, indent=2, default=str))
        return 0
    except Exception as exc:
        if capture is not None: capture.close()
        payload["status"] = "BLOCKED"; payload["error"] = f"{type(exc).__name__}: {exc}"; payload["traceback"] = traceback.format_exc()
        write_json(args.manifest, payload)
        print(json.dumps(payload, indent=2, default=str), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

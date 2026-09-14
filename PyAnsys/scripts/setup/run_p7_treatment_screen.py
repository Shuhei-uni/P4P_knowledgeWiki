#!/usr/bin/env python3
"""Build, prove, and run one approved Phase-07 treatment-screen child.

This runner implements the 15 compiled initial children plus the three
predeclared, bounded fourth branches activated by the Phase-07 decision gate.
It does not promote continuations or tune numerics. E1-E3 use the exact E0
initialized pair; E4 uses the exact E0 iteration-500 pair and the predeclared
inventory controller. E5 performs the required source-region capability probe
and refuses to solve when Fluent exposes only a whole-zone source rather than a
source bound to the frozen cell register.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_file_exists, remote_chdir, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    ensure_remote_directory,
)


EXPECTED_DIAMETER_M = 0.875936
LIQUID_INLET_KG_S = 116.92
VAPOR_INLET_KG_S = 80.69
MAX_COMMAND_KG_S = 146.15
PHASES = ("mixture", "phase-1", "phase-2")
SURFACES = ("liquidinlet", "steaminlet", "steamoutlet", "bottom")


def data_path(case_path: str) -> str:
    if not case_path.endswith(".cas.h5"):
        raise ValueError(case_path)
    return case_path[:-7] + ".dat.h5"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def set_optional(obj: Any, name: str, value: Any) -> None:
    try:
        setattr(obj, name, value)
    except Exception:
        pass


def candidate_spec(candidate: str) -> dict[str, Any]:
    specs: dict[str, dict[str, Any]] = {
        "P7-E1-PO-P1120": {"family": "E1-PO", "kind": "pressure-outlet", "value": 1_120_000.0},
        "P7-E1-PO-P1160": {"family": "E1-PO", "kind": "pressure-outlet", "value": 1_160_000.0},
        "P7-E1-PO-P1200": {"family": "E1-PO", "kind": "pressure-outlet", "value": 1_200_000.0},
        "P7-E2-OV-K000": {"family": "E2-OV", "kind": "outlet-vent", "value": 0.0},
        "P7-E2-OV-K003": {"family": "E2-OV", "kind": "outlet-vent", "value": 3.0},
        "P7-E2-OV-K007": {"family": "E2-OV", "kind": "outlet-vent", "value": 7.0},
        "P7-E2-OV-K010": {"family": "E2-OV", "kind": "outlet-vent", "value": 10.0},
        "P7-E3-MFO-Q025": {"family": "E3-MFO", "kind": "mass-flow-outlet", "value": 29.23},
        "P7-E3-MFO-Q050": {"family": "E3-MFO", "kind": "mass-flow-outlet", "value": 58.46},
        "P7-E3-MFO-Q100": {"family": "E3-MFO", "kind": "mass-flow-outlet", "value": 116.92},
        "P7-E3-MFO-Q14615": {"family": "E3-MFO", "kind": "mass-flow-outlet", "value": 146.15},
        "P7-E4-ADAPT-G025": {"family": "E4-ADAPT", "kind": "adaptive-mass-flow-outlet", "value": 0.25},
        "P7-E4-ADAPT-G050": {"family": "E4-ADAPT", "kind": "adaptive-mass-flow-outlet", "value": 0.50},
        "P7-E4-ADAPT-G100": {"family": "E4-ADAPT", "kind": "adaptive-mass-flow-outlet", "value": 1.00},
        "P7-E4-ADAPT-G150": {"family": "E4-ADAPT", "kind": "adaptive-mass-flow-outlet", "value": 1.50},
        "P7-E5-PSINK-G025": {"family": "E5-PSINK", "kind": "adaptive-liquid-only-sink", "value": 0.25},
        "P7-E5-PSINK-G050": {"family": "E5-PSINK", "kind": "adaptive-liquid-only-sink", "value": 0.50},
        "P7-E5-PSINK-G100": {"family": "E5-PSINK", "kind": "adaptive-liquid-only-sink", "value": 1.00},
    }
    if candidate not in specs:
        raise ValueError(f"candidate is not one of the approved Phase-07 initial or conditional fourth children: {candidate}")
    return specs[candidate]


def parse_residuals(text: str) -> dict[str, Any]:
    header_re = re.compile(r"^\s*iter\s+(.+?)\s+time/iter\s*$", re.I)
    number_re = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
    columns: list[str] | None = None
    iterations: list[int] = []
    series: dict[str, list[float]] = {}
    for line in text.splitlines():
        header = header_re.match(line)
        if header:
            next_columns = header.group(1).split()
            if columns is None:
                columns = next_columns
                series = {name: [] for name in columns}
            elif next_columns != columns:
                raise RuntimeError("residual column layout changed")
            continue
        if columns is None:
            continue
        tokens = line.split()
        if (
            len(tokens) < len(columns) + 1
            or not tokens[0].isdigit()
            or not all(number_re.match(value) for value in tokens[1 : len(columns) + 1])
        ):
            continue
        iteration = int(tokens[0])
        if iterations and iteration == iterations[-1]:
            continue
        if iterations and iteration < iterations[-1]:
            raise RuntimeError("residual native iteration moved backwards")
        iterations.append(iteration)
        for name, value in zip(columns, tokens[1 : len(columns) + 1]):
            series[name].append(float(value))
    if not iterations:
        raise RuntimeError("no native residual rows captured")
    return {
        "iterations": iterations,
        "series": series,
        "point_count": len(iterations),
        "curve_count": len(series),
        "source": "PyFluent transcript callback",
    }


def replace_named(branch: Any, name: str) -> Any:
    names = set(branch.get_object_names())
    if name in names:
        branch.delete(name_list=[name])
    branch.create(name=name)
    return branch[name]


def redirect_reports(solver: Any, monitor_root: str, candidate: str) -> dict[str, str]:
    ensure_remote_directory(solver, monitor_root)
    reports = solver.settings.solution.monitor.report_files
    names = sorted(str(name) for name in reports.get_object_names())
    required = {f"e0-flux-{phase.replace('-', '')}-{surface}-rfile" for phase in PHASES for surface in SURFACES}
    required |= {"e0-liquid-mass-total-rfile", "e0-liquid-volume-total-rfile"}
    missing = sorted(required - set(names))
    if missing:
        raise RuntimeError(f"parent report-file package is missing {missing}")
    paths: dict[str, str] = {}
    for name in names:
        path = str(PureWindowsPath(monitor_root) / f"{candidate}-{name}.out")
        if remote_file_exists(solver, path):
            raise FileExistsError(f"refusing to overwrite treatment monitor file: {path}")
        reports[name].file_name = path
        state = safe_get_state(reports[name], f"report file {name}")
        actual = state.get("file_name") if isinstance(state, Mapping) else None
        if not isinstance(actual, str) or PureWindowsPath(actual).name != PureWindowsPath(path).name:
            raise RuntimeError(f"report path readback mismatch for {name}: {actual!r}")
        paths[name] = path
    return paths


def base_invariants(solver: Any) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "treatment base models")
    boundaries = safe_get_state(solver.settings.setup.boundary_conditions, "treatment base boundaries")
    cells = safe_get_state(solver.settings.setup.cell_zone_conditions, "treatment base cell zones")
    if models.get("multiphase", {}).get("model") != "mixture":
        raise RuntimeError("treatment requires Mixture")
    phases = models.get("multiphase", {}).get("phases", {})
    if phases.get("phase-1", {}).get("material") != "water-vapor-at-psep":
        raise RuntimeError(f"phase-1 material mismatch: {phases}")
    if phases.get("phase-2", {}).get("material") != "water-liquid-at-psep":
        raise RuntimeError(f"phase-2 material mismatch: {phases}")
    if models.get("viscous", {}).get("k_epsilon_model") != "rng":
        raise RuntimeError("treatment requires RNG k-epsilon")
    rng = models.get("viscous", {}).get("rng", {})
    if rng.get("differential_viscosity_model") is not True or rng.get("swirl_dominated_flow") is not True:
        raise RuntimeError(f"parent RNG options not preserved: {rng}")
    interaction = models.get("discrete_phase", {}).get("general_settings", {}).get("interaction", {})
    if interaction.get("enabled") is not False:
        raise RuntimeError(f"DPM carrier interaction is not proven off: {interaction}")
    if "separator-purnanto" not in cells.get("fluid", {}):
        raise RuntimeError(f"fluid zone mismatch: {cells}")
    pressure = boundaries.get("pressure_outlet", {})
    if "steamoutlet" not in pressure:
        raise RuntimeError(f"steamoutlet missing: {boundaries}")
    outlet = pressure["steamoutlet"]
    diameter = float(outlet["phase"]["mixture"]["turbulence"]["backflow_hydraulic_diameter"])
    if abs(diameter - EXPECTED_DIAMETER_M) > 1e-12:
        raise RuntimeError(f"steamoutlet diameter mismatch: {diameter}")
    mass_inlets = boundaries.get("mass_flow_inlet", {})
    if set(("liquidinlet", "steaminlet")) - set(mass_inlets):
        raise RuntimeError(f"Phase-07 mass-flow inlets missing: {mass_inlets}")
    liq = float(mass_inlets["liquidinlet"]["phase"]["phase-2"]["momentum"]["mass_flow_rate"]["value"])
    vap = float(mass_inlets["steaminlet"]["phase"]["phase-1"]["momentum"]["mass_flow_rate"]["value"])
    if abs(liq - LIQUID_INLET_KG_S) > 1e-9 or abs(vap - VAPOR_INLET_KG_S) > 1e-9:
        raise RuntimeError(f"inlet targets changed: liquid={liq}, vapor={vap}")
    return {
        "models": models,
        "boundaries": boundaries,
        "cell_zone_conditions": cells,
        "steamoutlet_diameter_m": diameter,
        "liquid_inlet_kg_s": liq,
        "vapor_inlet_kg_s": vap,
    }


def set_liquid_backflow(outlet: Any, reference_outlet: Mapping[str, Any]) -> None:
    """Apply the explicit liquid-dominant backflow and parent outlet form."""
    mixture = outlet.phase["mixture"]
    reference_momentum = reference_outlet["phase"]["mixture"]["momentum"]
    reference_turbulence = reference_outlet["phase"]["mixture"]["turbulence"]
    mixture.momentum.set_state(reference_momentum)
    mixture.turbulence.set_state(reference_turbulence)
    phase_2 = outlet.phase["phase-2"]
    phase_1_state = safe_get_state(outlet.phase["phase-1"], "phase-1 outlet backflow state")
    if isinstance(phase_1_state, Mapping) and "volume_frac_spec_method" in phase_1_state.get("multiphase", {}):
        phase_1 = outlet.phase["phase-1"]
        phase_1.multiphase.volume_frac_spec_method = "Backflow Volume Fraction"
        phase_1.multiphase.backflow_volume_fraction.option = "value"
        phase_1.multiphase.backflow_volume_fraction.value = 0.0
    phase_2.multiphase.volume_frac_spec_method = "Backflow Volume Fraction"
    phase_2.multiphase.backflow_volume_fraction.option = "value"
    phase_2.multiphase.backflow_volume_fraction.value = 1.0


def mutate_boundary(solver: Any, spec: Mapping[str, Any], base: Mapping[str, Any]) -> dict[str, Any]:
    bc = solver.settings.setup.boundary_conditions
    kind = str(spec["kind"])
    if kind == "adaptive-liquid-only-sink":
        return probe_e5_capability(solver)

    if kind == "pressure-outlet":
        bc.set_zone_type(zone_list=["bottom"], new_type="pressure-outlet")
        bc = solver.settings.setup.boundary_conditions
        outlet = bc.pressure_outlet["bottom"]
        # Apply the parent-consistent backflow form first.  That helper copies
        # the parent mixture momentum state, including its gauge pressure, so
        # the child-controlled pressure must be the final write and readback.
        set_liquid_backflow(outlet, base["boundaries"]["pressure_outlet"]["steamoutlet"])
        outlet.phase["mixture"].momentum.gauge_pressure.option = "value"
        outlet.phase["mixture"].momentum.gauge_pressure.value = float(spec["value"])
        pressure_state = safe_get_state(outlet.phase["mixture"], "pressure-outlet child readback")
        actual_pressure = pressure_state["momentum"]["gauge_pressure"]["value"]
        if abs(float(actual_pressure) - float(spec["value"])) > 1e-6:
            raise RuntimeError(
                f"pressure-outlet child readback mismatch: requested={spec['value']} actual={actual_pressure}"
            )
    elif kind == "outlet-vent":
        bc.set_zone_type(zone_list=["bottom"], new_type="outlet-vent")
        bc = solver.settings.setup.boundary_conditions
        outlet = bc.outlet_vent["bottom"]
        mixture = outlet.phase["mixture"]
        mixture.momentum.gauge_pressure.option = "value"
        mixture.momentum.gauge_pressure.value = 1_120_000.0
        mixture.momentum.loss_coefficient.option = "polynomial"
        mixture.momentum.loss_coefficient.function_of = "normal-velocity"
        mixture.momentum.loss_coefficient.polynomial.function_of = "normal-velocity"
        mixture.momentum.loss_coefficient.polynomial.coefficients = [float(spec["value"])]
        set_liquid_backflow(outlet, base["boundaries"]["pressure_outlet"]["steamoutlet"])
    elif kind in {"mass-flow-outlet", "adaptive-mass-flow-outlet"}:
        bc.set_zone_type(zone_list=["bottom"], new_type="mass-flow-outlet")
        bc = solver.settings.setup.boundary_conditions
        outlet = bc.mass_flow_outlet["bottom"]
        for phase_name, value in (("phase-1", 0.0), ("phase-2", float(spec["value"]) if kind == "mass-flow-outlet" else 0.0)):
            momentum = outlet.phase[phase_name].momentum
            momentum.mass_flow_specification = "Mass Flow Rate"
            momentum.mass_flow_rate.option = "value"
            momentum.mass_flow_rate.value = value
    else:
        raise RuntimeError(f"unsupported treatment kind: {kind}")
    return base_invariants(solver)


def set_mass_flow_command(solver: Any, value: float) -> dict[str, Any]:
    outlet = solver.settings.setup.boundary_conditions.mass_flow_outlet["bottom"]
    outlet.phase["phase-1"].momentum.mass_flow_rate.option = "value"
    outlet.phase["phase-1"].momentum.mass_flow_rate.value = 0.0
    outlet.phase["phase-2"].momentum.mass_flow_rate.option = "value"
    outlet.phase["phase-2"].momentum.mass_flow_rate.value = float(value)
    # Fluent 2025 R2 can return a sparse parent-zone state immediately after a
    # save/reopen even though the phase child readbacks are complete. Read the
    # two phase branches directly so a transiently sparse parent response does
    # not falsely block an otherwise proven phase-specific command.
    phase_1_state = safe_get_state(outlet.phase["phase-1"], "adaptive phase-1 outlet command")
    phase_2_state = safe_get_state(outlet.phase["phase-2"], "adaptive phase-2 outlet command")
    readback = {
        "phase_1_kg_s": phase_1_state["momentum"]["mass_flow_rate"]["value"],
        "phase_2_kg_s": phase_2_state["momentum"]["mass_flow_rate"]["value"],
    }
    if abs(float(readback["phase_1_kg_s"])) > 1e-12 or abs(float(readback["phase_2_kg_s"]) - value) > 1e-9:
        raise RuntimeError(f"mass-flow outlet command readback mismatch: {readback} requested={value}")
    return readback


def latest_report_value(solver: Any, path: str) -> tuple[int, float]:
    parsed = parse_report_forms(read_remote_forms(solver, path))
    iterations = parsed.get("iterations", [])
    values = parsed.get("values", [])
    if not iterations or not values:
        raise RuntimeError(f"no report samples available at {path}")
    return int(iterations[-1]), float(values[-1])


def probe_e5_capability(solver: Any) -> dict[str, Any]:
    """Prove the region/source API before any E5 solve; block if it is whole-zone only."""
    registers = solver.settings.solution.cell_registers
    name = "p7_e5_y010_probe"
    if name in set(registers.get_object_names()):
        registers.delete(name_list=[name])
    registers.create(name=name)
    register = registers[name]
    register.type.set_state(
        {
            "option": "hexahedron",
            "hexahedron": {
                "min_point": [-2.067034, 0.0, -1.469893],
                "max_point": [1.066950, 0.10, 1.066889],
                "inside": True,
            },
        }
    )
    register_state = register.get_state()
    phase_2 = solver.settings.setup.cell_zone_conditions.fluid["separator-purnanto"].phase["phase-2"]
    phase_2.sources.enable = True
    mass_terms = phase_2.sources.terms["mass"]
    mass_terms.resize(size=1)
    mass_term_state = mass_terms[0].get_state()
    capability = {
        "register_name": name,
        "register_state": register_state,
        "phase2_mass_source_state": mass_term_state,
        "source_terms_state": phase_2.sources.get_state(),
        "status": "BLOCKED_REGION_SPECIFIC_SOURCE_UNAVAILABLE",
        "reason": (
            "Fluent 2025 R2 exposes phase-2 mass source terms as a uniform fluid-zone "
            "source list (value/none); the live source tree exposes no cell-register "
            "selection or region-specific mass/momentum source binding. The approved "
            "E5 frozen 0<=y<=0.10 m source-accounting contract cannot be implemented "
            "faithfully without an explicit UDF or a human-approved model/mesh change."
        ),
    }
    try:
        registers.delete(name_list=[name])
    except Exception:
        pass
    raise RuntimeError(json.dumps(capability))


def save_pair(solver: Any, case_path: str) -> None:
    solver.settings.file.write_case(file_name=case_path)
    solver.settings.file.write_data(file_name=data_path(case_path))
    if not remote_file_exists(solver, case_path) or not remote_file_exists(solver, data_path(case_path)):
        raise RuntimeError(f"paired save failed: {case_path}")


def run_fixed_screen(solver: Any, case_paths: Mapping[str, str], capture: SessionTranscriptCapture, report_paths: Mapping[str, str], manifest: dict[str, Any], manifest_path: Path) -> None:
    start_marker = capture.mark()
    solver.settings.solution.run_calculation.iterate(iter_count=50)
    save_pair(solver, case_paths["smoke"])
    smoke_residuals = parse_residuals(capture.text_since(start_marker))
    if smoke_residuals["point_count"] < 50:
        raise RuntimeError(f"smoke residual history too short: {smoke_residuals['point_count']}")
    if not all(remote_file_exists(solver, path) for path in report_paths.values()):
        raise RuntimeError("one or more treatment report files did not appear during smoke")
    manifest["events"].append({"event": "smoke", "active_iterations": 50, "case": case_paths["smoke"]})
    write_json(manifest_path, manifest)

    solver.settings.solution.run_calculation.iterate(iter_count=200)
    save_pair(solver, case_paths["checkpoint250"])
    manifest["events"].append({"event": "checkpoint", "active_iterations": 250, "case": case_paths["checkpoint250"]})
    write_json(manifest_path, manifest)

    solver.settings.solution.run_calculation.iterate(iter_count=250)
    save_pair(solver, case_paths["final"])
    manifest["events"].append({"event": "final", "active_iterations": 500, "case": case_paths["final"]})
    write_json(manifest_path, manifest)
    residuals = parse_residuals(capture.text_since(start_marker))
    if residuals["point_count"] < 500:
        raise RuntimeError(f"full treatment residual history too short: {residuals['point_count']}")
    for name, path in report_paths.items():
        history = parse_report_forms(read_remote_forms(solver, path))
        if len(history.get("iterations", [])) < 500:
            raise RuntimeError(f"treatment report history too short for {name}: {len(history.get('iterations', []))}")
    manifest["residuals"] = residuals


def run_adaptive_screen(
    solver: Any,
    case_paths: Mapping[str, str],
    capture: SessionTranscriptCapture,
    report_paths: Mapping[str, str],
    manifest: dict[str, Any],
    manifest_path: Path,
    gain: float,
    m_star: float,
    delta_m_ref: float,
) -> None:
    if not math.isfinite(m_star) or not math.isfinite(delta_m_ref) or delta_m_ref <= 0:
        raise RuntimeError(f"invalid adaptive normalization: M*={m_star}, DeltaMref={delta_m_ref}")
    mass_report = report_paths["e0-liquid-mass-total-rfile"]
    command_log: list[dict[str, Any]] = []
    active = 0
    marker = capture.mark()
    set_mass_flow_command(solver, 0.0)
    while active < 500:
        block = min(50, 500 - active)
        solver.settings.solution.run_calculation.iterate(iter_count=block)
        active += block
        native_iteration, mass = latest_report_value(solver, mass_report)
        error = max(0.0, (mass - m_star) / delta_m_ref)
        requested = min(MAX_COMMAND_KG_S, max(0.0, gain * LIQUID_INLET_KG_S * error))
        readback = set_mass_flow_command(solver, requested)
        command_log.append(
            {
                "active_iteration": active,
                "native_iteration": native_iteration,
                "Mcurrent_kg": mass,
                "Mstar_kg": m_star,
                "DeltaMref_kg": delta_m_ref,
                "normalized_error": error,
                "requested_command_kg_s": requested,
                "clamped_command_kg_s": requested,
                "saturated": requested >= MAX_COMMAND_KG_S,
                "readback": readback,
            }
        )
        if active == 50:
            save_pair(solver, case_paths["smoke"])
        elif active == 250:
            save_pair(solver, case_paths["checkpoint250"])
        elif active == 500:
            save_pair(solver, case_paths["final"])
        manifest["events"].append(command_log[-1] | {"event": "controller_update"})
        write_json(manifest_path, manifest)
    residuals = parse_residuals(capture.text_since(marker))
    if residuals["point_count"] < 500:
        raise RuntimeError(f"adaptive residual history too short: {residuals['point_count']}")
    if not all(remote_file_exists(solver, path) for path in report_paths.values()):
        raise RuntimeError("one or more adaptive report files did not appear")
    manifest["residuals"] = residuals
    manifest["controller_updates"] = command_log


def build_paths(run_root: str, candidate: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "prepared": str(root / f"{candidate}-prepared.cas.h5"),
        "smoke": str(root / f"{candidate}-active050.cas.h5"),
        "checkpoint250": str(root / f"{candidate}-active250.cas.h5"),
        "final": str(root / f"{candidate}-active500.cas.h5"),
        "monitor_root": str(root / "monitors"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    parser.add_argument("--m-star", type=float, default=None)
    parser.add_argument("--delta-m-ref", type=float, default=None)
    args = parser.parse_args()
    spec = candidate_spec(args.candidate)
    if args.manifest.exists():
        prior = json.loads(args.manifest.read_text(encoding="utf-8"))
        if prior.get("status") not in {"BLOCKED"} or prior.get("events"):
            raise FileExistsError(f"refusing to overwrite existing treatment manifest: {args.manifest}")
    if args.residual_history.exists():
        raise FileExistsError(f"refusing to overwrite existing treatment residuals: {args.residual_history}")

    paths = build_paths(args.run_root, args.candidate)
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": args.candidate,
        "family": spec["family"],
        "mode": "discovery",
        "server_id": args.server_id,
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "run_root": args.run_root,
        "requested_active_iterations": 500,
        "controlled_value": spec["value"],
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        for path in (*paths.values(), data_path(paths["prepared"]), data_path(paths["smoke"]), data_path(paths["checkpoint250"]), data_path(paths["final"]),):
            if path.endswith("monitors"):
                continue
            if remote_file_exists(solver, path):
                raise FileExistsError(f"refusing to overwrite treatment artifact: {path}")
        if not remote_file_exists(solver, args.parent_case) or not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"parent pair not visible: {args.parent_case}, {args.parent_data}")
        remote_chdir(solver, str(PureWindowsPath(args.parent_case).parent))
        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        base = base_invariants(solver)
        if spec["family"] == "E5-PSINK":
            mutate_boundary(solver, spec, base)
        report_paths = redirect_reports(solver, paths["monitor_root"], args.candidate)
        manifest["report_files"] = report_paths
        manifest["parent_readback"] = base
        manifest["residual_configuration"] = configure_residual_history(solver, 700)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=250)
        if spec["family"] != "E5-PSINK":
            child_readback = mutate_boundary(solver, spec, base)
            manifest["child_readback_before_save"] = child_readback
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()
        solver.settings.file.write_case(file_name=paths["prepared"])
        solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]) or not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("prepared paired child save failed")
        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        manifest["child_readback_after_reopen"] = base_invariants(solver)
        write_json(args.manifest, manifest)
        if spec["family"] == "E5-PSINK":
            raise RuntimeError("E5 capability probe should have blocked before prepared solve")
        if spec["family"] == "E4-ADAPT":
            if args.m_star is None or args.delta_m_ref is None:
                raise RuntimeError("adaptive child requires --m-star and --delta-m-ref")
            run_adaptive_screen(solver, paths, capture, report_paths, manifest, args.manifest, float(spec["value"]), args.m_star, args.delta_m_ref)
        else:
            run_fixed_screen(solver, paths, capture, report_paths, manifest, args.manifest)
        residuals = manifest.pop("residuals")
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["final_case"] = paths["final"]
        manifest["final_data"] = data_path(paths["final"])
        solver.settings.file.read_case(file_name=paths["final"])
        solver.settings.file.read_data(file_name=data_path(paths["final"]))
        manifest["final_readback"] = base_invariants(solver)
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

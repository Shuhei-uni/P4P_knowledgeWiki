#!/usr/bin/env python3
"""Run one Phase-07 E5-CZ-ABSORB discovery child.

This runner starts from the exact verified active-2500 E5-CZ parent.  It does
not split, remesh, reinitialize, add an outlet, patch, or use a UDF.  The only
scientific delta is the lower-zone inventory controller and the selected
source-capacity limit.  Fluent remains the authority for the case state and
the solver; this script performs explicit readback, checkpointing, and
file-backed evidence checks around the attached discovery run.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_e5_cz import (  # noqa: E402
    as_float,
    base_invariants,
    configure_sources,
    data_path,
    density_from_case,
    fluid_names,
    read_source_tree,
    try_integrated_source_reports,
    zone_inventory,
)
from run_p7_treatment_screen import latest_report_value, parse_residuals, save_pair  # noqa: E402


LIQUID_INLET_KG_S = 116.92
GAIN = 2.0
TARGET_FACTOR = 0.50
EXPECTED_DIAMETER_M = 0.875936
PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
LOWER_REGISTER = "p7_e5_cz_lower_y010"
ADJACENT_REGISTER = "p7-e5-absorb-adjacent-y030"
BROAD_REGISTER = "p7-e5-absorb-broad-y050"
ADJACENT_MIN = [-2.067034, 0.10, -1.469893]
ADJACENT_MAX = [1.066950, 0.30, 1.066889]
BROAD_MIN = [-2.067034, 0.0, -1.469893]
BROAD_MAX = [1.066950, 0.50, 1.066889]

CAPS = {
    "P7-E5-CZ-ABSORB-G200-CAP14615": 146.15,
    "P7-E5-CZ-ABSORB-G200-CAP29230": 292.30,
    "P7-E5-CZ-ABSORB-G200-CAP58460": 584.60,
}


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


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def create_box_register(solver: Any, name: str, minimum: list[float], maximum: list[float]) -> str:
    registers = solver.settings.solution.cell_registers
    existing = list(registers.get_object_names())
    actual = next((str(item) for item in existing if normalized_name(str(item)) == normalized_name(name)), None)
    if actual is None:
        registers.create(name=name)
        actual = next(
            (str(item) for item in registers.get_object_names() if normalized_name(str(item)) == normalized_name(name)),
            None,
        )
    if actual is None:
        raise RuntimeError(f"cell register was not created: {name}")
    register = registers[actual]
    register.set_state(
        {
            "name": actual,
            "type": {
                "option": "hexahedron",
                "hexahedron": {"min_point": minimum, "max_point": maximum, "inside": True},
            },
        }
    )
    state = register.get_state()
    box = state.get("type", {}).get("hexahedron", {}) if isinstance(state, Mapping) else {}
    if state.get("type", {}).get("option") != "hexahedron" or box.get("min_point") != minimum or box.get("max_point") != maximum:
        raise RuntimeError(f"cell-register readback mismatch for {actual}: {state}")
    return actual


def verify_lower_register(solver: Any) -> str:
    registers = solver.settings.solution.cell_registers
    actual = next(
        (str(item) for item in registers.get_object_names() if normalized_name(str(item)) == normalized_name(LOWER_REGISTER)),
        None,
    )
    if actual is None:
        raise RuntimeError(f"verified lower register is missing: {LOWER_REGISTER}")
    state = registers[actual].get_state()
    expected_min = [-2.067034, 0.0, -1.469893]
    expected_max = [1.06695, 0.1, 1.066889]
    box = state.get("type", {}).get("hexahedron", {}) if isinstance(state, Mapping) else {}
    if box.get("min_point") != expected_min or box.get("max_point") != expected_max or box.get("inside") is not True:
        raise RuntimeError(f"lower register readback mismatch: {state}")
    return actual


def replace_named(branch: Any, name: str) -> Any:
    names = set(str(item) for item in branch.get_object_names())
    if name in names:
        branch.delete(name_list=[name])
    branch.create(name=name)
    return branch[name]


def configure_inventory_reports(solver: Any) -> dict[str, Any]:
    volume = solver.settings.solution.report_definitions.volume
    lower = verify_lower_register(solver)
    adjacent = create_box_register(solver, ADJACENT_REGISTER, ADJACENT_MIN, ADJACENT_MAX)
    broad = create_box_register(solver, BROAD_REGISTER, BROAD_MIN, BROAD_MAX)
    definitions = (
        ("absorb-lower-liquid-mass", "volume-mass", None, [LOWER_ZONE], "phase-2"),
        ("absorb-lower-liquid-volume", "volume-integral", "phase-2-vof", [LOWER_ZONE], "mixture"),
        ("absorb-adjacent-liquid-mass", "volume-mass", None, [adjacent], "phase-2"),
        ("absorb-broad-liquid-mass", "volume-mass", None, [broad], "phase-2"),
    )
    readbacks: list[dict[str, Any]] = []
    for name, report_type, field, selections, phase in definitions:
        report = replace_named(volume, name)
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = selections
        if field is not None:
            report.field = field
        # Fluent 2025 R2 does not expose a writable phase selector on
        # volume-integral definitions; the phase is encoded by the selected
        # phase-specific field (for example phase-2-vof).  Volume-mass
        # definitions do expose the selector and still require it.
        if report_type != "volume-integral":
            report.phase = phase
        for key, value in (
            ("per_selection", False),
            ("average_over", 1),
            ("create_report_file", True),
            ("create_report_plot", True),
        ):
            set_optional(report, key, value)
        state = safe_get_state(report, f"absorber report {name}")
        if (
            not isinstance(state, Mapping)
            or state.get("report_type") != report_type
            or state.get("cell_zones") != selections
            or (report_type != "volume-integral" and state.get("phase") != phase)
        ):
            raise RuntimeError(f"absorber report readback mismatch for {name}: {state}")
        if field is not None and state.get("field") != field:
            raise RuntimeError(f"absorber report field readback mismatch for {name}: {state}")
        readbacks.append({"name": name, "state": state})
    return {
        "lower_register": lower,
        "adjacent_register": adjacent,
        "broad_register": broad,
        "definitions": readbacks,
    }


def resolve_report_path(configured: str, parent_dir: str) -> str:
    path = PureWindowsPath(str(configured))
    if path.is_absolute():
        return str(path)
    return str(PureWindowsPath(parent_dir) / path)


def parent_history_readback(solver: Any, parent_dir: str) -> dict[str, Any]:
    report = solver.settings.solution.monitor.report_files["e0-liquid-mass-total-rfile"]
    state = safe_get_state(report, "parent total-liquid report file")
    configured = state.get("file_name") if isinstance(state, Mapping) else None
    if not isinstance(configured, str) or not configured.strip():
        raise RuntimeError(f"parent liquid report path is not readable: {state}")
    resolved = resolve_report_path(configured, parent_dir)
    if not remote_file_exists(solver, resolved):
        # The parent case/data pair is the authoritative restart state for this
        # family.  A prior failed child can leave the parent's historical
        # report file absent from the live Fluent session even though the
        # loaded parent inventory is readable.  Preserve that evidence gap in
        # the manifest, but do not prevent an independent child from starting
        # when its controller baseline comes from the live zone inventory.
        return {
            "status": "MISSING",
            "configured_file_name": configured,
            "resolved_file_name": resolved,
            "latest_native_iteration": None,
            "latest_total_liquid_mass_kg": None,
            "history": [],
            "missing_info": "Parent total-liquid report history was not visible after the previous child failure; live parent zone inventory is used for M_L0.",
        }
    native_iteration, mass = latest_report_value(solver, resolved)
    return {
        "configured_file_name": configured,
        "resolved_file_name": resolved,
        "latest_native_iteration": native_iteration,
        "latest_total_liquid_mass_kg": mass,
        "history": parse_report_forms(read_remote_forms(solver, resolved)),
    }


def redirect_all_reports(solver: Any, monitor_root: str, candidate: str) -> dict[str, str]:
    ensure_remote_directory(solver, monitor_root)
    reports = solver.settings.solution.monitor.report_files
    names = sorted(str(item) for item in reports.get_object_names())
    required = {
        "e0-liquid-mass-total-rfile",
        "e0-liquid-volume-total-rfile",
        "absorb-lower-liquid-mass-rfile",
        "absorb-lower-liquid-volume-rfile",
        "absorb-adjacent-liquid-mass-rfile",
        "absorb-broad-liquid-mass-rfile",
    }
    required.update(
        f"e0-flux-{phase}-{surface}-rfile"
        for phase in ("mixture", "phase1", "phase2")
        for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")
    )
    missing = sorted(required - set(names))
    if missing:
        raise RuntimeError(f"required absorber report files are missing: {missing}; available={names}")
    paths: dict[str, str] = {}
    for name in names:
        path = str(PureWindowsPath(monitor_root) / f"{candidate}-{name}.out")
        if remote_file_exists(solver, path):
            raise FileExistsError(f"refusing to overwrite absorber report file: {path}")
        reports[name].file_name = path
        state = safe_get_state(reports[name], f"report file {name}")
        actual = state.get("file_name") if isinstance(state, Mapping) else None
        if not isinstance(actual, str) or PureWindowsPath(actual).name != PureWindowsPath(path).name:
            raise RuntimeError(f"report path readback mismatch for {name}: requested={path}; actual={actual!r}")
        paths[name] = path
        state = safe_get_state(reports[name], f"report file definition links {name}")
        definitions = state.get("report_defs") if isinstance(state, Mapping) else None
        if isinstance(definitions, list):
            for definition in definitions:
                if isinstance(definition, str) and definition not in paths:
                    # In Fluent 2025 R2, newly created volume-report monitor
                    # objects may retain generated names (report-file-1, ...)
                    # while their report_defs field carries the scientific
                    # definition name.  Expose both keys so downstream
                    # evidence checks can address either representation.
                    paths[definition] = path
    return paths


def build_paths(run_root: str, candidate: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "pre_change_recovery": str(root / f"{candidate}-pre-change-recovery.cas.h5"),
        "prepared": str(root / f"{candidate}-prepared.cas.h5"),
        "child_start": str(root / f"{candidate}-active000.cas.h5"),
        "smoke": str(root / f"{candidate}-active050.cas.h5"),
        "checkpoint100": str(root / f"{candidate}-active100.cas.h5"),
        "checkpoint250": str(root / f"{candidate}-active250.cas.h5"),
        "final": str(root / f"{candidate}-active500.cas.h5"),
        "monitor_root": str(root / "monitors"),
    }


def controller_command(mass_kg: float, m0_kg: float, cap_kg_s: float) -> dict[str, Any]:
    target = TARGET_FACTOR * m0_kg
    error = max(0.0, (mass_kg - target) / target) if target > 0 else float("nan")
    requested = max(0.0, GAIN * LIQUID_INLET_KG_S * error) if math.isfinite(error) else float("nan")
    clamped = min(cap_kg_s, requested) if math.isfinite(requested) else float("nan")
    return {
        "M_L_kg": mass_kg,
        "M_L0_kg": m0_kg,
        "M_L_target_kg": target,
        "normalized_error": error,
        "gain": GAIN,
        "source_cap_kg_s": cap_kg_s,
        "requested_command_kg_s": requested,
        "clamped_command_kg_s": clamped,
        "saturated": bool(math.isfinite(clamped) and clamped >= cap_kg_s - 1e-12),
    }


def source_audit(integrated: Mapping[str, Any], requested: float) -> dict[str, Any]:
    available = integrated.get("available", {})
    record = available.get("phase2_mass") if isinstance(available, Mapping) else None
    if not isinstance(record, Mapping) or "integral" not in record:
        raise RuntimeError(f"phase-2 get_sum source audit unavailable: {integrated}")
    measured = as_float(record["integral"])
    expected = -requested
    return {
        "field": record.get("field"),
        "reduction": record.get("reduction"),
        "measured_kg_s": measured,
        "expected_kg_s": expected,
        "absolute_error_kg_s": abs(measured - expected),
    }


def source_invariant_summary(solver: Any) -> dict[str, Any]:
    tree = read_source_tree(solver)
    parent = tree[PARENT_ZONE]
    lower = tree[LOWER_ZONE]
    phase1_off = parent["phase-1"].get("enable") is False and lower["phase-1"].get("enable") is False
    parent_off = all(parent[key].get("enable") is False for key in ("phase-1", "phase-2", "mixture"))
    lower_mass_on = lower["phase-2"].get("enable") is True
    lower_mixture_on = lower["mixture"].get("enable") is True
    if not phase1_off or not parent_off or not lower_mass_on or not lower_mixture_on:
        raise RuntimeError(f"source invariant mismatch: {tree}")
    return {
        "phase1_direct_mass_source_off": phase1_off,
        "parent_sources_off": parent_off,
        "lower_phase2_mass_source_on": lower_mass_on,
        "lower_mixture_momentum_source_on": lower_mixture_on,
        "tree": tree,
    }


def run_discovery(
    solver: Any,
    paths: Mapping[str, str],
    report_paths: Mapping[str, str],
    capture: SessionTranscriptCapture,
    manifest: dict[str, Any],
    manifest_path: Path,
    cap_kg_s: float,
    m0_kg: float,
    density_kg_m3: float,
) -> None:
    initial = zone_inventory(solver, density_kg_m3)
    if not math.isfinite(m0_kg) or m0_kg <= 0:
        raise RuntimeError(f"invalid parent lower-zone mass M_L0={m0_kg}")
    initial_command = controller_command(initial["phase2_mass_kg"], m0_kg, cap_kg_s)
    initial_source = configure_sources(
        solver,
        -initial_command["clamped_command_kg_s"] / initial["geometric_volume_m3"],
        initial["velocity_basis_m_s"],
    )
    initial_integrated = try_integrated_source_reports(solver)
    initial_audit = source_audit(initial_integrated, initial_command["clamped_command_kg_s"])
    initial_event = {
        "event": "controller_update",
        "active_iteration": 0,
        "native_iteration": None,
        **initial_command,
        "lower_inventory": initial,
        "source": initial_source,
        "source_audit": initial_audit,
        "direct_phase1_source_off": source_invariant_summary(solver)["phase1_direct_mass_source_off"],
    }
    manifest["initial_controller"] = initial_event
    manifest["events"].append(initial_event)
    save_pair(solver, paths["child_start"])
    manifest["events"].append({"event": "child_start_saved", "active_iteration": 0, "case": paths["child_start"]})
    write_json(manifest_path, manifest)

    marker = capture.mark()
    active = 0
    while active < 500:
        block = min(50, 500 - active)
        solver.settings.solution.run_calculation.iterate(iter_count=block)
        active += block
        console = capture.text_since(marker)
        if re.search(r"floating point exception|Divergence detected in AMG solver|fatal error", console, re.I):
            manifest["last_valid_active_iteration"] = active - block
            manifest["terminal_solver_diagnostics"] = {
                "active_iteration": active,
                "console_tail": console[-16000:],
            }
            write_json(manifest_path, manifest)
            raise RuntimeError(f"solver divergence/fatal diagnostic during block ending at active {active}")

        native_iteration, total_mass = latest_report_value(solver, report_paths["e0-liquid-mass-total-rfile"])
        inventory = zone_inventory(solver, density_kg_m3)
        command = controller_command(inventory["phase2_mass_kg"], m0_kg, cap_kg_s)
        source = configure_sources(
            solver,
            -command["clamped_command_kg_s"] / inventory["geometric_volume_m3"],
            inventory["velocity_basis_m_s"],
        )
        integrated = try_integrated_source_reports(solver)
        audit = source_audit(integrated, command["clamped_command_kg_s"])
        event = {
            "event": "controller_update",
            "active_iteration": active,
            "native_iteration": native_iteration,
            "total_liquid_mass_kg": total_mass,
            **command,
            "lower_inventory": inventory,
            "source": source,
            "source_audit": audit,
            "direct_phase1_source_off": source_invariant_summary(solver)["phase1_direct_mass_source_off"],
        }
        manifest["events"].append(event)
        manifest["warnings"] = {
            "floating_point_or_fatal_matches": len(re.findall(r"floating point exception|fatal error", console, re.I)),
            "divergence_matches": len(re.findall(r"Divergence detected in AMG solver", console, re.I)),
            "console_tail": console[-8000:],
        }
        write_json(manifest_path, manifest)

        if active == 50:
            save_pair(solver, paths["smoke"])
            if not all(remote_file_exists(solver, path) for path in report_paths.values()):
                raise RuntimeError("one or more absorber report files did not appear during smoke")
            manifest["smoke"] = {
                "active_iterations": 50,
                "case": paths["smoke"],
                "source_audit": audit,
                "source_invariants": source_invariant_summary(solver),
            }
            write_json(manifest_path, manifest)
        elif active == 100:
            save_pair(solver, paths["checkpoint100"])
        elif active == 250:
            save_pair(solver, paths["checkpoint250"])
        elif active == 500:
            save_pair(solver, paths["final"])

    residuals = parse_residuals(capture.text_since(marker))
    if residuals["point_count"] < 500:
        raise RuntimeError(f"absorber residual history too short: {residuals['point_count']}")
    histories: dict[str, Any] = {}
    for name, path in report_paths.items():
        if not remote_file_exists(solver, path):
            raise RuntimeError(f"required absorber report file is missing after run: {path}")
        history = parse_report_forms(read_remote_forms(solver, path))
        if history["points"] < 500:
            raise RuntimeError(f"absorber report history too short for {name}: {history['points']}")
        histories[name] = {"points": history["points"], "first_iteration": history["iterations"][0], "last_iteration": history["iterations"][-1]}
    manifest["report_history_summary"] = histories
    manifest["residuals"] = residuals
    manifest["controller_updates"] = len([event for event in manifest["events"] if event.get("event") == "controller_update"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--candidate", required=True, choices=tuple(CAPS))
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--residual-history", required=True, type=Path)
    args = parser.parse_args()
    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local absorber evidence")

    candidate = args.candidate
    cap_kg_s = CAPS[candidate]
    paths = build_paths(args.run_root, candidate)
    artifact_paths = [path for key, path in paths.items() if key != "monitor_root"]
    artifact_paths += [data_path(path) for path in artifact_paths]
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": candidate,
        "run_id": args.manifest.stem,
        "family": "E5-CZ-ABSORB",
        "mode": "attached-discovery",
        "server_id": args.server_id,
        "server_ip": os.getenv("STUDENT_IP", "unknown"),
        "server_ref": f"student@{os.getenv('STUDENT_IP', 'unknown')}",
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "run_root": args.run_root,
        "gain": GAIN,
        "source_cap_kg_s": cap_kg_s,
        "target_factor": TARGET_FACTOR,
        "controller_update_interval": 50,
        "requested_active_iterations": 500,
        "artifact_paths": paths,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        existing = [path for path in artifact_paths if remote_file_exists(solver, path)]
        if existing:
            raise FileExistsError(f"refusing to overwrite remote absorber artifacts: {existing}")
        if not remote_file_exists(solver, args.parent_case) or not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"exact active-2500 parent pair is not visible: {args.parent_case}; {args.parent_data}")
        parent_dir = str(PureWindowsPath(args.parent_case).parent)
        remote_chdir(solver, parent_dir)
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        names = fluid_names(solver)
        if names != [LOWER_ZONE, PARENT_ZONE]:
            raise RuntimeError(f"exact parent topology mismatch: {names}")
        parent_base = base_invariants(solver)
        parent_density = density_from_case(solver)
        parent_inventory = zone_inventory(solver, parent_density)
        parent_history = parent_history_readback(solver, parent_dir)
        runtime_state = safe_get_state(solver.settings.solution.run_calculation, "parent runtime state")
        manifest["parent_readback"] = {
            "fluid_zones": names,
            "base_invariants": parent_base,
            "density_kg_m3": parent_density,
            "lower_inventory": parent_inventory,
            "history": parent_history,
            "runtime_state": runtime_state,
            "stale_runtime_counter_note": "The completed parent package records a stale post-reopen runtime counter; report histories are authoritative for native coordinates.",
        }
        manifest["M_L0_kg"] = parent_inventory["phase2_mass_kg"]
        manifest["M_L_target_kg"] = TARGET_FACTOR * parent_inventory["phase2_mass_kg"]
        manifest["liquid_density_kg_m3"] = parent_density
        write_json(args.manifest, manifest)

        save_pair(solver, paths["pre_change_recovery"])
        manifest["events"].append({"event": "pre_change_recovery_saved", "case": paths["pre_change_recovery"]})
        manifest["monitor_definitions"] = configure_inventory_reports(solver)
        manifest["report_files"] = redirect_all_reports(solver, paths["monitor_root"], candidate)
        manifest["residual_configuration"] = configure_residual_history(solver, 800)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=50)
        write_json(args.manifest, manifest)

        # Save/reopen is the hard implementation gate before source-active data.
        # The parent has already been preserved above; this pair is the prepared
        # source/readout child and remains distinct from the final endpoint.
        source_off_tree = read_source_tree(solver)
        manifest["pre_source_tree"] = source_off_tree
        solver.settings.file.write_case(file_name=paths["prepared"])
        solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]) or not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("prepared absorber pair was not saved")
        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        reopened = fluid_names(solver)
        if reopened != [LOWER_ZONE, PARENT_ZONE]:
            raise RuntimeError(f"prepared save/reopen topology mismatch: {reopened}")
        manifest["prepared_reopen"] = {
            "fluid_zones": reopened,
            "base_invariants": base_invariants(solver),
            "source_tree": read_source_tree(solver),
        }
        # Fluent 2025 R2 can restore inherited report paths on reopen; apply the
        # child-local destinations again and prove the readback before solving.
        manifest["report_files_after_reopen"] = redirect_all_reports(solver, paths["monitor_root"], candidate)
        write_json(args.manifest, manifest)

        run_discovery(
            solver,
            paths=paths,
            report_paths=manifest["report_files_after_reopen"],
            capture=capture,
            manifest=manifest,
            manifest_path=args.manifest,
            cap_kg_s=cap_kg_s,
            m0_kg=float(manifest["M_L0_kg"]),
            density_kg_m3=float(parent_density),
        )
        residuals = manifest.pop("residuals")
        write_json(args.residual_history, residuals)
        manifest["residual_history"] = str(args.residual_history)
        manifest["transcript"] = str(capture_path)
        manifest["final_case"] = paths["final"]
        manifest["final_data"] = data_path(paths["final"])
        solver.settings.file.read_case(file_name=paths["final"])
        solver.settings.file.read_data(file_name=data_path(paths["final"]))
        manifest["final_readback"] = {
            "fluid_zones": fluid_names(solver),
            "base_invariants": base_invariants(solver),
            "source_invariants": source_invariant_summary(solver),
            "source_tree": read_source_tree(solver),
        }
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

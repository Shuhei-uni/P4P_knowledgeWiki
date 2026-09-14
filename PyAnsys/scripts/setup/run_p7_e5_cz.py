#!/usr/bin/env python3
"""Build, prove, and run one Phase-07 E5-CZ discovery child.

The child is always rebuilt from the exact E0 iteration-500 case/data pair.
The native Fluent cell-zone split is performed in the live session, then a
uniform phase-2 mass source and matched mixture-momentum source are applied to
the marked lower fluid zone.  This is deliberately a separate runner from the
fixed-mesh treatment screen: it records the topology delta and never treats a
whole-domain source as a substitute for the lower-zone source contract.
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
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history, ensure_remote_directory  # noqa: E402
from run_p7_treatment_screen import (  # noqa: E402
    base_invariants,
    data_path,
    latest_report_value,
    parse_report_forms,
    parse_residuals,
    read_remote_forms,
    redirect_reports,
    save_pair,
)


M_STAR_DEFAULT = 149.424869
DELTA_M_REF_DEFAULT = 223.250694
LIQUID_INLET_KG_S = 116.92
MAX_COMMAND_KG_S = 146.15
EXPECTED_TOTAL_CELLS = 342_609
EXPECTED_TOTAL_FACES = 1_647_633
EXPECTED_SOLVER_NODES = 1_046_255
EXPECTED_LOWER_CELLS = 3_794
EXPECTED_PARENT_CELLS = 338_815
REGISTER_NAME = "p7-e5-cz-lower-y010"
PARENT_ZONE = "separator-purnanto"
LOWER_ZONE = "p7-e5-lower-y010"
MIN_POINT = [-2.067034, 0.0, -1.469893]
MAX_POINT = [1.066950, 0.10, 1.066889]
GAINS = {"P7-E5-CZ-G025": 0.25, "P7-E5-CZ-G050": 0.50, "P7-E5-CZ-G100": 1.00}


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def as_float(value: Any) -> float:
    if isinstance(value, Mapping):
        if "Net" in value:
            value = value["Net"]
        elif "value" in value:
            value = value["value"]
    return float(value)


def fluid_names(solver: Any) -> list[str]:
    state = safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones")
    fluid = state.get("fluid", {}) if isinstance(state, Mapping) else {}
    return sorted(str(name) for name in fluid if str(name) != "settings")


def create_lower_register(solver: Any) -> tuple[str, dict[str, Any]]:
    registers = solver.settings.solution.cell_registers
    for name in list(registers.get_object_names()):
        if normalized_name(str(name)) == normalized_name(REGISTER_NAME):
            registers.delete(name_list=[name])
    registers.create(name=REGISTER_NAME)
    names = list(registers.get_object_names())
    actual = next((str(name) for name in names if normalized_name(str(name)) == normalized_name(REGISTER_NAME)), None)
    if actual is None:
        raise RuntimeError(f"cell register was not created; names={names}")
    register = registers[actual]
    register.set_state(
        {
            "name": actual,
            "type": {
                "option": "hexahedron",
                "hexahedron": {"min_point": MIN_POINT, "max_point": MAX_POINT, "inside": True},
            },
        }
    )
    state = register.get_state()
    box = nested(state, "type", "hexahedron")
    if nested(state, "type", "option") != "hexahedron" or box.get("min_point") != MIN_POINT or box.get("max_point") != MAX_POINT:
        raise RuntimeError(f"register readback mismatch: {state}")
    return actual, state


def split_lower_zone(solver: Any, capture: SessionTranscriptCapture) -> dict[str, Any]:
    before = fluid_names(solver)
    if PARENT_ZONE not in before:
        raise RuntimeError(f"parent fluid zone missing before split: {before}")
    register, register_state = create_lower_register(solver)
    marker = capture.mark()
    solver.settings.mesh.modify_zones.sep_cell_zone_mark(
        cell_zone_name=PARENT_ZONE,
        register=register,
        move_faces=True,
    )
    split_console = capture.text_since(marker)
    after_mark = fluid_names(solver)
    generated = [name for name in after_mark if name not in before and name != LOWER_ZONE]
    if len(generated) != 1:
        raise RuntimeError(f"expected one marked child fluid zone, before={before}, after={after_mark}, generated={generated}")
    generated_zone = generated[0]
    solver.settings.mesh.modify_zones.zone_name(zone_name=generated_zone, new_name=LOWER_ZONE)
    after_rename = fluid_names(solver)
    if set(after_rename) != {PARENT_ZONE, LOWER_ZONE}:
        raise RuntimeError(f"split/rename zone readback mismatch: {after_rename}")

    # These native commands provide the durable transcript evidence for the
    # topology delta and mesh check.  The expected counts are checked against
    # the technical split proof and recorded again for every scientific child.
    mesh_marker = capture.mark()
    solver.settings.mesh.size_info()
    solver.settings.mesh.check()
    mesh_console = capture.text_since(mesh_marker)
    observed_counts = {
        "total_cells": EXPECTED_TOTAL_CELLS if re.search(r"342609|342,609", split_console + mesh_console) else None,
        "total_faces": EXPECTED_TOTAL_FACES if re.search(r"1647633|1,647,633", split_console + mesh_console) else None,
        "solver_nodes": EXPECTED_SOLVER_NODES if re.search(r"1046255|1,046,255", split_console + mesh_console) else None,
        "lower_cells": EXPECTED_LOWER_CELLS if re.search(r"3794|3,794", split_console + mesh_console) else None,
        "parent_cells": EXPECTED_PARENT_CELLS if re.search(r"338815|338,815", split_console + mesh_console) else None,
    }
    if any(value is None for value in observed_counts.values()):
        raise RuntimeError(f"split mesh count evidence incomplete: {observed_counts}; transcript={split_console + mesh_console}")
    return {
        "register_name": register,
        "register_state": register_state,
        "before_fluid_zones": before,
        "generated_zone_before_rename": generated_zone,
        "after_fluid_zones": after_rename,
        "move_faces": True,
        "observed_counts": observed_counts,
        "split_console": split_console,
        "mesh_console": mesh_console,
    }


def source_terms(zone: Any, phase_name: str, terms: tuple[str, ...]) -> dict[str, Any]:
    phase = zone.phase[phase_name]
    phase.sources.enable = True
    values: dict[str, Any] = {}
    for term_name in terms:
        term = phase.sources.terms[term_name]
        term.resize(size=1)
        values[term_name] = term[0].get_state()
    return values


def set_source_term(zone: Any, phase_name: str, term_name: str, value: float) -> dict[str, Any]:
    phase = zone.phase[phase_name]
    phase.sources.enable = True
    term = phase.sources.terms[term_name]
    term.resize(size=1)
    term[0].set_state({"option": "value", "value": float(value)})
    state = safe_get_state(term[0], f"{phase_name}.{term_name} source term")
    option = state.get("option") if isinstance(state, Mapping) else None
    actual = state.get("value") if isinstance(state, Mapping) else None
    if option != "value" or actual is None or abs(float(actual) - float(value)) > 1e-12:
        raise RuntimeError(f"source term readback mismatch for {phase_name}.{term_name}: requested={value}, state={state}")
    return state


def lower_volume_and_velocity(solver: Any) -> dict[str, Any]:
    reports = solver.settings.results.report.volume_integrals
    geometry = reports.get_volume(
        cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]}, cell_function="cell-volume", current_domain="mixture"
    )
    volume = as_float(geometry)
    if not math.isfinite(volume) or volume <= 0:
        raise RuntimeError(f"invalid lower-zone volume: {geometry}")
    values: dict[str, Any] = {"geometric_volume_m3": volume, "velocity_integrals": {}, "velocity_basis_m_s": {}}
    for component in ("x", "y", "z"):
        field = f"phase-2-{component}-velocity"
        integral_value = reports.compute_volume_integral(
            cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]}, cell_function=field, current_domain="mixture"
        )
        integral = as_float(integral_value)
        values["velocity_integrals"][component] = integral
        values["velocity_basis_m_s"][component] = integral / volume
    vof = reports.compute_volume_integral(
        cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]}, cell_function="phase-2-vof", current_domain="mixture"
    )
    values["phase2_volume_m3"] = as_float(vof)
    return values


def zone_inventory(solver: Any, density_kg_m3: float) -> dict[str, Any]:
    lower = lower_volume_and_velocity(solver)
    lower["phase2_mass_kg"] = lower["phase2_volume_m3"] * density_kg_m3
    lower["liquid_density_kg_m3"] = density_kg_m3
    return lower


def read_source_tree(solver: Any) -> dict[str, Any]:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    result: dict[str, Any] = {}
    for zone_name in (PARENT_ZONE, LOWER_ZONE):
        zone = cells[zone_name]
        result[zone_name] = {
            "phase-1": safe_get_state(zone.phase["phase-1"].sources, f"{zone_name} phase-1 sources"),
            "phase-2": safe_get_state(zone.phase["phase-2"].sources, f"{zone_name} phase-2 sources"),
            "mixture": safe_get_state(zone.phase["mixture"].sources, f"{zone_name} mixture sources"),
        }
    return result


def configure_sources(solver: Any, mass_source: float, velocity_basis: Mapping[str, float]) -> dict[str, Any]:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    parent = cells[PARENT_ZONE]
    lower = cells[LOWER_ZONE]
    # No source is allowed in the parent zone, the vapor phase, or the
    # lower-zone phase-1 branch.
    parent.phase["phase-1"].sources.enable = False
    parent.phase["phase-2"].sources.enable = False
    parent.phase["mixture"].sources.enable = False
    lower.phase["phase-1"].sources.enable = False
    mass_state = set_source_term(lower, "phase-2", "mass", mass_source)
    lower.phase["mixture"].sources.enable = True
    momentum_states = {
        component: set_source_term(lower, "mixture", f"{component}-momentum", mass_source * float(velocity_basis[component]))
        for component in ("x", "y", "z")
    }
    tree = read_source_tree(solver)
    if tree[PARENT_ZONE]["phase-2"].get("enable") is not False:
        raise RuntimeError(f"parent phase-2 source was not disabled: {tree}")
    if tree[LOWER_ZONE]["phase-1"].get("enable") is not False:
        raise RuntimeError(f"lower phase-1 source was not disabled: {tree}")
    return {
        "mass_source_kg_m3_s": mass_source,
        "momentum_source_N_m3": {component: mass_source * float(velocity_basis[component]) for component in ("x", "y", "z")},
        "phase2_mass_term": mass_state,
        "momentum_terms": momentum_states,
        "source_tree": tree,
    }


def disable_sources(solver: Any) -> dict[str, Any]:
    cells = solver.settings.setup.cell_zone_conditions.fluid
    for zone_name in (PARENT_ZONE, LOWER_ZONE):
        for phase_name in ("phase-1", "phase-2", "mixture"):
            cells[zone_name].phase[phase_name].sources.enable = False
    return read_source_tree(solver)


def try_integrated_source_reports(solver: Any) -> dict[str, Any]:
    reports = solver.settings.results.report.volume_integrals
    # Fluent exposes the phase-specific user mass source as a mass-flow field
    # in this Mixture model. Use the mass-flow reduction (get_sum), not
    # compute_volume_integral: the latter applies a volume reduction to a field
    # whose quantity is already mass flow and returns a misleading value.
    # The corresponding mixture momentum source terms are not exposed as
    # volume-integral field functions in 2025 R2, so their integrated values
    # remain auditable from the read-back uniform source multiplied by the
    # measured lower-zone volume.
    candidates = {"phase2_mass": "phase-2-user-mass-source"}
    result: dict[str, Any] = {"available": {}, "errors": {}}
    for label, field in candidates.items():
        try:
            value = reports.get_sum(
                cell_zones=[LOWER_ZONE], locations={"geometry": [LOWER_ZONE]}, cell_function=field, current_domain="mixture"
            )
            result["available"][label] = {"field": field, "reduction": "get_sum", "integral": value}
        except Exception as exc:
            result["errors"][label] = f"{type(exc).__name__}: {exc}"
    return result


def build_paths(run_root: str, candidate: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "recovery": str(root / f"{candidate}-pre-split-recovery.cas.h5"),
        "split_parent": str(root / f"{candidate}-split-source-off.cas.h5"),
        "prepared": str(root / f"{candidate}-prepared.cas.h5"),
        "smoke": str(root / f"{candidate}-active050.cas.h5"),
        "checkpoint250": str(root / f"{candidate}-active250.cas.h5"),
        "final": str(root / f"{candidate}-active500.cas.h5"),
        "monitor_root": str(root / "monitors"),
    }


def density_from_case(solver: Any) -> float:
    state = safe_get_state(solver.settings.setup.materials.fluid["water-liquid-at-psep"], "liquid material")
    value = nested(state, "density", "value")
    if value is None:
        raise RuntimeError(f"liquid density was not readable: {state}")
    return float(value)


def run_controller(
    solver: Any,
    paths: Mapping[str, str],
    capture: SessionTranscriptCapture,
    report_paths: Mapping[str, str],
    manifest: dict[str, Any],
    manifest_path: Path,
    gain: float,
    m_star: float,
    delta_m_ref: float,
    density_kg_m3: float,
) -> None:
    if not math.isfinite(m_star) or not math.isfinite(delta_m_ref) or delta_m_ref <= 0:
        raise RuntimeError(f"invalid adaptive normalization: M*={m_star}, DeltaMref={delta_m_ref}")
    mass_report = report_paths["e0-liquid-mass-total-rfile"]
    active = 0
    commands: list[dict[str, Any]] = []
    # At E0-500 the normalized error is zero by definition.  This first block
    # is therefore the declared 50-iteration smoke with zero source, after
    # which the first auditable controller update is applied.
    initial_inventory = zone_inventory(solver, density_kg_m3)
    initial_basis = initial_inventory["velocity_basis_m_s"]
    initial_source = configure_sources(solver, 0.0, initial_basis)
    manifest["initial_source"] = initial_source
    marker = capture.mark()
    while active < 500:
        block = min(50, 500 - active)
        solver.settings.solution.run_calculation.iterate(iter_count=block)
        active += block
        recent_console = capture.text_since(marker)
        if re.search(r"floating point exception|Divergence detected in AMG solver", recent_console, re.I):
            manifest["terminal_solver_diagnostics"] = {
                "active_iteration": active,
                "native_iteration_hint": 500 + active,
                "last_console_tail": recent_console[-12000:],
            }
            manifest["last_valid_active_iteration"] = active - block
            write_json(manifest_path, manifest)
            raise RuntimeError(f"Fluent solver divergence/floating-point exception during active block ending at {active}")
        native_iteration, current_mass = latest_report_value(solver, mass_report)
        normalized_error = max(0.0, (current_mass - m_star) / delta_m_ref)
        requested = min(MAX_COMMAND_KG_S, max(0.0, gain * LIQUID_INLET_KG_S * normalized_error))
        inventory = zone_inventory(solver, density_kg_m3)
        basis = inventory["velocity_basis_m_s"]
        source = configure_sources(solver, -requested / inventory["geometric_volume_m3"], basis)
        integrated = try_integrated_source_reports(solver)
        command = {
            "active_iteration": active,
            "native_iteration": native_iteration,
            "Mcurrent_kg": current_mass,
            "Mstar_kg": m_star,
            "DeltaMref_kg": delta_m_ref,
            "normalized_error": normalized_error,
            "gain": gain,
            "requested_command_kg_s": requested,
            "clamped_command_kg_s": requested,
            "saturated": requested >= MAX_COMMAND_KG_S,
            "lower_inventory": inventory,
            "source": source,
            "integrated_source_reports": integrated,
            "analytical_integrated_phase2_source_kg_s": -requested,
        }
        commands.append(command)
        manifest["events"].append({"event": "controller_update", **command})
        write_json(manifest_path, manifest)
        if active == 50:
            save_pair(solver, paths["smoke"])
        elif active == 250:
            save_pair(solver, paths["checkpoint250"])
        elif active == 500:
            save_pair(solver, paths["final"])
    residuals = parse_residuals(capture.text_since(marker))
    if residuals["point_count"] < 500:
        raise RuntimeError(f"E5-CZ residual history too short: {residuals['point_count']}")
    if not all(remote_file_exists(solver, path) for path in report_paths.values()):
        raise RuntimeError("one or more E5-CZ report files did not appear")
    manifest["controller_updates"] = commands
    manifest["residuals"] = residuals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--candidate", required=True, choices=tuple(GAINS))
    parser.add_argument("--parent-case", required=True)
    parser.add_argument("--parent-data", required=True)
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--residual-history", type=Path, required=True)
    parser.add_argument("--m-star", type=float, default=M_STAR_DEFAULT)
    parser.add_argument("--delta-m-ref", type=float, default=DELTA_M_REF_DEFAULT)
    args = parser.parse_args()
    gain = GAINS[args.candidate]
    paths = build_paths(args.run_root, args.candidate)
    if args.manifest.exists() or args.residual_history.exists():
        raise FileExistsError("refusing to overwrite local E5-CZ evidence")
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": args.candidate,
        "run_id": args.manifest.stem,
        "family": "E5-CZ",
        "mode": "attached-discovery",
        "server_id": args.server_id,
        "parent_case": args.parent_case,
        "parent_data": args.parent_data,
        "run_root": args.run_root,
        "gain": gain,
        "requested_active_iterations": 500,
        "controller_update_interval": 50,
        "m_star_kg": args.m_star,
        "delta_m_ref_kg": args.delta_m_ref,
        "events": [],
    }
    write_json(args.manifest, manifest)
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True)
        ensure_remote_directory(solver, args.run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        artifact_paths = [
            paths[key]
            for key in ("recovery", "split_parent", "prepared", "smoke", "checkpoint250", "final")
        ]
        artifact_paths += [data_path(path) for path in artifact_paths]
        artifact_paths += [str(PureWindowsPath(paths["monitor_root"]) / f"{args.candidate}-placeholder.out")]
        existing = [path for path in artifact_paths if remote_file_exists(solver, path)]
        if existing:
            raise FileExistsError(f"refusing to overwrite remote E5-CZ artifacts: {existing}")
        if not remote_file_exists(solver, args.parent_case) or not remote_file_exists(solver, args.parent_data):
            raise FileNotFoundError(f"exact E0-500 parent pair is not visible: {args.parent_case}, {args.parent_data}")
        remote_chdir(solver, str(PureWindowsPath(args.parent_case).parent))
        capture_path = args.residual_history.with_name(args.residual_history.stem + "-transcript.txt")
        capture = SessionTranscriptCapture(solver, stream_path=capture_path)
        capture.start()

        solver.settings.file.read_case(file_name=args.parent_case)
        solver.settings.file.read_data(file_name=args.parent_data)
        base = base_invariants(solver)
        manifest["parent_readback"] = base
        manifest["liquid_density_kg_m3"] = density_from_case(solver)
        save_pair(solver, paths["recovery"])
        manifest["events"].append({"event": "pre_split_recovery", "case": paths["recovery"]})
        split = split_lower_zone(solver, capture)
        manifest["mesh_split"] = split
        disable_sources(solver)
        split_source_readback = read_source_tree(solver)
        manifest["split_source_off_readback"] = split_source_readback
        save_pair(solver, paths["split_parent"])
        manifest["events"].append({"event": "split_source_off_parent", "case": paths["split_parent"]})

        report_paths = redirect_reports(solver, paths["monitor_root"], args.candidate)
        manifest["report_files"] = report_paths
        manifest["residual_configuration"] = configure_residual_history(solver, 700)
        manifest["autosave_configuration"] = configure_autosave(solver, args.run_root, data_frequency=250)
        manifest["source_contract"] = {
            "parent_zone": PARENT_ZONE,
            "lower_zone": LOWER_ZONE,
            "phase2_mass_only": True,
            "mixture_momentum_components": ["x", "y", "z"],
            "patch_reset_route": "excluded",
        }
        write_json(args.manifest, manifest)

        # Save/reopen is a hard implementation gate before any source-active
        # iteration.  The split parent is source-off and is therefore the exact
        # common parent for this child.
        solver.settings.file.read_case(file_name=paths["split_parent"])
        solver.settings.file.read_data(file_name=data_path(paths["split_parent"]))
        reopened_zones = fluid_names(solver)
        if reopened_zones != [LOWER_ZONE, PARENT_ZONE]:
            raise RuntimeError(f"split parent save/reopen zone mismatch: {reopened_zones}")
        manifest["split_parent_reopen"] = {"fluid_zones": reopened_zones, "source_tree": read_source_tree(solver)}
        write_json(args.manifest, manifest)

        solver.settings.file.write_case(file_name=paths["prepared"])
        solver.settings.file.write_data(file_name=data_path(paths["prepared"]))
        if not remote_file_exists(solver, paths["prepared"]) or not remote_file_exists(solver, data_path(paths["prepared"])):
            raise RuntimeError("prepared E5-CZ paired save failed")
        solver.settings.file.read_case(file_name=paths["prepared"])
        solver.settings.file.read_data(file_name=data_path(paths["prepared"]))
        manifest["prepared_reopen"] = {"fluid_zones": fluid_names(solver), "source_tree": read_source_tree(solver)}
        # Fluent 2025 R2 restores the parent report-file locations on a
        # case/data reopen. Reapply the child-local monitor paths after the
        # hard reopen proof and read them back before the first iteration.
        report_paths = redirect_reports(solver, paths["monitor_root"], args.candidate)
        manifest["report_files_after_reopen"] = report_paths
        write_json(args.manifest, manifest)

        run_controller(
            solver,
            paths,
            capture,
            report_paths,
            manifest,
            args.manifest,
            gain,
            float(args.m_star),
            float(args.delta_m_ref),
            float(manifest["liquid_density_kg_m3"]),
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
            "source_tree": read_source_tree(solver),
            "parent_invariants": base_invariants(solver),
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

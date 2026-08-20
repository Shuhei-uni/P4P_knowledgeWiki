#!/usr/bin/env python3
"""Complete the live 03A Stage-3 P0 monitor-ready parent.

This script intentionally operates on the currently loaded Fluent session. It
does not reload the old builder case, because the operator may have completed
the base setup manually in the live session. It adds only the post-setup
instrumentation layer, writes one unique case-only candidate, reloads that
candidate, and records the authoritative readback locally.

No initialization, patching, iteration, data write, DPM injection, EWF
operation, or solver shutdown is performed here. The disposable smoke run and
final OneDrive release are separate actions so that a case-only P0 can never
accidentally acquire solution data.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PureWindowsPath
import sys
from typing import Any, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
import build_03a_08b_parity_full_geometry as stage1  # noqa: E402
import build_02e_y010_campaign as y010  # noqa: E402


DEFAULT_REMOTE_DIR = r"C:\Users\syok443\OneDrive - The University of Auckland\2026 Sem 2\700\Brine outlet geom"
ENTRY_SURFACE = "codex_brine_pipe_entry_y0"
MONITOR_PREFIX = "03a_stage3"
RESIDUAL_HISTORY_SIZE = 600


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def object_names(obj: Any) -> list[str]:
    try:
        return sorted(str(item) for item in obj.get_object_names())
    except Exception:
        return []


def delete_named(branch: Any, name: str) -> None:
    if name not in set(object_names(branch)):
        return
    for kwargs in ({"name_list": [name]}, {"names": [name]}, {"name": name}):
        try:
            branch.delete(**kwargs)
            return
        except Exception:
            pass
    try:
        branch.delete(name)
    except Exception as exc:
        raise RuntimeError(f"Could not delete owned object {name!r}") from exc


def replace_named(branch: Any, name: str) -> Any:
    delete_named(branch, name)
    branch.create(name=name)
    return branch[name]


def set_optional(obj: Any, attribute: str, value: Any) -> bool:
    try:
        setattr(obj, attribute, value)
        return True
    except Exception:
        return False


def create_register(solver: Any, name: str, max_point: list[float]) -> dict[str, Any]:
    registers = solver.settings.solution.cell_registers
    delete_named(registers, name)
    registers.create(name=name)
    registers[name].set_state(
        {
            "name": name,
            "type": {
                "option": "hexahedron",
                "hexahedron": {
                    "min_point": y010.Y010_MIN,
                    "max_point": max_point,
                    "inside": True,
                },
            },
        }
    )
    state = registers[name].get_state()
    box = nested(state, "type", "hexahedron") or {}
    if (
        nested(state, "type", "option") != "hexahedron"
        or box.get("min_point") != y010.Y010_MIN
        or box.get("max_point") != max_point
        or box.get("inside") is not True
    ):
        raise RuntimeError(f"Register readback mismatch for {name}: {state}")
    return state


def create_entry_surface(solver: Any) -> dict[str, Any]:
    """Verify the operator-corrected native brine-entry surface.

    The entry plane is operator-owned geometry.  The original provisional
    y=0 construction was intentionally removed from automation after the
    operator corrected the plane in Fluent.  This function now fails closed if
    the named native surface is missing, and never deletes or recreates it.
    The returned metadata records identity only; the authoritative geometry is
    read back from Fluent's surface facets by the correction audit/release
    workflow.
    """

    field_surfaces = solver.fields.field_data.surfaces
    allowed = set(str(name) for name in field_surfaces.allowed_values())
    if ENTRY_SURFACE not in allowed:
        raise RuntimeError(
            f"Required operator-corrected native surface {ENTRY_SURFACE!r} is missing; "
            "automation will not recreate the provisional y=0 plane."
        )
    surface_ids = [int(value) for value in solver.fields.field_data.get_surface_ids([ENTRY_SURFACE])]
    if not surface_ids:
        raise RuntimeError(f"Native surface {ENTRY_SURFACE!r} has no Fluent surface ID")
    return {
        "name": ENTRY_SURFACE,
        "surface_ids": surface_ids,
        "kind": "operator-corrected-native-surface",
        "definition": "Operator-owned corrected brine-pipe entry plane; geometry must be read back from native surface facets.",
        "diagnostic_only": True,
    }


def configure_residuals(solver: Any) -> dict[str, Any]:
    residual = solver.settings.solution.monitor.residual
    before = safe_get_state(residual, "P0 residual monitor before")
    equations = before.get("equations", {}) if isinstance(before, Mapping) else {}
    updated: list[str] = []
    for name in equations:
        try:
            residual.equations[name].monitor = True
            residual.equations[name].check_convergence = False
            updated.append(str(name))
        except Exception:
            try:
                residual.equations[name].set_state(
                    {"monitor": True, "check_convergence": False}
                )
                updated.append(str(name))
            except Exception:
                pass
    options = residual.options
    options.n_save = RESIDUAL_HISTORY_SIZE
    options.n_display = RESIDUAL_HISTORY_SIZE
    after = safe_get_state(residual, "P0 residual monitor after")
    return {
        "requested_history_size": RESIDUAL_HISTORY_SIZE,
        "equations_updated": updated,
        "state": after,
    }


def configure_report_common(report: Any, *, phase: str) -> dict[str, bool]:
    report.phase = phase
    return {
        "create_report_file": set_optional(report, "create_report_file", True),
        "create_report_plot": set_optional(report, "create_report_plot", True),
        "retain_instantaneous_values": set_optional(
            report, "retain_instantaneous_values", True
        ),
    }


def configure_flux_reports(solver: Any, zones: Mapping[str, str]) -> list[dict[str, Any]]:
    flux = solver.settings.solution.report_definitions.flux
    boundaries = {
        "liquid_inlet": zones["liquid_inlet"],
        "steam_inlet": zones["steam_inlet"],
        "steam_outlet": zones["steam_outlet"],
        "brine_outlet": zones["brine_outlet"],
    }
    specs: list[tuple[str, str, list[str]]] = []
    for phase in ("mixture", "phase-1", "phase-2"):
        for role, surface in boundaries.items():
            specs.append(
                (
                    f"{MONITOR_PREFIX}_flux_{phase.replace('-', '')}_{role}",
                    phase,
                    [surface],
                )
            )
    specs.extend(
        [
            (
                f"{MONITOR_PREFIX}_total_mixture_inlet",
                "mixture",
                [boundaries["liquid_inlet"], boundaries["steam_inlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_steam_outlet_total",
                "mixture",
                [boundaries["steam_outlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_brine_outlet_total",
                "mixture",
                [boundaries["brine_outlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_total_outlet",
                "mixture",
                [boundaries["steam_outlet"], boundaries["brine_outlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_full_domain_mass_imbalance",
                "mixture",
                list(boundaries.values()),
            ),
            (
                f"{MONITOR_PREFIX}_liquid_inlet_mass_flux",
                "phase-2",
                [boundaries["liquid_inlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_vapor_inlet_mass_flux",
                "phase-1",
                [boundaries["steam_inlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_routing_liquid_to_brine",
                "phase-2",
                [boundaries["brine_outlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_routing_liquid_to_steam",
                "phase-2",
                [boundaries["steam_outlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_routing_vapor_to_brine",
                "phase-1",
                [boundaries["brine_outlet"]],
            ),
            (
                f"{MONITOR_PREFIX}_routing_vapor_to_steam",
                "phase-1",
                [boundaries["steam_outlet"]],
            ),
        ]
    )
    records: list[dict[str, Any]] = []
    for name, phase, selected in specs:
        report = replace_named(flux, name)
        report.report_type = "flux-massflow"
        report.boundaries = selected
        toggles = configure_report_common(report, phase=phase)
        records.append(
            {
                "name": name,
                "kind": "flux",
                "phase": phase,
                "boundaries": selected,
                "toggles": toggles,
                "state": report.get_state(),
            }
        )
    return records


def configure_volume_reports(solver: Any, fluid_zone: str) -> list[dict[str, Any]]:
    volume = solver.settings.solution.report_definitions.volume
    specs = [
        ("y010_geometric_volume", y010.Y010_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y010_liquid_volume", y010.Y010_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y010_liquid_mass", y010.Y010_REGISTER, "volume-mass", None, "phase-2"),
        ("y030_geometric_volume", y010.Y030_REGISTER, "volume-integral", "cell-volume", "mixture"),
        ("y030_liquid_volume", y010.Y030_REGISTER, "volume-integral", "phase-2-vof", "mixture"),
        ("y030_liquid_mass", y010.Y030_REGISTER, "volume-mass", None, "phase-2"),
        ("total_liquid_volume", fluid_zone, "volume-integral", "phase-2-vof", "mixture"),
        ("total_liquid_mass", fluid_zone, "volume-mass", None, "phase-2"),
    ]
    records: list[dict[str, Any]] = []
    for suffix, cell_zone, report_type, field, phase in specs:
        name = f"{MONITOR_PREFIX}_inventory_{suffix}"
        report = replace_named(volume, name)
        report.report_type = report_type
        report = volume[name]
        report.cell_zones = [cell_zone]
        if field is not None:
            report.field = field
        toggles = configure_report_common(report, phase=phase)
        records.append(
            {
                "name": name,
                "kind": "volume",
                "report_type": report_type,
                "field": field,
                "cell_zones": [cell_zone],
                "phase": phase,
                "toggles": toggles,
                "state": report.get_state(),
            }
        )
    return records


def configure_surface_reports(solver: Any) -> list[dict[str, Any]]:
    surface = solver.settings.solution.report_definitions.surface
    records: list[dict[str, Any]] = []
    for suffix, field in (
        ("brine_entry_static_pressure", "pressure"),
        ("brine_entry_total_pressure", "total-pressure"),
    ):
        name = f"{MONITOR_PREFIX}_{suffix}"
        report = replace_named(surface, name)
        report.report_type = "surface-areaavg"
        report.surface_names = [ENTRY_SURFACE]
        report.field = field
        toggles = configure_report_common(report, phase="mixture")
        records.append(
            {
                "name": name,
                "kind": "surface",
                "report_type": "surface-areaavg",
                "field": field,
                "surface_names": [ENTRY_SURFACE],
                "toggles": toggles,
                "state": report.get_state(),
            }
        )
    return records


def configure_relative_expression(solver: Any) -> dict[str, Any]:
    branch = solver.settings.solution.report_definitions.single_valued_expression
    name = f"{MONITOR_PREFIX}_relative_mass_imbalance"
    report = replace_named(branch, name)
    # Fluent 2025 R2 exposes MassFlow, rather than MassFlowRate, in its
    # expression language. The denominator is nonzero for this physical inlet
    # setup; keeping the formula native makes the history live and auditable.
    definition = (
        'abs(MassFlow(["liquidinlet", "steaminlet"], phase="mixture")+'
        'MassFlow(["steamoutlet", "brineoutlet"], phase="mixture"))/'
        'abs(MassFlow(["liquidinlet", "steaminlet"], phase="mixture"))'
    )
    report.definition = definition
    toggles = {
        "create_report_file": set_optional(report, "create_report_file", True),
        "create_report_plot": set_optional(report, "create_report_plot", True),
        "retain_instantaneous_values": set_optional(
            report, "retain_instantaneous_values", True
        ),
    }
    state = report.get_state()
    if state.get("definition") != definition:
        raise RuntimeError(f"Relative mass-imbalance expression readback mismatch: {state}")
    return {
        "name": name,
        "kind": "single-valued-expression",
        "definition": definition,
        "toggles": toggles,
        "state": state,
    }


def ensure_dpm_off(solver: Any) -> dict[str, Any]:
    state = safe_get_state(solver.settings.setup.models.discrete_phase, "DPM P0 readback")
    interaction = nested(state, "general_settings", "interaction", "enabled")
    injections = nested(state, "injections")
    injection_names = sorted(str(name) for name in injections) if isinstance(injections, Mapping) else []
    if interaction is not False or injection_names:
        raise RuntimeError(f"P0 DPM guard failed: interaction={interaction}, injections={injection_names}")
    return {"interaction_enabled": interaction, "injection_names": injection_names, "state": state}


def write_case_only(solver: Any, path: str) -> None:
    if remote_file_exists(solver, path):
        raise FileExistsError(f"Refusing to overwrite candidate case: {path}")
    solver.settings.file.write_case(file_name=path)
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent did not expose the written case: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--output-case", default="")
    parser.add_argument("--snapshot-json", required=True)
    parser.add_argument(
        "--stamp",
        default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
    )
    args = parser.parse_args()
    output_case = args.output_case or str(
        PureWindowsPath(args.remote_dir)
        / f"03A-stage3-P0-monitor-ready-preinit-candidate-{args.stamp}.cas.h5"
    )

    solver = connect(server_id=args.server_id)
    if "2025 R2" not in str(solver.get_fluent_version()):
        raise RuntimeError(f"Expected Fluent 2025 R2, got {solver.get_fluent_version()!r}")
    if remote_file_exists(solver, output_case):
        raise FileExistsError(f"Refusing to overwrite candidate case: {output_case}")

    zones, _, cell_zones = stage1.resolve_zones(solver)
    fluid_state = safe_get_state(solver.settings.setup.cell_zone_conditions, "fluid zones")
    fluid_branch = fluid_state.get("fluid", {}) if isinstance(fluid_state, Mapping) else {}
    fluid_names = [str(name) for name in fluid_branch if str(name) != "settings"]
    if len(fluid_names) != 1:
        raise RuntimeError(f"Expected one fluid cell zone, got {fluid_names}")
    fluid_zone = fluid_names[0]

    registers = {
        y010.Y010_REGISTER: create_register(solver, y010.Y010_REGISTER, y010.Y010_MAX),
        y010.Y030_REGISTER: create_register(solver, y010.Y030_REGISTER, y010.Y030_MAX),
    }
    entry_surface = create_entry_surface(solver)
    residual = configure_residuals(solver)
    flux = configure_flux_reports(solver, zones)
    volume = configure_volume_reports(solver, fluid_zone)
    surface = configure_surface_reports(solver)
    relative = configure_relative_expression(solver)
    dpm = ensure_dpm_off(solver)

    # Capture the current model/settings tree without changing the operator's
    # manually completed base setup. The previous builder already proved this
    # session has no initialization/data history; this script preserves that
    # contract and only adds diagnostics.
    contract = stage1.compact_contract(solver, zones, dpm)
    report_definitions = safe_get_state(
        solver.settings.solution.report_definitions, "P0 report definitions"
    )
    write_case_only(solver, output_case)
    solver.settings.file.read_case(file_name=output_case)

    # Reload readback is authoritative for the candidate. Report definition
    # names are captured by branch because the full Settings tree is large.
    root = solver.settings.solution.report_definitions
    reload_reports = {
        branch: object_names(getattr(root, branch))
        for branch in (
            "flux",
            "volume",
            "surface",
            "single_valued_expression",
        )
    }
    reload_registers = {
        name: root_state.get_state()
        for name, root_state in (
            (y010.Y010_REGISTER, solver.settings.solution.cell_registers[y010.Y010_REGISTER]),
            (y010.Y030_REGISTER, solver.settings.solution.cell_registers[y010.Y030_REGISTER]),
        )
    }
    payload = {
        "status": "P0_CANDIDATE_CASE_ONLY",
        "server_id": str(args.server_id),
        "fluent_version": str(solver.get_fluent_version()),
        "candidate_case": output_case,
        "case_only": True,
        "initialization_called": False,
        "patch_called": False,
        "iterations_requested": 0,
        "data_written": False,
        "zones": zones,
        "fluid_zone": fluid_zone,
        "cell_zones": cell_zones,
        "registers": registers,
        "entry_surface": entry_surface,
        "residual": residual,
        "flux_reports": flux,
        "volume_reports": volume,
        "surface_reports": surface,
        "relative_mass_imbalance": relative,
        "dpm": dpm,
        "contract": contract,
        "report_definitions_before_reload": report_definitions,
        "report_definition_names_after_reload": reload_reports,
        "registers_after_reload": reload_registers,
        "one_drive_release_note": "Candidate only; smoke and immutable final release are separate operations.",
    }
    output = Path(args.snapshot_json).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, default=str), flush=True)
    print(f"snapshot_json: {output}", flush=True)
    print(f"candidate_case: {output_case}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

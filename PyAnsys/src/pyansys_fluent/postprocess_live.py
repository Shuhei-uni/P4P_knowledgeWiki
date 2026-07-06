#!/usr/bin/env python3
"""Reusable live-Fluent post-processing helpers.

Primary intent:
- connect to an existing Fluent session;
- load an existing case/data pair;
- inspect boundary/model/DPM state;
- extract flux-based carrier metrics;
- write structured summaries.

Optional explicit DPM sampling:
- when requested by the operator, run Fluent's existing `report/dpm-sample`
  workflow injection-by-injection on the already-loaded case to capture
  escaped/trapped/incomplete counts without rebuilding the setup.
"""

from __future__ import annotations

import contextlib
import io
import json
import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from pyansys_fluent.common import remote_chdir, safe_get_state
from pyansys_fluent.dependency_workflow import safe_child_names
from pyansys_fluent.setup_common import normalize_name, print_header, require_remote_input
from pyansys_fluent.setup_discovery import build_compact_boundary_summary


DEFAULT_OMITTED_DIAMETERS_UM = (562.0, 844.0, 1631.0)
DEFAULT_PHASE_DOMAIN_FALLBACK = {
    "vapor": "phase-1",
    "liquid": "phase-2",
}


def load_case_data_pair(
    solver: Any,
    *,
    case_file: str,
    data_file: str,
    load_strategy: str = "auto",
) -> dict[str, Any]:
    """Load an explicit case/data pair into the active Fluent session."""
    print_header("Load Case/Data For Post-Processing")
    require_remote_input(solver, case_file, "case file")
    require_remote_input(solver, data_file, "data file")

    case_path = PureWindowsPath(case_file)
    data_path = PureWindowsPath(data_file)
    remote_chdir(solver, str(case_path.parent))

    expected_data_name = case_path.name.removesuffix(".cas.h5") + ".dat.h5"
    use_paired_read = load_strategy == "paired" or (
        load_strategy == "auto" and data_path.name == expected_data_name
    )
    if use_paired_read:
        solver.settings.file.read_case_data(file_name=case_file)
        load_mode = "paired-read_case_data"
    else:
        solver.settings.file.read_case(file_name=case_file)
        solver.settings.file.read_data(file_name=data_file)
        load_mode = "explicit-read_case-then-read_data"

    return {
        "case_file": case_file,
        "data_file": data_file,
        "load_mode": load_mode,
        "case_name": case_path.name,
        "data_name": data_path.name,
        "case_data_name_match": data_path.name == expected_data_name,
    }


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def escape_scheme_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def recursive_find_phase_material_map(payload: Any) -> dict[str, str]:
    if isinstance(payload, Mapping):
        phase1 = payload.get("phase-1")
        phase2 = payload.get("phase-2")
        if isinstance(phase1, str) and isinstance(phase2, str):
            return {
                "phase-1": phase1,
                "phase-2": phase2,
            }
        for value in payload.values():
            found = recursive_find_phase_material_map(value)
            if found:
                return found
    elif isinstance(payload, list):
        for item in payload:
            found = recursive_find_phase_material_map(item)
            if found:
                return found
    return {}


def infer_phase_domain_map(models_state: Mapping[str, Any]) -> dict[str, Any]:
    multiphase_state = models_state.get("multiphase", {})
    if not isinstance(multiphase_state, Mapping):
        multiphase_state = {}

    material_map = recursive_find_phase_material_map(multiphase_state)
    vapor_domain = DEFAULT_PHASE_DOMAIN_FALLBACK["vapor"]
    liquid_domain = DEFAULT_PHASE_DOMAIN_FALLBACK["liquid"]
    warnings: list[str] = []

    for domain_name, material_name in material_map.items():
        material_key = normalize_name(material_name)
        if "vapor" in material_key or "steam" in material_key:
            vapor_domain = domain_name
        if "liquid" in material_key or "water" in material_key or "brine" in material_key:
            liquid_domain = domain_name

    if not material_map:
        warnings.append(
            "Could not discover phase-material mapping from the live state; using fallback phase-1=vapor, phase-2=liquid."
        )

    return {
        "phase_materials": material_map,
        "vapor_domain": vapor_domain,
        "liquid_domain": liquid_domain,
        "warnings": warnings,
    }


def discover_named_zones(boundary_summary: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    role_candidates = {
        "liquid_inlet": {"liquidinlet"},
        "steam_inlet": {"steaminlet"},
        "steam_outlet": {"steamoutlet", "outlet"},
    }

    named_roles: dict[str, str | None] = {
        "liquid_inlet": None,
        "steam_inlet": None,
        "steam_outlet": None,
    }
    all_outlets: list[str] = []
    warnings: list[str] = []

    for boundary_type, names in boundary_summary.items():
        normalized = {normalize_name(name): name for name in names}
        for role_name, candidates in role_candidates.items():
            for candidate in candidates:
                if candidate in normalized and named_roles[role_name] is None:
                    named_roles[role_name] = normalized[candidate]

        if "outlet" in normalize_name(boundary_type) or normalize_name(boundary_type) == "outflow":
            all_outlets.extend(str(name) for name in names)

    for role_name, value in named_roles.items():
        if value is None:
            warnings.append(f"Could not identify expected zone for role: {role_name}")

    ordered_outlets: list[str] = []
    seen: set[str] = set()
    preferred_outlet = named_roles["steam_outlet"]
    if preferred_outlet:
        ordered_outlets.append(preferred_outlet)
        seen.add(preferred_outlet)
    for name in all_outlets:
        if name not in seen:
            ordered_outlets.append(name)
            seen.add(name)

    return {
        "roles": named_roles,
        "all_outlets": ordered_outlets,
        "warnings": warnings,
    }


def _get_results_fluxes_branch(solver: Any) -> Any | None:
    try:
        fluxes = solver.settings.results.report.fluxes
    except Exception:
        return None
    try:
        if hasattr(fluxes, "is_active") and not fluxes.is_active():
            return None
    except Exception:
        return None
    return fluxes


_MASS_FLOW_LINE_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s+(-?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s*$")


def _parse_mass_flow_stdout(output: str) -> dict[str, float | None]:
    parsed: dict[str, float | None] = {}
    for raw_line in output.splitlines():
        line = raw_line.rstrip()
        match = _MASS_FLOW_LINE_RE.match(line)
        if not match:
            continue
        zone_name, value_text = match.groups()
        parsed[zone_name] = safe_float(value_text)
    return parsed


def _run_mass_flow_command_capture(fluxes: Any, *, domain: str, zones: Sequence[str]) -> dict[str, float | None]:
    command = getattr(fluxes, "mass_flow", None)
    if command is None:
        raise AttributeError("results.report.fluxes.mass_flow is unavailable")

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        command(domain=domain, zones=list(zones))
    return _parse_mass_flow_stdout(buffer.getvalue())


def extract_mass_flow_report(
    solver: Any,
    *,
    zones: Sequence[str],
    domains: Sequence[str] = ("mixture", "phase-1", "phase-2"),
) -> dict[str, Any]:
    fluxes = _get_results_fluxes_branch(solver)
    if fluxes is None:
        return {
            "available": False,
            "zones": list(zones),
            "by_domain": {},
            "warnings": ["results.report.fluxes is unavailable or inactive in this session."],
        }

    by_domain: dict[str, dict[str, float | None]] = {}
    warnings: list[str] = []
    for domain in domains:
        try:
            if hasattr(fluxes, "get_mass_flow"):
                result = fluxes.get_mass_flow(domain=domain, zones=list(zones))
                domain_payload: dict[str, float | None] = {}
                for key, value in result.items():
                    domain_payload[str(key)] = safe_float(value)
            else:
                domain_payload = _run_mass_flow_command_capture(fluxes, domain=domain, zones=zones)
        except Exception as exc:
            warnings.append(f"Mass-flow query failed for domain {domain}: {type(exc).__name__}: {exc}")
            continue

        by_domain[domain] = domain_payload

    return {
        "available": bool(by_domain),
        "zones": list(zones),
        "by_domain": by_domain,
        "warnings": warnings,
    }


def _sum_abs(zone_values: Mapping[str, float | None], zone_names: Sequence[str]) -> float | None:
    total = 0.0
    seen = False
    for zone_name in zone_names:
        value = safe_float(zone_values.get(zone_name))
        if value is None:
            continue
        total += abs(value)
        seen = True
    if not seen:
        return None
    return total


def _relative_balance_note(
    *,
    mass_imbalance_kg_s: float | None,
    carryover_kg_s: float | None,
) -> str:
    if mass_imbalance_kg_s is None:
        return "Mass imbalance could not be assessed from the available flux report."
    if carryover_kg_s is None:
        return "Mass imbalance is available, but steam-line liquid carryover is unavailable."
    if carryover_kg_s == 0.0:
        return "Steam-line liquid carryover is zero or below extraction precision; compare imbalance directly against other metrics."
    ratio = mass_imbalance_kg_s / carryover_kg_s
    if ratio <= 0.1:
        return "Mass imbalance is small relative to the reported steam-line liquid carryover."
    if ratio <= 1.0:
        return "Mass imbalance is comparable to the reported steam-line liquid carryover and should be treated cautiously."
    return "Mass imbalance is larger than the reported steam-line liquid carryover; do not treat carryover as strong quantitative evidence."


def calculate_carrier_metrics(
    carrier_fluxes: Mapping[str, Any],
    zone_roles: Mapping[str, str | None],
    *,
    vapor_domain: str,
    liquid_domain: str,
) -> dict[str, Any]:
    by_domain = carrier_fluxes.get("by_domain", {})
    mixture = by_domain.get("mixture", {})
    vapor = by_domain.get(vapor_domain, {})
    liquid = by_domain.get(liquid_domain, {})

    if not isinstance(mixture, Mapping):
        mixture = {}
    if not isinstance(vapor, Mapping):
        vapor = {}
    if not isinstance(liquid, Mapping):
        liquid = {}

    inlet_zones = [zone for zone in (zone_roles.get("liquid_inlet"), zone_roles.get("steam_inlet")) if zone]
    steam_outlet = zone_roles.get("steam_outlet")
    outlet_zones = [name for name in carrier_fluxes.get("zones", []) if name not in inlet_zones]

    m_liq_in = _sum_abs(liquid, inlet_zones)
    m_vap_in = _sum_abs(vapor, inlet_zones)
    m_liq_steam_out = _sum_abs(liquid, [steam_outlet] if steam_outlet else [])
    m_vap_steam_out = _sum_abs(vapor, [steam_outlet] if steam_outlet else [])
    m_mix_in = _sum_abs(mixture, inlet_zones)
    m_mix_out = _sum_abs(mixture, outlet_zones)

    eta_phase = None
    if m_liq_in not in (None, 0.0) and m_liq_steam_out is not None:
        eta_phase = 1.0 - (m_liq_steam_out / m_liq_in)

    x_out = None
    if m_vap_steam_out is not None and m_liq_steam_out is not None:
        denom = m_vap_steam_out + m_liq_steam_out
        if denom > 0.0:
            x_out = m_vap_steam_out / denom

    mass_imbalance_kg_s = None
    mass_imbalance_ratio = None
    if m_mix_in not in (None, 0.0) and m_mix_out is not None:
        mass_imbalance_kg_s = abs(m_mix_in - m_mix_out)
        mass_imbalance_ratio = mass_imbalance_kg_s / m_mix_in

    return {
        "m_liq_in": m_liq_in,
        "m_vap_in": m_vap_in,
        "m_liq_steam_out": m_liq_steam_out,
        "m_vap_steam_out": m_vap_steam_out,
        "m_mix_in": m_mix_in,
        "m_mix_out": m_mix_out,
        "eta_phase": eta_phase,
        "x_out": x_out,
        "mass_imbalance_kg_s": mass_imbalance_kg_s,
        "mass_imbalance_ratio": mass_imbalance_ratio,
        "mass_imbalance_note": _relative_balance_note(
            mass_imbalance_kg_s=mass_imbalance_kg_s,
            carryover_kg_s=m_liq_steam_out,
        ),
    }


def _get_nested(payload: Mapping[str, Any], path: Sequence[str]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def inspect_dpm_inventory(
    solver: Any,
    *,
    omitted_diameters_um: Sequence[float] = DEFAULT_OMITTED_DIAMETERS_UM,
) -> tuple[dict[str, Any], dict[str, Any]]:
    warnings: list[str] = []
    dpm_metrics: dict[str, Any] = {
        "result_available": False,
        "active_diameters_um": [],
        "represented_mass_flow_total": None,
        "aggregate_scope": "partial-bin diagnostic only",
        "missing_requested_bins_um": [float(value) for value in omitted_diameters_um],
    }

    try:
        dpm = solver.settings.setup.models.discrete_phase
    except Exception as exc:
        warnings.append(f"Discrete phase branch unavailable: {type(exc).__name__}: {exc}")
        return {
            "enabled": False,
            "warnings": warnings,
            "branch_state": {},
            "injection_count": 0,
            "injections": [],
            "result_fields_available": False,
        }, dpm_metrics

    branch_state = safe_get_state(dpm, "setup.models.discrete_phase")
    injections_branch = getattr(dpm, "injections", None)
    if injections_branch is None:
        warnings.append("DPM injections branch is unavailable.")
        return {
            "enabled": True,
            "warnings": warnings,
            "branch_state": branch_state,
            "injection_count": 0,
            "injections": [],
            "result_fields_available": False,
        }, dpm_metrics

    try:
        injection_names = sorted(str(name) for name in injections_branch.get_object_names())
    except Exception as exc:
        warnings.append(f"Could not enumerate DPM injections: {type(exc).__name__}: {exc}")
        injection_names = []

    injections: list[dict[str, Any]] = []
    active_diameters: list[float] = []
    represented_mass_flow_total = 0.0
    have_mass_flow_total = False
    result_fields_available = False

    for injection_name in injection_names:
        try:
            injection = injections_branch[injection_name]
        except Exception as exc:
            warnings.append(f"Could not access injection {injection_name}: {type(exc).__name__}: {exc}")
            continue

        injection_state = safe_get_state(injection, f"injections.{injection_name}")
        initial_values = safe_get_state(
            getattr(injection, "initial_values", object()),
            f"injections.{injection_name}.initial_values",
        )
        location_state = safe_get_state(
            getattr(getattr(injection, "initial_values", object()), "location", object()),
            f"injections.{injection_name}.initial_values.location",
        )
        mass_flow_state = safe_get_state(
            getattr(getattr(injection, "initial_values", object()), "mass_flow_rate", object()),
            f"injections.{injection_name}.initial_values.mass_flow_rate",
        )
        particle_size_state = safe_get_state(
            getattr(getattr(injection, "initial_values", object()), "particle_size", object()),
            f"injections.{injection_name}.initial_values.particle_size",
        )

        diameter_m = safe_float(
            _get_nested(particle_size_state, ("diameter",))
            or _get_nested(injection_state, ("diameter",))
            or _get_nested(injection_state, ("initial_values", "particle_size", "diameter"))
        )
        diameter_um = diameter_m * 1e6 if diameter_m is not None else None
        if diameter_um is not None:
            active_diameters.append(diameter_um)

        total_flow_rate = safe_float(
            _get_nested(mass_flow_state, ("total_flow_rate",))
            or _get_nested(injection_state, ("initial_values", "mass_flow_rate", "total_flow_rate"))
        )
        if total_flow_rate is not None:
            represented_mass_flow_total += total_flow_rate
            have_mass_flow_total = True

        injection_surfaces = _get_nested(location_state, ("injection_surfaces",))
        if injection_surfaces is None:
            injection_surfaces = _get_nested(injection_state, ("initial_values", "location", "injection_surfaces"))

        material = injection_state.get("material") if isinstance(injection_state, Mapping) else None

        result_fields: dict[str, Any] = {}
        candidate_sources = {
            "summary": safe_get_state(getattr(injection, "summary", object()), f"injections.{injection_name}.summary"),
            "statistics": safe_get_state(getattr(injection, "statistics", object()), f"injections.{injection_name}.statistics"),
            "state": injection_state,
        }
        for label, source in candidate_sources.items():
            if isinstance(source, Mapping):
                for key, value in source.items():
                    normalized = normalize_name(str(key))
                    if any(token in normalized for token in ("escaped", "trapped", "incomplete", "tracked", "fate", "result")):
                        result_fields[f"{label}.{key}"] = value
        if result_fields:
            result_fields_available = True

        injections.append(
            {
                "name": injection_name,
                "material": material,
                "diameter_m": diameter_m,
                "diameter_um": diameter_um,
                "injection_surfaces": injection_surfaces if isinstance(injection_surfaces, list) else [],
                "represented_mass_flow_rate": total_flow_rate,
                "child_names": safe_child_names(injection),
                "result_fields": result_fields,
            }
        )

    if not result_fields_available:
        warnings.append(
            "No stored DPM fate/result summary fields were found in the loaded session; this pass is inventory-only for DPM."
        )

    active_diameters_sorted = sorted(active_diameters)
    dpm_metrics.update(
        {
            "result_available": result_fields_available,
            "active_diameters_um": active_diameters_sorted,
            "represented_mass_flow_total": represented_mass_flow_total if have_mass_flow_total else None,
        }
    )

    inventory = {
        "enabled": True,
        "warnings": warnings,
        "branch_state": branch_state,
        "injection_count": len(injections),
        "injections": injections,
        "result_fields_available": result_fields_available,
    }
    return inventory, dpm_metrics


def _format_tui_list(values: Sequence[str]) -> str:
    if not values:
        return "()"
    return f"({' '.join(str(value) for value in values)})"


_DPM_SAMPLE_COUNT_RE = re.compile(r"number tracked = (?P<tracked>\d+)(?P<tail>.*)$", re.IGNORECASE | re.S)
_DPM_SAMPLE_FIELD_RE = re.compile(r"(?P<key>escaped|trapped|incomplete)\s*=\s*(?P<value>\d+)", re.IGNORECASE)


def parse_dpm_sample_output(output: str) -> dict[str, Any]:
    counts = {
        "tracked": None,
        "escaped": 0,
        "trapped": 0,
        "incomplete": 0,
    }
    summary_line = ""

    match = _DPM_SAMPLE_COUNT_RE.search(output)
    if not match:
        return {
            "counts": counts,
            "summary_line": summary_line,
            "warnings": ["Could not parse a `number tracked = ...` line from Fluent dpm-sample output."],
        }

    counts["tracked"] = int(match.group("tracked"))
    tail = match.group("tail")
    summary_line = f"number tracked = {counts['tracked']}"
    for field_match in _DPM_SAMPLE_FIELD_RE.finditer(tail):
        key = field_match.group("key").lower()
        value = int(field_match.group("value"))
        counts[key] = value
        summary_line += f", {key} = {value}"

    return {
        "counts": counts,
        "summary_line": summary_line,
        "warnings": [],
    }


def run_dpm_sample_for_injection(
    solver: Any,
    *,
    injection_name: str,
    boundary_names: Sequence[str],
    plane_names: Sequence[str] = (),
) -> dict[str, Any]:
    command = (
        "/report/dpm-sample\n"
        f"{_format_tui_list([injection_name])}\n"
        f"{_format_tui_list(boundary_names)}\n"
        f"{_format_tui_list(plane_names)}\n"
    )

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = solver.scheme.eval(
            f'(ti-menu-load-string "{escape_scheme_string(command)}")'
        )
    raw_output = buffer.getvalue()
    parsed = parse_dpm_sample_output(raw_output)
    counts = parsed["counts"]

    tracked = counts.get("tracked")
    escaped = counts.get("escaped", 0)
    trapped = counts.get("trapped", 0)
    incomplete = counts.get("incomplete", 0)
    escaped_fraction = None
    trapped_fraction = None
    incomplete_fraction = None
    if tracked not in (None, 0):
        escaped_fraction = escaped / tracked
        trapped_fraction = trapped / tracked
        incomplete_fraction = incomplete / tracked

    return {
        "name": injection_name,
        "command_ok": bool(result),
        "selected_boundaries": list(boundary_names),
        "selected_planes": list(plane_names),
        "counts": counts,
        "escaped_fraction": escaped_fraction,
        "trapped_fraction": trapped_fraction,
        "incomplete_fraction": incomplete_fraction,
        "summary_line": parsed["summary_line"],
        "warnings": parsed["warnings"],
        "raw_output": raw_output,
    }


def run_dpm_sample_per_injection(
    solver: Any,
    *,
    injection_names: Sequence[str],
    boundary_names: Sequence[str],
    plane_names: Sequence[str] = (),
) -> dict[str, Any]:
    warnings: list[str] = []
    samples: list[dict[str, Any]] = []
    aggregate_counts = {
        "tracked": 0,
        "escaped": 0,
        "trapped": 0,
        "incomplete": 0,
    }

    for injection_name in injection_names:
        try:
            sample = run_dpm_sample_for_injection(
                solver,
                injection_name=injection_name,
                boundary_names=boundary_names,
                plane_names=plane_names,
            )
        except Exception as exc:
            warnings.append(
                f"dpm-sample failed for {injection_name}: {type(exc).__name__}: {exc}"
            )
            sample = {
                "name": injection_name,
                "command_ok": False,
                "selected_boundaries": list(boundary_names),
                "selected_planes": list(plane_names),
                "counts": {
                    "tracked": None,
                    "escaped": 0,
                    "trapped": 0,
                    "incomplete": 0,
                },
                "escaped_fraction": None,
                "trapped_fraction": None,
                "incomplete_fraction": None,
                "summary_line": "",
                "warnings": [warnings[-1]],
                "raw_output": "",
            }

        counts = sample["counts"]
        for key in ("escaped", "trapped", "incomplete"):
            aggregate_counts[key] += int(counts.get(key) or 0)
        tracked = counts.get("tracked")
        if tracked is not None:
            aggregate_counts["tracked"] += int(tracked)

        warnings.extend(str(item) for item in sample.get("warnings", []))
        samples.append(sample)

    total_tracked = aggregate_counts["tracked"] or None
    escaped_fraction = None
    trapped_fraction = None
    incomplete_fraction = None
    if total_tracked:
        escaped_fraction = aggregate_counts["escaped"] / total_tracked
        trapped_fraction = aggregate_counts["trapped"] / total_tracked
        incomplete_fraction = aggregate_counts["incomplete"] / total_tracked

    return {
        "available": bool(samples),
        "mode": "dpm-sample-per-injection",
        "selected_boundaries": list(boundary_names),
        "selected_planes": list(plane_names),
        "samples": samples,
        "aggregate_counts": aggregate_counts,
        "escaped_fraction": escaped_fraction,
        "trapped_fraction": trapped_fraction,
        "incomplete_fraction": incomplete_fraction,
        "warnings": warnings,
    }


def capture_session_summary(solver: Any) -> dict[str, Any]:
    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "setup.boundary_conditions")
    models_state = safe_get_state(solver.settings.setup.models, "setup.models")

    boundary_summary: dict[str, list[str]] = {}
    if isinstance(boundary_state, Mapping):
        boundary_summary = build_compact_boundary_summary(boundary_state)

    phase_domain_map = infer_phase_domain_map(models_state if isinstance(models_state, Mapping) else {})
    zone_discovery = discover_named_zones(boundary_summary)
    warnings = list(phase_domain_map["warnings"]) + list(zone_discovery["warnings"])

    return {
        "fluent_version": solver.get_fluent_version(),
        "boundary_summary": boundary_summary,
        "models_state": models_state,
        "phase_domain_map": phase_domain_map,
        "zone_discovery": zone_discovery,
        "warnings": warnings,
    }


def determine_claim_class_ceiling(result: Mapping[str, Any]) -> str:
    carrier_fluxes = result.get("carrier_fluxes", {})
    carrier_metrics = result.get("carrier_metrics", {})
    dpm_inventory = result.get("dpm_inventory", {})

    flux_available = bool(carrier_fluxes.get("available"))
    eta_phase = carrier_metrics.get("eta_phase")
    imbalance_ratio = carrier_metrics.get("mass_imbalance_ratio")
    dpm_result_available = bool(dpm_inventory.get("result_fields_available"))

    if flux_available and eta_phase is not None and imbalance_ratio is not None and imbalance_ratio <= 0.05:
        if dpm_result_available:
            return "Numerically verified"
        return "Numerically verified"
    return "Debug only"


def build_limitations(
    *,
    session_summary: Mapping[str, Any],
    dpm_inventory: Mapping[str, Any],
    dpm_metrics: Mapping[str, Any],
    omitted_diameters_um: Sequence[float],
) -> list[str]:
    dpm_sampling = dpm_metrics.get("per_injection_sample", {})
    sampling_available = bool(dpm_sampling.get("available"))
    if sampling_available:
        first_line = (
            "This workflow reused the existing loaded case/data without setup rebuild, mesh replay, or injection creation. "
            "An explicit per-injection `dpm-sample` pass was run on the active injections."
        )
    else:
        first_line = (
            "This workflow is post-processing only. No setup rebuild, mesh replay, injection creation, or new DPM tracking was performed."
        )

    limitations = [
        first_line,
        (
            "The aggregate DPM interpretation for this run is intentionally partial because the user excluded "
            f"{', '.join(f'{int(value)} um' for value in omitted_diameters_um)}."
        ),
    ]
    if sampling_available:
        limitations.append(
            "Per-injection DPM counts were sampled against the selected reporting boundaries only, so they remain diagnostic rather than full validated fate accounting."
        )
    for warning in session_summary.get("warnings", []):
        limitations.append(f"Session warning: {warning}")
    for warning in dpm_inventory.get("warnings", []):
        limitations.append(f"DPM warning: {warning}")
    for warning in dpm_sampling.get("warnings", []):
        limitations.append(f"DPM sample warning: {warning}")
    return limitations


def compile_postprocess_result(
    *,
    server_id: str,
    run_label: str,
    load_summary: Mapping[str, Any],
    session_summary: Mapping[str, Any],
    carrier_fluxes: Mapping[str, Any],
    carrier_metrics: Mapping[str, Any],
    dpm_inventory: Mapping[str, Any],
    dpm_metrics: Mapping[str, Any],
    omitted_diameters_um: Sequence[float] = DEFAULT_OMITTED_DIAMETERS_UM,
) -> dict[str, Any]:
    limitations = build_limitations(
        session_summary=session_summary,
        dpm_inventory=dpm_inventory,
        dpm_metrics=dpm_metrics,
        omitted_diameters_um=omitted_diameters_um,
    )
    result = {
        "source": {
            "server_id": str(server_id),
            "run_label": run_label,
            **dict(load_summary),
        },
        "session": session_summary,
        "carrier_fluxes": carrier_fluxes,
        "carrier_metrics": carrier_metrics,
        "dpm_inventory": dpm_inventory,
        "dpm_metrics": dpm_metrics,
        "limitations": limitations,
        "claim_class_ceiling": "",
    }
    result["claim_class_ceiling"] = determine_claim_class_ceiling(result)
    return result


def _format_optional(value: float | None, *, scientific: bool = False) -> str:
    if value is None:
        return "unavailable"
    if scientific:
        return f"{value:.6e}"
    return f"{value:.6f}"


def render_markdown_report(result: Mapping[str, Any]) -> str:
    source = result.get("source", {})
    session = result.get("session", {})
    carrier_metrics = result.get("carrier_metrics", {})
    dpm_inventory = result.get("dpm_inventory", {})
    dpm_metrics = result.get("dpm_metrics", {})
    dpm_sampling = dpm_metrics.get("per_injection_sample", {})

    lines = [
        f"# Live Fluent Post-Processing Report: {source.get('run_label', 'unnamed-run')}",
        "",
        "## Source Case/Data",
        f"- Server id: `{source.get('server_id', 'unknown')}`",
        f"- Case file: `{source.get('case_file', 'unknown')}`",
        f"- Data file: `{source.get('data_file', 'unknown')}`",
        f"- Load mode: `{source.get('load_mode', 'unknown')}`",
        "",
        "## Boundary/Model Sanity",
        f"- Fluent version: `{session.get('fluent_version', 'unknown')}`",
    ]

    boundary_summary = session.get("boundary_summary", {})
    if isinstance(boundary_summary, Mapping):
        for boundary_type, names in boundary_summary.items():
            lines.append(f"- {boundary_type}: `{', '.join(names)}`")

    lines.extend(
        [
            "",
            "## Carrier Flux Metrics",
            f"- Liquid inlet mass flow: `{_format_optional(carrier_metrics.get('m_liq_in'))} kg/s`",
            f"- Vapor inlet mass flow: `{_format_optional(carrier_metrics.get('m_vap_in'))} kg/s`",
            f"- Steam-outlet liquid mass flow: `{_format_optional(carrier_metrics.get('m_liq_steam_out'), scientific=True)} kg/s`",
            f"- Steam-outlet vapor mass flow: `{_format_optional(carrier_metrics.get('m_vap_steam_out'))} kg/s`",
            f"- Phase-flux efficiency `eta_phase`: `{_format_optional(carrier_metrics.get('eta_phase'))}`",
            f"- Steam-outlet dryness `x_out`: `{_format_optional(carrier_metrics.get('x_out'))}`",
            f"- Mass imbalance: `{_format_optional(carrier_metrics.get('mass_imbalance_kg_s'), scientific=True)} kg/s`",
            f"- Mass-imbalance note: {carrier_metrics.get('mass_imbalance_note', 'unavailable')}",
            "",
            "## DPM Inventory",
            f"- DPM enabled: `{dpm_inventory.get('enabled', False)}`",
            f"- Active injections: `{dpm_inventory.get('injection_count', 0)}`",
            f"- Stored DPM result fields available: `{dpm_inventory.get('result_fields_available', False)}`",
            f"- Active diameters [um]: `{', '.join(f'{value:g}' for value in dpm_metrics.get('active_diameters_um', [])) or 'none found'}`",
            f"- Represented mass-flow total: `{_format_optional(dpm_metrics.get('represented_mass_flow_total'))} kg/s`",
        ]
    )

    if dpm_sampling.get("available"):
        aggregate_counts = dpm_sampling.get("aggregate_counts", {})
        lines.extend(
            [
                "",
                "## Per-Injection DPM Sample",
                f"- Sample mode: `{dpm_sampling.get('mode', 'unknown')}`",
                f"- Selected boundaries: `{', '.join(dpm_sampling.get('selected_boundaries', [])) or 'none'}`",
                f"- Aggregate tracked: `{aggregate_counts.get('tracked', 'unavailable')}`",
                f"- Aggregate escaped: `{aggregate_counts.get('escaped', 'unavailable')}`",
                f"- Aggregate trapped: `{aggregate_counts.get('trapped', 'unavailable')}`",
                f"- Aggregate incomplete: `{aggregate_counts.get('incomplete', 'unavailable')}`",
                "",
            ]
        )
        for sample in dpm_sampling.get("samples", []):
            counts = sample.get("counts", {})
            lines.append(
                "- "
                f"{sample.get('name', 'unknown')}: "
                f"tracked `{counts.get('tracked', 'unavailable')}`, "
                f"escaped `{counts.get('escaped', 'unavailable')}`, "
                f"trapped `{counts.get('trapped', 'unavailable')}`, "
                f"incomplete `{counts.get('incomplete', 'unavailable')}`"
            )

    lines.extend(
        [
            "",
            "## Limitations / Claim Class",
            f"- Claim class ceiling: `{result.get('claim_class_ceiling', 'Debug only')}`",
        ]
    )

    for item in result.get("limitations", []):
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"

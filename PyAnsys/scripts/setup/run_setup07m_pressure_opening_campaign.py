#!/usr/bin/env python3
"""Run setup 07m: zero-feed brine-pressure bracket then a guarded inlet ramp.

Every pressure/time-step member is cold-loaded from the accepted setup-07l
step-10 hydrostatic-rest checkpoint.  No member inherits the solution of a
different bracket member.  A later inlet ramp is permitted only when the
zero-feed opening matrix is finite, bounded, monotonic with pressure, quiet at
the centre pressure, and free of DPM tracking.

The pressure values are CFD-derived modified-pressure diagnostics.  They are
not plant or validated downstream brine-line boundary conditions.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import re
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import require_live_compute_node_count  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

import prepare_setup07l_hydrostatic_rest as prepare07l  # noqa: E402
import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07l_hydrostatic_rest as rest07l  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402


STUDY_ID = prepare07l.STUDY_ID
RUN_LABEL = "brine620k_07m_pressure_opening_campaign_v1"
REMOTE_ROOT = prepare07l.REMOTE_ROOT
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
MAX_ITERATIONS_PER_TIME_STEP = 20
MAX_VOF_COURANT = 0.25
LIQUID_FEED_KG_S = 116.92
VAPOR_FEED_KG_S = 80.69
STEAM_OUTLET_PRESSURE_PA = 1_120_000.0
BRINE_FACE_REST_PRESSURE_PA = 1_122_090.4
BRINE_FACE_AREA_M2 = 0.19936247
LIQUID_DENSITY_KG_M3 = transient07j.LIQUID_DENSITY_KG_M3
REFERENCE_LIQUID_VELOCITY_MS = (
    LIQUID_FEED_KG_S / (LIQUID_DENSITY_KG_M3 * BRINE_FACE_AREA_M2)
)
DYNAMIC_PRESSURE_PA = 0.5 * LIQUID_DENSITY_KG_M3 * REFERENCE_LIQUID_VELOCITY_MS**2
PRESSURES = (
    ("low", BRINE_FACE_REST_PRESSURE_PA - DYNAMIC_PRESSURE_PA),
    ("center", BRINE_FACE_REST_PRESSURE_PA),
    ("high", BRINE_FACE_REST_PRESSURE_PA + DYNAMIC_PRESSURE_PA),
)
TIME_STEPS_S = (1.0e-6, 3.0e-6, 1.0e-5)
RAMP_FRACTIONS = (0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 1.00)
RAMP_STEPS_PER_FRACTION = 3
FULL_FLOW_EXTRA_HOLD_STEPS = 7


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({str(key) for row in rows for key in row})
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def case_slug(pressure_label: str, dt_s: float) -> str:
    exponent = int(round(-math.log10(dt_s)))
    coefficient = dt_s * 10**exponent
    coefficient_text = f"{coefficient:g}".replace(".", "p")
    return f"p_{pressure_label}_dt_{coefficient_text}e-{exponent}"


def configured_pressure_outlet_state(
    steam_state: Mapping[str, Any], pressure_pa: float
) -> dict[str, Any]:
    result = copy.deepcopy(dict(steam_state))
    result["name"] = "brineoutlet"
    gauge = nested(result, "phase", "mixture", "momentum", "gauge_pressure")
    backflow = nested(
        result, "phase", "phase-2", "multiphase", "backflow_volume_fraction"
    )
    if not isinstance(gauge, dict) or not isinstance(backflow, dict):
        raise RuntimeError("pressure-outlet state lacks gauge-pressure/backflow branches")
    gauge.update({"option": "value", "value": float(pressure_pa)})
    backflow.update({"option": "value", "value": 1.0})
    return result


def open_brine_pressure_outlet(solver: Any, pressure_pa: float) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions
    before = {
        "walls": list(boundaries.wall.get_object_names()),
        "pressure_outlets": list(boundaries.pressure_outlet.get_object_names()),
    }
    if "brineoutlet" not in before["pressure_outlets"]:
        boundaries.set_zone_type(zone_list=["brineoutlet"], new_type="pressure-outlet")
    outlets = solver.settings.setup.boundary_conditions.pressure_outlet
    outlets["brineoutlet"].set_state(
        configured_pressure_outlet_state(outlets["steamoutlet"].get_state(), pressure_pa)
    )
    after = outlets["brineoutlet"].get_state()
    actual_pressure = nested(
        after, "phase", "mixture", "momentum", "gauge_pressure", "value"
    )
    actual_backflow = nested(
        after,
        "phase",
        "phase-2",
        "multiphase",
        "backflow_volume_fraction",
        "value",
    )
    if actual_pressure is None or not math.isclose(
        float(actual_pressure), pressure_pa, rel_tol=0.0, abs_tol=1.0e-5
    ):
        raise RuntimeError(f"brine pressure readback failed: {actual_pressure}")
    if actual_backflow is None or not math.isclose(
        float(actual_backflow), 1.0, rel_tol=0.0, abs_tol=1.0e-12
    ):
        raise RuntimeError(f"brine liquid-backflow readback failed: {actual_backflow}")
    if "brineoutlet" in solver.settings.setup.boundary_conditions.wall.get_object_names():
        raise RuntimeError("brineoutlet still reads back as a wall")
    return {"before": before, "after": after}


def set_time_step(solver: Any, dt_s: float) -> dict[str, Any]:
    controls = solver.settings.solution.run_calculation.transient_controls
    controls.time_step_size.set_state(dt_s)
    controls.max_iter_per_time_step.set_state(MAX_ITERATIONS_PER_TIME_STEP)
    solver.tui.define.models.multiphase.volume_fraction_parameters.courant_number(
        MAX_VOF_COURANT
    )
    state = controls.get_state()
    actual_dt = nested(state, "time_step_size")
    actual_inner = nested(state, "max_iter_per_time_step")
    if actual_dt is None or not math.isclose(
        float(actual_dt), dt_s, rel_tol=0.0, abs_tol=1.0e-14
    ):
        raise RuntimeError(f"time-step readback failed: {state}")
    if int(actual_inner or -1) != MAX_ITERATIONS_PER_TIME_STEP:
        raise RuntimeError(f"inner-iteration readback failed: {state}")
    return state


def dpm_readback(solver: Any) -> dict[str, Any]:
    dpm = solver.settings.setup.models.discrete_phase
    state = {
        "injection_names": list(dpm.injections.get_object_names()),
        "interaction": dpm.general_settings.interaction.get_state(),
        "unsteady_tracking": dpm.general_settings.unsteady_tracking.get_state(),
    }
    if state["injection_names"]:
        raise RuntimeError(f"DPM injection objects reappeared: {state['injection_names']}")
    if bool(state["interaction"].get("enabled")):
        raise RuntimeError(f"DPM interaction is enabled: {state['interaction']}")
    if bool(state["unsteady_tracking"].get("enabled")):
        raise RuntimeError(f"DPM unsteady tracking is enabled: {state['unsteady_tracking']}")
    return state


def save_pair(solver: Any, remote_stem: str, label: str) -> dict[str, str]:
    case = prepare07l.source07j.remote_join(REMOTE_ROOT, remote_stem + ".cas.h5")
    data = prepare07l.source07j.remote_join(REMOTE_ROOT, remote_stem + ".dat.h5")
    sweep.write_case_data_pair(solver, case, data, label)
    return {"case": case, "data": data}


def start_case_transcript(solver: Any, remote_name: str) -> str:
    try:
        solver.settings.file.stop_transcript()
    except Exception:
        pass
    remote = prepare07l.source07j.remote_join(REMOTE_ROOT, remote_name)
    solver.settings.file.start_transcript(file_name=remote)
    return remote


def stop_and_copy_transcript(solver: Any, remote: str, local: Path) -> str:
    try:
        solver.settings.file.stop_transcript()
    except Exception:
        pass
    text = sweep.remote_text_read_best_effort(solver, remote)
    if text:
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_text(text, encoding="utf-8")
    return text


def residual_tail(solver: Any, count: int = 20) -> list[dict[str, Any]]:
    rows = sweep.monitor_history_rows(solver)
    return rows[-count:] if rows else []


def reversed_flow_counts(text: str) -> list[int]:
    return [
        int(value)
        for value in re.findall(r"Reversed flow on\s+(\d+)\s+faces", text, re.I)
    ]


def finite_failures(row: Mapping[str, Any]) -> list[str]:
    return [
        f"non-finite {key}={value}"
        for key, value in row.items()
        if isinstance(value, (int, float)) and not math.isfinite(float(value))
    ]


def opening_gate(
    row: Mapping[str, Any], transcript_text: str, residuals: Sequence[Mapping[str, Any]]
) -> list[str]:
    failures = finite_failures(row)
    alpha = float(row["domain_volume_avg_liquid_volume_fraction"])
    if not -1.0e-6 <= alpha <= 1.0 + 1.0e-6:
        failures.append(f"volume-averaged liquid fraction outside [0,1]: {alpha}")
    courant = float(row["latest_global_courant"])
    if not math.isfinite(courant) or courant > MAX_VOF_COURANT:
        failures.append(f"Global Courant {courant} exceeds {MAX_VOF_COURANT}")
    for key in (
        "inlet_area_weighted_pressure_pa",
        "steamoutlet_area_weighted_pressure_pa",
        "brine_wall_area_weighted_pressure_pa",
    ):
        if abs(float(row[key]) - STEAM_OUTLET_PRESSURE_PA) > 50_000.0:
            failures.append(f"pressure outside 50-kPa anchor bracket: {key}={row[key]}")
    if abs(float(row["liquid_brineoutlet_kgs"])) > 2.0 * LIQUID_FEED_KG_S:
        failures.append(f"gross brine liquid flow: {row['liquid_brineoutlet_kgs']} kg/s")
    if float(row["brine_wall_area_weighted_velocity_ms"]) > 2.0 * REFERENCE_LIQUID_VELOCITY_MS:
        failures.append(
            f"gross brine velocity: {row['brine_wall_area_weighted_velocity_ms']} m/s"
        )
    if abs(float(row["mixture_steamoutlet_kgs"])) > 0.01 * (
        LIQUID_FEED_KG_S + VAPOR_FEED_KG_S
    ):
        failures.append(f"steam-outlet flow exceeds 1% reference feed: {row['mixture_steamoutlet_kgs']}")
    if abs(float(row["vapor_brineoutlet_kgs"])) > 0.01 * VAPOR_FEED_KG_S:
        failures.append(f"brine vapor flow exceeds 1% vapor feed: {row['vapor_brineoutlet_kgs']}")
    if rest07l.dpm_tracking_evidence(transcript_text):
        failures.append("DPM parcel tracking text reappeared")
    if residuals:
        final_continuity = float(residuals[-1].get("continuity", math.nan))
        row_tail = [float(item.get("continuity", math.nan)) for item in residuals[-5:]]
        if not math.isfinite(final_continuity) or final_continuity > 1.0e-2:
            failures.append(f"final continuity residual exceeds 1e-2: {final_continuity}")
        if len(row_tail) >= 5 and all(math.isfinite(value) for value in row_tail):
            if row_tail[-1] > row_tail[0] and row_tail[-1] > 1.5 * min(row_tail):
                failures.append(f"continuity residual tail is rising: {row_tail}")
    else:
        failures.append("residual history unavailable")
    return failures


def response_pattern_failures(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    """Gate each dt independently on the low/centre/high zero-feed response."""
    failures: list[str] = []
    by_dt: dict[float, dict[str, Mapping[str, Any]]] = {}
    for row in rows:
        by_dt.setdefault(float(row["requested_time_step_s"]), {})[
            str(row["pressure_label"])
        ] = row
    for dt_s in TIME_STEPS_S:
        group = by_dt.get(dt_s, {})
        if set(group) != {"low", "center", "high"}:
            failures.append(f"dt={dt_s:g}: incomplete pressure bracket")
            continue
        # Fluent's report convention is negative for outward flow.
        low = float(group["low"]["liquid_brineoutlet_kgs"])
        center = float(group["center"]["liquid_brineoutlet_kgs"])
        high = float(group["high"]["liquid_brineoutlet_kgs"])
        if not low < center < high:
            failures.append(
                f"dt={dt_s:g}: non-monotonic liquid response low={low}, center={center}, high={high}"
            )
        if low >= 0.0:
            failures.append(f"dt={dt_s:g}: low pressure did not produce outward liquid flow")
        if abs(center) > 0.10 * LIQUID_FEED_KG_S:
            failures.append(f"dt={dt_s:g}: centre flow is not quiet: {center} kg/s")
        if high <= 0.0:
            failures.append(f"dt={dt_s:g}: high pressure did not produce inward liquid flow")
    return failures


def scale_inlet_state(
    state: Mapping[str, Any], *, vapor_kg_s: float, liquid_kg_s: float
) -> dict[str, Any]:
    result = copy.deepcopy(dict(state))
    for phase, value in (("phase-1", vapor_kg_s), ("phase-2", liquid_kg_s)):
        target = nested(result, "phase", phase, "momentum", "mass_flow_rate")
        if not isinstance(target, dict):
            raise RuntimeError(f"inlet state lacks {phase} mass-flow branch")
        target.update({"option": "value", "value": float(value)})
    return result


def set_inlet_fraction(solver: Any, fraction: float) -> dict[str, Any]:
    inlets = solver.settings.setup.boundary_conditions.mass_flow_inlet
    requested = {
        "liquidinlet": {"vapor": 0.0, "liquid": LIQUID_FEED_KG_S * fraction},
        "steaminlet": {"vapor": VAPOR_FEED_KG_S * fraction, "liquid": 0.0},
    }
    result: dict[str, Any] = {}
    for zone, rates in requested.items():
        inlets[zone].set_state(
            scale_inlet_state(
                inlets[zone].get_state(),
                vapor_kg_s=rates["vapor"],
                liquid_kg_s=rates["liquid"],
            )
        )
        after = inlets[zone].get_state()
        for phase, key in (("phase-1", "vapor"), ("phase-2", "liquid")):
            actual = nested(after, "phase", phase, "momentum", "mass_flow_rate", "value")
            if actual is None or not math.isclose(
                float(actual), rates[key], rel_tol=0.0, abs_tol=1.0e-8
            ):
                raise RuntimeError(f"{zone}/{phase} ramp readback failed: {actual}")
        result[zone] = after
    return result


def run_matrix_case(
    solver: Any,
    source_checkpoint: Mapping[str, str],
    baseline_inventory_kg: float,
    domain_volume_m3: float,
    pressure_label: str,
    pressure_pa: float,
    dt_s: float,
) -> tuple[dict[str, Any], dict[str, str]]:
    slug = case_slug(pressure_label, dt_s)
    local_case_root = LOCAL_ROOT / "matrix" / slug
    local_case_root.mkdir(parents=True, exist_ok=True)
    solver.settings.file.read_case(file_name=source_checkpoint["case"])
    solver.settings.file.read_data(file_name=source_checkpoint["data"])
    transcript = start_case_transcript(solver, f"{RUN_LABEL}_{slug}.trn")
    try:
        initial_clock = transient07j.runtime_clock(solver)
        pressure_readback = open_brine_pressure_outlet(solver, pressure_pa)
        controls = set_time_step(solver, dt_s)
        dpm = dpm_readback(solver)
        pre_checkpoint = save_pair(
            solver, f"{RUN_LABEL}_{slug}_opened_t0", f"07m_{slug}_opened_t0"
        )
        solver.settings.solution.run_calculation.dual_time_iterate(
            time_step_count=1, max_iter_per_step=MAX_ITERATIONS_PER_TIME_STEP
        )
        clock = transient07j.runtime_clock(solver)
        if int(clock["time_step"]) != int(initial_clock["time_step"]) + 1:
            raise RuntimeError(f"time-step clock did not advance exactly once: {clock}")
        expected_time = float(initial_clock["flow_time_s"]) + dt_s
        if not math.isclose(
            float(clock["flow_time_s"]),
            expected_time,
            rel_tol=0.0,
            abs_tol=max(1.0e-12, dt_s * 1.0e-6),
        ):
            raise RuntimeError(f"flow-time clock mismatch: expected={expected_time}, actual={clock}")
        metrics = rest07l.physical_metrics(solver, 1)
        metrics.update(rest07l.inventory(metrics, domain_volume_m3))
        metrics.update(clock)
        residuals = residual_tail(solver)
        transcript_text = stop_and_copy_transcript(
            solver, transcript, local_case_root / "transcript.trn"
        )
        courant_values = rest07l.parse_global_courant(transcript_text)
        metrics.update(
            {
                "pressure_label": pressure_label,
                "requested_brine_pressure_pa": pressure_pa,
                "requested_time_step_s": dt_s,
                "liquid_inventory_change_kg": float(metrics["liquid_inventory_kg"])
                - baseline_inventory_kg,
                "latest_global_courant": courant_values[-1]
                if courant_values
                else math.nan,
                "max_global_courant": max(courant_values)
                if courant_values
                else math.nan,
                "max_reversed_flow_faces": max(reversed_flow_counts(transcript_text), default=0),
            }
        )
        failures = opening_gate(metrics, transcript_text, residuals)
        post_checkpoint = save_pair(
            solver, f"{RUN_LABEL}_{slug}_post_step", f"07m_{slug}_post_step"
        )
        write_csv(local_case_root / "residual_history.csv", residuals)
        case_result = {
            "status": "accepted" if not failures else "rejected",
            "classification": "diagnostic / zero-feed pressure-opening",
            "slug": slug,
            "pressure_readback": pressure_readback,
            "transient_controls_readback": controls,
            "dpm_readback": dpm,
            "initial_clock": initial_clock,
            "final_clock": clock,
            "metrics": metrics,
            "gate_failures": failures,
            "pre_step_checkpoint": pre_checkpoint,
            "post_step_checkpoint": post_checkpoint,
        }
        write_json(local_case_root / "case_manifest.json", case_result)
        return case_result, post_checkpoint
    finally:
        # Safe if the transcript was already stopped after a successful step.
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass


def ramp_gate(
    row: Mapping[str, Any],
    transcript_text: str,
    residuals: Sequence[Mapping[str, Any]],
) -> list[str]:
    failures = finite_failures(row)
    if float(row["latest_global_courant"]) > MAX_VOF_COURANT:
        failures.append(f"Global Courant exceeds {MAX_VOF_COURANT}")
    if not -1.0e-6 <= float(row["domain_volume_avg_liquid_volume_fraction"]) <= 1.0 + 1.0e-6:
        failures.append("volume-averaged liquid fraction is unbounded")
    for key in (
        "inlet_area_weighted_pressure_pa",
        "steamoutlet_area_weighted_pressure_pa",
        "brine_wall_area_weighted_pressure_pa",
    ):
        if abs(float(row[key]) - STEAM_OUTLET_PRESSURE_PA) > 100_000.0:
            failures.append(f"ramp pressure left 100-kPa safety bracket: {key}={row[key]}")
    if abs(float(row["liquid_brineoutlet_kgs"])) > 5.0 * LIQUID_FEED_KG_S:
        failures.append(f"gross ramp brine-liquid flow: {row['liquid_brineoutlet_kgs']}")
    if abs(float(row["vapor_brineoutlet_kgs"])) > 0.05 * VAPOR_FEED_KG_S:
        failures.append(f"gross vapor ingress/egress at brine outlet: {row['vapor_brineoutlet_kgs']}")
    if rest07l.dpm_tracking_evidence(transcript_text):
        failures.append("DPM parcel tracking text reappeared")
    if not residuals:
        failures.append("ramp residual history unavailable")
    else:
        continuity = float(residuals[-1].get("continuity", math.nan))
        if not math.isfinite(continuity) or continuity > 1.0e-2:
            failures.append(f"ramp final continuity residual exceeds 1e-2: {continuity}")
    return failures


def run_ramp(
    solver: Any,
    parent_checkpoint: Mapping[str, str],
    pressure_pa: float,
    domain_volume_m3: float,
    dt_s: float,
    *,
    fractions: Sequence[float] = RAMP_FRACTIONS,
    steps_per_fraction: int = RAMP_STEPS_PER_FRACTION,
    full_flow_extra_hold_steps: int = FULL_FLOW_EXTRA_HOLD_STEPS,
    output_name: str = "inlet_ramp",
) -> dict[str, Any]:
    ramp_root = LOCAL_ROOT / output_name
    ramp_root.mkdir(parents=True, exist_ok=True)
    remote_output_slug = re.sub(r"[^A-Za-z0-9_-]+", "_", output_name)
    solver.settings.file.read_case(file_name=parent_checkpoint["case"])
    solver.settings.file.read_data(file_name=parent_checkpoint["data"])
    transcript = start_case_transcript(solver, f"{RUN_LABEL}_inlet_ramp.trn")
    result: dict[str, Any] = {
        "status": "running",
        "classification": "diagnostic / conditional proportional inlet ramp",
        "parent_checkpoint": parent_checkpoint,
        "fixed_brine_pressure_pa": pressure_pa,
        "time_step_size_s": dt_s,
        "fractions": list(fractions),
        "steps_per_fraction": steps_per_fraction,
        "checkpoints": {},
        "blocks": [],
        "started_epoch": time.time(),
    }
    manifest_path = ramp_root / "ramp_manifest.json"
    write_json(manifest_path, result)
    rows: list[dict[str, Any]] = []
    try:
        open_brine_pressure_outlet(solver, pressure_pa)
        set_time_step(solver, dt_s)
        dpm_readback(solver)
        start_clock = transient07j.runtime_clock(solver)
        credited = 0
        for fraction in fractions:
            inlet_readback = set_inlet_fraction(solver, fraction)
            for _ in range(steps_per_fraction):
                solver.settings.solution.run_calculation.dual_time_iterate(
                    time_step_count=1, max_iter_per_step=MAX_ITERATIONS_PER_TIME_STEP
                )
                credited += 1
                clock = transient07j.runtime_clock(solver)
                expected_step = int(start_clock["time_step"]) + credited
                expected_time = float(start_clock["flow_time_s"]) + credited * dt_s
                if int(clock["time_step"]) != expected_step or not math.isclose(
                    float(clock["flow_time_s"]),
                    expected_time,
                    rel_tol=0.0,
                    abs_tol=max(1.0e-12, dt_s * 1.0e-6),
                ):
                    raise RuntimeError(f"ramp clock proof failed at step {credited}: {clock}")
            metrics = rest07l.physical_metrics(solver, credited)
            metrics.update(rest07l.inventory(metrics, domain_volume_m3))
            metrics.update(transient07j.runtime_clock(solver))
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
            courant = rest07l.parse_global_courant(transcript_text)
            row = {
                **metrics,
                "ramp_fraction": fraction,
                "credited_ramp_steps": credited,
                "latest_global_courant": courant[-1] if courant else math.nan,
                "max_global_courant": max(courant) if courant else math.nan,
                "max_reversed_flow_faces": max(reversed_flow_counts(transcript_text), default=0),
            }
            residuals = residual_tail(solver)
            failures = ramp_gate(row, transcript_text, residuals)
            rows.append(row)
            checkpoint = save_pair(
                solver,
                f"{RUN_LABEL}_{remote_output_slug}_fraction_{str(fraction).replace('.', 'p')}",
                f"07m_ramp_fraction_{fraction:g}",
            )
            result["checkpoints"][f"{fraction:g}"] = checkpoint
            result["blocks"].append(
                {
                    "fraction": fraction,
                    "credited_steps": credited,
                    "inlet_readback": inlet_readback,
                    "metrics": row,
                    "gate_failures": failures,
                }
            )
            result["last_heartbeat_epoch"] = time.time()
            write_csv(ramp_root / "physical_history.csv", rows)
            write_json(manifest_path, result)
            print(
                f"07m ramp: fraction={fraction:.0%}; steps={credited}; "
                f"Co={row['latest_global_courant']:.6g}; "
                f"m_brine_l={row['liquid_brineoutlet_kgs']:.6g} kg/s",
                flush=True,
            )
            if failures:
                raise RuntimeError("ramp gate failed: " + "; ".join(failures))
        if full_flow_extra_hold_steps:
            if not fractions or not math.isclose(float(fractions[-1]), 1.0):
                raise RuntimeError("a full-flow hold requires the final ramp fraction to be 1.0")
            # The production promotion rule requires ten consecutive full-flow
            # steps.  The default schedule supplies three and this hold adds seven.
            for _ in range(full_flow_extra_hold_steps):
                solver.settings.solution.run_calculation.dual_time_iterate(
                    time_step_count=1, max_iter_per_step=MAX_ITERATIONS_PER_TIME_STEP
                )
                credited += 1
                clock = transient07j.runtime_clock(solver)
                expected_step = int(start_clock["time_step"]) + credited
                expected_time = float(start_clock["flow_time_s"]) + credited * dt_s
                if int(clock["time_step"]) != expected_step or not math.isclose(
                    float(clock["flow_time_s"]),
                    expected_time,
                    rel_tol=0.0,
                    abs_tol=max(1.0e-12, dt_s * 1.0e-6),
                ):
                    raise RuntimeError(f"full-flow hold clock proof failed: {clock}")
            metrics = rest07l.physical_metrics(solver, credited)
            metrics.update(rest07l.inventory(metrics, domain_volume_m3))
            metrics.update(transient07j.runtime_clock(solver))
            transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
            courant = rest07l.parse_global_courant(transcript_text)
            hold_row = {
                **metrics,
                "ramp_fraction": 1.0,
                "credited_ramp_steps": credited,
                "full_flow_hold_steps": steps_per_fraction + full_flow_extra_hold_steps,
                "latest_global_courant": courant[-1] if courant else math.nan,
                "max_global_courant": max(courant) if courant else math.nan,
                "max_reversed_flow_faces": max(reversed_flow_counts(transcript_text), default=0),
            }
            hold_residuals = residual_tail(solver)
            hold_failures = ramp_gate(hold_row, transcript_text, hold_residuals)
            rows.append(hold_row)
            hold_checkpoint = save_pair(
                solver,
                f"{RUN_LABEL}_{remote_output_slug}_full_hold10",
                "07m_ramp_full_hold10",
            )
            result["checkpoints"]["full_hold10"] = hold_checkpoint
            result["blocks"].append(
                {
                    "fraction": 1.0,
                    "credited_steps": credited,
                    "full_flow_hold_steps": steps_per_fraction
                    + full_flow_extra_hold_steps,
                    "metrics": hold_row,
                    "gate_failures": hold_failures,
                }
            )
            write_csv(ramp_root / "physical_history.csv", rows)
            write_json(manifest_path, result)
            print(
                f"07m ramp: full-flow hold={steps_per_fraction + full_flow_extra_hold_steps} "
                f"steps; total={credited}; Co={hold_row['latest_global_courant']:.6g}; "
                f"m_brine_l={hold_row['liquid_brineoutlet_kgs']:.6g} kg/s",
                flush=True,
            )
            if hold_failures:
                raise RuntimeError("full-flow hold gate failed: " + "; ".join(hold_failures))
        transcript_text = stop_and_copy_transcript(
            solver, transcript, ramp_root / "transcript.trn"
        )
        residuals = residual_tail(solver, MAX_ITERATIONS_PER_TIME_STEP * 5)
        write_csv(ramp_root / "residual_history_tail.csv", residuals)
        result.update(
            {
                "status": "completed",
                "classification": "diagnostic / bounded proportional inlet-ramp startup",
                "credited_steps": credited,
                "final_clock": transient07j.runtime_clock(solver),
                "dpm_tracking_evidence": rest07l.dpm_tracking_evidence(transcript_text),
                "completed_epoch": time.time(),
                "limitation": (
                    "The arbitrary short ramp is a startup diagnostic only; it does not "
                    "establish downstream pressure, long-time level control, or production balance."
                ),
            }
        )
        write_json(manifest_path, result)
        return result
    except Exception as exc:
        result.update(
            {
                "status": "failed",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, result)
        raise
    finally:
        try:
            stop_and_copy_transcript(solver, transcript, ramp_root / "transcript.trn")
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", choices=("1", "2", "3"), default="1")
    parser.add_argument("--skip-ramp", action="store_true")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)

    source_root = prepare07l.local_root_for_server(args.server_id)
    source_preparation_path = source_root / "preparation_manifest.json"
    source_qualification_path = source_root / "qualification_manifest.json"
    source_preparation = json.loads(source_preparation_path.read_text(encoding="utf-8"))
    source_qualification = json.loads(source_qualification_path.read_text(encoding="utf-8"))
    if source_preparation.get("status") != "accepted":
        raise RuntimeError("setup-07l preparation is not accepted")
    if source_qualification.get("status") != "completed":
        raise RuntimeError("setup-07l qualification is not completed")
    source_checkpoint = source_qualification.get("checkpoints", {}).get("10")
    if not isinstance(source_checkpoint, Mapping) or not source_checkpoint.get("case"):
        raise RuntimeError("accepted setup-07l step-10 checkpoint is unavailable")
    source_metrics = source_qualification["blocks"][-1]["metrics"]
    baseline_inventory = float(source_metrics["liquid_inventory_kg"])
    domain_volume = float(source_preparation["mesh_metrics"]["domain_volume_m3"])

    manifest_path = LOCAL_ROOT / "campaign_manifest.json"
    attempt_history: list[dict[str, Any]] = []
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        attempt_history = list(previous.get("attempt_history", []))
        attempt_history.append(
            {
                "status": previous.get("status"),
                "classification": previous.get("classification"),
                "error": previous.get("error"),
                "controller_pid": previous.get("controller_pid"),
                "started_epoch": previous.get("started_epoch"),
                "failed_epoch": previous.get("failed_epoch"),
                "mutation_note": (
                    "attempt ended during live-rank preflight before any case/data load "
                    "or Fluent setting change"
                ),
            }
        )
    campaign: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": args.server_id,
        "controller_pid": os.getpid(),
        "status": "running",
        "classification": "diagnostic / pressure-opening matrix",
        "source_checkpoint": source_checkpoint,
        "source_setup": "accepted setup-07l step-10 hydrostatic rest",
        "pressure_definition": (
            "CFD-derived closed-face modified-pressure rest bracket (diagnostic); "
            "not a plant or validated downstream pressure"
        ),
        "rest_pressure_pa": BRINE_FACE_REST_PRESSURE_PA,
        "dynamic_pressure_half_width_pa": DYNAMIC_PRESSURE_PA,
        "pressure_cases_pa": {label: value for label, value in PRESSURES},
        "time_step_cases_s": list(TIME_STEPS_S),
        "matrix_members": [],
        "attempt_history": attempt_history,
        "controlled_conditions": {
            "inlet_flows": "zero for both phases at both inlets",
            "steamoutlet_pressure_pa": STEAM_OUTLET_PRESSURE_PA,
            "brine_backflow": "liquid VF=1, vapor VF=0",
            "DPM": "zero injections; interaction and unsteady tracking off",
            "EWF": "off/not introduced",
            "sink": "off/not introduced",
            "unchanged": (
                "transient explicit VOF, Geo-Reconstruct, RNG k-epsilon, gravity, "
                "Energy off, PISO, PRESTO, implicit body force, WFGC, 620431-cell mesh"
            ),
        },
        "started_epoch": time.time(),
    }
    write_json(manifest_path, campaign)

    # PyFluent must stream the console for the connectivity-roster parser to
    # receive Fluent's asynchronous table.  The stream is stopped before the
    # first file load and each formal case uses its own Fluent transcript.
    solver = connect(server_id=args.server_id, start_transcript=True)
    try:
        campaign["live_parallel_runtime"] = require_live_compute_node_count(
            solver, prepare07l.EXPECTED_COMPUTE_NODES
        )
        solver.transcript.stop()
        rows: list[dict[str, Any]] = []
        center_parent: dict[str, str] | None = None
        fatal_error = None
        for pressure_label, pressure_pa in PRESSURES:
            for dt_s in TIME_STEPS_S:
                print(
                    f"07m matrix: starting pressure={pressure_label} "
                    f"({pressure_pa:.3f} Pa), dt={dt_s:g} s",
                    flush=True,
                )
                try:
                    member, checkpoint = run_matrix_case(
                        solver,
                        source_checkpoint,
                        baseline_inventory,
                        domain_volume,
                        pressure_label,
                        pressure_pa,
                        dt_s,
                    )
                    campaign["matrix_members"].append(member)
                    rows.append(member["metrics"])
                    if pressure_label == "center" and math.isclose(dt_s, 1.0e-6):
                        center_parent = checkpoint
                    campaign["last_heartbeat_epoch"] = time.time()
                    write_csv(LOCAL_ROOT / "matrix_summary.csv", rows)
                    write_json(manifest_path, campaign)
                    print(
                        f"07m matrix: {member['slug']} -> {member['status']}; "
                        f"m_brine_l={member['metrics']['liquid_brineoutlet_kgs']:.6g} kg/s; "
                        f"Co={member['metrics']['latest_global_courant']:.6g}",
                        flush=True,
                    )
                except Exception as exc:
                    fatal_error = f"{type(exc).__name__}: {exc}"
                    break
            if fatal_error:
                break

        if fatal_error:
            raise RuntimeError(f"matrix member failed before a trustworthy checkpoint: {fatal_error}")
        individual_failures = [
            failure
            for member in campaign["matrix_members"]
            for failure in member.get("gate_failures", [])
        ]
        pattern_failures = response_pattern_failures(rows)
        campaign["individual_gate_failures"] = individual_failures
        campaign["response_pattern_failures"] = pattern_failures
        ramp_eligible = not individual_failures and not pattern_failures
        campaign["ramp_eligible"] = ramp_eligible
        campaign["matrix_status"] = "accepted" if ramp_eligible else "rejected"
        write_json(manifest_path, campaign)

        if args.skip_ramp or not ramp_eligible:
            campaign.update(
                {
                    "status": "completed",
                    "classification": (
                        "diagnostic / pressure-opening matrix accepted"
                        if ramp_eligible
                        else "diagnostic / pressure-opening matrix unresolved; ramp withheld"
                    ),
                    "ramp_status": "skipped" if args.skip_ramp else "withheld by gates",
                    "completed_epoch": time.time(),
                }
            )
            write_json(manifest_path, campaign)
            return 0 if ramp_eligible else 2

        if center_parent is None:
            raise RuntimeError("accepted centre-pressure 1e-6 checkpoint is unavailable")
        campaign["classification"] = "diagnostic / conditional inlet ramp running"
        write_json(manifest_path, campaign)
        ramp = run_ramp(
            solver,
            center_parent,
            BRINE_FACE_REST_PRESSURE_PA,
            domain_volume,
            1.0e-6,
        )
        campaign.update(
            {
                "status": "completed",
                "classification": "diagnostic / pressure-opening matrix plus inlet ramp",
                "ramp_status": ramp["status"],
                "ramp_manifest": str(LOCAL_ROOT / "inlet_ramp" / "ramp_manifest.json"),
                "completed_epoch": time.time(),
                "production_claim": False,
                "unresolved_physical_inputs": [
                    "downstream brine static pressure",
                    "downstream liquid-level datum",
                    "pipe/valve resistance curve",
                    "confirmed brine-face submergence and operating level",
                ],
            }
        )
        write_json(manifest_path, campaign)
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        campaign.update(
            {
                "status": "failed",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(manifest_path, campaign)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Cold-reload setup 07b and optionally run one protected diagnostic iteration."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import parse_named_report_rows  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402


STUDY_ID = "split_inlet_constant_water_level_sink_20260807"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
DEFAULT_CASE = REMOTE_ROOT + r"\mesh-900k_07b_sink_hook_v1_retry4_hooked_ramp0.cas.h5"
DEFAULT_DATA = REMOTE_ROOT + r"\mesh-900k_07b_sink_hook_v1_retry4_hooked_ramp0.dat.h5"
LIBRARY = "lib07b_cwl_bdfa31b0ec_r4"
EXPECTED_CELLS = 5_335_623


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--case", default=DEFAULT_CASE)
    result.add_argument("--data", default=DEFAULT_DATA)
    result.add_argument("--run-label", default="mesh-900k_07b_sink_smoke_v1")
    result.add_argument("--smoke", action="store_true")
    result.add_argument("--smoke-ramp", type=float, default=0.05)
    return result


def scalar_fields(solver: Any) -> list[str]:
    try:
        return [str(value) for value in solver.fields.field_data.scalar_fields.allowed_values()]
    except Exception:
        return [str(value) for value in solver.fields.field_info.get_scalar_fields_info()]


def find_field(allowed: Iterable[str], preferred: str, fallback: str) -> str:
    values = [str(value) for value in allowed]
    exact = [value for value in values if value.lower() == preferred.lower()]
    if len(exact) == 1:
        return exact[0]
    token = re.sub(r"[^a-z0-9]+", "", preferred.lower())
    matches = [
        value
        for value in values
        if token in re.sub(r"[^a-z0-9]+", "", value.lower())
    ]
    if len(matches) == 1:
        return matches[0]
    fallback_matches = [value for value in values if value.lower() == fallback.lower()]
    if len(fallback_matches) == 1:
        return fallback_matches[0]
    raise RuntimeError(
        f"readback mismatch: could not resolve UDM field {preferred!r}; "
        f"fallback={fallback!r}; UDM candidates="
        f"{[value for value in values if 'udm' in value.lower() or 'cwl07b' in value.lower()]}"
    )


def source_readback(solver: Any) -> dict[str, Any]:
    cell_zone = solver.settings.setup.cell_zone_conditions.fluid["fluid"]
    return {
        "liquid_sources": cell_zone.phase["phase-2"].sources.get_state(),
        "vapor_sources": cell_zone.phase["phase-1"].sources.get_state(),
        "mixture_sources": cell_zone.phase["mixture"].sources.get_state(),
    }


def validate_source_readback(
    readback: dict[str, Any], *, library: str = LIBRARY
) -> list[str]:
    errors: list[str] = []
    liquid = readback["liquid_sources"]
    vapor = readback["vapor_sources"]
    mixture = readback["mixture_sources"]
    expected = {
        "mass": f"cwl_liquid_mass_sink::{library}",
        "x-momentum": f"cwl_x_momentum_sink::{library}",
        "y-momentum": f"cwl_y_momentum_sink::{library}",
        "z-momentum": f"cwl_z_momentum_sink::{library}",
    }
    if not liquid.get("enable"):
        errors.append("liquid phase sources are disabled")
    if vapor.get("enable"):
        errors.append("vapor phase sources must remain disabled")
    if not mixture.get("enable"):
        errors.append("mixture momentum sources are disabled")
    for group, state, names in (
        ("liquid", liquid, ("mass",)),
        ("mixture", mixture, ("x-momentum", "y-momentum", "z-momentum")),
    ):
        terms = state.get("terms", {})
        for name in names:
            entries = terms.get(name, [])
            expected_udf = expected[name]
            if entries != [{"option": "udf", "udf": expected_udf}]:
                errors.append(
                    f"{group} {name} hook mismatch: expected={expected_udf!r}; "
                    f"actual={entries}"
                )
    return errors


def volume_integral(solver: Any, run_label: str, field: str) -> float:
    report = solver.settings.results.report.volume_integrals
    text = mesh_study.report_file_text(
        solver,
        REMOTE_ROOT,
        run_label,
        lambda path: report.volume_integral(
            cell_zones=["fluid"],
            cell_function=field,
            write_to_file=True,
            file_name=path,
            append_data=False,
        ),
    )
    rows = parse_named_report_rows(text, ["fluid"])
    if "fluid" not in rows:
        raise RuntimeError(f"could not parse volume integral of {field}: {text}")
    return float(rows["fluid"])


def rp_readback(solver: Any) -> dict[str, Any]:
    names = (
        "user/cwl07b/bottom-zone-id",
        "user/cwl07b/liquid-phase-index",
        "user/cwl07b/tau-s",
        "user/cwl07b/ramp",
        "user/cwl07b/alpha-min",
    )
    return {name: solver.scheme.eval(f"(rpgetvar '{name})") for name in names}


def latest_monitor_iteration(snapshot: dict[str, dict[str, Any]]) -> float | None:
    values = [
        float(item["last_iteration"])
        for item in snapshot.values()
        if item.get("last_iteration") is not None
    ]
    return max(values) if values else None


def main() -> int:
    args = parser().parse_args()
    if args.smoke and not 0.0 < args.smoke_ramp <= 0.1:
        raise ValueError("--smoke-ramp must lie in (0, 0.1]")
    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    output = LOCAL_ROOT / f"{args.run_label}_verification.json"
    solver = connect(server_id=args.server_id)
    payload: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": args.run_label,
        "status": "running",
        "classification": "diagnostic",
        "source_case": args.case,
        "source_data": args.data,
        "smoke_requested": args.smoke,
        "dpm": "off; no injections updated or tracked",
        "started_epoch": time.time(),
    }
    transcript = setup07b.remote_join(REMOTE_ROOT, f"{args.run_label}_transcript.trn")
    try:
        solver.settings.file.read_case(file_name=args.case)
        solver.settings.file.read_data(file_name=args.data)
        mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
        if int(mesh_metrics.get("cells", -1)) != EXPECTED_CELLS:
            raise RuntimeError(f"expected {EXPECTED_CELLS} cells; actual={mesh_metrics}")
        settings = mesh_study.capture_settings(solver, REMOTE_ROOT)
        settings.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
        errors = mesh_study.validate_settings(
            settings, mesh_metrics, require_phase_identity=True
        )
        hooks = source_readback(solver)
        errors.extend(validate_source_readback(hooks))
        parameters = rp_readback(solver)
        if not math.isclose(float(parameters["user/cwl07b/ramp"]), 0.0, abs_tol=1e-14):
            errors.append(f"cold-reload ramp is not zero: {parameters}")
        allowed = scalar_fields(solver)
        udm_fields = [
            field
            for field in allowed
            if "udm" in field.lower() or "cwl07b" in field.lower()
        ]
        if len(udm_fields) < 5:
            errors.append(f"fewer than five UDM fields after cold reload: {udm_fields}")
        payload.update(
            {
                "fluent_version": str(solver.get_fluent_version()),
                "fluent_health": str(solver.health_check.status()),
                "mesh_metrics": mesh_metrics,
                "mesh_quality_transcript": quality_text,
                "settings_readback": settings,
                "source_readback": hooks,
                "rp_parameter_readback": parameters,
                "udm_fields": udm_fields,
                "cold_reload_validation_errors": errors,
            }
        )
        if errors:
            raise RuntimeError("cold-reload validation failed: " + "; ".join(errors))

        if args.smoke:
            solver.settings.file.start_transcript(file_name=transcript)
            mask_field = find_field(
                allowed, "cwl07b-bottom-adjacent-mask", "udm-0"
            )
            mass_field = find_field(
                allowed, "cwl07b-liquid-mass-source-kgm3s", "udm-1"
            )
            sweep.start_iteration_monitor(solver)
            before_monitor = sweep.monitor_iteration_snapshot(solver)
            before_iteration = latest_monitor_iteration(before_monitor)
            command_counter_before = sweep.read_iteration_count(solver)
            setup07b.define_or_set_rp_var(
                solver, "user/cwl07b/ramp", args.smoke_ramp, "real"
            )
            try:
                solver.settings.solution.run_calculation.iterate(iter_count=1)
            finally:
                setup07b.define_or_set_rp_var(
                    solver, "user/cwl07b/ramp", 0.0, "real"
                )
            after_monitor = sweep.monitor_iteration_snapshot(solver)
            after_iteration = latest_monitor_iteration(after_monitor)
            command_counter_after = sweep.read_iteration_count(solver)
            if (
                before_iteration is None
                or after_iteration is None
                or not math.isclose(after_iteration, before_iteration + 1.0, abs_tol=1e-12)
            ):
                raise RuntimeError(
                    "one-iteration residual-history proof failed: "
                    f"before={before_iteration}; after={after_iteration}"
                )
            mask_integral = volume_integral(
                solver, f"{args.run_label}_mask_integral", mask_field
            )
            mass_sink_kgs = volume_integral(
                solver, f"{args.run_label}_mass_integral", mass_field
            )
            if mask_integral <= 0.0:
                raise RuntimeError(f"bottom-adjacent mask integral is not positive: {mask_integral}")
            if mass_sink_kgs >= 0.0:
                raise RuntimeError(f"liquid source integral is not a sink: {mass_sink_kgs}")
            checkpoint = setup07b.save_pair(
                solver, REMOTE_ROOT, f"{args.run_label}_one_iter_ramp_reset0"
            )
            payload["smoke_test"] = {
                "status": "accepted",
                "iterations_run": 1,
                "iteration_before": before_iteration,
                "iteration_after": after_iteration,
                "monitor_snapshot_before": before_monitor,
                "monitor_snapshot_after": after_monitor,
                "fluent_command_counter_before": command_counter_before,
                "fluent_command_counter_after": command_counter_after,
                "command_counter_note": (
                    "number-of-iterations is a per-command control in this case, not the "
                    "cumulative residual-history iteration; acceptance uses monitor history"
                ),
                "ramp_during_iteration": args.smoke_ramp,
                "ramp_after_iteration": solver.scheme.eval(
                    "(rpgetvar 'user/cwl07b/ramp)"
                ),
                "mask_field": mask_field,
                "mass_source_field": mass_field,
                "bottom_adjacent_mask_integral_m3": mask_integral,
                "integrated_liquid_mass_source_kgs": mass_sink_kgs,
                "checkpoint": checkpoint,
                "transcript": transcript,
            }
        payload.update(
            {
                "status": "complete",
                "completed_epoch": time.time(),
                "accepted_scope": (
                    "compiled/hooked persistence and one-iteration source execution"
                    if args.smoke
                    else "compiled/hooked persistence only"
                ),
                "not_accepted_scope": (
                    "steady carrier solution, sink time-scale selection, separator performance, "
                    "or mesh convergence"
                ),
            }
        )
    except BaseException as exc:
        payload.update(
            {
                "status": "unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        raise
    finally:
        try:
            if args.smoke:
                setup07b.define_or_set_rp_var(
                    solver, "user/cwl07b/ramp", 0.0, "real"
                )
        finally:
            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            setup07b.write_json(output, payload)
            print(json.dumps(payload, indent=2, default=str), flush=True)
            print(f"Verification written to {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

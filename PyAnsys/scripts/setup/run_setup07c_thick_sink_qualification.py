#!/usr/bin/env python3
"""Build and run setup 07c's bounded thick-sink diagnostic on clean mesh-900k."""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import classify_failure  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07b_sink_qualification as qualify07b  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import setup07c_thick_water_level_sink as setup07c  # noqa: E402
import verify_constant_water_level_sink as verify07b  # noqa: E402


STUDY_ID = "split_inlet_thickened_water_level_sink_20260808"
RUN_LABEL = "mesh-900k_band0p140165_tau0p100_v1"
LOCAL_DIR = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
REMOTE_DIR = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\{RUN_LABEL}"
ORIGINAL_MESH = r"C:\Users\qtra338\Documents\Mesh study\Meshes\mesh-900k.msh"
SETTINGS_FILE = r"C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set"
TEMPLATE_CASE = r"C:\Users\qtra338\Documents\Mesh study\partial_solution_diagnostic_20260801.cas.h5"
EXPECTED_CELLS = 5_335_623
EXPECTED_BASELINE_FINGERPRINT = (
    "424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5"
)
BOTTOM_AREA_M2 = 3.1649776
ONE_CELL_MASK_VOLUME_M3 = 0.027726243
ONE_CELL_MASK_COUNT = 5_438
NOMINAL_LAYERS = 16
DEFAULT_THICKNESS_M = NOMINAL_LAYERS * ONE_CELL_MASK_VOLUME_M3 / BOTTOM_AREA_M2
RAMP_STAGES = (
    (0.025, 100),
    (0.05, 100),
    (0.10, 150),
    (0.25, 150),
    (0.50, 250),
    (0.75, 250),
)
MASK_READBACK = re.compile(
    r"face-y=\[(?P<face_min>[-+0-9.eE]+),(?P<face_max>[-+0-9.eE]+)\].*?"
    r"thickness=(?P<thickness>[-+0-9.eE]+).*?marked-cells=(?P<count>[-+0-9.eE]+).*?"
    r"mask-volume=(?P<volume>[-+0-9.eE]+).*?marked-y=\[(?P<y_min>[-+0-9.eE]+),"
    r"(?P<y_max>[-+0-9.eE]+)\].*?liquid-inventory=(?P<inventory>[-+0-9.eE]+)",
    re.I | re.S,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--study-id", default=STUDY_ID)
    result.add_argument("--run-label", default=RUN_LABEL)
    result.add_argument(
        "--setup-branch",
        default="07c diagnostic thickened constant-water-level sink",
    )
    result.add_argument("--tau-s", type=float, default=0.1)
    result.add_argument("--layer-thickness-m", type=float, default=DEFAULT_THICKNESS_M)
    result.add_argument("--block", type=int, default=250)
    result.add_argument("--maximum-r1-iterations", type=int, default=2000)
    result.add_argument("--minimum-r1-iterations", type=int, default=1000)
    result.add_argument("--stable-windows-required", type=int, default=2)
    result.add_argument("--residual-limit", type=float, default=1.0e-3)
    result.add_argument("--minimum-free-gb", type=float, default=25.0)
    return result


def persist(
    manifest: Mapping[str, Any],
    physical_rows: list[dict[str, Any]],
    residual_rows: list[dict[str, Any]],
) -> None:
    mesh_study.write_json(LOCAL_DIR / "qualification_manifest.json", manifest)
    if physical_rows:
        mesh_study.write_csv(LOCAL_DIR / "physical_monitor_history.csv", physical_rows)
        mesh_study.write_csv(LOCAL_DIR / "mass_balance_history.csv", physical_rows)
    if residual_rows:
        sweep.write_monitor_history_csv(LOCAL_DIR / "residual_history.csv", residual_rows)


def parse_mask_readback(text: str) -> dict[str, float]:
    matches = list(MASK_READBACK.finditer(text))
    if not matches:
        raise RuntimeError(f"could not parse CWL07C mask readback: {text}")
    return {name: float(value) for name, value in matches[-1].groupdict().items()}


def validate_mask(
    readback: Mapping[str, float], *, bottom_y_m: float, thickness_m: float
) -> list[str]:
    errors: list[str] = []
    if readback["count"] <= ONE_CELL_MASK_COUNT:
        errors.append(f"thick mask count did not exceed 07b: {readback['count']}")
    if readback["volume"] <= ONE_CELL_MASK_VOLUME_M3:
        errors.append(f"thick mask volume did not exceed 07b: {readback['volume']}")
    if abs(readback["face_max"] - readback["face_min"]) > 1.0e-8:
        errors.append(f"bottom wall is not planar in y: {readback}")
    if not readback["face_min"] - 1.0e-8 <= bottom_y_m <= readback["face_max"] + 1.0e-8:
        errors.append(f"configured bottom y does not match bottom wall: {readback}")
    if readback["y_min"] < bottom_y_m - 1.0e-8:
        errors.append(f"mask extends below bottom: {readback}")
    maximum_allowed = bottom_y_m + thickness_m + 0.02
    if readback["y_max"] > maximum_allowed:
        errors.append(f"mask extends above requested band tolerance: {readback}")
    return errors


def latest_fields(solver: Any) -> tuple[str, str, list[str]]:
    fields = verify07b.scalar_fields(solver)
    mask = verify07b.find_field(fields, "cwl07c-thick-bottom-mask", "udm-0")
    source = verify07b.find_field(
        fields, "cwl07c-liquid-mass-source-kgm3s", "udm-1"
    )
    return mask, source, fields


def abrupt_change(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for name in (
        "pressure_drop_pa",
        "domain_liquid_inventory_kg",
        "sink_magnitude_kgs",
    ):
        old = abs(float(previous[name]))
        new = abs(float(current[name]))
        scale = max(old, new, 1.0e-12)
        result[name] = abs(new - old) / scale * 100.0
    return result


def main() -> int:
    global STUDY_ID, RUN_LABEL, LOCAL_DIR, REMOTE_DIR
    args = parser().parse_args()
    if args.tau_s <= 0.0 or args.layer_thickness_m <= 0.0:
        raise ValueError("tau and layer thickness must be positive")
    if args.maximum_r1_iterations < args.minimum_r1_iterations:
        raise ValueError("maximum R=1 iterations must be at least the minimum")

    STUDY_ID = args.study_id
    RUN_LABEL = args.run_label
    LOCAL_DIR = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
    REMOTE_DIR = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\{RUN_LABEL}"

    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    qualify07b.REMOTE_DIR = REMOTE_DIR
    qualify07b.LOCAL_DIR = LOCAL_DIR
    solver = connect(server_id=args.server_id)
    mesh_study.ensure_remote_directory(solver, REMOTE_DIR)
    physical_rows: list[dict[str, Any]] = []
    residual_rows: list[dict[str, Any]] = []
    stable_windows = 0
    stop_reason = ""
    transcript = setup07b.remote_join(REMOTE_DIR, "qualification_transcript.trn")
    manifest: dict[str, Any] = {
        "study_id": STUDY_ID,
        "setup_branch": args.setup_branch,
        "run_label": RUN_LABEL,
        "status": "preflight",
        "classification": "diagnostic in progress",
        "source_origin": "clean original mesh-900k.msh plus authoritative settings and fresh Hybrid Initialization",
        "original_mesh": ORIGINAL_MESH,
        "settings_file": SETTINGS_FILE,
        "template_case": TEMPLATE_CASE,
        "saved_solution_data_loaded": False,
        "nominal_equivalent_layers": NOMINAL_LAYERS,
        "one_cell_equivalent_thickness_m": ONE_CELL_MASK_VOLUME_M3 / BOTTOM_AREA_M2,
        "layer_thickness_m": args.layer_thickness_m,
        "tau_s": args.tau_s,
        "sink_strength_relative_to_tau_0p100": 0.1 / args.tau_s,
        "controlled_sensitivity": (
            "change only the liquid-sink time scale; preserve clean original "
            "mesh, band thickness, carrier physics, boundaries, solver controls, "
            "fresh initialization and DPM-off state"
        ),
        "ramp_stages": list(RAMP_STAGES),
        "maximum_r1_iterations": args.maximum_r1_iterations,
        "minimum_r1_iterations": args.minimum_r1_iterations,
        "dpm": "off; no injection update or tracking",
        "transcript": transcript,
        "checkpoints": {},
        "iteration_evidence": [],
        "started_epoch": time.time(),
    }
    persist(manifest, physical_rows, residual_rows)
    try:
        for path, label in (
            (ORIGINAL_MESH, "original 900k mesh"),
            (SETTINGS_FILE, "authoritative settings file"),
            (TEMPLATE_CASE, "case-only setup scaffold"),
        ):
            mesh_study.require_remote_input(solver, path, label)
        free_bytes = mesh_study.remote_free_bytes(
            solver, setup07b.remote_join(REMOTE_DIR, "_disk_preflight.txt")
        )
        manifest["remote_free_gb_at_start"] = free_bytes / 1_000_000_000.0
        if manifest["remote_free_gb_at_start"] < args.minimum_free_gb:
            raise RuntimeError(
                f"remote free space {manifest['remote_free_gb_at_start']:.2f} GB is below "
                f"the {args.minimum_free_gb:.2f} GB safety floor"
            )
        try:
            solver.settings.file.start_transcript(file_name=transcript)
        except RuntimeError as exc:
            if "already been started" not in str(exc).lower():
                raise
            solver.settings.file.stop_transcript()
            solver.settings.file.start_transcript(file_name=transcript)
            manifest["stale_transcript_recovered"] = True

        manifest["original_mesh_sha256"] = mesh_study.remote_file_sha256(
            solver,
            ORIGINAL_MESH,
            setup07b.remote_join(REMOTE_DIR, "_original_mesh_sha256.txt"),
        )
        manifest["original_mesh_load_transcript"] = mesh_study.read_mesh(
            solver, ORIGINAL_MESH
        )
        manifest["original_mesh_zone_mapping"] = mesh_study.current_zone_mapping(
            solver, allow_rename=True
        )
        original_metrics, original_quality = mesh_study.collect_mesh_reports(solver)
        manifest["original_mesh_metrics"] = original_metrics
        if int(original_metrics.get("cells", -1)) != EXPECTED_CELLS:
            raise RuntimeError(f"expected {EXPECTED_CELLS} clean cells; got {original_metrics}")

        manifest["template_replace_transcript"] = mesh_study.load_template_and_replace_mesh(
            solver, ORIGINAL_MESH
        )
        manifest["zone_mapping_after_template_replace"] = mesh_study.current_zone_mapping(
            solver, allow_rename=True
        )
        settings_text = mesh_study.apply_settings(solver, SETTINGS_FILE)
        manifest["settings_import_transcript"] = settings_text
        manifest["zone_mapping_after_settings"] = mesh_study.current_zone_mapping(
            solver, allow_rename=False
        )
        warnings = re.findall(r"no zone with name\s+([^\s\)]+)", settings_text, re.I)
        required_names = {
            mesh_study.normalize_zone_name(name)
            for name in (*mesh_study.FACE_ALIASES, *mesh_study.CELL_ALIASES)
        }
        critical_warnings = [
            name
            for name in warnings
            if mesh_study.normalize_zone_name(name) in required_names
        ]
        manifest["settings_import_no_zone_warnings"] = warnings
        manifest["settings_import_critical_zone_warnings"] = critical_warnings
        if critical_warnings:
            raise RuntimeError(f"settings import missed required zones: {critical_warnings}")

        mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
        (LOCAL_DIR / "mesh_quality.txt").write_text(quality_text, encoding="utf-8")
        preinit = mesh_study.capture_settings(solver, REMOTE_DIR)
        errors = mesh_study.validate_settings(
            preinit, mesh_metrics, require_phase_identity=False
        )
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM model unexpectedly active")
        if errors:
            raise RuntimeError("pre-initialization parity failed: " + "; ".join(errors))

        # First Hybrid Initialization makes phase identity fully reportable for
        # the baseline fingerprint. A second fresh Hybrid Initialization is
        # performed after the new library and hooks are installed.
        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        initialized = mesh_study.capture_settings(solver, REMOTE_DIR)
        initialized.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_DIR))
        errors = mesh_study.validate_settings(
            initialized, mesh_metrics, require_phase_identity=True
        )
        fingerprint_payload = copy.deepcopy(mesh_study.critical_fingerprint(initialized))
        dynamic_patch = fingerprint_payload.get("initialization", {}).pop("patch", None)
        fingerprint = mesh_study.fingerprint_sha256(fingerprint_payload)
        manifest["baseline_fingerprint"] = fingerprint
        manifest["fingerprint_removed_dynamic_patch"] = dynamic_patch
        if fingerprint != EXPECTED_BASELINE_FINGERPRINT:
            errors.append(
                f"baseline fingerprint mismatch: {fingerprint} != {EXPECTED_BASELINE_FINGERPRINT}"
            )
        if errors:
            raise RuntimeError("initialized baseline parity failed: " + "; ".join(errors))

        zone_text, zones = setup07b.list_zones(solver)
        phase_materials = setup07b.phase_material_map(solver)
        liquid_phase = setup07b.find_phase_for_material(
            phase_materials, setup07b.LIQUID_MATERIAL
        )
        phase_names = sorted(phase_materials)
        liquid_phase_index = phase_names.index(liquid_phase)
        bottom_zone_id = int(zones["bottom"]["id"])
        if zones["bottom"]["type"] != "wall":
            raise RuntimeError(f"bottom must remain a wall: {zones['bottom']}")
        bottom_area = mesh_study.surface_areas(
            solver, REMOTE_DIR, ["bottom", "wall-fluid"]
        )["bottom"]
        bottom_y = mesh_study.surface_scalar(
            solver,
            REMOTE_DIR,
            "bottom_y_centroid",
            ["bottom"],
            "y-coordinate",
        )["bottom"]
        manifest["geometry_readback"] = {
            "zone_table_transcript": zone_text,
            "bottom_zone_id": bottom_zone_id,
            "bottom_type": zones["bottom"]["type"],
            "bottom_area_m2": bottom_area,
            "bottom_y_m": bottom_y,
            "phase_materials": phase_materials,
            "liquid_phase": liquid_phase,
            "liquid_phase_index_zero_based": liquid_phase_index,
        }

        manifest["udm_allocation"] = setup07b.allocate_and_verify_udm(solver)
        deployment = setup07c.deploy_source(solver, REMOTE_DIR)
        manifest["udf_deployment"] = deployment
        manifest["compile_transcript"] = setup07c.compile_and_load(
            solver, deployment, REMOTE_DIR
        )
        manifest["rp_parameter_readback"] = setup07c.configure_rp_parameters(
            solver,
            bottom_zone_id=bottom_zone_id,
            liquid_phase_index=liquid_phase_index,
            tau_s=args.tau_s,
            ramp=0.0,
            alpha_min=1.0e-12,
            bottom_y_m=bottom_y,
            layer_thickness_m=args.layer_thickness_m,
        )
        manifest["adjust_hook"] = setup07c.hook_adjust(
            solver, deployment["library_name"]
        )
        manifest["source_hooks"] = setup07c.enable_and_hook_sources(
            solver, liquid_phase=liquid_phase, library=deployment["library_name"]
        )
        hooks = setup07c.source_readback(solver)
        errors = setup07c.validate_source_readback(
            hooks, library=deployment["library_name"]
        )
        if errors:
            raise RuntimeError("source hook readback failed: " + "; ".join(errors))

        # The formal starting field is fresh after the 07c source additions.
        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        mask_console = setup07c.execute_mask_builder(solver, deployment["library_name"])
        mask_readback = parse_mask_readback(mask_console)
        errors = validate_mask(
            mask_readback, bottom_y_m=bottom_y, thickness_m=args.layer_thickness_m
        )
        mask_field, source_field, fields = latest_fields(solver)
        mask_volume = qualify07b.volume_report(
            solver, "prepared_mask", "volume_integral", mask_field
        )
        if not math.isclose(mask_volume, mask_readback["volume"], rel_tol=2.0e-5):
            errors.append(
                f"mask volume report mismatch: field={mask_volume}; UDF={mask_readback['volume']}"
            )
        settings = mesh_study.capture_settings(solver, REMOTE_DIR)
        settings.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_DIR))
        errors.extend(
            mesh_study.validate_settings(settings, mesh_metrics, require_phase_identity=True)
        )
        if bool(solver.scheme.eval("(sg-dpm?)")):
            errors.append("DPM model unexpectedly active after hook")
        if errors:
            raise RuntimeError("prepared thick-mask preflight failed: " + "; ".join(errors))
        manifest.update(
            {
                "status": "prepared",
                "mesh_metrics": mesh_metrics,
                "settings_readback": settings,
                "source_readback": hooks,
                "mask_console_readback": mask_console,
                "mask_readback": mask_readback,
                "mask_field": mask_field,
                "source_field": source_field,
                "mask_volume_integral_m3": mask_volume,
                "udm_fields": [name for name in fields if "cwl07c" in name.lower() or "udm" in name.lower()],
            }
        )
        start_pair = setup07b.save_pair(
            solver, REMOTE_DIR, "start_clean_original_fresh_hybrid_ramp0"
        )
        manifest["checkpoints"]["start_ramp0"] = start_pair
        persist(manifest, physical_rows, residual_rows)

        # Cold reload proves that hooks, controls, and UDM naming persist.
        setup07b.restore_pair(solver, start_pair)
        cold_hooks = setup07c.source_readback(solver)
        cold_errors = setup07c.validate_source_readback(
            cold_hooks, library=deployment["library_name"]
        )
        cold_rp = setup07c.rp_readback(solver)
        if not math.isclose(float(cold_rp["user/cwl07c/ramp"]), 0.0, abs_tol=1e-14):
            cold_errors.append(f"cold reload ramp is not zero: {cold_rp}")
        if bool(solver.scheme.eval("(sg-dpm?)")):
            cold_errors.append("DPM model unexpectedly active after cold reload")
        cold_console = setup07c.execute_mask_builder(solver, deployment["library_name"])
        cold_mask = parse_mask_readback(cold_console)
        cold_errors.extend(
            validate_mask(cold_mask, bottom_y_m=bottom_y, thickness_m=args.layer_thickness_m)
        )
        if not math.isclose(cold_mask["volume"], mask_readback["volume"], rel_tol=1e-9):
            cold_errors.append(
                f"mask volume changed on cold reload: {mask_readback['volume']} -> {cold_mask['volume']}"
            )
        if cold_errors:
            raise RuntimeError("cold reload validation failed: " + "; ".join(cold_errors))
        manifest["cold_reload_readback"] = {
            "source_hooks": cold_hooks,
            "rp_parameters": cold_rp,
            "mask": cold_mask,
            "validation_errors": cold_errors,
        }

        # Protected tiny-ramp smoke test; restore the clean start afterwards.
        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, 0)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        smoke_ramp = 0.005
        setup07c.set_rp_real(solver, "user/cwl07c/ramp", smoke_ramp)
        try:
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=1)
            after = sweep.require_monitor_advance(solver, before, 1, 60.0)
            smoke_row = qualify07b.collect_metrics(
                solver,
                cumulative_iteration=1,
                r1_iteration=0,
                stage="protected_smoke",
                ramp=smoke_ramp,
                tau_s=args.tau_s,
                liquid_density=float(settings["phase_densities_kg_m3"][liquid_phase]),
                mask_field=mask_field,
                mass_source_field=source_field,
            )
        finally:
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
        projected_sink = smoke_row["sink_magnitude_kgs"] / smoke_ramp
        manifest["protected_smoke"] = {
            "ramp": smoke_ramp,
            "iteration_before": before,
            "iteration_after": after,
            "metrics": smoke_row,
            "projected_full_ramp_sink_kgs": projected_sink,
            "accepted": math.isfinite(projected_sink) and projected_sink <= 175.0,
        }
        manifest["checkpoints"]["smoke_ramp_reset0"] = setup07b.save_pair(
            solver, REMOTE_DIR, "protected_smoke_one_iter_ramp_reset0"
        )
        if not manifest["protected_smoke"]["accepted"]:
            raise RuntimeError(
                f"protected smoke projects unsafe full sink {projected_sink:.6g} kg/s"
            )

        # Restore the untouched formal starting field before production ramp.
        setup07b.restore_pair(solver, start_pair)
        setup07c.execute_mask_builder(solver, deployment["library_name"])
        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)
        sweep.set_verified_iteration_label(solver, 0)
        if solver.monitors.is_streaming:
            solver.monitors.stop()
        solver.monitors.start()
        manifest["status"] = "running"
        manifest["classification"] = "diagnostic qualification in progress"
        persist(manifest, physical_rows, residual_rows)

        liquid_density = float(settings["phase_densities_kg_m3"][liquid_phase])
        cumulative = 0
        for ramp, iterations in RAMP_STAGES:
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", ramp)
            before = sweep.monitor_iteration_snapshot(solver)
            solver.settings.solution.run_calculation.iterate(iter_count=iterations)
            after = sweep.require_monitor_advance(solver, before, iterations, 60.0)
            cumulative += iterations
            row = qualify07b.collect_metrics(
                solver,
                cumulative_iteration=cumulative,
                r1_iteration=0,
                stage=f"ramp_{ramp:.3f}",
                ramp=ramp,
                tau_s=args.tau_s,
                liquid_density=liquid_density,
                mask_field=mask_field,
                mass_source_field=source_field,
            )
            physical_rows.append(row)
            residual_rows = sweep.monitor_history_rows(solver)
            manifest["iteration_evidence"].append(
                {
                    "stage": f"ramp_{ramp:.3f}",
                    "requested": iterations,
                    "cumulative_iteration": cumulative,
                    "before": before,
                    "after": after,
                }
            )
            manifest["cumulative_iterations_completed"] = cumulative
            manifest["latest_metrics"] = row
            persist(manifest, physical_rows, residual_rows)
            print(
                f"07c ramp={ramp:.3f} cumulative={cumulative} "
                f"sink={row['sink_magnitude_kgs']:.6g} kg/s "
                f"liquid-balance={row['liquid_source_augmented_imbalance_percent']:.4g}%",
                flush=True,
            )
            if row["sink_magnitude_kgs"] > 175.0:
                stop_reason = f"sink exceeded 175 kg/s during ramp {ramp}"
                break

        if not stop_reason:
            manifest["checkpoints"]["ramp_complete"] = setup07b.save_pair(
                solver, REMOTE_DIR, f"ramp_complete_cumulative{cumulative}_r0p75"
            )
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", 1.0)
            r1_completed = 0
            while r1_completed < args.maximum_r1_iterations:
                requested = min(args.block, args.maximum_r1_iterations - r1_completed)
                before = sweep.monitor_iteration_snapshot(solver)
                solver.settings.solution.run_calculation.iterate(iter_count=requested)
                after = sweep.require_monitor_advance(solver, before, requested, 60.0)
                cumulative += requested
                r1_completed += requested
                row = qualify07b.collect_metrics(
                    solver,
                    cumulative_iteration=cumulative,
                    r1_iteration=r1_completed,
                    stage="ramp_1.00",
                    ramp=1.0,
                    tau_s=args.tau_s,
                    liquid_density=liquid_density,
                    mask_field=mask_field,
                    mass_source_field=source_field,
                )
                physical_rows.append(row)
                residual_rows = sweep.monitor_history_rows(solver)
                window = qualify07b.qualification_window(
                    physical_rows, residual_rows, args.residual_limit
                )
                manifest["iteration_evidence"].append(
                    {
                        "stage": "ramp_1.00",
                        "requested": requested,
                        "cumulative_iteration": cumulative,
                        "r1_iteration": r1_completed,
                        "before": before,
                        "after": after,
                    }
                )
                manifest.update(
                    {
                        "cumulative_iterations_completed": cumulative,
                        "r1_iterations_completed": r1_completed,
                        "latest_metrics": row,
                        "latest_500_iteration_assessment": window,
                    }
                )
                if r1_completed % 1000 == 0:
                    manifest["checkpoints"][f"r1_{r1_completed}"] = setup07b.save_pair(
                        solver,
                        REMOTE_DIR,
                        f"r1_iter{r1_completed}_cumulative{cumulative}",
                    )
                persist(manifest, physical_rows, residual_rows)
                print(
                    f"07c R=1 {r1_completed}/{args.maximum_r1_iterations} "
                    f"sink={row['sink_magnitude_kgs']:.6g} kg/s "
                    f"balance={row['liquid_source_augmented_imbalance_percent']:.4g}% "
                    f"window-pass={window['acceptance_window_pass']}",
                    flush=True,
                )

                r1_rows = [
                    item
                    for item in physical_rows
                    if int(item.get("r1_iteration", 0)) > 0
                ]
                if len(r1_rows) >= 2:
                    jumps = abrupt_change(r1_rows[-2], r1_rows[-1])
                    manifest["latest_block_change_percent"] = jumps
                    manifest.setdefault("block_change_history", []).append(
                        {"r1_iteration": r1_completed, **jumps}
                    )
                    # Inventory and sink naturally rise from near zero while the
                    # clean initialized liquid field first reaches the bottom
                    # band.  Those relative changes are diagnostic, not an
                    # instability.  Retain a hard pressure-jump guard only once
                    # at least three full-strength blocks exist.
                    if r1_completed >= 750 and jumps["pressure_drop_pa"] > 20.0:
                        stop_reason = f"abrupt >20% pressure-drop block change: {jumps}"
                if row["sink_magnitude_kgs"] > 175.0 and len(r1_rows) >= 2:
                    if row["domain_liquid_inventory_kg"] < r1_rows[-2]["domain_liquid_inventory_kg"]:
                        stop_reason = "sink exceeded 175 kg/s while liquid inventory fell"
                if stop_reason:
                    break
                if r1_completed >= args.minimum_r1_iterations:
                    stable_windows = stable_windows + 1 if window["acceptance_window_pass"] else 0
                    if stable_windows >= args.stable_windows_required:
                        break
        else:
            r1_completed = 0

        setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
        accepted = stable_windows >= args.stable_windows_required
        final_label = (
            f"accepted_r1_{r1_completed}_ramp_reset0"
            if accepted
            else f"diagnostic_stop_r1_{r1_completed}_ramp_reset0"
        )
        manifest["checkpoints"]["final"] = setup07b.save_pair(
            solver, REMOTE_DIR, final_label
        )
        manifest.update(
            {
                "status": "completed",
                "classification": (
                    "accepted 07c thick-sink diagnostic"
                    if accepted
                    else "diagnostic/unresolved thick-sink result"
                ),
                "stable_windows_observed": stable_windows,
                "stop_reason": stop_reason or "maximum iteration budget reached",
                "ramp_after_run": 0.0,
                "dpm_after_run": bool(solver.scheme.eval("(sg-dpm?)")),
                "completed_epoch": time.time(),
            }
        )
        persist(manifest, physical_rows, residual_rows)
        return 0
    except BaseException as exc:
        manifest.update(
            {
                "status": "failed",
                "classification": "diagnostic/unresolved implementation or run failure",
                "failure_category": classify_failure(exc),
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        try:
            setup07c.set_rp_real(solver, "user/cwl07c/ramp", 0.0)
            manifest["checkpoints"]["failure_ramp_reset0"] = setup07b.save_pair(
                solver, REMOTE_DIR, f"failure_ramp_reset0_{int(time.time())}"
            )
        except Exception as save_exc:
            manifest["failure_checkpoint_error"] = f"{type(save_exc).__name__}: {save_exc}"
        persist(manifest, physical_rows, residual_rows)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        persist(manifest, physical_rows, residual_rows)
        print(json.dumps(manifest, indent=2, default=str), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())

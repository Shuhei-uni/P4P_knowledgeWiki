#!/usr/bin/env python3
"""Prepare setup 07b from the original 900k mesh and fresh initialization.

This script intentionally runs zero production iterations.  It records the
original mesh identity, rebuilds the authoritative setup without reading any
saved solution data, hooks the liquid-sink UDF with ramp zero, performs fresh
Hybrid Initialization, saves a new case/data pair, cold-reloads it, and verifies
that the sources persist.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))

from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
import setup07b_constant_water_level_sink as setup07b  # noqa: E402
import verify_constant_water_level_sink as verify07b  # noqa: E402


STUDY_ID = "split_inlet_constant_water_level_sink_20260807"
RUN_LABEL = "mesh-900k_07b_clean_original_prepared_v1"
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / "clean_900k_preparation"
REMOTE_ROOT = (
    rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}\clean_900k_preparation"
)
ORIGINAL_MESH = r"C:\Users\qtra338\Documents\Mesh study\Meshes\mesh-900k.msh"
SETTINGS_FILE = r"C:\Users\qtra338\Documents\Mesh study\Source\mesh_study_settings.set"
TEMPLATE_CASE = (
    r"C:\Users\qtra338\Documents\Mesh study\partial_solution_diagnostic_20260801.cas.h5"
)
EXPECTED_CELLS = 5_335_623
EXPECTED_BASELINE_FINGERPRINT = (
    "424a9bf02bbd78060dee3a2874103e5149aa4aa555a09e2add69da4d2a0158c5"
)
LIBRARY_SUFFIX = "clean1"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--tau-s", type=float, default=0.1)
    result.add_argument("--alpha-min", type=float, default=1.0e-12)
    result.add_argument("--run-label", default=RUN_LABEL)
    return result


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    output = LOCAL_ROOT / f"{args.run_label}_manifest.json"
    solver = connect(server_id=args.server_id)
    payload: dict[str, Any] = {
        "study_id": STUDY_ID,
        "run_label": args.run_label,
        "status": "running",
        "classification": "diagnostic preparation",
        "original_mesh": ORIGINAL_MESH,
        "settings_file": SETTINGS_FILE,
        "case_only_template": TEMPLATE_CASE,
        "saved_solution_data_loaded": False,
        "production_iterations_run": 0,
        "dpm": "off; no injections updated or tracked",
        "started_epoch": time.time(),
    }
    transcript = setup07b.remote_join(REMOTE_ROOT, f"{args.run_label}_transcript.trn")
    try:
        for path, label in (
            (ORIGINAL_MESH, "original 900k mesh"),
            (SETTINGS_FILE, "authoritative settings file"),
            (TEMPLATE_CASE, "case-only setup scaffold"),
        ):
            mesh_study.require_remote_input(solver, path, label)
        setup07b.ensure_remote_root(solver, REMOTE_ROOT)
        solver.settings.file.start_transcript(file_name=transcript)

        # First read and fingerprint the original mesh itself. No case/data
        # solution field is used as an initial condition.
        payload["original_mesh_sha256"] = mesh_study.remote_file_sha256(
            solver,
            ORIGINAL_MESH,
            setup07b.remote_join(REMOTE_ROOT, "_original_mesh_sha256.txt"),
        )
        payload["original_mesh_load_transcript"] = mesh_study.read_mesh(
            solver, ORIGINAL_MESH
        )
        payload["original_mesh_zone_mapping"] = mesh_study.current_zone_mapping(
            solver, allow_rename=True
        )
        original_metrics, original_quality = mesh_study.collect_mesh_reports(solver)
        payload["original_mesh_metrics"] = original_metrics
        payload["original_mesh_quality_transcript"] = original_quality
        if int(original_metrics.get("cells", -1)) != EXPECTED_CELLS:
            raise RuntimeError(
                f"clean-origin mesh mismatch: expected {EXPECTED_CELLS} cells; "
                f"actual={original_metrics}"
            )

        # Reuse the accepted setup-07a case-only scaffold, replace its mesh with
        # the same original .msh, and then reapply the authoritative settings.
        # No .dat.h5 file is read, and Hybrid Initialization below overwrites
        # any case-stored initialization state.
        payload["template_replace_transcript"] = (
            mesh_study.load_template_and_replace_mesh(solver, ORIGINAL_MESH)
        )
        payload["zone_mapping_after_template_replace"] = (
            mesh_study.current_zone_mapping(solver, allow_rename=True)
        )
        settings_text = mesh_study.apply_settings(solver, SETTINGS_FILE)
        payload["settings_import_transcript"] = settings_text
        payload["zone_mapping_after_settings"] = mesh_study.current_zone_mapping(
            solver, allow_rename=False
        )
        warnings = re.findall(
            r"no zone with name\s+([^\s\)]+)", settings_text, re.IGNORECASE
        )
        payload["settings_import_no_zone_warnings"] = warnings
        required_names = {
            mesh_study.normalize_zone_name(name)
            for name in (*mesh_study.FACE_ALIASES, *mesh_study.CELL_ALIASES)
        }
        critical_warnings = [
            name
            for name in warnings
            if mesh_study.normalize_zone_name(name) in required_names
        ]
        payload["settings_import_critical_zone_warnings"] = critical_warnings
        payload["settings_import_warning_interpretation"] = (
            "The historical generic 'wall' entry is non-critical because the required "
            "wall-fluid and bottom zones are present, typed, and validated after import."
        )
        if critical_warnings:
            raise RuntimeError(
                f"settings import reported missing required zones: {critical_warnings}"
            )

        mesh_metrics, quality_text = mesh_study.collect_mesh_reports(solver)
        payload["prepared_mesh_metrics"] = mesh_metrics
        payload["prepared_mesh_quality_transcript"] = quality_text
        preinit = mesh_study.capture_settings(solver, REMOTE_ROOT)
        errors = mesh_study.validate_settings(
            preinit, mesh_metrics, require_phase_identity=False
        )
        if errors:
            raise RuntimeError("clean pre-initialization parity failed: " + "; ".join(errors))

        sweep.maybe_initialize(solver, "hybrid")
        sweep.set_verified_iteration_label(solver, 0)
        initialized = mesh_study.capture_settings(solver, REMOTE_ROOT)
        initialized.update(mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT))
        payload["initialized_settings_readback"] = initialized
        errors = mesh_study.validate_settings(
            initialized, mesh_metrics, require_phase_identity=True
        )
        raw_fingerprint_payload = mesh_study.critical_fingerprint(initialized)
        raw_fingerprint = mesh_study.fingerprint_sha256(raw_fingerprint_payload)
        normalized_fingerprint_payload = copy.deepcopy(raw_fingerprint_payload)
        dynamic_patch_state = normalized_fingerprint_payload.get(
            "initialization", {}
        ).pop("patch", None)
        baseline_fingerprint = mesh_study.fingerprint_sha256(
            normalized_fingerprint_payload
        )
        payload["initialized_baseline_fingerprint_raw"] = raw_fingerprint
        payload["initialized_baseline_fingerprint_normalized"] = baseline_fingerprint
        payload["fingerprint_normalization"] = {
            "removed_path": "initialization.patch",
            "removed_value": dynamic_patch_state,
            "reason": (
                "Fluent activates this default VOF patch-options subtree only after "
                "Hybrid Initialization. The accepted 07a fingerprint was captured before "
                "initialization and therefore lacks the subtree; all other settings remain hashed."
            ),
        }
        payload["expected_baseline_fingerprint"] = EXPECTED_BASELINE_FINGERPRINT
        if baseline_fingerprint != EXPECTED_BASELINE_FINGERPRINT:
            errors.append(
                "authoritative settings fingerprint mismatch: "
                f"{baseline_fingerprint} != {EXPECTED_BASELINE_FINGERPRINT}"
            )
        if errors:
            raise RuntimeError("clean initialized parity failed: " + "; ".join(errors))

        # Configure production monitor capacity and disable iteration-count
        # early exits only after proving parity with the authoritative baseline.
        sweep.configure_residual_history(solver, 10000)
        sweep.configure_full_iteration_run(solver, allow_early_convergence=False)

        preflight = {
            "bottom_zone_id": 50059,
            "liquid_phase": "phase-2",
            "liquid_phase_index_zero_based": 1,
        }
        payload["udm_allocation"] = setup07b.allocate_and_verify_udm(solver)
        deployment = setup07b.deploy_source(solver, REMOTE_ROOT)
        deployment["library_name"] = f"{deployment['library_name']}_{LIBRARY_SUFFIX}"
        payload["udf_deployment"] = deployment
        payload["compile_transcript"] = setup07b.compile_and_load(
            solver, deployment, REMOTE_ROOT
        )
        parameter_args = argparse.Namespace(
            tau_s=args.tau_s,
            ramp=0.0,
            alpha_min=args.alpha_min,
        )
        payload["rp_parameter_readback"] = setup07b.configure_rp_parameters(
            solver, preflight, parameter_args
        )
        payload["adjust_hook"] = setup07b.hook_adjust(
            solver, deployment["library_name"]
        )
        payload["source_hooks"] = setup07b.enable_and_hook_sources(
            solver, preflight, deployment["library_name"]
        )

        hooked_settings = mesh_study.capture_settings(solver, REMOTE_ROOT)
        hooked_settings.update(
            mesh_study.verify_initialized_phase_identity(solver, REMOTE_ROOT)
        )
        errors = mesh_study.validate_settings(
            hooked_settings, mesh_metrics, require_phase_identity=True
        )
        if errors:
            raise RuntimeError("post-hook carrier parity failed: " + "; ".join(errors))
        payload["posthook_settings_readback"] = hooked_settings

        checkpoint = setup07b.save_pair(
            solver, REMOTE_ROOT, f"{args.run_label}_fresh_hybrid_ramp0"
        )
        payload["prepared_checkpoint"] = checkpoint

        # Cold reload the prepared pair. This proves a later production run can
        # start from the saved clean-origin initialization without losing UDFs.
        setup07b.restore_pair(solver, checkpoint)
        cold_sources = verify07b.source_readback(solver)
        cold_errors = verify07b.validate_source_readback(
            cold_sources, library=deployment["library_name"]
        )
        cold_parameters = verify07b.rp_readback(solver)
        cold_fields = verify07b.scalar_fields(solver)
        udm_fields = [
            name
            for name in cold_fields
            if "udm" in name.lower() or "cwl07b" in name.lower()
        ]
        if len(udm_fields) < 5:
            cold_errors.append(f"fewer than five UDM fields after reload: {udm_fields}")
        if float(cold_parameters["user/cwl07b/ramp"]) != 0.0:
            cold_errors.append(f"cold-reload ramp is not zero: {cold_parameters}")
        if cold_errors:
            raise RuntimeError("prepared checkpoint cold-reload failed: " + "; ".join(cold_errors))
        payload["cold_reload_readback"] = {
            "source_hooks": cold_sources,
            "rp_parameters": cold_parameters,
            "udm_fields": udm_fields,
            "validation_errors": cold_errors,
        }
        payload.update(
            {
                "status": "prepared",
                "classification": "accepted clean-origin initialized start state",
                "production_iterations_run": 0,
                "completed_epoch": time.time(),
                "transcript": transcript,
                "next_action": (
                    "Run the controlled ramp/tau qualification from this clean-origin "
                    "fresh-Hybrid state; do not use setup-07a accumulated solution data."
                ),
            }
        )
    except BaseException as exc:
        payload.update(
            {
                "status": "unresolved",
                "classification": "diagnostic preparation failure",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        setup07b.write_json(output, payload)
        print(json.dumps(payload, indent=2, default=str), flush=True)
        print(f"Clean-origin preparation manifest: {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

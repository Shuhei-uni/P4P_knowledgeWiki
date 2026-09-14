#!/usr/bin/env python3
"""Run one remaining Phase 7.1A turbulence-family discovery child.

Each child loads the exact active-1000 absorber parent and applies exactly one
declared turbulence-family delta.  The runner shares the closure-family
instrumentation and terminal proof, but validates the option-specific
readback before the prepared save/reopen and attached 500-iteration solve.
"""

from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PureWindowsPath
import sys
import traceback
from typing import Any, Mapping

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from ansys.fluent.core.fields.field_data_interfaces import ScalarFieldDataRequest  # noqa: E402
from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    remote_file_sha256,
    scientific_readback,
)
from run_p71a_turbulence_closure import (  # noqa: E402
    CHECKPOINT,
    EXPECTED_ABSORBER_INTEGRAL,
    EXPECTED_ABSORBER_SOURCE,
    HORIZON,
    PARENT_CASE,
    PARENT_DATA,
    PARENT_FLUID_ZONES,
    PARENT_SETUP,
    REMOTE_BASE,
    REQUIRED_REPORTS,
    SMOKE,
    artifact_paths,
    diagnostic_counts,
    extract_histories,
    fluid_names,
    full_readback,
    make_run_paths,
    read_source_tree,
    rp_clock,
    save_pair_new,
    try_integrated_source_reports,
    validate_parent_readback,
    verify_report_paths,
    write_json,
    write_yaml,
)
from run_p7_e5_cz_absorb import redirect_all_reports  # noqa: E402
from run_p7_treatment_screen import parse_residuals  # noqa: E402


CONFIGS: dict[str, dict[str, Any]] = {
    "P71A-T2-RNG-PRODUCTION-LIMITER": {
        "candidate_id": "C2-T2-PROD",
        "delta": "RNG production limiter off to on",
        "allowed_path": ("models", "viscous", "options", "production_limiter", "enabled"),
        "expected": {"production_limiter": True},
    },
    "P71A-T2-RNG-DIFFERENTIAL-VISCOSITY-OFF": {
        "candidate_id": "C2-T2-DIFF",
        "delta": "RNG differential viscosity on to off",
        "allowed_path": ("models", "viscous", "rng", "differential_viscosity_model"),
        "expected": {"differential_viscosity": False},
    },
    "P71A-T2-RNG-SWIRL-OFF": {
        "candidate_id": "C2-T2-SWIRL",
        "delta": "RNG swirl modification on to off",
        "allowed_path": ("models", "viscous", "rng", "swirl_dominated_flow"),
        "expected": {"swirl": False},
    },
    "P71A-T2-RNG-KATO-LAUNDER": {
        "candidate_id": "C2-T2-KATO",
        "delta": "Kato-Launder production treatment off to on",
        "allowed_path": ("models", "viscous", "options", "production_kato_launder_enabled"),
        "expected": {"kato_launder": True},
    },
    "P71A-T3-SCALABLE-WALL-FUNCTIONS": {
        "candidate_id": "C2-T3-SCALABLE",
        "delta": "standard wall functions to scalable wall functions",
        "allowed_path": ("models", "viscous", "near_wall_treatment", "wall_treatment"),
        "expected": {"wall_treatment": "scalable-wall-functions"},
        "wall_evidence": True,
    },
    "P71A-T3-NON-EQUILIBRIUM-WALL-FUNCTIONS": {
        "candidate_id": "C2-T3-NON-EQ",
        "delta": "standard wall functions to non-equilibrium wall functions",
        "allowed_path": ("models", "viscous", "near_wall_treatment", "wall_treatment"),
        "expected": {"wall_treatment": "non-equilibrium-wall-fn"},
        "wall_evidence": True,
    },
    "P71A-T4-K-SECOND-ORDER": {
        "candidate_id": "C2-T4-K2",
        "delta": "k discretization first-order to second-order upwind",
        "allowed_path": ("methods", "spatial_discretization", "discretization_scheme", "k"),
        "expected": {"k_scheme": "second-order-upwind"},
    },
    "P71A-T4-MULTIPHASE-TURBULENCE-DISPERSION": {
        "candidate_id": "C2-T4-DISPERSION",
        "delta": "multiphase turbulence dispersion off to on",
        "allowed_path": (
            "models",
            "viscous",
            "multiphase_turbulence",
            "multiphase_options",
            "dispersion_in_relative_velocity",
        ),
        "expected": {"dispersion": True},
    },
}


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def remove_path(value: Any, path: tuple[str, ...]) -> None:
    if not path or not isinstance(value, dict):
        return
    if len(path) == 1:
        value.pop(path[0], None)
        return
    child = value.get(path[0])
    if isinstance(child, dict):
        remove_path(child, path[1:])


def scientific_without_delta(readback: Mapping[str, Any], path: tuple[str, ...]) -> dict[str, Any]:
    result = copy.deepcopy(dict(readback["scientific"]))
    remove_path(result, path)
    # Fluent materializes the default production-limiter clip factor when the
    # limiter is enabled.  It is an option-dependent default exposed by the
    # same declared toggle, not an independent scientific mutation.  Remove
    # only this known companion field from the outside-delta comparison; all
    # other settings remain strict.
    if path == ("models", "viscous", "options", "production_limiter", "enabled"):
        remove_path(result, ("models", "viscous", "options", "production_limiter", "clip_factor"))
    return result


def assert_only_declared_delta(before: Mapping[str, Any], after: Mapping[str, Any], path: tuple[str, ...]) -> None:
    if scientific_without_delta(before, path) != scientific_without_delta(after, path):
        raise RuntimeError(f"scientific state changed outside declared delta path {'.'.join(path)}")
    for key in ("materials", "cell_zone_conditions", "source_tree", "fluid_zone_names"):
        if before[key] != after[key]:
            raise RuntimeError(f"frozen parent state changed outside declared delta: {key}")


def assert_same_scientific_state(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    if before["scientific"] != after["scientific"]:
        raise RuntimeError("scientific state changed after the declared delta")
    for key in ("materials", "cell_zone_conditions", "source_tree", "fluid_zone_names"):
        if before[key] != after[key]:
            raise RuntimeError(f"frozen state changed after the declared delta: {key}")


def expected_validator_kwargs(config: Mapping[str, Any]) -> dict[str, Any]:
    expected = config.get("expected", {})
    return {
        "expected_wall_treatment": expected.get("wall_treatment", "standard-wall-fn"),
        "expected_production_limiter": expected.get("production_limiter", False),
        "expected_kato_launder": expected.get("kato_launder", False),
        "expected_dispersion": expected.get("dispersion", False),
        "expected_differential_viscosity": expected.get("differential_viscosity", True),
        "expected_swirl": expected.get("swirl", True),
        "expected_k_scheme": expected.get("k_scheme", "first-order-upwind"),
    }


def apply_delta(solver: Any, setup_id: str) -> None:
    expected = CONFIGS[setup_id]["expected"]
    models = solver.settings.setup.models
    if "production_limiter" in expected:
        models.viscous.options.production_limiter.enabled = expected["production_limiter"]
    elif "differential_viscosity" in expected:
        models.viscous.rng.differential_viscosity_model = expected["differential_viscosity"]
    elif "swirl" in expected:
        models.viscous.rng.swirl_dominated_flow = expected["swirl"]
    elif "kato_launder" in expected:
        models.viscous.options.production_kato_launder_enabled = expected["kato_launder"]
    elif "wall_treatment" in expected:
        models.viscous.near_wall_treatment.wall_treatment = expected["wall_treatment"]
    elif "k_scheme" in expected:
        k_scheme = solver.settings.solution.methods.spatial_discretization.discretization_scheme.get("k")
        k_scheme.set_state(expected["k_scheme"])
    elif "dispersion" in expected:
        models.viscous.multiphase_turbulence.multiphase_options.dispersion_in_relative_velocity = expected["dispersion"]
    else:
        raise RuntimeError(f"no implementation mapping for {setup_id}")


def wall_evidence(solver: Any) -> dict[str, Any]:
    evidence: dict[str, Any] = {"surfaces": {}, "fields": ["y-plus", "cell-wall-distance"]}
    for field_name in ("y-plus", "cell-wall-distance"):
        request = ScalarFieldDataRequest(
            surfaces=["bottom", "wall"],
            field_name=field_name,
            node_value=False,
            boundary_value=True,
        )
        data = solver.fields.field_data.get_field_data(request)
        evidence["surfaces"][field_name] = {}
        for surface, values in data.items():
            array = np.asarray(values, dtype=float)
            evidence["surfaces"][field_name][str(surface)] = {
                "points": int(array.size),
                "minimum": float(np.nanmin(array)),
                "maximum": float(np.nanmax(array)),
                "mean": float(np.nanmean(array)),
                "p95": float(np.nanpercentile(array, 95)),
            }
    evidence["status"] = "PASS"
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, choices=tuple(CONFIGS))
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--run-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--local-dir", required=True, type=Path)
    args = parser.parse_args()

    config = CONFIGS[args.candidate]
    local_dir = args.local_dir.expanduser().resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    local_manifest = local_dir / "run-manifest.json"
    local_residuals = local_dir / "residuals.json"
    local_reports = local_dir / "reports.json"
    local_transcript = local_dir / "transcript.txt"
    for path in (local_manifest, local_residuals, local_reports, local_transcript):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite local evidence artifact: {path}")

    run_id = f"{args.candidate}-student-{args.run_stamp}"
    run_root = str(PureWindowsPath(REMOTE_BASE) / args.candidate / args.run_stamp)
    paths = artifact_paths(run_root, args.candidate)
    manifest: dict[str, Any] = {
        "status": "RUNNING",
        "setup_id": args.candidate,
        "candidate_id": config["candidate_id"],
        "run_id": run_id,
        "family": "phase-07-1a-turbulence-family",
        "mode": "attached-discovery",
        "server_id": args.server_id,
        "server_ref": f"student@{os.getenv('STUDENT_IP', '10.0.0.5')}",
        "fluent_version_expected": "Ansys Fluent 2025 R2",
        "parent_setup_id": PARENT_SETUP,
        "parent_case": PARENT_CASE,
        "parent_data": PARENT_DATA,
        "parent_state": "active-1000",
        "controlled_delta": config["delta"],
        "requested_active_iterations": HORIZON,
        "smoke_iterations": SMOKE,
        "restart_field_mutation": "none; no initialization, patch, reset, remesh, or resplit",
        "remote_run_root": run_root,
        "artifact_paths": paths,
        "events": [],
    }
    write_json(local_manifest, manifest)
    solver: Any | None = None
    capture: SessionTranscriptCapture | None = None
    try:
        solver = connect(server_id=args.server_id, start_transcript=True, tcp_timeout_seconds=5)
        version = str(solver.get_fluent_version())
        if "2025 R2" not in version:
            raise RuntimeError(f"unexpected Fluent version: {version}")
        ensure_remote_directory(solver, run_root)
        ensure_remote_directory(solver, paths["monitor_root"])
        ensure_remote_directory(solver, paths["scratch_root"])
        for key, path in paths.items():
            if key.endswith("_case") or key.endswith("_data"):
                if remote_file_exists(solver, path):
                    raise FileExistsError(f"refusing to overwrite remote artifact: {path}")
        if not remote_file_exists(solver, PARENT_CASE) or not remote_file_exists(solver, PARENT_DATA):
            raise FileNotFoundError(f"exact active-1000 parent pair is not visible: {PARENT_CASE}; {PARENT_DATA}")
        manifest["parent_sha256"] = {
            "case": remote_file_sha256(solver, PARENT_CASE, str(PureWindowsPath(paths["scratch_root"]) / "parent-case-sha256.txt")),
            "data": remote_file_sha256(solver, PARENT_DATA, str(PureWindowsPath(paths["scratch_root"]) / "parent-data-sha256.txt")),
        }
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        parent = full_readback(solver)
        validate_parent_readback(parent, "rng")
        manifest["parent_readback"] = parent
        manifest["parent_validation"] = "PASS"
        if config.get("wall_evidence"):
            manifest["near_wall_evidence"] = wall_evidence(solver)
        write_json(local_manifest, manifest)

        apply_delta(solver, args.candidate)
        changed = full_readback(solver)
        validate_parent_readback(changed, "rng", **expected_validator_kwargs(config))
        assert_only_declared_delta(parent, changed, config["allowed_path"])
        manifest["delta_readback_before_save"] = changed
        manifest["delta_validation"] = "PASS"

        monitor_paths = redirect_all_reports(solver, paths["monitor_root"], args.candidate)
        residual_state_before = safe_get_state(solver.settings.solution.monitor.residual, "residual before instrumentation")
        residual_config = configure_residual_history(solver, HORIZON + 200)
        autosave_config = configure_autosave(solver, run_root, data_frequency=CHECKPOINT)
        manifest["report_files"] = monitor_paths
        manifest["residual_configuration"] = residual_config
        manifest["autosave_configuration"] = autosave_config
        manifest["residual_criteria_before_instrumentation"] = residual_state_before
        write_yaml(local_dir / "run-paths.yaml", make_run_paths(args.candidate, run_id, local_dir, paths, monitor_paths))

        save_pair_new(solver, paths["prepared_case"])
        solver.settings.file.read_case(file_name=paths["prepared_case"])
        solver.settings.file.read_data(file_name=paths["prepared_data"])
        prepared = full_readback(solver)
        assert_same_scientific_state(changed, prepared)
        if prepared["cell_zone_conditions"] != changed["cell_zone_conditions"] or prepared["source_tree"] != changed["source_tree"]:
            raise RuntimeError("prepared save/reopen changed frozen source or cell-zone state")
        verify_report_paths(solver, monitor_paths)
        manifest["prepared_reopen"] = prepared
        manifest["prepared_pair_verified"] = True
        write_json(local_manifest, manifest)

        capture = SessionTranscriptCapture(solver, stream_path=local_transcript, echo=False)
        capture.start()
        start = capture.mark()
        active = 0
        for block, target, save_key in ((SMOKE, SMOKE, "smoke_case"), (CHECKPOINT - SMOKE, CHECKPOINT, "checkpoint_case"), (HORIZON - CHECKPOINT, HORIZON, "final_case")):
            before = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=block)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10.0)
            active = target
            recent = capture.text_since(before)
            event = {
                "event": "discovery_block_complete",
                "active_iterations_from_child_start": active,
                "native_clock": rp_clock(solver),
                "diagnostics": diagnostic_counts(recent),
            }
            manifest.setdefault("events", []).append(event)
            save_pair_new(solver, paths[save_key])
            event["saved_case"] = paths[save_key]
            event["saved_data"] = data_path(paths[save_key])
            write_json(local_manifest, manifest)
        transcript = capture.text_since(start)
        residuals = parse_residuals(transcript)
        if residuals["point_count"] < HORIZON:
            raise RuntimeError(f"native residual transcript is short: {residuals['point_count']} points for {HORIZON} iterations")
        manifest["residuals"] = residuals
        manifest["achieved_active_iterations"] = active
        manifest["terminal_diagnostics"] = diagnostic_counts(transcript)
        manifest["final_native_clock"] = rp_clock(solver)
        write_json(local_residuals, residuals)
        capture.close()
        capture = None

        solver.settings.file.read_case(file_name=paths["final_case"])
        solver.settings.file.read_data(file_name=paths["final_data"])
        final_readback = full_readback(solver)
        assert_same_scientific_state(prepared, final_readback)
        verify_report_paths(solver, monitor_paths)
        histories = extract_histories(solver, monitor_paths, local_reports)
        if not REQUIRED_REPORTS.issubset(histories):
            raise RuntimeError(f"required evidence reports absent: {sorted(REQUIRED_REPORTS - set(histories))}")
        manifest["final_reopen"] = final_readback
        manifest["final_pair_verified"] = True
        manifest["report_histories_local"] = str(local_reports)
        manifest["integrated_source_readback"] = try_integrated_source_reports(solver)
        manifest["terminal_execution"] = {
            "status": "COMPLETE",
            "requested_active_iterations": HORIZON,
            "achieved_active_iterations": active,
            "final_native_clock": manifest.get("final_native_clock"),
            "paired_final_case": paths["final_case"],
            "paired_final_data": paths["final_data"],
            "required_report_count": len(histories),
        }
        manifest["status"] = "COMPLETE"
        write_json(local_manifest, manifest)
        print(json.dumps(manifest, indent=2, default=str, allow_nan=True))
        return 0
    except Exception as exc:
        if capture is not None:
            capture.close()
        manifest["status"] = "BLOCKED"
        manifest["error"] = f"{type(exc).__name__}: {exc}"
        manifest["traceback"] = traceback.format_exc()
        if solver is not None:
            try:
                manifest["last_live_clock"] = rp_clock(solver)
            except Exception:
                pass
        write_json(local_manifest, manifest)
        print(json.dumps(manifest, indent=2, default=str, allow_nan=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

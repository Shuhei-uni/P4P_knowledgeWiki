#!/usr/bin/env python3
"""Run one approved Phase 7.1A turbulence-closure discovery child.

This runner is intentionally narrower than the older Phase 07 treatment
drivers.  It loads the exact active-1000 absorber parent, proves the complete
parent state, changes only the requested k-epsilon closure (or nothing for the
T0 reference), proves the prepared save/reopen state, runs a short attached
500-iteration discovery solve, and writes the paired local evidence manifest.

No initialization, patch, reset, remesh, resplit, outlet change, transient
model, or absorber/source mutation is performed here.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
import traceback
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(ROOT / "scripts" / "setup"))

from extract_report_plot_histories import parse_report_forms, read_remote_forms  # noqa: E402
from pyansys_fluent.common import (  # noqa: E402
    remote_chdir,
    remote_file_exists,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture  # noqa: E402
from pyansys_fluent.stage4_native import (  # noqa: E402
    configure_autosave,
    configure_residual_history,
    data_path,
    ensure_remote_directory,
    remote_file_sha256,
    scientific_readback,
    set_turbulence_variant,
)
from run_p7_e5_cz import (  # noqa: E402
    fluid_names,
    read_source_tree,
    try_integrated_source_reports,
)
from run_p7_e5_cz_absorb import redirect_all_reports  # noqa: E402
from run_p7_treatment_screen import parse_residuals  # noqa: E402


PARENT_SETUP = "P7-E5-CZ-ABSORB-COLD-RAMP11692"
PARENT_CASE = r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.cas.h5"
PARENT_DATA = data_path(PARENT_CASE)
PARENT_FLUID_ZONES = {"separator-purnanto", "p7-e5-lower-y010"}
REMOTE_BASE = r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\Phase71A\TurbulenceFamily"
HORIZON = 500
SMOKE = 50
CHECKPOINT = 250
EXPECTED_ABSORBER_SOURCE = -379.2377886984495
EXPECTED_ABSORBER_INTEGRAL = -116.92
EXPECTED_LIQUID_INLET = 116.92
EXPECTED_VAPOR_INLET = 80.69
REQUIRED_REPORTS = {
    "e0-liquid-mass-total-rfile",
    "e0-liquid-volume-total-rfile",
    "absorb-lower-liquid-mass-rfile",
    "absorb-lower-liquid-volume-rfile",
    "absorb-adjacent-liquid-mass-rfile",
    "absorb-broad-liquid-mass-rfile",
}
REQUIRED_REPORTS.update(
    f"e0-flux-{phase}-{surface}-rfile"
    for phase in ("mixture", "phase1", "phase2")
    for surface in ("liquidinlet", "steaminlet", "steamoutlet", "bottom")
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str, allow_nan=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_yaml(path: Path, payload: Any) -> None:
    import yaml

    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite canonical run-paths file: {path}")
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def rp_clock(solver: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    try:
        result["current-iteration"] = solver.scheme.eval("(rpgetvar 'current-iteration)")
    except Exception as exc:
        result["current-iteration"] = {"error": f"{type(exc).__name__}: {exc}"}
    try:
        result["iterating"] = bool(solver.settings.solution.run_calculation.iterating())
    except Exception as exc:
        result["iterating"] = {"error": f"{type(exc).__name__}: {exc}"}
    return result


def artifact_paths(run_root: str, candidate: str) -> dict[str, str]:
    root = PureWindowsPath(run_root)
    return {
        "prepared_case": str(root / f"{candidate}-prepared.cas.h5"),
        "prepared_data": str(root / f"{candidate}-prepared.dat.h5"),
        "smoke_case": str(root / f"{candidate}-active050.cas.h5"),
        "smoke_data": str(root / f"{candidate}-active050.dat.h5"),
        "checkpoint_case": str(root / f"{candidate}-active250.cas.h5"),
        "checkpoint_data": str(root / f"{candidate}-active250.dat.h5"),
        "final_case": str(root / f"{candidate}-active500.cas.h5"),
        "final_data": str(root / f"{candidate}-active500.dat.h5"),
        "monitor_root": str(root / "monitors"),
        "scratch_root": str(root / "scratch"),
    }


def full_readback(solver: Any) -> dict[str, Any]:
    """Capture the complete comparison state before/after the closure delta."""
    return {
        "scientific": scientific_readback(solver),
        "materials": safe_get_state(solver.settings.setup.materials, "materials"),
        "cell_zone_conditions": safe_get_state(solver.settings.setup.cell_zone_conditions, "cell zones"),
        "source_tree": read_source_tree(solver),
        "fluid_zone_names": fluid_names(solver),
        "residual_monitor": safe_get_state(solver.settings.solution.monitor.residual, "residual monitor"),
        "report_definitions": safe_get_state(solver.settings.solution.report_definitions, "report definitions"),
        "autosave": safe_get_state(solver.settings.file.auto_save, "autosave"),
        "runtime": rp_clock(solver),
    }


def validate_parent_readback(
    readback: Mapping[str, Any],
    expected_closure: str,
    *,
    expected_wall_treatment: str = "standard-wall-fn",
    expected_production_limiter: bool = False,
    expected_kato_launder: bool = False,
    expected_dispersion: bool = False,
    expected_differential_viscosity: bool = True,
    expected_swirl: bool = True,
    expected_k_scheme: str = "first-order-upwind",
) -> dict[str, Any]:
    scientific = readback["scientific"]
    models = scientific["models"]
    methods = scientific["methods"]
    boundaries = scientific["boundaries"]
    cells = readback["cell_zone_conditions"]
    source_tree = readback["source_tree"]

    if nested(models, "multiphase", "model") != "mixture":
        raise RuntimeError("parent multiphase model is not Mixture")
    phases = nested(models, "multiphase", "phases") or {}
    if nested(phases, "phase-1", "material") != "water-vapor-at-psep":
        raise RuntimeError(f"phase-1 material mismatch: {phases}")
    if nested(phases, "phase-2", "material") != "water-liquid-at-psep":
        raise RuntimeError(f"phase-2 material mismatch: {phases}")
    if nested(models, "viscous", "model") != "k-epsilon":
        raise RuntimeError("parent viscous model is not k-epsilon")
    if nested(models, "viscous", "k_epsilon_model") != expected_closure:
        raise RuntimeError(
            f"closure readback mismatch: expected={expected_closure!r} "
            f"actual={nested(models, 'viscous', 'k_epsilon_model')!r}"
        )
    actual_wall_treatment = nested(models, "viscous", "near_wall_treatment", "wall_treatment")
    if actual_wall_treatment != expected_wall_treatment:
        raise RuntimeError(
            f"wall treatment mismatch: expected={expected_wall_treatment!r} actual={actual_wall_treatment!r}"
        )
    if nested(models, "viscous", "options", "curvature_correction", "enabled") is not False:
        raise RuntimeError("curvature correction is not proven off")
    actual_production_limiter = nested(models, "viscous", "options", "production_limiter", "enabled")
    if actual_production_limiter is not expected_production_limiter:
        raise RuntimeError(
            f"production limiter mismatch: expected={expected_production_limiter!r} actual={actual_production_limiter!r}"
        )
    kato_launder = nested(models, "viscous", "options", "production_kato_launder_enabled")
    if expected_closure == "realizable":
        # Fluent 2025 R2 does not expose the RNG/Kato-Launder option on the
        # realizable branch.  Its closure-specific readback instead exposes
        # rke_cmu_rotation_term.  An absent Kato field therefore means
        # "not applicable", not an enabled frozen option.
        if expected_kato_launder:
            raise RuntimeError("realizable branch cannot prove Kato-Launder production")
        if kato_launder not in (None, False):
            raise RuntimeError("realizable branch exposed enabled Kato-Launder production")
        if nested(models, "viscous", "turbulence_expert", "rke_cmu_rotation_term") is not False:
            raise RuntimeError("realizable closure rotation term is not proven off")
    elif kato_launder is not expected_kato_launder:
        raise RuntimeError(
            f"Kato-Launder production mismatch: expected={expected_kato_launder!r} actual={kato_launder!r}"
        )
    actual_dispersion = nested(models, "viscous", "multiphase_turbulence", "multiphase_options", "dispersion_in_relative_velocity")
    if actual_dispersion is not expected_dispersion:
        raise RuntimeError(
            f"multiphase turbulence dispersion mismatch: expected={expected_dispersion!r} actual={actual_dispersion!r}"
        )
    rng = nested(models, "viscous", "rng") or nested(models, "viscous", "rng_options") or {}
    actual_differential = nested(rng, "differential_viscosity_model")
    actual_swirl = nested(rng, "swirl_dominated_flow")
    if actual_differential is not expected_differential_viscosity:
        raise RuntimeError(
            f"RNG differential-viscosity mismatch: expected={expected_differential_viscosity!r} actual={actual_differential!r}"
        )
    if actual_swirl is not expected_swirl:
        raise RuntimeError(
            f"RNG swirl mismatch: expected={expected_swirl!r} actual={actual_swirl!r}"
        )
    if nested(models, "energy", "enabled") is True:
        raise RuntimeError("energy is unexpectedly enabled")
    if nested(models, "species", "enabled") is True:
        raise RuntimeError("species is unexpectedly enabled")

    fluid = nested(cells, "fluid") or {}
    actual_fluid = {str(name) for name in fluid if str(name) != "settings"}
    if actual_fluid != PARENT_FLUID_ZONES:
        raise RuntimeError(f"fluid-zone topology mismatch: {sorted(actual_fluid)}")

    walls = nested(boundaries, "wall") or {}
    pressure = nested(boundaries, "pressure_outlet") or {}
    mass_inlets = nested(boundaries, "mass_flow_inlet") or {}
    if "bottom" not in walls:
        raise RuntimeError("bottom wall is missing")
    if set(pressure) - {"settings", "steamoutlet"}:
        raise RuntimeError(f"unexpected pressure-outlet zones: {sorted(pressure)}")
    if {"liquidinlet", "steaminlet"} - set(mass_inlets):
        raise RuntimeError(f"mass-flow inlets are incomplete: {sorted(mass_inlets)}")
    if "bottom" in pressure or "bottom" in mass_inlets:
        raise RuntimeError("bottom is no longer a wall")

    liquid_flow = nested(mass_inlets, "liquidinlet", "phase", "phase-2", "momentum", "mass_flow_rate", "value")
    vapor_flow = nested(mass_inlets, "steaminlet", "phase", "phase-1", "momentum", "mass_flow_rate", "value")
    if liquid_flow is None or abs(float(liquid_flow) - EXPECTED_LIQUID_INLET) > 1e-9:
        raise RuntimeError(f"liquid inlet target mismatch: {liquid_flow!r}")
    if vapor_flow is None or abs(float(vapor_flow) - EXPECTED_VAPOR_INLET) > 1e-9:
        raise RuntimeError(f"vapor inlet target mismatch: {vapor_flow!r}")

    parent_sources = source_tree["separator-purnanto"]
    lower_sources = source_tree["p7-e5-lower-y010"]
    if parent_sources["phase-1"].get("enable") is not False:
        raise RuntimeError("parent-zone phase-1 source is not off")
    if parent_sources["phase-2"].get("enable") is not False:
        raise RuntimeError("parent-zone phase-2 source is not off")
    if lower_sources["phase-1"].get("enable") is not False:
        raise RuntimeError("lower-zone phase-1 source is not off")
    if lower_sources["phase-2"].get("enable") is not True:
        raise RuntimeError("lower-zone phase-2 absorber source is not enabled")

    flow_scheme = nested(methods, "p_v_coupling", "flow_scheme") or nested(methods, "pressure_velocity_coupling", "flow_scheme")
    if str(flow_scheme).upper() != "SIMPLE":
        raise RuntimeError(f"pressure-velocity coupling is not SIMPLE: {flow_scheme!r}")
    if nested(methods, "spatial_discretization", "gradient_scheme") not in {"green-gauss-node-based", "green-gauss-node"}:
        raise RuntimeError("Green-Gauss node-based gradient is not proven")
    discretization = nested(methods, "spatial_discretization", "discretization_scheme") or {}
    if discretization.get("pressure") != "presto!":
        raise RuntimeError("PRESTO! pressure is not proven")
    if discretization.get("mom") != "second-order-upwind":
        raise RuntimeError("second-order momentum is not proven")
    if discretization.get("k") != expected_k_scheme:
        raise RuntimeError(f"k discretization mismatch: expected={expected_k_scheme!r} actual={discretization.get('k')!r}")
    if discretization.get("epsilon") != "second-order-upwind":
        raise RuntimeError("second-order epsilon is not proven")
    if discretization.get("mp") != "quick":
        raise RuntimeError("QUICK phase-fraction treatment is not proven")

    return {
        "closure": expected_closure,
        "fluid_zones": sorted(actual_fluid),
        "bottom_wall": True,
        "absorber": {
            "zone": "p7-e5-lower-y010",
            "phase": "phase-2",
            "source_enable": lower_sources["phase-2"].get("enable"),
            "expected_source_kg_m3_s": EXPECTED_ABSORBER_SOURCE,
            "expected_integrated_kg_s": EXPECTED_ABSORBER_INTEGRAL,
        },
        "inlets": {"liquid_phase2_kg_s": float(liquid_flow), "vapor_phase1_kg_s": float(vapor_flow)},
        "coupling": flow_scheme,
    }


def non_viscous_scientific(readback: Mapping[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(dict(readback["scientific"]))
    models = result.get("models")
    if isinstance(models, Mapping):
        models.pop("viscous", None)
    return result


def assert_frozen_parent(before: Mapping[str, Any], after: Mapping[str, Any], *, expected_closure: str) -> None:
    if non_viscous_scientific(before) != non_viscous_scientific(after):
        raise RuntimeError("a scientific setting outside the viscous closure branch changed")
    for key in ("materials", "cell_zone_conditions", "source_tree", "fluid_zone_names"):
        if before[key] != after[key]:
            raise RuntimeError(f"frozen parent state changed outside allowed output paths: {key}")
    validate_parent_readback(after, expected_closure)


def save_pair_new(solver: Any, case_path: str) -> None:
    data = data_path(case_path)
    for path in (case_path, data):
        if remote_file_exists(solver, path):
            raise FileExistsError(f"refusing to overwrite paired artifact: {path}")
    solver.settings.file.write_case(file_name=case_path)
    solver.settings.file.write_data(file_name=data)
    if not remote_file_exists(solver, case_path) or not remote_file_exists(solver, data):
        raise RuntimeError(f"paired save failed: {case_path}")


def verify_report_paths(solver: Any, expected: Mapping[str, str]) -> None:
    state = safe_get_state(solver.settings.solution.monitor.report_files, "report files")
    if not isinstance(state, Mapping):
        raise RuntimeError("report-file state is not readable")
    for name, path in expected.items():
        actual = nested(state, name, "file_name")
        actual_text = str(actual)
        expected_name = PureWindowsPath(path).name.casefold()
        relative_name = PureWindowsPath(actual_text).name.casefold()
        if actual_text.lower() != str(path).lower() and relative_name != expected_name:
            raise RuntimeError(f"report path changed after reopen for {name}: {actual!r} != {path!r}")


def extract_histories(solver: Any, paths: Mapping[str, str], local_output: Path) -> dict[str, Any]:
    histories: dict[str, Any] = {}
    missing: list[str] = []
    short: dict[str, int] = {}
    for name, path in paths.items():
        if not remote_file_exists(solver, path):
            missing.append(name)
            continue
        try:
            record = parse_report_forms(read_remote_forms(solver, path))
        except Exception as exc:
            raise RuntimeError(f"could not parse report history {name}: {type(exc).__name__}: {exc}") from exc
        record.update({"monitor_name": name, "remote_file": path})
        histories[name] = record
        if int(record.get("points", 0)) < HORIZON:
            short[name] = int(record.get("points", 0))
    if missing:
        raise RuntimeError(f"required report files missing after solve: {missing}")
    if short:
        raise RuntimeError(f"required report histories shorter than {HORIZON}: {short}")
    write_json(local_output, {"kind": "phase71a_turbulence_report_histories", "reports": histories})
    return histories


def diagnostic_counts(text: str) -> dict[str, int]:
    return {
        "reversed_flow_messages": len(re.findall(r"Reversed flow on", text, re.I)),
        "turbulent_viscosity_limit_messages": len(re.findall(r"turbulent viscosity limited", text, re.I)),
        "amg_divergence_messages": len(re.findall(r"Divergence detected in AMG solver", text, re.I)),
        "floating_point_or_fatal_messages": len(re.findall(r"floating point exception|fatal error", text, re.I)),
    }


def run_blocks(solver: Any, capture: SessionTranscriptCapture, manifest: dict[str, Any], paths: Mapping[str, str], local_manifest: Path) -> dict[str, Any]:
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
    return residuals


def make_run_paths(candidate: str, run_id: str, local_dir: Path, paths: Mapping[str, str], report_paths: Mapping[str, str]) -> dict[str, Any]:
    return {
        "setup_id": candidate,
        "run_id": run_id,
        "phase_id": "phase-07-1a-absorber-convergence",
        "server": {
            "ref": f"student@{os.getenv('STUDENT_IP', '10.0.0.5')}",
            "id": "student",
            "ip": os.getenv("STUDENT_IP", "10.0.0.5"),
            "fluent_version": "Ansys Fluent 2025 R2",
        },
        "execution": {"mode": "attached-discovery", "requested_active_iterations": HORIZON, "smoke_iterations": SMOKE},
        "parent": {"setup_id": PARENT_SETUP, "case": PARENT_CASE, "data": PARENT_DATA},
        "remote": {"run_root": str(PureWindowsPath(paths["prepared_case"]).parent), "monitor_root": paths["monitor_root"], "scratch_root": paths["scratch_root"]},
        "prepared": {"case": paths["prepared_case"], "data": paths["prepared_data"]},
        "smoke": {"case": paths["smoke_case"], "data": paths["smoke_data"]},
        "checkpoint": {"case": paths["checkpoint_case"], "data": paths["checkpoint_data"]},
        "final": {"case": paths["final_case"], "data": paths["final_data"]},
        "report_files": dict(report_paths),
        "local_artifacts": {
            "directory": str(local_dir),
            "manifest": str(local_dir / "run-manifest.json"),
            "residuals": str(local_dir / "residuals.json"),
            "reports": str(local_dir / "reports.json"),
            "transcript": str(local_dir / "transcript.txt"),
        },
        "durability": {"status": "LOCAL_ONLY", "note": "Remote pair is preserved on student; no OneDrive promotion was requested by this queue."},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, choices=("P71A-T0-RNG-REFERENCE", "P71A-T1-STANDARD-KEPSILON", "P71A-T1-REALIZABLE-KEPSILON"))
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--run-stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--local-dir", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    closure = {"P71A-T0-RNG-REFERENCE": "rng", "P71A-T1-STANDARD-KEPSILON": "standard", "P71A-T1-REALIZABLE-KEPSILON": "realizable"}[args.candidate]
    delta = "none" if closure == "rng" else f"rng to {closure} k-epsilon"
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
        "candidate_id": {"P71A-T0-RNG-REFERENCE": "C2-T0", "P71A-T1-STANDARD-KEPSILON": "C2-T1-STD", "P71A-T1-REALIZABLE-KEPSILON": "C2-T1-REAL"}[args.candidate],
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
        "controlled_delta": delta,
        "requested_closure": closure,
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
        remote_chdir(solver, str(PureWindowsPath(PARENT_CASE).parent))
        solver.settings.file.read_case(file_name=PARENT_CASE)
        solver.settings.file.read_data(file_name=PARENT_DATA)
        parent = full_readback(solver)
        validate_parent_readback(parent, "rng")
        manifest["parent_readback"] = parent
        manifest["parent_validation"] = "PASS"
        write_json(local_manifest, manifest)

        if closure != "rng":
            set_turbulence_variant(solver, closure)
        changed = full_readback(solver)
        validate_parent_readback(changed, closure)
        assert_frozen_parent(parent, changed, expected_closure=closure)
        manifest["closure_readback_before_save"] = changed
        manifest["closure_validation"] = "PASS"

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
        assert_frozen_parent(changed, prepared, expected_closure=closure)
        remote_chdir(solver, paths["monitor_root"])
        verify_report_paths(solver, monitor_paths)
        manifest["prepared_reopen"] = prepared
        manifest["prepared_pair_verified"] = True
        write_json(local_manifest, manifest)

        capture = SessionTranscriptCapture(solver, stream_path=local_transcript, echo=False)
        capture.start()
        run_blocks(solver, capture, manifest, paths, local_manifest)
        residuals = manifest["residuals"]
        write_json(local_residuals, residuals)
        manifest["residual_history_local"] = str(local_residuals)
        capture.close()
        capture = None

        solver.settings.file.read_case(file_name=paths["final_case"])
        solver.settings.file.read_data(file_name=paths["final_data"])
        final_readback = full_readback(solver)
        assert_frozen_parent(prepared, final_readback, expected_closure=closure)
        remote_chdir(solver, paths["monitor_root"])
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
            "achieved_active_iterations": manifest.get("achieved_active_iterations"),
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

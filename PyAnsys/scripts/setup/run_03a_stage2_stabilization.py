#!/usr/bin/env python3
"""Run the independent 03A Stage-2 children through Fluent-native journals.

The runner deliberately submits one native journal per branch.  A floating
point exception, AMG divergence, or other unrecoverable native error therefore
terminates only that branch's journal; the runner records the expected/missing
artifacts and attempts the next independent child from its own Stage-1-derived
case/data pair.

Python prepares journals, submits them, reconnects/reads artifacts, and writes
read-only evidence.  It never calls a Fluent iteration method or owns a
client-side iteration/checkpoint loop.  N5 is two native phases because the
standard-k-epsilon bootstrap must be checkpointed before the settings API
restores RNG k-epsilon for the return-to-authority phase.
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

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import (  # noqa: E402
    calculate_carrier_metrics,
    capture_session_summary,
    extract_mass_flow_report,
    load_case_data_pair,
    plot_residual_history,
    write_json,
)


DEFAULT_REMOTE_DIR = r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet"
RESIDUAL_HISTORY_SIZE = 800
RETURN_AUTHORITY_ITERATIONS = 250


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def posix(path: str) -> str:
    return str(path).replace("\\", "/")


def ensure_absent(solver: Any, paths: list[str]) -> None:
    existing = [path for path in paths if remote_file_exists(solver, path)]
    if existing:
        raise FileExistsError("Refusing to overwrite Stage-2 run artifacts: " + ", ".join(existing))


def infer_failure_category(error: str) -> str:
    text = error.casefold()
    if "floating point" in text or "floating-point" in text or "fpe" in text:
        return "floating_point_exception"
    if "amg" in text and ("diverg" in text or "failure" in text):
        return "amg_divergence"
    if "connection" in text or "grpc" in text or "transport" in text:
        return "connection_lost_unknown_solver_state"
    if "journal" in text:
        return "native_journal_exception"
    return "native_run_exception"


def write_remote_journal(solver: Any, remote_journal: str, journal: str) -> None:
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)'
        for line in journal.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(remote_journal))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, remote_journal):
        raise RuntimeError(f"Fluent did not expose the native journal: {remote_journal}")


def render_branch_journal(
    *,
    branch: str,
    phase: str,
    parent_case: str,
    input_case: str,
    input_data: str,
    iterations: int,
    endpoint_case: str,
    transcript: str,
    residual_file: str,
) -> str:
    return "\n".join(
        [
            f"; 03A Stage-2 {branch} {phase} native journal",
            f"; Source parent lineage: {parent_case}",
            f"; Branch input case/data: {input_case} / {input_data}",
            "; Fluent owns this single steady iteration command.",
            "; If Fluent raises FPE/AMG divergence, later write/export commands may not execute.",
            "; The submitter records that branch failure and continues with independent children.",
            "/file/confirm-overwrite? no",
            f'/file/start-transcript "{posix(transcript)}"',
            "/solve/monitors/residual/print? yes",
            "/solve/monitors/residual/plot? yes",
            f"/solve/monitors/residual/n-save {RESIDUAL_HISTORY_SIZE}",
            f'/file/read-case-data "{posix(input_case)}"',
            f"/solve/iterate {iterations}",
            f'/file/write-case-data "{posix(endpoint_case)}"',
            f'/plot/residuals-set/plot-to-file "{posix(residual_file)}"',
            "/plot/residuals",
            "/plot/residuals-set/end-plot-to-file",
            "/file/stop-transcript",
            f"; 03A Stage-2 {branch} {phase} native journal finished; Fluent remains open.",
            "",
        ]
    )


def artifact_state(solver: Any, artifacts: Mapping[str, str]) -> dict[str, bool | None]:
    state: dict[str, bool | None] = {}
    for name, path in artifacts.items():
        if not path:
            continue
        try:
            state[name] = remote_file_exists(solver, path)
        except Exception:
            # A dropped gRPC connection leaves remote artifact state unknown;
            # do not turn that unknown into a false solver-failure claim.
            state[name] = None
    return state


def snapshot_monitors(solver: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"available": False, "sets": {}, "warnings": []}
    try:
        names = [str(name) for name in solver.monitors.get_monitor_set_names()]
    except Exception as exc:
        payload["warnings"].append(f"monitor-set enumeration failed: {type(exc).__name__}: {exc}")
        return payload
    for name in sorted(names):
        try:
            x_values, series = solver.monitors.get_monitor_set_data(name)
            payload["sets"][name] = {
                "x": list(x_values),
                "series": {str(key): list(values) for key, values in series.items()},
            }
            payload["available"] = True
        except Exception as exc:
            payload["warnings"].append(
                f"monitor-set {name!r} read failed: {type(exc).__name__}: {exc}"
            )
    return payload


def residual_payload_from_monitors(monitors: Mapping[str, Any]) -> dict[str, Any]:
    sets = monitors.get("sets", {}) if isinstance(monitors, Mapping) else {}
    residual = sets.get("residual", {}) if isinstance(sets, Mapping) else {}
    if not isinstance(residual, Mapping):
        return {"monitor_set": "residual", "iterations": [], "series": {}, "point_count": 0}
    return {
        "monitor_set": "residual",
        "iterations": residual.get("x", []),
        "series": residual.get("series", {}),
        "point_count": len(residual.get("x", [])),
        "curve_count": len(residual.get("series", {})),
    }


def current_settings_readback(solver: Any) -> dict[str, Any]:
    return {
        "models": safe_get_state(solver.settings.setup.models, "Stage-2 endpoint models"),
        "methods": safe_get_state(solver.settings.solution.methods, "Stage-2 endpoint methods"),
        "controls": safe_get_state(solver.settings.solution.controls, "Stage-2 endpoint controls"),
        "solver": safe_get_state(solver.settings.setup.general.solver, "Stage-2 endpoint solver"),
        "boundaries": safe_get_state(
            solver.settings.setup.boundary_conditions,
            "Stage-2 endpoint boundary conditions",
        ),
    }


def collect_endpoint_evidence(
    solver: Any,
    *,
    branch: str,
    phase: str,
    endpoint_case: str,
    endpoint_data: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Reload one complete endpoint and collect read-only evidence."""
    load_summary = load_case_data_pair(
        solver,
        case_file=endpoint_case,
        data_file=endpoint_data,
        load_strategy="paired",
    )
    session = capture_session_summary(solver)
    zone_discovery = session.get("zone_discovery", {})
    roles = zone_discovery.get("roles", {}) if isinstance(zone_discovery, Mapping) else {}
    zones: list[str] = []
    for role in ("liquid_inlet", "steam_inlet"):
        value = roles.get(role) if isinstance(roles, Mapping) else None
        if value and value not in zones:
            zones.append(str(value))
    for value in zone_discovery.get("all_outlets", []) if isinstance(zone_discovery, Mapping) else []:
        if value and value not in zones:
            zones.append(str(value))
    phase_map = session.get("phase_domain_map", {})
    vapor_domain = str(phase_map.get("vapor_domain", "phase-1"))
    liquid_domain = str(phase_map.get("liquid_domain", "phase-2"))
    carrier_fluxes = extract_mass_flow_report(
        solver,
        zones=zones,
        domains=(vapor_domain, liquid_domain),
    )
    carrier_metrics = calculate_carrier_metrics(
        carrier_fluxes,
        roles,
        vapor_domain=vapor_domain,
        liquid_domain=liquid_domain,
    )
    monitors = snapshot_monitors(solver)
    residual = residual_payload_from_monitors(monitors)
    output_dir.mkdir(parents=True, exist_ok=True)
    label = f"{branch}-{phase}"
    residual_json = output_dir / f"{label}-residual-check.json"
    residual_png = output_dir / f"{label}-residual-check.png"
    flux_json = output_dir / f"{label}-flux-check.json"
    monitor_json = output_dir / f"{label}-monitor-history.json"
    write_json(residual_json, residual)
    write_json(flux_json, {
        "run_label": label,
        "load": load_summary,
        "carrier_fluxes": carrier_fluxes,
        "carrier_metrics": carrier_metrics,
    })
    write_json(monitor_json, monitors)
    plot_warning = None
    try:
        plot_residual_history(residual, residual_png, title=f"03A Stage-2 {label} scaled residuals")
    except Exception as exc:
        plot_warning = f"residual plot failed: {type(exc).__name__}: {exc}"
    return {
        "load": load_summary,
        "session": session,
        "settings_readback": current_settings_readback(solver),
        "carrier_fluxes": carrier_fluxes,
        "carrier_metrics": carrier_metrics,
        "monitor_history": monitors,
        "residual_history": residual,
        "artifact_paths": {
            "flux_json": str(flux_json),
            "residual_json": str(residual_json),
            "residual_plot": str(residual_png) if plot_warning is None else None,
            "monitor_json": str(monitor_json),
        },
        "warnings": [plot_warning] if plot_warning else [],
    }


def prepare_phase_artifacts(
    solver: Any,
    *,
    child: Mapping[str, Any],
    phase: str,
    iterations: int,
    remote_dir: str,
    stamp: str,
    output_dir: Path,
) -> dict[str, Any]:
    branch = str(child["branch"])
    if phase == "standard-bootstrap":
        stem = f"03A-S2-{branch}-standard-from-i1000-plus{iterations}-{stamp}"
    elif phase == "rng-return":
        stem = f"03A-S2-{branch}-rng-return-plus{iterations}-{stamp}"
    else:
        stem = f"03A-S2-{branch}-from-i1000-plus{iterations}-{stamp}"
    endpoint_case = str(PureWindowsPath(remote_dir) / f"{stem}.cas.h5")
    endpoint_data = str(PureWindowsPath(remote_dir) / f"{stem}.dat.h5")
    transcript = str(PureWindowsPath(remote_dir) / f"{stem}.trn")
    residual_file = str(PureWindowsPath(remote_dir) / f"{stem}-residuals.out")
    remote_journal = str(PureWindowsPath(remote_dir) / f"{stem}.jou")
    local_journal = output_dir / f"{stem}.jou"
    ensure_absent(
        solver,
        [endpoint_case, endpoint_data, transcript, residual_file, remote_journal],
    )
    journal = render_branch_journal(
        branch=branch,
        phase=phase,
        parent_case=str(child["source_parent_case"]),
        input_case=str(child["pre_run_case"]),
        input_data=str(child["pre_run_data"]),
        iterations=iterations,
        endpoint_case=endpoint_case,
        transcript=transcript,
        residual_file=residual_file,
    )
    local_journal.parent.mkdir(parents=True, exist_ok=True)
    local_journal.write_text(journal, encoding="utf-8", newline="\n")
    write_remote_journal(solver, remote_journal, journal)
    return {
        "branch": branch,
        "phase": phase,
        "iterations_requested": iterations,
        "input_case": str(child["pre_run_case"]),
        "input_data": str(child["pre_run_data"]),
        "endpoint_case": endpoint_case,
        "endpoint_data": endpoint_data,
        "transcript": transcript,
        "residual_file": residual_file,
        "remote_journal": remote_journal,
        "local_journal": str(local_journal),
        "journal": journal,
        "artifacts": {
            "endpoint_case": endpoint_case,
            "endpoint_data": endpoint_data,
            "transcript": transcript,
            "residual_file": residual_file,
            "remote_journal": remote_journal,
        },
    }


def submit_phase(
    solver: Any,
    *,
    child: Mapping[str, Any],
    phase_artifacts: Mapping[str, Any],
    output_dir: Path,
    campaign_payload: dict[str, Any],
) -> dict[str, Any]:
    branch = str(phase_artifacts["branch"])
    phase = str(phase_artifacts["phase"])
    record: dict[str, Any] = {
        "branch": branch,
        "phase": phase,
        "input_case": phase_artifacts["input_case"],
        "input_data": phase_artifacts["input_data"],
        "expected_artifacts": phase_artifacts["artifacts"],
        "local_journal": phase_artifacts["local_journal"],
        "remote_journal": phase_artifacts["remote_journal"],
        "native_iterations_requested": phase_artifacts["iterations_requested"],
        "status": "SUBMITTED_NATIVE_RUN",
        "failure": None,
    }
    campaign_payload["phases"].append(record)
    write_json(output_dir / "campaign-live.json", campaign_payload)

    try:
        try:
            solver.tui.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.read_journal(file_name_list=[phase_artifacts["remote_journal"]])
    except Exception as exc:
        record["failure"] = {
            "category": infer_failure_category(f"{type(exc).__name__}: {exc}"),
            "exception": f"{type(exc).__name__}: {exc}",
        }
        try:
            solver.tui.file.stop_transcript()
        except Exception:
            pass
    finally:
        existence = artifact_state(solver, phase_artifacts["artifacts"])
        record["remote_existence"] = existence

    case_exists = existence.get("endpoint_case") is True
    data_exists = existence.get("endpoint_data") is True
    existence_unknown = any(value is None for value in existence.values())
    if case_exists and data_exists:
        record["status"] = (
            "RUN_COMPLETED_ENDPOINT_VERIFIED"
            if record["failure"] is None
            else "ENDPOINT_PRESENT_AFTER_NATIVE_EXCEPTION"
        )
        try:
            evidence = collect_endpoint_evidence(
                solver,
                branch=branch,
                phase=phase,
                endpoint_case=phase_artifacts["endpoint_case"],
                endpoint_data=phase_artifacts["endpoint_data"],
                output_dir=output_dir / "post_simulation_analysis",
            )
            record["evidence"] = evidence
        except Exception as exc:
            record["verification_error"] = f"{type(exc).__name__}: {exc}"
            record["status"] = "ENDPOINT_PRESENT_RELOAD_FAILED"
    elif case_exists or data_exists:
        record["status"] = "FAILED_PARTIAL_ENDPOINT"
        record["failure"] = record["failure"] or {
            "category": "partial_endpoint",
            "exception": "Only one member of the case/data endpoint pair exists.",
        }
    elif existence_unknown:
        record["status"] = "CONNECTION_LOST_UNKNOWN_SOLVER_STATE"
        record["failure"] = record["failure"] or {
            "category": "connection_lost_unknown_solver_state",
            "exception": "gRPC could not verify the remote endpoint artifacts after journal submission.",
        }
    else:
        record["status"] = "FAILED_NO_ENDPOINT"
        record["failure"] = record["failure"] or {
            "category": "native_run_no_endpoint",
            "exception": "Native journal returned without a complete endpoint pair.",
        }

    write_json(output_dir / f"{branch}-{phase}-run.json", record)
    write_json(output_dir / "campaign-live.json", campaign_payload)
    return record


def set_rng_authority(solver: Any) -> dict[str, Any]:
    """Restore the audited RNG model and canonical Stage-2 return methods."""
    viscous = solver.settings.setup.models.viscous
    viscous.model = "k-epsilon"
    viscous = solver.settings.setup.models.viscous
    viscous.k_epsilon_model = "rng"
    viscous = solver.settings.setup.models.viscous
    viscous.rng_options.differential_viscosity_model = True
    viscous.rng_options.swirl_dominated_flow = True
    try:
        viscous.near_wall_treatment.wall_treatment = "standard-wall-fn"
    except Exception:
        pass

    methods = solver.settings.solution.methods
    method_payload = {
        "pressure": "presto!",
        "mom": "second-order-upwind",
        "k": "second-order-upwind",
        "epsilon": "second-order-upwind",
        "mp": "quick",
    }
    try:
        methods.p_v_coupling.flow_scheme = "SIMPLE"
        methods.spatial_discretization.gradient_scheme = "green-gauss-node-based"
        methods.spatial_discretization.discretization_scheme.set_state(method_payload)
        methods.pseudo_time_method.set_state({"formulation": {"segregated_solver": "off"}})
        methods.high_order_term_relaxation.enable = False
    except Exception:
        methods = solver.settings.solution.methods
        methods.set_state(
            {
                "p_v_coupling": {"flow_scheme": "SIMPLE", "solve_n_phase": False},
                "gradient_scheme": "green-gauss-node-based",
                "discretization_scheme": method_payload,
                "pseudo_time_method": {"formulation": {"segregated_solver": "off"}},
                "high_order_term_relaxation": {"enable": False},
            }
        )
    solver.settings.solution.controls.under_relaxation.set_state(
        {
            "pressure": 0.3,
            "mom": 0.7,
            "density": 1.0,
            "body-force": 1.0,
            "drift": 0.1,
            "mp": 0.4,
            "k": 0.8,
            "epsilon": 0.8,
            "turb-viscosity": 1.0,
        }
    )
    readback = current_settings_readback(solver)
    models = readback["models"]
    methods_state = readback["methods"]
    controls = readback["controls"]
    mom = nested(methods_state, "discretization_scheme", "mom") or nested(
        methods_state, "spatial_discretization", "discretization_scheme", "mom"
    )
    k = nested(methods_state, "discretization_scheme", "k") or nested(
        methods_state, "spatial_discretization", "discretization_scheme", "k"
    )
    epsilon = nested(methods_state, "discretization_scheme", "epsilon") or nested(
        methods_state, "spatial_discretization", "discretization_scheme", "epsilon"
    )
    if (
        nested(models, "viscous", "k_epsilon_model") != "rng"
        or mom != "second-order-upwind"
        or k != "second-order-upwind"
        or epsilon != "second-order-upwind"
        or float(nested(controls, "under_relaxation", "k")) != 0.8
        or float(nested(controls, "under_relaxation", "epsilon")) != 0.8
    ):
        raise RuntimeError(f"RNG return-to-authority readback mismatch: {readback}")
    return readback


def prepare_n5_return_start(
    solver: Any,
    *,
    bootstrap_record: Mapping[str, Any],
    remote_dir: str,
    stamp: str,
    output_dir: Path,
) -> dict[str, Any]:
    endpoint_case = str(bootstrap_record["expected_artifacts"]["endpoint_case"])
    endpoint_data = str(bootstrap_record["expected_artifacts"]["endpoint_data"])
    stem = f"03A-S2-N5-rng-return-start-{stamp}"
    return_case = str(PureWindowsPath(remote_dir) / f"{stem}.cas.h5")
    return_data = str(PureWindowsPath(remote_dir) / f"{stem}.dat.h5")
    ensure_absent(solver, [return_case, return_data])
    load_case_data_pair(
        solver,
        case_file=endpoint_case,
        data_file=endpoint_data,
        load_strategy="paired",
    )
    readback = set_rng_authority(solver)
    solver.settings.file.write_case(file_name=return_case)
    solver.settings.file.write_data(file_name=return_data)
    if not all(remote_file_exists(solver, path) for path in (return_case, return_data)):
        raise RuntimeError("N5 RNG-return start pair was not written")
    load_case_data_pair(
        solver,
        case_file=return_case,
        data_file=return_data,
        load_strategy="paired",
    )
    reload_readback = set_rng_authority(solver)
    payload = {
        "source_standard_endpoint_case": endpoint_case,
        "source_standard_endpoint_data": endpoint_data,
        "return_start_case": return_case,
        "return_start_data": return_data,
        "restore_readback": readback,
        "reload_readback": reload_readback,
        "initialization": "none",
        "liquid_patch": False,
        "status": "CASE_DATA_VERIFIED",
    }
    write_json(output_dir / "N5-rng-return-preparation.json", payload)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="student")
    parser.add_argument("--stage2-manifest", required=True, type=Path)
    parser.add_argument("--remote-dir", default=DEFAULT_REMOTE_DIR)
    parser.add_argument("--stamp", default=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--manifest-json", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    stage2_path = args.stage2_manifest.expanduser().resolve()
    stage2 = json.loads(stage2_path.read_text(encoding="utf-8"))
    children = list(stage2.get("children", []))
    if stage2.get("setup_id") != "03A" or len(children) != 4:
        raise ValueError("Expected the verified 03A Stage-2 four-child manifest")
    if set(str(child.get("branch")) for child in children) != {"N1", "N3", "N4", "N5"}:
        raise ValueError("Stage-2 manifest must contain exactly N1, N3, N4, and N5")

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    args.manifest_json.expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
    campaign: dict[str, Any] = {
        "setup_id": "03A",
        "stage": "Stage 2",
        "purpose": "steady numerical-stabilization screen",
        "transport": "Fluent gRPC",
        "stage2_manifest": str(stage2_path),
        "parent_case": stage2.get("parent_case"),
        "parent_data": stage2.get("parent_data"),
        "failure_isolation": "one Fluent-native journal per branch; N5 has a separate standard bootstrap and RNG return journal",
        "phases": [],
        "status": "PLANNED",
    }
    write_json(args.manifest_json.expanduser().resolve(), campaign)

    solver = connect(server_id=args.server_id)
    fluent_version = str(solver.get_fluent_version())
    if "2025 R2" not in fluent_version:
        raise RuntimeError(f"Expected Fluent 2025 R2, got {fluent_version!r}")
    for child in children:
        for path in (str(child["pre_run_case"]), str(child["pre_run_data"])):
            if not remote_file_exists(solver, path):
                raise FileNotFoundError(f"Stage-2 input child is not visible through Fluent gRPC: {path}")

    indexed = {str(child["branch"]): child for child in children}
    campaign["status"] = "SUBMITTING_NATIVE_RUNS"
    write_json(args.manifest_json.expanduser().resolve(), campaign)

    # N1, N3, and N4 are independent 300-iteration initial screens.
    for branch in ("N1", "N3", "N4"):
        child = indexed[branch]
        try:
            artifacts = prepare_phase_artifacts(
                solver,
                child=child,
                phase="initial-screen",
                iterations=300,
                remote_dir=args.remote_dir,
                stamp=args.stamp,
                output_dir=output_dir,
            )
            submit_phase(
                solver,
                child=child,
                phase_artifacts=artifacts,
                output_dir=output_dir,
                campaign_payload=campaign,
            )
        except Exception as exc:
            record = {
                "branch": branch,
                "phase": "initial-screen",
                "status": "FAILED_PREPARATION",
                "failure": {
                    "category": infer_failure_category(f"{type(exc).__name__}: {exc}"),
                    "exception": f"{type(exc).__name__}: {exc}",
                },
            }
            campaign["phases"].append(record)
            write_json(output_dir / f"{branch}-initial-screen-run.json", record)
            write_json(args.manifest_json.expanduser().resolve(), campaign)

    # N5 standard bootstrap, followed only if its complete endpoint can be
    # reloaded and switched back to the canonical RNG authority.
    n5 = indexed["N5"]
    try:
        bootstrap_artifacts = prepare_phase_artifacts(
            solver,
            child=n5,
            phase="standard-bootstrap",
            iterations=500,
            remote_dir=args.remote_dir,
            stamp=args.stamp,
            output_dir=output_dir,
        )
        bootstrap_record = submit_phase(
            solver,
            child=n5,
            phase_artifacts=bootstrap_artifacts,
            output_dir=output_dir,
            campaign_payload=campaign,
        )
        if bootstrap_record.get("status") == "RUN_COMPLETED_ENDPOINT_VERIFIED":
            return_start = prepare_n5_return_start(
                solver,
                bootstrap_record=bootstrap_record,
                remote_dir=args.remote_dir,
                stamp=args.stamp,
                output_dir=output_dir,
            )
            n5_return_child = dict(n5)
            n5_return_child["pre_run_case"] = return_start["return_start_case"]
            n5_return_child["pre_run_data"] = return_start["return_start_data"]
            rng_artifacts = prepare_phase_artifacts(
                solver,
                child=n5_return_child,
                phase="rng-return",
                iterations=300,
                remote_dir=args.remote_dir,
                stamp=args.stamp,
                output_dir=output_dir,
            )
            submit_phase(
                solver,
                child=n5_return_child,
                phase_artifacts=rng_artifacts,
                output_dir=output_dir,
                campaign_payload=campaign,
            )
        else:
            record = {
                "branch": "N5",
                "phase": "rng-return",
                "status": "NOT_ATTEMPTED",
                "failure": {"category": "bootstrap_not_verified", "exception": "N5 standard bootstrap had no verified endpoint."},
            }
            campaign["phases"].append(record)
            write_json(output_dir / "N5-rng-return-run.json", record)
    except Exception as exc:
        record = {
            "branch": "N5",
            "phase": "standard-bootstrap-or-rng-return",
            "status": "FAILED_PREPARATION",
            "failure": {
                "category": infer_failure_category(f"{type(exc).__name__}: {exc}"),
                "exception": f"{type(exc).__name__}: {exc}",
            },
        }
        campaign["phases"].append(record)
        write_json(output_dir / "N5-preparation-failure.json", record)

    campaign["status"] = "RUNS_ATTEMPTED"
    campaign["interpretation_status"] = "pending user direction"
    campaign["return_to_authority"] = {
        "N1": "not automatically attempted; review 300-iteration screen before any 250-iteration canonical return",
        "N3": "not automatically attempted; review 300-iteration screen before any 250-iteration canonical return",
        "N4": "not automatically attempted; review 300-iteration screen before any 250-iteration canonical return",
        "N5": "standard bootstrap followed by 300-iteration RNG return when the bootstrap endpoint verified",
    }
    write_json(args.manifest_json.expanduser().resolve(), campaign)
    print(json.dumps(campaign, indent=2, default=str), flush=True)
    print(f"manifest_json: {args.manifest_json.expanduser().resolve()}", flush=True)
    print("RUNS_ATTEMPTED; Fluent remains open; no solver shutdown was issued.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

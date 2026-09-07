#!/usr/bin/env python3
"""Inspect whether Fluent 2024 R2 exposes a bulk VOF mass-flow outlet rate.

This bounded server-2 diagnostic cold-loads the accepted setup-07n-c centre
step-10 pair, converts ``brineoutlet`` to ``mass-flow-outlet`` only in memory,
captures the live Settings/TUI hierarchy, and then cold-reloads the same parent
to restore the accepted pressure-outlet state.  It performs no initialization,
iteration, or case/data write.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "inspection"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from inspect_setup07n_mesh_geometry import (  # noqa: E402
    capture_connected_clients,
    exclusive_writer_lock,
)
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import probe_object  # noqa: E402

import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_setup07m_pressure_opening_campaign as opening07m  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_setup07n_c_pressure_response_sign_probe as pressure_probe  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = (
    "brine620k_07n_b_server2_bulk_massflow_outlet_live_inspection_"
    "attempt1_20260825"
)
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
PARENT_STEM = (
    "brine620k_07n_c_server2_independent_step90_zero_feed_pressure_bracket_"
    "dt256em6_steps10_attempt2_20260825_centre_additional_step10"
)
PARENT_CASE = REMOTE_ROOT + rf"\{PARENT_STEM}.cas.h5"
PARENT_DATA = REMOTE_ROOT + rf"\{PARENT_STEM}.dat.h5"
PARENT_CASE_SHA256 = "bacf0d22343c933b3d87ee806e6b233152f76aa17f0e76519b9723cb5f2ea198"
PARENT_DATA_SHA256 = "0c000fc3715210936fe1d6793102e173694d6dd694f9bb78bd64024be35290a7"
PARENT_STEP = 100
PARENT_FLOW_TIME_S = 0.007670000000000005
PARENT_PRESSURE_PA = 1_122_349.5
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
MANIFEST_PATH = LOCAL_ROOT / "inspection_manifest.json"
GLOBAL_WRITER_LOCK = (
    PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server2_independent_writer.lock"
)


def write_json(path: Path, payload: Mapping[str, Any], *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if create:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, default=str)
            stream.write("\n")
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, default=str)
        stream.write("\n")
    temporary.replace(path)


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = REMOTE_ROOT + rf"\_{RUN_LABEL}_{label}_sha256.txt"
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "scratch": scratch,
        "sha256": pressure_probe.extension.mesh_study.remote_file_sha256(
            solver, path, scratch
        ),
    }


def object_probe(obj: Any, label: str) -> dict[str, Any]:
    probe = probe_object(obj)
    return {
        "label": label,
        "state": safe_get_state(obj, label),
        "child_names": probe.child_names,
        "command_names": probe.command_names,
        "allowed_values": probe.allowed_values,
        "python_attributes": sorted(
            name for name in dir(obj) if not str(name).startswith("_")
        ),
    }


def nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def flatten_paths(value: Any, prefix: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_paths(child, path))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            rows.extend(flatten_paths(child, f"{prefix}[{index}]"))
    else:
        rows.append({"path": prefix, "value": value})
    return rows


def clock_gate(solver: Any) -> dict[str, Any]:
    clock = transient07j.runtime_clock(solver)
    passed = int(clock["time_step"]) == PARENT_STEP and math.isclose(
        float(clock["flow_time_s"]),
        PARENT_FLOW_TIME_S,
        rel_tol=0.0,
        abs_tol=1.0e-12,
    )
    return {"clock": clock, "passed": passed}


def pressure_parent_gate(solver: Any) -> dict[str, Any]:
    result = pressure_probe.open_settings_gate(solver, PARENT_PRESSURE_PA)
    result["clock"] = clock_gate(solver)
    result["passed"] = bool(result.get("passed")) and result["clock"]["passed"]
    return result


def inspect_mass_flow_outlet(solver: Any) -> dict[str, Any]:
    boundaries = solver.settings.setup.boundary_conditions
    before = {
        "pressure_outlet_names": list(boundaries.pressure_outlet.get_object_names()),
        "mass_flow_outlet_names": list(boundaries.mass_flow_outlet.get_object_names()),
        "brine_pressure_state": safe_get_state(
            boundaries.pressure_outlet["brineoutlet"], "brine pressure outlet before conversion"
        ),
    }
    boundaries.set_zone_type(zone_list=["brineoutlet"], new_type="mass-flow-outlet")

    # Boundary type changes invalidate all previous handles.
    boundaries = solver.settings.setup.boundary_conditions
    names = list(boundaries.mass_flow_outlet.get_object_names())
    if "brineoutlet" not in names:
        raise RuntimeError("brineoutlet did not convert to mass-flow-outlet")
    outlet = boundaries.mass_flow_outlet["brineoutlet"]
    outlet_probe = object_probe(outlet, "mass_flow_outlet.brineoutlet")
    state = outlet_probe["state"]
    flat = flatten_paths(state)
    rate_paths = [
        row for row in flat if "mass_flow" in str(row["path"]).lower()
    ]

    phase_probes: dict[str, Any] = {}
    phase_state = state.get("phase", {}) if isinstance(state, Mapping) else {}
    if isinstance(phase_state, Mapping):
        for phase_name in phase_state:
            try:
                phase = outlet.phase[str(phase_name)]
                phase_probes[str(phase_name)] = object_probe(
                    phase, f"mass_flow_outlet.brineoutlet.phase[{phase_name}]"
                )
                try:
                    phase_probes[str(phase_name)]["momentum"] = object_probe(
                        phase.momentum,
                        f"mass_flow_outlet.brineoutlet.phase[{phase_name}].momentum",
                    )
                except Exception as exc:
                    phase_probes[str(phase_name)]["momentum_probe_error"] = (
                        f"{type(exc).__name__}: {exc}"
                    )
            except Exception as exc:
                phase_probes[str(phase_name)] = {
                    "probe_error": f"{type(exc).__name__}: {exc}"
                }

    mixture_rate = nested(
        state, "phase", "mixture", "momentum", "mass_flow_rate"
    )
    only_phasic_rates = (
        mixture_rate is None
        and nested(state, "phase", "phase-1", "momentum", "mass_flow_rate") is not None
        and nested(state, "phase", "phase-2", "momentum", "mass_flow_rate") is not None
    )
    tui_probe: dict[str, Any]
    try:
        tui_probe = object_probe(
            solver.tui.define.boundary_conditions.mass_flow_outlet,
            "tui.define.boundary_conditions.mass_flow_outlet",
        )
    except Exception as exc:
        tui_probe = {"probe_error": f"{type(exc).__name__}: {exc}"}

    return {
        "before_conversion": before,
        "after_conversion_membership": {
            "pressure_outlet_names": list(boundaries.pressure_outlet.get_object_names()),
            "mass_flow_outlet_names": names,
        },
        "outlet_probe": outlet_probe,
        "phase_probes": phase_probes,
        "mass_flow_paths": rate_paths,
        "tui_probe": tui_probe,
        "bulk_mixture_mass_flow_rate_exposed": mixture_rate is not None,
        "only_separate_phasic_mass_flow_rates_exposed": only_phasic_rates,
        "interpretation": (
            "A bulk/mixture total mass-flow rate is exposed; setup-07n-b may proceed "
            "to a separately gated setter/readback diagnostic."
            if mixture_rate is not None
            else "The live object exposes only separate phasic mass-flow rates; "
            "setup-07n-b as a bulk emergent-composition outlet is not implementable "
            "through this boundary object."
            if only_phasic_rates
            else "The wrapper hierarchy is inconclusive; classify as a path/version "
            "issue before considering a TUI fallback."
        ),
    }


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    if LOCAL_ROOT.exists():
        raise FileExistsError(f"refusing to overwrite inspection evidence: {LOCAL_ROOT}")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=False)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": "2",
        "status": "running",
        "classification": "diagnostic / unresolved live boundary inspection",
        "controller_pid": os.getpid(),
        "started_epoch": time.time(),
        "parent": {
            "case": PARENT_CASE,
            "case_expected_sha256": PARENT_CASE_SHA256,
            "data": PARENT_DATA,
            "data_expected_sha256": PARENT_DATA_SHA256,
            "clock": {"time_step": PARENT_STEP, "flow_time_s": PARENT_FLOW_TIME_S},
        },
        "physical_steps_run": 0,
        "initialization_performed": False,
        "case_data_written": False,
        "remote_in_memory_inspection_field_eligible_parent": False,
    }
    write_json(MANIFEST_PATH, payload, create=True)
    solver: Any | None = None
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK):
            solver = connect(server_id="2", tcp_timeout_seconds=5.0, start_transcript=True)
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_parent_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive server-2 ownership unresolved: {clients!r}")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, PARENT_CASE) or not remote_file_exists(
                solver, PARENT_DATA
            ):
                raise FileNotFoundError("accepted centre step-10 parent pair is incomplete")
            case = remote_hash(solver, PARENT_CASE, "parent_case")
            data = remote_hash(solver, PARENT_DATA, "parent_data")
            payload["parent_readback"] = {"case": case, "data": data}
            if case["sha256"] != PARENT_CASE_SHA256 or data["sha256"] != PARENT_DATA_SHA256:
                raise RuntimeError("accepted centre step-10 parent checksum mismatch")

            solver.settings.file.read_case(file_name=PARENT_CASE)
            solver.settings.file.read_data(file_name=PARENT_DATA)
            time.sleep(2.0)
            payload["parent_settings_gate"] = pressure_parent_gate(solver)
            if not payload["parent_settings_gate"]["passed"]:
                raise RuntimeError("accepted centre step-10 parent settings/clock gate failed")

            payload["mass_flow_outlet_inspection"] = inspect_mass_flow_outlet(solver)

            # Restore the exact accepted state after the in-memory type inspection.
            solver.settings.file.read_case(file_name=PARENT_CASE)
            solver.settings.file.read_data(file_name=PARENT_DATA)
            time.sleep(2.0)
            payload["restored_parent_settings_gate"] = pressure_parent_gate(solver)
            if not payload["restored_parent_settings_gate"]["passed"]:
                raise RuntimeError("accepted parent was not restored after inspection")

            inspection = payload["mass_flow_outlet_inspection"]
            conclusive = bool(inspection["bulk_mixture_mass_flow_rate_exposed"]) or bool(
                inspection["only_separate_phasic_mass_flow_rates_exposed"]
            )
            payload.update(
                {
                    "status": "completed" if conclusive else "diagnostic_unresolved",
                    "classification": (
                        "accepted diagnostic / live mass-flow-outlet hierarchy"
                        if conclusive
                        else "diagnostic / unresolved mass-flow-outlet hierarchy"
                    ),
                    "bulk_07n_b_implementation_authorized": bool(
                        inspection["bulk_mixture_mass_flow_rate_exposed"]
                    ),
                    "physical_steps_run": 0,
                    "parent_restored": True,
                    "completed_epoch": time.time(),
                }
            )
            write_json(MANIFEST_PATH, payload)
            return 0
    except (Exception, KeyboardInterrupt) as exc:
        payload.update(
            {
                "status": "stopped",
                "classification": "diagnostic / unresolved live boundary inspection",
                "bulk_07n_b_implementation_authorized": False,
                "error": f"{type(exc).__name__}: {exc}",
                "failed_epoch": time.time(),
            }
        )
        write_json(MANIFEST_PATH, payload)
        raise
    finally:
        if solver is not None:
            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

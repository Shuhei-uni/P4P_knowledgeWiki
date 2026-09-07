#!/usr/bin/env python3
"""Inspect live Fluent 2024 R2 paths required by the setup-07n-a pilot.

This probe acquires a local writer lock, authenticates one owner, cold-loads
the accepted setup-07l case *without data*, and inspects only the paths needed
by the later 07n-a runner.  It does not initialize, patch, iterate, or write a
Fluent case/data file.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from inspect_setup07n_mesh_geometry import (  # noqa: E402
    capture_connected_clients,
    exclusive_writer_lock,
    write_new_json,
)
from probe_setup07n_initialized_utl_volume import all_disabled  # noqa: E402
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402


EXPECTED_RANKS = 16
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_FIELDS = {"phase-2-vof", "pressure", "velocity-magnitude"}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--carrier-case", required=True)
    result.add_argument("--output-json", required=True)
    result.add_argument("--lock-file", required=True)
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def source_gate(setup: Any) -> dict[str, Any]:
    fluid = setup.cell_zone_conditions.fluid["fluid"]
    states = {
        phase: safe_get_state(fluid.phase[phase].sources, f"07n-a sources {phase}")
        for phase in ("mixture", "phase-1", "phase-2")
    }
    return {"states": states, "passed": all(all_disabled(v) for v in states.values())}


def dpm_gate(setup: Any) -> dict[str, Any]:
    dpm = setup.models.discrete_phase
    result = {
        "injection_names": list(dpm.injections.get_object_names()),
        "interaction": safe_get_state(dpm.general_settings.interaction, "DPM interaction"),
        "unsteady_tracking": safe_get_state(
            dpm.general_settings.unsteady_tracking, "DPM unsteady tracking"
        ),
    }
    result["passed"] = (
        not result["injection_names"]
        and all_disabled(result["interaction"])
        and all_disabled(result["unsteady_tracking"])
    )
    return result


def scalar_field_names(solver: Any) -> dict[str, Any]:
    attempts: list[dict[str, str]] = []
    values: list[str] = []
    try:
        values = [str(v) for v in solver.fields.field_data.scalar_fields.allowed_values()]
        method = "solver.fields.field_data.scalar_fields.allowed_values"
    except Exception as exc:
        attempts.append({"path": "field_data.scalar_fields", "error": repr(exc)})
        try:
            info = solver.fields.field_info.get_scalar_fields_info()
            values = [str(v) for v in info]
            method = "solver.fields.field_info.get_scalar_fields_info"
        except Exception as fallback_exc:
            attempts.append({"path": "field_info.get_scalar_fields_info", "error": repr(fallback_exc)})
            method = "unavailable"
    return {
        "method": method,
        "attempts": attempts,
        "available_fields": sorted(values),
        "expected_fields": sorted(EXPECTED_FIELDS),
        "expected_fields_present": sorted(EXPECTED_FIELDS.intersection(values)),
        "passed": EXPECTED_FIELDS.issubset(values),
        "field_count": len(values),
    }


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    output = Path(args.output_json).expanduser().resolve()
    lock = Path(args.lock_file).expanduser().resolve()
    if output.exists():
        raise FileExistsError(f"refusing to overwrite capability evidence: {output}")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": output.stem,
        "server_id": str(args.server_id),
        "carrier_case": args.carrier_case,
        "data_files_read": [],
        "physical_steps_run": 0,
        "fluent_outputs_written": [],
        "status": "running",
        "classification": "diagnostic / unresolved",
        "started_epoch": time.time(),
    }
    try:
        with exclusive_writer_lock(lock):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                # Fluent delivers TUI ownership/connectivity reports through
                # the PyFluent transcript stream.  Without it, a safe capture
                # can be empty even when the command completed.
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_case_load"] = clients
            if not clients.strip():
                raise RuntimeError(
                    "connected-client report was empty; ownership is unresolved"
                )
            if "No client is connected to server." not in clients:
                raise RuntimeError("another remote client is connected; refusing case load")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, args.carrier_case):
                raise FileNotFoundError(f"carrier case missing: {args.carrier_case}")
            solver.settings.file.read_case(file_name=args.carrier_case)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_case_load"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )

            setup = solver.settings.setup
            boundaries = setup.boundary_conditions
            payload["boundary_membership"] = {
                "wall": list(boundaries.wall.get_object_names()),
                "mass_flow_inlet": list(boundaries.mass_flow_inlet.get_object_names()),
                "pressure_outlet": list(boundaries.pressure_outlet.get_object_names()),
                "mass_flow_outlet": list(boundaries.mass_flow_outlet.get_object_names()),
            }
            payload["models"] = safe_get_state(setup.models, "07n-a live models")
            payload["methods"] = safe_get_state(
                solver.settings.solution.methods, "07n-a live methods"
            )
            payload["dpm_gate"] = dpm_gate(setup)
            payload["source_gate"] = source_gate(setup)
            payload["ewf_gate"] = {
                "sg_wallfilm_rpvar": solver.scheme.eval("(rpgetvar 'sg-wallfilm?)"),
                "model_parameters": solver.scheme.eval(
                    "(rpgetvar 'wall-film/model-parameters)"
                ),
            }
            payload["ewf_gate"]["passed"] = (
                payload["ewf_gate"]["sg_wallfilm_rpvar"] is False
                and not payload["ewf_gate"]["model_parameters"]
            )
            volume_integrals = solver.settings.results.report.volume_integrals
            commands = list(getattr(volume_integrals, "command_names", []))
            if not commands:
                commands = [
                    name
                    for name in ("minimum", "maximum", "volume_average")
                    if hasattr(volume_integrals, name)
                ]
            payload["volume_integral_commands"] = sorted(str(v) for v in commands)
            payload["volume_integral_gate_passed"] = all(
                name in payload["volume_integral_commands"]
                for name in ("minimum", "maximum", "volume_average")
            )
            payload["scalar_field_gate"] = scalar_field_names(solver)

            required = {
                "boundary": (
                    "brineoutlet" in payload["boundary_membership"]["wall"]
                    and set(payload["boundary_membership"]["mass_flow_inlet"])
                    >= {"liquidinlet", "steaminlet"}
                    and payload["boundary_membership"]["pressure_outlet"] == ["steamoutlet"]
                    and not payload["boundary_membership"]["mass_flow_outlet"]
                ),
                "dpm": payload["dpm_gate"]["passed"],
                "sources": payload["source_gate"]["passed"],
                "ewf": payload["ewf_gate"]["passed"],
                "volume_integrals": payload["volume_integral_gate_passed"],
                # A case-only load can leave solution fields inactive until
                # initialization.  The report service itself must exist here;
                # exact requested fields are a hard post-initialization gate
                # in the pilot runner.
                "scalar_field_service": (
                    payload["scalar_field_gate"]["method"] != "unavailable"
                ),
            }
            payload["required_gates"] = required
            payload["postinitialization_gate_required"] = (
                "phase-2-vof, pressure and velocity-magnitude must all be active "
                "before any physical step"
            )
            if not all(required.values()):
                raise RuntimeError(f"live capability/readback gates failed: {required}")
            payload.update(
                {
                    "status": "accepted",
                    "classification": "accepted diagnostic / live capability inspection",
                    "completed_epoch": time.time(),
                }
            )
            write_new_json(output, payload)
            return 0
    except Exception as exc:
        payload.update(
            {
                "status": "unresolved",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        if not output.exists():
            write_new_json(output, payload)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

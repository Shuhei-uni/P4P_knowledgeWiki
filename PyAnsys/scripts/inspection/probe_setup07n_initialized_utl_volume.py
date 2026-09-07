#!/usr/bin/env python3
"""Probe setup-07n UTL volume reports after a fresh case-only initialization.

The accepted setup-07l case is used only as a settings carrier.  No data file
is read, no pool is patched, no physical step is run, and no Fluent case/data
is written.  A uniquely named temporary cell register is deleted after its
mesh-volume reports are captured.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
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
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


EXPECTED_RANKS = 16


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--carrier-case", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--lock-file", required=True)
    parser.add_argument("--register-name", required=True)
    parser.add_argument("--minimum", type=float, nargs=3, required=True)
    parser.add_argument("--maximum", type=float, nargs=3, required=True)
    parser.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return parser


def capture_report(call) -> dict[str, Any]:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            result = call()
            time.sleep(1.0)
            if result is not None:
                print(result)
        return {"status": "returned", "raw_report": buffer.getvalue()}
    except Exception as exc:
        return {
            "status": "unavailable",
            "error": f"{type(exc).__name__}: {exc}",
            "raw_report": buffer.getvalue(),
        }


def all_disabled(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"enable", "enabled"} and child is True:
                return False
            if not all_disabled(child):
                return False
    elif isinstance(value, list):
        return all(all_disabled(child) for child in value)
    return True


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    output_path = Path(args.output_json).expanduser().resolve()
    lock_path = Path(args.lock_file).expanduser().resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite UTL probe evidence: {output_path}")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": output_path.stem,
        "status": "running",
        "classification": "diagnostic / unresolved",
        "server_id": str(args.server_id),
        "settings_carrier_case": args.carrier_case,
        "data_files_read": [],
        "physical_steps_run": 0,
        "case_data_outputs_written": [],
        "started_epoch": time.time(),
    }
    register_created = False
    try:
        with exclusive_writer_lock(lock_path):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_case_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError("another remote client is connected; refusing case load")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, args.carrier_case):
                raise FileNotFoundError(f"carrier case is missing: {args.carrier_case}")

            print("utl-probe: loading case only; no data file", flush=True)
            solver.settings.file.read_case(file_name=args.carrier_case)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_case_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )

            setup = solver.settings.setup
            dpm = setup.models.discrete_phase
            dpm_before = {
                "injection_names": list(dpm.injections.get_object_names()),
                "interaction": safe_get_state(
                    dpm.general_settings.interaction, "07n UTL DPM interaction"
                ),
                "unsteady_tracking": safe_get_state(
                    dpm.general_settings.unsteady_tracking,
                    "07n UTL DPM unsteady tracking",
                ),
            }
            if dpm_before["injection_names"]:
                raise RuntimeError(f"DPM injections are not empty: {dpm_before}")
            if not all_disabled(dpm_before["interaction"]) or not all_disabled(
                dpm_before["unsteady_tracking"]
            ):
                raise RuntimeError(f"DPM setting unexpectedly enabled: {dpm_before}")

            boundaries = setup.boundary_conditions
            boundary_membership = {
                "wall": list(boundaries.wall.get_object_names()),
                "pressure_outlet": list(boundaries.pressure_outlet.get_object_names()),
                "mass_flow_outlet": list(boundaries.mass_flow_outlet.get_object_names()),
                "mass_flow_inlet": list(boundaries.mass_flow_inlet.get_object_names()),
            }
            if "brineoutlet" not in boundary_membership["wall"]:
                raise RuntimeError(
                    f"carrier brine outlet is not closed as a wall: {boundary_membership}"
                )
            if "brineoutlet" in boundary_membership["pressure_outlet"]:
                raise RuntimeError("carrier brine outlet is still a pressure outlet")

            source_readback = {}
            fluid = setup.cell_zone_conditions.fluid["fluid"]
            for phase_name in ("mixture", "phase-1", "phase-2"):
                source_readback[phase_name] = safe_get_state(
                    fluid.phase[phase_name].sources,
                    f"07n UTL sources {phase_name}",
                )
                if not all_disabled(source_readback[phase_name]):
                    raise RuntimeError(
                        f"cell-zone source is enabled for {phase_name}: "
                        f"{source_readback[phase_name]}"
                    )

            payload["preinitialization_readback"] = {
                "general": safe_get_state(setup.general, "07n UTL general"),
                "models": safe_get_state(setup.models, "07n UTL models"),
                "solution_methods": safe_get_state(
                    solver.settings.solution.methods, "07n UTL solution methods"
                ),
                "boundary_membership": boundary_membership,
                "mass_flow_inlets": safe_get_state(
                    boundaries.mass_flow_inlet, "07n UTL mass-flow inlets"
                ),
                "steam_pressure_outlet": safe_get_state(
                    boundaries.pressure_outlet["steamoutlet"],
                    "07n UTL steam outlet",
                ),
                "brine_wall": safe_get_state(
                    boundaries.wall["brineoutlet"], "07n UTL brine wall"
                ),
                "dpm": dpm_before,
                "cell_zone_sources": source_readback,
            }

            print("utl-probe: fresh Hybrid Initialization", flush=True)
            sweep.maybe_initialize(solver, "hybrid")
            dpm_after = {
                "injection_names": list(
                    setup.models.discrete_phase.injections.get_object_names()
                ),
                "interaction": safe_get_state(
                    setup.models.discrete_phase.general_settings.interaction,
                    "07n UTL DPM interaction after initialization",
                ),
                "unsteady_tracking": safe_get_state(
                    setup.models.discrete_phase.general_settings.unsteady_tracking,
                    "07n UTL DPM unsteady tracking after initialization",
                ),
            }
            if (
                dpm_after["injection_names"]
                or not all_disabled(dpm_after["interaction"])
                or not all_disabled(dpm_after["unsteady_tracking"])
            ):
                raise RuntimeError(f"DPM gate failed after initialization: {dpm_after}")
            payload["postinitialization_dpm_readback"] = dpm_after

            registers = solver.settings.solution.cell_registers
            if args.register_name in registers.get_object_names():
                raise FileExistsError(
                    f"refusing to replace existing register: {args.register_name}"
                )
            solver.tui.mesh.adapt.cell_registers.add(
                args.register_name,
                "type",
                "hexahedron",
                "inside?",
                "yes",
                "max-point",
                *args.maximum,
                "min-point",
                *args.minimum,
            )
            register_created = True
            registers[
                args.register_name
            ].type.hexahedron.create_volume_surface.set_state(True)
            register_readback = registers[args.register_name].get_state()
            reports = solver.settings.results.report.volume_integrals
            payload["register"] = {
                "name": args.register_name,
                "minimum_m": list(args.minimum),
                "maximum_m": list(args.maximum),
                "settings_readback": register_readback,
                "reports": {
                    "volume": capture_report(
                        lambda: reports.volume(
                            cell_zones=[],
                            volumes=[args.register_name],
                            write_to_file=False,
                        )
                    ),
                    "minimum_y_coordinate": capture_report(
                        lambda: reports.minimum(
                            cell_zones=[],
                            volumes=[args.register_name],
                            cell_function="y-coordinate",
                            write_to_file=False,
                        )
                    ),
                    "maximum_y_coordinate": capture_report(
                        lambda: reports.maximum(
                            cell_zones=[],
                            volumes=[args.register_name],
                            cell_function="y-coordinate",
                            write_to_file=False,
                        )
                    ),
                },
            }
            registers.delete(name_list=[args.register_name])
            register_created = False
            payload["register"]["deleted_after_probe"] = (
                args.register_name not in registers.get_object_names()
            )
            payload["status"] = "accepted"
            payload["classification"] = "accepted diagnostic"
            payload["completed_epoch"] = time.time()
            write_new_json(output_path, payload)
            print(f"utl_probe_manifest: {output_path}", flush=True)
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
        if not output_path.exists():
            write_new_json(output_path, payload)
        raise
    finally:
        if register_created:
            try:
                solver.settings.solution.cell_registers.delete(
                    name_list=[args.register_name]
                )
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

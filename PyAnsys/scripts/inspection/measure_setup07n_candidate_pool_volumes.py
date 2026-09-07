#!/usr/bin/env python3
"""Measure exact patched pool volumes for Stage-0 setup-07n candidates.

Each candidate begins from a fresh Hybrid Initialization of the accepted 07l
case-only settings carrier.  The script patches phase-2 VOF in a uniquely
named level register and integrates the liquid VOF over the fluid zone.  It
does not read a data file, run a physical step, or save a case/data pair.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path, PureWindowsPath
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

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


EXPECTED_RANKS = 16
DOMAIN_VOLUME_M3 = 27.06309
LIQUID_DENSITY_KG_M3 = 881.2108764648438
POOL_MINIMUM_M = (-2.1, -1.5, -1.5)
POOL_MAXIMUM_XZ_M = (1.1, 1.1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--carrier-case", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--lock-file", required=True)
    parser.add_argument("--candidate-level", type=float, action="append", required=True)
    parser.add_argument("--register-prefix", required=True)
    parser.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return parser


def dpm_gate(dpm: Any) -> dict[str, Any]:
    result = {
        "injection_names": list(dpm.injections.get_object_names()),
        "interaction": safe_get_state(dpm.general_settings.interaction, "07n DPM interaction"),
        "unsteady_tracking": safe_get_state(
            dpm.general_settings.unsteady_tracking, "07n DPM unsteady tracking"
        ),
    }
    result["passed"] = (
        not result["injection_names"]
        and all_disabled(result["interaction"])
        and all_disabled(result["unsteady_tracking"])
    )
    return result


def source_gate(setup: Any) -> dict[str, Any]:
    fluid = setup.cell_zone_conditions.fluid["fluid"]
    states = {
        phase: safe_get_state(fluid.phase[phase].sources, f"07n sources {phase}")
        for phase in ("mixture", "phase-1", "phase-2")
    }
    return {"states": states, "passed": all(all_disabled(state) for state in states.values())}


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    output_path = Path(args.output_json).expanduser().resolve()
    lock_path = Path(args.lock_file).expanduser().resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite pool-volume evidence: {output_path}")
    if len(set(args.candidate_level)) != len(args.candidate_level):
        raise ValueError("candidate levels must be unique")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": output_path.stem,
        "status": "running",
        "classification": "diagnostic / unresolved",
        "settings_carrier_case": args.carrier_case,
        "data_files_read": [],
        "physical_steps_run": 0,
        "case_data_outputs_written": [],
        "candidate_basis": (
            "resolved crown plus two/four median crown-touching boundary-face "
            "vertical heights; boundary-face proxy pending volume-cell-height proof"
        ),
        "started_epoch": time.time(),
    }
    active_register = ""
    try:
        with exclusive_writer_lock(lock_path):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_case_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError("another remote client is connected; refusing case load")
            payload["fluent_version"] = str(solver.get_fluent_version())
            payload["health_status"] = str(solver.health_check.status())
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, args.carrier_case):
                raise FileNotFoundError(f"carrier case is missing: {args.carrier_case}")

            print("pool-volume: loading accepted case only; no data file", flush=True)
            solver.settings.file.read_case(file_name=args.carrier_case)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_case_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )
            setup = solver.settings.setup
            dpm_before = dpm_gate(setup.models.discrete_phase)
            sources_before = source_gate(setup)
            boundaries = setup.boundary_conditions
            boundary_gate = {
                "wall": list(boundaries.wall.get_object_names()),
                "pressure_outlet": list(boundaries.pressure_outlet.get_object_names()),
                "mass_flow_outlet": list(boundaries.mass_flow_outlet.get_object_names()),
            }
            if not dpm_before["passed"]:
                raise RuntimeError(f"DPM preinitialization gate failed: {dpm_before}")
            if not sources_before["passed"]:
                raise RuntimeError(f"source preinitialization gate failed: {sources_before}")
            if "brineoutlet" not in boundary_gate["wall"]:
                raise RuntimeError(f"brine outlet is not a wall: {boundary_gate}")
            payload["preinitialization_gates"] = {
                "dpm": dpm_before,
                "sources": sources_before,
                "boundary_membership": boundary_gate,
                "methods": safe_get_state(
                    solver.settings.solution.methods, "07n pool-volume methods"
                ),
                "models": safe_get_state(setup.models, "07n pool-volume models"),
            }

            remote_dir = str(PureWindowsPath(args.carrier_case).parent)
            registers = solver.settings.solution.cell_registers
            patch = solver.settings.solution.initialization.patch.calculate_patch
            candidates = []
            for index, level_y in enumerate(args.candidate_level, start=1):
                print(f"pool-volume: fresh initialization candidate={index}", flush=True)
                sweep.maybe_initialize(solver, "hybrid")
                dpm_after_init = dpm_gate(setup.models.discrete_phase)
                if not dpm_after_init["passed"]:
                    raise RuntimeError(
                        f"DPM gate failed after candidate {index} initialization: "
                        f"{dpm_after_init}"
                    )
                active_register = f"{args.register_prefix}_{index}"
                if active_register in registers.get_object_names():
                    raise FileExistsError(
                        f"refusing to replace existing register: {active_register}"
                    )
                solver.tui.mesh.adapt.cell_registers.add(
                    active_register,
                    "type",
                    "hexahedron",
                    "inside?",
                    "yes",
                    "max-point",
                    POOL_MAXIMUM_XZ_M[0],
                    level_y,
                    POOL_MAXIMUM_XZ_M[1],
                    "min-point",
                    *POOL_MINIMUM_M,
                )
                register_state = registers[active_register].get_state()
                before = mesh_study.volume_scalar(
                    solver,
                    remote_dir,
                    f"{args.register_prefix}_{index}_vf_before",
                    "phase-2-vof",
                )
                patch(
                    domain="phase-2",
                    cell_zones=[],
                    registers=[active_register],
                    variable="mp",
                    reference_frame="Relative to Cell Zone",
                    use_custom_field_function=False,
                    value=1.0,
                )
                after = mesh_study.volume_scalar(
                    solver,
                    remote_dir,
                    f"{args.register_prefix}_{index}_vf_after",
                    "phase-2-vof",
                )
                if not (math.isfinite(after) and after > before and 0.0 < after < 1.0):
                    raise RuntimeError(
                        f"candidate {index} patch failed: before={before} after={after}"
                    )
                liquid_volume = after * DOMAIN_VOLUME_M3
                candidates.append(
                    {
                        "index": index,
                        "target_level_y_m": level_y,
                        "register": active_register,
                        "register_state": register_state,
                        "domain_volume_average_liquid_vf_before": before,
                        "domain_volume_average_liquid_vf_after": after,
                        "liquid_volume_m3": liquid_volume,
                        "liquid_inventory_kg": liquid_volume * LIQUID_DENSITY_KG_M3,
                        "dpm_after_initialization": dpm_after_init,
                    }
                )
                registers.delete(name_list=[active_register])
                if active_register in registers.get_object_names():
                    raise RuntimeError(f"temporary register did not delete: {active_register}")
                active_register = ""

            payload["candidates"] = candidates
            payload["postmeasurement_gates"] = {
                "dpm": dpm_gate(setup.models.discrete_phase),
                "sources": source_gate(setup),
            }
            payload["status"] = "accepted"
            payload["classification"] = "accepted diagnostic"
            payload["limitation"] = (
                "exact patched mesh volumes, but candidate elevations still use a "
                "boundary-face-height proxy; no relaxation or constant-level claim"
            )
            payload["completed_epoch"] = time.time()
            write_new_json(output_path, payload)
            print(f"pool_volume_manifest: {output_path}", flush=True)
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
        if active_register:
            try:
                solver.settings.solution.cell_registers.delete(
                    name_list=[active_register]
                )
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

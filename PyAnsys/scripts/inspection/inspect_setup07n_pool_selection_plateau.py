#!/usr/bin/env python3
"""Bracket the exact cell-centroid selection plateau for the setup-07n pool.

This bounded diagnostic cold-loads the accepted setup-07l case *without data*,
performs one fresh Hybrid Initialization, and finds the interval of y-thresholds
that all select the same 98,473 whole cells as the successful lower face-proxy
startup pilot.  Each temporary register is patched to liquid only to obtain
Fluent's exact marked-cell count, then patched back to vapor and deleted.  It
does not iterate or write Fluent case/data files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path, PureWindowsPath
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
)
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = "brine620k_07n_stage0_pool_selection_plateau_attempt4_20260822"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_CARRIER_CASE = (
    REMOTE_ROOT + r"\brine620k_07l_hydrostatic_rest_v1_checkpoint_step10.cas.h5"
)
EXPECTED_CARRIER_SHA256 = (
    "ae1f7006f5170d0e9aa05dcd345bf5bb8ceac927abbd61c80b4e7d0484414e2a"
)
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
TARGET_Y_M = 0.016416369820944965
TARGET_MARKED_CELLS = 98_473
POOL_MINIMUM_M = (-2.1, -1.5, -1.5)
POOL_MAXIMUM_XZ_M = (1.1, 1.1)
INITIAL_SEARCH_STEP_M = 1.0e-4
BRACKET_TOLERANCE_M = 1.0e-10
MAX_SEARCH_DISTANCE_M = 0.02

LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / "brine620k_07n_stage0_geometry_v1"
MANIFEST_PATH = LOCAL_ROOT / f"{RUN_LABEL}.json"
TRANSCRIPT_PATH = LOCAL_ROOT / f"{RUN_LABEL}.trn"
GLOBAL_WRITER_LOCK = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server1_writer.lock"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def remote_join(name: str) -> str:
    return str(PureWindowsPath(REMOTE_ROOT) / name)


def write_manifest(payload: dict[str, Any], *, create: bool = False) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, indent=2, default=str) + "\n"
    if create:
        with MANIFEST_PATH.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
        return
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(rendered, encoding="utf-8")
    os.replace(temporary, MANIFEST_PATH)


def local_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    if MANIFEST_PATH.exists() or TRANSCRIPT_PATH.exists():
        raise FileExistsError(f"refusing to overwrite local evidence for {RUN_LABEL}")

    transcript_remote = remote_join(f"{RUN_LABEL}.trn")
    hash_scratch = remote_join(f"_{RUN_LABEL}_carrier_sha256.txt")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": RUN_LABEL,
        "status": "running",
        "classification": "diagnostic / unresolved",
        "server_id": args.server_id,
        "settings_carrier_case": REMOTE_CARRIER_CASE,
        "expected_carrier_sha256": EXPECTED_CARRIER_SHA256,
        "data_files_read": [],
        "physical_steps_run": 0,
        "initializations": 0,
        "patches": 0,
        "case_data_outputs_written": [],
        "target_threshold_y_m": TARGET_Y_M,
        "target_marked_cells": TARGET_MARKED_CELLS,
        "selection_box_minimum_m": list(POOL_MINIMUM_M),
        "selection_box_maximum_xz_m": list(POOL_MAXIMUM_XZ_M),
        "selection_rule": "whole cells whose centroids lie inside the hexahedral register",
        "started_epoch": time.time(),
    }
    write_manifest(payload, create=True)

    solver = None
    transcript_started = False
    client_stream_restarted = False
    active_register = ""
    query_index = 0
    queries: list[dict[str, Any]] = []
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_case_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError("another remote client is connected; refusing case load")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(f"unexpected Fluent version: {payload['fluent_version']}")
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, REMOTE_CARRIER_CASE):
                raise FileNotFoundError(REMOTE_CARRIER_CASE)
            if remote_file_exists(solver, transcript_remote):
                raise FileExistsError(f"refusing to overwrite remote transcript: {transcript_remote}")
            if remote_file_exists(solver, hash_scratch):
                raise FileExistsError(f"refusing to overwrite remote hash scratch: {hash_scratch}")
            carrier_sha = mesh_study.remote_file_sha256(
                solver, REMOTE_CARRIER_CASE, hash_scratch
            )
            payload["carrier_case_sha256"] = carrier_sha
            payload["remote_hash_scratch"] = hash_scratch
            if carrier_sha != EXPECTED_CARRIER_SHA256:
                raise RuntimeError(
                    f"carrier checksum mismatch expected={EXPECTED_CARRIER_SHA256} actual={carrier_sha}"
                )

            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            solver.settings.file.start_transcript(file_name=transcript_remote)
            transcript_started = True
            print("selection-plateau: cold-loading accepted setup-07l case only", flush=True)
            solver.settings.file.read_case(file_name=REMOTE_CARRIER_CASE)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_case_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )
            payload["carrier_gates"] = pilot.complete_gate(solver)
            if not payload["carrier_gates"]["passed"]:
                raise RuntimeError(f"carrier gate failed: {payload['carrier_gates']}")

            # The rank parser above relies on the default stdout transcript.
            # Only after all load/readback gates pass do we redirect the live
            # stream to a unique local file for marked-cell query isolation.
            solver.transcript.stop()
            solver.transcript.start(
                file_name=str(TRANSCRIPT_PATH), write_to_stdout=True
            )
            client_stream_restarted = True

            sweep.maybe_initialize(solver, "hybrid")
            payload["initializations"] = 1
            payload["postinitialization_gates"] = pilot.complete_gate(solver)
            if not payload["postinitialization_gates"]["passed"]:
                raise RuntimeError(
                    "postinitialization carrier gate failed: "
                    f"{payload['postinitialization_gates']}"
                )

            registers = solver.settings.solution.cell_registers
            patch = solver.settings.solution.initialization.patch.calculate_patch

            def count_at(level_y: float, purpose: str) -> int:
                nonlocal active_register, query_index
                query_index += 1
                active_register = f"s07n_plateau_a1_{query_index:03d}"
                if active_register in registers.get_object_names():
                    raise FileExistsError(f"temporary register already exists: {active_register}")
                before_text = (
                    TRANSCRIPT_PATH.read_text(encoding="utf-8", errors="replace")
                    if TRANSCRIPT_PATH.exists()
                    else ""
                )
                before_count = len(re.findall(r"([\d,]+)\s+cells marked", before_text, re.I))
                patched = False
                try:
                    solver.tui.mesh.adapt.cell_registers.add(
                        active_register,
                        "type",
                        "hexahedron",
                        "inside?",
                        "yes",
                        "max-point",
                        POOL_MAXIMUM_XZ_M[0],
                        float(level_y),
                        POOL_MAXIMUM_XZ_M[1],
                        "min-point",
                        *POOL_MINIMUM_M,
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
                    patched = True
                    payload["patches"] += 1
                    time.sleep(0.15)
                    transcript_text = TRANSCRIPT_PATH.read_text(
                        encoding="utf-8", errors="replace"
                    )
                    marked = [
                        int(value.replace(",", ""))
                        for value in re.findall(
                            r"([\d,]+)\s+cells marked", transcript_text, re.I
                        )
                    ]
                    if len(marked) != before_count + 1:
                        raise RuntimeError(
                            "could not isolate exactly one marked-cell report: "
                            f"before={before_count} after={len(marked)}"
                        )
                    count = marked[-1]
                    queries.append(
                        {
                            "query_index": query_index,
                            "purpose": purpose,
                            "threshold_y_m": float(level_y),
                            "marked_cells": count,
                        }
                    )
                    payload["queries"] = queries
                    write_manifest(payload)
                    return count
                finally:
                    if patched:
                        patch(
                            domain="phase-2",
                            cell_zones=[],
                            registers=[active_register],
                            variable="mp",
                            reference_frame="Relative to Cell Zone",
                            use_custom_field_function=False,
                            value=0.0,
                        )
                        payload["patches"] += 1
                    if active_register in registers.get_object_names():
                        registers.delete(name_list=[active_register])
                    if active_register in registers.get_object_names():
                        raise RuntimeError(f"temporary register did not delete: {active_register}")
                    active_register = ""

            target_count = count_at(TARGET_Y_M, "target verification")
            if target_count != TARGET_MARKED_CELLS:
                raise RuntimeError(
                    f"target count mismatch expected={TARGET_MARKED_CELLS} actual={target_count}"
                )

            lower_different_y = TARGET_Y_M
            lower_different_count = target_count
            search_step = INITIAL_SEARCH_STEP_M
            while lower_different_count == target_count:
                lower_different_y = TARGET_Y_M - search_step
                if TARGET_Y_M - lower_different_y > MAX_SEARCH_DISTANCE_M:
                    raise RuntimeError("lower selection transition not found within search bound")
                lower_different_count = count_at(
                    lower_different_y, "lower outward search"
                )
                search_step *= 2.0

            upper_different_y = TARGET_Y_M
            upper_different_count = target_count
            search_step = INITIAL_SEARCH_STEP_M
            while upper_different_count == target_count:
                upper_different_y = TARGET_Y_M + search_step
                if upper_different_y - TARGET_Y_M > MAX_SEARCH_DISTANCE_M:
                    raise RuntimeError("upper selection transition not found within search bound")
                upper_different_count = count_at(
                    upper_different_y, "upper outward search"
                )
                search_step *= 2.0

            lower_low = lower_different_y
            lower_high = TARGET_Y_M
            while lower_high - lower_low > BRACKET_TOLERANCE_M:
                midpoint = 0.5 * (lower_low + lower_high)
                if count_at(midpoint, "lower transition bisection") == target_count:
                    lower_high = midpoint
                else:
                    lower_low = midpoint

            upper_low = TARGET_Y_M
            upper_high = upper_different_y
            while upper_high - upper_low > BRACKET_TOLERANCE_M:
                midpoint = 0.5 * (upper_low + upper_high)
                if count_at(midpoint, "upper transition bisection") == target_count:
                    upper_low = midpoint
                else:
                    upper_high = midpoint

            centered_y = 0.5 * (lower_high + upper_low)
            centered_count = count_at(centered_y, "centered invariant-threshold verification")
            if centered_count != target_count:
                raise RuntimeError(
                    f"centered threshold count mismatch expected={target_count} actual={centered_count}"
                )
            payload["selection_plateau"] = {
                "lower_transition_bracket_y_m": [lower_low, lower_high],
                "lower_outside_count": lower_different_count,
                "upper_transition_bracket_y_m": [upper_low, upper_high],
                "upper_outside_count": upper_different_count,
                "invariant_interval_inner_y_m": [lower_high, upper_low],
                "invariant_interval_inner_width_m": upper_low - lower_high,
                "recommended_centered_threshold_y_m": centered_y,
                "recommended_centered_threshold_marked_cells": centered_count,
                "bracket_tolerance_m": BRACKET_TOLERANCE_M,
            }
            payload["temporary_registers_remaining"] = list(registers.get_object_names())
            payload["final_gates"] = pilot.complete_gate(solver)
            if not payload["final_gates"]["passed"]:
                raise RuntimeError(f"final carrier gate failed: {payload['final_gates']}")
            payload["status"] = "accepted"
            payload["classification"] = "accepted mesh-selection diagnostic"
            payload["eligible_parent"] = False
            payload["physical_interpretation"] = (
                "The centered threshold exactly and reproducibly selects the demonstrated "
                "98,473-cell pool. It is a CFD-defined diagnostic level, not a measured "
                "plant water level and not a direct volume-cell vertex-height measurement."
            )
            payload["completed_epoch"] = time.time()
            write_manifest(payload)
            return 0
    except Exception as exc:
        payload.update(
            {
                "status": "unresolved",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "queries": queries,
                "completed_epoch": time.time(),
            }
        )
        write_manifest(payload)
        raise
    finally:
        if solver is not None and active_register:
            try:
                registers = solver.settings.solution.cell_registers
                if active_register in registers.get_object_names():
                    registers.delete(name_list=[active_register])
            except Exception:
                pass
        if solver is not None and transcript_started:
            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            try:
                transcript_text = sweep.remote_text_read_best_effort(
                    solver, transcript_remote
                )
                if transcript_text and not TRANSCRIPT_PATH.exists():
                    TRANSCRIPT_PATH.write_text(transcript_text, encoding="utf-8")
                if TRANSCRIPT_PATH.exists():
                    payload["local_transcript"] = {
                        "path": str(TRANSCRIPT_PATH),
                        "sha256": local_sha256(TRANSCRIPT_PATH),
                    }
                    write_manifest(payload)
            except Exception as transcript_exc:
                payload["transcript_copy_error"] = (
                    f"{type(transcript_exc).__name__}: {transcript_exc}"
                )
                write_manifest(payload)
        if solver is not None and client_stream_restarted:
            try:
                solver.transcript.stop()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

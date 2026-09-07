#!/usr/bin/env python3
"""Probe implicit-VOF formulation and numerical readback without iterating.

The probe cold-loads the checksum-bound setup-07n-a step-940 case/data pair,
proves the accepted explicit/PISO parent, changes only the VOF formulation to
implicit through the readable Settings API, and records the resulting Fluent
2024 R2 discretization contract.  It does not initialize, iterate, or write a
case/data file.  Its output is diagnostic evidence, never a continuation
parent.
"""

from __future__ import annotations

import argparse
import difflib
import json
import math
import os
import re
import sys
import time
from collections.abc import Mapping
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
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_setup07j_transient_vof_qualification as transient07j  # noqa: E402
import run_setup07n_a_closeddrain_pilot as pilot  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = (
    "brine620k_07n_a_closeddrain_implicitvof_zero_step_"
    "readback_attempt9_20260823"
)
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_SETTINGS_ROOT = r"C:\Users\qtra338\AppData\Local\Temp"
PARENT_STEM = (
    REMOTE_ROOT
    + r"\brine620k_07n_a_closeddrain_meshselected_dt256em6_"
    r"hold100_stage8_attempt1_20260823_additional_step100"
)
PARENT_CASE = PARENT_STEM + ".cas.h5"
PARENT_DATA = PARENT_STEM + ".dat.h5"
EXPECTED_PARENT_CASE_SHA256 = (
    "03383ac0e1674b7a2acd47fc65ca84033c907f960bc3a4ace912e4902ce6c7c9"
)
EXPECTED_PARENT_DATA_SHA256 = (
    "a5963dfada0754dd24685b699a65ac341d90b9ce0c3dda11879863eb9ff0772a"
)
EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
EXPECTED_TIME_STEP = 940
EXPECTED_FLOW_TIME_S = 0.2227100000000037
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
GLOBAL_WRITER_LOCK = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server1_writer.lock"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def remote_join(name: str) -> str:
    return str(PureWindowsPath(REMOTE_ROOT) / name)


def write_manifest(path: Path, payload: Mapping[str, Any], *, create: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, default=str) + "\n"
    if create:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text)
        return
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = remote_join(f"_{RUN_LABEL}_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def setting_value(setting: Any) -> Any:
    """Read a scalar setting through its explicit state method."""

    return setting.get_state()


def allowed_values(setting: Any) -> list[str]:
    return [str(value) for value in setting.allowed_values()]


def numerical_snapshot(solver: Any) -> dict[str, Any]:
    multiphase = solver.settings.setup.models.multiphase
    methods = solver.settings.solution.methods
    discretization = methods.discretization_scheme
    result = {
        "multiphase": safe_get_state(multiphase, "multiphase"),
        "pressure_velocity_coupling": setting_value(
            methods.p_v_coupling.flow_scheme
        ),
        "pressure_velocity_coupling_allowed_values": allowed_values(
            methods.p_v_coupling.flow_scheme
        ),
        "pressure_scheme": setting_value(discretization["pressure"]),
        "pressure_scheme_allowed_values": allowed_values(discretization["pressure"]),
        "volume_fraction_scheme": setting_value(discretization["mp"]),
        "volume_fraction_scheme_allowed_values": allowed_values(discretization["mp"]),
        "transient_formulation": setting_value(methods.transient_formulation),
        "warped_face_gradient_correction": safe_get_state(
            methods.warped_face_gradient_correction, "WFGC"
        ),
        "methods": safe_get_state(methods, "methods"),
        "transient_controls": safe_get_state(
            solver.settings.solution.run_calculation.transient_controls,
            "transient controls",
        ),
        "residual_equations": list(
            solver.settings.solution.monitor.residual.equations.get_object_names()
        ),
    }
    try:
        vof_parameters = multiphase.vof_parameters
        result["settings_api_vof_parameters"] = safe_get_state(
            vof_parameters, "VOF parameters"
        )
        result["settings_api_vof_formulation"] = setting_value(
            vof_parameters.vof_formulation
        )
        result["settings_api_vof_formulation_allowed_values"] = allowed_values(
            vof_parameters.vof_formulation
        )
    except Exception as exc:
        result["settings_api_vof_formulation_unavailable"] = (
            f"{type(exc).__name__}: {exc}"
        )
    try:
        scalar_fields = [
            str(value)
            for value in solver.fields.field_data.scalar_fields.allowed_values()
        ]
        result["courant_scalar_fields"] = [
            value for value in scalar_fields if "courant" in value.lower()
        ]
        result["scalar_field_inventory_method"] = (
            "solver.fields.field_data.scalar_fields.allowed_values"
        )
    except Exception as primary_exc:
        try:
            field_info = solver.fields.field_info.get_scalar_fields_info()
            scalar_fields = [str(value) for value in field_info]
            result["courant_scalar_fields"] = [
                value for value in scalar_fields if "courant" in value.lower()
            ]
            result["scalar_field_inventory_method"] = (
                "solver.fields.field_info.get_scalar_fields_info"
            )
        except Exception as fallback_exc:
            result["courant_scalar_fields"] = []
            result["scalar_field_inventory_error"] = {
                "primary": f"{type(primary_exc).__name__}: {primary_exc}",
                "fallback": f"{type(fallback_exc).__name__}: {fallback_exc}",
            }
    result["version_specific_readback_note"] = (
        "Fluent 2024 R2 does not expose vof_parameters in the generated Settings "
        "tree; the formulation is therefore verified with exact repeatable "
        "write-settings exports and the resulting numerical-method readback"
    )
    return result


def set_formulation(solver: Any, value: str, label: str) -> str:
    command = (
        solver.tui.define.models.multiphase.volume_fraction_parameters.formulation
    )
    return mesh_study.capture_fluent(
        label,
        lambda: mesh_study.call_and_drain(lambda: command(value)),
    )


def settings_snapshot(solver: Any, label: str) -> dict[str, Any]:
    """Write and retrieve a unique Fluent settings file for exact comparison."""

    remote_name = f"{RUN_LABEL}_{label}.set"
    remote_path = str(PureWindowsPath(REMOTE_SETTINGS_ROOT) / remote_name)
    local_path = LOCAL_ROOT / f"{label}.set"
    if remote_file_exists(solver, remote_path) or local_path.exists():
        raise FileExistsError(f"refusing to overwrite settings evidence: {label}")
    command_transcript = mesh_study.capture_fluent(
        f"07n_implicit_readback_write_settings_{label}",
        lambda: mesh_study.call_and_drain(
            lambda: solver.tui.file.write_settings(remote_path)
        ),
    )
    if not remote_file_exists(solver, remote_path):
        raise RuntimeError(f"Fluent did not create settings evidence: {remote_path}")
    text = sweep.remote_text_read_best_effort(solver, remote_path)
    if not text:
        raise RuntimeError(f"could not retrieve settings evidence: {remote_path}")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with local_path.open("x", encoding="utf-8") as stream:
        stream.write(text)
    result = {
        "remote": remote_hash(solver, remote_path, f"{label}_settings"),
        "local": str(local_path),
        "command_transcript": command_transcript,
        "text_length": len(text),
        "_text": text,
    }
    return result


def invariant_snapshot(solver: Any) -> dict[str, Any]:
    setup = solver.settings.setup
    return {
        "boundary": pilot.boundary_gate(solver),
        "dpm": pilot.dpm_gate(setup.models.discrete_phase),
        "sources": pilot.source_gate(setup),
        "ewf": pilot.ewf_gate(solver),
        "models": safe_get_state(setup.models, "models"),
        "operating_conditions": safe_get_state(
            setup.general.operating_conditions, "operating conditions"
        ),
    }


def invariant_gate(snapshot: Mapping[str, Any]) -> bool:
    return all(
        bool(snapshot[key].get("passed"))
        for key in ("boundary", "dpm", "sources", "ewf")
    )


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=True)
    manifest_path = LOCAL_ROOT / "readback_manifest.json"
    transcript_path = LOCAL_ROOT / "readback_transcript.trn"
    local_lock_path = LOCAL_ROOT / "readback_writer.lock"
    transcript_remote = remote_join(f"{RUN_LABEL}_readback.trn")
    if manifest_path.exists():
        raise FileExistsError(f"refusing to overwrite probe attempt: {manifest_path}")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "study_id": STUDY_ID,
        "run_label": RUN_LABEL,
        "server_id": args.server_id,
        "status": "running",
        "classification": "diagnostic / unresolved zero-step formulation probe",
        "eligible_parent": False,
        "one_factor_change": "VOF formulation explicit -> implicit",
        "unchanged_contract": (
            "step-940 field; zero feed; brine wall; steam pressure outlet; PISO; "
            "RNG k-epsilon; Energy off; DPM zero/off; EWF off; no sources/sinks"
        ),
        "parent": {
            "case": PARENT_CASE,
            "case_expected_sha256": EXPECTED_PARENT_CASE_SHA256,
            "data": PARENT_DATA,
            "data_expected_sha256": EXPECTED_PARENT_DATA_SHA256,
            "eligibility_scope": "closed-pool diagnostic comparisons only",
        },
        "physical_steps_run": 0,
        "initializations_run": 0,
        "case_data_outputs_written": [],
        "fluent_auxiliary_outputs_written": [],
        "started_epoch": time.time(),
        "controller_pid": os.getpid(),
    }
    write_manifest(manifest_path, payload, create=True)
    solver: Any | None = None
    transcript_started = False
    try:
        with exclusive_writer_lock(GLOBAL_WRITER_LOCK), exclusive_writer_lock(
            local_lock_path
        ):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_parent_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive ownership unresolved: {clients!r}")
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
                raise FileNotFoundError("step-940 parent pair is incomplete")
            if remote_file_exists(solver, transcript_remote):
                raise FileExistsError(
                    f"refusing to overwrite remote transcript: {transcript_remote}"
                )
            case_hash = remote_hash(solver, PARENT_CASE, "parent_case")
            data_hash = remote_hash(solver, PARENT_DATA, "parent_data")
            payload["parent_readback"] = {"case": case_hash, "data": data_hash}
            if case_hash["sha256"] != EXPECTED_PARENT_CASE_SHA256:
                raise RuntimeError("parent case checksum mismatch")
            if data_hash["sha256"] != EXPECTED_PARENT_DATA_SHA256:
                raise RuntimeError("parent data checksum mismatch")

            solver.settings.file.read_case(file_name=PARENT_CASE)
            solver.settings.file.read_data(file_name=PARENT_DATA)
            time.sleep(2.0)
            payload["live_parallel_runtime_after_parent_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )
            payload["parent_complete_gate"] = pilot.complete_gate(solver)
            if not payload["parent_complete_gate"]["passed"]:
                raise RuntimeError("accepted explicit parent settings gate failed")
            parent_clock = transient07j.runtime_clock(solver)
            payload["clock_before"] = parent_clock
            if int(parent_clock["time_step"]) != EXPECTED_TIME_STEP or not math.isclose(
                float(parent_clock["flow_time_s"]),
                EXPECTED_FLOW_TIME_S,
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                raise RuntimeError(f"parent clock mismatch: {parent_clock}")

            try:
                solver.settings.file.stop_transcript()
            except Exception:
                pass
            solver.settings.file.start_transcript(file_name=transcript_remote)
            transcript_started = True

            before_numerics = numerical_snapshot(solver)
            before_invariants = invariant_snapshot(solver)
            explicit_parent_settings = settings_snapshot(solver, "explicit_parent")
            payload["before"] = {
                "numerics": before_numerics,
                "invariants": before_invariants,
                "settings": {
                    key: value
                    for key, value in explicit_parent_settings.items()
                    if key != "_text"
                },
            }
            if not invariant_gate(before_invariants):
                raise RuntimeError("pre-change invariant gate failed")

            payload["formulation_command_transcripts"] = {}
            payload["formulation_command_transcripts"]["implicit_a"] = set_formulation(
                solver, "implicit", "07n_implicit_readback_set_implicit_a"
            )
            implicit_a = numerical_snapshot(solver)
            implicit_a_clock = transient07j.runtime_clock(solver)
            implicit_a_settings = settings_snapshot(solver, "implicit_a")
            payload["formulation_command_transcripts"]["explicit_restore"] = (
                set_formulation(
                    solver, "explicit", "07n_implicit_readback_set_explicit_restore"
                )
            )
            explicit_restore = numerical_snapshot(solver)
            explicit_restore_clock = transient07j.runtime_clock(solver)
            explicit_restore_settings = settings_snapshot(
                solver, "explicit_restore"
            )
            payload["formulation_command_transcripts"]["implicit_b"] = set_formulation(
                solver, "implicit", "07n_implicit_readback_set_implicit_b"
            )
            after_numerics = numerical_snapshot(solver)
            after_invariants = invariant_snapshot(solver)
            after_clock = transient07j.runtime_clock(solver)
            implicit_b_settings = settings_snapshot(solver, "implicit_b")
            payload["after"] = {
                "numerics": after_numerics,
                "invariants": after_invariants,
            }
            payload["toggle_validation"] = {
                "explicit_parent": before_numerics,
                "implicit_a": implicit_a,
                "implicit_a_clock": implicit_a_clock,
                "implicit_a_settings": {
                    key: value
                    for key, value in implicit_a_settings.items()
                    if key != "_text"
                },
                "explicit_restore": explicit_restore,
                "explicit_restore_clock": explicit_restore_clock,
                "explicit_restore_settings": {
                    key: value
                    for key, value in explicit_restore_settings.items()
                    if key != "_text"
                },
                "implicit_b": after_numerics,
                "implicit_b_clock": after_clock,
                "implicit_b_settings": {
                    key: value
                    for key, value in implicit_b_settings.items()
                    if key != "_text"
                },
            }
            payload["clock_after"] = after_clock

            failures: list[str] = []
            explicit_text = explicit_parent_settings["_text"]
            implicit_a_text = implicit_a_settings["_text"]
            restored_text = explicit_restore_settings["_text"]
            implicit_b_text = implicit_b_settings["_text"]
            settings_diff = "\n".join(
                difflib.unified_diff(
                    explicit_text.splitlines(),
                    implicit_a_text.splitlines(),
                    fromfile="explicit_parent.set",
                    tofile="implicit_a.set",
                    lineterm="",
                )
            )
            diff_path = LOCAL_ROOT / "explicit_to_implicit_settings.diff"
            with diff_path.open("x", encoding="utf-8") as stream:
                stream.write(settings_diff + ("\n" if settings_diff else ""))
            payload["settings_comparison"] = {
                "explicit_to_implicit_changed": explicit_text != implicit_a_text,
                "explicit_restore_exact_match": restored_text == explicit_text,
                "implicit_repeat_exact_match": implicit_b_text == implicit_a_text,
                "implicit_marker": "(mp/scheme-type 0)",
                "explicit_parent_has_implicit_marker": bool(
                    re.search(r"^\(mp/scheme-type\s+0\)$", explicit_text, re.MULTILINE)
                ),
                "implicit_a_has_implicit_marker": bool(
                    re.search(r"^\(mp/scheme-type\s+0\)$", implicit_a_text, re.MULTILINE)
                ),
                "explicit_restore_has_implicit_marker": bool(
                    re.search(r"^\(mp/scheme-type\s+0\)$", restored_text, re.MULTILINE)
                ),
                "implicit_b_has_implicit_marker": bool(
                    re.search(r"^\(mp/scheme-type\s+0\)$", implicit_b_text, re.MULTILINE)
                ),
                "diff_local": str(diff_path),
                "diff_line_count": len(settings_diff.splitlines()),
                "diff_excerpt": settings_diff.splitlines()[:120],
            }
            if explicit_text == implicit_a_text:
                failures.append("settings export did not change after implicit command")
            if implicit_b_text != implicit_a_text:
                failures.append("implicit settings export was not exactly repeatable")
            if payload["settings_comparison"]["explicit_parent_has_implicit_marker"]:
                failures.append("accepted explicit parent contains implicit formulation marker")
            if not payload["settings_comparison"]["implicit_a_has_implicit_marker"]:
                failures.append("first implicit snapshot lacks formulation marker")
            if payload["settings_comparison"]["explicit_restore_has_implicit_marker"]:
                failures.append("explicit restore retained implicit formulation marker")
            if not payload["settings_comparison"]["implicit_b_has_implicit_marker"]:
                failures.append("second implicit snapshot lacks formulation marker")
            if (
                after_numerics["volume_fraction_scheme"]
                != implicit_a["volume_fraction_scheme"]
            ):
                failures.append("implicit VOF discretization was not repeatable")
            if not invariant_gate(after_invariants):
                failures.append("post-change boundary/DPM/source/EWF gate failed")
            if after_numerics["pressure_velocity_coupling"] != "PISO":
                failures.append("PISO did not remain selected")
            if after_numerics["pressure_scheme"] != "presto!":
                failures.append("PRESTO pressure did not remain selected")
            if after_numerics["transient_formulation"] != "unsteady-1st-order":
                failures.append("first-order transient formulation changed")
            mp_scheme = str(after_numerics["volume_fraction_scheme"])
            if mp_scheme not in after_numerics["volume_fraction_scheme_allowed_values"]:
                failures.append(
                    f"active VOF scheme {mp_scheme!r} is not in its allowed values"
                )
            if after_clock != parent_clock:
                failures.append(
                    f"zero-step clock changed: before={parent_clock} after={after_clock}"
                )
            if implicit_a_clock != parent_clock or explicit_restore_clock != parent_clock:
                failures.append("zero-step clock changed during formulation toggle validation")
            # Restore the exact accepted parent in memory before disconnecting.  The
            # probe writes no case/data and no downstream task may use its toggled
            # in-memory state as a parent.
            solver.settings.file.read_case(file_name=PARENT_CASE)
            solver.settings.file.read_data(file_name=PARENT_DATA)
            time.sleep(2.0)
            payload["restored_parent_gate"] = pilot.complete_gate(solver)
            payload["restored_parent_clock"] = transient07j.runtime_clock(solver)
            if not payload["restored_parent_gate"]["passed"]:
                raise RuntimeError("cold-reloaded parent did not restore the explicit gate")
            if payload["restored_parent_clock"] != parent_clock:
                raise RuntimeError("cold-reloaded parent clock mismatch")
            if failures:
                raise RuntimeError("; ".join(failures))

            payload.update(
                {
                    "status": "accepted",
                    "classification": "accepted diagnostic / zero-step implicit-VOF readback",
                    "supported_implicit_piso_baseline": True,
                    "iteration_authorized_by_this_probe": False,
                    "formulation_readback_method": (
                        "repeatable exact Fluent write-settings transition plus "
                        "post-change numerical Settings readback"
                    ),
                    "fluent_auxiliary_outputs_written": [
                        explicit_parent_settings["remote"]["path"],
                        implicit_a_settings["remote"]["path"],
                        explicit_restore_settings["remote"]["path"],
                        implicit_b_settings["remote"]["path"],
                        transcript_remote,
                    ],
                    "resulting_volume_fraction_scheme": mp_scheme,
                    "resulting_volume_fraction_scheme_allowed_values": after_numerics[
                        "volume_fraction_scheme_allowed_values"
                    ],
                    "completed_epoch": time.time(),
                }
            )
            write_manifest(manifest_path, payload)
            return 0
    except (Exception, KeyboardInterrupt) as exc:
        payload.update(
            {
                "status": "stopped_zero_step",
                "classification": "diagnostic / unresolved zero-step formulation probe",
                "supported_implicit_piso_baseline": False,
                "eligible_parent": False,
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        write_manifest(manifest_path, payload)
        raise
    finally:
        if solver is not None and transcript_started:
            try:
                solver.settings.file.stop_transcript()
                text = sweep.remote_text_read_best_effort(solver, transcript_remote)
                if text and not transcript_path.exists():
                    transcript_path.parent.mkdir(parents=True, exist_ok=True)
                    transcript_path.write_text(text, encoding="utf-8")
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())

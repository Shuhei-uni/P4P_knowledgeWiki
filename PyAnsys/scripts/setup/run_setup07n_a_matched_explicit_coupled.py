#!/usr/bin/env python3
"""Run the bounded explicit-VOF PISO-to-plain-Coupled setup-07n-a sensitivity.

The run cold-loads the checksum-bound accepted step-940 explicit/PISO parent,
changes only the pressure-velocity coupling to Fluent's plain ``Coupled``
scheme, and advances the same 0.00512 s window used by the other solver
comparisons.  It does not select ``Coupled with Volume Fractions`` and every
checkpoint remains diagnostic and ineligible for promotion.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_a_faceproxy_dt_extension as extension  # noqa: E402


RUN_LABEL = (
    "brine620k_07n_a_closeddrain_matchedwindow_explicit_coupled_"
    "dt256em6_steps20_attempt3_20260823"
)
PARENT_STEM = (
    extension.REMOTE_ROOT
    + r"\brine620k_07n_a_closeddrain_meshselected_dt256em6_"
    r"hold100_stage8_attempt1_20260823_additional_step100"
)
PARENT_CASE_SHA256 = (
    "03383ac0e1674b7a2acd47fc65ca84033c907f960bc3a4ace912e4902ce6c7c9"
)
PARENT_DATA_SHA256 = (
    "a5963dfada0754dd24685b699a65ac341d90b9ce0c3dda11879863eb9ff0772a"
)
TARGET_FLOW_SCHEME = "Coupled"
RUN_CLASSIFICATION = (
    "diagnostic / unresolved matched-window explicit-VOF plain-Coupled "
    "pressure-velocity sensitivity"
)
ONE_FACTOR_CHANGE = "pressure-velocity coupling PISO -> plain Coupled"
UNCHANGED_CONTRACT = (
    "exact accepted explicit step-940 field; zero feed; closed brine wall; "
    "steam pressure outlet; explicit VOF/Geo-Reconstruct; PRESTO/WFGC; "
    "first-order transient; RNG k-epsilon; Energy off; DPM zero/off; EWF "
    "off; no sources/sinks; no initialization"
)
ACCEPTANCE_LIMITATION = (
    "The endpoint is a closed-pool pressure-velocity solver diagnostic only. "
    "It does not validate constant-level drainage, plant pressure or level, "
    "or mesh/time-step independence, and it cannot parent another run."
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", choices=("1",), default="1")
    result.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return result


def coupled_settings_gate(solver: Any) -> dict[str, Any]:
    """Read back the complete explicit-VOF/plain-Coupled contract."""

    setup = solver.settings.setup
    methods = solver.settings.solution.methods
    method_state = {
        "pressure_velocity_coupling": methods.p_v_coupling.flow_scheme.get_state(),
        "pressure_velocity_coupling_allowed_values": list(
            methods.p_v_coupling.flow_scheme.allowed_values()
        ),
        "pressure_scheme": methods.discretization_scheme["pressure"].get_state(),
        "volume_fraction_scheme": methods.discretization_scheme["mp"].get_state(),
        "transient_formulation": methods.transient_formulation.get_state(),
        "warped_face_gradient_correction": (
            methods.warped_face_gradient_correction.get_state()
        ),
        "residual_equations": list(
            solver.settings.solution.monitor.residual.equations.get_object_names()
        ),
        "full_state": methods.get_state(),
    }
    method_state["passed"] = (
        method_state["pressure_velocity_coupling"] == TARGET_FLOW_SCHEME
        and TARGET_FLOW_SCHEME
        in method_state["pressure_velocity_coupling_allowed_values"]
        and method_state["pressure_scheme"] == "presto!"
        and method_state["volume_fraction_scheme"] == "geo-reconstruct"
        and method_state["transient_formulation"] == "unsteady-1st-order"
        and bool(method_state["warped_face_gradient_correction"].get("enable"))
        and method_state["full_state"]["p_v_coupling"].get("coupled_form") is False
    )
    result = {
        "boundary": extension.pilot.boundary_gate(solver),
        "methods": method_state,
        "dpm": extension.pilot.dpm_gate(setup.models.discrete_phase),
        "sources": extension.pilot.source_gate(setup),
        "ewf": extension.pilot.ewf_gate(solver),
        "models": setup.models.get_state(),
        "operating_conditions": setup.general.operating_conditions.get_state(),
    }
    result["passed"] = all(
        bool(result[key].get("passed"))
        for key in ("boundary", "methods", "dpm", "sources", "ewf")
    )
    return result


def apply_plain_coupled_change(solver: Any) -> dict[str, Any]:
    """Set and prove plain Coupled without altering explicit VOF."""

    methods = solver.settings.solution.methods
    flow_setting = methods.p_v_coupling.flow_scheme
    flow_before = str(flow_setting.get_state())
    flow_allowed = [str(value) for value in flow_setting.allowed_values()]
    if TARGET_FLOW_SCHEME not in flow_allowed:
        raise RuntimeError(
            "plain Coupled pressure-velocity scheme unavailable: "
            f"requested={TARGET_FLOW_SCHEME!r} allowed={flow_allowed}"
        )
    if flow_before != TARGET_FLOW_SCHEME:
        flow_setting.set_state(TARGET_FLOW_SCHEME)
    flow_after = str(flow_setting.get_state())
    if flow_after != TARGET_FLOW_SCHEME:
        raise RuntimeError(
            "pressure-velocity readback mismatch: "
            f"requested={TARGET_FLOW_SCHEME!r} actual={flow_after!r}"
        )

    volume_fraction_scheme = str(methods.discretization_scheme["mp"].get_state())
    transient_formulation = str(methods.transient_formulation.get_state())
    if volume_fraction_scheme != "geo-reconstruct":
        raise RuntimeError(
            "explicit VOF scheme changed unexpectedly: "
            f"actual={volume_fraction_scheme!r}"
        )
    if transient_formulation != "unsteady-1st-order":
        raise RuntimeError(
            "transient formulation changed unexpectedly: "
            f"actual={transient_formulation!r}"
        )

    remote_path = str(
        PureWindowsPath(extension.REMOTE_SETTINGS_ROOT)
        / f"{RUN_LABEL}_post_coupling_readback.set"
    )
    local_path = extension.LOCAL_ROOT / "post_coupling_readback.set"
    if extension.remote_file_exists(solver, remote_path) or local_path.exists():
        raise FileExistsError("refusing to overwrite coupling readback evidence")
    write_transcript = extension.mesh_study.capture_fluent(
        "07n_a_matched_explicit_coupled_write_post_coupling_settings",
        lambda: extension.mesh_study.call_and_drain(
            lambda: solver.tui.file.write_settings(remote_path)
        ),
    )
    text = extension.sweep.remote_text_read_best_effort(solver, remote_path)
    if not text:
        raise RuntimeError("could not retrieve post-coupling settings evidence")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with local_path.open("x", encoding="utf-8") as stream:
        stream.write(text)
    implicit_marker = bool(
        re.search(r"^\(mp/scheme-type\s+0\)$", text, re.MULTILINE)
    )
    if implicit_marker:
        raise RuntimeError("explicit branch unexpectedly contains implicit VOF marker")

    return {
        "requested": "explicit VOF with plain Coupled pressure-velocity scheme",
        "vof_formulation_changed": False,
        "pressure_velocity_coupling_before": flow_before,
        "pressure_velocity_coupling_requested": TARGET_FLOW_SCHEME,
        "pressure_velocity_coupling_after": flow_after,
        "pressure_velocity_coupling_allowed_values": flow_allowed,
        "volume_fraction_scheme_after": volume_fraction_scheme,
        "transient_formulation_after": transient_formulation,
        "settings_write_transcript": write_transcript,
        "settings_remote": extension.remote_hash(
            solver, remote_path, "post_coupling_settings"
        ),
        "settings_local": str(local_path),
        "implicit_settings_marker": implicit_marker,
        "explicit_formulation_evidence": (
            "checksum-bound explicit parent; no formulation setter called; "
            "Geo-Reconstruct retained; explicit-VOF Global Courant criterion "
            "required during marching"
        ),
    }


def main() -> int:
    args = parser().parse_args()
    extension.RUN_LABEL = RUN_LABEL
    extension.LOCAL_ROOT = (
        extension.PROJECT_ROOT / "output" / extension.STUDY_ID / RUN_LABEL
    )
    extension.PARENT_LABEL = Path(PARENT_STEM.replace("\\", "/")).name
    extension.PARENT_CASE = PARENT_STEM + ".cas.h5"
    extension.PARENT_DATA = PARENT_STEM + ".dat.h5"
    extension.EXPECTED_PARENT_CASE_SHA256 = PARENT_CASE_SHA256
    extension.EXPECTED_PARENT_DATA_SHA256 = PARENT_DATA_SHA256
    extension.INITIAL_TIME_STEP = 940
    extension.INITIAL_FLOW_TIME_S = 0.2227100000000037
    extension.TIME_STEP_SIZE_S = 2.56e-4
    extension.INNER_ITERATIONS = 20
    extension.ADDITIONAL_STEPS = 20
    extension.CHECKPOINT_ADDITIONAL_STEPS = {1, 5, 10, 20}
    extension.VOF_FORMULATION = "explicit"
    extension.EXPECTED_VOF_SCHEME = "geo-reconstruct"
    extension.EXPECTED_TRANSIENT_FORMULATION = "unsteady-1st-order"
    extension.COURANT_FIELD = None
    extension.ENDPOINT_ELIGIBILITY_ALLOWED = False
    extension.RUN_CLASSIFICATION = RUN_CLASSIFICATION
    extension.FINAL_CLASSIFICATION = RUN_CLASSIFICATION
    extension.ONE_FACTOR_CHANGE = ONE_FACTOR_CHANGE
    extension.UNCHANGED_CONTRACT = UNCHANGED_CONTRACT
    extension.PARENT_ELIGIBILITY_SCOPE = (
        "accepted explicit closed-pool diagnostic comparisons only"
    )
    extension.ACCEPTANCE_LIMITATION = ACCEPTANCE_LIMITATION
    extension.NEXT_ELIGIBILITY_SCOPE = "none; comparison/adjudication only"
    extension.SAVE_TAG = "07n_a_matched_explicit_coupled"
    extension.PRINT_LABEL = "07n-a explicit VOF/plain Coupled matched window"
    extension.active_settings_gate = coupled_settings_gate
    extension.apply_formulation_change = apply_plain_coupled_change

    sys.argv = [
        sys.argv[0],
        "--server-id",
        args.server_id,
        "--tcp-timeout-seconds",
        str(args.tcp_timeout_seconds),
    ]
    return extension.main()


if __name__ == "__main__":
    raise SystemExit(main())

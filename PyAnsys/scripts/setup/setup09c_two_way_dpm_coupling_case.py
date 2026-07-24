#!/usr/bin/env python3
"""Create setup 09c as a case-only two-way DPM derivative of the accepted 08b case.

This script intentionally:
- loads an existing `.cas.h5`;
- changes only the global DPM continuous-phase interaction controls;
- writes a new `.cas.h5`;
- does not initialize, iterate, or write `.dat.h5`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import remote_file_exists, safe_get_state, try_action  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402
from pyansys_fluent.setup_io import load_case_only, write_case_only  # noqa: E402


DEFAULT_SERVER_ID = "1"
DEFAULT_SOURCE_CASE = (
    r"C:\Users\syok443\P4P simulation\TwoPhaseInletV2(Purnanto).cas.h5"
)
DEFAULT_OUTPUT_CASE = (
    r"C:\Users\syok443\P4P simulation\scratch\TwoPhaseInletV2(Purnanto)-09c-two-way-dpm.cas.h5"
)
DEFAULT_SUMMARY_JSON = PROJECT_ROOT / "output" / "setup09c_two_way_dpm_coupling_summary.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Case-specific 09c Fluent build script. Load the accepted 08b Purnanto "
            "case, apply its explicit coupling steps, and write a case-only .cas.h5 artifact."
        )
    )
    parser.add_argument("--server-id", default=DEFAULT_SERVER_ID, help="Configured Fluent server id. Default: 3.")
    parser.add_argument("--source-case", default=DEFAULT_SOURCE_CASE, help="Remote 08b-style source .cas.h5 case.")
    parser.add_argument("--output-case", default=DEFAULT_OUTPUT_CASE, help="Remote output .cas.h5 path for setup 09c.")
    parser.add_argument(
        "--summary-json",
        default=str(DEFAULT_SUMMARY_JSON),
        help="Optional local JSON summary path for readback and inheritance details.",
    )
    parser.add_argument(
        "--iteration-interval",
        type=int,
        default=1,
        help="DPM source update iteration interval when two-way coupling is enabled. Default: 1.",
    )
    parser.add_argument(
        "--disable-update-sources-every-iteration",
        dest="update_sources_every_iteration",
        action="store_false",
        help="Leave source updates on the specified interval instead of every flow iteration.",
    )
    parser.set_defaults(update_sources_every_iteration=True)
    return parser


def _named_object_names(branch: Any) -> list[str]:
    for attr in ("get_object_names", "object_names", "list"):
        try:
            value = getattr(branch, attr)
            names = value() if callable(value) else value
            if isinstance(names, (list, tuple, set)):
                return sorted(str(name) for name in names)
        except Exception:
            pass
    return []


def _sum_injection_total_flow(dpm_state: dict[str, Any]) -> float:
    total = 0.0
    injections = dpm_state.get("injections", {})
    if not isinstance(injections, dict):
        return total
    for payload in injections.values():
        if not isinstance(payload, dict):
            continue
        try:
            total += float(payload["initial_values"]["mass_flow_rate"]["total_flow_rate"])
        except (KeyError, TypeError, ValueError):
            continue
    return total


def _extract_injection_surface_summary(dpm_state: dict[str, Any]) -> dict[str, list[str]]:
    summary: dict[str, list[str]] = {}
    injections = dpm_state.get("injections", {})
    if not isinstance(injections, dict):
        return summary
    for name, payload in injections.items():
        if not isinstance(payload, dict):
            continue
        surfaces = (
            payload.get("initial_values", {})
            .get("location", {})
            .get("injection_surfaces", [])
        )
        if isinstance(surfaces, str):
            summary[str(name)] = [surfaces]
        elif isinstance(surfaces, list):
            summary[str(name)] = [str(item) for item in surfaces]
    return summary


def main() -> int:
    args = build_parser().parse_args()
    solver = connect(server_id=args.server_id)

    print_header("Verify Source Case")
    if not remote_file_exists(solver, args.source_case):
        raise FileNotFoundError(f"Fluent cannot see source case: {args.source_case}")

    load_case_only(solver, args.source_case, label="Load 09c Source Case")

    print_header("Inspect Source DPM State")
    dpm = solver.settings.setup.models.discrete_phase
    interaction = dpm.general_settings.interaction
    injection_names = _named_object_names(dpm.injections)
    before_dpm = safe_get_state(dpm, "09c_source_dpm")
    before_interaction = safe_get_state(interaction, "09c_source_interaction")
    if not injection_names:
        raise RuntimeError("Source case has no active DPM injections; 09c requires an inherited DPM payload.")

    print_header("Apply 09c Two-Way DPM Interaction")
    if not try_action("set_dpm_interaction_enabled_true", lambda: setattr(interaction, "enabled", True)):
        raise RuntimeError("Could not enable DPM continuous-phase interaction")
    if not try_action(
        "set_dpm_update_sources_every_iteration",
        lambda: setattr(interaction, "update_sources_every_iteration", args.update_sources_every_iteration),
    ):
        raise RuntimeError("Could not set DPM source-update mode")
    if not try_action(
        "set_dpm_iteration_interval",
        lambda: setattr(interaction, "iteration_interval", args.iteration_interval),
    ):
        raise RuntimeError("Could not set DPM iteration interval")

    after_interaction = safe_get_state(interaction, "09c_interaction_after")
    after_dpm = safe_get_state(dpm, "09c_dpm_after")

    if not isinstance(after_interaction, dict) or not after_interaction.get("enabled", False):
        raise RuntimeError(f"Readback mismatch: expected enabled interaction, got {after_interaction}")
    if after_interaction.get("update_sources_every_iteration") != args.update_sources_every_iteration:
        raise RuntimeError(
            "Readback mismatch for update_sources_every_iteration: "
            f"expected {args.update_sources_every_iteration}, got {after_interaction}"
        )
    if int(after_interaction.get("iteration_interval", -1)) != args.iteration_interval:
        raise RuntimeError(
            f"Readback mismatch for iteration_interval: expected {args.iteration_interval}, got {after_interaction}"
        )

    write_case_only(solver, args.output_case, "setup09c_two_way_dpm_coupling")

    summary = {
        "setup_id": "09c",
        "server_id": str(args.server_id),
        "fluent_version": solver.get_fluent_version(),
        "source_case": args.source_case,
        "output_case": args.output_case,
        "branch_role": "two-way DPM coupling case-only derivative",
        "inheritance_basis": {
            "source_case_identity": "accepted 08b-style split-inlet carrier + existing DPM payload",
            "injection_count": len(injection_names),
            "injection_names": injection_names,
            "represented_total_mass_flow_kg_s": _sum_injection_total_flow(after_dpm if isinstance(after_dpm, dict) else {}),
            "injection_surfaces": _extract_injection_surface_summary(after_dpm if isinstance(after_dpm, dict) else {}),
        },
        "applied_change": {
            "interaction_enabled": True,
            "update_sources_every_iteration": args.update_sources_every_iteration,
            "iteration_interval": args.iteration_interval,
        },
        "before_interaction": before_interaction,
        "after_interaction": after_interaction,
        "before_dpm_state": before_dpm,
        "after_dpm_state": after_dpm,
        "notes": [
            "This script writes only a .cas.h5 artifact.",
            "No initialization, iteration, or .dat.h5 write is performed.",
            "The inherited injections remain bound to steaminlet; 09c changes only the DPM continuous-phase feedback controls.",
            "Eulerian Wall Film and re-entrainment remain out of scope for this case.",
        ],
    }

    if args.summary_json:
        summary_path = Path(args.summary_json).expanduser().resolve()
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
        print(f"summary_json: {summary_path}", flush=True)

    print("\nSetup 09c case-only build complete.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

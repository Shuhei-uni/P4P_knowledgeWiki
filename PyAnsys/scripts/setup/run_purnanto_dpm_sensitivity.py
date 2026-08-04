#!/usr/bin/env python3
"""Run DPM-only tracking sensitivity for a saved Purnanto enthalpy case."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pyansys_fluent.common import safe_get_state, try_action  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a DPM-only tracking sensitivity on a saved Purnanto case.")
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument("--case-filter", default="1600", help="Paper case selector. Default: 1600.")
    parser.add_argument(
        "--resume-case",
        default="",
        help="Remote case file. Defaults to the selected case final 1500-iteration case.",
    )
    parser.add_argument(
        "--resume-data",
        default="",
        help="Remote data file. Defaults to the selected case final 1500-iteration data.",
    )
    parser.add_argument(
        "--label",
        default="dpm_maxsteps_500000",
        help="Output label suffix.",
    )
    parser.add_argument(
        "--dpm-max-steps",
        type=int,
        default=500000,
        help="DPM max tracking steps for the sensitivity run.",
    )
    parser.add_argument(
        "--step-length-factor",
        type=float,
        default=0.0,
        help="Optional DPM step-length factor override. Use 0 to leave the saved value unchanged.",
    )
    parser.add_argument(
        "--harwell-csv",
        default=str(sweep.DEFAULT_HARWELL_CSV),
        help="Local Harwell injection CSV path.",
    )
    parser.add_argument(
        "--remote-output-dir",
        default=sweep.DEFAULT_REMOTE_OUTPUT_DIR,
        help="Remote Windows output folder visible to Fluent.",
    )
    parser.add_argument(
        "--local-output-dir",
        default=str(sweep.DEFAULT_LOCAL_OUTPUT_DIR),
        help="Local folder for parsed CSV/manifests and captured reports.",
    )
    parser.add_argument(
        "--dpm-velocity-mode",
        choices=("face-normal", "components"),
        default=sweep.DEFAULT_DPM_VELOCITY_MODE,
        help="Velocity mode metadata for result export.",
    )
    parser.add_argument(
        "--reapply-setup",
        action="store_true",
        help="Reapply inlet mass flows and DPM injection definitions before DPM tracking.",
    )
    parser.add_argument(
        "--save-case-data",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Save the case/data after the sensitivity run.",
    )
    return parser


def single_case_plan(case_filter: str, csv_path: Path) -> tuple[sweep.PaperCase, list[sweep.InjectionBin]]:
    groups = sweep.read_harwell_bins(csv_path)
    cases = sweep.selected_cases([case_filter])
    if len(cases) != 1:
        raise ValueError(f"--case-filter must select exactly one case, got {len(cases)}")
    case = cases[0]
    bins = groups[(case.csv_case, case.condition)]
    sweep.validate_case_bins(case, bins)
    return case, bins


def default_case_data_paths(case: sweep.PaperCase, remote_output_dir: str) -> tuple[str, str]:
    prefix = sweep.case_prefix(case)
    return (
        sweep.remote_join(remote_output_dir, f"{prefix}_1500.cas.h5"),
        sweep.remote_join(remote_output_dir, f"{prefix}_1500.dat.h5"),
    )


def load_case_data(solver: Any, case_file: str, data_file: str) -> None:
    print_header("Load Saved Case/Data")
    sweep.require_remote_input(solver, case_file, "resume case")
    sweep.require_remote_input(solver, data_file, "resume data")
    sweep.remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    if not sweep.try_action("read_resume_case", lambda: solver.settings.file.read_case(file_name=case_file)):
        raise RuntimeError(f"Could not read resume case: {case_file}")
    if not sweep.try_action("read_resume_data", lambda: solver.settings.file.read_data(file_name=data_file)):
        raise RuntimeError(f"Could not read resume data: {data_file}")


def apply_dpm_tracking_sensitivity(
    solver: Any,
    *,
    max_steps: int,
    step_length_factor: float,
) -> dict[str, Any]:
    print_header("Apply DPM Tracking Sensitivity")
    dpm = solver.settings.setup.models.discrete_phase
    before = safe_get_state(getattr(dpm, "tracking", None), "dpm.tracking")
    print("tracking_state_before:", json.dumps(before, indent=2, default=str))

    actions = {
        "set_dpm_max_num_steps": lambda: setattr(dpm.tracking, "max_num_steps", max_steps),
        "set_dpm_high_res_tracking_best_effort": lambda: setattr(dpm.numerics, "high_res_tracking", True),
        "set_dpm_interaction_off_best_effort": lambda: setattr(dpm.general_settings.interaction, "enabled", False),
        "set_dpm_sources_every_iteration_off_best_effort": lambda: setattr(
            dpm.general_settings.interaction,
            "update_sources_every_iteration",
            False,
        ),
    }
    if step_length_factor > 0:
        actions["set_dpm_step_length_factor"] = lambda: setattr(
            dpm.tracking.step_size_controls,
            "step_length_factor",
            step_length_factor,
        )
    action_results: dict[str, bool] = {}
    for label, action in actions.items():
        action_results[label] = try_action(label, action)

    after = safe_get_state(getattr(dpm, "tracking", None), "dpm.tracking")
    print("tracking_state_after:", json.dumps(after, indent=2, default=str))
    return {"before": before, "after": after, "actions": action_results}


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    case, bins = single_case_plan(args.case_filter, Path(args.harwell_csv).expanduser().resolve())
    prefix = f"{sweep.case_prefix(case)}_{sweep.slugify(args.label)}"
    local_output_dir = sweep.ensure_local_output_dir(args.local_output_dir)

    resume_case, resume_data = args.resume_case, args.resume_data
    if not resume_case and not resume_data:
        resume_case, resume_data = default_case_data_paths(case, args.remote_output_dir)
    if not (resume_case and resume_data):
        raise ValueError("--resume-case and --resume-data must be supplied together")

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    sweep.ensure_remote_directory_best_effort(solver, args.remote_output_dir)
    load_case_data(solver, resume_case, resume_data)
    sweep.require_current_case_shape(solver)

    inlet_readback = None
    injection_readbacks = None
    if args.reapply_setup:
        inlet_readback = sweep.set_inlet_phase_mass_flows(solver, case)
        injection_readbacks = sweep.set_dpm_injections(solver, bins, args.dpm_velocity_mode)
    else:
        print("setup_reapply: SKIPPED; using injections saved in case file")

    tracking = apply_dpm_tracking_sensitivity(
        solver,
        max_steps=args.dpm_max_steps,
        step_length_factor=args.step_length_factor,
    )

    report_text = sweep.run_dpm_reports(solver, args.remote_output_dir, prefix, bins)
    result_rows = sweep.parse_dpm_result_rows(case, bins, report_text, args.dpm_velocity_mode)
    iteration_count = sweep.read_iteration_count(solver)
    case_summary_row = sweep.parse_case_summary_row(case, bins, report_text, iteration_count or 0, result_rows)

    local_report = local_output_dir / f"{prefix}_dpm_report.txt"
    sweep.write_local_text(local_report, report_text)
    remote_report = sweep.remote_join(args.remote_output_dir, f"{prefix}_dpm_report.txt")
    sweep.remote_text_write_best_effort(solver, remote_report, report_text)

    local_case_csv = local_output_dir / f"{prefix}_injection_results.csv"
    sweep.write_local_csv(local_case_csv, result_rows, sweep.RESULT_FIELDS)
    remote_case_csv = sweep.remote_join(args.remote_output_dir, f"{prefix}_injection_results.csv")
    sweep.remote_text_write_best_effort(solver, remote_case_csv, sweep.rows_to_csv_text(result_rows, sweep.RESULT_FIELDS))

    local_summary_csv = local_output_dir / f"{prefix}_case_summary.csv"
    sweep.write_local_csv(local_summary_csv, [case_summary_row], sweep.CASE_SUMMARY_FIELDS)
    remote_summary_csv = sweep.remote_join(args.remote_output_dir, f"{prefix}_case_summary.csv")
    sweep.remote_text_write_best_effort(
        solver,
        remote_summary_csv,
        sweep.rows_to_csv_text([case_summary_row], sweep.CASE_SUMMARY_FIELDS),
    )

    remote_case = ""
    remote_data = ""
    if args.save_case_data:
        remote_case = sweep.remote_join(args.remote_output_dir, f"{prefix}.cas.h5")
        remote_data = sweep.remote_join(args.remote_output_dir, f"{prefix}.dat.h5")
        sweep.write_case_data_pair(solver, remote_case, remote_data, "dpm_sensitivity")

    manifest = {
        "case": case.csv_case,
        "condition": case.condition,
        "mode": "dpm_tracking_sensitivity",
        "source_case": resume_case,
        "source_data": resume_data,
        "dpm_max_steps": args.dpm_max_steps,
        "step_length_factor": args.step_length_factor if args.step_length_factor > 0 else "unchanged",
        "tracking": tracking,
        "remote_output_paths": {
            "case": remote_case,
            "data": remote_data,
            "dpm_report": remote_report,
            "injection_results": remote_case_csv,
            "case_summary": remote_summary_csv,
        },
        "local_output_paths": {
            "dpm_report": str(local_report),
            "injection_results": str(local_case_csv),
            "case_summary": str(local_summary_csv),
        },
        "iterations_completed": iteration_count,
        "dpm_velocity_mode": args.dpm_velocity_mode,
        "inlet_readback": inlet_readback,
        "injection_readback_names": sorted(injection_readbacks) if injection_readbacks else [],
        "case_summary": case_summary_row,
    }
    manifest_text = json.dumps(manifest, indent=2, default=str)
    local_manifest = local_output_dir / f"{prefix}_manifest.json"
    sweep.write_local_text(local_manifest, manifest_text)
    remote_manifest = sweep.remote_join(args.remote_output_dir, f"{prefix}_manifest.json")
    sweep.remote_text_write_best_effort(solver, remote_manifest, manifest_text)

    print_header("DPM Sensitivity Complete")
    print(f"local_case_summary: {local_summary_csv}")
    print(f"local_injection_results: {local_case_csv}")
    print(f"local_report: {local_report}")
    print(f"local_manifest: {local_manifest}")
    if remote_case:
        print(f"remote_case: {remote_case}")
        print(f"remote_data: {remote_data}")
    print(f"rows: {len(result_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Continue a Fluent case for one Purnanto condition.

By default this script connects to the live Fluent session and assumes the
previous run is still loaded.  You can also pass ``--resume-case`` and
``--resume-data`` to load a saved case/data pair before continuing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PureWindowsPath

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Continue the currently loaded Purnanto Fluent case.")
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument("--case-filter", default="1600", help="Paper case selector. Default: 1600.")
    parser.add_argument("--additional-iterations", type=int, default=100, help="Iterations to add.")
    parser.add_argument("--total-label", default="", help="Label for outputs, e.g. 200iter_continued.")
    parser.add_argument(
        "--verified-starting-iterations",
        type=int,
        default=None,
        help="Known completed iterations before continuing, from a controller log or trusted manifest.",
    )
    parser.add_argument(
        "--verified-completed-iterations",
        type=int,
        default=None,
        help="Known total completed iterations after this run, from a controller log or trusted manifest.",
    )
    parser.add_argument("--resume-case", default="", help="Optional remote case file to load before continuing.")
    parser.add_argument("--resume-data", default="", help="Optional remote data file to load before continuing.")
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
    parser.add_argument("--report-interval", type=int, default=25, help="Iteration chunk/progress interval.")
    parser.add_argument("--checkpoint-interval", type=int, default=0, help="Remote autosave interval. Use 0 to disable.")
    parser.add_argument(
        "--dpm-velocity-mode",
        choices=("face-normal", "components"),
        default=sweep.DEFAULT_DPM_VELOCITY_MODE,
        help="Velocity mode to reapply before continuing. Default: face-normal.",
    )
    parser.add_argument(
        "--gas-phase-material",
        default=sweep.DEFAULT_GAS_PHASE_MATERIAL,
        help="Required material readback for phase-1.",
    )
    parser.add_argument(
        "--liquid-phase-material",
        default=sweep.DEFAULT_LIQUID_PHASE_MATERIAL,
        help="Required material readback for phase-2.",
    )
    parser.add_argument(
        "--allow-coupled-dpm",
        action="store_true",
        help="Allow inherited DPM interaction with the continuous phase.",
    )
    parser.add_argument(
        "--no-reapply-setup",
        action="store_true",
        help="Do not reapply inlet mass flows or DPM injection definitions before continuing.",
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


def continuation_prefix(case: sweep.PaperCase, total_label: str) -> str:
    label = total_label.strip() or "continued"
    return f"{sweep.case_prefix(case)}_{sweep.slugify(label)}"


def validate_completion_label(args: argparse.Namespace) -> None:
    label = args.total_label.lower()
    if not any(token in label for token in ("1500", "final", "complete", "completed")):
        return
    if args.verified_completed_iterations is not None:
        if args.verified_starting_iterations is not None:
            expected = args.verified_starting_iterations + args.additional_iterations
            if args.verified_completed_iterations != expected:
                raise ValueError(
                    "--verified-completed-iterations must equal --verified-starting-iterations plus "
                    f"--additional-iterations ({expected})"
                )
        return
    raise ValueError(
        "--total-label implies a completed solve, but --verified-completed-iterations was not supplied. "
        "Use an unverified label or provide a trusted completed-iteration count."
    )


def read_resume_case_data(solver, case_file: str, data_file: str) -> None:
    print_header("Load Resume Case/Data")
    sweep.require_remote_input(solver, case_file, "resume case")
    sweep.require_remote_input(solver, data_file, "resume data")
    sweep.remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    if not sweep.try_action("read_resume_case", lambda: solver.settings.file.read_case(file_name=case_file)):
        raise RuntimeError(f"Could not read resume case: {case_file}")
    if not sweep.try_action("read_resume_data", lambda: solver.settings.file.read_data(file_name=data_file)):
        raise RuntimeError(f"Could not read resume data: {data_file}")


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()
    validate_completion_label(args)

    case, bins = single_case_plan(args.case_filter, Path(args.harwell_csv).expanduser().resolve())
    local_output_dir = sweep.ensure_local_output_dir(args.local_output_dir)
    prefix = continuation_prefix(case, args.total_label)

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    sweep.ensure_remote_directory_best_effort(solver, args.remote_output_dir)

    print_header(f"Continue {case.csv_case} / {case.condition}")
    if args.resume_case or args.resume_data:
        if not (args.resume_case and args.resume_data):
            raise ValueError("--resume-case and --resume-data must be supplied together")
        read_resume_case_data(solver, args.resume_case, args.resume_data)

    reported_start_iterations = sweep.read_iteration_count(solver)
    print(f"reported_starting_number_of_iterations: {reported_start_iterations}")
    print(
        "reported_number_of_iterations_note: this is Fluent's current iteration/run setting; "
        "it is not proof that a disconnected controller completed that many iterations"
    )
    sweep.require_current_case_shape(solver)
    physics_readback = sweep.require_case_physics(
        solver,
        gas_phase_material=args.gas_phase_material,
        liquid_phase_material=args.liquid_phase_material,
        allow_coupled_dpm=args.allow_coupled_dpm,
    )
    autosave_state = sweep.disable_inherited_fluent_autosave(
        solver,
        args.remote_output_dir,
        prefix,
    )

    inlet_readback = None
    injection_readbacks = None
    if args.no_reapply_setup:
        print("setup_reapply: SKIPPED by --no-reapply-setup")
    else:
        inlet_readback = sweep.set_inlet_phase_mass_flows(solver, case)
        injection_readbacks = sweep.set_dpm_injections(solver, bins, args.dpm_velocity_mode)

    iteration_evidence: list[dict[str, object]] = []
    completed = sweep.iterate_case(
        solver,
        args.additional_iterations,
        args.report_interval,
        args.checkpoint_interval,
        args.remote_output_dir,
        prefix,
        "chunked",
        evidence_out=iteration_evidence,
    )
    reported_end_iterations = sweep.read_iteration_count(solver)
    print(f"reported_ending_number_of_iterations: {reported_end_iterations}")

    if args.verified_starting_iterations is not None:
        observed_total = args.verified_starting_iterations + completed
        if (
            args.verified_completed_iterations is not None
            and observed_total != args.verified_completed_iterations
        ):
            raise RuntimeError(
                "Completed iteration total does not match the requested verified total: "
                f"observed={observed_total}, expected={args.verified_completed_iterations}"
            )
        sweep.set_verified_iteration_label(solver, observed_total)

    residual_rows = sweep.monitor_history_rows(solver)
    residual_iterations = [float(row["iteration"]) for row in residual_rows]
    expected_last_iteration = (
        args.verified_starting_iterations + completed
        if args.verified_starting_iterations is not None
        else completed
    )
    if not residual_iterations or max(residual_iterations) < expected_last_iteration:
        raise RuntimeError(
            "Residual history does not contain the expected continuation endpoint: "
            f"last={max(residual_iterations) if residual_iterations else None}, "
            f"expected={expected_last_iteration}"
        )
    residual_csv = local_output_dir / f"{prefix}_residual_history.csv"
    residual_fields = sweep.write_monitor_history_csv(residual_csv, residual_rows)
    remote_residual_csv = sweep.remote_join(args.remote_output_dir, f"{prefix}_residual_history.csv")
    sweep.remote_text_write_best_effort(
        solver,
        remote_residual_csv,
        sweep.rows_to_csv_text(residual_rows, residual_fields),
    )

    flow_case_file = sweep.remote_join(args.remote_output_dir, f"{prefix}_flow.cas.h5")
    flow_data_file = sweep.remote_join(args.remote_output_dir, f"{prefix}_flow.dat.h5")
    sweep.write_case_data_pair(solver, flow_case_file, flow_data_file, "continued_flow_pre_dpm")

    report_text = sweep.run_dpm_reports(solver, args.remote_output_dir, prefix, bins)
    result_rows = sweep.parse_dpm_result_rows(case, bins, report_text, args.dpm_velocity_mode)
    dpm_mass_balance = sweep.dpm_mass_balance_audit(result_rows)
    if args.verified_completed_iterations is not None:
        summary_iterations = args.verified_completed_iterations
    elif args.verified_starting_iterations is not None:
        summary_iterations = args.verified_starting_iterations + completed
    else:
        summary_iterations = completed
    case_summary_row = sweep.parse_case_summary_row(case, bins, report_text, summary_iterations, result_rows)

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

    post_dpm_injection_readbacks = injection_readbacks
    if not args.no_dpm_report:
        post_dpm_injection_readbacks = sweep.read_dpm_injections(
            solver,
            bins,
            args.dpm_velocity_mode,
        )

    case_file = sweep.remote_join(args.remote_output_dir, f"{prefix}_post_dpm.cas.h5")
    data_file = sweep.remote_join(args.remote_output_dir, f"{prefix}_post_dpm.dat.h5")
    sweep.write_case_data_pair(solver, case_file, data_file, "continued_post_dpm")

    manifest = {
        "case": case.csv_case,
        "condition": case.condition,
        "mode": "continue_current_case",
        "remote_output_paths": {
            "flow_case_pre_dpm": flow_case_file,
            "flow_data_pre_dpm": flow_data_file,
            "case": case_file,
            "data": data_file,
            "dpm_report": remote_report,
            "injection_results": remote_case_csv,
            "case_summary": remote_summary_csv,
            "residual_history": remote_residual_csv,
        },
        "reported_starting_number_of_iterations": reported_start_iterations,
        "reported_ending_number_of_iterations": reported_end_iterations,
        "reported_number_of_iterations_is_completion_proof": False,
        "verified_starting_iterations": args.verified_starting_iterations,
        "verified_completed_iterations": args.verified_completed_iterations,
        "additional_iterations_requested": args.additional_iterations,
        "additional_iterations_completed": completed,
        "iteration_evidence": iteration_evidence,
        "residual_history_rows": len(residual_rows),
        "summary_iterations": summary_iterations,
        "fluent_internal_autosave": autosave_state,
        "dpm_velocity_mode": args.dpm_velocity_mode,
        "dpm_report_mass_flow_basis": sweep.DPM_MASS_FLOW_BASIS,
        "physics_readback": physics_readback,
        "inlet_readback": inlet_readback,
        "injection_readback_names": sorted(injection_readbacks) if injection_readbacks else [],
        "injection_readbacks": injection_readbacks,
        "post_dpm_injection_readbacks": post_dpm_injection_readbacks,
        "case_summary": case_summary_row,
        "dpm_mass_balance": dpm_mass_balance,
    }
    manifest_text = json.dumps(manifest, indent=2, default=str)
    local_manifest = local_output_dir / f"{prefix}_manifest.json"
    sweep.write_local_text(local_manifest, manifest_text)
    remote_manifest = sweep.remote_join(args.remote_output_dir, f"{prefix}_manifest.json")
    sweep.remote_text_write_best_effort(solver, remote_manifest, manifest_text)

    print_header("Continuation Complete")
    print(f"local_case_summary: {local_summary_csv}")
    print(f"local_injection_results: {local_case_csv}")
    print(f"local_report: {local_report}")
    print(f"remote_case: {case_file}")
    print(f"remote_data: {data_file}")
    print(f"rows: {len(result_rows)}")
    if not dpm_mass_balance["passed"]:
        raise RuntimeError(
            "DPM fate mass does not reconcile with injected mass for: "
            f"{dpm_mass_balance['failed_injections']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

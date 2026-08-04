#!/usr/bin/env python3
"""Run DPM-only injection direction sensitivity on a saved Purnanto case."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import replace
from pathlib import Path, PureWindowsPath
from typing import Any, Sequence

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
from run_purnanto_dpm_sensitivity import (  # noqa: E402
    apply_dpm_tracking_sensitivity,
    default_case_data_paths,
    load_case_data,
    single_case_plan,
)


VARIANTS = ("face_normal", "z_negative", "z_positive")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare face-normal and explicit +/-z DPM injection directions on one saved flow field."
    )
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument("--case-filter", default="1440", help="Paper case selector. Default: 1440.")
    parser.add_argument("--resume-case", default="", help="Remote solved case file.")
    parser.add_argument("--resume-data", default="", help="Remote solved data file.")
    parser.add_argument(
        "--variant",
        action="append",
        choices=VARIANTS,
        default=[],
        help="Variant to run. Can be repeated. Defaults to all variants.",
    )
    parser.add_argument(
        "--label",
        default="direction_sensitivity",
        help="Output label suffix.",
    )
    parser.add_argument(
        "--dpm-max-steps",
        type=int,
        default=500000,
        help="DPM max tracking steps for each variant.",
    )
    parser.add_argument(
        "--step-length-factor",
        type=float,
        default=0.0,
        help="Optional DPM step-length factor override. Use 0 to leave unchanged.",
    )
    parser.add_argument("--harwell-csv", default=str(sweep.DEFAULT_HARWELL_CSV))
    parser.add_argument(
        "--remote-output-dir",
        default=sweep.DEFAULT_REMOTE_OUTPUT_DIR,
        help="Remote Windows output folder visible to Fluent.",
    )
    parser.add_argument(
        "--local-output-dir",
        default=str(sweep.DEFAULT_LOCAL_OUTPUT_DIR),
        help="Local output folder.",
    )
    parser.add_argument(
        "--save-case-data",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Optionally save case/data for every variant. Default: false.",
    )
    return parser


def variant_bins(
    bins: Sequence[sweep.InjectionBin],
    variant: str,
) -> tuple[list[sweep.InjectionBin], str]:
    if variant == "face_normal":
        return list(bins), "face-normal"
    if variant == "z_negative":
        return [replace(item, z_velocity_ms=-abs(item.z_velocity_ms)) for item in bins], "components"
    if variant == "z_positive":
        return [replace(item, z_velocity_ms=abs(item.z_velocity_ms)) for item in bins], "components"
    raise ValueError(f"Unknown variant: {variant}")


def summarize_variant(
    variant: str,
    case_summary: dict[str, Any],
) -> dict[str, Any]:
    gas = float(case_summary.get("gas_mass_flow_kgs") or 0)
    escaped = float(case_summary.get("escaped_kgs") or 0)
    trapped = float(case_summary.get("trapped_kgs") or 0)
    incomplete = float(case_summary.get("incomplete_kgs") or 0)
    injected = float(case_summary.get("dpm_injected_mass_flow_kgs") or 0)
    steam_quality = gas / (gas + escaped) * 100 if gas + escaped > 0 else ""
    escaped_fraction = escaped / injected if injected > 0 else ""
    trapped_fraction = trapped / injected if injected > 0 else ""
    incomplete_fraction = incomplete / injected if injected > 0 else ""
    return {
        "variant": variant,
        "case": case_summary.get("case"),
        "enthalpy_kJkg": case_summary.get("enthalpy_kJkg"),
        "gas_mass_flow_kgs": gas,
        "liquid_mass_flow_kgs": case_summary.get("liquid_mass_flow_kgs"),
        "dpm_injected_mass_flow_kgs": injected,
        "escaped_kgs": escaped,
        "trapped_kgs": trapped,
        "incomplete_kgs": incomplete,
        "escaped_fraction": escaped_fraction,
        "trapped_fraction": trapped_fraction,
        "incomplete_fraction": incomplete_fraction,
        "steam_quality_percent_from_escaped": steam_quality,
        "escaped_count": case_summary.get("escaped_count"),
        "trapped_count": case_summary.get("trapped_count"),
        "incomplete_count": case_summary.get("incomplete_count"),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_variant(
    solver: Any,
    *,
    case: sweep.PaperCase,
    bins: list[sweep.InjectionBin],
    source_case: str,
    source_data: str,
    variant: str,
    label: str,
    remote_output_dir: str,
    local_output_dir: Path,
    dpm_max_steps: int,
    step_length_factor: float,
    save_case_data: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    variant_slug = sweep.slugify(variant)
    prefix = f"{sweep.case_prefix(case)}_{sweep.slugify(label)}_{variant_slug}"
    bins_for_variant, velocity_mode = variant_bins(bins, variant)

    print_header(f"Variant {variant}")
    load_case_data(solver, source_case, source_data)
    sweep.require_current_case_shape(solver)
    inlet_readback = sweep.set_inlet_phase_mass_flows(solver, case)
    injection_readbacks = sweep.set_dpm_injections(solver, bins_for_variant, velocity_mode)
    tracking = apply_dpm_tracking_sensitivity(
        solver,
        max_steps=dpm_max_steps,
        step_length_factor=step_length_factor,
    )

    report_text = sweep.run_dpm_reports(solver, remote_output_dir, prefix, bins_for_variant)
    result_rows = sweep.parse_dpm_result_rows(case, bins_for_variant, report_text, velocity_mode)
    iteration_count = sweep.read_iteration_count(solver)
    case_summary = sweep.parse_case_summary_row(case, bins_for_variant, report_text, iteration_count or 0, result_rows)

    local_report = local_output_dir / f"{prefix}_dpm_report.txt"
    sweep.write_local_text(local_report, report_text)
    remote_report = sweep.remote_join(remote_output_dir, f"{prefix}_dpm_report.txt")
    sweep.remote_text_write_best_effort(solver, remote_report, report_text)

    local_results = local_output_dir / f"{prefix}_injection_results.csv"
    sweep.write_local_csv(local_results, result_rows, sweep.RESULT_FIELDS)
    remote_results = sweep.remote_join(remote_output_dir, f"{prefix}_injection_results.csv")
    sweep.remote_text_write_best_effort(solver, remote_results, sweep.rows_to_csv_text(result_rows, sweep.RESULT_FIELDS))

    local_summary = local_output_dir / f"{prefix}_case_summary.csv"
    sweep.write_local_csv(local_summary, [case_summary], sweep.CASE_SUMMARY_FIELDS)
    remote_summary = sweep.remote_join(remote_output_dir, f"{prefix}_case_summary.csv")
    sweep.remote_text_write_best_effort(solver, remote_summary, sweep.rows_to_csv_text([case_summary], sweep.CASE_SUMMARY_FIELDS))

    remote_case = ""
    remote_data = ""
    if save_case_data:
        remote_case = sweep.remote_join(remote_output_dir, f"{prefix}.cas.h5")
        remote_data = sweep.remote_join(remote_output_dir, f"{prefix}.dat.h5")
        sweep.write_case_data_pair(solver, remote_case, remote_data, f"{variant_slug}_case_data")

    manifest = {
        "case": case.csv_case,
        "condition": case.condition,
        "variant": variant,
        "source_case": source_case,
        "source_data": source_data,
        "velocity_mode": velocity_mode,
        "velocity_definition": (
            "Fluent face-normal direction with magnitude=abs(z_velocity_ms)"
            if velocity_mode == "face-normal"
            else f"Explicit components x=0, y=0, z={bins_for_variant[0].z_velocity_ms}"
        ),
        "dpm_max_steps": dpm_max_steps,
        "step_length_factor": step_length_factor if step_length_factor > 0 else "unchanged",
        "tracking": tracking,
        "inlet_readback": inlet_readback,
        "injection_readback_names": sorted(injection_readbacks),
        "case_summary": case_summary,
        "local_output_paths": {
            "dpm_report": str(local_report),
            "injection_results": str(local_results),
            "case_summary": str(local_summary),
        },
        "remote_output_paths": {
            "case": remote_case,
            "data": remote_data,
            "dpm_report": remote_report,
            "injection_results": remote_results,
            "case_summary": remote_summary,
        },
    }
    local_manifest = local_output_dir / f"{prefix}_manifest.json"
    manifest_text = json.dumps(manifest, indent=2, default=str)
    sweep.write_local_text(local_manifest, manifest_text)
    remote_manifest = sweep.remote_join(remote_output_dir, f"{prefix}_manifest.json")
    sweep.remote_text_write_best_effort(solver, remote_manifest, manifest_text)

    summary = summarize_variant(variant, case_summary)
    summary["local_case_summary"] = str(local_summary)
    summary["local_injection_results"] = str(local_results)
    summary["local_report"] = str(local_report)
    print("variant_summary:", json.dumps(summary, indent=2, default=str))
    return result_rows, case_summary, summary


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    local_output_dir = sweep.ensure_local_output_dir(args.local_output_dir)
    case, bins = single_case_plan(args.case_filter, Path(args.harwell_csv).expanduser().resolve())
    variants = args.variant or list(VARIANTS)

    source_case, source_data = args.resume_case, args.resume_data
    if not source_case and not source_data:
        source_case, source_data = default_case_data_paths(case, args.remote_output_dir)
    if not (source_case and source_data):
        raise ValueError("--resume-case and --resume-data must be supplied together")

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    sweep.ensure_remote_directory_best_effort(solver, args.remote_output_dir)
    sweep.remote_chdir(solver, str(PureWindowsPath(source_case).parent))

    combined_rows: list[dict[str, Any]] = []
    variant_summaries: list[dict[str, Any]] = []
    for variant in variants:
        rows, _case_summary, variant_summary = run_variant(
            solver,
            case=case,
            bins=bins,
            source_case=source_case,
            source_data=source_data,
            variant=variant,
            label=args.label,
            remote_output_dir=args.remote_output_dir,
            local_output_dir=local_output_dir,
            dpm_max_steps=args.dpm_max_steps,
            step_length_factor=args.step_length_factor,
            save_case_data=args.save_case_data,
        )
        for row in rows:
            row = dict(row)
            row["variant"] = variant
            combined_rows.append(row)
        variant_summaries.append(variant_summary)

    combined_path = local_output_dir / f"{sweep.case_prefix(case)}_{sweep.slugify(args.label)}_all_variants_injection_results.csv"
    if combined_rows:
        fields = ("variant",) + tuple(sweep.RESULT_FIELDS)
        sweep.write_local_csv(combined_path, combined_rows, fields)
        remote_combined = sweep.remote_join(args.remote_output_dir, combined_path.name)
        sweep.remote_text_write_best_effort(solver, remote_combined, sweep.rows_to_csv_text(combined_rows, fields))

    summary_path = local_output_dir / f"{sweep.case_prefix(case)}_{sweep.slugify(args.label)}_variant_summary.csv"
    write_csv(summary_path, variant_summaries)
    remote_summary = sweep.remote_join(args.remote_output_dir, summary_path.name)
    sweep.remote_text_write_best_effort(
        solver,
        remote_summary,
        sweep.rows_to_csv_text(variant_summaries, list(variant_summaries[0].keys())) if variant_summaries else "",
    )

    print_header("Direction Sensitivity Complete")
    print(f"variant_summary_csv: {summary_path}")
    print(f"combined_injection_csv: {combined_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Post-process an existing live Fluent case/data pair without mutating setup state.

This script is the operator entrypoint for reusable `08b`-style post-processing.
It connects to a configured gRPC server, loads an existing case/data pair, reads
carrier-field flux metrics plus DPM inventory, and writes JSON + Markdown output.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PureWindowsPath

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - local convenience fallback
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import (  # noqa: E402
    DEFAULT_OMITTED_DIAMETERS_UM,
    calculate_carrier_metrics,
    capture_session_summary,
    compile_postprocess_result,
    extract_mass_flow_report,
    inspect_dpm_inventory,
    load_case_data_pair,
    render_markdown_report,
    run_dpm_sample_per_injection,
    write_json,
    write_markdown,
)


DEFAULT_SERVER_ID = "2"
DEFAULT_CASE_FILE = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)"
    r"\TwoPhaseInletV2(Purnanto)-25-05000.cas.h5"
)
DEFAULT_DATA_FILE = (
    r"C:\Users\syok443\Documents\TwoPhaseInletV2(Purnanto)"
    r"\TwoPhaseInletV2(Purnanto)-25-05000.dat.h5"
)
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "live_postprocess"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only post-processing for an existing Fluent case/data pair."
    )
    parser.add_argument(
        "--server-id",
        default=DEFAULT_SERVER_ID,
        help="Configured Fluent server id to use. Default: 2.",
    )
    parser.add_argument(
        "--case-file",
        default=DEFAULT_CASE_FILE,
        help="Remote Fluent case file path visible to the chosen server.",
    )
    parser.add_argument(
        "--data-file",
        default=DEFAULT_DATA_FILE,
        help="Remote Fluent data file path visible to the chosen server.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Local output directory for JSON and Markdown summaries.",
    )
    parser.add_argument(
        "--run-label",
        default="",
        help="Optional label for output files. Defaults to the case stem.",
    )
    parser.add_argument(
        "--load-mode",
        choices=("auto", "paired", "explicit"),
        default="explicit",
        help=(
            "How to load the case/data pair. "
            "Use explicit for read_case then read_data, paired for Fluent's paired read_case_data, "
            "or auto to use paired only when filenames match. Default: explicit."
        ),
    )
    parser.add_argument(
        "--snapshot-json",
        default="",
        help="Optional path for a larger raw JSON snapshot of the normalized output.",
    )
    parser.add_argument(
        "--already-loaded",
        action="store_true",
        help="Assume the target case/data are already loaded in the active Fluent session and skip any load commands.",
    )
    parser.add_argument(
        "--dpm-sample-per-injection",
        action="store_true",
        help="Run Fluent report/dpm-sample one injection at a time on the active injections and capture parsed counts.",
    )
    parser.add_argument(
        "--dpm-sample-boundaries",
        nargs="*",
        default=["steaminlet"],
        help="Boundary names to pass into Fluent report/dpm-sample. Default: steaminlet.",
    )
    parser.add_argument(
        "--dpm-sample-planes",
        nargs="*",
        default=[],
        help="Optional plane names to pass into Fluent report/dpm-sample. Default: none.",
    )
    parser.add_argument(
        "--dpm-sample-prompt-order",
        choices=("sample-surfaces-first", "injections-first"),
        default="injections-first",
        help=(
            "Prompt order for report/dpm-sample. Default is Fluent TUI order: "
            "one release injection, sample boundaries, then planes."
        ),
    )
    parser.add_argument(
        "--dpm-sample-remote-dir",
        default="",
        help=(
            "Remote directory for per-injection .dpm sample files. "
            "Default: the remote case-file directory."
        ),
    )
    parser.add_argument(
        "--no-dpm-sample-fallback",
        action="store_true",
        help="Disable retry with the alternate dpm-sample prompt order when the first command does not parse counts.",
    )
    return parser


def derive_run_label(case_file: str, explicit_label: str) -> str:
    if explicit_label.strip():
        return explicit_label.strip()
    name = Path(case_file.replace("\\", "/")).name
    if name.endswith(".cas.h5"):
        return name[:-7]
    return Path(name).stem


def build_dpm_sample_file_names(
    *,
    case_file: str,
    remote_dir: str,
    run_label: str,
    boundary_names: list[str],
    injection_names: list[str],
) -> dict[str, str]:
    base_dir = PureWindowsPath(remote_dir) if remote_dir.strip() else PureWindowsPath(case_file).parent
    boundary_label = "-".join(boundary_names) if boundary_names else "no-boundary"
    safe_run_label = "".join(char if char.isalnum() or char in "._-" else "_" for char in run_label)
    safe_boundary_label = "".join(char if char.isalnum() or char in "._-" else "_" for char in boundary_label)

    sample_files: dict[str, str] = {}
    for injection_name in injection_names:
        safe_injection = "".join(char if char.isalnum() or char in "._-" else "_" for char in injection_name)
        sample_files[injection_name] = str(
            base_dir / f"{safe_run_label}-{safe_boundary_label}-{safe_injection}.dpm"
        )
    return sample_files


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    run_label = derive_run_label(args.case_file, args.run_label)
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_json = output_dir / f"{run_label}-summary.json"
    summary_md = output_dir / f"{run_label}-report.md"

    solver = connect(server_id=args.server_id)
    print(f"Connected to Fluent server {args.server_id}.")

    if args.already_loaded:
        load_summary = {
            "case_file": args.case_file,
            "data_file": args.data_file,
            "load_mode": "already-loaded-session",
            "case_name": Path(args.case_file.replace("\\", "/")).name,
            "data_name": Path(args.data_file.replace("\\", "/")).name,
            "case_data_name_match": True,
        }
    else:
        load_summary = load_case_data_pair(
            solver,
            case_file=args.case_file,
            data_file=args.data_file,
            load_strategy=args.load_mode,
        )
    session_summary = capture_session_summary(solver)

    zone_roles = session_summary["zone_discovery"]["roles"]
    zones_for_flux = []
    for value in (zone_roles.get("liquid_inlet"), zone_roles.get("steam_inlet")):
        if value and value not in zones_for_flux:
            zones_for_flux.append(value)
    for value in session_summary["zone_discovery"]["all_outlets"]:
        if value and value not in zones_for_flux:
            zones_for_flux.append(value)

    phase_domain_map = session_summary["phase_domain_map"]
    carrier_fluxes = extract_mass_flow_report(
        solver,
        zones=zones_for_flux,
        domains=(phase_domain_map["vapor_domain"], phase_domain_map["liquid_domain"]),
    )
    carrier_metrics = calculate_carrier_metrics(
        carrier_fluxes,
        zone_roles,
        vapor_domain=phase_domain_map["vapor_domain"],
        liquid_domain=phase_domain_map["liquid_domain"],
    )
    dpm_inventory, dpm_metrics = inspect_dpm_inventory(
        solver,
        omitted_diameters_um=DEFAULT_OMITTED_DIAMETERS_UM,
    )
    if args.dpm_sample_per_injection:
        sample_injection_names = [
            str(item.get("name"))
            for item in dpm_inventory.get("injections", [])
            if item.get("name")
        ]
        sample_file_names = build_dpm_sample_file_names(
            case_file=args.case_file,
            remote_dir=args.dpm_sample_remote_dir,
            run_label=run_label,
            boundary_names=args.dpm_sample_boundaries,
            injection_names=sample_injection_names,
        )
        sample_payload = run_dpm_sample_per_injection(
            solver,
            injection_names=sample_injection_names,
            boundary_names=args.dpm_sample_boundaries,
            plane_names=args.dpm_sample_planes,
            sample_file_names=sample_file_names,
            prompt_order=args.dpm_sample_prompt_order,
            fallback_prompt_order=None if args.no_dpm_sample_fallback else "sample-surfaces-first",
        )
        dpm_metrics["per_injection_sample"] = sample_payload

    result = compile_postprocess_result(
        server_id=str(args.server_id),
        run_label=run_label,
        load_summary=load_summary,
        session_summary=session_summary,
        carrier_fluxes=carrier_fluxes,
        carrier_metrics=carrier_metrics,
        dpm_inventory=dpm_inventory,
        dpm_metrics=dpm_metrics,
        omitted_diameters_um=DEFAULT_OMITTED_DIAMETERS_UM,
    )

    write_json(summary_json, result)
    write_markdown(summary_md, render_markdown_report(result))

    if args.snapshot_json.strip():
        write_json(Path(args.snapshot_json).expanduser().resolve(), result)

    print(f"summary_json: {summary_json}")
    print(f"summary_markdown: {summary_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

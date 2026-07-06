#!/usr/bin/env python3
"""Create a hybrid Fluent extraction bundle using both PyFluent and offline file reads.

This script is intentionally read-mostly:
- live export happens through PyFluent/gRPC
- offline export happens through local `.cas/.dat/.h5` inspection
- no setup values are intentionally modified

Use this when a saved case/data pair may contain unreported Fluent settings and
you want the most complete capture possible before rebuilding the setup.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.extraction import (  # noqa: E402
    capture_candidate_paths,
    capture_object_tree,
    collect_scheme_snapshot,
    iso_utc_now,
    load_remote_case_data,
    try_call,
    write_json,
)


DEFAULT_PATH_SPECS: list[dict[str, Any]] = [
    {"label": "settings_root", "paths": [["settings"]], "max_depth": 3},
    {"label": "setup", "paths": [["settings", "setup"]], "max_depth": 4},
    {"label": "setup_general", "paths": [["settings", "setup", "general"]], "max_depth": 4},
    {"label": "setup_models", "paths": [["settings", "setup", "models"]], "max_depth": 5},
    {
        "label": "multiphase_model",
        "paths": [
            ["settings", "setup", "models", "multiphase"],
            ["settings", "setup", "models", "multiphase_model"],
        ],
        "max_depth": 6,
    },
    {
        "label": "viscous_model",
        "paths": [["settings", "setup", "models", "viscous"]],
        "max_depth": 5,
    },
    {
        "label": "discrete_phase_model",
        "paths": [
            ["settings", "setup", "models", "discrete_phase"],
            ["settings", "setup", "models", "discrete_phase_model"],
            ["settings", "setup", "models", "dpm"],
        ],
        "max_depth": 7,
    },
    {
        "label": "materials",
        "paths": [["settings", "setup", "materials"]],
        "max_depth": 5,
    },
    {
        "label": "boundary_conditions",
        "paths": [["settings", "setup", "boundary_conditions"]],
        "max_depth": 6,
    },
    {
        "label": "cell_zone_conditions",
        "paths": [["settings", "setup", "cell_zone_conditions"]],
        "max_depth": 5,
    },
    {"label": "solution", "paths": [["settings", "solution"]], "max_depth": 5},
    {
        "label": "solution_initialization",
        "paths": [["settings", "solution", "initialization"]],
        "max_depth": 5,
    },
    {
        "label": "results",
        "paths": [["settings", "results"]],
        "max_depth": 4,
    },
    {
        "label": "file_api",
        "paths": [["settings", "file"]],
        "max_depth": 3,
        "include_state": False,
    },
]

DEFAULT_SCHEME_EXPRESSIONS = {
    "flow_time": "(rpgetvar 'flow-time)",
    "time_step": "(rpgetvar 'time-step)",
    "physical_time_step": "(rpgetvar 'physical-time-step)",
    "number_of_iterations": "(rpgetvar 'number-of-iterations)",
    "cwd": "(cx-send '(getcwd))",
    "operating_pressure": "(rpgetvar 'operating-pressure)",
    "gravity_vector": "(rpgetvar 'gravity)",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export a hybrid Fluent settings bundle using both PyFluent and offline file inspection."
    )
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id for PyFluent connection.")
    parser.add_argument("--case", help="Remote Fluent-visible case path (.cas/.cas.h5).")
    parser.add_argument("--data", help="Remote Fluent-visible data path (.dat/.dat.h5).")
    parser.add_argument(
        "--yes-load",
        action="store_true",
        help="Allow this script to replace the active live session by loading the supplied remote case/data.",
    )
    parser.add_argument(
        "--offline-case-file",
        help="Optional local case file to inspect offline with h5py/text parsing.",
    )
    parser.add_argument(
        "--offline-data-file",
        help="Optional local data file to inspect offline with h5py/text parsing.",
    )
    parser.add_argument(
        "--skip-live",
        action="store_true",
        help="Skip the PyFluent live-session export and run only offline extraction.",
    )
    parser.add_argument(
        "--skip-offline",
        action="store_true",
        help="Skip the offline case/data inspection.",
    )
    parser.add_argument(
        "--max-root-depth",
        type=int,
        default=3,
        help="Recursion depth for the broad settings-root crawl. Default: 3.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for output artifacts. Default: PyAnsys/output/hybrid_extract",
    )
    parser.add_argument(
        "--archive-root",
        help="Optional archive root. When set, write into archive-root/archive-name.",
    )
    parser.add_argument(
        "--archive-name",
        help="Required when --archive-root is used.",
    )
    parser.add_argument(
        "--report-ref",
        default="",
        help="Optional related setup-report path or identifier.",
    )
    parser.add_argument(
        "--notes-label",
        default="",
        help="Optional short label describing why this bundle exists.",
    )
    return parser


def resolve_output_dir(args: argparse.Namespace) -> Path:
    if args.archive_root:
        if not args.archive_name:
            raise RuntimeError("--archive-name is required when --archive-root is used.")
        return Path(args.archive_root).expanduser().resolve() / args.archive_name
    if args.output_dir:
        return Path(args.output_dir).expanduser().resolve()
    return ROOT / "output" / "hybrid_extract"


def write_offline_bundle(input_path: Path, output_dir: Path) -> dict[str, Any]:
    from extractors.python.h5_case_extractor import (  # noqa: WPS433,E402
        detect_format,
        inspect_hdf5,
        inspect_legacy_text,
    )

    file_format = detect_format(input_path)
    summary = inspect_hdf5(input_path) if file_format == "hdf5" else inspect_legacy_text(input_path)

    (output_dir / "tree.txt").write_text(
        "\n".join(summary.get("tree_lines", [])) + ("\n" if summary.get("tree_lines") else ""),
        encoding="utf-8",
    )
    write_json(output_dir / "summary.json", summary)

    candidate_text_blocks = []
    for item in summary.get("candidate_strings", []):
        candidate_text_blocks.append(f"## {item['path']}\n{item['text']}\n")
    (output_dir / "candidate_strings.txt").write_text(
        "\n".join(candidate_text_blocks),
        encoding="utf-8",
    )
    return summary


def collect_live_bundle(args: argparse.Namespace, output_dir: Path, notes: list[str]) -> dict[str, Any]:
    solver = connect(args.server_id)

    if args.case or args.data:
        if not args.case:
            raise RuntimeError("--case is required when loading remote files.")
        if not args.yes_load:
            raise RuntimeError("Refusing to load case/data without --yes-load.")
        load_remote_case_data(solver, args.case, args.data, notes)

    live_dir = output_dir / "live"
    live_dir.mkdir(parents=True, exist_ok=True)

    root_tree = capture_object_tree(
        solver.settings,
        "settings",
        notes,
        max_depth=args.max_root_depth,
    )
    targeted_branches = capture_candidate_paths(
        solver,
        notes,
        DEFAULT_PATH_SPECS,
    )
    session_probe = {
        "fluent_version": try_call("solver.get_fluent_version", solver.get_fluent_version, notes),
        "solver_dir": try_call("dir(solver)", lambda: sorted(dir(solver)), notes),
        "settings_dir": try_call("dir(solver.settings)", lambda: sorted(dir(solver.settings)), notes),
    }
    scheme_snapshot = collect_scheme_snapshot(solver, notes, DEFAULT_SCHEME_EXPRESSIONS)

    live_bundle = {
        "captured_at_utc": iso_utc_now(),
        "session_probe": session_probe,
        "scheme_snapshot": scheme_snapshot,
        "settings_root_tree": root_tree,
        "targeted_branches": targeted_branches,
    }

    write_json(live_dir / "session_probe.json", session_probe)
    write_json(live_dir / "scheme_snapshot.json", scheme_snapshot)
    write_json(live_dir / "settings_root_tree.json", root_tree)
    write_json(live_dir / "targeted_branches.json", targeted_branches)
    write_json(live_dir / "bundle.json", live_bundle)
    return live_bundle


def render_readme(metadata: dict[str, Any], capture_summary: dict[str, Any], notes: list[str]) -> str:
    lines = [
        f"# Hybrid Fluent Extraction Bundle: {metadata['bundle_name']}",
        "",
        "## Metadata",
        "",
        f"- Exported at (UTC): `{metadata['exported_at_utc']}`",
        f"- Related setup report: `{metadata.get('report_ref', '(none)')}`",
        f"- Notes label: `{metadata.get('notes_label', '(none)')}`",
        f"- Remote case path: `{metadata.get('remote_case', '(not supplied)')}`",
        f"- Remote data path: `{metadata.get('remote_data', '(not supplied)')}`",
        f"- Offline case file: `{metadata.get('offline_case_file', '(not supplied)')}`",
        f"- Offline data file: `{metadata.get('offline_data_file', '(not supplied)')}`",
        "",
        "## Coverage Summary",
        "",
        f"- Live PyFluent export: `{capture_summary['live_status']}`",
        f"- Offline case export: `{capture_summary['offline_case_status']}`",
        f"- Offline data export: `{capture_summary['offline_data_status']}`",
        f"- Notes recorded: `{len(notes)}`",
        "",
        "## Bundle Layout",
        "",
        "- `manifest.json`: top-level metadata and status",
        "- `live/`: live PyFluent capture bundle if a session was available",
        "- `offline_case/`: local case-file inventory if a local case file was supplied",
        "- `offline_data/`: local data-file inventory if a local data file was supplied",
        "- `notes.txt`: capture gaps and path failures",
        "",
        "## Interpretation Rules",
        "",
        "- Treat `live/targeted_branches.json` as the main settings-tree evidence.",
        "- Treat offline candidate strings as supporting hints, not as proof of effective live Fluent state.",
        "- Any branch missing from the live export should be treated as unresolved until checked on the Fluent machine.",
        "",
        "## Notes",
        "",
    ]

    if notes:
        for note in notes:
            lines.append(f"- {note}")
    else:
        lines.append("- None.")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = build_parser().parse_args()
    output_dir = resolve_output_dir(args)
    output_dir.mkdir(parents=True, exist_ok=True)

    notes: list[str] = []
    manifest: dict[str, Any] = {
        "bundle_name": args.archive_name or output_dir.name,
        "exported_at_utc": iso_utc_now(),
        "report_ref": args.report_ref,
        "notes_label": args.notes_label,
        "remote_case": args.case or "",
        "remote_data": args.data or "",
        "offline_case_file": args.offline_case_file or "",
        "offline_data_file": args.offline_data_file or "",
        "live_export_enabled": not args.skip_live,
        "offline_export_enabled": not args.skip_offline,
    }

    capture_summary = {
        "live_status": "skipped",
        "offline_case_status": "skipped",
        "offline_data_status": "skipped",
    }

    if not args.skip_live:
        live_bundle = collect_live_bundle(args, output_dir, notes)
        manifest["live_bundle"] = {
            "fluent_version": live_bundle["session_probe"].get("fluent_version"),
            "captured_at_utc": live_bundle["captured_at_utc"],
        }
        capture_summary["live_status"] = "captured"

    if not args.skip_offline and args.offline_case_file:
        case_path = Path(args.offline_case_file).expanduser().resolve()
        if not case_path.exists():
            raise FileNotFoundError(f"Offline case file not found: {case_path}")
        summary = write_offline_bundle(case_path, output_dir / "offline_case")
        manifest["offline_case_summary"] = {
            "input_file": str(case_path),
            "format": summary["format"],
            "candidate_string_count": summary.get("candidate_string_count", 0),
        }
        capture_summary["offline_case_status"] = "captured"

    if not args.skip_offline and args.offline_data_file:
        data_path = Path(args.offline_data_file).expanduser().resolve()
        if not data_path.exists():
            raise FileNotFoundError(f"Offline data file not found: {data_path}")
        summary = write_offline_bundle(data_path, output_dir / "offline_data")
        manifest["offline_data_summary"] = {
            "input_file": str(data_path),
            "format": summary["format"],
            "candidate_string_count": summary.get("candidate_string_count", 0),
        }
        capture_summary["offline_data_status"] = "captured"

    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "capture_summary.json", capture_summary)
    (output_dir / "notes.txt").write_text("\n".join(notes) + ("\n" if notes else ""), encoding="utf-8")
    (output_dir / "README.md").write_text(
        render_readme(manifest, capture_summary, notes),
        encoding="utf-8",
    )

    print(f"[OK] Output directory: {output_dir}")
    print(f"[OK] Live export status: {capture_summary['live_status']}")
    print(f"[OK] Offline case status: {capture_summary['offline_case_status']}")
    print(f"[OK] Offline data status: {capture_summary['offline_data_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

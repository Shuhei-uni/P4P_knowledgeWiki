#!/usr/bin/env python3
"""Export active Fluent setup state through PyFluent.

This script is intentionally read-mostly. It only loads a case/data file when
explicitly asked with --yes-load.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export reachable Fluent settings to JSON.")
    parser.add_argument("--case", help="Remote Fluent-visible case path (.cas.h5).")
    parser.add_argument("--data", help="Remote Fluent-visible data path (.dat.h5).")
    parser.add_argument(
        "--yes-load",
        action="store_true",
        help="Allow this script to replace the active session by loading the supplied case/data.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory for output artifacts. Default: PyAnsys/output/fluent_extract",
    )
    parser.add_argument(
        "--archive-root",
        help=(
            "Optional archive root. When set, the exporter creates a dated setup bundle "
            "under this root instead of writing directly to --output-dir."
        ),
    )
    parser.add_argument(
        "--archive-name",
        help="Required with --archive-root. Directory name for this exported setup bundle.",
    )
    parser.add_argument(
        "--report-ref",
        default="",
        help="Optional related setup-report path or identifier.",
    )
    parser.add_argument(
        "--notes-label",
        default="",
        help="Optional short label describing why this archive exists.",
    )
    return parser


def safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_json(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def try_get_state(label: str, getter, notes: list[str]) -> Any:
    try:
        return safe_json(getter())
    except Exception as exc:
        notes.append(f"{label}: unavailable ({exc})")
        return None


def try_scheme_eval(solver, expression: str, notes: list[str]) -> Any:
    try:
        return solver.scheme.eval(expression)
    except Exception as exc:
        notes.append(f"scheme {expression}: unavailable ({exc})")
        return None


def try_child_names(label: str, obj: Any, notes: list[str]) -> list[str]:
    try:
        return [str(name) for name in obj.child_names]
    except Exception as exc:
        notes.append(f"{label}.child_names: unavailable ({exc})")
        return []


def capture_branch(label: str, obj: Any, notes: list[str], *, max_depth: int = 2, depth: int = 0) -> Any:
    if not hasattr(obj, "get_state") or not hasattr(obj, "child_names"):
        return {"_non_settings_object": True}

    snapshot: dict[str, Any] = {
        "_state": try_get_state(label, obj.get_state, notes),
    }
    children = try_child_names(label, obj, notes)
    if children:
        snapshot["_child_names"] = children
    try:
        snapshot["_command_names"] = [str(name) for name in obj.command_names]
    except Exception:
        pass

    if depth >= max_depth:
        return snapshot

    for child_name in children:
        if child_name.startswith("_"):
            continue
        try:
            child_obj = getattr(obj, child_name)
        except Exception as exc:
            notes.append(f"{label}.{child_name}: unavailable ({exc})")
            continue
        snapshot[child_name] = capture_branch(
            f"{label}.{child_name}",
            child_obj,
            notes,
            max_depth=max_depth,
            depth=depth + 1,
        )
    return snapshot


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def summarize_boundary_names(boundary_state: Any) -> dict[str, list[str]]:
    if not isinstance(boundary_state, dict):
        return {}
    summary: dict[str, list[str]] = {}
    for boundary_type, zones in boundary_state.items():
        if not isinstance(zones, dict):
            continue
        names = sorted(str(name) for name in zones.keys() if str(name) != "settings")
        if names:
            summary[str(boundary_type)] = names
    return summary


def extract_mesh_counts(solver, notes: list[str]) -> dict[str, Any]:
    exprs = {
        "iterations": "(rpgetvar 'number-of-iterations)",
        "cwd": "(cx-send '(getcwd))",
    }
    return {key: try_scheme_eval(solver, expr, notes) for key, expr in exprs.items()}


def render_markdown_summary(
    metadata: dict[str, Any],
    settings_snapshot: dict[str, Any],
    scheme_snapshot: dict[str, Any],
    notes: list[str],
) -> str:
    boundary_summary = summarize_boundary_names(
        settings_snapshot.get("setup", {}).get("boundary_conditions")
    )
    models = settings_snapshot.get("setup", {}).get("models", {})
    solution = settings_snapshot.get("solution", {})
    methods = solution.get("methods", {}) if isinstance(solution, dict) else {}
    discretization = methods.get("discretization_scheme", {}) if isinstance(methods, dict) else {}

    lines = [
        f"# Actual Fluent Setup Archive: {metadata['archive_name']}",
        "",
        "## Archive Metadata",
        "",
        f"- Exported at (UTC): `{metadata['exported_at_utc']}`",
        f"- Fluent version: `{metadata.get('fluent_version', 'unknown')}`",
        f"- Source case: `{metadata.get('source_case', '(active session)')}`",
        f"- Source data: `{metadata.get('source_data', '(not supplied)')}`",
        f"- Related setup report: `{metadata.get('report_ref', '(none)')}`",
        f"- Notes label: `{metadata.get('notes_label', '(none)')}`",
        "",
        "## Boundary Summary",
        "",
    ]

    if boundary_summary:
        for boundary_type, names in boundary_summary.items():
            lines.append(f"- `{boundary_type}`: `{', '.join(names)}`")
    else:
        lines.append("- Boundary summary unavailable.")

    lines.extend(
        [
            "",
            "## Solver Snapshot",
            "",
            f"- Multiphase: `{models.get('multiphase', {})}`",
            f"- Energy: `{models.get('energy', {})}`",
            f"- Viscous: `{models.get('viscous', {})}`",
            f"- Pressure-velocity coupling: `{methods.get('p_v_coupling', {})}`",
            f"- Discretization: `{discretization}`",
            f"- Iteration count: `{scheme_snapshot.get('iterations')}`",
            f"- Fluent cwd: `{scheme_snapshot.get('cwd')}`",
            "",
            "## Files",
            "",
            "- `metadata.json`",
            "- `settings_snapshot.json`",
            "- `scheme_snapshot.json`",
            "- `notes.txt`",
            "",
            "## Capture Notes",
            "",
        ]
    )

    if notes:
        for note in notes:
            lines.append(f"- {note}")
    else:
        lines.append("- None.")

    lines.append("")
    return "\n".join(lines)


def file_exists(solver, path_text: str) -> bool:
    quoted = path_text.replace("\\", "\\\\").replace('"', '\\"')
    return bool(solver.scheme.eval(f'(file-exists? "{quoted}")'))


def load_remote_case_data(solver, case_path: str, data_path: str | None, notes: list[str]) -> None:
    if not file_exists(solver, case_path):
        raise FileNotFoundError(f"Fluent cannot see case file: {case_path}")
    if data_path and not file_exists(solver, data_path):
        raise FileNotFoundError(f"Fluent cannot see data file: {data_path}")

    case_name = PureWindowsPath(case_path).name
    case_dir = str(PureWindowsPath(case_path).parent)
    quoted_case_dir = case_dir.replace("\\", "\\\\").replace('"', '\\"')
    solver.scheme.eval(f'(chdir "{quoted_case_dir}")')

    if data_path:
        expected_data_name = case_name.removesuffix(".cas.h5") + ".dat.h5"
        actual_data_name = PureWindowsPath(data_path).name
        if actual_data_name == expected_data_name:
            solver.settings.file.read_case_data(file_name=case_path)
        else:
            notes.append(
                "Data filename does not match Fluent default pairing; loading case then explicit data."
            )
            solver.settings.file.read_case(file_name=case_path)
            solver.settings.file.read_data(file_name=data_path)
    else:
        solver.settings.file.read_case(file_name=case_path)


def main() -> int:
    args = build_parser().parse_args()
    if args.archive_root and not args.archive_name:
        raise RuntimeError("--archive-name is required when --archive-root is used.")

    if args.archive_root:
        output_dir = Path(args.archive_root).expanduser().resolve() / args.archive_name
    else:
        output_dir = (
            Path(args.output_dir).expanduser().resolve()
            if args.output_dir
            else ROOT / "output" / "fluent_extract"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    notes: list[str] = []
    solver = connect()

    if args.case or args.data:
        if not args.case:
            raise RuntimeError("--case is required when loading remote files.")
        if not args.yes_load:
            raise RuntimeError("Refusing to load case/data without --yes-load.")
        load_remote_case_data(solver, args.case, args.data, notes)

    settings_snapshot = {
        "fluent_version": try_get_state("fluent_version", solver.get_fluent_version, notes),
        "setup": {
            "general": try_get_state(
                "setup.general", solver.settings.setup.general.get_state, notes
            ),
            "models": try_get_state(
                "setup.models", solver.settings.setup.models.get_state, notes
            ),
            "models_multiphase_detail": capture_branch(
                "setup.models.multiphase",
                solver.settings.setup.models.multiphase,
                notes,
                max_depth=2,
            ),
            "materials": try_get_state(
                "setup.materials", solver.settings.setup.materials.get_state, notes
            ),
            "boundary_conditions": try_get_state(
                "setup.boundary_conditions",
                solver.settings.setup.boundary_conditions.get_state,
                notes,
            ),
            "cell_zone_conditions": try_get_state(
                "setup.cell_zone_conditions",
                solver.settings.setup.cell_zone_conditions.get_state,
                notes,
            ),
        },
        "solution": try_get_state("solution", solver.settings.solution.get_state, notes),
        "solution_initialization_detail": capture_branch(
            "solution.initialization",
            solver.settings.solution.initialization,
            notes,
            max_depth=2,
        ),
    }

    scheme_snapshot = {
        "flow_time": try_scheme_eval(solver, "(rpgetvar 'flow-time)", notes),
        "time_step": try_scheme_eval(solver, "(rpgetvar 'time-step)", notes),
        "physical_time_step": try_scheme_eval(solver, "(rpgetvar 'physical-time-step)", notes),
        "iterations": try_scheme_eval(solver, "(rpgetvar 'number-of-iterations)", notes),
        "cwd": try_scheme_eval(solver, "(cx-send '(getcwd))", notes),
    }

    metadata = {
        "archive_name": args.archive_name or output_dir.name,
        "exported_at_utc": iso_utc_now(),
        "fluent_version": settings_snapshot.get("fluent_version"),
        "source_case": args.case or "",
        "source_data": args.data or "",
        "report_ref": args.report_ref,
        "notes_label": args.notes_label,
        "mesh_and_runtime": extract_mesh_counts(solver, notes),
    }

    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "settings_snapshot.json").write_text(
        json.dumps(settings_snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "scheme_snapshot.json").write_text(
        json.dumps(scheme_snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "notes.txt").write_text("\n".join(notes) + ("\n" if notes else ""), encoding="utf-8")
    (output_dir / "README.md").write_text(
        render_markdown_summary(metadata, settings_snapshot, scheme_snapshot, notes),
        encoding="utf-8",
    )

    print(f"[OK] Output directory: {output_dir}")
    print(f"[OK] Notes recorded: {len(notes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export active Fluent setup state through PyFluent.

This script is intentionally read-mostly. It only loads a case/data file when
explicitly asked with --yes-load.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_connection import connect  # noqa: E402


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
    return parser


def safe_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): safe_json(val) for key, val in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    return value


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
            "models": try_get_state(
                "setup.models", solver.settings.setup.models.get_state, notes
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
    }

    scheme_snapshot = {
        "flow_time": try_scheme_eval(solver, "(rpgetvar 'flow-time)", notes),
        "time_step": try_scheme_eval(solver, "(rpgetvar 'time-step)", notes),
        "physical_time_step": try_scheme_eval(solver, "(rpgetvar 'physical-time-step)", notes),
        "cwd": try_scheme_eval(solver, "(cx-send '(getcwd))", notes),
    }

    (output_dir / "settings_snapshot.json").write_text(
        json.dumps(settings_snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "scheme_snapshot.json").write_text(
        json.dumps(scheme_snapshot, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "notes.txt").write_text("\n".join(notes) + ("\n" if notes else ""), encoding="utf-8")

    print(f"[OK] Output directory: {output_dir}")
    print(f"[OK] Notes recorded: {len(notes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

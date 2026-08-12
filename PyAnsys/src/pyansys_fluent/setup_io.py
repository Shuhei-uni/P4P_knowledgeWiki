#!/usr/bin/env python3
"""Shared file IO helpers for Fluent setup and offline recovery scripts."""

from __future__ import annotations

import json
from pathlib import Path, PureWindowsPath

from pyansys_fluent.common import remote_chdir, try_action
from pyansys_fluent.setup_common import print_header, require_remote_input


def dump_json_if_requested(path_text: str, payload: object) -> None:
    if not path_text:
        return
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"snapshot_json: wrote {path}")


def load_target_mesh(solver, mesh_path: str) -> None:
    print_header("Load Target Mesh")
    require_remote_input(solver, mesh_path, "target mesh")
    remote_chdir(solver, str(PureWindowsPath(mesh_path).parent))
    if not try_action("read_target_mesh", lambda: solver.settings.file.read_mesh(file_name=mesh_path)):
        raise RuntimeError("Could not read target mesh")


def load_case_only(solver, case_path: str, *, label: str = "Load Case") -> None:
    print_header(label)
    require_remote_input(solver, case_path, "case file")
    remote_chdir(solver, str(PureWindowsPath(case_path).parent))
    if not try_action("read_case", lambda: solver.settings.file.read_case(file_name=case_path)):
        raise RuntimeError("Could not read case")


def load_resume_case_data(solver, case_path: str, data_path: str) -> None:
    print_header("Load Resume Case/Data")
    require_remote_input(solver, case_path, "resume case")
    require_remote_input(solver, data_path, "resume data")
    remote_chdir(solver, str(PureWindowsPath(case_path).parent))
    if not try_action("read_resume_case", lambda: solver.settings.file.read_case(file_name=case_path)):
        raise RuntimeError("Could not read resume case")
    if not try_action("read_resume_data", lambda: solver.settings.file.read_data(file_name=data_path)):
        raise RuntimeError("Could not read resume data")


def write_case_only(solver, case_file: str, label: str) -> None:
    print_header(label)
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    if not try_action(f"write_case_{label}", lambda: solver.settings.file.write_case(file_name=case_file)):
        raise RuntimeError(f"Could not write case for {label}")


def write_case_data_pair(
    solver,
    case_file: str,
    data_file: str,
    label: str,
    *,
    allow_case_only: bool = False,
) -> str:
    print_header(label)
    remote_chdir(solver, str(PureWindowsPath(case_file).parent))
    if not try_action(f"write_case_{label}", lambda: solver.settings.file.write_case(file_name=case_file)):
        raise RuntimeError(f"Could not write case for {label}")
    if try_action(f"write_data_{label}", lambda: solver.settings.file.write_data(file_name=data_file)):
        return "case+data"
    if allow_case_only:
        print(
            f"write_data_{label}: SKIPPED/FAILED -> keeping case-only save because data writing is inactive",
            flush=True,
        )
        return "case-only"
    raise RuntimeError(f"Could not write data for {label}")

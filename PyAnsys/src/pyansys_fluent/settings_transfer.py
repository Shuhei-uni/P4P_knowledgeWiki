#!/usr/bin/env python3
"""Reusable Fluent settings-file transfer helpers."""

from __future__ import annotations

from pathlib import PureWindowsPath
from typing import Any

from pyansys_fluent.common import quote_scheme_string, remote_chdir, remote_file_exists, try_action
from pyansys_fluent.dependency_workflow import classify_failure
from pyansys_fluent.setup_common import print_header, require_remote_input


def _parent_dir(path_text: str) -> str:
    return str(PureWindowsPath(path_text).parent)


def _tui_load_string(solver: Any, command: str) -> Any:
    escaped = quote_scheme_string(command)
    return solver.scheme.exec((f'(ti-menu-load-string "{escaped}")',))


def _write_settings_tui(solver: Any, settings_path: str) -> None:
    solver.tui.file.write_settings(settings_path)


def _read_settings_tui(solver: Any, settings_path: str) -> None:
    solver.tui.file.read_settings(settings_path)


def _write_settings_fallback(solver: Any, settings_path: str) -> None:
    _tui_load_string(solver, f'/file/write-settings "{settings_path}"')


def _read_settings_fallback(solver: Any, settings_path: str) -> None:
    _tui_load_string(solver, f'/file/read-settings "{settings_path}"')


def _run_with_fallback(primary_label: str, primary, fallback_label: str, fallback) -> dict[str, Any]:
    try:
        primary()
        print(f"{primary_label}: OK", flush=True)
        return {
            "method": primary_label,
            "primary_error": None,
            "primary_category": None,
        }
    except Exception as primary_exc:
        primary_category = classify_failure(primary_exc)
        print(f"{primary_label}: FAILED -> {primary_exc}", flush=True)
        try:
            fallback()
            print(f"{fallback_label}: OK", flush=True)
            return {
                "method": fallback_label,
                "primary_error": repr(primary_exc),
                "primary_category": primary_category,
            }
        except Exception as fallback_exc:
            fallback_category = classify_failure(fallback_exc)
            raise RuntimeError(
                f"{primary_label} failed ({primary_category}): {primary_exc}; "
                f"{fallback_label} failed ({fallback_category}): {fallback_exc}"
            ) from fallback_exc


def _read_case(solver: Any, case_path: str, data_path: str | None = None) -> None:
    print_header("Load Source Case")
    require_remote_input(solver, case_path, "source case")
    remote_chdir(solver, _parent_dir(case_path))
    if not try_action("read_source_case", lambda: solver.settings.file.read_case(file_name=case_path), critical=False):
        raise RuntimeError(f"Could not read source case: {case_path}")

    if data_path:
        require_remote_input(solver, data_path, "source data")
        if not try_action("read_source_data", lambda: solver.settings.file.read_data(file_name=data_path), critical=False):
            raise RuntimeError(f"Could not read source data: {data_path}")


def _read_mesh(solver: Any, mesh_path: str) -> None:
    print_header("Load Target Mesh")
    require_remote_input(solver, mesh_path, "target mesh")
    remote_chdir(solver, _parent_dir(mesh_path))
    if not try_action("read_target_mesh", lambda: solver.settings.file.read_mesh(file_name=mesh_path), critical=False):
        raise RuntimeError(f"Could not read target mesh: {mesh_path}")


def _write_case_if_requested(solver: Any, output_case_path: str | None) -> None:
    if not output_case_path:
        return
    print_header("Write Output Case")
    remote_chdir(solver, _parent_dir(output_case_path))
    if not try_action("write_output_case", lambda: solver.settings.file.write_case(file_name=output_case_path), critical=False):
        raise RuntimeError(f"Could not write output case: {output_case_path}")


def capture_setup_diagnostics(solver: Any, label: str) -> dict[str, Any]:
    """Capture compact setup state after a load/import step."""

    def safe(label_text: str, getter):
        try:
            return getter()
        except Exception as exc:
            return {"_error": f"{label_text}: {type(exc).__name__}: {exc}"}

    boundary_state = safe(
        "boundary_conditions",
        lambda: solver.settings.setup.boundary_conditions.get_state(),
    )
    cell_zone_state = safe(
        "cell_zone_conditions",
        lambda: solver.settings.setup.cell_zone_conditions.get_state(),
    )

    return {
        "label": label,
        "fluent_version": safe("fluent_version", solver.get_fluent_version),
        "configuration": safe("configuration", solver.tui.file.show_configuration),
        "boundary_conditions": boundary_state,
        "cell_zone_conditions": cell_zone_state,
    }


def print_setup_diagnostics(summary: dict[str, Any]) -> None:
    """Print boundary and cell-zone names/types from a diagnostic snapshot."""

    print_header(f"Diagnostics: {summary['label']}")
    print(f"fluent_version: {summary.get('fluent_version')}")
    configuration = summary.get("configuration")
    if isinstance(configuration, str):
        print(configuration)
    else:
        print(f"configuration: {configuration}")

    for section_name in ("boundary_conditions", "cell_zone_conditions"):
        print(f"\n{section_name}:")
        section = summary.get(section_name)
        if not isinstance(section, dict):
            print(f"  {section!r}")
            continue
        for object_type, objects in section.items():
            if not isinstance(objects, dict):
                continue
            names = sorted(str(name) for name in objects if str(name) != "settings")
            if names:
                print(f"  {object_type}: {', '.join(names)}")


def write_settings_file(
    solver: Any,
    source_case_path: str,
    settings_path: str,
    source_data_path: str | None = None,
) -> dict[str, Any]:
    """Load a source case and write Fluent settings to a remote settings file."""

    _read_case(solver, source_case_path, source_data_path)
    before = capture_setup_diagnostics(solver, "source case before write-settings")
    print_setup_diagnostics(before)

    print_header("Write Settings File")
    remote_chdir(solver, _parent_dir(settings_path))
    command_result = _run_with_fallback(
        "tui_write_settings",
        lambda: _write_settings_tui(solver, settings_path),
        "fallback_write_settings",
        lambda: _write_settings_fallback(solver, settings_path),
    )

    if not remote_file_exists(solver, settings_path):
        raise FileNotFoundError(f"Fluent did not create settings file: {settings_path}")

    return {
        "settings_path": settings_path,
        "source_case_path": source_case_path,
        "source_data_path": source_data_path,
        "diagnostics": before,
        "command": command_result,
    }


def read_settings_file_onto_mesh(
    solver: Any,
    mesh_path: str,
    settings_path: str,
    output_case_path: str | None = None,
) -> dict[str, Any]:
    """Load a mesh, read Fluent settings onto it, and optionally write a case."""

    require_remote_input(solver, settings_path, "settings file")
    _read_mesh(solver, mesh_path)
    after_mesh = capture_setup_diagnostics(solver, "target mesh before read-settings")
    print_setup_diagnostics(after_mesh)

    print_header("Read Settings File")
    remote_chdir(solver, _parent_dir(settings_path))
    command_result = _run_with_fallback(
        "tui_read_settings",
        lambda: _read_settings_tui(solver, settings_path),
        "fallback_read_settings",
        lambda: _read_settings_fallback(solver, settings_path),
    )

    after_settings = capture_setup_diagnostics(solver, "target mesh after read-settings")
    print_setup_diagnostics(after_settings)
    _write_case_if_requested(solver, output_case_path)

    return {
        "mesh_path": mesh_path,
        "settings_path": settings_path,
        "output_case_path": output_case_path,
        "diagnostics": {
            "after_mesh": after_mesh,
            "after_settings": after_settings,
        },
        "command": command_result,
    }


def transfer_settings_to_mesh(
    solver: Any,
    source_case_path: str,
    mesh_path: str,
    settings_path: str,
    output_case_path: str | None = None,
    source_data_path: str | None = None,
) -> dict[str, Any]:
    """Write settings from a source case and read them onto a target mesh."""

    write_result = write_settings_file(
        solver,
        source_case_path=source_case_path,
        settings_path=settings_path,
        source_data_path=source_data_path,
    )
    read_result = read_settings_file_onto_mesh(
        solver,
        mesh_path=mesh_path,
        settings_path=settings_path,
        output_case_path=output_case_path,
    )
    return {
        "write": write_result,
        "read": read_result,
    }

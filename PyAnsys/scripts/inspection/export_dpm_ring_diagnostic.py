#!/usr/bin/env python3
"""Export DPM particle-track diagnostics for the suspected top-ring hangup.

The script targets the saved Purnanto enthalpy cases and creates Fluent
particle-track graphics for the high-incomplete-mass injections.  It saves the
graphics and, when Fluent provides it, a particle-history/report file on the
Windows Fluent host, then copies small artifacts back to the local Mac output
folder.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SETUP_SCRIPTS = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SETUP_SCRIPTS))

from pyansys_fluent.common import (  # noqa: E402
    quote_scheme_string,
    remote_file_exists,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.setup_common import print_header  # noqa: E402

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
from run_purnanto_dpm_sensitivity import (  # noqa: E402
    default_case_data_paths,
    load_case_data,
    single_case_plan,
)


DEFAULT_INJECTIONS = ("injection-5", "injection-6", "injection-7", "injection-8")
DEFAULT_PARTICLE_FIELD = "particle-resid-time"
DEFAULT_LOCAL_OUTPUT_DIR = sweep.DEFAULT_LOCAL_OUTPUT_DIR / "ring_diagnostic"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create DPM particle-track graphics/history for the suspected top-ring particle hangup."
    )
    parser.add_argument("--server-id", default="1", help="Configured Fluent server id. Default: 1.")
    parser.add_argument("--case-filter", default="1600", help="Paper case selector. Default: 1600.")
    parser.add_argument(
        "--resume-case",
        default="",
        help="Remote case file. Defaults to selected case final 1500-iteration case.",
    )
    parser.add_argument(
        "--resume-data",
        default="",
        help="Remote data file. Defaults to selected case final 1500-iteration data.",
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
        default=str(DEFAULT_LOCAL_OUTPUT_DIR),
        help="Local folder for copied artifacts and manifests.",
    )
    parser.add_argument(
        "--label",
        default="top_ring_diagnostic",
        help="Output label suffix.",
    )
    parser.add_argument(
        "--injections",
        default=",".join(DEFAULT_INJECTIONS),
        help="Comma-separated DPM injections to display. Default: injection-5..injection-8.",
    )
    parser.add_argument(
        "--mesh-surfaces",
        default="auto",
        help="Comma-separated wall/surface names to draw as mesh, or 'auto'. Default: auto.",
    )
    parser.add_argument(
        "--particle-field",
        default=DEFAULT_PARTICLE_FIELD,
        help=f"Field used to color particle tracks. Default: {DEFAULT_PARTICLE_FIELD}.",
    )
    parser.add_argument(
        "--filter-field",
        default=DEFAULT_PARTICLE_FIELD,
        help=f"Field used for the high-residence-time filter. Default: {DEFAULT_PARTICLE_FIELD}.",
    )
    parser.add_argument(
        "--filter-min",
        type=float,
        default=60.0,
        help="Minimum filter value for the high-residence-time object. Default: 60 seconds.",
    )
    parser.add_argument(
        "--filter-max",
        type=float,
        default=1.0e9,
        help="Maximum filter value. Default: 1e9.",
    )
    parser.add_argument("--no-filter", action="store_true", help="Do not create the filtered track object.")
    parser.add_argument("--coarsen", type=int, default=4, help="Particle-track coarsening factor. Default: 4.")
    parser.add_argument("--skip", type=int, default=0, help="Particle-track skip count. Default: 0.")
    parser.add_argument("--line-width", type=float, default=2.0, help="Particle-track line width. Default: 2.")
    parser.add_argument("--x-resolution", type=int, default=1800, help="Saved picture x resolution. Default: 1800.")
    parser.add_argument("--y-resolution", type=int, default=1200, help="Saved picture y resolution. Default: 1200.")
    parser.add_argument(
        "--track-object-name",
        default="top_ring_dpm_tracks",
        help="Fluent particle-track graphics object name.",
    )
    parser.add_argument(
        "--filtered-track-object-name",
        default="top_ring_high_time_dpm_tracks",
        help="Fluent filtered particle-track graphics object name.",
    )
    parser.add_argument(
        "--mesh-object-name",
        default="top_ring_wall_mesh",
        help="Fluent mesh graphics object name.",
    )
    parser.add_argument(
        "--probe-only",
        action="store_true",
        help="Connect and print available graphics settings without displaying/saving tracks.",
    )
    parser.add_argument(
        "--load-case-data",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Read the selected saved case/data before exporting. Default: yes.",
    )
    parser.add_argument(
        "--run-dpm-update",
        action="store_true",
        help="Run /solve/dpm-update before making graphics. Default: false.",
    )
    parser.add_argument(
        "--save-history",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Best-effort particle-track history/report file on the remote host. Default: yes.",
    )
    parser.add_argument(
        "--copy-remote-files",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Copy small remote artifacts back to the local output folder. Default: yes.",
    )
    parser.add_argument(
        "--max-copy-mb",
        type=float,
        default=25.0,
        help="Skip copying remote artifacts larger than this size. Default: 25 MB.",
    )
    parser.add_argument(
        "--pulse-formats",
        default="hsf,glb,avz,usd",
        help="Comma-separated Pulse export formats to try for particle tracks. Default: hsf,glb,avz,usd.",
    )
    parser.add_argument(
        "--xy-plots",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Write filtered particle-track XY plot data files when possible. Default: yes.",
    )
    parser.add_argument(
        "--xy-x-fields",
        default="particle-radial-position,particle-x-position,particle-y-position,particle-resid-time",
        help="Comma-separated X-axis fields for XY plot exports. Default: radial,x,y,residence-time.",
    )
    parser.add_argument(
        "--xy-y-field",
        default="particle-z-position",
        help="Y-axis particle field for XY plot exports. Default: particle-z-position.",
    )
    return parser


def split_csv(text: str) -> list[str]:
    return [part.strip() for part in text.split(",") if part.strip()]


def local_output_dir(path_text: str) -> Path:
    path = Path(path_text).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def call_capture(label: str, func: Callable[[], Any]) -> dict[str, Any]:
    print(f"{label}: starting")
    try:
        result = func()
        print(f"{label}: OK")
        return {"ok": True, "result": result}
    except Exception as exc:
        print(f"{label}: FAILED -> {type(exc).__name__}: {exc}")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def object_names(branch: Any) -> list[str]:
    try:
        return [str(name) for name in branch.get_object_names()]
    except Exception:
        return []


def boundary_names(boundary_state: Any, boundary_type: str) -> list[str]:
    if not isinstance(boundary_state, Mapping):
        return []
    values = boundary_state.get(boundary_type, {})
    if not isinstance(values, Mapping):
        return []
    return sorted(str(name) for name in values if str(name) != "settings")


def auto_mesh_surfaces(solver: Any) -> list[str]:
    boundary_state = safe_get_state(solver.settings.setup.boundary_conditions, "boundary_conditions")
    wall_names = boundary_names(boundary_state, "wall")
    if wall_names:
        return wall_names

    candidates: list[str] = []
    for boundary_type in ("wall", "pressure_outlet", "mass_flow_inlet", "velocity_inlet"):
        candidates.extend(boundary_names(boundary_state, boundary_type))
    return sorted(dict.fromkeys(candidates))


def create_named_object(branch: Any, name: str) -> tuple[Any, list[dict[str, Any]]]:
    actions: list[dict[str, Any]] = []
    names = object_names(branch)
    if name not in names:
        create_action = call_capture(f"create_{name}", lambda: branch.create(name=name))
        actions.append(create_action)
        if not create_action.get("ok"):
            actions.append(call_capture(f"assign_empty_{name}", lambda: branch.__setitem__(name, {})))
    return branch[name], actions


def set_attr_best_effort(obj: Any, attr: str, value: Any, label: str) -> dict[str, Any]:
    return call_capture(label, lambda: setattr(obj, attr, value))


def set_state_best_effort(obj: Any, state: Mapping[str, Any], label: str) -> dict[str, Any]:
    return call_capture(label, lambda: obj.set_state(dict(state)))


def first_existing_child(obj: Any, names: Sequence[str]) -> tuple[str, Any] | tuple[str, None]:
    for name in names:
        try:
            return name, getattr(obj, name)
        except AttributeError:
            continue
        except Exception:
            continue
    return "", None


def allowed_values_best_effort(obj: Any) -> list[str]:
    try:
        if hasattr(obj, "allowed_values"):
            return list(obj.allowed_values())
    except Exception:
        return []
    return []


def command_arg_allowed_values(command: Any, arg_name: str) -> list[str]:
    try:
        return allowed_values_best_effort(getattr(command, arg_name))
    except Exception:
        return []


def child_allowed_values(parent: Any, child_name: str) -> list[str]:
    try:
        return allowed_values_best_effort(getattr(parent, child_name))
    except Exception:
        return []


def command_child_arg_allowed_values(parent: Any, command_name: str, arg_name: str) -> list[str]:
    try:
        command = getattr(parent, command_name)
    except Exception:
        return []
    return command_arg_allowed_values(command, arg_name)


def particle_field_name(track: Any, requested: str) -> str:
    allowed = allowed_values_best_effort(track.field)
    if not allowed or requested in allowed:
        return requested
    aliases = {
        "particle-time": "particle-resid-time",
        "particle-residence-time": "particle-resid-time",
        "residence-time": "particle-resid-time",
    }
    replacement = aliases.get(requested)
    if replacement and replacement in allowed:
        print(f"field_alias: {requested} -> {replacement}")
        return replacement
    return requested


def configure_track_filter(
    track: Any,
    *,
    filter_field: str,
    filter_min: float,
    filter_max: float,
    label: str,
) -> dict[str, Any]:
    branch_name, branch = first_existing_child(track, ("filter_setting", "filter_settings"))
    if branch is None:
        return {"ok": False, "error": "No particle-track filter settings branch found"}

    if branch_name == "filter_setting":
        state = {
            "enabled": True,
            "field": filter_field,
            "option": True,
            "range": {"minimum": filter_min, "maximum": filter_max},
        }
    else:
        state = {
            "enabled": True,
            "field": filter_field,
            "options": {"inside": True, "outside": False},
            "filter_minimum": filter_min,
            "filter_maximum": filter_max,
        }
    result = set_state_best_effort(branch, state, label)
    result["branch"] = branch_name
    return result


def configure_picture(solver: Any, args: argparse.Namespace) -> list[dict[str, Any]]:
    picture = solver.settings.results.graphics.picture
    return [
        set_attr_best_effort(picture, "use_window_resolution", False, "picture_use_window_resolution_false"),
        set_attr_best_effort(picture, "x_resolution", args.x_resolution, "picture_x_resolution"),
        set_attr_best_effort(picture, "y_resolution", args.y_resolution, "picture_y_resolution"),
        set_attr_best_effort(picture, "dpi", 150, "picture_dpi"),
        set_attr_best_effort(picture, "invert_background", False, "picture_invert_background_false"),
        set_attr_best_effort(picture.driver_options, "hardcopy_format", "png", "picture_hardcopy_format_png"),
    ]


def configure_mesh_object(
    solver: Any,
    *,
    mesh_name: str,
    surfaces: Sequence[str],
) -> tuple[Any, list[dict[str, Any]]]:
    graphics = solver.settings.results.graphics
    mesh, actions = create_named_object(graphics.mesh, mesh_name)
    if surfaces:
        actions.append(set_attr_best_effort(mesh, "surfaces_list", list(surfaces), "mesh_surfaces_list"))
    actions.append(call_capture("mesh_state", lambda: safe_get_state(mesh, "mesh_object")))
    return mesh, actions


def configure_particle_track_object(
    solver: Any,
    *,
    name: str,
    injections: Sequence[str],
    mesh_name: str,
    particle_field: str,
    coarsen: int,
    skip: int,
    line_width: float,
    filter_field: str | None = None,
    filter_min: float | None = None,
    filter_max: float | None = None,
) -> tuple[Any, list[dict[str, Any]]]:
    graphics = solver.settings.results.graphics
    track, actions = create_named_object(graphics.particle_track, name)
    particle_field = particle_field_name(track, particle_field)
    if filter_field:
        filter_field = particle_field_name(track, filter_field)

    actions.extend(
        [
            set_attr_best_effort(track, "injections_list", list(injections), f"{name}_injections"),
            set_attr_best_effort(track, "field", particle_field, f"{name}_field"),
            set_attr_best_effort(track, "draw_mesh", True, f"{name}_draw_mesh"),
            set_attr_best_effort(track, "mesh_object", mesh_name, f"{name}_mesh_object"),
            set_attr_best_effort(track, "free_stream_particles", True, f"{name}_free_stream_particles"),
            set_attr_best_effort(track, "wall_film_particles", True, f"{name}_wall_film_particles"),
            set_attr_best_effort(track, "track_pdf_particles", False, f"{name}_track_pdf_particles_false"),
            set_attr_best_effort(track, "skip", skip, f"{name}_skip"),
            set_attr_best_effort(track, "coarsen", coarsen, f"{name}_coarsen"),
            set_state_best_effort(
                track.style_attribute,
                {"style": "line", "line_width": line_width, "marker_size": 0.03},
                f"{name}_style_attribute",
            ),
            set_state_best_effort(
                track.color_map,
                {"visible": True, "size": 12, "show_all": False},
                f"{name}_color_map",
            ),
        ]
    )

    if filter_field and filter_min is not None and filter_max is not None:
        actions.append(
            configure_track_filter(
                track,
                filter_field=filter_field,
                filter_min=filter_min,
                filter_max=filter_max,
                label=f"{name}_filter_setting",
            )
        )

    actions.append(call_capture(f"{name}_state", lambda: safe_get_state(track, name)))
    return track, actions


def display_graphics_object(solver: Any, *, mesh_name: str, track_name: str) -> list[dict[str, Any]]:
    graphics = solver.settings.results.graphics
    actions = [
        call_capture("display_mesh_object", lambda: graphics.mesh.display(object_name=mesh_name)),
        call_capture("add_track_to_graphics", lambda: graphics.particle_track.add_to_graphics(object_name=track_name)),
    ]
    if not any(action.get("ok") for action in actions[-1:]):
        actions.append(call_capture("display_track_object", lambda: graphics.particle_track.display(object_name=track_name)))
    if not any(action.get("ok") for action in actions[-2:]):
        actions.append(call_capture("display_track_child", lambda: graphics.particle_track[track_name].display()))
    return actions


def save_picture(solver: Any, remote_png: str) -> dict[str, Any]:
    attempts = [
        call_capture(
            "save_picture_settings_api",
            lambda: solver.settings.results.graphics.picture.save_picture(file_name=remote_png),
        ),
        call_capture("save_picture_tui_display", lambda: solver.tui.display.save_picture(remote_png)),
        call_capture("save_picture_tui_set_picture", lambda: solver.tui.display.set.picture.save_picture(remote_png)),
    ]
    return {"ok": any(attempt.get("ok") for attempt in attempts), "attempts": attempts}


def pulse_extension(write_format: str) -> str:
    return {
        "hsf": ".hsf",
        "glb": ".glb",
        "avz": ".avz",
        "usd": ".usd",
        "usda": ".usda",
        "usdc": ".usdc",
    }.get(write_format.lower(), f".{write_format.lower()}")


def save_pulse_exports(
    solver: Any,
    *,
    object_name: str,
    remote_output_dir: str,
    prefix: str,
    formats: Sequence[str],
) -> dict[str, Any]:
    try:
        pulse = solver.settings.results.graphics.pulse
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "exports": {}}
    exports: dict[str, Any] = {}
    for write_format in formats:
        clean_format = write_format.strip().lower()
        if not clean_format:
            continue
        remote_file = sweep.remote_join(
            remote_output_dir,
            f"{prefix}_{object_name}_pulse{pulse_extension(clean_format)}",
        )
        result = call_capture(
            f"pulse_write_{object_name}_{clean_format}",
            lambda fmt=clean_format, path=remote_file: pulse.write(
                object_name=object_name,
                write_format=fmt,
                file_name=path,
            ),
        )
        result["remote_path"] = remote_file
        exports[clean_format] = result
    return {"ok": any(result.get("ok") for result in exports.values()), "exports": exports}


def slug_field_name(field: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in field).strip("_")


def configure_xy_plot(track: Any, *, x_field: str, y_field: str, remote_file: str, label: str) -> list[dict[str, Any]]:
    return [
        set_attr_best_effort(track, "field", y_field, f"{label}_field_{y_field}"),
        set_attr_best_effort(track.plot, "enabled", True, f"{label}_plot_enabled"),
        set_attr_best_effort(track.plot, "x_axis_function", x_field, f"{label}_plot_x_axis_{x_field}"),
        set_attr_best_effort(track.plot, "to_file_enabled", True, f"{label}_plot_to_file_enabled"),
        set_attr_best_effort(track.plot, "file_name", remote_file, f"{label}_plot_file_name"),
        call_capture(f"{label}_plot_state", lambda: safe_get_state(track.plot, f"{label}.plot")),
    ]


def save_filtered_xy_plot_exports(
    solver: Any,
    *,
    base_name: str,
    injections: Sequence[str],
    mesh_name: str,
    x_fields: Sequence[str],
    y_field: str,
    filter_field: str,
    filter_min: float,
    filter_max: float,
    coarsen: int,
    skip: int,
    line_width: float,
    remote_output_dir: str,
    prefix: str,
) -> dict[str, Any]:
    exports: dict[str, Any] = {}
    for x_field in x_fields:
        clean_x = x_field.strip()
        if not clean_x:
            continue
        object_name = f"{base_name}_{slug_field_name(y_field)}_vs_{slug_field_name(clean_x)}"
        remote_file = sweep.remote_join(remote_output_dir, f"{prefix}_{object_name}.xy")
        track, actions = configure_particle_track_object(
            solver,
            name=object_name,
            injections=injections,
            mesh_name=mesh_name,
            particle_field=y_field,
            coarsen=coarsen,
            skip=skip,
            line_width=line_width,
            filter_field=filter_field,
            filter_min=filter_min,
            filter_max=filter_max,
        )
        actions.extend(configure_xy_plot(track, x_field=clean_x, y_field=y_field, remote_file=remote_file, label=object_name))
        actions.append(call_capture(f"{object_name}_display", lambda name=object_name: solver.settings.results.graphics.particle_track.display(object_name=name)))
        actions.append(call_capture(f"{object_name}_display_child", lambda obj=track: obj.display()))
        exports[clean_x] = {"remote_path": remote_file, "actions": actions}
    return {"ok": True, "exports": exports}


def run_dpm_update_if_requested(solver: Any, enabled: bool) -> dict[str, Any] | None:
    if not enabled:
        print("dpm_update: SKIPPED")
        return None
    return call_capture("solve_dpm_update", lambda: sweep.ti_menu(solver, "/solve/dpm-update"))


def ps_quote(path_text: str) -> str:
    return path_text.replace("'", "''")


def remote_system(solver: Any, command: str) -> Any:
    return solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')


def remote_file_size(solver: Any, remote_path: str, remote_output_dir: str) -> int | None:
    if not remote_file_exists(solver, remote_path):
        return None
    scratch = sweep.remote_join(remote_output_dir, "_codex_file_size.txt")
    command = (
        "powershell -NoProfile -ExecutionPolicy Bypass -Command "
        f"\"(Get-Item -LiteralPath '{ps_quote(remote_path)}').Length | "
        f"Set-Content -NoNewline -Encoding ASCII '{ps_quote(scratch)}'\""
    )
    try:
        remote_system(solver, command)
        text = sweep.remote_text_read_best_effort(solver, scratch).strip()
        return int(text) if text else None
    except Exception as exc:
        print(f"remote_file_size: FAILED for {remote_path} -> {exc}")
        return None


def copy_remote_binary(
    solver: Any,
    *,
    remote_path: str,
    local_path: Path,
    remote_output_dir: str,
    max_bytes: int,
) -> dict[str, Any]:
    size = remote_file_size(solver, remote_path, remote_output_dir)
    if size is None:
        return {"ok": False, "remote_path": remote_path, "local_path": str(local_path), "error": "remote file missing"}
    if size > max_bytes:
        return {
            "ok": False,
            "remote_path": remote_path,
            "local_path": str(local_path),
            "size_bytes": size,
            "error": f"remote file exceeds copy limit {max_bytes} bytes",
        }

    encoded = sweep.remote_join(remote_output_dir, f"{PureWindowsPath(remote_path).name}.b64.txt")
    command = (
        "powershell -NoProfile -ExecutionPolicy Bypass -Command "
        f"\"[Convert]::ToBase64String([IO.File]::ReadAllBytes('{ps_quote(remote_path)}')) | "
        f"Set-Content -NoNewline -Encoding ASCII '{ps_quote(encoded)}'\""
    )
    try:
        remote_system(solver, command)
        text = sweep.remote_text_read_best_effort(solver, encoded).strip()
        if not text:
            return {"ok": False, "remote_path": remote_path, "local_path": str(local_path), "error": "empty base64"}
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_bytes(base64.b64decode(text))
        return {
            "ok": True,
            "remote_path": remote_path,
            "local_path": str(local_path),
            "size_bytes": size,
        }
    except Exception as exc:
        return {
            "ok": False,
            "remote_path": remote_path,
            "local_path": str(local_path),
            "size_bytes": size,
            "error": f"{type(exc).__name__}: {exc}",
        }


def copy_remote_text(
    solver: Any,
    *,
    remote_path: str,
    local_path: Path,
    remote_output_dir: str,
    max_bytes: int,
) -> dict[str, Any]:
    size = remote_file_size(solver, remote_path, remote_output_dir)
    if size is None:
        return {"ok": False, "remote_path": remote_path, "local_path": str(local_path), "error": "remote file missing"}
    if size > max_bytes:
        return {
            "ok": False,
            "remote_path": remote_path,
            "local_path": str(local_path),
            "size_bytes": size,
            "error": f"remote file exceeds copy limit {max_bytes} bytes",
        }
    text = sweep.remote_text_read_best_effort(solver, remote_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(text, encoding="utf-8", errors="replace")
    return {
        "ok": True,
        "remote_path": remote_path,
        "local_path": str(local_path),
        "size_bytes": size,
    }


def configure_history_reporting(solver: Any, history_file: str) -> list[dict[str, Any]]:
    graphics = solver.settings.results.graphics
    actions = [
        set_attr_best_effort(graphics.particle_tracks, "history_filename", history_file, "history_filename"),
        call_capture("history_report_default_variables", lambda: graphics.particle_tracks.report_default_variables()),
    ]
    # These TUI settings expose more knobs in some Fluent versions.
    actions.extend(
        [
            call_capture(
                "tui_history_filename",
                lambda: solver.tui.display.set.particle_tracks.history_filename(history_file),
            ),
            call_capture("tui_report_to_file", lambda: solver.tui.display.set.particle_tracks.report_to("file")),
            call_capture("tui_report_type_step", lambda: solver.tui.display.set.particle_tracks.report_type("step")),
            call_capture(
                "tui_report_default_variables",
                lambda: solver.tui.display.set.particle_tracks.report_default_variables(),
            ),
        ]
    )
    return actions


def probe_settings(solver: Any, track_name: str) -> dict[str, Any]:
    graphics = solver.settings.results.graphics
    track, create_actions = create_named_object(graphics.particle_track, track_name)
    filter_branch_name, filter_branch = first_existing_child(track, ("filter_setting", "filter_settings"))
    filter_field = None
    if filter_branch is not None:
        _field_name, filter_field = first_existing_child(filter_branch, ("field",))
    return {
        "create_actions": create_actions,
        "boundary_conditions": safe_get_state(solver.settings.setup.boundary_conditions, "boundary_conditions"),
        "mesh_object_names": object_names(graphics.mesh),
        "particle_track_object_names": object_names(graphics.particle_track),
        "particle_track_state": safe_get_state(track, track_name),
        "particle_field_allowed_values": allowed_values_best_effort(track.field),
        "injections_allowed_values": allowed_values_best_effort(track.injections_list),
        "mesh_object_allowed_values": allowed_values_best_effort(track.mesh_object),
        "filter_branch_name": filter_branch_name,
        "filter_field_allowed_values": allowed_values_best_effort(filter_field) if filter_field is not None else [],
        "style_allowed_values": allowed_values_best_effort(track.style_attribute.style),
        "hardcopy_format_allowed_values": allowed_values_best_effort(
            graphics.picture.driver_options.hardcopy_format
        ),
        "pulse_state": safe_get_state(graphics.pulse, "graphics.pulse"),
        "pulse_mode_allowed_values": child_allowed_values(graphics.pulse, "pulse_mode"),
        "pulse_write_format_allowed_values": command_child_arg_allowed_values(graphics.pulse, "write", "write_format"),
        "plot_x_axis_allowed_values": child_allowed_values(track.plot, "x_axis_function"),
    }


def capture_existing_dpm_summary(solver: Any) -> str:
    report = solver.settings.results.report.discrete_phase
    parts = [
        sweep.capture_call("settings_dpm_summary_existing", lambda: report.summary()),
        sweep.capture_call(
            "settings_dpm_extended_summary_existing",
            lambda: report.extended_summary(
                write_to_file=False,
                include_in_domain_particles=True,
                pick_injection=False,
            ),
        ),
        sweep.capture_call("tui_particle_summary_existing", lambda: solver.tui.report.particle_summary()),
    ]
    return "\n".join(parts)


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv()

    case, _bins = single_case_plan(args.case_filter, Path(args.harwell_csv).expanduser().resolve())
    prefix = f"{sweep.case_prefix(case)}_{sweep.slugify(args.label)}"
    output_dir = local_output_dir(args.local_output_dir)

    resume_case, resume_data = args.resume_case, args.resume_data
    if not resume_case and not resume_data:
        resume_case, resume_data = default_case_data_paths(case, args.remote_output_dir)
    if args.load_case_data and not (resume_case and resume_data):
        raise ValueError("--resume-case and --resume-data must be supplied together")

    solver = connect(server_id=args.server_id)
    print(f"\nConnected to Fluent {solver.get_fluent_version()}")
    sweep.ensure_remote_directory_best_effort(solver, args.remote_output_dir)
    if args.load_case_data:
        load_case_data(solver, resume_case, resume_data)
        sweep.require_current_case_shape(solver)
    else:
        print("load_case_data: SKIPPED; using current Fluent state")

    injections = split_csv(args.injections)
    mesh_surfaces = auto_mesh_surfaces(solver) if args.mesh_surfaces.strip().lower() == "auto" else split_csv(args.mesh_surfaces)

    manifest: dict[str, Any] = {
        "case": case.csv_case,
        "condition": case.condition,
        "prefix": prefix,
        "source_case": resume_case,
        "source_data": resume_data,
        "injections": injections,
        "mesh_surfaces": mesh_surfaces,
        "remote_output_dir": args.remote_output_dir,
        "local_output_dir": str(output_dir),
        "probe": probe_settings(solver, f"{args.track_object_name}_probe"),
        "actions": {},
        "artifacts": {},
    }

    if args.probe_only:
        local_manifest = output_dir / f"{prefix}_probe_manifest.json"
        local_manifest.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
        print_header("Probe Complete")
        print(f"local_manifest: {local_manifest}")
        return 0

    remote_png = sweep.remote_join(args.remote_output_dir, f"{prefix}.png")
    remote_filtered_png = sweep.remote_join(args.remote_output_dir, f"{prefix}_high_time.png")
    remote_history = sweep.remote_join(args.remote_output_dir, f"{prefix}_particle_history.txt")
    pulse_formats = split_csv(args.pulse_formats)
    xy_x_fields = split_csv(args.xy_x_fields)

    print_header("Configure Graphics")
    _mesh, mesh_actions = configure_mesh_object(solver, mesh_name=args.mesh_object_name, surfaces=mesh_surfaces)
    _track, track_actions = configure_particle_track_object(
        solver,
        name=args.track_object_name,
        injections=injections,
        mesh_name=args.mesh_object_name,
        particle_field=args.particle_field,
        coarsen=args.coarsen,
        skip=args.skip,
        line_width=args.line_width,
    )
    manifest["actions"]["mesh"] = mesh_actions
    manifest["actions"]["track"] = track_actions

    if args.save_history:
        manifest["actions"]["history_setup"] = configure_history_reporting(solver, remote_history)

    run_update_result = run_dpm_update_if_requested(solver, args.run_dpm_update)
    if run_update_result is not None:
        manifest["actions"]["dpm_update"] = run_update_result

    manifest["actions"]["picture_setup"] = configure_picture(solver, args)

    print_header("Display And Save Unfiltered Tracks")
    manifest["actions"]["display_unfiltered"] = display_graphics_object(
        solver,
        mesh_name=args.mesh_object_name,
        track_name=args.track_object_name,
    )
    manifest["actions"]["save_unfiltered_png"] = save_picture(solver, remote_png)
    manifest["actions"]["pulse_unfiltered"] = save_pulse_exports(
        solver,
        object_name=args.track_object_name,
        remote_output_dir=args.remote_output_dir,
        prefix=prefix,
        formats=pulse_formats,
    )
    manifest["artifacts"]["remote_png"] = remote_png

    if not args.no_filter:
        print_header("Display And Save High-Time Tracks")
        _filtered_track, filtered_actions = configure_particle_track_object(
            solver,
            name=args.filtered_track_object_name,
            injections=injections,
            mesh_name=args.mesh_object_name,
            particle_field=args.particle_field,
            coarsen=args.coarsen,
            skip=args.skip,
            line_width=args.line_width,
            filter_field=args.filter_field,
            filter_min=args.filter_min,
            filter_max=args.filter_max,
        )
        manifest["actions"]["filtered_track"] = filtered_actions
        manifest["actions"]["display_filtered"] = display_graphics_object(
            solver,
            mesh_name=args.mesh_object_name,
            track_name=args.filtered_track_object_name,
        )
        manifest["actions"]["save_filtered_png"] = save_picture(solver, remote_filtered_png)
        manifest["actions"]["pulse_filtered"] = save_pulse_exports(
            solver,
            object_name=args.filtered_track_object_name,
            remote_output_dir=args.remote_output_dir,
            prefix=prefix,
            formats=pulse_formats,
        )
        manifest["artifacts"]["remote_filtered_png"] = remote_filtered_png
        if args.xy_plots:
            print_header("Write Filtered XY Plot Data")
            manifest["actions"]["filtered_xy_plots"] = save_filtered_xy_plot_exports(
                solver,
                base_name=f"{args.filtered_track_object_name}_xy",
                injections=injections,
                mesh_name=args.mesh_object_name,
                x_fields=xy_x_fields,
                y_field=args.xy_y_field,
                filter_field=args.filter_field,
                filter_min=args.filter_min,
                filter_max=args.filter_max,
                coarsen=args.coarsen,
                skip=args.skip,
                line_width=args.line_width,
                remote_output_dir=args.remote_output_dir,
                prefix=prefix,
            )

    print_header("Report DPM Summary")
    report_text = capture_existing_dpm_summary(solver)
    local_report = output_dir / f"{prefix}_dpm_report.txt"
    sweep.write_local_text(local_report, report_text)
    manifest["artifacts"]["local_dpm_report"] = str(local_report)

    if args.copy_remote_files:
        max_bytes = int(args.max_copy_mb * 1024 * 1024)
        copy_results: dict[str, Any] = {}
        copy_results["png"] = copy_remote_binary(
            solver,
            remote_path=remote_png,
            local_path=output_dir / Path(PureWindowsPath(remote_png).name),
            remote_output_dir=args.remote_output_dir,
            max_bytes=max_bytes,
        )
        if not args.no_filter:
            copy_results["filtered_png"] = copy_remote_binary(
                solver,
                remote_path=remote_filtered_png,
                local_path=output_dir / Path(PureWindowsPath(remote_filtered_png).name),
                remote_output_dir=args.remote_output_dir,
                max_bytes=max_bytes,
            )
        if args.save_history:
            copy_results["history"] = copy_remote_text(
                solver,
                remote_path=remote_history,
                local_path=output_dir / Path(PureWindowsPath(remote_history).name),
                remote_output_dir=args.remote_output_dir,
                max_bytes=max_bytes,
            )
        for action_key in ("pulse_unfiltered", "pulse_filtered"):
            action = manifest["actions"].get(action_key, {})
            if not isinstance(action, Mapping):
                continue
            exports = action.get("exports", {})
            if not isinstance(exports, Mapping):
                continue
            for write_format, result in exports.items():
                if not isinstance(result, Mapping):
                    continue
                remote_path = result.get("remote_path")
                if not remote_path:
                    continue
                copy_results[f"{action_key}_{write_format}"] = copy_remote_binary(
                    solver,
                    remote_path=str(remote_path),
                    local_path=output_dir / Path(PureWindowsPath(str(remote_path)).name),
                    remote_output_dir=args.remote_output_dir,
                    max_bytes=max_bytes,
                )
        xy_action = manifest["actions"].get("filtered_xy_plots", {})
        xy_exports = xy_action.get("exports", {}) if isinstance(xy_action, Mapping) else {}
        if isinstance(xy_exports, Mapping):
            for x_field, result in xy_exports.items():
                if not isinstance(result, Mapping):
                    continue
                remote_path = result.get("remote_path")
                if not remote_path:
                    continue
                copy_results[f"filtered_xy_{slug_field_name(str(x_field))}"] = copy_remote_text(
                    solver,
                    remote_path=str(remote_path),
                    local_path=output_dir / Path(PureWindowsPath(str(remote_path)).name),
                    remote_output_dir=args.remote_output_dir,
                    max_bytes=max_bytes,
                )
        manifest["artifacts"]["copy_results"] = copy_results

    local_manifest = output_dir / f"{prefix}_manifest.json"
    local_manifest.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

    print_header("DPM Ring Diagnostic Complete")
    print(f"local_manifest: {local_manifest}")
    print(f"local_report: {local_report}")
    for key, result in manifest.get("artifacts", {}).get("copy_results", {}).items():
        if isinstance(result, Mapping):
            print(f"{key}: {'OK' if result.get('ok') else 'FAILED'} -> {result.get('local_path') or result.get('error')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

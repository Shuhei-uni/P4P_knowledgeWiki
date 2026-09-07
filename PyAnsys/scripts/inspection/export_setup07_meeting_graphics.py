#!/usr/bin/env python3
"""Export meeting graphics for the setup-07 split-inlet diagnostics.

The exporter is deliberately post-processing only.  It loads saved case/data
pairs, creates temporary Results graphics objects, and writes pictures.  It
does not initialize, iterate, update DPM, or write case/data files.

The matched closed-bottom comparison uses the same plane, camera, picture
resolution, phase-2 volume-fraction range, and pressure range at 4000 and
6000 steady-solver iterations.  Those iteration numbers are diagnostic solver
iterate counts, not physical time.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any, Callable, Mapping, Sequence

from dotenv import load_dotenv
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from pyansys_fluent.common import remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402

from export_dpm_ring_diagnostic import (  # noqa: E402
    copy_remote_binary,
    remote_file_size,
    remote_system,
)


LOCAL_OUTPUT = PROJECT_ROOT / "output" / "setup07_meeting_visuals_20260811" / "fluent"
REMOTE_OUTPUT = r"C:\Users\qtra338\Documents\Mesh study\setup07_meeting_visuals_20260811"

REMOTE_MESH_ROOT = r"C:\Users\qtra338\Documents\Mesh study\split_inlet_mesh_convergence_20260801\mesh_900k"
REMOTE_SINK_ROOT = (
    r"C:\Users\qtra338\Documents\Mesh study\split_inlet_thickened_water_level_sink_20260808"
    r"\mesh-900k_band0p140165_tau0p100_v1"
)
SETUP07E_MANIFEST = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_mass_balance_sink_control_20260810"
    / "mesh-900k_band0p140165_target116p92_v1"
    / "qualification_manifest.json"
)


@dataclass(frozen=True)
class SavedState:
    key: str
    title: str
    case: str
    data: str
    export_boundary: bool = False
    export_sink_mask: bool = False
    export_pathlines: bool = False


SAVED_STATES: dict[str, SavedState] = {
    "sink07c": SavedState(
        key="sink07c",
        title="Setup 07c thick-sink full-strength endpoint",
        case=REMOTE_SINK_ROOT + r"\r1_iter2000_cumulative3000_resume.cas.h5",
        data=REMOTE_SINK_ROOT + r"\r1_iter2000_cumulative3000_resume.dat.h5",
        export_boundary=True,
        export_sink_mask=True,
        export_pathlines=True,
    ),
    "closed3000": SavedState(
        key="closed3000",
        title="Setup 07a closed-bottom 900k at iteration 3000",
        case=REMOTE_MESH_ROOT + r"\mesh-900k_iter3000_final.cas.h5",
        data=REMOTE_MESH_ROOT + r"\mesh-900k_iter3000_final.dat.h5",
    ),
    "closed4000": SavedState(
        key="closed4000",
        title="Setup 07a closed-bottom 900k at iteration 4000",
        case=REMOTE_MESH_ROOT + r"\mesh-900k_iter4000_iteration_diagnostic1.cas.h5",
        data=REMOTE_MESH_ROOT + r"\mesh-900k_iter4000_iteration_diagnostic1.dat.h5",
    ),
    "closed6000": SavedState(
        key="closed6000",
        title="Setup 07a closed-bottom 900k at iteration 6000",
        case=REMOTE_MESH_ROOT + r"\mesh-900k_iter6000_iteration_diagnostic3.cas.h5",
        data=REMOTE_MESH_ROOT + r"\mesh-900k_iter6000_iteration_diagnostic3.dat.h5",
        export_pathlines=True,
    ),
}

RESTORE_STATE = SavedState(
    key="sink07c_ramp_reset_final",
    title="Setup 07c saved ramp-reset final",
    case=REMOTE_SINK_ROOT + r"\diagnostic_resume_r1_2000_ramp_reset0.cas.h5",
    data=REMOTE_SINK_ROOT + r"\diagnostic_resume_r1_2000_ramp_reset0.dat.h5",
)
RESTORE_07E_STATE: SavedState | None = None


def register_setup07e_saved_state() -> None:
    """Register the latest preserved full-strength setup-07e checkpoint."""
    global RESTORE_07E_STATE
    if not SETUP07E_MANIFEST.exists():
        return
    manifest = json.loads(SETUP07E_MANIFEST.read_text(encoding="utf-8"))
    checkpoints = manifest.get("checkpoints", {})
    r1_keys = sorted(
        (key for key in checkpoints if key.startswith("r1_")),
        key=lambda value: int(value.split("_", 1)[1]),
    )
    if r1_keys:
        selected_key = r1_keys[-1]
        selected = checkpoints[selected_key]
        SAVED_STATES["sink07e"] = SavedState(
            key="sink07e",
            title=(
                "Setup 07e adaptive-sink preserved full-strength checkpoint "
                f"({selected_key.replace('_', '=')})"
            ),
            case=selected["case"],
            data=selected["data"],
            export_boundary=True,
            export_sink_mask=True,
            export_pathlines=True,
        )
    final = checkpoints.get("final")
    if final:
        RESTORE_07E_STATE = SavedState(
            key="sink07e_ramp_reset_final",
            title="Setup 07e saved ramp-reset final",
            case=final["case"],
            data=final["data"],
        )

PLANE_NAME = "meeting_longitudinal_xm1p5"
PLANE_X_M = -1.5
WINDOW_ID = 8
PICTURE_WIDTH = 1920
PICTURE_HEIGHT = 1440
PRESSURE_RANGE_PA = (1_100_000.0, 1_200_000.0)
VOLUME_FRACTION_RANGE = (0.0, 1.0)
VOLUME_FRACTION_ZOOM_RANGE = (0.0, 0.05)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--states",
        default="sink07c,closed4000,closed6000",
        help=(
            "Comma-separated saved states: sink07c, closed3000, closed4000, "
            "closed6000, and sink07e once its preserved R=1 checkpoint exists."
        ),
    )
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--local-output-dir", default=str(LOCAL_OUTPUT))
    parser.add_argument("--remote-output-dir", default=REMOTE_OUTPUT)
    parser.add_argument(
        "--restore-07c-final",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Restore the saved setup-07c ramp-reset final after exporting.",
    )
    parser.add_argument(
        "--restore-07e-final",
        action=argparse.BooleanOptionalAction,
        default=False,
        help=(
            "Restore the saved setup-07e ramp-reset final after exporting. "
            "Use with --no-restore-07c-final for setup-07e post-processing."
        ),
    )
    return parser


def capture(label: str, func: Callable[[], Any]) -> dict[str, Any]:
    try:
        result = func()
        print(f"[OK] {label}")
        return {"ok": True, "result": result}
    except Exception as exc:
        print(f"[WARN] {label}: {type(exc).__name__}: {exc}")
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def names(branch: Any) -> list[str]:
    try:
        return [str(value) for value in branch.get_object_names()]
    except Exception:
        return []


def remove_named(branch: Any, name: str) -> None:
    if name not in names(branch):
        return
    try:
        del branch[name]
    except Exception:
        branch.delete(name)


def recreate_named(branch: Any, name: str) -> Any:
    remove_named(branch, name)
    try:
        branch.create(name=name)
    except Exception:
        branch[name] = {}
    if name not in names(branch):
        raise RuntimeError(f"Fluent did not create graphics object {name!r}")
    return branch[name]


def readback_equals(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{label} readback mismatch: expected {expected!r}, got {actual!r}")


def ensure_remote_directory(solver: Any, remote_dir: str) -> None:
    escaped = remote_dir.replace("'", "''")
    command = (
        "powershell -NoProfile -ExecutionPolicy Bypass -Command "
        f'"New-Item -ItemType Directory -Force -Path \'{escaped}\' | Out-Null"'
    )
    remote_system(solver, command)


def verify_remote_pair(solver: Any, state: SavedState) -> None:
    for kind, path in (("case", state.case), ("data", state.data)):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"Missing remote {kind} for {state.key}: {path}")


def load_pair(solver: Any, state: SavedState) -> None:
    verify_remote_pair(solver, state)
    print(f"\nLoading {state.key}: {state.title}")
    solver.settings.file.read_case(file_name=state.case)
    solver.settings.file.read_data(file_name=state.data)
    print(f"Loaded {PureWindowsPath(state.case).name} and matching data; no iterations run.")


def dpm_interaction_state(solver: Any) -> dict[str, Any]:
    candidates = (
        (
            "setup.models.discrete_phase.general_settings.interaction",
            lambda: solver.settings.setup.models.discrete_phase.general_settings.interaction,
        ),
        (
            "setup.models.discrete_phase.interaction",
            lambda: solver.settings.setup.models.discrete_phase.interaction,
        ),
    )
    errors: dict[str, str] = {}
    for label, getter in candidates:
        try:
            return {"path": label, "state": safe_get_state(getter(), label)}
        except Exception as exc:
            errors[label] = f"{type(exc).__name__}: {exc}"
    raise RuntimeError(f"Could not read DPM interaction state: {errors}")


def require_dpm_off(solver: Any) -> dict[str, Any]:
    readback = dpm_interaction_state(solver)
    state = readback["state"]
    enabled = state.get("enabled") if isinstance(state, Mapping) else state
    if enabled not in (False, "false", "no", 0):
        raise RuntimeError(f"DPM interaction is not confirmed off: {readback}")
    return readback


def boundary_names(solver: Any) -> list[str]:
    state = safe_get_state(solver.settings.setup.boundary_conditions, "boundary_conditions")
    found: set[str] = set()
    if isinstance(state, Mapping):
        for values in state.values():
            if isinstance(values, Mapping):
                found.update(str(name) for name in values if str(name) != "settings")
    required = {"liquidinlet", "steaminlet", "steamoutlet", "bottom", "wall-fluid"}
    missing = required - found
    if missing:
        raise RuntimeError(f"Missing expected split-inlet boundaries: {sorted(missing)}")
    return sorted(found)


def activate_window(solver: Any, actions: list[dict[str, Any]]) -> Any:
    graphics = solver.settings.results.graphics
    actions.append(capture("open graphics window 8", lambda: graphics.windows.open_window(window_id=WINDOW_ID)))
    actions.append(capture("set graphics window 8", lambda: graphics.windows.set_window(window_id=WINDOW_ID)))
    graphics = solver.settings.results.graphics
    actions.append(capture("set window aspect ratio", lambda: graphics.windows.aspect_ratio(width=4.0, height=3.0)))
    return graphics


def create_longitudinal_plane(solver: Any) -> dict[str, Any]:
    planes = solver.settings.results.surfaces.plane_surface
    plane = recreate_named(planes, PLANE_NAME)
    plane.method = "yz-plane"
    plane.x = PLANE_X_M
    state = safe_get_state(plane, PLANE_NAME)
    readback_equals(state.get("method"), "yz-plane", "plane method")
    readback_equals(float(state.get("x")), PLANE_X_M, "plane x")
    return state


def apply_section_camera(graphics: Any) -> list[dict[str, Any]]:
    view = graphics.views
    actions = [
        capture("section camera target", lambda: view.camera.target(xyz=[-1.5, -3.0, -0.2])),
        capture("section camera position", lambda: view.camera.position(xyz=[8.0, -3.0, -0.2])),
        capture("section camera up", lambda: view.camera.up_vector(xyz=[0.0, 1.0, 0.0])),
        capture("section camera orthographic", lambda: view.camera.projection(type="orthographic")),
        capture("section camera auto-scale", lambda: view.auto_scale()),
        capture("section camera zoom", lambda: view.camera.zoom(factor=0.88)),
    ]
    return actions


def apply_angled_camera(graphics: Any) -> list[dict[str, Any]]:
    view = graphics.views
    return [
        capture("angled camera target", lambda: view.camera.target(xyz=[-1.55, -3.0, -0.2])),
        capture("angled camera position", lambda: view.camera.position(xyz=[8.0, 2.0, 7.0])),
        capture("angled camera up", lambda: view.camera.up_vector(xyz=[0.0, 1.0, 0.0])),
        capture("angled camera orthographic", lambda: view.camera.projection(type="orthographic")),
        capture("angled camera auto-scale", lambda: view.auto_scale()),
        capture("angled camera zoom", lambda: view.camera.zoom(factor=0.82)),
    ]


def configure_picture(graphics: Any, image_format: str) -> dict[str, Any]:
    picture = graphics.picture
    picture.use_window_resolution = False
    picture.x_resolution = PICTURE_WIDTH
    picture.y_resolution = PICTURE_HEIGHT
    picture.invert_background = True
    picture.driver_options.hardcopy_format = image_format
    state = safe_get_state(picture, "picture")
    if state.get("driver_options", {}).get("hardcopy_format") != image_format:
        raise RuntimeError(f"Hardcopy format readback mismatch: {state}")
    return state


def save_remote_picture(solver: Any, graphics: Any, remote_path: str) -> list[dict[str, Any]]:
    attempts = [
        capture(
            "save picture settings API",
            lambda: graphics.picture.save_picture(file_name=remote_path),
        ),
        capture(
            "save picture results TUI",
            lambda: solver.tui.results.graphics.picture.save_picture(remote_path),
        ),
    ]
    return attempts


def copy_picture(
    solver: Any,
    graphics: Any,
    *,
    stem: str,
    local_dir: Path,
    remote_dir: str,
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for image_format, suffix in (("png", ".png"), ("ppm", ".ppm")):
        remote_path = remote_dir + "\\" + stem + suffix
        local_raw = local_dir / (stem + suffix)
        picture_state = configure_picture(graphics, image_format)
        save_actions = save_remote_picture(solver, graphics, remote_path)
        size = remote_file_size(solver, remote_path, remote_dir)
        attempt: dict[str, Any] = {
            "format": image_format,
            "remote_path": remote_path,
            "picture_state": picture_state,
            "save_actions": save_actions,
            "remote_size_bytes": size,
        }
        if size and size > 0:
            copy = copy_remote_binary(
                solver,
                remote_path=remote_path,
                local_path=local_raw,
                remote_output_dir=remote_dir,
                max_bytes=60 * 1024 * 1024,
            )
            attempt["copy"] = copy
            if copy.get("ok"):
                if image_format == "ppm":
                    local_png = local_dir / (stem + ".png")
                    with Image.open(local_raw) as image:
                        image.save(local_png)
                    attempt["converted_png"] = str(local_png)
                else:
                    local_png = local_raw
                with Image.open(local_png) as image:
                    attempt["local_dimensions"] = list(image.size)
                    image.verify()
                attempt["ok"] = True
                attempts.append(attempt)
                return {"ok": True, "local_png": str(local_png), "attempts": attempts}
        attempt["ok"] = False
        attempts.append(attempt)
    return {"ok": False, "attempts": attempts}


def make_contour(
    solver: Any,
    graphics: Any,
    *,
    state_key: str,
    field: str,
    minimum: float,
    maximum: float,
    output_stem: str,
    local_dir: Path,
    remote_dir: str,
) -> dict[str, Any]:
    name = f"meeting_{state_key}_{field.replace('-', '_')}"
    contour = recreate_named(graphics.contour, name)
    allowed = [str(value) for value in contour.field.allowed_values()]
    if field not in allowed:
        raise RuntimeError(f"Contour field {field!r} unavailable in {state_key}")
    contour.field = field
    contour.surfaces_list = [PLANE_NAME]
    contour.filled = True
    contour.contour_lines = False
    contour.node_values = False
    contour.boundary_values = False
    contour.range_option.set_state(
        {
            "option": "auto-range-off",
            "auto_range_off": {
                "clip_to_range": True,
                "minimum": minimum,
                "maximum": maximum,
            },
        }
    )
    contour.coloring.set_state({"option": "banded", "banded": {}})
    contour.color_map.set_state(
        {
            "visible": True,
            "size": 21,
            "color": "field-velocity",
            "log_scale": False,
            "format": "%0.3g",
            "show_all": True,
            "font_automatic": True,
            "bground_transparent": False,
            "title_elements": "Variable and Object Name",
        }
    )
    readback = safe_get_state(contour, name)
    readback_equals(readback.get("field"), field, f"{name} field")
    readback_equals(readback.get("surfaces_list"), [PLANE_NAME], f"{name} surfaces")
    readback_equals(readback.get("node_values"), False, f"{name} node values")
    range_state = readback.get("range_option", {})
    readback_equals(range_state.get("option"), "auto-range-off", f"{name} range option")
    manual = range_state.get("auto_range_off", {})
    readback_equals(float(manual.get("minimum")), minimum, f"{name} minimum")
    readback_equals(float(manual.get("maximum")), maximum, f"{name} maximum")
    graphics.contour.display(object_name=name)
    camera_actions = apply_section_camera(graphics)
    picture = copy_picture(
        solver,
        graphics,
        stem=output_stem,
        local_dir=local_dir,
        remote_dir=remote_dir,
    )
    return {
        "object_name": name,
        "field": field,
        "surface": PLANE_NAME,
        "range": [minimum, maximum],
        "readback": readback,
        "camera_actions": camera_actions,
        "picture": picture,
    }


def choose_allowed(child: Any, preferred: str, fallback: str | None = None) -> str:
    raw_values = child.allowed_values()
    values = [str(value) for value in raw_values] if raw_values else []
    if not values or preferred in values:
        return preferred
    if fallback and fallback in values:
        return fallback
    return values[0]


def make_boundary_map(
    solver: Any,
    graphics: Any,
    *,
    state_key: str,
    local_dir: Path,
    remote_dir: str,
) -> dict[str, Any]:
    colors = {
        "wall-fluid": "silver",
        "bottom": "orange",
        "liquidinlet": "blue",
        "steaminlet": "red",
        "steamoutlet": "green",
    }
    name = f"meeting_{state_key}_boundary_map"
    mesh = recreate_named(graphics.mesh, name)
    mesh.surfaces_list = list(colors)
    mesh.options.set_state(
        {"nodes": False, "edges": True, "faces": True, "partitions": False, "overset": False, "gap": False}
    )
    mesh.edge_type.set_state({"option": "outline", "outline": True})
    mesh.coloring.option = "automatic"
    automatic_options = [str(value) for value in (mesh.coloring.automatic.option.allowed_values() or [])]
    if "id" in automatic_options:
        mesh.coloring.automatic.option = "id"
    readback = safe_get_state(mesh, name)
    readback_equals(readback.get("surfaces_list"), list(colors), "boundary map surfaces")
    graphics.mesh.display(object_name=name)
    camera_actions = apply_angled_camera(graphics)
    picture = copy_picture(
        solver,
        graphics,
        stem=f"{state_key}_boundary_map",
        local_dir=local_dir,
        remote_dir=remote_dir,
    )
    return {
        "surface_colors_requested": colors,
        "object": readback,
        "camera_actions": camera_actions,
        "picture": picture,
    }


def make_pathline(
    solver: Any,
    graphics: Any,
    *,
    state_key: str,
    release_surface: str,
    local_dir: Path,
    remote_dir: str,
) -> dict[str, Any]:
    mesh_name = f"meeting_{state_key}_pathline_wall_mesh"
    mesh = recreate_named(graphics.mesh, mesh_name)
    mesh.surfaces_list = ["wall-fluid", "bottom", "liquidinlet", "steaminlet", "steamoutlet"]
    mesh.options.set_state(
        {"nodes": False, "edges": True, "faces": False, "partitions": False, "overset": False, "gap": False}
    )
    mesh.edge_type.set_state({"option": "outline", "outline": True})

    name = f"meeting_{state_key}_carrier_pathline_{release_surface}"
    pathline = recreate_named(graphics.pathline, name)
    allowed_domains = [str(value) for value in pathline.velocity_domain.allowed_values()]
    if "all-phases" not in allowed_domains:
        raise RuntimeError(f"all-phases pathline domain unavailable: {allowed_domains}")
    pathline.velocity_domain = "all-phases"
    pathline.field = "velocity-magnitude"
    pathline.release_from_surfaces = [release_surface]
    pathline.step = 2000
    pathline.skip = 0
    pathline.coarsen = 3
    pathline.options.set_state(
        {"oil_flow": False, "reverse": False, "node_values": True, "relative": False}
    )
    pathline.style_attribute.set_state({"style": "line", "line_width": 2.0})
    pathline.color_map.set_state(
        {
            "visible": True,
            "size": 21,
            "color": "field-velocity",
            "log_scale": False,
            "format": "%0.3g",
            "show_all": True,
            "bground_transparent": False,
            "title_elements": "Variable and Object Name",
        }
    )
    readback = safe_get_state(pathline, name)
    if readback.get("release_from_surfaces") != [release_surface]:
        pathline = graphics.pathline[name]
        pathline.release_from_surfaces.set_state([release_surface])
        readback = safe_get_state(pathline, name)
    readback_equals(readback.get("velocity_domain"), "all-phases", f"{name} velocity domain")
    readback_equals(readback.get("field"), "velocity-magnitude", f"{name} field")
    readback_equals(readback.get("release_from_surfaces"), [release_surface], f"{name} release surface")
    graphics.mesh.display(object_name=mesh_name)
    graphics.pathline.add_to_graphics(object_name=name)
    camera_actions = apply_angled_camera(graphics)
    picture = copy_picture(
        solver,
        graphics,
        stem=f"{state_key}_carrier_pathlines_from_{release_surface}",
        local_dir=local_dir,
        remote_dir=remote_dir,
    )
    return {
        "object_name": name,
        "label": f"Carrier-field pathlines released from {release_surface}; not DPM tracks",
        "readback": readback,
        "camera_actions": camera_actions,
        "picture": picture,
    }


def record_graphic(
    result: dict[str, Any],
    key: str,
    exporter: Callable[[], dict[str, Any]],
) -> None:
    try:
        value = exporter()
        value.setdefault("ok", bool(value.get("picture", {}).get("ok")))
        result["graphics"][key] = value
    except Exception as exc:
        print(f"[WARN] graphics export {key}: {type(exc).__name__}: {exc}")
        result["graphics"][key] = {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def export_state(
    solver: Any,
    state: SavedState,
    *,
    local_dir: Path,
    remote_dir: str,
) -> dict[str, Any]:
    load_pair(solver, state)
    result: dict[str, Any] = {
        "title": state.title,
        "case": state.case,
        "data": state.data,
        "fluent_version": str(solver.get_fluent_version()),
        "health": str(solver.health_check.status()),
        "dpm_interaction": require_dpm_off(solver),
        "boundaries": boundary_names(solver),
        "actions": [],
        "graphics": {},
    }
    if "2024 R2" not in result["fluent_version"] and result["fluent_version"] != "24.2.0":
        raise RuntimeError(f"Expected Fluent 2024 R2 (24.2.0), got {result['fluent_version']}")
    graphics = activate_window(solver, result["actions"])
    result["plane"] = create_longitudinal_plane(solver)
    graphics = solver.settings.results.graphics
    if state.export_boundary:
        record_graphic(
            result,
            "boundary_map",
            lambda: make_boundary_map(
                solver, graphics, state_key=state.key, local_dir=local_dir, remote_dir=remote_dir
            ),
        )
    record_graphic(
        result,
        "phase2_vof",
        lambda: make_contour(
            solver,
            graphics,
            state_key=state.key,
            field="phase-2-vof",
            minimum=VOLUME_FRACTION_RANGE[0],
            maximum=VOLUME_FRACTION_RANGE[1],
            output_stem=f"{state.key}_phase2_liquid_volume_fraction_xm1p5",
            local_dir=local_dir,
            remote_dir=remote_dir,
        ),
    )
    record_graphic(
        result,
        "phase2_vof_zoom",
        lambda: make_contour(
            solver,
            graphics,
            state_key=state.key,
            field="phase-2-vof",
            minimum=VOLUME_FRACTION_ZOOM_RANGE[0],
            maximum=VOLUME_FRACTION_ZOOM_RANGE[1],
            output_stem=f"{state.key}_phase2_liquid_volume_fraction_zoom0p05_xm1p5",
            local_dir=local_dir,
            remote_dir=remote_dir,
        ),
    )
    record_graphic(
        result,
        "pressure",
        lambda: make_contour(
            solver,
            graphics,
            state_key=state.key,
            field="pressure",
            minimum=PRESSURE_RANGE_PA[0],
            maximum=PRESSURE_RANGE_PA[1],
            output_stem=f"{state.key}_static_pressure_xm1p5",
            local_dir=local_dir,
            remote_dir=remote_dir,
        ),
    )
    if state.export_sink_mask:
        record_graphic(
            result,
            "sink_mask",
            lambda: make_contour(
                solver,
                graphics,
                state_key=state.key,
                field="cwl07c-thick-bottom-mask",
                minimum=0.0,
                maximum=1.0,
                output_stem=f"{state.key}_thick_sink_mask_xm1p5",
                local_dir=local_dir,
                remote_dir=remote_dir,
            ),
        )
    if state.export_pathlines:
        for release_surface in ("liquidinlet", "steaminlet"):
            key = f"carrier_pathlines_{release_surface}"
            record_graphic(
                result,
                key,
                lambda surface=release_surface: make_pathline(
                    solver,
                    graphics,
                    state_key=state.key,
                    release_surface=surface,
                    local_dir=local_dir,
                    remote_dir=remote_dir,
                ),
            )
    return result


def main() -> int:
    register_setup07e_saved_state()
    args = build_parser().parse_args()
    if args.restore_07e_final and RESTORE_07E_STATE is None:
        raise RuntimeError(
            "Setup-07e final ramp-zero checkpoint is not available in its manifest"
        )
    load_dotenv(PROJECT_ROOT / ".env")
    requested = [value.strip() for value in args.states.split(",") if value.strip()]
    unknown = [value for value in requested if value not in SAVED_STATES]
    if unknown:
        raise ValueError(f"Unknown saved state(s): {unknown}")
    local_dir = Path(args.local_output_dir).expanduser().resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    solver = connect(server_id=args.server_id)
    ensure_remote_directory(solver, args.remote_output_dir)

    manifest_path = local_dir / "fluent_graphics_manifest.json"
    existing_states: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(existing.get("states"), dict):
                existing_states = existing["states"]
        except Exception:
            existing_states = {}
    manifest: dict[str, Any] = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "classification": "diagnostic",
        "postprocessing_only": True,
        "no_iterations_run": True,
        "dpm_update_run": False,
        "plane": {"name": PLANE_NAME, "method": "yz-plane", "x_m": PLANE_X_M},
        "matched_ranges": {
            "phase_2_liquid_volume_fraction": list(VOLUME_FRACTION_RANGE),
            "phase_2_liquid_volume_fraction_zoom": list(VOLUME_FRACTION_ZOOM_RANGE),
            "static_pressure_pa": list(PRESSURE_RANGE_PA),
        },
        "picture_resolution": [PICTURE_WIDTH, PICTURE_HEIGHT],
        "states": existing_states,
    }
    try:
        for key in requested:
            manifest["states"][key] = export_state(
                solver,
                SAVED_STATES[key],
                local_dir=local_dir,
                remote_dir=args.remote_output_dir,
            )
            manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    finally:
        restore_state = None
        if args.restore_07e_final:
            restore_state = RESTORE_07E_STATE
        elif args.restore_07c_final:
            restore_state = RESTORE_STATE
        if restore_state is not None:
            restore: dict[str, Any] = {
                "state": restore_state.__dict__,
                "attempted": True,
            }
            try:
                load_pair(solver, restore_state)
                restore["dpm_interaction"] = require_dpm_off(solver)
                restore["ok"] = True
            except Exception as exc:
                restore["ok"] = False
                restore["error"] = f"{type(exc).__name__}: {exc}"
            manifest["restore"] = restore
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(f"\nManifest: {manifest_path}")
    print("Post-processing only: no initialization, iterations, DPM update, or case/data write was issued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

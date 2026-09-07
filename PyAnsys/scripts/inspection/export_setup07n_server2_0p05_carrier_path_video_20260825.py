#!/usr/bin/env python3
"""Export a short carrier-pathline video from the accepted server-2 0.05% field.

This is post-processing only.  It cold-loads one checksum-bound case/data pair,
creates temporary Results graphics objects, writes PNG pictures, and encodes
those pictures locally.  It does not initialize, iterate, update DPM, change a
physical setting, or write case/data files.

The displayed lines are massless carrier-field pathlines through the frozen VOF
endpoint velocity field.  They are not DPM particles, droplets, or a physical-
time material history.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageEnhance, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INSPECTION_DIR = PROJECT_ROOT / "scripts" / "inspection"
SETUP_DIR = PROJECT_ROOT / "scripts" / "setup"
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(INSPECTION_DIR))
sys.path.insert(0, str(SETUP_DIR))

import export_setup07_meeting_graphics as graphics_base  # noqa: E402
import run_setup07n_c_pressure_response_sign_probe as pressure_probe  # noqa: E402
import run_setup07n_server2_matched_target_pressure_0p1feed_20260825 as matched  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402
from inspect_setup07n_mesh_geometry import (  # noqa: E402
    capture_connected_clients,
    exclusive_writer_lock,
)
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
    safe_get_state,
)
from pyansys_fluent.connection import connect  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
RUN_LABEL = (
    "brine620k_07n_s2_p1122264_0p05feed_step100_"
    "carrier_pathline_video_attempt3_20260825"
)
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_OUTPUT = rf"C:\Users\qtra338\Documents\Mesh study\{RUN_LABEL}"
LOCAL_OUTPUT = PROJECT_ROOT / "output" / STUDY_ID / RUN_LABEL
RAW_DIR = LOCAL_OUTPUT / "raw_fluent_frames"
ANNOTATED_DIR = LOCAL_OUTPUT / "annotated_frames"
VIDEO_FRAMES_DIR = LOCAL_OUTPUT / "video_frames"
MANIFEST_PATH = LOCAL_OUTPUT / "video_manifest.json"
LOCK_PATH = PROJECT_ROOT / "output" / STUDY_ID / "setup07n_server2_independent_writer.lock"

SOURCE_STEM = (
    "brine620k_07n_s2_p1122264_0p05feed_dt128_i100_s10_a1_20260825_"
    "feed_0p05_percent_targetpressure_dt128_inner100_additional_step10"
)
SOURCE_CASE = str(PureWindowsPath(REMOTE_ROOT) / f"{SOURCE_STEM}.cas.h5")
SOURCE_DATA = str(PureWindowsPath(REMOTE_ROOT) / f"{SOURCE_STEM}.dat.h5")
SOURCE_CASE_SHA256 = "d0247380c036588b8bd56de8428deb3d82340fe153c38e31c0fbeb4028c0bd52"
SOURCE_DATA_SHA256 = "3844735627f590560c59d24b5f1221a858bc501af5881e83026396b99d75e97b"
SOURCE_TIME_STEP = 100
SOURCE_FLOW_TIME_S = 0.00639
SOURCE_PRESSURE_PA = 1_122_263.6212370484
SOURCE_INLET_FRACTION = 0.0005
SOURCE_VELOCITY_MAX_MS = 0.1044935

EXPECTED_VERSION = "Ansys Fluent 2024 R2"
EXPECTED_RANKS = 16
WIDTH = 1600
HEIGHT = 900
FPS = 12
PATHLINE_STEPS = (40, 70, 110, 170, 250, 360, 500, 700, 950, 1250, 1600, 2000)
RELEASE_SURFACES = ("liquidinlet", "steaminlet")
FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
FFPROBE = Path("/opt/homebrew/bin/ffprobe")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(payload: dict[str, Any], *, create: bool = False) -> None:
    text = json.dumps(payload, indent=2, default=str) + "\n"
    if create:
        LOCAL_OUTPUT.mkdir(parents=True, exist_ok=False)
        RAW_DIR.mkdir()
        ANNOTATED_DIR.mkdir()
        VIDEO_FRAMES_DIR.mkdir()
        with MANIFEST_PATH.open("x", encoding="utf-8") as stream:
            stream.write(text)
        return
    temporary = MANIFEST_PATH.with_suffix(".json.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, MANIFEST_PATH)


def remote_hash(solver: Any, path: str, label: str) -> dict[str, str]:
    scratch = str(PureWindowsPath(REMOTE_OUTPUT) / f"_{label}_sha256.txt")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"refusing to overwrite remote hash evidence: {scratch}")
    return {
        "path": path,
        "sha256": mesh_study.remote_file_sha256(solver, path, scratch),
        "scratch": scratch,
    }


def verify_source(solver: Any) -> dict[str, Any]:
    for path in (SOURCE_CASE, SOURCE_DATA):
        if not remote_file_exists(solver, path):
            raise FileNotFoundError(f"required remote source is missing: {path}")
    case = remote_hash(solver, SOURCE_CASE, "source_case")
    data = remote_hash(solver, SOURCE_DATA, "source_data")
    if case["sha256"] != SOURCE_CASE_SHA256:
        raise RuntimeError("source case checksum mismatch")
    if data["sha256"] != SOURCE_DATA_SHA256:
        raise RuntimeError("source data checksum mismatch")
    return {"case": case, "data": data}


def phase_identity(solver: Any) -> dict[str, Any]:
    species = solver.settings.setup.models.species.model.get_state()
    materials = species.get("phase_material", {}) if isinstance(species, dict) else {}
    result = {
        "phase_1": materials.get("phase-1"),
        "phase_2": materials.get("phase-2"),
    }
    result["passed"] = (
        result["phase_1"] == "water-vapor-at-psep"
        and result["phase_2"] == "water-liquid-at-psep"
    )
    return result


def loaded_state_gate(solver: Any) -> dict[str, Any]:
    open_gate = pressure_probe.open_settings_gate(solver, SOURCE_PRESSURE_PA)
    inlet_gate = matched.fraction_gate(solver, SOURCE_INLET_FRACTION)
    clock = pressure_probe.transient07j.runtime_clock(solver)
    identity = phase_identity(solver)
    required_open_parts = ("boundary", "methods", "dpm", "sources", "ewf")
    passed = (
        all(bool(open_gate[key].get("passed")) for key in required_open_parts)
        and bool(inlet_gate.get("passed"))
        and bool(identity.get("passed"))
        and int(clock["time_step"]) == SOURCE_TIME_STEP
        and math.isclose(
            float(clock["flow_time_s"]), SOURCE_FLOW_TIME_S, rel_tol=0.0, abs_tol=1.0e-12
        )
    )
    return {
        "passed": passed,
        "clock": clock,
        "phase_identity": identity,
        "open_settings": open_gate,
        "inlets": inlet_gate,
        "zero_inlet_gate_expected_false": open_gate["zero_inlets"],
    }


def remote_png_path(stem: str) -> str:
    return str(PureWindowsPath(REMOTE_OUTPUT) / f"{stem}.png")


def save_png(solver: Any, graphics: Any, stem: str) -> dict[str, Any]:
    remote_path = remote_png_path(stem)
    if remote_file_exists(solver, remote_path):
        raise FileExistsError(f"refusing to overwrite remote PNG: {remote_path}")
    picture = graphics.picture
    picture.use_window_resolution = False
    picture.x_resolution = WIDTH
    picture.y_resolution = HEIGHT
    picture.invert_background = True
    picture.driver_options.hardcopy_format = "png"
    picture_state = safe_get_state(picture, "pathline picture")
    expected = picture_state.get("driver_options", {}).get("hardcopy_format")
    if expected != "png":
        raise RuntimeError(f"PNG hardcopy readback mismatch: {picture_state}")
    graphics.picture.save_picture(file_name=remote_path)
    remote_size = graphics_base.remote_file_size(solver, remote_path, REMOTE_OUTPUT)
    if not remote_size or remote_size <= 0:
        raise RuntimeError(f"remote PNG is empty or missing: {remote_path}")
    local_path = RAW_DIR / f"{stem}.png"
    copy = graphics_base.copy_remote_binary(
        solver,
        remote_path=remote_path,
        local_path=local_path,
        remote_output_dir=REMOTE_OUTPUT,
        max_bytes=60 * 1024 * 1024,
    )
    if not copy.get("ok"):
        raise RuntimeError(f"remote PNG copy failed: {copy}")
    with Image.open(local_path) as image:
        dimensions = list(image.size)
        image.verify()
    if dimensions != [WIDTH, HEIGHT]:
        raise RuntimeError(f"unexpected PNG dimensions: {dimensions}")
    return {
        "remote_path": remote_path,
        "remote_size_bytes": remote_size,
        "local_path": str(local_path),
        "local_size_bytes": local_path.stat().st_size,
        "local_dimensions": dimensions,
        "local_sha256": sha256(local_path),
        "picture_readback": picture_state,
    }


def configure_camera(graphics: Any) -> None:
    view = graphics.views
    view.camera.target(xyz=[-1.55, -3.0, -0.2])
    view.camera.position(xyz=[8.0, 2.0, 7.0])
    view.camera.up_vector(xyz=[0.0, 1.0, 0.0])
    view.camera.projection(type="orthographic")
    view.auto_scale()
    view.camera.zoom(factor=0.95)


def configure_mesh(graphics: Any, name: str) -> dict[str, Any]:
    surfaces = [
        "wall-fluid",
        "inlet-outer-wall",
        "liquidinlet",
        "steaminlet",
        "steamoutlet",
        "brineoutlet",
    ]
    mesh = graphics_base.recreate_named(graphics.mesh, name)
    mesh.surfaces_list = surfaces
    mesh.options.set_state(
        {
            "nodes": False,
            "edges": True,
            "faces": False,
            "partitions": False,
            "overset": False,
            "gap": False,
        }
    )
    mesh.edge_type.set_state({"option": "outline", "outline": True})
    readback = safe_get_state(mesh, name)
    if readback.get("surfaces_list") != surfaces:
        mesh = graphics.mesh[name]
        mesh.surfaces_list.set_state(surfaces)
        readback = safe_get_state(mesh, name)
    # Fluent 2024 R2 can filter non-displayable boundary patches from a mesh
    # outline and insert the adjacent interior.  That does not change the
    # pathline release.  Require the scientifically useful vessel/outlet
    # outline, preserve the exact filtering in evidence, and gate the release
    # surface independently on the pathline object below.
    actual_surfaces = [str(value) for value in readback.get("surfaces_list", [])]
    mandatory = {"wall-fluid", "liquidinlet", "steamoutlet", "brineoutlet"}
    if not mandatory.issubset(set(actual_surfaces)):
        raise RuntimeError(
            f"mesh outline lost mandatory surfaces {sorted(mandatory)}: {readback}"
        )
    readback["_requested_surfaces"] = surfaces
    readback["_fluent_filtered_surfaces"] = actual_surfaces
    return readback


def configure_pathline(graphics: Any, name: str, release_surface: str) -> dict[str, Any]:
    pathline = graphics_base.recreate_named(graphics.pathline, name)
    allowed_domains = [str(value) for value in pathline.velocity_domain.allowed_values()]
    allowed_releases = [str(value) for value in pathline.release_from_surfaces.allowed_values()]
    if "all-phases" not in allowed_domains:
        raise RuntimeError(f"all-phases pathline domain unavailable: {allowed_domains}")
    if release_surface not in allowed_releases:
        raise RuntimeError(
            f"release surface {release_surface!r} unavailable: {allowed_releases}"
        )
    pathline.velocity_domain = "all-phases"
    pathline.field = "velocity-magnitude"
    pathline.release_from_surfaces = [release_surface]
    pathline.step = PATHLINE_STEPS[0]
    pathline.skip = 0
    pathline.coarsen = 3
    pathline.options.set_state(
        {"oil_flow": False, "reverse": False, "node_values": True, "relative": False}
    )
    # In 2024 R2 the manual-range child is inactive until the option is changed,
    # so a one-shot parent set_state rejects ``auto_range_off``.  Activate the
    # option, reacquire the graphics child, then set and verify its active child.
    fixed_range_error: str | None = None
    try:
        pathline.range.option = "auto-range-off"
        pathline = graphics.pathline[name]
        pathline.range.auto_range_off.set_state(
            {"clip_to_range": True, "minimum": 0.0, "maximum": 0.105}
        )
    except Exception as exc:
        fixed_range_error = f"{type(exc).__name__}: {exc}"
        pathline = graphics.pathline[name]
        pathline.range.option = "auto-range"
    pathline.style_attribute.set_state(
        {"style": "line", "line_width": 2.0, "arrow_space": 12, "arrow_scale": 1.0}
    )
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
    if readback.get("release_from_surfaces") != [release_surface]:
        raise RuntimeError(
            f"release surface readback mismatch for {release_surface}: {readback}"
        )
    if readback.get("velocity_domain") != "all-phases":
        raise RuntimeError(f"velocity domain readback mismatch: {readback}")
    if readback.get("field") != "velocity-magnitude":
        raise RuntimeError(f"field readback mismatch: {readback}")
    range_readback = readback.get("range", {})
    fixed_range_passed = False
    if range_readback.get("option") == "auto-range-off":
        manual = range_readback.get("auto_range_off", {})
        minimum = manual.get("minimum")
        maximum = manual.get("maximum")
        fixed_range_passed = (
            minimum is not None
            and maximum is not None
            and math.isclose(float(minimum), 0.0, abs_tol=1.0e-12)
            and math.isclose(float(maximum), 0.105, abs_tol=1.0e-12)
        )
    readback["_fixed_velocity_range_requested_ms"] = [0.0, 0.105]
    readback["_fixed_velocity_range_passed"] = fixed_range_passed
    readback["_fixed_velocity_range_error"] = fixed_range_error
    return readback


def export_release_frames(
    solver: Any,
    graphics: Any,
    *,
    release_surface: str,
) -> dict[str, Any]:
    mesh_name = f"{RUN_LABEL}_{release_surface}_mesh"
    pathline_name = f"{RUN_LABEL}_{release_surface}_pathline"
    mesh_readback = configure_mesh(graphics, mesh_name)
    pathline_readback = configure_pathline(graphics, pathline_name, release_surface)
    frames: list[dict[str, Any]] = []
    for index, step in enumerate(PATHLINE_STEPS, start=1):
        pathline = solver.settings.results.graphics.pathline[pathline_name]
        pathline.step = step
        step_readback = safe_get_state(pathline, pathline_name)
        if int(step_readback.get("step")) != step:
            raise RuntimeError(f"pathline step readback mismatch: {step_readback}")
        if step_readback.get("release_from_surfaces") != [release_surface]:
            raise RuntimeError(f"release surface changed during render: {step_readback}")
        graphics = solver.settings.results.graphics
        graphics.mesh.display(object_name=mesh_name)
        graphics.pathline.add_to_graphics(object_name=pathline_name)
        configure_camera(graphics)
        stem = f"{release_surface}_pathline_reveal_{index:02d}_step{step:04d}"
        picture = save_png(solver, graphics, stem)
        frames.append(
            {
                "index": index,
                "pathline_step": step,
                "pathline_readback": step_readback,
                "picture": picture,
            }
        )
        print(f"[frame] {release_surface} {index}/{len(PATHLINE_STEPS)} step={step}", flush=True)
    return {
        "release_surface": release_surface,
        "label": f"{release_surface}-origin massless carrier pathlines",
        "mesh_readback": mesh_readback,
        "initial_pathline_readback": pathline_readback,
        "frames": frames,
        "passed": len(frames) == len(PATHLINE_STEPS),
    }


def fonts() -> tuple[ImageFont.FreeTypeFont | ImageFont.ImageFont, ...]:
    candidates = (
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    )
    regular_path = candidates[0] if candidates[0].exists() else None
    bold_path = candidates[1] if candidates[1].exists() else regular_path
    if regular_path:
        return (
            ImageFont.truetype(str(bold_path), 42),
            ImageFont.truetype(str(regular_path), 26),
            ImageFont.truetype(str(regular_path), 22),
        )
    return (ImageFont.load_default(), ImageFont.load_default(), ImageFont.load_default())


def annotate(raw_path: Path, *, release_surface: str, index: int, total: int) -> Path:
    title_font, body_font, small_font = fonts()
    with Image.open(raw_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, 0, WIDTH, 88), fill=(10, 16, 26, 224))
    draw.rectangle((0, HEIGHT - 94, WIDTH, HEIGHT), fill=(10, 16, 26, 224))
    origin = "Liquid-inlet origin" if release_surface == "liquidinlet" else "Steam-inlet origin"
    draw.text(
        (36, 21),
        "Massless carrier-flow pathlines — 0.05% feed",
        font=title_font,
        fill=(255, 255, 255, 255),
    )
    draw.text(
        (36, HEIGHT - 82),
        f"{origin}  •  endpoint t = 6.39 ms  •  pathway reveal {index}/{total}",
        font=body_font,
        fill=(255, 255, 255, 255),
    )
    draw.text(
        (36, HEIGHT - 45),
        "Frozen VOF velocity field • DPM off • playback is not physical time",
        font=small_font,
        fill=(200, 213, 230, 255),
    )
    output = ANNOTATED_DIR / f"{release_surface}_{index:02d}.png"
    image.save(output)
    return output


def title_card(background: Path, *, title: str, subtitle: str, stem: str) -> Path:
    title_font, body_font, small_font = fonts()
    with Image.open(background) as source:
        image = source.convert("RGB")
    image = ImageEnhance.Brightness(image).enhance(0.28)
    draw = ImageDraw.Draw(image, "RGBA")
    box = (120, 245, WIDTH - 120, 655)
    draw.rounded_rectangle(box, radius=24, fill=(7, 13, 23, 218))
    title_box = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_box[2] - title_box[0]
    draw.text(((WIDTH - title_width) / 2, 330), title, font=title_font, fill="white")
    subtitle_box = draw.textbbox((0, 0), subtitle, font=body_font)
    subtitle_width = subtitle_box[2] - subtitle_box[0]
    draw.text(
        ((WIDTH - subtitle_width) / 2, 405),
        subtitle,
        font=body_font,
        fill=(215, 225, 239),
    )
    note = "Accepted low-feed diagnostic • endpoint t = 6.39 ms • DPM off"
    note_box = draw.textbbox((0, 0), note, font=small_font)
    note_width = note_box[2] - note_box[0]
    draw.text(
        ((WIDTH - note_width) / 2, 470),
        note,
        font=small_font,
        fill=(177, 195, 218),
    )
    output = ANNOTATED_DIR / f"{stem}.png"
    image.save(output)
    return output


def add_repeated(sequence: list[Path], source: Path, count: int) -> None:
    sequence.extend([source] * count)


def encode_video(releases: dict[str, Any]) -> dict[str, Any]:
    if not FFMPEG.exists() or not FFPROBE.exists():
        raise FileNotFoundError("ffmpeg/ffprobe not found at the expected Homebrew path")
    annotated: dict[str, list[Path]] = {}
    for release_surface, record in releases.items():
        if not record.get("passed"):
            continue
        paths: list[Path] = []
        for frame in record["frames"]:
            paths.append(
                annotate(
                    Path(frame["picture"]["local_path"]),
                    release_surface=release_surface,
                    index=int(frame["index"]),
                    total=len(record["frames"]),
                )
            )
        annotated[release_surface] = paths
    if "liquidinlet" not in annotated:
        raise RuntimeError("no proven liquid-inlet pathline frames were available")

    liquid = annotated["liquidinlet"]
    intro = title_card(
        liquid[-1],
        title="0.05% feed: carrier-flow pathway",
        subtitle="Massless pathlines through the accepted endpoint field",
        stem="intro",
    )
    sequence: list[Path] = []
    add_repeated(sequence, intro, FPS)
    for path in liquid:
        add_repeated(sequence, path, 3)
    add_repeated(sequence, liquid[-1], FPS)

    if "steaminlet" in annotated:
        steam = annotated["steaminlet"]
        transition = title_card(
            steam[-1],
            title="Steam-inlet origin",
            subtitle="Same frozen endpoint field; a different release surface",
            stem="steam_transition",
        )
        add_repeated(sequence, transition, FPS // 2)
        for path in steam:
            add_repeated(sequence, path, 3)
        add_repeated(sequence, steam[-1], FPS)

    outro = title_card(
        liquid[-1],
        title="Carrier-flow visualization only",
        subtitle="Not droplets, DPM tracks, carryover, or separator efficiency",
        stem="outro",
    )
    add_repeated(sequence, outro, FPS)

    frame_records: list[dict[str, Any]] = []
    for index, source in enumerate(sequence):
        destination = VIDEO_FRAMES_DIR / f"frame_{index:04d}.png"
        if destination.exists():
            raise FileExistsError(f"refusing to overwrite video frame: {destination}")
        shutil.copy2(source, destination)
        frame_records.append(
            {"frame": index, "source": str(source), "path": str(destination)}
        )

    output = LOCAL_OUTPUT / "setup07n_0p05_carrier_pathlines.mp4"
    command = [
        str(FFMPEG),
        "-n",
        "-framerate",
        str(FPS),
        "-i",
        str(VIDEO_FRAMES_DIR / "frame_%04d.png"),
        "-c:v",
        "libx264",
        "-preset",
        "slow",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0 or not output.exists():
        raise RuntimeError(
            f"ffmpeg failed rc={completed.returncode}: {completed.stderr[-4000:]}"
        )
    probe_command = [
        str(FFPROBE),
        "-v",
        "error",
        "-show_entries",
        "format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_frames",
        "-of",
        "json",
        str(output),
    ]
    probed = subprocess.run(probe_command, capture_output=True, text=True, check=True)
    return {
        "path": str(output),
        "sha256": sha256(output),
        "size_bytes": output.stat().st_size,
        "fps": FPS,
        "frame_count": len(sequence),
        "duration_s": len(sequence) / FPS,
        "ffmpeg_command": command,
        "ffprobe": json.loads(probed.stdout),
        "frame_records": frame_records,
        "annotated_frames": {
            key: [
                {"path": str(path), "sha256": sha256(path), "size_bytes": path.stat().st_size}
                for path in paths
            ]
            for key, paths in annotated.items()
        },
    }


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": RUN_LABEL,
        "status": "running",
        "classification": "accepted diagnostic post-processing visualization",
        "eligible_parent": False,
        "server_id": "2",
        "started_epoch": time.time(),
        "local_pid": os.getpid(),
        "source": {
            "case": SOURCE_CASE,
            "case_sha256": SOURCE_CASE_SHA256,
            "data": SOURCE_DATA,
            "data_sha256": SOURCE_DATA_SHA256,
            "time_step": SOURCE_TIME_STEP,
            "flow_time_s": SOURCE_FLOW_TIME_S,
            "accepted_window_s": 0.00128,
            "inlet_fraction": SOURCE_INLET_FRACTION,
            "requested_brine_pressure_pa": SOURCE_PRESSURE_PA,
            "velocity_max_ms": SOURCE_VELOCITY_MAX_MS,
        },
        "scientific_label": (
            "Massless carrier-flow pathlines through the frozen 0.05%-feed VOF endpoint; "
            "DPM is off and these are not droplet trajectories or physical-time histories."
        ),
        "postprocessing_only": True,
        "no_initialization": True,
        "no_iterations": True,
        "no_dpm_update": True,
        "no_case_data_writes": True,
        "no_physical_setting_changes": True,
        "releases": {},
    }
    write_manifest(payload, create=True)
    try:
        with exclusive_writer_lock(LOCK_PATH):
            solver = connect(server_id="2", tcp_timeout_seconds=5.0, start_transcript=True)
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(f"exclusive Fluent ownership unresolved: {clients!r}")
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            if payload["health_status"] not in ("Status.SERVING", "SERVING"):
                raise RuntimeError(f"server is not SERVING: {payload['health_status']}")
            if payload["fluent_version"] != EXPECTED_VERSION:
                raise RuntimeError(
                    f"expected {EXPECTED_VERSION}, got {payload['fluent_version']}"
                )
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            graphics_base.ensure_remote_directory(solver, REMOTE_OUTPUT)
            payload["verified_source"] = verify_source(solver)
            write_manifest(payload)

            solver.settings.file.read_case(file_name=SOURCE_CASE)
            solver.settings.file.read_data(file_name=SOURCE_DATA)
            time.sleep(1.0)
            payload["loaded_state_gate"] = loaded_state_gate(solver)
            if not payload["loaded_state_gate"]["passed"]:
                raise RuntimeError("loaded checkpoint failed physical/settings/clock readback")
            write_manifest(payload)

            actions: list[dict[str, Any]] = []
            graphics = graphics_base.activate_window(solver, actions)
            graphics.windows.aspect_ratio(width=16.0, height=9.0)
            payload["graphics_window_actions"] = actions
            payload["picture_resolution"] = [WIDTH, HEIGHT]
            payload["requested_fixed_velocity_range_ms"] = [0.0, 0.105]
            payload["pathline_steps"] = list(PATHLINE_STEPS)
            write_manifest(payload)

            for release_surface in RELEASE_SURFACES:
                try:
                    payload["releases"][release_surface] = export_release_frames(
                        solver,
                        solver.settings.results.graphics,
                        release_surface=release_surface,
                    )
                except Exception as exc:
                    payload["releases"][release_surface] = {
                        "passed": False,
                        "rejected": True,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                    if release_surface == "liquidinlet":
                        raise
                    print(
                        f"[reject] optional {release_surface} pathlines: "
                        f"{type(exc).__name__}: {exc}",
                        flush=True,
                    )
                write_manifest(payload)

            payload["video"] = encode_video(payload["releases"])
            payload["resident_state_after_export"] = {
                "case": SOURCE_CASE,
                "data": SOURCE_DATA,
                "time_step": SOURCE_TIME_STEP,
                "flow_time_s": SOURCE_FLOW_TIME_S,
            }
            payload["status"] = "completed"
            payload["completed_epoch"] = time.time()
            write_manifest(payload)
            print(payload["video"]["path"], flush=True)
            print(
                "Post-processing only: zero initialization, iterations, DPM updates, and case/data writes.",
                flush=True,
            )
    except Exception as exc:
        payload["status"] = "failed"
        payload["error"] = f"{type(exc).__name__}: {exc}"
        payload["failed_epoch"] = time.time()
        write_manifest(payload)
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

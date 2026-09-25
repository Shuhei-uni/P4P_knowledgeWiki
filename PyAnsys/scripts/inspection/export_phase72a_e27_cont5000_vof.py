#!/usr/bin/env python3
"""Export and retrieve a native Fluent phase-2 VOF contour at E2.7 N13586."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path, PureWindowsPath
import struct
import sys
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "PyAnsys" / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256


RUN_ROOT = ROOT / "PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z"
RUN_MANIFEST = RUN_ROOT / "run-manifest.json"
OUT = ROOT / "PyAnsys/output/phase72a_e27_cont5000_native_vof"
FIGURES = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/figures"
LOCAL_PNG = FIGURES / "E2.7-CONT5000-phase2-vof-xy-z0-final13586.png"
MANIFEST_PATH = OUT / "export-manifest.json"
SERVER_ID = "1"
EXPECTED_ITERATION = 13586
REMOTE_BASE = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\FamilyE\E2.7-continuation-5000\20260923T102912Z")
REMOTE_FIGURES = REMOTE_BASE / "figures"
PLANE = "p72a-e27-cont5000-xy-z0"
CONTOUR = "p72a-e27-cont5000-phase2-vof"
DISPLAY_RANGE = [0.0, 1.0]


def write(record: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    run = json.loads(RUN_MANIFEST.read_text(encoding="utf-8"))
    require(run.get("status") == "COMPLETE", "continuation run manifest is not COMPLETE")
    require(run.get("terminal_native_iteration") == EXPECTED_ITERATION, "continuation did not end at native iteration 13586")
    pair = run["durable_final_pair"]
    record = {
        "status": "STARTED",
        "server_id": SERVER_ID,
        "fluent_version_expected": "Ansys Fluent 2025 R2",
        "solve_issued": False,
        "source_case": pair["case"],
        "source_data": pair["data"],
        "source_case_sha256": pair["case_sha256"],
        "source_data_sha256": pair["data_sha256"],
        "source_run_manifest": str(RUN_MANIFEST.relative_to(ROOT)),
        "checkpoint": "completed E2.7 + 5000 continuation, native 13586",
        "surface": {"type": "xy-plane", "coordinate": "Z=0 m", "normal": "+Z"},
        "field": "phase-2-vof",
        "display_range": DISPLAY_RANGE,
        "camera": {"projection": "orthographic", "target": [0.0, 3.495, 0.0], "position": [0.0, 3.495, 10.0], "up": [0.0, 1.0, 0.0]},
        "remote_png": str(REMOTE_FIGURES / "P72A-E2.7-CONT5000-phase2-vof-xy-z0-N13586.png"),
        "local_png": str(LOCAL_PNG.relative_to(ROOT)),
    }
    write(record)
    solver = connect(SERVER_ID, start_transcript=False, tcp_timeout_seconds=5)
    try:
        require("2025 R2" in str(solver.get_fluent_version()), "unexpected Fluent version")
        iteration = round(float(solver.settings.setup.named_expressions["P71V2Iteration"].get_value()))
        require(iteration == EXPECTED_ITERATION, f"Fluent session is at native {iteration}, expected {EXPECTED_ITERATION}")
        require(remote_file_exists(solver, pair["case"]), "durable final case is missing on Server 1")
        require(remote_file_exists(solver, pair["data"]), "durable final data is missing on Server 1")
        scratch = PureWindowsPath(run["remote_paths"]["scratch_root"])
        case_hash = remote_file_sha256(solver, pair["case"], str(scratch / "vof-export-source-case.sha256.txt"))
        data_hash = remote_file_sha256(solver, pair["data"], str(scratch / "vof-export-source-data.sha256.txt"))
        require(case_hash == pair["case_sha256"] and data_hash == pair["data_sha256"], "loaded final pair hashes differ from the run manifest")
        record["loaded_native_iteration"] = iteration
        record["verified_remote_hashes"] = {"case": case_hash, "data": data_hash}
        ensure_remote_directory(solver, str(REMOTE_FIGURES))
        require(not remote_file_exists(solver, record["remote_png"]), "refusing to overwrite an existing native Fluent contour")

        surfaces = solver.settings.results.surfaces.plane_surface
        plane_names = set(map(str, surfaces.get_object_names()))
        if PLANE not in plane_names:
            surfaces.create(name=PLANE)
        surfaces[PLANE].set_state({"method": "xy-plane", "z": 0.0})
        plane_state = surfaces[PLANE].get_state()
        require(float(plane_state.get("z")) == 0.0, f"plane did not read back at Z=0: {plane_state}")

        graphics = solver.settings.results.graphics
        contours = graphics.contour
        contour_names = set(map(str, contours.get_object_names()))
        if CONTOUR not in contour_names:
            contours.create(name=CONTOUR)
        contour = contours[CONTOUR]
        require("phase-2-vof" in contour.field.allowed_values(), "phase-2 VOF is not an available contour field")
        contour.set_state({
            "field": "phase-2-vof",
            "surfaces_list": [PLANE],
            "range_options": {"global_range": False, "auto_range": False, "clip_to_range": False, "minimum": 0.0, "maximum": 1.0},
            "options": {"filled": True, "node_values": True, "boundary_values": False, "contour_lines": False},
        })
        record["plane_state"] = plane_state
        record["contour_state"] = contour.get_state()
        require(record["contour_state"].get("field") == "phase-2-vof", "contour field readback mismatch")
        require(record["contour_state"]["range_options"].get("auto_range") is False, "contour auto-range remained enabled")
        require(record["contour_state"]["range_options"].get("minimum") == 0.0 and record["contour_state"]["range_options"].get("maximum") == 1.0, "contour range readback mismatch")
        contour.display()

        camera = graphics.views.camera
        camera.projection(type="orthographic")
        camera.target(xyz=[0.0, 3.495, 0.0])
        camera.position(xyz=[0.0, 3.495, 10.0])
        camera.up_vector(xyz=[0.0, 1.0, 0.0])
        graphics.views.auto_scale()
        graphics.picture.use_window_resolution = False
        graphics.picture.x_resolution = 2400
        graphics.picture.y_resolution = 1800
        record["picture_state"] = graphics.picture.get_state()
        graphics.picture.save_picture(file_name=record["remote_png"])
        require(remote_file_exists(solver, record["remote_png"]), "Fluent did not write the native contour PNG")

        encoded_path = record["remote_png"] + ".base64.txt"
        powershell = (
            f"[IO.File]::WriteAllText('{encoded_path}',"
            f"[Convert]::ToBase64String([IO.File]::ReadAllBytes('{record['remote_png']}')))"
        )
        encoded_command = base64.b64encode(powershell.encode("utf-16le")).decode("ascii")
        command = f"cmd /c powershell -NoProfile -EncodedCommand {encoded_command}"
        solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')
        payload = base64.b64decode(read_text(solver, encoded_path), validate=True)
        require(payload.startswith(b"\x89PNG\r\n\x1a\n"), "retrieved file is not a PNG")
        LOCAL_PNG.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_PNG.write_bytes(payload)
        require(LOCAL_PNG.is_file() and LOCAL_PNG.stat().st_size > 0, "local native Fluent PNG is missing")
        width, height = struct.unpack(">II", payload[16:24])
        record["png"] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest(), "width": width, "height": height}
        require((width, height) == (2400, 1800), f"unexpected PNG resolution: {(width, height)}")
        record["status"] = "COMPLETE_NATIVE_FLUENT_EXPORT_AWAIT_VISUAL_QA"
        write(record)
        print(json.dumps({"status": record["status"], "local_png": record["local_png"], "remote_png": record["remote_png"], "png": record["png"]}, indent=2))
        # Keep the loaded 13586 case/data and leave the contour displayed. Do not exit Fluent.
        return 0
    except Exception as exc:
        record["status"] = "EXPORT_BLOCKED"
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc()
        write(record)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export a cleaner native Fluent E2.7 continuation phase-2 VOF contour."""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path, PureWindowsPath
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "PyAnsys" / "src"))
from pyansys_fluent.common import quote_scheme_string, remote_file_exists
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256

RUN_ROOT = ROOT / "PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z"
RUN = json.loads((RUN_ROOT / "run-manifest.json").read_text(encoding="utf-8"))
FIGURES = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/figures"
LOCAL = FIGURES / "E2.7-CONT5000-phase2-vof-xy-z0-final13586-v3.png"
OUT = ROOT / "PyAnsys/output/phase72a_e27_cont5000_native_vof_v3"
REMOTE_BASE = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\FamilyE\E2.7-continuation-5000\20260923T102912Z")
REMOTE = str(REMOTE_BASE / "figures" / "P72A-E2.7-CONT5000-phase2-vof-xy-z0-N13586-v3.png")
EXPECTED = 13586


def main() -> None:
    assert RUN["status"] == "COMPLETE" and RUN["terminal_native_iteration"] == EXPECTED
    pair = RUN["durable_final_pair"]
    record = {"status": "STARTED", "solve_issued": False, "server_id": "1", "native_iteration": EXPECTED,
              "source_case": pair["case"], "source_data": pair["data"],
              "source_case_sha256": pair["case_sha256"], "source_data_sha256": pair["data_sha256"],
              "source_run_manifest": str((RUN_ROOT / "run-manifest.json").relative_to(ROOT)),
              "surface": {"type": "XY plane", "z_m": 0.0}, "field": "phase-2-vof", "display_range": [0.0, 1.0],
              "local_png": str(LOCAL.relative_to(ROOT)), "remote_png": REMOTE,
              "layout": "portrait 1600x1800; shortened native contour name; compact legend; date/version title and axis widget hidden"}
    OUT.mkdir(parents=True, exist_ok=True)
    solver = connect("1", start_transcript=False, tcp_timeout_seconds=5)
    assert "2025 R2" in str(solver.get_fluent_version())
    assert round(float(solver.settings.setup.named_expressions["P71V2Iteration"].get_value())) == EXPECTED
    assert remote_file_exists(solver, pair["case"]) and remote_file_exists(solver, pair["data"])
    scratch = PureWindowsPath(RUN["remote_paths"]["scratch_root"])
    ch = remote_file_sha256(solver, pair["case"], str(scratch / "vof-v3-source-case.sha256.txt"))
    dh = remote_file_sha256(solver, pair["data"], str(scratch / "vof-v3-source-data.sha256.txt"))
    assert (ch, dh) == (pair["case_sha256"], pair["data_sha256"])
    assert not remote_file_exists(solver, REMOTE), f"refusing to overwrite {REMOTE}"

    graphics = solver.settings.results.graphics
    contours = graphics.contour
    old = "p72a-e27-cont5000-phase2-vof"
    new = "E27-VOF"
    names = set(map(str, contours.get_object_names()))
    if old in names:
        contours.rename(old=old, new=new)
    elif "E27-phase2-VOF" in names:
        contours.rename(old="E27-phase2-VOF", new=new)
    contour = contours[new]
    contour.display()
    contour.set_state({"field": "phase-2-vof", "surfaces_list": ["p72a-e27-cont5000-xy-z0"],
                       "range_options": {"global_range": False, "auto_range": False, "clip_to_range": False,
                                         "minimum": 0.0, "maximum": 1.0},
                       "options": {"filled": True, "node_values": True, "boundary_values": False,
                                   "contour_lines": False}})
    cmap = contour.color_map.get_state()
    cmap.update({"font_size": 0.018, "length": 0.42, "width": 4.0})
    contour.color_map.set_state(cmap)
    graphics.colors.set_state({"titles": {"left_top": "", "left_bottom": "", "right_top": "",
                                           "right_middle": "", "right_bottom": ""}})
    graphics.windows.logo = False
    graphics.windows.axes.visible = False
    graphics.views.camera.projection(type="orthographic")
    graphics.views.auto_scale()
    graphics.views.camera.zoom(factor=1.15)
    graphics.picture.use_window_resolution = False
    graphics.picture.x_resolution = 1600
    graphics.picture.y_resolution = 1800
    graphics.picture.landscape = False
    record["contour_state"] = contour.get_state()
    record["color_state"] = graphics.colors.get_state()
    record["picture_state"] = graphics.picture.get_state()
    assert record["contour_state"]["field"] == "phase-2-vof"
    assert record["contour_state"]["range_options"]["minimum"] == 0.0
    assert record["contour_state"]["range_options"]["maximum"] == 1.0
    ensure_remote_directory(solver, str(REMOTE_BASE / "figures"))
    graphics.picture.save_picture(file_name=REMOTE)
    assert remote_file_exists(solver, REMOTE)
    encoded_path = REMOTE + ".base64.txt"
    powershell = f"[IO.File]::WriteAllText('{encoded_path}',[Convert]::ToBase64String([IO.File]::ReadAllBytes('{REMOTE}')))"
    encoded = base64.b64encode(powershell.encode("utf-16le")).decode("ascii")
    solver.scheme.eval(f'(system "{quote_scheme_string(f"cmd /c powershell -NoProfile -EncodedCommand {encoded}")}")')
    payload = base64.b64decode(read_text(solver, encoded_path), validate=True)
    assert payload.startswith(b"\x89PNG\r\n\x1a\n")
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL.write_bytes(payload)
    width, height = struct.unpack(">II", payload[16:24])
    record["png"] = {"width": width, "height": height, "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    assert (width, height) == (1600, 1800), f"Fluent exported unexpected dimensions {(width, height)}"
    record["status"] = "COMPLETE_NATIVE_FLUENT_EXPORT_AWAIT_VISUAL_QA"
    (OUT / "export-manifest.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": record["status"], "local_png": str(LOCAL), "png": record["png"]}, indent=2))


if __name__ == "__main__":
    main()

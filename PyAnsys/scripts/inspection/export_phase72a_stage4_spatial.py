"""Export native bulk-VF and EWF-thickness views of the verified N48483 pair."""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import argparse
import base64
import hashlib
import json
import math
import struct
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts/setup")]
import run_phase72a_stage4_analytical as native
from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType

OUT = ROOT / "output/phase72a-stage4-core-development/20261008/native-figures"
FIG = ROOT.parent / "Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/core-development/figures"
MANIFEST = OUT.parent / "core17/run-manifest.json"


def short_system(solver, command):
    command.encode("ascii")
    if len(command) > 1024 or any(c in command for c in "\r\n%!^&|<>"):
        raise ValueError("Unsafe or oversized native file command")
    codes = " ".join(map(str, command.encode("ascii")))
    result = solver.scheme.eval("(system (list->string (map integer->char '(" + codes + "))))")
    if result not in (0, None):
        raise RuntimeError(f"Native file command failed: {result}")


def fetch_png(solver, remote, target):
    """Use one bounded certutil command; preserve native PNG pixels exactly."""
    encoded = remote + ".b64.txt"
    if native.remote_file_exists(solver, encoded):
        raise FileExistsError(encoded)
    short_system(solver, f'cmd /c certutil -encode "{remote}" "{encoded}"')
    text = native.read_text(solver, encoded)
    body = "".join(line.strip() for line in text.splitlines() if not line.startswith("-----"))
    payload = base64.b64decode(body, validate=True)
    assert payload.startswith(b"\x89PNG\r\n\x1a\n")
    digest = hashlib.sha256(payload).hexdigest()
    scratch = str(PureWindowsPath(remote).parent / ("png-" + str(time.time_ns()) + ".sha256.txt"))
    assert native.checked_remote_sha256(solver, remote, scratch) == digest
    target.write_bytes(payload)
    return {"sha256": digest, "bytes": len(payload), "resolution": list(struct.unpack(">II", payload[16:24])),
            "transfer": "ONE_FILE_BOUNDED_CERTUTIL_ENCODE_NATIVE_TEXT_READ_AND_SHA256"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inspect", action="store_true")
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    FIG.mkdir(exist_ok=True)
    m = json.loads(MANIFEST.read_text())
    assert m["status"] == "CHECKPOINT_VERIFIED" and m["verified_native_end"] == 48483
    solver = native.attach()
    assert not solver.settings.solution.run_calculation.iterating()
    before = native.snapshot(solver)
    assert before["native_iteration"] == m["verified_native_end"]
    assert before["film"]["film_elapsed_time"] == m["verified_film_time_s"]
    assert before["parameters"] == m["prepared_parameters"]
    native.d.q.r.require_match({"fields": before["bulk"]}, {"fields": m["bulk_reference"]})
    graphics = solver.settings.results.graphics
    surfaces = solver.fields._field_info._get_surfaces_info()
    fields = solver.fields._field_info._get_scalar_fields_info()
    inspection = {"native_iteration": before["native_iteration"], "film_clock_s": before["film"]["film_elapsed_time"],
                  "surfaces": surfaces, "graphics_children": graphics.child_names,
                  "contour_names": graphics.contour.get_object_names(),
                  "picture": graphics.picture.get_state(),
                  "field_metadata": {k: v for k, v in fields.items() if k in ["phase-2-vof", "film-thickness", "film-mass"]}}
    native.dump(OUT / "inspection.json", inspection)
    if args.inspect:
        print(json.dumps(inspection, indent=2, default=str), flush=True)
        return
    stamp = datetime.now(timezone.utc).strftime("%H%M%S")
    remote_dir = PureWindowsPath(m["work_root"]) / ("native-figures-" + stamp)
    if not native.remote_file_exists(solver, remote_dir.as_posix()):
        short_system(solver, f'cmd /c mkdir "{remote_dir}"')
    assert native.remote_file_exists(solver, remote_dir.as_posix())
    pair = m["latest_pair"]
    for kind in ["case", "data"]:
        digest = native.checked_remote_sha256(solver, pair[kind], str(remote_dir / (kind + ".sha256.txt")))
        assert digest == pair[kind + "_sha256"]
    planes = solver.settings.results.surfaces.plane_surface
    plane = "p72s4-xy-z0"
    if plane not in planes.get_object_names():
        planes.create(name=plane)
    planes[plane].set_state({"method": "xy-plane", "z": 0.0})
    inlet_centres = np.asarray(solver.fields.field_data.get_field_data(SurfaceFieldDataRequest(
        surfaces=["liquidinlet"], data_types=[SurfaceDataType.FacesCentroid]))["liquidinlet"].face_centroids)
    inlet_y = float(inlet_centres[:, 1].mean())
    inlet_plane = "p72s4-inlet-xz"
    if inlet_plane not in planes.get_object_names():
        planes.create(name=inlet_plane)
    assert "zx-plane" in planes[inlet_plane].method.allowed_values()
    planes[inlet_plane].set_state({"method": "zx-plane", "y": inlet_y})
    clips = solver.settings.results.surfaces.iso_clip
    clip = "p72s4-film-back-half"
    if clip not in clips.get_object_names():
        clips.create(name=clip)
    assert "z-coordinate" in clips[clip].field.allowed_values()
    clips[clip].set_state({"field": "z-coordinate", "surfaces": ["wall", "wall:004"],
                           "range": {"minimum": -2.0, "maximum": 0.0}})
    upper_vf = "p72s4-vf-upper-y"
    upper_film = "p72s4-film-upper-y"
    for name, source in [(upper_vf, plane), (upper_film, clip)]:
        if name not in clips.get_object_names():
            clips.create(name=name)
        clips[name].set_state({"field": "y-coordinate", "surfaces": [source],
                               "range": {"minimum": 4.1, "maximum": 7.1}})
    graphics.lighting.lights_on = False
    graphics.windows.axes.visible = False
    record = {"status": "EXPORTING", "source_pair": pair, "server_id": "1", "solve_issued": False,
              "native_iteration": before["native_iteration"], "film_clock_s": before["film"]["film_elapsed_time"],
              "source_classification": "FINITE_CHECKPOINT_ACCURACY_UNQUALIFIED", "figures": [],
              "geometry_units": "m", "plane": planes[plane].get_state(), "film_cutaway": clips[clip].get_state(),
              "inlet_plane": planes[inlet_plane].get_state(), "inlet_height_basis": "Mean native liquidinlet face-centroid y",
              "upper_region": {"y_min_m": 4.1, "y_max_m": 7.1,
                               "vf_clip": clips[upper_vf].get_state(), "film_clip": clips[upper_film].get_state()},
              "lighting": graphics.lighting.get_state(),
              "active_film_walls": ["wall", "wall:004"],
              "claim_limit": "Bulk phase-2 VF is frozen; film thickness is a separate EWF field; no stationary-film claim"}
    cameras = {
        "whole": {"target": [-0.55, 3.5, 0], "position": [-0.55, 3.5, 12], "up": [0, 1, 0],
                  "width": 4.2, "height": 8.4, "resolution": [1200, 2400]},
        "upper": {"target": [-0.45, 5.6, 0], "position": [-0.45, 5.6, 12], "up": [0, 1, 0],
                  "width": 4.0, "height": 3.0, "resolution": [2400, 1800]},
        "inlet-section": {"target": [-0.45, inlet_y, -0.25], "position": [-0.45, inlet_y+10, -0.25],
                          "up": [0, 0, -1], "width": 4.0, "height": 3.0, "resolution": [2400, 1800]},
    }
    cameras["upper-detail"] = cameras["upper"]
    jobs = [("VF", "phase-2-vof", [plane], [0, 1], "whole"),
            ("VF", "phase-2-vof", [upper_vf], [0, 1], "upper"),
            ("VF", "phase-2-vof", [upper_vf], None, "upper-detail"),
            ("VF", "phase-2-vof", [inlet_plane], [0, 1], "inlet-section"),
            ("EWF", "film-thickness", [clip], [0, .0025], "whole"),
            ("EWF", "film-thickness", [upper_film], [0, .0025], "upper")]
    if args.preview:
        jobs = jobs[:1]
    for label, field, chosen, limits, view in jobs:
        name = "P72-" + label
        contours = graphics.contour
        if name not in contours.get_object_names():
            contours.create(name=name)
        contour = contours[name]
        assert field in contour.field.allowed_values()
        contour.set_state({"field": field, "surfaces_list": chosen,
                           "range_options": {"global_range": False, "auto_range": True, "clip_to_range": False},
                           "options": {"filled": True, "node_values": True, "boundary_values": field == "film-thickness", "contour_lines": False}})
        contour.range_options.compute()
        discovered = contour.range_options.get_state()
        if limits is None:
            observed_max = float(discovered["maximum"])
            assert observed_max > 0
            scale = 10 ** math.floor(math.log10(observed_max))
            upper = next(v * scale for v in [1, 2, 5, 10] if v * scale >= observed_max)
            limits = [0, upper]
        contour.range_options.set_state({"global_range": False, "auto_range": False,
                                         "clip_to_range": False, "minimum": limits[0], "maximum": limits[1]})
        cmap = contour.color_map.get_state()
        cmap.update({"font_size": .016, "length": .48, "width": 4.0})
        contour.color_map.set_state(cmap)
        graphics.colors.set_state({"titles": {"left_top": "", "left_bottom": "", "right_top": "", "right_middle": "", "right_bottom": ""}})
        graphics.windows.logo = False
        graphics.windows.axes.visible = False
        contour.display()
        camera = graphics.views.camera
        c = cameras[view]
        camera.projection(type="orthographic")
        camera.position(xyz=c["position"])
        camera.target(xyz=c["target"])
        camera.up_vector(xyz=c["up"])
        graphics.views.auto_scale()
        camera.position(xyz=c["position"])
        camera.target(xyz=c["target"])
        camera.up_vector(xyz=c["up"])
        camera.field(width=c["width"], height=c["height"])
        graphics.picture.use_window_resolution = False
        graphics.picture.landscape = view != "whole"
        graphics.picture.x_resolution, graphics.picture.y_resolution = c["resolution"]
        filename = f"native-N48483-{label.lower()}-{view}-{stamp}.png"
        remote = str(remote_dir / filename)
        assert not native.remote_file_exists(solver, remote)
        graphics.picture.save_picture(file_name=remote)
        artifact = fetch_png(solver, remote, FIG / filename)
        assert artifact["resolution"] == c["resolution"]
        record["figures"].append({"local": str(FIG / filename), "remote": remote, "field": field,
                                  "surfaces": chosen, "view": view, "observed_range": discovered,
                                  "display_range": limits, "contour_readback": contour.get_state(),
                                  "camera": c, "picture_readback": graphics.picture.get_state(),
                                  "visual_qa": "PENDING", **artifact})
        native.dump(OUT / ("export-" + stamp + ".json"), record)
        print("NATIVE_PNG_EXPORTED", filename, artifact, flush=True)
    after = native.snapshot(solver)
    assert after == before, "Scientific state changed during native export"
    record.update(status="EXPORTED_VISUAL_QA_PENDING", scientific_state_unchanged=True)
    native.dump(OUT / ("export-" + stamp + ".json"), record)
    print("SCIENTIFIC_STATE_UNCHANGED", flush=True)


if __name__ == "__main__":
    main()

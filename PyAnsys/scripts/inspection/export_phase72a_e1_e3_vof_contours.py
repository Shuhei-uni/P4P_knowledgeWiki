"""Export matched native Fluent phase-2 VOF contours from final E-family pairs; no solve."""

from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path, PureWindowsPath

from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.connection import connect
from pyansys_fluent.stage4_native import ensure_remote_directory


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "PyAnsys/output/phase72a_e1_e3_native_vof_contours_20260923_v2"
MANIFESTS = {
    "E0": ROOT / "PyAnsys/output/phase72a_ewf_family_e_student_20260922T115500Z/E0/run-manifest.json",
    "E1": ROOT / "PyAnsys/output/phase72a_ewf_student_e1_run_20260923T024000Z/E1/run-manifest.json",
    "E3": ROOT / "PyAnsys/output/phase72a_ewf_student_e3_run_20260923T032500Z/E3/run-manifest.json",
    "E2.7": ROOT / "PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/run-manifest.json",
}
REMOTE_DIR = PureWindowsPath(
    r"C:\Users\Shuhei Yokkaichi\Documents\OneDrive - The University of Auckland"
    r"\P4P-Fluent-Artifacts\Phase72A\FamilyE\figures\E1-E3-VOF-20260923-v2"
)
REMOTE_E27_DIR = PureWindowsPath(
    r"C:\Users\Shuhei Yokkaichi\Documents\OneDrive - The University of Auckland"
    r"\P4P-Fluent-Artifacts\Phase72A\FamilyE\figures\E2.7-VOF-20260923"
)
OUTPUT_DIRS = {
    "E0": ROOT / "PyAnsys/output/phase72a_e0_native_vof_contour_20260923",
    "E2.7": ROOT / "PyAnsys/output/phase72a_e27_native_vof_contour_20260923",
}
REMOTE_DIRS = {
    "E0": REMOTE_DIR.parent / "E0-VOF-20260923",
    "E2.7": REMOTE_E27_DIR,
}
PLANE = "p72a-e13-xy-z0"
CONTOUR = "p72a-e13-phase2-vof"


def write(record: dict, output_dir: Path) -> None:
    (output_dir / "export-manifest.json").write_text(json.dumps(record, indent=2, default=str) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=("E0", "E1", "E3", "E2.7"), help="Export one case; default is the original E1/E3 pair")
    args = parser.parse_args()
    cases = (args.case,) if args.case else ("E1", "E3")
    output_dir = OUTPUT_DIRS.get(args.case, OUT)
    remote_dir = REMOTE_DIRS.get(args.case, REMOTE_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    record = {"status": "STARTED", "server_id": "student", "solve_issued": False,
              "surface": {"type": "xy-plane", "z_m": 0.0},
              "field": "phase-2-vof", "display_range": [0.0, 1.0],
              "cases": {}}
    write(record, output_dir)
    solver = None
    try:
        solver = connect("student", start_transcript=False, tcp_timeout_seconds=5)
        assert "2025 R2" in str(solver.get_fluent_version())
        records = {case: json.loads(MANIFESTS[case].read_text()) for case in cases}
        for case, manifest in records.items():
            assert manifest["status"] == "COMPLETE"
            expected_iteration = 8586
            assert manifest["terminal_native_iteration_before_save"] == expected_iteration
            pair = manifest["durable_final_pair"]
            case_path, data_path = pair["case"], pair["data"]
            assert remote_file_exists(solver, case_path)
            assert remote_file_exists(solver, data_path)
            record["cases"][case] = {"case": case_path, "data": data_path,
                                      "source_manifest": str(MANIFESTS[case].relative_to(ROOT)),
                                      "checkpoint": "completed final native 8586",
                                      "case_sha256": pair["case_sha256"],
                                      "data_sha256": pair["data_sha256"]}
        write(record, output_dir)
        ensure_remote_directory(solver, str(remote_dir))
        for case in cases:
            info = record["cases"][case]
            solver.settings.file.read_case(file_name=info["case"])
            solver.settings.file.read_data(file_name=info["data"])
            assert round(float(solver.settings.setup.named_expressions["P71V2Iteration"].get_value())) == expected_iteration
            surfaces = solver.settings.results.surfaces.plane_surface
            if PLANE not in surfaces.get_object_names():
                surfaces.create(name=PLANE)
            surfaces[PLANE].set_state({"method": "xy-plane", "z": 0.0})
            assert surfaces[PLANE].get_state()["z"] == 0.0
            graphics = solver.settings.results.graphics
            contours = graphics.contour
            if CONTOUR not in contours.get_object_names():
                contours.create(name=CONTOUR)
            contour = contours[CONTOUR]
            assert "phase-2-vof" in contour.field.allowed_values()
            contour.set_state({"field": "phase-2-vof", "surfaces_list": [PLANE],
                               "range_options": {"global_range": False, "auto_range": False,
                                                 "clip_to_range": False, "minimum": 0.0, "maximum": 1.0},
                               "options": {"filled": True, "node_values": True,
                                           "boundary_values": False, "contour_lines": False}})
            info["contour_state"] = contour.get_state()
            assert info["contour_state"]["field"] == "phase-2-vof"
            assert info["contour_state"]["range_options"]["auto_range"] is False
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
            remote_png = str(remote_dir / f"P72A-{case}-phase2-vof-xy-z0-final8586.png")
            graphics.picture.save_picture(file_name=remote_png)
            assert remote_file_exists(solver, remote_png)
            info["remote_png"] = remote_png
            info["picture_state"] = graphics.picture.get_state()
            info["status"] = "EXPORTED_NATIVE_FLUENT"
            write(record, output_dir)
        record["status"] = "EXPORTED_NATIVE_FLUENT_AWAIT_LOCAL_QA"
        write(record, output_dir)
        print(json.dumps({"status": record["status"], "images": {c: record["cases"][c]["remote_png"] for c in record["cases"]}}, indent=2))
    except Exception as exc:
        record["status"] = "EXPORT_BLOCKED"
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc()
        write(record, output_dir)
        raise


if __name__ == "__main__":
    main()

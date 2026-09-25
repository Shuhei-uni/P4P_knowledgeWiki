#!/usr/bin/env python3
"""Compute terminal EWF wetted area from the preserved Fluent HDF5 pair."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
RUN_ROOT = ROOT / "PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z"
RUN = json.loads((RUN_ROOT / "run-manifest.json").read_text(encoding="utf-8"))
FIGURE_MANIFEST = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/figures/E2.7-CONT5000-requested-histories-manifest.json"
OUT = ROOT / "PyAnsys/output/phase72a_e27_cont5000_wetted_area/wetted-area.json"
LOCAL_PAIR = (
    Path.home()
    / "Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase72A/FamilyE/E2.7-continuation-5000/20260923T102912Z"
)
CASE = LOCAL_PAIR / "P72A-E2.7-CONT5000-final-N13586.cas.h5"
DATA = LOCAL_PAIR / "P72A-E2.7-CONT5000-final-N13586.dat.h5"
WALL_NAME = "wall"
CRITICAL_THICKNESS_M = 1e-10
FLUENT_REPORTED_GEOMETRIC_AREA_M2 = 53.4369522992766


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    expected_pair = RUN["durable_final_pair"]
    case_hash, data_hash = sha256(CASE), sha256(DATA)
    if case_hash != expected_pair["case_sha256"] or data_hash != expected_pair["data_sha256"]:
        raise RuntimeError("Local OneDrive final pair does not match the completed-run manifest hashes")

    with h5py.File(CASE, "r") as case, h5py.File(DATA, "r") as data:
        topology = case["meshes/1/faces/zoneTopology"]
        zone_names = [name.decode("utf-8") for name in topology["name"][0].split(b";")]
        matches = [i for i, name in enumerate(zone_names) if name == WALL_NAME]
        if len(matches) != 1:
            raise RuntimeError(f"Expected one wall zone in Fluent mesh; found {matches}")
        zone_i = matches[0]
        face_start = int(topology["minId"][zone_i]) - 1
        face_stop = int(topology["maxId"][zone_i])
        face_count = face_stop - face_start

        nodes_per_face_all = case["meshes/1/faces/nodes/1/nnodes"][()].astype(np.int64)
        connectivity_all = case["meshes/1/faces/nodes/1/nodes"][()].astype(np.int64)
        coordinates = case["meshes/1/nodes/coords/426"][()]
        offsets = np.concatenate(([0], np.cumsum(nodes_per_face_all)))
        film_height = data["results/1/phase-1/faces/SV_EFILM_HEIGHT/1"][()]
        if len(film_height) != face_count:
            raise RuntimeError(f"Film-height faces ({len(film_height)}) do not match {WALL_NAME} faces ({face_count})")

        face_areas = np.empty(face_count, dtype=np.float64)
        for local_i, global_i in enumerate(range(face_start, face_stop)):
            node_ids = connectivity_all[offsets[global_i] : offsets[global_i + 1]] - 1
            vertices = coordinates[node_ids]
            # Polygon vector area; matches Fluent's native geometric wall-area report.
            face_areas[local_i] = 0.5 * np.linalg.norm(
                np.cross(vertices, np.roll(vertices, -1, axis=0)).sum(axis=0)
            )

    if np.any(~np.isfinite(film_height)) or np.any(film_height < 0):
        raise RuntimeError("Film thickness array contains non-finite or negative values")
    geometric_area = float(face_areas.sum())
    geometric_error = abs(geometric_area - FLUENT_REPORTED_GEOMETRIC_AREA_M2)
    if geometric_error > 1e-10:
        raise RuntimeError(f"Reconstructed wall area {geometric_area} differs from Fluent reference by {geometric_error} m^2")

    wet = film_height > CRITICAL_THICKNESS_M
    covered_area = float(face_areas[wet].sum())
    dry_area = geometric_area - covered_area
    result = {
        "status": "COMPUTED_AND_GEOMETRY_CROSSCHECKED",
        "native_iteration": RUN["terminal_native_iteration"],
        "field": "film-coverage",
        "coverage_rule": "Fluent EWF Film Coverage equals 1 when film thickness exceeds the critical film thickness and 0 when below it.",
        "critical_film_thickness_m": CRITICAL_THICKNESS_M,
        "measurement_method": "Integrate the reconstructed per-face Film Coverage indicator over the active EWF wall, using mesh face polygon areas from the Fluent case HDF5 and EWF face thicknesses from the paired Fluent data HDF5.",
        "source_case": str(CASE),
        "source_data": str(DATA),
        "source_case_sha256": case_hash,
        "source_data_sha256": data_hash,
        "wall_zone": WALL_NAME,
        "wall_face_count": int(face_count),
        "wet_face_count": int(np.count_nonzero(wet)),
        "dry_face_count": int(face_count - np.count_nonzero(wet)),
        "zero_thickness_face_count": int(np.count_nonzero(film_height == 0.0)),
        "positive_but_below_coverage_threshold_face_count": int(np.count_nonzero((film_height > 0.0) & ~wet)),
        "wet_area_m2": covered_area,
        "dry_area_m2": dry_area,
        "wet_area_fraction": covered_area / geometric_area,
        "geometric_wall_area_m2_from_hdf5_mesh": geometric_area,
        "geometric_wall_area_m2_from_prior_fluent_native_report": FLUENT_REPORTED_GEOMETRIC_AREA_M2,
        "geometric_area_abs_difference_m2": geometric_error,
        "native_report_note": "The EWF wetted-area integral was reconstructed offline from the preserved terminal Fluent HDF5 pair because Server 1 became unreachable during an attempted live report calculation. The per-face wall area reconstruction exactly matches the prior Fluent-native wall-area report; wetted area uses Fluent's documented Film Coverage threshold definition.",
        "documentation": "https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_wet.html",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    plot_data = json.loads(FIGURE_MANIFEST.read_text(encoding="utf-8"))
    plot_data["ewf_area"]["wetted_area_m2_terminal"] = covered_area
    plot_data["ewf_area"]["wetted_area_fraction_terminal"] = covered_area / geometric_area
    plot_data["ewf_area"]["wetted_area_source"] = str(OUT.relative_to(ROOT))
    plot_data["ewf_area"]["wetted_area_method"] = result["measurement_method"]
    FIGURE_MANIFEST.write_text(json.dumps(plot_data, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

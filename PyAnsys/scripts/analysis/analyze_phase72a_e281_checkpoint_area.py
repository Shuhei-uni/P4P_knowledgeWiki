#!/usr/bin/env python3
"""Reconstruct E2.81 wall coverage and thickness-band areas from saved pairs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import h5py
import numpy as np

EXPECTED_WALL_AREA_M2 = 53.4369522992766
COVERAGE_CRITICAL_THICKNESS_M = 1e-10
THRESHOLDS_MM = (0.01, 0.05, 0.10, 0.25, 0.50)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def native_coordinate(case_path: Path) -> int:
    match = re.search(r"checkpoint-(\d+)-", case_path.name)
    if match:
        return int(match.group(1))
    match = re.search(r"-N(\d+)\.cas\.h5$", case_path.name)
    if match:
        return int(match.group(1))
    raise ValueError(f"Cannot identify native iteration from {case_path.name}")


def face_area_weights(case: h5py.File) -> tuple[np.ndarray, int]:
    topology = case["meshes/1/faces/zoneTopology"]
    zone_names = [item.decode("utf-8") for item in topology["name"][0].split(b";")]
    matching_zones = [i for i, name in enumerate(zone_names) if name == "wall"]
    if len(matching_zones) != 1:
        raise RuntimeError(f"Expected exactly one EWF wall zone; found {matching_zones}")
    zone_i = matching_zones[0]
    first_face = int(topology["minId"][zone_i]) - 1
    stop_face = int(topology["maxId"][zone_i])
    face_count = stop_face - first_face

    nodes_per_face = case["meshes/1/faces/nodes/1/nnodes"][()].astype(np.int64)
    connectivity = case["meshes/1/faces/nodes/1/nodes"][()].astype(np.int64)
    coordinates = case["meshes/1/nodes/coords/426"][()]
    offsets = np.concatenate(([0], np.cumsum(nodes_per_face)))
    areas = np.empty(face_count, dtype=np.float64)
    for local_i, global_i in enumerate(range(first_face, stop_face)):
        node_ids = connectivity[offsets[global_i] : offsets[global_i + 1]] - 1
        vertices = coordinates[node_ids]
        areas[local_i] = 0.5 * np.linalg.norm(
            np.cross(vertices, np.roll(vertices, -1, axis=0)).sum(axis=0)
        )
    return areas, face_count


def inspect_pair(case_path: Path, wall_areas: np.ndarray, wall_face_count: int) -> dict[str, Any]:
    data_path = Path(str(case_path).replace(".cas.h5", ".dat.h5"))
    if not data_path.is_file():
        raise FileNotFoundError(f"Missing paired data file for {case_path}")
    with h5py.File(data_path, "r") as data:
        thickness = data["results/1/phase-1/faces/SV_EFILM_HEIGHT/1"][()].astype(np.float64)
    if len(thickness) != wall_face_count:
        raise RuntimeError(
            f"{case_path.name}: found {len(thickness)} film heights for {wall_face_count} wall faces"
        )
    if np.any(~np.isfinite(thickness)) or np.any(thickness < 0):
        raise RuntimeError(f"{case_path.name}: film thickness contains invalid values")
    total_area = float(wall_areas.sum())
    error = abs(total_area - EXPECTED_WALL_AREA_M2)
    if error > 1e-10:
        raise RuntimeError(
            f"{case_path.name}: reconstructed wall area {total_area} differs from Fluent by {error} m^2"
        )

    wet = thickness > COVERAGE_CRITICAL_THICKNESS_M
    row: dict[str, Any] = {
        "native_iteration": native_coordinate(case_path),
        "pair_case": str(case_path),
        "pair_data": str(data_path),
        "case_sha256": sha256(case_path),
        "data_sha256": sha256(data_path),
        "wall_face_count": wall_face_count,
        "wall_area_m2": total_area,
        "wall_area_abs_error_vs_fluent_m2": error,
        "wet_area_m2_film_coverage": float(wall_areas[wet].sum()),
        "wet_area_fraction_film_coverage": float(wall_areas[wet].sum() / total_area),
        "dry_area_m2_film_coverage": float(wall_areas[~wet].sum()),
        "max_film_thickness_mm": float(np.max(thickness) * 1000.0),
        "area_weighted_mean_thickness_mm": float(np.dot(wall_areas, thickness) / total_area * 1000.0),
        "positive_thickness_area_m2_below_coverage_threshold": float(
            wall_areas[(thickness > 0.0) & ~wet].sum()
        ),
    }
    for threshold_mm in THRESHOLDS_MM:
        area = float(wall_areas[thickness >= threshold_mm / 1000.0].sum())
        key = f"area_at_or_above_{threshold_mm:g}_mm_m2"
        row[key] = area
        row[key.replace("area_at_or_above", "fraction_at_or_above").replace("_m2", "")] = area / total_area

    band_edges_mm = (0.0, *THRESHOLDS_MM, float("inf"))
    for lower, upper in zip(band_edges_mm[:-1], band_edges_mm[1:]):
        low_m = lower / 1000.0
        high_m = upper / 1000.0
        in_band = (thickness >= low_m) & (thickness < high_m)
        upper_name = "inf" if np.isinf(upper) else f"{upper:g}"
        key = f"area_{lower:g}_to_{upper_name}_mm_m2"
        row[key] = float(wall_areas[in_band].sum())
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_manifest", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
    local_root = Path(manifest["local_run_root"])
    checkpoint_root = Path(manifest["local_checkpoint_root"])
    checkpoint_pairs = sorted(checkpoint_root.glob("checkpoint-*.cas.h5"))
    named_pairs = sorted(
        [
            *local_root.glob("P72A-E2.81-start-N*.cas.h5"),
            *local_root.glob("P72A-E2.81-final-N*.cas.h5"),
            *local_root.glob("P72A-E2.81-review-N*.cas.h5"),
        ]
    )
    pairs = sorted({path.resolve() for path in [*checkpoint_pairs, *named_pairs]}, key=native_coordinate)
    if not pairs:
        raise RuntimeError(f"No paired E2.81 case files found under {local_root}")

    with h5py.File(pairs[0], "r") as first_case:
        wall_areas, wall_face_count = face_area_weights(first_case)
    rows = [inspect_pair(path, wall_areas, wall_face_count) for path in pairs]
    rows.sort(key=lambda row: row["native_iteration"])
    out_dir = Path(manifest["local_output_root"]) / "checkpoint-area"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "checkpoint-thickness-area.json"
    csv_path = out_dir / "checkpoint-thickness-area.csv"
    output = {
        "status": "COMPUTED_AND_GEOMETRY_CROSSCHECKED",
        "experiment": "E2.81",
        "wall_zone": "wall",
        "coverage_rule": "Film Coverage is one when film thickness exceeds the documented 1e-10 m critical threshold.",
        "coverage_critical_thickness_m": COVERAGE_CRITICAL_THICKNESS_M,
        "cumulative_thresholds_mm": list(THRESHOLDS_MM),
        "disjoint_bands_mm": [list(pair) for pair in zip((0.0, *THRESHOLDS_MM), (*THRESHOLDS_MM, None))],
        "wall_face_count": wall_face_count,
        "reconstructed_geometric_wall_area_m2": float(wall_areas.sum()),
        "fluent_reported_geometric_wall_area_m2": EXPECTED_WALL_AREA_M2,
        "checkpoint_pair_count": len(checkpoint_pairs),
        "analyzed_pair_count_including_start_and_final": len(rows),
        "rows": rows,
    }
    json_path.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({k: v for k, v in output.items() if k != "rows"}, indent=2))
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()

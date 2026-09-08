#!/usr/bin/env python3
"""Inspect a Fluent ``.msh.h5`` artifact without loading or modifying Fluent.

The script reads the public HDF5 structure written by Fluent Meshing and emits
a compact JSON record covering artifact identity, mesh counts, coordinate
bounds, zone topology, cell-type counts, and boundary-zone geometry. It does
not estimate solver-side quality metrics that are not explicitly stored in the
mesh file; those require a later authoritative Fluent inspection.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np


CELL_TYPE_LABELS = {
    1: "triangle",
    2: "tetrahedron",
    3: "quadrilateral",
    4: "hexahedron",
    5: "pyramid",
    6: "wedge",
    7: "polyhedron",
}

ZONE_TYPE_LABELS = {
    2: "interior",
    3: "wall",
    5: "pressure-outlet",
    10: "velocity-inlet",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mesh", type=Path, help="Local Fluent .msh.h5 file")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. Existing files are not overwritten.",
    )
    return parser.parse_args()


def scalar_attr(group: h5py.Group, name: str) -> int | float | str | None:
    value = group.attrs.get(name)
    if value is None:
        return None
    array = np.asarray(value).reshape(-1)
    if not len(array):
        return None
    item = array[0]
    if isinstance(item, bytes):
        return item.decode("utf-8", "replace")
    if hasattr(item, "item"):
        return item.item()
    return item


def decoded_blob(dataset: h5py.Dataset) -> str:
    values = np.asarray(dataset[...]).reshape(-1)
    if not len(values):
        return ""
    value = values[0]
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)


def semicolon_names(dataset: h5py.Dataset, expected: int) -> list[str]:
    names = [part for part in decoded_blob(dataset).split(";") if part]
    if len(names) != expected:
        raise ValueError(
            f"Expected {expected} semicolon-delimited names at {dataset.name}, "
            f"found {len(names)}: {names}"
        )
    return names


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_coordinates(mesh: h5py.Group, expected_count: int) -> np.ndarray:
    coordinates = np.empty((expected_count, 3), dtype=np.float64)
    covered = np.zeros(expected_count, dtype=bool)
    for dataset in mesh["nodes/coords"].values():
        minimum = int(scalar_attr(dataset, "minId") or 0)
        maximum = int(scalar_attr(dataset, "maxId") or 0)
        if minimum < 1 or maximum < minimum:
            raise ValueError(f"Invalid node-ID range in {dataset.name}")
        values = np.asarray(dataset[...], dtype=np.float64)
        expected_shape = (maximum - minimum + 1, 3)
        if values.shape != expected_shape:
            raise ValueError(
                f"Coordinate shape mismatch at {dataset.name}: "
                f"expected {expected_shape}, found {values.shape}"
            )
        coordinates[minimum - 1 : maximum] = values
        covered[minimum - 1 : maximum] = True
    if not np.all(covered):
        missing = int(np.count_nonzero(~covered))
        raise ValueError(f"Coordinate sections leave {missing} node IDs uncovered")
    return coordinates


def topology_records(group: h5py.Group, *, kind: str) -> list[dict[str, Any]]:
    count = int(scalar_attr(group, "nZones") or 0)
    names = semicolon_names(group["name"], count)
    ids = np.asarray(group["id"][...], dtype=np.int64)
    minima = np.asarray(group["minId"][...], dtype=np.int64)
    maxima = np.asarray(group["maxId"][...], dtype=np.int64)
    dimensions = np.asarray(group["dimension"][...], dtype=np.int64)
    zone_types = (
        np.asarray(group["zoneType"][...], dtype=np.int64)
        if "zoneType" in group
        else np.full(count, -1, dtype=np.int64)
    )
    records: list[dict[str, Any]] = []
    for index in range(count):
        code = int(zone_types[index])
        record: dict[str, Any] = {
            "id": int(ids[index]),
            "name": names[index],
            "dimension": int(dimensions[index]),
            "min_id": int(minima[index]),
            "max_id": int(maxima[index]),
            f"{kind}_count": int(maxima[index] - minima[index] + 1),
        }
        if code >= 0:
            record["zone_type_code"] = code
            record["zone_type"] = ZONE_TYPE_LABELS.get(code, f"code-{code}")
        records.append(record)
    return records


def polygon_area_vector(points: np.ndarray) -> np.ndarray:
    """Return the oriented area vector using Newell's polygon formula."""
    return 0.5 * np.sum(np.cross(points, np.roll(points, -1, axis=0)), axis=0)


def boundary_geometry(
    mesh: h5py.Group,
    coordinates: np.ndarray,
    face_zones: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sections = mesh["faces/nodes"]
    c0_sections = mesh["faces/c0"]
    c1_sections = mesh["faces/c1"]
    zone_by_range = {
        (int(record["min_id"]), int(record["max_id"])): record
        for record in face_zones
    }
    results: list[dict[str, Any]] = []
    total_area_vector = np.zeros(3, dtype=np.float64)
    total_boundary_area = 0.0

    for section_name, section in sections.items():
        minimum = int(scalar_attr(section, "minId") or 0)
        maximum = int(scalar_attr(section, "maxId") or 0)
        zone = zone_by_range.get((minimum, maximum))
        if zone is None or zone.get("zone_type") == "interior":
            continue

        node_counts = np.asarray(section["nnodes"][...], dtype=np.int64)
        node_ids = np.asarray(section["nodes"][...], dtype=np.int64)
        if int(node_counts.sum()) != len(node_ids):
            raise ValueError(f"Face-node count mismatch in {section.name}")

        offsets = np.concatenate(([0], np.cumsum(node_counts)))
        face_areas = np.empty(len(node_counts), dtype=np.float64)
        face_centroids = np.empty((len(node_counts), 3), dtype=np.float64)
        area_vectors = np.empty((len(node_counts), 3), dtype=np.float64)
        used_nodes: list[np.ndarray] = []
        for index in range(len(node_counts)):
            ids = node_ids[offsets[index] : offsets[index + 1]]
            points = coordinates[ids - 1]
            vector = polygon_area_vector(points)
            area_vectors[index] = vector
            face_areas[index] = np.linalg.norm(vector)
            face_centroids[index] = np.mean(points, axis=0)
            used_nodes.append(ids)

        unique_nodes = np.unique(np.concatenate(used_nodes))
        zone_points = coordinates[unique_nodes - 1]
        bounds_min = zone_points.min(axis=0)
        bounds_max = zone_points.max(axis=0)
        spans = bounds_max - bounds_min
        area = float(face_areas.sum())
        vector_sum = area_vectors.sum(axis=0)
        total_area_vector += vector_sum
        total_boundary_area += area
        if area > 0:
            weighted_centroid = np.average(face_centroids, axis=0, weights=face_areas)
            mean_normal = vector_sum / area
        else:
            weighted_centroid = np.full(3, np.nan)
            mean_normal = np.full(3, np.nan)

        c0 = np.asarray(c0_sections[section_name][...], dtype=np.int64)
        c1 = np.asarray(c1_sections[section_name][...], dtype=np.int64)
        constant_axes = [
            axis
            for axis, span in zip(("x", "y", "z"), spans, strict=True)
            if abs(float(span)) <= 1.0e-10
        ]
        results.append(
            {
                **zone,
                "section": section_name,
                "unique_node_count": int(len(unique_nodes)),
                "nodes_per_face": {
                    str(int(key)): int(value)
                    for key, value in sorted(Counter(node_counts.tolist()).items())
                },
                "area_m2": area,
                "face_area_m2": {
                    "minimum": float(face_areas.min()),
                    "mean": float(face_areas.mean()),
                    "maximum": float(face_areas.max()),
                },
                "bounds_m": {
                    "minimum": bounds_min.tolist(),
                    "maximum": bounds_max.tolist(),
                    "span": spans.tolist(),
                },
                "constant_coordinate_axes": constant_axes,
                "area_weighted_face_centroid_m": weighted_centroid.tolist(),
                "oriented_area_vector_m2": vector_sum.tolist(),
                "area_weighted_mean_normal": mean_normal.tolist(),
                "adjacency": {
                    "c0_zero_count": int(np.count_nonzero(c0 == 0)),
                    "c1_zero_count": int(np.count_nonzero(c1 == 0)),
                },
            }
        )

    closure_norm = float(np.linalg.norm(total_area_vector))
    closure_ratio = closure_norm / total_boundary_area if total_boundary_area else None
    return results, {
        "total_boundary_area_m2": total_boundary_area,
        "oriented_area_vector_sum_m2": total_area_vector.tolist(),
        "oriented_area_vector_closure_ratio": closure_ratio,
    }


def inspect(mesh_path: Path) -> dict[str, Any]:
    stat = mesh_path.stat()
    with h5py.File(mesh_path, "r") as handle:
        mesh = handle["meshes/1"]
        cell_count = int(scalar_attr(mesh, "cellCount") or 0)
        face_count = int(scalar_attr(mesh, "faceCount") or 0)
        node_count = int(scalar_attr(mesh, "nodeCount") or 0)
        coordinates = load_coordinates(mesh, node_count)
        cell_zones = topology_records(mesh["cells/zoneTopology"], kind="cell")
        face_zones = topology_records(mesh["faces/zoneTopology"], kind="face")
        node_zones = topology_records(mesh["nodes/zoneTopology"], kind="node")
        cell_codes = np.asarray(mesh["cells/ctype/1/cell-types"][...], dtype=np.int64)
        cell_type_counts = {
            f"{int(code)}:{CELL_TYPE_LABELS.get(int(code), 'unknown')}": int(count)
            for code, count in zip(*np.unique(cell_codes, return_counts=True), strict=True)
        }
        boundary_zones, boundary_summary = boundary_geometry(
            mesh, coordinates, face_zones
        )
        bounds_min = coordinates.min(axis=0)
        bounds_max = coordinates.max(axis=0)

        settings: dict[str, str] = {}
        if "settings" in handle:
            for name in ("Origin", "Solver", "Version"):
                if name in handle["settings"]:
                    settings[name.lower()] = decoded_blob(handle["settings"][name])

        return {
            "schema": "p4p.fluent-mesh-h5-inspection.v1",
            "inspected_at_utc": datetime.now(timezone.utc).isoformat(),
            "artifact": {
                "path": str(mesh_path.resolve()),
                "size_bytes": stat.st_size,
                "modified_at_utc": datetime.fromtimestamp(
                    stat.st_mtime, timezone.utc
                ).isoformat(),
                "sha256": sha256_file(mesh_path),
            },
            "stored_metadata": {
                "dimension": int(scalar_attr(mesh, "dimension") or 0),
                "units": scalar_attr(mesh, "units"),
                "mesh_version": int(scalar_attr(mesh, "version") or 0),
                **settings,
            },
            "counts": {
                "cells": cell_count,
                "faces": face_count,
                "nodes": node_count,
                "edges": int(scalar_attr(mesh, "edgeCount") or 0),
                "boundary_faces": int(
                    sum(
                        zone["face_count"]
                        for zone in face_zones
                        if zone.get("zone_type") != "interior"
                    )
                ),
                "interior_faces": int(
                    sum(
                        zone["face_count"]
                        for zone in face_zones
                        if zone.get("zone_type") == "interior"
                    )
                ),
            },
            "coordinate_bounds_m": {
                "minimum": bounds_min.tolist(),
                "maximum": bounds_max.tolist(),
                "span": (bounds_max - bounds_min).tolist(),
            },
            "cell_type_counts": cell_type_counts,
            "cell_zones": cell_zones,
            "face_zones": face_zones,
            "node_zones": node_zones,
            "boundary_geometry": boundary_zones,
            "boundary_summary": boundary_summary,
            "limitations": [
                "No Fluent session was loaded or modified.",
                "Face centroids are vertex means, area-weighted across each zone.",
                "Solver-side mesh quality metrics are not inferred from meshing-workflow targets.",
                "Geometry equivalence and flow-behaviour parity with setup 08b are not established by this structural inspection.",
            ],
        }


def main() -> int:
    args = parse_args()
    mesh_path = args.mesh.expanduser().resolve()
    if not mesh_path.is_file():
        raise FileNotFoundError(mesh_path)
    payload = inspect(mesh_path)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        output = args.output.expanduser().resolve()
        if output.exists():
            raise FileExistsError(f"Refusing to overwrite existing output: {output}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered + "\n", encoding="utf-8")
        print(f"\nWrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

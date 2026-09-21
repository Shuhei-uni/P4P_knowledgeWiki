#!/usr/bin/env python3
"""Prove Phase 7b's vertical cutoff mapping from two exact local artifacts.

Read-only HDF5 inspection: no Fluent connection, solver operation, input write,
or claim of complete three-dimensional geometry equivalence. The optional
output is a new JSON evidence file; existing outputs are never overwritten.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np


_SPEC = importlib.util.spec_from_file_location(
    "phase07b_mesh_helpers", Path(__file__).with_name("inspect_fluent_mesh_h5.py")
)
assert _SPEC is not None and _SPEC.loader is not None
helpers = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(helpers)

EXPECTED_OLD_SHA256 = "2771ef93c30518c5706688814474c3860e2693c2a70ed7893e5c82bcc9361b9c"
EXPECTED_FULL_SHA256 = "0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394"
LANDMARK_TOLERANCE_M = 1.0e-5
MAX_AREA_RELATIVE_DIFFERENCE = 0.005
CAP_RESOLUTION_M = 0.001  # Historical cutoff was recorded to millimetres.
FRACTIONS = (0.2, 0.4, 0.6, 0.8, 1.0)


def extract_geometry(
    path: Path, expected_sha256: str, selected_names: tuple[str, ...]
) -> dict[str, Any]:
    digest = helpers.sha256_file(path)
    if digest != expected_sha256:
        raise ValueError(f"Artifact identity mismatch for {path}: {digest}")
    with h5py.File(path, "r") as handle:
        mesh = handle["meshes/1"]
        count = int(helpers.scalar_attr(mesh, "nodeCount"))
        coordinates = helpers.load_coordinates(mesh, count)
        topology = helpers.topology_records(mesh["faces/zoneTopology"], kind="face")
        zones = {zone["name"]: zone for zone in topology}
        missing = set(selected_names) - set(zones)
        if missing:
            raise ValueError(f"Missing boundary zones in {path}: {sorted(missing)}")
        # A solver case can store every face zone in one connectivity section.
        # Slice intersections by face IDs; do not require zone/section equality.
        sections = []
        for section in mesh["faces/nodes"].values():
            first = int(helpers.scalar_attr(section, "minId"))
            last = int(helpers.scalar_attr(section, "maxId"))
            if not any(
                first <= zones[name]["max_id"] and last >= zones[name]["min_id"]
                for name in selected_names
            ):
                continue
            counts = np.asarray(section["nnodes"], dtype=np.int64)
            offsets = np.concatenate(([0], np.cumsum(counts)))
            if len(counts) != last - first + 1 or int(offsets[-1]) != len(section["nodes"]):
                raise ValueError(f"Invalid face connectivity lengths: {section.name}")
            if np.any(counts < 3):
                raise ValueError(f"Non-polygon face in {section.name}")
            sections.append((section, first, last, offsets))
        boundaries = {}
        for name in selected_names:
            zone = zones[name]
            bounds_min = np.full(3, np.inf)
            bounds_max = np.full(3, -np.inf)
            area = 0.0
            vector = np.zeros(3)
            slices = []
            covered = 0
            for section, first, last, offsets in sections:
                low = max(first, zone["min_id"])
                high = min(last, zone["max_id"])
                if low > high:
                    continue
                start, stop = low - first, high - first + 1
                node_start, node_stop = int(offsets[start]), int(offsets[stop])
                ids = np.asarray(section["nodes"][node_start:node_stop], dtype=np.int64)
                if np.any(ids < 1) or np.any(ids > count):
                    raise ValueError(f"Invalid node IDs for {name} in {path}")
                points = coordinates[np.unique(ids) - 1]
                bounds_min = np.minimum(bounds_min, points.min(axis=0))
                bounds_max = np.maximum(bounds_max, points.max(axis=0))
                for index in range(start, stop):
                    local_ids = ids[offsets[index] - node_start : offsets[index + 1] - node_start]
                    face_vector = helpers.polygon_area_vector(coordinates[local_ids - 1])
                    area += float(np.linalg.norm(face_vector))
                    vector += face_vector
                covered += high - low + 1
                slices.append({
                    "connectivity_section": section.name,
                    "face_ids_inclusive": [low, high],
                    "flat_nodes_slice_half_open": [node_start, node_stop],
                })
            if covered != zone["face_count"] or area <= 0:
                raise ValueError(f"Incomplete or empty boundary extraction for {name}")
            boundaries[name] = {
                **zone,
                "evidence_label": "Observed",
                "bounds_m": {"minimum": bounds_min.tolist(), "maximum": bounds_max.tolist()},
                "area_m2": area,
                "oriented_area_vector_m2": vector.tolist(),
                "source_slices": slices,
            }
        return {
            "evidence_label": "Observed",
            "path": str(path),
            "sha256": digest,
            "size_bytes": path.stat().st_size,
            "counts": {
                name: int(helpers.scalar_attr(mesh, attribute))
                for name, attribute in (("cells", "cellCount"), ("faces", "faceCount"), ("nodes", "nodeCount"))
            },
            "stored_units": helpers.scalar_attr(mesh, "units"),
            "coordinate_datasets": [
                {"path": dataset.name, "node_ids_inclusive": [
                    int(helpers.scalar_attr(dataset, "minId")), int(helpers.scalar_attr(dataset, "maxId"))
                ]}
                for dataset in mesh["nodes/coords"].values()
            ],
            "zone_topology_path": mesh["faces/zoneTopology"].name,
            "coordinate_bounds_m": {"minimum": coordinates.min(axis=0).tolist(), "maximum": coordinates.max(axis=0).tolist()},
            "boundaries": boundaries,
        }


def derive_mapping(old: dict[str, Any], full: dict[str, Any]) -> dict[str, Any]:
    old_zones, full_zones = old["boundaries"], full["boundaries"]
    landmarks = []
    area_checks = []
    for old_name, full_name in (
        ("liquidinlet", "liquid-inlet"),
        ("steaminlet", "steam-inlet"),
        ("steamoutlet", "steam-outlet"),
    ):
        before, after = old_zones[old_name], full_zones[full_name]
        relative = abs(after["area_m2"] / before["area_m2"] - 1)
        if relative > MAX_AREA_RELATIVE_DIFFERENCE:
            raise ValueError(f"Boundary-area mismatch for {old_name}: {relative}")
        area_checks.append({"old_zone": old_name, "full_zone": full_name, "absolute_relative_difference": relative})
        edges = ("minimum", "maximum") if "inlet" in old_name else ("minimum",)
        if old_name == "steamoutlet":
            for boundary in (before, after):
                if abs(boundary["bounds_m"]["maximum"][1] - boundary["bounds_m"]["minimum"][1]) > LANDMARK_TOLERANCE_M:
                    raise ValueError("Steam-outlet landmark is not a horizontal plane")
        for edge in edges:
            y_old, y_full = before["bounds_m"][edge][1], after["bounds_m"][edge][1]
            landmarks.append({"evidence_label": "Observed", "old_zone": old_name, "full_zone": full_name,
                              "edge": edge, "old_y_m": y_old, "full_y_m": y_full, "offset_m": y_full - y_old})
    offsets = np.asarray([item["offset_m"] for item in landmarks])
    spread = float(np.ptp(offsets))
    if spread > LANDMARK_TOLERANCE_M:
        raise ValueError(f"Inconsistent vertical landmarks: offset spread {spread} m")
    bottom = old_zones["bottom"]["bounds_m"]
    if abs(bottom["maximum"][1] - bottom["minimum"][1]) > LANDMARK_TOLERANCE_M:
        raise ValueError("Historical bottom is not a horizontal plane")
    old_cut = float(bottom["minimum"][1])
    offset = float(np.median(offsets))
    raw_cap = old_cut + offset
    cap = round(raw_cap / CAP_RESOLUTION_M) * CAP_RESOLUTION_M
    if abs(cap - raw_cap) > LANDMARK_TOLERANCE_M:
        raise ValueError("Mapped cap is inconsistent with historical millimetre precision")
    floor = float(full["coordinate_bounds_m"]["minimum"][1])
    if abs(full_zones["wall"]["bounds_m"]["minimum"][1] - floor) > LANDMARK_TOLERANCE_M:
        raise ValueError("Global lower node datum is not reproduced on the wall")
    if floor >= cap:
        raise ValueError("Collector cap does not lie above the lower datum")
    return {
        "status": "PASS",
        "evidence_label": "Inferred",
        "interpretation": "Shared vertical elevation mapping only; not full three-dimensional geometry equivalence.",
        "coordinate_unit_basis": "Full mesh stores m; old metric interpretation is supported by historical records and matching 0.724 m inlet height/areas.",
        "landmark_tolerance_m": LANDMARK_TOLERANCE_M,
        "max_area_relative_difference": MAX_AREA_RELATIVE_DIFFERENCE,
        "landmarks": landmarks,
        "area_checks": area_checks,
        "offset_median_m": offset,
        "offset_spread_m": spread,
        "old_cutoff_y_m": old_cut,
        "mapped_cap_unrounded_m": raw_cap,
        "mapped_cap_from_offset_extrema_m": [old_cut + float(offsets.min()), old_cut + float(offsets.max())],
        "declared_cap_resolution_m": CAP_RESOLUTION_M,
        "collector_cap_y_m": cap,
        "lower_datum": {"evidence_label": "Observed", "y_m": floor,
                        "basis": "Minimum y of the exact full-mesh node coordinates, also present on wall; a numerical mesh datum."},
        "collector_height_span_m": cap - floor,
        "collector_tops": [{"fraction": fraction, "top_y_m": floor + fraction * (cap - floor)} for fraction in FRACTIONS],
        "limitations": [
            "The 1e-5 m check is a consistency tolerance, not a statistical uncertainty estimate.",
            "The nominal cap preserves the historical cutoff's millimetre reporting precision.",
            "No plant pool elevation or exact underlying CAD lower datum is established.",
            "The historical 900k cutoff maps to +0.020 m; Shuhei's later 342k mesh bottom at approximately 0 m is a distinct reference.",
            "No live Fluent state, actual selected cell centroids, collector cell counts, or collector volumes were inspected.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-mesh", required=True, type=Path)
    parser.add_argument("--full-mesh", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="New JSON evidence file; omit for stdout only")
    args = parser.parse_args()
    output = args.output.expanduser().resolve() if args.output else None
    if output and (output.exists() or "raw" in output.parts):
        raise ValueError("Output must be a new file outside any raw directory")
    old = extract_geometry(args.old_mesh.expanduser().resolve(), EXPECTED_OLD_SHA256,
                           ("liquidinlet", "steaminlet", "steamoutlet", "bottom"))
    full = extract_geometry(args.full_mesh.expanduser().resolve(), EXPECTED_FULL_SHA256,
                            ("liquid-inlet", "steam-inlet", "steam-outlet", "wall"))
    payload = {"schema": "p4p.phase07b-geometry-proof.v1", "observed_at_utc": datetime.now(timezone.utc).isoformat(),
               "method": "Local read-only HDF5 coordinates and face connectivity; no Fluent connection.",
               "old_artifact": old, "full_artifact": full, "mapping": derive_mapping(old, full)}
    rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as stream:
            stream.write(rendered)
        print(json.dumps({"status": "PASS", "output": str(output), "mapping": payload["mapping"]}, indent=2))
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

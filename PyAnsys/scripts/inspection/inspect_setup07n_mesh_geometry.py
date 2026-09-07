#!/usr/bin/env python3
"""Derive setup-07n brine crown and local vertical cell resolution.

This is a bounded Stage-0 mesh diagnostic.  It acquires the setup-07n local
writer lock, cold-loads only the accepted mesh on server 1, reads mesh data,
and writes a new JSON record.  It does not import a data field, initialize,
patch, iterate, or save Fluent state.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import io
import json
import math
import os
import re
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from ansys.fluent.core.field_data_interfaces import SurfaceDataType  # noqa: E402
from pyansys_fluent.common import (  # noqa: E402
    remote_file_exists,
    require_live_compute_node_count,
)
from pyansys_fluent.connection import connect  # noqa: E402

import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


EXPECTED_MESH_SHA256 = "0d75a86e53bc020aeefa4b13ef8616413a862b15646355d90d8037d1be888394"
EXPECTED_RANKS = 16
EXPECTED_BRINE_AREA_M2 = 0.19936247
GRAVITY_MS2 = 9.81


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--mesh", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--lock-file", required=True)
    parser.add_argument("--remote-hash-scratch", required=True)
    parser.add_argument("--probe-register-name", required=True)
    parser.add_argument("--tcp-timeout-seconds", type=float, default=5.0)
    return parser


@contextlib.contextmanager
def exclusive_writer_lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"another setup-07n writer owns {path}") from exc
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\nstarted_epoch={time.time()}\n")
        handle.flush()
        yield


def capture_connected_clients(solver: Any) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = solver.tui.server.print_connected_clients()
        time.sleep(1.0)
        if result is not None:
            print(result)
    return buffer.getvalue()


def element_node_indices(element: Any) -> list[int]:
    if element.node_indices:
        return list(dict.fromkeys(int(index) for index in element.node_indices))
    return list(
        dict.fromkeys(
            int(index)
            for facet in element.facets
            for index in facet.node_indices
        )
    )


def stats(values: Iterable[float]) -> dict[str, Any]:
    sequence = [float(value) for value in values]
    if not sequence:
        return {"count": 0}
    return {
        "count": len(sequence),
        "minimum": min(sequence),
        "median": statistics.median(sequence),
        "maximum": max(sequence),
        "mean": statistics.fmean(sequence),
    }


def normalized(vector):
    magnitude = math.sqrt(sum(float(value) ** 2 for value in vector))
    if magnitude <= 0.0:
        raise RuntimeError("brine outlet normal has zero magnitude")
    return [float(value) / magnitude for value in vector]


def polygon_area_centroid(points, np):
    """Return planar polygon area and a triangle-area-weighted centroid."""

    if len(points) < 3:
        return 0.0, np.mean(points, axis=0)
    origin = points[0]
    total_area = 0.0
    weighted_centroid = np.zeros(3, dtype=float)
    for index in range(1, len(points) - 1):
        first = points[index]
        second = points[index + 1]
        triangle_area = 0.5 * float(np.linalg.norm(np.cross(first - origin, second - origin)))
        if triangle_area <= 0.0:
            continue
        total_area += triangle_area
        weighted_centroid += triangle_area * (origin + first + second) / 3.0
    if total_area <= 0.0:
        return 0.0, np.mean(points, axis=0)
    return total_area, weighted_centroid / total_area


def coordinate_key(values) -> tuple[float, float, float]:
    return tuple(round(float(value), 10) for value in values)


def surface_component(surface: Any, data_type: SurfaceDataType, attribute: str):
    if isinstance(surface, dict):
        return surface.get(data_type)
    return getattr(surface, attribute, None)


def normalize_zone_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def resolve_surface(available: list[str], aliases: tuple[str, ...], role: str) -> str:
    normalized = {normalize_zone_name(name): name for name in available}
    matches = {
        normalized[normalize_zone_name(alias)]
        for alias in aliases
        if normalize_zone_name(alias) in normalized
    }
    if len(matches) != 1:
        raise RuntimeError(
            f"could not resolve {role} surface from aliases={aliases}; "
            f"matches={sorted(matches)} available={sorted(available)}"
        )
    return matches.pop()


def write_new_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def main() -> int:
    args = build_parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    output_path = Path(args.output_json).expanduser().resolve()
    lock_path = Path(args.lock_file).expanduser().resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to overwrite Stage-0 evidence: {output_path}")

    payload: dict[str, Any] = {
        "schema_version": 1,
        "run_label": output_path.stem,
        "classification": "diagnostic / unresolved",
        "status": "running",
        "server_id": str(args.server_id),
        "mesh": args.mesh,
        "expected_mesh_sha256": EXPECTED_MESH_SHA256,
        "started_epoch": time.time(),
        "prohibited_actions": [
            "no data-field load",
            "no initialization or patch",
            "no physical iteration",
            "no Fluent case/data write",
        ],
    }
    try:
        with exclusive_writer_lock(lock_path):
            solver = connect(
                server_id=args.server_id,
                tcp_timeout_seconds=args.tcp_timeout_seconds,
                start_transcript=True,
            )
            payload["health_status"] = str(solver.health_check.status())
            payload["fluent_version"] = str(solver.get_fluent_version())
            clients = capture_connected_clients(solver)
            payload["connected_clients_before_mesh_load"] = clients
            if "No client is connected to server." not in clients:
                raise RuntimeError(
                    "remote connected-client ownership is not exclusive; refusing mesh load"
                )
            payload["live_parallel_runtime"] = require_live_compute_node_count(
                solver, EXPECTED_RANKS
            )
            if not remote_file_exists(solver, args.mesh):
                raise FileNotFoundError(f"remote mesh is missing: {args.mesh}")
            if remote_file_exists(solver, args.remote_hash_scratch):
                raise FileExistsError(
                    "refusing to overwrite remote checksum evidence: "
                    f"{args.remote_hash_scratch}"
                )
            mesh_sha256 = mesh_study.remote_file_sha256(
                solver, args.mesh, args.remote_hash_scratch
            )
            payload["mesh_sha256"] = mesh_sha256
            payload["remote_hash_scratch"] = args.remote_hash_scratch
            if mesh_sha256 != EXPECTED_MESH_SHA256:
                raise RuntimeError(
                    f"mesh checksum mismatch: expected={EXPECTED_MESH_SHA256} actual={mesh_sha256}"
                )

            print("stage0: cold-loading accepted mesh", flush=True)
            solver.settings.file.read_mesh(file_name=args.mesh)
            time.sleep(2.0)
            if str(solver.get_fluent_version()) != "Ansys Fluent 2024 R2":
                raise RuntimeError("Fluent version changed after mesh load")
            payload["live_parallel_runtime_after_mesh_load"] = (
                require_live_compute_node_count(solver, EXPECTED_RANKS)
            )

            field_data = solver.fields.field_data
            available_surfaces = list(field_data.surfaces.allowed_values())
            brine_surface = resolve_surface(
                available_surfaces,
                ("brineoutlet", "brine-outlet", "brine_outlet"),
                "brine outlet",
            )
            wall_surface = resolve_surface(
                available_surfaces,
                ("wall", "wall-fluid", "wall_fluid"),
                "separator/pipe wall",
            )
            zone_info = list(field_data.get_zones_info())
            cell_zones = [
                zone for zone in zone_info if getattr(zone.zone_type, "name", "") == "CELL"
            ]
            if len(cell_zones) != 1:
                raise RuntimeError(
                    "expected exactly one cell zone for full mesh retrieval; "
                    f"actual={[(zone.name, str(zone.zone_type)) for zone in cell_zones]}"
                )
            cell_zone = cell_zones[0].name
            payload["live_zone_resolution"] = {
                "available_surfaces": available_surfaces,
                "brine_surface": brine_surface,
                "wall_surface": wall_surface,
                "cell_zone": cell_zone,
            }
            print("stage0: fetching brine and wall surface geometry", flush=True)
            surface_payload = field_data.get_surface_data(
                data_types=[
                    SurfaceDataType.Vertices,
                    SurfaceDataType.FacesConnectivity,
                    SurfaceDataType.FacesCentroid,
                    SurfaceDataType.FacesNormal,
                ],
                surfaces=[brine_surface, wall_surface],
            )
            brine = surface_payload[brine_surface]
            wall = surface_payload[wall_surface]
            vertices = surface_component(brine, SurfaceDataType.Vertices, "vertices")
            faces = surface_component(
                brine, SurfaceDataType.FacesConnectivity, "connectivity"
            )
            centroids = surface_component(
                brine, SurfaceDataType.FacesCentroid, "face_centroids"
            )
            normals = surface_component(
                brine, SurfaceDataType.FacesNormal, "face_normals"
            )
            if vertices is None or faces is None or centroids is None or normals is None:
                raise RuntimeError("brine surface geometry response is incomplete")

            import numpy as np

            polygon_areas = []
            polygon_centroids = []
            for connectivity in faces:
                points = vertices[np.asarray(connectivity, dtype=int)]
                face_area, face_centroid = polygon_area_centroid(points, np)
                polygon_areas.append(face_area)
                polygon_centroids.append(face_centroid)
            areas = np.asarray(polygon_areas, dtype=float)
            area = float(np.sum(areas))
            center = np.average(np.asarray(polygon_centroids), axis=0, weights=areas)
            axis = np.asarray(normalized(np.sum(normals, axis=0)), dtype=float)
            offsets = vertices - center
            projected = offsets - np.outer(offsets @ axis, axis)
            radial = np.linalg.norm(projected, axis=1)
            equivalent_radius = math.sqrt(area / math.pi)
            perimeter_radius = float(np.max(radial))
            crown_y = float(np.max(vertices[:, 1]))
            invert_y = float(np.min(vertices[:, 1]))
            crown_tolerance = max(1.0e-9, perimeter_radius * 1.0e-7)

            face_heights = []
            crown_face_heights = []
            for connectivity in faces:
                face_y = vertices[np.asarray(connectivity, dtype=int), 1]
                height = float(np.max(face_y) - np.min(face_y))
                if height > 0.0:
                    face_heights.append(height)
                    if float(np.max(face_y)) >= crown_y - crown_tolerance:
                        crown_face_heights.append(height)

            if not crown_face_heights:
                raise RuntimeError("no brine boundary faces touch the resolved crown")

            wall_vertices = surface_component(wall, SurfaceDataType.Vertices, "vertices")
            if wall_vertices is None:
                raise RuntimeError("wall surface vertices are unavailable")
            wall_offsets = wall_vertices - center
            wall_axial = wall_offsets @ axis
            wall_radial_vectors = wall_offsets - np.outer(wall_axial, axis)
            wall_radial = np.linalg.norm(wall_radial_vectors, axis=1)
            radial_tolerance = max(0.02 * perimeter_radius, 2.0e-4)
            cylinder_mask = np.abs(wall_radial - perimeter_radius) <= radial_tolerance
            matching_axial = wall_axial[cylinder_mask]
            positive_extent = (
                float(np.max(matching_axial[matching_axial >= 0.0]))
                if np.any(matching_axial >= 0.0)
                else 0.0
            )
            negative_extent = (
                float(-np.min(matching_axial[matching_axial <= 0.0]))
                if np.any(matching_axial <= 0.0)
                else 0.0
            )
            inward_sign = 1.0 if positive_extent >= negative_extent else -1.0
            inferred_pipe_length = max(positive_extent, negative_extent)

            payload["brine_outlet_geometry"] = {
                "area_m2": area,
                "area_method": "polygon triangulation from surface vertices/connectivity",
                "raw_face_normal_norm_sum_not_area": float(
                    np.sum(np.linalg.norm(normals, axis=1))
                ),
                "expected_area_m2": EXPECTED_BRINE_AREA_M2,
                "area_relative_difference": abs(area - EXPECTED_BRINE_AREA_M2)
                / EXPECTED_BRINE_AREA_M2,
                "face_count": len(faces),
                "vertex_count": len(vertices),
                "area_weighted_centroid_m": [float(value) for value in center],
                "area_weighted_axis_normal": [float(value) for value in axis],
                "equivalent_radius_m": equivalent_radius,
                "perimeter_radius_m": perimeter_radius,
                "resolved_crown_y_m": crown_y,
                "resolved_invert_y_m": invert_y,
                "opening_vertical_extent_m": crown_y - invert_y,
                "boundary_face_vertical_height_m": stats(face_heights),
                "crown_touching_face_vertical_height_m": stats(crown_face_heights),
            }
            payload["outlet_leg_geometry"] = {
                "method": (
                    "wall vertices within the stated radial tolerance of the brine "
                    "outlet cylinder, measured from the outlet plane"
                ),
                "radial_tolerance_m": radial_tolerance,
                "matching_wall_vertex_count": int(np.sum(cylinder_mask)),
                "axis_sign_toward_inferred_domain": inward_sign,
                "positive_axis_extent_m": positive_extent,
                "negative_axis_extent_m": negative_extent,
                "inferred_resolved_pipe_length_m": inferred_pipe_length,
                "classification": "mesh-derived cylindrical-wall inference",
            }

            print("stage0: fetching fluid cell mesh for exact local cell heights", flush=True)
            try:
                mesh = field_data.get_mesh(cell_zone)
            except Exception as exc:
                payload["volume_cell_mesh_api"] = {
                    "status": "unavailable",
                    "error": f"{type(exc).__name__}: {exc}",
                    "path": "solver.fields.field_data.get_mesh(cell_zone)",
                }
                registers = solver.settings.solution.cell_registers
                if args.probe_register_name in registers.get_object_names():
                    raise FileExistsError(
                        "refusing to replace existing probe register: "
                        f"{args.probe_register_name}"
                    ) from exc
                probe_half_width = 2.0 * perimeter_radius
                probe_half_height = max(
                    2.0 * statistics.median(crown_face_heights), 0.02
                )
                probe_min = [
                    float(center[0] - probe_half_width),
                    crown_y - probe_half_height,
                    float(center[2] - probe_half_width),
                ]
                probe_max = [
                    float(center[0] + probe_half_width),
                    crown_y + probe_half_height,
                    float(center[2] + probe_half_width),
                ]
                solver.tui.mesh.adapt.cell_registers.add(
                    args.probe_register_name,
                    "type",
                    "hexahedron",
                    "inside?",
                    "yes",
                    "max-point",
                    *probe_max,
                    "min-point",
                    *probe_min,
                )
                register_before = registers[args.probe_register_name].get_state()
                surfaces_before = set(field_data.surfaces.allowed_values())
                volume_surface_error = ""
                try:
                    registers[
                        args.probe_register_name
                    ].type.hexahedron.create_volume_surface.set_state(True)
                    time.sleep(1.0)
                except Exception as volume_exc:
                    volume_surface_error = (
                        f"{type(volume_exc).__name__}: {volume_exc}"
                    )
                register_after = registers[args.probe_register_name].get_state()
                surfaces_after = set(field_data.surfaces.allowed_values())
                created_surfaces = sorted(surfaces_after - surfaces_before)
                created_surface_geometry: dict[str, Any] = {}
                if created_surfaces:
                    created_payload = field_data.get_surface_data(
                        data_types=[
                            SurfaceDataType.Vertices,
                            SurfaceDataType.FacesConnectivity,
                            SurfaceDataType.FacesCentroid,
                        ],
                        surfaces=created_surfaces,
                    )
                    for created_name in created_surfaces:
                        created = created_payload[created_name]
                        created_vertices = surface_component(
                            created, SurfaceDataType.Vertices, "vertices"
                        )
                        created_faces = surface_component(
                            created, SurfaceDataType.FacesConnectivity, "connectivity"
                        )
                        created_centroids = surface_component(
                            created, SurfaceDataType.FacesCentroid, "face_centroids"
                        )
                        created_surface_geometry[created_name] = {
                            "vertex_count": (
                                len(created_vertices)
                                if created_vertices is not None
                                else 0
                            ),
                            "face_count": (
                                len(created_faces) if created_faces is not None else 0
                            ),
                            "centroid_count": (
                                len(created_centroids)
                                if created_centroids is not None
                                else 0
                            ),
                            "vertex_y_range_m": (
                                [
                                    float(np.min(created_vertices[:, 1])),
                                    float(np.max(created_vertices[:, 1])),
                                ]
                                if created_vertices is not None
                                and len(created_vertices) > 0
                                else []
                            ),
                        }
                volume_reports: dict[str, Any] = {}
                volume_integrals = solver.settings.results.report.volume_integrals
                for report_name, report_call in (
                    (
                        "volume",
                        lambda: volume_integrals.volume(
                            cell_zones=[],
                            volumes=[args.probe_register_name],
                            write_to_file=False,
                        ),
                    ),
                    (
                        "minimum_y_coordinate",
                        lambda: volume_integrals.minimum(
                            cell_zones=[],
                            volumes=[args.probe_register_name],
                            cell_function="y-coordinate",
                            write_to_file=False,
                        ),
                    ),
                    (
                        "maximum_y_coordinate",
                        lambda: volume_integrals.maximum(
                            cell_zones=[],
                            volumes=[args.probe_register_name],
                            cell_function="y-coordinate",
                            write_to_file=False,
                        ),
                    ),
                ):
                    report_buffer = io.StringIO()
                    try:
                        with contextlib.redirect_stdout(
                            report_buffer
                        ), contextlib.redirect_stderr(report_buffer):
                            report_result = report_call()
                            time.sleep(1.0)
                            if report_result is not None:
                                print(report_result)
                        volume_reports[report_name] = {
                            "status": "returned",
                            "raw_report": report_buffer.getvalue(),
                        }
                    except Exception as report_exc:
                        volume_reports[report_name] = {
                            "status": "unavailable",
                            "error": f"{type(report_exc).__name__}: {report_exc}",
                            "raw_report": report_buffer.getvalue(),
                        }
                properties_buffer = io.StringIO()
                try:
                    with contextlib.redirect_stdout(properties_buffer), contextlib.redirect_stderr(
                        properties_buffer
                    ):
                        properties_result = (
                            solver.tui.mesh.adapt.cell_registers.list_properties(
                                args.probe_register_name
                            )
                        )
                        time.sleep(1.0)
                        if properties_result is not None:
                            print(properties_result)
                finally:
                    registers.delete(name_list=[args.probe_register_name])
                payload["cell_register_probe"] = {
                    "name": args.probe_register_name,
                    "minimum_m": probe_min,
                    "maximum_m": probe_max,
                    "properties_report": properties_buffer.getvalue(),
                    "settings_before_volume_surface": register_before,
                    "settings_after_volume_surface": register_after,
                    "volume_surface_set_error": volume_surface_error,
                    "created_surface_names": created_surfaces,
                    "created_surface_geometry": created_surface_geometry,
                    "utl_volume_reports": volume_reports,
                    "deleted_after_probe": (
                        args.probe_register_name not in registers.get_object_names()
                    ),
                }
                payload["status"] = "unresolved"
                payload["classification"] = "diagnostic / unresolved"
                payload["next_gate"] = (
                    "resolve exact local volume-cell spacing from the register/report "
                    "path or another Fluent 2024 R2-supported mesh export; do not "
                    "initialize or run 07n-a from boundary-face spacing alone"
                )
                payload["completed_epoch"] = time.time()
                write_new_json(output_path, payload)
                print(f"stage0_manifest: {output_path}", flush=True)
                print("stage0: exact cell mesh API unavailable; stopped unresolved", flush=True)
                return 2
            print(
                f"stage0: received nodes={len(mesh.nodes)} cells={len(mesh.elements)}",
                flush=True,
            )
            outlet_keys = {coordinate_key(vertex) for vertex in vertices}
            adjacent_cells: list[dict[str, Any]] = []
            for element in mesh.elements:
                indices = element_node_indices(element)
                cell_nodes = [mesh.nodes[index] for index in indices]
                coordinates = [[node.x, node.y, node.z] for node in cell_nodes]
                y_values = [coordinate[1] for coordinate in coordinates]
                y_min = float(min(y_values))
                y_max = float(max(y_values))
                if any(coordinate_key(coordinate) in outlet_keys for coordinate in coordinates):
                    adjacent_cells.append(
                        {
                            "cell_id": int(element._id),
                            "y_min_m": y_min,
                            "y_max_m": y_max,
                            "vertical_height_m": y_max - y_min,
                            "node_count": len(indices),
                        }
                    )

            crown_cells = [
                cell
                for cell in adjacent_cells
                if cell["y_min_m"] <= crown_y + crown_tolerance
                and cell["y_max_m"] >= crown_y - crown_tolerance
                and cell["vertical_height_m"] > 0.0
            ]
            if not crown_cells:
                closest = max(adjacent_cells, key=lambda cell: cell["y_max_m"], default=None)
                raise RuntimeError(
                    "no boundary-adjacent volume cell spans the crown; "
                    f"closest={closest}"
                )
            crown_height_stats = stats(cell["vertical_height_m"] for cell in crown_cells)
            local_height = float(crown_height_stats["median"])
            candidates = {
                "crown_plus_2_local_cells": crown_y + 2.0 * local_height,
                "crown_plus_4_local_cells": crown_y + 4.0 * local_height,
            }

            crown_points = vertices[
                np.abs(vertices[:, 1] - crown_y) <= crown_tolerance
            ]
            crown_point = np.mean(crown_points, axis=0)
            search_radius = 2.0 * perimeter_radius
            candidate_resolution: dict[str, Any] = {}
            for name, target_y in candidates.items():
                heights = []
                for element in mesh.elements:
                    indices = element_node_indices(element)
                    cell_nodes = [mesh.nodes[index] for index in indices]
                    y_values = [float(node.y) for node in cell_nodes]
                    y_min = min(y_values)
                    y_max = max(y_values)
                    if not (y_min <= target_y <= y_max) or y_max <= y_min:
                        continue
                    center_xyz = [
                        statistics.fmean(
                            float(getattr(node, coordinate)) for node in cell_nodes
                        )
                        for coordinate in ("x", "y", "z")
                    ]
                    distance = float(np.linalg.norm(np.asarray(center_xyz) - crown_point))
                    if distance <= search_radius:
                        heights.append(y_max - y_min)
                candidate_resolution[name] = {
                    "target_level_y_m": target_y,
                    "submergence_above_crown_m": target_y - crown_y,
                    "local_cell_vertical_height_m": stats(heights),
                    "gravity_time_scale_s": math.sqrt((target_y - crown_y) / GRAVITY_MS2),
                    "selection": (
                        "cells whose vertical extent crosses the target and whose "
                        "vertex-mean centre is within two outlet radii of the crown"
                    ),
                }
                if len(heights) < 5:
                    raise RuntimeError(
                        f"too few local cells resolve candidate {name}: count={len(heights)}"
                    )

            payload["boundary_adjacent_cell_count"] = len(adjacent_cells)
            payload["crown_adjacent_cells"] = crown_cells
            payload["crown_adjacent_vertical_height_m"] = crown_height_stats
            payload["candidate_levels"] = candidate_resolution
            payload["mesh_counts_from_field_data"] = {
                "nodes": len(mesh.nodes),
                "cells": len(mesh.elements),
            }
            payload["next_gate"] = (
                "fresh initialization and exact patched liquid-volume/inventory "
                "integrals for both candidate levels; no physical iteration yet"
            )
            payload["status"] = "accepted"
            payload["classification"] = "accepted diagnostic"
            payload["completed_epoch"] = time.time()
            write_new_json(output_path, payload)
            print(f"stage0_manifest: {output_path}", flush=True)
            print(f"resolved_crown_y_m: {crown_y:.12g}", flush=True)
            print(f"crown_local_cell_height_m: {local_height:.12g}", flush=True)
            return 0
    except Exception as exc:
        payload.update(
            {
                "status": "unresolved",
                "classification": "diagnostic / unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        if not output_path.exists():
            write_new_json(output_path, payload)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

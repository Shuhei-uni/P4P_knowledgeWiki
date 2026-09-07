#!/usr/bin/env python3
"""Preserve the live Fluent state, then preflight the resolved brine-outlet mesh.

This inspection intentionally does not import settings, initialize, or iterate.
It is the mutation boundary between the prior closed-bottom/sink diagnostics and
the resolved-outlet carrier qualification.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Mapping
from pathlib import Path, PureWindowsPath
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

from pyansys_fluent.common import remote_chdir, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.mesh_convergence import (  # noqa: E402
    named_zones,
    normalize_zone_name,
    parse_mesh_check,
    parse_mesh_quality,
    parse_mesh_size,
)

import run_purnanto_enthalpy_sweep as sweep  # noqa: E402
import run_split_inlet_mesh_convergence as mesh_study  # noqa: E402


STUDY_ID = "split_inlet_resolved_brine_outlet_20260813"
REMOTE_ROOT = rf"C:\Users\qtra338\Documents\Mesh study\{STUDY_ID}"
REMOTE_MESH = (
    r"C:\Users\qtra338\Documents\Mesh study\Meshes"
    r"\brine-outlet-620kcells.msh.h5"
)
LOCAL_ROOT = PROJECT_ROOT / "output" / STUDY_ID / "preflight"

REQUIRED_ALIASES: dict[str, tuple[str, ...]] = {
    "liquidinlet": ("liquid-inlet", "liquid_inlet", "inlet-liquid", "inlet_liquid"),
    "steaminlet": ("steam-inlet", "steam_inlet", "inlet-steam", "inlet_steam"),
    "steamoutlet": ("steam-outlet", "steam_outlet", "outlet-steam"),
    "brineoutlet": (
        "brine-outlet",
        "brine_outlet",
        "brine outlet",
        "liquidoutlet",
        "liquid-outlet",
        "liquid_outlet",
    ),
}

PHYSICAL_FACE_CATEGORIES = {
    "axis",
    "fan",
    "interior",
    "interface",
    "mass_flow_inlet",
    "outflow",
    "porous_jump",
    "pressure_inlet",
    "pressure_outlet",
    "symmetry",
    "velocity_inlet",
    "wall",
}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--server-id", default="1")
    result.add_argument("--mesh", default=REMOTE_MESH)
    result.add_argument("--skip-live-backup", action="store_true")
    return result


def remote_join(directory: str, name: str) -> str:
    return str(PureWindowsPath(directory) / name)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")


def resolve_roles(available: Mapping[str, str]) -> tuple[dict[str, Any], list[str]]:
    normalized: dict[str, list[str]] = {}
    for name in available:
        normalized.setdefault(normalize_zone_name(name), []).append(str(name))
    roles: dict[str, Any] = {}
    errors: list[str] = []
    for role, aliases in REQUIRED_ALIASES.items():
        candidates: list[str] = []
        for alias in (role, *aliases):
            candidates.extend(normalized.get(normalize_zone_name(alias), []))
        matches = sorted(set(candidates))
        if len(matches) != 1:
            errors.append(
                f"required role {role!r} resolved to {matches}; "
                f"available zones={sorted(available)}"
            )
            continue
        name = matches[0]
        roles[role] = {"name": name, "category": available[name]}
    return roles, errors


def current_iteration_label(solver: Any) -> Any:
    try:
        return sweep.read_iteration_count(solver)
    except Exception as exc:
        return f"unavailable: {type(exc).__name__}: {exc}"


def collect_mesh_reports_robust(
    solver: Any, transcript: str
) -> tuple[dict[str, Any], str]:
    """Collect reports with one combined-buffer parse for asynchronous stdout."""
    size_text = mesh_study.capture_fluent(
        "mesh_size_info",
        lambda: mesh_study.call_and_drain(
            lambda: solver.settings.mesh.size_info(), delay_seconds=2.5
        ),
    )
    check_text = mesh_study.capture_fluent(
        "mesh_check",
        lambda: mesh_study.call_and_drain(
            lambda: solver.settings.mesh.check(), delay_seconds=2.5
        ),
    )
    quality_text = mesh_study.capture_fluent(
        "mesh_quality",
        lambda: mesh_study.call_and_drain(
            lambda: solver.settings.mesh.quality(), delay_seconds=2.5
        ),
    )
    combined = size_text + check_text + quality_text
    try:
        metrics = parse_mesh_size(combined)
        metrics.update(parse_mesh_check(combined))
        metrics.update(parse_mesh_quality(combined))
    except ValueError:
        transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
        if not transcript_text.strip():
            raise RuntimeError(
                "mesh reports produced neither captured stdout nor a readable transcript"
            )
        combined = transcript_text
        metrics = parse_mesh_size(combined)
        metrics.update(parse_mesh_check(combined))
        metrics.update(parse_mesh_quality(combined))
    metrics["characteristic_size_m"] = (
        metrics["domain_volume_m3"] / metrics["cells"]
    ) ** (1.0 / 3.0)
    return metrics, combined


def main() -> int:
    args = parser().parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    LOCAL_ROOT.mkdir(parents=True, exist_ok=True)
    solver = connect(server_id=args.server_id)
    if not sweep.ensure_remote_directory_best_effort(solver, REMOTE_ROOT):
        raise RuntimeError(f"could not create remote study directory {REMOTE_ROOT}")

    started = time.time()
    manifest: dict[str, Any] = {
        "study_id": STUDY_ID,
        "classification": "diagnostic preflight",
        "status": "running",
        "mesh_file": args.mesh,
        "started_epoch": started,
        "fluent_version": str(solver.get_fluent_version()),
        "fluent_health": str(solver.health_check.status()),
        "dpm": "not run; no injections updated or tracked",
        "ewf": "off/not introduced",
        "sink_udf": "not loaded or applied to the new mesh",
    }
    transcript = remote_join(REMOTE_ROOT, "brine_outlet_mesh_preflight.trn")

    try:
        if not args.skip_live_backup:
            backup_case = remote_join(
                REMOTE_ROOT, "pre_brine_mesh_live_state_unverified.cas.h5"
            )
            backup_data = remote_join(
                REMOTE_ROOT, "pre_brine_mesh_live_state_unverified.dat.h5"
            )
            manifest["preserved_live_state"] = {
                "case": backup_case,
                "data": backup_data,
                "reported_iteration_setting_not_completion_proof": current_iteration_label(
                    solver
                ),
            }
            sweep.write_case_data_pair(
                solver,
                backup_case,
                backup_data,
                "pre_brine_mesh_live_state_unverified",
            )

        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        solver.settings.file.start_transcript(file_name=transcript)
        mesh_study.require_remote_input(solver, args.mesh, "resolved brine-outlet mesh")
        remote_chdir(solver, str(PureWindowsPath(args.mesh).parent))
        manifest["mesh_sha256"] = mesh_study.remote_file_sha256(
            solver,
            args.mesh,
            remote_join(REMOTE_ROOT, "_mesh_sha256.txt"),
        )
        manifest["mesh_load_transcript"] = mesh_study.read_mesh(solver, args.mesh)
        mesh_metrics, quality_text = collect_mesh_reports_robust(solver, transcript)
        manifest["mesh_metrics"] = mesh_metrics
        (LOCAL_ROOT / "mesh_quality.txt").write_text(quality_text, encoding="utf-8")

        boundary_state = safe_get_state(
            solver.settings.setup.boundary_conditions,
            "setup.boundary_conditions_after_mesh_load",
        )
        cell_state = safe_get_state(
            solver.settings.setup.cell_zone_conditions,
            "setup.cell_zone_conditions_after_mesh_load",
        )
        all_face_objects = (
            named_zones(boundary_state) if isinstance(boundary_state, Mapping) else {}
        )
        face_zones = {
            name: category
            for name, category in all_face_objects.items()
            if category in PHYSICAL_FACE_CATEGORIES
        }
        cell_zones = named_zones(cell_state) if isinstance(cell_state, Mapping) else {}
        roles, errors = resolve_roles(face_zones)
        if len(cell_zones) != 1:
            errors.append(f"expected one fluid cell zone; actual={cell_zones}")
        elif "fluid" not in {normalize_zone_name(name) for name in cell_zones}:
            errors.append(f"fluid cell-zone identity unresolved: {cell_zones}")
        if int(mesh_metrics.get("partitions", -1)) != 16:
            errors.append(
                f"expected 16 partitions; actual={mesh_metrics.get('partitions')}"
            )
        if mesh_metrics.get("negative_volume_reported"):
            errors.append("mesh check reported negative cell volume")
        if mesh_metrics.get("raw_check_contains_error"):
            errors.append("mesh check transcript contains an error")

        external_zones = [
            name
            for name, category in face_zones.items()
            if category not in {"interior", "interface"}
        ]
        areas: dict[str, float] = {}
        if external_zones:
            areas = mesh_study.surface_areas(solver, REMOTE_ROOT, external_zones)
        manifest.update(
            {
                "available_face_zones": face_zones,
                "available_cell_zones": cell_zones,
                "resolved_roles": roles,
                "surface_areas_m2": areas,
                "validation_errors": errors,
            }
        )

        brine = roles.get("brineoutlet", {}).get("name")
        if brine:
            centroid: dict[str, float] = {}
            try:
                for field, key in (
                    ("x-coordinate", "x_m"),
                    ("y-coordinate", "y_m"),
                    ("z-coordinate", "z_m"),
                ):
                    centroid[key] = mesh_study.surface_scalar(
                        solver,
                        REMOTE_ROOT,
                        f"brine_outlet_centroid_{key}",
                        [brine],
                        field,
                    )[brine]
                manifest["brine_outlet_centroid_m"] = centroid
            except Exception as exc:
                manifest["brine_outlet_centroid_m"] = None
                manifest["brine_outlet_centroid_note"] = (
                    "coordinate surface averaging is inactive in Fluent before a "
                    f"solution is initialized: {type(exc).__name__}: {exc}"
                )

        manifest["status"] = "accepted" if not errors else "unresolved"
        manifest["completed_epoch"] = time.time()
        write_json(LOCAL_ROOT / "preflight_manifest.json", manifest)
        sweep.remote_text_write_best_effort(
            solver,
            remote_join(REMOTE_ROOT, "preflight_manifest.json"),
            json.dumps(manifest, indent=2, default=str),
        )
        return 0 if not errors else 2
    except Exception as exc:
        manifest.update(
            {
                "status": "unresolved",
                "error": f"{type(exc).__name__}: {exc}",
                "completed_epoch": time.time(),
            }
        )
        write_json(LOCAL_ROOT / "preflight_manifest.json", manifest)
        raise
    finally:
        try:
            solver.settings.file.stop_transcript()
        except Exception:
            pass
        transcript_text = sweep.remote_text_read_best_effort(solver, transcript)
        if transcript_text:
            (LOCAL_ROOT / "brine_outlet_mesh_preflight.trn").write_text(
                transcript_text, encoding="utf-8"
            )


if __name__ == "__main__":
    raise SystemExit(main())

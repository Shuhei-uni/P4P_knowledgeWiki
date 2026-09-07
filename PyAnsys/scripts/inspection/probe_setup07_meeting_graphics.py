#!/usr/bin/env python3
"""Probe live Fluent 2024 R2 graphics paths for setup-07 meeting exports.

This targeted inspection does not load a case, run iterations, change physics,
or update DPM.  It may create temporary post-processing objects with a unique
``meeting_probe_`` prefix so their dynamic children and allowed values can be
read, then attempts to delete only those temporary objects.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.dependency_workflow import probe_object, safe_allowed_values  # noqa: E402


OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "setup07_meeting_visuals_20260811"
    / "live_graphics_probe.json"
)


def object_names(branch: Any) -> list[str]:
    try:
        return [str(name) for name in branch.get_object_names()]
    except Exception:
        return []


def dpm_interaction_readback(solver: Any) -> dict[str, Any]:
    candidates = (
        ("discrete_phase.interaction", lambda: solver.settings.setup.models.discrete_phase.interaction),
        (
            "discrete_phase.general_settings.interaction",
            lambda: solver.settings.setup.models.discrete_phase.general_settings.interaction,
        ),
    )
    errors: dict[str, str] = {}
    for label, getter in candidates:
        try:
            return {"path": label, "state": safe_get_state(getter(), label)}
        except Exception as exc:
            errors[label] = f"{type(exc).__name__}: {exc}"
    return {"state": "unavailable in graphics probe", "errors": errors}


def create_probe(branch: Any, name: str) -> tuple[Any | None, dict[str, Any]]:
    evidence: dict[str, Any] = {"name": name, "before": object_names(branch)}
    try:
        if name not in evidence["before"]:
            branch.create(name=name)
            evidence["create_method"] = "create(name=...)"
        evidence["after_create"] = object_names(branch)
        return branch[name], evidence
    except Exception as first:
        evidence["create_error"] = f"{type(first).__name__}: {first}"
    try:
        branch[name] = {}
        evidence["create_method"] = "mapping assignment"
        evidence["after_create"] = object_names(branch)
        return branch[name], evidence
    except Exception as second:
        evidence["assignment_error"] = f"{type(second).__name__}: {second}"
        return None, evidence


def delete_probe(branch: Any, name: str) -> dict[str, Any]:
    evidence: dict[str, Any] = {"name": name}
    try:
        branch.delete(name=name)
        evidence["delete_method"] = "delete(name=...)"
    except Exception as first:
        evidence["delete_error"] = f"{type(first).__name__}: {first}"
        try:
            del branch[name]
            evidence["delete_method"] = "mapping deletion"
        except Exception as second:
            evidence["mapping_delete_error"] = f"{type(second).__name__}: {second}"
    evidence["after_delete"] = object_names(branch)
    evidence["deleted"] = name not in evidence["after_delete"]
    return evidence


def probe_named_collection(branch: Any, name: str, children: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "collection": probe_object(branch).__dict__,
        "object_names_before": object_names(branch),
    }
    obj, creation = create_probe(branch, name)
    result["creation"] = creation
    if obj is not None:
        result["object"] = probe_object(obj).__dict__
        result["state"] = safe_get_state(obj, name)
        result["children"] = {}
        for child_name in children:
            try:
                child = getattr(obj, child_name)
                result["children"][child_name] = {
                    "probe": probe_object(child).__dict__,
                    "allowed_values": safe_allowed_values(child),
                    "state": safe_get_state(child, f"{name}.{child_name}"),
                }
            except Exception as exc:
                result["children"][child_name] = {
                    "error": f"{type(exc).__name__}: {exc}"
                }
        result["deletion"] = delete_probe(branch, name)
    return result


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    solver = connect(server_id="1")
    graphics = solver.settings.results.graphics
    surfaces = solver.settings.results.surfaces

    result: dict[str, Any] = {
        "fluent_version": str(solver.get_fluent_version()),
        "health": str(solver.health_check.status()),
        "dpm_interaction": dpm_interaction_readback(solver),
        "graphics": probe_object(graphics).__dict__,
        "surfaces": probe_object(surfaces).__dict__,
        "picture": {
            "probe": probe_object(graphics.picture).__dict__,
            "state": safe_get_state(graphics.picture, "picture"),
        },
        "views": {
            "probe": probe_object(graphics.views).__dict__,
            "state": safe_get_state(graphics.views, "views"),
        },
    }
    result["plane_surface"] = probe_named_collection(
        surfaces.plane_surface,
        "meeting_probe_plane",
        ["method", "x", "y", "z", "point", "normal"],
    )
    result["contour"] = probe_named_collection(
        graphics.contour,
        "meeting_probe_contour",
        [
            "field",
            "surfaces_list",
            "range_option",
            "range",
            "filled",
            "node_values",
            "draw_mesh",
        ],
    )
    result["pathline"] = probe_named_collection(
        graphics.pathline,
        "meeting_probe_pathline",
        [
            "velocity_domain",
            "field",
            "release_from_surfaces",
            "skip",
            "coarsen",
            "maximum_steps",
            "step_size",
            "draw_mesh",
        ],
    )
    OUTPUT.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(OUTPUT)
    print("Inspection only: no case load, solver iteration, physics change or DPM update was issued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Probe Fluent 2024 R2 source-list activation, then restore a protected case."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_ROOT = (
    r"C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807"
)
DEFAULT_CASE = REMOTE_ROOT + r"\mesh-900k_07b_sink_hook_v1_retry2_prehook.cas.h5"
DEFAULT_DATA = REMOTE_ROOT + r"\mesh-900k_07b_sink_hook_v1_retry2_prehook.dat.h5"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_constant_water_level_sink_20260807"
    / "source_term_activation_probe.json"
)
DEFAULT_FUNCTION = "cwl_liquid_mass_sink::lib07b_cwl_bdfa31b0ec_r2"


def public_names(obj: Any) -> list[str]:
    return sorted(name for name in dir(obj) if not name.startswith("_"))


def inspect_term(term_list: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "is_active": term_list.is_active(),
        "state": safe_get_state(term_list, "term_list"),
        "public_names": public_names(term_list),
    }
    for index in (0, 1):
        try:
            item = term_list[index]
            payload[f"item_{index}"] = {
                "is_active": item.is_active(),
                "active_children": item.get_active_child_names(),
                "state": safe_get_state(item, f"item_{index}"),
                "option_active": item.option.is_active(),
                "option_allowed": (
                    list(item.option.allowed_values()) if item.option.is_active() else []
                ),
            }
        except Exception as exc:
            payload[f"item_{index}"] = {"error": f"{type(exc).__name__}: {exc}"}
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--case", default=DEFAULT_CASE)
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--function", default=DEFAULT_FUNCTION)
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env")
    solver = connect(server_id=args.server_id)
    payload: dict[str, Any] = {"case": args.case, "data": args.data, "restored": False}
    try:
        solver.settings.file.read_case(file_name=args.case)
        solver.settings.file.read_data(file_name=args.data)
        sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
            "phase-2"
        ].sources
        payload["before_enable"] = safe_get_state(sources, "sources_before")
        sources.enable.set_state(True)
        sources = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
            "phase-2"
        ].sources
        payload["after_enable"] = {
            "state": safe_get_state(sources, "sources_after"),
            "terms": list(sources.terms.get_object_names()),
        }
        for name in sources.terms.get_object_names():
            payload[f"term_{name}_before_resize"] = inspect_term(sources.terms[name])
            sources.terms[name].resize(size=1)
            refreshed = solver.settings.setup.cell_zone_conditions.fluid["fluid"].phase[
                "phase-2"
            ].sources.terms[name]
            payload[f"term_{name}_after_resize"] = inspect_term(refreshed)
            try:
                refreshed.set_state([{"option": "udf", "udf": args.function}])
                refreshed = solver.settings.setup.cell_zone_conditions.fluid[
                    "fluid"
                ].phase["phase-2"].sources.terms[name]
                payload[f"term_{name}_after_atomic_udf_set"] = inspect_term(refreshed)
            except Exception as exc:
                payload[f"term_{name}_after_atomic_udf_set"] = {
                    "error": f"{type(exc).__name__}: {exc}"
                }
    finally:
        solver.settings.file.read_case(file_name=args.case)
        solver.settings.file.read_data(file_name=args.data)
        payload["restored"] = True
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, default=str))
        print(f"Probe written to {output}; protected case/data restored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

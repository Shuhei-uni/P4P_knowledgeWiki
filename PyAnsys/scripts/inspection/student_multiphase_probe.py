#!/usr/bin/env python3
"""Probe live multiphase settings paths against a local Student Fluent session."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


MESH = Path(r"C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\purnanto-extended.msh")


def main() -> int:
    solver = connect(server_id="2")
    try:
        solver.settings.file.read_mesh(file_name=str(MESH))
        m = solver.settings.setup.models.multiphase
        print("before_state:", m.get_state())

        setattr(m, "model", "mixture")
        print("after_model_state:", m.get_state())
        print("active_children:", m.get_active_child_names())
        print("has_number_of_phases:", hasattr(m, "number_of_phases"))
        print("number_of_phases_attr:", getattr(m, "number_of_phases", None))

        try:
            setattr(m, "number_of_phases", 2)
            print("setattr_number_of_phases: OK")
        except Exception as exc:
            print(f"setattr_number_of_phases: FAILED -> {exc}")

        try:
            m.set_state({"number_of_phases": 2})
            print("set_state_number_of_phases: OK")
        except Exception as exc:
            print(f"set_state_number_of_phases: FAILED -> {exc}")

        try:
            solver.scheme.exec(
                ('(ti-menu-load-string "/define/models/multiphase/mixture yes 2")',)
            )
            print("tui_number_of_phases: OK")
        except Exception as exc:
            print(f"tui_number_of_phases: FAILED -> {exc}")

        print("final_state:", m.get_state())
        return 0
    finally:
        solver.exit()


if __name__ == "__main__":
    raise SystemExit(main())

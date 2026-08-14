#!/usr/bin/env python3
"""Build fine-mesh 02d patch cases and a dormant Fluent-native run journal.

This script deliberately does *not* read or execute the generated journal.
It builds independent initialized-and-patched case/data inputs, then creates
one Fluent-native queue that later runs each input to 500 and 1000 iterations
with paired explicit checkpoints at both milestones.
"""

from __future__ import annotations

from pathlib import Path, PureWindowsPath
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_DIR = PureWindowsPath(r"C:\Users\syok443\P4P simulation")
STAMP = "20260814T000000Z"
IC0_CASE = REMOTE_DIR / "VOF-IC0-P1120-preinit-20260814T000000Z.cas.h5"
JOURNAL_ID = f"02d-fine-vof-ic0-ic1-ic2-queue-{STAMP}"
REMOTE_JOURNAL = REMOTE_DIR / f"{JOURNAL_ID}.jou"
TRANSCRIPT = REMOTE_DIR / f"{JOURNAL_ID}.trn"
LOCAL_JOURNAL = PROJECT_ROOT / "queues" / f"{JOURNAL_ID}.jou"

MESH_MIN = (-2.068679, -1.484584, -1.461048)
MESH_MAX_XZ = (1.066749, 1.066830)
POOL_HEIGHTS = (0.00, 0.15, 0.30, 0.45, 0.60)


def posix(path: PureWindowsPath) -> str:
    return path.as_posix()


def y_code(height: float) -> str:
    return f"Y{int(round(height * 100)):03d}"


def register_name(height: float) -> str:
    return f"vof_ic2_pool_below_y_{height:0.2f}m".replace(".", "p")


def ic2_case(height: float) -> PureWindowsPath:
    return REMOTE_DIR / f"VOF-IC2-{y_code(height)}-P1120-fine-patch-platform-{STAMP}.cas.h5"


def ic2_data(height: float) -> PureWindowsPath:
    return REMOTE_DIR / f"VOF-IC2-{y_code(height)}-P1120-fine-patch-platform-{STAMP}.dat.h5"


IC1_CASE = REMOTE_DIR / f"VOF-IC1-P1120-fine-patch-platform-{STAMP}.cas.h5"
IC1_DATA = REMOTE_DIR / f"VOF-IC1-P1120-fine-patch-platform-{STAMP}.dat.h5"


def ensure_absent(solver: Any, *paths: PureWindowsPath) -> None:
    for path in paths:
        if remote_file_exists(solver, str(path)):
            raise FileExistsError(f"Refusing to overwrite existing artifact: {path}")


def set_boundary_register(solver: Any, name: str) -> dict[str, Any]:
    registers = solver.settings.solution.cell_registers
    if name in registers.get_object_names():
        registers.delete(name_list=name)
    registers.create(name=name)
    registers[name].set_state(
        {
            "name": name,
            "type": {
                "option": "boundary",
                "boundary": {
                    "distance_option": {"option": "cell-distance", "cell_distance": 5},
                    "boundary_list": ["brine-outlet"],
                },
            },
        }
    )
    state = safe_get_state(registers[name], name)
    boundary = state.get("type", {}).get("boundary", {}) if isinstance(state, dict) else {}
    if (
        state.get("type", {}).get("option") != "boundary"
        or boundary.get("boundary_list") != ["brine-outlet"]
        or boundary.get("distance_option", {}).get("cell_distance") != 5
    ):
        raise RuntimeError(f"IC1 register readback mismatch: {state}")
    return state


def set_pool_register(solver: Any, height: float) -> dict[str, Any]:
    name = register_name(height)
    registers = solver.settings.solution.cell_registers
    if name in registers.get_object_names():
        registers.delete(name_list=name)
    registers.create(name=name)
    registers[name].set_state(
        {
            "name": name,
            "type": {
                "option": "hexahedron",
                "hexahedron": {
                    "min_point": list(MESH_MIN),
                    "max_point": [MESH_MAX_XZ[0], height, MESH_MAX_XZ[1]],
                    "inside": True,
                },
            },
        }
    )
    state = safe_get_state(registers[name], name)
    hexahedron = state.get("type", {}).get("hexahedron", {}) if isinstance(state, dict) else {}
    if state.get("type", {}).get("option") != "hexahedron" or hexahedron.get("max_point", [None, None])[1] != height:
        raise RuntimeError(f"IC2 register readback mismatch for y={height}: {state}")
    return state


def patch_phase_two_liquid(solver: Any, register: str) -> None:
    solver.settings.solution.initialization.patch.calculate_patch(
        domain="phase-2", registers=[register], variable="mp", value=1.0
    )


def write_pair(solver: Any, case: PureWindowsPath, data: PureWindowsPath) -> None:
    solver.settings.file.write_case(file_name=str(case))
    solver.settings.file.write_data(file_name=str(data))
    for path in (case, data):
        if not remote_file_exists(solver, str(path)):
            raise RuntimeError(f"Fluent did not expose written artifact: {path}")


def queue_job_lines(case_id: str, case: PureWindowsPath, data: PureWindowsPath | None) -> list[str]:
    root = REMOTE_DIR / f"{case_id}-fine-iter"
    lines = [f"; BEGIN {case_id}", f'/file/read-case "{posix(case)}"']
    if data is None:
        lines.append("/solve/initialize/hyb-initialization")
    else:
        lines.append(f'/file/read-data "{posix(data)}"')
    lines.extend(
        [
            "/solve/iterate 500",
            f'/file/write-case-data "{posix(PureWindowsPath(str(root) + "500.cas.h5"))}"',
            "/solve/iterate 500",
            f'/file/write-case-data "{posix(PureWindowsPath(str(root) + "1000.cas.h5"))}"',
            f"; END {case_id}",
        ]
    )
    return lines


def render_queue() -> str:
    lines = [
        f"; Dormant Fluent-native 02d fine-mesh queue: {JOURNAL_ID}",
        "; Do not execute until timestep, monitoring, and transient-readiness gates are approved.",
        "; IC0 is initialized in the journal. IC1/IC2 load their independently patched case/data fields.",
        "/file/confirm-overwrite? no",
        f'/file/start-transcript "{posix(TRANSCRIPT)}"',
    ]
    lines.extend(queue_job_lines("VOF-IC0-P1120", IC0_CASE, None))
    lines.extend(queue_job_lines("VOF-IC1-P1120", IC1_CASE, IC1_DATA))
    for height in POOL_HEIGHTS:
        lines.extend(queue_job_lines(f"VOF-IC2-{y_code(height)}-P1120", ic2_case(height), ic2_data(height)))
    lines.extend(["/file/stop-transcript", "; Queue complete; Fluent remains open."])
    return "\n".join(lines) + "\n"


def write_remote_journal(solver: Any, journal: str) -> None:
    expressions = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)' for line in journal.splitlines()
    )
    solver.scheme.exec(
        (f'(with-output-to-file "{quote_scheme_string(posix(REMOTE_JOURNAL))}" (lambda () {expressions}))',)
    )
    if not remote_file_exists(solver, str(REMOTE_JOURNAL)):
        raise RuntimeError(f"Fluent did not expose remote journal: {REMOTE_JOURNAL}")


def main() -> int:
    LOCAL_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    journal = render_queue()
    LOCAL_JOURNAL.write_text(journal, encoding="utf-8", newline="\n")

    solver = connect(server_id="2")
    if not remote_file_exists(solver, str(IC0_CASE)):
        raise FileNotFoundError(f"Fine IC0 source case not visible: {IC0_CASE}")
    ensure_absent(solver, IC1_CASE, IC1_DATA, *(path for height in POOL_HEIGHTS for path in (ic2_case(height), ic2_data(height))))

    # IC1 begins from the clean, no-patch IC0 case.
    solver.settings.file.read_case(file_name=str(IC0_CASE))
    solver.settings.solution.initialization.hybrid_initialize()
    ic1_register = set_boundary_register(solver, "vof_ic1_brine_outlet_5cells")
    patch_phase_two_liquid(solver, "vof_ic1_brine_outlet_5cells")
    write_pair(solver, IC1_CASE, IC1_DATA)

    # Every IC2 sibling begins from the saved IC1 field, never another pool height.
    pool_registers: dict[str, dict[str, Any]] = {}
    for height in POOL_HEIGHTS:
        solver.settings.file.read_case(file_name=str(IC1_CASE))
        solver.settings.file.read_data(file_name=str(IC1_DATA))
        state = set_pool_register(solver, height)
        patch_phase_two_liquid(solver, register_name(height))
        write_pair(solver, ic2_case(height), ic2_data(height))
        pool_registers[y_code(height)] = state

    write_remote_journal(solver, journal)
    print(f"ic1_register: {ic1_register}")
    print(f"pool_registers: {pool_registers}")
    print(f"local_journal: {LOCAL_JOURNAL}")
    print(f"remote_journal: {REMOTE_JOURNAL}")
    print("journal_started: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

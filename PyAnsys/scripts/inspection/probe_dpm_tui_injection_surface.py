#!/usr/bin/env python3
"""Probe Fluent 2024 R2 TUI commands for assigning a DPM surface injection surface.

Purpose:
- Connect to an already-open Fluent gRPC server.
- Create or reuse one disposable DPM injection.
- Try likely TUI/menu commands.
- Read back the PyFluent state after every attempt.
- Print enough information so we can identify the real command.

Run from project root:

    .venv/bin/python scripts/inspection/probe_dpm_tui_injection_surface.py \
      --server-id 4 \
      --injection-name __probe_surface_injection__ \
      --surface-name steaminlet \
      --surface-id 6 \
      --material water-liquid \
      --diameter 0.000112 \
      --mass-flow-rate 0.001

Notes:
- This is a probe/debug script, not production setup code.
- It should be run after the carrier setup has already enabled DPM.
- It creates one test injection only.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-id", default="4")
    parser.add_argument("--injection-name", default="__probe_surface_injection__")
    parser.add_argument("--surface-name", default="steaminlet")
    parser.add_argument(
        "--surface-id",
        default="6",
        help="Zone id for the injection surface. From your mesh log, steaminlet appears to be zone 6.",
    )
    parser.add_argument("--material", default="water-liquid")
    parser.add_argument("--diameter", type=float, default=112e-6)
    parser.add_argument("--mass-flow-rate", type=float, default=1e-3)
    parser.add_argument("--delete-existing", action="store_true")
    return parser


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80, flush=True)


def as_json(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return repr(obj)


def safe_state(label: str, obj: Any) -> Any:
    try:
        state = obj.get_state()
        print(f"{label}: OK")
        print(as_json(state))
        return state
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}")
        return None


def try_py(label: str, func) -> bool:
    print_header(label)
    try:
        result = func()
        print(f"{label}: OK -> {result!r}", flush=True)
        return True
    except Exception as exc:
        print(f"{label}: FAILED -> {exc}", flush=True)
        traceback.print_exc()
        return False


def tui(solver, label: str, command: str) -> bool:
    """
    Run one Fluent TUI command string through Scheme.

    Most failed commands are still useful because Fluent prints the actual
    prompt/menu error to the terminal.
    """
    print_header(f"TUI TRY: {label}")
    print(command)
    try:
        result = solver.scheme.exec((f'(ti-menu-load-string "{escape_scheme_string(command)}")',))
        print(f"TUI RESULT: {result!r}", flush=True)
        return True
    except Exception as exc:
        print(f"TUI FAILED: {exc}", flush=True)
        traceback.print_exc()
        return False


def escape_scheme_string(value: str) -> str:
    return (
        value
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
    )


def get_injection_branch(solver):
    return solver.settings.setup.models.discrete_phase.injections


def get_injection(branch, name: str):
    return branch[name]


def list_injections(branch) -> list[str]:
    try:
        names = list(branch.get_object_names())
        print(f"injection names: {names}", flush=True)
        return names
    except Exception as exc:
        print(f"Could not list injections: {exc}", flush=True)
        return []


def delete_injection_if_present(branch, name: str) -> None:
    names = set(list_injections(branch))
    if name not in names:
        return

    print_header(f"Delete existing probe injection: {name}")
    for label, deleter in [
        ("branch.__delitem__", lambda: branch.__delitem__(name)),
        ("branch.delete name_list", lambda: branch.delete(name_list=[name])),
    ]:
        try:
            deleter()
            print(f"{label}: OK")
            return
        except Exception as exc:
            print(f"{label}: FAILED -> {exc}")


def create_probe_injection_with_python_api(
    solver,
    *,
    injection_name: str,
    material: str,
    diameter: float,
    mass_flow_rate: float,
) -> None:
    branch = get_injection_branch(solver)

    names = set(list_injections(branch))
    if injection_name not in names:
        try_py(
            f"create injection {injection_name}",
            lambda: branch.create(name=injection_name),
        )

    injection = get_injection(branch, injection_name)

    # These were already working in your main script, so use Python API for them.
    try_py("set particle_type inert", lambda: setattr(injection, "particle_type", "inert"))
    injection = get_injection(branch, injection_name)

    try_py("set material", lambda: setattr(injection, "material", material))
    injection = get_injection(branch, injection_name)

    try_py("set injection_type surface", lambda: setattr(injection.injection_type, "option", "surface"))
    injection = get_injection(branch, injection_name)

    try_py(
        "set mass flow rate",
        lambda: injection.initial_values.mass_flow_rate.set_state(
            {"total_flow_rate": mass_flow_rate}
        ),
    )

    try_py(
        "set velocity face-normal",
        lambda: injection.initial_values.velocity.set_state(
            {
                "use_face_normal_direction": True,
                "x_velocity": 0.0,
                "y_velocity": 0.0,
                "z_velocity": 0.0,
            }
        ),
    )

    try_py(
        "set particle diameter",
        lambda: injection.initial_values.particle_size.set_state(
            {"option": "uniform", "diameter": diameter}
        ),
    )


def readback_injection(solver, injection_name: str) -> None:
    print_header(f"READBACK: {injection_name}")
    branch = get_injection_branch(solver)
    names = list_injections(branch)
    if injection_name not in names:
        print(f"{injection_name} does not exist.")
        return

    injection = get_injection(branch, injection_name)

    safe_state("full injection state", injection)
    safe_state("location state", injection.initial_values.location)
    safe_state("initial_values state", injection.initial_values)


def discover_tui_menus(solver) -> None:
    """
    These commands are intentionally read-only/help-oriented.
    They should print Fluent's available menus/commands to the terminal.
    """
    print_header("DISCOVER TUI MENUS")

    discovery_commands = [
        ("root help", "?\n"),
        ("define help", "/define\n?\nq\n"),
        ("define models help", "/define/models\n?\nq\n"),
        ("define models dpm help", "/define/models/dpm\n?\nq\n"),
        ("define injections help", "/define/injections\n?\nq\n"),
        ("define injections slash help", "/define/injections/\n?\nq\n"),
        ("report zones maybe", "/mesh/modify-zones/list-zones\n"),
        ("boundary conditions help", "/define/boundary-conditions\n?\nq\n"),
    ]

    for label, command in discovery_commands:
        tui(solver, label, command)


def probe_tui_surface_assignment(
    solver,
    *,
    injection_name: str,
    surface_name: str,
    surface_id: str,
) -> None:
    """
    Try several likely command forms. Some will fail. The point is to expose
    the real menu prompt/accepted syntax in the Fluent transcript.

    We try both surface name and zone id because Fluent TUI often wants zone IDs,
    while PyFluent settings often expose names.
    """
    print_header("PROBE TUI SURFACE ASSIGNMENT")

    values_to_try = [
        surface_name,
        surface_id,
        f"({surface_name})",
        f"({surface_id})",
        f'"{surface_name}"',
    ]

    # Candidate command names. We do not assume these are all correct.
    # The failed attempts should still reveal the correct nearby command names.
    candidate_prefixes = [
        "/define/injections/set-injection-properties",
        "/define/injections/set-injection-property",
        "/define/injections/set",
        "/define/injections/modify",
        "/define/injections/edit",
        "/define/injections/surface",
        "/define/injections/change-surface",
        "/define/injections/set-surface",
        "/define/injections/set-surfaces",
        "/define/injections/initial-values",
        "/define/injections/location",
    ]

    # Try compact one-line forms first.
    for prefix in candidate_prefixes:
        for surface_value in values_to_try:
            command = f"{prefix} {injection_name} injection-surfaces {surface_value}\n"
            tui(solver, f"{prefix} name/property/value {surface_value}", command)
            readback_injection(solver, injection_name)

    # Try interactive prompt-style forms.
    # These are deliberately broad because Fluent TUI menus often ask:
    # injection name -> property -> value -> quit.
    prompt_sequences = []

    for surface_value in values_to_try:
        prompt_sequences.extend(
            [
                (
                    f"interactive modify surface by value {surface_value}",
                    (
                        "/define/injections/modify\n"
                        f"{injection_name}\n"
                        "injection-surfaces\n"
                        f"{surface_value}\n"
                        "q\n"
                    ),
                ),
                (
                    f"interactive set surface by value {surface_value}",
                    (
                        "/define/injections/set\n"
                        f"{injection_name}\n"
                        "injection-surfaces\n"
                        f"{surface_value}\n"
                        "q\n"
                    ),
                ),
                (
                    f"interactive edit location by value {surface_value}",
                    (
                        "/define/injections/edit\n"
                        f"{injection_name}\n"
                        "location\n"
                        f"{surface_value}\n"
                        "q\n"
                    ),
                ),
                (
                    f"interactive initial values location {surface_value}",
                    (
                        "/define/injections/initial-values\n"
                        f"{injection_name}\n"
                        "location\n"
                        f"{surface_value}\n"
                        "q\n"
                    ),
                ),
            ]
        )

    for label, command in prompt_sequences:
        tui(solver, label, command)
        readback_injection(solver, injection_name)


def probe_scheme_paths(solver, *, injection_name: str, surface_name: str, surface_id: str) -> None:
    """
    Scheme-level probes. These are guesses, but useful because some Fluent
    internals expose lower-level commands that TUI wraps.

    Most may fail. Keep the terminal output.
    """
    print_header("PROBE SCHEME PATHS")

    scheme_exprs = [
        # Read/list style probes.
        "(cx-send '(get-zones))",
        "(cx-send '(get-domain-zones))",
        "(cx-send '(list-zones))",
        "(cx-send '(dpm-injections))",
        "(cx-send '(list-dpm-injections))",

        # Candidate setter forms using name/id.
        f'(cx-send \'(dpm-set-injection-surface "{injection_name}" "{surface_name}"))',
        f"(cx-send '(dpm-set-injection-surface \"{injection_name}\" {surface_id}))",
        f'(cx-send \'(set-dpm-injection-surface "{injection_name}" "{surface_name}"))',
        f"(cx-send '(set-dpm-injection-surface \"{injection_name}\" {surface_id}))",
    ]

    for expr in scheme_exprs:
        print_header(f"SCHEME TRY: {expr}")
        try:
            result = solver.scheme.exec((expr,))
            print(f"SCHEME RESULT: {result!r}", flush=True)
        except Exception as exc:
            print(f"SCHEME FAILED: {exc}", flush=True)
            traceback.print_exc()
        readback_injection(solver, injection_name)


def main() -> int:
    args = build_parser().parse_args()

    solver = connect(server_id=args.server_id)
    print(f"Connected to Fluent {solver.get_fluent_version()}")

    branch = get_injection_branch(solver)

    if args.delete_existing:
        delete_injection_if_present(branch, args.injection_name)

    print_header("INITIAL INJECTION LIST")
    list_injections(branch)

    create_probe_injection_with_python_api(
        solver,
        injection_name=args.injection_name,
        material=args.material,
        diameter=args.diameter,
        mass_flow_rate=args.mass_flow_rate,
    )

    readback_injection(solver, args.injection_name)

    discover_tui_menus(solver)

    probe_tui_surface_assignment(
        solver,
        injection_name=args.injection_name,
        surface_name=args.surface_name,
        surface_id=str(args.surface_id),
    )

    probe_scheme_paths(
        solver,
        injection_name=args.injection_name,
        surface_name=args.surface_name,
        surface_id=str(args.surface_id),
    )

    print_header("FINAL READBACK")
    readback_injection(solver, args.injection_name)

    print(
        "\nDone. Search the terminal output for the first point where "
        "'injection_surfaces' changes from False to a real surface/name/id."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
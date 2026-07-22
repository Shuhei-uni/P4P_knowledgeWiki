#!/usr/bin/env python3
"""Run legacy Fluent DPM Particle Tracks Summary reports.

The normal workflow assumes the desired case/data pair is already loaded in
the connected Fluent session.  The script discovers the current DPM injection
list, records each live index and name, and tracks by name so the result can be
audited even when injection names or counts differ between cases.

Case/data loading remains available through ``--load-case-data`` for sessions
where the operator explicitly wants the script to load the inputs.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import io
import json
import math
import re
import sys
import traceback
from collections.abc import Mapping, Sequence
from pathlib import Path, PureWindowsPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402
from pyansys_fluent.postprocess_live import load_case_data_pair  # noqa: E402
from pyansys_fluent.setup_common import print_header, require_remote_input  # noqa: E402


_COUNT_RE = re.compile(
    r"(?P<key>tracked|escaped|aborted|trapped|incomplete|evaporated|injected|inserted)"
    r"\s*=\s*(?P<value>[+-]?\d+(?:\.\d+)?)",
    re.IGNORECASE,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Discover the live Fluent DPM injections and run legacy Particle "
            "Tracks Summary reports one injection at a time."
        )
    )
    parser.add_argument("--server-id", default="1")
    parser.add_argument(
        "--case-file",
        default="",
        help="Remote Fluent case path; required only with --load-case-data.",
    )
    parser.add_argument(
        "--data-file",
        default="",
        help="Remote Fluent data path; required only with --load-case-data.",
    )
    parser.add_argument(
        "--load-case-data",
        action="store_true",
        help="Explicitly load --case-file and --data-file before discovery.",
    )
    parser.add_argument(
        "--already-loaded",
        action="store_true",
        help="Compatibility alias; the default workflow already assumes Fluent is loaded.",
    )
    parser.add_argument(
        "--load-mode",
        choices=("explicit", "paired"),
        default="explicit",
        help="Case/data loading mode when --load-case-data is used.",
    )
    parser.add_argument(
        "--injection",
        dest="injection_names",
        action="append",
        help="Track a live injection by name; repeat to select multiple names.",
    )
    parser.add_argument(
        "--index",
        dest="injection_indices",
        action="append",
        type=int,
        help="Track a live injection-list index; repeat to select multiple indices.",
    )
    parser.add_argument(
        "--order",
        choices=("live", "diameter-ascending", "diameter-descending"),
        default="diameter-ascending",
        help="Ordering for selected injections. Default: diameter-ascending.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output" / "dpm_particle_tracks"),
    )
    parser.add_argument("--run-label", default="")
    parser.add_argument(
        "--inspect-only",
        action="store_true",
        help="Discover and write the live injection inventory without tracking.",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Record a failed injection and continue with the remaining selections.",
    )
    parser.add_argument(
        "--detailed-output",
        action="store_true",
        help="Also write JSON, CSV, and raw transcript artifacts. The default is a simple text summary only.",
    )
    return parser


def _json_default(value: Any) -> str:
    return str(value)


def _recursive_find_numeric(payload: Any, keys: set[str]) -> float | None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            normalized = str(key).lower().replace("_", "-")
            if normalized in keys:
                try:
                    result = float(value)
                    if math.isfinite(result):
                        return result
                except (TypeError, ValueError):
                    pass
        for value in payload.values():
            found = _recursive_find_numeric(value, keys)
            if found is not None:
                return found
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes)):
        for value in payload:
            found = _recursive_find_numeric(value, keys)
            if found is not None:
                return found
    return None


def _diameter_um(injection: Any) -> float | None:
    try:
        state = injection.initial_values.particle_size.get_state()
    except Exception:
        state = None
    diameter_m = _recursive_find_numeric(
        state,
        {"diameter", "particle-diameter", "particle-size"},
    )
    if diameter_m is None:
        try:
            state = injection.get_state()
        except Exception:
            state = None
        diameter_m = _recursive_find_numeric(
            state,
            {"diameter", "particle-diameter", "particle-size"},
        )
    if diameter_m is None:
        return None
    return diameter_m * 1.0e6 if abs(diameter_m) < 1.0 else diameter_m


def _compact_state(obj: Any, label: str) -> Any:
    try:
        state = obj.get_state()
        return dict(state) if isinstance(state, Mapping) else state
    except Exception as exc:
        return {"_capture_error": f"{label}: {type(exc).__name__}: {exc}"}


def discover_live_injections(solver: Any) -> list[dict[str, Any]]:
    """Return the current DPM list with live index, name, and metadata."""
    try:
        branch = solver.settings.setup.models.discrete_phase.injections
    except Exception as exc:
        raise RuntimeError(
            "order/dependency issue: no active DPM injection branch is available. "
            "Load the intended Fluent case/data pair first."
        ) from exc

    try:
        names = [str(name) for name in branch.get_object_names()]
    except Exception as exc:
        raise RuntimeError(
            "path/version issue: Fluent did not expose the live DPM injection names."
        ) from exc

    if not names:
        raise RuntimeError("order/dependency issue: the live DPM injection list is empty.")

    discovered: list[dict[str, Any]] = []
    for index, name in enumerate(names):
        injection = branch[name]
        state = _compact_state(injection, f"injections.{name}")
        initial_values = state.get("initial_values", {}) if isinstance(state, Mapping) else {}
        location = initial_values.get("location", {}) if isinstance(initial_values, Mapping) else {}
        injection_type = state.get("injection_type", {}) if isinstance(state, Mapping) else {}
        discovered.append(
            {
                "index": index,
                "name": name,
                "diameter_um": _diameter_um(injection),
                "particle_type": state.get("particle_type") if isinstance(state, Mapping) else None,
                "material": state.get("material") if isinstance(state, Mapping) else None,
                "injection_type": injection_type,
                "injection_surfaces": (
                    location.get("injection_surfaces") if isinstance(location, Mapping) else None
                ),
                "state": state,
            }
        )
    return discovered


def select_injections(
    discovered: Sequence[Mapping[str, Any]],
    *,
    requested_names: Sequence[str] | None,
    requested_indices: Sequence[int] | None,
    order: str,
) -> list[dict[str, Any]]:
    by_name = {str(item["name"]): item for item in discovered}
    by_index = {int(item["index"]): item for item in discovered}

    if requested_names or requested_indices:
        selected: list[Mapping[str, Any]] = []
        seen: set[str] = set()
        for name in requested_names or []:
            if name not in by_name:
                raise RuntimeError(
                    f"path/version issue: requested injection {name!r} is not in the live list "
                    f"{list(by_name)}"
                )
            if name not in seen:
                selected.append(by_name[name])
                seen.add(name)
        for index in requested_indices or []:
            if index not in by_index:
                raise RuntimeError(
                    f"path/version issue: requested injection index {index} is invalid; "
                    f"valid range is 0..{len(discovered) - 1}"
                )
            name = str(by_index[index]["name"])
            if name not in seen:
                selected.append(by_index[index])
                seen.add(name)
    else:
        selected = list(discovered)

    def diameter_key(item: Mapping[str, Any]) -> tuple[bool, float, int]:
        diameter = item.get("diameter_um")
        return (diameter is None, float(diameter or 0.0), int(item["index"]))

    if order == "live":
        selected.sort(key=lambda item: int(item["index"]))
    elif order == "diameter-ascending":
        selected.sort(key=diameter_key)
    else:
        selected.sort(key=diameter_key, reverse=True)
    return [dict(item) for item in selected]


def execute_tui(solver: Any, command: str) -> Any:
    """Execute a literal TUI command without using nested generated wrappers."""
    framed_command = command if command.endswith("\n") else command + "\n"
    method = getattr(solver, "execute_tui", None)
    if method is not None:
        return method(framed_command)
    return solver.scheme.eval(
        f'(ti-menu-load-string "{quote_scheme_string(framed_command)}")'
    )


def configure_particle_track_summary(solver: Any) -> dict[str, Any]:
    """Configure the legacy non-object Particle Tracks Summary workflow."""
    commands = [
        '/file/set-tui-version "24.2"',
        "/preferences/graphics/enable-non-object-based-workflow yes",
        "/display/set/particle-tracks/report-type summary",
        # Fluent 2024 R2's live prompt calls the console destination "screen".
        "/display/set/particle-tracks/report-to screen",
        "/display/set/particle-tracks/display? no",
    ]
    for command in commands:
        execute_tui(solver, command)
    return {"commands": commands, "report_type": "summary", "display": False}


def _quote_tui_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def build_track_command(injection_name: str) -> str:
    safe_name = _quote_tui_string(injection_name)
    # The live 2024 R2 prompt requires the phase domain and colour variable
    # before the selected injection.  The colour variable is irrelevant
    # because display is disabled for Summary.
    return (
        f'/display/particle-tracks particle-tracks mixture particle-resid-time '
        f'"{safe_name}" () 0 0'
    )


def parse_summary_report(raw_output: str) -> dict[str, int | None]:
    counts: dict[str, int | None] = {
        "tracked": None,
        # Fluent omits fates that did not occur in a Summary report.  Treat
        # omitted fate rows as zero once a tracked count is present.
        "escaped": 0,
        "aborted": 0,
        "trapped": 0,
        "incomplete": 0,
        "evaporated": 0,
        "injected": 0,
        "inserted": 0,
    }
    for match in _COUNT_RE.finditer(raw_output):
        key = match.group("key").lower()
        counts[key] = int(float(match.group("value")))
    return counts


def track_one_injection(solver: Any, item: Mapping[str, Any]) -> dict[str, Any]:
    name = str(item["name"])
    command = build_track_command(name)
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            returned = execute_tui(solver, command)
    except Exception as exc:
        raw_output = buffer.getvalue()
        return {
            "index": int(item["index"]),
            "name": name,
            "status": "failed",
            "failure_category": "requires TUI fallback",
            "error": f"{type(exc).__name__}: {exc}",
            "command": command,
            "raw_output": raw_output,
            "counts": parse_summary_report(raw_output),
            "returned": repr(exc),
        }

    raw_output = buffer.getvalue()
    counts = parse_summary_report(raw_output)
    summary_line = next(
        (
            line.strip()
            for line in raw_output.splitlines()
            if "number tracked" in line.lower()
        ),
        "",
    )
    if counts["tracked"] is None:
        return {
            "index": int(item["index"]),
            "name": name,
            "status": "failed",
            "failure_category": "path/version issue",
            "error": "Particle Tracks returned without a parseable Summary count.",
            "command": command,
            "raw_output": raw_output,
            "summary_line": summary_line,
            "counts": counts,
            "returned": repr(returned),
        }
    return {
        "index": int(item["index"]),
        "name": name,
        "status": "ok",
        "failure_category": None,
        "error": None,
        "command": command,
        "raw_output": raw_output,
        "summary_line": summary_line,
        "counts": counts,
        "returned": repr(returned),
    }


def format_dpm_console_report(payload: Mapping[str, Any]) -> str:
    """Return the compact report a user can paste into a setup report."""
    lines = [
        "DPM Particle Tracks Summary",
        f"Run: {payload.get('run_label', 'unnamed')}",
        "",
    ]
    results = payload.get("results", [])
    if not results:
        lines.append("No Particle Tracks computations were run.")
        lines.append("")
        for item in payload.get("selected_injections", []) or payload.get("injections", []):
            lines.append(
                f"index={item.get('index')} injection={item.get('name')}"
            )
        return "\n".join(lines) + "\n"

    metadata_by_name = {
        str(item.get("name")): item for item in payload.get("injections", [])
    }
    for result in results:
        name = str(result.get("name", "unknown"))
        metadata = metadata_by_name.get(name, {})
        diameter = metadata.get("diameter_um")
        diameter_text = f", diameter = {float(diameter):g} um" if diameter is not None else ""
        lines.append(f"Injection: {name}{diameter_text}")
        if result.get("status") != "ok":
            lines.append(
                f"status = {result.get('status', 'failed')}, "
                f"error = {result.get('error', 'unknown error')}"
            )
            lines.append("")
            continue

        summary_line = str(result.get("summary_line", "")).strip()
        if not summary_line:
            counts = result.get("counts", {})
            summary_line = (
                f"number tracked = {counts.get('tracked')}, "
                f"escaped = {counts.get('escaped', 0)}, "
                f"trapped = {counts.get('trapped', 0)}, "
                f"incomplete = {counts.get('incomplete', 0)}"
            )
        lines.extend(["DPM Iteration ....", summary_line, ""])

    return "\n".join(lines)


def write_console_report(
    output_dir: Path,
    run_label: str,
    payload: Mapping[str, Any],
) -> Path:
    """Write the compact DPM report; detailed artifacts are opt-in."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{run_label}-summary.txt"
    path.write_text(format_dpm_console_report(payload), encoding="utf-8")
    return path


def write_outputs(
    output_dir: Path,
    run_label: str,
    payload: Mapping[str, Any],
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{run_label}-particle-track-summary.json"
    csv_path = output_dir / f"{run_label}-particle-track-summary.csv"
    transcript_path = output_dir / f"{run_label}-particle-track-transcript.txt"
    json_path.write_text(
        json.dumps(payload, indent=2, default=_json_default) + "\n",
        encoding="utf-8",
    )

    fieldnames = [
        "index",
        "diameter_um",
        "injection",
        "material",
        "particle_type",
        "status",
        "tracked",
        "escaped",
        "aborted",
        "trapped",
        "incomplete",
        "evaporated",
        "injected",
        "inserted",
        "failure_category",
        "error",
    ]
    metadata_by_name = {
        str(item["name"]): item for item in payload.get("injections", [])
    }
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in payload.get("results", []):
            name = str(result.get("name"))
            metadata = metadata_by_name.get(name, {})
            counts = result.get("counts", {})
            writer.writerow(
                {
                    "index": result.get("index"),
                    "diameter_um": metadata.get("diameter_um"),
                    "injection": name,
                    "material": metadata.get("material"),
                    "particle_type": metadata.get("particle_type"),
                    "status": result.get("status"),
                    **{key: counts.get(key) for key in fieldnames[6:14]},
                    "failure_category": result.get("failure_category"),
                    "error": result.get("error"),
                }
            )

    transcript_lines: list[str] = []
    for result in payload.get("results", []):
        transcript_lines.append(
            f"===== index={result.get('index')} injection={result.get('name')} ====="
        )
        transcript_lines.append(str(result.get("raw_output", "")))
    transcript_path.write_text("\n".join(transcript_lines), encoding="utf-8")
    return json_path, csv_path, transcript_path


def run_dpm_particle_track_check(
    solver: Any,
    *,
    case_file: str = "",
    data_file: str = "",
    load_case_data: bool = False,
    load_mode: str = "explicit",
    injection_names: Sequence[str] = (),
    injection_indices: Sequence[int] = (),
    order: str = "diameter-ascending",
    inspect_only: bool = False,
    keep_going: bool = False,
    run_label: str = "active-session",
) -> dict[str, Any]:
    """Run the current dynamic DPM check on an existing solver session."""
    payload: dict[str, Any] = {
        "case_file": case_file,
        "data_file": data_file,
        "run_label": run_label,
        "load_requested": bool(load_case_data),
        "selection": {
            "names": list(injection_names),
            "indices": list(injection_indices),
            "order": order,
        },
        "report_controls": {},
        "injections": [],
        "selected_injections": [],
        "results": [],
    }

    payload["fluent_version"] = solver.get_fluent_version()

    if load_case_data:
        if not case_file.strip() or not data_file.strip():
            raise ValueError("--load-case-data requires both --case-file and --data-file.")
        print_header("Load Case/Data")
        require_remote_input(solver, case_file, "case file")
        require_remote_input(solver, data_file, "data file")
        payload["load"] = load_case_data_pair(
            solver,
            case_file=case_file,
            data_file=data_file,
            load_strategy=load_mode,
        )
    else:
        payload["load"] = {"mode": "already-loaded-session"}
        print_header("Use Already-Loaded Case/Data")
        print("No case/data load requested; inspecting the active Fluent session.", flush=True)

    print_header("Discover Live DPM Injections")
    discovered = discover_live_injections(solver)
    selected = select_injections(
        discovered,
        requested_names=injection_names,
        requested_indices=injection_indices,
        order=order,
    )
    payload["injections"] = discovered
    payload["selected_injections"] = [
        {"index": item["index"], "name": item["name"]} for item in selected
    ]
    for item in discovered:
        marker = "*" if item["name"] in {str(x["name"]) for x in selected} else " "
        print(
            f"{marker} index={item['index']} name={item['name']} "
            f"diameter_um={item['diameter_um']} material={item['material']}",
            flush=True,
        )

    if not inspect_only:
        print_header("Configure Summary Particle Tracks")
        payload["report_controls"] = configure_particle_track_summary(solver)

        print_header("Track Selected Injections")
        for item in selected:
            print(f"Tracking index={item['index']} name={item['name']} ...", flush=True)
            result = track_one_injection(solver, item)
            payload["results"].append(result)
            print(
                f"{item['name']}: {result['status']} counts={result['counts']} "
                f"category={result['failure_category']}",
                flush=True,
            )
            if result["status"] != "ok" and not keep_going:
                break

    return payload


def main() -> int:
    args = build_parser().parse_args()
    if args.load_case_data and args.already_loaded:
        raise ValueError("Use either --load-case-data or --already-loaded, not both.")

    run_label = args.run_label.strip()
    if not run_label:
        run_label = PureWindowsPath(args.data_file).stem if args.data_file else "active-session"
    output_dir = Path(args.output_dir).expanduser().resolve()

    print_header("Connect")
    solver = connect(server_id=args.server_id)
    print(f"Connected to {solver.get_fluent_version()}", flush=True)
    payload = run_dpm_particle_track_check(
        solver,
        case_file=args.case_file,
        data_file=args.data_file,
        load_case_data=args.load_case_data,
        load_mode=args.load_mode,
        injection_names=args.injection_names or (),
        injection_indices=args.injection_indices or (),
        order=args.order,
        inspect_only=args.inspect_only,
        keep_going=args.keep_going,
        run_label=run_label,
    )

    report_path = write_console_report(output_dir, run_label, payload)
    print(format_dpm_console_report(payload), end="", flush=True)
    print(f"report: {report_path}")
    if args.detailed_output:
        json_path, csv_path, transcript_path = write_outputs(output_dir, run_label, payload)
        print(f"json: {json_path}")
        print(f"csv: {csv_path}")
        print(f"transcript: {transcript_path}")
    return 0 if args.inspect_only or all(
        item["status"] == "ok" for item in payload["results"]
    ) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)

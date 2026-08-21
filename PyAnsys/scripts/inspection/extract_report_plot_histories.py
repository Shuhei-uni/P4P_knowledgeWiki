#!/usr/bin/env python3
"""Recover Fluent report-plot histories from native report files.

The live PyFluent monitor endpoint can expose an empty history even when
Fluent's Report File objects have written a complete ``.out`` history.  This
script discovers the configured report files, resolves relative names against
an operator-supplied remote directory, reads the Fluent Lisp-style forms
through Scheme, and writes portable JSON/PNG artifacts.

The script is intentionally read-only: it does not load case/data, change
Fluent's working directory, start monitors, iterate, or write to the Fluent
host.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from datetime import datetime
import json
import math
from pathlib import Path, PureWindowsPath
import re
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import quote_scheme_string, remote_file_exists  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Recover Fluent Report File histories for configured report plots "
            "without changing the active session."
        )
    )
    parser.add_argument(
        "--server-id",
        default="1",
        help="Configured Fluent endpoint routing alias. Default: 1.",
    )
    parser.add_argument(
        "--report-dir",
        default="",
        help=(
            "Remote Windows directory used to resolve relative Report File "
            "names. Fluent's working directory is not changed."
        ),
    )
    parser.add_argument(
        "--filename-suffix",
        default="",
        help=(
            "Optional replacement suffix for Fluent's generated report-file names. "
            "For example, '.out' reads an unsuffixed file and '_1_1.out' reads "
            "the corresponding numbered variant while retaining the configured "
            "report definition mapping."
        ),
    )
    parser.add_argument(
        "--report-name",
        dest="report_names",
        action="append",
        default=[],
        help=(
            "Optional case-insensitive substring filter for a monitor/report "
            "name. Repeat to select several histories."
        ),
    )
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="Include configured Report Files whose active flag is false.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "output" / "report_plot_histories"),
        help="Local directory for JSON and PNG artifacts.",
    )
    parser.add_argument(
        "--filename-prefix",
        default="report_plot_histories",
        help="Prefix for generated local artifacts.",
    )
    parser.add_argument(
        "--title",
        default="Fluent Report Plot Histories",
        help="Title used for the overview PNG.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Write JSON only and skip the overview PNG.",
    )
    return parser


def resolve_remote_report_path(
    file_name: str,
    report_dir: str,
    filename_suffix: str = "",
) -> str:
    """Resolve a Fluent Report File name without changing the Fluent session."""
    configured = PureWindowsPath(str(file_name).strip())
    if filename_suffix.strip():
        suffix = filename_suffix.strip()
        if not suffix.startswith("_") and not suffix.startswith("."):
            suffix = f".{suffix}"
        basename = configured.name
        if re.search(r"_\d+_\d+\.out$", basename, flags=re.IGNORECASE):
            replaced = re.sub(r"_\d+_\d+\.out$", suffix, basename, flags=re.IGNORECASE)
        else:
            replaced = re.sub(r"\.out$", suffix, basename, flags=re.IGNORECASE)
        configured = configured.with_name(replaced)
    if configured.is_absolute() or not report_dir.strip():
        return str(configured)
    return str(PureWindowsPath(report_dir.strip()) / configured)


def read_remote_forms(solver: Any, path: str) -> Any:
    """Read all Scheme-readable forms from a remote Fluent text file."""
    escaped = quote_scheme_string(path)
    expression = (
        f'(with-input-from-file "{escaped}" '
        "(lambda () (let loop ((x (read)) (out (quote ()))) "
        "(if (eof-object? x) (reverse out) (loop (read) (cons x out))))))"
    )
    return solver.scheme.eval(expression)


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _as_text(value: Any) -> str:
    if isinstance(value, (list, tuple)) and value:
        return str(value[-1])
    return str(value)


def parse_report_forms(payload: Any) -> dict[str, Any]:
    """Parse the common Fluent report-file header and iteration/value pairs.

    Fluent versions may add nested header forms before the numeric rows.  The
    parser therefore locates the first numeric item instead of relying on a
    fixed header length.  If a future serialization uses a different data
    shape, fail explicitly so the artifact is marked incomplete.
    """
    if not isinstance(payload, (list, tuple)) or len(payload) < 5:
        length = len(payload) if hasattr(payload, "__len__") else "unknown"
        raise ValueError(f"unexpected report-file form payload: length={length}")

    report_file_label = _as_text(payload[0])
    x_label = _as_text(payload[1])
    report_definition = _as_text(payload[2])

    numeric_start = None
    for index, item in enumerate(payload[3:], start=3):
        if _is_number(item):
            numeric_start = index
            break
    if numeric_start is None:
        raise ValueError(f"no numeric history found for {report_definition}")

    numeric = list(payload[numeric_start:])
    if len(numeric) < 2:
        raise ValueError(f"incomplete iteration/value history for {report_definition}")
    if len(numeric) % 2:
        numeric = numeric[:-1]

    iterations: list[int] = []
    values: list[float] = []
    for index in range(0, len(numeric), 2):
        if not _is_number(numeric[index]) or not _is_number(numeric[index + 1]):
            raise ValueError(f"non-numeric report row at offset {numeric_start + index}")
        iterations.append(int(float(numeric[index])))
        values.append(float(numeric[index + 1]))

    return {
        "report_file_label": report_file_label,
        "x_label": x_label,
        "report_definition": report_definition,
        "points": len(iterations),
        "iterations": iterations,
        "values": values,
        "summary": {
            "first_iteration": iterations[0] if iterations else None,
            "last_iteration": iterations[-1] if iterations else None,
            "first_value": values[0] if values else None,
            "last_value": values[-1] if values else None,
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None,
        },
    }


def _report_definition_candidates(monitor_name: str, config: Mapping[str, Any]) -> list[str]:
    values: list[str] = [monitor_name]
    report_defs = config.get("report_defs", [])
    if isinstance(report_defs, str):
        values.append(report_defs)
    elif isinstance(report_defs, Sequence):
        values.extend(str(item) for item in report_defs)
    return values


def matches_filter(
    monitor_name: str,
    config: Mapping[str, Any],
    filters: Sequence[str],
) -> bool:
    if not filters:
        return True
    candidates = [candidate.casefold() for candidate in _report_definition_candidates(monitor_name, config)]
    return any(any(selector.casefold() in candidate for candidate in candidates) for selector in filters)


def _finite_values(values: Sequence[float]) -> list[float]:
    return [value for value in values if math.isfinite(value)]


def set_plot_scale(axis: Any, values: Sequence[float]) -> None:
    finite = _finite_values(values)
    if not finite:
        return
    nonzero = [abs(value) for value in finite if value != 0.0]
    if min(finite) > 0.0 and max(finite) / min(finite) > 1e3:
        axis.set_yscale("log")
    elif min(finite) < 0.0 < max(finite) and nonzero:
        if max(nonzero) / min(nonzero) > 1e3:
            axis.set_yscale("symlog", linthresh=max(max(nonzero) * 1e-6, 1e-12))


def _plot_title(record: Mapping[str, Any]) -> str:
    return str(record.get("report_definition") or record.get("monitor_name") or "report")


def write_overview_plot(records: Sequence[Mapping[str, Any]], output_path: Path, title: str) -> None:
    """Write a compact overview while preserving raw histories in JSON."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    columns = min(5, max(1, len(records)))
    rows = max(1, math.ceil(len(records) / columns))
    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(4.2 * columns, 3.1 * rows),
        squeeze=False,
        constrained_layout=True,
    )
    flat_axes = list(axes.flat)
    for axis, record in zip(flat_axes, records):
        axis.plot(record["iterations"], record["values"], linewidth=0.85, color="#2563eb")
        axis.set_title(_plot_title(record), fontsize=8)
        axis.set_xlabel("Iteration", fontsize=7)
        axis.tick_params(axis="both", labelsize=7)
        axis.grid(True, which="both", alpha=0.25)
        set_plot_scale(axis, record["values"])
    for axis in flat_axes[len(records) :]:
        axis.axis("off")
    figure.suptitle(title, fontsize=14)
    figure.savefig(output_path, dpi=180)
    plt.close(figure)


def main() -> int:
    args = build_parser().parse_args()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"{args.filename_prefix}_{timestamp}.json"
    png_path = output_dir / f"{args.filename_prefix}_{timestamp}.png"

    solver = connect(server_id=args.server_id, start_transcript=False)
    monitor_state = solver.settings.solution.monitor.get_state()
    report_files = monitor_state.get("report_files", {})
    if not isinstance(report_files, Mapping):
        raise RuntimeError("Fluent did not expose solution.monitor.report_files as a mapping")

    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    considered = 0

    for monitor_name, raw_config in report_files.items():
        if not isinstance(raw_config, Mapping):
            errors.append({"monitor_name": str(monitor_name), "error": "invalid report-file configuration"})
            continue
        config = dict(raw_config)
        if not args.include_inactive and config.get("active") is False:
            continue
        if not matches_filter(str(monitor_name), config, args.report_names):
            continue
        considered += 1

        configured_name = str(config.get("file_name") or "").strip()
        if not configured_name:
            errors.append({"monitor_name": str(monitor_name), "error": "missing file_name"})
            continue
        resolved_name = resolve_remote_report_path(
            configured_name,
            args.report_dir,
            args.filename_suffix,
        )
        print(f"Reading {monitor_name}: {resolved_name}", flush=True)
        try:
            if not remote_file_exists(solver, resolved_name):
                raise FileNotFoundError(f"Fluent cannot see remote report file: {resolved_name}")
            record = parse_report_forms(read_remote_forms(solver, resolved_name))
            record.update(
                {
                    "monitor_name": str(monitor_name),
                    "configured_file_name": configured_name,
                    "resolved_file_name": resolved_name,
                    "report_defs": config.get("report_defs", []),
                }
            )
            records.append(record)
            print(f"  recovered {record['points']} points", flush=True)
        except Exception as exc:
            errors.append(
                {
                    "monitor_name": str(monitor_name),
                    "configured_file_name": configured_name,
                    "resolved_file_name": resolved_name,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            print(f"  FAILED: {type(exc).__name__}: {exc}", flush=True)

    payload = {
        "kind": "fluent_report_file_histories",
        "case_identity": {
            "status": "unavailable",
            "basis": "read-only extraction from an existing session; this script does not load case/data",
        },
        "remote_report_dir": args.report_dir or None,
        "report_filename_suffix": args.filename_suffix or None,
        "configured_report_file_count": len(report_files),
        "selected_report_file_count": considered,
        "recovered_report_file_count": len(records),
        "errors": errors,
        "reports": records,
    }
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved report history JSON to: {json_path}")

    if records and not args.no_plot:
        write_overview_plot(records, png_path, args.title)
        print(f"Saved report history overview to: {png_path}")

    if not records:
        print("No report histories were recovered; preserve the JSON error manifest and investigate the paths.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

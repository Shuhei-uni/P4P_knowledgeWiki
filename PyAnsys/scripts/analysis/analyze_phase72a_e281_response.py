"""Align E2.81 Fluent reports, quantify matched response, and write SVG figures.

Uses only the Python standard library so the post-run record can be reproduced
without a plotting package.  The native Report File histories remain the
source for values; the SVGs are views over those histories.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

E27_NATIVE_ENDPOINT = 8586
E27_FIXED_FILM_DT_S = 1.0e-5


def load_report_histories(output_root: Path) -> dict[str, dict[str, Any]]:
    path = output_root / "report-histories.json"
    if not path.is_file():
        raise FileNotFoundError(f"Missing completed report histories: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload:
        raise ValueError("Report histories are empty or have an unexpected shape")
    return payload


def history_for(histories: dict[str, dict[str, Any]], *suffixes: str) -> tuple[str, dict[str, Any]]:
    folded_suffixes = tuple(value.casefold() for value in suffixes)
    matches = [
        (name, record)
        for name, record in histories.items()
        if any(name.casefold().endswith(suffix) for suffix in folded_suffixes)
        or any(
            any(str(record.get(field, "")).casefold().endswith(suffix) for field in ("definition_name", "report_definition"))
            for suffix in folded_suffixes
        )
    ]
    # Prefer the metric immediately following the EWF namespace. A broad
    # endswith match for "velocity-mag-awavg" also matches the separate
    # "surface-velocity-mag-awavg" monitor.
    exact_metrics = [
        (name, record)
        for name, record in matches
        if any(
            name.casefold().endswith(f"ewf-{suffix}")
            or any(
                str(record.get(field, "")).casefold().endswith(f"ewf-{suffix}")
                for field in ("definition_name", "report_definition")
            )
            for suffix in folded_suffixes
        )
    ]
    if exact_metrics:
        matches = exact_metrics
    if len(matches) != 1:
        raise KeyError(f"Expected one history for {suffixes}; found {[name for name, _ in matches]}")
    return matches[0]


def history_rows(record: dict[str, Any]) -> dict[int, float]:
    iterations = record.get("iterations")
    values = record.get("values")
    if not isinstance(iterations, list) or not isinstance(values, list) or len(iterations) != len(values):
        raise ValueError(f"Invalid parsed history {record.get('definition_name', record.get('report_definition'))}")
    rows = {int(iteration): float(value) for iteration, value in zip(iterations, values)}
    if len(rows) != len(iterations):
        raise ValueError("A report history contains duplicate native coordinates")
    return rows


def parse_transcript(path: Path) -> dict[int, dict[str, float]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing native solve transcript: {path}")
    def native_row(line: str) -> int | None:
        fields = line.split()
        if len(fields) < 10 or not fields[0].isdigit() or len(fields[0]) < 4:
            return None
        if not re.fullmatch(r"(?:\d+:)?\d{2}:\d{2}", fields[-2]) or not fields[-1].isdigit():
            return None
        try:
            for value in fields[1:-2]:
                float(value)
        except ValueError:
            return None
        return int(fields[0])
    film_re = re.compile(
        r"Film time\s*=\s*([-+\d.eE]+)\s+with timestep\s*=\s*([-+\d.eE]+).*?max_cfl:\s*([-+\d.eE]+)",
        re.IGNORECASE,
    )
    residual_re = re.compile(
        r"sub-iteration:\s*\d+\s+residual\s*-\s*h:\s*([-+\d.eE]+);\s*u:\s*([-+\d.eE]+);\s*v:\s*([-+\d.eE]+)",
        re.IGNORECASE,
    )
    records: dict[int, dict[str, float]] = {}
    current_iteration: int | None = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        row_native = native_row(line)
        if row_native is not None:
            # Fluent prints the completed global residual row before the next
            # step's EWF sub-iteration messages; those following messages
            # therefore belong to the next native iteration.
            current_iteration = row_native + 1
            records.setdefault(current_iteration, {})
            continue
        if current_iteration is None:
            continue
        film_match = film_re.search(line)
        if film_match:
            record = records[current_iteration]
            record["film_time_s"] = float(film_match.group(1))
            record["film_timestep_s"] = float(film_match.group(2))
            record["film_courant_max"] = float(film_match.group(3))
        residual_match = residual_re.search(line)
        if residual_match:
            record = records[current_iteration]
            for name, value in zip(("ewf_h_residual_max", "ewf_u_residual_max", "ewf_v_residual_max"), residual_match.groups()):
                number = abs(float(value))
                record[name] = max(record.get(name, 0.0), number)
                record[name.replace("_max", "_last")] = number
            record["ewf_residual_rows"] = record.get("ewf_residual_rows", 0.0) + 1.0
    if not records:
        raise ValueError("No native iteration rows were recovered from the solve transcript")
    return records


def read_e27_monitor(monitor_dir: Path, metric: str) -> float | None:
    expected = f"p72a-e2.7-ewf-{metric}.out".casefold()
    matches = [path for path in monitor_dir.glob("*.out") if path.name.casefold().endswith(expected)]
    if len(matches) != 1:
        return None
    values: dict[int, float] = {}
    for line in matches[0].read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            values[int(parts[0])] = float(parts[1])
        except ValueError:
            continue
    return values.get(E27_NATIVE_ENDPOINT)


def write_joined_csv(
    path: Path,
    histories: dict[str, dict[str, Any]],
    transcript: dict[int, dict[str, float]],
) -> list[int]:
    series = {name: history_rows(record) for name, record in histories.items()}
    coordinates = sorted(set.intersection(*(set(rows) for rows in series.values())))
    if not coordinates:
        raise ValueError("E2.81 report files have no common native coordinates")
    fields = ["native_iteration"] + list(series) + [
        "film_time_s", "film_time_increment_s", "film_timestep_s", "film_courant_max",
        "ewf_h_residual_max", "ewf_u_residual_max", "ewf_v_residual_max",
        "ewf_h_residual_last", "ewf_u_residual_last", "ewf_v_residual_last", "ewf_residual_rows",
    ]
    # The first reported solve step gives the pre-step EWF time from its own
    # timestep, keeping the parent's nonzero displayed Fluent time out of the
    # incremental fast-step comparison.
    first_film = next((n for n in coordinates if "film_time_s" in transcript.get(n, {})), None)
    initial_time = None
    if first_film is not None:
        initial_time = transcript[first_film]["film_time_s"] - transcript[first_film]["film_timestep_s"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for iteration in coordinates:
            row: dict[str, Any] = {"native_iteration": iteration}
            row.update({name: rows[iteration] for name, rows in series.items()})
            row.update(transcript.get(iteration, {}))
            if initial_time is not None and "film_time_s" in row:
                row["film_time_increment_s"] = row["film_time_s"] - initial_time
            writer.writerow(row)
    return coordinates


def svg_panel(
    *, x: float, y: float, width: float, height: float, title: str, x_label: str, y_label: str,
    x_range: tuple[float, float], series: list[dict[str, Any]], y_scale: str = "linear",
    reference_x: float | None = None, reference_lines: list[dict[str, Any]] | None = None,
) -> str:
    left, right, top, bottom = x + 72, x + width - 18, y + 34, y + height - 52
    all_y = [float(value) for item in series for value in item["y"] if math.isfinite(float(value))]
    if reference_lines:
        all_y.extend(float(item["value"]) for item in reference_lines if math.isfinite(float(item["value"])))
    all_y = [value for value in all_y if value > 0] if y_scale == "log" else all_y
    if not all_y:
        all_y = [1.0, 10.0] if y_scale == "log" else [0.0, 1.0]
    if y_scale == "log":
        ymin = math.floor(math.log10(min(all_y)))
        ymax = math.ceil(math.log10(max(all_y)))
        if ymin == ymax:
            ymax += 1
        y_map = lambda value: bottom - (math.log10(max(float(value), 10.0 ** ymin)) - ymin) / (ymax - ymin) * (bottom - top)
        tick_vals = [10.0**v for v in range(ymin, ymax + 1)]
    else:
        ymin, ymax = min(0.0, min(all_y)), max(all_y)
        if math.isclose(ymin, ymax):
            ymax = ymin + 1.0
        pad = (ymax - ymin) * 0.06
        ymin -= pad
        ymax += pad
        y_map = lambda value: bottom - (float(value) - ymin) / (ymax - ymin) * (bottom - top)
        tick_vals = [ymin + i * (ymax - ymin) / 4.0 for i in range(5)]
    xmin, xmax = x_range
    if math.isclose(xmin, xmax):
        xmax = xmin + 1
    x_map = lambda value: left + (float(value) - xmin) / (xmax - xmin) * (right - left)
    output = [f'<g class="panel"><text x="{x + 8}" y="{y + 20}" class="panel-title">{html.escape(title)}</text>']
    for tick in tick_vals:
        yy = y_map(tick)
        label = f"{tick:.3g}" if y_scale == "linear" else f"1e{math.log10(tick):.0f}"
        output.append(f'<line x1="{left:.1f}" y1="{yy:.1f}" x2="{right:.1f}" y2="{yy:.1f}" class="grid"/>')
        output.append(f'<text x="{left - 9:.1f}" y="{yy + 4:.1f}" text-anchor="end" class="tick">{label}</text>')
    for i in range(5):
        value = xmin + i * (xmax - xmin) / 4.0
        xx = x_map(value)
        output.append(f'<line x1="{xx:.1f}" y1="{top:.1f}" x2="{xx:.1f}" y2="{bottom:.1f}" class="grid"/>')
        output.append(f'<text x="{xx:.1f}" y="{bottom + 18:.1f}" text-anchor="middle" class="tick">{value:.0f}</text>')
    output.append(f'<line x1="{left:.1f}" y1="{bottom:.1f}" x2="{right:.1f}" y2="{bottom:.1f}" class="axis"/>')
    output.append(f'<line x1="{left:.1f}" y1="{top:.1f}" x2="{left:.1f}" y2="{bottom:.1f}" class="axis"/>')
    if reference_x is not None and xmin <= reference_x <= xmax:
        xx = x_map(reference_x)
        output.append(f'<line x1="{xx:.1f}" y1="{top:.1f}" x2="{xx:.1f}" y2="{bottom:.1f}" class="reference-v"/>')
    for item in reference_lines or []:
        value = float(item["value"])
        if (y_scale == "linear" or value > 0) and min(all_y) <= value <= max(all_y):
            yy = y_map(value)
            output.append(f'<line x1="{left:.1f}" y1="{yy:.1f}" x2="{right:.1f}" y2="{yy:.1f}" stroke="{item.get("color", "#64748b")}" stroke-width="1.4" stroke-dasharray="6 5"/>')
    for item in series:
        pts = []
        for xv, yv in zip(item["x"], item["y"]):
            value = float(yv)
            if math.isfinite(value) and (y_scale == "linear" or value > 0):
                pts.append(f"{x_map(xv):.1f},{y_map(value):.1f}")
        if pts:
            dash = ' stroke-dasharray="6 5"' if item.get("dash") else ""
            output.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{item["color"]}" stroke-width="1.6"{dash}/>')
    output.append(f'<text x="{(left + right) / 2:.1f}" y="{y + height - 8}" text-anchor="middle" class="axis-label">{html.escape(x_label)}</text>')
    output.append(f'<text x="{x + 13}" y="{(top + bottom) / 2:.1f}" text-anchor="middle" class="axis-label" transform="rotate(-90 {x + 13} {(top + bottom) / 2:.1f})">{html.escape(y_label)}</text>')
    legend_x, legend_y = right - 165, top + 14
    for index, item in enumerate(series):
        yy = legend_y + index * 17
        output.append(f'<line x1="{legend_x}" y1="{yy}" x2="{legend_x + 23}" y2="{yy}" stroke="{item["color"]}" stroke-width="2"/>')
        output.append(f'<text x="{legend_x + 29}" y="{yy + 4}" class="legend">{html.escape(item["label"])}</text>')
    if reference_lines:
        for index, item in enumerate(reference_lines):
            yy = legend_y + (len(series) + index) * 17
            output.append(f'<line x1="{legend_x}" y1="{yy}" x2="{legend_x + 23}" y2="{yy}" stroke="{item.get("color", "#64748b")}" stroke-width="1.5" stroke-dasharray="6 5"/>')
            output.append(f'<text x="{legend_x + 29}" y="{yy + 4}" class="legend">{html.escape(item["label"])}</text>')
    output.append("</g>")
    return "\n".join(output)


def write_svg(path: Path, title: str, panels: list[dict[str, Any]], columns: int, *, reference_x: float | None = None) -> None:
    cell_w, cell_h = 620, 330
    rows = math.ceil(len(panels) / columns)
    width, height = columns * cell_w, rows * cell_h + 54
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172033}.title{font-size:21px;font-weight:700}.panel-title{font-size:15px;font-weight:600}.tick{font-size:10px;fill:#475569}.legend{font-size:10px}.axis-label{font-size:11px}.grid{stroke:#dbe3ec;stroke-width:1}.axis{stroke:#334155;stroke-width:1}.reference-v{stroke:#0f172a;stroke-width:1.3;stroke-dasharray:3 5}</style>',
        f'<text x="24" y="31" class="title">{html.escape(title)}</text>',
    ]
    for index, panel in enumerate(panels):
        col, row = index % columns, index // columns
        x, y = col * cell_w + 2, row * cell_h + 48
        body.append(svg_panel(
            x=x, y=y, width=cell_w - 8, height=cell_h - 10,
            x_range=panel["x_range"], reference_x=reference_x, **{k: v for k, v in panel.items() if k != "x_range"},
        ))
    body.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(body), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_manifest", type=Path)
    parser.add_argument("--e27-monitor-dir", type=Path)
    parser.add_argument("--figure-dir", type=Path)
    args = parser.parse_args()
    manifest = json.loads(args.run_manifest.read_text(encoding="utf-8"))
    output_root = Path(manifest["local_output_root"])
    histories = load_report_histories(output_root)
    transcript_path = output_root / "transcript-native-solve.txt"
    transcript = parse_transcript(transcript_path)
    output_csv = output_root / "e281-per-iteration-history.csv"
    coordinates = write_joined_csv(output_csv, histories, transcript)
    if len(coordinates) < 3001 or coordinates[0] != 5586 or coordinates[-1] != 8586:
        raise ValueError(f"Expected all 3,001 E2.81 report coordinates 5586..8586; got {len(coordinates)} ({coordinates[0]}..{coordinates[-1]})")

    descriptors = [
        ("film-mass-total", "Film mass", "kg", "#1d4ed8", 1.0),
        ("thickness-max", "Maximum film thickness", "mm", "#dc2626", 1000.0),
        ("thickness-awavg", "Area-weighted film thickness", "mm", "#ea580c", 1000.0),
        ("velocity-mag-awavg", "Area-weighted film speed", "m/s", "#059669", 1.0),
        ("velocity-mag-max", "Maximum film speed", "m/s", "#7c3aed", 1.0),
        ("wet-area", "Film Coverage area", "m2", "#0891b2", 1.0),
        ("courant-max", "Maximum film Courant", "-", "#9333ea", 1.0),
    ]
    series_by_metric: dict[str, dict[str, Any]] = {}
    matched: dict[str, Any] = {}
    for suffix, label, unit, color, scale in descriptors:
        name, record = history_for(histories, suffix)
        rows = history_rows(record)
        series_by_metric[suffix] = {"x": sorted(rows), "y": [rows[n] * scale for n in sorted(rows)], "label": "E2.81", "color": color}
        matched_value = rows.get(E27_NATIVE_ENDPOINT)
        e27_value = read_e27_monitor(args.e27_monitor_dir, suffix) if args.e27_monitor_dir else None
        matched_value_in_display_units = None if matched_value is None else matched_value * scale
        e27_value_in_display_units = None if e27_value is None else e27_value * scale
        matched[suffix] = {
            "label": label,
            "unit": unit,
            "e2_81_native_8586": matched_value_in_display_units,
            "e2_7_native_8586": e27_value_in_display_units,
            "e2_81_minus_e2_7": None if matched_value_in_display_units is None or e27_value_in_display_units is None else matched_value_in_display_units - e27_value_in_display_units,
            "e2_81_scale_factor": None if matched_value_in_display_units is None or e27_value_in_display_units in (None, 0) else matched_value_in_display_units / e27_value_in_display_units,
        }
        if e27_value is not None:
            series_by_metric[suffix]["reference_line"] = {"value": e27_value * scale, "color": "#334155", "label": "E2.7 at 8586"}

    first_time = transcript[min(n for n in transcript if "film_time_s" in transcript[n])]
    time_origin = first_time["film_time_s"] - first_time["film_timestep_s"]
    time_rows = sorted((n, item["film_time_s"] - time_origin) for n, item in transcript.items() if "film_time_s" in item)
    e27_time = [(n, (n - 5586) * E27_FIXED_FILM_DT_S) for n in sorted(transcript) if n >= 5586]

    def response_panel(suffix: str) -> dict[str, Any]:
        item = series_by_metric[suffix]
        return {
            "title": next(desc[1] for desc in descriptors if desc[0] == suffix),
            "x_label": "Native iteration",
            "y_label": next(desc[2] for desc in descriptors if desc[0] == suffix),
            "x_range": (5586, 8586),
            "series": [{"x": item["x"], "y": item["y"], "label": "E2.81", "color": item["color"]}],
            "reference_lines": [item["reference_line"]] if "reference_line" in item else [],
        }

    response_panels = [response_panel(key) for key in ("film-mass-total", "thickness-max", "thickness-awavg", "velocity-mag-awavg", "wet-area", "courant-max")]
    response_panels.append({
        "title": "EWF film time advanced from the native-5586 start",
        "x_label": "Native iteration", "y_label": "Film time increment (s)", "x_range": (5586, 8586),
        "series": [{"x": [n for n, _ in time_rows], "y": [v for _, v in time_rows], "label": "E2.81", "color": "#0891b2"},
                   {"x": [n for n, _ in e27_time], "y": [v for _, v in e27_time], "label": "E2.7 fixed step", "color": "#334155", "dash": True}],
    })
    figure_dir = args.figure_dir or (Path(__file__).resolve().parents[3] / "Project/experiments/phase-07-2a-wall-liquid-routing/ewf-family/e2.81/figures")
    write_svg(figure_dir / "film-response.svg", "E2.81 fast-time film response", response_panels, 2, reference_x=E27_NATIVE_ENDPOINT)

    area_path = output_root / "checkpoint-area" / "checkpoint-thickness-area.csv"
    if not area_path.is_file():
        raise FileNotFoundError(f"Missing checkpoint thickness-area table: {area_path}")
    with area_path.open(newline="", encoding="utf-8") as handle:
        area_rows = list(csv.DictReader(handle))
    area_rows = sorted(area_rows, key=lambda row: int(row["native_iteration"]))
    e281_area_endpoint = next(
        (row for row in area_rows if int(row["native_iteration"]) == E27_NATIVE_ENDPOINT),
        None,
    )
    if e281_area_endpoint is None:
        raise ValueError(f"Thickness-area table has no native-{E27_NATIVE_ENDPOINT} E2.81 row")
    e27_area_path = output_root / "e27-matched-thickness-area.json"
    area_comparison: dict[str, Any] = {}
    if e27_area_path.is_file():
        e27_area = json.loads(e27_area_path.read_text(encoding="utf-8"))["measurements"]
        area_fields = [
            "wet_area_m2_film_coverage",
            *(f"area_at_or_above_{value:g}_mm_m2" for value in (0.01, 0.05, 0.10, 0.25, 0.50)),
            "area_0_to_0.01_mm_m2",
            "area_0.01_to_0.05_mm_m2",
            "area_0.05_to_0.1_mm_m2",
            "area_0.1_to_0.25_mm_m2",
            "area_0.25_to_0.5_mm_m2",
            "area_0.5_to_inf_mm_m2",
        ]
        area_comparison = {
            key: {
                "e2_7_native_8586_m2": float(e27_area[key]),
                "e2_81_native_8586_m2": float(e281_area_endpoint[key]),
                "e2_81_minus_e2_7_m2": float(e281_area_endpoint[key]) - float(e27_area[key]),
            }
            for key in area_fields
        }
    area_x = [int(row["native_iteration"]) for row in area_rows]
    thresholds = (0.01, 0.05, 0.10, 0.25, 0.50)
    area_colors = ("#1d4ed8", "#059669", "#ea580c", "#dc2626", "#7c3aed")
    cumulative_series = []
    for threshold, color in zip(thresholds, area_colors):
        field = f"area_at_or_above_{threshold:g}_mm_m2"
        cumulative_series.append({"x": area_x, "y": [float(row[field]) for row in area_rows], "label": f">= {threshold:g} mm", "color": color})
    bands = ((0.0, 0.01), (0.01, 0.05), (0.05, 0.10), (0.10, 0.25), (0.25, 0.50), (0.50, math.inf))
    band_colors = ("#94a3b8", "#38bdf8", "#34d399", "#fbbf24", "#fb7185", "#8b5cf6")
    band_series = []
    for (lower, upper), color in zip(bands, band_colors):
        upper_name = "inf" if math.isinf(upper) else f"{upper:g}"
        field = f"area_{lower:g}_to_{upper_name}_mm_m2"
        band_series.append({"x": area_x, "y": [float(row[field]) for row in area_rows], "label": f"{lower:g} to {upper_name} mm", "color": color})
    write_svg(figure_dir / "wet-area-by-thickness.svg", "E2.81 active-wall area by film thickness", [
        {"title": "Cumulative wall area above thickness threshold", "x_label": "Native iteration", "y_label": "Area (m2)", "x_range": (5586, 8586), "series": cumulative_series},
        {"title": "Disjoint wall-area thickness bands", "x_label": "Native iteration", "y_label": "Area (m2)", "x_range": (5586, 8586), "series": band_series},
    ], 2, reference_x=E27_NATIVE_ENDPOINT)

    health_x = sorted(n for n, item in transcript.items() if any(key in item for key in ("ewf_h_residual_max", "film_courant_max")))
    health_panels = [
        {"title": "EWF sub-iteration residual maxima per native step", "x_label": "Native iteration", "y_label": "Absolute residual (log scale)", "x_range": (5586, 8586), "y_scale": "log", "series": [
            {"x": health_x, "y": [transcript[n].get(f"ewf_{letter}_residual_max", 0.0) for n in health_x], "label": letter, "color": color}
            for letter, color in (("h", "#1d4ed8"), ("u", "#dc2626"), ("v", "#059669"))]},
        {"title": "Maximum film Courant", "x_label": "Native iteration", "y_label": "Courant", "x_range": (5586, 8586), "series": [{"x": health_x, "y": [transcript[n].get("film_courant_max", 0.0) for n in health_x], "label": "E2.81", "color": "#7c3aed"}], "reference_lines": [{"value": 0.4, "label": "configured max 0.4", "color": "#334155"}]},
        {"title": "Adaptive film timestep", "x_label": "Native iteration", "y_label": "Timestep (s)", "x_range": (5586, 8586), "series": [{"x": health_x, "y": [transcript[n].get("film_timestep_s", 0.0) for n in health_x], "label": "E2.81", "color": "#0891b2"}, {"x": health_x, "y": [E27_FIXED_FILM_DT_S for _ in health_x], "label": "E2.7 fixed", "color": "#334155", "dash": True}]},
        {"title": "Film outflow monitor", "x_label": "Native iteration", "y_label": "Reported mass outflow (kg)", "x_range": (5586, 8586), "series": [{"x": history_rows(history_for(histories, "outflow-mass-total")[1]).keys(), "y": history_rows(history_for(histories, "outflow-mass-total")[1]).values(), "label": "E2.81", "color": "#ea580c"}]},
    ]
    write_svg(figure_dir / "ewf-numerical-health.svg", "E2.81 EWF numerical health and film transfer", health_panels, 2, reference_x=E27_NATIVE_ENDPOINT)

    residual_steps = sorted(
        (n, item)
        for n, item in transcript.items()
        if "film_time_s" in item and "ewf_residual_rows" in item
    )
    def residual_segment(label: str, rows: list[tuple[int, dict[str, float]]], stop: float, cap: int) -> dict[str, Any]:
        complete = [
            (n, item)
            for n, item in rows
            if all(f"ewf_{letter}_residual_last" in item for letter in "huv")
        ]
        reached = [
            n for n, item in complete
            if all(item[f"ewf_{letter}_residual_last"] <= stop for letter in "huv")
        ]
        at_cap = [n for n, item in rows if item.get("ewf_residual_rows", 0.0) >= cap]
        return {
            "segment": label,
            "native_first": rows[0][0] if rows else None,
            "native_last": rows[-1][0] if rows else None,
            "steps_with_residuals": len(rows),
            "steps_with_all_three_last_residuals_at_or_below_stop": len(reached),
            "configured_stop": stop,
            "maximum_subiterations": cap,
            "steps_at_or_above_subiteration_cap": len(at_cap),
            "max_abs_residuals_h_u_v": {
                letter: max((item.get(f"ewf_{letter}_residual_max", 0.0) for _, item in rows), default=None)
                for letter in "huv"
            },
            "largest_residual_step_native": max(
                rows,
                key=lambda row: max(row[1].get(f"ewf_{letter}_residual_max", 0.0) for letter in "huv"),
            )[0] if rows else None,
        }

    residual_health = {
        "interpretation": "Per-step last captured h/u/v values are compared with that segment's configured stop value; this is not a global flow-convergence test.",
        "adaptive_segment": residual_segment("adaptive 5587-8586", residual_steps, 5e-4, 4),
    }

    summary = {
        "status": "ANALYZED",
        "experiment": "E2.81",
        "native_coordinates": {"count": len(coordinates), "first": coordinates[0], "last": coordinates[-1]},
        "matched_native_8586": matched,
        "matched_thickness_area_native_8586": area_comparison,
        "film_time": {
            "initial_from_first_tui_step_s": time_origin,
            "final_tui_time_s": transcript[max(n for n, item in transcript.items() if "film_time_s" in item)]["film_time_s"],
            "increment_from_native_5586_s": time_rows[-1][1],
            "e2_7_fixed_step_increment_s": (E27_NATIVE_ENDPOINT - 5586) * E27_FIXED_FILM_DT_S,
            "increment_ratio_vs_e2_7_fixed": time_rows[-1][1] / ((E27_NATIVE_ENDPOINT - 5586) * E27_FIXED_FILM_DT_S),
        },
        "ewf_subiteration_residual_health": residual_health,
        "figures": [str(figure_dir / name) for name in ("film-response.svg", "wet-area-by-thickness.svg", "ewf-numerical-health.svg")],
        "all_iteration_history_csv": str(output_csv),
        "threshold_area_csv": str(area_path),
    }
    summary_path = output_root / "e281-response-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

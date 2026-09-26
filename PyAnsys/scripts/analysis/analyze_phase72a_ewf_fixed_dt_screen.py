"""Compare the fixed-step EWF screen against E2.7 over native iterations 5586-8586."""
from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze_phase72a_e281_response import history_rows, parse_transcript  # noqa: E402

NATIVE_FIRST = 5586
NATIVE_LAST = 8586
E27_DT = 1.0e-5
E27_MONITORS = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\E2.7\20260923T071523Z\monitors")
CASES = {
    "E2.82": ("20260926T134145Z", 1.25e-5),
    "E2.83": ("20260926T144249Z", 1.50e-5),
    "E2.84": ("20260926T154347Z", 1.75e-5),
}
METRICS = {
    "courant-max": ("EWF max Courant", "-", 1.0),
    "film-mass-total": ("Film mass", "kg", 1.0),
    "thickness-max": ("Maximum film thickness", "mm", 1000.0),
    "thickness-awavg": ("Area weighted film thickness", "mm", 1000.0),
    "velocity-mag-awavg": ("Area weighted film speed", "m/s", 1.0),
    "velocity-mag-max": ("Maximum film speed", "m/s", 1.0),
}


def load_case(case: str, stamp: str) -> tuple[dict[str, dict[int, float]], dict[int, dict[str, float]], dict]:
    root = REPO / "output" / f"phase72a_ewf_fixed_dt_{case.lower()}_{stamp}"
    payload = json.loads((root / "report-histories.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "run-manifest.json").read_text(encoding="utf-8-sig"))
    selected: dict[str, dict[int, float]] = {}
    for suffix in METRICS:
        matches = [
            record for name, record in payload.items()
            if name.casefold().endswith(f"ewf-{suffix}")
            or str(record.get("definition_name", "")).casefold().endswith(f"ewf-{suffix}")
        ]
        if len(matches) != 1:
            raise ValueError(f"{case}: expected one EWF {suffix} history, got {len(matches)}")
        selected[suffix] = history_rows(matches[0])
    transcript = parse_transcript(root / "transcript-native-solve.txt")
    return selected, transcript, manifest


def load_e27(suffix: str) -> dict[int, float]:
    expected = f"p72a-e2.7-ewf-{suffix}.out".casefold()
    matches = [path for path in E27_MONITORS.iterdir() if path.name.casefold().endswith(expected)]
    if len(matches) != 1:
        raise ValueError(f"E2.7: expected one monitor {expected}, got {[p.name for p in matches]}")
    rows: dict[int, float] = {}
    for line in matches[0].read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                rows[int(parts[0])] = float(parts[1])
            except ValueError:
                continue
    return {n: v for n, v in rows.items() if NATIVE_FIRST <= n <= NATIVE_LAST}


def argmax(rows: dict[int, float]) -> tuple[int, float]:
    finite = [(n, v) for n, v in rows.items() if math.isfinite(v)]
    if not finite:
        raise ValueError("No finite values in a required history")
    return max(finite, key=lambda item: item[1])


def svg_plot(path: Path, curves: list[dict], title: str, y_label: str, log: bool = False) -> str:
    width, height = 1120, 790
    left, right, top, bottom = 86, 1070, 70, 682
    colors = {"E2.7": "#334155", "E2.82": "#0284c7", "E2.83": "#dc2626", "E2.84": "#7c3aed"}
    values = [v for c in curves for v in c["values"] if math.isfinite(v) and (not log or v > 0)]
    if log:
        lo = math.floor(math.log10(min(values)))
        hi = math.ceil(math.log10(max(values)))
        if hi <= lo:
            hi = lo + 1
        ymin, ymax = 10.0**lo, 10.0**hi
        fy = lambda v: bottom - (math.log10(max(v, ymin)) - lo) / (hi - lo) * (bottom - top)
        ticks = [(10.0**i, f"1e{i}") for i in range(lo, hi + 1)]
    else:
        ymin, ymax = min(0.0, min(values)), max(values)
        if math.isclose(ymin, ymax):
            ymax = ymin + 1.0
        pad = (ymax - ymin) * 0.06
        ymin -= pad
        ymax += pad
        fy = lambda v: bottom - (v - ymin) / (ymax - ymin) * (bottom - top)
        ticks = [(ymin + i * (ymax - ymin) / 5, f"{ymin + i * (ymax - ymin) / 5:.3g}") for i in range(6)]
    x_min = min(x for c in curves for x in c["x"])
    x_max = max(x for c in curves for x in c["x"])
    fx = lambda value: left + (value - x_min) / (x_max - x_min) * (right - left)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#0f172a}.grid{stroke:#e2e8f0}.axis{stroke:#475569}.tick{font-size:12px}.title{font-size:21px;font-weight:600}.legend{font-size:14px}</style>',
             f'<text x="{left}" y="35" class="title">{title}</text>']
    for val, label in ticks:
        y = fy(val)
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'<text x="{left-9}" y="{y+4:.1f}" class="tick" text-anchor="end">{label}</text>')
    for i in range(5):
        value = x_min + i * (x_max - x_min) / 4
        x = fx(value)
        parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="grid"/>')
        parts.append(f'<text x="{x:.1f}" y="{bottom+22}" class="tick" text-anchor="middle">{value:.4g}</text>')
    parts.extend([f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>',
                  f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>',
                  f'<text x="26" y="{(top+bottom)/2}" class="tick" transform="rotate(-90 26 {(top+bottom)/2})" text-anchor="middle">{y_label}</text>',
                  f'<text x="{(left+right)/2}" y="{bottom+50}" class="tick" text-anchor="middle">Film elapsed time from native 5586 (s)</text>'])
    for c in curves:
        pts = " ".join(f"{fx(x):.1f},{fy(v):.1f}" for x, v in zip(c["x"], c["values"]) if math.isfinite(v) and (not log or v > 0))
        color = colors[c["label"]]
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>')
    for i, c in enumerate(curves):
        x = left + i * 175
        color = colors[c["label"]]
        parts.append(f'<line x1="{x}" y1="{height-25}" x2="{x+25}" y2="{height-25}" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<text x="{x+32}" y="{height-20}" class="legend">{c["label"]}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")
    return str(path)


def main() -> None:
    output = REPO / "output" / "phase72a_ewf_fixed_dt_comparison_20260927"
    output.mkdir(parents=True, exist_ok=True)
    data: dict[str, dict] = {}
    e27_rows = {suffix: load_e27(suffix) for suffix in METRICS}
    data["E2.7"] = {"histories": e27_rows, "transcript": {}, "dt": E27_DT}
    for case, (stamp, dt) in CASES.items():
        histories, transcript, manifest = load_case(case, stamp)
        if manifest.get("status") != "COMPLETE" or manifest.get("last_native_iteration") != NATIVE_LAST:
            raise ValueError(f"{case} manifest is not a complete native-8586 run")
        data[case] = {"histories": histories, "transcript": transcript, "dt": dt, "manifest": manifest}

    coordinates = list(range(NATIVE_FIRST, NATIVE_LAST + 1))
    csv_path = output / "ewf-timestep-screen.csv"
    columns = ["native_iteration"] + [f"{case}_film_elapsed_time_s" for case in data] + [f"{case}_{suffix}" for case in data for suffix in METRICS]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for n in coordinates:
            row = {"native_iteration": n}
            for case, item in data.items():
                row[f"{case}_film_elapsed_time_s"] = (n - NATIVE_FIRST) * item["dt"]
                for suffix, (_, _, scale) in METRICS.items():
                    row[f"{case}_{suffix}"] = item["histories"][suffix].get(n, "")
            writer.writerow(row)

    summary: dict[str, dict] = {}
    for case, item in data.items():
        metrics: dict[str, dict] = {}
        for suffix, (label, unit, scale) in METRICS.items():
            rows = item["histories"][suffix]
            interval = {n: v for n, v in rows.items() if NATIVE_FIRST <= n <= NATIVE_LAST}
            peak_n, peak_v = argmax(interval)
            start = interval[NATIVE_FIRST]
            end = interval[NATIVE_LAST]
            metrics[suffix] = {
                "label": label, "unit": unit, "native_5586": start * scale,
                "native_8586": end * scale, "interval_peak": peak_v * scale,
                "interval_peak_native_iteration": peak_n,
                "change_5586_to_8586": (end - start) * scale,
            }
        residual = item["transcript"]
        residual_rows = [(n, r) for n, r in residual.items() if NATIVE_FIRST < n <= NATIVE_LAST and "ewf_h_residual_max" in r]
        resid_peaks = {
            letter: max(((r.get(f"ewf_{letter}_residual_max", 0.0), n) for n, r in residual_rows), default=(None, None))
            for letter in "huv"
        }
        same_time_step = round(0.03 / item["dt"])
        same_time_native = NATIVE_FIRST + same_time_step
        metrics["matched_physical_time_0.03s"] = {
            "native_iteration": same_time_native,
            "actual_elapsed_time_s": same_time_step * item["dt"],
            "metrics": {
                suffix: item["histories"][suffix][same_time_native] * scale
                for suffix, (_, _, scale) in METRICS.items()
            },
        }
        metrics["stability"] = {
            "max_abs_ewf_subiteration_residuals_h_u_v": {letter: {"value": pair[0], "native_iteration": pair[1]} for letter, pair in resid_peaks.items()},
            "steps_with_all_ewf_last_residuals_at_or_below_1e-5": sum(
                all(r.get(f"ewf_{letter}_residual_last", math.inf) <= 1e-5 for letter in "huv") for _, r in residual_rows
            ) if case != "E2.7" else None,
            "captured_ewf_residual_steps": len(residual_rows),
            "final_film_elapsed_time_s": max((r.get("film_time_s", 0.0) for r in residual.values()), default=None),
            "requested_fixed_timestep_s": item["dt"],
            "event_flags": item["manifest"].get("event_flags") if case != "E2.7" else None,
        }
        summary[case] = metrics

    figure_curves = {}
    for suffix in ("film-mass-total", "velocity-mag-awavg", "courant-max", "thickness-max"):
        curves = []
        for case, item in data.items():
            unit_scale = METRICS[suffix][2]
            rows = item["histories"][suffix]
            curves.append({"label": case, "x": [(n - NATIVE_FIRST) * item["dt"] for n in coordinates], "values": [rows[n] * unit_scale for n in coordinates]})
        filename = f"{suffix}.svg"
        figure_curves[suffix] = svg_plot(output / filename, curves, METRICS[suffix][0], METRICS[suffix][1], log=(suffix in ("courant-max", "film-mass-total", "velocity-mag-awavg", "thickness-max")))
    summary["metadata"] = {
        "native_interval": [NATIVE_FIRST, NATIVE_LAST], "iterations_per_run": NATIVE_LAST - NATIVE_FIRST,
        "e27_reference_fixed_dt_s": E27_DT,
        "figure_paths": figure_curves, "joined_history_csv": str(csv_path),
        "interpretation_limit": "Endpoint growth and numerical excursions are compared; completing 3000 iterations is not evidence of physical or time-step convergence.",
    }
    (output / "ewf-timestep-screen-summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

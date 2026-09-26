"""Plot selected phase-2 steamoutlet flux histories for E2.7 through E2.84."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "output" / "phase72a_ewf_fixed_dt_comparison_20260927"
FIRST, LAST = 5586, 8586
METRIC = "v2-flux-phase2-steamoutlet"
E27_MONITORS = Path(r"C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\E2.7\20260923T071523Z\monitors")
CASE_FILES = {
    "E2.8": REPO / "output" / "phase72a_ewf_direct_e28_20260926T010700Z" / "e28-per-iteration-history.csv",
    "E2.81": REPO / "output" / "phase72a_ewf_direct_e281_20260926T052048Z" / "e281-per-iteration-history.csv",
}
FIXED_CASES = {
    "E2.82": "phase72a_ewf_fixed_dt_e2.82_20260926T134145Z",
    "E2.83": "phase72a_ewf_fixed_dt_e2.83_20260926T144249Z",
    "E2.84": "phase72a_ewf_fixed_dt_e2.84_20260926T154347Z",
}
COLORS = {
    "E2.7": "#111827", "E2.8": "#ea580c", "E2.81": "#7c3aed",
    "E2.82": "#0284c7", "E2.83": "#059669", "E2.84": "#dc2626",
}
DASHES = {"E2.7": "", "E2.8": "7 3", "E2.81": "2 3", "E2.82": "9 3", "E2.83": "4 2", "E2.84": "11 3 2 3"}


def read_plain_monitor(directory: Path, report: str) -> dict[int, float]:
    wanted = report.casefold()
    matches = [p for p in directory.iterdir() if p.name.casefold().endswith(wanted)]
    # The unsuffixed E2.7 file is the original native-5586 through native-8586 history.
    matches = [p for p in matches if "_8587" not in p.name.casefold() and "_1_" not in p.name.casefold()]
    if len(matches) != 1:
        raise ValueError(f"Expected one base monitor ending {report}; found {[p.name for p in matches]}")
    rows: dict[int, float] = {}
    for line in matches[0].read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if len(fields) >= 2:
            try:
                rows[int(fields[0])] = float(fields[1])
            except ValueError:
                continue
    return {n: value for n, value in rows.items() if FIRST <= n <= LAST}


def read_selected_csv(path: Path) -> dict[int, float]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if "native_iteration" not in (reader.fieldnames or []) or METRIC not in (reader.fieldnames or []):
            raise ValueError(f"{path} does not contain {METRIC} on native_iteration")
        rows = {
            int(float(row["native_iteration"])): float(row[METRIC])
            for row in reader if row.get("native_iteration") and row.get(METRIC)
        }
    return {n: value for n, value in rows.items() if FIRST <= n <= LAST}


def read_fixed_histories() -> dict[str, dict[int, float]]:
    result: dict[str, dict[int, float]] = {}
    for case, folder in FIXED_CASES.items():
        path = REPO / "output" / folder / "report-histories.json"
        histories = json.loads(path.read_text(encoding="utf-8"))
        record = histories.get(METRIC)
        if not record:
            raise ValueError(f"{path} is missing report history {METRIC}")
        result[case] = {int(n): float(v) for n, v in zip(record["iterations"], record["values"])}
    return result


def plot_svg(path: Path, series: dict[str, dict[int, float]]) -> None:
    width, height = 1200, 790
    left, right = 104, 1140
    top1, bottom1 = 88, 392
    top2, bottom2 = 493, 692
    coords = list(range(FIRST, LAST + 1))
    all_values = [series[case][n] for case in series for n in coords]
    y1_min, y1_max = -25.5, -0.5
    diff = {case: {n: series[case][n] - series["E2.7"][n] for n in coords} for case in series}
    diff_values = [value for rows in diff.values() for value in rows.values() if math.isfinite(value)]
    delta = max(0.01, max(abs(v) for v in diff_values))
    y2_min, y2_max = -delta * 1.2, delta * 1.2
    fx = lambda n: left + (n - FIRST) / (LAST - FIRST) * (right - left)
    fy1 = lambda v: bottom1 - (v - y1_min) / (y1_max - y1_min) * (bottom1 - top1)
    fy2 = lambda v: bottom2 - (v - y2_min) / (y2_max - y2_min) * (bottom2 - top2)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#0f172a}.grid{stroke:#e2e8f0}.axis{stroke:#475569}.tick{font-size:12px}.title{font-size:21px;font-weight:600}.subtitle{font-size:14px}.legend{font-size:14px}</style>',
        '<text x="104" y="32" class="title">Phase-2 signed mass flux at steamoutlet — E2.7 to E2.84</text>',
        '<text x="104" y="57" class="subtitle">Negative values indicate outflow. Native iteration 5586–8586; E2.8 uses its selected trajectory with fixed-step recovery after native 7000.</text>',
        '<text x="104" y="78" class="subtitle">Top: absolute flux history (kg/s). Bottom: difference from E2.7 at each native iteration (kg/s).</text>',
    ]

    def axes(top: float, bottom: float, ymin: float, ymax: float, ticks: int, label: str, map_y):
        for i in range(ticks + 1):
            val = ymin + (ymax - ymin) * i / ticks
            y = map_y(val)
            parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" class="grid"/>')
            parts.append(f'<text x="{left-9}" y="{y+4:.1f}" class="tick" text-anchor="end">{val:.3g}</text>')
        for i in range(5):
            n = FIRST + (LAST - FIRST) * i / 4
            x = fx(n)
            parts.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" class="grid"/>')
            parts.append(f'<text x="{x:.1f}" y="{bottom+18}" class="tick" text-anchor="middle">{n:.0f}</text>')
        parts.extend([
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" class="axis"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>',
            f'<text x="25" y="{(top+bottom)/2}" class="tick" transform="rotate(-90 25 {(top+bottom)/2})" text-anchor="middle">{label}</text>',
            f'<text x="{(left+right)/2}" y="{bottom+38}" class="tick" text-anchor="middle">Native iteration</text>',
        ])

    axes(top1, bottom1, y1_min, y1_max, 5, "Signed phase-2 mass flux (kg/s)", fy1)
    axes(top2, bottom2, y2_min, y2_max, 4, "Difference from E2.7 (kg/s)", fy2)
    # The six selected trajectories overlap closely, so dashed styles distinguish them.
    for case, rows in series.items():
        points = " ".join(f"{fx(n):.1f},{fy1(rows[n]):.1f}" for n in coords)
        dash = f' stroke-dasharray="{DASHES[case]}"' if DASHES[case] else ""
        parts.append(f'<polyline points="{points}" fill="none" stroke="{COLORS[case]}" stroke-width="2"{dash}/>')
    zero_y = fy2(0.0)
    parts.append(f'<line x1="{left}" y1="{zero_y:.1f}" x2="{right}" y2="{zero_y:.1f}" stroke="#64748b" stroke-width="1.5" stroke-dasharray="5 4"/>')
    for case, rows in diff.items():
        points = " ".join(f"{fx(n):.1f},{fy2(rows[n]):.1f}" for n in coords)
        dash = f' stroke-dasharray="{DASHES[case]}"' if DASHES[case] else ""
        parts.append(f'<polyline points="{points}" fill="none" stroke="{COLORS[case]}" stroke-width="2"{dash}/>')
    for i, case in enumerate(series):
        col, row = i % 3, i // 3
        x, y = left + col * 300, 747 + row * 22
        dash = f' stroke-dasharray="{DASHES[case]}"' if DASHES[case] else ""
        parts.append(f'<line x1="{x}" y1="{y}" x2="{x+25}" y2="{y}" stroke="{COLORS[case]}" stroke-width="3"{dash}/>')
        parts.append(f'<text x="{x+32}" y="{y+5}" class="legend">{case}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    series: dict[str, dict[int, float]] = {"E2.7": read_plain_monitor(E27_MONITORS, f"{METRIC}.out")}
    series.update({case: read_selected_csv(path) for case, path in CASE_FILES.items()})
    series.update(read_fixed_histories())
    coords = set(range(FIRST, LAST + 1))
    for case, rows in series.items():
        missing = sorted(coords - set(rows))
        if missing:
            raise ValueError(f"{case} is missing {len(missing)} native flux points; first missing {missing[:5]}")

    csv_path = OUTPUT / "phase2-steamoutlet-flux-e2.7-to-e2.84.csv"
    names = list(series)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["native_iteration", *names])
        writer.writeheader()
        for n in range(FIRST, LAST + 1):
            writer.writerow({"native_iteration": n, **{case: series[case][n] for case in names}})

    baseline = series["E2.7"]
    stats = {}
    for case, rows in series.items():
        values = [rows[n] for n in range(FIRST, LAST + 1)]
        differences = {n: rows[n] - baseline[n] for n in range(FIRST, LAST + 1)}
        max_native = max(differences, key=lambda n: abs(differences[n]))
        terminal = [rows[n] for n in range(7590, 8581)]
        stats[case] = {
            "start_native_5586_kg_s": rows[FIRST], "end_native_8586_kg_s": rows[LAST],
            "mean_native_5586_8586_kg_s": sum(values) / len(values),
            "mean_native_7590_8580_kg_s": sum(terminal) / len(terminal),
            "minimum_kg_s": min(values), "maximum_kg_s": max(values),
            "endpoint_delta_from_e2_7_kg_s": rows[LAST] - baseline[LAST],
            "max_abs_delta_from_e2_7_kg_s": abs(differences[max_native]),
            "max_abs_delta_native_iteration": max_native,
        }
    summary = {
        "status": "ANALYZED", "metric": METRIC, "units": "kg/s",
        "sign_convention": "Negative values indicate outflow from the phase-2 steamoutlet boundary.",
        "native_interval": [FIRST, LAST], "points_per_case": LAST - FIRST + 1,
        "case_provenance": {
            "E2.8": "Selected trajectory, adaptive prefix followed by fixed-step recovery from native 7000 after the adaptive branch diverged.",
            "E2.81": "Selected complete 3000-iteration adaptive trajectory.",
            "E2.82-E2.84": "Independent complete fixed-step trajectories from common native-5586 parent.",
        },
        "cases": stats,
        "plot": str(OUTPUT / "phase2-steamoutlet-flux-e2.7-to-e2.84.svg"),
        "csv": str(csv_path),
        "interpretation_limit": "Bulk-flow flux is compared as recorded on each selected trajectory; a phase-2 steamoutlet flux change alone does not establish wall-film carryover or a film-transport mechanism.",
    }
    summary_path = OUTPUT / "phase2-steamoutlet-flux-e2.7-to-e2.84-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    plot_svg(OUTPUT / "phase2-steamoutlet-flux-e2.7-to-e2.84.svg", series)
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()

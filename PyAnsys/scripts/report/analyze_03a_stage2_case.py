#!/usr/bin/env python3
"""Build durable, branch-scoped Stage-2 reporting evidence.

The script reads already-recorded JSON artifacts only.  It does not connect to
Fluent and does not issue solver commands.  Run it one branch at a time so the
corresponding case report can be written and reviewed before moving on.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import math
import statistics
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
PYANSYS_ROOT = REPOSITORY_ROOT / "PyAnsys"
STAGE1_RESIDUAL = PYANSYS_ROOT / "output/post_simulation_analysis/03a_08b_parity_full_geometry_iter1000_20260817T110345Z-residual-check.json"
STAGE1_FLUX = PYANSYS_ROOT / "output/post_simulation_analysis/03a_08b_parity_full_geometry_iter1000_20260817T110345Z-flux-check.json"
INITIAL_DIR = PYANSYS_ROOT / "output/03a_stage2/20260817T125355Z/run/post_simulation_analysis"
EXTENSION_DIR = PYANSYS_ROOT / "output/03a_stage2/20260817T132736Z/extension-700/post_simulation_analysis"
STAGE2_MANIFEST = PYANSYS_ROOT / "output/03a_stage2/20260817T124452Z/03a_stage2_children.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def residual_points(payload: dict[str, Any], minimum_iteration: float = -math.inf) -> dict[str, list[tuple[float, float]]]:
    x_values = [number(value) for value in payload.get("iterations", [])]
    series = payload.get("series", {})
    output: dict[str, list[tuple[float, float]]] = {}
    if not isinstance(series, dict):
        return output
    for name, values in series.items():
        points: list[tuple[float, float]] = []
        for x, value in zip(x_values, values):
            y = number(value)
            if x is not None and y is not None and x > minimum_iteration and y > 0:
                points.append((x, y))
        output[str(name)] = points
    return output


def merge_series(chunks: list[dict[str, list[tuple[float, float]]]]) -> dict[str, list[tuple[float, float]]]:
    names = sorted({name for chunk in chunks for name in chunk})
    merged: dict[str, list[tuple[float, float]]] = {}
    for name in names:
        by_x: dict[float, float] = {}
        for chunk in chunks:
            for x, y in chunk.get(name, []):
                by_x[x] = y
        merged[name] = sorted(by_x.items())
    return merged


def phase_paths(branch: str) -> list[tuple[str, Path, float]]:
    if branch == "N5":
        return [
            ("Stage 1 canonical", STAGE1_RESIDUAL, -math.inf),
            ("N5 standard bootstrap", INITIAL_DIR / "N5-standard-bootstrap-residual-check.json", 1000.0),
            ("N5 restored RNG return", INITIAL_DIR / "N5-rng-return-residual-check.json", 1500.0),
            ("N5 RNG +700 continuation", EXTENSION_DIR / "N5-extension-700-residual-check.json", 1800.0),
        ]
    return [
        ("Stage 1 canonical", STAGE1_RESIDUAL, -math.inf),
        (f"{branch} initial +300", INITIAL_DIR / f"{branch}-initial-screen-residual-check.json", 1000.0),
        (f"{branch} +700 continuation", EXTENSION_DIR / f"{branch}-extension-700-residual-check.json", 1300.0),
    ]


def flux_paths(branch: str) -> list[tuple[str, Path]]:
    if branch == "N5":
        return [
            ("Stage 1 canonical", STAGE1_FLUX),
            ("N5 standard bootstrap", INITIAL_DIR / "N5-standard-bootstrap-flux-check.json"),
            ("N5 restored RNG return", INITIAL_DIR / "N5-rng-return-flux-check.json"),
            ("N5 RNG +700 continuation", EXTENSION_DIR / "N5-extension-700-flux-check.json"),
        ]
    return [
        ("Stage 1 canonical", STAGE1_FLUX),
        (f"{branch} initial +300", INITIAL_DIR / f"{branch}-initial-screen-flux-check.json"),
        (f"{branch} +700 continuation", EXTENSION_DIR / f"{branch}-extension-700-flux-check.json"),
    ]


def branch_definition(branch: str) -> dict[str, Any]:
    manifest = read_json(STAGE2_MANIFEST)
    for child in manifest.get("children", []):
        if child.get("branch") == branch:
            return child.get("branch_definition", {})
    return {}


def residual_summary(points: dict[str, list[tuple[float, float]]]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for name, values in sorted(points.items()):
        data = [value for _, value in values]
        tail = data[-100:]
        if not data:
            continue
        ordered = sorted(tail)
        p95 = ordered[min(len(ordered) - 1, int(0.95 * (len(ordered) - 1)))]
        summary[name] = {
            "first": data[0],
            "last": data[-1],
            "minimum": min(data),
            "maximum": max(data),
            "final_100_count": len(tail),
            "final_100_median": statistics.median(tail),
            "final_100_p95": p95,
        }
    return summary


def make_plot(
    branch: str,
    merged: dict[str, list[tuple[float, float]]],
    transitions: list[tuple[float, str]],
    output: Path,
    title_suffix: str = "",
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(13, 7.5), constrained_layout=True)
    for name, values in merged.items():
        if values:
            x_values, y_values = zip(*values)
            ax.plot(x_values, y_values, linewidth=1.25, label=name)
    for x_value, label in transitions:
        ax.axvline(x_value, color="0.35", linewidth=0.9, linestyle="--")
        ax.text(x_value, 1.02, label, transform=ax.get_xaxis_transform(), rotation=90, va="bottom", ha="right", fontsize=8)
    ax.set_yscale("log")
    ax.set_xlabel("Fluent native iteration")
    ax.set_ylabel("Fluent scaled residual")
    ax.set_title(f"03A Stage-2 {branch}: full recorded scaled residual history{title_suffix}")
    ax.grid(True, which="major", linestyle="-", alpha=0.25)
    ax.grid(True, which="minor", linestyle=":", alpha=0.18)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=9)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch", choices=("N1", "N3", "N4", "N5"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    chunks: list[dict[str, list[tuple[float, float]]]] = []
    phase_records: list[dict[str, Any]] = []
    for label, path, minimum_iteration in phase_paths(args.branch):
        if not path.exists():
            chunks.append({})
            phase_records.append({
                "label": label,
                "source": str(path),
                "minimum_iteration_exclusive": minimum_iteration,
                "status": "missing_local_artifact",
                "point_count": 0,
                "first_iteration": None,
                "last_iteration": None,
            })
            continue
        payload = read_json(path)
        points = residual_points(payload, minimum_iteration)
        chunks.append(points)
        all_x = [x for values in points.values() for x, _ in values]
        phase_records.append({
            "label": label,
            "source": str(path),
            "minimum_iteration_exclusive": minimum_iteration,
            "point_count": len(all_x),
            "first_iteration": min(all_x) if all_x else None,
            "last_iteration": max(all_x) if all_x else None,
        })

    merged = merge_series(chunks)
    extension_points = residual_points(
        read_json(EXTENSION_DIR / f"{args.branch}-extension-700-residual-check.json"),
        1800.0 if args.branch == "N5" else 1300.0,
    ) if (EXTENSION_DIR / f"{args.branch}-extension-700-residual-check.json").exists() else {}
    extension_has_points = any(extension_points.values())
    transitions = [(1000.0, "Stage 1 end")]
    if args.branch == "N5":
        transitions.extend([(1500.0, "standard end"), (1800.0, "RNG +300 end")])
        transitions.append((2500.0, "N5 endpoint" if extension_has_points else "N5 endpoint residual pending"))
    else:
        transitions.extend([(1300.0, "+300 end")])
        transitions.append((2000.0, f"{args.branch} endpoint" if extension_has_points else f"{args.branch} endpoint residual pending"))

    output_dir = args.output_dir.expanduser().resolve()
    plot_path = output_dir / f"{args.branch}-full-scaled-residuals.png"
    summary_path = output_dir / f"{args.branch}-summary.json"
    plot_suffix = "" if extension_has_points else " (extension residual history incomplete)"
    make_plot(args.branch, merged, transitions, plot_path, title_suffix=plot_suffix)

    flux_records: list[dict[str, Any]] = []
    for label, path in flux_paths(args.branch):
        if not path.exists():
            flux_records.append({
                "label": label,
                "source": str(path),
                "status": "missing_local_artifact",
                "carrier_metrics": {},
            })
            continue
        payload = read_json(path)
        flux_records.append({
            "label": label,
            "source": str(path),
            "carrier_metrics": payload.get("carrier_metrics", {}),
        })

    summary = {
        "branch": args.branch,
        "branch_definition": branch_definition(args.branch),
        "phase_records": phase_records,
        "phase_residual_summaries": [
            {
                "label": record["label"],
                "source": record["source"],
                "status": record.get("status", "available"),
                "residuals": residual_summary(chunks[index]),
            }
            for index, record in enumerate(phase_records)
        ],
        "full_residual_summary": residual_summary(merged),
        "final_continuation_residual_summary": residual_summary(extension_points),
        "flux_records": flux_records,
        "plot": str(plot_path),
        "interpretation_status": "pending user direction",
        "notes": [
            "Residual values are direct Fluent scaled-monitor values.",
            "Phase histories were filtered by actual native iteration coordinates; no missing intervals were interpolated.",
            "Monitor histories can retain pre-phase points, so point count is not treated as the sole iteration-completion proof.",
        ],
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, default=str), flush=True)
    print(f"summary_json: {summary_path}", flush=True)
    print(f"plot_png: {plot_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

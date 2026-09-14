#!/usr/bin/env python3
"""Compare the finite Phase 7.1A turbulence-family discovery histories."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


CASES = (
    ("t0-rng-reference", "RNG reference"),
    ("t1-standard-kepsilon", "Standard k-epsilon"),
    ("t1-realizable-kepsilon", "Realizable k-epsilon"),
)


def load_case(base: Path, directory: str, label: str) -> dict:
    root = base / directory
    residuals = json.loads((root / "residuals.json").read_text())
    reports = json.loads((root / "reports.json").read_text())["reports"]
    summary = json.loads((root / "analysis-summary.json").read_text())
    return {
        "directory": directory,
        "label": label,
        "root": root,
        "residuals": residuals,
        "reports": reports,
        "summary": summary,
    }


def series(case: dict, name: str) -> tuple[list[float], list[float]]:
    residuals = case["residuals"]
    return residuals["iterations"], residuals["series"][name]


def report(case: dict, name: str) -> tuple[list[float], list[float]]:
    item = case["reports"][name]
    return item["iterations"], item["values"]


def build_figure(cases: list[dict], output: Path) -> None:
    colors = {case["directory"]: color for case, color in zip(cases, ("#1b4965", "#ca6702", "#9b2226"))}
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), constrained_layout=True)

    for name, title, axis in (
        ("continuity", "Continuity residual", axes[0, 0]),
        ("k", "Turbulent kinetic energy residual", axes[0, 1]),
        ("epsilon", "Dissipation residual", axes[1, 0]),
        ("vf-phase-2", "Liquid volume-fraction residual", axes[1, 1]),
    ):
        for case in cases:
            x, y = series(case, name)
            axis.plot(x, y, label=case["label"], lw=1.2, color=colors[case["directory"]])
        axis.set_title(title)
        axis.set_xlabel("Native iteration")
        axis.set_yscale("log")
        axis.grid(True, alpha=0.25)

    axes[0, 0].legend(loc="best", fontsize=8)
    fig.suptitle("Phase 7.1A turbulence-family finite discovery comparison")
    fig.savefig(output, dpi=180)
    plt.close(fig)


def build_balance_figure(cases: list[dict], output: Path) -> None:
    colors = {case["directory"]: color for case, color in zip(cases, ("#1b4965", "#ca6702", "#9b2226"))}
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    report_names = (
        ("e0-liquid-mass-total-rfile", "Total liquid mass [kg]", axes[0]),
        ("absorb-lower-liquid-mass-rfile", "Lower absorber-zone liquid mass [kg]", axes[1]),
        ("e0-flux-phase2-steamoutlet-rfile", "Phase-2 steam-outlet flux [kg/s]", axes[2]),
    )
    for report_name, title, axis in report_names:
        for case in cases:
            x, y = report(case, report_name)
            axis.plot(x, y, label=case["label"], lw=1.2, color=colors[case["directory"]])
        axis.set_title(title)
        axis.set_xlabel("Native iteration")
        axis.grid(True, alpha=0.25)
    axes[0].legend(loc="best", fontsize=8)
    fig.suptitle("Phase 7.1A coupled phase/source histories")
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args()

    cases = [load_case(args.family_dir, directory, label) for directory, label in CASES]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    residual_figure = args.output_dir / "turbulence-family-residual-comparison.png"
    balance_figure = args.output_dir / "turbulence-family-phase-balance-comparison.png"
    build_figure(cases, residual_figure)
    build_balance_figure(cases, balance_figure)

    compact_cases = []
    for case in cases:
        summary = case["summary"]
        compact_cases.append(
            {
                "directory": case["directory"],
                "label": case["label"],
                "setup_id": summary["setup_id"],
                "run_id": summary["run_id"],
                "controlled_delta": summary["controlled_delta"],
                "parent_sha256": summary["parent_sha256"],
                "report_count": summary["report_count"],
                "report_points": summary["report_points"],
                "residual_point_count": summary["residual_point_count"],
                "late_window_statistics": summary["late_window_statistics"],
                "diagnostics": summary["diagnostics"],
                "source_readback": summary["source_readback"],
                "figures": summary["figures"],
            }
        )

    payload = {
        "kind": "phase71a_turbulence_family_comparison",
        "scope": "finite 500-active-iteration attached discovery histories from native 1000 parent state",
        "cases": compact_cases,
        "figures": {
            "residual_comparison": str(residual_figure),
            "phase_balance_comparison": str(balance_figure),
        },
        "claim_limits": [
            "This is a bounded finite-horizon comparison, not a convergence or qualification result.",
            "The runs differ only in the declared turbulence closure delta after exact-parent readback.",
            "The comparison has no contour-level evidence; selected-cell inventories and report histories are the available spatial proxies.",
            "No hypothesis route is authorized by this comparison alone.",
        ],
    }
    args.summary.write_text(json.dumps(payload, indent=2) + "\n")


if __name__ == "__main__":
    main()

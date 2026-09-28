#!/usr/bin/env python3
"""Summarize size-resolved Phase 8 DPM fate counts without imputing incompletes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.build_receipt.read_text(encoding="utf-8"))
    if receipt["status"] != "CASE_DATA_VERIFIED" or receipt.get("tracking_status") != "COMPLETE":
        raise RuntimeError("Seven-bin DPM build or tracking is not complete")
    family = receipt["family"]
    if family not in ("F1", "F2") or receipt["mode"] != "diagnostic":
        raise RuntimeError("This fate summary requires a one-way F1/F2 diagnostic child")
    flows = receipt["reopened"]["dpm_flows_kg_s"]
    rows = []
    for result in sorted(receipt["particle_tracks"]["results"],
                         key=lambda r: r["name"]):
        if result["status"] != "ok":
            raise RuntimeError(f"Incomplete native report for {result['name']}")
        counts = result["counts"]
        tracked = int(counts["tracked"])
        if tracked <= 0 or sum(int(counts[k]) for k in ("escaped", "trapped", "incomplete")) != tracked:
            raise RuntimeError(f"Unaccounted fates for {result['name']}")
        weight = float(flows[result["name"]])
        rows.append({"name": result["name"], "diameter_um": float(next(
            item["diameter_um"] for item in receipt["particle_tracks"]["injections"]
            if item["name"] == result["name"])),
                     "diagnostic_weight_kg_s": weight, "tracked": tracked,
                     **{k: int(counts[k]) for k in ("escaped", "trapped", "incomplete")},
                     **{f"{k}_fraction": int(counts[k]) / tracked
                        for k in ("escaped", "trapped", "incomplete")}})
    total_weight = sum(row["diagnostic_weight_kg_s"] for row in rows)
    weighted = {k: sum(row["diagnostic_weight_kg_s"] * row[f"{k}_fraction"] for row in rows) / total_weight
                for k in ("escaped", "trapped", "incomplete")}
    summary = {"build_receipt": str(args.build_receipt), "family": family, "bins": rows,
               "total_tracks": sum(row["tracked"] for row in rows),
               "total_diagnostic_weight_kg_s": total_weight,
               "weighted_fate_fraction": weighted,
               "interpretation": "Incomplete tracks are unresolved; escaped fraction is a lower bound on represented diagnostic weight, not a physical carryover efficiency."}
    args.output.mkdir(parents=True, exist_ok=True)
    x = np.arange(len(rows))
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    bottom = np.zeros(len(rows))
    for fate, color in (("escaped", "#3377ba"), ("trapped", "#389b74"), ("incomplete", "#d89039")):
        values = np.array([row[f"{fate}_fraction"] for row in rows])
        ax.bar(x, values, bottom=bottom, label=fate.capitalize(), color=color)
        bottom += values
    ax.set_xticks(x, [f"{row['diameter_um']:.2f}" for row in rows])
    ax.set_xlabel("Representative droplet diameter (µm)")
    ax.set_ylabel("Fraction of tracked trajectories")
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y", alpha=0.25)
    ax.legend(loc="upper right")
    ax.set_title(f"{family} diagnostic DPM fates at 26.81 m/s; 613 tracks per bin")
    fig.tight_layout()
    figure = args.output / f"{family.lower()}-diagnostic-dpm-fates-26p81.png"
    fig.savefig(figure, dpi=170)
    plt.close(fig)
    summary["figure"] = str(figure)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(args.output / "summary.json"), "figure": str(figure),
                      "weighted_fate_fraction": weighted}, indent=2))


if __name__ == "__main__":
    main()

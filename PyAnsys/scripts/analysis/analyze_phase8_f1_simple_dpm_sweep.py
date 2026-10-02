#!/usr/bin/env python3
"""Compare weighted diagnostic DPM fates on the five F1 SIMPLE carriers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "phase8-analysis" / "f1-simple-vs-coupled-n10000"
SPEEDS = [20.11, 23.46, 26.81, 29.48, 32.14]
FATES = ["escaped", "trapped", "incomplete"]
COLORS = {"escaped": "#35b779", "trapped": "#d99b24", "incomplete": "#7b8794"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    rows = []
    for speed in SPEEDS:
        key = str(speed).replace(".", "p")
        path = ROOT / "output" / "phase8-analysis" / f"{key}-f1-simple-n10000" / "dpm-fates" / "summary.json"
        summary = json.loads(path.read_text(encoding="utf-8"))
        if summary.get("family") != "F1" or float(summary.get("speed_m_s")) != speed:
            raise RuntimeError(f"DPM fate summary does not match {speed:g} m/s: {path}")
        fractions = summary["weighted_fate_fraction"]
        if any(fate not in fractions for fate in FATES) or not np.isclose(sum(fractions[f] for f in FATES), 1.0, atol=2e-6):
            raise RuntimeError(f"Weighted fates do not sum to one: {path}")
        rows.append({"speed_m_s": speed, "summary": str(path.relative_to(ROOT)).replace("\\", "/"),
                     "summary_sha256": digest(path), "weighted_fate_fraction": {f: float(fractions[f]) for f in FATES},
                     "bin_count": len(summary["bins"]), "bins": summary["bins"]})

    x = np.arange(len(rows))
    bottom = np.zeros(len(rows))
    fig, ax = plt.subplots(figsize=(10, 5.8))
    for fate in FATES:
        values = np.array([r["weighted_fate_fraction"][fate] for r in rows]) * 100
        ax.bar(x, values, bottom=bottom, label=fate.capitalize(), color=COLORS[fate], width=.62)
        bottom += values
    ax.set_xticks(x, [f"{s:.2f}" for s in SPEEDS])
    ax.set(xlabel="Nominal inlet speed (m/s)", ylabel="Share of represented DPM diagnostic weight (%)",
           ylim=(0, 100))
    ax.grid(axis="y", alpha=.25)
    ax.set_axisbelow(True)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(.5, 1.12), frameon=False)
    fig.suptitle("One-way diagnostic DPM fates on F1 SIMPLE carriers", y=1.02)
    fig.tight_layout()
    figure = OUT / "f1-simple-diagnostic-dpm-fates.png"
    fig.savefig(figure, dpi=180, bbox_inches="tight")
    plt.close(fig)

    receipt = {"status": "COMPLETE", "family": "F1", "carrier_method_package": "SIMPLE / segregated pseudo-time off / second-order k",
               "speeds_m_s": SPEEDS, "represented_dpm_fraction_of_feed": 0.05, "interaction": "one-way",
               "bin_count_per_speed": 7, "maximum_tracking_steps": 50000, "solve_issued": False,
               "runs": rows, "figure": str(figure.relative_to(ROOT)).replace("\\", "/"),
               "figure_sha256": digest(figure),
               "claim_limit": "Weighted particle fates are diagnostics on poor numerical SIMPLE carriers with 5% one-way represented DPM weight. Incomplete tracks remain unresolved; these fractions are not separator efficiency or validated particle separation."}
    output = OUT / "f1-simple-diagnostic-dpm-fates.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": str(output), "figure": str(figure),
                      "weighted_fate_fraction": [r["weighted_fate_fraction"] for r in rows]}, indent=2))


if __name__ == "__main__":
    main()

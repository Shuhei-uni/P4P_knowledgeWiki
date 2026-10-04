"""Restore missing display plots using rounded, committed Phase 8 result tables.

This does not reconstruct raw run evidence or replace the original analyses.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PHASE = Path(__file__).resolve().parents[3] / "Project/experiments/phase-08-storyline-reconstruction"


def table(text, header):
    block = text.split(header, 1)[1].strip().split("\n\n", 1)[0]
    return [line.strip("| ").split("|") for line in block.splitlines()[1:]]


def main():
    source = PHASE / "f1-one-inlet/results.md"
    text = source.read_text()
    output = source.parent / "figures"
    rows = table(text, "| Speed (m/s) | Steam-outlet liquid / feed, Coupled → SIMPLE (%) | Final liquid inventory, Coupled → SIMPLE (kg) | Pressure difference, Coupled → SIMPLE (kPa) |")
    speeds = [float(row[0]) for row in rows]
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    labels = ["Steam-outlet liquid / liquid feed (%)", "Final Eulerian liquid inventory (kg)", "Steam-face to outlet pressure difference (kPa)"]
    for column, (ax, label) in enumerate(zip(axes, labels), 1):
        values = np.array([[float(v) for v in row[column].split("→")] for row in rows])
        ax.plot(speeds, values[:, 0], "o-", color="#7b8794", label="Coupled recovery")
        ax.plot(speeds, values[:, 1], "o-", color="#c54843", label="SIMPLE reconstruction")
        ax.set(xlabel="Nominal inlet speed (m/s)", ylabel=label)
        ax.grid(alpha=.25)
    axes[0].legend()
    fig.suptitle("F1 numerical-package comparison at N10,000\nReplotted from rounded results-table values")
    fig.tight_layout()
    fig.savefig(output / "f1-simple-vs-coupled-n10000.png", dpi=180)
    plt.close(fig)

    rows = table(text, "| Speed (m/s) | Escaped represented weight (%) | Trapped represented weight (%) | Incomplete represented weight (%) |")
    x = np.arange(len(rows))
    bottom = np.zeros(len(rows))
    fig, ax = plt.subplots(figsize=(10, 5.8))
    for column, label, color in [(1, "Escaped", "#35b779"), (2, "Trapped", "#d99b24"), (3, "Incomplete", "#7b8794")]:
        values = np.array([float(row[column]) for row in rows])
        ax.bar(x, values, bottom=bottom, label=label, color=color, width=.62)
        bottom += values
    ax.set_xticks(x, [row[0].strip() for row in rows])
    ax.set(xlabel="Nominal inlet speed (m/s)", ylabel="Share of represented DPM diagnostic weight (%)", ylim=(0, 101))
    ax.grid(axis="y", alpha=.25)
    ax.set_axisbelow(True)
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(.5, 1.12), frameon=False)
    fig.suptitle("One-way diagnostic DPM fates on F1 SIMPLE carriers\nReplotted from rounded results-table values")
    fig.tight_layout(rect=(0, 0, 1, .94))
    fig.savefig(output / "f1-simple-diagnostic-dpm-fates.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()

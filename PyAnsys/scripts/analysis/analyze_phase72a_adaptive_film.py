"""Plot measured adaptive film time, rates and numerical controls from native evidence."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/phase72a-adaptive-server1/20261005"


def main():
    histories = json.loads((OUT / "report-histories.json").read_text())
    clocks = {int(k): v for k, v in json.loads((OUT / "film-clock-history.json").read_text()).items()}
    inventory = histories["p72a-e2.7-ewf-film-mass-total"]
    ids = inventory["iterations"]
    native_time = np.asarray([0.1 if i == 33586 else clocks[i][0] for i in ids])
    time_ms = (0.02 + native_time - 0.1) * 1000
    values = lambda name: np.asarray(histories[name]["values"])
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
    axes[0, 0].plot(time_ms, inventory["values"], color="#276B9D")
    axes[0, 0].set_ylabel("Film inventory (kg)")
    axes[0, 1].plot(time_ms, 1000 * values("p72a-e2.7-ewf-thickness-max"), color="#276B9D")
    axes[0, 1].set_ylabel("Maximum film thickness (mm)")
    accrete = values("p72a-e2.7-ewf-secondary-phase-mass-total")
    axes[1, 0].plot(time_ms, accrete, label="Native accretion", color="#276B9D")
    drainage = values("p72a-e2.7-ewf-outflow-mass-total")
    window = min(100, len(ids) - 1)
    rates = (drainage[window:] - drainage[:-window]) / (native_time[window:] - native_time[:-window])
    axes[1, 0].plot(time_ms[window:], rates, label=f"Drainage over {window} updates", color="#B87520")
    axes[1, 0].set_ylabel("Accretion / drainage (kg/s)")
    axes[1, 0].legend()
    axes[1, 1].plot(time_ms, drainage - drainage[0], color="#B87520")
    axes[1, 1].set_ylabel("Drained film mass since N33586 (kg)")
    for axis in axes.flat:
        axis.set_xlabel("Added film time since corrected E2.7 restart (ms)")
        axis.grid(alpha=0.2)
        axis.ticklabel_format(axis="y", style="plain", useOffset=False)
    fig.suptitle(f"Adaptive continuation of N33586 — native N{ids[0]}–N{ids[-1]}")
    fig.savefig(OUT / "adaptive-film-histories.png", dpi=160)
    plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), layout="constrained", sharex=True)
    axes[0].step(time_ms[1:], [1e6 * clocks[i][1] for i in ids[1:]], where="post")
    axes[0].set_ylabel("Accepted film step (µs, rounded)")
    axes[1].plot(time_ms[1:], [clocks[i][2] for i in ids[1:]])
    axes[1].axhline(0.05, color="#B87520", linestyle="--", label="Courant target 0.05")
    axes[1].set_ylabel("Solved maximum film CFL")
    axes[1].set_xlabel("Added film time since corrected E2.7 restart (ms)")
    axes[1].legend()
    for axis in axes:
        axis.grid(alpha=0.2)
    fig.savefig(OUT / "adaptive-step-cfl.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()

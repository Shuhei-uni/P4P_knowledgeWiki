"""Replot existing wall-treatment evidence; no Fluent connection or solve."""
from pathlib import Path
import csv
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "Project/observations/figures/wall-liquid-interaction"
MACHINE = ROOT / "PyAnsys/output/wall-liquid-interaction-comparison"
R_SOURCE = ROOT / "PyAnsys/output/phase72a_family_r/analysis-20260923T054600Z-cs-sensitivity-v2/tail-summary.csv"
E_SOURCES = {
    "E0": ROOT / "PyAnsys/output/phase72a_ewf_family_e_student_20260922T115500Z/E0/report-histories.json",
    "E2.7": ROOT / "PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/report-histories.json",
}
F_SOURCE = ROOT / "Project/experiments/phase-08-storyline-reconstruction/results.md"


def save(fig, name):
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    MACHINE.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False})
    with R_SOURCE.open() as stream:
        rows = list(csv.DictReader(stream))
    r = {row["case"]: row for row in rows}
    flux = lambda name: -float(r[name]["phase2_outlet_mean_last_500_kg_s"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout="constrained")
    cases = [f"R{i}" for i in range(8)]
    axes[0].plot([1000 * float(r[c]["k_s_m"]) for c in cases],
                 [flux(c) for c in cases], "o-", color="#2166ac")
    for c in cases:
        axes[0].annotate(c, (1000 * float(r[c]["k_s_m"]), flux(c)),
                         xytext=(4, 7), textcoords="offset points", fontsize=9)
    axes[0].set(xlabel="Roughness height, k_s (mm)",
                ylabel="Bulk liquid outflow at steamoutlet (kg/s)",
                title="Roughness height: C_s = 0.5")
    for names, label, colour in [(["R3", "R8", "R9"], "k_s = 0.5 mm", "#2166ac"),
                                 (["R5", "R10", "R11"], "k_s = 2 mm", "#d6604d")]:
        axes[1].plot([float(r[c]["C_s"]) for c in names], [flux(c) for c in names],
                     "o-", label=label, color=colour)
        for c in names:
            axes[1].annotate(c, (float(r[c]["C_s"]), flux(c)),
                             xytext=(4, 7), textcoords="offset points", fontsize=9)
    axes[1].axhline(flux("R0"), color="0.4", linestyle="--", label="Smooth R0")
    axes[1].set(xlabel="Roughness constant, C_s", title="Constant at fixed roughness height")
    axes[1].set_xticks([0.5, 0.75, 1.0])
    axes[1].legend(fontsize=9)
    for ax in axes:
        ax.set_ylim(0, 33)
        ax.grid(alpha=0.2)
    fig.suptitle("Wall roughness changes predicted steam-outlet liquid flow\n"
                 "EWF off; native 8087–8586 means; positive = outward flow", fontsize=13)
    save(fig, "01-roughness-steamoutlet.png")

    fig, ax = plt.subplots(figsize=(9, 4.8), layout="constrained")
    e_summary = {}
    exports = {}
    for name, source in E_SOURCES.items():
        report = json.loads(source.read_text())["v2-flux-phase2-steamoutlet"]
        data = dict(zip(report["iterations"], report["values"]))
        coordinates = np.arange(5586, 8587)
        assert all(int(i) in data for i in coordinates), name
        values = -np.array([data[int(i)] for i in coordinates], dtype=float)
        assert np.isfinite(values).all()
        ax.plot(coordinates, values, label=f"{name}: " + ("EWF off" if name == "E0" else "EWF with phase accretion"), lw=1.4)
        tail = values[coordinates >= 8087]
        e_summary[name] = {"tail_mean_outflow_kg_s": float(tail.mean()),
                           "tail_std_kg_s": float(tail.std(ddof=1)), "samples": len(tail)}
        exports[name] = values
    ax.axvspan(8087, 8586, color="0.6", alpha=0.15, label="Final 500 iterations")
    ax.set(xlabel="Native iteration", ylabel="Bulk liquid outflow at steamoutlet (kg/s)",
           title="EWF-off baseline versus E2.7\nSame native-5586 parent; smooth walls; positive = outward flow", ylim=(0, 28))
    ax.grid(alpha=0.2)
    ax.legend(fontsize=10)
    save(fig, "02-ewf-off-vs-e27.png")
    with (MACHINE / "e0-e27-outflow.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["native_iteration", "E0_outflow_kg_s", "E2.7_outflow_kg_s"])
        writer.writerows(zip(coordinates, exports["E0"], exports["E2.7"]))

    # Read the current rounded Project table directly; absent raw batch files
    # are not reconstructed or described as verified here.
    lines = F_SOURCE.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("| Speed (m/s) | DPM share | F3 bulk outlet"))
    f_rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        f_rows.append([float(cells[0]), cells[1], *[float(v) for v in cells[2:]]])
    assert len(f_rows) == 5
    fig, ax = plt.subplots(figsize=(10, 5), layout="constrained")
    x = np.arange(len(f_rows))
    for index, label, shift, colour in [(2, "F3: EWF off", -0.18, "#2166ac"),
                                        (3, "F4: provisional EWF on", 0.18, "#d6604d")]:
        bars = ax.bar(x + shift, [row[index] for row in f_rows], width=0.36, label=label, color=colour)
        ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
    ax.set_xticks(x, [f"{row[0]:.2f} m/s\n{row[1]} DPM" for row in f_rows])
    ax.set(ylabel="Bulk liquid outflow / total water feed (%)", ylim=(0, 119),
           title="F3 versus F4: wall-film treatment changes bulk liquid routing\n"
                 "Native N15500–16000 comparison; rounded values from the Project results table")
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    save(fig, "03-f3-vs-f4.png")
    sources = [R_SOURCE, *E_SOURCES.values(), F_SOURCE]
    summary = {"sources": [{"path": str(p.relative_to(ROOT)),
                             "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],
               "roughness": rows, "ewf_comparison": e_summary,
               "ewf_tail_window": [8087, 8586],
               "ewf_tail_mean_reduction_percent": 100 * (1 - e_summary["E2.7"]["tail_mean_outflow_kg_s"] / e_summary["E0"]["tail_mean_outflow_kg_s"]),
               "f3_f4": {"columns": ["speed_m_s", "dpm_share", "F3_outlet_percent", "F4_outlet_percent", "F3_bulk_kg", "F4_bulk_kg", "F4_film_kg"],
                         "rows": f_rows, "basis": "rounded Project table; raw matched batch absent from this checkout"},
               "claim_limit": "Model sensitivity, not validated separation efficiency. Balances and EWF transfers remain incomplete."}
    (MACHINE / "plot-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(e_summary, indent=2))
    print("E2.7 mean reduction (%):", summary["ewf_tail_mean_reduction_percent"])
    print("Saved three plots to", OUT)


if __name__ == "__main__":
    main()

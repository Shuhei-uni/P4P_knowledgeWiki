"""Plot the selected matched 15 ms film-drain comparison for the report.

Run with PyAnsys/.venv/bin/python from any working directory. Values come
from the unchanged analysed native record. No Fluent connection is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "PyAnsys/output/phase72a-stage4-ewf-drain/20261007/analysis-summary.json"
EXPECTED_SHA256 = "a2174bb73598520d881c700117f20ceb284c8982b6f91f04efb45bef97b05e03"
DEFAULT_OUT = ROOT / "Project/Final research report/Shuhei Report/figures"
STEM = "results-direct-film-drain"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    source_hash = sha256(SOURCE)
    if source_hash != EXPECTED_SHA256:
        raise ValueError("Selected source changed; inspect before replacing report assets")
    record = json.loads(SOURCE.read_text())
    off, on = (record["screens"][key] for key in ("off", "on"))
    for arm in (off, on):
        if not (
            arm["status"] == "SCREEN_COMPLETE_VERIFIED"
            and arm["native_start"] == 40483
            and arm["native_end"] == 41483
            and arm["updates"] == 1000
            and abs(arm["added_film_time_s"] - 0.015) < 1e-12
            and arm["bulk_equations_frozen"]
            and arm["bulk_reports_unchanged"]
            and arm["paired_reopen"] == "PASS"
            and arm["outflow_convention"] == "USER_DRAIN_EXCLUDED_FROM_NATIVE_OUTFLOW"
        ):
            raise ValueError("Matched comparison conditions failed")
    if off["film_initial_kg"] != on["film_initial_kg"]:
        raise ValueError("Initial inventories differ")
    lower = [arm["lower_final_kg"] for arm in (off, on)]
    native = [arm["mass_changes_kg"]["outflow"] for arm in (off, on)]
    direct = [arm["drain_integral_left_kg"] for arm in (off, on)]
    external = [native[i] + direct[i] for i in range(2)]
    net_gain = external[1] - external[0]
    lower_reduction = 100 * (lower[0] - lower[1]) / lower[0]
    values = {
        "initial_total_film_kg": off["film_initial_kg"],
        "lower_final_kg_off_on": lower,
        "total_final_kg_off_on": [arm["film_final_kg"] for arm in (off, on)],
        "native_outflow_kg_off_on": native,
        "direct_sink_kg_off_on": direct,
        "external_removal_kg_off_on": external,
        "external_removal_net_gain_kg": net_gain,
        "lower_film_reduction_percent": lower_reduction,
        "direct_sink_quadrature_span_kg": on["drain_quadrature_span_kg"],
    }
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 10, "axes.labelsize": 10})
    fig, axes = plt.subplots(1, 2, figsize=(16 / 2.54, 7.5 / 2.54))
    grey, blue = "#8E8E8E", "#0072B2"
    x = [0, 1]
    labels = ["Drain OFF", "Drain ON"]
    axes[0].bar(x, lower, width=0.55, color=[grey, blue])
    axes[0].set(title="(a) Lower-wall film at 15 ms", ylabel="Film mass (kg)", ylim=(0, 0.245))
    for i, value in enumerate(lower):
        axes[0].text(i, value + 0.007, f"{value:.5f}", ha="center", va="bottom")
    axes[0].text(0.5, 0.232, f"{lower_reduction:.2f}% less lower-wall film", ha="center", va="top", fontsize=9)
    axes[1].bar(x, native, width=0.55, color=grey, label="Native outflow")
    axes[1].bar(x, direct, width=0.55, bottom=native, color=blue, label="Direct sink")
    axes[1].set(title="(b) External removal over 15 ms", ylabel="Removed liquid (kg)", ylim=(0, 0.90))
    for i in x:
        axes[1].text(i, native[i] / 2, f"{native[i]:.4f}", ha="center", va="center", color="white")
        if direct[i] > 0:
            axes[1].text(i, native[i] + direct[i] / 2, f"{direct[i]:.4f}", ha="center", va="center", color="white")
        axes[1].text(i, external[i] + 0.015, f"{external[i]:.4f}", ha="center", va="bottom")
    axes[1].text(0.5, 0.86, f"Net gain: +{net_gain:.4f} kg", ha="center", va="top", fontsize=9)
    axes[1].legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), ncol=2, frameon=False, fontsize=9, handlelength=1.1, columnspacing=0.8)
    for ax in axes:
        ax.set_xticks(x, labels)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#DDDDDD", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(left=0.10, right=0.98, top=0.86, bottom=0.26, wspace=0.45)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for suffix in ("png", "pdf"):
        path = args.output_dir / f"{STEM}.{suffix}"
        fig.savefig(path, dpi=300, metadata={"Creator": "Matplotlib"} if suffix == "pdf" else None)
        outputs[suffix] = {"filename": path.name, "sha256": sha256(path)}
    plt.close(fig)
    provenance = {
        "figure": STEM,
        "source": {"path": str(SOURCE.relative_to(ROOT)), "sha256": source_hash},
        "script": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": sha256(Path(__file__))},
        "scope": "Matched N40483–N41483, 1000 updates, 15 ms; expanded film domain; frozen bulk",
        "processing": "Bars use exact analysed endpoints and cumulative masses. No smoothing, interpolation, resampling or additional solver updates. Direct sink uses preceding-rate integration and is added once to native outflow.",
        "values": values,
        "conditions_verified": True,
        "claim_limit": "Numerical local-drain comparison under fixed bulk forcing; no stationary film, whole-separator closure or physical validation claim.",
        "output": outputs,
        "size_cm": [16, 7.5],
        "software": {"matplotlib": matplotlib.__version__},
    }
    (args.output_dir / f"{STEM}.provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"external_removal_net_gain_kg": net_gain, "lower_film_reduction_percent": lower_reduction, "outputs": list(outputs)}))


if __name__ == "__main__":
    main()

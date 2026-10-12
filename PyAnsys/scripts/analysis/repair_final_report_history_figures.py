"""Rebuild the two report history figures from their selected source arrays.

Run with ``PyAnsys/.venv/bin/python`` from any working directory. The default
destination is the final report's figures folder; ``--output-dir`` allows an
independent reproduction. No Fluent connection, raw-data edit, interpolation,
subsampling or smoothing is used. Source hashes and numerical checks must pass
before either report asset is replaced.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT = ROOT / "Project/Final research report/figures"
SOURCE_SPECS = {
    "historical_liquid": (
        "PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv",
        "fd2dc3dd83f8a0ce55770295ff14402717de1786d316a6d078e71de156c25f26",
    ),
    "historical_residuals": (
        "PyAnsys/output/phase72a-lineage-N45606/20261005/carrier-residuals.csv",
        "2f056c646cb59fb037f11e4780ec6faddb74fb78a88c23a4c55aa6a8613b8149",
    ),
    "shortened_liquid": (
        "PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/final-histories.json",
        "9882b96f527d1c5337990759a14eb31f51f3ff600e298855ea75170886307524",
    ),
    "shortened_residuals": (
        "PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/carrier-residuals.json",
        "ef9c462d3eab58e25a278b1c8fd1f1f0e4013bf55a09a4df8f5f661da5e68b49",
    ),
    "startup_metrics": (
        "PyAnsys/output/phase72a-stage3-early-ewf-server1/20261005/analysis-summary.json",
        "a0e5b2faa71429e68fa2fc1e3ef87c9992158e77f1319b4acfdf5e35163caf52",
    ),
    "selected_film_history": (
        "PyAnsys/output/phase72a-stage3-film-development-server1/20261005/selected-history/selected-case-history-N25815.csv",
        "961c587832364b8d4e8d831fa5b295959b8dc5f4f1661d8e074e7819373e2afd",
    ),
}
EVENTS = [
    (1580, "A", "combined model activation"),
    (2080, "B", "inlet ramp"),
    (4080, "C", "full feed"),
    (5080, "D", "bulk freeze and faster film stepping"),
    (7190, "E", "lower-target recovery"),
    (13390, "F", "20 µs local step screen"),
    (22615, "G", "smaller-step recovery"),
]
RESTARTS = [7190, 13390, 22615]
BLUE, ORANGE, PURPLE = "#0072B2", "#B86D20", "#A64C9D"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_sources() -> dict:
    sources = {}
    for role, (relative, expected) in SOURCE_SPECS.items():
        actual = sha256(ROOT / relative)
        if actual != expected:
            raise ValueError(f"Source hash changed: {relative}")
        sources[role] = {"path": relative, "sha256": actual}
    return sources


def csv_rows(role: str) -> list[dict]:
    with (ROOT / SOURCE_SPECS[role][0]).open(newline="") as stream:
        return list(csv.DictReader(stream))


def json_source(role: str) -> dict:
    return json.loads((ROOT / SOURCE_SPECS[role][0]).read_text())


def column(rows: list[dict], key: str) -> np.ndarray:
    return np.array([float(row[key]) for row in rows], dtype=float)


def exact_window(rows: list[dict], first: int, last: int) -> list[dict]:
    selected = [row for row in rows if first <= int(row["native_iteration"]) <= last]
    ids = np.array([int(row["native_iteration"]) for row in selected])
    np.testing.assert_array_equal(ids, np.arange(first, last + 1))
    return selected


def report_values(histories: dict, key: str, ids: np.ndarray) -> np.ndarray:
    series = histories[key]
    if len(series["iterations"]) != len(series["values"]):
        raise ValueError(f"Report lengths differ: {key}")
    mapping = dict(zip(series["iterations"], series["values"]))
    return np.array([mapping[int(n)] for n in ids], dtype=float)


def array_digest(values: np.ndarray) -> str:
    """Hash canonical little-endian float64 values, including every point."""
    return hashlib.sha256(np.asarray(values, dtype="<f8").tobytes()).hexdigest()


def metrics(values: np.ndarray) -> dict:
    return {
        "peak": float(values.max()),
        "p95": float(np.percentile(values, 95)),
        "mean": float(values.mean()),
        "end": float(values[-1]),
    }


def startup_arrays() -> tuple[dict, dict]:
    historical_ids = np.arange(1581, 4581)
    shortened_ids = np.arange(2081, 5081)
    historical = exact_window(csv_rows("historical_liquid"), 1581, 4580)
    residuals = exact_window(csv_rows("historical_residuals"), 1581, 4580)
    shortened = json_source("shortened_liquid")
    shortened_residuals = json_source("shortened_residuals")
    summary = json_source("startup_metrics")
    bulk = report_values(shortened, "v2-total-liquid-mass", shortened_ids)
    film = report_values(shortened, "p72a-e2.7-ewf-film-mass-total", shortened_ids)
    arrays = {
        "historical": {
            "native_iteration": historical_ids,
            "continuity": column(residuals, "continuity"),
            "bulk_plus_film_kg": column(historical, "bulk_plus_ewf_kg"),
            "signed_outlet_kg_s": column(historical, "phase2_steamoutlet_signed_kg_s"),
        },
        "early_ewf": {
            "native_iteration": shortened_ids,
            "continuity": np.array([shortened_residuals[str(n)][0] for n in shortened_ids]),
            "bulk_plus_film_kg": bulk + film,
            "signed_outlet_kg_s": report_values(shortened, "v2-flux-phase2-steamoutlet", shortened_ids),
        },
    }
    factors = [summary["normalization"][key]["continuity"] for key in ("historical_B", "new_N5080")]
    for field in ("last", "minimum", "maximum"):
        np.testing.assert_allclose([factor[field] for factor in factors], 386.0459609770594, rtol=0, atol=1e-12)

    checked_metrics = {}
    for window, selection in (("ramp", slice(0, 2000)), ("final_500_of_matched_1000_target_hold", slice(-500, None))):
        checked_metrics[window] = {}
        for case, series in arrays.items():
            checked_metrics[window][case] = {}
            for metric_name, values in (
                ("continuity", series["continuity"]),
                ("bulk_plus_film_kg", series["bulk_plus_film_kg"]),
                ("outward_liquid_kg_s", -series["signed_outlet_kg_s"]),
            ):
                actual = metrics(values[selection])
                expected = summary["comparison"][window][case][metric_name]
                np.testing.assert_allclose(list(actual.values()), [expected[key] for key in actual], rtol=1e-12, atol=1e-12)
                checked_metrics[window][case][metric_name] = actual
    checks = {
        "historical_native_range": [1581, 4580],
        "shortened_native_range": [2081, 5080],
        "matched_points_per_case": 3000,
        "activation_hold_excluded": True,
        "ramp_end_update": 2000,
        "continuity_normalisation_factor": 386.0459609770594,
        "continuity_normalisation_common_to_both_cases": True,
        "liquid_fraction_residual_excluded": "Different native normalisation; excluded from the comparison.",
        "ramp_and_final_500_metrics_against_native_summary": "PASS",
        "verified_metrics": checked_metrics,
        "outlet_sign": "Native signed steamoutlet flux; negative is outward. Summary checks use outward magnitudes.",
        "array_sha256": {case: {key: array_digest(values) for key, values in series.items()} for case, series in arrays.items()},
    }
    return arrays, checks


def film_arrays() -> tuple[dict, dict]:
    rows = exact_window(csv_rows("selected_film_history"), 1, 25815)
    arrays = {key: column(rows, key) for key in (
        "native_iteration", "bulk_liquid_kg", "bulk_plus_ewf_kg",
        "phase2_steamoutlet_signed_kg_s", "film_kg", "accretion_kg_s", "drainage_kg_s",
    )}
    for values in arrays.values():
        if not np.isfinite(values).all():
            raise ValueError("Selected film array contains non-finite values")
    np.testing.assert_allclose(arrays["bulk_plus_ewf_kg"], arrays["bulk_liquid_kg"] + arrays["film_kg"], rtol=0, atol=1e-8)
    endpoint = {
        "bulk_liquid_kg": 61.05488260946753,
        "bulk_plus_ewf_kg": 67.74315813996104,
        "phase2_steamoutlet_signed_kg_s": -3.429961885581568,
        "film_kg": 6.688275530493504,
        "accretion_kg_s": 81.12137742644737,
        "drainage_kg_s": 68.21860582890211,
    }
    for key, expected in endpoint.items():
        np.testing.assert_allclose(arrays[key][-1], expected, rtol=0, atol=1e-12)
    checks = {
        "native_range": [1, 25815],
        "plotted_points_per_series": 25815,
        "event_markers": EVENTS,
        "preserved_restart_diamonds": RESTARTS,
        "outlet_sign": "Native signed steamoutlet flux; negative is outward",
        "drainage_rate_definition": "Source CSV rate from cumulative outflow change / accepted film time",
        "bulk_plus_film_identity": "PASS at every selected row",
        "verified_endpoint": endpoint,
        "original_csv_arrays_retained": True,
        "excluded_siblings_and_rejected_recoveries_unchanged": True,
        "array_sha256": {key: array_digest(values) for key, values in arrays.items()},
    }
    return arrays, checks


def style_axes(axes) -> None:
    for ax in axes:
        ax.grid(which="major", color="#DDDDDD", linewidth=0.6, alpha=0.7)
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=10)


def provenance(fig, stem: str, checks: dict, sources: dict, out: Path) -> None:
    path = out / f"{stem}.png"
    fig.savefig(path, dpi=300, facecolor="white")
    text = [artist.get_text() for artist in fig.findobj(matplotlib.text.Text) if artist.get_text()]
    record = {
        "figure": stem,
        "processing": "Numerical replot from the unchanged selected source arrays; every selected point drawn without smoothing, interpolation or subsampling.",
        "script": {
            "path": str(Path(__file__).resolve().relative_to(ROOT)),
            "sha256": sha256(Path(__file__).resolve()),
        },
        "checks": checks,
        "plot_text": text,
        "sources": sources,
        "output": {"sha256": sha256(path), "dpi": 300, "size_inches": list(fig.get_size_inches())},
        "software": {"matplotlib": matplotlib.__version__, "numpy": np.__version__},
    }
    (out / f"{stem}.provenance.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    plt.close(fig)


def draw_startup(arrays: dict, checks: dict, sources: dict, out: Path) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(6.8, 6.4), sharex=True)
    fig.subplots_adjust(left=0.19, right=0.955, top=0.88, bottom=0.11, hspace=0.16)
    x = np.arange(1, 3001)
    for case, color, label in (("historical", ORANGE, "Historical startup"), ("early_ewf", BLUE, "Shortened startup")):
        series = arrays[case]
        axes[0].semilogy(x, series["continuity"], color=color, linewidth=0.9, label=label)
        axes[1].plot(x, series["bulk_plus_film_kg"], color=color, linewidth=1.3)
        axes[2].plot(x, series["signed_outlet_kg_s"], color=color, linewidth=1.3)
    for panel, ax in zip("abc", axes):
        ax.axvspan(2000, 3000, color="#F5F5F5", zorder=0)
        ax.axvline(2000, color="#777777", linestyle="--", linewidth=0.8)
        ax.text(0.02, 0.94, f"({panel})", transform=ax.transAxes, va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
        ax.set_xlim(0, 3000)
    axes[0].set_ylabel("Continuity residual\n(common scale)")
    axes[0].set_ylim(3e-4, 1.5e-2)
    axes[1].set_ylabel("Bulk + film\nliquid inventory (kg)")
    axes[1].set_ylim(16, 310)
    axes[1].set_yticks([100, 200, 300])
    axes[2].set_ylabel("Signed liquid flux\nat steam outlet (kg/s)")
    axes[2].set_ylim(-25.5, 0.8)
    axes[2].set_yticks([-20, -10, 0])
    axes[2].text(0.02, 0.06, "Negative = outward", transform=axes[2].transAxes, fontsize=9.5)
    axes[2].set_xticks(np.arange(0, 3001, 500))
    axes[2].set_xlabel("Updates since inlet ramp start\n1–2000: ramp; 2001–3000: full-feed hold")
    fig.suptitle("Startup comparison at matched inlet loading", fontsize=12, y=0.975)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.56, 0.95), ncol=2, frameon=False, fontsize=10)
    style_axes(axes)
    keys = ("historical_liquid", "historical_residuals", "shortened_liquid", "shortened_residuals", "startup_metrics")
    provenance(fig, "results-described-startup", checks, {key: sources[key] for key in keys}, out)


def draw_film(arrays: dict, checks: dict, sources: dict, out: Path) -> None:
    fig, axes = plt.subplots(4, 1, figsize=(6.8, 7.8), sharex=True)
    fig.subplots_adjust(left=0.18, right=0.98, top=0.925, bottom=0.09, hspace=0.15)
    x = arrays["native_iteration"]
    lines = [
        [("bulk_liquid_kg", BLUE, "Bulk liquid"), ("bulk_plus_ewf_kg", PURPLE, "Bulk + film")],
        [("phase2_steamoutlet_signed_kg_s", BLUE, None)],
        [("film_kg", BLUE, None)],
        [("accretion_kg_s", BLUE, "Accretion"), ("drainage_kg_s", ORANGE, "Drainage")],
    ]
    for panel, ax, series in zip("abcd", axes, lines):
        for key, color, label in series:
            ax.plot(x, arrays[key], color=color, linewidth=1.1, label=label)
            # Keep the original restart diamonds on each primary trace and both
            # inventory traces. Drainage is preserved as the complete source line.
            if key != "drainage_kg_s":
                indexes = np.array(RESTARTS) - 1
                ax.plot(x[indexes], arrays[key][indexes], linestyle="none", marker="D", markersize=4, color=color)
        for n, letter, _ in EVENTS:
            ax.axvline(n, color="#999999", linestyle="--", linewidth=0.65, zorder=0)
        ax.text(0.985, 1.005, f"({panel})", transform=ax.transAxes, va="bottom", ha="right", fontsize=10)
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
        ax.set_xlim(0, 26000)
    for n, letter, _ in EVENTS:
        # A/B and C/D are close at report width; stagger each pair vertically.
        y = 0.78 if letter in ("B", "D") else 0.95
        axes[0].text(n + 75, y, letter, transform=axes[0].get_xaxis_transform(), va="top", fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "pad": 1})
    axes[0].set_ylabel("Liquid inventory (kg)")
    axes[0].set_ylim(-3, 73)
    axes[0].set_yticks([0, 20, 40, 60])
    axes[0].legend(loc="lower right", ncol=2, fontsize=9.5, frameon=True, borderpad=0.35, handlelength=1.5, columnspacing=1)
    axes[1].set_ylabel("Signed liquid flux\nat steam outlet (kg/s)")
    axes[1].set_ylim(-3.6, 0.2)
    axes[1].set_yticks([-3, -2, -1, 0])
    axes[1].text(0.50, 0.75, "Negative = outward", transform=axes[1].transAxes, fontsize=9.5)
    axes[2].set_ylabel("Film inventory (kg)")
    axes[2].set_ylim(-0.3, 7)
    axes[2].set_yticks([0, 2, 4, 6])
    axes[3].set_ylabel("Film rate (kg/s)")
    axes[3].set_ylim(-4, 86)
    axes[3].set_yticks([0, 40, 80])
    axes[3].legend(loc="lower right", ncol=2, fontsize=9.5, frameon=True, borderpad=0.35, handlelength=1.5, columnspacing=1)
    axes[3].set_xticks(np.arange(0, 25001, 5000))
    axes[3].set_xlabel("Native solver iteration\nBulk fields frozen after D; diamonds mark selected restarts")
    fig.suptitle("Selected startup and frozen-bulk film history", fontsize=12, y=0.98)
    style_axes(axes)
    provenance(fig, "results-described-film-history", checks, {"selected_film_history": sources["selected_film_history"]}, out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    sources = verify_sources()
    startup, startup_checks = startup_arrays()
    film, film_checks = film_arrays()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10.5,
        "axes.labelsize": 10.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "path.simplify": False,
        "agg.path.chunksize": 0,
    })
    draw_startup(startup, startup_checks, sources, args.output_dir)
    draw_film(film, film_checks, sources, args.output_dir)
    print(json.dumps({
        "output_dir": str(args.output_dir.resolve()),
        "source_hashes": "PASS",
        "startup_metric_checks": "PASS",
        "startup_points_per_case": 3000,
        "film_points_per_series": 25815,
        "film_endpoint_and_inventory_checks": "PASS",
        "smoothing_interpolation_or_subsampling": False,
    }, indent=2))


if __name__ == "__main__":
    main()

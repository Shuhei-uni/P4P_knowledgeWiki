"""Reduce recovered analytical-film evidence; no Fluent connection or solve."""
from pathlib import Path
import csv
import hashlib
import json
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "PyAnsys/output/phase72a-stage4-analytical/20261008"
DOC = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/analytical-film"
FILM = re.compile(r"Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)")


def value(v):
    return float(v[0] if isinstance(v, list) else v)


def block(record):
    folder = ROOT / record["local"]
    raw = folder / "raw"
    text = (raw / "solve.trn").read_text()
    printed = np.asarray([tuple(map(float, m.groups())) for m in FILM.finditer(text)])
    count = len(printed)
    assert count
    ids = np.arange(record["start"], record["start"] + count + 1)
    h = {}
    for name in record["report_paths"]:
        rows = {}
        for line in (raw / (name + ".out")).read_text().splitlines():
            parts = line.split()
            if len(parts) == 2 and parts[0].isdigit():
                rows[int(parts[0])] = float(parts[1])
        assert all(int(i) in rows for i in ids[1:]), name
        # Fluent's compute API expands a mass-flow report into source and
        # physical-flux components. Its native file contains physical flux.
        baseline = record["initial_reports"].get(name + "(without-sources)",
                                                   record["initial_reports"][name])
        h[name] = np.asarray([value(baseline)] + [rows[int(i)] for i in ids[1:]])
        assert np.isfinite(h[name]).all()
    dt = printed[:, 1]
    t = np.r_[record["before"]["film"]["film_elapsed_time"], printed[:, 0]]
    changes = {key: float(h["p72d-total-" + key][-1] - h["p72d-total-" + key][0])
               for key in ["mass", "outflow", "stripped", "separated"]}
    inputs = {key: float(np.sum(h["p72d-total-" + key][1:] * dt)) for key in ["secondary", "dpm"]}
    direct = float(np.sum(h["p72d-drain-rate"][:-1] * dt))
    direct_right = float(np.sum(h["p72d-drain-rate"][1:] * dt))
    signed = sum(changes.values()) + direct - sum(inputs.values())
    error = 100 * abs(signed) / max(abs(sum(inputs.values())), 1e-30)
    timing = re.findall(r"Average wall-clock time per iteration:\s*([\deE.+-]+)", text)
    simulation = re.findall(r"Simulation wall-clock time for (\d+) iterations\s+([\deE.+-]+) sec", text)
    bulk_names = ["v2-total-liquid-mass", "v2-flux-phase2-steamoutlet", "v2-flux-phase1-steamoutlet"]
    bulk_history_available = all(name in h for name in bulk_names)
    metrics = {"native_start": int(ids[0]), "native_end": int(ids[-1]), "updates": count,
               "duration_s": float(dt.sum()), "changes_kg": changes, "inputs_kg": inputs,
               "direct_drain_kg": direct, "drain_quadrature_span_kg": abs(direct-direct_right),
               "ledger_signed_residual_kg": signed, "ledger_error_percent": error,
               "ledger_method": "Reported source-rate integral; DPM event deposition not independently reconciled",
               "dpm_tracking_events": len(re.findall(r"DPM Iteration", text)),
               "peak_courant": float(h["p72d-total-courant"].max()),
               "peak_thickness_m": float(h["p72d-total-thickness"].max()),
               "peak_reported_speed_m_s": float(h["p72a-e2.7-ewf-velocity-mag-max"].max()),
               "mean_direct_drain_kg_s": direct / dt.sum(),
               "mean_storage_kg_s": changes["mass"] / dt.sum(),
               "subiteration_rows": len(re.findall(r"sub-iteration:", text)),
               "timer_wall_s_per_iteration": float(timing[-1]) if timing else None,
               "simulation_wall_s": sum(float(seconds) for _, seconds in simulation) if simulation else None,
               "physical_bulk_flux_baseline": "API without-sources component matches native report-file convention",
               "bulk_history_available": bulk_history_available,
               "bulk_unchanged": all(np.array_equal(h[name], np.repeat(h[name][0], len(ids)))
                                     for name in bulk_names) if bulk_history_available else None,
               "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir()},
               "native_classification": record["status"]}
    upper = np.load(folder / "upper-fields.npz")
    speed = np.sqrt(sum(upper["film-" + axis + "-velocity"]**2 for axis in "xyz"))
    mass = upper["film-mass"]
    metrics["endpoint_upper_velocity"] = {
        "mass_weighted_speed_m_s": float(np.sum(mass*speed) / np.sum(mass)),
        "diagnostic_threshold_m_s": 1000,
        "mass_above_threshold_kg": float(mass[speed > 1000].sum()),
        "mass_fraction_above_threshold": float(mass[speed > 1000].sum()/mass.sum()),
        "faces_above_threshold": int((speed > 1000).sum()),
        "thickness_at_fastest_face_m": float(upper["film-thickness"][speed.argmax()]),
        "endpoint_npz_sha256": hashlib.sha256((folder / "upper-fields.npz").read_bytes()).hexdigest()}
    (folder / "analysis.json").write_text(json.dumps(metrics, indent=2) + "\n")
    return metrics, t, h


def main():
    results = {}
    histories = {}
    for arm in ["analytical10", "analytical5", "momentum10"]:
        path = OUT / arm / "run-manifest.json"
        if not path.exists():
            continue
        m = json.loads(path.read_text())
        metrics, times, signals = [], [], {}
        for n, relative in enumerate(m["blocks"]):
            record = json.loads((ROOT / relative / "run-manifest.json").read_text())
            met, t, h = block(record)
            metrics.append(met)
            skip = 0 if n == 0 else 1
            times.extend(t[skip:])
            for name, rows in h.items():
                signals.setdefault(name, []).extend(rows[skip:])
        if metrics:
            changes = {key: sum(met["changes_kg"][key] for met in metrics)
                       for key in metrics[0]["changes_kg"]}
            inputs = {key: sum(met["inputs_kg"][key] for met in metrics)
                      for key in metrics[0]["inputs_kg"]}
            drain = sum(met["direct_drain_kg"] for met in metrics)
            signed = sum(changes.values()) + drain - sum(inputs.values())
            aggregate = {
                "updates": sum(met["updates"] for met in metrics),
                "duration_s": sum(met["duration_s"] for met in metrics),
                "changes_kg": changes, "inputs_kg": inputs,
                "direct_drain_kg": drain, "ledger_signed_residual_kg": signed,
                "ledger_error_percent": 100 * abs(signed) / max(abs(sum(inputs.values())), 1e-30),
                "dpm_tracking_events": sum(met["dpm_tracking_events"] for met in metrics),
                "bulk_unchanged": all(met["bulk_unchanged"] for met in metrics),
                "simulation_wall_s": sum(met["simulation_wall_s"] for met in metrics)
                                     if all(met["simulation_wall_s"] is not None for met in metrics) else None,
                **{key: max(met[key] for met in metrics)
                   for key in ["peak_courant", "peak_thickness_m", "peak_reported_speed_m_s"]},
            }
            results[arm] = {"status": m["status"], "step_s": m["step_s"], "blocks": metrics,
                            "aggregate": aggregate,
                            "added_film_time_s": m["verified_film_time_s"] - m["parent_film_time_s"],
                            "final_native_iteration": m["verified_native_end"]}
            histories[arm] = (np.asarray(times) - m["parent_film_time_s"],
                              {name: np.asarray(v) for name, v in signals.items()})
    (OUT / "comparison-summary.json").write_text(json.dumps(results, indent=2) + "\n")
    if histories:
        figure_dir = DOC / "figures"
        figure_dir.mkdir(parents=True, exist_ok=True)
        fig, grid = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
        axes = grid.ravel()
        names = ["p72d-upper-mass", "p72a-e2.7-ewf-velocity-mag-max", "p72d-drain-rate", "p72d-total-courant"]
        labels = {"analytical10": "Analytical, 10 µs", "analytical5": "Analytical, 5 µs",
                  "momentum10": "Full momentum, 10 µs"}
        for arm, (t, h) in histories.items():
            # Keep the failure comparison at its original short horizon even
            # when the full-momentum control later advances much further.
            stop = results[arm]["blocks"][0]["updates"] + 1
            for ax, name in zip(axes, names):
                ax.plot(t[:stop]*1000, h[name][:stop], label=labels[arm], linewidth=1.2)
        for ax, label in zip(axes, ["Upper-film mass (kg)", "Maximum film speed (m/s)",
                                    "Direct drain (kg/s)", "Maximum film Courant"]):
            ax.set(xlabel="Added accepted film time (ms)", ylabel=label)
            ax.grid(alpha=.2)
        axes[0].legend(fontsize=9)
        axes[1].set_yscale("log")
        axes[3].set_yscale("log")
        axes[3].axhline(1, linestyle="--", color="#555555", linewidth=1)
        fig.suptitle("Short film checks — same parent; frozen bulk")
        fig.savefig(figure_dir / "matched-development.png", dpi=180)
        plt.close(fig)
        if "momentum10" in histories and len(results["momentum10"]["blocks"]) > 1:
            t, h = histories["momentum10"]
            fig, grid = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
            names = ["p72d-total-mass", "p72a-e2.7-ewf-velocity-mag-max",
                     "p72d-drain-rate", "p72d-total-courant"]
            labels = ["Total film mass (kg)", "Maximum film speed (m/s)",
                      "Direct drain (kg/s)", "Maximum film Courant"]
            for ax, name, label in zip(grid.ravel(), names, labels):
                ax.plot(t*1000, h[name], color="#2ca02c", linewidth=1.2)
                ax.set(xlabel="Added accepted film time (ms)", ylabel=label)
                ax.grid(alpha=.2)
            grid[1, 1].axhline(1, linestyle="--", color="#555555", linewidth=1)
            fig.suptitle("Full momentum, 10 µs — same parent; frozen bulk")
            fig.savefig(figure_dir / "momentum-control.png", dpi=180)
            plt.close(fig)
    print(json.dumps({arm: {k: v for k, v in data["blocks"][-1].items() if k != "source_sha256"}
                      for arm, data in results.items()}, indent=2))


if __name__ == "__main__":
    main()

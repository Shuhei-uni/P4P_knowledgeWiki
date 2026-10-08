"""Offline cadence/source-accounting screen; preserve the original ledger."""
from pathlib import Path
import hashlib
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from analyze_phase72a_stage4_analytical import block, FILM

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "PyAnsys/output/phase72a-stage4-dpm-cadence/20261008"
DOC = ROOT / "Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/dpm-cadence"
CONTROL = ROOT / "PyAnsys/output/phase72a-stage4-report-cost/20261008/core17/run-N41503-N42503"


def event_positions(text):
    """Associate each native tracking message with the following film update."""
    updates, pending, positions = 0, False, []
    for line in text.splitlines():
        if "DPM Iteration" in line:
            if pending:
                raise ValueError("Two tracking events without an intervening film update")
            pending = True
        if FILM.search(line):
            updates += 1
            if pending:
                positions.append(updates)
                pending = False
    if pending:
        raise ValueError("Tracking event lacks a reported film update")
    return positions


def reduce(folder):
    record = json.loads((folder / "run-manifest.json").read_text())
    met, t, h = block(record)
    text = (folder / "raw/solve.trn").read_text()
    dt = np.asarray([float(match[1]) for match in FILM.findall(text)])
    events = event_positions(text)
    stocks = sum(np.diff(h["p72d-total-" + key]) for key in ("mass", "outflow", "stripped", "separated"))
    residual = stocks + h["p72d-drain-rate"][:-1] * dt - (h["p72d-total-secondary"][1:] + h["p72d-total-dpm"][1:]) * dt
    assert np.isclose(residual.sum(), met["ledger_signed_residual_kg"], atol=1e-12)
    cadence = record["before"]["parameters"]["iters-per-dpm-step"]
    if len(events) > 1:
        assert np.all(np.diff(events) == cadence)
    dpm = met["inputs_kg"]["dpm"]
    met.update(nominal_film_steps_per_dpm_step=cadence,
               observed_tracking_update_positions=events,
               residual_fraction_of_reported_dpm_input=met["ledger_signed_residual_kg"] / dpm,
               hypothesis_inverse_cadence=1 / cadence,
               hypothesis_remaining_difference_kg=met["ledger_signed_residual_kg"] - dpm / cadence,
               residual_at_tracking_updates_kg=float(residual[np.asarray(events, dtype=int) - 1].sum()),
               bulk_endpoints_unchanged=record["before"]["bulk"] == record["final"]["bulk"],
               parameters_unchanged_during_solve=record["before"]["parameters"] == record["final"]["parameters"],
               source_manifest_sha256=hashlib.sha256((folder / "run-manifest.json").read_bytes()).hexdigest())
    return met, t, h, residual


def main():
    arms = {"dpm20": reduce(CONTROL)}
    manifest = OUT / "dpm40/run-manifest.json"
    if manifest.exists():
        m = json.loads(manifest.read_text())
        if m["blocks"]:
            assert len(m["blocks"]) == 1
            arms["dpm40"] = reduce(ROOT / m["blocks"][0])
    comparison = {}
    if "dpm40" in arms:
        a, b = arms["dpm20"][0], arms["dpm40"][0]
        assert a["native_start"] == b["native_start"] == 41503
        assert a["updates"] == b["updates"] == 1000
        assert np.isclose(a["duration_s"], b["duration_s"], atol=1e-12)
        comparison = {
            "residual_fraction_ratio_40_to_20": b["residual_fraction_of_reported_dpm_input"] / a["residual_fraction_of_reported_dpm_input"],
            "hypothesis_ratio": 0.5,
            "film_gain_relative_change": b["changes_kg"]["mass"] / a["changes_kg"]["mass"] - 1,
            "drain_relative_change": b["direct_drain_kg"] / a["direct_drain_kg"] - 1,
            "reported_dpm_input_relative_change": b["inputs_kg"]["dpm"] / a["inputs_kg"]["dpm"] - 1,
            "whole_command_time_reduction_percent": 100 * (1 - b["simulation_wall_s"] / a["simulation_wall_s"]),
            "claim_limit": "A cadence trend cannot determine particle mass actually applied or justify correcting the ledger",
        }
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
        for label, (met, t, h, residual) in arms.items():
            axes[0].plot((t - t[0]) * 1000, np.r_[0, np.cumsum(residual)] * 1000, label=label)
            axes[1].plot((t - t[0]) * 1000, h["p72d-total-mass"] - h["p72d-total-mass"][0], label=label)
        for ax, ylabel in zip(axes, ["Cumulative ledger residual (g)", "Film mass gain (kg)"]):
            ax.set(xlabel="Added accepted film time (ms)", ylabel=ylabel)
            ax.grid(alpha=.2)
        axes[0].legend()
        fig.suptitle("DPM cadence contrast — unchanged film physics and 10 µs step")
        d = DOC / "figures"; d.mkdir(parents=True, exist_ok=True)
        fig.savefig(d / "cadence-accounting.png", dpi=180); plt.close(fig)
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"status": "CADENCE_COMPARISON" if len(arms) == 2 else "CONTROL_ONLY",
               "arms": {name: met for name, (met, *_rest) in arms.items()}, "comparison": comparison,
               "ledger_correction_applied": False,
               "required_proof": "Native deposited particle mass and its source normalization interval, independently reconciled"}
    (OUT / "comparison-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if len(arms) == 2:
        plot = DOC / "figures/cadence-accounting.png"
        provenance = {
            "figure_sha256": hashlib.sha256(plot.read_bytes()).hexdigest(),
            "analysis_summary_sha256": hashlib.sha256((OUT / "comparison-summary.json").read_bytes()).hexdigest(),
            "source_manifest_sha256": {name: met["source_manifest_sha256"] for name, (met, *_rest) in arms.items()},
            "source_window": [41503, 42503], "film_step_s": 1e-5,
            "ledger": "Delta film + cumulative loss stocks + left-step direct drain - right-step reported phase/DPM source rates",
            "quantities": {"x": "Accepted added film time, ms", "left": "Cumulative uncorrected ledger residual, g", "right": "Film mass gain, kg"},
            "claim_limit": "No event-mass conservation proof; no ledger correction applied",
        }
        plot.with_suffix('.provenance.json').write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "comparison": comparison,
                      "arms": {name: {key: met[key] for key in ["ledger_error_percent", "residual_fraction_of_reported_dpm_input", "observed_tracking_update_positions", "simulation_wall_s"]} for name, (met, *_rest) in arms.items()}}, indent=2))


if __name__ == "__main__":
    main()

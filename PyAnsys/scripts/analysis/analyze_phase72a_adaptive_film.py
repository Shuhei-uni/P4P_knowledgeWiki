"""Plot measured adaptive film time, rates and numerical controls from native evidence."""
from pathlib import Path
import argparse
import csv
import json
import re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/phase72a-adaptive-server1/20261005"


def recovered_analysis(bundle):
    """Use complete reports and reconcile the lost transcript tail against native state."""
    source = bundle.parent
    manifest = json.loads((source / "run-manifest.json").read_text())
    state = dict(json.loads((bundle / "native-film-solution-state.json").read_text()))
    reference = json.loads((source / "prepared-reopen.json").read_text())
    histories = {}
    for file in sorted((bundle / "reports").glob("*.out")):
        data = {}
        for line in file.read_text().splitlines():
            fields = line.split()
            if len(fields) == 2 and fields[0].isdigit():
                i, value = int(fields[0]), float(fields[1])
                if i in data and data[i] != value:
                    raise ValueError(f"Conflicting duplicate report: {file.name} N{i}")
                data[i] = value
        histories[file.stem] = data
    mass = histories["p72a-e2.7-ewf-film-mass-total"]
    ids = np.asarray(sorted(mass))
    start, end = int(ids[0]), int(ids[-1])
    if len(histories) != 29 or not np.array_equal(ids, np.arange(start, end + 1)):
        raise ValueError("Incomplete report set or coordinates")
    if any(set(h) != set(ids) for h in histories.values()):
        raise ValueError("Report coverage differs")
    values = lambda name: np.asarray([histories[name][int(i)] for i in ids])
    cfl = values("p72a-e2.7-ewf-courant-max")
    parameters = reference["film_parameters"]
    target = parameters["courant-number"]
    steps = []
    dt = parameters["adapt-init-dt"]
    for solved_cfl in cfl[1:]:
        steps.append(dt)
        if solved_cfl > target:
            dt /= parameters["adapt-tstp-dec"]
        elif solved_cfl < target / 2:
            dt *= parameters["adapt-tstp-inc"]
    steps = np.asarray(steps)
    # The parent clock was independently verified in its saved data settings.
    parent_clock = 0.1000000000000217
    exact_clock = np.r_[parent_clock, parent_clock + np.cumsum(steps)]
    if abs(exact_clock[-1] - state["film_elapsed_time"]) > 1e-10:
        raise ValueError("CFL-controller reconstruction does not match exact native endpoint clock")
    if abs(steps[-1] - state["film_timestep"]) > 1e-15:
        raise ValueError("Reconstructed step differs from native endpoint step")
    if state["max_timestep_count"] - 28000 != end - start:
        raise ValueError("Native saved film-step count differs from report horizon")
    observed = {int(k): v for k, v in json.loads((source / "film-clock-history.json").read_text()).items()}
    text = (source / "batch-N44606-N45606.txt").read_text()
    film = re.compile(r"Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)")
    row = re.compile(r"^\s*(\d+)\s+[\d.+-]+e[+-]\d+\s+")
    pending = None
    for line in text.splitlines():
        match = film.search(line)
        if match:
            pending = [float(v) for v in match.groups()]
        elif row.match(line) and pending is not None:
            observed[int(row.match(line)[1])] = pending
            pending = None
    stream_errors = []
    for i, record in observed.items():
        pos = i - start
        if not 1 <= pos < len(ids):
            raise ValueError("Observed film coordinate outside recovered report horizon")
        error = abs(exact_clock[pos] - record[0])
        stream_errors.append(error)
        if error > 5.1e-8 or abs(steps[pos - 1] - record[1]) > 5.1e-9:
            raise ValueError(f"Reconstructed native time/step conflicts with stream at N{i}")
    if set(observed) != set(range(start + 1, max(observed) + 1)):
        raise ValueError("Unexpected transcript gap before the final lost tail")
    native_time = exact_clock
    time_ms = (0.02 + native_time - parent_clock) * 1000
    inventory = values("p72a-e2.7-ewf-film-mass-total")
    thickness = values("p72a-e2.7-ewf-thickness-max")
    drainage = values("p72a-e2.7-ewf-outflow-mass-total")
    accrete = values("p72a-e2.7-ewf-secondary-phase-mass-total")
    carrier = values("v2-total-liquid-mass")
    outflow = -values("v2-flux-phase2-steamoutlet")

    def window(lo, hi):
        elapsed = native_time[hi] - native_time[lo]
        collected = float(np.sum(accrete[lo + 1:hi + 1] * steps[lo:hi]))
        gain = float(inventory[hi] - inventory[lo])
        drained = float(drainage[hi] - drainage[lo])
        return {"native_start": int(ids[lo]), "native_end": int(ids[hi]),
                "film_elapsed_s": float(elapsed), "inventory_gain_kg": gain,
                "inventory_growth_kg_s": gain / elapsed,
                "integrated_accretion_kg": collected, "mean_accretion_kg_s": collected / elapsed,
                "drained_mass_kg": drained, "mean_drainage_kg_s": drained / elapsed,
                "drainage_deficit_percent": 100 * (collected - drained) / collected,
                "film_ledger_error_percent": 100 * abs(gain + drained - collected) / collected,
                "maximum_thickness_m": float(thickness[lo:hi + 1].max())}

    windows = [window(lo, lo + 1000) for lo in range(20, len(ids) - 1000, 1000)]
    overall = window(0, len(ids) - 1)
    summary = {"status": "RECOVERED_AND_ANALYSED_N45606", "native_window": [start, end],
        "native_updates": end - start, "report_count": len(histories), "report_points_each": len(ids),
        "adaptive_elapsed_s": float(state["film_elapsed_time"] - parent_clock),
        "total_added_film_time_since_corrected_E27_s": float(0.02 + state["film_elapsed_time"] - parent_clock),
        "film_inventory_start_kg": float(inventory[0]), "film_inventory_end_kg": float(inventory[-1]),
        "film_inventory_gain_percent": float(100 * (inventory[-1] / inventory[0] - 1)),
        "maximum_thickness_start_m": float(thickness[0]), "maximum_thickness_end_m": float(thickness[-1]),
        "peak_maximum_thickness_m": float(thickness.max()),
        "bulk_liquid_start_kg": float(carrier[0]), "bulk_liquid_end_kg": float(carrier[-1]),
        "phase2_outlet_start_kg_s": float(outflow[0]), "phase2_outlet_end_kg_s": float(outflow[-1]),
        "final_1000_outlet_mean_kg_s": float(outflow[-1000:].mean()),
        "accepted_step_initial_s": float(steps[0]), "accepted_step_final_s": float(steps[-1]),
        "peak_film_cfl": float(cfl[1:].max()), "final_film_cfl": float(cfl[-1]),
        "overall": overall, "windows_1000_updates": windows,
        "time_recovery": {"directly_mapped_stream_updates": len(observed),
            "reconstructed_tail_updates": end - max(observed), "last_mapped_stream_iteration": max(observed),
            "native_endpoint_clock_s": state["film_elapsed_time"],
            "native_step_count_increment": state["max_timestep_count"] - 28000,
            "max_stream_clock_rounding_error_s": max(stream_errors),
            "endpoint_clock_reconstruction_error_s": float(exact_clock[-1] - state["film_elapsed_time"]),
            "method": "Complete native CFL reports and verified adaptive control law; exact endpoint clock, step and count validate reconstruction",
            "limitation": "Last 233 updates lack client transcript; no complete final-tail residual or no-event claim"},
        "execution": {"controller_failure": "gRPC stream timeout", "solver_completed_native_batch": end,
            "requested_total_added_film_horizon_s": 0.05, "requested_horizon_reached": False},
        "steady_film": False, "claim_limit": "Film-side numerical development; full separator closure and physical validity unqualified"}
    (bundle / "analysis-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (bundle / "window-summary.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(windows[0]));writer.writeheader();writer.writerows(windows)
    with (bundle / "film-history.csv").open("w", newline="") as f:
        writer = csv.writer(f);writer.writerow(["native_iteration", "native_film_clock_s", "added_film_time_since_E27_s", "accepted_step_s", "clock_evidence", "film_inventory_kg", "maximum_thickness_m", "accretion_kg_s", "cumulative_drainage_kg", "film_cfl"])
        for j, i in enumerate(ids):
            writer.writerow([i, native_time[j], time_ms[j] / 1000, "" if j == 0 else steps[j - 1],
                "parent" if j == 0 else "stream-validated control-law reconstruction" if i in observed else "tail reconstructed and exact-endpoint validated",
                inventory[j], thickness[j], accrete[j], drainage[j], cfl[j]])
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    axes[0, 0].plot(time_ms, inventory, color="#276B9D")
    axes[0, 0].set_ylabel("Film inventory (kg)")
    axes[0, 1].plot(time_ms, 1000 * thickness, color="#276B9D")
    axes[0, 1].set_ylabel("Maximum film thickness (mm)")
    axes[1, 0].plot(time_ms, accrete, label="Native accretion", color="#276B9D", linewidth=0.7, alpha=0.75)
    rate_window = 100
    drainage_rate = (drainage[rate_window:] - drainage[:-rate_window]) / (native_time[rate_window:] - native_time[:-rate_window])
    axes[1, 0].plot(time_ms[rate_window:], drainage_rate, color="#B87520", label="Drainage, trailing 100 updates")
    axes[1, 0].set_ylabel("Accretion / drainage (kg/s)");axes[1, 0].legend(fontsize=9)
    rate_window = 1000
    storage_rate = (inventory[rate_window:] - inventory[:-rate_window]) / (native_time[rate_window:] - native_time[:-rate_window])
    axes[1, 1].plot(time_ms[rate_window:], storage_rate, color="#276B9D", label="Storage, trailing 1,000 updates")
    axes[1, 1].axhline(0, color="#555555", linestyle="--", label="Zero storage")
    axes[1, 1].set_ylabel("Film inventory growth (kg/s)");axes[1, 1].legend(fontsize=9);axes[1, 1].set_ylim(bottom=0)
    for axis in axes.flat:
        axis.set_xlabel("Added film time since corrected E2.7 restart (ms)");axis.grid(alpha=0.2)
        axis.ticklabel_format(axis="y", style="plain", useOffset=False)
    fig.suptitle(f"Adaptive film to N{end}: drainage improves, inventory still grows")
    fig.savefig(bundle / "adaptive-film-histories.png", dpi=170);fig.savefig(bundle / "adaptive-film-histories.pdf");plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), layout="constrained", sharex=True)
    cutoff = max(observed) - start
    axes[0].step(time_ms[1:cutoff + 1], steps[:cutoff] * 1e6, where="post", label="Recorded timestep")
    axes[0].step(time_ms[cutoff:], np.r_[steps[cutoff - 1], steps[cutoff:]] * 1e6, where="post", color="#B87520", linestyle="--", label="Recovered final 233 updates")
    axes[0].set_ylabel("Accepted film step (µs)");axes[0].legend(fontsize=9)
    axes[1].plot(time_ms[1:], cfl[1:], label="Complete native CFL report")
    axes[1].axhline(target, color="#B87520", linestyle="--", label="Courant target 0.05")
    axes[1].axhline(target / 2, color="#777777", linestyle=":", label="Step increase threshold 0.025")
    axes[1].set_ylabel("Maximum film CFL");axes[1].legend(fontsize=9)
    for axis in axes:
        axis.grid(alpha=0.2)
    axes[1].set_xlabel("Added film time since corrected E2.7 restart (ms)")
    fig.savefig(bundle / "adaptive-step-cfl.png", dpi=170);fig.savefig(bundle / "adaptive-step-cfl.pdf");plt.close(fig)
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.5), layout="constrained", sharex=True)
    axes[0].plot(time_ms, carrier, alpha=0.4, linewidth=0.6, label="Native report")
    axes[0].set_ylabel("Bulk liquid inventory (kg)")
    axes[1].plot(time_ms, outflow, alpha=0.4, linewidth=0.6, label="Native report")
    axes[1].set_ylabel("Liquid carryover at steam outlet (kg/s)")
    for axis, series in zip(axes, [carrier, outflow]):
        mean = np.convolve(series, np.ones(1000) / 1000, mode="valid")
        axis.plot(time_ms[999:], mean, color="#222222", linewidth=1, label="Mean over 1,000 updates")
        axis.legend(fontsize=9)
    axes[1].set_xlabel("Added film time since corrected E2.7 restart (ms)")
    for axis in axes:
        axis.grid(alpha=0.2);axis.ticklabel_format(axis="y", style="plain", useOffset=False)
    fig.suptitle("Bulk liquid inventory and liquid carryover")
    fig.savefig(bundle / "carrier-histories.png", dpi=170);fig.savefig(bundle / "carrier-histories.pdf");plt.close(fig)
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recovered-bundle", type=Path)
    args = parser.parse_args()
    if args.recovered_bundle:
        recovered_analysis(args.recovered_bundle)
        return
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

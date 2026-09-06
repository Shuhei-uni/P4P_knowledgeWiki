"""Create the predeclared P6 discovery numerical-adequacy figure from residual JSONs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-paths", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run_paths = yaml.safe_load(args.run_paths.read_text(encoding="utf-8"))
    root = args.run_paths.resolve().parents[4]
    records = []
    for run in run_paths["runs"]:
        path = root / run["residual_history"]
        data = json.loads(path.read_text(encoding="utf-8"))
        if data["point_count"] != 551 or data["iterations"] != list(range(15000, 15551)):
            raise RuntimeError(f"invalid native residual history: {path}")
        if any(len(values) != 551 for values in data["series"].values()):
            raise RuntimeError(f"unaligned residual history: {path}")
        records.append((run["case_id"], data, str(path)))
    curves = list(records[0][1]["series"])
    if any(list(data["series"]) != curves for _, data, _ in records):
        raise RuntimeError("residual curve layouts differ between discovery cases")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(4, 2, figsize=(14, 16), sharex=True, constrained_layout=True)
    for axis, curve in zip(axes.flat, curves):
        for case_id, data, _ in records:
            axis.semilogy(data["iterations"], data["series"][curve], linewidth=0.9, label=case_id)
        axis.set_title(curve)
        axis.set_ylabel("Scaled residual")
        axis.grid(True, which="both", alpha=0.25)
    axes.flat[-1].axis("off")
    axes.flat[0].legend(fontsize=8, ncol=2)
    for axis in axes.flat[:-1]:
        axis.set_xlabel("Native iteration")
    fig.suptitle("F3 numerical adequacy: Phase 06 discovery scaled residuals", fontsize=15)
    png = args.output_dir / "F3_numerical_adequacy_residuals.png"
    fig.savefig(png, dpi=180)
    plt.close(fig)
    summary = {"figure": str(png), "cases": {}}
    for case_id, data, path in records:
        summary["cases"][case_id] = {
            "source": path,
            "native_coordinate": [data["iterations"][0], data["iterations"][-1]],
            "unique_samples": data["point_count"],
            "raw_rows": data["raw_row_count"],
            "duplicates_removed": data["verified_duplicate_boundary_rows_removed"],
            "final_residuals": {name: values[-1] for name, values in data["series"].items()},
            "final_100_mean": {name: sum(values[-100:]) / 100 for name, values in data["series"].items()},
        }
    (args.output_dir / "F3_numerical_adequacy_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figure": str(png), "cases": len(records), "curves": len(curves)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

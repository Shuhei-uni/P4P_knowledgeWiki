#!/usr/bin/env python3
"""Compare saved Phase 8 F3 particle fates before and after a tracking-step probe."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


FATES = ("escaped", "trapped", "incomplete")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def fate_counts(result: dict) -> dict[str, int]:
    counts = result["counts"]
    tracked = int(counts["tracked"])
    require(tracked > 0, f"No trajectories in {result['name']}")
    require(sum(int(counts[fate]) for fate in FATES) == tracked,
            f"Unaccounted trajectory fate in {result['name']}")
    return {fate: int(counts[fate]) for fate in FATES} | {"tracked": tracked}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("carrier_manifest", type=Path)
    parser.add_argument("probe_receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    carrier = json.loads(args.carrier_manifest.read_text(encoding="utf-8"))
    probe = json.loads(args.probe_receipt.read_text(encoding="utf-8"))
    require(carrier["status"] == "COMPLETE" and carrier["tracking_status"] == "COMPLETE",
            "Carrier tracking is incomplete")
    require(probe["status"] == "COMPLETE", "Probe tracking is incomplete")
    endpoint = carrier["checkpoints"][-1]
    require(probe["source_case_sha256"] == endpoint["case_sha256"] and
            probe["source_data_sha256"] == endpoint["data_sha256"],
            "Probe and carrier endpoints differ")
    require(probe["tracking_before"]["max_num_steps"] == 50000 and
            probe["tracking_after"]["max_num_steps"] == probe["max_steps"],
            "Tracking-step readback mismatch")
    flows = carrier["source_readback"]["dpm_flows_kg_s"]
    baseline = {item["name"]: item for item in carrier["particle_tracks"]["results"]}
    changed = {item["name"]: item for item in probe["results"]}
    require(set(flows) == set(baseline) == set(changed), "All seven injection bins are required")
    rows = []
    totals = {tag: {fate: 0.0 for fate in FATES} for tag in ("baseline", "probe")}
    for name, feed in flows.items():
        require(feed > 0, f"Invalid feed for {name}")
        before, after = fate_counts(baseline[name]), fate_counts(changed[name])
        require(before["tracked"] == after["tracked"], f"Track count changed for {name}")
        for tag, counts in (("baseline", before), ("probe", after)):
            for fate in FATES:
                totals[tag][fate] += feed * counts[fate] / counts["tracked"]
        rows.append({"name": name, "feed_kg_s": feed,
                     "baseline_50000_counts": before,
                     f"probe_{probe['max_steps']}_counts": after})
    total_feed = sum(flows.values())
    result = {
        "carrier_manifest": str(args.carrier_manifest),
        "probe_receipt": str(args.probe_receipt),
        "max_steps": probe["max_steps"],
        "feed_kg_s": total_feed,
        "bins": rows,
        "represented_fate_kg_s": totals,
        "represented_fate_fraction": {
            tag: {fate: rate / total_feed for fate, rate in rates.items()}
            for tag, rates in totals.items()
        },
        "claim_limit": "Tracking-step sensitivity is postprocessing evidence only; incomplete trajectories remain unresolved and the carrier field is unchanged.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

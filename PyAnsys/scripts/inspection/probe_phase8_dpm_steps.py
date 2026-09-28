#!/usr/bin/env python3
"""Probe whether a higher DPM step cap resolves incomplete Phase 8 tracks."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup"),
                str(ROOT / "scripts" / "inspection")]

from ansys.fluent.core import launch_fluent
from pyansys_fluent.common import safe_get_state
from build_phase8_purnanto_parity_pilots import pair, sha256
from run_phase8_parity_carrier import dump, load_pair, require
from run_dpm_particle_tracks import (
    configure_particle_track_summary, discover_live_injections, execute_tui,
    track_one_injection,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child-receipt", type=Path, required=True)
    parser.add_argument("--max-steps", type=int, default=200000)
    parser.add_argument("--bin", action="append", default=["09cv3-finemist-14um"])
    args = parser.parse_args()
    require(50000 < args.max_steps <= 500000, "Probe cap must be above 50k and at most 500k")
    child = json.loads(args.child_receipt.read_text(encoding="utf-8"))
    require(child["status"] == "CASE_DATA_VERIFIED" and child.get("tracking_status") == "COMPLETE",
            "Reference diagnostic child or its tracking record is incomplete")
    base = Path(child["child_base"])
    for kind, path in zip(("case", "data"), pair(base)):
        require(path.is_file(), f"Missing child {kind} pair")
        require(sha256(path) == child["child_pair"][f"{kind}_sha256"], f"Child {kind} hash changed")
    label = f"F2-26p81-dpm-maxsteps-{args.max_steps}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    output = ROOT / "output" / "phase8-dpm" / label / "probe.json"
    receipt = {"status": "RUNNING", "source_receipt": str(args.child_receipt),
               "source_case_sha256": child["child_pair"]["case_sha256"],
               "source_data_sha256": child["child_pair"]["data_sha256"],
               "max_steps": args.max_steps, "bins": args.bin, "results": []}
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double", processor_count=4,
                           ui_mode="gui", start_timeout=240, cleanup_on_exit=True, start_transcript=True)
    try:
        load_pair(solver, base)
        tracking = solver.settings.setup.models.discrete_phase.tracking
        receipt["tracking_before"] = safe_get_state(tracking, "tracking before")
        require(receipt["tracking_before"]["max_num_steps"] == 50000,
                "Reference child step cap changed")
        tracking.max_num_steps = args.max_steps
        receipt["tracking_after"] = safe_get_state(tracking, "tracking after")
        require(receipt["tracking_after"]["max_num_steps"] == args.max_steps,
                "Tracking-step readback failed")
        receipt["report_controls"] = configure_particle_track_summary(solver)
        execute_tui(solver, "/report/dpm-zone-summaries-per-injection? yes")
        receipt["report_controls"]["per_injection_zone_summaries"] = True
        injection_map = {item["name"]: item for item in discover_live_injections(solver)}
        for name in args.bin:
            require(name in injection_map, f"Missing requested probe bin: {name}")
            receipt["results"].append(track_one_injection(solver, injection_map[name]))
            dump(output, receipt)
        receipt["status"] = "COMPLETE" if all(item["status"] == "ok" for item in receipt["results"]) else "PARTIAL"
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(output, receipt)
        solver.exit()
    print(json.dumps({"status": receipt["status"], "probe": str(output),
                      "counts": {r["name"]: r["counts"] for r in receipt["results"]}}, indent=2))


if __name__ == "__main__":
    main()

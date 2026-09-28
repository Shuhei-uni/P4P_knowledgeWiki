#!/usr/bin/env python3
"""Recover per-boundary DPM fates from a saved Phase 8 diagnostic child."""
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
from run_dpm_particle_tracks import run_dpm_particle_track_check
from run_phase8_parity_carrier import dump, load_pair, pair, require, sha256


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("child_receipt", type=Path)
    args = parser.parse_args()
    child = json.loads(args.child_receipt.read_text(encoding="utf-8"))
    require(child["status"] == "CASE_DATA_VERIFIED" and child["mode"] == "diagnostic" and
            child["family"] in ("F1", "F2"), "Expected a verified one-way diagnostic child")
    base = Path(child["child_base"])
    for kind, path in zip(("case", "data"), pair(base)):
        require(path.is_file() and sha256(path) == child["child_pair"][f"{kind}_sha256"],
                f"Diagnostic {kind} identity changed")
    label = (f"{child['family']}-26p81-dpm-zone-retrack-"
             f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    output = ROOT / "output" / "phase8-dpm" / label / "retrack.json"
    receipt = {"status": "RUNNING", "source_receipt": str(args.child_receipt),
               "source_case_sha256": child["child_pair"]["case_sha256"],
               "source_data_sha256": child["child_pair"]["data_sha256"],
               "zone_summaries": True, "tracking_control_changed": False}
    dump(output, receipt)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double",
                           processor_count=4, ui_mode="gui", start_timeout=240,
                           cleanup_on_exit=True, start_transcript=True)
    try:
        load_pair(solver, base)
        receipt["particle_tracks"] = run_dpm_particle_track_check(
            solver, run_label=label, order="diameter-ascending", keep_going=True,
            zone_summaries=True)
        receipt["status"] = "COMPLETE" if all(
            item.get("status") == "ok" for item in receipt["particle_tracks"]["results"]
        ) else "PARTIAL"
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(output, receipt)
        solver.exit()
    print(json.dumps({"status": receipt["status"], "receipt": str(output)}, indent=2))


if __name__ == "__main__":
    main()

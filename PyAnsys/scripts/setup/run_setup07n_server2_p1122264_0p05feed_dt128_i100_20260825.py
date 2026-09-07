#!/usr/bin/env python3
"""Second pressure retarget for the bounded 0.05%-feed drainage diagnostic."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "setup"))

import run_setup07n_c_pressure_response_sign_probe as probe  # noqa: E402
import run_setup07n_server2_target_pressure_0p05feed_matched_dt128_inner100_20260825 as source  # noqa: E402


RUN_LABEL = "brine620k_07n_s2_p1122264_0p05feed_dt128_i100_s10_a1_20260825"
TARGET_PRESSURE_PA = 1_122_263.6212370484


def rewrite_pressure_provenance() -> None:
    run_root = probe.PROJECT_ROOT / "output" / probe.STUDY_ID / RUN_LABEL
    path = run_root / "campaign_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.update(
        {
            "one_factor_change": (
                "relative to completed p1122246 0.05%-feed run: brine pressure "
                "1122246.4660643323 -> 1122263.6212370484 Pa only"
            ),
            "pressure_interpolation": {
                "pressure_pa": TARGET_PRESSURE_PA,
                "target_outward_liquid_kgs": source.TARGET_LIQUID_DRAIN_KGS,
                "basis": (
                    "linear interpolation of the two completed 0.05%-feed "
                    "pressure responses at 1122207.446 and 1122246.466 Pa"
                ),
                "plant_boundary_validated": False,
            },
        }
    )
    probe.write_json(path, payload)


def main() -> int:
    source.RUN_LABEL = RUN_LABEL
    source.TARGET_PRESSURE_PA = TARGET_PRESSURE_PA
    result = source.main()
    rewrite_pressure_provenance()
    return result


if __name__ == "__main__":
    raise SystemExit(main())

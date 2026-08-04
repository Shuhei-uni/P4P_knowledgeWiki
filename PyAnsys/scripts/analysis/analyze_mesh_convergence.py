#!/usr/bin/env python3
"""Analyze a completed three-level carrier-field mesh study.

Input CSV columns:
level,cells,domain_volume,metric,value

Levels must be coarse, medium, and fine. The script computes characteristic
size, adjacent percentage changes, observed order, Richardson extrapolation,
and GCI when the sequence is monotonic and mathematically usable.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

LEVELS = ("coarse", "medium", "fine")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("input_csv", type=Path)
    result.add_argument("--output-csv", type=Path, required=True)
    result.add_argument("--output-json", type=Path, required=True)
    return result


def load_rows(path: Path) -> dict[str, dict[str, dict[str, float]]]:
    grouped: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            level = row["level"].strip().lower()
            if level not in LEVELS:
                raise ValueError(f"Unsupported level {level!r}")
            cells = int(row["cells"])
            volume = float(row["domain_volume"])
            if cells <= 0 or volume <= 0:
                raise ValueError("cells and domain_volume must be positive")
            grouped[row["metric"].strip()][level] = {
                "cells": float(cells),
                "volume": volume,
                "h": (volume / cells) ** (1.0 / 3.0),
                "value": float(row["value"]),
            }
    for metric, levels in grouped.items():
        missing = set(LEVELS) - set(levels)
        if missing:
            raise ValueError(f"{metric}: missing levels {sorted(missing)}")
    return grouped


def analyze(metric: str, levels: dict[str, dict[str, float]]) -> dict[str, object]:
    c, m, f = (levels[level] for level in LEVELS)
    if not (c["h"] > m["h"] > f["h"]):
        return {"metric": metric, "status": "invalid_grid_order"}

    r21 = m["h"] / f["h"]
    r32 = c["h"] / m["h"]
    e21 = m["value"] - f["value"]
    e32 = c["value"] - m["value"]
    pct_cm = abs(e32 / m["value"]) * 100 if m["value"] else math.nan
    pct_mf = abs(e21 / f["value"]) * 100 if f["value"] else math.nan
    monotonic = e21 * e32 > 0

    result: dict[str, object] = {
        "metric": metric,
        "status": "percentage_change_only",
        "coarse": c["value"],
        "medium": m["value"],
        "fine": f["value"],
        "h_coarse": c["h"],
        "h_medium": m["h"],
        "h_fine": f["h"],
        "r_coarse_medium": r32,
        "r_medium_fine": r21,
        "pct_coarse_medium": pct_cm,
        "pct_medium_fine": pct_mf,
        "monotonic": monotonic,
    }
    if not monotonic or not e21 or not e32:
        return result

    # Closed-form p is valid for nearly uniform refinement. Nonuniform
    # sequences require a nonlinear solve and are conservatively not promoted.
    if abs(r21 - r32) / ((r21 + r32) / 2) > 0.05:
        result["status"] = "nonuniform_refinement_percentage_only"
        return result

    r = (r21 + r32) / 2
    ratio = abs(e32 / e21)
    if ratio <= 0 or r <= 1:
        return result
    p = math.log(ratio) / math.log(r)
    if not math.isfinite(p) or p <= 0:
        result["status"] = "unusable_observed_order"
        return result

    extrapolated = f["value"] + (f["value"] - m["value"]) / (r**p - 1)
    ea21 = abs((f["value"] - m["value"]) / f["value"]) if f["value"] else math.nan
    ea32 = abs((m["value"] - c["value"]) / m["value"]) if m["value"] else math.nan
    gci21 = 1.25 * ea21 / (r**p - 1) * 100
    gci32 = 1.25 * ea32 / (r**p - 1) * 100
    asymptotic_ratio = gci32 / (gci21 * r**p) if gci21 else math.nan
    result.update(
        {
            "status": "gci_computed",
            "observed_order": p,
            "richardson_extrapolated": extrapolated,
            "gci_fine_percent": gci21,
            "gci_medium_percent": gci32,
            "asymptotic_ratio": asymptotic_ratio,
        }
    )
    return result


def main() -> int:
    args = parser().parse_args()
    results = [analyze(metric, levels) for metric, levels in load_rows(args.input_csv).items()]
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in results for key in row})
    with args.output_csv.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
    args.output_json.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


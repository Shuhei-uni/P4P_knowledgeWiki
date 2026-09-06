"""Rebuild one P6 discovery residual JSON from its preserved Fluent transcript.

This is an execution-evidence repair utility.  It does not connect to Fluent,
mutate a case, interpolate samples, or manufacture values: it parses the
native rows already retained in the transcript and refuses a misaligned or
unexpected horizon.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "setup"
sys.path.insert(0, str(SCRIPT_DIR))
from run_p6_discovery_case import parse_native_residual_transcript  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-unique-points", type=int, required=True)
    parser.add_argument("--expected-raw-rows", type=int, required=True)
    parser.add_argument("--expected-start", type=int, required=True)
    parser.add_argument("--expected-end", type=int, required=True)
    args = parser.parse_args()

    transcript = args.transcript.resolve()
    output = args.output.resolve()
    parsed = parse_native_residual_transcript(transcript.read_text(encoding="utf-8"))
    iterations = parsed["iterations"]
    if len(iterations) != args.expected_unique_points:
        raise RuntimeError(f"unique point count {len(iterations)} != {args.expected_unique_points}")
    if parsed["raw_row_count"] != args.expected_raw_rows:
        raise RuntimeError(f"raw row count {parsed['raw_row_count']} != {args.expected_raw_rows}")
    if iterations[0] != args.expected_start or iterations[-1] != args.expected_end:
        raise RuntimeError(
            f"native coordinate {iterations[0]}..{iterations[-1]} != "
            f"{args.expected_start}..{args.expected_end}"
        )
    if any(right <= left for left, right in zip(iterations, iterations[1:])):
        raise RuntimeError("residual iterations are not strictly increasing")
    if any(len(values) != len(iterations) for values in parsed["series"].values()):
        raise RuntimeError("residual series are not aligned with native coordinates")
    parsed["rebuild"] = {
        "method": "reparsed preserved solver transcript after repeated-header parser repair",
        "transcript": str(transcript),
        "interpolation": "none",
    }
    output.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "point_count": len(iterations), "curve_count": len(parsed["series"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

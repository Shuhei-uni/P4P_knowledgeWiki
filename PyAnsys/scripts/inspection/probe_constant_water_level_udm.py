#!/usr/bin/env python3
"""Allocate five UDM slots on a protected 900k copy, inspect, then restore it."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.connection import connect  # noqa: E402


REMOTE_ROOT = (
    r"C:\Users\qtra338\Documents\Mesh study\split_inlet_constant_water_level_sink_20260807"
)
DEFAULT_CASE = REMOTE_ROOT + r"\mesh-900k_07b_sink_hook_v1_retry2_prehook.cas.h5"
DEFAULT_DATA = REMOTE_ROOT + r"\mesh-900k_07b_sink_hook_v1_retry2_prehook.dat.h5"
DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "split_inlet_constant_water_level_sink_20260807"
    / "udm_allocation_probe.json"
)
REQUIRED_UDM = 5


def capture(call) -> tuple[Any, str]:
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        result = call()
    return result, stream.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-id", default="1")
    parser.add_argument("--case", default=DEFAULT_CASE)
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    load_dotenv(PROJECT_ROOT / ".env")
    solver = connect(server_id=args.server_id)
    payload: dict[str, Any] = {
        "case": args.case,
        "data": args.data,
        "requested_locations": REQUIRED_UDM,
        "restored": False,
    }
    try:
        solver.settings.file.read_case(file_name=args.case)
        solver.settings.file.read_data(file_name=args.data)
        _, transcript = capture(
            lambda: solver.tui.define.user_defined.user_defined_memory(REQUIRED_UDM)
        )
        allowed = [
            str(name) for name in solver.fields.field_data.scalar_fields.allowed_values()
        ]
        user_memory = [
            name
            for name in allowed
            if re.search(r"(?:user[-_ ]?memory|udm)", name, re.I)
        ]
        payload.update(
            {
                "status": "accepted" if len(user_memory) >= REQUIRED_UDM else "unresolved",
                "allocation_transcript": transcript,
                "user_memory_fields": user_memory,
                "scalar_field_count": len(allowed),
            }
        )
    except Exception as exc:
        payload.update(
            {
                "status": "unresolved",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )
        raise
    finally:
        solver.settings.file.read_case(file_name=args.case)
        solver.settings.file.read_data(file_name=args.data)
        payload["restored"] = True
        output = Path(args.output).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2, default=str))
        print(f"UDM probe written to {output}; protected case/data restored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

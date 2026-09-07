#!/usr/bin/env python3
"""Read Fluent iteration and autosave state without changing it."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from pyansys_fluent.common import safe_get_state  # noqa: E402
from pyansys_fluent.connection import connect  # noqa: E402


RPVARS = (
    "current-iteration",
    "number-of-iterations",
    "autosave/frequency/data",
    "autosave/frequency/case",
    "autosave/filename",
    "autosave/numfiles",
    "mmp/autosave/frequency/data",
    "mmp/autosave/frequency/case",
    "mmp/autosave/filename",
    "mmp/autosave/numfiles",
)


def main() -> int:
    load_dotenv()
    solver = connect()
    values = {}
    for name in RPVARS:
        try:
            values[name] = solver.scheme.eval(f"(rpgetvar '{name})")
        except Exception as exc:
            values[name] = f"{type(exc).__name__}: {exc}"
    print(json.dumps({"rpvars": values}, indent=2, default=str))
    try:
        activity = safe_get_state(solver.settings.solution.calculation_activity, "calculation_activity")
    except Exception as exc:
        activity = {"_capture_error": f"{type(exc).__name__}: {exc}"}
    print(json.dumps({"calculation_activity": activity}, indent=2, default=str))
    print("probe_complete: no state was changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

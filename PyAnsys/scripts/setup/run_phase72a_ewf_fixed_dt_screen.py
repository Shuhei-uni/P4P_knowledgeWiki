#!/usr/bin/env python3
"""Run the Phase 7.2A fixed-EWF-timestep sensitivity children in live Fluent.

Call ``run_screen(solver)`` from the persistent Fluent 2025 R2 Python REPL
started under the direct-fluent-use workflow. Each child reloads and verifies
the common native-5586 parent, then uses the established E2.81 instrumentation
and run controller with E2.7 fixed-step controls and one timestep delta.
"""

from __future__ import annotations

from pathlib import Path
import types
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / "PyAnsys" / "scripts" / "setup" / "run_phase72a_e281_direct.py"
CASES = (("E2.82", 1.25e-5), ("E2.83", 1.50e-5), ("E2.84", 1.75e-5))


def _replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Expected one {label} template occurrence, found {count}")
    return source.replace(old, new, 1)


def _case_module(case_id: str, film_timestep: float) -> types.ModuleType:
    if case_id not in {item[0] for item in CASES}:
        raise ValueError(f"Unknown fixed-timestep case: {case_id}")
    source = TEMPLATE.read_text(encoding="utf-8")
    source = source.replace("E2.81", case_id).replace("e2.81", case_id.lower())
    source = source.replace("e281", case_id.lower().replace(".", ""))

    # Match E2.7's active EWF controls; the fixed timestep is the sole active
    # numerical change in each child.
    replacements = (
        ('"ewf-adaptive?": True,', '"ewf-adaptive?": False,'),
        ('"courant-number": 0.4,', '"courant-number": 0.05,'),
        ('"sub-iter-stop": 5e-4,', '"sub-iter-stop": 1e-5,'),
        ('"sub-iter-nums": 4,', '"sub-iter-nums": 10,'),
        ('"timestep-max": 1e-5,', f'"timestep-max": {film_timestep!r},'),
    )
    for old, new in replacements:
        source = _replace_once(source, old, new, old)

    marker = '            if actual == 7196:\n'
    smoke = (
        '            if batch_number == 1:\n'
        '                missing_smoke_reports = [\n'
        '                    path for path in report_paths.values()\n'
        '                    if not Path(path).is_file() or Path(path).stat().st_size == 0\n'
        '                ]\n'
        '                require(not missing_smoke_reports, f"first-iteration report smoke failed: {missing_smoke_reports}")\n'
        '                manifest["one_iteration_smoke"] = "PASS_ALL_NATIVE_REPORT_FILES_WRITTEN"\n'
        '                dump(manifest_path, manifest)\n'
    )
    source = _replace_once(source, marker, smoke + marker, "smoke insertion point")

    module = types.ModuleType(f"phase72a_{case_id.lower().replace('.', '_')}")
    module.__file__ = str(TEMPLATE)
    module.__package__ = ""
    exec(compile(source, str(TEMPLATE), "exec"), module.__dict__)
    # Include a one-iteration instrumentation smoke inside the requested 3,000
    # iteration horizon, then checkpoint at native +250, +500, ... +3,000.
    module.BATCHES = [1, 249] + [250] * 11
    module.FIXED_FILM_TIMESTEP = film_timestep
    return module


def run_screen(solver: Any) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case_id, film_timestep in CASES:
        print(
            f"\n{case_id}: independent native-5586 parent; fixed film timestep "
            f"{film_timestep:.3e} s; 3,000 iterations",
            flush=True,
        )
        module = _case_module(case_id, film_timestep)
        result = module.run_e281(solver)
        result["requested_film_timestep_s"] = film_timestep
        results.append(result)
        print(
            f"{case_id}: {result.get('status')} at native "
            f"{result.get('terminal_native_iteration', result.get('last_native_iteration'))}",
            flush=True,
        )
        if result.get("status") != "COMPLETE":
            print(f"{case_id}: stopping the series after incomplete run; preserve and inspect its checkpoint.", flush=True)
            break
    return results

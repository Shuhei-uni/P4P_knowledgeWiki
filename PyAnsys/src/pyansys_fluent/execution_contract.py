"""Offline checks shared by future runners; importing this module never attaches."""
from __future__ import annotations

from contextlib import contextmanager
import math
import ntpath
import subprocess
import json
from typing import Any


def windows_path(value: str, *, working_directory: str | None = None) -> str:
    """Compare declared Windows paths without changing Fluent's stored values."""
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError("A nonempty Windows path is required")
    value = value.replace("/", "\\")
    drive, tail = ntpath.splitdrive(value)
    if not drive or not tail.startswith("\\"):
        if not working_directory:
            raise ValueError("Relative paths need the verified server working directory")
        base = windows_path(working_directory)
        if drive:
            raise ValueError("Drive-relative paths are ambiguous")
        value = ntpath.join(base, value)
    return ntpath.normcase(ntpath.normpath(value))


def compare_state(actual: Any, expected: Any, *, numeric_paths=(), path_paths=(),
                  rel_tol=1e-12, abs_tol=1e-12, working_directory=None) -> dict:
    """Allow rounding/path syntax only at explicit paths; all other values are exact."""
    if not all(math.isfinite(x) and x >= 0 for x in (rel_tol, abs_tol)):
        raise ValueError("Comparison tolerances must be finite and nonnegative")
    numeric = {tuple(p) for p in numeric_paths}
    paths = {tuple(p) for p in path_paths}
    if numeric & paths:
        raise ValueError("A path cannot have both numeric and path comparison rules")
    differences, normalization = [], []

    def visit(a, e, path):
        if isinstance(a, dict) and isinstance(e, dict):
            if a.keys() != e.keys():
                differences.append({"path": list(path), "reason": "object keys differ"})
            for key in sorted(a.keys() & e.keys(), key=str):
                visit(a[key], e[key], (*path, key))
            return
        if isinstance(a, (list, tuple)) and type(a) is type(e):
            if len(a) != len(e):
                differences.append({"path": list(path), "reason": "sequence length differs"})
            for i, (av, ev) in enumerate(zip(a, e)):
                visit(av, ev, (*path, i))
            return
        if isinstance(a, bool) or isinstance(e, bool):
            same = type(a) is type(e) and a == e
        elif path in numeric and isinstance(a, (int, float)) and isinstance(e, (int, float)):
            same = math.isfinite(a) and math.isfinite(e) and math.isclose(
                a, e, rel_tol=rel_tol, abs_tol=abs_tol)
        elif path in paths:
            try:
                same = windows_path(a, working_directory=working_directory) == windows_path(
                    e, working_directory=working_directory)
            except ValueError:
                same = False
        else:
            same = a == e
            if isinstance(a, float) or isinstance(e, float):
                same = same and all(not isinstance(v, float) or math.isfinite(v) for v in (a, e))
        if not same:
            differences.append({"path": list(path), "reason": "value differs"})
        elif a != e:
            normalization.append({"path": list(path), "before": e, "after": a})

    visit(actual, expected, ())
    return {"status": "PASS" if not differences else "FAIL",
            "differences": differences, "normalization": normalization}


def require_state_same(actual, expected, **rules):
    result = compare_state(actual, expected, **rules)
    if result["status"] != "PASS":
        raise RuntimeError("State changed outside declared comparison rules: " +
                           json.dumps(result["differences"]))
    return result


@contextmanager
def native_transcript(file_settings, path):
    """One start/stop pair; cleanup errors cannot replace the solver error."""
    start, stop = file_settings.start_transcript, file_settings.stop_transcript
    if not start.is_active():
        if not stop.is_active():
            raise RuntimeError("Transcript start unavailable; reconcile session state")
        stop()
    start(file_name=str(path))
    try:
        yield
    except BaseException:
        try:
            stop()
        except Exception as exc:
            print("TRANSCRIPT_CLOSE_AFTER_FAILURE", type(exc).__name__, flush=True)
        raise
    else:
        stop()


def require_named_objects(available, required):
    """Detect missing names and duplicate injection names before state-dict comparison."""
    available, required = list(available), list(required)
    if len(available) != len(set(available)):
        raise RuntimeError("Duplicate object names require bounded import repair")
    missing = sorted(set(required) - set(available))
    if missing:
        raise RuntimeError("Required objects are missing: " + ", ".join(missing))


def verify_drain_probe(proof: dict, *, setup_identity: str, frozen_bulk: bool,
                       required_bulk_equations=("drift", "flow", "ke", "mp")) -> dict:
    """Validate supplied functional evidence, never a nonzero sink from held bulk fields.

    The run owner supplies native accepted-time and independently integrated drain
    evidence from a bounded probe, with its declared ledger tolerance. This check
    does not configure a drain or claim a steady film or whole-separator closure.
    """
    failures = []
    if not setup_identity or proof.get("setup_identity") != setup_identity:
        failures.append("probe identity does not match the selected setup")
    if proof.get("direct_film_drain") is not True:
        failures.append("no direct film drain established")
    if proof.get("native_evidence_verified") is not True or not proof.get("evidence_paths"):
        failures.append("native probe evidence is missing")
    values = [proof.get(k) for k in ("film_start_s", "film_end_s", "drained_mass_kg",
                                     "ledger_error_percent", "ledger_limit_percent")]
    if not all(type(v) in (int, float) and math.isfinite(v) for v in values):
        failures.append("probe quantities are missing or nonfinite")
    else:
        begin, end, drained, error, limit = values
        if begin < 0 or end <= begin or drained <= 0:
            failures.append("accepted film advancement and positive direct removal are required")
        if error < 0 or limit < 0 or error > limit:
            failures.append("film ledger exceeds the declared probe tolerance")
    if frozen_bulk:
        equations = proof.get("bulk_equations")
        if (not isinstance(equations, dict) or set(equations) != set(required_bulk_equations)
                or any(v is not False for v in equations.values())):
            failures.append("bulk freeze is not established")
        if proof.get("bulk_fields_unchanged") is not True:
            failures.append("bulk field preservation is not established")
    return {"status": "PASS" if not failures else "UNVERIFIED", "failures": failures,
            "claim": "direct film drainage during the bounded probe only"}


def should_check_health(now, last_check, event_key, previous_event_key, *, period=300):
    """Health checks run on a timer or a new event, not each poll of a persistent error."""
    if not math.isfinite(period) or period <= 0:
        raise ValueError("Health-check period must be finite and positive")
    return now - last_check >= period or (event_key is not None and event_key != previous_event_key)


def probe_runtime(executable: str, modules=(), *, extra_paths=(), timeout=5) -> dict:
    """Probe one explicit interpreter without shell discovery or package installation."""
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("A finite positive timeout is required")
    payload = json.dumps({"modules": list(modules), "paths": list(extra_paths)})
    code = ("import importlib,json,sys; p=json.loads(sys.argv[1]); "
            "sys.path[:0]=p['paths']; "
            "versions={n:getattr(importlib.import_module(n),'__version__',None) for n in p['modules']}; "
            "print(json.dumps({'executable':sys.executable,'version':sys.version.split()[0],'modules':versions}))")
    try:
        result = subprocess.run([executable, "-c", code, payload], capture_output=True,
                                text=True, timeout=timeout, check=False)
        if result.returncode:
            return {"status": "UNAVAILABLE", "returncode": result.returncode}
        receipt = json.loads(result.stdout)
        return {"status": "PASS", **receipt}
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        return {"status": "UNAVAILABLE", "error_type": type(exc).__name__}

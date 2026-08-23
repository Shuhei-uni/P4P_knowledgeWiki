#!/usr/bin/env python3
"""Shared mechanics for the 03A Stage-4 Fluent-native continuation queue."""

from __future__ import annotations

import contextlib
import copy
from dataclasses import dataclass
import fcntl
import io
import json
import os
from pathlib import Path, PureWindowsPath
import re
import sys
import time
from typing import Any, Iterator, Mapping, TextIO

from pyansys_fluent.common import quote_scheme_string, remote_file_exists, safe_get_state


@dataclass(frozen=True)
class Stage4Experiment:
    experiment_id: str
    parent_branch: str
    parent_case: str
    parent_data: str
    parent_iteration: int
    turbulence_variant: str
    objective: str


def win(root: str, name: str) -> str:
    return str(PureWindowsPath(root) / name)


def posix(path: str) -> str:
    return path.replace("\\", "/")


def data_path(case_path: str) -> str:
    if not case_path.endswith(".cas.h5"):
        raise ValueError(f"Expected .cas.h5 path, got {case_path!r}")
    return case_path[:-7] + ".dat.h5"


@contextlib.contextmanager
def exclusive_writer_lock(path: Path) -> Iterator[TextIO]:
    """Hold one non-blocking local writer lock for the full owner lifetime."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"Another 03A Stage-4 writer owns {path}") from exc
        handle.seek(0)
        handle.truncate()
        handle.write(f"pid={os.getpid()}\n")
        handle.flush()
        try:
            yield handle
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class EventLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise FileExistsError(f"Refusing to overwrite event evidence: {self.path}")
        self.path.touch(exist_ok=False)

    def emit(self, kind: str, **fields: Any) -> None:
        payload = {
            "timestamp_epoch": time.time(),
            "kind": kind,
            **fields,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, default=str) + "\n")
            handle.flush()
        print(json.dumps(payload, default=str), flush=True)


class Tee:
    """Mirror owner stdout/stderr into one append-only local console file."""

    def __init__(self, primary: TextIO, path: Path) -> None:
        self.primary = primary
        self.file = path.open("x", encoding="utf-8")

    def write(self, text: str) -> int:
        self.primary.write(text)
        self.file.write(text)
        self.file.flush()
        return len(text)

    def flush(self) -> None:
        self.primary.flush()
        self.file.flush()

    def isatty(self) -> bool:
        return False

    def close(self) -> None:
        self.file.close()


def write_new_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def write_status(path: Path, payload: Mapping[str, Any]) -> None:
    """Atomically replace the explicitly mutable operational status snapshot."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    temporary.replace(path)


def capture_connected_clients(solver: Any) -> dict[str, Any]:
    buffer = io.StringIO()
    command = "/server/print-connected-grpc-clients"
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        try:
            result = solver.tui.server.print_connected_grpc_clients()
        except AttributeError:
            command = "/server/print-connected-clients"
            result = solver.tui.server.print_connected_clients()
        time.sleep(1.0)
        if result is not None:
            print(result)
    raw = buffer.getvalue()
    return {
        "command": command,
        "raw_report": raw,
        "exclusive": "No client is connected to server." in raw,
    }


def ensure_remote_directory(solver: Any, path: str) -> None:
    if remote_file_exists(solver, path):
        return
    command = f'cmd /c mkdir "{path}"'
    result = solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')
    if result not in (0, None) or not remote_file_exists(solver, path):
        raise RuntimeError(f"Could not create Fluent-host directory {path!r}; result={result!r}")


def remote_text_read(solver: Any, path: str) -> str:
    if not remote_file_exists(solver, path):
        return ""
    quoted = quote_scheme_string(path)
    expression = (
        f'(let ((p (open-input-file "{quoted}"))) '
        "(let loop ((chars '())) "
        "(let ((c (read-char p))) "
        "(if (eof-object? c) "
        "(begin (close-input-port p) (list->string (reverse chars))) "
        "(loop (cons c chars))))))"
    )
    value = solver.scheme.eval(expression)
    return "" if value is None else str(value)


def remote_file_sha256(solver: Any, path: str, scratch: str) -> str:
    if not remote_file_exists(solver, path):
        raise FileNotFoundError(f"Remote hash input is missing: {path}")
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"Refusing to overwrite remote hash evidence: {scratch}")
    command = f'cmd /c certutil -hashfile "{path}" SHA256 > "{scratch}" 2>&1'
    solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')
    text = remote_text_read(solver, scratch)
    matches = re.findall(r"\b[0-9a-fA-F]{64}\b", text.replace(" ", ""))
    if not matches:
        raise RuntimeError(f"Could not parse SHA256 for {path}: {text[:500]}")
    return matches[0].lower()


def remote_free_bytes(solver: Any, scratch: str) -> int:
    if remote_file_exists(solver, scratch):
        raise FileExistsError(f"Refusing to overwrite remote disk evidence: {scratch}")
    command = (
        'cmd /c powershell -NoProfile -Command "(Get-PSDrive -Name C).Free" '
        f'> "{scratch}" 2>&1'
    )
    solver.scheme.eval(f'(system "{quote_scheme_string(command)}")')
    text = remote_text_read(solver, scratch)
    match = re.search(r"(?:^|\s)(\d{8,})(?:\s|$)", text)
    if not match:
        raise RuntimeError(f"Could not parse remote free disk bytes: {text[:500]}")
    return int(match.group(1))


def write_remote_text_new(solver: Any, path: str, text: str) -> None:
    if remote_file_exists(solver, path):
        raise FileExistsError(f"Refusing to overwrite remote text evidence: {path}")
    body = " ".join(
        f'(display "{quote_scheme_string(line)}") (newline)'
        for line in text.splitlines()
    )
    expression = (
        f'(with-output-to-file "{quote_scheme_string(posix(path))}" '
        f"(lambda () {body}))"
    )
    solver.scheme.exec((expression,))
    if not remote_file_exists(solver, path):
        raise RuntimeError(f"Fluent did not expose remote text artifact: {path}")


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def recursive_key(value: Any, key: str) -> Any:
    if isinstance(value, Mapping):
        if key in value:
            return value[key]
        for child in value.values():
            found = recursive_key(child, key)
            if found is not None:
                return found
    return None


def scientific_readback(solver: Any) -> dict[str, Any]:
    models = safe_get_state(solver.settings.setup.models, "Stage-4 models")
    methods = safe_get_state(solver.settings.solution.methods, "Stage-4 methods")
    controls = safe_get_state(solver.settings.solution.controls, "Stage-4 controls")
    general = safe_get_state(solver.settings.setup.general, "Stage-4 general")
    boundaries = safe_get_state(
        solver.settings.setup.boundary_conditions,
        "Stage-4 boundaries",
    )
    injections: list[str] | dict[str, str]
    try:
        injections = list(
            solver.settings.setup.models.discrete_phase.injections.get_object_names()
        )
    except Exception as exc:
        injections = {"capture_error": f"{type(exc).__name__}: {exc}"}
    return {
        "general": general,
        "models": models,
        "methods": methods,
        "controls": controls,
        "boundaries": boundaries,
        "dpm_injections": injections,
    }


def verify_parent_state(
    readback: Mapping[str, Any],
    *,
    expected_turbulence: str,
) -> dict[str, Any]:
    models = readback["models"]
    methods = readback["methods"]
    controls = readback["controls"]
    general = readback["general"]
    boundaries = readback["boundaries"]
    multiphase = nested(models, "multiphase", "model")
    viscous_model = nested(models, "viscous", "model")
    turbulence = nested(models, "viscous", "k_epsilon_model")
    time_model = nested(general, "solver", "time")
    flow_scheme = nested(methods, "p_v_coupling", "flow_scheme") or nested(
        methods, "pressure_velocity_coupling", "flow_scheme"
    )
    momentum_urf = nested(controls, "under_relaxation", "mom")
    mp_equation = nested(controls, "equations", "mp")
    drift_equation = nested(controls, "equations", "drift")
    if multiphase != "mixture":
        raise RuntimeError(f"Parent multiphase model mismatch: {multiphase!r}")
    if viscous_model != "k-epsilon" or turbulence != expected_turbulence:
        raise RuntimeError(
            f"Parent turbulence mismatch: model={viscous_model!r} variant={turbulence!r}"
        )
    if time_model != "steady":
        raise RuntimeError(f"Parent is not steady: {time_model!r}")
    if str(flow_scheme).upper() != "SIMPLE":
        raise RuntimeError(f"Parent coupling is not SIMPLE: {flow_scheme!r}")
    if momentum_urf is None or abs(float(momentum_urf) - 0.3) > 1.0e-12:
        raise RuntimeError(f"Parent momentum URF is not 0.3: {momentum_urf!r}")
    if mp_equation is not True or drift_equation is not True:
        raise RuntimeError(
            f"Parent full-Mixture equations are not active: mp={mp_equation!r} drift={drift_equation!r}"
        )
    injections = readback.get("dpm_injections")
    if isinstance(injections, list) and injections:
        raise RuntimeError(f"DPM injections are unexpectedly present: {injections}")
    for outlet in ("steamoutlet", "brineoutlet"):
        pressure = recursive_key(nested(boundaries, "pressure_outlet", outlet), "gauge_pressure")
        value = recursive_key(pressure, "value") if isinstance(pressure, Mapping) else pressure
        if value is None or abs(float(value) - 1_120_000.0) > 0.5:
            raise RuntimeError(f"{outlet} pressure mismatch: {value!r}")
    return {
        "multiphase_model": multiphase,
        "viscous_model": viscous_model,
        "turbulence_variant": turbulence,
        "time_model": time_model,
        "flow_scheme": flow_scheme,
        "momentum_urf": momentum_urf,
        "mp_equation": mp_equation,
        "drift_equation": drift_equation,
        "dpm_injections": injections,
    }


def assert_controlled_scientific_delta(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    turbulence_variant: str,
) -> None:
    """Fail unless the only allowed scientific change is the turbulence branch."""

    left = copy.deepcopy(dict(before))
    right = copy.deepcopy(dict(after))
    if turbulence_variant == "rng":
        if left != right:
            raise RuntimeError("Unchanged Stage-4 continuation changed the scientific readback")
        return
    for payload in (left, right):
        models = payload.get("models")
        if isinstance(models, dict):
            models.pop("viscous", None)
    if left != right:
        raise RuntimeError(
            "S4-04 changed a scientific setting outside the viscous-model branch"
        )


def set_turbulence_variant(solver: Any, variant: str) -> None:
    viscous = solver.settings.setup.models.viscous
    initial = safe_get_state(viscous, "viscous before variant change")
    if nested(initial, "model") != "k-epsilon":
        raise RuntimeError(f"Cannot switch a non-k-epsilon model: {initial!r}")
    viscous.k_epsilon_model = variant
    readback = safe_get_state(solver.settings.setup.models.viscous, "viscous after variant change")
    if nested(readback, "k_epsilon_model") != variant:
        raise RuntimeError(f"Turbulence variant readback mismatch: {readback!r}")


def redirect_report_files(solver: Any, monitor_root: str) -> dict[str, str]:
    ensure_remote_directory(solver, monitor_root)
    report_files = solver.settings.solution.monitor.report_files
    names = sorted(str(name) for name in report_files.get_object_names())
    required_fragments = (
        "full_domain_mass_imbalance",
        "inventory_total_liquid_mass",
        "inventory_y010_liquid_mass",
        "inventory_y030_liquid_mass",
        "flux_phase1_brine_outlet",
        "flux_phase1_steam_outlet",
        "flux_phase2_brine_outlet",
        "flux_phase2_steam_outlet",
    )
    missing = [fragment for fragment in required_fragments if not any(fragment in name for name in names)]
    if missing:
        raise RuntimeError(f"Stage-4 parent monitor package is incomplete: missing={missing}")
    paths: dict[str, str] = {}
    for name in names:
        path = win(monitor_root, f"{name}.out")
        if remote_file_exists(solver, path):
            raise FileExistsError(f"Refusing to overwrite monitor file: {path}")
        report = solver.settings.solution.monitor.report_files[name]
        report.file_name = path
        state = safe_get_state(report, f"report file {name}")
        actual = state.get("file_name") if isinstance(state, Mapping) else None
        if not isinstance(actual, str):
            raise RuntimeError(f"Report path readback is unavailable for {name}: {actual!r}")
        verify_report_file_location(
            actual,
            monitor_root=monitor_root,
            report_name=name,
        )
        paths[name] = actual
    return paths


def configure_residual_history(solver: Any, size: int) -> dict[str, Any]:
    residual = solver.settings.solution.monitor.residual
    residual.options.n_save = size
    try:
        residual.options.n_display = size
    except Exception:
        pass
    state = safe_get_state(residual, "Stage-4 residual monitor")
    actual = recursive_key(state, "n_save")
    if actual is None or int(actual) < size:
        raise RuntimeError(f"Residual history readback is too small: {actual!r}")
    return state


def configure_autosave(solver: Any, root: str) -> dict[str, Any]:
    requested = {
        "case_frequency": "each-time",
        "data_frequency": 5000,
        "root_name": win(root, "checkpoint-%i"),
        "retain_most_recent_files": True,
        "max_files": 6,
        "append_file_name_with": {
            "file_suffix_type": "time-step",
            "file_decimal_digit": 6,
        },
    }
    solver.settings.file.auto_save.set_state(requested)
    actual = safe_get_state(solver.settings.file.auto_save, "Stage-4 autosave")
    if not isinstance(actual, Mapping):
        raise RuntimeError(f"Autosave readback is unavailable: {actual!r}")
    for key in ("case_frequency", "data_frequency", "root_name", "max_files"):
        if actual.get(key) != requested[key]:
            raise RuntimeError(f"Autosave readback mismatch for {key}: {actual.get(key)!r}")
    return dict(actual)


def normalized_windows_path(path: str) -> PureWindowsPath:
    collapsed = re.sub(r"\\+", r"\\", path.replace("/", "\\"))
    return PureWindowsPath(collapsed)


def verify_report_file_location(
    actual: str,
    *,
    monitor_root: str,
    report_name: str,
    allow_relative: bool = False,
) -> None:
    path = normalized_windows_path(actual)
    root = normalized_windows_path(monitor_root)
    if not path.is_absolute() and allow_relative:
        if str(path.parent) not in (".", ""):
            raise RuntimeError(
                f"Relative report file contains an unexpected subdirectory: {actual!r}"
            )
    elif str(path.parent).lower() != str(root).lower():
        raise RuntimeError(
            f"Report file escaped its Stage-4 monitor directory: {actual!r}"
        )
    if not path.name.startswith(report_name) or not path.name.endswith(".out"):
        raise RuntimeError(
            f"Report filename does not preserve its definition identity: {actual!r}"
        )


def render_native_queue(experiments: list[dict[str, Any]], iterations: int) -> str:
    lines = [
        "; 03A Stage-4 promising-state development queue",
        "; Fluent owns every solve, autosave, transcript, and final endpoint write.",
        "; Each experiment is an independent cold load from its prepared case and Stage-3 data.",
        "/file/confirm-overwrite? no",
    ]
    for item in experiments:
        lines.extend(
            [
                f'; BEGIN {item["experiment_id"]}',
                f'(chdir "{posix(item["monitor_root"])}")',
                f'/file/read-case "{posix(item["prepared_case"])}"',
                f'/file/read-data "{posix(item["parent_data"])}"',
                f'/file/start-transcript "{posix(item["transcript"])}"',
                "/solve/monitors/residual/print? yes",
                "/solve/monitors/residual/plot? no",
                f"/solve/monitors/residual/n-save {iterations + 1000}",
                f"/solve/iterate {iterations}",
                f'/file/write-case-data "{posix(item["endpoint_case"])}"',
                f'/plot/residuals-set/plot-to-file "{posix(item["residual_file"])}"',
                "/plot/residuals",
                "/plot/residuals-set/end-plot-to-file",
                "/file/stop-transcript",
                f'; END {item["experiment_id"]}',
            ]
        )
    lines.extend(("; Stage-4 native queue finished; Fluent remains open.", ""))
    return "\n".join(lines)

"""Prepare, submit and recover native analytical-film comparisons on Server 1."""
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import re
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts/setup")]
import run_phase72a_stage4_ewf_drain as d
import submit_phase72a_stage4_long_native as native
from run_phase72a_stage3_early_ewf import attach as base_attach
from run_phase72a_e27_server1_continuation import native_iteration, pair_save
from pyansys_fluent.stage4_native import ensure_remote_directory
from pyansys_fluent.remote_text import read_text, write_ascii_text_new
from pyansys_fluent.common import remote_file_exists
from ansys.fluent.core.fields.field_data_interfaces import SurfaceFieldDataRequest, SurfaceDataType

OUT = ROOT / "output/phase72a-stage4-analytical/20261008"
WORK = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\analytical-20261008")
ARMS = {"analytical10": (False, 10e-6), "analytical5": (False, 5e-6), "momentum10": (True, 10e-6)}


def attach():
    """Bound initial v252 discovery using the existing recovery pattern."""
    from ansys.fluent.core._grpc_services.scheme_interpreter_service_v0 import SchemeInterpreterService
    from ansys.api.fluent.v0 import scheme_eval_pb2
    from ansys.fluent.core._grpc_services.application_runtime_service_v0 import ApplicationRuntimeService
    from ansys.api.fluent.v0 import app_utilities_pb2
    original = SchemeInterpreterService.string_eval
    optional = {name: getattr(ApplicationRuntimeService, name) for name in
                ["get_build_info", "get_controller_process_info", "get_solver_process_info"]}

    def version_query(service, expression):
        if expression == "(cx-version)":
            return service._stub.StringEval(scheme_eval_pb2.StringEvalRequest(input=expression),
                                           metadata=service._metadata, timeout=5).output
        return original(service, expression)

    def build_info(service):
        response = service._stub.GetBuildInfo(app_utilities_pb2.GetBuildInfoRequest(),
                                              metadata=service._metadata, timeout=5)
        return response.build_time, response.build_id, response.vcs_revision, response.vcs_branch

    def controller_info(service):
        response = service._stub.GetControllerProcessInfo(app_utilities_pb2.GetControllerProcessInfoRequest(),
                                                          metadata=service._metadata, timeout=5)
        return response.process_id, response.hostname, response.working_directory

    def solver_info(service):
        response = service._stub.GetSolverProcessInfo(app_utilities_pb2.GetSolverProcessInfoRequest(),
                                                      metadata=service._metadata, timeout=5)
        return response.process_id, response.hostname, response.working_directory

    # PyFluent fetches build metadata for a log message during connection.
    # GetBuildInfo stalled while finite Settings/version queries still worked.
    # The SDK already handles RuntimeError by leaving optional process
    # properties unavailable. Bound these calls without inventing properties
    # or weakening the separate mandatory v252 version check.
    SchemeInterpreterService.string_eval = version_query
    ApplicationRuntimeService.get_build_info = build_info
    ApplicationRuntimeService.get_controller_process_info = controller_info
    ApplicationRuntimeService.get_solver_process_info = solver_info
    try:
        return base_attach()
    finally:
        SchemeInterpreterService.string_eval = original
        for name, method in optional.items():
            setattr(ApplicationRuntimeService, name, method)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n")
    temp.replace(path)


def manifest(arm):
    return OUT / arm / "run-manifest.json"


def load(arm):
    m = json.loads(manifest(arm).read_text())
    if "prepared_parameters" not in m and (OUT / arm / "prepared-readback.json").exists():
        m["prepared_parameters"] = json.loads((OUT / arm / "prepared-readback.json").read_text())["parameters"]
    return m


def checked_remote_sha256(s, path, scratch):
    """Hash one file with the previously used certutil route, never PowerShell.

    Check the exact command before any remote call. Do not batch paths or
    interpolate scripts into cmd.exe. The 1024-character bound is deliberately
    below Windows' 8191-character command-prompt limit.
    """
    for value in (path, scratch):
        value.encode("ascii", errors="strict")
        if any(character in value for character in '\"\r\n%!^&|<>'):
            raise ValueError("Unsafe character in native hash path")
    command = f'cmd /c certutil -hashfile "{path}" SHA256 > "{scratch}" 2>&1'
    if len(command) > 1024:
        raise ValueError(f"Native hash command too long: {len(command)} > 1024")
    for value in (path, scratch):
        exists = remote_file_exists(s, value.replace("\\", "/"))
        if value == path and not exists:
            raise FileNotFoundError(path)
        if value == scratch and exists:
            raise FileExistsError("Refusing to overwrite hash evidence: " + scratch)
    # Numeric characters preserve literal Windows backslashes through Fluent's
    # evaluator. Nested quoted system strings can turn \n / \t into controls.
    codes = " ".join(str(code) for code in command.encode("ascii"))
    result = s.scheme.eval("(system (list->string (map integer->char '(" + codes + "))))")
    output = read_text(s, scratch.replace("\\", "/"))
    matches = re.findall(r"\b[0-9a-fA-F]{64}\b", output.replace(" ", ""))
    if result not in (0, None) or len(matches) != 1:
        raise RuntimeError(f"Native checksum failed for {path!r} (result={result!r}): {output[:500]}")
    return matches[0].lower()


def terminal_pair(record, status):
    """Resolve a saved endpoint from native completion evidence; never solve."""
    match = re.search(r'\(status\s+\.\s+"([A-Z_]+)"\)', status)
    completed = re.search(r'\(completed-updates\s+\.\s+(\d+)\)', status)
    if not match or not completed:
        raise RuntimeError("Missing native terminal status/count; preserve and recover evidence")
    classification = match[1]
    successful = classification == "HORIZON_REACHED_PENDING_VERIFICATION"
    if classification not in ["HORIZON_REACHED_PENDING_VERIFICATION", "NUMERICAL_REJECTED",
                              "UNREALISTIC", "EVIDENCE_OR_SOLVER_STOP"]:
        raise RuntimeError("Native job has no saved terminal endpoint: " + classification)
    count = int(completed[1])
    if count > record["count"] or (successful and count != record["count"]):
        raise RuntimeError("Native completion count differs from submitted horizon")
    if classification == "EVIDENCE_OR_SOLVER_STOP":
        # Older native journals incremented requested steps after iterate
        # returned, even after an interrupt. Use complete matching report
        # histories, then verify the saved pair/clock before accepting work.
        histories = []
        for name in ("thickness-history", "courant-history"):
            history = re.search(r'\(' + name + r'\s+(\d+)\s+(\d+)\s+(\d+)\s+[^\s()]+\s+#t\)', status)
            if not history:
                raise RuntimeError("Partial native stop lacks a complete " + name)
            first, last, rows = map(int, history.groups())
            if first not in (record["start"], record["start"] + 1) or rows != last - first + 1:
                raise RuntimeError("Partial native report history is not contiguous")
            histories.append(last)
        if histories[0] != histories[1] or not record["start"] < histories[0] <= record["target"]:
            raise RuntimeError("Partial native report histories disagree")
        count = histories[0] - record["start"]
    work = PureWindowsPath(record["work"])
    label = f"final-N{record['target']}" if successful else "rejected-preserved"
    return successful, {"case": str(work / (label + ".cas.h5")),
                        "data": str(work / (label + ".dat.h5")),
                        "native_iteration": record["start"] + count}


def reopen_recovery_pair(s, pair):
    """Require both artifacts before replacing the loaded case; no initialize."""
    for kind in ("case", "data"):
        if not remote_file_exists(s, pair[kind]):
            raise FileNotFoundError("Saved native endpoint missing: " + pair[kind])
    s.settings.file.read_case(file_name=pair["case"])
    s.settings.file.read_data(file_name=pair["data"])
    if native_iteration(s) != pair["native_iteration"]:
        raise RuntimeError("Reopened native endpoint has the wrong iteration")


def store_verified_text(s, path, target, expected_hash):
    """Recover a text artifact against its server hash without changing raw/."""
    if target.exists():
        data = target.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected_hash:
            raise RuntimeError("Immutable local evidence differs from native source: " + path)
    else:
        contents = read_text(s, path).encode("ascii")
        variants = [contents, contents.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")]
        matches = [data for data in variants if hashlib.sha256(data).hexdigest() == expected_hash]
        if not matches:
            raise RuntimeError("Native text bytes/hash differ: " + path)
        data = matches[0]
        target.write_bytes(data)
    return {"path": path, "bytes": len(data), "sha256": expected_hash,
            "verification": "ONE_FILE_BOUNDED_CERTUTIL_HASH_AND_NATIVE_TEXT_READ"}


def close_terminal_report_files(s, paths):
    """Release this terminal job's file writers before taking source hashes."""
    normalize = lambda path: re.sub(r"/+", "/", path.replace("\\", "/")).casefold()
    wanted = {normalize(path) for path in paths.values()}
    files = s.settings.solution.monitor.report_files
    state = files.get_state()
    selected = {}
    for name, item in state.items():
        definitions = item["report_defs"]
        if len(definitions) != 1 or definitions[0] not in paths:
            continue
        current = normalize(item["file_name"])
        expected = normalize(paths[definitions[0]])
        # Native case writing can replace absolute report names with paths
        # relative to Fluent's working directory, using doubled separators.
        relative = not (":" in current or current.startswith("/"))
        if current == expected or (relative and expected.endswith("/" + current)):
            selected[name] = {"active": False}
    if len(selected) != len(wanted):
        raise RuntimeError("Report destinations do not match the native job; retain endpoint")
    files.set_state(selected)
    actual = files.get_state()
    if any(actual[name]["active"] for name in selected):
        raise RuntimeError("Native report writers remain active")
    return list(selected)


def snapshot(s):
    return {"version": str(s.get_fluent_version()), "native_iteration": native_iteration(s),
            "film": dict(s.rp_vars("wall-film/solution-state")),
            "parameters": dict(s.rp_vars("wall-film/model-parameters")),
            "equations": s.settings.solution.controls.equations.get_state(),
            "bulk": d.compute(s, d.BULK),
            "walls": {name: s.settings.setup.boundary_conditions.wall[name].phase["mixture"].wall_film.get_state()
                      for name in ["wall", "wall:004"]}}


def save(s, work, label):
    return pair_save(s, work / (label + ".cas.h5"), work / "scratch", scratch_tag=label)


def fields(s, destination):
    result = {}
    for name, label in [("wall", "upper"), ("wall:004", "lower")]:
        values = d.facets(s, name)
        geometry = s.fields.field_data.get_field_data(SurfaceFieldDataRequest(
            surfaces=[name], data_types=[SurfaceDataType.FacesCentroid]))[name].face_centroids
        values["centroids"] = np.asarray(geometry)
        np.savez(destination / (label + "-fields.npz"), **values)
        result[label] = {"faces": len(values["film-mass"]),
                         "mass_kg": float(values["film-mass"].sum()),
                         "max_thickness_m": float(values["film-thickness"].max()),
                         "max_speed_m_s": float(np.sqrt(sum(values["film-" + axis + "-velocity"]**2
                                                              for axis in "xyz")).max())}
    return result


def audit(s, arm):
    momentum, step = ARMS[arm]
    p = dict(s.rp_vars("wall-film/model-parameters"))
    for key, value in {"solve-wallfilm?": True, "solve-momentum?": True,
                       "mom-equation?": momentum, "secondary-phase-mode": 1,
                       "dpm-collection?": True, "film-stripping?": True,
                       "film-separation?": True, "ewf-adaptive?": False}.items():
        assert p[key] == value, (key, p[key], value)
    assert math.isclose(p["timestep-max"], step, rel_tol=1e-12)
    assert not any(s.settings.solution.controls.equations.get_state().values())
    return d.drain.audit(s, True)


def instrument(s, folder):
    files = s.settings.solution.monitor.report_files
    state = files.get_state()
    updates, paths = {}, {}
    for name, item in state.items():
        assert len(item["report_defs"]) == 1
        definition = item["report_defs"][0]
        assert definition not in paths
        path = (folder / (definition + ".out")).as_posix()
        paths[definition] = path
        updates[name] = {"file_name": path, "frequency_of": "iteration", "frequency": 1, "active": True}
    files.set_state(updates)
    actual = files.get_state()
    for name, expected in updates.items():
        assert actual[name]["active"] and actual[name]["frequency"] == 1
        assert native.normalized_windows_path(actual[name]["file_name"]) == native.normalized_windows_path(expected["file_name"])
    return paths


def prepare(arm):
    assert not manifest(arm).exists(), "Reconcile an existing arm; never repeat preparation blindly"
    s = attach()
    assert not s.settings.solution.run_calculation.iterating()
    out, work = OUT / arm, WORK / arm
    out.mkdir(parents=True, exist_ok=True)
    for folder in [WORK, WORK / "scratch", work, work / "scratch"]:
        ensure_remote_directory(s, str(folder))
    m = {"status": "PREPARING", "arm": arm, "server_id": "1",
         "authority": "human_20261008_start_analytical_method", "initialization": "FORBIDDEN",
         "blocks": [], "work_root": str(work), "requires_laptop_for_solve": False}
    dump(manifest(arm), m)
    if not (OUT / "preserved-current.json").exists():
        m["preserved_previous"] = save(s, WORK, "preserved-N" + str(native_iteration(s)))
        dump(OUT / "preserved-current.json", {"pair": m["preserved_previous"], "state": snapshot(s)})
        dump(manifest(arm), m)
    parent = json.loads((native.OUT / "run-manifest.json").read_text())["parent_pair"]
    for kind in ["case", "data"]:
        actual = checked_remote_sha256(s, parent[kind], str(work / "scratch" / ("parent-" + kind + ".sha256.txt")))
        assert actual == parent[kind + "_sha256"]
    s.settings.file.read_case(file_name=parent["case"])
    s.settings.file.read_data(file_name=parent["data"])
    before = snapshot(s)
    assert before["native_iteration"] == 41483
    assert not any(before["equations"].values())
    m.update(parent_pair=parent, parent_film_time_s=before["film"]["film_elapsed_time"],
             parent_parameters=before["parameters"], bulk_reference=before["bulk"])
    dump(out / "parent-readback.json", before)
    dump(manifest(arm), m)
    momentum, step = ARMS[arm]
    changes = {"mom-equation?": momentum, "timestep-max": step}
    d.q.r.setparams(s, changes)
    s.settings.setup.named_expressions["P72dRefreshSpan"].definition = f"{step:.17g}[s]"
    s.settings.solution.run_calculation.profile_update_interval = 1
    s.settings.file.auto_save.data_frequency = 0
    m["prepared_pair"] = save(s, work, "prepared-N41483")
    dump(manifest(arm), m)
    s.settings.file.read_case(file_name=m["prepared_pair"]["case"])
    s.settings.file.read_data(file_name=m["prepared_pair"]["data"])
    after = snapshot(s)
    assert after["native_iteration"] == 41483
    assert after["film"]["film_elapsed_time"] == before["film"]["film_elapsed_time"]
    assert after["parameters"] == {k: changes.get(k, v) for k, v in before["parameters"].items()}
    d.q.r.require_match({"fields": after["bulk"]}, {"fields": before["bulk"]})
    m["drain_audit"] = audit(s, arm)
    m["field_summary"] = fields(s, out)
    m.update(status="PREPARED_REOPEN_VERIFIED", latest_pair=m["prepared_pair"],
             verified_native_end=41483, verified_film_time_s=after["film"]["film_elapsed_time"],
             controlled_delta=changes, step_s=step, prepared_parameters=after["parameters"],
             configuration_route="v252_native_RP_API_and_paired_reopen")
    dump(out / "prepared-readback.json", after)
    dump(manifest(arm), m)
    print("PREPARED", arm, m["field_summary"], flush=True)


def build_native_code(work, start, count, step):
    native.WORK = work
    code = native.native_code()
    replacements = {
        "(define p72l-start 41483)": f"(define p72l-start {start})",
        "(define p72l-total 200000)": f"(define p72l-total {count})",
        "(cons 'fixed-film-step-s 0.000015)": f"(cons 'fixed-film-step-s {step:.17g})",
        '(p72l-write-pair "final-N241483")': f'(p72l-write-pair "final-N{start+count}")',
        '  (p72l-progress)\n  (let loop ()':
        '  (p72l-progress)\n  (ti-menu-load-string "/parallel/timer/reset")\n  (let loop ()',
        '  (if (string=? p72l-status "RUNNING")\n      (begin':
        '  (ti-menu-load-string "/parallel/timer/usage")\n  (if (string=? p72l-status "RUNNING")\n      (begin',
        '(begin\n        (ti-menu-load-string "/solve/iterate 1000")\n        (set! p72l-completed (+ p72l-completed p72l-block))':
        '(let ((steps (min p72l-block (- p72l-total p72l-completed))))\n'
        '        (ti-menu-load-string (string-append "/solve/iterate " (number->string steps)))\n'
        '        (set! p72l-completed (+ p72l-completed steps))',
    }
    for old, new in replacements.items():
        assert code.count(old) == 1, old
        code = code.replace(old, new)
    old = '(let ((steps (min p72l-block (- p72l-total p72l-completed))))'
    assert code.count(old) == 1
    code = code.replace(old,
        '(let* ((steps (min p72l-block (- p72l-total p72l-completed)))\n'
        '             (expected-target (+ p72l-start p72l-completed steps)))')
    code = code.replace('        (set! p72l-completed (+ p72l-completed steps))\n', '')
    old = '(set! p72l-status (p72l-classify p72l-h p72l-c\n          (+ p72l-start p72l-completed)))'
    assert code.count(old) == 1
    code = code.replace(old,
        '(set! p72l-completed (max 0 (- (min (list-ref p72l-h 1) (list-ref p72l-c 1)) p72l-start)))\n'
        '        (set! p72l-status (p72l-classify p72l-h p72l-c expected-target))')
    return code


def submit(arm, count):
    m = load(arm)
    recovery_tail = (m["status"] == "NATIVE_REJECTED" and arm == "momentum10"
                     and m.get("recovery_reason") == "CLIENT_MONITOR_INTERPRETER_INTERRUPT"
                     and count == m.get("recovery_target", -1) - m["verified_native_end"])
    assert m["status"] in ["PREPARED_REOPEN_VERIFIED", "CHECKPOINT_VERIFIED"] or recovery_tail
    assert count >= 1000 or (count == 20 and not m["blocks"]) or recovery_tail, "One setup smoke or exact interrupted-horizon recovery; otherwise long fixed-input solve"
    s = attach()
    assert not s.settings.solution.run_calculation.iterating()
    # Preserve native transfer cadence for same-arm continuation. Check the
    # complete parameter list and persistent reports, not only the counter.
    active = dict(s.rp_vars("wall-film/model-parameters"))
    if native_iteration(s) != m["verified_native_end"] or active != m["prepared_parameters"]:
        s.settings.file.read_case(file_name=m["latest_pair"]["case"])
        s.settings.file.read_data(file_name=m["latest_pair"]["data"])
        continuation = "EXACT_PAIRED_RELOAD"
    else:
        continuation = "LIVE_PARAMETERS_COUNTER_AND_STOCKS_MATCHED_NO_RELOAD"
        if m["blocks"]:
            previous = json.loads((ROOT.parent / m["blocks"][-1] / "run-manifest.json").read_text())
            names = [name for name in previous["final_reports"] if name.endswith(("-mass", "-outflow", "-stripped", "-separated", "-thickness"))]
            d.q.r.require_match({"fields": d.compute(s, names)},
                                {"fields": {name: previous["final_reports"][name] for name in names}})
    assert native_iteration(s) == m["verified_native_end"]
    audit(s, arm)
    begin = native_iteration(s)
    label = f"run-N{begin}-N{begin+count}"
    work = WORK / arm / label
    local = OUT / arm / label
    assert not local.exists(), "Reconcile prior native submission"
    local.mkdir()
    for folder in [work, work / "monitors", work / "scratch", work / "checkpoints"]:
        ensure_remote_directory(s, str(folder))
    paths = instrument(s, work / "monitors")
    before = snapshot(s)
    values = d.compute(s, list(paths))
    autosave = native.configure_autosave(s, str(work / "checkpoints"), data_frequency=5000)
    code = build_native_code(work, begin, count, m["step_s"])
    journal = '\n'.join([f'/file/start-transcript "{(work / "native-run.trn").as_posix()}"',
                         f'(load "{(work / "native-run.scm").as_posix()}")', '(p72l-run)', ''])
    for name, content in [("native-run.scm", code), ("native-run.jou", journal)]:
        write_ascii_text_new(s, str(work / name), content)
        (local / name).write_text(content)
    record = {"status": "PREPARED_NATIVE", "arm": arm, "start": begin, "count": count,
              "target": begin + count, "step_s": m["step_s"], "before": before,
              "initial_reports": values, "report_paths": paths, "autosave": autosave,
              "work": str(work), "local": str(local.relative_to(ROOT.parent)),
              "native_status": str(work / "native-status.scm"),
              "native_transcript": str(work / "native-run.trn"),
              "continuation_route": continuation,
              "submitted_utc": datetime.now(timezone.utc).isoformat()}
    dump(local / "run-manifest.json", record)
    m.update(status="SUBMITTING_NATIVE", active_block=record["local"], active_target=record["target"])
    dump(manifest(arm), m)
    s.transcript.start(file_name=str(local / "submission-stream.txt"), write_to_stdout=False)
    path = (work / "native-run.jou").as_posix()
    command = '(ti-menu-load-string "/file/read-journal \\\"' + path + '\\\"")'
    acknowledgement = s.scheme.exec((command,), wait=False, silent=False)
    m.update(status="SUBMITTED_NATIVE", acknowledgement=str(acknowledgement))
    dump(manifest(arm), m)
    print("SUBMITTED_NATIVE", arm, begin, record["target"], flush=True)
    # Observe startup only; Fluent owns the whole native solve after this process exits.
    for _ in range(12):
        time.sleep(1)
        stream = local / "submission-stream.txt"
        if stream.exists() and "Film time =" in stream.read_text():
            break
    s.transcript.stop()


def capture(arm):
    m = load(arm)
    assert m["status"] in ["SUBMITTED_NATIVE", "SUBMITTING_NATIVE", "RECOVERY_REQUIRED"]
    local = ROOT.parent / m["active_block"]
    record = json.loads((local / "run-manifest.json").read_text())
    s = attach()
    if s.settings.solution.run_calculation.is_active():
        assert not s.settings.solution.run_calculation.iterating(), "Native job remains active"
    status = read_text(s, record["native_status"])
    successful, pair = terminal_pair(record, status)
    work = PureWindowsPath(record["work"])
    raw = local / "raw"
    paths = {"native-status.scm": record["native_status"], "solve.trn": record["native_transcript"],
             **{name + ".out": path for name, path in record["report_paths"].items()}}
    # The previous bulk EncodedCommand exceeded cmd.exe's limit and coincided
    # with Fluent closing. Remove that route entirely, including .ps1 variants.
    # Each checksum now uses one short, prechecked certutil command; text is
    # transferred through Scheme, with no shell script or archive.
    for kind in ("case", "data"):
        if not remote_file_exists(s, pair[kind]):
            raise FileNotFoundError(pair[kind])
    for kind in ("case", "data"):
        scratch = str(work / "scratch" / (kind + "-" + str(time.time_ns()) + ".sha256.txt"))
        pair[kind + "_sha256"] = checked_remote_sha256(s, pair[kind], scratch)
    if m["status"] == "RECOVERY_REQUIRED":
        if not s.settings.setup.cell_zone_conditions.is_active():
            current = 0
        elif "P71V2Iteration" in s.settings.setup.named_expressions.get_object_names():
            current = native_iteration(s)
        else:
            raise RuntimeError("Unknown loaded case; preserve its endpoint before recovery")
        if current not in (0, pair["native_iteration"]):
            # Preserve an unexpected loaded endpoint before replacing it.
            save(s, work, f"pre-recovery-N{current}-{time.time_ns()}")
        reopen_recovery_pair(s, pair)
        record["capture_route"] = "SAVED_NATIVE_PAIR_REOPEN_AFTER_SERVER_RESTART_NO_SOLVE"
    else:
        assert native_iteration(s) == pair["native_iteration"]
        record["capture_route"] = "LIVE_TERMINAL_ENDPOINT_NO_RELOAD"
    final = snapshot(s)
    audit(s, arm)
    assert final["parameters"] == m["prepared_parameters"]
    assert final["native_iteration"] == pair["native_iteration"]
    if record["capture_route"] == "LIVE_TERMINAL_ENDPOINT_NO_RELOAD":
        record["solved_endpoint_before_reopen"] = final
        if (local / "report-writer-reopen.json").exists():
            record["capture_route"] = "NATIVE_PAIR_ALREADY_REOPENED_TO_RELEASE_REPORT_HANDLES_NO_SOLVE"
        else:
            # Turning report activity OFF does not release Windows file
            # handles. Paired reopen closes them and verifies recoverability.
            # Solved source-rate histories own the ledger; instantaneous
            # collection readback can clear on reload.
            reopen_recovery_pair(s, pair)
            after = snapshot(s)
            assert after["parameters"] == final["parameters"]
            for key in ("film_elapsed_time", "max_timestep_count"):
                assert after["film"][key] == final["film"][key]
            d.q.r.require_match({"fields": after["bulk"]}, {"fields": final["bulk"]})
            final = after
            record["capture_route"] = "NATIVE_PAIR_REOPEN_VERIFIED_AND_REPORT_HANDLES_RELEASED_NO_SOLVE"
    record["closed_terminal_report_files"] = close_terminal_report_files(s, record["report_paths"])
    dump(local / "capture-readback.json", {"pair": pair, "final": final,
                                           "native_status": status, "route": record["capture_route"]})
    metadata = []
    raw.mkdir(exist_ok=True)
    for name, path in paths.items():
        scratch = str(work / "scratch" / ("text-" + str(time.time_ns()) + ".sha256.txt"))
        digest = checked_remote_sha256(s, path, scratch)
        metadata.append(store_verified_text(s, path, raw / name, digest))
    dump(local / "source-receipt.json", metadata)
    printed = [tuple(map(float, match.groups())) for match in d.FILM.finditer((raw / "solve.trn").read_text())]
    actual_count = final["native_iteration"] - record["start"]
    assert len(printed) == actual_count
    assert all(math.isclose(v[1], record["step_s"], rel_tol=1e-8) for v in printed)
    assert final["film"]["max_timestep_count"] - record["before"]["film"]["max_timestep_count"] == actual_count
    assert math.isclose(final["film"]["film_elapsed_time"] - record["before"]["film"]["film_elapsed_time"],
                        actual_count * record["step_s"], abs_tol=1e-9)
    if successful:
        assert final["native_iteration"] == record["target"]
        assert len(printed) == record["count"]
        assert all(math.isclose(v[1], record["step_s"], rel_tol=1e-8) for v in printed)
        assert final["film"]["max_timestep_count"] - record["before"]["film"]["max_timestep_count"] == record["count"]
        assert math.isclose(final["film"]["film_elapsed_time"] - record["before"]["film"]["film_elapsed_time"],
                            record["count"] * record["step_s"], abs_tol=1e-9)
    d.q.r.require_match({"fields": final["bulk"]}, {"fields": m["bulk_reference"]})
    field_summary = fields(s, local)
    reports = d.compute(s, list(record["report_paths"]))
    record.update(status="CHECKPOINT_VERIFIED" if successful else "NATIVE_REJECTED",
                  native_status_readback=status, final=final, final_reports=reports,
                  pair=pair, field_summary=field_summary, printed_film_updates=len(printed),
                  accepted_updates=actual_count, accepted_added_film_time_s=actual_count * record["step_s"])
    dump(local / "run-manifest.json", record)
    m["blocks"].append(record["local"])
    m.update(status=record["status"], latest_pair=pair, verified_native_end=final["native_iteration"],
             verified_film_time_s=final["film"]["film_elapsed_time"], active_target=None)
    dump(manifest(arm), m)
    print(record["status"], arm, final["native_iteration"], field_summary, flush=True)


def observe(arm, seconds):
    """Listen to output only. Never evaluate Scheme during a native solve."""
    import grpc
    from ansys.api.fluent.v0 import transcript_pb2, transcript_pb2_grpc
    from pyansys_fluent.connection import resolve_connection_kwargs

    if not 1 <= seconds <= 60:
        raise ValueError("Passive observation must be bounded to 1–60 seconds")
    m = load(arm)
    local = ROOT.parent / m["active_block"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    config = resolve_connection_kwargs("1", start_transcript=False, tcp_timeout_seconds=5)
    channel = grpc.insecure_channel(f"{config['ip']}:{config['port']}")
    chunks = []
    try:
        stream = transcript_pb2_grpc.TranscriptStub(channel).BeginStreaming(
            transcript_pb2.TranscriptRequest(), metadata=[("password", config["password"])],
            timeout=seconds)
        for response in stream:
            chunks.append(response.transcript)
    except grpc.RpcError as error:
        if error.code() != grpc.StatusCode.DEADLINE_EXCEEDED:
            raise
    finally:
        channel.close()
        text = "".join(chunks)
        (local / ("transcript-observer-" + stamp + ".txt")).write_text(text)
    clocks = re.findall(r"Film time = ([\deE.+-]+)", text)
    print("PASSIVE_TRANSCRIPT_ONLY", len(text), "characters", "last_film_time_s",
          float(clocks[-1]) if clocks else None,
          "native_terminal_seen", "/file/stop-transcript" in text, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "submit", "capture", "observe"])
    parser.add_argument("--arm", choices=list(ARMS), required=True)
    parser.add_argument("--count", type=int)
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()
    {"prepare": lambda: prepare(args.arm), "submit": lambda: submit(args.arm, args.count),
     "capture": lambda: capture(args.arm),
     "observe": lambda: observe(args.arm, args.seconds)}[args.action]()

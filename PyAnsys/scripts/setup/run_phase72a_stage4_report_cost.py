"""Native paired report-cost screen; reuse the proven Server 1 run/recovery layer."""
from pathlib import Path, PureWindowsPath
import argparse
import json
import time

import run_phase72a_stage4_analytical as base

ANALYTICAL_OUT = base.OUT
OUT = base.ROOT / "output/phase72a-stage4-report-cost/20261008"
WORK = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\report-cost-20261008")
CORE = {
    *("p72d-total-" + key for key in ["mass", "secondary", "dpm", "outflow", "stripped", "separated", "courant", "thickness"]),
    *("p72d-lower-" + key for key in ["mass", "secondary", "dpm", "outflow", "stripped", "separated"]),
    "p72d-upper-mass", "p72d-drain-rate", "p72a-e2.7-ewf-velocity-mag-max",
}
assert len(CORE) == 17


def report_plan(state, folder, selected):
    """Disable unused writers; keep critical native reports at every update."""
    updates, paths = {}, {}
    definitions = []
    for name, item in state.items():
        if len(item["report_defs"]) != 1:
            raise RuntimeError("Benchmark requires single-definition report files")
        definition = item["report_defs"][0]
        if definition in definitions:
            raise RuntimeError("Duplicate report writer: " + definition)
        definitions.append(definition)
        enabled = selected is None or definition in selected
        updates[name] = {"active": enabled}
        if enabled:
            path = (folder / (definition + ".out")).as_posix()
            paths[definition] = path
            updates[name].update(file_name=path, frequency_of="iteration", frequency=1)
    if selected is not None and set(paths) != selected:
        raise RuntimeError("Missing core report definition")
    return updates, paths


def instrument(s, folder):
    matches = [part for part in PureWindowsPath(folder).parts if part in ("core17", "full60")]
    if len(matches) != 1:
        raise RuntimeError("Ambiguous report benchmark arm")
    arm = matches[0]
    selected = CORE if arm == "core17" else None
    files = s.settings.solution.monitor.report_files
    updates, paths = report_plan(files.get_state(), folder, selected)
    files.set_state(updates)
    actual = files.get_state()
    for name, expected in updates.items():
        assert actual[name]["active"] == expected["active"]
        if expected["active"]:
            assert actual[name]["frequency"] == 1
            assert base.native.normalized_windows_path(actual[name]["file_name"]) == base.native.normalized_windows_path(expected["file_name"])
    assert not any(item["active"] for item in s.settings.solution.monitor.report_plots.get_state().values())
    return paths


def save_pair(s, work, label):
    """Save once and use the bounded one-file checksum route for both artifacts."""
    pair = {"case": str(work / (label + ".cas.h5")), "data": str(work / (label + ".dat.h5")),
            "native_iteration": base.native_iteration(s)}
    for key in ("case", "data"):
        if base.remote_file_exists(s, pair[key]):
            raise FileExistsError(pair[key])
    s.settings.file.write_case(file_name=pair["case"])
    s.settings.file.write_data(file_name=pair["data"])
    for key in ("case", "data"):
        pair[key + "_sha256"] = base.checked_remote_sha256(
            s, pair[key], str(work / "scratch" / (key + "-" + str(time.time_ns()) + ".sha256.txt")))
    return pair


def prepare(arm):
    if base.manifest(arm).exists():
        raise RuntimeError("Reconcile existing benchmark arm before preparation")
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    work, local = WORK / arm, OUT / arm
    local.mkdir(parents=True, exist_ok=True)
    for folder in [WORK, WORK / "scratch", work, work / "scratch", work / "prepared-monitors"]:
        base.ensure_remote_directory(s, str(folder))
    live = base.snapshot(s)
    final = json.loads((ANALYTICAL_OUT / "momentum10/run-manifest.json").read_text())
    if (live["native_iteration"] == final["verified_native_end"]
            and live["film"]["film_elapsed_time"] == final["verified_film_time_s"]
            and live["parameters"] == final["prepared_parameters"]):
        base.d.q.r.require_match({"fields": live["bulk"]}, {"fields": final["bulk_reference"]})
        preserved = final["latest_pair"]
    else:
        preserved = save_pair(s, work, "preserved-N" + str(live["native_iteration"]) + "-" + str(time.time_ns()))
    parent_record = json.loads((ANALYTICAL_OUT / "momentum10/run-N41483-N41503/run-manifest.json").read_text())
    parent = parent_record["pair"]
    for key in ("case", "data"):
        actual = base.checked_remote_sha256(s, parent[key], str(work / "scratch" / ("parent-" + key + "-" + str(time.time_ns()) + ".sha256.txt")))
        assert actual == parent[key + "_sha256"]
    base.reopen_recovery_pair(s, parent)
    before = base.snapshot(s)
    assert before["native_iteration"] == 41503
    assert before["parameters"] == final["prepared_parameters"]
    base.audit(s, arm)
    # Freeze the report choice in the saved child. submit() only relocates
    # active destinations; no physical model or source coefficient changes.
    paths = instrument(s, work / "prepared-monitors")
    pair = {"case": str(work / "prepared-N41503.cas.h5"),
            "data": str(work / "prepared-N41503.dat.h5"), "native_iteration": 41503}
    present = [base.remote_file_exists(s, pair[k]) for k in ("case", "data")]
    if any(present):
        if not all(present):
            raise RuntimeError("Incomplete prepared pair: preserve and recover before retry")
        for key in ("case", "data"):
            pair[key + "_sha256"] = base.checked_remote_sha256(s, pair[key], str(work / "scratch" / ("prepared-recovery-" + key + "-" + str(time.time_ns()) + ".sha256.txt")))
    else:
        pair = save_pair(s, work, "prepared-N41503")
    base.reopen_recovery_pair(s, pair)
    after = base.snapshot(s)
    assert after["parameters"] == before["parameters"]
    assert all(after["film"][k] == v for k, v in before["film"].items() if k != "injection_interval")
    # Rewriting/reopening this parent resets the elapsed native DPM span to
    # one film step. Require the same observed reset in both benchmark arms;
    # do not confuse it with the nominal 20-film-step tracker cadence.
    assert after["film"]["injection_interval"] == 1e-5
    assert after["equations"] == before["equations"]
    base.d.q.r.require_match({"fields": after["bulk"]}, {"fields": before["bulk"]})
    base.audit(s, arm)
    active = {item["report_defs"][0] for item in s.settings.solution.monitor.report_files.get_state().values() if item["active"]}
    assert active == set(paths)
    summary = base.fields(s, local)
    m = {"status": "PREPARED_REOPEN_VERIFIED", "arm": arm, "server_id": "1",
         "authority": "human_20261008_keep_running_server1", "initialization": "FORBIDDEN",
         "blocks": [], "work_root": str(work), "requires_laptop_for_solve": False,
         "preserved_previous": preserved, "parent_pair": parent,
         "parent_film_time_s": before["film"]["film_elapsed_time"], "parent_parameters": before["parameters"],
         "bulk_reference": before["bulk"], "prepared_pair": pair, "latest_pair": pair,
         "verified_native_end": 41503, "verified_film_time_s": after["film"]["film_elapsed_time"],
         "prepared_parameters": after["parameters"], "step_s": 1e-5,
         "controlled_delta": {"active_report_count": len(active), "report_frequency": 1},
         "common_restart_span": {"parent_readback_s": before["film"]["injection_interval"],
                                 "prepared_readback_s": after["film"]["injection_interval"],
                                 "nominal_film_steps_per_dpm_step": 20},
         "field_summary": summary}
    base.dump(local / "parent-readback.json", before)
    base.dump(local / "prepared-readback.json", after)
    base.dump(base.manifest(arm), m)
    print("PREPARED_REPORT_SCREEN", arm, len(active), after["native_iteration"], flush=True)


def configure():
    base.OUT, base.WORK = OUT, WORK
    base.ARMS = {"full60": (True, 1e-5), "core17": (True, 1e-5)}
    base.instrument = instrument


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["prepare", "submit", "capture", "observe"])
    parser.add_argument("--arm", choices=["full60", "core17"], required=True)
    parser.add_argument("--count", type=int, default=1000)
    parser.add_argument("--seconds", type=int, default=30)
    args = parser.parse_args()
    configure()
    {"prepare": lambda: prepare(args.arm), "submit": lambda: base.submit(args.arm, args.count),
     "capture": lambda: base.capture(args.arm), "observe": lambda: base.observe(args.arm, args.seconds)}[args.action]()

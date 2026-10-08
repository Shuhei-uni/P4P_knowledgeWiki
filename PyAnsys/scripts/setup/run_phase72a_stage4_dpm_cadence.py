"""Native Server 1 DPM-cadence contrast; no active-run Scheme monitoring."""
from pathlib import PureWindowsPath
import argparse
import json
import numpy as np

import run_phase72a_stage4_report_cost as reports

base = reports.base
OUT = base.ROOT / "output/phase72a-stage4-dpm-cadence/20261008"
WORK = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\dpm-cadence-20261008")
ARM = "dpm40"


def cadence_parameters(parent):
    """One numerical change; retained model flags are inherited, not defaults."""
    if parent["iters-per-dpm-step"] != 20:
        raise RuntimeError("Cadence control must start from verified 20-step tracking")
    return {**parent, "iters-per-dpm-step": 40}


def instrument(s, folder):
    files = s.settings.solution.monitor.report_files
    updates, paths = reports.report_plan(files.get_state(), folder, reports.CORE)
    files.set_state(updates)
    actual = files.get_state()
    assert {x["report_defs"][0] for x in actual.values() if x["active"]} == reports.CORE
    for name, expected in updates.items():
        assert actual[name]["active"] == expected["active"]
        if expected["active"]:
            assert actual[name]["frequency"] == 1
            assert base.native.normalized_windows_path(actual[name]["file_name"]) == base.native.normalized_windows_path(expected["file_name"])
    assert not any(x["active"] for x in s.settings.solution.monitor.report_plots.get_state().values())
    return paths


def matching_films(before, after):
    for wall in ("upper", "lower"):
        x, y = np.load(before / (wall + "-fields.npz")), np.load(after / (wall + "-fields.npz"))
        ox = np.lexsort(x["centroids"].T[::-1]); oy = np.lexsort(y["centroids"].T[::-1])
        assert len(np.unique(x["centroids"], axis=0)) == len(ox)
        assert len(np.unique(y["centroids"], axis=0)) == len(oy)
        assert set(x.files) == set(y.files)
        for key in x.files:
            assert np.array_equal(x[key][ox], y[key][oy]), (wall, key)


def prepare():
    # Reuse the verified parent, preservation, report-plan and common-restart
    # procedure. This saves its 20-step child before a separate cadence child.
    reports.prepare(ARM)
    m = base.load(ARM)
    m.update(status="PREPARING_CADENCE_CHILD", authority="human_20261008_keep_running_server1")
    base.dump(base.manifest(ARM), m)
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    before = base.snapshot(s)
    expected = cadence_parameters(before["parameters"])
    assert before["parameters"] == m["prepared_parameters"]
    base.d.q.r.setparams(s, {"iters-per-dpm-step": 40})
    changed = base.snapshot(s)
    assert changed["parameters"] == expected
    assert changed["film"] == before["film"]
    assert changed["walls"] == before["walls"]
    pair = reports.save_pair(s, WORK / ARM, "prepared-dpm40-N41503")
    base.reopen_recovery_pair(s, pair)
    after = base.snapshot(s)
    assert after["native_iteration"] == 41503
    assert after["film"] == before["film"]
    assert after["parameters"] == expected
    assert after["equations"] == before["equations"]
    assert after["walls"] == before["walls"]
    base.d.q.r.require_match({"fields": after["bulk"]}, {"fields": before["bulk"]})
    base.audit(s, ARM)
    destination = OUT / ARM / "cadence-prepared-fields"
    destination.mkdir()
    summary = base.fields(s, destination)
    matching_films(OUT / ARM, destination)
    m.update(status="PREPARED_REOPEN_VERIFIED", prepared_pair=pair, latest_pair=pair,
             prepared_parameters=after["parameters"], field_summary=summary,
             controlled_delta={"iters-per-dpm-step": {"parent": 20, "child": 40}},
             report_configuration={"active_count": 17, "frequency": 1},
             common_restart_span={**m["common_restart_span"], "nominal_film_steps_per_dpm_step": 40},
             parent_film_fields_exact=True,
             claim_limit="Cadence contrast tests a normalization hypothesis; it does not prove event-mass conservation")
    base.dump(OUT / ARM / "cadence-prepared-readback.json", after)
    base.dump(base.manifest(ARM), m)
    print("PREPARED_DPM_CADENCE", 40, "steps", "FILM_FIELDS_EXACT", flush=True)


def configure():
    reports.OUT, reports.WORK = OUT, WORK
    base.OUT, base.WORK = OUT, WORK
    base.ARMS = {ARM: (True, 1e-5)}
    reports.instrument = base.instrument = instrument


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["prepare", "submit", "capture", "observe"])
    p.add_argument("--count", type=int, default=1000)
    p.add_argument("--seconds", type=int, default=30)
    a = p.parse_args()
    configure()
    {"prepare": prepare, "submit": lambda: base.submit(ARM, a.count),
     "capture": lambda: base.capture(ARM), "observe": lambda: base.observe(ARM, a.seconds)}[a.action]()

"""Continue the preserved full-momentum film with the verified 17-report plan."""
from pathlib import PureWindowsPath
import argparse
import json
import time
import run_phase72a_stage4_report_cost as reports
from run_phase72a_stage4_dpm_cadence import matching_films

base = reports.base
OUT = base.ROOT / "output/phase72a-stage4-core-development/20261008"
WORK = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\Stage4\core-development-20261008")
ARM = "core17"


def prepare():
    if base.manifest(ARM).exists():
        raise RuntimeError("Reconcile existing continuation before preparing another")
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    local, work = OUT / ARM, WORK / ARM
    local.mkdir(parents=True, exist_ok=True)
    for folder in [WORK, WORK / "scratch", work, work / "scratch", work / "prepared-monitors"]:
        base.ensure_remote_directory(s, str(folder))
    live = base.snapshot(s)
    cadence_path = base.ROOT / "output/phase72a-stage4-dpm-cadence/20261008/dpm40/run-manifest.json"
    cadence = json.loads(cadence_path.read_text())
    # Ordinary continuation is selected only after this diagnostic is saved,
    # captured and classified; never replace a still-active native run.
    assert cadence["status"] == "CHECKPOINT_VERIFIED"
    comparison = json.loads((cadence_path.parents[1] / "comparison-summary.json").read_text())
    assert comparison["status"] == "CADENCE_COMPARISON"
    assert live["native_iteration"] == cadence["verified_native_end"]
    assert live["parameters"] == cadence["prepared_parameters"]
    assert live["film"]["film_elapsed_time"] == cadence["verified_film_time_s"]
    base.d.q.r.require_match({"fields": live["bulk"]}, {"fields": cadence["bulk_reference"]})
    preserved = cadence["latest_pair"]
    original = json.loads((reports.ANALYTICAL_OUT / "momentum10/run-manifest.json").read_text())
    assert original["verified_native_end"] == 43483
    parent = original["latest_pair"]
    for key in ("case", "data"):
        digest = base.checked_remote_sha256(s, parent[key], str(work / "scratch" / ("parent-" + key + "-" + str(time.time_ns()) + ".sha256.txt")))
        assert digest == parent[key + "_sha256"]
    base.reopen_recovery_pair(s, parent)
    before = base.snapshot(s)
    assert before["native_iteration"] == 43483
    assert before["parameters"] == original["prepared_parameters"]
    assert before["film"]["film_elapsed_time"] == original["verified_film_time_s"]
    base.d.q.r.require_match({"fields": before["bulk"]}, {"fields": original["bulk_reference"]})
    base.audit(s, ARM)
    assert before["parameters"]["iters-per-dpm-step"] == 20
    prior_fields = local / "parent-fields"; prior_fields.mkdir()
    base.fields(s, prior_fields)
    paths = reports.instrument(s, work / "prepared-monitors")
    pair = reports.save_pair(s, work, "prepared-N43483")
    base.reopen_recovery_pair(s, pair)
    after = base.snapshot(s)
    assert after["parameters"] == before["parameters"]
    assert all(after["film"][key] == value for key, value in before["film"].items() if key != "injection_interval")
    assert after["film"]["injection_interval"] == 1e-5
    assert after["equations"] == before["equations"]
    assert after["walls"] == before["walls"]
    base.d.q.r.require_match({"fields": after["bulk"]}, {"fields": before["bulk"]})
    base.audit(s, ARM)
    summary = base.fields(s, local)
    matching_films(prior_fields, local)
    m = {"status": "PREPARED_REOPEN_VERIFIED", "arm": ARM, "server_id": "1",
         "authority": "human_20261008_keep_running_server1", "initialization": "FORBIDDEN",
         "requires_laptop_for_solve": False, "blocks": [], "work_root": str(work),
         "preserved_previous": preserved, "parent_pair": parent, "prepared_pair": pair, "latest_pair": pair,
         "parent_film_time_s": before["film"]["film_elapsed_time"], "parent_parameters": before["parameters"],
         "prepared_parameters": after["parameters"], "bulk_reference": before["bulk"],
         "verified_native_end": 43483, "verified_film_time_s": after["film"]["film_elapsed_time"],
         "step_s": 1e-5, "field_summary": summary, "parent_film_fields_exact": True,
         "controlled_delta": {"report_count": 17, "physics": "NONE", "numerics": "NONE"},
         "report_paths": paths,
         "common_restart_span": {"parent_readback_s": before["film"]["injection_interval"], "prepared_readback_s": 1e-5},
         "scientific_classification": "DIAGNOSTIC_DEVELOPMENT_ACCURACY_UNQUALIFIED",
         "claim_limit": "Continues film development; unresolved DPM event ledger and absent inner residuals prevent accuracy qualification"}
    base.dump(local / "parent-readback.json", before)
    base.dump(local / "prepared-readback.json", after)
    base.dump(base.manifest(ARM), m)
    print("PREPARED_CORE_DEVELOPMENT", 43483, "FILM_FIELDS_EXACT", flush=True)


def configure():
    base.OUT, base.WORK = OUT, WORK
    base.ARMS = {ARM: (True, 1e-5)}
    base.instrument = reports.instrument


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["prepare", "submit", "capture", "observe"])
    p.add_argument("--count", type=int, default=5000)
    p.add_argument("--seconds", type=int, default=30)
    a = p.parse_args(); configure()
    {"prepare": prepare, "submit": lambda: base.submit(ARM, a.count),
     "capture": lambda: base.capture(ARM), "observe": lambda: base.observe(ARM, a.seconds)}[a.action]()

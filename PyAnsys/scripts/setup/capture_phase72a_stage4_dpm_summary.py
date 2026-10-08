"""Preserve live steady-flow DPM reporting before case/data reopen."""
from pathlib import Path, PureWindowsPath
import argparse
import json
import time
import run_phase72a_stage4_analytical as base


def capture(manifest_path):
    m = json.loads(manifest_path.read_text())
    if m["status"] != "SUBMITTED_NATIVE":
        raise RuntimeError("Capture the native live summary before endpoint recovery/reopen")
    local = base.ROOT.parent / m["active_block"]
    record = json.loads((local / "run-manifest.json").read_text())
    s = base.attach()
    assert not s.settings.solution.run_calculation.iterating()
    before = base.snapshot(s)
    assert before["native_iteration"] == record["target"]
    assert before["parameters"] == record["before"]["parameters"]
    stamp = str(time.time_ns())
    work = PureWindowsPath(record["work"])
    path = work / ("live-dpm-summary-" + stamp + ".trn")
    assert not base.remote_file_exists(s, str(path))
    s.settings.file.start_transcript(file_name=path.as_posix())
    try:
        # Version-matched generated v252 TUI and official command list both
        # identify this as reporting; never issue Display/Track here.
        s.settings.results.report.discrete_phase.summary()
    finally:
        s.settings.file.stop_transcript()
    digest = base.checked_remote_sha256(s, str(path), str(work / "scratch" / ("dpm-summary-" + stamp + ".sha256.txt")))
    folder = local / "live-dpm-evidence"
    folder.mkdir(exist_ok=True)
    summary_file = folder / ("summary-" + stamp + ".trn")
    receipt = base.store_verified_text(s, str(path), summary_file, digest)
    stale = "out-dated" in summary_file.read_text()
    after = base.snapshot(s)
    for key in ["native_iteration", "film", "parameters", "equations", "bulk", "walls"]:
        assert before[key] == after[key], key
    state = s.settings.setup.models.discrete_phase.get_state()
    base.dump(folder / ("receipt-" + stamp + ".json"), {
        "native_iteration": after["native_iteration"], "no_solve": True,
        "summary_status": "UNAVAILABLE_STALE" if stale else "REPORTED_PENDING_INTERPRETATION",
        "scientific_state_unchanged": True, "transcript": receipt,
        "dpm_state": state,
        "claim_limit": "One final tracking summary is not an integrated event-mass ledger"})
    print("LIVE_DPM_SUMMARY_STALE" if stale else "LIVE_DPM_SUMMARY_PRESERVED", after["native_iteration"], folder, flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    capture(p.parse_args().manifest)

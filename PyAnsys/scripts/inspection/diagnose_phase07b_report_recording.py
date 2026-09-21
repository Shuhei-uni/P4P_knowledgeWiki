"""Exercise three source-free steady iterations, capture files, restore N=10.

Technical recording diagnostic only; not part of any collector screen.
"""
from __future__ import annotations
import json
import signal
import ntpath
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "src"))
from dotenv import load_dotenv
load_dotenv(BASE / ".env")
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.common import remote_file_exists

ZONE = "simple-spiral-separator--brine-outlet-"
ROOT = "C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal"


def source_flags(s):
    return {p: s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.enable()
            for p in ["mixture", "phase-1", "phase-2"]}


def main():
    folder = BASE / "output/phase07b_preparation"
    recovery = json.loads((folder / "diagnostic-recovery.json").read_text())
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    r = {"report": ROOT + "/reports/p7b-recording-diagnostic-" + stamp + ".out",
         "transcript": ROOT + "/logs/p7b-recording-diagnostic-" + stamp + ".trn",
         "final_case": ROOT + "/case-data/p7b-recording-diagnostic-" + stamp + ".cas.h5",
         "requested_iterations": 3, "scientific_screen": False, "status": "PREPARING"}
    out = folder / "diagnostic-report-recording.json"
    def persist():
        out.write_text(json.dumps(r, indent=2, default=str) + "\n")
    # The installed PyFluent reflection handshake has no RPC deadline. Bound
    # only local connection construction; never exit the remote Fluent server.
    def connection_deadline(signum, frame):
        raise TimeoutError("PyFluent connection construction exceeded 60 seconds")
    persist()
    print("CONNECTING_WITH_60_SECOND_DEADLINE", flush=True)
    previous_handler = signal.signal(signal.SIGALRM, connection_deadline)
    signal.alarm(60)
    try:
        s = connect(server_id=1, start_transcript=False, tcp_timeout_seconds=5)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous_handler)
    print("CONNECTED_CHECKING_REPORT_DEFINITION", flush=True)
    assert s.rp_vars("sol/iterations") == 10
    assert not any(source_flags(s).values())
    assert s.settings.setup.general.solver.time() == "steady"
    # Reconstruct the already persisted diagnostic fixture after wrap-up restored
    # the original source-free pair. Disable its sources before any solve.
    fixture = json.loads((folder / "diagnostic-source-persistence.json").read_text())
    print("LOADING_EXPRESSION_FIXTURE", flush=True)
    s.settings.file.read_case_data(file_name=fixture["case"])
    for phase in ["mixture", "phase-1", "phase-2"]:
        s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[phase].sources.enable = False
    assert s.rp_vars("sol/iterations") == 10
    assert not any(source_flags(s).values())
    definitions = s.settings.solution.report_definitions.single_valued_expression
    if "p7b-diag-water-expression-native" not in definitions.get_object_names():
        definitions.create(name="p7b-diag-water-expression-native")
    ex = s.settings.solution.report_definitions.single_valued_expression["p7b-diag-water-expression-native"]
    ex.definition = "P7bDiagWaterVolume"
    assert ex.definition() == "P7bDiagWaterVolume"
    names = ["p7b-diag-water-expression-native", "p7b-diag-native-water-volume"]
    r["initial_computed"] = s.settings.solution.report_definitions.compute(report_defs=names)
    files = s.settings.solution.monitor.report_files
    if "p7b-diag-history" not in files.get_object_names():
        files.create(name="p7b-diag-history")
    rf = s.settings.solution.monitor.report_files["p7b-diag-history"]
    rf.file_name = r["report"]
    rf.report_defs = names
    rf.frequency = 1
    rf.active = True
    r["report_file_readback"] = rf.get_state()
    persist()
    assert ntpath.normcase(ntpath.normpath(rf.file_name())) == ntpath.normcase(ntpath.normpath(r["report"]))
    assert rf.frequency_of() == "iteration"
    r["initial_source_flags"] = source_flags(s)
    r["status"] = "RUNNING"
    persist()
    s.settings.file.start_transcript(file_name=r["transcript"])
    print("RUNNING_THREE_SOURCE_FREE_ITERATIONS", flush=True)
    s.settings.solution.run_calculation.iterate(iter_count=3)
    r["final_iteration"] = s.rp_vars("sol/iterations")
    assert r["final_iteration"] == 13
    assert not any(source_flags(s).values())
    r["final_computed"] = s.settings.solution.report_definitions.compute(report_defs=names)
    s.settings.file.write_case_data(file_name=r["final_case"])
    r["final_data"] = r["final_case"].replace(".cas.h5", ".dat.h5")
    r["final_pair_exists"] = all(remote_file_exists(s, r[k]) for k in ["final_case", "final_data"])
    assert r["final_pair_exists"]
    s.settings.file.stop_transcript()
    report_text = read_text(s, r["report"])
    transcript_text = read_text(s, r["transcript"])
    (folder / "diagnostic-recording.out").write_text(report_text)
    (folder / "diagnostic-recording.trn").write_text(transcript_text)
    r["report_text"] = report_text
    r["status"] = "RECORDED_RESTORING"
    persist()
    print("RECORDED", report_text, flush=True)
    s.settings.file.read_case_data(file_name=recovery["case"])
    r["restored_iteration"] = s.rp_vars("sol/iterations")
    r["restored_source_flags"] = source_flags(s)
    r["restored_solver"] = s.settings.setup.general.solver.get_state()
    r["restored_case"] = recovery["case"]
    assert r["restored_iteration"] == 10
    assert not any(r["restored_source_flags"].values())
    r["status"] = "RESTORED_PENDING_HISTORY_VALIDATION"
    persist()
    print(r["status"], flush=True)


if __name__ == "__main__":
    main()

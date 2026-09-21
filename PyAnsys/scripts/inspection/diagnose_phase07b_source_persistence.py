"""Check native-expression source attachment and same-session save/reload.

No iterations. The six S20 source slots are exercised, saved and read back,
then source enables are switched off. This is not a source-coupling smoke test.
"""
from __future__ import annotations
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "src"))
from dotenv import load_dotenv
load_dotenv(BASE / ".env")
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists

ZONE = "simple-spiral-separator--brine-outlet-"
ROOT = "C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal"
HOOKS = {"phase-2": {"mass": "P7bDiagSink"}, "mixture": {
    "x-momentum": "P7bDiagSinkX", "y-momentum": "P7bDiagSinkY",
    "z-momentum": "P7bDiagSinkZ", "k": "P7bDiagSinkK",
    "epsilon": "P7bDiagSinkEpsilon"}}


def snapshot(s):
    return {
        "iteration": s.rp_vars("sol/iterations"),
        "solver": s.settings.setup.general.solver.get_state(),
        "sources": {p: s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.get_state()
                    for p in ["mixture", "phase-1", "phase-2"]},
        "expressions": s.settings.setup.named_expressions.get_state(),
        "water_volume": s.settings.setup.named_expressions["P7bDiagWaterVolume"].get_value(),
        "viscous": s.settings.setup.models.viscous.get_state(),
        "multiphase": s.settings.setup.models.multiphase.get_state(),
        "boundaries": s.settings.setup.boundary_conditions.get_state(),
        "methods": s.settings.solution.methods.get_state(),
    }


def main():
    s = connect(server_id=1, start_transcript=False, tcp_timeout_seconds=5)
    assert s.rp_vars("sol/iterations") == 10
    for p in ["mixture", "phase-1", "phase-2"]:
        assert s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.enable() is False
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    record = {"case": ROOT + "/case-data/p7b-expression-diagnostic-" + stamp + ".cas.h5",
              "status": "STARTED", "source_coupling_tested": False}
    record["data"] = record["case"].replace(".cas.h5", ".dat.h5")
    out = BASE / "output/phase07b_preparation/diagnostic-source-persistence.json"
    out.write_text(json.dumps(record, indent=2))
    for phase, sources in HOOKS.items():
        s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[phase].sources.enable = True
        for equation, expression in sources.items():
            src = s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[phase].sources
            src.terms[equation].resize(size=1)
            src.terms[equation][0].option = "value"
            item = s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[phase].sources.terms[equation][0]
            assert item.value.is_active()
            item.value = expression
            assert item.value() == expression
            print("ATTACHED", phase, equation, item.get_state(), flush=True)
    record["before"] = snapshot(s)
    s.settings.file.write_case_data(file_name=record["case"])
    assert all(remote_file_exists(s, record[k]) for k in ["case", "data"])
    print("SAVED", record["case"], flush=True)
    s.settings.file.read_case_data(file_name=record["case"])
    record["after"] = snapshot(s)
    record["equal_readback"] = record["before"] == record["after"]
    record["configuration_equal"] = {
        k: v for k, v in record["before"].items() if k != "water_volume"
    } == {k: v for k, v in record["after"].items() if k != "water_volume"}
    record["water_volume_close"] = math.isclose(
        record["before"]["water_volume"], record["after"]["water_volume"],
        rel_tol=1e-12, abs_tol=1e-15)
    for phase in HOOKS:
        s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[phase].sources.enable = False
    record["final_sources"] = {p: s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.get_state()
                               for p in ["mixture", "phase-1", "phase-2"]}
    record["status"] = "PASS" if record["configuration_equal"] and record["water_volume_close"] else "MISMATCH"
    out.write_text(json.dumps(record, indent=2, default=str) + "\n")
    print("RESULT", record["status"], record["final_sources"], flush=True)
    assert record["status"] == "PASS"


if __name__ == "__main__":
    main()

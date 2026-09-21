"""Stage unhooked Phase7b native expressions and record their live diagnostics.

No solver iteration, C compilation, source attachment, or whole-domain export.
Requires the source-free N=10 preparation state and a saved diagnostic pair.
Definitions are diagnostic objects, not proof of source-coupling readiness.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PYANSYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PYANSYS / "src"))
from dotenv import load_dotenv

load_dotenv(PYANSYS / ".env")
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists

ZONE = "simple-spiral-separator--brine-outlet-"
TOPS = [-1.1836669883728028, -.8827502412796020, -.5818334941864014,
        -.2809167470932006, .020]


def main():
    output = PYANSYS / "output/phase07b_preparation/diagnostic-expressions.json"
    recovery = json.loads((output.parent / "diagnostic-recovery.json").read_text())
    s = connect(server_id=1, start_transcript=False, tcp_timeout_seconds=5)
    assert s.rp_vars("sol/iterations") == 10
    assert s.settings.setup.general.solver.time() == "steady"
    fluid = s.settings.setup.cell_zone_conditions.fluid[ZONE]
    for phase in ["mixture", "phase-1", "phase-2"]:
        assert fluid.phase[phase].sources.enable() is False
    assert all(remote_file_exists(s, recovery[key]) for key in ["case", "data"])
    record = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "recovery": recovery, "source_attachment": False, "expressions": {}}
    loc = f"['{ZONE}']"
    definitions = {
        "P7bDiagAlpha": 'Volumefraction(phase="phase-2")',
        "P7bDiagLiquidU": 'Velocity(phase="phase-2").x',
        "P7bDiagLiquidV": 'Velocity(phase="phase-2").y',
        "P7bDiagLiquidW": 'Velocity(phase="phase-2").z',
        "P7bDiagK": 'TurbulentKineticEnergyk(phase="mixture")',
        "P7bDiagEpsilon": 'TurbulenceDissipationRate(phase="mixture")',
        "P7bDiagWaterVolume": f"VolumeInt(P7bDiagAlpha,{loc})",
        "P7bDiagLiquidIn": 'MassFlow(["liquid-inlet"],phase="phase-2")',
    }
    for percentage, top in zip([20, 40, 60, 80, 100], TOPS):
        predicate = f"AND(y >= -1.4845837354660034[m], y <= {top:.16g}[m])"
        definitions[f"P7bDiagMask{percentage}"] = f"IF({predicate},1.0,0.0)"
        definitions[f"P7bDiagCount{percentage}"] = f"CountIf({predicate},{loc})"
        definitions[f"P7bDiagVolume{percentage}"] = f"VolumeInt(P7bDiagMask{percentage},{loc})"
    definitions.update({
        "P7bDiagSink": "-P7bDiagMask20*881.77[kg/m^3]*min(1.0,max(0.0,P7bDiagAlpha))/0.0024095893[s]",
        "P7bDiagSinkX": "P7bDiagSink*P7bDiagLiquidU",
        "P7bDiagSinkY": "P7bDiagSink*P7bDiagLiquidV",
        "P7bDiagSinkZ": "P7bDiagSink*P7bDiagLiquidW",
        "P7bDiagSinkK": "P7bDiagSink*P7bDiagK",
        "P7bDiagSinkEpsilon": "P7bDiagSink*P7bDiagEpsilon",
        "P7bDiagSinkIntegral": f"VolumeInt(P7bDiagSink,{loc})",
    })
    for name, definition in definitions.items():
        entry = {"definition": definition}
        try:
            if name not in s.settings.setup.named_expressions.get_object_names():
                s.settings.setup.named_expressions.create(name=name)
            else:
                assert s.settings.setup.named_expressions[name].definition() == definition
            obj = s.settings.setup.named_expressions[name]
            obj.definition = definition
            entry["readback"] = obj.get_state()
            # get_info() raises a Fluent CDR error in this observed 252 case.
            # Use exact definition/unit readback plus direct scalar evaluation.
            if any(x in name for x in ["Count", "Volume", "LiquidIn", "Integral"]):
                entry["value"] = obj.get_value()
            entry["status"] = "RETURNED"
        except Exception as exc:
            entry.update(status="ERROR", error=str(exc))
        record["expressions"][name] = entry
        output.write_text(json.dumps(record, indent=2, default=str) + "\n")
        print(name, json.dumps(entry, default=str), flush=True)
    report = s.settings.solution.report_definitions.volume
    name = "p7b-diag-native-water-volume"
    if name not in report.get_object_names():
        report.create(name=name)
    report[name].report_type = "volume-integral"
    report[name].field = "phase-2-vof"
    report[name].cell_zones = [ZONE]
    record["native_volume_report"] = {
        "state": report[name].get_state(),
        "fields": report[name].field.allowed_values(),
        "zones": report[name].cell_zones.allowed_values(),
    }
    record["iteration_after"] = s.rp_vars("sol/iterations")
    output.write_text(json.dumps(record, indent=2, default=str) + "\n")
    print("NATIVE_REPORT", json.dumps(record["native_volume_report"], default=str), flush=True)


if __name__ == "__main__":
    main()

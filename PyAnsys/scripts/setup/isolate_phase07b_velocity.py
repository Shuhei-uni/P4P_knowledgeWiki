"""Isolate one unhooked Phase 7b velocity operation; never solve or shut down.

Each RPC has its own persisted stage/result so an asynchronous Cortex error
cannot erase preceding successful values. Requires the preserved clean N3 state.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import json
import signal
import sys
import traceback

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE / "src"))
from dotenv import load_dotenv
load_dotenv(BASE / ".env")
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import read_text

ROOT = "C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal"
ZONE = "simple-spiral-separator--brine-outlet-"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["native", "phase", "mixture", "slip"])
    parser.add_argument("axis", choices=list("xyz"))
    parser.add_argument("--evaluation", choices=["direct", "report", "field-report"], default="direct")
    parser.add_argument("--component-first", action="store_true",
                        help="Test scalar component context syntax, Velocity.x(phase=...).")
    parser.add_argument("--reload-clean", action="store_true",
                        help="Restore the preserved Phase 7b N3 pair before this probe.")
    args = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = f"velocity-{args.operation}-{args.axis}-{args.evaluation}-{stamp}"
    out = BASE / "output/phase07b_preparation" / run
    out.mkdir()
    record = {"operation": args.operation, "axis": args.axis, "evaluation": args.evaluation,
              "component_first": args.component_first,
              "iterations_issued": 0, "source_attachment": False, "steps": [],
              "remote_transcript": f"{ROOT}/logs/p7b-{run}.trn"}

    def persist():
        (out / "result.json").write_text(json.dumps(record, indent=2, default=str) + "\n")

    def deadline(*_args):
        raise TimeoutError("Diagnostic RPC deadline exceeded")

    signal.signal(signal.SIGALRM, deadline)

    def step(name, fn, seconds=30):
        entry = {"name": name, "state": "STARTED"}
        record["steps"].append(entry)
        persist()
        print(name, flush=True)
        signal.alarm(seconds)
        try:
            value = fn()
            entry.update(state="PASS", value=value)
            return value
        except Exception as exc:
            entry.update(state="FAILED", error=str(exc))
            raise
        finally:
            signal.alarm(0)
            persist()

    s = None
    transcript_started = False
    try:
        signal.alarm(30)
        s = connect(server_id=1, start_transcript=False, tcp_timeout_seconds=5)
        signal.alarm(0)
        record["process"] = {k: getattr(s.connection_properties, k, None)
                             for k in ["cortex_pid", "fluent_host_pid"]}
        def stream_line(text):
            with (out / "stream-stages.jsonl").open("a") as handle:
                handle.write(json.dumps({"stage": record["steps"][-1]["name"] if record["steps"] else "preflight",
                                         "text": text}) + "\n")
        s.transcript.register_callback(stream_line)
        s.transcript.start(file_name=str(out / "stream.trn"), write_to_stdout=False)
        if args.reload_clean:
            case = ROOT + "/case-data/p7b-clean-smoke-20260912T080713Z.cas.h5"
            assert remote_file_exists(s, case) and remote_file_exists(s, case.replace(".cas.h5", ".dat.h5"))
            step("restore_clean_pair", lambda: s.settings.file.read_case_data(file_name=case), 120)
        assert step("iteration", lambda: s.settings.setup.named_expressions["P7bGlobalIteration"].get_value()) == 3
        flags = step("source_flags", lambda: {
            p: s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[p].sources.enable()
            for p in ["mixture", "phase-1", "phase-2"]})
        assert not any(flags.values())
        step("start_transcript", lambda: s.settings.file.start_transcript(file_name=record["remote_transcript"]))
        transcript_started = True
        if args.operation == "native":
            name = "p7b-isolated-phase-" + args.axis
            group = s.settings.solution.report_definitions.volume
            if name not in group.get_object_names():
                step("create_native_report", lambda: group.create(name=name))
            group = s.settings.solution.report_definitions.volume
            step("report_type", lambda: group[name].report_type.set_state("volume-integral"))
            field = f"phase-2-{args.axis}-velocity"
            assert field in group[name].field.allowed_values()
            step("report_field", lambda: group[name].field.set_state(field))
            step("report_zone", lambda: group[name].cell_zones.set_state([ZONE]))
            step("report_readback", lambda: group[name].get_state())
            value = step("compute_native_report", lambda: s.settings.solution.report_definitions.compute(report_defs=[name]))
        else:
            name = "P7bIsolated" + args.operation.title() + args.axis.upper()
            if args.evaluation == "field-report":
                name += "Field"
            liq = f'Velocity(phase="phase-2").{args.axis}'
            mix = f'Velocity(phase="mixture").{args.axis}'
            if args.component_first:
                liq = f'Velocity.{args.axis}(phase="phase-2")'
                mix = f'Velocity.{args.axis}(phase="mixture")'
            field = {"phase": liq, "mixture": mix, "slip": f"abs({liq}-{mix})"}[args.operation]
            definition = field if args.evaluation == "field-report" else f'VolumeInt({field},["{ZONE}"])'
            group = s.settings.setup.named_expressions
            if name not in group.get_object_names():
                step("create_expression", lambda: group.create(name=name))
            group = s.settings.setup.named_expressions
            step("set_definition", lambda: group[name].definition.set_state(definition))
            step("definition_readback", lambda: group[name].definition())
            if args.evaluation == "direct":
                value = step("evaluate_expression", lambda: group[name].get_value())
            elif args.evaluation == "report":
                report_name = f"p7b-isolated-{args.operation}-{args.axis}-expression"
                reports = s.settings.solution.report_definitions.single_valued_expression
                if report_name not in reports.get_object_names():
                    step("create_expression_report", lambda: reports.create(name=report_name))
                reports = s.settings.solution.report_definitions.single_valued_expression
                step("set_expression_report", lambda: reports[report_name].definition.set_state(name))
                step("expression_report_readback", lambda: reports[report_name].get_state())
                value = step("compute_expression_report", lambda: s.settings.solution.report_definitions.compute(report_defs=[report_name]))
            else:
                report_name = f"p7b-isolated-{args.operation}-{args.axis}-field"
                reports = s.settings.solution.report_definitions.volume
                if report_name not in reports.get_object_names():
                    step("create_field_report", lambda: reports.create(name=report_name))
                reports = s.settings.solution.report_definitions.volume
                step("field_report_type", lambda: reports[report_name].report_type.set_state("volume-integral"))
                assert "expr:" + name in reports[report_name].field.allowed_values()
                step("field_report_expression", lambda: reports[report_name].field.set_state("expr:" + name))
                step("field_report_zone", lambda: reports[report_name].cell_zones.set_state([ZONE]))
                step("field_report_readback", lambda: reports[report_name].get_state())
                value = step("compute_field_report", lambda: s.settings.solution.report_definitions.compute(report_defs=[report_name]))
        record["value"] = value
        step("stop_transcript", lambda: s.settings.file.stop_transcript())
        transcript_started = False
        text = step("retrieve_transcript", lambda: read_text(s, record["remote_transcript"]))
        (out / "diagnostic.trn").write_text(text)
        record["cortex_faults"] = text.count("SEGMENTATION VIOLATION")
        if record["cortex_faults"]:
            raise RuntimeError("Cortex fatal signal recorded in diagnostic transcript")
        record["status"] = "PASS"
    except Exception as exc:
        signal.alarm(0)
        record.update(status="FAILED", error=str(exc))
        (out / "error.txt").write_text(traceback.format_exc())
        if s is not None and transcript_started:
            try:
                step("stop_failed_transcript", lambda: s.settings.file.stop_transcript(), 10)
                text = step("retrieve_failed_transcript", lambda: read_text(s, record["remote_transcript"]), 10)
                (out / "diagnostic.trn").write_text(text)
            except Exception:
                pass
        raise
    finally:
        if s is not None:
            try:
                s.transcript.stop()
            except Exception:
                pass
        persist()
        print("EVIDENCE", out, flush=True)
    print("RESULT", record["status"], record.get("value"), flush=True)


if __name__ == "__main__":
    main()

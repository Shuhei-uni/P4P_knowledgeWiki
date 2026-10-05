"""Continue the verified Server 1 adaptive-film child in native 1000-update batches.

Attach only. Never initialize, launch, terminate, or overwrite an endpoint.
Time and film balance come from native film clocks and file-backed reports.
"""
from pathlib import Path, PureWindowsPath
import argparse
import base64
import json
import math
import re
import sys
import subprocess
import traceback

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts/setup")]
from pyansys_fluent.connection import connect
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.common import quote_scheme_string
from pyansys_fluent.stage4_native import ensure_remote_directory, remote_file_sha256
from run_phase72a_e27_server1_continuation import native_iteration, pair_save, dump
from run_phase72a_local_film_replay import readback

OUT = ROOT / "output/phase72a-adaptive-server1/20261005"
WORK = PureWindowsPath(r"C:\Users\syok443\Documents\FluentRuns\Phase72A\ContactAbsorber\adaptive-20261005")
FILM = re.compile(r"Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)")
ROW = re.compile(r"^\s*(\d+)\s+[\d.+-]+e[+-]\d+\s+", re.M)


def film_records(text):
    pending = None
    result = {}
    for line in text.splitlines():
        match = FILM.search(line)
        if match:
            if pending is not None:
                raise RuntimeError("Unmapped film time record")
            pending = [float(v) for v in match.groups()]
        elif ROW.match(line) and pending is not None:
            coordinate = int(ROW.match(line)[1])
            if coordinate in result:
                raise RuntimeError("Duplicate native film coordinate")
            result[coordinate] = pending
            pending = None
    if pending is not None:
        raise RuntimeError("Missing terminal iteration for film record")
    return result


def history(text):
    values = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit():
            values[int(parts[0])] = float(parts[1])
    return values


def assess(histories, clocks, start, end):
    mass = histories["p72a-e2.7-ewf-film-mass-total"]
    drain = histories["p72a-e2.7-ewf-outflow-mass-total"]
    accrete = histories["p72a-e2.7-ewf-secondary-phase-mass-total"]
    ids = list(range(start + 1, end + 1))
    previous_time = 0.1 if start == 33586 else clocks[start][0]
    initial_time = previous_time
    integrated = 0.0
    for i in ids:
        step = clocks[i][0] - previous_time
        if step <= 0:
            raise RuntimeError("Non-increasing native film clock")
        integrated += accrete[i] * step
        previous_time = clocks[i][0]
    duration = previous_time - initial_time
    gain = mass[end] - mass[start]
    drained = drain[end] - drain[start]
    return {
        "native_window": [start, end], "film_elapsed_s": duration,
        "inventory_gain_kg": gain, "inventory_growth_kg_s": gain / duration,
        "integrated_accretion_kg": integrated, "drained_mass_kg": drained,
        "drainage_deficit_percent": 100 * (integrated - drained) / integrated,
        "storage_fraction_of_accretion_percent": 100 * gain / integrated,
        "film_ledger_error_percent": 100 * abs(gain + drained - integrated) / abs(integrated),
        "accepted_step_printed_min_s": min(clocks[i][1] for i in ids),
        "accepted_step_printed_max_s": max(clocks[i][1] for i in ids),
        "peak_solved_film_cfl": max(clocks[i][2] for i in ids),
        "time_basis": "Native cumulative film clock differences; printed timestep is rounded",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blocks", type=int, default=1)
    parser.add_argument("--target-additional-film-time", type=float)
    args = parser.parse_args()
    path = OUT / "run-manifest.json"
    manifest = json.loads(path.read_text()) if path.exists() else {
        "authority": "human_2026_10_05_full_server1_ownership",
        "server_id": "1", "parent_native_iteration": 33586,
        "parent_case_sha256": "1dedd5e01fca7b694c7af4c9da23f823c328931b6ee64a7aa717a63b25e0fe11",
        "parent_data_sha256": "5810d6049a6862d04e2c55791eee75de9a471d349ab73052366ca69f3c87c25e",
        "parent_native_film_clock_s": 0.1, "parent_added_film_time_from_E27_s": 0.02,
        "lineage": "Server 1 continuation of independent four-rank local N33586 endpoint",
        "controlled_delta": {"ewf-adaptive?": True, "adapt-init-dt": 1e-6,
                             "adapt-tstp-inc": 1.2, "adapt-tstp-dec": 2.0},
        "courant_target": 0.05, "native_maximum_step_bound": "NOT_EXPOSED_OR_CLAIMED",
        "work_root": str(WORK), "blocks": [], "verified_native_end": 33606,
        "status": "SMOKE_COMPLETE",
        "claim_limit": "Film ledger only; no full separator closure or physical validation",
    }
    if manifest["status"] in {"RUNNING", "EXECUTION_UNCERTAIN"}:
        raise RuntimeError("Reconcile previous command before continuation")
    solver = connect("1", start_transcript=False)
    expected = manifest["verified_native_end"]
    if native_iteration(solver) != expected:
        raise RuntimeError("Live endpoint differs from verified continuation")
    reference = json.loads((OUT / "prepared-reopen.json").read_text())
    actual = readback(solver)
    for group in reference:
        if group != "fields" and actual[group] != reference[group]:
            raise RuntimeError(f"Invariant changed: {group}")
    solver.settings.file.auto_save.retain_most_recent_files = False
    report_paths = {}
    for name in solver.settings.solution.monitor.report_files.get_object_names():
        obj = solver.settings.solution.monitor.report_files[name]
        defs = obj.report_defs()
        if len(defs) != 1 or obj.frequency() != 1 or not obj.active():
            raise RuntimeError(f"Invalid report instrumentation: {name}")
        report_paths[defs[0]] = obj.file_name()
    manifest["report_paths"] = report_paths
    try:
        for _ in range(args.blocks):
            start = native_iteration(solver)
            end = start + 1000
            transcript = OUT / f"batch-N{start}-N{end}.txt"
            if transcript.exists():
                raise RuntimeError("Existing batch transcript; reconcile before submission")
            manifest.update(status="RUNNING", command=f"/solve/iterate 1000", active_native_window=[start, end])
            dump(path, manifest)
            print("SUBMIT", start, end, flush=True)
            solver.transcript.start(file_name=str(transcript), write_to_stdout=False)
            solver.tui.solve.iterate(1000)
            # A settings RPC after the native solve provides a terminal service barrier.
            if native_iteration(solver) != end:
                raise RuntimeError("Native solve did not reach requested endpoint")
            current = readback(solver)
            solver.transcript.stop()
            all_text = (OUT / "adaptive-smoke-transcript.txt").read_text()
            for file in sorted(OUT.glob("batch-N*-N*.txt")):
                all_text += "\n" + file.read_text()
            clocks = film_records(all_text)
            if set(clocks) != set(range(33587, end + 1)):
                raise RuntimeError("Film clock history incomplete")
            histories = {name: history(read_text(solver, remote)) for name, remote in report_paths.items()}
            if any(set(h) != set(range(33586, end + 1)) for h in histories.values()):
                raise RuntimeError("Native report history incomplete")
            dump(OUT / "report-histories.json", {
                k: {"iterations": sorted(v), "values": [v[i] for i in sorted(v)], "file": report_paths[k]}
                for k, v in histories.items()})
            dump(OUT / "film-clock-history.json", {str(i): v for i, v in clocks.items()})
            metrics = assess(histories, clocks, start, end)
            metrics["overall"] = assess(histories, clocks, 33586, end)
            metrics["maximum_thickness_m"] = current["fields"]["p72a-e2.7-ewf-thickness-max"][0]
            metrics["film_inventory_kg"] = current["fields"]["p72a-e2.7-ewf-film-mass-total"][0]
            metrics["bulk_liquid_inventory_kg"] = current["fields"]["v2-total-liquid-mass"][0]
            metrics["phase2_outlet_without_sources_kg_s"] = current["fields"]["v2-flux-phase2-steamoutlet(without-sources)"][0]
            pair = pair_save(solver, WORK / f"adaptive-block-N{end}.cas.h5", WORK / "scratch", scratch_tag=f"N{end}")
            dump(OUT / f"endpoint-N{end}.json", {"pair": pair, "readback": current, "metrics": metrics})
            manifest["blocks"].append(metrics)
            manifest.update(status="BLOCK_COMPLETE", verified_native_end=end, latest_pair=pair,
                            added_film_time_since_N33586_s=clocks[end][0] - 0.1,
                            total_added_film_time_from_E27_s=0.02 + clocks[end][0] - 0.1)
            dump(path, manifest)
            print("BLOCK_COMPLETE", json.dumps(metrics), flush=True)
            if not all(math.isfinite(x) for x in [metrics["film_inventory_kg"], metrics["maximum_thickness_m"]]):
                raise RuntimeError("Nonfinite film state")
            if metrics["maximum_thickness_m"] > 0.003 or metrics["film_inventory_kg"] > 12.3 or metrics["peak_solved_film_cfl"] > 1:
                manifest["status"] = "NUMERICAL_RECOVERY_REQUIRED"
                dump(path, manifest)
                return 2
            if metrics["overall"]["film_ledger_error_percent"] > 1:
                manifest["status"] = "FILM_LEDGER_REVIEW_REQUIRED"
                dump(path, manifest)
                return 2
            if args.target_additional_film_time and manifest["added_film_time_since_N33586_s"] >= args.target_additional_film_time:
                break
        if args.target_additional_film_time and manifest["added_film_time_since_N33586_s"] < args.target_additional_film_time:
            manifest["status"] = "REQUESTED_HORIZON_NOT_REACHED"
            dump(path, manifest)
            return 2
        # Prove the selected endpoint survives a paired reopen before handoff.
        solver.settings.file.read_case(file_name=manifest["latest_pair"]["case"])
        solver.settings.file.read_data(file_name=manifest["latest_pair"]["data"])
        reopened = readback(solver)
        if reopened != current:
            raise RuntimeError("Final saved/reopened fields or settings differ")
        dump(OUT / f"reopen-N{manifest['verified_native_end']}.json", reopened)
        subprocess.run([sys.executable, str(ROOT / "scripts/analysis/analyze_phase72a_adaptive_film.py")], check=True)
        manifest["final_reopen"] = "PASS_FIELDS_AND_SETTINGS"
        durable = PureWindowsPath(r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\ContactAbsorber\adaptive-20261005") / f"N{manifest['verified_native_end']}"
        ensure_remote_directory(solver, str(durable))
        final_copy = {}
        for kind in ("case", "data"):
            source = manifest["latest_pair"][kind]
            destination = str(durable / PureWindowsPath(source).name)
            ps = f"if (Test-Path -LiteralPath '{destination}') {{ throw 'Destination exists' }}; Copy-Item -LiteralPath '{source}' -Destination '{destination}'"
            command = "cmd /c powershell -NoProfile -EncodedCommand " + base64.b64encode(ps.encode("utf-16le")).decode()
            if solver.scheme.eval(f'(system "{quote_scheme_string(command)}")') != 0:
                raise RuntimeError("Final OneDrive copy failed")
            observed = remote_file_sha256(solver, destination, str(WORK / "scratch" / f"durable-N{manifest['verified_native_end']}-{kind}.sha"))
            if observed != manifest["latest_pair"][kind + "_sha256"]:
                raise RuntimeError("Final durable-copy hash mismatch")
            final_copy[kind] = destination
            final_copy[kind + "_sha256"] = observed
        manifest["shared_final_transfer"] = {
            **final_copy, "status": "SERVER1_ONEDRIVE_COPY_HASH_VERIFIED",
            "cloud_sync_completion": "UNVERIFIED",
            "library_archive": r"C:\Users\syok443\OneDrive - The University of Auckland\P4P-Fluent-Artifacts\Phase72A\ContactAbsorber\local20000\20261004T081120Z\contact-libraries.zip",
        }
        manifest["status"] = "REQUESTED_BATCHES_COMPLETE"
        dump(path, manifest)
        return 0
    except Exception:
        manifest.update(status="EXECUTION_UNCERTAIN", error=traceback.format_exc())
        dump(path, manifest)
        raise


if __name__ == "__main__":
    raise SystemExit(main())

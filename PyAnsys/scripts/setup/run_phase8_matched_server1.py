#!/usr/bin/env python3
"""Execute the authorized matched Phase 8 batch on existing Server 1 only.

No Fluent launch, local Student session, reinitialization of bulk fields, or
automatic numerical recovery variants. Inputs and final pairs use the shared
artifact folder; checkpoints and monitor files stay on Server 1 local disk.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup")]

from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists, safe_get_state
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import (
    configure_autosave, configure_residual_history, ensure_remote_directory,
    exclusive_writer_lock, remote_file_sha256, remote_text_read,
)
from build_phase8_dpm_reference import inspect as inspect_dpm
from build_phase8_f4_provisional_ewf import E27_CONTROLS, inspect as inspect_ewf
from build_09cV2_student_velocity_adaptation import FILM_MATERIAL
from run_phase8_f3_pilot import reset_phase8_reports, add_dpm_mass_source_report
from run_phase8_f4_provisional_pilot import configure_film_reports
from run_phase8_parity_carrier import (
    ITERATION_ROW, FAILURE_MARKER, dump, require, configure_reports, check_reports,
)


def load(solver, pair):
    solver.settings.file.read_case(file_name=pair["case"])
    solver.settings.file.read_data(file_name=pair["data"])


def save(solver, directory, name):
    ensure_remote_directory(solver, str(directory))
    pair = {k: str(directory / f"{name}.{suffix}.h5")
            for k, suffix in [("case", "cas"), ("data", "dat")]}
    for path in pair.values():
        require(not remote_file_exists(solver, path), f"Refusing overwrite: {path}")
    solver.settings.file.write_case(file_name=pair["case"])
    solver.settings.file.write_data(file_name=pair["data"])
    for key in ("case", "data"):
        pair[key + "_sha256"] = remote_file_sha256(
            solver, pair[key], str(directory / f"{name}-{key}.sha256.txt"))
    return pair


def audit(solver, point):
    dpm = inspect_dpm(solver, fraction=point["fraction"], allocated=True,
                      speed=point["speed_m_s"])
    require(dpm["interaction"] == {
        "enabled": True, "iteration_interval": 100,
        "update_sources_every_iteration": False}, "DPM source cadence drift")
    require(dpm["tracking"]["max_num_steps"] == 50000, "DPM tracking cap drift")
    require(solver.rp_vars("dpm/average/nodes?") is False, "DPM averaging drift")
    require(abs(float(solver.rp_vars("dpm/relax")) - 0.5) < 1e-9,
            "DPM source relaxation drift")
    require(dpm["methods"]["p_v_coupling"]["flow_scheme"] == "Coupled",
            "Unexpected carrier solver")
    fluids = solver.settings.setup.cell_zone_conditions.fluid.get_state()
    require(all(not phase.get("sources", {}).get("enable", False)
                for zone in fluids.values() for phase in zone.get("phase", {}).values()),
            "Active cell source/absorber in Phase 8")
    return {"dpm": dpm, "film": inspect_ewf(solver) if point["family"] == "F4" else None,
            "node_based_averaging": False, "source_relaxation": 0.5,
            "controls": safe_get_state(solver.settings.solution.controls, "controls")}


def enable_film(solver):
    # The same verified 2025 R2 EWF setup-only fallback as the existing F4.
    # Calculation below remains a coarse Settings/PyFluent solve.
    methods = solver.settings.solution.methods.get_state()
    solver.tui.define.models.eulerian_wallfilm.enable_wallfilm_model("yes")
    solver.execute_tui('/define/models/eulerian-wallfilm/film-material yes '
                       f'"{FILM_MATERIAL}"\n')
    params = solver.rp_vars("wall-film/model-parameters")
    require(set(E27_CONTROLS) <= set(dict(params)), "EWF controls unavailable")
    solver.rp_vars("wall-film/model-parameters",
                   [(k, E27_CONTROLS.get(str(k), v)) for k, v in params])
    solver.tui.define.models.eulerian_wallfilm.solve_wallfilm_equation("yes")
    film = solver.settings.setup.boundary_conditions.wall["wall"].phase["mixture"].wall_film
    film.eulerian_film_wall = True
    film.film_condition_type = "film-wall-boundary"
    film.enable_flow_momentum_coupling = False
    film.enable_dpm_wall_splash = True
    solver.tui.define.models.eulerian_wallfilm.initialize_wallfilm_model()
    require(solver.settings.solution.methods.get_state() == methods,
            "Enabling EWF changed carrier methods")
    return inspect_ewf(solver)


def verify_source(solver, pair, scratch):
    for key in ("case", "data"):
        # OneDrive may need time to deliver the explicitly staged starting pair.
        deadline = time.monotonic() + 900
        while not remote_file_exists(solver, pair[key]):
            require(time.monotonic() < deadline, f"Source did not sync: {pair[key]}")
            time.sleep(10)
        actual = remote_file_sha256(solver, pair[key], str(scratch / f"source-{key}.sha256.txt"))
        require(actual == pair[key + "_sha256"], f"Source bytes differ: {pair[key]}")


def run_point(solver, spec, point, batch):
    local = Path(spec["local_output"]) / point["id"]
    local.mkdir(parents=True, exist_ok=False)
    work = Path(spec["remote_work"]) / point["id"]
    final = Path(spec["remote_final"]) / point["id"]
    monitors = work / "monitors"
    for directory in (work, monitors, final):
        ensure_remote_directory(solver, str(directory))
    receipt = {**point, "status": "PREFLIGHT", "server_id": "1",
               "remote_work": str(work), "remote_final": str(final),
               "checkpoints": [], "started_at": datetime.now(timezone.utc).isoformat()}
    receipt_path = local / "manifest.json"
    dump(receipt_path, receipt)
    verify_source(solver, point["source"], work)
    load(solver, point["source"])
    receipt["fluent_version"] = str(solver.get_fluent_version())
    require("2025 R2" in receipt["fluent_version"], "Unexpected Fluent release")
    if point.get("enable_ewf"):
        receipt["film_build"] = enable_film(solver)
    receipt["configured"] = audit(solver, point)
    reset_phase8_reports(solver)
    definitions, paths = configure_reports(solver, monitors, create_local_directory=False)
    receipt["dpm_source_reports"] = add_dpm_mass_source_report(solver, monitors, definitions, paths)
    if point["family"] == "F4":
        receipt["film_reports"] = configure_film_reports(solver, monitors, definitions, paths)
    receipt["report_definitions"], receipt["report_paths"] = definitions, paths
    receipt["autosave"] = configure_autosave(solver, str(work), data_frequency=1000)
    receipt["residual_configuration"] = configure_residual_history(solver, 6500)
    solver.settings.mesh.check()
    receipt["start_pair"] = save(solver, work, "start")
    load(solver, receipt["start_pair"])
    receipt["start_reopen"] = audit(solver, point)
    require(receipt["configured"] == receipt["start_reopen"], "Start reopen changed setup")
    check_reports(solver, definitions, paths)
    solver.settings.solution.report_definitions.compute(report_defs=list(definitions))
    receipt["status"] = "RUNNING"
    dump(receipt_path, receipt)
    with SessionTranscriptCapture(solver, stream_path=local / "transcript.txt") as capture:
        for offset in range(1000, point["additional_iterations"] + 1, 1000):
            print(f'{point["id"]}: starting block ending at N{point["start_iteration"] + offset}', flush=True)
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            text = capture.text_since(marker)
            rows = sorted(set(map(int, ITERATION_ROW.findall(text))))
            expected = point["start_iteration"] + offset
            require(rows and rows[-1] == expected and
                    set(range(expected - 999, expected + 1)) <= set(rows),
                    f"Native horizon not proven: expected N{expected}, observed {rows[-3:]}")
            require(not FAILURE_MARKER.search(text), "Fatal solver event; preserve latest valid checkpoint")
            checkpoint = save(solver, work, f"N{expected}")
            receipt["checkpoints"].append({"native_iteration": expected, **checkpoint})
            receipt["last_verified_native_iteration"] = expected
            dump(receipt_path, receipt)
    receipt["final_pair"] = save(solver, final, "final")
    load(solver, receipt["final_pair"])
    receipt["final_reopen"] = audit(solver, point)
    require(receipt["start_reopen"] == receipt["final_reopen"], "Final setup drift")
    check_reports(solver, definitions, paths)
    for name, path in paths.items():
        text = remote_text_read(solver, path)
        require(text.strip(), f"Missing report history: {name}")
        (local / "monitors").mkdir(exist_ok=True)
        (local / "monitors" / f"{name}.out").write_text(text, encoding="utf-8")
    receipt.update(status="COMPLETE", completed_at=datetime.now(timezone.utc).isoformat(),
                   achieved_additional_iterations=point["additional_iterations"])
    dump(receipt_path, receipt)
    batch["completed"].append(point["id"])
    print(f'{point["id"]}: COMPLETE at N16000; final pair saved and reopened', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text())
    require(spec["server_id"] == "1", "This batch is authorized on Server 1 only")
    output = Path(spec["local_output"])
    output.mkdir(parents=True, exist_ok=True)
    batch_path = output / "batch-manifest.json"
    require(not batch_path.exists(), "Reconcile existing batch before restarting")
    batch = {"status": "PREFLIGHT", "server_id": "1", "spec": str(args.spec.resolve()),
             "completed": [], "requested_points": len(spec["points"])}
    dump(batch_path, batch)
    with exclusive_writer_lock(output / "server1-writer.lock"):
        solver = connect("1", start_transcript=True, tcp_timeout_seconds=5)
        try:
            # Preserve the previous loaded endpoint before the Phase 8 allocation.
            prior = Path(spec["remote_final"]) / "preserved-server1-session"
            batch["preserved_server1_pair"] = save(solver, prior, "previous")
            batch["status"] = "RUNNING"
            dump(batch_path, batch)
            for point in spec["points"]:
                batch["active_point"] = point["id"]
                dump(batch_path, batch)
                run_point(solver, spec, point, batch)
                dump(batch_path, batch)
            batch.update(status="COMPLETE", active_point=None)
        except Exception as exc:
            batch.update(status="BLOCKED", error=repr(exc))
            active = batch.get("active_point")
            receipt_path = output / str(active) / "manifest.json"
            if active and receipt_path.exists():
                receipt = json.loads(receipt_path.read_text())
                receipt.update(status="BLOCKED", error=repr(exc))
                dump(receipt_path, receipt)
            raise
        finally:
            dump(batch_path, batch)
            # Attached Server 1 stays alive, including after a failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

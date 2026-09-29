#!/usr/bin/env python3
"""Continue a verified F3 pilot, correcting the native DPM source report."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "scripts" / "setup"),
                str(ROOT / "scripts" / "inspection")]

from ansys.fluent.core import launch_fluent
from build_09cV2_student_velocity_adaptation import set_leaf_readback
from pyansys_fluent.common import safe_get_state
from pyansys_fluent.dpm_transcript import SessionTranscriptCapture
from pyansys_fluent.stage4_native import configure_autosave, configure_residual_history
from build_phase8_dpm_reference import inspect as audit_dpm
from run_dpm_particle_tracks import run_dpm_particle_track_check
from run_phase8_f3_pilot import add_dpm_mass_source_report
from run_phase8_parity_carrier import (
    FAILURE_MARKER, ITERATION_ROW, RUN_ROOT, FINAL_ROOT, check_reports,
    dump, load_pair, require, save_pair, sha256,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_manifest", type=Path)
    parser.add_argument("--target-native", type=int, default=15000)
    parser.add_argument("--source-every-iteration", action="store_true",
                        help="Enable held DPM source updates each flow iteration while retaining particle retracking interval")
    parser.add_argument("--dpm-source-urf", type=float,
                        help="Set the Discrete Phase Sources under-relaxation factor")
    args = parser.parse_args()
    require(args.dpm_source_urf is None or 0 < args.dpm_source_urf <= 1,
            "DPM source under-relaxation factor must be within (0, 1]")
    source = json.loads(args.source_manifest.read_text(encoding="utf-8"))
    require(source["status"] == "COMPLETE" and source["family"] == "F3",
            "F3 source must be complete")
    start = int(source["checkpoints"][-1]["native_iteration"])
    require(args.target_native > start and (args.target_native - start) % 1000 == 0,
            "Extend by whole 1000-iteration blocks")
    source_case = Path(source["checkpoints"][-1]["case"])
    source_data = Path(source["checkpoints"][-1]["data"])
    require(source_case.is_file() and source_data.is_file(), "F3 final pair missing")
    for kind, path in (("case", source_case), ("data", source_data)):
        require(sha256(path) == source["checkpoints"][-1][f"{kind}_sha256"],
                f"F3 source {kind} hash changed")
    interval = int(source["source_interval"])
    prior_interaction = source.get("final_reopen_readback", source.get("source_readback", {})).get("interaction", {})
    source_suffix = ("-source-every-iteration" if
                     args.source_every_iteration or prior_interaction.get("update_sources_every_iteration") else "")
    urf_suffix = (f"-dpmurf{str(args.dpm_source_urf).replace('.', 'p')}"
                  if args.dpm_source_urf is not None else "")
    label = (f"F3-26p81-5pct-coupled-upd{interval}{source_suffix}{urf_suffix}-extension-to{args.target_native}-"
             f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}")
    local, final = RUN_ROOT / label, FINAL_ROOT / label
    manifest = ROOT / "output" / "phase8-carrier" / label / "manifest.json"
    require(not local.exists() and not final.exists() and not manifest.exists(),
            "F3 continuation collision")
    local.mkdir(parents=True)
    final.mkdir(parents=True)
    receipt = {"status": "RUNNING", "family": "F3", "variant": "allocated-two-way-dpm",
               "source_interval": interval, "source_manifest": str(args.source_manifest),
               "numerical_delta": {
                   "enable_source_updates_every_flow_iteration": args.source_every_iteration,
                   "set_dpm_source_urf": args.dpm_source_urf,
                   "particle_retracking_interval": interval,
               },
               "source_receipt": source["source_receipt"],
               "source_case": str(source_case), "source_data": str(source_data),
               "source_case_sha256": sha256(source_case), "source_data_sha256": sha256(source_data),
               "start_native_iteration": start, "target_native_iteration": args.target_native,
               "paths": {"local": str(local), "final": str(final),
                         "transcript": str(local / "transcript.txt")},
               "checkpoints": [], "claim_limit": "Inert DPM fates and storage require separate accounting."}
    dump(manifest, receipt)
    solver = launch_fluent(product_version="25.2", dimension=3, precision="double",
                           processor_count=4, ui_mode="gui", start_timeout=240,
                           cleanup_on_exit=True, start_transcript=True)
    capture = None
    try:
        load_pair(solver, Path(str(source_case).removesuffix(".cas.h5")))
        receipt["source_readback"] = audit_dpm(solver, fraction=0.05, allocated=True)
        interaction = receipt["source_readback"]["interaction"]
        require(interaction["iteration_interval"] == interval,
                "F3 particle retracking interval mismatch")
        before_source_every_iteration = bool(interaction["update_sources_every_iteration"])
        if args.source_every_iteration:
            require(interval > 1 and not before_source_every_iteration,
                    "Source-update recovery requires a prior interval branch with held sources")
            set_leaf_readback(
                solver.settings.setup.models.discrete_phase.general_settings.interaction.update_sources_every_iteration,
                True, "DPM sources updated every flow iteration")
        receipt["configured_source_readback"] = audit_dpm(solver, fraction=0.05, allocated=True)
        require(receipt["configured_source_readback"]["interaction"]["iteration_interval"] == interval
                and receipt["configured_source_readback"]["interaction"]["update_sources_every_iteration"]
                is (before_source_every_iteration or args.source_every_iteration),
                "Configured F3 DPM source controls mismatch")
        relaxation = (solver.settings.solution.controls.pseudo_time_explicit_relaxation_factor
                      .global_dt_pseudo_relax)
        receipt["source_urf_before"] = safe_get_state(relaxation, "F3 pseudo-time explicit relaxation")
        keys = [key for key in receipt["source_urf_before"]
                if "dpm" in key.lower() or "discrete" in key.lower()]
        require(len(keys) == 1, f"Expected one DPM source URF control, got {keys}")
        receipt["source_urf_key"] = keys[0]
        if args.dpm_source_urf is not None:
            require(receipt["configured_source_readback"]["interaction"]["update_sources_every_iteration"],
                    "Lower DPM source URF requires per-flow-iteration source updates to apply the full source")
            relaxation.set_state({keys[0]: args.dpm_source_urf})
        receipt["source_urf_after"] = safe_get_state(relaxation, "configured F3 pseudo-time explicit relaxation")
        expected_urf = (args.dpm_source_urf if args.dpm_source_urf is not None
                        else float(receipt["source_urf_before"][keys[0]]))
        require(abs(float(receipt["source_urf_after"][keys[0]]) - expected_urf) < 1e-9,
                "Configured F3 DPM source URF mismatch")
        require(all(receipt["source_urf_after"][key] == value for key, value in
                    receipt["source_urf_before"].items() if key != keys[0]),
                "Unrelated F3 under-relaxation factors changed")
        receipt["autosave_configuration"] = configure_autosave(
            solver, str(local), data_frequency=1000)
        receipt["residual_configuration"] = configure_residual_history(
            solver, args.target_native + 200)
        definitions = dict(source["report_definitions"])
        bad = "p8-dpm-mass-source-total"
        require(bad in definitions and definitions[bad]["kind"] in
                ("volume-integral", "volume-sum"), "DPM source report missing")
        if definitions[bad]["kind"] == "volume-integral":
            solver.settings.solution.monitor.report_files.delete(name_list=[f"{bad}-rfile"])
            solver.settings.solution.report_definitions.volume.delete(name_list=[bad])
            definitions.pop(bad)
        monitor_root = local / "monitors"
        monitor_root.mkdir(parents=True)
        paths = {}
        for name in definitions:
            report = solver.settings.solution.monitor.report_files[f"{name}-rfile"]
            report.active = False
            path = monitor_root / f"{name}.out"
            require(not path.exists(), f"Report path exists: {path}")
            report.file_name = str(path)
            report.active = True
            paths[name] = str(path)
        receipt["corrected_dpm_source_report"] = add_dpm_mass_source_report(
            solver, monitor_root, definitions, paths)
        require(receipt["corrected_dpm_source_report"]["status"] == "INSTALLED",
                "F3 correction did not install a native source sum")
        receipt["report_definitions"] = definitions
        receipt["report_paths"] = paths
        check_reports(solver, definitions, paths)
        solver.settings.mesh.check()
        capture = SessionTranscriptCapture(solver, stream_path=local / "transcript.txt").start()
        receipt["start_pair"] = save_pair(solver, local / f"active{start}")
        load_pair(solver, local / f"active{start}")
        receipt["start_reopen_readback"] = audit_dpm(solver, fraction=0.05, allocated=True)
        require(receipt["start_reopen_readback"]["interaction"] ==
                receipt["configured_source_readback"]["interaction"],
                "F3 DPM interaction settings changed after start-pair reopen")
        receipt["start_reopen_source_urf"] = safe_get_state(
            solver.settings.solution.controls.pseudo_time_explicit_relaxation_factor.global_dt_pseudo_relax,
            "reopened F3 pseudo-time explicit relaxation")
        require(receipt["start_reopen_source_urf"] == receipt["source_urf_after"],
                "F3 source URF changed after start-pair reopen")
        check_reports(solver, definitions, paths)
        receipt["initial_report_compute"] = solver.settings.solution.report_definitions.compute(
            report_defs=list(definitions))
        require(len(receipt["initial_report_compute"]) == len(definitions),
                "F3 continuation initial report computation incomplete")
        dump(manifest, receipt)
        for endpoint in range(start + 1000, args.target_native + 1, 1000):
            marker = capture.mark()
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            capture.wait_until_quiet(quiet_seconds=0.5, timeout_seconds=10)
            block = capture.text_since(marker)
            rows = [int(value) for value in ITERATION_ROW.findall(block)]
            require(rows and rows[-1] == endpoint and
                    set(range(endpoint - 999, endpoint + 1)).issubset(set(rows)),
                    f"F3 continuation missing N{endpoint} native rows")
            require(not FAILURE_MARKER.search(block), f"F3 fatal event before N{endpoint}")
            destination = final / "final" if endpoint == args.target_native else local / f"active{endpoint}"
            receipt["checkpoints"].append({"native_iteration": endpoint,
                                           **save_pair(solver, destination)})
            receipt["last_valid_native_iteration"] = endpoint
            dump(manifest, receipt)
        load_pair(solver, final / "final")
        receipt["final_reopen_readback"] = audit_dpm(solver, fraction=0.05, allocated=True)
        require(receipt["final_reopen_readback"]["interaction"] ==
                receipt["configured_source_readback"]["interaction"],
                "F3 DPM interaction settings changed after final-pair reopen")
        receipt["final_reopen_source_urf"] = safe_get_state(
            solver.settings.solution.controls.pseudo_time_explicit_relaxation_factor.global_dt_pseudo_relax,
            "final F3 pseudo-time explicit relaxation")
        require(receipt["final_reopen_source_urf"] == receipt["source_urf_after"],
                "F3 source URF changed after final-pair reopen")
        check_reports(solver, definitions, paths)
        try:
            receipt["particle_tracks"] = run_dpm_particle_track_check(
                solver, run_label=label, order="diameter-ascending", keep_going=True,
                zone_summaries=True)
            receipt["tracking_status"] = "COMPLETE" if all(
                item.get("status") == "ok" for item in receipt["particle_tracks"]["results"]
            ) else "PARTIAL"
        except Exception as exc:
            receipt["tracking_status"] = "BLOCKED"
            receipt["tracking_error"] = repr(exc)
        receipt["status"] = "COMPLETE"
    except Exception as exc:
        receipt["status"] = "BLOCKED"
        receipt["error"] = repr(exc)
        raise
    finally:
        dump(manifest, receipt)
        if capture is not None:
            capture.close()
        if receipt["status"] == "COMPLETE":
            solver.exit()
    print(json.dumps({"status": receipt["status"], "manifest": str(manifest)}, indent=2))


if __name__ == "__main__":
    main()

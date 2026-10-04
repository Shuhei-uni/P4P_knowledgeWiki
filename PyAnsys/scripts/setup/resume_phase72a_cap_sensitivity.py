"""Recover a preserved live cap-test endpoint without replaying completed work."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
import json
import sys
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_phase72a_stage2_e27_roughness import (
    CASES, SOURCE_HASHES, dump, require, connect, ensure_remote_directory,
    native_iteration, validate_e27, pair_save, SessionTranscriptCapture,
    parse_report_forms, read_remote_forms, safe_get_state, remote_file_exists,
)
from run_phase72a_family_r_native import OUTER_WALL_ZONES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-run', type=Path, required=True)
    parser.add_argument('--output-root', type=Path, required=True)
    parser.add_argument('--stamp', required=True)
    args = parser.parse_args()
    source_path = args.source_run / 'run-manifest.json'
    manifest = json.loads(source_path.read_text())
    case = manifest['case']
    out = args.output_root.resolve()
    out.mkdir(parents=True, exist_ok=False)
    receipt = out / 'run-manifest.json'
    work = PureWindowsPath(manifest['work_root']) / ('recovery-' + args.stamp)
    scratch = work / 'scratch'
    durable = PureWindowsPath(manifest['durable_root'])
    manifest.update(status='RECOVERY_PREFLIGHT', recovered_from_manifest=str(source_path),
                    recovery_started_utc=datetime.now(timezone.utc).isoformat(),
                    continuity_transcript_limit='Original laptop stream stops before N14586; no interpolation across the missing residual interval.')
    dump(receipt, manifest)
    capture = None
    try:
        solver = connect(manifest['server_id'], start_transcript=False, tcp_timeout_seconds=5)
        require(native_iteration(solver) == 14586, 'live endpoint changed; reconcile before replay')
        require(manifest['parent_hashes_observed'] == SOURCE_HASHES, 'original parent identity differs')
        manifest['recovery_live_e27_readback'] = validate_e27(solver, max_thickness=1.0)
        for wall in OUTER_WALL_ZONES:
            turbulence = solver.settings.setup.boundary_conditions.wall[wall].phase['mixture'].turbulence.get_state()
            require(abs(turbulence['roughness_height']['value'] - CASES[case]) < 1e-12, 'roughness drift')
            require(turbulence['roughness_const']['value'] == 0.5, 'roughness constant drift')
        for name in solver.settings.solution.monitor.report_files.get_object_names():
            state = safe_get_state(solver.settings.solution.monitor.report_files[name], name)
            definition = state['report_defs'][0]
            live_path = PureWindowsPath(state['file_name'])
            expected_path = PureWindowsPath(manifest['report_paths'][definition])
            matched = live_path == expected_path
            if not matched and not live_path.is_absolute():
                matched = expected_path.parts[-len(live_path.parts):] == live_path.parts
            require(matched and remote_file_exists(solver, str(expected_path)), 'report path differs or recorded file is absent')
            require(state['active'] and state['frequency'] == 1, 'report cadence differs')
        prior_history = parse_report_forms(read_remote_forms(solver, manifest['report_paths']['p72a-e2.7-ewf-thickness-max']))
        require(prior_history['points'] >= 1000 and prior_history['iterations'][-1] == 14586, 'recorded history does not match the live endpoint')
        for folder in (work, scratch):
            ensure_remote_directory(solver, str(folder))
        manifest['recovered_first_block_pair'] = pair_save(solver, work / 'recovered-N14586.cas.h5', scratch, scratch_tag='recovered')
        manifest['completed_blocks'] = [manifest['recovered_first_block_pair']]
        capture = SessionTranscriptCapture(solver, stream_path=out / 'transcript-stream.txt', echo=False).start()
        manifest['status'] = 'RUNNING_SETTINGS_API'
        dump(receipt, manifest)
        for block in (2, 3):
            solver.settings.solution.run_calculation.iterate(iter_count=1000)
            coordinate = native_iteration(solver)
            require(coordinate == 13586 + block * 1000, 'recovery block did not reach its horizon')
            manifest['completed_blocks'].append(pair_save(solver, work / f'block{block}-N{coordinate}.cas.h5', scratch, scratch_tag=f'block{block}'))
            dump(receipt, manifest)
        capture.wait_until_quiet(quiet_seconds=2, timeout_seconds=30)
        capture.close()
        capture = None
        manifest['terminal_native_iteration'] = native_iteration(solver)
        prefix = f'P72A-STAGE2-E27-{case}-cap1m-recovery-{args.stamp}'
        manifest['final_pair_local'] = pair_save(solver, work / f'{prefix}-final-N16586.cas.h5', scratch, scratch_tag='final-local')
        manifest['final_pair_durable'] = pair_save(solver, durable / f'{prefix}-final-N16586.cas.h5', scratch, scratch_tag='final-durable')
        solver.settings.file.read_case(file_name=manifest['final_pair_local']['case'])
        solver.settings.file.read_data(file_name=manifest['final_pair_local']['data'])
        manifest['final_reopen_native_iteration'] = native_iteration(solver)
        require(manifest['final_reopen_native_iteration'] in (16585, 16586), 'unexpected final reopen coordinate')
        manifest['final_reopen_e27_readback'] = validate_e27(solver, max_thickness=1.0)
        histories = {}
        for name, path in manifest['report_paths'].items():
            histories[name] = parse_report_forms(read_remote_forms(solver, path))
            histories[name].update(definition_name=name, remote_file=path)
            require(histories[name]['points'] >= 3000 and histories[name]['iterations'][-1] == 16586, 'incomplete history')
        dump(out / 'report-histories.json', histories)
        manifest.update(status='COMPLETE', solve_finished_utc=datetime.now(timezone.utc).isoformat())
        dump(receipt, manifest)
        return 0
    except Exception as exc:
        manifest.update(status='BLOCKED', error=str(exc), traceback=traceback.format_exc())
        dump(receipt, manifest)
        return 2
    finally:
        if capture is not None:
            capture.close()


if __name__ == '__main__':
    raise SystemExit(main())

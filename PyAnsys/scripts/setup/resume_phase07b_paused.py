"""Continue a verified paused Phase 7b endpoint without reload or initialization.

Requires a matching preservation receipt, inactive prior recorder, unchanged
live iteration/configuration, and complete prefix evidence. Native report and
transcript destinations remain open on the PC. New local evidence inherits the
old records verbatim; new checkpoints have unique names. No session shutdown.
"""
from prepare_phase07b_collector import *
import shutil
from pathlib import PureWindowsPath
from pyansys_fluent.phase07b_flux_monitor import FluxFaceZone, Phase07bFluxMonitor
sys.path.insert(0, str(BASE / 'scripts/inspection'))
from export_phase07b_sections import export_sections
sys.path.insert(0, str(BASE / 'scripts/analysis'))
from analyze_phase07b_screen import parse_history, parse_residuals, parse_flux, coverage


def audit(path, parser, end):
    data, result = parser(path)
    coverage(result, data, end)
    assert result['complete_to_expected_end'], result
    assert result['last_iteration'] == end, result
    return data, result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent-manifest', type=Path, required=True)
    ap.add_argument('--preservation-receipt', type=Path, required=True)
    a = ap.parse_args()
    old = json.loads(a.parent_manifest.read_text())
    receipt = json.loads(a.preservation_receipt.read_text())
    start = receipt['iteration']
    assert receipt['status'] == 'PRESERVED' and receipt['pair_exists']
    assert receipt['iteration_after_save'] == start and 0 < start < 5000
    prior_monitor = old['flux_monitor']
    assert not prior_monitor['registered'] and prior_monitor['error'] is None
    assert prior_monitor['last_completed_iteration'] == start
    assert prior_monitor['local_rows'] == prior_monitor['remote_write_completed_rows']
    assert prior_monitor['local_rows'] == start - prior_monitor['start_iteration']
    parent = a.parent_manifest.parent
    _, flux_audit = audit(parent / 'collector-flux.jsonl', parse_flux, start)
    _, residual_audit = audit(parent / 'solve.trn', parse_residuals, start)
    run = f"p7b-s{old['percent']:03d}-resume-" + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = BASE / 'output' / run
    out.mkdir()
    shutil.copytree(parent / 'initial-sections', out / 'initial-sections')
    shutil.copy2(parent / 'solve.trn', out / 'solve.trn')
    r = {k: old[k] for k in ['percent', 'definitions', 'source_slots', 'sections', 'parent_case']}
    r.update(run_id=run, status='VERIFYING_PAUSED_ENDPOINT', steps=[], pairs={},
             requested_iterations=5000, start_iteration=start,
             parent_manifest=str(a.parent_manifest.resolve()),
             preservation_receipt=str(a.preservation_receipt.resolve()),
             preserved_case=receipt['case'], report=old['report'],
             remote_transcript=old['remote_transcript'],
             resume_mode='continue verified live state; no reload or initialization',
             inherited_flux_monitor=prior_monitor,
             inherited_evidence={'flux': flux_audit, 'residuals': residual_audit,
                                 'initial_sections': str((parent / 'initial-sections').resolve())})
    def persist():
        (out / 'manifest.json').write_text(json.dumps(r, indent=2, default=str) + '\n')
    def timeout(*_):
        raise TimeoutError('RPC deadline; reconcile actual progress before retry')
    signal.signal(signal.SIGALRM, timeout)
    def step(name, fn, seconds=90):
        print(name, flush=True)
        item = {'name': name, 'state': 'STARTED'}
        r['steps'].append(item)
        persist()
        signal.alarm(seconds)
        try:
            value = fn()
            item.update(state='PASS', value=value)
            return value
        except Exception as exc:
            item.update(state='FAIL', error=str(exc))
            raise
        finally:
            signal.alarm(0)
            persist()
    s = m = None
    transcript_callback = None
    def n():
        return int(s.settings.setup.named_expressions['P7bGlobalIteration'].get_value())
    def save(tag):
        path = ROOT + '/case-data/' + run + '-' + tag + '.cas.h5'
        assert not any(remote_file_exists(s, path.replace('.cas.h5', ext)) for ext in ['.cas.h5', '.dat.h5'])
        step('save_' + tag, lambda: s.settings.file.write_case_data(file_name=path), 180)
        assert all(remote_file_exists(s, path.replace('.cas.h5', ext)) for ext in ['.cas.h5', '.dat.h5'])
        r['pairs'][tag] = path
        persist()
    def history(end):
        path = out / f'history-{end:05d}.out'
        path.write_text(read_text(s, r['report']))
        data, result = audit(path, parse_history, end)
        return data, result
    def append_transcript(chunk):
        with (out / 'solve.trn').open('a') as handle:
            handle.write(chunk)
    try:
        s = step('connect', lambda: connect(server_id=1, start_transcript=False, tcp_timeout_seconds=5), 30)
        s.transcript.start(file_name=str(out / 'solve-segment.trn'), write_to_stdout=False)
        transcript_callback = s.transcript.register_callback(append_transcript, keep_new_lines=True)
        def verify():
            assert n() == start
            assert s.settings.setup.general.solver.time() == 'steady'
            assert all(remote_file_exists(s, receipt['case'].replace('.cas.h5', ext)) for ext in ['.cas.h5', '.dat.h5'])
            for name, definition in r['definitions'].items():
                assert s.settings.setup.named_expressions[name].definition() == definition, name
            for zone, phases in r['source_slots'].items():
                for phase, sources in phases.items():
                    assert s.settings.setup.cell_zone_conditions.fluid[zone].phase[phase].sources.get_state() == sources, (zone, phase)
            assert not any(v['check_convergence'] for v in s.settings.solution.monitor.residual.equations.get_state().values())
            info = s.fields.solution_variable_info.get_zones_info()
            assert info['p7b-collector'].count == COUNTS[r['percent']]
            assert info[ZONE].count + info['p7b-collector'].count == 620431
            for face in prior_monitor['face_zones']:
                assert info[face['name']].count == face['expected_owned_count']
            rf = s.settings.solution.monitor.report_files['p7b-screen-history']
            assert rf.active() and rf.frequency() == 1 and rf.frequency_of() == 'iteration'
            # Fluent may persist this as a relative Windows path after save/reopen.
            live_path = rf.file_name()
            expected = PureWindowsPath(r['report'])
            actual_path = PureWindowsPath(live_path)
            assert actual_path == expected or actual_path == PureWindowsPath('reports') / expected.name
            assert read_text(s, live_path) == read_text(s, r['report'])
            r['live_report_file'] = rf.get_state()
            assert s.settings.solution.report_definitions.get_state() == old['report_definitions']
            r['reports'] = rf.report_defs()
            data, scalar_audit = history(start)
            expected_volume = data['p7bwatervolume'][-1]
            live_volume = s.settings.setup.named_expressions['P7bWaterVolume'].get_value()
            assert math.isclose(live_volume, expected_volume, rel_tol=1e-10, abs_tol=1e-12)
            last = json.loads((parent / 'collector-flux.jsonl').read_text().splitlines()[-1])
            assert json.loads(read_text(s, last['remote_path'])) == last
            assert n() == start
            return {'iteration': start, 'pair_exists': True, 'water_volume': live_volume,
                    'scalar_history': scalar_audit, 'remote_flux_last_row_matches': True}
        r['resume_verification'] = step('verify_exact_live_endpoint_and_evidence', verify, 180)
        faces = [FluxFaceZone(**item) for item in prior_monitor['face_zones']]
        m = Phase07bFluxMonitor(s, face_zones=faces, start_iteration=start,
                               local_jsonl=out / 'collector-flux.jsonl',
                               remote_directory=ROOT + '/reports',
                               prefix_source=parent / 'collector-flux.jsonl')
        m.register()
        r.update(status='RUNNING', actual_iteration=start, flux_monitor=m.manifest())
        persist()
        current = start
        # Short first continuation check, then the original 500-iteration grid.
        targets = sorted(set([min(start + 5, 5000)] + list(range((start // 500 + 1) * 500, 5001, 500))))
        for target in targets:
            step(f'iterate_{current}_to_{target}',
                 lambda current=current, target=target: s.settings.solution.run_calculation.iterate(iter_count=target-current),
                 max(600, (target-current)*20))
            actual = n()
            r['actual_iteration'] = actual
            assert actual == target, (actual, target)
            m.assert_complete(actual)
            r['flux_monitor'] = m.manifest()
            last = json.loads((out / 'collector-flux.jsonl').read_text().splitlines()[-1])
            assert json.loads(read_text(s, last['remote_path'])) == last
            r.setdefault('remote_flux_readbacks', []).append({'iteration': actual, 'path': last['remote_path'], 'matches_local': True})
            _, scalar_audit = history(actual)
            _, flux_audit = audit(out / 'collector-flux.jsonl', parse_flux, actual)
            _, residual_audit = audit(out / 'solve.trn', parse_residuals, actual)
            r['recording_audit'] = {'iteration': actual, 'scalar': scalar_audit, 'flux': flux_audit, 'residuals': residual_audit}
            transcript = (out / 'solve.trn').read_text()
            assert not any(marker in transcript for marker in ['SEGMENTATION VIOLATION', 'floating point exception', 'Divergence detected'])
            r['latest_metrics'] = step(f'metrics_{actual}', lambda: s.settings.solution.report_definitions.compute(report_defs=r['reports']))
            save('final' if actual == 5000 else f'n{actual:05d}')
            current = actual
            r['segment_iterations'] = current - start
            persist()
        m.unregister()
        r['flux_monitor'] = m.manifest()
        m = None
        r['final_sections'] = step('extract_final_sections', lambda: export_sections(s, r['sections'], out / 'final-sections'), 180)
        step('close_native_transcript', lambda: s.settings.file.stop_transcript())
        r.update(status='HORIZON_COMPLETE_ANALYSIS_PENDING', completed_iterations=current)
        persist()
    except Exception as exc:
        signal.alarm(0)
        r.update(status='BLOCKED_EXECUTION', error=str(exc))
        (out / 'error.txt').write_text(traceback.format_exc())
        raise
    finally:
        signal.alarm(0)
        if m is not None:
            try:
                m.unregister()
            except Exception as exc:
                r['callback_cleanup_error'] = str(exc)
            r['flux_monitor'] = m.manifest()
        if s is not None:
            try:
                if transcript_callback is not None:
                    s.transcript.unregister_callback(transcript_callback)
                s.transcript.stop()
            except Exception as exc:
                r['transcript_cleanup_error'] = str(exc)
        persist()
        print('EVIDENCE', out, flush=True)


if __name__ == '__main__':
    main()

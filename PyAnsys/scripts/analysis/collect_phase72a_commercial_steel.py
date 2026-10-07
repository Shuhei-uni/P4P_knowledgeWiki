"""Read-only extraction of the completed N29815 commercial-steel run."""
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'setup'))
import run_phase72a_commercial_steel_continuation as run
from pyansys_fluent.remote_text import read_text
from pyansys_fluent.stage4_native import remote_file_sha256
from pyansys_fluent.common import remote_file_exists


def main():
    raw = run.OUT / 'raw' / 'N29815-20261007'
    if (raw / 'extraction.json').exists():
        print('Existing extraction retained; no source evidence overwritten')
        return
    raw.mkdir(parents=True, exist_ok=True)
    m = json.loads(run.MANIFEST.read_text())
    s = run.attach()
    assert run.native_iteration(s) == 29815
    assert s.settings.solution.run_calculation.iterate.is_active()
    film = run.film(s)
    assert film['max_timestep_count'] == 28235
    roughness = run.roughness(s)
    for name, values in roughness.items():
        assert values['roughness_height']['value'] == (0 if name == 'bottom' else 4.5e-5)
        assert values['roughness_const']['value'] == .5
    pair = dict(m['expected_final_pair'], native_iteration=29815)
    token = uuid.uuid4().hex[:8]
    for kind in ['case', 'data']:
        assert remote_file_exists(s, pair[kind])
        pair[kind + '_sha256'] = remote_file_sha256(s, pair[kind], str(run.WORK / 'scratch' / f'analysis-N29815-{token}-{kind}.sha256'))
    print('N29815_IDLE_PAIRED_FILES_HASH_VERIFIED', flush=True)
    record = {'native_iteration':29815,'film':film,'pair':pair,'roughness':roughness,
              'readback':run.state(s)['readback'], 'report_paths':m['report_paths'],
              'report_definitions':s.settings.solution.report_definitions.get_state(),
              'new_solve_calls':0,'reopen':'NOT_REQUIRED_FOR_READ_ONLY_EXTRACTION'}
    for name, path in m['report_paths'].items():
        target = raw / f'{name}.out'
        if not target.exists():
            target.write_text(read_text(s,path))
        print('EXTRACTED',name,flush=True)
    record['transcript_sources'] = {}
    for start,end in [(25815,25835),(25835,26815),(26815,29815)]:
        name = f'batch-N{start}-N{end}.trn' if end == 25835 else f'native-continuation-N{start}-N{end}.trn'
        target = raw / name
        if not target.exists():
            remote = str(run.WORK / name)
            if remote_file_exists(s, remote):
                target.write_text(read_text(s, remote))
            elif end == 25835:
                # The probe's complete client stream survives its native file gap.
                with target.open('x') as stream:
                    stream.write((run.OUT / 'batch-N25815-N25835.txt').read_text())
            else:
                raise FileNotFoundError(remote)
        record['transcript_sources'][name] = ('complete client stream; native probe file absent'
                                               if end == 25835 else 'native server transcript')
    with (raw / 'extraction.json').open('x') as stream:
        stream.write(json.dumps(record,indent=2)+'\n')
    m.update(status='COMPLETE_NATIVE_VERIFIED',active_target=None,verified_native_end=29815,
             last_observed_native_iteration=29815,completed_updates=4000,remaining_updates=0,
             latest_pair=pair,latest_saved_pair=pair,film_time_s=film['film_elapsed_time'],
             final_completion='NATIVE_TARGET_PAIRED_FILES_HASHES_AND_HISTORIES_EXTRACTED',
             live_idle=True,analysis='PENDING',extraction=str(raw / 'extraction.json'))
    run.dump(run.MANIFEST,m)
    print('EXTRACTION_COMPLETE',flush=True)


if __name__ == '__main__':
    main()

"""Submit one native journal for the human-requested 997k +2000 continuation."""
import argparse,fcntl,json,math,re,sys,time,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_phase9_mesh_startup as r
from pyansys_fluent.common import quote_scheme_string


def render_journal(folder, prefix=""):
    folder_name=lambda name:prefix+name
    path=lambda name:str(folder/folder_name(name)).replace('\\','/')
    return '\n'.join([
        '/file/start-transcript "'+path('native-extra2000.trn')+'"',
        '/solve/iterate 1000',
        '/file/write-case-data "'+path('checkpoint-after-first1000.cas.h5')+'"',
        '/solve/iterate 1000',
        '/file/write-case-data "'+path('endpoint-after-extra2000.cas.h5')+'"',
        '/file/stop-transcript',''])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output;manifest=out/'run-manifest.json';m=json.loads(manifest.read_text())
    lock=(r.OUT/'controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    s=r.attach();r.require_idle(s)
    if r.native_iteration(s)!=8080:raise RuntimeError('Expected verified 997k N8080 start')
    parent=json.loads((r.OUT/'997k-run.json').read_text());proof=json.loads(Path(parent['blocks'][-1]['checkpoint_proof']).read_text())
    before=r.base.state(s);r.require_match(before['readback'],proof['after']['readback'])
    r.require_setup_same(before['setup'],proof['after']['setup'])
    if before['methods']!=proof['after']['methods']:raise RuntimeError('Methods differ from prepared endpoint')
    r.require_bulk_audit(s);r.assert_bulk_active(s);r.read_feed(s,1.0)
    clock=r.film(s)
    if not math.isclose(clock['film_elapsed_time'],parent['final_film']['film_elapsed_time'],abs_tol=1e-12):raise RuntimeError('Start film clock changed')
    folder=r.WORK/'997k';prefix=m['run_id']+'-';r.ensure_remote_directory(s,str(folder))
    # Explicit native paired writes at +1000 and +2000 replace periodic autosaves.
    previous_autosave=s.settings.file.auto_save.get_state();s.settings.file.auto_save.data_frequency=0
    journal=render_journal(folder,prefix);remote=str(folder/(prefix+'extra2000.jou'))
    (out/'extra2000.jou').write_text(journal);r.write_ascii_text_new(s,remote,journal)
    s.transcript.start(file_name=m['live_transcript'],write_to_stdout=False)
    m.update(status='RUNNING',active_mesh='997k',active_stage='native-extra2000',verified_native_end=8080,
        latest_pair=parent['final_pair'],active_target=10080,start_pair=parent['final_pair'],start_state=before,
        film_start_s=clock['film_elapsed_time'],previous_autosave=previous_autosave,remote_journal=remote,
        native_transcript=str(folder/(prefix+'native-extra2000.trn')),midpoint_expected_native=9080,
        midpoint_pair={'case':str(folder/(prefix+'checkpoint-after-first1000.cas.h5')),'data':str(folder/(prefix+'checkpoint-after-first1000.dat.h5'))},
        endpoint_pair={'case':str(folder/(prefix+'endpoint-after-extra2000.cas.h5')),'data':str(folder/(prefix+'endpoint-after-extra2000.dat.h5'))})
    r.dump(manifest,m);print('NATIVE_JOURNAL_SUBMITTED 997k 8080 10080 CHECKPOINT 9080',flush=True)
    command='/file/read-journal "'+remote.replace('\\','/')+'"'
    try:
        # One command submission. Fluent performs both solves and both paired saves.
        s.scheme.eval('(ti-menu-load-string "'+quote_scheme_string(command)+'")')
        if r.native_iteration(s)!=10080:raise RuntimeError('Journal did not reach requested native endpoint; do not resubmit')
        r.assert_bulk_active(s);r.require_bulk_audit(s);r.read_feed(s,1.0)
        after=r.base.state(s);r.require_setup_same(after['setup'],before['setup'])
        if after['methods']!=before['methods']:raise RuntimeError('Methods changed during continuation')
        for pair in [m['midpoint_pair'],m['endpoint_pair']]:
            for key in ['case','data']:
                if not r.remote_file_exists(s,pair[key]):raise RuntimeError('Native checkpoint member missing')
                pair[key+'_sha256']=r.remote_file_sha256(s,pair[key],str(folder/f'{Path(pair[key]).name}-{key}.sha256.txt'))
        text=r.read_text(s,m['native_transcript']);(out/'native-extra2000.trn').write_text(text)
        from run_phase72a_adaptive_film import FILM
        rows=[tuple(map(float,x.groups())) for x in FILM.finditer(text)]
        if len(rows)!=2000 or any(not all(math.isfinite(v) for v in row) for row in rows):raise RuntimeError('Accepted film evidence incomplete')
        if re.search(r'floating point exception|fatal error|Divergence detected',text,re.I):raise RuntimeError('Numerical recovery required')
        if not math.isclose(rows[-1][0]-m['film_start_s'],2000e-7,abs_tol=1e-10):raise RuntimeError('Accepted film clock differs')
        m['midpoint_pair']['native_iteration']=9080;m['endpoint_pair']['native_iteration']=10080
        m.update(status='COMPLETE_NATIVE_CONTINUATION',verified_native_end=10080,active_target=None,
            latest_pair=m['endpoint_pair'],film_end_s=rows[-1][0],peak_film_courant=max(row[2] for row in rows),end_state=after)
        r.dump(manifest,m);print('NATIVE_CONTINUATION_COMPLETE 10080',flush=True)
    except BaseException:
        m.update(status='RECOVERY_REQUIRED',error=traceback.format_exc());r.dump(manifest,m);raise
    finally:
        receipt=json.loads((r.OUT/'desktop-controller.json').read_text());receipt.update(status=m['status']);r.dump(r.OUT/'desktop-controller.json',receipt)

if __name__=='__main__':main()

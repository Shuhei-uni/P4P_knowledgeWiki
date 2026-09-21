"""Human-requested three-iteration fault reproduction, with separate stage logs.

Preserve and restore the connected Phase 7b state. Never run collector sources.
This diagnostic does not clear a scientific lifecycle gate.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import ntpath
import signal
import sys
import traceback

BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE/'src'))
from dotenv import load_dotenv
load_dotenv(BASE/'.env')
from pyansys_fluent.connection import connect
from pyansys_fluent.common import remote_file_exists
from pyansys_fluent.remote_text import read_text

ZONE = 'simple-spiral-separator--brine-outlet-'
ROOT = 'C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal'

def flags(s):
    return {ph:s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable()
            for ph in ['mixture','phase-1','phase-2']}

def counts(s):
    return {'rpvars':s.rp_vars('sol/iterations'),
            'solver_via_cx_send':s.scheme.eval("(cx-send '(rpgetvar 'sol/iterations))")}

def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder=BASE/'output/phase07b_preparation'/('fault-retest-'+stamp)
    folder.mkdir(parents=True)
    r={'stamp':stamp,'authorization':'Human explicitly requested test the fault on 2026-09-12',
       'scientific_screen':False,'requested_iterations':3,'stage':'CONNECTING'}
    def persist():
        (folder/'result.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
    def stage(x):
        r['stage']=x; persist(); print(x,flush=True)
    def deadline(*args): raise TimeoutError('API operation exceeded diagnostic deadline')
    signal.signal(signal.SIGALRM,deadline)
    signal.alarm(30)
    s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5)
    signal.alarm(0)
    r['connection']={key:getattr(s.connection_properties,key,None)
                     for key in ['ip','port','cortex_pid','fluent_host_pid','cortex_host']}
    r['initial_counts']=counts(s)
    r['initial_sources']=flags(s)
    assert not any(r['initial_sources'].values())
    assert s.settings.setup.general.solver.time()=='steady'
    fixture=json.loads((BASE/'output/phase07b_preparation/diagnostic-source-persistence.json').read_text())
    assert all(remote_file_exists(s,fixture[k]) for k in ['case','data'])
    r['original_case']=ROOT+'/case-data/p7b-before-fault-retest-'+stamp+'.cas.h5'
    r['original_data']=r['original_case'].replace('.cas.h5','.dat.h5')
    stage('PRESERVING_ORIGINAL')
    signal.alarm(120)
    s.settings.file.write_case_data(file_name=r['original_case'])
    signal.alarm(0)
    assert all(remote_file_exists(s,r[k]) for k in ['original_case','original_data'])
    transcript_active=False
    try:
        r['setup_transcript']=ROOT+'/logs/p7b-fault-retest-setup-'+stamp+'.trn'
        stage('LOADING_DIAGNOSTIC_FIXTURE')
        s.settings.file.start_transcript(file_name=r['setup_transcript']); transcript_active=True
        signal.alarm(120)
        s.settings.file.read_case_data(file_name=fixture['case'])
        signal.alarm(0)
        for ph in ['mixture','phase-1','phase-2']:
            s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable=False
        assert not any(flags(s).values())
        defs=s.settings.solution.report_definitions.single_valued_expression
        name='p7b-diag-water-expression-native'
        if name not in defs.get_object_names(): defs.create(name=name)
        s.settings.solution.report_definitions.single_valued_expression[name].definition='P7bDiagWaterVolume'
        assert s.settings.solution.report_definitions.single_valued_expression[name].definition()=='P7bDiagWaterVolume'
        files=s.settings.solution.monitor.report_files
        if 'p7b-diag-history' not in files.get_object_names(): files.create(name='p7b-diag-history')
        rf=s.settings.solution.monitor.report_files['p7b-diag-history']
        r['report']=ROOT+'/reports/p7b-fault-retest-'+stamp+'.out'
        rf.file_name=r['report']; rf.report_defs=[name,'p7b-diag-native-water-volume']; rf.frequency=1; rf.active=True
        assert ntpath.normcase(ntpath.normpath(rf.file_name()))==ntpath.normcase(ntpath.normpath(r['report']))
        r['before_counts']=counts(s); r['before_sources']=flags(s)
        s.settings.file.stop_transcript(); transcript_active=False
        setup_text=read_text(s,r['setup_transcript']); (folder/'setup.trn').write_text(setup_text)
        r['setup_fatal_count']=setup_text.count('SEGMENTATION VIOLATION')
        if r['setup_fatal_count']: raise RuntimeError('Cortex fault reproduced during setup; no iterations issued')
        r['solve_transcript']=ROOT+'/logs/p7b-fault-retest-solve-'+stamp+'.trn'
        s.settings.file.start_transcript(file_name=r['solve_transcript']); transcript_active=True
        stage('RUNNING_THREE_SOURCE_FREE_ITERATIONS')
        signal.alarm(120)
        s.settings.solution.run_calculation.iterate(iter_count=3)
        signal.alarm(0)
        r['after_counts']=counts(s); r['after_sources']=flags(s)
        s.settings.file.stop_transcript(); transcript_active=False
        for key,filename in [('solve_transcript','solve.trn'),('report','reports.out')]:
            txt=read_text(s,r[key]); (folder/filename).write_text(txt)
            if key=='solve_transcript': r['solve_fatal_count']=txt.count('SEGMENTATION VIOLATION')
        r['status']='FAULT_REPRODUCED' if r['solve_fatal_count'] else 'NO_CORTEX_FAULT_REPRODUCED_PENDING_VALIDATION'
        stage('EVIDENCE_CAPTURED')
    except Exception as exc:
        signal.alarm(0)
        r['error']=str(exc); r['status']='DIAGNOSTIC_STOPPED'; (folder/'error.txt').write_text(traceback.format_exc()); persist()
    finally:
        signal.alarm(0)
        if transcript_active:
            try: s.settings.file.stop_transcript()
            except Exception as exc: r['transcript_stop_error']=str(exc)
        stage('RESTORING_ORIGINAL')
        signal.alarm(120)
        s.settings.file.read_case_data(file_name=r['original_case'])
        signal.alarm(0)
        r['restored_counts']=counts(s); r['restored_sources']=flags(s)
        r['restoration_pass']=r['restored_counts']==r['initial_counts'] and not any(r['restored_sources'].values())
        stage('FINISHED')
    print(json.dumps(r,indent=2,default=str),flush=True)
    print('EVIDENCE',folder,flush=True)

if __name__=='__main__': main()

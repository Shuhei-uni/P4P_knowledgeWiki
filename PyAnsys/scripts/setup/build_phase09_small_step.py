"""Create the single predeclared smaller-pseudo-time child from the fresh N0 pair."""
from build_phase09_pool import *
from run_phase09_pool import scalar_metrics
import fcntl,time

parent=BASE/'output/phase09/h0p1-20260929T062514Z/manifest.json'
previous=parent.parent/'h0p1-20260929T062514Z-flow-n00050-20260929T070536Z/run.json'
m=json.loads(parent.read_text());last=json.loads(previous.read_text())
assert last['status']=='BLOCK_COMPLETE' and last['pair_exists']
lock=(BASE/'output/phase09-preflight/server1.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
tag='h0p1-scale01-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out=BASE/'output/phase09'/tag;out.mkdir()
r={'status':'BUILDING','tag':tag,'height':.1,'initial_native_iteration':0,'case':ROOT+'/case-data/'+tag+'-n00000.cas.h5','reports':m['reports'],'definitions':m['definitions'],'initialization':m['initialization'],'parent_manifest':str(parent),'parent_initial_case':m['case'],'preserved_previous_endpoint':last['case'],'controlled_delta':{'automatic_pseudo_time_scale':{'before':.3,'after':.1}},'iterations_issued':0}
def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
persist();signal.alarm(600)
try:
 s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating()
 assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==1050
 assert all(remote_file_exists(s,last['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
 s.settings.file.read_case_data(file_name=m['case']);assert_contract(s)
 assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
 r['fresh_before']=snapshot(s)
 scale=s.settings.solution.run_calculation.pseudo_time_settings.time_step_method.time_step_size_scale_factor
 assert scale()==.3
 scale.set_state(.1);assert scale()==.1
 s.settings.solution.run_calculation.pseudo_time_settings.verbosity=1
 r['instrumentation_delta']='pseudo-time verbosity 0 to 1; logs actual automatic step'
 r['before']=snapshot(s)
 baseline=copy.deepcopy(r['fresh_before']);changed=copy.deepcopy(r['before'])
 baseline['pseudo_time']['time_step_method']['time_step_size_scale_factor']=.1
 baseline['pseudo_time']['verbosity']=1
 assert baseline==changed,'Unexpected setup delta'
 s.settings.file.write_case_data(file_name=r['case'])
 assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
 s.settings.file.read_case_data(file_name=r['case']);assert_contract(s)
 r['after']=snapshot(s);assert r['before']==r['after'],'Save/reopen changed setup'
 assert s.settings.solution.run_calculation.pseudo_time_settings.time_step_method.time_step_size_scale_factor()==.1
 assert int(s.settings.setup.named_expressions['P9Iteration'].get_value())==0
 f=np.load(parent.parent/'initial-fields.npz');sv=s.fields.solution_variable_data
 for var,domain,key in [('SV_P','mixture','pressure'),('SV_VOF','phase-2','alpha')]:
  data=np.asarray(sv.get_data(variable_name=var,zone_names=[ZONE],domain_name=domain)[ZONE]);assert np.array_equal(data,f[key]),var
 for v in ['SV_U','SV_V','SV_W']:assert np.max(np.abs(sv.get_data(variable_name=v,zone_names=[ZONE],domain_name='mixture')[ZONE]))==0
 r['initial_metrics']=scalar_metrics(s,r['reports']);assert abs(r['initial_metrics']['p9liquidmass']-4096.7698038261215)<1e-6
 r['status']='READY_FOR_SMOKE';persist()
 (BASE/'output/phase09-preflight/small-step-build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}))
 print('READY_FOR_SMOKE',out/'manifest.json',flush=True)
except Exception as e:r['error']=repr(e);persist();raise
finally:signal.alarm(0)

"""Finish the zero-solve child after resolving documented linked control readbacks."""
from build_low_order_rhie import *
out=BASE/'output/pressure-gravity-initialization/low-order-rhie-20261002T135759Z';r=json.loads((out/'manifest.json').read_text());assert r['status']=='BUILD_REPAIR_REQUIRED' and r['iterations_issued']==0
lock=(BASE/'output/phase09-preflight/server1.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
signal.alarm(600)
def persist():(out/'manifest.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
try:
 s=connect(1,start_transcript=False,tcp_timeout_seconds=5);assert not s.settings.solution.run_calculation.iterating();assert_contract(s)
 assert all(remote_file_exists(s,r['preserved_endpoint'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
 current=snapshot(s);assert current==r['before'],'Live child changed after failed invariant check'
 parent_path=Path(r['configuration_parent_manifest']);parent=json.loads(parent_path.read_text());expected=copy.deepcopy(parent['after']);m=expected['methods'];m['multiphase_numerics']['advanced_stability_controls']['p_v_coupling']['rhie_chow_flux']['low_order_rhie_chow']=True;m['expert']['disable_rhie_chow_flux']=True;m['vof_numerics']['high_order_rc']=True;m['vof_numerics'].pop('high_order_rc_hybrid_treatment',None)
 for k in ['solver','operating','models','materials','boundaries','zones','methods','controls','expressions','residual_options','residual_equations','pseudo_time']:assert expected[k]==current[k],k
 a=np.load(out/'initial-fields.npz');sv=s.fields.solution_variable_data
 for var,key in [('SV_P','pressure'),('SV_VOF','alpha')]:
  domain='phase-2' if var=='SV_VOF' else 'mixture';arr=np.asarray(sv.get_data(variable_name=var,zone_names=[ZONE],domain_name=domain)[ZONE]);assert np.array_equal(arr,a[key])
 for var in ['SV_U','SV_V','SV_W']:assert np.max(abs(np.asarray(sv.get_data(variable_name=var,zone_names=[ZONE],domain_name='mixture')[ZONE])))==0
 r['repair']={'cause':'Single documented low-order setter updates three equivalent low-order controls and deactivates hybrid control','solves_issued':0,'precise_method_changes':['multiphase_numerics/advanced_stability_controls/p_v_coupling/rhie_chow_flux/low_order_rhie_chow false to true','expert/disable_rhie_chow_flux false to true','vof_numerics/high_order_rc false to true','vof_numerics/high_order_rc_hybrid_treatment inactive']}
 r['aux_before_write']=capture_aux(s,out/'aux-before-write.npz');persist()
 s.settings.file.write_case_data(file_name=r['case']);assert all(remote_file_exists(s,r['case'].replace('.cas.h5',e)) for e in ['.cas.h5','.dat.h5'])
 s.settings.file.read_case_data(file_name=r['case']);assert_contract(s);r['after']=snapshot(s);r['aux_after_reopen']=capture_aux(s,out/'aux-after-reopen.npz')
 for k in ['solver','operating','models','materials','boundaries','zones','methods','controls','expressions','residual_options','residual_equations','pseudo_time']:assert r['before'][k]==r['after'][k],k
 for var,key in [('SV_P','pressure'),('SV_VOF','alpha')]:
  domain='phase-2' if var=='SV_VOF' else 'mixture';assert np.array_equal(np.asarray(sv.get_data(variable_name=var,zone_names=[ZONE],domain_name=domain)[ZONE]),a[key])
 r['initial_native_iteration']=s.settings.setup.named_expressions['P9Iteration'].get_value();assert r['initial_native_iteration']==0
 metrics={k:float(v[0]) for row in s.settings.solution.report_definitions.compute(report_defs=r['reports']) for k,v in row.items()};r['initial_metrics']=metrics
 for ph in ['l','v','m']:
  for boundary in ['li','vi','bo','so','net']:assert abs(metrics['p9'+ph+boundary])<1e-12
 assert metrics['p9maxspeed']==0
 r['status']='READY_FOR_SMOKE';r.pop('error',None);persist();(BASE/'output/pressure-gravity-initialization/build-receipt.json').write_text(json.dumps({'manifest':str(out/'manifest.json')}));print(str(out/'manifest.json'),flush=True)
except Exception as e:r.update(status='BUILD_REPAIR_REQUIRED',error=repr(e));persist();raise
finally:signal.alarm(0)

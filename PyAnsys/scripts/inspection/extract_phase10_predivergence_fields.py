"""Read saved Phase 10 fields only; never iterate, initialise, or save a case.

Compare baseline OFF at N1000 (M01-M06) and N2000 (M02-M06).
Restore the verified BF01 ON N3005 pair even after an extraction error.
Raw arrays are native cell fields in Fluent's zone/partition order.
"""
from pathlib import Path
import argparse, hashlib, json, os, sys, time
import numpy as np
import ansys.fluent.core as pf
import ansys.fluent.core.fluent_connection as fc
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence'
DEST=OUT/'predivergence-mesh-sensitivity'
sys.path[:0]=[str(ROOT/'PyAnsys/scripts/setup'),str(ROOT/'PyAnsys/src')]
from deploy_phase10_bf01 import Bridge, psquote
from pyansys_fluent.remote_text import write_ascii_text_new, read_text

def inputs():
    levels=json.loads((OUT/'restart-native-manifests-60569-20261010.json').read_text())['levels']
    for level,date in [('M05','20261011'),('M06','20261012')]:
        levels[level]=json.loads((OUT/f'vpn-restored-{date}/{level}-manifest.json').read_text())
    jobs=[]
    for n in [1000,2000]:
        for level in ['M01','M02','M03','M04','M05','M06']:
            if n==2000 and level=='M01':continue
            m=levels[level];c=next(x for x in m['checkpoints'] if x['iteration']==n)
            assert c['requested_iteration']==n
            jobs.append(dict(level=level,iteration=n,pair=c['pair'],reports=c['reports'],
                             settings=m['settings_readback'],initial_reports=m['initial_reports']))
    # Every baseline checkpoint must carry identical scientific settings.
    assert all(j['settings']==jobs[0]['settings'] for j in jobs)
    return jobs

def hash_proof(cfg,jobs):
    """Only allowed after fresh idle/controller proof; read explicit source pairs."""
    import uuid
    b=Bridge(cfg);tag=uuid.uuid4().hex[:8]
    ps=cfg['work']+'/predivergence-hashes-'+tag+'.ps1';res=ps+'.json'
    code="$ErrorActionPreference='Stop'\n$rows=@()\n"
    for j in jobs:
        for kind in ['case','data']:
            pair=j['pair'];code+='$h=(Get-FileHash -LiteralPath '+psquote(pair[kind])+' -Algorithm SHA256).Hash.ToLower()\n'
            code+='if($h -ne '+psquote(pair[kind+'_sha256'].lower())+'){throw "Source checkpoint hash mismatch"}\n'
            code+='$rows+=@{level='+psquote(j['level'])+';iteration='+str(j['iteration'])+';kind='+psquote(kind)+';sha256=$h}\n'
    code+='$rows | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath '+psquote(res)+' -Encoding Ascii\n'
    try:
        write_ascii_text_new(b,ps,code);b.shell_file(ps);proof=json.loads(read_text(b,res))
        (DEST/('source-hashes-'+tag+'.json')).write_text(json.dumps(proof,indent=2)+'\n')
        return dict(native_receipt=res,verified_files=proof)
    finally:b.channel.close()

def attach(cfg):
    # Native host runs v0 services; local PyFluent 0.39 would otherwise probe v1.
    fc._server_supports_v1=lambda channel:False
    pf.config.check_health=False
    return pf.connect_to_fluent(ip=cfg['ip'],port=cfg['port'],password=os.environ['PHASE10_API_PASSWORD'],
       allow_remote_host=True,insecure_mode=True,cleanup_on_exit=False,start_watchdog=False,start_transcript=False)

def counter(s):return s.settings.solution.report_definitions.compute(report_defs=['p10-iteration'])[0]['p10-iteration'][0]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--smoke',action='store_true');a=ap.parse_args()
    DEST.mkdir(exist_ok=True);(DEST/'raw').mkdir(exist_ok=True)
    jobs=inputs();jobs=jobs[:1] if a.smoke else jobs
    cfg=json.loads((OUT/'run-config.json').read_text())
    restore=json.loads((OUT/'bodyforce-BF01-diagnosis/zero-update-OFF-reopen.json').read_text())['restore_pair']
    proof=json.loads((DEST/'preflight.json').read_text())
    assert proof['proof']['old_controller_absent'] and not proof['proof']['workers']
    result=dict(status='EXTRACTING',solves_issued=0,classification='UNCONVERGED_FIXED_ITERATION_MESH_SENSITIVITY',
       comparison_coordinates=[1000,2000],M07_excluded='USER_SKIPPED_N718',BF01_excluded='DIFFERENT_BODY_FORCE_SETTING',sources=[],restore_pair=restore)
    receipt=DEST/('smoke.json' if a.smoke else 'extraction.json')
    def persist():receipt.write_text(json.dumps(result,indent=2,default=str)+'\n')
    s=None;loaded=False
    try:
        s=attach(cfg);assert not s.settings.solution.run_calculation.iterating();assert counter(s)==3005
        result['source_hashes']=hash_proof(cfg,jobs);persist()
        for j in jobs:
            target=DEST/'raw'/f"{j['level']}-N{j['iteration']}-native.npz"
            metadata=target.with_suffix('.json')
            if target.exists():
                old=json.loads(metadata.read_text());assert old['pair']==j['pair'];result['sources'].append(old);continue
            start=time.monotonic();s.settings.file.read_case(file_name=j['pair']['case']);loaded=True
            s.settings.file.read_data(file_name=j['pair']['data'])
            assert counter(s)==j['iteration'];assert not s.settings.setup.models.multiphase.advanced_formulation.implicit_body_force()
            zi=s.fields.solution_variable_info.get_zones_info();zones=[z for z in zi.zone_names if zi[z].zone_type=='fluid'];assert zones==['fluid']
            nc=zi['fluid'].count;assert nc==j['pair']['counts']['cells']
            arrays={};specs=[('centroid','mixture','SV_CENTROID'),('volume','mixture','SV_VOLUME'),
               ('u','mixture','SV_U'),('v','mixture','SV_V'),('w','mixture','SV_W'),('pressure','mixture','SV_P'),('alpha','phase-2','SV_VOF')]
            for key,domain,var in specs:
                data=s.fields.solution_variable_data.get_data(variable_name=var,zone_names=['fluid'],domain_name=domain)
                arr=np.asarray(data['fluid']).reshape(nc,3) if key=='centroid' else np.asarray(data['fluid']).reshape(nc)
                assert np.isfinite(arr).all(),key;arrays[key]=arr
                print(j['level'],j['iteration'],key,'READ',flush=True)
            assert (arrays['volume']>0).all();assert arrays['alpha'].min()>=-1e-12 and arrays['alpha'].max()<=1+1e-12
            quality=__import__('csv').DictReader((ROOT/'PyAnsys/output/mesh-audits/2026-10-08-purnanto-remesh/single-family/mesh-quality-summary.csv').open())
            quality=list(quality)[int(j['level'][1:])-1];vol=float(arrays['volume'].sum());assert abs(vol-float(quality['volume_m3']))/vol<1e-7
            original={k:v[0] for d in j['reports'] for k,v in d.items()}
            rho=j['settings']['materials']['fluid']['water-liquid-at-psep']['density']['value']
            mass=float(np.dot(arrays['volume'],arrays['alpha'])*rho);speed=np.sqrt(arrays['u']**2+arrays['v']**2+arrays['w']**2)
            mean=float(np.dot(arrays['volume'],speed)/vol)
            assert np.isclose(mass,original['p10-mass-phase-2'],rtol=1e-9), (mass,original['p10-mass-phase-2'])
            assert np.isclose(mean,original['p10-speed-mean'],rtol=1e-9), (mean,original['p10-speed-mean'])
            np.savez_compressed(target,**arrays)
            meta=dict(level=j['level'],iteration=j['iteration'],pair=j['pair'],original_checkpoint_reports=j['reports'],
                cells=nc,total_volume_m3=vol,liquid_mass_kg=mass,volume_mean_speed_m_s=mean,max_speed_m_s=float(speed.max()),
                field_mapping=specs,zone='fluid',native_cell_centroid_bounds=[arrays['centroid'].min(axis=0).tolist(),arrays['centroid'].max(axis=0).tolist()],
                local_array_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,
                seconds=time.monotonic()-start,cell_order='Native Fluent zone and partition order; same for all seven arrays',
                reload_limit='Outlet face velocities can change on reload; comparison uses cell fields, verified against original bulk reports',
                new_solved_updates=0)
            metadata.write_text(json.dumps(meta,indent=2)+'\n');result['sources'].append(meta);persist()
            print(j['level'],j['iteration'],'SAVED',round(meta['seconds'],1),flush=True)
        result['status']='EXTRACTED'
    except Exception as e:result.update(status='EXTRACTION_ERROR',error=repr(e));raise
    finally:
        if s is not None:
            try:
                assert not s.settings.solution.run_calculation.iterating()
                if loaded:
                    s.settings.file.read_case(file_name=restore['case']);s.settings.file.read_data(file_name=restore['data'])
                result['restore_iteration']=counter(s)
                result['restore_ON']=s.settings.setup.models.multiphase.advanced_formulation.implicit_body_force()
                result['restore_verified']=result['restore_iteration']==3005 and result['restore_ON']
                assert result['restore_verified']
            except Exception as e:result['restore_error']=repr(e)
            s._fluent_connection._channel.close()
        persist()
    print(json.dumps(dict(status=result['status'],sources=len(result['sources']),solves_issued=0,restore_verified=result.get('restore_verified'))))
if __name__=='__main__':main()

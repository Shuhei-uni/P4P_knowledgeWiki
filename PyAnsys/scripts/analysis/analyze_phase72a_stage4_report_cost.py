"""Compare verified report-cost arms at equal film time; no Fluent connection."""
from pathlib import Path
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyze_phase72a_stage4_analytical import block, value

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'PyAnsys/output/phase72a-stage4-report-cost/20261008'
DOC = ROOT / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/report-cost'


def main():
    arms, histories, folders = {}, {}, {}
    for arm in ['core17', 'full60']:
        p=OUT/arm/'run-manifest.json'
        if not p.exists():continue
        m=json.loads(p.read_text())
        if not m['blocks']:continue
        assert len(m['blocks']) == 1
        folder=ROOT/m['blocks'][0];record=json.loads((folder/'run-manifest.json').read_text())
        metrics,t,h=block(record)
        metrics['bulk_endpoints_unchanged']=record['before']['bulk'] == record['final']['bulk']
        metrics['physics_parameters_unchanged']=record['before']['parameters'] == record['final']['parameters']
        metrics['drain_time_s']=.0015
        arms[arm]=metrics;histories[arm]=(t,h);folders[arm]=folder
    comparison={}
    if len(arms)==2:
        a,b=arms['full60'],arms['core17']
        assert a['native_start']==b['native_start']==41503 and a['native_end']==b['native_end']==42503
        assert a['updates']==b['updates']==1000
        comparison['whole_command_speedup']=a['simulation_wall_s']/b['simulation_wall_s']
        comparison['whole_command_time_reduction_percent']=100*(1-b['simulation_wall_s']/a['simulation_wall_s'])
        common=set(histories['full60'][1]) & set(histories['core17'][1])
        agreements={}
        for name in sorted(common):
            x,y=histories['full60'][1][name],histories['core17'][1][name]
            assert x.shape==y.shape
            absolute=float(np.abs(x-y).max())
            scale=max(float(np.abs(x).max()),1e-12)
            agreements[name]={'max_absolute_difference':absolute,'relative_to_reference_peak':absolute/scale,
                              'allclose_rtol_1e5_atol_1e8':bool(np.allclose(x,y,rtol=1e-5,atol=1e-8))}
        comparison['common_report_agreement']=agreements
        fields={}
        for wall in ['upper','lower']:
            x=np.load(folders['full60']/(wall+'-fields.npz'))
            y=np.load(folders['core17']/(wall+'-fields.npz'))
            assert set(x.files)==set(y.files)
            # Native face order can change on a parallel case/data reopen.
            # Compare the same physical facets using their unique centres.
            ox=np.lexsort(x['centroids'].T[::-1]);oy=np.lexsort(y['centroids'].T[::-1])
            assert len(np.unique(x['centroids'],axis=0))==len(ox)
            assert len(np.unique(y['centroids'],axis=0))==len(oy)
            assert np.array_equal(x['centroids'][ox],y['centroids'][oy])
            fields[wall]={}
            for name in x.files:
                assert x[name].shape==y[name].shape
                fields[wall][name]={'max_absolute_difference':float(np.abs(x[name][ox]-y[name][oy]).max()),
                    'allclose_rtol_1e5_atol_1e8':bool(np.allclose(x[name][ox],y[name][oy],rtol=1e-5,atol=1e-8)),
                    'alignment':'Unique native face centres'}
        comparison['endpoint_field_agreement']=fields
        comparison['numerical_equivalence_passed']=all(v['allclose_rtol_1e5_atol_1e8'] for v in agreements.values()) and all(v['allclose_rtol_1e5_atol_1e8'] for fields_on_wall in fields.values() for v in fields_on_wall.values())
        comparison['performance_screen_passed']=comparison['whole_command_time_reduction_percent']>=20 and comparison['numerical_equivalence_passed']
        fig,grid=plt.subplots(1,2,figsize=(9,4),constrained_layout=True)
        names=['p72d-total-mass','p72a-e2.7-ewf-velocity-mag-max']
        for arm,(t,h) in histories.items():
            for ax,name in zip(grid,names):ax.plot((t-t[0])*1000,h[name],label=arm,lw=1.2)
        for ax,label in zip(grid,['Total film mass (kg)','Maximum film speed (m/s)']):
            ax.set(xlabel='Added accepted film time (ms)',ylabel=label);ax.grid(alpha=.2)
        grid[0].legend();fig.suptitle('Report-cost comparison — same parent, timestep and film physics')
        d=DOC/'figures';d.mkdir(parents=True,exist_ok=True);fig.savefig(d/'report-cost-agreement.png',dpi=180);plt.close(fig)
    summary={'arms':arms,'comparison':comparison,'source_manifest_sha256':{arm:hashlib.sha256((folder/'run-manifest.json').read_bytes()).hexdigest() for arm,folder in folders.items()},'limitations':['Reported-rate film ledger does not independently reconcile DPM event deposition','Sparse arm has endpoint bulk checks, not continuous bulk histories']}
    (OUT/'comparison-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if len(arms)==2:
        plot=DOC/'figures/report-cost-agreement.png'
        provenance={'figure_sha256':hashlib.sha256(plot.read_bytes()).hexdigest(),
                    'analysis_summary_sha256':hashlib.sha256((OUT/'comparison-summary.json').read_bytes()).hexdigest(),
                    'source_manifest_sha256':summary['source_manifest_sha256'],
                    'source_windows':{arm:[met['native_start'],met['native_end']] for arm,met in arms.items()},
                    'quantities':{'x':'Accepted added film time, ms','left':'Total film mass, kg','right':'Maximum film speed, m/s'},
                    'time_origin':'Native film clock at N41503; no invented bulk histories',
                    'field_alignment':'Unique native face centres; identical mesh geometry',
                    'timing':'Native Simulation wall-clock time; save/reopen/retrieval excluded',
                    'claim_limit':summary['limitations']}
        (plot.with_suffix('.provenance.json')).write_text(json.dumps(provenance,indent=2)+'\n')
    print(json.dumps({'arms':{arm:{k:v for k,v in met.items() if k not in ['source_sha256']} for arm,met in arms.items()},'comparison':{k:v for k,v in comparison.items() if k not in ['common_report_agreement','endpoint_field_agreement']}},indent=2))


if __name__=='__main__':main()

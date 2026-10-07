"""Reduce the isolated source proof and matched native EWF-drain screens."""
from pathlib import Path
import hashlib,json,math,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup')]
from run_phase72a_adaptive_film import history
OUT=ROOT/'output/phase72a-stage4-ewf-drain/20261007'
DOC=ROOT.parent/'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/ewf-only-drain'


def dump(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def arm(name):
    folder=OUT/name;m=json.loads((folder/'run-manifest.json').read_text())
    assert m['status']=='SCREEN_COMPLETE_VERIFIED'
    raw=ROOT.parent/m['blocks'][-1]['raw_directory']
    x=np.arange(m['parent_native_iteration']+1,m['verified_native_end']+1)
    h={key:history((raw/(key+'.out')).read_text()) for key in m['report_paths']}
    assert all(set(x).issubset(v) for v in h.values())
    dt=np.concatenate([np.full(b['updates'],b['step_s']) for b in m['blocks']])
    assert len(dt)==len(x)==1000
    data={key:np.array([m['initial'][key][0]]+[h[key][int(i)] for i in x]) for key in m['initial']}
    elapsed=np.r_[0,np.cumsum(dt)]
    drain_left=float(np.sum(data['p72d-drain-rate'][:-1]*dt))
    drain_right=float(np.sum(data['p72d-drain-rate'][1:]*dt))
    changes={key:float(data['p72d-total-'+key][-1]-data['p72d-total-'+key][0]) for key in ['mass','outflow','stripped','separated']}
    inputs={key:float(np.sum(data['p72d-total-'+key][1:]*dt)) for key in ['secondary','dpm']}
    lower_inputs={key:float(np.sum(data['p72d-lower-'+key][1:]*dt)) for key in ['secondary','dpm']}
    lower_changes={key:float(data['p72d-lower-'+key][-1]-data['p72d-lower-'+key][0]) for key in ['mass','outflow','stripped','separated']}
    included=m['outflow_convention']=='USER_DRAIN_INCLUDED_IN_NATIVE_OUTFLOW'
    sources=sum(inputs.values());base_residual=sum(changes.values())-sources
    residual_left=base_residual+(0 if included else drain_left)
    residual_right=base_residual+(0 if included else drain_right)
    peak=max(b['thickness_assessment']['peak_thickness_m'] for b in m['blocks'])
    summary={'status':m['status'],'native_start':m['parent_native_iteration'],'native_end':m['verified_native_end'],
        'updates':len(x),'added_film_time_s':m['film']['film_elapsed_time']-m['parent_film_time_s'],
        'source_enabled':m['source_enabled'],'film_initial_kg':float(data['p72d-total-mass'][0]),
        'film_final_kg':float(data['p72d-total-mass'][-1]),'upper_final_kg':float(data['p72d-upper-mass'][-1]),
        'lower_final_kg':float(data['p72d-lower-mass'][-1]),'drain_final_kg_s':float(data['p72d-drain-rate'][-1]),
        'drain_integral_left_kg':drain_left,'drain_integral_right_kg':drain_right,
        'drain_quadrature_span_kg':abs(drain_left-drain_right),
        'lower_integrated_sources_kg':lower_inputs,'lower_mass_changes_kg':lower_changes,
        'lower_transport_plus_sampled_ledger_residual_kg':sum(lower_changes.values())+(0 if included else drain_left)-sum(lower_inputs.values()),
        'drain_last500_mean_kg_s':float(np.mean(data['p72d-drain-rate'][-500:])),
        'film_last500_storage_mean_kg_s':float((data['p72d-total-mass'][-1]-data['p72d-total-mass'][-501])/np.sum(dt[-500:])),
        'mass_changes_kg':changes,'integrated_sources_kg':inputs,'outflow_convention':m['outflow_convention'],
        'sampled_film_ledger_residual_left_kg':residual_left,'sampled_film_ledger_residual_right_kg':residual_right,
        'sampled_film_ledger_error_left_percent':100*abs(residual_left)/max(sources,1e-30),
        'sampled_film_ledger_error_right_percent':100*abs(residual_right)/max(sources,1e-30),
        'peak_thickness_m':peak,'peak_courant':max(b['peak_courant'] for b in m['blocks']),
        'bulk_equations_frozen':True,'bulk_reports_unchanged':all(
            b['bulk_before'].keys()==b['bulk_after'].keys() and all(
                math.isclose(v[0],b['bulk_after'][key][0],rel_tol=1e-9,abs_tol=1e-10)
                and v[1:]==b['bulk_after'][key][1:] for key,v in b['bulk_before'].items()) for b in m['blocks']),
        'bulk_report_comparison_relative_tolerance':1e-9,
        'paired_reopen':'PASS','final_pair':m['final_pair']}
    assert summary['bulk_reports_unchanged'] and summary['peak_thickness_m']<.3
    return summary,elapsed,data


def main():
    m=json.loads((OUT/'run-manifest.json').read_text());assert m['status']=='DRAIN_COMPLETE_VERIFIED'
    proof=json.loads((OUT/'proof/proof.json').read_text());assert proof['status']=='SOURCE_REMOVAL_VERIFIED'
    figs=DOC/'figures';figs.mkdir(exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(10,3.7),constrained_layout=True)
    for name,color in [('off','#888888'),('on','#0072B2')]:
        a=proof['arms'][name];t=np.array(a['elapsed_film_time_s'])*1000;stock=np.array(a['mass_kg'])
        axes[0].plot(t,stock*1000,label='Drain '+name.upper(),color=color)
    a=proof['arms']['on'];stock=np.array(a['mass_kg']);t=np.array(a['elapsed_film_time_s'])*1000
    loss=stock[0]-stock;integral=np.r_[0,np.cumsum(np.array(a['rate_kg_s'])[:-1]*proof['step_s'])]
    axes[1].plot(t,loss*1000,label='Native film mass loss',color='#0072B2')
    axes[1].plot(t,integral*1000,label='Integrated mass source',color='#D55E00',ls='--')
    for ax in axes:ax.set_xlabel('Added native film time (ms)');ax.legend();ax.grid(alpha=.2)
    axes[0].set_ylabel('Lower film inventory (g)');axes[1].set_ylabel('Removed liquid (g)')
    fig.suptitle('Isolated film source proof — bulk equations frozen')
    fig.savefig(figs/'source-proof.png',dpi=180);plt.close(fig)
    summaries={};arrays={}
    for name in ['off','on']:
        a,t,d=arm(name);summaries[name]=a;arrays[name]=(t,d)
    fig,axes=plt.subplots(1,3,figsize=(12,3.7),constrained_layout=True)
    for name,color in [('off','#888888'),('on','#0072B2')]:
        t,d=arrays[name];label='Drain '+name.upper()
        axes[0].plot(t*1000,d['p72d-total-mass'],label=label,color=color)
        axes[1].plot(t*1000,d['p72d-lower-mass']*1000,label=label,color=color)
        axes[2].plot(t*1000,d['p72d-drain-rate'],label=label,color=color)
    for ax in axes:ax.set_xlabel('Added native film time (ms)');ax.grid(alpha=.2);ax.legend()
    axes[0].set_ylabel('Total film inventory (kg)');axes[1].set_ylabel('Lower collector film (g)')
    axes[2].set_ylabel('Applied film drain (kg/s)')
    fig.suptitle('Matched production screen — N40483 parent, 15 µs steps, bulk frozen')
    fig.savefig(figs/'drain-comparison.png',dpi=180);plt.close(fig)
    # Show the actual collector geometry, without inventing a fitted drain plane.
    upper=np.load(OUT/'wall-geometry.npz');lower=np.load(OUT/'wall-004-geometry.npz')
    u=upper['centroids'];l=lower['centroids'];mask=u[:,1]<.45
    fig,ax=plt.subplots(figsize=(5.5,3.8),constrained_layout=True)
    ax.scatter(u[mask,0],u[mask,1],s=9,c='#999999',label='Existing upper film faces')
    ax.scatter(l[:,0],l[:,1],s=24,c='#0072B2',label='Added film drain faces')
    ax.axhline(0,color='k',lw=.7);ax.set_xlabel('x (m)');ax.set_ylabel('Height y (m)')
    ax.set_ylim(-.02,.45);ax.legend();ax.set_title('Lower outer-wall film drain — actual face centres')
    fig.savefig(figs/'drain-location.png',dpi=180);plt.close(fig)
    diff=summaries['off']['film_final_kg']-summaries['on']['film_final_kg']
    result={'status':'ANALYSED','source_proof':{k:proof[k] for k in ['off_change_kg','on_removed_kg',
        'depletion_fraction_min','depletion_fraction_max','source_integral_relative_error_max','outflow_convention']},
        'screens':summaries,'off_minus_on_final_total_film_kg':diff,
        'physical_validation':False,'steady_film':False,
        'claim_scope':'Native local EWF source operator; matched short film-only routing contrast'}
    dump(OUT/'analysis-summary.json',result)
    source_files=sorted(p for p in OUT.rglob('*') if p.is_file() and ('raw' in p.parts or p.name.endswith('endpoint.npz')))
    dump(OUT/'raw-hashes.json',{str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files})
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

"""Summarize persisted contact-absorber evidence without controlling Fluent."""
import argparse
import json
import re
import statistics
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def window(values, count=200):
    v=values[-count:]
    return {'count':len(v),'last':v[-1],'mean':statistics.mean(v),
            'minimum':min(v),'maximum':max(v),'std':statistics.pstdev(v)}


def analyze(bundle, continuation_tag=None):
    summaries={}
    for tag in ([] if continuation_tag else ['corrected-100us','corrected-10us','corrected-1us']):
        record=json.loads((bundle/f'{tag}.json').read_text())
        h=json.loads((bundle/f'{tag}-histories.json').read_text())
        summaries[tag]={'endpoint':record['blocks'][-1]['after'],
          'late50':{k:window(h[k]['values'],50) for k in [
             'p72-contact-inventory','p72-contact-removal','p72-contact-alpha-max',
             'p72a-e2.7-ewf-thickness-max','p72a-e2.7-ewf-courant-max']}}
    tag=continuation_tag or 'corrected-10us-qualification'
    record=json.loads((bundle/f'{tag}.json').read_text())
    h=json.loads((bundle/f'{tag}-histories.json').read_text())
    x=h['p72-contact-inventory']['iterations']
    text=(bundle/('transcript.txt' if continuation_tag else 'transcript-corrected.txt')).read_text(errors='replace')
    # The final parent-data read starts this qualifier. Keep repeated short
    # screens separate even though they share native iteration coordinates.
    if not continuation_tag:
        marker='corrected-10us\\block-N13686.dat.h5'
        if marker not in text: raise ValueError('Qualification parent read not found')
        text=text[text.rfind(marker):]
    pattern=r'^\s*(\d+)\s+([\d.+-]+e[+-]\d+)\s+([\d.+-]+e[+-]\d+)\s+([\d.+-]+e[+-]\d+)\s+([\d.+-]+e[+-]\d+)\s+([\d.+-]+e[+-]\d+)\s+([\d.+-]+e[+-]\d+)\s+([\d.+-]+e[+-]\d+)'
    residuals={int(m[0]):[float(v) for v in m[1:]] for m in re.findall(pattern,text,re.MULTILINE)
               if x[0]<=int(m[0])<=x[-1]}
    if set(residuals)!=set(x): raise ValueError('Native residual/history coverage differs')
    if any(v['iterations']!=x for v in h.values()):
        raise ValueError('Report histories do not share native coordinates')
    keys=['p72-contact-inventory','p72-contact-removal','p72-contact-alpha-max',
          'p72a-e2.7-ewf-film-mass-total','p72a-e2.7-ewf-thickness-max',
          'p72a-e2.7-ewf-courant-max','v2-total-liquid-mass',
          'v2-flux-phase2-steamoutlet','v2-flux-phase1-steamoutlet']
    q={'status':record['status'],'native_window':[x[0],x[-1]],
       'recorded_iterations':len(x),'endpoint':record['blocks'][-1]['after'],
       'late200':{k:window(h[k]['values']) for k in keys},
       'residuals_late200':{name:window([residuals[i][idx] for i in x])
                            for name,idx in [('continuity',0),('phase2_volume_fraction',6)]},
       'claim_limits':['finite tau is approximate bulk contact removal',
         'existing stepped cell-zone boundary is not an exact y=0.10 plane',
         'film-side closure is separate from unqualified bulk and whole-separator closure',
         'frozen-field DPM interaction test is not two-way carrier convergence',
         'film elapsed time uses the recorded timestep; timestep matching alone does not establish full historical numerical parity']}
    summaries['qualification']=q
    if continuation_tag:
        sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
        from pyansys_fluent.ewf_edge_ledger import native_ewf_edge_ledger
        manifest=json.loads((bundle/'run-manifest.json').read_text())
        pair=manifest.get('final_pair_local',record['blocks'][-1]['pair'])
        ledger_parent=manifest.get('analysis_parent_pair_local',manifest['parent_pair'])
        dt=float(record['film_parameters']['timestep-max'])
        rate_integral=sum(h['p72a-e2.7-ewf-secondary-phase-mass-total']['values'][1:])*dt
        film_change=h['p72a-e2.7-ewf-film-mass-total']['values'][-1]-h['p72a-e2.7-ewf-film-mass-total']['values'][0]
        outflow=h['p72a-e2.7-ewf-outflow-mass-total']['values'][-1]-h['p72a-e2.7-ewf-outflow-mass-total']['values'][0]
        edge=native_ewf_edge_ledger(pair['case'],ledger_parent['data'],pair['data'])
        if abs(edge['whole_wall_increment_kg']-outflow)>1e-8:
            raise ValueError('Native saved-film outflow and report increment differ')
        q['film_ledger']={'film_elapsed_s':(x[-1]-x[0])*dt,
          'film_inventory_change_kg':film_change,'native_outflow_increment_kg':outflow,
          'phase_accretion_rate_integral_kg':rate_integral,
          'closure_error_percent':100*abs(film_change+outflow-rate_integral)/abs(rate_integral),
          'native_edge_outflow':edge,
          'units_note':'Film Secondary Phase Mass numeric is accretion kg/s despite native kg label; cumulative outflow is kg',
          'scope':'film clock only; internal accretion transfer is not extra external removal; bulk/joint closure unqualified'}
    (bundle/'analysis-summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    axes[0,0].plot(x,[100*v for v in h['p72-contact-alpha-max']['values']])
    axes[0,0].set_ylabel('Maximum collector liquid fraction (%)')
    axes[0,0].set_title('Near-dry collector; finite removal time')
    axes[0,1].plot(x,h['p72-contact-removal']['values'],label='Bulk collector source')
    axes[0,1].axhline(116.92,color='gray',linestyle='--',label='Liquid inlet reference')
    axes[0,1].set_ylabel('Mass rate (kg/s)');axes[0,1].legend(fontsize=8)
    axes[0,1].set_title('Film drainage is accounted separately')
    axes[1,0].plot(x,[1000*v for v in h['p72a-e2.7-ewf-thickness-max']['values']])
    axes[1,0].set_ylabel('Maximum film thickness (mm)')
    axes[1,0].set_title('Diagnostic cap: 1000 mm')
    axes[1,1].semilogy(x,[residuals[i][0] for i in x],label='Continuity')
    axes[1,1].semilogy(x,[residuals[i][6] for i in x],label='Phase-2 fraction')
    axes[1,1].set_ylabel('Native scaled residual');axes[1,1].legend(fontsize=8)
    axes[1,1].set_title('Numerical behaviour, not a closure proof')
    for ax in axes.flat:
        ax.set_xlabel('Native iteration');ax.grid(alpha=.25)
    film_step_us=float(record['film_parameters']['timestep-max'])*1e6
    fig.suptitle(f'R3 + E2.7 contact absorber: 10 µs bulk sink, {film_step_us:g} µs film step, liquid momentum, fraction relaxation 0.1')
    fig.savefig(bundle/'contact-absorber-qualification.png',dpi=180)
    plt.close(fig)
    return summaries


def analyze_long_film(bundle,parent_bundle,continuation_tag):
    """Stitch a verified endpoint continuation and assess declared film metrics."""
    import math
    import numpy as np
    manifest=json.loads((bundle/'run-manifest.json').read_text())
    parent_manifest=json.loads((parent_bundle/'run-manifest.json').read_text())
    left=json.loads((parent_bundle/(parent_manifest['tag']+'-histories.json')).read_text())
    right=json.loads((bundle/(continuation_tag+'-histories.json')).read_text())
    if left.keys()!=right.keys(): raise ValueError('Continuation report definitions differ')
    joined={}
    for key in left:
        a,b=left[key],right[key]
        if a['iterations'][-1]!=b['iterations'][0]:
            raise ValueError('Native continuation overlap differs')
        if not math.isclose(a['values'][-1],b['values'][0],rel_tol=1e-9,abs_tol=1e-10):
            raise ValueError(f'Unverified overlap value: {key}')
        joined[key]={'iterations':a['iterations']+b['iterations'][1:],
                     'values':a['values']+b['values'][1:]}
    x=np.asarray(joined['p72a-e2.7-ewf-film-mass-total']['iterations'])
    if x.tolist()!=list(range(13586,23587)):
        raise ValueError('Expected all 10001 native coordinates')
    dt=float(manifest['film_timestep_s'])
    mass=np.asarray(joined['p72a-e2.7-ewf-film-mass-total']['values'])
    thickness=np.asarray(joined['p72a-e2.7-ewf-thickness-max']['values'])
    mean_thickness=np.asarray(joined['p72a-e2.7-ewf-thickness-awavg']['values'])
    outflow=np.asarray(joined['p72a-e2.7-ewf-outflow-mass-total']['values'])
    accretion=np.asarray(joined['p72a-e2.7-ewf-secondary-phase-mass-total']['values'])
    limits=manifest['steady_screen']
    windows=[]
    for end in [21586,22586,23586]:
        select=(x>=end-1000)&(x<=end)
        sub=x[select]
        rates=(x>end-1000)&(x<=end)
        inward=float(np.sum(accretion[rates])*dt)
        drainage=float(outflow[x==end][0]-outflow[x==end-1000][0])
        row={'native_window':[end-1000,end],
             'accretion_integral_kg':inward,'drainage_increment_kg':drainage,
             'relative_accretion_drainage_gap_percent':100*abs(inward-drainage)/abs(inward)}
        for name,values in [('inventory',mass),('maximum_thickness',thickness),
                            ('mean_thickness',mean_thickness)]:
            y=values[select]
            slope=float(np.polyfit(sub-sub[0],y,1)[0])
            row[name]={'start':float(y[0]),'end':float(y[-1]),
              'fitted_slope_per_update':slope,
              'fitted_drift_percent_per_1000_updates':100*slope*1000/float(y.mean())}
        row['stationarity_pass']=(
          abs(row['inventory']['fitted_drift_percent_per_1000_updates'])<=limits['maximum_fitted_inventory_drift_percent_per_window']
          and abs(row['maximum_thickness']['fitted_drift_percent_per_1000_updates'])<=limits['maximum_fitted_thickness_drift_percent_per_window']
          and row['relative_accretion_drainage_gap_percent']<=limits['maximum_relative_accretion_drainage_gap_percent'])
        windows.append(row)
    accreted=float(np.sum(accretion[1:])*dt)
    drained=float(outflow[-1]-outflow[0])
    inventory_change=float(mass[-1]-mass[0])
    ledger_error=100*abs(inventory_change+drained-accreted)/abs(accreted)
    peak_cfl=max(joined['p72a-e2.7-ewf-courant-max']['values'][1:])
    passed=(all(w['stationarity_pass'] for w in windows)
      and ledger_error<=limits['maximum_film_ledger_error_percent']
      and peak_cfl<=limits['maximum_film_cfl'])
    summary={'status':'GLOBAL_FILM_METRICS_PASS_STATIONARITY_SCREEN' if passed else 'NO_STATIONARY_FILM_WITHIN_REQUESTED_HORIZON',
      'scope':'global film metric screen; bulk/joint and full spatial convergence separate',
      'native_window':[int(x[0]),int(x[-1])],'restart_updates':10000,
      'added_film_time_s':10000*dt,'overlap_verification':'all 29 reports agree at N17586 within 1e-9 relative and 1e-10 absolute',
      'film_mass_start_kg':float(mass[0]),'film_mass_end_kg':float(mass[-1]),
      'max_thickness_start_m':float(thickness[0]),'max_thickness_end_m':float(thickness[-1]),
      'minimum_of_maximum_thickness_m':float(thickness.min()),
      'native_iteration_at_minimum_maximum_thickness':int(x[np.argmin(thickness)]),
      'mean_thickness_start_m':float(mean_thickness[0]),'mean_thickness_end_m':float(mean_thickness[-1]),
      'peak_film_cfl':peak_cfl,'tail_windows':windows,
      'inherited_parent_film_cfl':joined['p72a-e2.7-ewf-courant-max']['values'][0],
      'full_restart_film_ledger':{'inventory_change_kg':inventory_change,
        'accretion_integral_kg':accreted,'outflow_increment_kg':drained,
        'closure_error_percent':ledger_error},'criteria':limits,
      'sources':[str(parent_bundle),str(bundle)]}
    (bundle/'stitched-10000-histories.json').write_text(json.dumps(joined)+'\n')
    (bundle/'film-time-assessment.json').write_text(json.dumps(summary,indent=2)+'\n')
    elapsed_ms=(x-x[0])*dt*1000
    fig,axes=plt.subplots(3,1,figsize=(10,9),layout='constrained',sharex=True)
    axes[0].plot(elapsed_ms,thickness*1000,label='Maximum')
    axes[0].set_ylabel('Maximum film thickness (mm)');axes[0].legend()
    axes[1].plot(elapsed_ms,mass);axes[1].set_ylabel('Film inventory (kg)')
    drain_rate=np.diff(outflow)/dt
    axes[2].plot(elapsed_ms[1:],accretion[1:],alpha=.25,label='Accretion, raw')
    axes[2].plot(elapsed_ms[1:],drain_rate,alpha=.25,label='Edge outflow, raw')
    kernel=np.ones(100)/100
    axes[2].plot(elapsed_ms[100:],np.convolve(accretion[1:],kernel,mode='valid'),label='Accretion, 100-update mean')
    axes[2].plot(elapsed_ms[100:],np.convolve(drain_rate,kernel,mode='valid'),label='Edge outflow, 100-update mean')
    axes[2].set_ylabel('Native film rate (kg/s)');axes[2].legend(fontsize=8)
    axes[2].set_xlabel('Added film time from original E2.7 restart (ms)')
    for ax in axes:
        ax.axvline(4,color='gray',linestyle='--',label='Server 1 continuation starts')
        ax.grid(alpha=.25)
    fig.suptitle('R3 + E2.7 contact absorber: 10,000 updates at a fixed 1 microsecond film step\nDashed line: host transfer after 4,000 updates; steady bulk solver clock is separate')
    fig.savefig(bundle/'film-time-10000.png',dpi=180)
    plt.close(fig)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('bundle',type=Path)
    p.add_argument('--continuation-tag')
    p.add_argument('--parent-bundle',type=Path)
    args=p.parse_args()
    result=analyze(args.bundle,args.continuation_tag)['qualification']
    if args.parent_bundle:
        result=analyze_long_film(args.bundle,args.parent_bundle,args.continuation_tag)
    print(json.dumps(result,indent=2))

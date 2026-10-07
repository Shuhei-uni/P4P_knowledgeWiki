"""Compare selected film histories at equal native film time, retaining raw signals."""
from pathlib import Path
import csv
import hashlib
import json
import math
import re

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[2]
CAMPAIGN = ROOT/'output/phase72a-stage3-speed-sensitivity-server1/20261006'
BASE = ROOT/'output/phase72a-stage3-film-development-server1/20261005'
STARTUP = ROOT/'output/phase72a-stage3-early-ewf-server1/20261005'
PROJECT = ROOT.parent/'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/inlet-speed-500ms'
REPORTS = {'film_kg':'p72a-e2.7-ewf-film-mass-total',
           'accretion_kg_s':'p72a-e2.7-ewf-secondary-phase-mass-total',
           'cumulative_drainage_kg':'p72a-e2.7-ewf-outflow-mass-total',
           'bulk_liquid_kg':'v2-total-liquid-mass',
           'carryover_signed_kg_s':'v2-flux-phase2-steamoutlet'}
COLORS = {'reference':'#1f77b4','low':'#2ca02c','high':'#d17a19'}


def load(path):
    return json.loads(Path(path).read_text())


def selected_blocks(m, label, terminal):
    """Follow the selected time joins backwards; exclude rejected and sibling arms."""
    if label=='reference':
        chosen = [next(a for a in m['sensitivity_arms'].values() if a['pair']['native_iteration']==5090),
                  m['mid_film_arms'][m['mid_film_selected_arm']]]
    else:
        qualified=m['alternative_sensitivity']['qualified_fixed_step_s']
        chosen=[next(a for a in reversed(list(m['sensitivity_arms'].values()))
                     if math.isclose(a['metrics']['printed_step_max_s'],qualified,rel_tol=1e-8))]
    allowed={a['pair']['case_sha256'] for a in chosen}
    rejected={b['pair']['case_sha256'] for b in m.get('campaign_rejected_blocks',[])}
    candidates=[b for b in m['blocks'] if b.get('pair') and b['pair']['case_sha256'] not in rejected
                and (Path(b.get('output','')).name.startswith('adaptive-') or b['pair']['case_sha256'] in allowed)
                and b['peak_film_cfl']<=1 and b['film_ledger_error_percent']<=.1]
    cursor=terminal; backwards=[]
    while cursor>.0035+1e-10:
        matches=[b for b in candidates if abs(b['film_time_s']-cursor)<1e-10]
        if not matches:
            raise RuntimeError(f'{label}: missing selected predecessor at film time {cursor}')
        b=matches[-1];backwards.append(b);cursor=b['film_time_s']-b['added_film_time_s']
        candidates=[x for x in candidates if x is not b]
    assert abs(cursor-.0035)<1e-10
    return backwards[::-1]


def history_rows(m, label, terminal):
    startup=STARTUP if label=='reference' else CAMPAIGN/label/'startup'
    h=load(startup/'final-histories.json')
    reports={k:dict(zip(h[name]['iterations'],h[name]['values'])) for k,name in REPORTS.items()}
    prepared=load(startup/'prepared-reopen.json')['state']['readback']['fields']
    rows=[{'native_iteration':1580,'film_time_s':0.,'film_dt_s':0.,'film_kg':0.,
           'cumulative_drainage_kg':0.,'accretion_kg_s':0.,'drainage_kg_s':0.,
           'bulk_liquid_kg':prepared['v2-total-liquid-mass'][0],
           'carryover_signed_kg_s':prepared['v2-flux-phase2-steamoutlet(without-sources)'][0],
           'source_segment':'prepared A; dry film'}]
    for n in range(1581,5081):
        row={k:values[n] for k,values in reports.items()}
        row.update(native_iteration=n,film_time_s=(n-1580)*1e-6,film_dt_s=1e-6,
                   drainage_kg_s=(row['cumulative_drainage_kg']-rows[-1]['cumulative_drainage_kg'])/1e-6,
                   source_segment='startup')
        rows.append(row)
    cache={}
    blocks=selected_blocks(m,label,terminal)
    for b in blocks:
        folder=Path(b['output']);start,end=b['native_start'],b['native_end']
        if folder not in cache:
            h=load(folder/'report-histories.json')
            cache[folder]={k:dict(zip(h[name]['iterations'],h[name]['values'])) for k,name in REPORTS.items()}
        signals=cache[folder]
        assert abs(rows[-1]['film_time_s']-(b['film_time_s']-b['added_film_time_s']))<1e-10
        for key in ['film_kg','cumulative_drainage_kg','bulk_liquid_kg','carryover_signed_kg_s']:
            assert np.isclose(rows[-1][key],signals[key][start],rtol=1e-8,atol=1e-8),(label,start,key)
        clocks=load(folder/f'clocks-N{start}-N{end}.json')
        exact=(b['printed_step_min_s']==b['printed_step_max_s']
               and math.isclose(b['final_accepted_step_s']*b['updates'],b['added_film_time_s'],rel_tol=1e-10,abs_tol=1e-12))
        for n in range(start+1,end+1):
            t=b['film_time_s']-b['added_film_time_s']+(n-start)*b['final_accepted_step_s'] if exact else clocks[str(n)][0]
            if n==end:t=b['film_time_s']
            dt=b['final_accepted_step_s'] if exact else t-rows[-1]['film_time_s']
            assert dt>0
            row={k:values[n] for k,values in signals.items()}
            assert all(math.isfinite(x) for x in row.values())
            row.update(native_iteration=n,film_time_s=t,film_dt_s=dt,
                       drainage_kg_s=(row['cumulative_drainage_kg']-rows[-1]['cumulative_drainage_kg'])/dt,
                       source_segment=folder.name)
            rows.append(row)
    assert abs(rows[-1]['film_time_s']-terminal)<1e-10
    return rows,blocks


def window(rows, seconds=.01):
    finish=rows[-1]['film_time_s'];start=max(0,finish-seconds)
    duration=acc=drain=storage=0.
    for previous,row in zip(rows[:-1],rows[1:]):
        overlap=max(0,min(finish,row['film_time_s'])-max(start,previous['film_time_s']))
        if overlap:
            duration+=overlap;acc+=overlap*row['accretion_kg_s'];drain+=overlap*row['drainage_kg_s']
            storage+=overlap*(row['film_kg']-previous['film_kg'])/row['film_dt_s']
    assert abs(duration-min(seconds,finish))<1e-10
    return {'duration_s':duration,'accretion_kg_s':acc/duration,'drainage_kg_s':drain/duration,
            'storage_kg_s':storage/duration,'drainage_deficit_percent':100*(acc-drain)/acc}


RESIDUAL_NAMES=['continuity','x-velocity','y-velocity','z-velocity','k','epsilon','phase-2']


def startup_residuals(label):
    startup=STARTUP if label=='reference' else CAMPAIGN/label/'startup'
    if label=='reference':
        path=startup/'carrier-residuals.json';rows={int(n):v for n,v in load(path).items()}
    else:
        path=startup/'startup.trn';rows={}
        for line in path.read_text().splitlines():
            if re.match(r'^\s*\d+\s+[\d.+-]+e[+-]\d+\s+',line):
                tokens=line.split();n=int(tokens[0]);values=[float(v) for v in tokens[1:8]]
                assert len(values)==7 and all(math.isfinite(v) for v in values)
                if n in rows:assert rows[n]==values,(label,n,'Conflicting native carrier residuals')
                rows[n]=values
    required=list(range(1581,5081));assert set(required).issubset(rows)
    assert all(len(rows[n])==7 and all(math.isfinite(v) for v in rows[n]) for n in required)
    if label!='reference':
        native_export=startup/'carrier-residuals.json'
        old=load(native_export) if native_export.exists() else {}
        repaired=bool(old) and any(len(v)!=7 for v in old.values())
        if old and not repaired:
            assert all(old[str(n)]==rows[n] for n in required)
        native_export.write_text(json.dumps({str(n):rows[n] for n in sorted(rows)},indent=2)+'\n')
        (startup/'carrier-residual-coverage.json').write_text(json.dumps({
            'status':'NATIVE_SEVEN_RESIDUALS_VERIFIED','native_range':[1581,5080],'rows':3500,
            'source':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'numeric_columns':RESIDUAL_NAMES,'repaired_incomplete_numeric_export':repaired,
            'new_solve_calls':0},indent=2)+'\n')
    out=CAMPAIGN/f'{label}-startup-scaled-residuals.csv'
    with out.open('w',newline='') as stream:
        writer=csv.writer(stream);writer.writerow(['native_iteration']+RESIDUAL_NAMES)
        writer.writerows([n]+rows[n] for n in required)
    return {'native_range':[1581,5080],'rows':3500,'columns':RESIDUAL_NAMES,'source':str(path),
            'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'export':str(out),
            'final_500_mean':dict(zip(RESIDUAL_NAMES,np.mean([rows[n] for n in range(4581,5081)],axis=0).tolist()))}


def main():
    job=load(CAMPAIGN/'run-manifest.json');data={};sources={};summaries={}
    for label,entry in job['cases'].items():
        path=Path(entry.get('run_manifest',BASE/'run-manifest.json' if label=='reference' else CAMPAIGN/label/'film-development/run-manifest.json'))
        if not path.exists():continue
        m=load(path)
        if not m.get('latest_metrics') or m['latest_metrics']['film_time_s']<.004:continue
        terminal=entry.get('film_time_s',m['latest_metrics']['film_time_s'])
        rows,blocks=history_rows(m,label,terminal);data[label]=rows
        final=load(entry.get('endpoint',Path(m['latest_metrics']['output'])/f"endpoint-N{m['latest_metrics']['native_end']}.json"))
        field_path=Path(final['metrics']['facet_fields']);facets=dict(np.load(field_path))
        assert np.isclose(facets['film-mass'].sum(),rows[-1]['film_kg'],rtol=2e-6)
        summary={'nominal_speed_m_s':entry['nominal_speed_m_s'],'film_time_s':terminal,
                 'film_kg':rows[-1]['film_kg'],'bulk_liquid_kg':rows[-1]['bulk_liquid_kg'],
                 'carryover_signed_kg_s':rows[-1]['carryover_signed_kg_s'],
                 'film_max_facet_thickness_mm':float(facets['film-thickness'].max()*1000),
                 'final_10ms':window(rows),'status':entry['status'] if entry['status']=='COMPLETE_500MS' else ('PAUSED' if job['status']=='PAUSED' else 'RUNNING'),
                 'native_iteration':final['pair']['native_iteration'],'field_file':str(field_path),
                 'startup_carrier_residuals':startup_residuals(label)}
        fields=final['state']['readback']['fields']
        feed=fields['v2-flux-phase2-liquidinlet(without-sources)'][0]
        vapor_feed=fields['v2-flux-phase1-steaminlet'][0]
        outlet=fields['v2-flux-phase2-steamoutlet(without-sources)'][0]
        assert math.isclose(feed,entry['liquid_feed_kg_s'],rel_tol=1e-10)
        assert math.isclose(vapor_feed,entry['vapor_feed_kg_s'],rel_tol=1e-10)
        assert math.isclose(outlet,summary['carryover_signed_kg_s'],rel_tol=1e-10,abs_tol=1e-10)
        summary['frozen_carrier_snapshot']={'liquid_feed_kg_s':feed,'vapor_feed_kg_s':vapor_feed,
            'liquid_steamoutlet_signed_kg_s':outlet,'liquid_steamoutlet_percent_of_feed':-100*outlet/feed,
            'vapor_steamoutlet_signed_kg_s':fields['v2-flux-phase1-steamoutlet'][0],
            'contact_removal_kg_s':fields['p72-contact-removal'][0]}
        summaries[label]=summary;sources[label]={'run_manifest':str(path),'endpoint':final['pair'],
                                                'selected_blocks':blocks,'facets':facets}
        out=CAMPAIGN/f'selected-film-history-{label}.csv'
        with out.open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    if not data:return
    figures=PROJECT/'figures';figures.mkdir(parents=True,exist_ok=True)
    fig,axes=plt.subplots(2,1,figsize=(11,8),sharex=True,layout='constrained')
    for label,rows in data.items():
        t=np.array([r['film_time_s'] for r in rows])*1000;speed=summaries[label]['nominal_speed_m_s'];color=COLORS[label]
        axes[0].plot(t,[r['film_kg'] for r in rows],color=color,lw=1.2,label=f'{speed:.2f} m/s')
        axes[1].plot(t[1:],[r['accretion_kg_s'] for r in rows[1:]],color=color,lw=.8,label=f'{speed:.2f}: accretion')
        axes[1].plot(t[1:],[r['drainage_kg_s'] for r in rows[1:]],color=color,lw=.7,ls='--',label=f'{speed:.2f}: drainage')
    axes[0].set(ylabel='EWF film inventory (kg)',title='Inlet-speed comparison at equal film time')
    axes[1].set(ylabel='Film mass rate (kg/s)',xlabel='Native film time since dry start at A (ms)')
    for ax in axes:ax.grid(alpha=.2);ax.legend(fontsize=9);ax.set_xlim(0,500)
    image=figures/'film-development-three-speeds.png';fig.savefig(image,dpi=180);plt.close(fig)
    complete=len(data)==3 and all(e['status']=='COMPLETE_500MS' for e in job['cases'].values())
    lines=['# Stage 3 — Inlet-speed sensitivity at 500 ms','',
           '| State | Evidence |','| --- | --- |',f'| Controller | `{job["status"]}`; active case {job.get("active_case")} |',
           '| Scope | Three speed arms; independent startup from prepared A; film develops under each arm\'s frozen bulk fields |',
           '| Horizon | 500 ms native film time; not carrier elapsed physical time or a stationarity declaration |',
           '| Setup | [Scientific contract](setup.md) |',
           '| Machine state | [Campaign manifest](../../../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/run-manifest.json) |',
           '| Supervision | [Read-only monitor](../../../../../../PyAnsys/output/phase72a-stage3-speed-sensitivity-server1/20261006/monitor-state.json) |','',
           '![Film development at three inlet speeds](figures/film-development-three-speeds.png)','',
           '*Raw selected film histories; no smoothing. Solid rate lines show accretion; dashed lines show drainage. Rejected branches and unselected timestep arms are excluded.*','',
           '| Nominal speed (m/s) | State | Film time (ms) | Film mass (kg) | Bulk + film (kg) | Maximum facet thickness (mm) |',
           '| ---: | --- | ---: | ---: | ---: | ---: |']
    for label,entry in job['cases'].items():
        if label in summaries:
            q=summaries[label];lines.append(f'| {q["nominal_speed_m_s"]:.2f} | {q["status"]} | {q["film_time_s"]*1000:.6f} | {q["film_kg"]:.6f} | {q["bulk_liquid_kg"]+q["film_kg"]:.6f} | {q["film_max_facet_thickness_mm"]:.6f} |')
        else:lines.append(f'| {entry["nominal_speed_m_s"]:.2f} | {entry["status"]} | — | — | — | — |')
    lines+=['','| Nominal speed (m/s) | Final-window accretion (kg/s) | Drainage (kg/s) | Storage (kg/s) | Drainage deficit (%) |','| ---: | ---: | ---: | ---: | ---: |']
    for q in summaries.values():
        w=q['final_10ms'];lines.append(f'| {q["nominal_speed_m_s"]:.2f} | {w["accretion_kg_s"]:.6f} | {w["drainage_kg_s"]:.6f} | {w["storage_kg_s"]:.6f} | {w["drainage_deficit_percent"]:.6f} |')
    lines+=['','| Nominal speed (m/s) | Liquid feed (kg/s) | Vapor feed (kg/s) | Liquid steam-outlet flux (kg/s; signed) | Liquid steam-outlet/feed (%) | Contact removal (kg/s) |',
            '| ---: | ---: | ---: | ---: | ---: | ---: |']
    for q in summaries.values():
        snapshot=q['frozen_carrier_snapshot']
        lines.append(f'| {q["nominal_speed_m_s"]:.2f} | {snapshot["liquid_feed_kg_s"]:.6f} | {snapshot["vapor_feed_kg_s"]:.6f} | {snapshot["liquid_steamoutlet_signed_kg_s"]:.6f} | {snapshot["liquid_steamoutlet_percent_of_feed"]:.6f} | {snapshot["contact_removal_kg_s"]:.6f} |')
    lines+=['','*Carrier snapshots are fixed after each speed\'s own startup. Steam-outlet flux excludes the volume contact source; negative is outward. Outlet/feed is a reported ratio, not a qualified separator-efficiency result.*']
    lines+=['','*Rates use a common final 10 ms film-time window, with partial boundary increments weighted by overlap. During execution these are the latest available windows, not all 500 ms endpoints.*','',
            '| Qualification | Limit |','| --- | --- |','| Bulk fields | Frozen after each speed\'s own startup; constant carrier inventory and outlet flux do not establish full-model convergence |',
            '| Film solver | Alternative implicit inner residuals unavailable; not counted as passed |',
            '| Comparison | Equal-time developing-film sensitivity; full-model stationarity, whole-separator closure and timestep independence remain unqualified |']
    lines+=['','| Scaled carrier residual: final 500 startup updates | 26.81 m/s | 20.11 m/s | 32.14 m/s |',
            '| --- | ---: | ---: | ---: |']
    for name in RESIDUAL_NAMES:
        values=[f'{summaries[label]["startup_carrier_residuals"]["final_500_mean"][name]:.5g}' if label in summaries else '—' for label in ['reference','low','high']]
        lines.append('| '+name+' | '+' | '.join(values)+' |')
    lines+=['','*All seven carrier residuals cover N1581–N5080 for each available arm. Bulk equations are then frozen; there are no new carrier residuals during the long film continuation. Reported scaled means do not prove stationarity.*']
    if complete:
        geometry=np.load(BASE/'wall-thickness-views/wall-geometry.npz');vertices=geometry['vertices'];indices=np.split(geometry['connectivity'],np.cumsum(geometry['face_sizes'])[:-1]);polygons=[vertices[i] for i in indices]
        areas=np.array([.5*np.linalg.norm(np.cross(p,np.roll(p,-1,axis=0)).sum(axis=0)) for p in polygons]);display=[p[:,[0,2,1]] for p in polygons]
        upper=max(.3,math.ceil(max(s['facets']['film-thickness'].max()*1000 for s in sources.values())/.05)*.05);norm=Normalize(0,upper);cmap=plt.get_cmap('viridis')
        fig=plt.figure(figsize=(15,8));axes=[fig.add_subplot(1,3,n+1,projection='3d') for n in range(3)]
        limits=[(vertices[:,i].min(),vertices[:,i].max()) for i in [0,2,1]]
        for ax,label in zip(axes,['low','reference','high']):
            facets=sources[label]['facets'];assert np.allclose(facets['centroids'],geometry['centroids'],rtol=0,atol=1e-7)
            thickness=facets['film-thickness'];ax.add_collection3d(Poly3DCollection(display,facecolors=cmap(norm(thickness*1000)),edgecolors='none',linewidths=0,antialiased=False))
            for setter,(a,b) in zip([ax.set_xlim,ax.set_ylim,ax.set_zlim],limits):setter(a-.025*(b-a),b+.025*(b-a))
            ax.set_box_aspect([b-a for a,b in limits]);ax.view_init(elev=12,azim=-135);ax.set_proj_type('ortho');ax.set(xlabel='X (m)',ylabel='Z (m)',zlabel='Height Y (m)',title=f'{summaries[label]["nominal_speed_m_s"]:.2f} m/s\nFilm mass {summaries[label]["film_kg"]:.3f} kg');ax.grid(False)
            summaries[label]['area_at_least_0p1mm_percent']=float(100*areas[thickness>=1e-4].sum()/areas.sum())
        fig.subplots_adjust(left=.01,right=.91,top=.86,bottom=.12,wspace=.03);mapper=plt.cm.ScalarMappable(norm=norm,cmap=cmap);bar=fig.colorbar(mapper,cax=fig.add_axes([.93,.24,.014,.49]));bar.set_label('Wall-film thickness (mm)');fig.suptitle('Three inlet speeds — wall film at 500 ms',fontsize=19)
        wall=figures/'wall-film-thickness-three-speeds-500ms.png';fig.savefig(wall,dpi=180);plt.close(fig)
        lines+=['','![Wall film at three inlet speeds](figures/wall-film-thickness-three-speeds-500ms.png)','',
                '*Actual Fluent facet fields at the three preserved endpoints; same geometry, camera and colour scale; no interpolation or smoothing.*']
    (PROJECT/'results.md').write_text('\n'.join(lines)+'\n')
    record={'status':'COMPLETE_DATA_VISUAL_QA_PENDING' if complete else ('PARTIAL_PAUSED_DATA_VERIFIED' if job['status']=='PAUSED' else 'PARTIAL_RUNNING_DATA_VERIFIED'),
            'summaries':summaries,'case_selected_blocks':{k:v['selected_blocks'] for k,v in sources.items()},
            'figures':[str(p) for p in figures.glob('*.png')],'native_scaling':'Unchanged; native film-clock joins checked',
            'drainage_method':'Cumulative outflow difference / film increment; exact full-precision steps for constant batches; saved endpoints anchor variable printed clocks',
            'final_rate_window_s':.01,'claim_limit':'Developing film with frozen bulk; no stationary or full-model qualification'}
    (CAMPAIGN/'analysis-summary.json').write_text(json.dumps(record,indent=2)+'\n')
    print('SPEED_ANALYSIS',record['status'],{k:round(v['film_time_s']*1000,3) for k,v in summaries.items()})


if __name__=='__main__':main()

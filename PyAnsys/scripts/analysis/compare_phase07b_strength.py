"""Offline G2 comparison; preserve G1 outputs and label partial/failure evidence.

Pass the original S40 directory, S40-T020 directory, and S40-T100 directory.
Each new case must already have a verified terminal disposition and analysis.
"""
from pathlib import Path
import argparse
import json
import hashlib
import numpy as np
from analyze_phase07b_screen import parse_history, derive, parse_flux, parse_residuals, plt, analyze


def digest(path):
    return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('baseline',type=Path);ap.add_argument('t020',type=Path);ap.add_argument('t100',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--native-graphics',type=Path,required=True,help='Verified native Fluent export manifest; never locally render spatial fields')
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    records={};histories={};endpoints={}
    for label,tau,run in [('S40 baseline',.0024095893,a.baseline),('S40-T020',.02,a.t020),('S40-T100',.1,a.t100)]:
        m=json.loads((run/'manifest.json').read_text())
        assert m['percent']==40 and m.get('tau_s',.0024095893)==tau
        terminal_path=run/'terminal-disposition.json'
        failure=json.loads(terminal_path.read_text()) if terminal_path.exists() else None
        if failure:
            assert failure['disposition']=='NUMERICAL_FAILURE'
            recovery=json.loads((run/'recovery-sections.json').read_text())
            stage=recovery['stage'];n=recovery['iteration']
            section_dir=run/recovery.get('directory',stage+'-sections')
            end=failure['last_completed_iteration']
        else:
            assert m['status']=='HORIZON_COMPLETE_ANALYSIS_PENDING' and m['completed_iterations']==5000
            stage='final';n=end=5000;section_dir=run/'final-sections'
        summary=json.loads((run/'analysis/summary.json').read_text())
        for stream in ['history','collector_flux','residuals']:
            assert summary[stream]['complete_to_expected_end'] and summary[stream]['last_iteration']==end,(label,stream)
        assert not summary['missing_required_derived_metrics']
        h,audit=max([parse_history(p) for p in run.glob('history-*.out')],key=lambda pair:pair[1]['last_iteration'])
        d,_=derive(h);flux,_=parse_flux(run/'collector-flux.jsonl');residuals,_=parse_residuals(run/'solve.trn')
        histories[label]=(h['iteration'],d,flux,residuals)
        endpoints[label]=(run,section_dir,n,stage)
        records[label]={'tau_s':tau,'run':str(run.resolve()),'manifest':digest(run/'manifest.json'),
                        'history':audit['source'],'original_analysis':digest(run/'analysis/summary.json'),
                        'completed_iteration':end,'field_iteration':n,'field_stage':stage,
                        'disposition':failure or 'HORIZON_COMPLETE','screening_indicators':summary['declared_screening_indicators'],
                        'fixed_late_windows':summary['fixed_late_windows'],'source_lag':summary['applied_source_lag_audit']}
    # Recompute history figures into G2; preserve original case evidence.
    for label,(run,_,_,_) in endpoints.items():
        output=a.output/label.lower().replace(' ','-')
        analyze(run,output,render_sections=False)
        records[label]['g2_analysis']=digest(output/'summary.json')
    fig,axes=plt.subplots(3,1,figsize=(11,9),sharex=True,layout='constrained')
    for color,(label,(x,d,f,_)) in zip(['tab:blue','tab:orange','tab:green'],histories.items()):
        axes[0].plot(x,d['whole_water_volume'],lw=.8,color=color,label=label)
        axes[1].plot(x,d['native_applied_removal'],lw=.8,color=color,label=label)
        axes[2].plot(f['iteration'],f['delivery_kg_s'],lw=.8,color=color,label=label+' delivery')
        axes[2].plot(f['iteration'],f['escape_kg_s'],lw=.65,ls=':',color=color,label=label+' escape')
    for ax,ylabel in zip(axes,['Whole liquid volume (m³)','Applied removal (kg/s)','Collector crossing (kg/s)']):
        ax.set_ylabel(ylabel);ax.grid(alpha=.2)
    axes[0].legend();axes[2].legend(fontsize=8,ncol=2)
    axes[1].axhline(float(next(iter(histories.values()))[1]['liquid_measured_feed'][0]),color='black',ls=':',label='Liquid feed')
    axes[1].legend();axes[2].set_xlabel('Steady iteration (not physical time)')
    fig.suptitle('G2 — Does weaker removal change accumulation and liquid collection?\nRaw histories; solid collector delivery and dotted escape')
    if any(isinstance(r['disposition'],dict) for r in records.values()):
        for ax in axes[1:]:ax.set_yscale('symlog',linthresh=1)
    fig.savefig(a.output/'G2-inventory-removal.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(4,1,figsize=(11,11),sharex=True,layout='constrained')
    for label,(x,d,_,res) in histories.items():
        for ax,phase in zip(axes[:3],['liquid','vapor','mixture']):
            ax.plot(x,d[phase+'_closure_percent_feed'],lw=.8,label=label)
        worst=np.max(np.stack([v for k,v in res.items() if k!='iteration']),axis=0)
        axes[3].semilogy(res['iteration'],worst,lw=.8,label=label)
    for ax,phase in zip(axes[:3],['Liquid','Vapour','Mixture']):
        ax.set_ylabel(phase+' closure (% feed)');ax.axhspan(-1,1,color='grey',alpha=.18);ax.grid(alpha=.2)
        if any(isinstance(r['disposition'],dict) for r in records.values()):ax.set_yscale('symlog',linthresh=1)
    axes[0].legend();axes[3].axhline(1e-3,color='black',ls=':');axes[3].set_ylabel('Maximum of seven residuals')
    axes[3].set_xlabel('Steady iteration (not physical time)');axes[3].grid(alpha=.2)
    fig.suptitle('G2 — Source-inclusive closure and all-equation numerical behaviour\nApplied source counted once; individual equations retained in each case analysis')
    fig.savefig(a.output/'G2-closure-residuals.png',dpi=160);plt.close(fig)
    native=json.loads(a.native_graphics.read_text())
    assert native['status']=='COMPLETE_NATIVE_EXPORTS_QA_PASS'
    for label in records:
        entries=[v for v in native['figures'] if v['case_id']==label]
        assert len(entries)>=6 and all(v['iteration']==records[label]['field_iteration'] for v in entries)
        assert {v['plane'] for v in entries if v['field']=='phase-2-vof'}=={'y0p5','y1p5','y3p0','y5p0','x0','z0'}
        for v in entries:
            path=Path(v['local_file'])
            assert v['visual_qa']=='PASS' and v['remote_hash_matches'] is True
            assert path.is_file() and digest(path)['sha256']==v['sha256']
            assert v['range_options']['global_range'] is False and v['range_options']['auto_range'] is False
            assert [v['range_options']['minimum'],v['range_options']['maximum']]==native['shared_ranges'][v['field']]
        records[label]['native_spatial_figures']=entries
    result={'status':'G2_COMPLETE_BOUNDED_DISCOVERY','cases':records,'native_graphics_manifest':digest(a.native_graphics),'qualification':False,'figures':sorted(str(p) for p in a.output.glob('G2-*.png')),
            'rule':'Fixed full late windows only; no partial-run substitution. Native applied source counted once. Steady iteration slopes are not storage rates.'}
    (a.output/'comparison.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'output':str(a.output),'cases':list(records),'qualification':False}))


if __name__=='__main__':main()

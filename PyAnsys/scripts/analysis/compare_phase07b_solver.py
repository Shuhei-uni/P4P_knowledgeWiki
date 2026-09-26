"""Terminal E4/E5/E6 history comparison; native spatial QA is a separate required gate."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_phase07b_screen import analyze, parse_history, parse_residuals, derive, fingerprint, plt, expected_residual_equations


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('control',type=Path)
    ap.add_argument('child',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--experiment',choices=['E4','E5','E6','E7'],default='E4')
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    streams={};records={}
    labels={'E4':['SIMPLE','Coupled-Off'],'E5':['Coupled-CFL200','Coupled-CFL20'],'E6':['Coupled-CFL20','Coupled-CFL20-NPhase'],'E7':['NPhase-T020','NPhase-T100']}[a.experiment]
    for label,run in zip(labels,[a.control,a.child]):
        m=json.loads((run/'manifest.json').read_text())
        assert m['percent']==40 and m['tau_s']==(.1 if a.experiment=='E7' and run==a.child else .02)
        failure=run/'terminal-disposition.json'
        assert (m.get('completed_iterations')==5000 and m['status']=='HORIZON_COMPLETE_ANALYSIS_PENDING') or failure.exists(), 'Reconcile terminal disposition first'
        if run==a.child:
            assert m['experiment_id']==a.experiment
            assert m['numerical_treatment']['status']=='EXACT_PREDECLARED_DELTA_PASS'
            assert m['initial_field_parity']['status']=='INITIAL_PHYSICAL_FIELDS_EXACTLY_EQUAL'
            if a.experiment=='E5':
                import copy
                control=json.loads((a.control/'manifest.json').read_text())
                expected=copy.deepcopy(control['selected_controls']);expected['p_v_controls']['flow_courant_number']=20.
                assert m['selected_controls']==expected and m['selected_methods']==control['selected_methods']
                assert control['selected_controls']['p_v_controls']['flow_courant_number']==200.
            if a.experiment=='E6':
                import copy
                control=json.loads((a.control/'manifest.json').read_text())
                expected=copy.deepcopy(control['selected_methods']);expected['p_v_coupling']['solve_n_phase']=True
                assert m['selected_methods']==expected and m['selected_controls']==control['selected_controls']
                assert control['selected_methods']['p_v_coupling']['solve_n_phase'] is False
            if a.experiment=='E7':
                control=json.loads((a.control/'manifest.json').read_text())
                assert control['experiment_id']=='E6'
                assert m['source_treatment']['status']=='EXACT_TAU_ONLY_DELTA_PASS'
                assert m['source_treatment']['control_run']==control['run_id']
                for key in ['selected_methods','selected_controls','source_slots']:
                    assert m[key]==control[key]
                assert {k for k in m['definitions'] if m['definitions'][k]!=control['definitions'][k]}=={'P7bSink'}
        dest=a.output/label.lower();analyze(run,dest,render_sections=False)
        summary=json.loads((dest/'summary.json').read_text())
        for stream in ['history','collector_flux','residuals']:
            assert summary[stream]['complete_to_expected_end'], (label,stream)
        assert not summary['missing_required_derived_metrics']
        h,audit=max([parse_history(p) for p in run.glob('history-*.out')],key=lambda x:x[1]['last_iteration'])
        d,units=derive(h);res,ra=parse_residuals(run/'solve.trn')
        assert set(res)=={'iteration'} | expected_residual_equations(m)
        streams[label]=(h,d,res)
        # Preserve every scalar and every raw residual on its native coordinates.
        for suffix,data in [('scalar',h),('residual',res)]:
            keys=['iteration']+sorted(k for k in data if k!='iteration')
            np.savetxt(a.output/(label.lower()+'-'+suffix+'.csv'),np.column_stack([data[k] for k in keys]),delimiter=',',header=','.join(keys),comments='')
        records[label]={'run':str(run),'manifest':fingerprint(run/'manifest.json'),
                        'history':audit['source'],'analysis':fingerprint(dest/'summary.json'),
                        'residual_source':ra['source'],'late_windows':summary['fixed_late_windows'],
                        'indicators':summary['declared_screening_indicators'],
                        'source_lag':summary['applied_source_lag_audit'],
                        'terminal_disposition':json.loads(failure.read_text()) if failure.exists() else 'HORIZON_COMPLETE'}
    fig,axes=plt.subplots(4,1,figsize=(11,11),sharex=True,layout='constrained')
    for label,(h,d,res) in streams.items():
        x=h['iteration']
        for ax,phase in zip(axes[:3],['liquid','vapor','mixture']):
            ax.plot(x,d[phase+'_closure_percent_feed'],lw=.75,label=label)
        axes[3].plot(x,d['whole_water_volume'],lw=.8,label=label)
    for ax,phase in zip(axes[:3],['Liquid','Vapor','Mixture']):
        ax.set_ylabel(phase+' error (% feed)');ax.axhspan(-1,1,color='grey',alpha=.15);ax.set_yscale('symlog',linthresh=1)
    axes[3].set_ylabel('Liquid inventory (m³)');axes[3].set_xlabel('Steady iteration (not physical time)')
    for ax in axes:ax.grid(alpha=.2);ax.axvspan(4501,5000,color='grey',alpha=.08)
    axes[0].legend();fig.suptitle(a.experiment+' — '+('Does pressure–velocity coupling improve independent mass closure?' if a.experiment=='E4' else ('Does lower Coupled Courant improve independent mass closure?' if a.experiment=='E5' else ('Does a fivefold weaker sink improve independent mass closure?' if a.experiment=='E7' else 'Does solving all phase fractions improve independent mass closure?')))+'\nRaw histories; signed applied source counted once; shaded late window')
    fig.savefig(a.output/(a.experiment+'-F1-closure-inventory.png'),dpi=160);plt.close(fig)
    base_order=['continuity','x-velocity','y-velocity','z-velocity','k','epsilon','vf-phase-2']
    union=set().union(*(set(res)-{'iteration'} for h,d,res in streams.values()))
    equations=base_order+sorted(union-set(base_order))
    count=len(equations)+1;rows=(count+1)//2
    fig,axes=plt.subplots(rows,2,figsize=(13,3*rows),sharex=True,layout='constrained');axes=axes.ravel()
    for label,(h,d,res) in streams.items():
        for ax,eq in zip(axes,equations):
            if eq in res:ax.semilogy(res['iteration'],res[eq],lw=.7,label=label)
            else:ax.plot([],[],label=label+' — not exposed')
        axes[len(equations)].semilogy(h['iteration'],h['p7bmaximumspeed'],lw=.7,label=label)
    for ax,eq in zip(axes,equations):
        ax.set_ylabel(eq);ax.axhline(1e-3,color='black',ls=':',lw=.7)
        if any(eq not in res for h,d,res in streams.values()):ax.legend(fontsize=8)
    axes[len(equations)].set_ylabel('Maximum speed (m/s)')
    for ax in axes[:count]:ax.grid(alpha=.2);ax.axvline(2700,color='grey',ls=':',lw=.7);ax.set_xlabel('Steady iteration')
    for ax in axes[count:]:ax.set_visible(False)
    axes[0].legend()
    fig.suptitle(a.experiment+' — Raw all-equation residuals and speed excursions\nIdentical scaling options do not imply identical physical error scales')
    fig.savefig(a.output/(a.experiment+'-F2-residual-speed.png'),dpi=160);plt.close(fig)
    result={'status':'HISTORIES_COMPLETE_NATIVE_COMPARISON_PENDING','cases':records,
            'qualified':False,'figures':[str(p) for p in sorted(a.output.glob(a.experiment+'-*.png'))],
            'remaining':'Verify checkpoint pairs, diagnostic snapshots and native common-scale spatial figures; inspect images and write the experiment interpretation before declaring completion.'}
    (a.output/'comparison.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(result['status'])


if __name__=='__main__':main()

"""File-only E8 conditioning evidence; frozen phase equations cannot qualify.

Terminal use requires CONDITIONING_GATE_NOT_MET at N1000 and the matching local
terminal audit. --partial explicitly permits a saved conditioning checkpoint.
No native field replacement, live API, smoothing, interpolation or fake VF curves.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from analyze_phase07b_screen import parse_history, derive, stats
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'scripts/setup'))
from run_phase07b_mixture_startup import ACTIVE_FLOW, conditioning_gate, parse_stage_residuals

LIMIT=('Volume fraction and slip remain frozen. Phase budgets, zero or bounded '
       'inventory and low carryover cannot qualify the full Mixture model. '
       'Iteration is a solver coordinate, not physical time.')


def fp(path):
    return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def metric_stats(x,values,unit):
    result=stats(x,values,unit)
    if len(values):result['last']=float(values[-1]) if np.isfinite(values[-1]) else None
    return result


def build(run, output, *, partial=False, terminal_audit=None, checkpoint=None):
    manifest_path=run/'manifest.json'; manifest_text=manifest_path.read_text(); r=json.loads(manifest_text)
    assert r['experiment_id']=='E8'
    assert r.get('switch_iteration') is None and r.get('full_equation_iterations',0)==0, 'This analyzer is conditioning-only'
    if partial:
        assert checkpoint is not None and checkpoint in [50]+list(range(200,1001,100)), 'Partial analysis requires explicit saved checkpoint'
        end=checkpoint; scope=f'PARTIAL conditioning through N{end}'
    else:
        assert checkpoint in (None,1000)
        assert r['status']=='CONDITIONING_GATE_NOT_MET' and r['completed_iterations']==r['actual_iteration']==1000
        assert r['terminal_artifacts_verified']
        from audit_phase07b_startup import verify_iteration_accounting
        verify_iteration_accounting(r,1000)
        assert terminal_audit is not None, 'Require independent matching terminal local audit'
        audit=json.loads(terminal_audit.read_text())
        assert audit['run_id']==r['run_id'] and audit['status']=='E8_TERMINAL_LOCAL_AUDIT_PASS'
        assert audit['terminal'] and audit['controller_lock_free'] and audit['common_scalar_prefix_end']==1000
        end=1000; scope='Completed conditioning: gate not met at N1000'
    assert not output.exists(), 'Use a unique derived output directory; do not overwrite evidence'
    history_path=run/f'history-{end:05d}.out'; transcript=run/f'conditioning-native-to-{end:05d}.trn'
    history,ha=parse_history(history_path); residuals,ra=parse_stage_residuals(transcript,'conditioning',0,end)
    assert np.array_equal(history['iteration'],np.arange(1,end+1))
    assert not ha['conflicting_indices'] and not ha['nonfinite_columns'] and not ha['rejected_lines']
    assert set(residuals)=={'iteration'}|ACTIVE_FLOW
    derived,units=derive(history); x=history['iteration']
    gates=[]
    for n in range(200,end+1,100):
        ghpath=run/f'history-{n:05d}.out'; grpath=run/f'conditioning-native-to-{n:05d}.trn'
        gh,_=parse_history(ghpath); gr,_=parse_stage_residuals(grpath,'conditioning',0,n)
        gate=conditioning_gate(gh,gr,n)
        assert [g for g in r['conditioning_gates'] if g['iteration']==n]==[gate], ('Gate differs from controller',n)
        gate={**gate,'source_history':fp(ghpath),'source_residuals':fp(grpath)}
        gate['failed_requirements']=[]
        if any(v>=1e-3 for v in gate['active_residual_maxima'].values()):gate['failed_requirements'].append('active_residuals')
        if gate['mixture_closure_mean_absolute_percent_feed']>1:gate['failed_requirements'].append('native_mixture_closure')
        gate['failed_requirements'] += [k for k,v in gate['mean_changes'].items() if v['absolute_change_percent']>1]
        gates.append(gate)
    if not partial: assert len(gates)==9 and all(not g['passed'] for g in gates)
    lag=float(np.max(np.abs(derived['native_applied_removal'][1:]-derived['current_expression_removal'][:-1])))
    assert lag<=1e-9
    windows={}
    bounds=[(1,end)] + ([(end-199,end-100),(end-99,end)] if end>=200 else [])
    for lo,hi in bounds:
        mask=(x>=lo)&(x<=hi); rm=(residuals['iteration']>=lo)&(residuals['iteration']<=hi)
        windows[f'{lo}-{hi}']={'metrics':{k:metric_stats(x[mask],v[mask],units[k]) for k,v in derived.items()},
                               'active_residuals':{k:metric_stats(residuals['iteration'][rm],residuals[k][rm],'scaled residual') for k in sorted(ACTIVE_FLOW)}}
    output.mkdir(parents=True)
    (output/'manifest-at-analysis.json').write_text(manifest_text)
    summary={'experiment_id':'E8','run_id':r['run_id'],'scope':scope,'partial':partial,'end_iteration':end,
             'generated_utc':datetime.now(timezone.utc).isoformat(),'status':'PARTIAL_CONDITIONING_ANALYSIS' if partial else 'CONDITIONING_TERMINAL_GATE_VERIFIED',
             'sources':{'manifest_snapshot':fp(output/'manifest-at-analysis.json'),'history':fp(history_path),'residuals':fp(transcript)},
             'history_audit':ha,'residual_audit':ra,'active_equations':sorted(ACTIVE_FLOW),'gates':gates,'windows':windows,
             'source_lag':{'pairs':end-1,'max_absolute_error_kg_s':lag},'phase_equations_solved':False,'qualified':False,
             'full_model_endpoint_tested':False,'claim_limit':LIMIT,
             'observation':('All nine predeclared conditioning checkpoints failed; VF/slip were not restored.' if not partial else 'Saved conditioning prefix only; terminal disposition is pending.'),
             'interpretation':('The documented initially-converged-flow prerequisite was not reached within this investigator-selected 1000-iteration budget.' if not partial else 'No terminal inference from a partial conditioning prefix.'),
             'figure_status':'CREATED_VISUAL_QA_PENDING'}
    if terminal_audit:summary['sources']['terminal_audit']=fp(terminal_audit)
    columns=['iteration','passed','continuity_max','x_velocity_max','y_velocity_max','z_velocity_max','k_max','epsilon_max',
             'mixture_closure_meanabs_percent','liquid_drop_mean_change_percent','steam_drop_mean_change_percent','max_speed_mean_change_percent','failed_requirements']
    with (output/'conditioning-gates.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=columns);writer.writeheader()
        for g in gates:
            row={'iteration':g['iteration'],'passed':g['passed'],'mixture_closure_meanabs_percent':g['mixture_closure_mean_absolute_percent_feed'],
                 'liquid_drop_mean_change_percent':g['mean_changes']['liquid_inlet_pressure_drop']['absolute_change_percent'],
                 'steam_drop_mean_change_percent':g['mean_changes']['steam_inlet_pressure_drop']['absolute_change_percent'],
                 'max_speed_mean_change_percent':g['mean_changes']['maximum_mixture_speed']['absolute_change_percent'],
                 'failed_requirements':'; '.join(g['failed_requirements'])}
            row.update({k.replace('-','_')+'_max':v for k,v in g['active_residual_maxima'].items()});writer.writerow(row)
    table=['# E8 conditioning gate evidence', '', scope, '',
           '| End N | Windows (earlier / latest) | Worst active residual | Mixture mean-absolute closure (%) | Liquid / steam pressure mean changes (%) | Speed mean change (%) | Gate |',
           '|---:|---|---:|---:|---:|---:|---|']
    for g in gates:
        changes=g['mean_changes'];w=g['windows']
        table.append(f"| {g['iteration']} | {w[0][0]}–{w[0][1]} / {w[1][0]}–{w[1][1]} | {max(g['active_residual_maxima'].values()):.6g} | {g['mixture_closure_mean_absolute_percent_feed']:.6g} | {changes['liquid_inlet_pressure_drop']['absolute_change_percent']:.6g} / {changes['steam_inlet_pressure_drop']['absolute_change_percent']:.6g} | {changes['maximum_mixture_speed']['absolute_change_percent']:.6g} | {'PASS' if g['passed'] else 'FAIL'} |")
    table += ['', 'Require every active residual <1e-3, and mixture closure plus each mean change ≤1%. Exact means, all six residual maxima and source hashes are in summary.json; individual residual maxima are also in the CSV.', '', LIMIT,'']
    (output/'conditioning-gates.md').write_text('\n'.join(table))
    figure_paths=figures(output,x,derived,residuals,scope,end)
    summary['figures']=[{'file':fp(p),'caption':caption,'visual_qa':'PENDING'} for p,caption in figure_paths]
    (output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    return summary


def figures(output,x,d,residuals,scope,end):
    plt.rcParams.update({'font.size':10,'axes.labelsize':11,'axes.titlesize':12,'legend.fontsize':9,'savefig.dpi':180})
    colors={'liquid':'#0072b2','vapor':'#d55e00','mixture':'#222222'}
    def prepare(title):
        fig,axes=plt.subplots(3,1,figsize=(11.5,10),sharex=True)
        fig.suptitle(title+'\n'+scope,fontsize=14,y=.98)
        for ax in axes:
            ax.grid(alpha=.2);ax.set_xlim(1,end)
            if end>=200:
                ax.axvspan(end-199,end-100,color='#999999',alpha=.09)
                ax.axvspan(end-99,end,color='#56b4e9',alpha=.11)
        axes[-1].set_xlabel('Native steady-solver iteration')
        fig.subplots_adjust(top=.9,bottom=.12,left=.12,right=.96,hspace=.30)
        fig.text(.12,.05,'VF and slip frozen throughout; phase budgets/inventory cannot validate the full model.\nRaw traces; no smoothing. Shading: preceding 100 (gray), latest 100 (blue), where available.',fontsize=9)
        return fig,axes
    fig,axes=prepare('E8-F1 · Independent budgets, inventory and removal')
    for phase in ['liquid','vapor','mixture']:
        axes[0].plot(x,d[phase+'_closure_percent_feed'],label=phase.title()+' (native mixture)' if phase=='mixture' else phase.title(),color=colors[phase],lw=1.)
    axes[0].axhline(0,color='#777777',lw=.8);axes[0].axhspan(-1,1,color='#009e73',alpha=.12)
    axes[0].set_ylabel('Signed budget / feed (%)');axes[0].set_title('Boundary flux + applied source once; phase-specific or total feed denominator')
    axes[0].legend(ncol=3,loc='best')
    for key,label,style in [('whole_water_volume','Whole','-'),('above_water_volume','Above collector','--'),('collector_water_volume','Collector',':')]:
        axes[1].plot(x,d[key],label=label,linestyle=style,lw=1.5)
    axes[1].set_ylabel('Native liquid volume (m³)');axes[1].set_title('Frozen-fraction inventory is a diagnostic, not evidence of bounded full-model inventory');axes[1].legend(ncol=3)
    axes[2].plot(x,d['native_applied_removal'],label='Native applied removal',color='#222222',lw=1.4)
    axes[2].plot(x,d['current_expression_removal'],label='Current-field expression removal',color='#cc79a7',ls='--',lw=1.2)
    axes[2].set_ylabel('Removal (kg/s)');axes[2].set_title('Applied source and recomputed expression retained separately');axes[2].legend(ncol=2)
    p1=output/'E8-F1-conditioning-budgets.png';fig.savefig(p1);plt.close(fig)
    fig,axes=prepare('E8-F2 · Active equations and conditioning stability')
    all_residuals=np.concatenate([residuals[k] for k in sorted(ACTIVE_FLOW)])
    assert np.all(all_residuals>=0), 'Negative native residual'
    if np.all(all_residuals>0): axes[0].set_yscale('log')
    else:
        positive=all_residuals[all_residuals>0]
        linear=max(float(positive.min())*.1 if len(positive) else 1e-12,1e-15)
        axes[0].set_yscale('symlog',linthresh=linear)
        axes[0].text(.99,.02,f'Zeros retained; linear scale below {linear:.2g}',transform=axes[0].transAxes,ha='right',fontsize=8)
    for key in sorted(ACTIVE_FLOW):
        axes[0].plot(residuals['iteration'],residuals[key],label=key,lw=1.)
    axes[0].axhline(1e-3,color='#222222',ls='--',lw=.9,label='strict < 10⁻³ gate')
    axes[0].set_ylabel('Native scaled residual');axes[0].set_title('Six solved equations only; inactive VF curves are not generated');axes[0].legend(ncol=4,fontsize=8)
    axes[1].plot(x,d['liquid_inlet_pressure_drop'],label='Liquid inlet − outlet',color='#0072b2')
    axes[1].plot(x,d['steam_inlet_pressure_drop'],label='Steam inlet − outlet',color='#d55e00')
    axes[1].set_ylabel('Pressure drop (Pa)');axes[1].set_title('Gate compares adjacent 100-iteration means with a 100 Pa denominator floor');axes[1].legend(ncol=2)
    axes[2].plot(x,d['maximum_mixture_speed'],color='#222222',lw=1.)
    axes[2].set_ylabel('Maximum speed (m/s)');axes[2].set_title('Native mixture maximum; gate compares adjacent means with a 1 m/s floor')
    p2=output/'E8-F2-conditioning-residuals.png';fig.savefig(p2);plt.close(fig)
    return [(p1,'Raw source-inclusive phase/native-mixture budgets, regional normalized-native liquid inventory and removal during frozen conditioning. No full-model conservation or inventory qualification.'),
            (p2,'Actual six-equation residuals, both inlet-to-outlet pressure drops and native maximum speed. Gate decisions use all individual latest-100 residuals and adjacent-window means, not visual flattening.')]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('run',type=Path);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--partial',action='store_true');ap.add_argument('--checkpoint',type=int);ap.add_argument('--terminal-audit',type=Path)
    a=ap.parse_args();s=build(a.run,a.output,partial=a.partial,checkpoint=a.checkpoint,terminal_audit=a.terminal_audit)
    print(json.dumps({'status':s['status'],'run_id':s['run_id'],'end_iteration':s['end_iteration'],'output':str(a.output)}))


if __name__=='__main__':main()

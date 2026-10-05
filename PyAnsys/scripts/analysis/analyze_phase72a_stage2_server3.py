"""Plot the N45606 aggressive continuation and publish its bounded evidence."""
from pathlib import Path
import csv
import json
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'output/phase72a-stage2-server3/20261005'
RECORD = ROOT.parent / 'Project/experiments/phase-07-2a-wall-liquid-routing/stage-02-combined-ewf-roughness/aggressive-server3'


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant',choices=['aggressive','moderate'],default='aggressive')
    args=parser.parse_args()
    if args.variant=='moderate':
        OUT=OUT/'moderate-restart'
    m=json.loads((OUT/'run-manifest.json').read_text())
    if not m['blocks']:
        raise RuntimeError('No verified solve evidence')
    reports=json.loads((OUT/'report-histories.json').read_text())
    h={name:dict(zip(v['iterations'],v['values'])) for name,v in reports.items()}
    clocks,inner={},{}
    for b in m['blocks']:
        a,z=b['native_start'],b['native_end']
        clocks.update({int(k):v for k,v in json.loads((OUT/f'clocks-N{a}-N{z}.json').read_text()).items()})
        inner.update({int(k):v for k,v in json.loads((OUT/f'film-residuals-N{a}-N{z}.json').read_text()).items()})
    ids=sorted(clocks)
    assert ids==list(range(45607,m['verified_native_end']+1))
    clock0=m['parent_film_clock_s']
    t=np.array([clocks[n][0] for n in ids])
    dt=np.diff(np.r_[clock0,t])
    mass=np.array([h['p72a-e2.7-ewf-film-mass-total'][n] for n in ids])
    drain=np.array([h['p72a-e2.7-ewf-outflow-mass-total'][n] for n in ids])
    acc=np.array([h['p72a-e2.7-ewf-secondary-phase-mass-total'][n] for n in ids])
    parent=json.loads((OUT/'prepared-reopen.json').read_text())['state']['readback']['fields']
    drainage=np.diff(np.r_[parent['p72a-e2.7-ewf-outflow-mass-total'][0],drain])/dt
    storage=np.diff(np.r_[parent['p72a-e2.7-ewf-film-mass-total'][0],mass])/dt
    with (OUT/'film-history.csv').open('w') as f:
        w=csv.writer(f)
        w.writerow(['native_iteration','native_film_clock_s','added_since_N45606_ms','film_mass_kg','accretion_kg_s','drainage_kg_s','storage_kg_s','printed_step_us','film_cfl','h_final','u_final','v_final'])
        for j,n in enumerate(ids):
            w.writerow([n,t[j],(t[j]-clock0)*1000,mass[j],acc[j],drainage[j],storage[j],clocks[n][1]*1e6,clocks[n][2],*inner[n][-1][1:]])
    x=(t-clock0)*1000
    fig,axs=plt.subplots(4,1,figsize=(10,12),sharex=True,constrained_layout=True)
    axs[0].plot(np.r_[0,x],np.r_[parent['p72a-e2.7-ewf-film-mass-total'][0],mass],color='#336699')
    axs[0].set_ylabel('Film inventory (kg)')
    for y,label,color in [(acc,'Accretion','#336699'),(drainage,'Drainage','#39764d'),(storage,'Storage','#ac6b29')]:
        axs[1].plot(x,y,label=label,color=color,lw=.65,alpha=.7)
    axs[1].set_ylabel('Film rate (kg/s)');axs[1].legend(loc='best')
    axs[2].plot(x,[clocks[n][1]*1e6 for n in ids],label='Accepted step',color='#336699')
    axs[2].set_ylabel('Film timestep (µs)')
    right=axs[2].twinx();right.plot(x,[clocks[n][2] for n in ids],color='#ac6b29',lw=.8,label='CFL');right.set_ylabel('Film CFL')
    for k,label in enumerate(['h','u','v'],1):
        axs[3].semilogy(x,[max(inner[n][-1][k],1e-30) for n in ids],label=label,lw=.65)
    axs[3].axhline(1e-5,color='#777777',ls=':',label='Recorded stop value')
    axs[3].set_ylabel('Final EWF residual');axs[3].legend(loc='best')
    axs[3].set_xlabel('Film time added after N45606 (ms)')
    for ax in axs:
        ax.grid(alpha=.2)
    for repair in m.get('numerical_repairs',[]):
        n=repair['native_iteration']
        mark=(clocks[n][0]-clock0)*1000
        label=', '.join(f'{k}={v}' for k,v in repair['delta'].items())
        for ax in axs:
            ax.axvline(mark,color='#666666',ls='--',lw=.7)
        axs[0].annotate(label,(mark,float(np.interp(mark,x,mass))),xytext=(4,8),textcoords='offset points',fontsize=8)
    controls=m['controlled_delta']
    fig.suptitle(f"Stage 2 N45606 → N{ids[-1]} on Server 3\nCurrent adaptive target {controls['courant-number']}; growth {controls['adapt-tstp-inc']}; raw histories",fontsize=13)
    RECORD.mkdir(parents=True,exist_ok=True)
    fig.savefig(OUT/'film-convergence.png',dpi=160)
    fig.savefig(RECORD/'film-convergence.png',dpi=160)
    plt.close(fig)
    latest=m['blocks'][-1]
    elapsed=m['blocks'][-1]['native_film_clock_s']-clock0
    gain=mass[-1]-parent['p72a-e2.7-ewf-film-mass-total'][0]
    lost=drain[-1]-parent['p72a-e2.7-ewf-outflow-mass-total'][0]
    integrated=float(np.sum(acc*dt))
    summary={'native_start':45606,'native_end':ids[-1],'updates':len(ids),'added_film_time_s':elapsed,
             'overall_storage_kg_s':gain/elapsed,'overall_ledger_error_percent':100*abs(gain+lost-integrated)/integrated,
             'latest':latest,'native_report_count':len(h),'film_residual_updates':len(inner),
             'stationarity':'UNQUALIFIED; apply sustained-window screen and numerical adequacy',
             'time_precision':'Endpoint exact; intermediate printed clocks rounded to approximately 0.05 microseconds'}
    (OUT/'analysis-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    rows=[('Status',m['status']),('Verified native endpoint',f'N{ids[-1]}'),('Additional updates',str(len(ids))),
          ('Film time added after N45606',f'{elapsed*1000:.6f} ms'),('Total corrected-restart added film time',f"{latest['corrected_restart_added_time_s']*1000:.6f} ms"),
          ('Accepted final film step',f"{latest['actual_final_step_s']*1e6:.6f} µs"),('Film inventory',f'{mass[-1]:.6f} kg'),
          ('Last-window accretion',f"{latest['accretion_kg_s']:.6f} kg/s"),('Last-window drainage',f"{latest['drainage_kg_s']:.6f} kg/s"),
          ('Last-window storage',f"{latest['storage_kg_s']:.6f} kg/s"),('Last-window drainage deficit',f"{latest['drainage_deficit_percent']:.6f}%"),
          ('Overall film ledger error',f"{summary['overall_ledger_error_percent']:.6f}%"),('Maximum thickness in last window',f"{latest['maximum_thickness_m']*1000:.6f} mm"),
          ('Peak CFL in last window',f"{latest['peak_film_cfl']:.6f}"),('Last-window final EWF residual above 1',f"{latest['film_final_residual_above_1_updates']} / {latest['updates']} updates"),
          ('Last-window updates meeting the film stop value',f"{latest['film_all_final_residuals_below_1e5_minus_percent']:.2f}%"),
          ('Saved-endpoint reopen',m.get('final_reopen','MISSING')),('Steady film','Not qualified by this record')]
    text='# Stage 2 — Server 3 aggressive continuation result\n\n| Measure | Verified evidence |\n| --- | --- |\n'
    text+=''.join(f'| {k} | {v} |\n' for k,v in rows)
    text+='\n![Film continuation histories](film-convergence.png)\n\nNative reports and final EWF subiteration residuals; rates use successive cumulative mass and film-clock differences. Intermediate clocks are rounded.\n\n'
    text+='| Evidence / limit | Record |\n| --- | --- |\n'
    text+='| Controlled delta and parent | [Setup](setup.md) |\n'
    text+='| Machine state and paired endpoint hashes | [Run manifest](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/run-manifest.json) |\n'
    text+='| Native histories and quantitative summary | [Analysis summary](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/analysis-summary.json) |\n'
    text+='| Film rates and residuals | [CSV](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/film-history.csv) |\n'
    text+='| Comparison limit | Server transfer can change residual normalization; a smaller scaled residual alone cannot prove improvement |\n'
    text+='| Implicit-film subiteration control | [Fluent 2025 R2 user guide §30.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_eqns.html) |\n'
    for repair in m.get('numerical_repairs',[]):
        text+=f"| Verified numerical change at N{repair['native_iteration']} | {repair['delta']}; paired reopen {repair['reopen']} |\n"
    text+='| Accounting limit | Film ledger only; steady carrier pseudo-time is not physical film time |\n'
    text+='| Scientific limit | No whole-separator closure, timestep independence or physical validation |\n'
    if args.variant=='moderate':
        text=text.replace('phase72a-stage2-server3/20261005/','phase72a-stage2-server3/20261005/moderate-restart/')
    if m.get('excluded_probe_manifest'):
        text+='| Excluded larger-step branch | [Preserved aggressive-probe evidence](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/analysis-summary.json); N45906 is not the field parent of this restart |\n'
    text+='| Next action | Continue stable batches to the bounded horizon; repair severe inner-film failures before longer compute |\n'
    (RECORD/'results.md').write_text(text)
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()

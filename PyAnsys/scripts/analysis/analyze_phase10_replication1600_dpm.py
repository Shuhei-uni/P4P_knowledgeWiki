"""Audit Final-column particle mass and compare M04 to historical Case 4."""
from pathlib import Path
import csv
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'PyAnsys/src'))
from pyansys_fluent.dpm_reports import parse_mass_transfer_rows,parse_fate_rows,_MASS_ROW_RE

OUT=ROOT/'PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04'
LIMIT=int(sys.argv[sys.argv.index('--max-tracking-steps')+1]) if '--max-tracking-steps' in sys.argv else None
DEST=OUT/('DPM-evidence' if LIMIT is None else 'DPM-limit'+str(LIMIT)+'-evidence')
TERMINAL={'escaped','trapped','incomplete','aborted','evaporated','removed','absorbed'}


def plot_summary(summary):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    old=summary.get('original_10000_step_M04_mass_kg_s',summary['historical_rounded_mass_kg_s'])
    new=summary['aggregate']['final_mass_kg_s']
    feed=summary['aggregate']['injected_kg_s']
    names=['Historical spiral','M04'] if LIMIT is None else ['M04: 10,000 steps',f'M04: {LIMIT:,} steps']
    fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
    escape=[old['escaped'],new['escaped']]
    axes[0].bar(names,escape,color=['#8b96a3','#276e9d']);axes[0].set_ylabel('Escaped mass flow (kg/s)')
    axes[0].set_ylim(0,max(escape)*1.22)
    for i,value in enumerate(escape):axes[0].text(i,value,f'{value:.5f}',ha='center',va='bottom')
    trap=[old['trapped']/feed*100,new['trapped']/feed*100]
    incomplete=[old['incomplete']/feed*100,new['incomplete']/feed*100]
    axes[1].bar(names,trap,label='Trapped',color='#276e9d')
    axes[1].bar(names,incomplete,bottom=trap,label='Incomplete',color='#e5ae49')
    axes[1].set_ylim(0,106);axes[1].set_ylabel('Injected particle mass (%)')
    axes[1].legend(frameon=False,loc='upper center',ncol=2,bbox_to_anchor=(0.5,1.2))
    for i,(a,b) in enumerate(zip(trap,incomplete)):
        axes[1].text(i,a/2,f'{a:.2f}%',ha='center',va='center',color='white')
        axes[1].text(i,a+b/2,f'{b:.2f}%',ha='center',va='center',fontsize=9)
    for ax in axes:
        ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    title='Spiral Case 4, 1600 kJ/kg: particle fates at carrier N1500' if LIMIT is None else 'M04 Case 4: tracking-limit sensitivity on unchanged N1500 fields'
    fig.suptitle(title,fontsize=12)
    fig.savefig(DEST/'case4-dpm-comparison.png',dpi=170);plt.close(fig)


def half_unit(token):
    mantissa,exponent=(token.lower().split('e')+[0])[:2] if 'e' in token.lower() else (token,0)
    decimals=len(mantissa.split('.')[1]) if '.' in mantissa else 0
    return 0.5*10**(int(exponent)-decimals)


def audit_report(text,injected):
    assert 'Mass Transfer Summary' in text and re.search(r'Initial\s+Final\s+Change',text)
    assert 'Mass Flow (kg/s)' in text
    mass=parse_mass_transfer_rows(text);counts=parse_fate_rows(text)
    assert mass and counts,'Missing fresh fate mass/count rows'
    rows=[r for r in mass if r['fate']!='net'];net=[r for r in mass if r['fate']=='net']
    assert len(net)<=1 and all(r['fate'] in TERMINAL for r in rows),mass
    if not net:
        # Fluent omits Net when an injection has only one terminal fate/row.
        # Accept only this observed format, with an independently matching
        # count table and injected-mass closure still required below.
        assert len(rows)==len(counts)==1 and rows[0]['fate']==counts[0]['fate'],mass
    totals={f:sum(r['final_kg_s'] for r in rows if r['fate']==f) for f in TERMINAL}
    fate_count={f:sum(r['count'] for r in counts if r['fate']==f) for f in TERMINAL}
    count_total=sum(fate_count.values());assert count_total>0
    section=text.split('Mass Transfer Summary',1)[1]
    tokens=[m.group('final') for line in section.splitlines() if (m:=_MASS_ROW_RE.match(line.rstrip())) and m.group('fate').strip().lower()!='net']
    roundoff=sum(half_unit(token) for token in tokens)+1e-9
    error=sum(totals.values())-injected
    assert abs(error)<=roundoff,(injected,totals,error,roundoff)
    if net:
        assert abs(net[0]['final_kg_s']-sum(totals.values()))<=roundoff+half_unit(next(m.group('final') for line in section.splitlines() if (m:=_MASS_ROW_RE.match(line.rstrip())) and m.group('fate').strip().lower()=='net'))
    return {'injected_kg_s':injected,'final_mass_kg_s':totals,'terminal_counts':fate_count,'tracked_count':count_total,
            'mass_error_kg_s':error,'printed_roundoff_bound_kg_s':roundoff,'mass_accounting_verified':True,
            'zone_rows':rows,'count_rows':counts,'net_row_present':bool(net)}


def main():
    manifest=json.loads((DEST/'raw/manifest.json').read_text())
    expected=json.loads((OUT/'spiral-reference/exact-injection-readbacks.json').read_text())
    assert manifest['DPM_completed_updates']==manifest['DPM_update_dispatches']==1
    assert manifest['solved_updates']==0 and manifest['strict_reopen_verified'] and manifest['carrier_reports_unchanged']
    results={}
    for name,definition in expected.items():
        text=(DEST/'raw'/manifest['report_files'][name].replace('\\','/').rsplit('/',1)[-1]).read_text()
        results[name]=audit_report(text,definition['initial_values']['mass_flow_rate']['total_flow_rate'])
    total=sum(r['injected_kg_s'] for r in results.values())
    aggregate=audit_report((DEST/'raw/DPM-aggregate.txt').read_text(),total)
    for fate in TERMINAL:
        summed=sum(r['final_mass_kg_s'][fate] for r in results.values())
        tolerance=aggregate['printed_roundoff_bound_kg_s']+sum(r['printed_roundoff_bound_kg_s'] for r in results.values())
        assert abs(summed-aggregate['final_mass_kg_s'][fate])<=tolerance
    assert sum(r['tracked_count'] for r in results.values())==aggregate['tracked_count']
    transcript=(DEST/'raw/DPM-tracking.trn').read_text()
    tracked=re.findall(r'number tracked\s*=\s*(\d+)',transcript)
    assert tracked and int(tracked[0])==aggregate['tracked_count'],tracked
    historical=json.loads((OUT/'spiral-reference/raw/case_4_1600_manifest.json').read_text())
    # Direct preserved aggregate values are rounded by Fluent; keep them as such.
    old={fate:float(historical['case_summary'][fate+'_kgs']) for fate in ['escaped','trapped','incomplete']}
    summary={'status':'DPM_COMPLETE_MASS_ACCOUNTING_VERIFIED_CARRIER_UNQUALIFIED','carrier_iteration':1500,
             'carrier_updates':0,'DPM_completed_updates':1,'injection_count':9,'aggregate':aggregate,'injections':results,
             'historical_rounded_mass_kg_s':old,'tracking_seconds':manifest['tracking_seconds'],
             'comparison_limits':manifest['source_limits']+['Particle mass uses the labelled Final column, never count fractions. Incomplete trajectories remain unresolved. Printed mass precision bounds accounting verification.']}
    if LIMIT is not None:
        assert manifest['settings_readback']['models']['discrete_phase']['tracking']['max_num_steps']==LIMIT
        summary['tracking_max_num_steps']=LIMIT
        original=json.loads((OUT/'DPM-evidence/summary.json').read_text())['aggregate']
        summary['original_10000_step_M04_mass_kg_s']=original['final_mass_kg_s']
        summary['incomplete_mass_reduction_percent']=100*(1-aggregate['final_mass_kg_s']['incomplete']/original['final_mass_kg_s']['incomplete'])
        def incomplete_time(item):
            row=next((r for r in item['count_rows'] if r['fate']=='incomplete'),None)
            return row['elapsed_time_s'] if row else None
        summary['incomplete_elapsed_time_comparison_s']={'10000_steps':incomplete_time(original),str(LIMIT)+'_steps':incomplete_time(aggregate)}
        summary['same_parcel_count_as_10000']=aggregate['tracked_count']==original['tracked_count']
        assert summary['same_parcel_count_as_10000']
    (DEST/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    plot_summary(summary)
    with (DEST/'injection-fates.csv').open('w',newline='') as file:
        columns=['injection','diameter_um','injected_kg_s','escaped_kg_s','trapped_kg_s','incomplete_kg_s','aborted_kg_s','tracked_count','mass_error_kg_s']
        writer=csv.DictWriter(file,fieldnames=columns);writer.writeheader()
        for name,r in results.items():
            writer.writerow({'injection':name,'diameter_um':expected[name]['initial_values']['particle_size']['diameter']*1e6,
                'injected_kg_s':r['injected_kg_s'],**{f+'_kg_s':r['final_mass_kg_s'][f] for f in ['escaped','trapped','incomplete','aborted']},
                'tracked_count':r['tracked_count'],'mass_error_kg_s':r['mass_error_kg_s']})
    print(json.dumps({k:summary[k] for k in ['status','tracking_seconds','carrier_updates','DPM_completed_updates']}))
    print(json.dumps({'M04_final_mass_kg_s':aggregate['final_mass_kg_s'],'tracked_count':aggregate['tracked_count'],'historical_rounded_mass_kg_s':old}))


if __name__=='__main__':main()

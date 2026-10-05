"""Audit the supplied-mesh startup against the completed 60k recipe."""
from pathlib import Path
import json
import re
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/analysis'))
from plot_phase72a_endpoint_lineage import ROW,SUB,NAMES,out_file
OUT=ROOT/'output/phase72a-stage3-slit154k-server3/20261005'
REF=ROOT/'output/phase72a-stage3-early-ewf-server1/20261005'
PROJECT=ROOT.parent/'Project/experiments/phase-07-2a-wall-liquid-routing/stage-03-shortened-reconstruction/early-ewf-startup/slit154k'
FILM=re.compile(r'Film time = ([\deE.+-]+) with timestep = ([\deE.+-]+), \(max_cfl: ([\deE.+-]+)\)')


def main():
    m=json.loads((OUT/'run-manifest.json').read_text())
    assert m['verified_native_end']==m['native_target'] and m['final_reopen']=='PASS'
    start=m['native_start'];end=m['native_target'];ids=list(range(start+1,end+1))
    records=json.loads((OUT/'final-histories.json').read_text());h={}
    for name,record in records.items():
        native=out_file(OUT/f'final-{name}.out')
        assert set(ids).issubset(native),name
        array=np.array([native[i] for i in ids]);assert np.isfinite(array).all(),name
        cached=dict(zip(record['iterations'],record['values']))
        assert np.array_equal(array,[cached[i] for i in ids]),name
        h[name]=array
    residuals,film,clocks={},{},{}
    discarded_recovery_frames=[]
    for filename in m.get('transcript_files',['smoke-transcript.txt','run-transcript.txt']):
        pending=[];clock=None
        for line in (OUT/filename).read_text().splitlines():
            found=SUB.search(line)
            if found:pending.append([int(found[1]),*[float(v) for v in found.groups()[1:]]])
            found=FILM.search(line)
            if found:clock=[float(v) for v in found.groups()]
            found=ROW.match(line)
            if found:
                n=int(found[1]);value=[float(v) for v in found.groups()[1:]]
                if filename.startswith('recovered-') and clock and not np.isclose(clock[0],(n-start)*1e-6,atol=1e-12,rtol=0):
                    # The first reattached stream frame can contain buffered
                    # pre-disconnection film text beside a current carrier row.
                    discarded_recovery_frames.append({'file':filename,'iteration':n,'film_clock':clock})
                    pending=[];clock=None
                    continue
                if n in residuals:assert residuals[n]==value
                residuals[n]=value
                if pending:film[n]={'last':pending[-1][1:],'subiterations':pending[-1][0]}
                if clock:clocks[n]=clock
                pending=[];clock=None
    missing={name:sorted(set(ids)-set(signal)) for name,signal in [('carrier',residuals),('film_inner',film),('film_clock',clocks)]}
    # A controller transport failure loses streamed text while native reports
    # can remain complete. Preserve those gaps; never invent residual samples.
    assert not any(start+500<i<=start+2500 for absent in missing.values() for i in absent), 'Ramp evidence incomplete'
    observed_clocks=[i for i in ids if i in clocks]
    assert np.allclose([clocks[i][1] for i in observed_clocks],1e-6,atol=1e-15,rtol=0)
    assert np.allclose([clocks[i][0] for i in observed_clocks],[(i-start)*1e-6 for i in observed_clocks],atol=1e-12,rtol=0)
    final_clock=json.loads((OUT/'final-reopen.json').read_text())['film_solution_state']['film_elapsed_time']
    assert np.isclose(final_clock,3500e-6,atol=1e-12,rtol=0)
    for name,obj in [('carrier-residuals',residuals),('film-residuals',film),('film-clocks',clocks)]:
        (OUT/f'{name}.json').write_text(json.dumps(obj,indent=2)+'\n')
    reference=json.loads((REF/'final-histories.json').read_text())
    rid=list(range(1581,5081));rh={name:np.array([dict(zip(v['iterations'],v['values']))[i] for i in rid]) for name,v in reference.items()}
    rc=json.loads((REF/'carrier-residuals.json').read_text())
    continuity=np.array([residuals[i][0] if i in residuals else np.nan for i in ids]);ref_cont=np.array([rc[str(i)][0] for i in rid])
    combined=h['v2-total-liquid-mass']+h['p72a-e2.7-ewf-film-mass-total']
    ref_combined=rh['v2-total-liquid-mass']+rh['p72a-e2.7-ewf-film-mass-total']
    carry=-h['v2-flux-phase2-steamoutlet'];ref_carry=-rh['v2-flux-phase2-steamoutlet']
    ramp=slice(500,2500);tail=slice(3000,3500)
    def stats(values):
        observed=values[np.isfinite(values)];complete=len(observed)==len(values)
        return {'peak':float(observed.max()) if complete else None,
                'p95':float(np.percentile(observed,95)) if complete else None,
                'mean':float(observed.mean()) if complete else None,
                'end':float(values[-1]) if np.isfinite(values[-1]) else None,
                'observed_count':len(observed),'expected_count':len(values)}
    comparison={name:{'reference_ramp':stats(a[ramp]),'slit_ramp':stats(b[ramp]),'reference_final500':stats(a[tail]),'slit_final500':stats(b[tail])}
                for name,a,b in [('continuity',ref_cont,continuity),('combined_liquid_kg',ref_combined,combined),('outward_liquid_kg_s',ref_carry,carry)]}
    failed=[i for i in ids if i in film and max(film[i]['last'])>1e-5]
    source_error=np.max(abs(h['v2-applied-absorber']+h['p72-contact-removal']))
    blocks=[v for v in m['blocks'] if v['stage']=='ramp'];assert len(blocks)==200
    for j,block in enumerate(blocks):
        assert block['native_start']==start+500+j*10 and block['native_end']==start+500+(j+1)*10
        assert np.isclose(block['feed']['multiplier'],.25+.75*j*10/2000,rtol=0,atol=1e-12)
    assert m['blocks'][-1]['feed']['multiplier']==1.
    summary={'status':'COMPLETE','native_start':start,'native_end':end,'updates':3500,'report_count':len(h),
             'ramp_schedule':'PASS_200_EXACT_BLOCKS','comparison':comparison,'film_inner_failed_updates':failed,
             'ramp_film_inner_failed_updates':[i for i in failed if start+500<i<=start+2500],
             'max_source_tracking_error_kg_s':float(source_error),'mapped_initial_bulk_liquid_kg':m['mapped_bulk_liquid_mass_kg'],
             'reference_initial_bulk_liquid_kg':31.35713621088837,'final_bulk_liquid_kg':float(h['v2-total-liquid-mass'][-1]),
             'final_film_kg':float(h['p72a-e2.7-ewf-film-mass-total'][-1]),'final_liquid_carryover_kg_s':float(carry[-1]),
             'film_elapsed_time_s':final_clock,'transcript_missing_updates':missing,
             'discarded_misaligned_recovery_frames':discarded_recovery_frames,
             'film_inner_observed_updates':len(ids)-len(missing['film_inner']),
             'limitations':['Geometry and mesh change together','Native A interpolation is not conservative field identity','No stationary film or physical validation','Check residual normalizers before raw residual-ratio claims']}
    if any(missing.values()):
        summary['limitations'].append('Connection timeout lost part of full-feed residual transcript; film failures are observed counts and final-500 continuity comparison is unavailable')
    (OUT/'analysis-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    figdir=PROJECT/'figures';figdir.mkdir(parents=True,exist_ok=True)
    x=np.arange(1,3501)
    fig,axs=plt.subplots(3,1,figsize=(10,9),sharex=True)
    for ax,a,b,label in zip(axs,[ref_cont,ref_combined,ref_carry],[continuity,combined,carry],['Continuity residual','Bulk + film liquid (kg)','Outward liquid (kg/s)']):
        ax.plot(x,a,label='Reference 60k',color='tab:orange',lw=1)
        ax.plot(x,b,label='Vertical slit 154k',color='tab:blue',lw=1)
        ax.axvline(500,color='.4',ls=':');ax.axvline(2500,color='.4',ls='--')
        ax.axvspan(0,500,color='.8',alpha=.2);ax.axvspan(2500,3500,color='.8',alpha=.2)
        ax.set_ylabel(label);ax.grid(alpha=.2)
    axs[0].set_yscale('log');axs[0].legend();axs[-1].set_xlabel('Carrier updates after prepared A; hold 0–500, ramp 500–2500, target hold 2500–3500')
    fig.suptitle('Same startup recipe; supplied slit geometry and mesh change')
    if any(missing.values()):fig.text(.5,.01,'Full-feed continuity gap: controller connection lost; inventory and outlet histories remain complete.',ha='center',fontsize=9)
    fig.tight_layout(rect=[0,.035,1,1])
    fig.savefig(figdir/'startup-comparison.png',dpi=180)
    filmfig,fa=plt.subplots(2,2,figsize=(10,7),sharex=True)
    traces=[(h['p72a-e2.7-ewf-film-mass-total'],'Film mass (kg)'),(h['p72a-e2.7-ewf-secondary-phase-mass-total'],'Accretion (kg/s)'),
            (h['p72a-e2.7-ewf-thickness-max']*1000,'Maximum thickness (mm)'),(np.array([max(film[i]['last']) if i in film else np.nan for i in ids]),'Maximum final inner residual')]
    for ax,(values,label) in zip(fa.flat,traces):
        ax.plot(x*1e-3,values,lw=1);ax.set_ylabel(label);ax.set_xlabel('Film time (ms)');ax.grid(alpha=.2)
    fa[1,1].set_yscale('log');fa[1,1].axhline(1e-5,color='.4',ls=':')
    if any(missing.values()):filmfig.text(.5,.01,'Inner-residual gap is unobserved; native film mass, accretion and thickness histories are complete.',ha='center',fontsize=9)
    filmfig.tight_layout(rect=[0,.035,1,1])
    filmfig.savefig(figdir/'film-development.png',dpi=180)
    with PdfPages(OUT/'startup-comparison.pdf') as pdf:pdf.savefig(fig);pdf.savefig(filmfig)
    text=['# Vertical-slit 154k startup — completed result','', '| Item | Verified result |','| --- | --- |',
          f'| Completion | {3500} updates; N{start}–N{end}; final pair saved/reopened |',f'| Native reports | {len(h)} complete frequency-1 histories |',
          f'| Ramp | All 200 ten-update blocks match the reference schedule |',f'| Mapped A bulk inventory | {m["mapped_bulk_liquid_mass_kg"]:.6f} kg; reference 31.357136 kg |',
          f'| Final bulk / film | {summary["final_bulk_liquid_kg"]:.6f} / {summary["final_film_kg"]:.6f} kg |',f'| Final outward liquid | {carry[-1]:.6f} kg/s |',
          f'| Film inner failures | {len(failed)} among {summary["film_inner_observed_updates"]} observed updates; {len(summary["ramp_film_inner_failed_updates"])} during the complete ramp |',
          f'| Streamed evidence gaps | {len(missing["carrier"])} carrier and {len(missing["film_inner"])} film-inner updates missing during full-feed hold; no final-500 continuity comparison |',
          '| Recovery | Python controller timed out during the full-feed hold; Fluent finished the original native command; final endpoint recovered without further iterations |',
          f'| Film clock | {final_clock*1000:.6f} ms |','| Comparison limit | Supplied geometry and mesh change together; residual normalization requires qualification |',
          '| Scientific limit | No steady-film, physical-validation or mesh-convergence claim |','| Setup | [Run contract](setup.md) |','',
          '![Matched startup comparison](figures/startup-comparison.png)','', '| Ramp peak | Reference 60k | Vertical slit 154k |','| --- | ---: | ---: |']
    for name,record in comparison.items():text.append(f'| {name} | {record["reference_ramp"]["peak"]:.6g} | {record["slit_ramp"]["peak"]:.6g} |')
    text+=['','![Film development and numerical adequacy](figures/film-development.png)','',
           '| Evidence | Link |','| --- | --- |','| Full metrics | [Analysis summary](../../../../../../PyAnsys/output/phase72a-stage3-slit154k-server3/20261005/analysis-summary.json) |',
           '| Native paths and hashes | [Manifest](../../../../../../PyAnsys/output/phase72a-stage3-slit154k-server3/20261005/run-manifest.json) |']
    (PROJECT/'results.md').write_text('\n'.join(text)+'\n')
    m['analysis']={'status':'COMPLETE','summary':str(OUT/'analysis-summary.json'),'results':str(PROJECT/'results.md')}
    m['status']='COMPLETE_ANALYSED';(OUT/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print('SLIT_STARTUP_ANALYSIS_COMPLETE',json.dumps(summary),flush=True)


if __name__=='__main__':main()

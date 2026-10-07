"""Native-clock plots and bounded results for the selected Stage 4 continuation."""
from pathlib import Path
import sys,json,csv,math,re,hashlib,argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
import run_phase72a_stage4_realism as run
from run_phase72a_adaptive_film import history,FILM,ROW
OUT=run.OUT;DOC=ROOT.parent/'Project/experiments/phase-07-2a-wall-liquid-routing/stage-04-ewf-wall-parameters/realism-continuation';FIG=DOC/'figures'

def main():
 global OUT,DOC,FIG
 parser=argparse.ArgumentParser();parser.add_argument('--feedback-off',action='store_true');args=parser.parse_args()
 if args.feedback_off:OUT=OUT/'feedback-off';DOC=DOC/'feedback-off';FIG=DOC/'figures'
 m=json.loads((OUT/'run-manifest.json').read_text());assert m['status']=='COMPLETE'
 FIG.mkdir(exist_ok=True)
 raw=OUT/'raw'/f"N{m['verified_native_end']}";raw.mkdir(parents=True,exist_ok=True)
 inputs=list(OUT.glob('*.out'))+[OUT/Path(b['transcript'].replace('\\','/')).name for b in m['blocks']]+[OUT/'report-definitions.json',OUT/'prepared-reopen.json',OUT/'loaded-parent.json',OUT/'run-manifest.json']
 for p in inputs:
  target=raw/p.name
  if not target.exists():target.write_bytes(p.read_bytes())
  assert target.read_bytes()==p.read_bytes()
 histories={name:history((raw/(name+'.out')).read_text()) for name in m['report_paths']}
 start=m['parent_native_iteration'];end=m['verified_native_end'];bulk_end=m['bulk_target_iteration'];x=np.arange(start,end+1)
 parent=json.loads((OUT/'loaded-parent.json').read_text());t0=parent['film']['film_elapsed_time']
 clocks={start:t0};dtmap={};cfl={};continuity={};tracking=[]
 for b in m['blocks']:
  text=(raw/Path(b['transcript'].replace('\\','/')).name).read_text();printed=[tuple(map(float,z.groups())) for z in FILM.finditer(text)]
  assert len(printed)==b['updates']
  tracking.extend({'segment':b['label'],'native_start':b['native_start'],'native_end':b['native_end'],'tracked':int(z[1]),'escaped':int(z[2])} for z in re.finditer(r'number tracked\s*=\s*(\d+),\s*escaped\s*=\s*(\d+)',text))
  for j,i in enumerate(range(b['native_start']+1,b['native_end']+1)):
   clocks[i]=b['film_start_s']+(j+1)*b['step_s'];dtmap[i]=b['step_s'];cfl[i]=printed[j][2]
   assert abs(clocks[i]-printed[j][0])<6e-8
  if not b['frozen_bulk']:
   for line in text.splitlines():
    match=ROW.match(line)
    if match and start<int(match[1])<=bulk_end:
     parts=line.split()
     if len(parts)>=8:continuity[int(match[1])]=float(parts[1])
 assert set(range(start+1,end+1)).issubset(clocks)
 assert set(range(start+1,bulk_end+1)).issubset(continuity)
 keys={'bulk':'v2-total-liquid-mass','flux':'v2-flux-phase2-steamoutlet','film':run.MASS,'accretion':run.ACC,'drainmass':run.DRAIN,'dpm':'p72s4-dpm-source','stripmass':'p72s4-stripped-mass','sepmass':'p72s4-separated-mass'}
 a={}
 for key,name in keys.items():
  h=histories[name]
  assert set(x).issubset(h),(name,'missing initial/terminal history')
  a[key]=np.array([h[int(i)] for i in x]);assert np.isfinite(a[key]).all()
 t=np.array([clocks[int(i)] for i in x]);delta=np.diff(t)
 assert abs(t[-1]-m['verified_film_time_s'])<1e-10
 rates={key:np.r_[np.nan,np.diff(a[src])/delta] for key,src in [('drain','drainmass'),('strip','stripmass'),('sep','sepmass'),('storage','film')]}
 bulkidx=bulk_end-start;transition=t[bulkidx];freeze=x>bulk_end;late=freeze & (t>=t[-1]-.005)
 summary={'start_iteration':start,'bulk_end_iteration':bulk_end,'final_iteration':end,'parent_film_time_s':t0,'bulk_added_film_time_s':transition-t0,'film_only_added_s':t[-1]-transition,'final_film_time_s':t[-1],'metrics':{},'late_window_s':.005,'peak_courant':max(cfl.values()),'bulk_continuity_final':continuity[bulk_end],'bulk_continuity_peak':max(continuity.values()),'source_units_note':'DPM and signed secondary-phase transfer kg/s; outflow/stripped/separated native kg; sampled ledger is diagnostic, not whole-system conservation','steady_film':False}
 for key in ['bulk','flux','film','accretion','dpm']:
  summary['metrics'][key]={'parent':float(a[key][0]),'transition':float(a[key][bulkidx]),'final':float(a[key][-1]),'last5ms_mean':float(np.mean(a[key][late]))}
 for key,values in rates.items():summary['metrics'][key]={'last5ms_mean':float(np.mean(values[late])),'final':float(values[-1])}
 sources=float(np.sum((a['accretion'][1:]+a['dpm'][1:])*delta));changes=sum(a[k][-1]-a[k][0] for k in ['film','drainmass','stripmass','sepmass']);summary['sampled_ledger_error_percent']=float(100*abs(changes-sources)/max(float(np.sum((np.abs(a['accretion'][1:])+np.abs(a['dpm'][1:]))*delta)),1e-30))
 summary['bulk_only_continuity_rows']=len(continuity);summary['native_report_points']=len(x)
 summary['dpm_tracking']={'events':tracking,'event_count':len(tracking),'counts_note':'Tracking-event counts; repeated particle tracks are not unique particles or escaped mass.'}
 summary['cumulative_mass_decreases']={key:int(np.count_nonzero(np.diff(a[key]) < -1e-10)) for key in ['drainmass','stripmass','sepmass']}
 summary['sampled_film_ledger_windows']={}
 for label,mask in [('bulk_active',x[1:]<=bulk_end),('bulk_frozen',x[1:]>bulk_end)]:
  integrated=float(np.sum((a['accretion'][1:]+a['dpm'][1:])[mask]*delta[mask]))
  inventory=float(sum(np.sum(np.diff(a[k])[mask]) for k in ['film','drainmass','stripmass','sepmass']))
  absolute=float(np.sum((np.abs(a['accretion'][1:])+np.abs(a['dpm'][1:]))[mask]*delta[mask]))
  summary['sampled_film_ledger_windows'][label]={'integrated_sources_kg':integrated,'inventory_plus_cumulative_outflow_change_kg':inventory,'residual_kg':inventory-integrated,'absolute_source_normalized_error_percent':100*abs(inventory-integrated)/max(absolute,1e-30)}
 summary['film_last5ms_change_kg']=float(a['film'][-1]-a['film'][np.flatnonzero(late)[0]])
 summary['negative_secondary_transfer_points']=int(np.count_nonzero(a['accretion'] < 0))
 (OUT/'analysis-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
 with (OUT/'diagnostics.csv').open('w') as stream:
  w=csv.writer(stream);w.writerow(['native_iteration','film_time_s','frozen_bulk','bulk_liquid_kg','steamoutlet_phase2_signed_kg_s','film_mass_kg','accretion_kg_s','drainage_kg_s','stripping_kg_s','separation_kg_s','dpm_source_kg_s','storage_kg_s','new_scaled_continuity','film_courant'])
  for j,i in enumerate(x):w.writerow([i,t[j],i>bulk_end,a['bulk'][j],a['flux'][j],a['film'][j],a['accretion'][j],rates['drain'][j],rates['strip'][j],rates['sep'][j],a['dpm'][j],rates['storage'][j],continuity.get(int(i),''),cfl.get(int(i),'')])
 plt.rcParams.update({'font.size':10,'axes.titlesize':11})
 fig,axes=plt.subplots(3,1,figsize=(9,8),sharex=True)
 xb=x[:bulkidx+1]
 for ax,key,title,y in [(axes[0],'bulk','Bulk liquid inventory','Mass (kg)'),(axes[1],'flux','Phase-2 steamoutlet boundary flux','Signed flux (kg/s)')]:
  ax.plot(xb,a[key][:bulkidx+1],lw=1);ax.axhline(a[key][0],ls='--',color='gray',lw=.8,label='N29815 parent');ax.set_title(title,loc='left');ax.set_ylabel(y);ax.legend(fontsize=8)
  ax.grid(alpha=.2)
 axes[2].semilogy(sorted(continuity),[continuity[i] for i in sorted(continuity)],lw=.8)
 axes[2].set_title(f'Continuity during the {bulk_end-start} bulk solves',loc='left');axes[2].set_ylabel('Scaled residual');axes[2].set_xlabel('Native iteration');axes[2].grid(alpha=.2)
 axes[0].text(.02,.04,f'Bulk fields are frozen after N{bulk_end}',transform=axes[0].transAxes,fontsize=9)
 fig.tight_layout();fig.savefig(FIG/'bulk-response.png',dpi=160);fig.savefig(FIG/'bulk-response.pdf');plt.close(fig)
 fig,axes=plt.subplots(4,1,figsize=(10,11),sharex=True);window=x>=bulk_end;tm=(t[window]-transition)*1000
 axes[0].plot(tm,a['film'][window],lw=1);axes[0].set_ylabel('Film mass (kg)');axes[0].set_title('Film inventory',loc='left')
 for key,v in [('Secondary-phase transfer (signed)',a['accretion']),('Drainage',rates['drain']),('Storage',rates['storage'])]:axes[1].plot(tm,v[window],lw=.9,label=key)
 axes[1].set_ylabel('Rate (kg/s)');axes[1].set_title('Film mass rates',loc='left');axes[1].legend(fontsize=8)
 for key,v in [('Stripping',rates['strip']),('Edge separation',rates['sep']),('DPM source',a['dpm'])]:axes[2].plot(tm,v[window],lw=.9,label=key)
 axes[2].set_ylabel('Rate (kg/s)');axes[2].set_title('Particle transfer diagnostics',loc='left');axes[2].legend(fontsize=8)
 axes[3].plot(tm[1:],[cfl[int(i)] for i in x[window][1:]],lw=.9);axes[3].set_ylabel('Film Courant');axes[3].set_title('Native film Courant',loc='left');axes[3].set_xlabel(f'Added EWF-only time after N{bulk_end} bulk freeze (ms)')
 for ax in axes:ax.grid(alpha=.2)
 axes[0].text(.03,.05,'All bulk equation groups frozen; Flow Momentum Coupling OFF',transform=axes[0].transAxes,fontsize=9)
 fig.tight_layout();fig.savefig(FIG/'film-response.png',dpi=160);fig.savefig(FIG/'film-response.pdf');plt.close(fig)
 manifest={'inputs':{str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()},'figures':[str(p.relative_to(ROOT.parent)) for p in FIG.iterdir()],'new_solve_calls':0}
 (OUT/'figure-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()

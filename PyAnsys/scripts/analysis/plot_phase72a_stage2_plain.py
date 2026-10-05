from pathlib import Path
from datetime import datetime,timezone
import json,csv,re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
ROOT=Path(__file__).resolve().parents[3]
RUN=ROOT/'PyAnsys/output/phase72a-stage2-server3/20261005/moderate-restart'
OUT=RUN/'plain-plots';OUT.mkdir(exist_ok=True)
summary=json.loads((RUN/'analysis-summary.json').read_text())
end=summary['native_end'];latest=summary['latest']
plt.rcParams.update({'font.size':12,'axes.titlesize':17,'axes.labelsize':12,'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False})
source=ROOT/'PyAnsys/output/phase72a-lineage-N45606/20261005/selected-lineage-histories.csv'
old=[r for r in csv.DictReader(source.open()) if int(r['native_iteration'])>=13586 and r['native_film_clock_s'] and r['film_kg']]
new=[r for r in csv.DictReader((RUN/'film-history.csv').open()) if int(r['native_iteration'])<=end]
t=np.array([float(r['native_film_clock_s']) for r in old]); mass=np.array([float(r['film_kg']) for r in old]); nt=np.array([float(r['native_film_clock_s']) for r in new]);nm=np.array([float(r['film_mass_kg']) for r in new])
assert abs(mass[-1]-6.360049592042239)<1e-8
fig,ax=plt.subplots(figsize=(10,4.8),layout='constrained')
ax.plot((t-.08)*1000,mass,color='#326aa8',lw=2.2,label='Earlier verified history')
ax.plot(np.r_[(t[-1]-.08)*1000,(nt-.08)*1000],np.r_[mass[-1],nm],color='#dc7f2a',lw=3,label='Completed Server 3 continuation')
ax.scatter([(nt[-1]-.08)*1000],[nm[-1]],color='#dc7f2a',s=45,zorder=5)
ax.set(title='1. The film is still gaining liquid',xlabel='Film time since corrected restart (milliseconds)',ylabel='Liquid held in the film (kg)')
ax.text(.03,.94,'Steady film: this curve would become flat.',transform=ax.transAxes,va='top',bbox={'facecolor':'white','edgecolor':'#dddddd','boxstyle':'round,pad=.5'})
ax.annotate(f'{nm[-1]:.3f} kg',xy=((nt[-1]-.08)*1000,nm[-1]),xytext=(-76,-32),textcoords='offset points',arrowprops={'arrowstyle':'->','color':'#555555'},fontsize=12)
ax.grid(alpha=.2);ax.legend(loc='lower right',fontsize=10)
fig.savefig(OUT/'01-film-mass.png',dpi=155);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,4.6),layout='constrained')
vals=[latest['accretion_kg_s'],latest['drainage_kg_s'],latest['storage_kg_s']]
labels=['Arrives on film\n(accretion)','Leaves the film\n(drainage)','Film mass grows\n(storage rate)']
bars=ax.bar(range(3),vals,color=['#326aa8','#488061','#dc7f2a'],width=.57)
for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+2,f'{v:.1f} kg/s',ha='center',fontsize=15,fontweight='bold')
ax.set_xticks(range(3),labels);ax.set_ylim(0,103);ax.set_ylabel('Liquid rate (kg/s)')
ax.set_title('2. More liquid arrives than leaves')
ax.text(.5,.96,'About 82 in − 74 out = 8 added to the film',ha='center',va='top',transform=ax.transAxes,fontsize=13)
ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
fig.savefig(OUT/'02-film-balance.png',dpi=155);plt.close(fig)
SUB=re.compile(r'sub-iteration:\s*(\d+) residual - h:\s*([^;]+); u:\s*([^;]+); v:\s*(\S+)')
ROW=re.compile(r'^\s*(\d+)\s+[\d.+-]+e[+-]\d+\s+')
records={};sources=[]
for p in sorted(RUN.glob('batch-N*-N*.txt')):
 sources.append(str(p));text=p.read_text();pending=None;finished=None
 for line in text.splitlines():
  a=SUB.search(line)
  if a:pending=[int(a[1]),*map(float,a.groups()[1:])]
  if 'Film time =' in line and pending is not None:finished=pending;pending=None
  row=ROW.match(line)
  if row and finished is not None:
   n=int(row[1]);records[n]=finished;finished=None
# The saved probe verifies its terminal film record independently.
probe=json.loads((RUN/'film-residuals-N45606-N45706.json').read_text())
for n,v in probe.items():records[int(n)]=v[-1]
ids=sorted(records);values=np.array([max(records[n][1:]) for n in ids])
assert ids[0]==45607
fig,ax=plt.subplots(figsize=(10,4.9),layout='constrained')
ax.axvspan(45606,45706,color='#edf3f8',zorder=0)
ax.axhspan(1e-9,1e-5,color='#edf5ed',zorder=0)
ax.semilogy(ids,values,color='#326aa8',lw=1.1)
ax.axhline(1e-5,color='#444444',ls='--',lw=1.3)
ax.axvline(45706,color='#999999',ls=':',lw=1)
ax.set_ylim(1e-8,max(50,float(values.max())*2));ax.set_xlim(45606,ids[-1]+10)
ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
ax.set(title='3. The film solves do not always settle',xlabel='Fluent iteration (N)',ylabel='Highest final film residual (log scale)')
ax.text(.02,.94,'First 100 updates passed.\nLater updates have repeated bursts.',transform=ax.transAxes,va='top',bbox={'facecolor':'white','edgecolor':'#dddddd','boxstyle':'round,pad=.45'})
ax.text(.99,1e-5,' Stop value: 0.00001 ',transform=ax.get_yaxis_transform(),va='bottom',ha='right',fontsize=10,bbox={'facecolor':'white','edgecolor':'none'})
ax.grid(alpha=.18,which='major')
fig.savefig(OUT/'03-film-solver-errors.png',dpi=155);plt.close(fig)
receipt={'snapshot_utc':datetime.now(timezone.utc).isoformat(),'mass_and_balance_verified_end':end,'balance_window':[latest['native_start'],latest['native_end']],'latest_balances_kg_s':vals,'residual_transcript_through':ids[-1],'residual_points':len(ids),'post_probe_final_residual_above_1':sum(max(records[n][1:])>1 for n in ids if n>45706),'source_mass_history':str(source),'source_summary':str(RUN/'analysis-summary.json'),'source_transcripts':sources,'note':'Completed mass/balance evidence and partial live residual transcript are separate; no interpolation or solver changes.'}
(OUT/'plot-sources.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))

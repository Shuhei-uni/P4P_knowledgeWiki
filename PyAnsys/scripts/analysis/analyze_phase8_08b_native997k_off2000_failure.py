"""Plot captured native residual divergence; source transcript left unchanged."""
from pathlib import Path
import re,json,csv,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'PyAnsys/output/phase8-stage2/20261007/08b-native997k/run2000-off'
PROJECT=ROOT/'Project/experiments/phase-08-storyline-reconstruction/stage-02-fine-mesh-simple/08b-native997k/run2000-off'
source=OUT/'raw/recovered-host-native-transcript.txt'
if not source.exists():source=OUT/'raw/passive-native-transcript.txt'
text=source.read_text();rows=[]
for line in text.splitlines():
 parts=line.split()
 if len(parts)<8 or not parts[0].isdigit():continue
 try:
  n=int(parts[0]);values=[float(x) for x in parts[1:8]]
 except ValueError:continue
 if 10000<=n<=12000:rows.append([n]+values)
by_n={row[0]:row for row in rows};rows=[by_n[n] for n in sorted(by_n)];assert rows[-1][0]==10022
header=['native_iteration','continuity','x_velocity','y_velocity','z_velocity','k','epsilon','volume_fraction_phase2']
with (OUT/'captured-residuals.csv').open('w') as f:
 w=csv.writer(f);w.writerow(header);w.writerows(rows)
figdir=PROJECT/'figures';figdir.mkdir(exist_ok=True)
fig,axes=plt.subplots(1,2,figsize=(10.5,4),sharex=True)
x=[row[0]-10000 for row in rows]
for col,label in [(1,'Continuity'),(5,'k'),(6,'epsilon')]:axes[0].semilogy(x,[row[col] for row in rows],marker='o',markersize=3,label=label)
for col,label in [(2,'x velocity'),(3,'y velocity'),(4,'z velocity'),(7,'Liquid volume fraction')]:axes[1].semilogy(x,[row[col] for row in rows],marker='o',markersize=3,label=label)
for ax in axes:
 ax.set_xlabel('Additional carrier iterations from N10000');ax.set_ylabel('Native reported residual');ax.grid(True,which='major',alpha=.25);ax.legend(fontsize=8);ax.axvline(22,color='k',ls=':',lw=1)
axes[0].set_title('Continuity and turbulence');axes[1].set_title('Momentum and liquid fraction')
fig.suptitle('08b settings on new 997,604-cell mesh — absorber OFF\nLast printed N10022; numerical divergence followed by SIGSEGV',fontsize=11)
fig.tight_layout();fig.savefig(figdir/'startup-divergence.png',dpi=180);plt.close(fig)
build=json.loads((OUT/'build.json').read_text())
missing=sorted(set(range(10000,10023))-set(by_n))
receipt={'status':'NUMERICAL_DIVERGENCE_THEN_SOLVER_SIGSEGV','source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'server_id':'2','mesh_cells':997604,'settings_parent':'08b on replacement997k mesh','absorber_enabled':False,'requested_additional_iterations':2000,'start_native_iteration':10000,'last_printed_native_iteration':10022,'observed_additional_updates':22,'exact_crash_iteration':'Not available; crash followed last printedN10022','last_verified_usable_pair':build['prepared_pair'],'first_scheduled_inrun_autosave_iteration':10100,'post_start_checkpoint':'No scheduled autosave reached; last verified pairN10000','native_rows':len(rows),'missing_printed_rows':missing,'final_residuals':dict(zip(header,rows[-1])),'critical_rows':{str(n):dict(zip(header,by_n[n])) for n in [10019,10020,10021,10022]},'host_terminal_manifest':'Recovered after user restartedServer2' if (OUT/'recovered-host-job-manifest.json').exists() else 'Unavailable after Fluent server shutdown','failed_pair':'No post-failure save verified; server inaccessible','limit':'Failure of this parent/settings/mesh/interpolated-start route; no universal impossibility or absorber-effect claim'}
(OUT/'observed-failure-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'rows':len(rows),'missing_rows':missing,'last_native':rows[-1][0],'failure':receipt['status']}))

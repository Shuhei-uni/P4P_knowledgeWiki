"""Native-geometry and liquid-fraction meeting figures, with explicit snapshot provenance."""
from pathlib import Path
import json,hashlib
import numpy as np
from analyze_phase07b_screen import plt,parse_residuals
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
BASE=Path(__file__).resolve().parents[2];P=BASE/'output/phase07b-meeting-20260922';OUT=P/'figures';OUT.mkdir(exist_ok=True)
CASES=['S20','S40','S60','S80','S100'];TOPS=[-1.1836669883728028,-.882750241279602,-.5818334941864014,-.2809167470932006,.02]
RUNS=['p7b-s020-20260920T221831Z','p7b-s040-20260921T013001Z','p7b-s060-resume-20260921T113238Z','p7b-s080-20260921T130348Z','p7b-s100-20260921T160825Z']
plt.rcParams.update({'font.size':12,'axes.titlesize':14,'axes.labelsize':12,'legend.fontsize':10,'figure.titlesize':17})
def load(f,axes=None):
 with np.load(f) as a:d={k:a[k] for k in a.files}
 off=np.r_[0,np.cumsum(d['face_sizes'])];v=d['vertices'];polys=[v[d['connectivity'][off[i]:off[i+1]]] for i in range(len(off)-1)]
 return d,[p[:,axes] if axes else p for p in polys]
def clip(poly,top):
 out=[]
 for a,b in zip(poly,np.roll(poly,-1,axis=0)):
  ia=a[1]<=top;ib=b[1]<=top
  if ia:out.append(a)
  if ia!=ib:out.append(a+(b-a)*(top-a[1])/(b[1]-a[1]))
 return np.array(out)
def save(fig,name):fig.savefig(OUT/name,dpi=190,bbox_inches='tight');plt.close(fig)
def geometry():
 idx=json.loads((P/'geometry/index.json').read_text());fig=plt.figure(figsize=(12,9));ax=fig.add_subplot(121,projection='3d')
 for name,r in idx['surfaces'].items():
  d,polys=load(P/'geometry'/r['file']);poly=[p[:,[0,2,1]] for p in polys]
  col='#8f9aa3';alpha=.16
  if name=='steam-outlet':col='#bc4c20';alpha=1
  elif 'inlet' in name and r['zone_type']=='velocity-inlet':col='#2166ac' if name=='steam-inlet' else '#00a6a6';alpha=1
  elif name=='brine-outlet':col='#333333';alpha=1
  elif name=='wall:010':col='#58acb0';alpha=.3
  ax.add_collection3d(Poly3DCollection(poly,facecolor=col,edgecolor='none',alpha=alpha,rasterized=True))
 ax.set(xlim=(-2.2,1.2),ylim=(-1.6,1.2),zlim=(-1.55,7.1),xlabel='x (m)',ylabel='z (m)',zlabel='y (m)');ax.set_xticks([-2,0,1]);ax.set_yticks([-1,0,1]);ax.grid(False);ax.set_box_aspect((3.4,2.8,8.65));ax.view_init(elev=13,azim=-58);ax.set_title('Actual mesh boundary surfaces')
 ax.text(-.4,0,6.3,'Steam outlet',color='#9b3a19',fontsize=11)
 ax.text(-2.25,-1.2,2.5,'Split inlet',color='#2166ac',fontsize=11)
 ax.text(.3,1.05,-.55,'Brine face: wall',fontsize=11)
 ax2=fig.add_subplot(122);d,polys=load(P/'S100/p7b-meeting-z0.npz',[0,1]);ax2.add_collection(PolyCollection(polys,facecolor='#e7edf0',edgecolor='none',antialiased=False))
 filled=[q for p in polys if len(q:=clip(p,.02))>=3];ax2.add_collection(PolyCollection(filled,facecolor='#58acb0',edgecolor='none',antialiased=False))
 ax2.autoscale_view();ax2.set_aspect('equal');ax2.set(xlabel='x (m)',ylabel='y (m)',title='Central section: z = 0 m')
 ax2.axhline(.02,color='#137c82',ls='--',lw=1.3);ax2.annotate('Maximum removal region\ny ≤ +0.020 m',xy=(.75,-.55),xytext=(1.35,.65),arrowprops={'arrowstyle':'->'},fontsize=12)
 ax2.annotate('No standing pool required',xy=(.8,-1.1),xytext=(1.35,-1.2),arrowprops={'arrowstyle':'->'},fontsize=11)
 ax2.text(1.35,4.5,'620,431 cells\nFull lower geometry\nSteady Mixture / RNG\nEnergy off',fontsize=12,linespacing=1.7)
 ax2.set_xlim(-1.2,3.6);ax2.set_ylim(-1.6,7.15);ax2.spines[['top','right']].set_visible(False)
 fig.suptitle('Full separator and ideal collector');fig.subplots_adjust(top=.91,wspace=.06);save(fig,'geometry-overview.png')
 fig,axs=plt.subplots(1,5,figsize=(14,5),sharex=True,sharey=True,layout='constrained')
 for ax,case,top in zip(axs,CASES,TOPS):
  ax.add_collection(PolyCollection(polys,facecolor='#e7edf0',edgecolor='none',antialiased=False));filled=[q for p in polys if len(q:=clip(p,top))>=3];ax.add_collection(PolyCollection(filled,facecolor='#168b92',edgecolor='none',antialiased=False))
  ax.axhline(.02,color='#666666',ls=':',lw=1);ax.axhline(top,color='#08656a',ls='--',lw=1);ax.set_title(f'{case}\ny top = {top:+.3f} m');ax.set_aspect('equal');ax.set(xlim=(-1.12,1.12),ylim=(-1.55,.4),xlabel='x (m)')
  ax.spines[['top','right']].set_visible(False)
 axs[0].set_ylabel('y (m)');fig.suptitle('Five nested removal extents | lower-region detail, z = 0 m');save(fig,'collector-regions.png')
def fractions():
 audit={}
 for axis,xy in [('z',[0,1]),('x',[2,1])]:
  fig,axs=plt.subplots(1,5,figsize=(13,9),sharex=True,sharey=True,layout='constrained')
  for ax,case,top in zip(axs,CASES,TOPS):
   f=P/case/f'p7b-meeting-{axis}0.npz';d,polys=load(f,xy);values=d['phase-2-vof'];assert np.isfinite(values).all() and values.min()>=-1e-7 and values.max()<=1+1e-7
   coll=PolyCollection(polys,array=values,cmap='viridis',clim=(0,1),edgecolors='none',antialiased=False,rasterized=True);ax.add_collection(coll);ax.autoscale_view();ax.set_aspect('equal')
   ax.axhline(top,color='#c85f15',ls='--',lw=1);ax.set_title(case+('\nN4000 recovery' if case=='S100' else '\nN5000'),fontsize=13);ax.set_xlabel(('x' if axis=='z' else 'z')+' (m)');ax.set_ylim(-1.55,7.05)
   audit[f'{case}-{axis}0']={'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'facets':len(values),'minimum':float(values.min()),'maximum':float(values.max())}
  axs[0].set_ylabel('y (m)');fig.colorbar(coll,ax=axs,location='bottom',shrink=.6,pad=.025,label='Liquid volume fraction (0 = no liquid; 1 = all liquid)');fig.suptitle(f'Full-height liquid volume fraction | {axis} = 0 m\nDashed lines mark each collector top; native facet values, common 0–1 scale',fontsize=15);save(fig,f'liquid-fraction-{axis}0-all-cases.png')
 # Individual case figures: both full-height sections.
 for case,top in zip(CASES,TOPS):
  fig,axs=plt.subplots(1,2,figsize=(7,10),sharey=True,layout='constrained')
  for ax,axis,xy in zip(axs,['z','x'],[[0,1],[2,1]]):
   d,polys=load(P/case/f'p7b-meeting-{axis}0.npz',xy);coll=PolyCollection(polys,array=d['phase-2-vof'],cmap='viridis',clim=(0,1),edgecolors='none',antialiased=False)
   ax.add_collection(coll);ax.autoscale_view();ax.set_aspect('equal');ax.axhline(top,color='#c85f15',ls='--');ax.set_title(f'{axis} = 0 m');ax.set_xlabel(('x' if axis=='z' else 'z')+' (m)')
  axs[0].set_ylabel('y (m)');fig.colorbar(coll,ax=axs,location='bottom',shrink=.6,label='Liquid volume fraction');fig.suptitle(case+(' | N4000 recovery checkpoint' if case=='S100' else ' | N5000')+'\nNative fields; common 0–1 scale',fontsize=14);save(fig,f'{case}-liquid-volume-fraction.png')
 (OUT/'liquid-fraction-provenance.json').write_text(json.dumps(audit,indent=2)+'\n')
def residuals():
 fig,axs=plt.subplots(2,2,figsize=(14,8),sharex=True,sharey=True,layout='constrained')
 for ax,case,run in zip(axs.flat,CASES,RUNS):
  d,a=parse_residuals(BASE/'output'/run/'solve.trn')
  for k,v in d.items():
   if k!='iteration':ax.plot(d['iteration'],v,label=k,lw=.8)
  ax.axhline(1e-3,color='black',ls='--',lw=1);ax.set_yscale('log');ax.set_ylim(1e-6,1e3);ax.set_title(f'{case} | N1–5000');ax.set_xlabel('Steady iteration');ax.set_ylabel('Scaled residual');ax.grid(alpha=.2)
 handles,labels=axs.flat[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=7,fontsize=11);fig.suptitle('All seven residuals | four completed cases\nDashed line: 10⁻³ screening threshold',fontsize=16);save(fig,'residuals-completed-cases.png')
 d,a=parse_residuals(BASE/'output'/RUNS[-1]/'solve.trn');fig,axs=plt.subplots(1,2,figsize=(14,6),layout='constrained')
 for ax,mask,title in [(axs[0],d['iteration']<=4100,'S100 | N1–4100 before terminal window'),(axs[1],d['iteration']>=4100,'S100 | N4100–4182 numerical runaway')]:
  for k,v in d.items():
   if k!='iteration':ax.plot(d['iteration'][mask],v[mask],label=k,lw=1)
  ax.axhline(1e-3,color='black',ls='--');ax.set_yscale('log');ax.set_title(title);ax.set(xlabel='Steady iteration',ylabel='Scaled residual');ax.grid(alpha=.2)
 axs[0].set_ylim(1e-6,1e3);handles,labels=axs[0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside lower center',ncol=7,fontsize=11);fig.suptitle('S100 failed at attempted N4183 | all completed residual records retained\nRight panel uses an expanded vertical scale to show divergence',fontsize=16);save(fig,'residuals-S100-failure.png')
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--geometry-only',action='store_true');a=ap.parse_args();geometry()
 if not a.geometry_only:fractions();residuals()
 print(str(OUT))

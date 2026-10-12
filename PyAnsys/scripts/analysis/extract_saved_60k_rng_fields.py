"""Read saved RNG fields and reconstruct approximate gradients, without Fluent."""
from pathlib import Path
import json,hashlib,csv,re
from collections import defaultdict
import h5py,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path('/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase9/initial-bulk-development-final/selected-1791516474564823000')
OUT=ROOT/'PyAnsys/output/rng-local-60k/20261009'

def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 paths={k:SOURCE/'60k'/f'60k-initial-bulk-N8080.{ext}.h5' for k,ext in [('case','cas'),('data','dat')]}
 hashes={k:digest(p) for k,p in paths.items()}
 assert hashes==json.loads((SOURCE/'selection-manifest.json').read_text())['pairs']['60k']['hashes']
 with h5py.File(paths['case']) as case,h5py.File(paths['data']) as data:
  m=case['meshes/1'];n=int(m.attrs['cellCount'][0]);ns=int(m['cells/zoneTopology/maxId'][0]);assert n==60964
  xyz=list(m['nodes/coords'].values())[0][:]
  counts=m['faces/nodes/1/nnodes'][:].astype(int);off=np.r_[0,np.cumsum(counts)];nodes=m['faces/nodes/1/nodes'][:].astype(int)-1
  c0=m['faces/c0/1'][:].astype(int)-1;c1=np.full(len(c0),-1)
  for ds in m['faces/c1'].values():c1[int(ds.attrs['minId'][0])-1:int(ds.attrs['maxId'][0])]=ds[:].astype(int)-1
  assert np.all(c0>=0)
  vol=np.zeros(n);moment=np.zeros((n,3));closure=np.zeros((n,3));surface=np.zeros(n);fc=np.zeros((len(c0),3));fa=np.zeros(len(c0))
  for f in range(len(c0)):
   p=xyz[nodes[off[f]:off[f+1]]];a=np.broadcast_to(p[0],p[1:-1].shape);b=p[1:-1];c=p[2:]
   av=np.cross(b-a,c-a)/2;avec=av.sum(0);area=np.linalg.norm(avec)
   # Signed planar-face centroid; works for concave polygons.
   weights=av@(avec/area);cent=((a+b+c)/3*weights[:,None]).sum(0)/weights.sum();fc[f]=cent;fa[f]=area
   vs=np.einsum('ij,ij->i',a,np.cross(b,c))/6;vv=vs.sum();mm=(vs[:,None]*(a+b+c)/4).sum(0)
   for cid,sign in [(c0[f],1),(c1[f],-1)]:
    if cid>=0:vol[cid]+=sign*vv;moment[cid]+=sign*mm;closure[cid]+=sign*avec;surface[cid]+=area
  centres=moment/vol[:,None]
  sign=np.sign(np.median(vol));vol*=sign
  assert np.all(vol>0) and np.all(np.isfinite(centres))
  closure_relative=np.linalg.norm(closure,axis=1)/surface
  assert closure_relative.max()<1e-8
  mapping={'k':'SV_K','epsilon':'SV_D','mu_t':'SV_MU_T','mu':'SV_MU_LAM','rho':'SV_DENSITY','u':'SV_U','v':'SV_V','w':'SV_W','wall_distance':'SV_WALL_DIST'}
  cells=data['results/1/phase-1/cells'];values={}
  for alias,key in mapping.items():
   ds=cells[key+'/1'];assert ds.shape==(n,) and int(ds.attrs['minId'][0])==1;values[alias]=ds[:]
  velocity=np.column_stack([values[a] for a in ['u','v','w']])
  assert np.all(values['k']>0) and np.all(values['epsilon']>0)
  # Every neighbour face contributes a centre-to-centre observation.
  interior=np.flatnonzero(c1>=0);left=c0[interior];right=c1[interior]
  target=np.r_[left,right];source=np.r_[right,left];delta=centres[source]-centres[target];dv=velocity[source]-velocity[target]
  # Use stored wall/inlet/outlet face velocities for boundary observations.
  faces=data['results/1/phase-1/faces'];bv=np.full((len(c0),3),np.nan)
  for component,key in enumerate(['SV_U','SV_V','SV_W']):
   for ds in faces[key].values():bv[int(ds.attrs['minId'][0])-1:int(ds.attrs['maxId'][0]),component]=ds[:]
  boundary=np.flatnonzero((c1<0)&np.all(np.isfinite(bv),axis=1))
  target=np.r_[target,c0[boundary]];delta=np.vstack([delta,fc[boundary]-centres[c0[boundary]]]);dv=np.vstack([dv,bv[boundary]-velocity[c0[boundary]]])
  weights=1/np.einsum('ij,ij->i',delta,delta)
  normal=np.zeros((n,3,3));rhs=np.zeros((n,3,3))
  np.add.at(normal,target,np.einsum('ni,nj,n->nij',delta,delta,weights))
  np.add.at(rhs,target,np.einsum('ni,nj,n->nij',delta,dv,weights))
  eigen=np.linalg.eigvalsh(normal);condition=eigen[:,-1]/eigen[:,0]
  assert np.all(eigen[:,0]>0) and condition.max()<1e12
  grad=np.linalg.solve(normal,rhs).transpose(0,2,1) # [cell,velocity component,coordinate]
  # Test the same mesh stencils against a prescribed affine vector field.
  affine=np.array([[1.,2.,-.5],[-2.,.3,1.],[.2,-.6,3.]])
  test_rhs=np.zeros_like(rhs);np.add.at(test_rhs,target,np.einsum('ni,nj,n->nij',delta,delta@affine.T,weights))
  test_grad=np.linalg.solve(normal,test_rhs).transpose(0,2,1)
  affine_error=np.max(np.abs(test_grad-affine));assert affine_error<1e-8
  rv=case['settings/Rampant Variables'][0].decode()
  controls={key:re.search(r'\('+re.escape(key)+r'\s+([^\)]+)\)',rv).group(1) for key in ['rng-ke-on?','rng-swirl-on?','rng-swirl-const','rng-visc-mod-on?','rng-kecmu','curvature-correction?']}
 strain=(grad+grad.transpose(0,2,1))/2;spin=(grad-grad.transpose(0,2,1))/2
 strain_mag=np.sqrt(2*np.sum(strain**2,axis=(1,2)));vorticity_mag=np.sqrt(2*np.sum(spin**2,axis=(1,2)))
 tau=values['k']/values['epsilon'];mu_ref=.0845*values['rho']*values['k']**2/values['epsilon']
 neighbours=defaultdict(set);boundary_by_cell=defaultdict(list)
 for a,b in zip(left,right):neighbours[int(a)].add(int(b));neighbours[int(b)].add(int(a))
 for f in boundary:boundary_by_cell[int(c0[f])].append(int(f))
 probes=[('Inlet approach',[-1.8,2.066,-1.1]),('Below inlet, outer region',[.95,1.5,0]),('Below inlet, inner region',[.40,1.5,0]),('Lower vessel, outer region',[.95,.3,0]),('Upper vessel, inner region',[.40,4,0]),('Upper vessel, outer region',[.95,4,0])]
 samples=[]
 for name,point in probes:
  i=int(np.argmin(np.sum((centres[:ns]-point)**2,axis=1)));near=set(neighbours[i]);two=set(near)
  for j in near:two.update(neighbours[j])
  two.discard(i);jj=np.array(sorted(two));dd=centres[jj]-centres[i];vv=velocity[jj]-velocity[i]
  for f in boundary_by_cell[i]:dd=np.vstack([dd,fc[f]-centres[i]]);vv=np.vstack([vv,bv[f]-velocity[i]])
  ww=1/np.sum(dd**2,axis=1);g2=np.linalg.solve(dd.T@(ww[:,None]*dd),dd.T@(ww[:,None]*vv)).T
  error=np.linalg.norm(g2-grad[i])/np.linalg.norm(grad[i])
  sample={'location':name,'requested_xyz_m':point,'cell_id':i+1,'cell_centroid_xyz_m':centres[i].tolist(),'distance_from_request_m':float(np.linalg.norm(centres[i]-point)),
   **{k:float(a[i]) for k,a in values.items()},'velocity_gradient_s_inv':grad[i].tolist(),'gradient_two_ring_s_inv':g2.tolist(),'gradient_two_ring_relative_difference':float(error),
   'gradient_normal_matrix_condition':float(condition[i]),'strain_rate_magnitude_s_inv':float(strain_mag[i]),'vorticity_magnitude_s_inv':float(vorticity_mag[i]),
   'turbulence_time_scale_s':float(tau[i]),'strain_timescale_ratio':float(strain_mag[i]*tau[i]),'vorticity_timescale_ratio':float(vorticity_mag[i]*tau[i]),
   'mu_t_over_mu':float(values['mu_t'][i]/values['mu'][i]),'high_Re_RNG_mu_reference_Pa_s':float(mu_ref[i]),'mu_t_over_high_Re_reference':float(values['mu_t'][i]/mu_ref[i])}
  samples.append(sample);print(name,sample['cell_id'],sample['k'],sample['epsilon'],sample['mu_t'],sample['vorticity_timescale_ratio'],'gradient sensitivity',error,flush=True)
 result={'status':'SAVED_FIELDS_WITH_OFFLINE_GRADIENT_ESTIMATES','native_iteration':8080,'mesh_cells':n,'separator_cells':ns,'paths':{k:str(v) for k,v in paths.items()},'sha256':hashes,'script_sha256':digest(Path(__file__)),
 'fluent_version':'25.2','saved_model_controls':controls,'field_mapping':mapping,
 'gradient_convention':'G[i,j]=d velocity_component_i / d coordinate_j; component and coordinate order x,y,z',
 'gradient_method':'Inverse-distance-squared weighted least squares from face-neighbour cell centres and stored boundary face velocities; two-ring reconstruction is a sensitivity diagnostic.',
 'definitions':{'strain':'sqrt(2*Sij*Sij), Sij=(Gij+Gji)/2','vorticity':'|curl(u)| = sqrt(2*Wij*Wij), Wij=(Gij-Gji)/2','timescale':'k/epsilon','high_Re_RNG_reference_mu_t':'0.0845*rho*k^2/epsilon'},
 'checks':{'hashes_match_selected_manifest':True,'all_reconstructed_cell_volumes_positive':True,'max_relative_cell_face_closure':float(closure_relative.max()),'max_gradient_condition':float(condition.max()),'affine_gradient_max_error_s_inv':float(affine_error)},
 'saved_separator_ranges':{k:{'min':float(a[:ns].min()),'max':float(a[:ns].max())} for k,a in values.items()},'samples':samples,
 'limits':['Nearest-cell point samples are illustrative, not region averages.','Gradients are reconstructed estimates, not saved Fluent-native gradients; stencil sensitivity is reported.','Vorticity*k/epsilon is a local rotation-timescale diagnostic, not the native RNG swirl parameter or the section swirl number.','Differential viscosity and swirl modifications are both enabled; mu_t/reference does not isolate swirl alone.','The exact Fluent swirl multiplier and response to changing its constant cannot be recovered from this one saved state using the public functional form.','Initial bulk-development snapshot; no steady-state, grid independence or physical-validation claim.']}
 (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
 columns=['location','cell_id','k','epsilon','mu_t','rho','mu_t_over_mu','strain_rate_magnitude_s_inv','vorticity_magnitude_s_inv','turbulence_time_scale_s','strain_timescale_ratio','vorticity_timescale_ratio','mu_t_over_high_Re_reference','gradient_two_ring_relative_difference']
 with (OUT/'samples.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');writer.writeheader();writer.writerows(samples)
 np.savez_compressed(OUT/'all-cell-fields-and-gradients.npz',cell_id=np.arange(n)+1,centroid_xyz_m=centres,cell_volume_m3=vol,velocity_gradient_s_inv=grad,strain_rate_magnitude_s_inv=strain_mag,vorticity_magnitude_s_inv=vorticity_mag,**values)
 fig,axes=plt.subplots(1,2,figsize=(10,5));ys=np.arange(len(samples));labels=[a['location'] for a in samples]
 axes[0].barh(ys-.15,[a['strain_timescale_ratio'] for a in samples],height=.3,label='Strain × k/ε')
 axes[0].barh(ys+.15,[a['vorticity_timescale_ratio'] for a in samples],height=.3,label='Vorticity × k/ε');axes[0].axvline(1,color='gray',ls='--');axes[0].set(xlabel='Local time-scale ratio',yticks=ys,yticklabels=labels);axes[0].legend(fontsize=8)
 axes[1].barh(ys,[a['mu_t_over_high_Re_reference'] for a in samples]);axes[1].axvline(1,color='gray',ls='--');axes[1].set(xlabel='Saved μt / (0.0845 ρ k²/ε)',yticks=ys,yticklabels=[])
 for ax in axes:ax.invert_yaxis();ax.grid(axis='x',alpha=.2)
 fig.suptitle('60,964 cells — saved N8080 RNG fields\nGradient diagnostics are offline estimates; viscosity ratio includes multiple model effects',fontsize=10);fig.tight_layout();fig.savefig(OUT/'local-rng-diagnostics.png',dpi=170);plt.close(fig)
if __name__=='__main__':main()

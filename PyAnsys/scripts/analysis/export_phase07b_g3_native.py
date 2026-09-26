"""G3/E4/E5/E6 native Fluent hotspot/context contours; no solving or image modification."""
from pathlib import Path
import argparse,base64,fcntl,hashlib,json,math,signal
from datetime import datetime,timezone
from PIL import Image
from export_phase07b_g2_native import BASE,connect,ROOT,remote_file_exists,read_text

def main():
 ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--ranges-from',type=Path);ap.add_argument('--experiment',choices=['G3','E4','E5','E6','E7'],default='G3');args=ap.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=False)
 lock=(BASE/'output/phase07b-server1-controller.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ').lower();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('Reconcile uncertain native export before retry')))
 current=json.loads((args.run/'manifest.json').read_text());original=json.loads((BASE/'output/p7b-s40-t020-resume-20260921T231240Z/manifest.json').read_text())
 assert current['completed_iterations']==5000 and current['status']=='HORIZON_COMPLETE_ANALYSIS_PENDING'
 specs=[('DIAG-N5000',current,'final',5000),('DIAG-N4500',current,'n04500',4500),('ORIGINAL-N5000',original,'final',5000)]
 if args.experiment=='E4':
  assert current['experiment_id']=='E4'
  diag=json.loads((BASE/'output/p7b-s40-t020-diag-resume-20260922T122811Z/manifest.json').read_text())
  specs=[('COUPLED-N5000',current,'final',5000),('DIAG-N5000',diag,'final',5000),('ORIGINAL-N5000',original,'final',5000)]
 if args.experiment=='E5':
  assert current['experiment_id']=='E5'
  control=json.loads((BASE/'output/p7b-s40-t020-coupled-off-20260922T134224Z/manifest.json').read_text())
  specs=[('CFL20-N5000',current,'final',5000),('CFL200-N5000',control,'final',5000)]
 if args.experiment=='E6':
  assert current['experiment_id']=='E6'
  control=json.loads((BASE/'output/p7b-s40-t020-coupled-cfl20-20260922T202845Z/manifest.json').read_text())
  specs=[('NPHASE-N5000',current,'final',5000),('CFL20-N5000',control,'final',5000)]
 if args.experiment=='E7':
  assert current['experiment_id']=='E7'
  control=json.loads((BASE/'output/p7b-s40-t020-coupled-cfl20-nphase-resume-20260923T231816Z/manifest.json').read_text())
  specs=[('T100-N5000',current,'final',5000),('T020-N5000',control,'final',5000)]
 record={'status':'EXPORTING','created_utc':datetime.now(timezone.utc).isoformat(),'additional_iterations':0,'sources':{},'figures':[],'claim_limit':'Finite saved states only; N4500/N5000 bracket unsaved event N4763. Not convergence or causal proof.'}
 if args.experiment=='E4':record['claim_limit']='Matched finite N5000 states; coupling contrast with identical initial fields. Spatial differences alone do not establish convergence or causality.'
 if args.experiment=='E5':record['claim_limit']='Matched finite N5000 states; only Flow Courant differs. Spatial differences alone do not establish convergence or causality.'
 if args.experiment=='E6':record['claim_limit']='Matched finite N5000 states; only Solve N-Phase Volume Fraction Equations differs. Spatial differences alone do not establish convergence or causality.'
 if args.experiment=='E7':record['claim_limit']='Matched finite N5000 states; only sink tau differs (0.02 vs 0.10 s), including linked sink scaling. No convergence or physical validation claim.'
 record['experiment']=args.experiment
 def persist():(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 def py(code):return s.scheme.eval('(%py-eval '+json.dumps(code)+')')
 def transfer(remote,local):
  b=base64.b64decode(py("__import__('base64').b64encode(__import__('pathlib').Path("+repr(remote)+").read_bytes()).decode()"));sha=hashlib.sha256(b).hexdigest();assert sha==py("__import__('hashlib').sha256(__import__('pathlib').Path("+repr(remote)+").read_bytes()).hexdigest()")
  local.write_bytes(b)
  with Image.open(local) as im:dim=im.size;im.verify()
  return sha,list(dim)
 signal.alarm(60);s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5);s.transcript.start(file_name=str(out/'export.trn'),write_to_stdout=False)
 assert not s.settings.solution.run_calculation.iterating()
 assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==5000
 for k,v in current['definitions'].items():assert s.settings.setup.named_expressions[k].definition()==v
 summary_path=BASE/'output/phase07b-g4/coupled-off/summary.json' if args.experiment=='E4' else args.run/'analysis/summary.json'
 if args.experiment=='E5':summary_path=BASE/'output/phase07b-g5/coupled-cfl20/summary.json'
 if args.experiment=='E6':summary_path=BASE/'output/phase07b-g6/coupled-cfl20-nphase/summary.json'
 if args.experiment=='E7':summary_path=BASE/'output/phase07b-g7/nphase-t100/summary.json'
 expected=json.loads(summary_path.read_text())['latest_metrics']['whole_water_volume']['value'];assert math.isclose(s.settings.setup.named_expressions['P7bWaterVolume'].get_value(),expected,rel_tol=1e-12)
 assert all(remote_file_exists(s,current['pairs']['final'].replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
 record['preserved_current_endpoint']=current['pairs']['final'];record['fluent_version']=str(s.get_fluent_version());loaded=current['pairs']['final'];surfaces={};ranges={}
 def load(spec):
  nonlocal loaded
  label,m,tag,n=spec;pair=m['pairs'][tag];signal.alarm(600)
  assert all(remote_file_exists(s,pair.replace('.cas.h5',x)) for x in ['.cas.h5','.dat.h5'])
  if loaded!=pair:s.settings.file.read_case_data(file_name=pair);loaded=pair
  assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==n
  for k,v in m['definitions'].items():assert s.settings.setup.named_expressions[k].definition()==v
  record['sources'][label]={'case':pair,'data':pair.replace('.cas.h5','.dat.h5'),'iteration':n,'water_volume':s.settings.setup.named_expressions['P7bWaterVolume'].get_value()};persist()
 def surface(axis,value):
  name='g3-'+stamp+('-hot' if axis=='y' else '-x0');iso=s.settings.results.surfaces.iso_surface
  if name not in iso.get_object_names():iso.create(name=name);s.settings.results.surfaces.iso_surface[name].set_state({'field':axis+'-coordinate','iso_values':[value]})
  state=s.settings.results.surfaces.iso_surface[name].get_state();assert state['field']==axis+'-coordinate' and state['iso_values']==[value];return name,state
 def contour(name,surf,field):
  g=s.settings.results.graphics;g.contour.create(name=name);c=s.settings.results.graphics.contour[name];assert field in c.field.allowed_values()
  c.set_state({'field':field,'surfaces_list':[surf],'filled':True,'node_values':False,'draw_mesh':False,'range_options':{'global_range':False,'auto_range':True}});c.range_options.compute();return c,c.range_options.get_state()
 y=2.4272831100788324
 if args.ranges_from:
  prior=json.loads(args.ranges_from.read_text())
  for label,m,tag,n in specs:assert prior['sources'][label]['case']==m['pairs'][tag] and prior['sources'][label]['iteration']==n
  ranges=prior['speed_discovery'];record['range_provenance']=str(args.ranges_from)
 else:
  for spec in specs:
   load(spec);signal.alarm(100);surf,_=surface('y',y);name='g3-range-'+stamp; c,obs=contour(name,surf,'velocity-magnitude');ranges[spec[0]]=obs;s.settings.results.graphics.contour.delete(name_list=[name]);persist()
 speedmax=math.ceil(max(v['maximum'] for v in ranges.values())/10)*10;record['shared_ranges']={'phase-2-vof':[0,1],'velocity-magnitude':[0,speedmax]};record['speed_discovery']=ranges
 for spec in specs:
  load(spec);label,m,tag,n=spec
  scenes=[('hot','y',y,'phase-2-vof'),('hot','y',y,'velocity-magnitude')]
  if n==5000:scenes.append(('axial','x',0.,'phase-2-vof'))
  for plane,axis,value,field in scenes:
   signal.alarm(100);surf,ss=surface(axis,value);slug=label+'-'+plane+('-liquid' if field=='phase-2-vof' else '-speed');name=('t100' if label.startswith('T100-') else 't020' if label.startswith('T020-') else 'np' if label.startswith('NPHASE-') else 'f20' if label.startswith('CFL20-') else 'f200' if label.startswith('CFL200-') else 'c' if label.startswith('COUPLED') else 'd' if label.startswith('DIAG') else 'o')+str(n)+('-h' if axis=='y' else '-x')+('-vf' if field=='phase-2-vof' else '-u');c,obs=contour(name,surf,field);lo,hi=record['shared_ranges'][field];assert obs['minimum']>=lo-1e-6 and obs['maximum']<=hi+1e-6
   c.range_options.set_state({'global_range':False,'auto_range':False,'minimum':lo,'maximum':hi,'clip_to_range':False});c.colorings.set_state({'banded':False,'smooth':True});c.color_map.set_state({'color':'sequential-viridis','size':11,'log_scale':False,'format':'%0.2f' if field=='phase-2-vof' else '%0.0f','font_automatic':False,'font_size':24 if axis=='y' else 18,'visible':True})
   g=s.settings.results.graphics;g.windows.logo=False;g.windows.text.visible=False;pic=g.picture;pic.use_window_resolution=False;pic.landscape=axis=='y';pic.x_resolution=2400 if axis=='y' else 1600;pic.y_resolution=1800 if axis=='y' else 2400;c.display();view=g.views;view.auto_scale()
   target=[.3,y,-1.] if axis=='y' else [0,2.755,0];pos=[.3,y+20,-1.] if axis=='y' else [20,2.755,0];up=[0,0,-1] if axis=='y' else [0,1,0];size=[1.0,.8] if axis=='y' else [6.,10.2]
   view.camera.projection(type='orthographic');view.camera.position(xyz=pos);view.camera.target(xyz=target);view.camera.up_vector(xyz=up);view.camera.field(width=size[0],height=size[1]);viewname='g3-'+stamp+'-'+name;view.save_view(view_name=viewname);remoteview=ROOT+'/exports/'+viewname+'.vw';view.write_views(file_name=remoteview,view_list=[viewname]);(out/(slug+'.vw')).write_text(read_text(s,remoteview))
   remote=ROOT+'/exports/'+viewname+'.png';assert not remote_file_exists(s,remote);pic.save_picture(file_name=remote);local=out/(slug+'.png');sha,dim=transfer(remote,local)
   record['figures'].append({'label':label,'iteration':n,'plane':plane,'surface_state':ss,'field':field,'units':'1' if field=='phase-2-vof' else 'm/s','observed_range':obs,'range_options':c.range_options.get_state(),'contour_state':c.get_state(),'picture_state':pic.get_state(),'camera':{'position':pos,'target':target,'up':up,'field':size,'view_file':str(out/(slug+'.vw'))},'local_file':str(local),'remote_file':remote,'sha256':sha,'dimensions':dim,'visual_qa':'PENDING'});persist();g.contour.delete(name_list=[name]);print('exported',slug,flush=True)
 load(specs[0]);assert math.isclose(s.settings.setup.named_expressions['P7bWaterVolume'].get_value(),expected,rel_tol=1e-12);record['restored_endpoint']=current['pairs']['final'];record['status']='NATIVE_EXPORTS_COMPLETE_VISUAL_QA_PENDING';persist();s.transcript.stop();signal.alarm(0);print('COMPLETE',out,flush=True)
if __name__=='__main__':main()

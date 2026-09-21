"""Stage approved unhooked collector expressions; compare native phase velocities.

No solve, C dependency, or source attachment. Current clean N3 case is preserved.
"""
from pathlib import Path
import json,signal,sys
BASE=Path(__file__).resolve().parents[2];sys.path.insert(0,str(BASE/'src'))
from dotenv import load_dotenv
load_dotenv(BASE/'.env')
from pyansys_fluent.connection import connect
ZONE='simple-spiral-separator--brine-outlet-'
def main():
 p=BASE/'output/phase07b_preparation'; old=json.loads((p/'diagnostic-expressions.json').read_text()); r={'scientific_screen':False,'source_attachment':False,'expressions':{},'velocity_comparison':{}}
 def persist(): (p/'clean-expression-validation.json').write_text(json.dumps(r,indent=2,default=str)+'\n')
 signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError('API deadline')));signal.alarm(30);s=connect(server_id=1,start_transcript=False,tcp_timeout_seconds=5);signal.alarm(0)
 assert s.settings.setup.named_expressions['P7bGlobalIteration'].get_value()==3
 assert s.settings.setup.user_defined.auto_compile_compiled_functions() is False
 for ph in ['mixture','phase-1','phase-2']: assert not s.settings.setup.cell_zone_conditions.fluid[ZONE].phase[ph].sources.enable()
 for name,entry in old['expressions'].items():
  ex=s.settings.setup.named_expressions
  if name not in ex.get_object_names(): ex.create(name=name)
  ex[name].definition=entry['definition'];assert ex[name].definition()==entry['definition']
  v={'definition':entry['definition']}
  if any(x in name for x in ['Count','Volume','LiquidIn','Integral']): v['value']=ex[name].get_value()
  r['expressions'][name]=v;persist()
 print('EXPRESSIONS_STAGED',flush=True)
 for component,nativefield in zip('xyz',['phase-2-x-velocity','phase-2-y-velocity','phase-2-z-velocity']):
  report='p7b-clean-phase-'+component
  rv=s.settings.solution.report_definitions.volume
  if report not in rv.get_object_names(): rv.create(name=report)
  rv[report].report_type='volume-integral'
  allowed=rv[report].field.allowed_values()
  if nativefield not in allowed:
   r['velocity_comparison'][component]={'status':'FIELD_UNAVAILABLE','candidate':nativefield,'velocity_fields':[v for v in allowed if 'velocity' in v]};persist();continue
  rv[report].field=nativefield;rv[report].cell_zones=[ZONE]
  ename='P7bLiquidVelocityIntegral'+component.upper();ex=s.settings.setup.named_expressions
  ex.create(name=ename);ex[ename].definition=f'VolumeInt(Velocity(phase="phase-2").{component},["{ZONE}"])'
  dname='P7bSlipMagnitudeIntegral'+component.upper();ex.create(name=dname);ex[dname].definition=f'VolumeInt(abs(Velocity(phase="phase-2").{component}-Velocity(phase="mixture").{component}),["{ZONE}"])'
  r['velocity_comparison'][component]={'native':s.settings.solution.report_definitions.compute(report_defs=[report]),'expression':ex[ename].get_value(),'liquid_mixture_absolute_difference_integral':ex[dname].get_value(),'native_state':rv[report].get_state()};persist();print(component,r['velocity_comparison'][component],flush=True)
 r['global_iteration']=s.settings.setup.named_expressions['P7bGlobalIteration'].get_value();persist()
if __name__=='__main__':main()

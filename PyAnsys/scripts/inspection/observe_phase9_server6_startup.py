"""Observe Server 6 transcript streaming; send no case, setting or solve changes."""
from pathlib import Path
import json,math,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server6_997k_common import attach,run,OUT
from pyansys_fluent.ewf_staged import FILM,residuals

def main():
 s=attach();stamp=str(time.time_ns());path=OUT/('startup-stream-'+stamp+'.trn')
 s.transcript.start(file_name=str(path),write_to_stdout=False)
 print('STARTUP_TRANSCRIPT_SUBSCRIBED',str(path),flush=True)
 deadline=time.monotonic()+300
 try:
  while time.monotonic()<deadline:
   contents=path.read_text(errors='replace') if path.exists() else ''
   rows=[tuple(map(float,m.groups())) for m in FILM.finditer(contents)]
   iterations=residuals(contents)
   if rows:
    first=rows[0]
    if not math.isclose(first[0],.0006501,abs_tol=1e-10) or not math.isclose(first[1],1e-7,abs_tol=1e-14):
     raise RuntimeError('Observed startup film clock/step differs from selected origin')
    r={'status':'FILM_ADVANCEMENT_OBSERVED','server_id':'6','mesh_cells':997604,
       'parent_native_iteration':8080,'film_time_s':rows[-1][0],
       'film_step_s':rows[-1][1],'peak_observed_courant':max(x[2] for x in rows),
       'observed_film_updates':len(rows),'observed_native_iteration':max(iterations) if iterations else None,
       'transcript':str(path),'observer_mutations':0,'run_complete':False}
    run.dump(OUT/'startup-observation.json',r);print(json.dumps(r,indent=2),flush=True);return
   time.sleep(1)
  run.dump(OUT/'startup-observation.json',{'status':'NO_FILM_ADVANCEMENT_OBSERVED_WITHIN_STARTUP_WINDOW','server_id':'6','transcript':str(path),'observer_mutations':0})
 finally:s.transcript.stop()

if __name__=='__main__':main()

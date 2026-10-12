"""Finish partial preservation after laptop closure; never interrupt or solve."""
import json,time
from phase9_server6_slit_common import attach,run,OUT
from run_phase9_server6_slit_ewf import lane_save

def main():
 state=json.loads((OUT/'from4235-partial-preservation.json').read_text())
 assert state['status']=='OWNED_WAITER_CANCELLED_INTERRUPT_PENDING' and state['interrupt_submitted']
 s=attach();control=s.settings.solution.run_calculation
 run.require_idle(s);assert not control.iterating() and control.iterate.is_active()
 assert run.native_iteration(s)==71313
 tag=str(time.time_ns())
 state['resumed_after_laptop_closure']=True
 state['additional_interrupt_submitted']=False
 run.dump(OUT/'from4235-partial-preservation.json',state)
 # Wait for native journal completion/idle; no replay of interrupted iterations.
 for attempt in range(36):
  try:
   run.require_idle(s)
   if control.iterating():raise RuntimeError('still iterating')
   n=run.native_iteration(s);clock=run.film(s)['film_elapsed_time'];time.sleep(2)
   if n!=run.native_iteration(s) or abs(clock-run.film(s)['film_elapsed_time'])>1e-12:raise RuntimeError('clock changing')
   break
  except RuntimeError:
   time.sleep(5)
 else:raise RuntimeError('Native idle unconfirmed; do not load or replay')
 first=lane_save(s,run.WORK/'slit154k/ewf-200ms',f'preserved-first-before-42p35ms-N{n}-{tag}')
 state.update(status='FIRST_PARTIAL_PAIR_SAVED',first_pair=first);run.dump(OUT/'from4235-partial-preservation.json',state)
 # Saving flushes any final EWF clock update after interrupt; capture stable state.
 n=run.native_iteration(s);clock=run.film(s)['film_elapsed_time'];time.sleep(3)
 assert run.native_iteration(s)==n and abs(run.film(s)['film_elapsed_time']-clock)<1e-12
 pair=lane_save(s,run.WORK/'slit154k/ewf-200ms',f'preserved-stable-before-42p35ms-N{n}-{tag}')
 assert run.native_iteration(s)==n and abs(run.film(s)['film_elapsed_time']-clock)<1e-12
 if s.settings.file.stop_transcript.is_active():s.settings.file.stop_transcript()
 run.load(s,pair);assert run.native_iteration(s)==n and abs(run.film(s)['film_elapsed_time']-clock)<1e-12
 state.update(status='PARTIAL_NATIVE_ENDPOINT_PRESERVED_IDLE',native_iteration=n,film=run.film(s),pair=pair,reopen_verified=True,no_solve_replay=True)
 run.dump(OUT/'from4235-partial-preservation.json',state)
 print('PARTIAL_NATIVE_ENDPOINT_PRESERVED_IDLE',n,clock,flush=True)
if __name__=='__main__':main()

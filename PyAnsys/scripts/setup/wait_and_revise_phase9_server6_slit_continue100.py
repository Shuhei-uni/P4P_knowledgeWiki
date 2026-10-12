"""Host-local boundary wait; revise once after the orphan native journal ends."""
import time,traceback
from phase9_server6_slit_common import OUT,run
from pyansys_fluent.stage4_native import exclusive_writer_lock
import revise_phase9_server6_slit_continue100 as revision

def main():
    with exclusive_writer_lock(OUT/'target100-transition.lock'):
        receipt=OUT/'target100-transition.json'
        run.dump(receipt,{'status':'WAITING_NATIVE_BOUNDARY','target_film_s':.1,'requested_step_s':1e-6,'requested_courant_ceiling':.8,'never_exit_fluent':True})
        while True:
            try:
                revision.main()
            except RuntimeError as exc:
                if 'busy; no mutation submitted' in str(exc):
                    time.sleep(30)
                    continue
                run.dump(receipt,{'status':'BLOCKED','error':traceback.format_exc(),'solve_replay_authorized':False})
                raise
            except BaseException:
                run.dump(receipt,{'status':'BLOCKED','error':traceback.format_exc(),'solve_replay_authorized':False})
                raise
            else:
                run.dump(receipt,{'status':'CONTINUE100_CONTROLLER_DISPATCHED','target_film_s':.1,'next_case':'angle213k_after_verified_vertical_completion'})
                return

if __name__=='__main__':main()

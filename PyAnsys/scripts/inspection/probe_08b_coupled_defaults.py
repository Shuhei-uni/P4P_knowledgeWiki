"""Read-only-artifact probe of controls changed by the intended Coupled switch."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts/setup'),str(ROOT/'src')]
import run_phase9_mesh_startup as run


def main():
    s=run.previous.attach()
    if not s.settings.solution.run_calculation.iterate.is_active():raise RuntimeError('Require idle Server 3')
    child=json.loads((run.OUT/'342k-prepared.json').read_text())
    path=run.OUT/'raw/08b-settings-audit/08b-coupled-global-default-probe.json'
    if path.exists():raise FileExistsError(path)
    try:
        s.settings.file.read_case(file_name=str(run.SHARED/'P4P-Fluent-Artifacts/08b/TwoPhaseInletV2(Purnanto).cas.h5'))
        before={'controls':s.settings.solution.controls.get_state(),'domains':s.rp_vars('domains'),
                'multiphase_native':{k:v for k,v in s.rp_vars().items() if k.startswith('mp/')}}
        s.settings.solution.methods.p_v_coupling.flow_scheme='Coupled'
        s.settings.solution.methods.pseudo_time_method.formulation.coupled_solver='global-time-step'
        after={'controls':s.settings.solution.controls.get_state(),'domains':s.rp_vars('domains'),
               'methods':s.settings.solution.methods.get_state()}
        run.dump(path,{'before':before,'after':after,'solves':0,'reference_file_modified':False})
        print('COUPLED_DEFAULT_PROBE_CAPTURED',flush=True)
    finally:run.load(s,child['pair'])
    run.require_match(run.base.state(s)['readback'],child['state']['readback'])
    print('PHASE9_RESTORED',flush=True)


if __name__=='__main__':main()

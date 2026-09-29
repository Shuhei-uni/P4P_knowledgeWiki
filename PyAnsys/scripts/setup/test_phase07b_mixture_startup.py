"""Offline E8 guards: real stage columns, continuity, and prospective gate."""
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from run_phase07b_mixture_startup import ACTIVE_FLOW, ACTIVE_FULL, SLIP_VARIABLES, conditioning_gate, parse_stage_residuals, verify_frozen_phase_arrays


class StageEvidenceTests(unittest.TestCase):
    def transcript(self, root, equations, indices, values=None):
        p=Path(root)/'native.trn'; ordered=sorted(equations)
        lines=['iter '+' '.join(ordered)+' time/iter']
        for n in indices:
            row=(values or {}).get(n,[1e-4]*len(ordered))
            lines.append(str(n)+' '+' '.join(map(str,row))+' 0:00:01 1')
        p.write_text('\n'.join(lines)+'\n'); return p

    def test_six_real_columns_only(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.transcript(root,ACTIVE_FLOW,range(1,201))
            data,audit=parse_stage_residuals(p,'conditioning',0,200)
            self.assertEqual(set(data),ACTIVE_FLOW|{'iteration'})
            self.assertEqual(audit['inactive_native_columns'],[])

    def test_native_inactive_columns_not_synthesized_or_gated(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.transcript(root,ACTIVE_FULL,range(1,201))
            data,audit=parse_stage_residuals(p,'conditioning',0,200)
            self.assertEqual(set(data),ACTIVE_FLOW|{'iteration'})
            self.assertEqual(audit['inactive_native_columns'],['vf-phase-1','vf-phase-2'])

    def test_missing_or_conflicting_active_row_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            for indices,values in [(list(range(1,200)),None),([1,2,2,3],None)]:
                p=self.transcript(root,ACTIVE_FLOW,indices,values)
                if indices[-1]==3:
                    with p.open('a') as f:f.write('2 '+' '.join(['.3']*6)+' 0:00:01 1\n')
                with self.assertRaises(AssertionError):parse_stage_residuals(p,'conditioning',0,200 if indices[-1]==199 else 3)

    def test_full_stage_requires_eight_and_original_indices(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.transcript(root,ACTIVE_FULL,range(200,501))
            data,audit=parse_stage_residuals(p,'full',200,500)
            self.assertEqual(data['iteration'][0],201); self.assertEqual(audit['excluded_start_boundary'][0]['iteration'],200)
            p=self.transcript(root,ACTIVE_FLOW,range(201,501))
            with self.assertRaises(AssertionError):parse_stage_residuals(p,'full',200,500)

    def fixture(self):
        n=200
        h={'iteration':np.arange(1,n+1),'p7bappliedsource':np.zeros(n),
           'p7bmixtureliquidinlet':np.full(n,120.),'p7bmixturesteaminlet':np.full(n,80.),
           'p7bmixtureoutlet':np.full(n,-200.),'p7bmixturebrinewall':np.zeros(n),
           'p7bdropliquid':np.full(n,500.),'p7bdropsteam':np.full(n,400.),'p7bmaximumspeed':np.full(n,60.)}
        r={k:np.full(n,1e-4) for k in ACTIVE_FLOW};r['iteration']=np.arange(1,n+1)
        return h,r

    def test_gate_pass_and_strict_residual_threshold(self):
        h,r=self.fixture();self.assertTrue(conditioning_gate(h,r,200)['passed'])
        r['continuity'][-1]=1e-3;self.assertFalse(conditioning_gate(h,r,200)['passed'])

    def test_signed_cancellation_cannot_pass_closure(self):
        h,r=self.fixture();h['p7bmixtureoutlet'][-100:]+=np.tile([4.,-4.],50)
        gate=conditioning_gate(h,r,200)
        self.assertEqual(gate['mixture_closure_mean_absolute_percent_feed'],2.)
        self.assertFalse(gate['passed'])

    def test_unstable_pressure_or_speed_rejected(self):
        for key in ['p7bdropliquid','p7bdropsteam','p7bmaximumspeed']:
            h,r=self.fixture();h[key][-100:]*=1.03
            self.assertFalse(conditioning_gate(h,r,200)['passed'])

    def test_missing_scalar_index_rejected(self):
        h,r=self.fixture();h={k:v[:-1] for k,v in h.items()}
        with self.assertRaises(AssertionError):conditioning_gate(h,r,200)

    def test_actual_slip_mutation_rejected_derived_velocity_allowed(self):
        base={}
        for ph in ['mixture','phase-1','phase-2']:
            for var in SLIP_VARIABLES+(['SV_VOF','SV_U','SV_V','SV_W'] if ph!='mixture' else []):
                base[f'z0_{ph}_{var}']=np.zeros(3)
        current={k:v.copy() for k,v in base.items()}
        current['z0_phase-2_SV_U'][:]=3.
        self.assertTrue(verify_frozen_phase_arrays(current,base,['zone'])['actual_stored_slip_exact'])
        current['z0_phase-2_SV_SLIP_U'][0]=1e-12
        with self.assertRaises(AssertionError):verify_frozen_phase_arrays(current,base,['zone'])


if __name__=='__main__':unittest.main()

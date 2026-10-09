"""Regression checks for scientific gates and safe native-journal ordering."""
from pathlib import Path
import importlib.util
import math
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from pyansys_fluent import ewf_staged as p


def window(mass=50., outlet=-1., collector=20., pressure=1000.):
    h = {n: [0.]*1000 for n in p.BULK}
    h.update({'v2-total-liquid-mass': [mass]*1000,
              'v2-flux-phase2-steamoutlet': [outlet]*1000,
              'p72-contact-removal': [collector]*1000,
              'v2-applied-absorber': [-collector]*1000,
              'p72s3-pressure-inlet': [pressure]*1000,
              'p72s3-pressure-outlet': [0.]*1000})
    return {'histories': h, 'residuals': {i: {'continuity': .001, 'vf-phase-2': .002} for i in range(1000)}}


def evidence(count=1000, dt=1e-6, start=8000):
    names = list(dict.fromkeys(p.BULK+p.FILM_REPORTS))
    initial = {n: 0. for n in names}
    initial.update({'p72d-total-mass': .01, 'p72d-upper-mass': .01})
    h = {n: {i: 0. for i in range(start+1, start+count+1)} for n in names}
    for j, i in enumerate(range(start+1, start+count+1), 1):
        h['p72d-total-mass'][i] = .01+.1*j*dt
        h['p72d-upper-mass'][i] = h['p72d-total-mass'][i]
        h['p72d-total-secondary'][i] = .1
        h['p72d-total-thickness'][i] = 1e-4
        h['p72r-film-speed-max'][i] = 5.
        h['p72d-total-courant'][i] = .01
    text = ''.join(f'Film time = {j*dt:.14g} with timestep = {dt:.14g}, (max_cfl: 0.01)\n' for j in range(1,count+1))
    return text, h, initial


class PolicyTests(unittest.TestCase):
    def test_ladder_clock_and_final_reserve(self):
        self.assertAlmostEqual(sum(s.duration for s in p.LADDER), .019)
        self.assertEqual(sum(s.count for s in p.LADDER), 5000)
        self.assertAlmostEqual(3000*10e-6, .03)

    def test_refresh_preserves_physical_dpm_time(self):
        for block in p.LADDER:
            d = p.refresh_plan(block.dt)
            self.assertEqual(d['film-per-flow-iters'], 1)
            self.assertEqual(d['sub-time-steps'], 1)
            self.assertAlmostEqual(d['iters-per-dpm-step']*block.dt, 20e-6)
            self.assertLessEqual(block.dt/.0015, .01)
        with self.assertRaises(ValueError): p.refresh_plan(20e-6)
        # A separately qualified particle interval changes tracking cadence,
        # while film/drain refresh remains one update per flow iteration.
        d = p.refresh_plan(10e-6,200e-6)
        self.assertEqual(d['iters-per-dpm-step'],20)
        self.assertEqual(d['sub-time-steps'],1)
        self.assertEqual(d['film-per-flow-iters'],1)

    def test_bulk_gate_requires_three_complete_windows(self):
        self.assertFalse(p.bulk_gate([window(),window()],116.92,1)['pass'])
        self.assertTrue(p.bulk_gate([window(),window(),window()],116.92,1)['pass'])

    def test_bulk_drift_cannot_be_hidden_by_small_residuals(self):
        self.assertFalse(p.bulk_gate([window(50),window(51),window(52)],116.92,1)['pass'])
        self.assertFalse(p.bulk_gate([window(outlet=-1),window(outlet=-1.1),window(outlet=-1.2)],116.92,1)['pass'])

    def test_collector_must_match_applied_source(self):
        windows = [window(),window(),window()]
        windows[-1]['histories']['v2-applied-absorber'][-1] = -10.
        self.assertFalse(p.bulk_gate(windows,116.92,1)['pass'])

    def test_invalid_residuals_forbid_freeze(self):
        windows = [window(),window(),window()]
        windows[-1]['residuals'][999]['continuity'] = float('nan')
        self.assertFalse(p.bulk_gate(windows,116.92,1)['pass'])

    def test_source_ledger_and_missing_inner_claim(self):
        text,h,initial = evidence()
        a = p.assess_block(text,h,initial,8000,1000,1e-6,0)
        self.assertTrue(a['pass'])
        self.assertLess(a['ledger_fraction'], 1e-10)
        self.assertEqual(a['inner_convergence'], 'UNAVAILABLE_OR_INCOMPLETE_CLAIM_LIMIT')
        h['p72d-total-mass'][9000] += .01
        self.assertIn('FILM_LEDGER_OPERATING_LIMIT',p.assess_block(text,h,initial,8000,1000,1e-6,0)['failures'])

    def test_every_sample_checked_not_only_endpoint(self):
        text,h,initial = evidence()
        text = text.replace('(max_cfl: 0.01)','(max_cfl: 1.1)',1)
        self.assertIn('COURANT_OPERATING_CEILING',p.assess_block(text,h,initial,8000,1000,1e-6,0)['failures'])
        h['p72d-total-thickness'][8001] = .3
        self.assertIn('THICKNESS_LIMIT',p.assess_block(text,h,initial,8000,1000,1e-6,0)['failures'])

    def test_verified_net_source_basis_retains_original_and_detects_storage_error(self):
        text,h,initial = evidence()
        # Separation has already reduced the supplied net source. Adding its
        # release counter again is rejected under the default gross basis.
        h['p72d-total-separated'][9000] = 2e-5
        self.assertIn('FILM_LEDGER_OPERATING_LIMIT',
                      p.assess_block(text,h,initial,8000,1000,1e-6,0)['failures'])
        a = p.assess_block(text,h,initial,8000,1000,1e-6,0,
                           ledger_basis='verified-v252-net-secondary')
        self.assertTrue(a['pass'])
        self.assertAlmostEqual(a['original_ledger_residual_kg'],2e-5)
        h['p72d-total-mass'][9000] += 2e-5
        self.assertIn('FILM_LEDGER_OPERATING_LIMIT',p.assess_block(
            text,h,initial,8000,1000,1e-6,0,
            ledger_basis='verified-v252-net-secondary')['failures'])

    def test_recorded_inner_failure_not_hidden_by_low_courant(self):
        text,h,initial = evidence()
        text = text.replace('Film time =','sub-iteration: 30 residual - h: 0.01; u: 0.01; v: 0.01\nFilm time =')
        a = p.assess_block(text,h,initial,8000,1000,1e-6,0)
        self.assertIn('ACHIEVED_INNER_RESIDUAL_LIMIT',a['failures'])

    def test_strict_candidate_requires_every_inner_step(self):
        text,h,initial = evidence()
        text = text.replace('Film time =','sub-iteration: 4 residual - h: 1e-8; u: 1e-8; v: 1e-8\nFilm time =')
        text = text.replace('h: 1e-8; u: 1e-8','h: 160; u: 120',1)
        self.assertTrue(p.assess_block(text,h,initial,8000,1000,1e-6,0)['pass'])
        a = p.assess_block(text,h,initial,8000,1000,1e-6,0,require_all_inner=True)
        self.assertIn('ALL_INNER_STEPS_REQUIRED',a['failures'])
        self.assertEqual(a['inner_steps_passed'],999)
        self.assertEqual(a['inner_convergence'],'FAILED_OR_MISSING_REQUIRED_STEP')

    def test_horizon_and_missing_history_rejected(self):
        text,h,initial = evidence()
        with self.assertRaises(ValueError): p.assess_block(text,h,initial,8000,1000,2e-6,0)
        del h['p72d-total-mass'][8050]
        with self.assertRaises(ValueError): p.assess_block(text,h,initial,8000,1000,1e-6,0)

    def test_journal_saves_then_stops_then_signals(self):
        text = p.journal('C:/work',1000,9000,token='unique')
        self.assertEqual(text.count('/solve/iterate '),1)
        self.assertLess(text.index('/solve/iterate'),text.index('/file/write-case-data'))
        self.assertLess(text.index('/file/write-case-data'),text.index('/file/stop-transcript'))
        self.assertLess(text.index('/file/stop-transcript'),text.index('returned.txt'))
        self.assertLess(text.index('returned.txt'),text.index('P72STAGED_RETURNED_unique'))
        self.assertNotIn('/exit',text)
        with self.assertRaises(ValueError): p.journal('C:/work',1000,9000,token='bad"token')


class NativeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0,str(ROOT/'scripts/setup'))
        spec = importlib.util.spec_from_file_location('staged_runner',ROOT/'scripts/setup/run_phase72a_staged_ewf.py')
        cls.module = importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.module)

    def test_unconfirmed_native_return_blocks_settings_even_in_recovery(self):
        owner = self.module.Runner.__new__(self.module.Runner)
        owner.native_pending = True
        owner.s = Mock()
        with self.assertRaises(RuntimeError):owner.idle()
        owner.s.settings.solution.run_calculation.iterating.assert_not_called()

    def test_finite_age_with_failed_bulk_gate_does_not_require_freeze(self):
        import run_phase72a_direct_development as direct
        owner = direct.DirectDevelopment.__new__(direct.DirectDevelopment)
        owner.production = True
        owner.dt = 10e-6
        owner.m = {'target_film_clock_s': .300}
        owner.spec = {'liquid_feed_kg_s':116.92}
        owner.pressure_floor = 1.
        owner.s = Mock()
        owner.clock = Mock(side_effect=[.299,.309])
        owner.batch = Mock(return_value={'assessment':window()})
        owner.save = Mock()
        owner.flush = lambda **kw: owner.m.update(kw)
        with patch.object(direct.r.base,'native_iteration',return_value=50000):
            owner.stabilize('C_TEST')
        self.assertTrue(owner.m['finite_cutoff_reached_active_bulk'])
        self.assertFalse(owner.m['bulk_stability_qualified'])
        owner.batch.assert_called_once_with(1000,'C_TEST')
        owner.s.settings.solution.controls.equations.set_state.assert_not_called()

    def test_batch_has_no_settings_or_scheme_reads_while_native_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            owner = self.module.Runner({'work':'C:/work','output':tmp,'parent_pair':{},'native_block_timeout_s':10})
            owner.dt = 1e-6;owner.names = list(dict.fromkeys(p.BULK+p.FILM_REPORTS))
            owner.s = Mock();events=[];files={};passive={};text,h,initial=evidence()
            owner.m['native_return_seen'] = True  # Previous block's receipt.
            owner.values = lambda:initial
            owner.clock = lambda: .001 if passive.get('complete') else 0.
            def iterating():
                self.assertFalse(owner.native_pending);events.append('idle-read');return False
            owner.s.settings.solution.run_calculation.iterating.side_effect=iterating
            owner.s.settings.solution.controls.equations.get_state.side_effect=lambda:{'flow':True}
            def start_stream(file_name,write_to_stdout):
                passive['path']=Path(file_name);passive['path'].write_text('');events.append('stream-start')
            owner.s.transcript.start.side_effect=start_stream
            def dispatch(*args,**kwargs):
                self.assertTrue(owner.native_pending);events.append('dispatch')
                self.assertFalse(owner.m['native_return_seen'])
                self.assertTrue(kwargs['wait'])
                with self.assertRaises(RuntimeError): owner.idle()
                token=Path(owner.m['active_block']).name
                passive['path'].write_text('P72STAGED_RETURNED_'+token)
                passive['complete']=True;events.append('native-return')
            owner.s.scheme.exec.side_effect=dispatch
            def reader(s,path):
                self.assertFalse(owner.native_pending)
                if path.endswith('returned.txt'): return 'NATIVE_COMMAND_RETURNED'
                if path.endswith('native-run.trn'): return text
                for n in owner.names:
                    if path.endswith(n+'.out'):return ''.join(f'{i} {v:.17g}\n' for i,v in h[n].items())
                raise AssertionError(path)
            with patch.object(self.module.r.base,'native_iteration',side_effect=lambda s:9000 if passive.get('complete') else 8000), \
                 patch.object(self.module.r.base,'ensure_remote_directory'), \
                 patch.object(self.module.r,'instrument',side_effect=lambda s,folder,names:{n:str(folder/(n+'.out')) for n in names}), \
                 patch.object(self.module,'configure_autosave'), \
                 patch.object(self.module.r,'write_ascii_text_new'), \
                 patch.object(self.module.r,'read_text',side_effect=reader), \
                 patch.object(self.module.r.base,'checked_remote_sha256',return_value='a'*64), \
                 patch.object(self.module,'PassiveProgress'):
                record=owner.batch(1000,'test')
            self.assertTrue(record['assessment']['pass'])
            self.assertLess(events.index('stream-start'),events.index('dispatch'))
            self.assertLess(events.index('dispatch'),events.index('native-return'))
            self.assertNotIn('idle-read',events[events.index('dispatch')+1:events.index('native-return')])


if __name__ == '__main__':unittest.main()

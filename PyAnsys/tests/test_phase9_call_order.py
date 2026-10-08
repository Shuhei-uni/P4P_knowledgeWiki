"""Safety barriers for the Phase 9 controller; no live Fluent calls."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/setup'))
import run_phase9_mesh_startup as r

class Ordering(unittest.TestCase):
    def solver(self,busy=False):
        return NS(settings=NS(setup=NS(cell_zone_conditions=NS(is_active=lambda:True),
                    user_defined=NS(load=Mock())),
                 solution=NS(run_calculation=NS(iterate=NS(is_active=lambda:not busy))),
                 file=NS(read_case=Mock(),read_data=Mock(),
                         start_transcript=Mock(),stop_transcript=Mock())))

    def test_busy_prevents_load_or_feed_change(self):
        s=self.solver(True)
        with patch.object(r,'remote_file_exists') as exists,patch.object(r.base,'loading') as feed:
            with self.assertRaises(RuntimeError):r.load(s,{'case':'c','data':'d'})
            with self.assertRaises(RuntimeError):r.set_loading(s,.5)
            exists.assert_not_called();feed.assert_not_called();s.settings.file.read_case.assert_not_called()

    def test_missing_data_preserves_loaded_case(self):
        s=self.solver()
        with patch.object(r,'remote_file_exists',side_effect=[True,False]),patch.object(r,'remote_chdir') as cd:
            with self.assertRaises(FileNotFoundError):r.load(s,{'case':'c','data':'d'})
            s.settings.file.read_case.assert_not_called();cd.assert_not_called()

    def test_pair_load_orders_case_library_data_then_coordinate(self):
        s=self.solver();calls=[]
        s.settings.file.read_case.side_effect=lambda **kw:calls.append('case')
        s.settings.setup.user_defined.load.side_effect=lambda **kw:calls.append('udf')
        s.settings.file.read_data.side_effect=lambda **kw:calls.append('data')
        with patch.object(r,'remote_file_exists',return_value=True),patch.object(r,'remote_chdir'),\
             patch.object(r,'native_iteration',side_effect=lambda _:calls.append('coordinate') or 3800):
            r.load(s,{'case':'c','data':'d','native_iteration':3800})
        self.assertEqual(calls,['case','udf','data','coordinate'])

    def test_wrong_loaded_coordinate_rejected(self):
        s=self.solver()
        with patch.object(r,'remote_file_exists',return_value=True),patch.object(r,'remote_chdir'),\
             patch.object(r,'native_iteration',return_value=3790):
            with self.assertRaises(RuntimeError):r.load(s,{'case':'c','data':'d','native_iteration':3800})

    def test_normal_transcript_has_one_start_and_one_stop(self):
        s=self.solver();calls=[]
        s.settings.file.start_transcript.is_active.return_value=True
        s.settings.file.start_transcript.side_effect=lambda **kw:calls.append('start')
        s.settings.file.stop_transcript.side_effect=lambda:calls.append('stop')
        with r.native_batch_transcript(s,'local.trn'):calls.append('solve')
        self.assertEqual(calls,['start','solve','stop'])

    def test_failed_cleanup_does_not_mask_solver_failure(self):
        s=self.solver();s.settings.file.start_transcript.is_active.return_value=True
        s.settings.file.stop_transcript.side_effect=RuntimeError('close failed')
        with self.assertRaisesRegex(ValueError,'solver failed'):
            with r.native_batch_transcript(s,'local.trn'):raise ValueError('solver failed')

    def test_unavailable_transcript_prevents_solve(self):
        s=self.solver();s.settings.file.start_transcript.is_active.return_value=False
        s.settings.file.stop_transcript.is_active.return_value=False
        with self.assertRaises(RuntimeError):
            with r.native_batch_transcript(s,'local.trn'):self.fail('solve executed')
        s.settings.file.start_transcript.assert_not_called()

    def test_pending_run_rejected_before_preparation_or_load(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(r,'OUT',Path(tmp)),\
             patch.object(r,'prepare_child') as prepare,patch.object(r,'load') as load:
            r.dump(Path(tmp)/'08b-settings-audit-approved.json',{'status':'APPLIED_REOPEN_VERIFIED'})
            r.dump(Path(tmp)/'342k-run.json',{'status':'RUNNING'})
            with self.assertRaises(RuntimeError):r.run_child(self.solver(),'342k')
            prepare.assert_not_called();load.assert_not_called()

    def test_bad_numerics_never_save_or_promote_endpoint(self):
        for cfl,error in [('1.2',''),('0.1','Fatal error'),('0.1','Divergence detected')]:
            with self.subTest(cfl=cfl,error=error),tempfile.TemporaryDirectory() as tmp,\
                 patch.object(r,'OUT',Path(tmp)),patch.object(r,'native_iteration',return_value=3800),\
                 patch.object(r,'assert_bulk_active'),patch.object(r.base,'iterate'),\
                 patch.object(r,'save') as save,patch.object(r,'read_text',return_value=
                    f'Film time = 0.0002221 with timestep = 1e-7, (max_cfl: {cfl})\n{error}'):
                s=self.solver();s.rp_vars=Mock(return_value=[('timestep-max',1e-7)])
                s.settings.file.start_transcript.is_active.return_value=True
                m={'label':'342k','verified_native_end':3800,'blocks':[{'film_end_s':.000222}],
                   'latest_pair':{'case':'safe','data':'safe'}}
                with self.assertRaises(RuntimeError):r.batch(s,m,1,'ramp')
                self.assertEqual(m['verified_native_end'],3800)
                self.assertEqual(m['latest_pair']['case'],'safe');save.assert_not_called()

    def test_valid_ramp_uses_transcript_clock_without_extra_film_rpc(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(r,'OUT',Path(tmp)),\
             patch.object(r,'native_iteration',return_value=3800),patch.object(r,'assert_bulk_active'),\
             patch.object(r.base,'iterate'),patch.object(r,'film') as film,\
             patch.object(r,'read_text',return_value='Film time = 0.0002221 with timestep = 1e-7, (max_cfl: 0.1)'):
            s=self.solver();s.rp_vars=Mock(return_value=[('timestep-max',1e-7)])
            s.settings.file.start_transcript.is_active.return_value=True
            m={'label':'342k','verified_native_end':3800,'blocks':[{'film_end_s':.000222}]}
            r.batch(s,m,1,'ramp',checkpoint=False)
            self.assertEqual(m['verified_native_end'],3801);film.assert_not_called()

    def test_setup_capture_keeps_campaign_stream_on_success_and_failure(self):
        for failed in [False,True]:
            with self.subTest(failed=failed),tempfile.TemporaryDirectory() as tmp:
                s=self.solver();s.transcript=NS(is_streaming=True,register_callback=Mock(return_value='step'),
                    unregister_callback=Mock(),start=Mock(),stop=Mock())
                def capture():
                    with r.client_capture(s,Path(tmp)/'step.txt'):
                        if failed:raise ValueError('setup failed')
                if failed:
                    with self.assertRaises(ValueError):capture()
                else:capture()
                s.transcript.start.assert_not_called();s.transcript.stop.assert_not_called()
                s.transcript.unregister_callback.assert_called_once_with('step')

    def test_final_feed_read_does_not_call_setter(self):
        s=self.solver()
        bc={}
        for zone,phase,value in [('liquidinlet','phase-2',116.92),('steaminlet','phase-1',80.69)]:
            bc[zone]=NS(phase={phase:NS(momentum=NS(mass_flow_rate=NS(get_state=lambda v=value:{'value':v})))})
        s.settings.setup.boundary_conditions=NS(mass_flow_inlet=bc)
        with patch.object(r.base,'loading') as setter:
            self.assertEqual(r.read_feed(s,1)['liquid_kg_s'],116.92)
            setter.assert_not_called()

    def test_server3_campaign_excludes_server4_mesh(self):
        with tempfile.TemporaryDirectory() as tmp,patch.object(r,'OUT',Path(tmp)),patch.object(r,'run_child') as run:
            r.dump(Path(tmp)/'campaign-manifest.json',{'status':'RUNNING','active_mesh':'997k',
                'mesh_order':['60k','342k','680k','997k','2_6M'],'completed':['60k','342k','680k','997k']})
            r.dump(Path(tmp)/'server-assignment.json',{'authority':'human_split',
                'server3':{'mesh_order':['60k','342k','680k','997k']}})
            r.campaign(self.solver());run.assert_not_called()
            import json
            result=json.loads((Path(tmp)/'campaign-manifest.json').read_text())
            self.assertNotIn('2_6M',result['mesh_order'])
            self.assertEqual(result['status'],'COMPLETE_PREPARATION_ONLY')

    def test_inherited_transcript_recovered_when_active_flag_is_stale(self):
        s=self.solver();s.settings.file.start_transcript.is_active.return_value=True
        s.settings.file.start_transcript.side_effect=[RuntimeError('A transcript has already been started. Error Object: #f'),None]
        with r.native_batch_transcript(s,'new.trn'):pass
        self.assertEqual(s.settings.file.start_transcript.call_count,2)
        self.assertEqual(s.settings.file.stop_transcript.call_count,2)

if __name__=='__main__':unittest.main(verbosity=2)

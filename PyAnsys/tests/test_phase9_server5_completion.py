"""Server 5 command completion and final-time checks without Fluent mutations."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts/setup')]
from phase9_server5_live_stream import journal_idle_from_attributes, read_stream_tail, wait_for_native_journal
from run_phase9_server5_342k_ewf import recovery_stages, verify_film_updates, controls_match, microseconds_to_seconds


class Completion(unittest.TestCase):
    def test_idle_requires_loaded_case_idle_solver_and_closed_transcript(self):
        good={'setup/cell-zone-conditions':True,'solution/run-calculation/iterate':True,'file/start-transcript':True,'file/stop-transcript':False}
        self.assertTrue(journal_idle_from_attributes(good))
        for key in good:
            self.assertFalse(journal_idle_from_attributes(dict(good,**{key:not good[key]})))
            self.assertFalse(journal_idle_from_attributes({k:v for k,v in good.items() if k!=key}))

    def test_missed_close_message_recovers_on_native_idle(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'live.txt';path.write_text('Film output without closure marker')
            probe=Mock(side_effect=[False,None,True]);now=[0]
            wait_for_native_journal(path,probe=probe,sleeper=lambda seconds:now.__setitem__(0,now[0]+seconds),clock=lambda:now[0])
            self.assertEqual(probe.call_count,3)
            self.assertEqual(now[0],120)

    def test_stale_close_marker_does_not_override_busy_native_state(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'live.txt';path.write_text('/file/stop-transcript\nTranscript closed.')
            probe=Mock(side_effect=[False,True]);sleep=Mock()
            wait_for_native_journal(path,probe=probe,sleeper=sleep,clock=lambda:0)
            sleep.assert_called_once_with(15)

    def test_tail_read_is_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'live.txt';path.write_bytes(b'x'*200000+b'END')
            text=read_stream_tail(path,100)
            self.assertEqual(len(text),100);self.assertTrue(text.endswith('END'))

    def test_one_us_schedule_reaches_exact_endpoints(self):
        stages=recovery_stages(.13805,1e-6)
        self.assertEqual(sum(x[1] for x in stages),61950)
        self.assertAlmostEqual(.13805+sum(x[1]*x[2] for x in stages[:-1]),.195)
        self.assertEqual(stages[-1][1:],(5000,1e-6,True))
        self.assertEqual(recovery_stages(.195,1e-6),[('bulk-reactivation-to-200ms',5000,1e-6,True)])
        self.assertEqual(recovery_stages(.2,1e-6),[])

    def test_high_courant_is_recorded_without_limit_rejection(self):
        text='Film time = 1e-1 with timestep = 1.00e-06, (max_cfl: 1551.32)'
        self.assertEqual(verify_film_updates(text,1,1e-6),1551.32)

    def test_two_point_five_us_schedule_keeps_physical_endpoints(self):
        stages=recovery_stages(.16905,2.5e-6)
        self.assertEqual(sum(x[1] for x in stages),12380)
        self.assertAlmostEqual(.16905+sum(x[1]*x[2] for x in stages[:-1]),.195)
        self.assertEqual(stages[-1][1:],(2000,2.5e-6,True))
        self.assertAlmostEqual(.16905+sum(x[1]*x[2] for x in stages),.2)

    def test_native_float_serialization_does_not_reject_correct_controls(self):
        self.assertEqual(microseconds_to_seconds(2.5),2.5e-6)
        actual={'timestep-max':2.5e-6,'iters-per-dpm-step':8}
        self.assertTrue(controls_match(actual,{'timestep-max':2.4999999999999998e-6,'iters-per-dpm-step':8}))
        self.assertFalse(controls_match(actual,{'timestep-max':1e-6,'iters-per-dpm-step':8}))
        self.assertFalse(controls_match(actual,{'timestep-max':2.5e-6,'iters-per-dpm-step':20}))


if __name__=='__main__':unittest.main()

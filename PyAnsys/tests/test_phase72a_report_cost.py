"""Check required evidence and report ownership before the report-cost screen."""
from pathlib import Path, PureWindowsPath
from types import SimpleNamespace
from unittest.mock import Mock
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/setup"))
import run_phase72a_stage4_report_cost as runner


class ReportCostTests(unittest.TestCase):
    def state(self):
        definitions = sorted(runner.CORE) + ["bulk-" + str(i) for i in range(43)]
        return {"file-" + str(i): {"report_defs": [name], "active": True,
                                  "file_name": "C:/original/" + name + ".out"}
                for i, name in enumerate(definitions)}

    def test_core_keeps_guards_and_ledger_and_disables_other_writers(self):
        updates, paths = runner.report_plan(self.state(), PureWindowsPath('C:/run/monitors'), runner.CORE)
        self.assertEqual(set(paths), runner.CORE)
        self.assertEqual(sum(item['active'] for item in updates.values()), 17)
        for name in ['p72d-total-courant', 'p72d-total-thickness', 'p72d-drain-rate',
                     'p72d-total-secondary', 'p72d-total-dpm']:
            self.assertIn(name, paths)
        self.assertTrue(all(item.get('frequency') == 1 for item in updates.values() if item['active']))

    def test_missing_ledger_definition_rejects_plan_before_mutation(self):
        state=self.state();state.pop('file-0')
        with self.assertRaisesRegex(RuntimeError, 'Missing core'):
            runner.report_plan(state, PureWindowsPath('C:/run/monitors'), runner.CORE)

    def test_core_selection_is_identical_for_prepared_and_solve_destinations(self):
        for folder in ['C:/run/core17/prepared-monitors', 'C:/run/core17/run-N41503-N42503/monitors']:
            state=self.state()
            updates, paths=runner.report_plan(state, PureWindowsPath(folder), runner.CORE)
            actual={name:{**item, **updates[name]} for name,item in state.items()}
            files=Mock();files.get_state.side_effect=[state,actual]
            solver=SimpleNamespace(settings=SimpleNamespace(solution=SimpleNamespace(
                monitor=SimpleNamespace(report_files=files, report_plots=SimpleNamespace(get_state=lambda:{})))))
            self.assertEqual(set(runner.instrument(solver, PureWindowsPath(folder))), runner.CORE)


if __name__ == '__main__':
    unittest.main()

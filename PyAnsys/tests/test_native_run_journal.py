from __future__ import annotations

import unittest

from pyansys_fluent.native_run_journal import (
    SteadyNativeRunJournal,
    render_steady_native_run_journal,
)


class NativeRunJournalTests(unittest.TestCase):
    def test_renders_fluent_owned_run_with_transcript_and_residual_export(self) -> None:
        text = render_steady_native_run_journal(
            SteadyNativeRunJournal(
                iterations=5000,
                transcript_file=r"C:\FluentRuns\09cV3\run.trn",
                residual_file=r"C:\FluentRuns\09cV3\residuals.out",
                residual_history_size=6000,
            )
        )

        self.assertIn('/file/start-transcript "C:/FluentRuns/09cV3/run.trn"', text)
        self.assertIn("/solve/monitors/residual/print? yes", text)
        self.assertIn("/solve/monitors/residual/n-save 6000", text)
        self.assertIn("/solve/iterate 5000", text)
        self.assertIn('/plot/residuals-set/plot-to-file "C:/FluentRuns/09cV3/residuals.out"', text)
        self.assertIn("/file/stop-transcript", text)
        self.assertNotIn("exit", text.lower())

    def test_preserves_loaded_residual_history_size_when_omitted(self) -> None:
        text = render_steady_native_run_journal(
            SteadyNativeRunJournal(
                iterations=100,
                transcript_file=r"D:\runs\run.trn",
                residual_file=r"D:\runs\residuals.out",
                plot_residuals=False,
            )
        )

        self.assertNotIn("n-save", text)
        self.assertIn("/solve/monitors/residual/plot? no", text)

    def test_rejects_non_windows_or_unsafe_paths(self) -> None:
        bad_paths = [
            "/tmp/run.trn",
            "relative\\run.trn",
            'C:\\runs\\bad"name.trn',
            "C:\\runs\\bad\nname.trn",
        ]
        for path in bad_paths:
            with self.subTest(path=path), self.assertRaises(ValueError):
                render_steady_native_run_journal(
                    SteadyNativeRunJournal(
                        iterations=10,
                        transcript_file=path,
                        residual_file=r"C:\runs\residuals.out",
                    )
                )

    def test_rejects_non_positive_counts(self) -> None:
        with self.assertRaises(ValueError):
            render_steady_native_run_journal(
                SteadyNativeRunJournal(
                    iterations=0,
                    transcript_file=r"C:\runs\run.trn",
                    residual_file=r"C:\runs\residuals.out",
                )
            )
        with self.assertRaises(ValueError):
            render_steady_native_run_journal(
                SteadyNativeRunJournal(
                    iterations=10,
                    transcript_file=r"C:\runs\run.trn",
                    residual_file=r"C:\runs\residuals.out",
                    residual_history_size=0,
                )
            )


if __name__ == "__main__":
    unittest.main()

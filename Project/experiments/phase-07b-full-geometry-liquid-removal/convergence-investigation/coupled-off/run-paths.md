# E4 execution map

Completed at N5000 with [G4 results](results.md). The original wrapper filename defect is reconciled in `PyAnsys/output/phase07b-convergence-investigation/e4/completion-reconciliation.json`; do not rerun the reconciliation or controller. E5 is the current frontier.

- Case: `S40-T020-COUPLED-OFF`.
- Run: `p7b-s40-t020-coupled-off-20260922T134224Z`.
- Scientific contract: [setup](setup.md).
- Runner: `PyAnsys/scripts/setup/run_phase07b_screen.py`, with
  `--coupled-off-capability` and `--spike-diagnostics`.
- Local run manifest, native scalar copies, transcript, exact-face flux,
  diagnostic samples, paired checkpoint map and native field arrays:
  `PyAnsys/output/p7b-s40-t020-coupled-off-20260922T134224Z/`.
- Detached worker 16444, controller 16445 at launch. Current process identity
  and lock ownership must be reconciled before any recovery; do not relaunch
  based on a stale PID alone.
- Exact launch, job manifest and runner log:
  `PyAnsys/output/phase07b-convergence-investigation/e4/`.
- Live Coupled/Off probe and restored E3 endpoint proof:
  `PyAnsys/output/phase07b-e4-control-probe-20260922T1352/receipt.json`.
  The filename is an identifier; the receipt's UTC field is the actual time.
- PC paths are unique children under the original Phase-7b local PC root,
  as recorded by the run manifest. Use Fluent API only. Never terminate Fluent.

The initial wrapper spec mistakenly required section `manifest.json` rather
than the exporter's `index.json`. Its original spec is retained as
`job-launched.yaml`; `job.yaml` has the corrected local evidence paths. The
running worker already loaded the original spec and may report BLOCKED solely
for those two paths after successful completion. **Do not rerun the controller.**
After the worker terminates, use
`PyAnsys/.venv/bin/python PyAnsys/scripts/analysis/reconcile_phase07b_e4_job.py`
to verify corrected files and the declared local verifier, retaining the
original receipt. This performs zero Fluent calls or solver iterations.

At a verified terminal disposition, run the existing case analyzer with
`--histories-only` and `compare_phase07b_solver.py` against original T020.
The latter writes E4-F1/F2 and raw CSVs but deliberately leaves G4 pending
checkpoint/snapshot audit, native spatial export/visual QA and interpretation.
The existing autonomous-investigation heartbeat continues through those steps.

During ordinary progress, `PyAnsys/scripts/analysis/audit_phase07b_running.py`
checks local checkpoint-complete scalar copies, contiguous streamed histories,
source lag, snapshot hashes/native parity and the held controller lock. Pass
the run directory and a new `--output` audit path. It creates no Fluent client
and makes no solver changes. Read freshness/lag warnings and reconcile actual
state before deciding that intervention is needed.

# Run control

Run only a case whose build receipt proves the intended experiment.

For short discovery work, keep the scientific loop close enough to inspect the
terminal evidence and choose the next probe immediately.

For long work, checkpoint and use deterministic completion proof. A process exit
code alone is not proof; verify the requested horizon and required artifacts.

Use long native solve commands while inputs stay fixed, bounded by the next
required decision. Short ramp blocks preserve the recorded inlet-change spacing;
monitoring alone does not require short solve blocks. Keep checkpoints on the
Fluent host and time solve, save, reopen and retrieval separately before claiming
a performance improvement.

Give each native batch one transcript start and one stop; close on failure while
preserving the original solver error. Reuse
`pyansys_fluent.execution_contract.native_transcript`. Test command order with
mocks and parser/monitor-reader logic with saved files before a live probe. Test
new native readers on a tiny known file with a finite bound in a recoverable
child. Prefer a simple journal for a fixed horizon; add native decision logic
only when the experiment requires it.

During maintenance of an active run, stage runtime changes without editing its
controller, watcher, imported dependencies or machine records. Deploy after
reconciling the idle session and latest endpoint. The hash-guarded
[staged update](../../../../PyAnsys/workflow_updates/20261008/README.md) is an
offline implementation for subsequent launches, not an instruction to restart
current work.

## Supervision and evidence retrieval

Use the existing watcher for continuous supervision. Inspect compact receipts
and bounded transcript tails first; use a finite Fluent query only when local
evidence cannot resolve a material uncertainty. A timeout alone does not prove
a stopped solver. Wake the agent on a new failure/stall, checkpoint decision,
completion, or explicit status request; routine progress stays in the watcher.
Deduplicate repeated events and bound health checks even while a failure persists.

`python3 PyAnsys/tools/workflow_evidence.py status <output-root>` reads local
receipts without importing a controller or connecting to Fluent. Add
`--controller-name <runner-filename>` to verify the recorded local PID. Its
observed stream position is separate from the saved/verified endpoint.

## Long-run handoff

For a detached run, create a job specification with the exact runner argv and
working directory, manifest path, required output files, optional verifier, and
originating task identity. `PyAnsys/scripts/orchestration/run_and_handoff.py`
is the repository entry point. Persist `RUNNING`, capture runner output and
return code, verify the required files and observed iteration/time horizon, then
persist `COMPLETE` or `BLOCKED` before any task wake-up or post-run analysis.

Before detaching, test both server-local execution and retrieval of the native
transcript, monitor files, terminal receipt and paired checkpoints. Record the
retrieval route and whether it survives loss of the Fluent connection. Reuse
existing host/file access; if independent access is unavailable, state that
limit rather than promising recoverable evidence after disconnection. Keep
credentials out of receipts. Validate a fixed journal and its local save paths
offline before one bounded startup check.

The completion check should establish final case/data presence and pairing,
declared monitor/report/history outputs, checkpoints required by the setup, and
consistency with the run-path map. A completed execution can still have missing
scientific evidence; make that deficiency visible in the manifest rather than
rerunning automatically.

Before launching an existing job ID, reconcile its prior manifest and process
state. Preserve the latest valid checkpoint after a crash or FPE, then let the
scientific loop choose a verified continuation or recovery route.

If the solver/session fails, preserve the latest valid checkpoint, recreate or
reconnect the session under the phase authority, and resume when scientifically
equivalent. Do not silently reinitialize a resumed calculation.

Unexpected physics or poor residuals are not execution-stop conditions unless
the experiment declared one. Let the evidence contract decide what can later be
claimed.

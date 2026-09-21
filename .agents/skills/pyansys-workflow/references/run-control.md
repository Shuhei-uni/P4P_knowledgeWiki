# Run control

Run only a case whose build receipt proves the intended experiment.

For short discovery work, keep the scientific loop close enough to inspect the
terminal evidence and choose the next probe immediately.

For long work, checkpoint and use deterministic completion proof. A process exit
code alone is not proof; verify the requested horizon and required artifacts.

## Long-run handoff

For a detached run, create a job specification with the exact runner argv and
working directory, manifest path, required output files, optional verifier, and
originating task identity. `PyAnsys/scripts/orchestration/run_and_handoff.py`
is the repository entry point. Persist `RUNNING`, capture runner output and
return code, verify the required files and observed iteration/time horizon, then
persist `COMPLETE` or `BLOCKED` before any task wake-up or post-run analysis.

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

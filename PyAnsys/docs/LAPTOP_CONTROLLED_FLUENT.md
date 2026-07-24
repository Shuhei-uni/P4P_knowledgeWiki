# Laptop-Controlled Fluent and Narrow Self-Healing Host

## Responsibility Boundary

The laptop agent owns setup planning, live Settings API/TUI work, readback
verification, checkpoint selection, recovery decisions, analysis, and
scientific interpretation.

The Fluent-PC watchdog owns only Fluent launch, process/gRPC health, bounded
restart, and publication of the current generation, host, port, and password.

The optional Fluent-PC run worker owns only explicit load, run, checkpoint, and
save requests. Neither Fluent-PC process can build a setup, select a recovery
checkpoint, interpret a result, or automatically resume an interrupted request.

The complete laptop-side setup-plan, ledger, run handoff, recovery-verification,
analysis-manifest, and result-package procedure is documented in
[`SETUP_TO_RESULTS_WORKFLOW.md`](./SETUP_TO_RESULTS_WORKFLOW.md).

## Private Bridge

Both computers require an absolute `FLUENT_BRIDGE_DIR`. The local paths may
differ if the same network share or synchronized directory is mounted
differently.

```text
latest_connection.json
run_requests/
  incoming/
  running/
  completed/
  failed/
run_receipts/
```

Keep the directory outside Git and restrict it to the accounts operating the
laptop and Fluent PC. `latest_connection.json` contains the Fluent password.
The password is never copied into run receipts, ledgers, console output, or
transcripts.

The watchdog writes connection documents through a same-directory temporary
file followed by atomic replacement. Non-running states clear host, port, and
password so the laptop cannot reconnect with stale credentials.

## Fluent-PC Startup

From PowerShell in `PyAnsys`:

```powershell
$env:FLUENT_BRIDGE_DIR = "C:\Private\FluentBridge"
$env:FLUENT_ADVERTISED_HOST = "10.0.0.5"
$env:FLUENT_LOCAL_EXE = "C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe"

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_watchdog.py"
```

Start the run worker separately:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_run_worker.py"
```

Use Task Scheduler for persistent startup only after the foreground
forced-crash test passes. Both processes should use the account that owns the
private bridge and Fluent output directories.

## Laptop Connection and Ledger

Set the laptop's mapped bridge path:

```bash
export FLUENT_BRIDGE_DIR=/private/path/to/FluentBridge
```

`connect()` rereads `latest_connection.json` for every new session, rejects
stale heartbeats and old generations, connects with `allow_remote_host=True`,
and verifies health and Fluent version. Never retain Settings API object handles
across a generation change.

The laptop ledger is runtime state under `PyAnsys/output/agent-ledgers/`. It
records the active and last-completed steps, explicit retry safety, connection
generation, and laptop-accepted case/data checkpoints. It is not a setup
compiler and contains no connection password.

## Run Requests

Example fresh-run request:

```json
{
  "schema_version": 1,
  "job_id": "010v2-run-1500",
  "expected_generation": 14,
  "mode": "initialize",
  "source_case": "C:\\cases\\010V2.cas.h5",
  "source_data": null,
  "target_total_iterations": 1500,
  "completed_iterations": 0,
  "checkpoint_interval": 250,
  "report_interval": 25,
  "output_directory": "C:\\cases\\runs\\010V2-run-1500",
  "overwrite": false
}
```

Submit it from the laptop:

```bash
.venv/bin/python scripts/orchestration/submit_run_request.py request.json
```

For resume, the laptop first reconnects and verifies a candidate pair, then
submits a new request:

```json
{
  "schema_version": 1,
  "job_id": "010v2-run-1500-resume-1",
  "expected_generation": 15,
  "mode": "resume",
  "source_case": "C:\\cases\\runs\\010V2-run-1500\\010v2-run-1500-checkpoint-00001000.cas.h5",
  "source_data": "C:\\cases\\runs\\010V2-run-1500\\010v2-run-1500-checkpoint-00001000.dat.h5",
  "target_total_iterations": 1500,
  "completed_iterations": 1000,
  "checkpoint_interval": 250,
  "report_interval": 25,
  "output_directory": "C:\\cases\\runs\\010V2-run-1500-resume-1",
  "overwrite": false
}
```

Resume never initializes. Because the target is absolute, this request runs
only the remaining `500` iterations.

Checkpoint retention is rolling to avoid filling the Fluent computer's disk.
During a run, the worker keeps only the newest two verified numbered pairs:

```text
010v2-run-1500-checkpoint-00001000.cas.h5
010v2-run-1500-checkpoint-00001000.dat.h5
010v2-run-1500-checkpoint-00001250.cas.h5
010v2-run-1500-checkpoint-00001250.dat.h5
```

After the final pair is verified, the older recovery pair is removed. The
output directory therefore contains the canonical final case/data pair plus
the most recent recovery pair. A failed write is not pruned until its case and
data files have both passed the stability check.

Case-building scripts that use the shared `RunPersistence` helper follow the
same rolling rule for numbered case/data checkpoints. Pure direct case-only
saves remain explicitly named laptop artifacts; the helper never scans or
deletes setup-parent or setup-branch files.

## Failure and Recovery

The watchdog restarts Fluent only after the Fluent process exits or three
consecutive independent gRPC health failures. Ordinary Python, request,
file-path, Settings API, or TUI errors do not restart healthy Fluent.

If the generation changes during a run, the worker writes an `interrupted`
receipt with the last file-verified checkpoint and stops. The laptop agent:

1. waits for a higher running connection generation;
2. reconnects and verifies health/version;
3. loads the ledger-selected case/data pair;
4. inspects and accepts it, or falls back to an earlier pair;
5. submits an explicit resume only after verification.

If restored state cannot be proven, mark the ledger `human_review` rather than
retrying.

## Acceptance Test

1. Connect from the laptop through the bridge.
2. Apply and read back one reversible setup operation, then save a case.
3. Submit a short run and verify checkpoints and final data.
4. Kill Fluent during a second run.
5. Confirm a higher generation and new credentials appear.
6. Confirm the request remains interrupted without automatic resume.
7. Verify a checkpoint on the laptop and submit resume.
8. Confirm resume completes without initialization.
9. Submit an invalid request and confirm the Fluent generation is unchanged.
10. Exercise the restart budget and confirm a terminal failed status.

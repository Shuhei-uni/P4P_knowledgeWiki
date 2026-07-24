# Fluent Host Worker

## Purpose

Run this worker on the Windows computer where Fluent is installed. The worker owns one Fluent process, connects to its local gRPC server, publishes a heartbeat, and relaunches Fluent after a bounded process or connection failure.

The worker now includes a narrow local filesystem job protocol. Its first and
only supported stage is `health_check`. The stage opens a separate short-lived
PyFluent connection to the current worker-owned Fluent generation, checks gRPC
health, records version evidence, and detaches with `cleanup_on_exit=False`.

It does not yet:

- load or mutate a case;
- submit setup, run, or analysis stages;
- checkpoint or resume a simulation;
- adopt a Fluent process left behind by a previously killed worker;
- prove that Student or professional licensing will recover after every failure;
- install itself as a Windows service.

Use only an empty disposable Fluent session for the first forced-crash test.

## Files

- library: `src/pyansys_fluent/host_worker.py`
- job protocol: `src/pyansys_fluent/job_protocol.py`
- Windows-facing CLI: `scripts/orchestration/fluent_host_worker.py`
- job submission CLI: `scripts/orchestration/submit_fluent_job.py`
- offline tests: `tests/test_host_worker.py` and `tests/test_job_protocol.py`
- runtime state: `output/fluent_host_worker/`

The runtime directory contains:

- `host-worker-status.json`;
- `host-worker.lock`, which prevents two workers from launching competing Fluent sessions;
- one server-info file per Fluent generation;
- generation-specific Fluent stdout/stderr logs.
- `jobs/incoming`, `jobs/running`, `jobs/completed`, and `jobs/failed`;
- atomic stage receipts under `receipts`.

Server-info files contain connection credentials. Keep the runtime directory private and do not commit or paste those files into logs or chat.

Job files are claimed with a same-filesystem atomic rename. A job is moved to
`completed` only after its receipt has been validated, atomically committed,
and read back successfully. If receipt persistence fails, the job remains in
`running`; it is never silently reported as complete.

## Before The First Test

On the Fluent computer, confirm the exact interpreter and PyFluent version:

```powershell
Set-Location "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys"

& ".\.venv\Scripts\python.exe" -c "import sys; import ansys.fluent.core as pyfluent; print(sys.executable); print(pyfluent.__version__)"
```

Confirm the exact Fluent executable path. The validated university machine uses:

```text
C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe
```

Other examples already used by this repository include:

```text
C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe
C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe
C:\Program Files\ANSYS Inc\ANSYS Student\v261\fluent\ntbin\win64\fluent.exe
```

Use the path that actually exists on the target computer. Record the full Fluent build/service pack before treating any connection result as a reusable capability.

## Validated University Machine Baseline

The current live baseline is:

- Windows 11;
- Python 3.12.10;
- `ansys-fluent-core` / PyFluent 0.40.2;
- Ansys Fluent 2025 R2 (`v252`);
- all 14 lifecycle tests passing;
- the 120-second headless launch and gRPC smoke test passing;
- forced Fluent termination recovering from generation 1 to generation 2.

Do not replace these values with a different workstation's paths or versions
when recording the job-protocol live test.

## Pull And Run All Offline Tests

In PowerShell on the university Fluent computer:

```powershell
Set-Location "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki"
git switch codex/fluent-autonomy-skeleton
git pull --ff-only

Set-Location ".\PyAnsys"

& ".\.venv\Scripts\python.exe" -c "import sys; import ansys.fluent.core as pyfluent; print(sys.version); print(sys.executable); print(pyfluent.__version__)"

& ".\.venv\Scripts\python.exe" -m unittest discover `
  -s ".\tests" `
  -p "test_*.py" `
  -v
```

This command uses `python.exe` directly; it does not require the Windows `py`
launcher.

The offline suite must pass before launching Fluent. In particular, it covers:

- schema validation and round trips;
- atomic claim and duplicate-claim prevention;
- atomic receipt validation and readback;
- successful and failed health stages;
- malformed input quarantine;
- timeout and generation-mismatch failures;
- cleanup-disabled stage connection and non-terminating detachment;
- the original lifecycle and forced-relaunch behavior.

## Two-Minute Lifecycle Smoke Test

This launches headless, double-precision, three-dimensional Fluent with two processors, monitors it for 120 seconds, then stops the worker-owned process:

```powershell
$FluentExe = "C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe"
$WorkDir = Join-Path (Get-Location) "output\fluent_host_worker_lifecycle_test"
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_host_worker.py" `
  --fluent-exe $FluentExe `
  --work-dir $WorkDir `
  --dimension 3 `
  --precision double `
  --processor-count 2 `
  --max-runtime 120
```

Expected states in `host-worker-status.json` are:

```text
starting
→ waiting-for-server-info
→ connecting
→ running
→ stopped
```

In a second PowerShell terminal:

```powershell
Set-Location "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys"
$WorkDir = Join-Path (Get-Location) "output\fluent_host_worker_lifecycle_test"
Get-Content (Join-Path $WorkDir "host-worker-status.json") -Wait
```

The `running` state must include:

- a non-null `fluent_pid`;
- `fluent_process_alive: true`;
- the detected Fluent version;
- a stable `worker_boot_id` and increasing `heartbeat_sequence`;
- `last_health_success_unix_seconds` and `heartbeat_ttl_seconds`;
- generation-specific stdout/stderr paths;
- a regularly changing `updated_unix_seconds`.

## Live Health-Job Protocol Test

Use a new runtime directory so results from the earlier lifecycle test cannot
be mistaken for current receipts.

In PowerShell terminal 1:

```powershell
Set-Location "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys"

$FluentExe = "C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe"
$WorkDir = Join-Path (Get-Location) "output\fluent_host_worker_job_protocol_test"
New-Item -ItemType Directory -Force -Path $WorkDir | Out-Null

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_host_worker.py" `
  --fluent-exe $FluentExe `
  --work-dir $WorkDir `
  --dimension 3 `
  --precision double `
  --processor-count 2 `
  --job-poll-interval 1 `
  --max-restarts 3 `
  --restart-window 600
```

Wait until `host-worker-status.json` reports `state: running`. In PowerShell
terminal 2:

```powershell
Set-Location "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys"

$WorkDir = Join-Path (Get-Location) "output\fluent_host_worker_job_protocol_test"
$StatusPath = Join-Path $WorkDir "host-worker-status.json"
$Before = Get-Content $StatusPath -Raw | ConvertFrom-Json
$Before

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\submit_fluent_job.py" `
  --work-dir $WorkDir `
  --job-id "health-live-001" `
  --timeout 30
```

Wait up to 30 seconds for the receipt:

```powershell
$ReceiptPath = Join-Path $WorkDir "receipts\health-live-001.json"
$Deadline = (Get-Date).AddSeconds(30)
while (-not (Test-Path $ReceiptPath)) {
  if ((Get-Date) -ge $Deadline) {
    throw "Timed out waiting for $ReceiptPath"
  }
  Start-Sleep -Milliseconds 250
}

$Receipt = Get-Content $ReceiptPath -Raw | ConvertFrom-Json
$Receipt
```

The receipt must show:

```text
schema_version: 1
stage_type: health_check
status: success
worker_boot_id: same value as $Before.worker_boot_id
fluent_generation: same value as $Before.generation
fluent_pid: same value as $Before.fluent_pid
fluent_version: 25.2 / 2025 R2 value reported by Fluent
pyfluent_version: 0.40.2
observed_health_result: true
client_detached: true
fluent_process_alive_after_detach: true
error: null
```

Verify the job and process state:

```powershell
$CompletedPath = Join-Path $WorkDir "jobs\completed\health-live-001.json"
if (-not (Test-Path $CompletedPath)) {
  throw "The successful job was not moved to completed."
}

Start-Sleep -Seconds 5
$After = Get-Content $StatusPath -Raw | ConvertFrom-Json

if ($After.state -ne "running") {
  throw "Worker is no longer running: $($After.state)"
}
if ($After.worker_boot_id -ne $Before.worker_boot_id) {
  throw "Worker boot ID changed during the health stage."
}
if ($After.generation -ne $Before.generation) {
  throw "Fluent generation changed during stage detachment."
}
if ($After.fluent_pid -ne $Before.fluent_pid) {
  throw "Fluent PID changed during stage detachment."
}
if (-not $After.fluent_process_alive) {
  throw "Fluent is not alive after the stage client detached."
}

"PASS: health receipt committed and stage client detached without terminating Fluent."
```

## Live Generation-Mismatch Failure Test

While the same worker is still running, submit a deliberately stale generation:

```powershell
$Current = Get-Content $StatusPath -Raw | ConvertFrom-Json
$WrongGeneration = [int]$Current.generation + 99

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\submit_fluent_job.py" `
  --work-dir $WorkDir `
  --job-id "health-wrong-generation" `
  --expected-generation $WrongGeneration `
  --timeout 30
```

Wait for `receipts\health-wrong-generation.json`. Expected evidence:

- receipt `status` is `failed`;
- `error.type` is `RuntimeError`;
- `error.message` identifies the expected and observed generations;
- `error.retryable` is `true`;
- the observed Fluent generation and PID are still recorded;
- the job is under `jobs\failed`, never `jobs\completed`;
- Fluent remains alive on the original PID.

Stop the worker with `Ctrl+C` after both protocol tests. A clean stop terminates
the Fluent process owned by the worker.

## Forced Relaunch Test

Run the worker without `--max-runtime`:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_host_worker.py" `
  --fluent-exe "C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe" `
  --work-dir ".\output\fluent_host_worker" `
  --processor-count 2 `
  --max-restarts 3 `
  --restart-window 600
```

Wait until the status is `running`. In a second terminal, deliberately stop only the disposable Fluent PID recorded by the worker:

```powershell
$status = Get-Content ".\output\fluent_host_worker\host-worker-status.json" -Raw | ConvertFrom-Json
$status

Stop-Process -Id $status.fluent_pid -Force
```

Do not run this command if the PID has changed, the status is not `running`, or Fluent contains unsaved work.

Expected recovery:

```text
running generation 1
→ restarting
→ starting generation 2
→ waiting-for-server-info
→ connecting
→ running generation 2
```

Success requires:

1. `generation` increases;
2. `fluent_pid` changes;
3. `restart_count_total` increases;
4. a new server-info filename is used;
5. gRPC health becomes active again;
6. no physical Fluent GUI interaction is required.

Stop the worker with `Ctrl+C`. A clean worker stop terminates the Fluent process it owns.

On Windows, each launched Fluent generation is assigned to a kill-on-close Job Object. Closing that ownership handle terminates the launcher and its descendant process tree, including solver/MPI children that might otherwise survive a parent-only termination. If Job Object assignment fails, the generation is rejected rather than monitored without process-tree ownership.

## Failure Behavior

The default budget permits three restarts in ten minutes. The fourth failure inside that window produces:

```text
state: failed
```

and exits the worker with a non-zero status. This prevents an invalid installation, licensing failure, or bad launch command from producing an infinite Fluent restart loop.

Each failed generation keeps separate stdout and stderr logs. Check those logs before raising the restart budget.

## Task Scheduler Trial

Only configure Task Scheduler after the interactive smoke and forced-relaunch tests pass.

Suggested initial action:

- Program/script: the repository's `.venv\Scripts\python.exe`
- Arguments: the absolute path to `scripts\orchestration\fluent_host_worker.py` plus the tested arguments
- Start in: the absolute `PyAnsys` directory
- Restart task on failure: enabled with a conservative delay
- Parallel task instances: disabled

Start with a headless worker in the same Windows user account that can launch Fluent successfully. Whether the task can run while the user is logged out depends on the installed Fluent edition, licensing, and Windows session behavior and must be tested rather than assumed.

The worker also enforces its own exclusive lock, so an accidental second Task Scheduler instance exits instead of launching a second Fluent process.

## Current Recovery Boundary

The worker currently recreates the PyFluent session object after each Fluent restart and discards every old session/setting handle. That is sufficient for launch and connection recovery.

The next implementation step begins only after the live health receipt and
generation-mismatch tests pass. It should add a similarly transactional,
read-only case identity/load probe before any case mutation is attempted.
Checkpoint-aware simulation recovery comes later.

# Fluent Host Worker

## Purpose

Run this worker on the Windows computer where Fluent is installed. The worker owns one Fluent process, connects to its local gRPC server, publishes a heartbeat, and relaunches Fluent after a bounded process or connection failure.

This first implementation is a lifecycle smoke-test tool. It does not yet:

- load or mutate a case;
- submit setup/run/analysis jobs;
- checkpoint or resume a simulation;
- adopt a Fluent process left behind by a previously killed worker;
- prove that Student or professional licensing will recover after every failure;
- install itself as a Windows service.

Use only an empty disposable Fluent session for the first forced-crash test.

## Files

- library: `src/pyansys_fluent/host_worker.py`
- Windows-facing CLI: `scripts/orchestration/fluent_host_worker.py`
- offline tests: `tests/test_host_worker.py`
- runtime state: `output/fluent_host_worker/`

The runtime directory contains:

- `host-worker-status.json`;
- `host-worker.lock`, which prevents two workers from launching competing Fluent sessions;
- one server-info file per Fluent generation;
- generation-specific Fluent stdout/stderr logs.

Server-info files contain connection credentials. Keep the runtime directory private and do not commit or paste those files into logs or chat.

## Before The First Test

On the Fluent computer, confirm the exact interpreter and PyFluent version:

```powershell
Set-Location "C:\Users\Shuhei Yokkaichi\Documents\CFD\P4P_knowledgeWiki\PyAnsys"

& ".\.venv\Scripts\python.exe" -c "import sys; import ansys.fluent.core as pyfluent; print(sys.executable); print(pyfluent.__version__)"
```

Confirm the exact Fluent executable path. Examples already used by this repository include:

```text
C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe
C:\Program Files\ANSYS Inc\v252\fluent\ntbin\win64\fluent.exe
C:\Program Files\ANSYS Inc\ANSYS Student\v261\fluent\ntbin\win64\fluent.exe
```

Use the path that actually exists on the target computer. Record the full Fluent build/service pack before treating any connection result as a reusable capability.

## Two-Minute Smoke Test

This launches headless, double-precision, three-dimensional Fluent with two processors, monitors it for 120 seconds, then stops the worker-owned process:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_host_worker.py" `
  --fluent-exe "C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe" `
  --work-dir ".\output\fluent_host_worker" `
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
Get-Content ".\output\fluent_host_worker\host-worker-status.json" -Wait
```

The `running` state must include:

- a non-null `fluent_pid`;
- `fluent_process_alive: true`;
- the detected Fluent version;
- a stable `worker_boot_id` and increasing `heartbeat_sequence`;
- `last_health_success_unix_seconds` and `heartbeat_ttl_seconds`;
- generation-specific stdout/stderr paths;
- a regularly changing `updated_unix_seconds`.

## Forced Relaunch Test

Run the worker without `--max-runtime`:

```powershell
& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\fluent_host_worker.py" `
  --fluent-exe "C:\Program Files\ANSYS Inc\v242\fluent\ntbin\win64\fluent.exe" `
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

The next implementation step is a job/stage protocol:

1. accept a read-only health or case-load stage;
2. execute it in a short-lived stage client;
3. detach the stage client without terminating supervisor-owned Fluent;
4. record a stage receipt;
5. recover the stage after a forced Fluent restart.

Checkpoint-aware simulation recovery comes after that protocol is proven.

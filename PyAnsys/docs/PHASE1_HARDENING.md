# Phase 1 Recovery Hardening

This milestone hardens the live-proven interruption/resume loop in two places:

1. the owning worker now accepts a local, generation-pinned request to terminate
   the complete worker-owned Fluent process tree; and
2. a candidate case/data checkpoint is reopened through a second
   cleanup-disabled PyFluent client before `run-state.json` advances.

The existing `fluent_host_worker.py` entrypoint enables both protections.

## Why the termination path changed

The original live procedure killed `host-worker-status.json.fluent_pid`. On
Fluent 2025 R2 for Windows, the launched `fluent.exe` process can exit after it
starts `cx2520.exe` and the solver/MPI descendants. Killing the launcher PID did
not necessarily interrupt the active Fluent server.

The hardened worker keeps the Windows Job Object ownership inside the process
that launched Fluent. A separate control-polling thread remains responsive even
while `resumable_run` blocks the normal job polling loop. A control request is
accepted only when both of these values match the current worker:

- `expected_worker_boot_id`;
- `expected_fluent_generation`.

The owning worker then closes the process tree through its existing
`FluentProcessManager.stop()` path. Callers no longer read server-info
credentials, discover child processes, or run `taskkill` manually.

## New status evidence

The hardened status document retains existing fields and adds:

- `launcher_pid`;
- `launcher_process_alive`;
- `grpc_server_pid` when it can be discovered from the non-secret listening
  port;
- `process_tree_owned`;
- `process_tree_alive`.

`fluent_pid` now prefers the observed gRPC server PID and falls back to the
launcher PID only while the server PID is unavailable.

The server-info password is never copied into status, receipts, logs, or control
requests.

## Safe forced-interruption procedure

Start the worker and submit a `resumable_run` exactly as documented in
`FLUENT_HOST_WORKER.md`, using a new runtime directory.

After at least one nonzero checkpoint has been committed, submit the control
request from a second PowerShell terminal:

```powershell
Set-Location "C:\Users\syok443\Documents\P4P_knowledgeWiki\PyAnsys"

$WorkDir = Join-Path $PWD "output\fluent_host_worker_resume_test_003"
$RequestId = "terminate-resume-live-001"

& ".\.venv\Scripts\python.exe" `
  ".\scripts\orchestration\request_fluent_generation_termination.py" `
  --work-dir $WorkDir `
  --request-id $RequestId
```

The CLI reads the public worker status and pins the request to its current boot
ID and generation. It does not read the server-info file.

Wait for the control receipt:

```powershell
$ControlReceiptPath = Join-Path $WorkDir "control\receipts\$RequestId.json"
while (-not (Test-Path -LiteralPath $ControlReceiptPath -PathType Leaf)) {
  Start-Sleep -Milliseconds 250
}
$ControlReceipt = Get-Content $ControlReceiptPath -Raw | ConvertFrom-Json
$ControlReceipt | ConvertTo-Json -Depth 10
```

Required success evidence:

```text
status: success
action: terminate_current_generation
expected_worker_boot_id: observed_worker_boot_id
expected_fluent_generation: observed_fluent_generation
process_tree_owned: true
termination_requested: true
termination_observed: true
error: null
```

The active resumable job remains under `jobs\running`. Its current attempt is
committed as retryable, the worker launches the next generation, and the job
resumes from the latest committed checkpoint without hybrid-initializing again.

## Checkpoint reopen contract

Each checkpoint now follows this order:

1. write a uniquely named candidate `.cas.h5`;
2. write the matching candidate `.dat.h5`;
3. confirm both files are nonempty and size-stable;
4. attach a second cleanup-disabled PyFluent client to the same worker-owned
   Fluent generation;
5. read the candidate case;
6. read the matching candidate data;
7. confirm gRPC health remains active;
8. detach the verification client;
9. confirm the primary run client remains healthy;
10. only then atomically advance `last_checkpoint` and
    `completed_iterations` in `run-state.json`.

Checkpoint metadata records a `verification` object with:

- verification mode;
- generation and observed Fluent PID;
- case and data paths;
- timestamps;
- data-load result;
- health result;
- detach result;
- Fluent version when available;
- configured dimension and precision.

A failed reopen leaves the previous `last_checkpoint` untouched. Candidate
files can remain on disk for diagnosis, but they are not resumable because the
atomic run state never references them.

## Verification isolation tradeoff

The current mode is `fresh-client-same-generation`. It is stronger than the
previous file-size-only check because Fluent actually reads both artifacts
through a newly attached client. It deliberately does not launch a second
concurrent Fluent process, which could consume another licence or interfere
with the university host.

A future hardening step can add full fresh-process verification where licence
availability is known. The durable checkpoint metadata makes the verification
mode explicit so the two levels are never confused.

## Offline validation

Run the full suite after pulling:

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover `
  -s ".\tests" `
  -p "test_*.py" `
  -v
```

The added tests cover:

- atomic control submission and receipt persistence;
- wrong worker-boot rejection;
- worker-owned generation termination;
- case/data reopen through a fresh client;
- no initialization or iteration during verification;
- checkpoint commitment only after reopen verification.

## Runtime security

Keep every worker runtime directory private and uncommitted. It contains
server-info credentials, Fluent logs, control receipts, run-state documents,
and potentially large case/data checkpoints.

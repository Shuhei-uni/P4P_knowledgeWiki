# Native Fluent Run and Autosave Policy

## Key rule

Python may prepare a Fluent case, configure the native run controls, and reconnect later for inspection. Python must not own a long simulation by repeatedly calling Fluent iteration commands or by issuing client-side checkpoint writes after each block.

The calculation and its recovery points belong to Fluent itself:

```text
Python setup/inspection -> Fluent-native initialization -> Fluent-native run + autosave -> Python reconnect/inspect
```

This policy applies to steady and transient runs unless a separate workflow explicitly documents why a solver-side alternative is unavailable.

## Why this matters

A PyFluent call such as `solver.tui.solve.iterate(...)` or `solver.settings.solution.run_calculation.iterate(...)` is a client-issued command. A Python loop around that call also owns the progress count, checkpoint timing, interrupt handling, and final save. If the gRPC connection disappears, that loop can no longer guarantee that the next checkpoint or final file will be written.

Fluent has its own calculation activity and autosave controls. For a steady-state calculation, the data-save frequency is specified in iterations. Fluent can retain only the most recent autosave files, so the solver can continue saving without Python remaining attached and without retaining the entire checkpoint history.

## Approved workflow

### 1. Prepare the case

Python is allowed to:

1. connect and verify the requested Fluent endpoint;
2. load and audit the intended case or mesh;
3. apply setup changes in dependency order;
4. read back boundary, model, material, and DPM settings;
5. write the case-only setup artifact;
6. configure Fluent's native calculation activities and autosave settings if the live path has been inspected and verified.

Setup builders should stop at a valid `.cas.h5` artifact. Do not hybrid-initialize, iterate, and write a long-run `.dat.h5` from a setup-builder Python loop.

### 2. Configure native autosave in Fluent

In Fluent's calculation-activity/autosave controls:

- set `Save Data File Every` to the desired steady-state iteration interval, for example `500`;
- choose a hard-coded path on the Fluent computer, not a laptop-local path;
- choose `Only if Modified` for the associated case when the mesh and setup remain unchanged, or `Each Time` when a paired case/data snapshot is required at every checkpoint;
- enable retention of only the most recent files and keep at least two checkpoint slots for failure tolerance;
- use a run-specific root name so an old run cannot be mistaken for the current one;
- verify the resulting remote filenames and the current autosave state before starting the calculation.

Fluent appends the steady-state iteration number to autosaved filenames. “Overwrite” therefore means limiting the retained set and allowing Fluent to replace the oldest retained file, not assuming that every checkpoint has one fixed filename.

The case and data files together are the restart artifact. If only data files are autosaved, retain a matching case file whose mesh and setup have not changed. If the mesh or case settings change during the run, write a new paired case/data checkpoint.

### 3. Start and detach safely

1. Complete initialization in Fluent and confirm that it has returned to an idle/ready state.
2. Confirm the iteration limit, monitors, and autosave settings in Fluent.
3. Start the calculation from Fluent's own `Run Calculation`/`Calculate` control or from a Fluent-native journal that is executed by Fluent.
4. Disconnect only the Python client if needed. Do not call `solver.exit()` or `solver.force_exit()`; those are shutdown/termination operations, not client detachment.
5. Do not treat a Python stdout log or local JSON file as proof that the remote solve is still running. Fluent's live state and remote autosave files are authoritative.

For runs that need observable text evidence while Fluent is too busy to serve a
new gRPC client, generate a Fluent-native steady-run journal with
`scripts/setup/generate_native_run_journal.py`. The generated journal:

- starts `file/start-transcript` before iteration, so Fluent writes console input
  and output to a Windows-local transcript;
- enables `solve/monitors/residual/print?`, putting the iteration number and
  residual row in that progressively written transcript;
- executes one Fluent-native `solve/iterate` command rather than a Python loop;
- exports Fluent's retained residual history through
  `plot/residuals-set/plot-to-file` after the iteration command returns; and
- stops the transcript but deliberately leaves Fluent open.

From the repository root, for example:

```bash
PyAnsys/.venv/bin/python \
  PyAnsys/scripts/setup/generate_native_run_journal.py \
  --iterations 5000 \
  --transcript-file 'C:\FluentRuns\09cV3\run.trn' \
  --residual-file 'C:\FluentRuns\09cV3\residuals.out' \
  --residual-history-size 6000 \
  --output-journal PyAnsys/output/09cV3-native-run.jou
```

Copy the generated journal to the Fluent computer and read it from Fluent only
after the intended case is loaded, initialization is complete, autosave has
been verified, and the output directory already exists. The transcript is the
live monitoring artifact. The dedicated residual file is a post-run/post-
interrupt snapshot: it is not continuously rewritten during the iteration
command. Put the Windows output directory on an authenticated read-only SMB
share if a remote observer must tail the transcript without using gRPC.

The normal PyFluent iteration method is synchronous from the Python caller's perspective. Sending one long command and then killing the client connection is not a substitute for a verified native run. If a native journal or GUI start is not available, keep the command attached and state that limitation explicitly rather than pretending the run is detached.

### 4. Reconnect and recover

After a connection loss:

1. reconnect to the existing Fluent session without starting a second Fluent process;
2. check whether Fluent is still solving or has returned to idle;
3. read the live iteration counter and residual/physical monitor histories;
4. inspect the remote autosave evidence and identify the newest complete case/data pair;
5. do not reload a checkpoint into a session that is still actively solving;
6. if Fluent stopped, resume from the newest verified checkpoint using Fluent's own read-case/data and run controls;
7. record the exact case/data filenames, iteration, Fluent version, and monitor state after recovery.

A dropped client connection is recoverable only if the Fluent process and the Fluent computer remain alive. Autosave protects against losing the client connection; it cannot make a crashed Fluent process continue by itself.

### 5. Use the reconnecting monitor

The repository provides a read-only monitor at
`scripts/inspection/monitor_native_run.py`. It is designed to run in a separate
terminal and be stopped/restarted independently of Fluent:

```bash
python3 PyAnsys/scripts/inspection/monitor_native_run.py \
  --server-id 1 \
  --poll-interval-seconds 30 \
  --checkpoint-pair \
    'C:\\path\\run-500.cas.h5' \
    'C:\\path\\run-500.dat.h5' \
  --checkpoint-pair \
    'C:\\path\\run-1000.cas.h5' \
    'C:\\path\\run-1000.dat.h5'
```

The monitor:

- reconnects after transient transport failures with bounded exponential backoff;
- records connection generations so a recovered client is distinguishable from the original connection;
- reads Fluent health, version, run-control values, summarized monitor data, and explicitly supplied checkpoint-pair existence;
- derives live iteration from the newest monitor x-value rather than treating Fluent's configured maximum-iteration RP value as completed progress, then compares it with the last snapshot (including a snapshot persisted by an earlier monitor process);
- writes an atomic latest-state JSON plus an append-only JSONL event log;
- reports `advancing`, `not_advancing`, `went_backwards_or_reloaded`, or `unknown` rather than falsely claiming that Fluent is idle or stopped;
- never calls initialization, iteration, save, reload, interrupt, `solver.exit()`, or `solver.force_exit()`.

The monitor does not infer case identity from `server_id`, and it does not guess
autosave filenames. Pass each retained case/data pair explicitly with repeated
`--checkpoint-pair` options. A `complete` pair is evidence that both remote files
are visible; a `partial` pair must not be used for recovery.

## Explicit 03A Stage-3 adaptive blocking exception

The `03A-stage3` F01–F12 convergence sweep is a narrow, user-approved exception to the normal detached/native-run preference because its next solver state depends on an evidence gate evaluated at discrete iteration checkpoints. The authoritative scientific workflow is:

Project/experiments/full-geometry-03a-mixture-08b-parity-baseline/stage-03/setup-source.md is the migrated authority for
the Stage-3 execution specification.

For **F01–F12 only**, an execution agent may keep its client attached and issue one synchronous blocking Fluent solve command for the current decision block:

- `750` iterations for the first assessment at an intermediate state;
- `250` iterations for each subsequent reassessment;
- final-condition blocks as defined by the Stage-3 authority.

The return of that blocking Fluent command is intentionally the wake-up point for the agent. The agent may then inspect histories, evaluate the frozen Stage-3 gate, save the prescribed transition checkpoint, apply only the prescribed next state, and issue the next blocking solve command.

This exception has strict limits:

- do **not** implement a Python `for`/`while` loop around iteration calls;
- do **not** issue one-iteration or other fine-grained client loops;
- every new solve block must follow an explicit Stage-3 decision point;
- configure Fluent-native autosave locally so recovery does not depend solely on the client call returning;
- do not silently repeat a block after a transport failure when completion is uncertain;
- first reconnect to the same Fluent process and establish the actual completed iteration/stage state;
- classify gRPC/client/transport loss separately from a Fluent numerical failure;
- keep all run-specific autosaves/checkpoints on the Fluent computer's local storage;
- this exception does not authorize the same client-owned adaptive pattern for other campaigns unless the user explicitly approves it.

The purpose of the exception is orchestration wake-up at scientifically required checkpoints, not moving solver ownership back into a generic Python iteration runner.

### Fixed-3,000 Stage-3 supervisor override

The user additionally approved a narrow operational override for the assigned
fixed-block queue `F02 -> F04 -> F11 -> F06 -> F05`. Its supervisor is
`scripts/setup/run_03a_stage3_override_native_queue_server2.py`. Python may
remain active across the queue so it can reconcile a completed Fluent-native
stage, restore its named case/data endpoint, apply the prescribed transition,
and submit the next native stage.

This remains safe only under these limits:

- Fluent owns every 3,000-iteration solve, native autosave, transcript, and
  endpoint write; Python never polls individual iterations or writes periodic
  checkpoints.
- The local resume ledger is intent/audit evidence, not recovery authority. A
  resumed supervisor must verify and reload the named Fluent case/data pair;
  it must never repeat a stage recorded as submitted but not yet reconciled.
- A `PAUSE` file in the local campaign directory stops the supervisor at the
  next stage boundary. A mid-stage pause must be issued through Fluent's Pause
  control, not Interrupt/Ctrl+C, because Interrupt exits a journal.
- A process-level Fluent crash, missing endpoint, or transport uncertainty
  blocks the queue for recovery; it cannot be safely skipped unattended.

## Prohibited Python run patterns

Except for the explicit `03A-stage3` blocking exception above, do not add or use Python code that:

- loops over `solver.settings.solution.run_calculation.iterate(...)`;
- loops over `solver.tui.solve.iterate(...)`;
- writes a checkpoint only after a Python loop receives a successful iteration response;
- relies on `RunPersistence.record_checkpoint` or a local run-state JSON as the only recovery mechanism;
- reconnects and silently repeats an unknown in-memory iteration block;
- calls `solver.exit()` at the end of a long run when the intention is merely to detach the client.

Post-run Python inspection and offline case/data analysis remain allowed. They must not change the solver state or be required for Fluent to reach its next checkpoint.

## Evidence and uncertainty

- `Reported`: Fluent's User's Guide documents autosaving case/data files during a calculation, iteration-based frequency for steady solutions, “Only if Modified” versus “Each Time” case saving, and retention of only the most recent files.
- `Inferred`: once these settings are accepted by Fluent, the solve-side autosave is independent of a laptop-side Python polling loop because Fluent owns the calculation and file-write activity. Verify the live settings on the target Fluent release before a long run.
- `Not live-verified here`: an arbitrary PyFluent client disconnect in the middle of a synchronous iteration RPC. Do not use that as the resilience mechanism.
- `Reported`: PyFluent exposes existing monitor sets through `get_monitor_set_names()` and `get_monitor_set_data()`; the reconnecting monitor uses those read-only accessors without starting a new calculation or callback loop ([PyFluent monitor guide](https://fluent.docs.pyansys.com/version/stable/user_guide/monitors.html)).
- `Reported`: Fluent's `number-of-iterations` RP value is the run-control maximum in the live 2025 R2 session; it is retained by the monitor as configuration context, not used as the completed-iteration count.
- `Inferred`: a snapshot that observes an increasing monitor x-coordinate is classified as `advancing`; an unchanged coordinate is reported conservatively as `not_advancing`, because a read-only client cannot distinguish idle from a stalled or paused solver without a release-specific solver-status variable.

## Sources

- [Ansys Fluent 2025 R2 User's Guide — Reading and Writing Case and Data Files](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_CaseDataFiles.html)
- [Ansys Fluent 2025 R2 Text Command List — `file/auto-save`](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_tcl/x1-50005.html)
- [PyFluent — connecting to an existing Fluent session](https://fluent.docs.pyansys.com/version/stable/user_guide/session/launching_ansys_fluent.html)

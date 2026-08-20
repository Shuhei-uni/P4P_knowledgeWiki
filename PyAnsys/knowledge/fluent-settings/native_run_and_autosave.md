# Fluent Run Execution and Autosave

Choose the simplest execution mode that gives the experiment the control it needs. Setup construction is separate: first produce/verify the case, then make the run plan, then execute it.

## Run modes

| Mode | Best for | Who controls progress |
|---|---|---|
| **Simple TUI** | one prepared case, uninterrupted solve | Fluent executes one submitted command |
| **Fluent journal** | multiple independent cases or a fixed sequence | Fluent executes the journal |
| **Agent-owned Python** | staged/adaptive runs with intermediate decisions | Python/agent supervises explicit decision blocks |

## 1. Simple TUI

Use one solve command when nothing needs to change before the requested run completes.

Typical flow:

```text
load/verify case -> configure autosave if needed -> initialize -> send one solve command -> inspect result
```

Examples include one steady `solve/iterate N` run or one fixed transient advance. Do not add a client-side orchestration framework merely to wrap one uninterrupted solve.

## 2. Fluent journal batch

Use a journal when several cases/stages can run in a predetermined order without inspecting an intermediate result to decide the next action.

A robust journal should:

- use explicit full paths;
- load the intended case before each run;
- initialize exactly as defined by the experiment;
- use unique run/output names;
- configure autosave/checkpoints where recovery matters;
- start a transcript/log when useful;
- write the required final case/data artifacts;
- avoid relying on laptop-local paths for Fluent-side files.

Typical use:

```text
case A -> initialize -> run -> save
case B -> initialize -> run -> save
case C -> initialize -> run -> save
```

There is no reason for an agent to remain attached just to submit the next independent case.

## 3. Agent-owned Python

Use Python when the next solver action depends on evidence produced during the run: staged ramping, changing numerics/models, adaptive convergence gates, conditional continuation, or similar workflows.

Implement the run as a recoverable state machine:

```text
establish current state
-> run to next decision point
-> inspect monitors/evidence
-> save/verify checkpoint and record stage
-> decide next state
-> apply required change
-> continue
```

Loops are acceptable when they encode this explicit run plan. They must not blindly repeat an unknown block or assume that the client-side counter is authoritative after a transport failure.

After reconnecting, first establish the actual Fluent case/stage/iteration/checkpoint state. Then continue from that observed state.

### Supervisor handoff

Whenever an agent-owned Python run is created, provide:

- the exact command to launch it;
- which Fluent endpoint/case it expects;
- what files/logs/monitors the supervising agent should watch;
- how the current stage is identified;
- checkpoint/autosave locations;
- numerical/scientific stop conditions;
- what to do after gRPC loss, Fluent failure, or an interrupted script;
- the exact resume command or resume-state procedure.

The aim is that a separate overseeing agent can safely supervise or resume the run without reconstructing the workflow from source code.

## Autosave and recovery

Use Fluent-native autosave when losing progress would be costly, regardless of run mode.

Good defaults:

- write to storage local/accessible to the Fluent host;
- use run-specific names;
- retain a small rolling set rather than every checkpoint indefinitely;
- keep a matching `.cas.h5` for `.dat.h5` recovery when setup/mesh is unchanged;
- write a new paired case/data checkpoint when the setup changes during a staged run;
- verify important checkpoint files actually exist before relying on them.

A local Python state file is useful orchestration evidence for agent-owned runs, but recovery should be reconciled against the actual Fluent/checkpoint state before issuing new solver work.

## Monitoring

Use the lightest monitoring method that fits the mode:

- simple TUI: command completion plus normal Fluent monitors/transcript;
- journal batch: transcript, per-case output files and autosaves;
- agent-owned Python: stage ledger plus the monitors/checkpoints used by the decision logic.

`scripts/inspection/monitor_native_run.py` may be used for read-only observation when appropriate. A blocked read-only request while Fluent is solving is not by itself proof of failure.

## Storage discipline

Run transcripts, monitor exports and intermediate analysis files should be retained only when they support recovery, debugging, result reporting, analysis or plots. Do not accumulate every intermediate artifact in `PyAnsys/output/`; remove temporary/superseded files once their evidence has been distilled into the retained result artifacts.

## Examples

**Twelve already-built pressure cases:** generate one journal with explicit input/output paths and per-case autosave/transcript handling. Let Fluent execute the batch.

**Staged convergence ramp:** use a Python supervisor that runs the current block, evaluates the gate, writes/validates the transition checkpoint, applies the next solver state, and continues. Hand the user an exact launch command plus a supervisor/resume checklist.

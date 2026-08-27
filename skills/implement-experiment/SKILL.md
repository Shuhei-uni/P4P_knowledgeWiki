---
name: implement-experiment
description: "Orchestrate implementation of an approved experiment from setup.md through verified Fluent case construction, initialization, run execution, checkpoint/recovery, and completed simulation artifacts. Use after the scientific question and setup are already decided."
---

# Implement Experiment

Turn an approved `setup.md` into a verified simulation run. Do not redesign the scientific question unless implementation exposes a blocking contradiction.

## Contract

Input:

- approved `setup.md`;
- explicit parent/reference case where applicable;
- run target and compute constraints;
- required monitors/evidence identified by analysis planning.

Output:

- verified child case;
- observed initialization/run state;
- completed or recoverable simulation artifacts;
- clear implementation status and failures;
- no scientific interpretation beyond implementation observations.

## Workflow

```text
setup.md
-> inspect parent/live state
-> build requested delta
-> read back + verify
-> save/reopen child case
-> configure required monitors/checkpoints
-> initialize
-> run
-> observe completion/recovery state
-> hand off to analysis
```

## Use existing implementation tools

Prefer the existing `fluent-case-build-and-run` skill and reusable PyAnsys modules/scripts for Fluent operations. Do not duplicate their low-level recipes here.

Treat Fluent as a dependency-ordered state machine. Inspect live active settings before mutation, reacquire objects after dependency-changing operations, and read back important values.

## Build only the requested delta

From `setup.md`, extract:

- parent case;
- intended changes;
- invariants that must remain unchanged;
- initialization method;
- run duration/iterations/physical time;
- required report definitions/monitors;
- checkpoint/autosave expectations.

Do not silently add physics, numerics, models, or acceptance criteria.

If the setup is ambiguous in a way that changes the experiment, stop and escalate rather than choosing a convenient interpretation.

## Verification gate

Before running, require evidence that:

- the intended changes are present;
- declared invariants remain intact;
- the case can be saved and reopened;
- the saved state still matches the intended setup;
- required analysis monitors/report definitions exist before a long run when they cannot be reconstructed later.

Use machine-readable checks where available. Human-readable `setup.md` remains the experiment definition; machine state is evidence that implementation matches it.

## Run ownership

For long runs, prefer Fluent-native execution/checkpointing or the repository's established resilient run mechanism. Do not keep an agent context alive merely to babysit a solver.

Record the difference between:

- run launched;
- run observed active;
- requested horizon reached;
- final state independently verified.

Do not claim completion from elapsed wall time alone.

## Recovery

When a run crashes or becomes unavailable:

1. preserve the latest known-good checkpoint/state;
2. determine whether the failure is infrastructure, setup, or numerical;
3. avoid silently reinitializing a resumed calculation;
4. return a structured failure to the scientific loop.

The next action may be `RERUN_FROM_CHECKPOINT`, `REPAIR_SETUP`, `NUMERICAL_SENSITIVITY`, or `HUMAN_REVIEW_REQUIRED`; do not automatically create a new experiment.

## Delegate when useful

Use subagents for read-only implementation review when the setup is complex, for example:

- one checks intended Fluent state/invariants;
- one checks analysis instrumentation;
- one checks run/recovery safety.

The main agent owns mutations and final verification.

## Handoff

Report only what was observed:

- case built/reload-verified or not;
- initialization completed or not;
- run launched/completed/recovered or not;
- observed final iteration/physical time where available;
- checkpoint/final artifact locations;
- implementation deviations or uncertainties.

Then hand off to `plan-analysis` / analysis execution. Scientific meaning belongs later.
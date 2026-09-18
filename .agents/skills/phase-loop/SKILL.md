---
name: phase-loop
description: "Advance the active CFD phase through experiment design, Fluent execution, analysis, recovery, and evidence-backed closure inside the recorded phase envelope."
---

# Phase Loop

Own the scientific loop from the next useful experiment to the strongest
evidence-backed phase statement.

Read the active `CONTEXT.md`, `phase-state.yaml`, and only the setup/result
records relevant to the current frontier. Then use:

- [lifecycle](references/lifecycle.md) for the few hard scientific gates;
- [experiment cycle](references/experiment-cycle.md) for design → run → analysis;
- [recovery](references/recovery.md) when anything fails or blocks.

Legacy `phase-loop` / `auto-loop` state labels may remain in historical
records. Treat them as queue-driven versus autonomous modes of this one workflow.

## Operating rule

The human is **not** a normal workflow gate.

Inside the recorded phase envelope, choose experiments, repair implementation,
restart/rebuild recoverable work, analyse evidence, and continue without asking
for routine approval. Ask only when:

- the scientific question or allowed scope must change;
- an external action is irreversible and not already authorized; or
- the task genuinely depends on the human's preference/judgement rather than
  discoverable evidence.

A build/configuration/coding failure means **the experiment was not tested**.
It does not reject the scientific idea.

## Loop

Repeat until the phase reaches a supported conclusion, the timebox ends, or a
genuine external block remains:

1. Identify the current uncertainty and the cheapest experiment that can
   materially reduce it.
2. Define the controlled delta, required evidence, decisive figures, and the
   claim the run could support **before compute**.
3. Use `pyansys-workflow` to inspect/build/prove/run the exact case.
4. Use `cfd-numerical-analysis` to produce the planned evidence first, then
   supporting diagnostics.
5. Separate observation, interpretation, and conclusion. Update `results.md`
   and the compact machine state.
6. Decide whether the evidence calls for another discovery probe, deeper
   qualification, a repair/rerun, or phase closure. Continue immediately when
   the next action is in scope.

Use independent subagents only where they answer a concrete uncertainty or
challenge a consequential inference. Do not create review ceremonies for facts
that can be checked deterministically.

## Completion

A run is complete only when its requested horizon and required artifacts are
verified. A phase is complete only when the lifecycle reference permits the
bounded statement being made.

Solver success is not scientific success. Solver failure is not scientific
falsification.

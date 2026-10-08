---
name: pyansys-workflow
description: "Inspect, build, run, recover, or extract Fluent/PyFluent evidence; transfer an existing case to a new mesh with native Replace Mesh."
---

# PyAnsys Workflow

`PyAnsys/` is the executable Fluent layer. Carry out the scientific intent
already recorded by the active experiment; do not redesign the experiment here.

Use the branch that matches the task:

- [inspection and build](references/inspection-build.md) — discover live state,
  apply the controlled delta, read back, save/reopen, smoke-test;
- [replace mesh](references/replace-mesh.md) — reuse an existing case setup on a
  supplied mesh, including native interpolation when continuing saved data;
- [run control](references/run-control.md) — execute, checkpoint, supervise, and
  prove completion;
- [fleet and artifacts](references/fleet-and-artifacts.md) — choose/reconcile
  live endpoints, case-data transfers, output paths, and durable checkpoints;
- [manual fallback](references/manual-fallback.md) — use version-matched Fluent
  guides and their screenshots to build and verify TUI commands for nested
  settings, unclear activation order, or unresolved configuration;
- [special operations](references/special-operations.md) — pool patching and
  other narrow case operations.

## Core rules

Treat Fluent as a dependency-ordered state machine.

Prefer live Settings/API inspection over remembered paths. Reacquire objects
after upstream model/topology changes. A successful setter call is not proof:
read back the state that matters.

## Review code before execution

Before a build, launch, continuation, or retry, review the actual code/journal
that will run on the Fluent host. Reuse review evidence for unchanged code and
prerequisites; review each changed path and its affected callers again.

1. Trace the executed path step by step: entry point, helpers, command delivery
   to Fluent, state changes, solve, checkpoint, and completion. Include controller
   and watcher interactions when used.
2. For each Fluent command, verify version support, arguments, units, names,
   required starting state, and expected readback. Check dependency order from
   case loading and model activation through initialization or continuation,
   instrumentation, solving, and saving.
3. Check timing: blocking versus asynchronous calls, completion acknowledgements,
   timeouts, polling, scheduled input changes, and checkpoint timing. Wait for
   verified completion before a dependent command; use state evidence rather
   than an arbitrary sleep. Keep one command owner per session so controllers,
   watchers, and retries cannot send conflicting mutations during a solve.
4. Check error paths: preserve the original exception/transcript, detect failed
   commands and missing outputs, and prevent dependent work after a failed step.
   Before replaying a command, establish whether it already took effect.
5. Use the smallest relevant offline check and one bounded live smoke check for
   new or changed Fluent behavior. Follow the selected branch's verification
   rules; account for smoke iterations in the requested horizon.

Complete the review only when each executed command has verified prerequisites,
order, timing, and a way to check its result. Put a concise review outcome,
code identity, and unresolved execution risks in the existing build/run receipt.

## Execution evidence and repair

For every child case preserve:

- exact parent identity;
- controlled changes and invariants;
- important output paths;
- readback evidence;
- saved/reopened artifact identity;
- smoke-test / instrumentation evidence;
- terminal run evidence.

On a detected configuration or coding error, begin repair promptly: capture the
failed command, error, and current Fluent state; identify the cause; patch the
working implementation in `PyAnsys/`; then review and verify the affected path
before retrying. Apply the verified patch on the execution host as well. A fix
is complete only when the failed operation and its dependent steps succeed with
the required readback/artifacts. Preserve original evidence, including `raw/`.

Follow [run control](references/run-control.md) for safe deployment when a
controller/session is still active. Reconcile its progress and preserve the
latest valid endpoint before restart/recreate under the phase authority. A
timeout alone does not justify replaying a solve. If the same error recurs,
inspect new evidence and revise the fix or use another verified route; avoid
unchanged retries. Continue in-scope recovery without routine human approval;
record a durable external block when required resources remain unavailable.
Do not mark the scientific candidate failed because setup code was wrong.

## Fallbacks

For nested settings or unclear activation order, follow the manual fallback
branch and prefer its guide-and-screenshot-based TUI recipe. Use Settings/API
for straightforward changes and for readback. A TUI or journal route does
**not** require a human approval round-trip merely because it is TUI; establish
the exact Fluent version/case prerequisites and verify by readback plus
save/reopen.

Never guess a configuration from another Fluent version just to keep the run
moving.

## Session safety

Follow the active phase/session authority. Preserve valuable endpoints before
replacement and never terminate an unrelated or unpreserved Fluent process.
When the phase explicitly owns the session, ordinary restart/recreate recovery
does not require another human confirmation.

Return concise execution proof to the calling workflow, not a scientific
interpretation.

---
name: pyansys-workflow
description: "Inspect, build, run, recover, or extract evidence from Fluent/PyFluent for the active experiment."
---

# PyAnsys Workflow

`PyAnsys/` is the executable Fluent layer. Carry out the scientific intent
already recorded by the active experiment; do not redesign the experiment here.

Use the branch that matches the task:

- [inspection and build](references/inspection-build.md) — discover live state,
  apply the controlled delta, read back, save/reopen, smoke-test;
- [run control](references/run-control.md) — execute, checkpoint, supervise, and
  prove completion;
- [manual fallback](references/manual-fallback.md) — resolve uncertain Fluent
  configuration from the version-matched manual and live tree;
- [special operations](references/special-operations.md) — pool patching and
  other narrow case operations.

## Core rules

Treat Fluent as a dependency-ordered state machine.

Prefer live Settings/API inspection over remembered paths. Reacquire objects
after upstream model/topology changes. A successful setter call is not proof:
read back the state that matters.

For every child case preserve:

- exact parent identity;
- controlled changes and invariants;
- important output paths;
- readback evidence;
- saved/reopened artifact identity;
- smoke-test / instrumentation evidence;
- terminal run evidence.

Configuration or coding errors are recoverable implementation failures. Inspect,
research, repair, restart/recreate a recoverable child/session when authorized,
and try again. Do not mark the scientific candidate failed because setup code
was wrong.

## Fallbacks

A TUI or journal route does **not** require a human approval round-trip merely
because it is TUI. Use it only when the Settings/API path is unavailable or
insufficient, the exact Fluent version/case prerequisites are understood, and
the result can be verified by readback plus save/reopen.

Never guess a configuration from another Fluent version just to keep the run
moving.

## Session safety

Follow the active phase/session authority. Preserve valuable endpoints before
replacement and never terminate an unrelated or unpreserved Fluent process.
When the phase explicitly owns the session, ordinary restart/recreate recovery
does not require another human confirmation.

Return concise execution proof to the calling workflow, not a scientific
interpretation.

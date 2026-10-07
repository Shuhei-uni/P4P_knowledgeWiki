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

# Fluent Settings Agent Knowledge Base

Purpose: provide an agent-friendly, searchable reference for automating Ansys Fluent model settings through PyFluent / gRPC / TUI fallbacks.

Main idea: most Fluent automation failures come from either:

1. **Wrong order**: setting a child before its parent object/model exists or is active.
2. **Wrong path**: Fluent's settings tree differs by version, solver mode, model combination, phase count, particle type, or boundary type.

This package is intentionally not a perfect Fluent API dump. It is a practical scaffold for dependency-aware automation. The agent should always inspect the live Fluent tree, read back values, and use documentation/TUI fallbacks when paths fail.

## Key run-policy knowledge

Python prepares and audits the case; Fluent owns initialization, iteration, and
autosave. Do not build a long-running Python loop around
`solver.tui.solve.iterate(...)` or
`solver.settings.solution.run_calculation.iterate(...)`. Configure Fluent's
native calculation-activity autosave, start the run from Fluent or a
Fluent-native journal, and reconnect later for monitoring or recovery.

Read [native run and autosave policy](native_run_and_autosave.md) before
authoring or using any long-run workflow. The policy is specifically designed
for a dropped laptop/gRPC connection and requires at least one verified remote
case/data recovery point.

Use `../../scripts/inspection/monitor_native_run.py` for read-only progress
monitoring after a reconnect. It owns no solver work; it only reconnects,
observes, persists local monitor state, and reports explicitly supplied native
checkpoint pairs.

The repository code now mirrors this assumption. Shared execution mechanics are in `../../src/pyansys_fluent/common.py`, and dependency-aware step orchestration is in `../../src/pyansys_fluent/dependency_workflow.py`.

## Recommended use

1. Start with `indices/master_index.json`.
2. Read `orders/global_setup_order.yaml` first.
3. For a model, read both:
   - `trees/<model>_tree.md`
   - `orders/<model>_order.yaml`
4. Use `templates/dependency_aware_setter_pseudocode.py` as the automation pattern.
5. Use `docs/documentation_map.md` when live paths do not match this guide.
6. Log failures using `templates/failure_log_template.md`.
7. For initialization, iteration, checkpointing, and reconnection, use
   `native_run_and_autosave.md`; do not use a client-side iteration loop.

## Core automation rule

```text
enable parent -> refresh/reacquire tree -> inspect children/options -> set child -> read back -> log success/failure
```

Do not treat Fluent like a normal static Python object model. Treat it like a GUI state machine.

## Canonical failure categories

Use these labels consistently in logs and notes:

1. `order/dependency issue`
2. `path/version issue`
3. `invalid value/format issue`
4. `PyFluent wrapper limitation`
5. `requires TUI fallback`
6. `requires manual GUI cleanup`

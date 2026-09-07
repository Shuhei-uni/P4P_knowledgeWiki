# Fluent Settings Agent Knowledge Base

Purpose: provide an agent-friendly, searchable reference for automating Ansys Fluent model settings through PyFluent / gRPC / TUI fallbacks.

Main idea: most Fluent automation failures come from either:

1. **Wrong order**: setting a child before its parent object/model exists or is active.
2. **Wrong path**: Fluent's settings tree differs by version, solver mode, model combination, phase count, particle type, or boundary type.

This package is intentionally not a perfect Fluent API dump. It is a practical scaffold for dependency-aware automation. The agent should always inspect the live Fluent tree, read back values, and use documentation/TUI fallbacks when paths fail.

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

## Core automation rule

```text
enable parent -> refresh/reacquire tree -> inspect children/options -> set child -> read back -> log success/failure
```

Do not treat Fluent like a normal static Python object model. Treat it like a GUI state machine.

For compiled cell-zone sources, the working Fluent 2024 R2 sequence is:

```text
load clean mesh -> transfer authoritative case/settings -> verify zones/settings
-> fresh initialize -> allocate UDMs -> compile/load UDF -> attach source lists atomically
-> read every hook and RP control back -> save -> cold reload -> verify again
```

Never infer UDM reservation from a successful library-load call. Require the
positive reservation transcript and the expected named UDM fields. Never infer
source attachment from a setter returning normally; reacquire the source
container and compare its complete state. For a clean qualification start,
record that no `.dat.h5` was loaded and that zero production iterations ran.

## Canonical failure categories

Use these labels consistently in logs and notes:

1. `order/dependency issue`
2. `path/version issue`
3. `invalid value/format issue`
4. `PyFluent wrapper limitation`
5. `requires TUI fallback`
6. `requires manual GUI cleanup`

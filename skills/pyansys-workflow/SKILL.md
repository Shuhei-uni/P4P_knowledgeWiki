---
name: pyansys-workflow
description: "Use as the entrypoint for executable PyAnsys/Fluent work. Routes the task to inspection, case building, run orchestration, reusable code, and compact evidence handling without duplicating those procedures."
---

# PyAnsys Workflow

Start with `PyAnsys/AGENTS.md`. Use this skill as a router, not as a second operating contract.

## Route the task

- **Connection or live-state question** -> use the connection/inspection scripts first.
- **Creating or modifying a Fluent case** -> use `../fluent-case-build-and-run/SKILL.md`.
- **Planning or executing a calculation** -> use `../fluent-run-orchestration/SKILL.md`.
- **Post-simulation evidence extraction** -> use `../post-simulation-analysis/SKILL.md`.
- **Repository/output cleanup** -> use `../repo-maintenance/SKILL.md`.

## Common PyAnsys rules

For non-trivial Fluent mutation:

1. read the relevant `PyAnsys/knowledge/fluent-settings/` tree/order;
2. inspect the live Fluent state;
3. mutate in dependency order;
4. reacquire after parent/type/object changes;
5. read back critical settings.

Canonical pattern:

```text
enable/create parent -> reacquire -> inspect -> set -> read back
```

`server_id` is routing only, never case identity.

Keep case-specific scripts thin. Put reusable mechanics in `PyAnsys/src/pyansys_fluent/` and parameterize behavior that is likely to be reused rather than copying whole workflows.

Treat `PyAnsys/output/` as temporary/generated evidence. Keep only what remains useful for verification, recovery, analysis, plots, reporting, reproducibility, or active debugging.

## Example

If asked to create and run a new pressure sweep: use the case-build skill to produce and verify the siblings, then use the run-orchestration skill to decide how the prepared cases should be executed. Do not make `pyansys-workflow` itself define a second run policy.

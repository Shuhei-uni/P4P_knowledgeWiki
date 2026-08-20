---
name: fluent-case-build-and-run
description: "Use when deriving and verifying a Fluent child case from an explicit parent before handing it to the run-orchestration workflow. Covers parent/child identity, controlled deltas, recovery, dependency-order mutation, and reload verification."
---

# Fluent Case Build and Run

Use this skill to create and verify the case that will be run. Run-mode selection belongs in `../fluent-run-orchestration/SKILL.md`.

## Build the child case

1. Require an explicit parent-case path. `server_id` is routing only, never case identity.
2. Load the exact parent and reacquire all Fluent settings objects.
3. Define the intended delta and the important inherited settings that must remain unchanged.
4. If the loaded field state matters, preserve a separate recovery `.cas.h5` + `.dat.h5` pair before mutation.
5. Apply changes in dependency order:

```text
enable/create parent -> reacquire -> inspect -> set -> read back
```

6. Audit both the intended changes and the frozen invariants.
7. Write the child `.cas.h5`.
8. Reload the child and repeat the critical audit before declaring it ready.

Do not overwrite the parent or an existing child unless explicitly requested.

## Keep implementation reusable

Case scripts should stay thin. Put repeated connection, IO, mapping, inspection, checkpoint, or settings mechanics in `PyAnsys/src/pyansys_fluent/` rather than copying them between setup scripts.

## Handoff to execution

Once the child case is verified, hand the run-planning task to `../fluent-run-orchestration/SKILL.md` with:

- exact verified child-case path;
- parent path and intended delta;
- initialization requirements;
- required monitors/evidence;
- relevant recovery/checkpoint requirements;
- any unresolved assumptions that affect the run.

Do not choose a complicated run method merely because the case-building script already has a Python connection open.

## Example

**Pressure sibling:** load the verified parent, change only the brine outlet pressure, read back that pressure plus the frozen model/boundary settings, write and reload the sibling `.cas.h5`, then hand the sibling set to the run-orchestration skill for journal batching.

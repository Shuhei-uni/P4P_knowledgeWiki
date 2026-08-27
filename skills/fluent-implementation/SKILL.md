---
name: fluent-implementation
description: "Implement a selected P4P Fluent experiment from setup.md: inspect the parent, build and verify the case, then initialize/run it using the simplest robust mechanism."
---

# Fluent implementation

Use this skill for:

```text
setup.md → CASE → INITIALISE / RUN
```

Read the selected `setup.md` first and apply only its controlled delta.

## Proven-code and live-state rule

Inspect known-working repository code before constructing an equivalent
PyFluent access pattern from memory. Reuse the access pattern, not case-specific
names, values, paths, or branch assumptions. If the current live Fluent tree
differs, inspect and adapt.

Treat `server_id` as connection routing only. Establish parent and output case
identity from explicit paths or independently observed Fluent state, inspect
what is loaded, and do not overwrite a parent or existing output
unintentionally.

## Build the case

For dependency-sensitive state, use:

```text
enable/change parent → reacquire → inspect children/options
→ set one logical child → read back → continue
```

Reacquire after loading case/data or mesh, enabling a model, creating an object,
changing an object/type, or changing phase count. Verify critical intended
changes and important invariants by readback. Prefer existing reusable helpers;
extract a helper only when repeated working behaviour justifies it.

Write and verify the required case artifact. Record parent/start identity,
controlled change, critical readback, artifact location, and unresolved
implementation uncertainty. Do not put scientific conclusions in the builder.

## Initialize and run

Choose the simplest robust mechanism needed by the experiment:

```text
direct Fluent iterate | Fluent-native journal/batch
| bounded Python-supervised blocks when a decision is required between blocks
```

Do not categorically ban or require Python supervision. Fluent should own long
iteration and native autosave; record the actual method, requested budget,
observed state, and checkpoint/data locations. The documented 03A Stage-3
F01–F12 adaptive blocking path is a narrow exception, not a generic runner.

When a deep path is uncertain, use `fluent-live-inspection` rather than guess.

## Known working code

- `PyAnsys/src/pyansys_fluent/connection.py`
- `PyAnsys/src/pyansys_fluent/dependency_workflow.py`
- `PyAnsys/src/pyansys_fluent/common.py`

Search existing setup scripts for a proven case pattern, then parameterise it
for the current experiment and verify it against the current live state.

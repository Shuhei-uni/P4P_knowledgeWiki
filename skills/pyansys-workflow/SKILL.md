---
name: pyansys-workflow
description: "Use when working with PyAnsys executable automation for Fluent/PyFluent: connection checks, inspection scripts, setup rebuild scripts, remote Student Edition fallback, machine-readable validation targets, claim gates, dependency-ordered Fluent settings, or PyAnsys knowledge updates."
---

# PyAnsys Workflow

## Core Rule

Use `PyAnsys/` as the executable automation layer for Fluent setup, inspection, rebuild, focused run orchestration, machine-readable target manifests, and claim-gate logic. Treat Fluent as a dependency-ordered GUI state machine, not a stable static Python object tree.

For live end-to-end operations, route to the two non-skill workflow documents:

- `workflows/fluent-build-and-run.md`
- `workflows/fluent-analyze-and-report.md`

They orchestrate the four focused operational skills. Keep this
`pyansys-workflow` skill for PyAnsys code, tooling, environment, and knowledge
maintenance rather than using it as a fifth operational phase.

From now on, keep the workflow split:
- setup-building scripts create or modify only `.cas.h5`
- `PyAnsys/scripts/setup/save_data_after_iterations.py` is the standard runner for loading an existing `.cas.h5`, hybrid-initializing it, running iterations, and writing only `.dat.h5`

Do not merge setup mutation and run/save back into one large script unless the user explicitly asks for it.

Before non-trivial edits, read:

1. `AGENTS.md` at the repository root for cross-system routing.
2. `PyAnsys/AGENTS.md` for the local automation contract.
3. `PyAnsys/knowledge/fluent-settings/README.md`.
4. `PyAnsys/knowledge/fluent-settings/agent_start_prompt.md`.
5. `PyAnsys/knowledge/fluent-settings/indices/master_index.json`.
6. `PyAnsys/knowledge/fluent-settings/orders/global_setup_order.yaml`.
7. `PyAnsys/knowledge/fluent-settings/indices/path_dependency_index.json`.
8. Relevant model-specific `trees/*.md` and `orders/*.yaml`.
9. Core helpers: `src/pyansys_fluent/common.py`, `connection.py`, `dependency_workflow.py`, `setup_common.py`, and `setup_io.py`.

For non-interactive work, invoke the repository interpreter directly rather
than relying on activation state from an earlier shell or tool invocation:

```bash
/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python -c 'import sys; print(sys.executable)'
```

The expected path is
`/Users/shuheiyokkaichi/Developer/P4P_knowledgeWiki/PyAnsys/.venv/bin/python`.
Use that executable for every PyAnsys script. Interactive `source
.../.venv/bin/activate` is optional only within the same terminal session as
the following command.

## Search Workflow

Use `rg` to find existing helpers and prior discoveries before writing new code:

```bash
rg -n "target setting|boundary role|DPM|reacquire|readback|TUI|claim" PyAnsys/src PyAnsys/scripts PyAnsys/knowledge PyAnsys/docs
```

For setup intent or lineage, use `$setup-report` style lookup. For reusable CFD method logic, use `$cfd-wiki` style lookup. For project claim interpretation, use `$research-project-wiki` style lookup.

## Fluent Settings Rule

Follow this canonical order for non-trivial setting changes:

```text
enable parent -> refresh/reacquire -> inspect children/options -> set child -> read back -> classify failure
```

Mandatory habits:

- Reacquire objects after enabling models, creating objects, changing types, loading a case/data file, changing phase count, or switching boundary/model families.
- Inspect live child names, commands, and allowed values before setting deep paths.
- Treat readback mismatch as failure even when no exception was raised.
- Classify failures as `order/dependency issue`, `path/version issue`, `invalid value/format issue`, `PyFluent wrapper limitation`, `requires TUI fallback`, or `requires manual GUI cleanup`.

## Inspection-First Workflow

Before writing a setup script for a new Fluent branch:

1. Run `scripts/connection/check_connection.py`.
2. Run `scripts/inspection/inspect_fluent_session.py`.
3. Add a targeted non-mutating probe if paths or object names are unclear.
4. Only then edit or create mutation-heavy setup code.

Use the full multi-agent workflow described in `PyAnsys/AGENTS.md` when the task touches DPM, multiphase, Energy, EWF, nested path discovery, model activation order, setup derivation, TUI fallback, or physics assumptions.

## Code Placement

Keep file roles strict:

- `src/pyansys_fluent/`: reusable library code.
- `scripts/connection/`: bootstrap and preflight.
- `scripts/inspection/`: non-mutating discovery and probes.
- `scripts/setup/`: case-specific orchestration.
- `knowledge/fluent-settings/`: dependency order, settings trees, successful paths, and failures.
- `knowledge/`: machine-readable targets and claim-gate support.
- `output/`: generated extracts only; do not treat as authoritative knowledge.

Setup scripts should remain thin: parse inputs, connect, verify remote files, load case/mesh, inspect state, enable models, set materials/zones/boundaries/solution, read back, then write `.cas.h5`.

For initialization, iteration, and data writing, use the focused runner:

```text
PyAnsys/scripts/setup/save_data_after_iterations.py
input: remote .cas.h5 path + iteration count
output: derived name_X.dat.h5
loader helper: PyAnsys/src/pyansys_fluent/setup_io.py::load_case_only
```

Runner contract:
- load only the remote `.cas.h5`
- hybrid-initialize
- run iterations through the Settings API with TUI fallback
- write only `.dat.h5`
- verify the written `.dat.h5` is visible to Fluent

Do not add mesh loading, setup mutation, or case/data paired checkpoint persistence to this runner by default.

## Cross-System Sync

After PyAnsys work:

- If claim-gating behavior changed, align the human-readable rule in `ResearchProject_wiki/wiki/vnv/`.
- If reusable CFD method knowledge was discovered, summarize it in `CFD_wiki/`.
- If a concrete setup branch changed, sync the setup identity into `Setups/`.
- If target manifests or automated checks need human review, link them from the matching project V&V page.

Append new working paths, required orders, TUI workarounds, or repeatable failures to the relevant `PyAnsys/knowledge/fluent-settings/` files, at minimum `logs/successful_paths.md` for successful live discoveries.

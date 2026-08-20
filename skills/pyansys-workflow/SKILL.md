---
name: pyansys-workflow
description: "Use for executable PyAnsys/Fluent work: connection and inspection, dependency-ordered setup changes, selecting a run mode, writing run orchestration, and maintaining compact machine-readable evidence."
---

# PyAnsys Workflow

Use `PyAnsys/` for executable Fluent automation. Keep setup construction, run planning, and run execution distinct.

## 1. Inspect before changing Fluent

For non-trivial settings work:

1. read `PyAnsys/AGENTS.md` and the relevant `knowledge/fluent-settings/` order/tree;
2. connect through the repository helpers;
3. inspect the loaded case and active Fluent tree;
4. mutate in dependency order;
5. read back critical values.

Canonical pattern:

```text
enable/create parent -> reacquire -> inspect -> set -> read back
```

Never infer case identity from `server_id`; it is routing only.

## 2. Keep setup building separate

A setup builder should normally produce a verified `.cas.h5` and stop. Preserve an explicit case/data recovery pair first when modifying a developed solution whose field state matters.

Keep case-specific scripts thin and reuse `src/pyansys_fluent/` for shared mechanics.

## 3. Choose the run mode

| Mode | Use when | Agent involvement |
|---|---|---|
| **Simple TUI** | one prepared case, one uninterrupted run | submit one solve command |
| **Fluent journal** | several independent/fixed cases or stages | generate/submit robust journal; no need to supervise every case |
| **Agent-owned Python** | staged/adaptive run where later actions depend on intermediate evidence | supervise checkpoints and decisions through a recoverable state machine |

For journals, use explicit paths, unique outputs, transcripts and recovery/autosave as appropriate.

For agent-owned Python, reconcile actual Fluent state after reconnects before continuing. Provide the exact launch command plus supervisor instructions: what to watch, checkpoint locations, stage identification, stop conditions, and resume procedure.

Detailed policy: `PyAnsys/knowledge/fluent-settings/native_run_and_autosave.md`.

## 4. Keep `output/` small

`PyAnsys/output/` is temporary/generated evidence storage. Retain only artifacts still needed for checks, result reports, plots, reproducibility, or active debugging. Remove duplicate snapshots, superseded plots, temporary field dumps, and other regenerable bulk once they are no longer useful.

Do not use `output/` as the authoritative home for Fluent case/data archives.

## Failure rule

If a deep Fluent path fails, first check dependency order, reacquire the object, inspect active children/options, then classify the failure. Use a TUI fallback only after inspecting the Settings API path. Record reusable discoveries in `PyAnsys/knowledge/fluent-settings/`.

## Examples

**Simple case:** load a verified case, configure autosave if needed, then issue one TUI iteration command. Do not build an orchestration framework around it.

**Staged convergence ramp:** write a Python state-machine script that runs to the next checkpoint, inspects monitors, decides whether to change the solver state, records the checkpoint, and continues. Give the overseeing agent the exact command and recovery procedure.

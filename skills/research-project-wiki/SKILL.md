---
name: research-project-wiki
description: "Deprecated compatibility workflow for retained ResearchProject_wiki records; use project-loop and Project/ for current project work."
---

> **Transitional compatibility skill.** Do not route new current-state work here. Use `project-loop` and `Project/`; use this file only for explicitly authorized historical repair until the #19 cleanup stage.

# Research Project Wiki

## Core Rule

Use the root `Project/` layer for current project-specific interpretation, decisions, selected experiments, evidence boundaries, and claim limits. Use `ResearchProject_wiki/` only for retained detailed interpretation, technical notes, chronology, and human-readable V&V provenance until a later cutover. Do not duplicate reusable CFD methods from `CFD_wiki/` or concrete setup lineage from `Setups/`; link and summarize instead.

Before editing, read:

1. `AGENTS.md` at the repository root for cross-system routing.
2. `ResearchProject_wiki/AGENTS.md` for local schemas and required logs.
3. `Project/index.md` for current project authority, then `ResearchProject_wiki/wiki/index.md` for retained detail and provenance.

Never edit anything under `ResearchProject_wiki/raw/`.

## Search Workflow

Start from `Project/index.md`, then open only the relevant retained layer when needed:

- Scope detail: `ResearchProject_wiki/wiki/project/`
- Retained progress: `ResearchProject_wiki/wiki/progress/current-status.md`, `ResearchProject_wiki/wiki/progress/experiments.md`, `ResearchProject_wiki/wiki/progress/blockers.md`
- Technical detail: `ResearchProject_wiki/wiki/technical/` and `ResearchProject_wiki/wiki/model/`
- V&V and claim strength: `ResearchProject_wiki/wiki/vnv/`
- Literature/project evidence: `ResearchProject_wiki/wiki/sources/`, `ResearchProject_wiki/wiki/literature/`, `ResearchProject_wiki/wiki/synthesis/`
- Open issues: `ResearchProject_wiki/wiki/gaps/open-questions.md`

Use `rg` for targeted searches:

```bash
rg -n "run id|setup id|claim|blocker|inlet regime" ResearchProject_wiki/wiki
```

If the project question depends on prior CFD literature, use `$cfd-wiki` style lookup first, then carry only the project impact summary into `ResearchProject_wiki/`.

## Mandatory Progress Logging

If a task explicitly repairs retained progress history, append a dated entry to `ResearchProject_wiki/wiki/log.md` with operation tag `progress-update`. Ordinary progress updates belong in `Project/` and must not append to the frozen legacy log. Include:

- what changed since the last update;
- current status;
- blockers, or `None` if there are none;
- next action.

When available, also sync `ResearchProject_wiki/wiki/progress/current-status.md`.

## Modelling Work Workflow

When modelling work is performed, record the current experiment in `Project/experiments/<experiment-id>/setup.md` and `results.md`. For an explicit historical-record maintenance task only, use the retained workflow below:

1. Update `wiki/progress/current-status.md`.
2. Add a run entry to `wiki/progress/experiments.md` using the mandatory experiment schema.
3. Update `wiki/progress/blockers.md` if convergence failed or work is blocked.
4. Link to technical pages with settings and evidence.
5. Update or create `wiki/vnv/` records if claim strength changes.
6. Link PyAnsys machine-readable outputs from the matching V&V page when automation produced targets or claim-gate summaries.
7. Append one entry to `wiki/log.md`.

## Update Rules

Use evidence labels `Reported`, `Inferred`, and `Assumed`. Every setup-critical value needs a citation, preferably `([source-id], p.<page>)`, and units.

Use the project layers intentionally:

- `wiki/project/`: intent, scope, roadmap, phase decisions.
- `wiki/technical/` and `wiki/model/`: geometry, mesh, solver, boundary conditions, convergence diagnostics.
- `wiki/progress/`: execution tracking and blockers.
- `wiki/vnv/`: claim policy, verification, validation, target interpretation, sign-off.
- `wiki/sources/`, `wiki/literature/`, `wiki/synthesis/`: source extraction and project-facing synthesis.

Finish by updating the relevant `Project/` index or experiment record. Update `ResearchProject_wiki/wiki/index.md` or append `ResearchProject_wiki/wiki/log.md` only when the task explicitly changes retained wiki content or repairs its provenance.

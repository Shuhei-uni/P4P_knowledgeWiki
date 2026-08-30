---
name: research-project-wiki
description: "Retired workflow. Do not use. Current project scientific truth lives in Project/, starting at Project/index.md. Kept only for historical reference."
disable-model-invocation: true
---

# Research Project Wiki

**Retired / unrouted.** Do not use this skill as a current workflow authority.
Start at `Project/index.md` instead. Do not recreate `ResearchProject_wiki/`.

## Core Rule

Use `ResearchProject_wiki/` for project-specific interpretation, decisions, progress, technical notes, blockers, modelling records, and human-readable V&V sign-off. Do not duplicate reusable CFD methods from `CFD_wiki/` or concrete setup lineage from `Setups/`; link and summarize instead.

Before editing, read:

1. `AGENTS.md` at the repository root for cross-system routing.
2. `ResearchProject_wiki/AGENTS.md` for local schemas and required logs.
3. `ResearchProject_wiki/wiki/index.md` for the maintained page catalog.

Never edit anything under `ResearchProject_wiki/raw/`.

## Search Workflow

Start from `ResearchProject_wiki/wiki/index.md`, then open only the relevant layer:

- Scope: `wiki/project/`
- Progress: `wiki/progress/current-status.md`, `wiki/progress/experiments.md`, `wiki/progress/blockers.md`
- Technical detail: `wiki/technical/` and `wiki/model/`
- V&V and claim strength: `wiki/vnv/`
- Literature/project evidence: `wiki/sources/`, `wiki/literature/`, `wiki/synthesis/`
- Open issues: `wiki/gaps/open-questions.md`

Use `rg` for targeted searches:

```bash
rg -n "run id|setup id|claim|blocker|inlet regime" ResearchProject_wiki/wiki
```

If the project question depends on prior CFD literature, use `$cfd-wiki` style lookup first, then carry only the project impact summary into `ResearchProject_wiki/`.

## Mandatory Progress Logging

If the user prompt asks for `progress` in any form, append a dated entry to `ResearchProject_wiki/wiki/log.md` with operation tag `progress-update`. Include:

- what changed since the last update;
- current status;
- blockers, or `None` if there are none;
- next action.

When available, also sync `ResearchProject_wiki/wiki/progress/current-status.md`.

## Modelling Work Workflow

When modelling work is performed:

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

Finish by updating `ResearchProject_wiki/wiki/index.md` and appending `ResearchProject_wiki/wiki/log.md` whenever maintained wiki content changes.

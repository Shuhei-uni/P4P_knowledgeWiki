# Repository guide

This repository has three deliberately separate systems:

```text
CFD_wiki = reusable external CFD knowledge
Project  = current project-specific scientific truth
PyAnsys  = implementation, execution, and data tools
```

## Start with the current project

- Begin project work at [`Project/index.md`](Project/index.md).
- Load only the latest relevant experiment `setup.md` or `results.md`, then a parent record when the question requires it. Do not preload legacy logs or whole knowledge trees.
- Create `setup.md` and `results.md` together only for a human-selected experiment under `Project/experiments/<campaign>/<experiment>/`.
- Keep unselected proposals in the conversation or temporary reasoning; do not create repository records for them.
- Update `Project/index.md` only when the current scientific state changes. Git history is the operational history; do not create chat/work logs or duplicate project state.

## Keep ownership clear

- Put reusable literature, CFD methods, and generic Fluent guidance in `CFD_wiki/`; preserve its citations, evidence labels, units, and uncertainty.
- Put case implementation, execution, inspection, extraction, and generated evidence in `PyAnsys/`. Prefer proven reusable code and inspect dynamic Fluent state before inventing a new access pattern.
- Put current scientific questions, selected experiments, findings, and next uncertainty in `Project/`. Generated/debug artifacts are evidence or diagnostics, not project conclusions.
- `Setups/` and `ResearchProject_wiki/` are retained provenance/compatibility areas during this migration. Do not create new selected-work mirrors or delete historical material without the explicit cleanup stage.

## Core safeguards

- Never edit any file under a `raw/` directory.
- Do not silently copy case-specific names, values, paths, or branch assumptions between experiments.
- Keep source citations and `Reported`, `Inferred`, `Assumed`, `Missing`, and related uncertainty labels required by the owning local guide.
- Before changing a subsystem, read its local guide: [`CFD_wiki/AGENTS.md`](CFD_wiki/AGENTS.md), [`ResearchProject_wiki/AGENTS.md`](ResearchProject_wiki/AGENTS.md), or [`PyAnsys/AGENTS.md`](PyAnsys/AGENTS.md).

## Migration and task guides

For note moves, inspect the Git diff and search old references after the move; Obsidian does not rewrite every Markdown, code, or path-literal reference. Run `python3 scripts/check_stale_paths.py` after a move.

Use only the task-specific guide needed: [repository architecture](docs/agent-guides/repository-architecture.md), [content routing](docs/agent-guides/content-routing.md), [setup reports](docs/agent-guides/setup-reports.md), [Fluent guidance](docs/agent-guides/fluent-guidance.md), [evidence lookup](docs/agent-guides/evidence-lookup.md), [progress reporting](docs/agent-guides/progress-reporting.md), [wiki change discipline](docs/agent-guides/wiki-change-discipline.md), or [delegation](docs/agent-guides/delegation.md).

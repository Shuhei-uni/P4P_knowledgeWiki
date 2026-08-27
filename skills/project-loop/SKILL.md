---
name: project-loop
description: Review current P4P scientific state, propose experiments, create the selected experiment setup, or interpret results and update the next research direction.
---

# Project loop

Use this skill for the main scientific loop:

```text
Review → Propose → Human selects → setup.md → implementation → results.md
→ findings → update Project/index.md when current state changes → Review again
```

Start at `Project/index.md`. Load only the latest relevant experiment and the
parent evidence needed for the current question. Use `CFD_wiki` only when
reusable or external CFD evidence is required; use `PyAnsys` only for the
implementation, execution, or evidence-tooling branch.

## Review

Identify what is known, what remains unresolved, what the latest experiment
actually showed, and which uncertainty is worth reducing next. Do not read
historical progress logs by default.

## Propose

Propose a small set of experiments that distinguish useful explanations or
reduce the important uncertainty. Keep proposals in conversation or temporary
reasoning. Do not create setup records for unselected proposals.

## Create the selected setup

Create only the human-selected experiment under:

```text
Project/experiments/<campaign>/<experiment>/setup.md
Project/experiments/<campaign>/<experiment>/results.md
```

The setup should state the scientific question, selection rationale,
parent/start state, controlled change, frozen context, run requirement or
budget, and evidence/monitors required. Prefer a concise delta from a known
parent instead of restating the entire Fluent case. It is ready when
`fluent-implementation` can execute it without reconstructing scientific
intent.

## Review results

Read the experiment `results.md` and keep these separate:

```text
measured evidence | evidence limitations | observations | findings/interpretation
```

Add findings only where the evidence supports them. State what the result
implies for the next review, but do not create the next setup until a human
selects it.

Update `Project/index.md` only when current scientific state changes. Do not
maintain a second chronological work log or duplicate the same truth across
systems.

## Ownership

```text
Project  = project-specific scientific truth
CFD_wiki = reusable/external CFD knowledge
PyAnsys  = implementation and evidence tooling
```

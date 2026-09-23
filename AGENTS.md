# Repository contract

Route truth to one owner:

| Owner | Stores |
| --- | --- |
| `Project/` | Current project question, phase scope, selected work, results, and claim limits |
| `CFD_wiki/` | Reusable CFD literature, methods, and generic Fluent guidance |
| `PyAnsys/` | Executable Fluent/PyFluent implementation and machine evidence |
| `.agents/skills/` | A small set of workflows that operate on those owners |

For project science start at `Project/index.md`, then read only the active
phase material needed for the current decision.

## Workflow map

Use one owning workflow skill and let it follow its internal references:

- `phase-planner` — human phase framing/reframing;
- `phase-loop` — experiment selection, execution, recovery, analysis, and phase closure;
- `pyansys-workflow` — Fluent implementation/execution;
- `cfd-numerical-analysis` — CFD evidence and figures;
- `cfd-wiki` — reusable research/method knowledge;
- `report-writing` — technical report production;
- `workflow-surgeon` — repair the agent workflow itself;
- `writing-for-agents` — edit agent instructions;
- `wait-what` and `direct-fluent-use` — explicit human controls.

A sub-step is not a reason to create another `SKILL.md`. Put branch-specific
procedure/reference material inside the owning workflow folder. Create a new
skill only when it needs a genuinely distinct invocation boundary.

Fluent runs:
When running simulations try to run in large batches, rather than iter(10) do around 1000 (Prefer using TUI run commands for cases where its just setup and then run) and when saving checkpoint save it on fluent local machine rather than onedrive. Onedrive is for start or final case/data pair that we'd like to share across computers not a place to store everything.

## Autonomy

The human sets or changes the scientific envelope through `phase-planner`.
Inside that envelope, `phase-loop` owns ordinary experiment choice, technical
recovery, analysis, and continuation.

Do not turn implementation errors, solver failures, missing plots, or routine
evidence gaps into human review gates. Recover them in-scope or record a durable
external block. Ask the human only when the scientific scope/goal must change,
an unauthorized irreversible external action is required, or the user's
judgement is itself the missing input.

Before a consequential decision, consult only the evidence sources that could
change it: current Project evidence, reusable CFD evidence, and live/version-
matched Fluent evidence. Parallel review is optional when it resolves a concrete
uncertainty; it is not ceremony.

## Durable truth

- Keep a fact in its owning system and link to it elsewhere.
- `CONTEXT.md` holds the current phase contract; `setup.md` holds runnable
  scientific intent; `results.md` holds evidence/interpretation;
  `phase-state.yaml` holds compact machine state.
- Git history is chronology. Avoid diary-style duplicate logs.
- Treat every `raw/` directory as immutable source/generated evidence.
- Carry case-specific names, values, parents, and assumptions only from verified
  records for that case.

## Fluent safety

Preserve valuable endpoints before replacement and never terminate an unrelated
or unpreserved Fluent process. When the active phase explicitly owns the
session/fleet, its recorded authority governs restart/recreate recovery.

## Skill maintenance

Use `writing-for-agents` when editing agent instructions and keep the active
invocation map in [`.agents/invocation.md`](.agents/invocation.md).

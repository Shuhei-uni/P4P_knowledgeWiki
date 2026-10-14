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

## File management

After pulling changes, inspect `git status --short` and the repository root.
Check newly added paths against the owner table before creating more files.

- Store phase-specific proposals, observations, technical notes and scientific
  figures under `Project/experiments/<phase>/`. Keep shared model guidance and
  cross-phase comparisons in the shared Project folders.
- Store Shuhei's report in `Project/Final research report/Shuhei Report/`,
  Andy's report in `Project/Final research report/andy-draft/`, and poster
  sections and assets in `Project/Poster/`. Keep shared report guidance beside
  the two report folders. Store shared meeting material in `Project/meetings/`
  and its retained exports/review images in `Project/meetings/output/`.
- Put executable utilities in the appropriate `PyAnsys/scripts/` category,
  reusable Python modules in `PyAnsys/src/`, implementation documentation in
  `PyAnsys/docs/`, and historical implementation notes in `PyAnsys/docs/historical/`.
  Machine-generated evidence stays under `PyAnsys/output/` or its existing
  recorded machine owner.
- Use an operating-system temporary directory for disposable scratch files.
  Retain useful review images beside their report or meeting output. The root
  contains the owner directories, repository configuration and README support
  assets; create task output inside its owner instead of a new root work folder.
- When moving files, update links, imports, generator destinations, tests and
  agent references. Remove empty source folders. Preserve every `raw/` directory
  and follow the existing active-controller safety rules.
- Before committing, review `git diff --name-status` and the staged diff.
  Include both sides of each move and only changes authorized for that commit.
  Check affected links and the smallest relevant runtime/test path.

## Workflow map

Use one owning workflow skill and let it follow its internal references:

- `phase-planner` — human phase framing/reframing;
- `phase-loop` — experiment selection, execution, recovery, analysis, and phase closure;
- `configure-run-monitor` — scheduled-monitor configuration and planner handoff;
- `pyansys-workflow` — Fluent implementation/execution;
	- New EWF setups must prove the intended drainage path, including direct film removal with frozen bulk when that mode is required; see its inspection/build reference.
- `cfd-numerical-analysis` — CFD evidence and figures;
- `cfd-wiki` — reusable research/method knowledge;
- `report-writing` — assemble Project evidence and figures into technical reports;
- `stem-research-writing` — academic argument, findings to emphasise, report flow, and scientific prose;
- `spatial-composition` — visual hierarchy, depth, and editable composition for posters, slides, and web layouts;
- `workflow-surgeon` — repair the agent workflow itself;
- `writing-for-agents` — edit agent instructions;
- `wait-what` and `direct-fluent-use` — explicit human controls.

A sub-step is not a reason to create another `SKILL.md`. Put branch-specific
procedure/reference material inside the owning workflow folder. Create a new
skill only when it needs a genuinely distinct invocation boundary.

Fluent runs: use 1000 or more iterations while inputs stay fixed, bounded by the
next required experiment decision. Use short commands for one smoke check or
scheduled input changes. Observe live output without splitting a fixed solve.
Save checkpoints and transcripts on the Fluent computer's local disk; use
OneDrive for shared starting files and selected final pairs. Follow the
`pyansys-workflow` run-control reference for detached execution and supervision.

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

For file lookup, use `rg --files` to locate an owner, `rg -n` to find the relevant
section, then read only that section or selected JSON fields. Keep combined
parallel output within the tool budget. Reuse unchanged material already read;
refresh mutable state when it can change the decision. If output is truncated,
narrow the query instead of printing the same large result again.

### Writing/Reponding
For Markdown under `Project/experiments/`, use tables and figures as the main
content. Apply the [experiment presentation contract](Project/experiments/README.md#presentation)
to setup, results, context, index, and interpretation records.
When writing a back to me, use 90% of the way to ASD-STE100. For report writing use 80% of the way to ASD-STE100.
I like the use of of diagrams/images, this helps me visualise a process, an idea, a problem and allows me to understand what you're convey much easier. This could be generated by you or made through fluent.

For plots, I prefer a simple plot done through python. Basic Matplotlib plot will do.

## Fluent safety

Preserve valuable endpoints before replacement and never terminate an unrelated
or unpreserved Fluent process. When the active phase explicitly owns the
session/fleet, its recorded authority governs restart/recreate recovery.

## Skill maintenance

Use `writing-for-agents` when editing agent instructions and keep the active
invocation map in [`.agents/invocation.md`](.agents/invocation.md).

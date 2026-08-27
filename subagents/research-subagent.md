# Research Subagent Brief

Work in the root `Project/` authority for ordinary current-state work. Work in retained `ResearchProject_wiki` detail/provenance records only when the task explicitly repairs or annotates that historical corpus. Read `Project/index.md` before advising on current project state.

## Mission

Maintain the project-specific evidence trail:
- current status
- experiment trace
- blockers
- project decisions
- interpretation of what the CFD work means for this research project

## Primary Files You May Touch

- `Project/`
- `Project/index.md`
- `Project/experiments/`
- `ResearchProject_wiki/wiki/`
- `ResearchProject_wiki/wiki/index.md`
- `ResearchProject_wiki/wiki/log.md`
- `ResearchProject_wiki/wiki/progress/`

## Do

- read `Project/index.md` first, then `ResearchProject_wiki/wiki/index.md` for retained detail
- link to `CFD_wiki` pages instead of duplicating reusable technical detail
- record current progress in the relevant `Project/` page or selected experiment; append legacy progress entries only for explicit historical repair
- keep blockers, assumptions, and next actions explicit
- treat non-converged runs and failed ideas as first-class project evidence

## Do Not

- write generic CFD tutorial material that belongs in `CFD_wiki`
- create or rename setup lineage records in `Setups/`
- present assumptions as reported facts

## Mandatory Reminder

If the task explicitly repairs retained progress history, you must:
1. append a dated entry to `ResearchProject_wiki/wiki/log.md` using `progress-update`;
2. include what changed, current status, blockers, and next action;
3. sync `ResearchProject_wiki/wiki/progress/current-status.md` if the retained historical state changed. Ordinary current-state updates belong in `Project/`.

## Handoff Back to Main Agent

Return:
- the project-state update
- any unresolved blocker
- any cross-link needed to CFD or setup-report material

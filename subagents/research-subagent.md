# Research Subagent Brief

Work only in `ResearchProject_wiki` unless the main agent explicitly expands scope.

## Mission

Maintain the project-specific evidence trail:
- current status
- experiment trace
- blockers
- project decisions
- interpretation of what the CFD work means for this research project

## Primary Files You May Touch

- `ResearchProject_wiki/wiki/`
- `ResearchProject_wiki/wiki/index.md`
- `ResearchProject_wiki/wiki/log.md`
- `ResearchProject_wiki/wiki/progress/`

## Do

- read `ResearchProject_wiki/wiki/index.md` first
- link to `CFD_wiki` pages instead of duplicating reusable technical detail
- append progress-style entries when the user's request is about progress
- keep blockers, assumptions, and next actions explicit
- treat non-converged runs and failed ideas as first-class project evidence

## Do Not

- write generic CFD tutorial material that belongs in `CFD_wiki`
- create or rename setup lineage records in `Setups/`
- present assumptions as reported facts

## Mandatory Reminder

If the user asks for `progress`, you must:
1. append a dated entry to `ResearchProject_wiki/wiki/log.md` using `progress-update`;
2. include what changed, current status, blockers, and next action;
3. sync `ResearchProject_wiki/wiki/progress/current-status.md` if the project state changed.

## Handoff Back to Main Agent

Return:
- the project-state update
- any unresolved blocker
- any cross-link needed to CFD or setup-report material

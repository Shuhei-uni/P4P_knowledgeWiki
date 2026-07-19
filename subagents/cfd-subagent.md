# CFD Subagent Brief

Work only in `CFD_wiki` unless the main agent explicitly expands scope.

## Mission

Produce reusable CFD knowledge:
- paper lookup support
- source extraction
- Fluent click-by-click guidance
- setup reconstruction sheets
- cross-paper synthesis

## Primary Files You May Touch

- `CFD_wiki/wiki/`
- `CFD_wiki/paper_lookup/`
- `CFD_wiki/wiki/index.md`
- `CFD_wiki/wiki/log.md`

## Do

- read `CFD_wiki/wiki/index.md` first
- use `CFD_wiki/paper_lookup/index.md` for complex CFD evidence scans
- preserve `Reported`, `Inferred`, `Assumed`, `Missing`, and `Not Applicable` labels
- keep Fluent guidance procedural and reusable
- link new material to existing entities, concepts, setups, or synthesis pages when relevant

## Do Not

- write project-progress narration
- update `ResearchProject_wiki` directly unless the main agent explicitly asks
- create setup-instance lineage records in `Setups/`
- duplicate full project-specific explanations that belong elsewhere

## Handoff Back to Main Agent

Return:
- the reusable CFD result
- any project-impact summary in 2-4 lines if needed
- any setup-report implication that should be handled separately

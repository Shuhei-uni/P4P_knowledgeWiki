# AGENTS.md

## Mission
This repository has two separate but linked knowledge systems:
- `CFD_wiki`
- `ResearchProject_wiki`

Use both wikis together without mixing their roles, so shared CFD knowledge stays reusable and project execution stays traceable.

## Wiki Roles (Separated Knowledge)
- `CFD_wiki`: reusable CFD reconstruction knowledge, paper extraction, solver/model setup patterns, cross-paper synthesis.
- `ResearchProject_wiki`: project-specific decisions, experiment progress, blockers, milestones, and report-facing evidence trail.

Do not duplicate full pages across both wikis. Link and summarize instead.

## Routing Rules
When handling a request, route content first, then write:
1. If the request is generic CFD method/literature/setup knowledge, update `CFD_wiki` first.
2. If the request is specific to the geothermal separator research project, update `ResearchProject_wiki`.
3. If both apply, write core technical extraction in `CFD_wiki`, then add a project-impact summary in `ResearchProject_wiki` with links to the CFD page.

## Fluent Guidance Priority Rule
For setup/how-to questions in Fluent:
1. Check `CFD_wiki/wiki/guidance/` first and answer with click-by-click steps.
2. Then pull case-specific numerical values from `CFD_wiki/wiki/setups/` and/or project pages as needed.
3. If the question is project-specific, still keep the generic click paths in `CFD_wiki/wiki/guidance/` and only summarize project impact in `ResearchProject_wiki`.

## Cross-Wiki Orchestration Workflow
For work that touches both wikis:
1. Read indexes first:
   - `CFD_wiki/wiki/index.md`
   - `ResearchProject_wiki/wiki/index.md`
2. Update the primary target wiki based on routing rules.
3. Add a short cross-reference note in the secondary wiki (no large duplication).
4. Update index/log files in any wiki that changed.

## Mandatory Progress Logging Rule
Any time the user prompt asks for `progress` (for example: "progress", "show progress", "update progress", "what's the progress"):
1. Append a new dated entry to:
   - `ResearchProject_wiki/wiki/log.md`
2. Use operation tag:
   - `progress-update`
3. Include:
   - what changed since last update
   - current status
   - blockers (if any)
   - next action
4. If available, also sync:
   - `ResearchProject_wiki/wiki/progress/current-status.md`

This rule is mandatory even when the core technical work happened in `CFD_wiki`.

## Source Integrity
- Never edit files under any `raw/` directory.
- Keep citations and uncertainty labels from each wiki's local `AGENTS.md` contract.

## Conflict Resolution
If a rule here conflicts with a wiki-local `AGENTS.md`:
- Follow local schema/style inside that wiki.
- Still enforce the mandatory progress logging rule to `ResearchProject_wiki`.

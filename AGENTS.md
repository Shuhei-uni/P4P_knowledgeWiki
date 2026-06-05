# AGENTS.md

## Mission
This repository has three separate but linked knowledge systems:
- `CFD_wiki`
- `ResearchProject_wiki`
- `Setup report`

Use them together without mixing their roles, so shared CFD knowledge stays reusable, project execution stays traceable, and setup-branch lineage stays easy to follow.

## Knowledge Roles (Separated Knowledge)
- `CFD_wiki`: reusable CFD reconstruction knowledge, paper extraction, solver/model setup patterns, cross-paper synthesis.
- `ResearchProject_wiki`: project-specific decisions, experiment progress, blockers, milestones, and report-facing evidence trail.
- `Setup report`: ordered case-definition records for concrete setup branches, parent/child variants, and report-ready setup snapshots.

Do not duplicate full pages across these systems. Link and summarize instead.

## Setup Report Role
Use `Setup report/` for setup-instance documents, not for generic CFD knowledge and not for day-to-day progress logging.

Put these in `Setup report/`:
- named case/setup definitions;
- parent/child setup variants;
- strict sequence/history of how one setup branch led to another;
- report-facing setup snapshots with concrete boundary conditions, assumptions, and calculation notes.

Do not use `Setup report/` for:
- reusable cross-project CFD guidance;
- literature extraction or paper synthesis;
- general project status, blockers, or milestone tracking.

The controlling map for setup-report lineage is:
- `Setup report/order-dictionary.md`

## Routing Rules
When handling a request, route content first, then write:
1. If the request is generic CFD method/literature/setup knowledge, update `CFD_wiki` first.
2. If the request is specific to the geothermal separator research project, update `ResearchProject_wiki`.
3. If the request is about a specific simulation setup/report branch, active case definition, setup naming, or setup lineage, update `Setup report/`.
4. If both apply, write core technical extraction in `CFD_wiki`, then add a project-impact summary in `ResearchProject_wiki` with links to the CFD page.
5. If the work defines or changes a concrete setup branch, keep the technical/project context in the appropriate wiki and store the actual setup-instance record in `Setup report/`.

## Fluent Guidance Priority Rule
For setup/how-to questions in Fluent:
1. Check `CFD_wiki/wiki/guidance/` first and answer with click-by-click steps.
2. Then pull case-specific numerical values from `CFD_wiki/wiki/setups/` and/or project pages as needed.
3. If the question is project-specific, still keep the generic click paths in `CFD_wiki/wiki/guidance/`, use `ResearchProject_wiki` for project impact, and use `Setup report/` only if a concrete setup report must be created or revised.

## Cross-System Orchestration Workflow
For work that touches multiple knowledge systems:
1. Read indexes first:
   - `CFD_wiki/wiki/index.md`
   - `ResearchProject_wiki/wiki/index.md`
   - `Setup report/order-dictionary.md` if setup lineage or naming is involved
2. Update the primary target based on routing rules.
3. Add a short cross-reference note in the secondary system(s) when needed (no large duplication).
4. Update index/log files in any wiki that changed.
5. If a setup report changed, update `Setup report/order-dictionary.md` whenever the change affects ordering, branch identity, or naming.

## Subagent Operating Model
This repository supports a lightweight subagent workflow without requiring separate worktrees.

Use subagents as scoped workers, not as independent owners of truth.
The main agent remains responsible for routing, cross-system consistency, and final write approval.

### Main Agent Responsibilities
- read the root routing contract first;
- decide the primary target system before writing;
- assign at most one primary subagent by default;
- assign a secondary subagent only when the task genuinely spans systems;
- reconcile overlaps, remove duplication, and ensure indexes/logs/order maps are updated;
- treat repository files, not old chats, as the durable source of truth.

### Available Subagents
- `CFD subagent`
  - lane: `CFD_wiki`
  - purpose: paper lookup, source extraction, Fluent guidance, reusable setup logic, cross-paper synthesis
- `Research subagent`
  - lane: `ResearchProject_wiki`
  - purpose: project decisions, progress, blockers, experiment interpretation, next actions
- `Setup subagent`
  - lane: `Setup report/`
  - purpose: setup-instance records, branch naming, parent/child lineage, report-facing setup snapshots

### Subagent Deployment Rule
Use subagents when:
- the task is multi-step and would benefit from scoped parallel thinking;
- the task spans more than one knowledge role;
- the task needs a reusable extraction or cleanup pass that should stay within one lane.

Do not use subagents when:
- the task is a small single-file update;
- routing is obvious and the edit is short;
- the task is mostly conversational and does not require durable file changes.

### Subagent Authority Boundaries
- Subagents may edit only within their assigned lane unless the main agent explicitly expands scope.
- Subagents must not decide repository routing policy.
- Subagents must not duplicate full content across systems.
- Subagents must not archive chats.
- Subagents must never edit any `raw/` directory.

### Default Coordination Pattern
1. Main agent classifies the task.
2. Main agent selects the primary subagent.
3. Primary subagent drafts or updates only its lane.
4. If needed, a secondary subagent adds a short supporting update in its own lane.
5. Main agent integrates, deduplicates, updates cross-links, and verifies logs/indexes/order references.

### Quality Gate Before Accepting Subagent Output
Before finalizing subagent work, verify:
1. the correct primary wiki or setup system was chosen;
2. citations and uncertainty labels follow the local contract;
3. full-page duplication was avoided across systems;
4. changed systems had their index/log files updated as required;
5. `Setup report/order-dictionary.md` was updated if setup lineage changed;
6. `ResearchProject_wiki/wiki/log.md` and `ResearchProject_wiki/wiki/progress/current-status.md` were updated when project state changed.

### Prompt Source
Reusable prompt briefs for each subagent live in:
- `subagents/README.md`
- `subagents/cfd-subagent.md`
- `subagents/research-subagent.md`
- `subagents/setup-subagent.md`

## Setup Report Ordering Rule
When creating, renaming, or reorganizing files in `Setup report/`:
1. Check `Setup report/order-dictionary.md` first.
2. Preserve the existing numbered sequence once assigned.
3. Prefer adding a new number or branch suffix such as `08`, `08a`, or `08b` over renaming older reports again.
4. Avoid status words like `current`, `latest`, or `final` in setup-report filenames.
5. Update cross-links and any wiki references that point to the renamed or newly added setup report.

## Setup Report Creation Rule
Create or update a `Setup report/` file when the request involves any of:
- a new setup branch or variant;
- a concrete Fluent boundary-condition package for a named case;
- a report-facing setup record for a run or planned run;
- setup cleanup, ordering, naming, or parent/child lineage reconstruction.

If the request only needs reusable guidance or project interpretation, do not create a setup report unnecessarily.

## Complex Task CFD Lookup Rule
For complex tasks, quickly check the CFD paper lookup layer before deciding what evidence or prior research applies.

Use this rule when the request involves any of:
- CFD model choices, solver setup, boundary conditions, mesh/numerics, validation, or uncertainty.
- Geothermal separator design, steam-water separation, carryover, steam purity, entrainment/deposition, annular flow, geofluid properties, or downstream ORC/system implications.
- Multi-step research/project decisions where prior papers may change the recommended approach.

Workflow:
1. Read `CFD_wiki/paper_lookup/index.md`.
2. Open only the relevant chunk file(s) under `CFD_wiki/paper_lookup/`.
3. Use the lookup to identify applicable source/setup/synthesis pages or raw-paper sections.
4. Carry applicable evidence into the answer or wiki update with citations and uncertainty labels.
5. If nothing applies, state that the CFD lookup was checked and no relevant prior-paper guidance was found.

This is a quick evidence scan, not a full ingest. Do not load every dictionary chunk unless the task genuinely spans all topics.

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

## Operating Discipline
These rules adapt general coding-agent caution to this knowledge-wiki repository. They are meant to reduce unnecessary edits, invented certainty, and accidental mixing of the three knowledge roles.

### Think Before Writing
Before editing wiki pages or setup reports:
- State key assumptions when the request can be interpreted more than one way.
- If routing is ambiguous, identify the likely target wiki and why before writing.
- If a simpler response without file edits would satisfy the user, say so.
- If source evidence is missing or unclear, label the uncertainty instead of filling gaps silently.

### Simplicity First
- Add the minimum content needed to answer the request or preserve the evidence trail.
- Do not create new pages, templates, categories, or workflows unless the existing structure cannot hold the information cleanly.
- Prefer short summaries with links over duplicated explanations across both wikis.
- Keep beginner-facing Fluent guidance practical and step-wise; avoid theory unless it directly helps the setup task.

### Surgical Wiki Changes
When editing existing wiki content or setup reports:
- Touch only files required by the routing rules, local schema, index updates, and log requirements.
- Match the page's existing structure, heading style, citation style, and uncertainty labels.
- Do not rewrite adjacent sections just for polish.
- Do not remove or relabel previous assumptions, blockers, or failed experiments unless the new evidence directly supersedes them.
- If unrelated stale or duplicated content is noticed, mention it rather than fixing it opportunistically.

### Goal-Driven Execution
For multi-step wiki work, define a brief success checklist before editing:
1. Target page(s) updated with the requested knowledge or project trace.
2. Citations, labels, and missing-information notes preserved or added as needed.
3. Cross-links, indexes, logs, and setup-order references updated for every system that changed.

After editing, verify the changed files still satisfy the relevant local `AGENTS.md` schema and the root routing rules.

## Conflict Resolution
If a rule here conflicts with a wiki-local `AGENTS.md`:
- Follow local schema/style inside that wiki.
- Still enforce the mandatory progress logging rule to `ResearchProject_wiki`.

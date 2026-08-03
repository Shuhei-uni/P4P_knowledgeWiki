# AGENTS.md

## Mission
This repository has four linked systems with different jobs:
- `CFD_wiki`
- `ResearchProject_wiki`
- `Setups`
- `PyAnsys`

Use them together without mixing their roles, so shared CFD knowledge stays reusable, project execution stays traceable, setup-branch lineage stays easy to follow, and automation artifacts stay machine-usable.

## Knowledge Roles (Separated Knowledge)
- `CFD_wiki`: reusable CFD reconstruction knowledge, paper extraction, solver/model setup patterns, cross-paper synthesis.
- `ResearchProject_wiki`: project-specific decisions, experiment progress, blockers, milestones, report-facing evidence trail, and project-owned verification/validation records.
- `Setups`: ordered case-definition records for concrete setup branches, parent/child variants, and report-ready setup snapshots.
- `PyAnsys`: executable automation workspace for Fluent setup, inspection, rebuild, run orchestration, and machine-readable target/claim-gate artifacts.

Do not duplicate full pages across these systems. Link and summarize instead.

## Top-Level Directory Map
- `CFD_wiki/`: reusable literature, method, and Fluent-guidance knowledge.
- `ResearchProject_wiki/`: project-facing interpretation, progress, technical notes, and `wiki/vnv/` sign-off records.
- `Setups/`: setup lifecycle views, lineage, and concrete case-definition history, controlled by `Setups/order-dictionary.md`.
- `PyAnsys/`: automation code, inspection tools, setup scripts, extracted case knowledge, and machine-readable V&V target logic.
- `skills/`: focused repo-local Codex operating skills.
- `workflows/`: non-skill orchestration documents that call the focused skills.
- `PROJECT_TREE.md`: quick orientation tree for the repo layout.

For the laptop-controlled Fluent loop, use:
- `workflows/fluent-build-and-run.md`
- `workflows/fluent-analyze-and-report.md`

These workflows call exactly four focused skills under `skills/`: case build,
initialization/run, result analysis, and results-report writing. They read setup
Markdown directly and do not hash it.

## Setup Report Role
Use `Setups/` for setup-instance documents, not for generic CFD knowledge and not for day-to-day progress logging.

Put these in `Setups/`:
- named case/setup definitions;
- parent/child setup variants;
- strict sequence/history of how one setup branch led to another;
- report-facing setup snapshots with concrete boundary conditions, assumptions, and calculation notes.

Do not use `Setups/` for:
- reusable cross-project CFD guidance;
- literature extraction or paper synthesis;
- general project status, blockers, or milestone tracking.

The controlling map for setup-report lineage is:
- `Setups/order-dictionary.md`

## Routing Rules
When handling a request, route content first, then write:
1. If the request is generic CFD method/literature/setup knowledge, update `CFD_wiki` first.
2. If the request is specific to the geothermal separator research project, update `ResearchProject_wiki`.
3. If the request is about a specific simulation setup/report branch, active case definition, setup naming, or setup lineage, update `Setups/`.
4. If the request is about executable automation, PyFluent path discovery, machine-readable validation targets, or claim-gate scripts, update `PyAnsys` first and then sync any needed human-readable summary into the relevant wiki.
5. If both apply, write core technical extraction in `CFD_wiki`, then add a project-impact summary in `ResearchProject_wiki` with links to the CFD page.
6. If the work defines or changes a concrete setup branch, keep the technical/project context in the appropriate wiki and store the actual setup-instance record in `Setups/`.

## Fluent Guidance Priority Rule
For setup/how-to questions in Fluent:
1. Check `CFD_wiki/wiki/guidance/` first and answer with click-by-click steps.
2. Then pull case-specific numerical values from `CFD_wiki/wiki/setups/` and/or project pages as needed.
3. If the question is project-specific, still keep the generic click paths in `CFD_wiki/wiki/guidance/`, use `ResearchProject_wiki` for project impact, and use `Setups/` only if a concrete setup report must be created or revised.

## Cross-System Orchestration Workflow
For work that touches multiple knowledge systems:
1. Read indexes first:
   - `CFD_wiki/wiki/index.md`
   - `ResearchProject_wiki/wiki/index.md`
   - `Setups/order-dictionary.md` if setup lineage or naming is involved
   - `PyAnsys/AGENTS.md` and relevant `PyAnsys/knowledge/` paths if automation or machine-readable targets are involved
2. Update the primary target based on routing rules.
3. Add a short cross-reference note in the secondary system(s) when needed (no large duplication).
4. Update index/log files in any wiki that changed.
5. If a setup report changed, update `Setups/order-dictionary.md` whenever the change affects ordering, branch identity, or naming.
6. If automation behavior or target manifests changed, keep the human-readable claim logic aligned with `ResearchProject_wiki/wiki/vnv/`.

## Subagent Workflow
For larger multi-step or cross-system tasks, use the lightweight subagent briefs in:
- `subagents/README.md`
- `subagents/cfd-subagent.md`
- `subagents/research-subagent.md`
- `subagents/setup-subagent.md`

Keep the root routing rules in this file as the source of truth. Subagents are scoped helpers only; the main agent remains responsible for routing, deduplication, cross-links, index/log/order updates, and final consistency checks.

## Setup Report Ordering Rule
When creating, renaming, or reorganizing files in `Setups/`:
1. Check `Setups/order-dictionary.md` first.
2. Preserve the existing numbered sequence once assigned.
3. Prefer adding a new number or branch suffix such as `08`, `08a`, or `08b` over renaming older reports again.
4. Avoid status words like `current`, `latest`, or `final` in setup-report filenames.
5. Update cross-links and any wiki references that point to the renamed or newly added setup report.

## Setup Report Creation Rule
Create or update a `Setups/` file when the request involves any of:
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

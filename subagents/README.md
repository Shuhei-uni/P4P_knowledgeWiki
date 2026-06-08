# Subagent Workflow

This directory defines the lightweight subagent model for `P4P_knowledgeWiki`.

These files are prompt briefs and operating constraints, not independent policy documents.
The root [`AGENTS.md`](../AGENTS.md) remains the routing source of truth.

## Why These Subagents Exist

The repository has three different knowledge roles:
- reusable CFD knowledge
- project-specific research trace
- setup-branch records

Subagents help keep those roles separate during larger tasks.
They are meant to reduce duplication and context sprawl, not to replace the main agent.

## Available Subagents

### 1. CFD subagent
- prompt file: `cfd-subagent.md`
- lane: `CFD_wiki`
- use for: paper lookup, Fluent guidance, reusable setup extraction, synthesis

### 2. Research subagent
- prompt file: `research-subagent.md`
- lane: `ResearchProject_wiki`
- use for: progress, blockers, project interpretation, next actions, report trace

### 3. Setup subagent
- prompt file: `setup-subagent.md`
- lane: `Setup report/`
- use for: setup definitions, numbering, branch lineage, report-facing case records

## Main-Agent Rule

The main agent must:
1. decide the primary target first;
2. deploy one primary subagent by default;
3. use a secondary subagent only if cross-system support is genuinely needed;
4. integrate outputs and remove duplication before finalizing.

## Typical Assignment Patterns

- Generic CFD question:
  - primary: `CFD subagent`
- Project progress or blocker update:
  - primary: `Research subagent`
- New case definition or setup branch:
  - primary: `Setup subagent`
  - secondary: `Research subagent` only if project state changes
- Reusable CFD extraction with project impact:
  - primary: `CFD subagent`
  - secondary: `Research subagent`

## Handoff Standard

Any subagent handoff should be short and include:
- what file(s) it touched or recommends touching;
- what assumptions remain;
- what should be logged or cross-linked next.

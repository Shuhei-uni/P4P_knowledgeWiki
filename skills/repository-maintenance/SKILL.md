---
name: repository-maintenance
description: Maintain the lean P4P repository structure, route content to the correct owner, make bounded cross-system edits, and delegate focused audit/review work.
---

# Repository maintenance

Use this skill when changing repository structure, moving/routing knowledge, cleaning obsolete material, or coordinating a multi-area repository edit.

## Ownership

```text
CFD_wiki = reusable CFD literature, methods, generic Fluent guidance
Project  = project-specific scientific truth, selected experiments, findings, claim limits
PyAnsys  = Fluent implementation, inspection, execution, extraction, machine evidence
skills   = focused repeatable procedures
```

Start project work from `Project/index.md`. Do not recreate the retired project wiki, numbered Setups/report architecture, progress logs, or a giant legacy tree merely to preserve old navigation; exact retired history remains recoverable from Git.

## Route before writing

- Reusable CFD/literature knowledge → `CFD_wiki/`.
- Current scientific questions, selected experiments, interpretation and claim limits → `Project/`.
- Executable automation, live Fluent discovery, run support and machine-readable evidence → `PyAnsys/`.
- Repeatable procedure → the smallest applicable skill.

Prefer links over duplicated pages. Historical Project records may retain old paths as explicit provenance, but active links should resolve.

## Change discipline

Before editing, identify the owning system and any uncertainty that affects the change.

While editing:

- make the smallest change that solves the actual problem;
- preserve citations, evidence labels, uncertainty, failed experiments and historical interpretations;
- do not rewrite adjacent material merely for polish;
- never edit `raw/` source material;
- keep generated/debug output out of normal Project context;
- do not create a new index, log, schema, compatibility layer, or framework unless repeated real use has earned it.

After editing, check changed links and the applicable local `AGENTS.md` contract.

## Historical recovery and cleanup

Use Git history when an exact retired file is needed. Restore or retain a historical artifact in the working tree only when it has clear ongoing value that Project, CFD_wiki, PyAnsys, or Git history cannot conveniently provide.

Do not perform cosmetic rewrites of immutable historical provenance.

## Delegation

Use subagents when parallel read-only discovery, audit, or independent review reduces context load or catches omissions. Keep the main agent responsible for scope, reconciliation, writes, cross-links, tests and final decisions.

A good subagent brief contains:

```text
GOAL
SCOPE
CONTEXT
CONSTRAINTS
EVIDENCE TO INSPECT
RETURN FORMAT
DONE WHEN
```

Prefer bounded read-only subagents for audits. After a meaningful cross-system migration or cleanup, use a fresh reviewer when useful. Do not maintain fixed subagent prompt files that duplicate repository instructions.

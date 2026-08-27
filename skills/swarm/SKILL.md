---
name: swarm
description: "Split a broad read-only investigation into parallel subagent tasks and synthesize the results without bloating the main context. Use for repository audits, literature/evidence review, experiment-history reconstruction, or any task with separable discovery work."
---

# Swarm

Use parallel subagents for breadth, not for duplicated bureaucracy.

## Suitable tasks

Use Swarm when a task can be decomposed into independent discovery questions, for example:

- audit separate experiment families;
- inspect setup, results, and observation sources in parallel;
- compare several branches/cases;
- review literature by topic;
- inspect numerical, physical, and implementation evidence separately.

Do not use Swarm when multiple agents would mutate the same files/state or when one sequential dependency dominates the task.

## Main-agent responsibilities

The main agent must:

- define the decomposition;
- give each subagent a narrow scope and output format;
- avoid overlapping write ownership;
- synthesize findings;
- resolve contradictions;
- make final decisions;
- perform final mutations/edits unless ownership is explicitly partitioned safely.

## Subagent brief

Each subagent should receive:

- the exact question;
- paths/sources to inspect;
- what not to do;
- required evidence/path citations;
- concise output schema.

Prefer outputs such as:

```text
Finding
Evidence/path
Confidence/uncertainty
Why it matters
```

Do not ask subagents to create permanent coordination documents unless the task genuinely requires one.

## Context protection

Have subagents return distilled findings rather than full file dumps. The main context should retain conclusions and evidence pointers, not every intermediate read.

## Synthesis

Group findings into:

- agreement;
- unique evidence;
- contradictions;
- gaps;
- required follow-up.

When two agents disagree, inspect the underlying evidence or launch a targeted tie-breaker subagent. Do not average contradictory claims.

## Write safety

Default Swarm work to read-only. If parallel writes are needed, partition paths so no two agents edit the same file and require the main agent to review the combined diff.

## Output

Return one synthesized result that is smaller and more useful than the combined subagent outputs, with clear evidence pointers and unresolved gaps.
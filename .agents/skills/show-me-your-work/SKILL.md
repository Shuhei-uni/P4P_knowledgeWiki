---
name: show-me-your-work
description: "Reconstruct a concise evidence trail for a long or autonomous research sequence: what decisions were made, why, what evidence supported them, what changed, and where the durable artifacts live. Use for handoff, review, or debugging unattended work without dumping full chat history."
---

# Show Me Your Work

Make an autonomous sequence auditable without reproducing every intermediate thought or tool call.

## Purpose

A fresh human or agent should be able to answer:

- What goal was being pursued?
- What experiments/actions were chosen?
- Why were they chosen?
- What evidence was produced?
- What failed or changed course?
- What conclusions are currently supported?
- What is the next action or human decision?
- Where are the durable files?

## Reconstruct from durable evidence

Prefer repository artifacts over chat memory:

- `setup.md`;
- `results.md`;
- plots/figures;
- relevant commits/diffs;
- run/checkpoint evidence;
- explicit issue/task decisions.

Do not invent missing rationale. Mark it unavailable or uncertain.

## Summarize decisions, not every action

Capture only consequential transitions, for example:

```text
goal
-> experiment selected because ...
-> implementation succeeded/failed because ...
-> evidence showed ...
-> interpretation limited by ...
-> next action chosen because ...
```

Skip routine file reads, successful deterministic extractions, and repeated low-level commands unless they explain a failure.

## Evidence links

For each important decision include the strongest evidence pointer:

- experiment path;
- results/figure path;
- commit/issue when relevant;
- machine artifact only when it materially verifies implementation/run state.

## Contradictions and course changes

Explicitly show when:

- an earlier interpretation was superseded;
- a numerical failure changed the experiment plan;
- a human overrode the autonomous choice;
- a reviewer/interrogation found a blocker;
- the goal was narrowed or expanded.

Do not rewrite history into a cleaner story than actually occurred.

## Output

Produce a compact handoff with:

1. **Goal**
2. **Current state**
3. **Key decisions and evidence**
4. **Important failures/course changes**
5. **Supported conclusions**
6. **Unresolved questions/risks**
7. **Next action / human gate**
8. **Durable artifact paths**

Do not create a permanent progress-log system by default. Write this into an existing handoff/task location only when useful or explicitly requested.
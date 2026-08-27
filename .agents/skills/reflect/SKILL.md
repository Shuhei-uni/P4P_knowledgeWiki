---
name: reflect
description: "Perform a short structured self-review after a meaningful workflow step to detect goal drift, unsupported assumptions, repeated failures, and unnecessary complexity. Use as a lightweight checkpoint, not a substitute for independent adversarial review."
---

# Reflect

Use a short self-check before carrying momentum into the next step.

## Trigger points

Useful after:

- designing an experiment;
- implementing a complicated case;
- finishing a major analysis;
- interpreting surprising evidence;
- repeated failed attempts;
- a long autonomous work sequence.

Do not reflect after every trivial action.

## Questions

Ask:

1. What goal am I actually trying to advance?
2. What did I just learn or establish?
3. What am I assuming without evidence?
4. Did the task drift from the original question?
5. Am I adding structure/process that does not improve the result?
6. Have I repeated the same failed strategy?
7. Is there a simpler next action?
8. Does the next step require an independent reviewer or human gate?

## Evidence check

Separate:

- observed evidence;
- inference;
- unresolved uncertainty.

If a conclusion cannot be traced to evidence, downgrade it or request the missing evidence.

## Complexity check

Prefer removing unnecessary files, abstractions, skills, and workflow stages over adding compensating structure.

Ask:

> Can the next agent understand and execute this with less context than before?

If not, simplify.

## Escalation

Use `interrogate` instead of reflection when independent adversarial review is warranted. Reflection is the agent checking itself; interrogation is other agents trying to break the work.

## Output

Return only:

- what changed in understanding;
- the biggest remaining risk/assumption;
- the simplest justified next step.

Do not create a permanent reflection log unless explicitly requested.
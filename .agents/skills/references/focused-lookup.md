# Focused lookup delegation

Use this protocol when research supports a parent agent's pending decision.
The lookup agent gathers evidence; the parent retains the decision.

## Dispatch

Run each applicable lookup path in its own subagent, in parallel when possible.
Give the subagent a compact brief:

```text
Decision: <the decision this evidence will inform>
Question: <one precise unknown to resolve>
Useful fact: <the evidence, contradiction, limit, or prior result that could
change or constrain the decision>
Scope: <relevant phase, model, Fluent version, source family, or time boundary>
Return: <answer, strongest evidence pointers, contradictions, missing
information, and decision impact>
```

Do not send the parent agent's whole working context when the brief and exact
starting pointers are sufficient. Do not ask the lookup agent to choose or
approve the scientific direction.

When this protocol is already running inside a lookup subagent, perform the
lookup directly and return the packet below; do not delegate recursively. If
subagents are unavailable, use the same brief and packet locally while opening
only the smallest relevant sources.

## Return packet

Return a compact, source-linked packet:

```text
Answer: <direct answer to the question>
Evidence: <strongest exact paths, sections, figures, or manual pages>
Contradictions: <material disagreement or none found>
Missing: <important unresolved information>
Decision impact: <what this supports, weakens, rules out, or leaves open>
```

The lookup is complete only when the question is answered or explicitly
unresolved, every material claim has an evidence pointer, and the decision
impact preserves the source's uncertainty and claim limits.

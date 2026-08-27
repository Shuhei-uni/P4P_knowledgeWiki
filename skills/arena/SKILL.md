---
name: arena
description: "Generate multiple independent candidate solutions or experiment designs, select the strongest base, and synthesize useful ideas from the rest. Use when there are several plausible approaches and diversity is more valuable than one agent refining its first idea."
---

# Arena

Use independent candidates to reduce first-idea bias.

## When to use

Good uses include:

- experiment design;
- analysis-plan alternatives;
- numerical recovery strategies;
- competing report structures;
- major modelling choices where several defensible approaches exist.

Do not use Arena for trivial deterministic tasks.

## Fan out

Spawn several independent subagents, usually 3–5.

Give each the same core problem, goal, constraints, and evidence. Do not tell later candidates what earlier candidates proposed.

Require each candidate to return:

- proposed approach;
- reasoning/evidence;
- main strengths;
- main risks/confounders;
- what would falsify or reject it;
- cost/complexity.

Keep responses concise enough for synthesis.

## Evaluate

The main agent compares candidates against explicit criteria tied to the task, such as:

- scientific information value;
- control of confounding variables;
- numerical feasibility;
- evidence requirements;
- implementation risk;
- compute cost;
- reversibility;
- alignment with project goal.

Do not choose by majority vote or writing quality alone.

## Synthesize

Choose the strongest candidate as the base. Graft only genuinely compatible ideas from the others.

Do not merge every idea into an overengineered hybrid.

The final result should usually be simpler than the union of all candidates.

## Record disagreement

Preserve meaningful disagreements that affect the decision. If two candidates depend on different unresolved assumptions, surface that uncertainty instead of hiding it through synthesis.

## Output

Return:

- chosen base;
- why it won;
- useful ideas adopted from alternatives;
- important rejected alternatives and why;
- unresolved disagreement/human gate if any.

Then hand the selected result back to the calling skill.
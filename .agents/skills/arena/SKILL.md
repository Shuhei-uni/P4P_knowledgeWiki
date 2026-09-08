---
name: arena
description: "Compare several human-approved CONTEXT.md scientific directions or experiment strategies without selecting an executable route. Use when approved approaches deserve independent comparison before a human decision."
---

# Arena

Use independent reasoning to compare candidates already approved in
`CONTEXT.md`. The human, not this skill, chooses an executable route.

## Keep the judging level clear

At the **phase level**, favour the direction with the strongest scientific reasoning: which line of inquiry best advances the phase question and attacks the most important uncertainty?

At the **experiment level**, favour information value: how much of the relevant hypothesis could this experiment or linked campaign resolve, how interpretable would that evidence be, and is the learning worth the compute?

Do not apply one generic rubric to every level of the investigation.

## Compare independently

Give several subagents the same approved candidate set, evidence, constraints,
and level of decision. Let them reason independently before seeing alternatives.

Ask them to assess the approved alternatives rather than generate new ones.

## Judge from evidence

Compare the candidates using the criteria that matter for the calling skill. Scientific reasoning, prior evidence, information value, interpretability, feasibility, and cost may all matter, but their importance depends on whether the Arena is choosing a phase direction or an experiment strategy.

Do not choose by majority vote, confidence of writing, or novelty.

## Preserve the decision boundary

The output may identify strengths, conflicts, and evidence needs across the
approved candidates. It must not merge them into an unapproved experiment or
select an executable strategy.

Preserve meaningful disagreements when the evidence does not resolve them.

## Output

Return the comparison, evidence-supported tradeoffs, any useful constraints,
and unresolved disagreement that still matters.

Then hand the result to `phase-grill` / the human for any selection or context
change.

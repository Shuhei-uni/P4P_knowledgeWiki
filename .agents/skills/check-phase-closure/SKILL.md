---
name: check-phase-closure
description: "Decide whether an autonomous scientific phase should continue, conclude, or return to the human. Use after a meaningful experiment or analysis cycle to judge whether the phase now has sufficient evidence for its intended decision or scientific statement, whether important uncertainty still justifies more work, and whether the loop is stagnating."
---

# Check Phase Closure

Decide whether another scientific cycle is justified.

The goal is not complete understanding. The goal is sufficient evidence for the decision or scientific statement this phase was created to make.

## Judge the phase, not just the last experiment

Use the accumulated phase evidence, not only the newest result.

Ask:

- Can the phase question now be answered with a bounded, evidence-backed statement?
- Is the evidence strong enough for that statement, given implementation quality, run depth, comparisons, and numerical credibility?
- Is there an unresolved hypothesis or materially challenged assumption that could still change the phase-level conclusion?
- Is there a feasible next investigation with enough information value to justify its compute and effort?

Remaining uncertainty is normal. Continue only when resolving it could materially change the phase answer.

## Treat assumptions proportionately

Working assumptions should stay visible, but they are not automatically new experiments.

Use three practical states:

- `accepted-for-now`: no current evidence makes the assumption important enough to test;
- `questioned`: some evidence or reasoning makes it relevant, but it does not yet threaten the phase conclusion;
- `materially-challenged`: there is a credible reason it could change the phase conclusion.

Do not demand proof of every assumption. Ask whether the remaining assumptions materially bound or threaten the statement the phase needs to make.

## Return one of three outcomes

### CONTINUE

Choose `CONTINUE` when an important unresolved hypothesis or materially challenged assumption remains and there is a useful, feasible investigation that could materially strengthen or change the phase answer.

State the uncertainty that justifies another cycle. Do not design the experiment here; hand the uncertainty back to `scientific-phase-loop`.

### CONCLUDE PHASE

Choose `CONCLUDE PHASE` when there is sufficient evidence for the decision or scientific statement the phase was created to make and further feasible work is unlikely to change that statement enough to matter.

A bounded, conditional, or negative conclusion is valid. Do not require the model to be fully understood.

State the supported phase-level conclusion, the important limits on it, and any assumptions that remain accepted-for-now or questioned but do not materially threaten it.

### RETURN TO HUMAN / PHASE-PLANNER

Choose `RETURN TO HUMAN / PHASE-PLANNER` when useful progress depends on a phase-level judgement outside the current autonomous boundaries: a major modelling assumption, scope change, project-direction choice, resource decision, unresolved ambiguity, or explicit human gate.

State the decision boundary and the evidence that brought the phase there.

## Anti-loop safeguard

Track whether meaningful cycles are actually changing the scientific picture.

If two consecutive experiment or analysis cycles fail to materially change the current understanding, reduce an important uncertainty, strengthen the phase-level statement, or materially update an assumption, treat that as stagnation.

Do not respond by generating a third minor variation of the same idea.

Instead, either:

- rethink the investigation substantially, including whether a different experiment-design mode, analysis, model assumption, or branch is needed; or
- return `RETURN TO HUMAN / PHASE-PLANNER` when the necessary rethink crosses a genuine phase-level boundary.

Stagnation is evidence about the usefulness of the current route.

## Output

Return only:

1. **Outcome:** `CONTINUE`, `CONCLUDE PHASE`, or `RETURN TO HUMAN / PHASE-PLANNER`;
2. **Phase-level statement currently supported**;
3. **Important unresolved hypothesis or materially challenged assumption**, if any;
4. **Why another cycle is or is not worth doing**;
5. **Stagnation status**, including whether the two-cycle safeguard has been triggered;
6. **Important limits or human decision boundary**.

Do not create the next experiment. This skill decides whether the loop has earned another cycle.
---
name: question-experiment
description: "Challenge and justify candidate simulation experiments before compute is spent. Use after experiment ideas exist but before one is selected, to check them against past simulation evidence, relevant literature, expected information gain, scientific impact, confounding, and cost."
---

# Question Experiment

Do not let the first plausible experiment become the next experiment by momentum alone.

Your job is to challenge candidate experiments before compute is spent and decide which ones genuinely earn a run.

## Start from the phase uncertainty

Keep the current phase question and uncertainty in view. A candidate is useful only if its outcome could materially improve the phase understanding.

Ask what the experiment is supposed to teach, not merely what parameter it changes.

## Look for evidence before paying for new evidence

Before recommending a run, look at the evidence already available.

Use relevant past simulation setups, results, observations, plots, and comparisons to determine whether the proposed question has already been answered, partially answered, contradicted, or left genuinely unresolved.

Use literature, Fluent guidance, and general CFD knowledge to sharpen the hypothesis and identify known mechanisms, likely sensitivities, or better ways to test the question.

Treat these sources carefully. Unless prior evidence is genuinely equivalent to the proposed case, they inform the hypothesis; they do not establish the result of the new simulation.

If an existing result can answer the question through additional analysis, prefer that over another expensive run.

## Challenge the candidate

For each serious candidate, ask:

- What important uncertainty would this resolve?
- Why is this question still unresolved by previous simulations?
- What does existing evidence make more or less plausible?
- What would we learn if the hypothesis is wrong?
- Could different outcomes distinguish competing explanations?
- Is the proposed change confounded by other changes?
- Could a cheaper diagnostic, analysis, or simpler simulation answer the same question?
- Is the likely scientific impact large enough to justify the compute cost?
- Would the result change what we do next, or merely add another data point?

Reject, merge, or reshape weak candidates rather than preserving them for politeness.

## Compare information value

Prefer experiments that have high expected information value, not experiments that merely have a high chance of producing a desirable result.

A strong experiment can be valuable in several directions: success teaches something, failure teaches something, and unexpected behavior exposes a new branch worth understanding.

Be skeptical of broad sweeps when one well-chosen case can discriminate between explanations. Be equally skeptical of a single narrow case when the response shape itself is the uncertainty.

## Use independent challenge when stakes are high

For expensive, consequential, or ambiguous choices, use independent subagents, `arena`, or `interrogate` to challenge the candidates from different perspectives.

Useful viewpoints include:

- prior-simulation evidence;
- CFD/numerical credibility;
- physical plausibility and literature;
- experimental design and confounding;
- information value versus compute cost.

Agreement across independent evidence-based critiques is useful signal. The main agent still owns the synthesis.

## Output

Return a short judgement on the candidate set:

- which experiments are strongly justified;
- which should be modified, merged, deferred, or rejected;
- what existing evidence supports that judgement;
- what uncertainty each surviving experiment would resolve;
- which experiment is the best use of compute now, and why.

Do not claim what the selected simulation will do. State the expectation as a hypothesis and let the simulation data decide.

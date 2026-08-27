---
name: question-experiment
description: "Challenge and justify candidate simulation experiments or linked experiment campaigns before compute is spent. Use after candidate strategies exist but before one is selected, to judge scientific value, evidence and interpretability, and cost-effectiveness against past simulation evidence, literature, and the current phase uncertainty."
---

# Question Experiment

Challenge candidate experiment strategies before compute is spent and decide which ones genuinely earn a run.

A strategy may be one decisive setup or a small series of linked setups whose value comes from the comparison, trend, sequence, or combined evidence. Judge the strategy at the level where its scientific value actually exists.

## Start from the phase uncertainty

Keep the current phase question and uncertainty in view. A candidate is useful only if its outcomes could materially improve the phase understanding.

Ask what the strategy is supposed to teach, not merely what parameters it changes.

## Look for evidence before paying for new evidence

Before recommending a run, inspect the evidence already available.

Use relevant past simulation setups, results, observations, plots, and comparisons to determine whether the proposed question has already been answered, partially answered, contradicted, or left genuinely unresolved.

Use literature, Fluent guidance, and general CFD knowledge to sharpen the hypothesis, identify known mechanisms, and reveal better ways to test the question.

Unless prior evidence is genuinely equivalent to the proposed case, these sources inform the hypothesis; they do not establish the result of the new simulation.

If existing simulation data can answer the question through additional analysis, prefer that over another expensive run.

## Judge with three criteria

Score each serious strategy from 0 to 4 on the three criteria below. The score guides judgement; it does not automatically select a winner.

### 1. Scientific value

Will this setup or linked series materially reduce an important uncertainty in the phase?

Strong strategies distinguish explanations, establish a useful trend, eliminate a branch, expose important behavior, or materially change what should happen next.

Do not reject a supporting setup merely because its standalone value is low when it is necessary for a high-value comparison or sequence.

### 2. Evidence and interpretability

Will the planned setup or series produce evidence that can actually be interpreted?

Strong strategies have a meaningful comparison basis, control or acknowledge important confounders, capture the required simulation behavior, and have a clear logic linking multiple setups when several are needed.

A strategy that produces lots of data but cannot answer its question is weak.

### 3. Cost-effectiveness

Is the expected learning worth the compute and implementation cost?

Strong strategies use the smallest useful number of simulations, reuse existing evidence where possible, avoid redundant cases, and justify why each setup contributes to the combined learning.

A larger campaign can be justified when the series reveals something that no single run can.

## Challenge the strategy as a whole

Ask:

- What important uncertainty does this strategy reduce?
- Why is it still unresolved by previous simulations or existing analysis?
- What different outcomes would teach us?
- Does the strategy distinguish competing explanations or reveal a response shape that matters?
- Are the comparisons interpretable enough to support the intended claim?
- Does every setup contribute useful information individually or through the campaign logic?
- Could fewer runs, existing data, or a cheaper diagnostic answer the same question?

Reject, merge, split, reshape, or defer weak strategies when the evidence supports doing so.

## Use independent challenge when stakes are high

For expensive, consequential, or ambiguous choices, use independent subagents, `arena`, or `interrogate` to challenge the strategy from different perspectives.

Useful viewpoints include prior-simulation evidence, CFD/numerical credibility, physical plausibility and literature, experimental design, and information value versus compute cost.

Agreement across independent evidence-based critiques is useful signal. The main agent still owns the synthesis.

## Output

Return a concise judgement on the candidate strategies:

- the three-criterion assessment;
- what existing evidence supports the judgement;
- what uncertainty each surviving strategy would reduce;
- which strategies should be modified, merged, deferred, or rejected;
- which strategy is the best justified use of compute now, and why.

Do not claim what the selected simulation or campaign will do. State expectations as hypotheses and let the simulation data decide.

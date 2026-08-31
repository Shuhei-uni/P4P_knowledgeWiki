---
name: question-experiment
description: "Challenge and justify candidate simulation experiments or linked campaigns before compute is spent. In hypothesis-test mode, independent adversarial review is mandatory before the strategy can proceed to the hard transition gate."
---

# Question Experiment

Challenge candidate experiment strategies before compute is spent and decide which ones genuinely earn further consideration.

A strategy may be one decisive setup or a small series whose value comes from the comparison, trend, sequence, or combined evidence. Judge the strategy at the level where its scientific value actually exists.

This skill recommends. It does **not** grant lifecycle permission; `verify-phase-transition` does that.

## Start from the phase uncertainty

Keep the fixed phase question, current lifecycle state, and verified discovery evidence in view.

Ask what the strategy is supposed to teach, not merely what parameters it changes.

For hypothesis-test review, require the verified hypothesis contract and intended strong statement form. If `DISCOVERY_EVIDENCE` or `HYPOTHESIS_DEFINITION` has not passed, do not approve a qualification strategy.

## Look for evidence before paying for new evidence

Inspect relevant past setups, results, observations, figures, failed/blocked runs, and comparisons.

Use literature, Fluent guidance, and general CFD knowledge to sharpen the hypothesis, identify mechanisms, and expose known confounders. These sources may justify a test; they do not substitute for project simulation evidence unless genuinely equivalent evidence already exists.

If existing data can answer the question through additional analysis, prefer that over another expensive run.

## Challenge assumptions without inventing missing facts

Review the experiment's working assumptions and distinguish them from missing human-owned facts.

Use:

- `accepted-for-now`;
- `questioned`;
- `materially-challenged`.

A normal working assumption can be bounded. A materially challenged assumption should be repaired, explicitly tested, or reflected in the claim limit.

A missing plant setpoint, measurement location, validation target, controller law, or other human-owned fact must not be converted into an assumed surrogate unless the phase contract explicitly authorizes that surrogate class. If the strategy depends on such a fact, recommend `HUMAN_REQUIRED`.

## Judge with three criteria

Score each serious strategy from 0 to 4 on:

### 1. Scientific value

Will it materially reduce an important uncertainty in the phase?

Strong strategies distinguish explanations, establish useful bounds/trends, eliminate a branch, expose important behaviour, or materially change what should happen next.

### 2. Evidence and interpretability

Will the strategy produce evidence that can actually support the intended judgement?

Strong strategies have a meaningful reference, visible assumptions, controlled confounders, preplanned histories/fields/figures, and a clear logic linking any multiple setups.

For hypothesis qualification, explicitly ask:

- Could the declared evidence support the intended strong statement?
- Is the required numerical credibility evidence instrumented before the run?
- Are support and rejection outcomes both interpretable?
- Is a competing explanation still distinguishable?
- Does any required history disappear after reconnect/restart under the proposed workflow?

A strategy that produces lots of data but cannot make the intended claim is weak.

### 3. Cost-effectiveness

Is the expected learning worth the compute and implementation cost?

Use the smallest useful strategy, but do not shorten a qualification run until it becomes discovery-scale.

For ordinary steady iteration-based full-geometry hypothesis qualification, challenge any horizon below 10,000 iterations unless there is an explicit human-approved exception or a scientifically equivalent non-iteration basis.

For slow inventory/stationarity behaviour, ask whether the proposed horizon and continuation/restart plan are deep enough to distinguish persistent drift from a durable state.

## Mandatory independent review for hypothesis qualification

For every hypothesis-test strategy, use a fresh independent reviewer/subagent before recommending it.

Use `interrogate` as the adversarial-review pattern when helpful. Give the reviewer the phase question, discovery evidence, hypothesis contract, setup strategy, intended strong statement, evidence/figure plan, proposed horizon, and important assumptions. Do not prime the reviewer with the main agent's preferred answer.

Useful review lenses include:

- prior-simulation collision and novelty;
- CFD/numerical credibility;
- physical plausibility/literature;
- experiment design/confounding;
- evidence completeness;
- information value versus compute;
- whether a human boundary is being bypassed.

Classify surviving issues as `blocker`, `important`, `minor`, or `non-issue`.

A surviving blocker means the strategy is **not ready** for `HYPOTHESIS_RUN_READY` verification.

Independent review is optional for simple low-cost discovery candidates unless the design is consequential/ambiguous, but the hard `DISCOVERY_DESIGN` gate still applies upstream.

## Challenge the strategy as a whole

Ask:

- What important uncertainty does this strategy reduce?
- Why is it unresolved by existing evidence?
- What would we learn if the hypothesis is supported?
- What would we learn if it is weakened/rejected?
- Does the strategy distinguish a competing explanation?
- Could the required claim be supported from the planned evidence?
- Are any setup assumptions materially threatened?
- Is an unresolved human lock present?
- Could fewer runs or existing data answer the same question?
- Is the horizon appropriately discovery-scale or qualification-scale for its label?

Reject, merge, split, reshape, or defer weak strategies.

## Output

Return:

- mode: `discovery` or `hypothesis-test`;
- three-criterion assessment;
- independent-review result when mandatory;
- strongest surviving criticisms and their severity;
- existing evidence supporting the judgement;
- assumptions/missing facts that matter;
- whether the strategy should be modified, deferred, rejected, or sent to the relevant `verify-phase-transition` gate;
- the best justified strategy, if any, and why.

Do not claim what the simulation will do. State expectations as hypotheses and let the data decide.

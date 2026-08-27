---
name: design-experiment
description: "Turn an important scientific uncertainty into a small number of high-information simulation experiments. Use when new simulation evidence is needed and the agent must choose what is worth the compute cost, what behavior would be informative, and what data must be captured before the run."
---

# Design Experiment

Design simulations to learn something important, not to generate more cases.

A simulation is expensive evidence. It should earn its compute cost by reducing an important uncertainty, distinguishing between plausible explanations, or revealing behavior that materially changes the direction of the phase.

## Start from the uncertainty

Begin with the question the phase still cannot answer.

Understand what is known, what is only suspected, what competing explanations are plausible, and what observation would actually change the current understanding.

Do not begin from an available parameter list and ask what can be swept. Begin from the uncertainty and ask what experiment could resolve it.

Reasoning, literature, previous experience, and prior simulations can shape the hypothesis. Unless there is genuinely equivalent prior evidence, they do not establish what this new simulation will do.

## Make the simulation earn its cost

Prefer a small number of high-information simulations over broad brute-force sweeps.

For each candidate, ask:

- What uncertainty does this run reduce?
- What would we learn if it behaves as expected?
- What would we learn if it behaves differently?
- What useful behavior might appear between those extremes?
- Can this run distinguish between competing explanations?
- Is there a cheaper or clearer way to obtain the same information?

A failed hypothesis can still make an experiment valuable if the result meaningfully narrows the landscape.

Avoid running many nearby cases merely to search blindly for a good result. Use coarse exploration only when the shape of the response itself is the question.

## Design for interpretation

The experiment should make its own result as interpretable as possible.

Identify the reference or parent state, the intentional change, and the important conditions that should remain comparable. Change one important thing at a time when causal isolation matters. Change several things together only when the combination itself is the object of study or when the experiment is deliberately testing an interaction.

Think about possible confounders before paying for the run. Initialization, run length, mesh, timestep, numerical scheme, boundary conditions, monitor definitions, and comparison windows can all change the meaning of the result.

Do not demand artificial purity when the science requires a larger formulation change. Instead make the comparison and its limitations explicit.

## Plan the evidence before the run

A simulation only answers the question if the relevant behavior is observable.

Before implementation, decide what evidence would make the outcome interpretable. This may include residual histories, mass and phase balances, monitor stability, inventories, fluxes, local fields, contours, time histories, comparisons, or derived quantities.

Call `plan-analysis` when the analysis requirements are non-trivial. If decisive evidence must be recorded during the run, make that part of the experiment before the case is launched.

Do not discover after a long simulation that the only quantity capable of answering the question was never monitored.

## Explore alternatives when the choice matters

When several genuinely different experiments could attack the same uncertainty, use independent subagents, `arena`, or `interrogate` to widen and challenge the design space.

Ask for different ways of learning the same thing, not cosmetic variations of one setup.

The main agent synthesises the alternatives and chooses based on expected information, interpretability, feasibility, and compute cost. Do not select by majority vote or sophistication.

## Output

Return only the experiments that genuinely earn consideration.

For each one, make clear:

- the question it is testing;
- the hypothesis or competing explanations;
- the intended change and comparison basis;
- the behavior or evidence that would be informative;
- what different outcomes would teach us;
- the important numerical or implementation requirements;
- the rough cost and why the run is worth it now.

When human selection is expected, provide a small set of meaningfully different options and recommend the one with the strongest expected information value.

Once an experiment is selected, turn it into `setup.md`. The setup should define the experiment, not predict its result.

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

## Generate meaningful alternatives

When more than one useful route is visible, create a small set of genuinely different experiments that attack the uncertainty in different ways.

Do not produce cosmetic variations just to create options. Alternatives should represent different ways of learning something important.

Use independent subagents or `arena` when widening the design space would improve the choice.

## Make each simulation earn its cost

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

## Question the experiments before selecting one

Do not select the first plausible candidate by momentum.

Once serious candidates exist, call `question-experiment` to challenge them against:

- past simulation results and observations;
- relevant literature or Fluent guidance;
- whether the uncertainty has already been partly answered;
- confounding and numerical risk;
- expected information gain;
- likely scientific impact;
- compute and implementation cost.

The critic may reject, merge, reshape, or reprioritize candidates. If existing evidence can answer the question without another simulation, do that instead.

The selected experiment should be the best justified use of compute now, not necessarily the safest, easiest, or most likely to confirm the current hypothesis.

## Create the setup only after selection

Once an experiment survives questioning and is selected, call `create-setup`.

`design-experiment` owns what is worth testing. `create-setup` owns turning that choice into a precise `setup.md` contract for implementation.

Do not mix setup formatting, repository routing, or detailed Fluent implementation mechanics into the experiment-design reasoning.

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

After `question-experiment`, identify the strongest justified experiment and why it earned selection.

After selection, hand it to `create-setup`. The setup should define the experiment, not predict its result.

---
name: design-experiment
description: "Turn an important scientific uncertainty into one or more high-information simulation experiment strategies. Use when new simulation evidence is needed and the agent must decide what linked setup or campaign is worth the compute cost, what behavior would be informative, and what data must be captured before the runs."
---

# Design Experiment

Design simulations to learn something important, not to generate more cases.

A useful design may be one decisive setup or a small campaign of linked setups whose combined evidence answers a question that no single run can. The unit of design is the scientific strategy, not automatically one simulation.

## Start from the uncertainty

Begin with the question the phase still cannot answer.

Understand what is known, what is only suspected, what competing explanations are plausible, and what observation would actually change the current understanding.

Do not begin from an available parameter list and ask what can be swept. Begin from the uncertainty and ask what evidence could resolve it.

Reasoning, literature, previous experience, and prior simulations can shape the hypothesis. Unless there is genuinely equivalent prior evidence, they do not establish what a new simulation will do.

## Design the smallest useful strategy

Prefer the smallest simulation strategy that can produce the needed learning.

Sometimes that is one discriminating run. Sometimes it is a pair of controlled comparisons, a short sensitivity series, or a staged campaign where later setups become meaningful only in relation to earlier ones.

A supporting setup does not need high standalone impact if it creates the reference, comparison, or sequence that makes the campaign informative.

## Design the evidence at the same time

Analysis planning is part of experiment design, not an afterthought.

For each hypothesis or comparison, decide what result would let you judge it and what evidence must therefore exist when the run finishes. Work backward from the judgement you want to make.

Prefer evidence that shows behaviour over the run rather than only a final snapshot. Iteration/time histories, residuals, balances, physical monitors, fluxes, inventories, and other question-specific values often tell much more than one endpoint.

Plan useful plots, contours, and other visualisations before the simulation. Visual evidence should help reveal the behaviour relevant to the hypothesis, while concise tables can support exact comparisons.

If a quantity must be instrumented before solving, make that requirement part of the experiment now. Do not discover after an expensive run that the decisive history or monitor was never recorded.

For linked setups, make the evidence comparable enough that the intended campaign-level comparison is actually possible.

## Design for interpretation

Identify the reference or parent state, the intentional changes, and the important conditions that should remain comparable across the setup or setup series.

Think about confounders before paying for the runs. Initialization, run length, mesh, timestep, numerical scheme, boundary conditions, monitor definitions, and comparison windows can all change the meaning of the result.

Do not demand artificial purity when the science requires a larger formulation change. Make the comparison and its limitations explicit instead.

## Generate and question candidate strategies

When several plausible ways exist to attack the uncertainty, generate a small set of genuinely different experiment strategies. A strategy may contain one setup or several linked setups.

Use independent subagents, `arena`, or literature-focused `swarm` work when they help expose better alternatives.

Then call `question-experiment` before selection. Judge each strategy against past simulation evidence, relevant literature or CFD guidance, and the three key criteria:

1. scientific value;
2. evidence and interpretability;
3. cost-effectiveness.

The purpose is to make every candidate earn its place through the same evidence-based judgement. `question-experiment` may recommend keeping, reshaping, merging, splitting, deferring, or rejecting strategies.

## Select and formalize

Choose the best justified strategy for the current uncertainty. The selected strategy may be a single setup or a small linked campaign.

Then call `create-setup` to convert that strategy into one or more setup records. `design-experiment` owns why the experiment strategy is worth doing and what evidence will judge it. `create-setup` owns the precise handoff for implementation.

Do not write predicted results into the setup records. The strategy defines what will be tested and what would be informative; the simulation data decides what actually happened.
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

For each strategy, ask:

- What uncertainty does this strategy reduce?
- Why might one setup be enough, or why are several needed?
- What would we learn if the behavior matches the hypothesis?
- What would we learn if it does not?
- What useful intermediate or unexpected behavior could appear?
- Can the strategy distinguish competing explanations or reveal a trend that matters?
- Could fewer runs or existing data provide the same information?

Do not force every setup to have high standalone impact. A supporting setup can be valuable because it creates the reference, comparison, or sequence that makes the campaign informative.

## Design for interpretation

The strategy should make its own result as interpretable as possible.

Identify the reference or parent state, the intentional changes, and the important conditions that should remain comparable across the setup or setup series.

Think about confounders before paying for the runs. Initialization, run length, mesh, timestep, numerical scheme, boundary conditions, monitor definitions, and comparison windows can all change the meaning of the result.

Do not demand artificial purity when the science requires a larger formulation change. Make the comparison and its limitations explicit instead.

## Plan the evidence before the run

A simulation only answers the question if the relevant behavior is observable.

Before implementation, decide what evidence would make the strategy interpretable. This may include residual histories, mass and phase balances, monitor stability, inventories, fluxes, local fields, contours, time histories, comparisons, or derived quantities.

Call `plan-analysis` when the analysis requirements are non-trivial. If decisive evidence must be recorded during the run, make that part of the experiment design before any case is launched.

For linked setups, make sure the planned evidence is comparable enough to support the intended cross-case interpretation.

## Generate and question candidate strategies

When several plausible ways exist to attack the uncertainty, generate a small set of genuinely different experiment strategies. A strategy may contain one setup or several linked setups.

Use independent subagents, `arena`, or other broadening methods when they help expose alternatives.

Then call `question-experiment` before selection. Judge each strategy against past simulation evidence, relevant literature or CFD guidance, and the three key criteria:

1. scientific value;
2. evidence and interpretability;
3. cost-effectiveness.

The purpose is not to distrust any idea because of when it was generated. It is to make every candidate earn its place through the same evidence-based judgement.

`question-experiment` may recommend keeping, reshaping, merging, splitting, deferring, or rejecting strategies.

## Select and formalize

Choose the best justified strategy for the current uncertainty. The selected strategy may be a single setup or a small linked campaign.

Then call `create-setup` to convert that strategy into one or more setup records. `create-setup` owns the precise setup handoff; `design-experiment` owns why the experiment strategy is worth doing.

Do not write predicted results into the setup records. The strategy defines what will be tested and what would be informative; the simulation data decides what actually happened.

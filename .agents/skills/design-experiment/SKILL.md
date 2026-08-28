---
name: design-experiment
description: "Turn an important scientific uncertainty into a high-information simulation strategy in either discovery mode or hypothesis-test mode. Use when new simulation evidence is needed and the agent must decide what setup or campaign is worth the compute cost, what behavior would be informative, what working assumptions matter, and what data must be captured before the runs."
---

# Design Experiment

Design simulations to learn something important, not to generate more cases.

A useful design may be one decisive setup or a campaign of linked setups whose combined evidence answers a question that no single run can. The unit of design is the scientific strategy, not automatically one simulation.

## Start from the uncertainty

Begin with the question the phase still cannot answer.

Understand what is known, what is only suspected, what competing explanations are plausible, and what observation would actually change the current understanding.

Do not begin from an available parameter list and ask what can be swept. Begin from the uncertainty and ask what evidence could resolve it.

Reasoning, literature, previous experience, and prior simulations can shape the hypothesis. Unless there is genuinely equivalent prior evidence, they do not establish what a new simulation will do.

## Respect the experiment-design mode

The scientific phase loop has two useful experiment-design modes. Choose based on the kind of uncertainty, not by habit.

### Discovery mode: find where to look

Use discovery mode when literature, previous simulations, and reasoning still leave several plausible directions and the important mechanism or experiment direction is unclear.

Call `explore-experiment-space` to build a quick discovery campaign of at most twelve cases. Twelve is a hard ceiling, not a target; use fewer whenever they span the useful uncertainty adequately. A rough budget of 500 to 1,000 iterations per case is a useful default when that is enough to reveal early comparative behaviour. Treat that range as a planning ballpark, not a universal convergence criterion.

Discovery mode optimises breadth and information across the matrix. Its results are screening evidence: useful for finding promising directions, eliminating weak ones, exposing unexpected behaviour, and sharpening hypotheses. Do not normally turn a short discovery run into a strong claim about settled model behaviour.

### Hypothesis-test mode: earn a stronger answer

Use hypothesis-test mode when there is a specific, important question whose answer could support a meaningful scientific statement about the model.

Prefer one focused experiment or a very small linked campaign, with enough run length and evidence to make the intended judgement credible. A run around 10,000 iterations may be an appropriate ballpark for the current project when that duration is deliberately chosen to expose the required behaviour, but the justified run length comes from the experiment and model rather than from a universal number.

Before spending that compute, make clear what hypothesis is being tested, what observations would support or weaken it, and what histories, plots, contours, balances, or other evidence are required to make the resulting statement.

A promising discovery case may become the basis of a focused hypothesis test, including an explicitly planned continuation when scientifically legitimate. Do not silently upgrade discovery evidence into hypothesis-test evidence simply because the early result looks convincing.

## Use the live fleet as a constraint and opportunity

When this design will require new Fluent compute, use the current resource envelope from `fluent-fleet-orchestration`. If no current fleet snapshot exists, obtain one before finalizing the runnable strategy.

Know which servers are actually available now and which exact parent/recovery artifacts are already local, available through OneDrive, transferable from another active server, or stranded on an unavailable machine.

Let this affect **campaign shape and execution efficiency**, not the scientific question itself:

- if several independent, worthwhile branches already exist and several servers are active, prefer a portfolio that can run them concurrently;
- for discovery work, consider wave-based matrices that use the active fleet and re-evaluate later cases after early evidence arrives;
- favor strategies whose exact parents can be staged safely without unnecessary duplication or reconstruction;
- account for transfer/recovery cost when two strategies are scientifically comparable.

Do not create weak extra cases merely because a server is idle. Unused capacity can, however, justify a deliberately bold speculative probe when the mainline campaign cannot use that server and the probe has meaningful asymmetric information value. Prefer a genuinely different question, mechanism, formulation, or challenged assumption over another minor variation whose outcome is unlikely to change the investigation.

Keep scientific setup identity server-neutral. Server assignment and local paths are resolved after setup creation by `fluent-fleet-orchestration`.

## Record working assumptions without becoming fixated on them

Alongside the hypothesis, list the assumptions that are being accepted so the experiment can be interpreted. These may concern the model formulation, mesh adequacy, initialization, boundary treatment, monitor meaning, numerical scheme, comparison basis, or other conditions that are not the direct target of the experiment.

Keep hypotheses and assumptions distinct:

- a **hypothesis** is something the experiment is actively trying to test;
- a **working assumption** is something being treated as acceptable for now so the test can proceed.

Do not turn every assumption into another experiment. Record only assumptions that materially shape the interpretation or could plausibly limit the conclusion.

Use three practical states when useful:

- `accepted-for-now`;
- `questioned`;
- `materially-challenged`.

Assumptions should be revisited when evidence makes them relevant, not continuously attacked by default. A materially challenged assumption may become a future experiment target if it could change the phase-level conclusion.

## Design the smallest useful strategy

Prefer the smallest simulation strategy that can produce the needed learning within the selected mode.

In hypothesis-test mode, that may be one discriminating run, a pair of controlled comparisons, a short sensitivity series, or a staged campaign where later setups become meaningful only in relation to earlier ones.

In discovery mode, the smallest useful strategy may deliberately be a bounded multi-case matrix because breadth is the information source. Keep it to the fewest cases that meaningfully span the plausible directions, never more than twelve quick screening cases.

A supporting setup does not need high standalone impact if it creates the reference, comparison, or sequence that makes the campaign informative.

## Design the evidence at the same time

Analysis planning is part of experiment design, not an afterthought.

For each hypothesis or comparison, decide what result would let you judge it and what evidence must therefore exist when the run finishes. Work backward from the judgement you want to make.

Prefer evidence that shows behaviour over the run rather than only a final snapshot. Iteration/time histories, residuals, balances, physical monitors, fluxes, inventories, and other question-specific values often tell much more than one endpoint.

Plan useful plots, contours, and other visualisations before the simulation. Visual evidence should help reveal the behaviour relevant to the hypothesis, while concise tables can support exact comparisons.

If a quantity must be instrumented before solving, make that requirement part of the experiment now. Do not discover after an expensive run that the decisive history or monitor was never recorded.

For linked setups or discovery matrices, make the evidence comparable enough that the intended comparison is actually possible.

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

Apply those criteria in the context of the chosen mode. Discovery strategies can earn their place through combined screening value across a matrix; hypothesis-test strategies should earn the greater compute through the strength of the answer they could support.

The purpose is to make every candidate earn its place through the same evidence-based judgement. `question-experiment` may recommend keeping, reshaping, merging, splitting, deferring, or rejecting strategies.

## Select and formalize

Choose the best justified strategy for the current uncertainty and mode. The selected strategy may be a focused setup, a small linked campaign, or a bounded discovery matrix.

Then call `create-setup` to convert that strategy into the required server-neutral setup records. `design-experiment` owns why the experiment strategy is worth doing, what working assumptions bound it, and what evidence will judge it. `create-setup` owns the precise scientific handoff; `fluent-fleet-orchestration` later resolves exact placement, staging, and durable artifact handling.

Do not write predicted results into the setup records. The strategy defines what will be tested and what would be informative; the simulation data decides what actually happened.
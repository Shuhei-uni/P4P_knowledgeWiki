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

## Check for prior experiment collisions before generating candidates

Before proposing new experiments, inspect the retained Project history across all phases, not only the current phase. Start from `Project/index.md`, `Project/experiments/README.md`, relevant phase indexes, `Project/observations/`, and the setup/results records of the closest historical experiments.

Search by scientific substance rather than experiment names alone: physical mechanism, modelling choice, formulation, boundary condition, numerical change, initialization, operating regime, intended question, and comparison logic.

For every serious candidate, identify the closest prior experiment or experiments and record:

- what was already tested;
- what happened, including failed, non-converged, partial, rejected, or inconclusive outcomes;
- the exact scientific delta of the proposed experiment;
- why existing evidence or additional analysis of existing data does not already answer the question;
- a novelty judgement: `NEW`, `PARTIAL REPEAT`, `REPLICATION`, or `REDUNDANT`.

A new setup ID, parent, phase, or slightly different parameter value does not make an experiment scientifically new. Reject `REDUNDANT` candidates before they consume design effort or compute. Keep a `REPLICATION` only when repeating prior work is itself the scientific purpose. A failed or inconclusive historical run still counts as prior work; rerun it only when a specific correction, stronger evidence requirement, or unresolved question makes the new attempt materially different.

This collision check applies equally to mainline experiments, discovery cases, and speculative probes.

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

When the live fleet has two or more servers usable for new compute, the runnable portfolio must include at least one bold speculative probe suitable for the loop's dedicated bold-probe lane. Do not let ordinary mainline work consume every usable server merely because it can. The bold candidate must still pass the prior-experiment collision check and have a clear learning target; generate a genuinely different question, mechanism, formulation, regime, or challenged assumption rather than a cosmetic variation.

Do not create weak extra cases merely because a server is idle. If no non-redundant, interpretable bold probe can be justified within the current modelling and execution boundaries, say why rather than disguising filler as exploration; the scientific loop then decides whether analysis, literature work, or a human boundary is needed to create a valid next probe.

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

## Design the evidence and figure plan at the same time

Analysis planning is part of experiment design, not an afterthought.

For each hypothesis or comparison, decide what result would let you judge it and what evidence must therefore exist when the run finishes. Work backward from the judgement you want to make.

Prefer evidence that shows behaviour over the run rather than only a final snapshot. Iteration/time histories, residuals, balances, physical monitors, fluxes, inventories, and other question-specific values often tell much more than one endpoint.

### Require a small core figure set

Do not merely request an "overview plot" or plot every available monitor. Define a **small core figure set** before the run whose purpose is to answer the scientific question as directly as possible.

As a default:

- discovery mode: usually `1-3` core figures reused consistently across the screening cases;
- hypothesis-test mode: usually `2-5` core figures, each supporting a distinct reasoning step;
- additional overview/debug plots may exist as supporting artifacts, but they do **not** count as core scientific figures unless they directly answer the question.

The first core figure should normally be the most direct visual answer to the experiment question. Later figures should explain the mechanism, comparison, or numerical adequacy needed to interpret that answer.

Residuals and generic convergence dashboards are supporting numerical evidence by default. Promote them into the core figure set only when convergence or solver behaviour is itself part of the hypothesis.

### Specify each planned figure explicitly

For every core figure, record:

| Field | Required content |
|---|---|
| `figure_id` | Stable short name such as `F1`, `F2` |
| `question` | The exact sub-question this figure answers |
| `message` | What scientific distinction the figure is intended to make, without predicting the result |
| `plot_type` | History, contour, profile, targeted comparison, scatter, bar, etc. |
| `x_axis` | Quantity, units, and domain/window; use iteration or physical time for evolving behaviour unless another axis is scientifically more informative |
| `y_axis_or_field` | Exact quantity/field, units, sign convention, phase/surface/zone scope |
| `series_or_cases` | Which variables/cases belong together and why |
| `comparison_basis` | Parent/reference/baseline, aligned window, normalization, threshold, or none |
| `reduction` | Raw, mean, rolling statistic, final-window range, area/volume average, integral, etc. |
| `data_source` | Monitor, report definition, `.out` history, case/data field, derived calculation, checkpoint, etc. |
| `pre_run_instrumentation` | Anything that must exist before solving so the figure can be produced |
| `interpretation_use` | What observation in this figure would support, weaken, or distinguish the competing explanations |

If one of these items is genuinely not applicable, say so rather than leaving the plot concept vague.

### Figure-design rules

- Prefer **one scientific message per figure**. Do not dump many unrelated monitors into one panel simply because they are available.
- For quantities that evolve during the solve, iteration or physical time should normally be the x-axis. Use endpoint bars/scatters only when the comparison or relationship itself is the scientific question.
- Use targeted comparisons. Do not create unreadable all-branch spaghetti plots when a branch-by-branch history or a small controlled comparison communicates the result more clearly.
- Keep units, sign conventions, phase/zone scope, reference definitions, and comparison windows explicit.
- Avoid dual y-axes unless there is a strong scientific reason; separate figures are usually clearer.
- Do not smooth away oscillations, reversals, drift, or failure tails. If a smoothed/reduced view is useful, preserve the raw history and state the reduction.
- A contour must answer a spatial question. Do not add generic velocity/pressure/volume-fraction contours merely because they are easy to produce.
- A figure can contain matched panels when the panels together answer one question; do not use panels as a way to hide an unfocused plot dump.
- For linked cases, keep definitions and axes comparable where the scientific comparison depends on them. Do not force identical limits when doing so would hide an important feature; record any deliberate difference.

### Plan the evidence behind the figures

The plot plan is also an instrumentation contract. If the decisive figure needs a history that cannot be reconstructed from the final `.dat.h5`, require the corresponding report definition/file/monitor before the run begins.

If the planned figure uses a derived metric, define the calculation, units, sign convention, source quantities, and comparison window now.

For linked setups or discovery matrices, make the evidence comparable enough that the intended comparison is actually possible.

The output of this section should make it possible for a later analysis agent to create the high-impact figures without inventing the scientific story after seeing the data.

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

Then call `create-setup` to convert that strategy into the required server-neutral setup records. `design-experiment` owns why the experiment strategy is worth doing, what working assumptions bound it, what evidence will judge it, and the core figure plan that communicates that evidence. `create-setup` owns the precise scientific handoff; `fluent-fleet-orchestration` later resolves exact placement, staging, and durable artifact handling.

Do not write predicted results into the setup records. The strategy defines what will be tested, what would be informative, and how the evidence should be visualised; the simulation data decides what actually happened.

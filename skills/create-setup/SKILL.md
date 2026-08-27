---
name: create-setup
description: "Turn one selected and justified experiment strategy into one or more clear setup records for implementation. Use after design-experiment and question-experiment have selected the strategy, before implement-experiment builds or runs the Fluent cases."
---

# Create Setup

Turn a selected experiment strategy into precise scientific and implementation handoffs.

The strategy may require one setup or several linked setups. Create the smallest set of setup records needed to preserve the intended campaign logic.

Do not redesign the strategy here. Preserve the reasoning that justified it and make each intended test explicit enough that a fresh implementation agent can build and run it without needing the design conversation.

## Carry forward the scientific intent

The setup record or linked setup set should make clear:

- the phase question the strategy contributes to;
- the specific uncertainty being tested;
- the hypothesis or competing explanations;
- why the strategy was selected over alternatives;
- the prior simulation or literature evidence that informed the choice;
- what the experiment or series is expected to teach, without predicting the result as fact.

When several setups belong together, make their relationship explicit: what each setup contributes, what comparison or sequence links them, and why the combined evidence is more useful than any one case alone.

## Define each experiment boundary

For every setup, state the reference or parent case, the intentional change, and what must remain comparable.

Make clear which settings are inherited, which are deliberately changed, and which differences would compromise interpretation.

If the selected strategy still contains an ambiguity that would materially change the experiment, return it for clarification rather than silently choosing.

## Define what must be observable

Carry the analysis requirements into the setup records before the runs.

Record the monitors, histories, fields, fluxes, reports, checkpoints, or other evidence needed to answer the experiment question. Use `plan-analysis` when the required evidence is non-trivial.

If evidence cannot be reconstructed after the run, make its instrumentation an explicit pre-run requirement.

For linked setups, make sure the evidence basis is comparable across the series where the planned interpretation depends on that comparison.

## Define the run intent

Specify enough about initialization, run mode, run length or stopping basis, numerical settings, checkpointing, and comparison basis for `implement-experiment` to reproduce the intended tests.

Do not invent unnecessary Fluent detail. Prefer a clear delta from a verified parent/reference case where that is safer and easier to audit.

## Preserve uncertainty

A setup is a plan, not a result.

Keep hypotheses labelled as hypotheses. Do not write expected trends as conclusions, and do not add acceptance criteria that were never part of the experiment design.

## Output

Create or update one setup record per distinct simulation in the selected strategy, using the repository's canonical setup location and naming conventions.

A useful setup record should contain, in a concise form:

- question and rationale;
- hypothesis or competing explanations;
- prior evidence informing the experiment;
- parent/reference identity;
- controlled change;
- frozen comparison context;
- implementation/run intent;
- evidence and analysis requirements;
- important assumptions, risks, and known limitations;
- campaign relationship when the setup is part of a linked series.

The handoff is complete when `implement-experiment` can build and run every intended setup and `interpret-experiment` can later recover both the purpose of each run and the logic of the combined experiment strategy.

---
name: create-setup
description: "Turn one selected and justified simulation experiment into a clear setup.md contract for implementation. Use after design-experiment and question-experiment have selected the experiment, before implement-experiment builds or runs the Fluent case."
---

# Create Setup

Turn a selected experiment into a precise scientific and implementation handoff.

Do not redesign the experiment here. Preserve the reasoning that justified it and make the intended test explicit enough that a fresh implementation agent can build and run it without needing the design conversation.

## Carry forward the scientific intent

The setup should make clear:

- the phase question this experiment contributes to;
- the specific uncertainty being tested;
- the hypothesis or competing explanations;
- why this experiment was selected over alternatives;
- the prior simulation or literature evidence that informed the choice;
- what the experiment is expected to teach, without predicting the result as fact.

## Define the experiment boundary

State the reference or parent case, the intentional change, and what must remain comparable.

Make clear which settings are inherited, which are deliberately changed, and which differences would compromise interpretation.

If the selected design still contains an ambiguity that would materially change the experiment, return it for clarification rather than silently choosing.

## Define what must be observable

Carry the analysis requirements into the setup before the run.

Record the monitors, histories, fields, fluxes, reports, checkpoints, or other evidence needed to answer the experiment question. Use `plan-analysis` when the required evidence is non-trivial.

If evidence cannot be reconstructed after the run, make its instrumentation an explicit pre-run requirement.

## Define the run intent

Specify enough about initialization, run mode, run length or stopping basis, numerical settings, checkpointing, and comparison basis for `implement-experiment` to reproduce the intended test.

Do not invent unnecessary Fluent detail. Prefer a clear delta from a verified parent/reference case where that is safer and easier to audit.

## Preserve uncertainty

A setup is a plan, not a result.

Keep hypotheses labelled as hypotheses. Do not write expected trends as conclusions, and do not add acceptance criteria that were never part of the experiment design.

## Output

Create or update `setup.md` in the experiment's canonical project location.

A useful setup should contain, in a concise form:

- question and rationale;
- hypothesis or competing explanations;
- prior evidence informing the experiment;
- parent/reference identity;
- controlled change;
- frozen comparison context;
- implementation/run intent;
- evidence and analysis requirements;
- important assumptions, risks, and known limitations.

The handoff is complete when `implement-experiment` can build and run the intended test and `interpret-experiment` can later recover what question the run was meant to answer.

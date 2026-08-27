---
name: create-setup
description: "Turn one selected and justified experiment strategy into one or more clear setup records for implementation. Use after design-experiment and question-experiment have selected the strategy, before implement-experiment builds or runs the Fluent cases."
---

# Create Setup

Turn a selected experiment strategy into precise scientific and implementation handoffs.

The strategy may require one setup or several linked setups. Create the smallest set of setup records needed to preserve the intended campaign logic.

Do not redesign the strategy here. Preserve the reasoning that justified it and make each intended test explicit enough that a fresh implementation agent can build and run it without needing the design conversation.

## Carry forward the scientific intent

The setup record or linked setup set should make clear the phase question, the uncertainty being tested, the hypothesis or competing explanations, why the strategy was selected, the prior simulation or literature evidence that informed it, and what the experiment is intended to teach without predicting the result as fact.

When several setups belong together, make their relationship explicit: what each setup contributes, what comparison or sequence links them, and why the combined evidence is useful.

## Define each experiment boundary

For every setup, state the verified parent/reference case, the intentional change, and what must remain comparable.

Make clear which settings are inherited, which are deliberately changed, and which differences would compromise interpretation.

If the selected strategy still contains an ambiguity that would materially change the experiment, return it for clarification rather than silently choosing.

## Carry the analysis design into the setup

The evidence plan created during `design-experiment` belongs in the setup contract.

Record the histories, monitors, report definitions, fields, fluxes, contours, checkpoints, or other outputs required to judge the hypothesis. Prefer iteration/time histories where behaviour over the run matters rather than relying on one final snapshot.

If evidence cannot be reconstructed after the run, make its instrumentation an explicit pre-run requirement.

For linked setups, preserve compatible definitions and output bases wherever the campaign depends on cross-case comparison.

## Define the run intent

Specify enough about initialization when required, run mode, fixed iteration target, numerical settings, checkpointing, and comparison basis for `implement-experiment` to reproduce the intended tests.

Do not invent unnecessary Fluent detail. Prefer a clear delta from a verified parent/reference case where that is safer and easier to audit.

## Preserve uncertainty

A setup is a plan, not a result.

Keep hypotheses labelled as hypotheses. Do not write expected trends as conclusions, and do not add acceptance criteria that were never part of the experiment design.

## Output

Create or update one setup record per distinct simulation in the selected strategy, using the repository's canonical setup location and naming conventions.

A useful setup record contains the question and rationale, hypothesis, prior evidence, parent/reference identity, controlled change, frozen comparison context, run intent, required evidence/visualisations, important assumptions and limitations, and any relationship to the wider linked campaign.

The handoff is complete when `implement-experiment` can build and run every intended setup and `interpret-experiment` can later recover both the purpose of each run and the logic of the combined experiment strategy.
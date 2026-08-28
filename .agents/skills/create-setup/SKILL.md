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

For every setup, state the verified parent/reference artifact, the intentional change, and what must remain comparable.

Prefer a server-neutral parent artifact identity over a machine-specific path. When available, record the artifact ID and enough provenance to distinguish the exact parent case/data state from similarly named files. Server identities and local paths belong to the later execution plan created by `fluent-fleet-orchestration`, not to the scientific meaning of the setup.

Make clear which settings are inherited, which are deliberately changed, and which differences would compromise interpretation.

If the selected strategy still contains an ambiguity that would materially change the experiment, return it for clarification rather than silently choosing.

## Carry the analysis design into the setup

The evidence plan created during `design-experiment` belongs in the setup contract.

Record the histories, monitors, report definitions, fields, fluxes, contours, checkpoints, or other outputs required to judge the hypothesis. Prefer iteration/time histories where behaviour over the run matters rather than relying on one final snapshot.

If evidence cannot be reconstructed after the run, make its instrumentation an explicit pre-run requirement.

For linked setups, preserve compatible definitions and output bases wherever the campaign depends on cross-case comparison.

## Define the run intent

Specify enough about initialization when required, run mode, fixed iteration target, numerical settings, checkpointing, and comparison basis for `implement-experiment` to reproduce the intended tests.

When the resulting final state is scientifically important, likely to become a future parent, or expensive to reproduce, mark it for durable preservation as a complete paired case+data artifact. Likewise, identify any deliberately selected recovery checkpoint worth preserving beyond the local server. Do not request OneDrive promotion for every routine autosave.

Do not invent unnecessary Fluent detail. Prefer a clear delta from a verified parent/reference case where that is safer and easier to audit.

## Keep the experiment packet together

The canonical experiment directory should keep these three records together:

```text
experiment/
├── setup.md
├── run-paths.yaml
└── results.md
```

`setup.md` is the server-neutral scientific contract. `run-paths.yaml` is populated later by `fluent-fleet-orchestration` once live placement and exact filesystem destinations are known. `results.md` records the resulting evidence and interpretation.

Do not put machine-specific server paths into `setup.md` merely because they are known at setup time. Do not create a second durable path manifest elsewhere. Keeping the three records together makes a fresh agent able to recover what was intended, where the actual run/artifacts lived, and what happened.

## Preserve uncertainty

A setup is a plan, not a result.

Keep hypotheses labelled as hypotheses. Do not write expected trends as conclusions, and do not add acceptance criteria that were never part of the experiment design.

## Output

Create or update one `setup.md` per distinct simulation in the selected strategy, using the repository's canonical experiment location and naming conventions.

A useful setup record contains the question and rationale, hypothesis, prior evidence, parent/reference artifact identity, controlled change, frozen comparison context, run intent, required evidence/visualisations, important assumptions and limitations, durability intent for final/selected recovery states, and any relationship to the wider linked campaign.

Do not bind the setup to a server merely because the parent currently lives there. After setup creation, `fluent-fleet-orchestration` resolves the current live server placement, verified parent source, any OneDrive transfer, exact runtime server reference, and exact remote paths into the sibling `run-paths.yaml`.

The handoff is complete when `fluent-fleet-orchestration` can place the setup, `implement-experiment` can build and run it from the exact resolved parent, and `interpret-experiment` can later recover both the purpose of the run and the logic of the combined experiment strategy.
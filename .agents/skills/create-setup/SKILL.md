---
name: create-setup
description: "Turn a selected and justified discovery or hypothesis strategy into precise server-neutral setup records, preserving lifecycle permission, evidence requirements, core figures, qualification horizon, and claim limits for faithful implementation."
---

# Create Setup

Turn a selected experiment strategy into precise scientific and implementation handoffs.

Do not redesign the strategy here. Preserve the reasoning and make the setup explicit enough that a fresh implementation agent can execute it without reconstructing the design conversation.

## Require the correct lifecycle state

Read the phase-root `phase-state.yaml`.

For a **discovery** setup require `DISCOVERY_DESIGN == PASS`.

For a **hypothesis-test** setup require:

```text
DISCOVERY_EVIDENCE == PASS
HYPOTHESIS_DEFINITION == PASS
question-experiment completed with no surviving blocker
```

Do not create later-stage setup records under an unresolved `HUMAN_REQUIRED` lock.

Do not convert missing human-owned information into an assumed surrogate unless the phase contract explicitly authorizes that surrogate class.

## Carry forward the scientific intent

Every setup or linked setup set should make clear:

- phase question;
- lifecycle mode: `discovery` or `hypothesis-test`;
- uncertainty/hypothesis being tested;
- competing explanation where relevant;
- why the strategy was selected;
- prior simulation/literature evidence that informed it;
- exact parent/reference artifact identity;
- intentional change and frozen comparison context;
- what the experiment is intended to teach without predicting the result.

For a hypothesis setup also preserve the verified hypothesis contract:

```text
hypothesis
verified discovery basis
competing explanation / material alternative
intended strong statement form
what would support it
what would weaken/reject it
important assumptions / claim limits
```

## Define each experiment boundary

For every setup state the verified parent/reference artifact, intentional delta, and invariants.

Prefer server-neutral artifact identity over machine paths. Server assignment and local paths belong later in `run-paths.yaml` through `fluent-fleet-orchestration`.

If an ambiguity would materially change the experiment, return it upstream rather than silently choosing.

## Carry the evidence and figure design unchanged

The evidence plan and core figure plan from `design-experiment` are part of the setup contract, not optional suggestions.

Record all required histories, reports, fields, fluxes, balances, residual/equation histories, contours, checkpoints, and derived metrics needed to judge the experiment.

If a quantity cannot be reconstructed after the run, mark its instrumentation as a **hard pre-run requirement**.

### Preserve the core figure contract

Include a compact **Core figure plan**. For each core figure record at least:

| Field | Required content |
|---|---|
| Figure | Stable ID/title |
| Question | Exact sub-question |
| Plot | Plot type and intended message |
| X-axis | Quantity, units, window |
| Y-axis / field | Exact quantity, units, sign, phase/zone/surface scope |
| Series / cases | What belongs together and why |
| Comparison basis | Parent/reference/window/normalization/threshold |
| Reduction | Raw/history/final-window statistic/etc. |
| Data source | Monitor/report/case-data/derived/checkpoint |
| Instrumentation | What must exist before solve |
| Interpretation use | What observation supports/weakens/distinguishes explanations |

Typical core-figure counts remain roughly `1–3` for discovery and `2–5` for hypothesis qualification. Supporting debug figures are secondary.

The first core figure should normally be the most direct visual answer to the experiment question.

## Define the run intent explicitly

Record:

- initialization intent;
- run mode;
- fixed iteration/time horizon;
- qualification/final analysis window;
- numerical settings that are part of the experiment;
- checkpoint/autosave intent;
- continuation/restart qualification when required;
- durability intent for final/selected recovery states.

### Hypothesis qualification depth

For ordinary steady iteration-based full-geometry hypothesis qualification, the setup must specify at least **10,000 iterations** unless it records:

- an explicit human-approved shorter-run exception; or
- a scientifically equivalent non-iteration qualification basis.

For slow inventory/routing/stationarity questions, use the deeper horizon selected by `design-experiment`, often 10k–30k.

Do not write `hypothesis-test` on a discovery-scale run and expect downstream skills to accept it.

When the intended statement depends on steady/stationary/bounded/reference behaviour, carry any required continuation or cold save/reopen qualification window into the setup.

## Make required evidence non-waivable after the run

Separate:

- **required evidence** — must exist for the intended judgement;
- **supporting evidence** — useful but not gate-critical.

If scaled residual history, a phase balance, a checkpoint comparison, or another signal is listed as required, later agents must not quietly waive it because the run finished without it.

Changing the evidence contract after seeing the result requires an explicit upstream redesign; it is not an interpretation convenience.

## Keep the experiment packet together

Use:

```text
experiment/
├── setup.md
├── run-paths.yaml
└── results.md
```

`setup.md` is server-neutral scientific intent. `run-paths.yaml` is populated by `fluent-fleet-orchestration`. `results.md` records resulting evidence/interpretation.

Do not put server paths into `setup.md` just because they are known.

## Preserve uncertainty

A setup is a plan, not a result.

Keep hypotheses labelled as hypotheses. Do not write expected trends as conclusions or add post-hoc acceptance criteria.

The figure/evidence plan may state what observations discriminate explanations, but not which result Fluent will produce.

## Output

Create/update one `setup.md` per distinct simulation in the selected strategy.

A complete setup should contain:

- phase/lifecycle mode and prerequisite gate references;
- question/rationale/hypothesis;
- prior evidence and competing explanation where relevant;
- parent/reference artifact identity;
- controlled delta and invariants;
- run/qualification intent and horizon;
- required versus supporting evidence;
- core figure plan;
- assumptions/limits;
- continuation/restart requirement if any;
- durability intent;
- linked-campaign relationship when applicable.

The handoff is complete when `fluent-fleet-orchestration` can place it, `implement-experiment` can prove and execute it faithfully, and later analysis can judge the exact predeclared evidence without inventing a new story after the run.

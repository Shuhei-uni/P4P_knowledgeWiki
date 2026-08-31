---
name: design-experiment
description: "Turn the current phase uncertainty into a high-information discovery strategy or, only after verified discovery, a deep hypothesis-qualification strategy. Design the evidence and core figures before compute is spent."
---

# Design Experiment

Design simulations to learn something important, not to generate more cases.

A useful design may be one decisive setup or a campaign of linked setups whose combined evidence answers a question that no single run can. The unit of design is the scientific strategy, not automatically one simulation.

## Respect the mandatory phase lifecycle

This skill has two modes, but they are not interchangeable entry points inside an autonomous phase.

```text
DISCOVERY DESIGN
→ discovery runs and analysis
→ DISCOVERY_EVIDENCE = PASS
→ HYPOTHESIS_DEFINITION = PASS
→ HYPOTHESIS-TEST DESIGN
```

Discovery is the normal first experiment-design stage of a new phase. Hypothesis-test mode is legal only when the phase-root `phase-state.yaml` shows `DISCOVERY_EVIDENCE == PASS` and `HYPOTHESIS_DEFINITION == PASS`, unless the human phase handoff supplied equivalent verified discovery evidence and `verify-phase-transition` accepted it.

Do not bypass the lifecycle because one candidate looks obvious.

## Start from the uncertainty

Begin with the question the phase still cannot answer.

Understand what is known, what is only suspected, what competing explanations are plausible, and what observation would actually change the current understanding.

Do not begin from an available parameter list and ask what can be swept. Begin from the uncertainty and ask what evidence could resolve it.

Reasoning, literature, previous experience, and prior simulations can shape the hypothesis. Unless there is genuinely equivalent prior evidence, they do not establish what a new simulation will do.

## Check for prior experiment collisions before generating candidates

Before proposing new experiments, inspect retained Project history across all phases, not only the current phase. Search by scientific substance: physical mechanism, modelling choice, formulation, boundary condition, numerical change, initialization, operating regime, intended question, and comparison logic.

For every serious candidate record:

- what was already tested;
- what happened, including failed, non-converged, partial, rejected, or inconclusive outcomes;
- the exact scientific delta;
- why existing evidence/additional analysis does not already answer the question;
- novelty: `NEW`, `PARTIAL REPEAT`, `REPLICATION`, or `REDUNDANT`.

Reject `REDUNDANT` candidates. A failed historical run still counts; rerun only when a concrete correction or unresolved delta makes the new attempt scientifically different.

This collision check applies equally to mainline, discovery, and speculative work.

## Discovery mode — earn a hypothesis

Use discovery mode to determine **what deserves qualification**, not to produce the final phase claim.

Use `explore-experiment-space` when breadth is useful. A discovery campaign may contain at most twelve cases; use fewer whenever they span the useful uncertainty. Roughly 500–1,000 iterations per case is a useful project ballpark when sufficient to expose comparative behaviour, not a convergence criterion.

Design discovery for:

- breadth across plausible mechanisms/branches;
- comparability;
- early response shape and direction;
- diagnostics that distinguish explanations;
- enough evidence to formulate a falsifiable hypothesis.

Every discovery strategy must state what it is screening and what outcome would justify deeper qualification.

### Mandatory discovery output

The discovery design must define the evidence needed so the later analysis can produce:

```text
candidate hypothesis
supporting discovery observations
strongest competing explanation
why discovery alone is insufficient for the final claim
what a long qualification run would need to establish
```

A discovery campaign has not succeeded merely because its cases completed. It succeeds when its evidence can narrow the uncertainty enough to earn a specific hypothesis.

Before implementation, `scientific-phase-loop` must obtain `DISCOVERY_DESIGN == PASS` from `verify-phase-transition`.

## Hypothesis-test mode — design for a strong statement

Use hypothesis-test mode only after the hypothesis contract is verified.

Start from the hypothesis contract, not from the most promising discovery setup. Preserve:

- one clear falsifiable hypothesis/question;
- discovery evidence that motivated it;
- strongest competing explanation or material alternative;
- observations that would support it;
- observations that would weaken/reject it;
- important assumptions and claim limits.

### Write the intended claim form before designing the run

State the form of strong statement the evidence should be capable of supporting, without predicting which answer will occur.

For example:

> Under the specified model and boundary conditions, the carrier solution is or is not demonstrably bounded and phase-mass-closed over the declared qualification window.

Then work backward from that statement. If a piece of evidence would be required to make the statement defensible, instrument it before the solve.

### Long qualification depth is mandatory

For ordinary steady iteration-based full-geometry hypothesis qualification in this project, the planned horizon must be **at least 10,000 iterations** by default.

For slow inventory, routing, stationarity, or convergence questions, 10k–30k or another deliberately justified longer horizon may be appropriate.

A shorter hypothesis run is allowed only when:

- the human explicitly approves the exception; or
- the experiment uses a scientifically equivalent non-iteration qualification basis appropriate to the model/question.

Do not relabel a 500–1,000 iteration discovery screen as `hypothesis-test`.

When the intended claim depends on steady/stationary/bounded/reference behaviour, include a deliberate continuation or cold save/reopen qualification window when needed to distinguish a durable state from a favourable transient.

### Hypothesis qualification contract

Record at minimum:

```yaml
hypothesis: ...
discovery_basis: ...
competing_explanation: ...
intended_statement_form: ...
would_support: ...
would_weaken: ...
qualification_horizon: ...
qualification_window: ...
restart_or_continuation_requirement: ...
required_numerical_evidence: ...
required_physical_evidence: ...
required_core_figures: ...
```

If numerical credibility is necessary to the claim, scaled residual/equation histories or another explicitly justified equivalent are **required evidence**, not optional post-run decoration.

Missing required evidence after the run means the evidence gate fails; do not design a contract whose requirements the implementation cannot actually capture.

## Use the live fleet as a constraint and opportunity

Use the current resource envelope from `fluent-fleet-orchestration` before finalizing runnable work.

Know which servers are reachable, which exact parents/recovery states are available locally or through OneDrive, and which sessions the active scientific goal can take over under its authority envelope.

Let fleet state influence campaign shape and execution efficiency, not the scientific question itself.

When two or more servers are usable for new compute, include a justified bold-probe candidate for the dedicated bold lane. Call `bold-probe-research` before selecting it. Do not invent weak extra cases merely to use idle capacity.

Keep setup identity server-neutral. Placement is resolved later.

## Record working assumptions without hiding missing facts

Keep hypotheses and assumptions distinct:

- **hypothesis** — actively tested;
- **working assumption** — accepted temporarily so the test can proceed;
- **missing human-owned fact** — cannot be replaced by an assumption unless the phase contract explicitly authorizes a surrogate class.

Use `accepted-for-now`, `questioned`, and `materially-challenged` where useful.

If an assumption would materially determine the answer rather than merely bound it, surface that before compute. If it crosses a human boundary, the correct result is `HUMAN_REQUIRED`, not an invented target or plant parameter.

## Design the smallest useful strategy

Prefer the smallest strategy that can produce the needed learning **at the required evidence depth**.

In discovery this may be a bounded small matrix because breadth is the information source.

In hypothesis-test mode this may be one deep run, a controlled pair, or a very small linked campaign. “Smallest” must not be used to shrink the qualification horizon until the intended claim is no longer supportable.

## Design evidence and figures before the run

Analysis planning is part of experiment design.

For each hypothesis/comparison decide what result would let you judge it and what evidence must therefore exist when the run finishes. Prefer behaviour over the run rather than only an endpoint.

### Require a small core figure set

Default:

- discovery: usually `1–3` reusable core figures;
- hypothesis qualification: usually `2–5` core figures supporting distinct reasoning steps.

The first core figure should normally be the most direct visual answer to the experiment question. Generic residual dashboards are supporting numerical evidence unless convergence itself is the question.

For every core figure specify:

| Field | Required content |
|---|---|
| `figure_id` | Stable ID |
| `question` | Exact sub-question |
| `message` | Scientific distinction, without predicting result |
| `plot_type` | History/contour/profile/comparison/etc. |
| `x_axis` | Quantity, units, window |
| `y_axis_or_field` | Exact quantity/field, units, sign, phase/zone scope |
| `series_or_cases` | What belongs together and why |
| `comparison_basis` | Parent/reference/window/normalization |
| `reduction` | Raw/mean/final-window/etc. |
| `data_source` | Monitor/report/case-data/derived/checkpoint |
| `pre_run_instrumentation` | What must exist before solve |
| `interpretation_use` | What observation distinguishes explanations |

### Figure and evidence rules

- one scientific message per figure;
- use iteration/physical time for evolving quantities unless another axis is more informative;
- avoid unfocused spaghetti plots and unnecessary dual axes;
- preserve raw oscillation/drift even when showing reductions;
- contours must answer a spatial question;
- define units, sign conventions, phase/zone scope, and comparison windows;
- if a decisive history cannot be reconstructed from final data, require its monitor/report before the run;
- define derived metrics before execution.

The later analysis agent should be able to create the key figures without inventing the scientific story after seeing the data.

## Generate and challenge candidate strategies

When several plausible strategies exist, generate a small set of genuinely different approaches. Use `arena`, independent subagents, or literature-focused `swarm` when useful.

Call `question-experiment` before selection.

For hypothesis qualification, independent challenge is mandatory. The reviewer must check not only scientific value, interpretability, and cost, but also whether the proposed evidence/horizon could actually support the intended strong statement and whether a human lock or material missing fact is being bypassed.

`question-experiment` recommends a strategy. It does not grant lifecycle permission.

## Select and formalize

Choose the best justified strategy for the current mode, then call `create-setup`.

Before discovery implementation, require `DISCOVERY_DESIGN == PASS` from `verify-phase-transition`.

Before hypothesis qualification launch, require `HYPOTHESIS_RUN_READY == PASS` after setup creation, implementation readback/save-reopen/smoke, instrumentation verification, horizon verification, and the runtime-specific self-wake contract are all in place.

Do not write predicted results into setup records. The setup defines what will be tested, what evidence will judge it, and how that evidence should be visualised. Simulation data decides what happened.

---
name: verify-phase-transition
description: "Independently verify that Phase Loop or Auto Loop has satisfied a hard lifecycle transition. Return PASS or BLOCK; the calling loop must autonomously recover a BLOCK and may not self-overrule it."
---

# Verify Phase Transition

Act as the independent gatekeeper for `phase-loop` and `auto-loop`.

This skill does not design the next experiment, reinterpret inconvenient evidence, or help the calling agent justify a preferred transition. Its job is narrower:

> Has the evidence required for this exact lifecycle transition actually been produced and verified?

A transition is permission to advance, not a progress summary.

## Independent-review rule

Use a fresh independent reviewer/subagent whenever the runtime supports subagents. Give the reviewer the phase contract, `phase-state.yaml`, the artifacts/evidence relevant to the requested transition, and the gate criteria, but do not prime it with the main agent's preferred answer.

Where useful, use `interrogate` as the adversarial-review pattern. The main scientific agent may synthesize factual corrections, but it may not convert a surviving blocker into a pass merely because it disagrees with the reviewer.

Machine-checkable requirements should be checked deterministically before scientific judgement. Do not ask a reviewer to infer whether a file exists, whether the requested iteration count was reached, how many valid discovery cases completed, or whether a recorded gate is already blocked when those facts can be verified directly.

## Allowed outputs

Return exactly one gate status:

- `PASS` — every mandatory requirement for this transition is satisfied and evidenced;
- `BLOCK` — the transition is not allowed yet. The caller must inspect, research,
  repair, sensitise, defer, or durably record this path under the autonomous
  recovery contract before choosing another valid in-envelope path.

The calling loop must not proceed past `BLOCK`.

A later verification may replace a prior `BLOCK` only after new evidence resolves the listed deficiency. A durable autonomous block permits the loop to defer that path and continue other valid work, but never to claim this transition passed.

## Canonical lifecycle gates

Use these gate IDs in `phase-state.yaml`.

### `PHASE_CONTRACT`

Require:

- a phase-root `CONTEXT.md` with the current human-approved planning state and,
  for Auto Loop, its recorded bounded exploration envelope;
- a fixed phase question/goal;
- explicit in-scope and out-of-scope boundaries;
- important known facts versus assumptions/missing information separated;
- what would count as enough evidence for a useful phase conclusion;
- the active loop type and autonomy authority envelope, including Fluent
  fleet/session authority;
- autonomous recovery and durable-block recording conditions.

For Phase Loop, require a declared setup queue. For Auto Loop, require the
recorded family focus, deepening/enumeration direction, hypothesis horizon,
stop time/timezone, and one recorded Fluent-authority outcome. Do not pass if
  either loop lacks a defensible recorded assumption/sensitivity plan for a
  material external fact needed to begin.

### `DISCOVERY_DESIGN`

Require:

- `CONTEXT.md` identifies every proposed screen by candidate ID, origin,
  authority source, and decision-gate linkage;
- current phase uncertainty is explicit;
- prior-experiment collision check completed;
- discovery strategy is genuinely screening/diagnostic rather than a disguised qualification claim;
- required monitors/histories and core figures are specified before execution;
- each proposed case can teach something relevant;
- the campaign contains enough contrastive cases to satisfy its declared
  decision gate, with no case outside the Phase Loop queue or Auto Loop
  envelope added for breadth or idle capacity;
- every possible long-run promotion is a named conditional qualification path
  or an Auto Loop-recorded path linked to completed discovery evidence;
- no unsupported surrogate is being passed off as a fact; material unknowns
  must be labelled `Assumed`, bounded by research/sensitivity where feasible,
  and reflected in the claim limit.

Return `BLOCK` when a proposed case lacks valid authority, provenance, required
evidence, or decision-gate coverage. If a fact or direction is missing, return
`BLOCK` with the narrowest research, sensitivity, or in-envelope recovery
needed. A Phase Loop cannot silently replace a queue item with an unrelated
scientific case.

### `DISCOVERY_EXECUTION`

Require for every discovery run counted as evidence:

- exact parent identity verified;
- intended setup state read back;
- save/reopen verification passed;
- smoke test passed;
- required file-backed instrumentation appeared at declared paths;
- requested discovery horizon was actually reached;
- final case/data and required histories are locatable;
- the discovery agent remained attached until terminal execution evidence returned.

A tool/RPC timeout while Fluent is still solving is not terminal discovery evidence.

### `DISCOVERY_EVIDENCE`

Require:

- every Phase Loop queue item or Auto Loop-generated discovery case required by
  the declared gate has completed and passed its execution requirements;
- the completed discovery runs have been compared and analysed, not merely listed;
- the planned core figures/equivalent decisive evidence exist;
- the corresponding `results.md` identifies the exact experiment/run and
  answers its declared screening question rather than only listing outputs;
- selected core figures are embedded in the report with readable captions and
  figure-linked observations, or each unavailable required figure records its
  evidence consequence;
- raw histories, manifests, and machine paths are supporting detail rather than
  the report's main narrative;
- important numerical/physical caveats are identified;
- discovery has materially narrowed the uncertainty;
- at least one specific, falsifiable hypothesis is supported strongly enough to justify qualification compute;
- a meaningful competing explanation or claim limit is stated;
- discovery evidence is not being presented as the final qualification result.

Do not pass because an early result looks decisive unless the recorded gate
explicitly covers that result and its declared evidence is complete. If a Phase
Loop screen is insufficient or uncertainty remains broad, return `BLOCK` and
recover with its nearest allowed diagnostic. Auto Loop must make another
in-envelope screen or record a durable autonomous block.

If no defensible hypothesis has emerged, return `BLOCK` and require more/better discovery rather than permitting a weak hypothesis test.

### `HYPOTHESIS_DEFINITION`

Require a hypothesis contract containing:

- a named human-approved conditional qualification path, or an Auto
  Loop-recorded qualification path, and the gate that triggered it;
- one clear falsifiable statement/question;
- the discovery evidence that motivated it;
- the strongest competing explanation or material alternative;
- what observations would support it;
- what observations would weaken/reject it;
- the form of strong statement the project could make if evidence is sufficient;
- important assumptions and claim limits.

### `HYPOTHESIS_RUN_READY`

Require:

- `DISCOVERY_EVIDENCE == PASS` and `HYPOTHESIS_DEFINITION == PASS`;
- the setup references the authorized context qualification-path ID and no
  unresolved context lock exists;
- a focused long-run setup/campaign designed backward from the intended strong statement;
- required histories, balances, residuals/numerical evidence, fields, checkpoints, and core figures are instrumented before the solve;
- exact parent/setup/readback/save-reopen/smoke verification passed;
- the selected horizon is adequate for the claim;
- for ordinary steady iteration-based full-geometry qualification, the planned horizon is at least 10,000 iterations unless the setup declares a scoped Auto Loop qualification horizon (normally 2,000 iterations) with a correspondingly bounded claim, or a scientifically equivalent non-iteration basis is recorded;
- when a claim depends on stationarity/steady behaviour, restart/continuation qualification is included when needed to distinguish transient drift from a durable state;
- for Codex detached hypothesis runs, exact originating thread capture, `COMPLETE` and `BLOCKED` wake triggers, and deterministic completion verification are configured before launch.

A discovery-scale run must not pass this gate merely because it is labelled `hypothesis-test`.

### `HYPOTHESIS_EXECUTION`

Require:

- the approved horizon was actually reached, or a genuine execution failure is recorded as `BLOCK`;
- required final paired case/data exist;
- required report/monitor/checkpoint outputs exist at declared locations;
- terminal completion verification passed;
- on Codex, the exact originating scientific thread was resumed or a separately recorded handoff failure exists after terminal evidence was safely persisted.

Poor scientific behaviour is evidence, not an execution failure, when Fluent successfully reached the approved horizon.

### `HYPOTHESIS_EVIDENCE`

Require:

- all evidence declared necessary to judge the hypothesis is present;
- planned core figures/equivalent analyses have been produced;
- the corresponding `results.md` gives a plot-led answer to the hypothesis:
  selected core figures are embedded with captions, observations are tied to
  them, and the report states the bounded conclusion and limitations;
- referenced report-facing figures exist at their declared Project-local paths,
  or the report explicitly records why a required figure is unavailable and
  the resulting evidence block;
- numerical credibility is assessed using the evidence the setup said was required;
- required residual/history evidence is not silently waived after the run;
- final-window/qualification statistics use an explicit window/basis;
- the hypothesis is classified from the data with important limits and competing explanations retained;
- the resulting statement is no stronger than implementation quality, run depth, and evidence completeness allow.

If a required history, core figure, or curated result explanation is missing,
return `BLOCK`; do not compensate with prose, raw artifact links, or a generic
diagnostic dashboard.

### `PHASE_CLOSURE`

Normal autonomous `CONCLUDE PHASE` requires all of:

- `PHASE_CONTRACT == PASS`;
- `DISCOVERY_EVIDENCE == PASS`;
- `HYPOTHESIS_DEFINITION == PASS`;
- `HYPOTHESIS_RUN_READY == PASS`;
- `HYPOTHESIS_EXECUTION == PASS`;
- `HYPOTHESIS_EVIDENCE == PASS`;
- no unresolved autonomous recovery item that would materially change the
  proposed closure statement;
- independent review finds that the proposed phase-level statement follows from the accumulated evidence and further feasible work is unlikely to materially change that statement.

A human may explicitly terminate/reframe a phase earlier. The autonomous loop may not manufacture an early `CONCLUDE PHASE` by skipping qualification.

## Persist the decision

Write or update the phase-root `phase-state.yaml` with:

```yaml
state: <current lifecycle state>
gates:
  <GATE_ID>:
    status: PASS | BLOCK
    checked_at: <timestamp or commit/run reference when available>
    evidence:
      - <artifact/path/manifest/result pointer>
    missing:
      - <exact unsatisfied requirement>
    reviewer: <independent reviewer/subagent reference when available>
```

Keep this file as current machine-readable workflow state, not a narrative log. Git history records prior gate states.

Do not mark the next lifecycle state active until the gate permitting that transition is `PASS`.

## Output

Return:

1. gate ID;
2. status: `PASS` or `BLOCK`;
3. deterministic checks performed;
4. strongest independent-review finding;
5. exact evidence supporting the status;
6. exact missing requirements when not `PASS`;
7. permitted next lifecycle state when `PASS`.

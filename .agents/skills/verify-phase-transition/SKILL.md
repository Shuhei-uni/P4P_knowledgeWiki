---
name: verify-phase-transition
description: "Independently verify that an autonomous scientific phase has satisfied the hard requirements for a lifecycle transition. Use before every scientific-phase-loop transition that changes lifecycle state. Return PASS, BLOCK, or HUMAN_REQUIRED; the calling loop may not self-overrule BLOCK or HUMAN_REQUIRED."
---

# Verify Phase Transition

Act as the independent gatekeeper for `scientific-phase-loop`.

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
- `BLOCK` — the transition is not allowed yet, but the deficiency can be addressed within the current phase/autonomy boundary;
- `HUMAN_REQUIRED` — progress requires information, permission, or a phase-level decision that the autonomous loop is not allowed to invent or self-authorize.

The calling loop must not proceed past `BLOCK` or `HUMAN_REQUIRED`.

A later verification may replace a prior `BLOCK` only after new evidence resolves the listed deficiency. A `HUMAN_REQUIRED` lock may be cleared only by explicit human input/authorization or by newly located authoritative evidence that directly resolves the stated missing fact without changing the phase contract.

## Canonical lifecycle gates

Use these gate IDs in `phase-state.yaml`.

### `PHASE_CONTRACT`

Require:

- a fixed phase question/goal;
- explicit in-scope and out-of-scope boundaries;
- important known facts versus assumptions/missing information separated;
- what would count as enough evidence for a useful phase conclusion;
- the autonomous authority envelope, including Fluent fleet/session authority;
- explicit human-return conditions.

Do not pass if the loop would need to invent a plant fact, validation target, physical boundary condition, or other human-owned fact in order to begin.

### `DISCOVERY_DESIGN`

Require:

- current phase uncertainty is explicit;
- prior-experiment collision check completed;
- discovery strategy is genuinely screening/diagnostic rather than a disguised qualification claim;
- the planned discovery campaign contains **at least 6 and at most 12 cases**;
- the six-case minimum is not being waived simply because an early candidate looks promising;
- required monitors/histories and core figures are specified before execution;
- each proposed case can teach something relevant;
- bold-probe research has been performed when a bold lane is required;
- no unresolved human lock is being bypassed with an invented surrogate unless the phase contract explicitly authorizes that surrogate class.

Return `BLOCK` when fewer than six discovery cases are planned. A different discovery case-count rule requires explicit human phase-level authorization.

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

- **at least six valid discovery cases have completed** and passed their execution requirements;
- the completed discovery runs have been compared and analysed, not merely listed;
- the planned core figures/equivalent decisive evidence exist;
- important numerical/physical caveats are identified;
- discovery has materially narrowed the uncertainty;
- at least one specific, falsifiable hypothesis is supported strongly enough to justify qualification compute;
- a meaningful competing explanation or claim limit is stated;
- discovery evidence is not being presented as the final qualification result.

Do not pass because one or two early cases look decisive. The six-case minimum is intended to provide comparative breadth before hypothesis promotion. If fewer than six valid cases exist, return `BLOCK`. If six cases are complete but uncertainty remains broad, require additional discovery up to the twelve-case ceiling or a redesigned discovery strategy.

If no defensible hypothesis has emerged, return `BLOCK` and require more/better discovery rather than permitting a weak hypothesis test.

### `HYPOTHESIS_DEFINITION`

Require a hypothesis contract containing:

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
- a focused long-run setup/campaign designed backward from the intended strong statement;
- required histories, balances, residuals/numerical evidence, fields, checkpoints, and core figures are instrumented before the solve;
- exact parent/setup/readback/save-reopen/smoke verification passed;
- the selected horizon is adequate for the claim;
- for ordinary steady iteration-based full-geometry qualification, the planned horizon is at least 10,000 iterations unless an explicit human-approved exception or scientifically equivalent non-iteration qualification basis is recorded;
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
- numerical credibility is assessed using the evidence the setup said was required;
- required residual/history evidence is not silently waived after the run;
- final-window/qualification statistics use an explicit window/basis;
- the hypothesis is classified from the data with important limits and competing explanations retained;
- the resulting statement is no stronger than implementation quality, run depth, and evidence completeness allow.

If a required history is missing, return `BLOCK`; do not compensate with prose.

### `PHASE_CLOSURE`

Normal autonomous `CONCLUDE PHASE` requires all of:

- `PHASE_CONTRACT == PASS`;
- `DISCOVERY_EVIDENCE == PASS`;
- `HYPOTHESIS_DEFINITION == PASS`;
- `HYPOTHESIS_RUN_READY == PASS`;
- `HYPOTHESIS_EXECUTION == PASS`;
- `HYPOTHESIS_EVIDENCE == PASS`;
- no unresolved `HUMAN_REQUIRED` lock;
- independent review finds that the proposed phase-level statement follows from the accumulated evidence and further feasible work is unlikely to materially change that statement.

A human may explicitly terminate/reframe a phase earlier. The autonomous loop may not manufacture an early `CONCLUDE PHASE` by skipping qualification.

## Persist the decision

Write or update the phase-root `phase-state.yaml` with:

```yaml
state: <current lifecycle state>
gates:
  <GATE_ID>:
    status: PASS | BLOCK | HUMAN_REQUIRED
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
2. status: `PASS`, `BLOCK`, or `HUMAN_REQUIRED`;
3. deterministic checks performed;
4. strongest independent-review finding;
5. exact evidence supporting the status;
6. exact missing requirements when not `PASS`;
7. permitted next lifecycle state when `PASS`.

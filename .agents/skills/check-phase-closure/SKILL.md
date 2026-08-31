---
name: check-phase-closure
description: "Decide whether an autonomous scientific phase should continue, conclude, or return to the human after verified hypothesis evidence exists. Normal autonomous closure is illegal until the mandatory lifecycle gates have passed."
---

# Check Phase Closure

Decide whether the phase has earned a conclusion **after** the mandatory discovery → hypothesis-qualification lifecycle has produced verified evidence.

This is not an early-exit skill for discovery.

## Closure precondition

Before scientific closure judgement, read the phase-root `phase-state.yaml`.

Normal autonomous `CONCLUDE PHASE` is not permitted unless all of these are `PASS`:

```text
PHASE_CONTRACT
DISCOVERY_EVIDENCE
HYPOTHESIS_DEFINITION
HYPOTHESIS_RUN_READY
HYPOTHESIS_EXECUTION
HYPOTHESIS_EVIDENCE
```

There must also be no unresolved `HUMAN_REQUIRED` lock.

If the lifecycle is incomplete:

- return `CONTINUE` when the missing work is still inside the current phase/autonomy boundary;
- return `RETURN TO HUMAN / PHASE-PLANNER` when the missing requirement is human-owned;
- do **not** reinterpret short discovery evidence as sufficient phase closure.

A human may explicitly terminate or reframe a phase before this lifecycle completes. That is a human decision, not autonomous `CONCLUDE PHASE`.

## Judge the phase, not only the last run

Use accumulated evidence across discovery, hypothesis qualification, previous phases, numerical checks, and important claim limits.

Ask:

- What phase-level statement is actually supported now?
- Did the hypothesis qualification reach the depth and evidence completeness required by its setup contract?
- Did required residual/numerical histories, physical monitors, balances, and core figures actually exist?
- Does the phase-level statement stay within the verified model/setup/run limitations?
- Is there a competing explanation or materially challenged assumption that could still change the answer?
- Is there a feasible next investigation whose result could materially strengthen or reverse the proposed conclusion?

A bounded, conditional, or negative conclusion is valid. A missing required evidence stream is not.

If the hypothesis setup required scaled residual history, restart evidence, a final-window statistic, or another qualification signal and it is unavailable, closure is blocked until that evidence is repaired, rerun, or the human explicitly changes the claim/evidence requirement before the run.

Do not weaken the evidence standard after seeing an inconvenient result.

## Treat assumptions proportionately

Use:

- `accepted-for-now`;
- `questioned`;
- `materially-challenged`.

Do not demand proof of every assumption. Ask whether an assumption materially limits or threatens the specific phase-level statement.

A missing plant fact or other human-owned parameter is not a working assumption merely because the agent would like to continue. If the conclusion depends on it, return to the human.

## Return one of three outcomes

### `CONTINUE`

Choose `CONTINUE` when:

- a lifecycle gate remains `BLOCK` but can be resolved autonomously;
- the verified hypothesis result reveals another focused uncertainty that could materially change the phase answer;
- evidence is incomplete for the intended statement;
- another discovery/qualification cycle has clear information value.

State which lifecycle state should be reopened and why. Do not design the experiment here.

### `CONCLUDE PHASE`

Choose `CONCLUDE PHASE` only when:

- all lifecycle preconditions above are `PASS`;
- an independent `verify-phase-transition` review of `PHASE_CLOSURE` returns `PASS`;
- the accumulated evidence supports a useful bounded statement;
- further feasible work is unlikely to change that statement enough to matter.

State the supported conclusion, important claim limits, and any assumptions that remain accepted-for-now/questioned but do not threaten it.

### `RETURN TO HUMAN / PHASE-PLANNER`

Choose this when useful progress depends on a decision or fact outside the granted autonomy envelope: scope/model-boundary change, missing plant/validation information, phase-question change, explicit resource decision, or another persisted human lock.

State exactly what decision/fact is needed and which evidence brought the phase to that boundary.

## Independent closure review is mandatory

Before `CONCLUDE PHASE`, call `verify-phase-transition` for `PHASE_CLOSURE`.

That review must independently check that:

- the mandatory lifecycle actually occurred;
- the hypothesis evidence gate passed on the evidence promised before the run;
- the proposed phase-level statement follows from the data rather than from labels/setup intent;
- no important missing evidence is being waived retrospectively;
- no unresolved human lock is being bypassed;
- the conclusion is no broader than the tested formulation/range/conditions.

The scientific loop may not self-overrule a closure `BLOCK`.

## Anti-loop safeguard

Track whether meaningful cycles are changing the scientific picture.

If two consecutive cycles fail to reduce an important uncertainty, strengthen the statement, or materially update an assumption:

- do not generate a third nearby variation by habit;
- reopen discovery with a substantially different researched question/branch, including the bold-probe process when appropriate; or
- return to the human if the needed rethink crosses the phase boundary.

Stagnation can justify changing the route. It does not justify skipping qualification.

## Output

Return only:

1. **Outcome:** `CONTINUE`, `CONCLUDE PHASE`, or `RETURN TO HUMAN / PHASE-PLANNER`;
2. **Lifecycle readiness:** which mandatory gates are `PASS`, `BLOCK`, or `HUMAN_REQUIRED`;
3. **Phase-level statement currently supported**;
4. **Important unresolved hypothesis / materially challenged assumption / missing evidence**, if any;
5. **Why another cycle is or is not worth doing**;
6. **Stagnation status**;
7. **Important limits or human decision boundary**;
8. **PHASE_CLOSURE verifier result** when conclusion is proposed.

Do not create the next experiment. This skill decides whether the verified lifecycle has earned closure.

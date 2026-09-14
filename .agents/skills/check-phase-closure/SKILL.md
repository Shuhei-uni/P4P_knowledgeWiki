---
name: check-phase-closure
description: "Decide whether an autonomous scientific phase should continue, conclude, or finish timeboxed with durable autonomous blocks after verified hypothesis evidence exists."
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

There must also be no unresolved autonomous recovery item that would materially
change the proposed closure statement.

If the lifecycle is incomplete:

- return `CONTINUE` when a repair, sensitivity, or in-envelope alternate path
  remains feasible;
- return `AUTONOMOUSLY BLOCKED / TIMEBOX EXHAUSTED` when no such path remains
  or the recorded deadline prevents another launch;
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

If the hypothesis setup required scaled residual history, restart evidence, a final-window statistic, or another qualification signal and it is unavailable, closure is blocked until that evidence is repaired, rerun, or the claim is bounded to what the verified evidence can support.

Do not weaken the evidence standard after seeing an inconvenient result.

## Treat assumptions proportionately

Use:

- `accepted-for-now`;
- `questioned`;
- `materially-challenged`.

Do not demand proof of every assumption. Ask whether an assumption materially limits or threatens the specific phase-level statement.

A missing external parameter is not a working fact merely because the agent
would like to continue. Research the narrowest defensible range, record an
`Assumed` surrogate/sensitivity where it is material, and bound the conclusion;
if no defensible path remains, preserve an autonomous block.

## Return one of three outcomes

### `CONTINUE`

Choose `CONTINUE` when:

- a lifecycle gate remains `BLOCK` and the approved context path explicitly
  authorizes the repair;
- the verified hypothesis result requires a named Phase Loop-approved context
  path, or an Auto Loop-recorded path still inside its envelope, that could
  materially change the phase answer;
- evidence is incomplete for the intended statement;
- another authorized discovery/qualification cycle has clear information value.

State which lifecycle state should be reopened and why. Do not design the experiment here.

### `CONCLUDE PHASE`

Choose `CONCLUDE PHASE` only when:

- all lifecycle preconditions above are `PASS`;
- an independent `verify-phase-transition` review of `PHASE_CLOSURE` returns `PASS`;
- the accumulated evidence supports a useful bounded statement;
- further feasible work is unlikely to change that statement enough to matter.

State the supported conclusion, important claim limits, and any assumptions that remain accepted-for-now/questioned but do not threaten it.

### `AUTONOMOUSLY BLOCKED / TIMEBOX EXHAUSTED`

Choose this only after autonomous recovery has exhausted the useful,
context-consistent options or the timebox has ended. It may cover a missing
external fact, unavailable resource, phase-boundary conflict, or failed
technical route, but it is a durable autonomous disposition—not a request for
a reply.

State the attempted research/repairs, the exact unresolved limitation, retained
artifacts, and the strongest bounded conclusion supported.

## Independent closure review is mandatory

Before `CONCLUDE PHASE`, call `verify-phase-transition` for `PHASE_CLOSURE`.

That review must independently check that:

- the mandatory lifecycle actually occurred;
- the hypothesis evidence gate passed on the evidence promised before the run;
- the proposed phase-level statement follows from the data rather than from labels/setup intent;
- no important missing evidence is being waived retrospectively;
- no unresolved recovery item is being bypassed;
- the conclusion is no broader than the tested formulation/range/conditions.

The scientific loop may not self-overrule a closure `BLOCK`.

## Anti-loop safeguard

Track whether meaningful cycles are changing the scientific picture.

If two consecutive cycles fail to reduce an important uncertainty, strengthen the statement, or materially update an assumption:

- do not generate a third nearby variation by habit;
- generate a materially different, research-backed in-envelope diagnostic or
  sensitivity route; or
- record `AUTONOMOUSLY BLOCKED / TIMEBOX EXHAUSTED` with the failed approaches
  and the retained evidence.

Stagnation can justify changing the route. It does not justify skipping qualification.

## Output

Return only:

1. **Outcome:** `CONTINUE`, `CONCLUDE PHASE`, or `AUTONOMOUSLY BLOCKED / TIMEBOX EXHAUSTED`;
2. **Lifecycle readiness:** which mandatory gates are `PASS` or `BLOCK`;
3. **Phase-level statement currently supported**;
4. **Important unresolved hypothesis / materially challenged assumption / missing evidence**, if any;
5. **Why another cycle is or is not worth doing**;
6. **Stagnation status**;
7. **Important limits and durable autonomous-block boundary**;
8. **PHASE_CLOSURE verifier result** when conclusion is proposed.

Do not create the next experiment. This skill decides whether the verified lifecycle has earned closure.

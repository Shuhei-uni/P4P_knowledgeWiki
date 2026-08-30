# Phase 06 — Full Geometry with Brine Pool

## Status and fixed phase-level question

**Selected by the human; phase definition only.** No new CFD case has been
configured or run under this phase.

> **Can a full-geometry CFD model reproduce a physically credible, controlled
> bottom brine-pool operating condition for the separator, rather than merely
> a response to a fixed brine-outlet pressure?**

This question is fixed for every later Phase-6 stage. A stage may narrow the
uncertainty it addresses, but it must not substitute a different ultimate
question or assume the answer is a particular multiphase model, time treatment,
outlet type, or control law.

For Phase 6, a credible controlled operating condition requires a meaningful
pool-level observable at the real measurement location, a specified target and
acceptable band, physically grounded outlet/control behaviour, phase-resolved
conservation consistent with the level behaviour, and numerically credible
equation and output histories.

## Stage-question rule

Later stage questions are subordinate to the fixed phase question. Each must
state which uncertainty it reduces and how its result could change the
phase-level answer. Examples include: identifying the plant control mechanism,
constructing and verifying a pool-level observable, testing a specified
controlled quasi-steady outlet, or determining whether literal controller
dynamics are required. A pressure-only, turbulence-only, or numerical sweep
does not qualify unless it directly tests one of those links.

## Why this phase now

Stage 5 held the brine outlet at a fixed gauge pressure. Across the controlled
pressure × practical-`k-epsilon` screens, every candidate retained non-zero
imbalance and moving liquid inventory; higher pressure was worse and
Realizable `k-epsilon` did not improve on RNG. Those observations do not model
the reported plant mechanism in which the brine outlet is adjusted to hold a
bottom liquid-pool level near a setpoint.

**Reported by the human.** The real separator has a finely controlled liquid
brine pool at the bottom. Its outlet behaviour is tuned to maintain a nearly
constant pool level. Pool level and scaled-residual behaviour are therefore
more meaningful primary targets than the unqualified total-liquid inventory
seen under a fixed outlet pressure.

**Human context, not a phase target.** A rough thought about inlet and brine
outlet flow magnitudes motivated the discussion, but it is not a fixed Phase-6
target, acceptance criterion, or candidate controller setpoint. Stage 5 does
show that phase-specific and mixture-flow quantities differ materially, so
every later stage must define its flow basis explicitly rather than treating a
single rough value as the answer.

## Reframed evidence logic

The liquid balance remains an essential corroborating conservation check; it
is not replaced by level. For a liquid pool, net liquid flow determines the
direction of level motion. The phase therefore treats the following as a
linked evidence set, not alternatives:

| Role | Required evidence |
|---|---|
| primary physical target | pool level relative to the actual setpoint and admissible band |
| primary control response | brine-outlet/valve condition and phase-resolved brine discharge responding in the direction required by level error |
| conservation check | liquid inlet/outlet fluxes, full-domain and pool-region liquid balance, and inventory/level trend |
| numerical credibility | scaled residual histories plus bounded outlet/control and level histories |
| model-observable validity | a geometry- and phase-definition-specific mapping from simulated liquid volume/fraction to the physical level-measurement location |

Residual stability alone is not enough: a residual plateau can coexist with a
pool at the wrong level or a slowly drifting pool. Conversely, a pool-level
claim is not supportable if phase balance is persistently unaccounted for.

## Phase boundaries

- Begin by reconstructing the physical level-control boundary, not by adding
  another fixed-pressure or turbulence-variant sweep.
- Retain the full geometry, F11 context, and steady programme initially.
- Do not invent the level setpoint, sensor location, level band, valve curve,
  downstream pressure, controller gains, or actuator limits. Record each as
  `Missing Info` until an authoritative project/plant source is located.
- A controlled **quasi-steady** operating-point strategy may be considered
  after the mechanism is specified: successive bounded steady solves can seek
  a target pool level through an explicitly declared outlet relation. It is
  not a claim to reproduce the real controller's time response.
- A literal controller transient, controller tuning, or a VOF/transient model
  is outside this initial phase unless the human explicitly selects that scope
  after the required control data are known.
- Do not promote a final case as a new parent unless the controlled boundary,
  level metric, numerical evidence, and final paired artifact have all been
  verified.

## Information needed before a runnable setup

1. Normal pool-level setpoint, nominal operating band, and alarm/trip limits.
2. Level instrument measurement location and its relation to the CFD geometry.
3. Brine outlet hardware: control valve, pump, downstream pressure regulation,
   or another mechanism.
4. Valve/line characteristic such as `C_v`, loss curve, nominal opening,
   opening limits, and downstream pressure.
5. Controller type and limits if dynamic behaviour is ultimately required:
   controller mode, sampling/response time, gains or tuning, and saturation.
6. Whether the real pool has a sufficiently identifiable interface for a
   simulated level metric, or whether volume below a stated elevation is the
   appropriate proxy.

## Enough evidence for a phase conclusion

The phase can conclude one of the following only after the control mechanism
and level observable are explicit:

- a controlled steady operating point is feasible in the retained model and
  remains numerically credible over an agreed evidence window;
- the fixed-pressure boundary was a material cause of the prior apparent
  inventory drift, but other limitations still prevent a report-ready state;
- the controlled boundary does not cure the issue, strengthening a bounded
  case for a model-form or other setup-fidelity change; or
- a faithful answer requires a time-dependent controller/model and must return
  to the human for that scope decision.

## Sources

- [03A Stage 5 results](../phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-05/results.md)
- [03A Stage 5 setup](../phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-05/setup.md)
- [current Project state](../../index.md)

# P71A-T4-K-SECOND-ORDER setup draft

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery turbulence-equation numerical sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW numerical sensitivity; current k is first-order |
| Controlled delta | k discretization first-order to second-order upwind |
| Run authorization | Direct human phase-loop invocation on 2026-09-11 |

## Question

Is first-order k acting as a necessary stabilizer, or is it contributing to
the turbulence-field and phase-routing behaviour observed in the baseline?

## Controlled change

Change only the k discretization. Preserve RNG closure, wall treatment, epsilon
discretization, phase-fraction scheme, pressure coupling, URFs, absorber,
boundaries, and DPM state.

The reusable helper's second-order k request is not evidence that second-order
k is the correct baseline; it is the deliberate delta for this packet. Planned
horizon: 500 native iterations after smoke, using the verified T0 parent and
the shared contract in the [family README](../README.md).

## Decision boundary

Only coupled improvement in turbulence stability, continuity, and phase/source
evidence is informative. A first-order endpoint remains a numerical result,
not final physical qualification.

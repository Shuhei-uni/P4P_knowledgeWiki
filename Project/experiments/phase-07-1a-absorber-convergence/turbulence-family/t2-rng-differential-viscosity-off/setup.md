# P71A-T2-RNG-DIFFERENTIAL-VISCOSITY-OFF setup draft

| Field | Value |
| --- | --- |
| Status | PLANNING_DRAFT_NOT_EXECUTABLE |
| Lifecycle role | Discovery RNG-option sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW RNG-option sensitivity |
| Controlled delta | RNG differential viscosity on to off |
| Run authorization | None |

## Question

Is the active RNG differential-viscosity modification contributing to
turbulent-viscosity limiting or destabilizing the lower absorber region?

## Controlled change

Keep RNG k-epsilon, swirl modification, standard wall functions, all numerical
schemes, first-order k treatment, URFs, absorber, boundaries, and DPM state
unchanged. Disable only differential viscosity and read it back.

This is a sensitivity test, not a claim that the low-Reynolds-number
modification is physically inappropriate. Its relevance depends on actual
near-wall resolution. Planned horizon: 500 native iterations after smoke,
using the verified T0 parent and the shared contract in the
[family README](../README.md).

## Decision boundary

Interpret the turbulence response together with phase routing, absorber
delivery, and lower/total inventory evidence.

# P71A-T2-RNG-KATO-LAUNDER setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery turbulence-production sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW turbulence-production sensitivity |
| Controlled delta | Kato-Launder production treatment off to on |
| Run authorization | Direct human phase-loop invocation on 2026-09-11 |

## Question

Does a Kato-Launder production treatment improve response to strong rotation,
stagnation, or recirculation without damaging phase routing?

## Controlled change

Keep RNG k-epsilon, differential viscosity, swirl modification, standard wall
functions, numerical methods, URFs, absorber, boundaries, and DPM state
unchanged. Enable only Kato-Launder production treatment and verify it.

This branch is later than the production-limiter probe because it changes the
turbulence-production response in a more flow-specific way. Planned horizon:
500 native iterations after smoke, using the verified T0 parent and the shared
contract in the [family README](../README.md).

## Decision boundary

Do not interpret improved residuals as success if the absorber removes liquid
from the wrong elevation or vapor routing changes materially.

# P71A-T2-RNG-PRODUCTION-LIMITER setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery RNG-option sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW turbulence-production sensitivity |
| Controlled delta | RNG production limiter off to on |
| Run authorization | Direct human phase-loop invocation on 2026-09-11 |

## Question

Is excessive modeled turbulence production contributing to k/epsilon residual
growth and turbulent-viscosity limiting in the absorber branch?

## Controlled change

Keep RNG k-epsilon, its current differential-viscosity and swirl options,
standard wall functions, and all non-turbulence settings unchanged. Enable only
the production limiter and read it back.

The limiter is a turbulence-model change, not permission to loosen the
turbulent-viscosity ratio limit or residual criteria. Planned horizon: 500
native iterations after smoke, using the verified T0 parent and the shared
evidence/core-figure contract in the [family README](../README.md).

## Decision boundary

Treat this branch as useful only if it reduces instability without hiding a
phase imbalance or changing the absorber interpretation.

# P71A-T1-STANDARD-KEPSILON setup draft

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery closure comparison |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW closure comparison relative to RNG reference |
| Controlled delta | RNG k-epsilon to standard k-epsilon |
| Candidate ID | C2-T1-STD |
| Origin/authority | human-approved-context-only; current human selection |
| Decision gate | G0 / DISCOVERY_DESIGN |
| Run authorization | Phase Loop finite queue only; no direct run from this record |

## Question

Does standard k-epsilon reduce turbulence residual growth or
turbulent-viscosity limiting while preserving absorber delivery, phase routing,
and phase-resolved mass accounting?

## Controlled change

Change only the viscous closure to standard k-epsilon. Read back all
closure-specific options after the change. Do not force RNG-only differential
viscosity or swirl controls onto the standard model. Preserve the baseline wall
treatment, numerical schemes, first-order k treatment, URFs, absorber,
boundaries, and DPM isolation wherever applicable.

Load the active-1000 parent as-is. Do not reinitialize, patch, reset, remesh,
resplit, or alter the restart field. The requested standard closure must be
read back before any iteration.

Planned discovery horizon: 500 native iterations after smoke. Use the same
verified parent as T0 and the shared evidence/core-figure contract in the
[family README](../README.md). The common closure path is in
[closure-path-readback.md](../closure-path-readback.md).

## Decision boundary

A lower turbulence residual alone is insufficient. The branch is informative
only if phase/source evidence remains credible and no upper-zone or vapor
removal artifact is introduced.

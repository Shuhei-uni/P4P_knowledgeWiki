# P71A-T1-REALIZABLE-KEPSILON setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery closure comparison |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW closure comparison relative to RNG reference |
| Controlled delta | RNG k-epsilon to realizable k-epsilon |
| Candidate ID | C2-T1-REAL |
| Origin/authority | human-approved-context-only; current human selection |
| Decision gate | G0 / DISCOVERY_DESIGN |
| Run authorization | Phase Loop finite queue only; no direct run from this record |

## Question

Does realizable k-epsilon produce a more bounded turbulence field in the
separator while preserving bottom-only absorber and vapor-only outlet routing?

## Controlled change

Change only the viscous closure to realizable k-epsilon. Read back the
closure-specific options rather than assuming RNG differential-viscosity or
swirl controls transfer. Preserve baseline wall treatment, numerical schemes,
first-order k treatment, URFs, absorber, boundaries, and DPM isolation wherever
applicable.

Load the active-1000 parent as-is. Do not reinitialize, patch, reset, remesh,
resplit, or alter the restart field. The requested realizable closure must be
read back before any iteration.

Planned discovery horizon: 500 native iterations after smoke. Use the same
verified parent as T0 and the shared evidence/core-figure contract in the
[family README](../README.md). The common closure path is in
[closure-path-readback.md](../closure-path-readback.md).

## Decision boundary

Compare coupled evidence, not only k/epsilon residuals. A candidate that
improves turbulence residuals while worsening phase closure or absorber
delivery is not a successful branch.

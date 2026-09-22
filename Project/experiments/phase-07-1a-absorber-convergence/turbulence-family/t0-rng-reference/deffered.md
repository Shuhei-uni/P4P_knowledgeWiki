# P71A-T0-RNG-REFERENCE setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Reference/discovery control |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Controlled delta | None; exact active reference state |
| Candidate ID | C2-T0 |
| Origin/authority | human-approved-context-only; current human selection |
| Decision gate | G0 / DISCOVERY_DESIGN |
| Run authorization | Phase Loop finite queue only; no direct run from this record |

## Question

What is the reproducible residual, turbulence-limiting, phase-routing, and
absorber-balance behaviour of the exact active baseline against which later
turbulence settings will be compared?

## Reference state and run intent

Use the active settings in the baseline record without normalization or
cleanup. Preserve RNG k-epsilon, RNG differential viscosity on, RNG swirl
modification on, standard wall functions, first-order k, second-order epsilon,
and all current numerical controls.

Planned discovery horizon: 500 native iterations after smoke, with any
extension declared only after the discovery gate. Use the verified parent state
without reinitialization, patching, resetting, remeshing, resplitting, or
restart-field alteration. Do not apply a second initialization to the evolved
active-1000 parent.

The closure path and readback sequence are defined in
[closure-path-readback.md](../closure-path-readback.md).

Required evidence and figures are defined in the
[turbulence-family README](../README.md). This control establishes
comparability; it does not qualify the absorber or prove steady convergence.

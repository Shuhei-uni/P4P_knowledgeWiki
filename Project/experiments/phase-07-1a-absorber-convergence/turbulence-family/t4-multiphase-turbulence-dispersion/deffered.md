# P71A-T4-MULTIPHASE-TURBULENCE-DISPERSION setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery phase-slip/turbulence sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW Mixture slip/turbulence coupling sensitivity |
| Controlled delta | Multiphase turbulence dispersion off to on |
| Run authorization | Direct human phase-loop invocation on 2026-09-11 |

## Question

Does turbulent dispersion in the relative-velocity treatment improve phase
routing and absorber delivery, or does it make the steady residual problem
worse?

## Controlled change

Keep the Mixture model, turbulence closure, wall treatment, numerical methods,
URFs, absorber, boundaries, and DPM state unchanged. Enable only multiphase
turbulence dispersion in relative velocity and read back the phase/slip state.

This is not a pure closure comparison. It is a later coupled
Mixture/turbulence branch because it can alter phase slip and liquid
transport. Planned horizon: 500 native iterations after smoke, using the
verified T0 parent and the shared contract in the [family README](../README.md).

## Decision boundary

A branch that improves liquid delivery but worsens residuals may still be
informative, but it is not a convergence winner. Report routing and stability
separately.

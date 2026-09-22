# P71A-T3-NON-EQUILIBRIUM-WALL-FUNCTIONS setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery near-wall/separation sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW wall-treatment sensitivity |
| Controlled delta | Standard wall functions to non-equilibrium wall functions |
| Run authorization | Direct human phase-loop invocation on 2026-09-11 |

## Question

Does a wall treatment that accounts for non-equilibrium boundary-layer
behaviour improve the coupled solution in recirculating and adverse-pressure-
gradient regions?

## Controlled change and prerequisite

Change only the near-wall treatment. Preserve the selected turbulence closure,
RNG options where applicable, discretization, URFs, absorber, boundaries, and
DPM state. Require evidence of relevant separation/recirculation or strong
pressure gradients and inspect wall-distance/y-plus evidence first.

Planned horizon: 500 native iterations after smoke. Use the verified T0 parent
unless a later gate selects a closure-specific parent. Use the shared contract
in the [family README](../README.md).

## Decision boundary

Do not treat a wall-treatment branch as a closure winner. It answers a
near-wall compatibility question.

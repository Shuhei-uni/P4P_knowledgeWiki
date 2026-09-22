# P71A-T3-SCALABLE-WALL-FUNCTIONS setup draft

> **Status — DEFFERED (2026-09-22):** Deferred after the Server-3 approach
> was paused; retain this setup as planning provenance only.

| Field | Value |
| --- | --- |
| Status | READY_FOR_PHASE_LOOP |
| Lifecycle role | Discovery near-wall sensitivity |
| Phase context | [Phase 7.1A CONTEXT](../../CONTEXT.md) |
| Baseline | [Active Fluent baseline](../../baseline-setup-record.md) |
| Parent identity | P7-E5-CZ-ABSORB-COLD-RAMP11692 active-1000 pair; see [parent reference](../parent-reference.md) |
| Novelty | NEW wall-treatment sensitivity |
| Controlled delta | Standard wall functions to scalable wall functions |
| Run authorization | Direct human phase-loop invocation on 2026-09-11 |

## Question

Is the convergence problem sensitive to treatment of the unresolved or
coarsely resolved near-wall region?

## Controlled change and prerequisite

Change only the wall treatment to scalable wall functions and read back the
near-wall state. Preserve the selected turbulence closure and every other
setting. Inspect wall-distance or y-plus evidence before execution; this is a
near-wall sensitivity, not an automatic physical improvement.

Planned horizon: 500 native iterations after smoke. Use the verified T0 parent
unless a later gate selects a closure-specific parent. Use the shared contract
in the [family README](../README.md).

## Decision boundary

A calmer solution is useful only if it preserves lower-zone phase-2 removal,
upper-zone liquid allowance, and phase-resolved balances.

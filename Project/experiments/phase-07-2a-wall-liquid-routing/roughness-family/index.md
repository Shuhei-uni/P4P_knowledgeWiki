# Phase 7.2A Family R — Wall Roughness

## Scientific purpose

Test whether wall roughness changes near-wall liquid momentum enough to reduce
phase-2 liquid carryover through `steamoutlet`, while EWF remains off.

## Frozen comparison

Every child begins from the exact [7.2A baseline handoff](../baseline-control-handoff.md)
and keeps EWF off, the v2 absorber, full-loading inlets, steady Coupled /
Global-Time-Step numerics, all bottom boundaries as walls, and the same mesh
and materials. The only physical delta is the roughness applied to the
intended wall zones.

| Case | EWF | `k_s` (m) | `C_s` | Purpose | Status |
| --- | --- | ---: | ---: | --- | --- |
| `R0` | off | `0` | — | smooth-wall control copy | selected control |
| `R1` | off | `5e-5` | `0.5` | clean-steel-scale diagnostic | selected |
| `R2` | off | `2e-4` | `0.5` | moderate roughness diagnostic | selected |
| `R3` | off | `5e-4` | `0.5` | strong roughness diagnostic | selected |
| `R4` | off | `1e-3` | `0.5` | aggressive extension if R1–R3 show a coherent unresolved trend | optional |

## Selection evidence

The primary response is phase-2 `steamoutlet` carryover, interpreted together
with outer-wall liquid vertical velocity, lower-region liquid delivery,
inventory slope, absorber/source tracking, phase-resolved closure, and solver
health. A monotonic response is useful but not required; a flat response is a
valid negative result if the runs are numerically comparable.

Roughness must be applied only to the named wall zones and read back before
solving. If Fluent cannot expose a clean wall-only `k_s`/`C_s` delta, record a
capability block rather than emulating roughness with a different model,
outlet, source, mesh, or solver change.

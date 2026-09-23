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
| `R0` | off | `0` | `0.5` | smooth-wall control copy | complete; tail carryover `-24.3715 kg/s` |
| `R1` | off | `5e-5` | `0.5` | clean-steel-scale diagnostic | complete; carryover magnitude `+21.21%` vs R0 |
| `R2` | off | `2e-4` | `0.5` | moderate roughness diagnostic | complete; carryover magnitude `+15.20%` vs R0 |
| `R3` | off | `5e-4` | `0.5` | strong roughness diagnostic | complete; carryover magnitude `+1.15%` vs R0 |
| `R4` | off | `1e-3` | `0.5` | human-requested rougher extension | complete; carryover magnitude `-9.79%` vs R0; oscillatory |
| `R5` | off | `2e-3` | `0.5` | human-requested rougher extension | complete; carryover magnitude `-20.58%` vs R0; major liquid-inventory depletion |
| `R6` | off | `4e-3` | `0.5` | second doubled-roughness extension | running; see [setup](extension-r6-r7-setup.md) |
| `R7` | off | `8e-3` | `0.5` | second doubled-roughness extension | queued; see [setup](extension-r6-r7-setup.md) |

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

## Result

The original six-case screen is complete, and R6–R7 are now in progress. The original R0–R3 negative outlet screen was
superseded by the explicit [R4–R5 extension](extension-r4-r5-setup.md). Stronger
roughness reduced modeled outlet flux, but neither run establishes improved
separation: R4 is oscillatory and R5 depleted much of its liquid inventory. See
[results.md](results.md) for matched-window statistics, execution receipts,
figures, solver-health evidence, and claim limits.

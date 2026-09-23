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
| `R6` | off | `4e-3` | `0.5` | second doubled-roughness extension | complete; carryover magnitude `-38.38%` vs R0; `183.5 kg` domain-liquid loss |
| `R7` | off | `8e-3` | `0.5` | second doubled-roughness extension | complete; carryover magnitude `-44.09%` vs R0; `187.1 kg` domain-liquid loss |
| `R8` | off | `5e-4` | `0.75` | R3-height roughness-constant sensitivity | complete |
| `R9` | off | `5e-4` | `1.0` | R3-height roughness-constant sensitivity | complete |
| `R10` | off | `2e-3` | `0.75` | R5-height roughness-constant sensitivity | complete |
| `R11` | off | `2e-3` | `1.0` | R5-height roughness-constant sensitivity | complete |

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

R8–R11 are the human-selected roughness-constant sensitivity extension; see [extension-r8-r11-setup.md](extension-r8-r11-setup.md). All four runs passed the terminal artifact checks; the matched comparison is in [results.md](results.md).

The R0–R11 branch is complete. The original R0–R3 negative outlet screen was
extended by [R4–R5](extension-r4-r5-setup.md), [R6–R7](extension-r6-r7-setup.md)
roughness-height cases, and the [R8–R11 roughness-constant sensitivity](extension-r8-r11-setup.md). Lower outlet
flux at the larger settings does not establish improved separation: R4 and R9
are oscillatory, and R5–R7 and R10–R11 depleted much of the domain liquid
inventory. See
[results.md](results.md) for matched-window statistics, execution receipts,
figures, solver-health evidence, and claim limits.

# Phase 7.1A — Family E: Eulerian Wall Film

## Status and assignment

**Human-selected discovery family — 2026-09-22.** Run this family on
**Server 3**, independently from the roughness stream on Server 1. The [shared
v2 mechanism-screen contract](../v2-mechanism-family-screen/index.md) owns the
parent, ramp, frozen scaffold, and common evidence requirements.

No child is executed merely because this planning record exists.

## Family question

> Does explicitly converting near-wall liquid into a wall-attached draining
> film produce a routing behaviour that the bulk v2 Mixture field does not?

The decisive comparison is `C0/E0` versus `E2`: smooth wall, no EWF against
smooth wall with phase accretion enabled. Wall roughness is zero throughout
this family so any improvement is not confounded with added wall shear.

## Case matrix

All rows use the same v2 parent, the common first-2,000-iteration inlet ramp,
`k_s = 0`, and no roughness constant effect.

| Case | EWF treatment | Roughness | Purpose | Status |
| --- | --- | ---: | --- | --- |
| `C0` / `E0` | off | `0` | Shared smooth-wall, no-EWF control | selected control |
| `E1` | on, basic wall-film model | `0` | Isolate the basic EWF effect | selected |
| `E2` | on + phase accretion | `0` | Allow bulk liquid to enter the wall film | selected, primary comparison |
| `E3` | E2 + one separately named, relevant film-physics option | `0` | Test whether the remaining film behaviour matters | capability-gated optional extension |

`E3` is deliberately capability-gated. Before any mutation, the execution
record must name the exact Fluent 2025 R2 film option(s) meant by “relevant
film physics” and prove that they are available and distinct from phase
accretion. No arbitrary bundle of wetting, drag, entrainment, or coupling
options may be added under the E3 label. If no single defensible additional
option is available, record E3 as not run rather than widening the family.

The EWF setup must also verify how film mass, film flow toward the bottom, and
film-to-bulk transfer are exposed in the live Fluent tree. Missing a film
monitor is an evidence gap to repair before solving, not permission to infer
film drainage from a global liquid balance.

## Required interpretation

Track the shared phase/source and balance evidence, plus:

- wall-film mass/inventory;
- film mass flow toward the bottom, if exposed;
- bulk-to-film accretion and film-to-bulk transfer, if exposed;
- outer-wall liquid velocity and lower-vessel inventory; and
- steam leakage and liquid carryover.

The useful positive result is not merely more total liquid removal. It is
evidence that liquid leaves the bulk near-wall trajectory, enters the explicit
film, and moves downward while vapor remains auditable. A global inventory
decrease without this phase-resolved transfer evidence is inconclusive.

## Rejection and claim limits

Reject a comparison if EWF changes roughness, inlet schedule, absorber law,
bottom boundary, solver scaffold, or initialization. Reject any apparent EWF
success if film transfer or vapor routing cannot be accounted for. Even a
successful E2/E3 screen establishes only a numerical mechanism result inside
this model; it does not validate a physical wall-film closure or plant
performance.


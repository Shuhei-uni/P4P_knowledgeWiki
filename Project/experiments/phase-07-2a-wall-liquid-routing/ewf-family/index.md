# Phase 7.2A Family E — Eulerian Wall Film

## Scientific purpose

Test whether explicit wall-film formation captures liquid that otherwise
remains in the bulk near-wall trajectory and carries to `steamoutlet`.

## Frozen comparison

Every child begins from the exact [7.2A baseline handoff](../baseline-control-handoff.md)
with `k_s=0`. The mesh, inlet state, absorber, steady Coupled /
Global-Time-Step treatment, bottom walls, materials, and all non-film settings
remain fixed. The first screen does not combine EWF with roughness.

| Case | EWF treatment | Roughness | Purpose | Status |
| --- | --- | ---: | --- | --- |
| `E0` | off | `0` | smooth no-film control copy | selected control |
| `E1` | basic EWF model | `0` | isolate basic film response | selected |
| `E2` | EWF plus phase accretion | `0` | allow bulk liquid to enter the film | selected, primary |
| `E3` | E2 plus one separately named film option | `0` | capability-gated extension | optional |

## Selection evidence

The positive mechanism signature requires more than lower global liquid
inventory. The report must show film mass/inventory, bulk-to-film accretion,
film-to-bulk transfer, and film movement toward the lower region wherever the
live Fluent model exposes those quantities, together with phase-2
`steamoutlet` carryover, vapor routing, closure, and numerical health.

Before E1/E2 mutation, the child must identify the live Fluent EWF control
names and prove their readback and persistence. Before E3, the additional
option must be named explicitly and shown to be distinct from phase accretion;
an arbitrary bundle of wetting, drag, entrainment, or coupling controls is not
allowed under the E3 label. If film transfer or flow cannot be instrumented,
record the evidence gap and do not infer drainage from inventory alone.

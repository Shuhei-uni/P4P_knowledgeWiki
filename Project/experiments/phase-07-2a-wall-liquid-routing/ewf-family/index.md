# Phase 7.2A Family E — Eulerian Wall Film

## Scientific purpose

Test whether explicit wall-film formation captures liquid that otherwise
remains in the bulk near-wall trajectory and carries to `steamoutlet`.

## Current execution status

**Partial completed screen / E2 and E2.1 numerical blocks — 2026-09-23.** On
`student`, E0, E1, and the human-selected E3 reached native 8586 with verified
final pairs and histories. E2 and E2.1 both reached their configured maximum
film thickness at native 5650 and failed with an FPE at 5653 before the first
250-iteration checkpoint. E2.1 has recovered native report files sampled at
every iteration through 5652. See the [current result](results.md) before
using any historical Server-3 preflight record.

**E2.1 selected by the human — 2026-09-23.** Test the E2 phase-accretion
configuration with only the maximum film-thickness limit raised from `0.01 m`
to `0.3 m`, and retain per-iteration film-thickness/mass monitoring. This is a
numerical-limit sensitivity, not a physical target thickness. The
[setup contract](e2.1/setup.md) defines the parent, invariants, run horizon,
and evidence. It was built and saved/reopened at native 5586 with the `0.3 m`
readback. The continuation blocked at 5653; recovered reports show the cap
was reached at 5650, followed by runaway film values and FPE. See the [E2.1
result](results.md#e21--maximum-thickness-sensitivity--2026-09-23).

**E2.2 numerical recovery — 2026-09-23.** Following E2.1's cap hit and FPE,
test the recorded sub-iteration recovery: retain the `0.3 m` cap and change
only EWF film sub-iterations from 5 to 20. The [setup contract](e2.2/setup.md)
defines the fresh parent, run horizon, and per-iteration report evidence.

## Frozen comparison

Every child begins independently from the exact [7.2A baseline handoff](../baseline-control-handoff.md).
E0–E2.1 keep `k_s=0`; E3 is the explicitly selected E1-plus-R3
roughness interaction. The mesh, inlet state, absorber, steady Coupled /
Global-Time-Step treatment, bottom walls, materials, and all non-film settings
remain fixed except for E3's named wall-roughness delta.

| Case | EWF treatment | Roughness | Purpose | Status |
| --- | --- | ---: | --- | --- |
| `E0` | off | `0` | smooth no-film control copy | complete |
| `E1` | basic EWF model | `0` | isolate basic film response | complete; film histories zero |
| `E2` | EWF plus phase accretion | `0` | allow bulk liquid to enter the film | numerical block at native 5653; recovery also failed |
| `E3` | basic EWF as in E1 | `5e-4 m`, `C_s=0.5` as in R3 | test the EWF–roughness interaction against E1 and R3 | complete; film histories zero |
| `E2.1` | EWF plus phase accretion, max thickness `0.3 m` | `0` | test sensitivity to E2's `0.01 m` thickness-limit event | cap reached at 5650; FPE at 5653; every-iteration reports recovered |
| `E2.2` | EWF plus phase accretion, 20 film sub-iterations, max thickness `0.3 m` | `0` | test a numerical recovery at fixed E2.1 thickness limit | built/reopened at 5586; running with native report files at every iteration |

## Selection evidence

The positive mechanism signature requires more than lower global liquid
inventory. The report must show film mass/inventory, bulk-to-film accretion,
film-to-bulk transfer, and film movement toward the lower region wherever the
live Fluent model exposes those quantities, together with phase-2
`steamoutlet` carryover, vapor routing, closure, and numerical health.

Before E1/E2/E2.1/E3 mutation, the child must identify the live Fluent EWF control
names and prove their readback and persistence. E3 must reproduce E1's basic
film settings (phase accretion off) and R3's wall-zone roughness scope,
`k_s=5e-4 m`, and `C_s=0.5`, with no other new film option. Compare E3 with
E1 to isolate the roughness effect under basic EWF, and with R3 to inspect
the EWF effect under R3 roughness; E0 anchors the two-factor comparison.
If film transfer or flow cannot be instrumented,
record the evidence gap and do not infer drainage from inventory alone.

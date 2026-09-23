# Phase 7.2A Family E — Eulerian Wall Film

## Scientific purpose

Test whether explicit wall-film formation captures liquid that otherwise
remains in the bulk near-wall trajectory and carries to `steamoutlet`.

## Current execution status

**Partial completed screen / E2 numerical block — 2026-09-23.** On `student`,
E0, E1, and the human-selected E3 reached the requested native 8586 endpoint
with verified final pairs and histories. E2 phase accretion was built and
started but diverged before the first checkpoint; a smaller-initial-film-step
recovery reproduced the early FPE and left the student endpoint unresponsive
to MCP inspection. See the [current result](results.md) before using any
historical Server-3 preflight record.

## Frozen comparison

Every child begins independently from the exact [7.2A baseline handoff](../baseline-control-handoff.md).
E0–E2 keep `k_s=0`; E3 is the explicitly selected E1-plus-R3
roughness interaction. The mesh, inlet state, absorber, steady Coupled /
Global-Time-Step treatment, bottom walls, materials, and all non-film settings
remain fixed except for E3's named wall-roughness delta.

| Case | EWF treatment | Roughness | Purpose | Status |
| --- | --- | ---: | --- | --- |
| `E0` | off | `0` | smooth no-film control copy | complete |
| `E1` | basic EWF model | `0` | isolate basic film response | complete; film histories zero |
| `E2` | EWF plus phase accretion | `0` | allow bulk liquid to enter the film | numerical block at native 5653; recovery also failed |
| `E3` | basic EWF as in E1 | `5e-4 m`, `C_s=0.5` as in R3 | test the EWF–roughness interaction against E1 and R3 | complete; film histories zero |

## Selection evidence

The positive mechanism signature requires more than lower global liquid
inventory. The report must show film mass/inventory, bulk-to-film accretion,
film-to-bulk transfer, and film movement toward the lower region wherever the
live Fluent model exposes those quantities, together with phase-2
`steamoutlet` carryover, vapor routing, closure, and numerical health.

Before E1/E2/E3 mutation, the child must identify the live Fluent EWF control
names and prove their readback and persistence. E3 must reproduce E1's basic
film settings (phase accretion off) and R3's wall-zone roughness scope,
`k_s=5e-4 m`, and `C_s=0.5`, with no other new film option. Compare E3 with
E1 to isolate the roughness effect under basic EWF, and with R3 to inspect
the EWF effect under R3 roughness; E0 anchors the two-factor comparison.
If film transfer or flow cannot be instrumented,
record the evidence gap and do not infer drainage from inventory alone.

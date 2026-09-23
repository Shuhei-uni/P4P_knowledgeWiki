# Phase 7.2A Family E — Eulerian Wall Film

## Scientific purpose

Test whether explicit wall-film formation captures liquid that otherwise
remains in the bulk near-wall trajectory and carries to `steamoutlet`.

## Current execution status

**Partial completed screen; E2 numerical blocks remain — 2026-09-23.** On
`student`, E0, E1, E3, and E2.7 reached native 8586 with verified final pairs
and histories. E2 and E2.1–E2.6 reached their configured maximum film
thickness and failed with FPE (E2.6 cap at 5760/FPE at 5765). E2.7 retained
Phase Accretion and EWF Coupled Solution but disabled film-wall Flow Momentum
Coupling; it completed through 8586 without cap or FPE, with all 26 native
Report Files recovered at every iteration. This is a run-specific numerical
response and does not establish convergence or a physical carryover benefit.
See the [current result](results.md).

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
defines the fresh parent, run horizon, and per-iteration report evidence. This
also hit the cap at 5650 and failed with FPE at 5653; raising sub-iterations
did not stabilize the run.

**E2.3 numerical recovery — 2026-09-23.** Retain E2.2's `0.3 m` cap and 20
film sub-iterations, and reduce only the initial film time step from `1e-4 s`
to `1e-6 s` to test whether a smaller initial film step changes the cap/FPE
sequence. See [setup contract](e2.3/setup.md).

**E2.4 Courant sensitivity — 2026-09-23.** Repeat E2.1 independently and
reduce only the adaptive EWF Courant number from `0.25` to `0.05`. Native
every-iteration reports and EWF `h/u/v` sub-iteration residual output were
captured. The thickness cap was reached at 5737 and the FPE occurred at 5742,
delaying (but not preventing) the E2.1 cap/FPE sequence. See the [E2.4
result](results.md#e24--lower-adaptive-film-courant-number--2026-09-23).

**E2.5 fixed film time step — 2026-09-23.** Repeat E2.1 independently with
adaptive stepping OFF and Fluent's fixed EWF timestep `1e-6 s`. The maximum
thickness cap was reached at 6018 and FPE occurred at 6022. The result and
every-iteration reports are in the [E2.5 result](results.md#e25--fixed-ewf-film-time-step--2026-09-23).
**E2.6 combined controls — 2026-09-23.** The user selected a combined test of
10 film sub-iterations, Courant `0.05`, fixed timestep `1e-5 s`, and EWF
Coupled Solution ON. It reached the `0.3 m` cap at 5760 and failed with FPE at
5765. Fixed stepping makes the Courant value inactive. See [E2.6 setup](e2.6/setup.md).
**E2.7 Flow Momentum Coupling off — 2026-09-23.** Repeating E2.6 from the
same native-5586 parent with Phase Accretion and EWF Coupled Solution ON, but
film-wall Flow Momentum Coupling OFF, completed through 8586 with no cap or
FPE. Maximum thickness was `0.000331 m`; film mass reached `3.111 kg` and was
still increasing in the final window. The shared 5760 response differed
strongly from E2.6, but moving inventory and absorber under-tracking limit
interpretation. See the [E2.7 result](results.md#e27--flow-momentum-coupling-off--2026-09-23).

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
| `E2.2` | EWF plus phase accretion, 20 film sub-iterations, max thickness `0.3 m` | `0` | test a numerical recovery at fixed E2.1 thickness limit | cap at 5650; FPE at 5653; every-iteration reports recovered |
| `E2.3` | E2.2 plus `1e-6 s` initial film time step | `0` | test whether a smaller initial film step delays instability at the same cap | cap at 5647; FPE at 5653; every-iteration reports recovered; stopped |
| `E2.4` | E2.1 with adaptive film Courant `0.05` instead of `0.25` | `0` | test lower adaptive film Courant independently | cap at 5737; FPE at 5742; every-iteration reports and EWF residual transcript recovered |
| `E2.5` | E2.1 with adaptive stepping off and fixed film timestep `1e-6 s` | `0` | test a fixed small EWF time step independently | cap at 6018; FPE at 6022; every-iteration reports and EWF residual transcript recovered |
| `E2.6` | E2.1 with 10 sub-iterations, Courant `0.05`, fixed timestep `1e-5 s`, and EWF Coupled Solution ON | `0` | test the user's combined numerical/coupling setting | cap at 5760; FPE at 5765; 26 every-iteration native Report Files recovered through 5764 |
| `E2.7` | E2.6 with film-wall Flow Momentum Coupling OFF; phase accretion retained | `0` | test one-way flow-to-film momentum interaction with phase accretion active | complete to 8586; max thickness `0.000331 m`; no cap/FPE; response not qualified as converged |

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

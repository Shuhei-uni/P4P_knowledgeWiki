# Phase 7.2A Family E — Eulerian Wall Film

## Scientific purpose

Test whether explicit wall-film formation captures liquid that otherwise
remains in the bulk near-wall trajectory and carries to `steamoutlet`.

## Current execution status

**Partial completed screen; E2 numerical blocks remain — updated 2026-09-27.** On
`student`, E0, E1, E3, E2.7, E2.81, and the independent fixed-step follow-on
cases E2.82–E2.84 reached native 8586 with paired final data and histories.
E2 and E2.1–E2.6 reached their configured maximum film thickness and failed
with FPE (E2.6 cap at 5760/FPE at 5765). E2.7 completed without cap or FPE.
E2.81 completed its adaptive horizon but remained numerically unqualified.
Among the new fixed-step candidates, E2.82 had much smaller excursions than
E2.81 but still showed a late Courant/speed spike; E2.83 and E2.84 reached the
0.3 m thickness cap and diverged. At matched 0.03 s film time E2.82's film
mass was only 1.1% above E2.7. None establishes stable transport, convergence,
or physical carryover benefit. See the [fixed-step comparison](results.md#e282e284--fixed-ewf-timestep-screen--2026-09-27)
and [current results](results.md).

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

**E4 direct-film inlet and fast adaptive screen — 2026-09-25.** A new
exploratory branch was built from the verified native-5586 baseline, but the
generated build used the EWF Initial Condition User Source Terms instead of
the requested EWF Boundary Condition film-flux fields. The fast controls were
read back, but the run reached the `0.3 m` cap, extreme CFL/velocity, and
absorber under-tracking by native 5871; only the native-5750 checkpoint was
paired. This is an implementation/solver failure and does not test direct
film-boundary injection. See the [E4 setup and run record](e4-direct-film-inlet/setup.md)
and [E4 result](results.md#e4--direct-ewf-film-feed-attempt--2026-09-25).

**E2.8 adaptive speed screen — 2026-09-26.** Starting from the same native-5586
parent as E2.7, the aggressive adaptive profile reached an E2.7-like film
state by native 7000 after 1,414 additional iterations, then became unstable
and was stopped at 7318. Recovery from the preserved native-7000 pair used
E2.7's fixed-step controls and completed to 8586. The selected trajectory is
3,000 additional iterations, with 318 discarded divergent iterations also
executed. It is not a stable completion of the fast profile. See the
[E2.8 setup and execution record](e2.8/setup.md) and [E2.8 result](results.md#e28--adaptive-speed-screen-with-fixed-step-recovery--2026-09-26).

**E2.81 slightly tightened adaptive follow-up — 2026-09-26.** From the same
native-5586 parent, set maximum film Courant to `0.4`, increase factor to
`1.5`, maximum sub-iterations to `4`, and stop residual to `5e-4`; adaptive
stepping remained on. E2.81 reached a close E2.7-like film response at native
7196 after 1,610 iterations and completed the full 3,000-iteration horizon at
8586 without fatal solver flags. The terminal response had elevated film
speed and maximum thickness, and 2,998 updates reached the sub-iteration cap,
so this is not a converged/stable-film claim. See the [E2.81 setup and
result](e2.81/setup.md) and [analysis](results.md#e281--slightly-tightened-adaptive-ewf--2026-09-26).

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
| `E2.8` | E2.7 plus aggressive adaptive stepping and reduced film sub-iteration allowance; fixed-step recovery after adaptive divergence | `0` | screen whether E2.7-like film response can be reached with fewer iterations | fast branch approached E2.7 by native 7000 after 1,414 iterations, then diverged; recovered to 8586 on a hybrid trajectory; not a stable fast-profile result |
| `E2.81` | E2.8 adaptive profile slightly tightened: Courant `0.4`, increase `1.5`, four sub-iterations, stop `5e-4` | `0` | retain an E2.7-like response at lower iteration count while surviving E2.8's risk window | close E2.7-like state at native 7196 after 1,610 iterations; full horizon completed, but late speed/thickness and residual cap frequency leave numerical response unqualified |

## Fixed-timestep follow-on screen

E2.82–E2.84 are independent children of the same verified native-5586 parent.
Each completed 3,000 additional iterations with adaptive stepping off and
only the fixed film timestep changed from E2.7. The [matched-time comparison
and numerical-health results](results.md#e282e284--fixed-ewf-timestep-screen--2026-09-27)
include the full 0.03 s comparison and later excursions.

| Case | Fixed film timestep | Result |
| --- | ---: | --- |
| `E2.82` | `1.25e-5 s` | Best bounded candidate: at 0.03 s, film mass was 3.144 kg versus E2.7's 3.111 kg; late peak CFL 3.31 and speed 4,170 m/s still prevent calling it stable. |
| `E2.83` | `1.50e-5 s` | Thickness cap first hit at native 7800; peak CFL `2.03e8`, with grossly nonphysical film values. |
| `E2.84` | `1.75e-5 s` | Thickness cap first hit at native 7473; peak CFL `2.60e8`, with grossly nonphysical film values. |

The [phase-2 `steamoutlet` flux overlay](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/phase2-steamoutlet-flux-e2.7-to-e2.84.svg)
also compares E2.7, E2.8, and E2.81–E2.84 over native 5586–8586; its selected
trajectory and sign conventions are recorded in [results](results.md).

## Exploratory branches outside the frozen comparison

| Case | Controlled change | Status |
| --- | --- | --- |
| `E4` | direct EWF inlet attempt; aggressive adaptive stepping | stopped at 5871 after cap/velocity/CFL divergence; used Initial Condition User Source Terms, not the intended Boundary Condition; not a hypothesis test |

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

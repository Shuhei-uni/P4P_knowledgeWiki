# Phase 7.1A — Family N: v2 numerical improvement

## Status and role

**Human-selected next discovery family — 2026-09-22.** This family is the
immediate numerical follow-up to the verified v2 baseline. It is deliberately
separate from the roughness and Eulerian Wall Film mechanism families: those
families change the liquid-transport mechanism, whereas Family N changes only
the steady solution treatment used to advance the same v2 absorber problem.

The family is discovery-only until a branch shows a bounded, auditable late
trajectory. No branch is authorized to claim a physical absorber, plant
drainage, or Phase 08 readiness.

## Family question

> Can a steady pressure-based Coupled solver with Coupled-compatible Global
> Time Step pseudo-time treatment make the v2 absorber trajectory more bounded
> or more durable than the SIMPLE reference, while preserving the phase-2-only
> source accounting and phase routing?

The central comparison is numerical: same v2 parent, mesh, absorber law,
initial field, and inlet-development history; only the solver package changes.
Pseudo-time is a numerical continuation device and must never be interpreted as
physical time.

## Staged family queue

| Case | Controlled change | Purpose | Status |
| --- | --- | --- | --- |
| `N0` | Existing v2 SIMPLE reference and 0.25→1.00 loading history | Comparison control; use the authoritative v2 result rather than mutating the prepared parent | complete with limits |
| `N1` | `SIMPLE` → `Coupled` plus steady `Global Time Step`, automatic pseudo-timestep selection initially | Test the combined solver package recommended for the source-dominated absorber state | next |
| `N2` | One conservative pseudo-time policy change selected from N1 readback, such as a verified initial/cap/growth control | Determine whether N1 is sensitive to pseudo-time aggressiveness | gated by N1 |
| `N3` | One additional numerical control selected from N1/N2 evidence, such as a single relaxation or discretization change | Continue the smallest evidence-driven improvement sequence | gated by prior evidence |

N1 is the only branch specified for immediate preparation. N2 and N3 must not
be filled with guessed values before the live Fluent tree exposes the supported
controls and N1 shows which failure mode needs changing. Every child starts from
the same prepared v2 pair and common loading rule; a later child is not silently
continued from a previous child’s field.

The first N1 preflight was attempted read-only on 2026-09-22. The recorded
`student` endpoint was unavailable, and the reachable server-1 endpoint did not
contain the exact v2 prepared parent. N1 therefore remains unrun; see its
[preflight result](n1-coupled-global-pseudo-time/results.md). This access block
does not weaken or falsify the solver hypothesis.

## Frozen comparison scaffold

Unless a later family row explicitly names its single delta, preserve:

- the verified `Separator-purnanto-60k.msh.h5` mesh and `60,964` fluid-cell
  topology;
- steady pressure-based Mixture with implicit dispersed phase treatment,
  phase 1 vapor and phase 2 liquid, and the recorded RNG k-epsilon settings;
- the phase-2-only v2 virtual-outlet source, matching liquid momentum removal,
  shared `k`/epsilon removal, and zero direct phase-1 mass source;
- fresh Hybrid Initialization from the prepared parent, with no patch, pool,
  sink-off warm-up, or restart-field alteration;
- `liquidinlet`, `steaminlet`, `steamoutlet`, and all bottom boundaries as
  recorded in the v2 baseline; no new outlet or wall-film model;
- PRESTO!, Green-Gauss node-based gradients, existing discretization,
  under-relaxation, residual definitions, DPM state, and energy/species-off
  state unless a later branch declares one exact delta;
- the common first-2,000-iteration inlet schedule: start at `0.25` of
  `116.92 kg/s` liquid and `80.69 kg/s` steam, ramp linearly to the final
  targets, and update every `10` iterations.

`Coupled with Volume Fractions` is not part of N1. The live parent’s slip/drift
and volume-fraction treatment must be read back; enabling an unavailable or
incompatible volume-fraction coupling option would be a different experiment.

## Common evidence contract

Every branch must preserve native-iteration histories and paired checkpoints,
and report at minimum:

1. exact parent identity and pre/post-mutation solver readback;
2. coupling, Global Time Step, automatic/fixed pseudo-time policy, and any
   available initial/max/growth/Courant controls;
3. inlet commands and realized liquid/steam phase fluxes;
4. `P71V2Command`, named removal, native applied phase-2 source, and zero
   phase-1 source;
5. lower-zone available liquid and lower-zone inventory;
6. whole-separator liquid mass/volume and phase-1 vapor inventory;
7. mixture, vapor, and liquid fluxes at `steamoutlet`;
8. source-inclusive phase and mixture closure, including storage while the
   trajectory is nonstationary;
9. residuals, pressure-outlet reverse flow, AMG/FPE/non-finite warnings, and
   turbulent-viscosity limiting; and
10. wall-clock cost or solver-time evidence sufficient to compare expensive
   Coupled iterations with the SIMPLE reference.

## Throughout-run monitoring schedule

The run is monitored as a trajectory, not judged from the final residual
vector. The control loop, checkpoint package, and event log have distinct
purposes.

### Every 10-iteration control block

Record one native-iteration row for each completed control block containing:

| Monitor group | Required quantities | Why it is monitored |
| --- | --- | --- |
| Loading | scheduled liquid/steam commands and realized liquid/steam inlet phase fluxes | Confirms that the declared `0.25 -> 1.00` loading ramp is actually applied and that the two inlets remain on the intended path |
| Absorber command | `P71V2Command`, named-expression removal, native applied phase-2 source, absolute and relative command-minus-applied error | Separates commanded throughput from realized removal and identifies lower-zone starvation |
| Phase exclusion | direct phase-1 source, direct vapor removal, and any nonzero phase-1 absorber contribution | Verifies that N1 has not changed the physical absorber interpretation |
| Lower liquid | lower-zone available liquid volume, lower-zone liquid mass/volume, and lower-zone phase-2 fraction | Shows whether the source is liquid-starved or receiving a developed liquid field |
| Global inventory | total liquid mass/volume, phase-1 vapor inventory, and their block-to-block slopes | Detects accumulation or depletion that residuals can hide |
| Routing | mixture, phase-1, and phase-2 fluxes at `steamoutlet`; inlet/outlet phase balance; pressure-outlet reverse-flow face count or available equivalent | Tests phase routing and distinguishes liquid removal from vapor leakage or reverse recirculation |
| Closure | phase-resolved and mixture source-inclusive imbalance, including storage term while nonstationary | Prevents a global sum from masking a phase-specific accounting failure |
| Solver health | continuity, x/y/z momentum, `k`, epsilon, and phase-fraction residuals; AMG/FPE/non-finite warnings; turbulent-viscosity limiting | Captures stability, not just endpoint residual magnitude |
| Cost | elapsed wall-clock time and solver time per block, if exposed | Tests whether Coupled improves endurance at an unacceptable computational cost |

The raw native histories must retain every block row. Derived slopes,
relative errors, and warning flags may be added as analysis fields but must not
replace the raw monitor values.

### At active iterations 0, 500, 1,000, 1,500, and 2,000

At each checkpoint, preserve a paired case/data artifact and a readback package
containing:

- parent/child identity and solver settings;
- current ramp multiplier and realized inlet fluxes;
- all absorber, inventory, routing, closure, residual, warning, and cost
  monitors above;
- a phase-2 volume-fraction field and velocity/pressure field suitable for
  checking whether the trajectory is physically and numerically recognizable;
- turbulent-viscosity limiting or equivalent turbulence-health evidence; and
- the exact native iteration coordinate used by every history.

The active-0 package is the post-reopen parent reference, not a solved result.
The 500-iteration packages show early development, 1,000 and 1,500 show the
transition toward base flow, and 2,000 is the first late-ramp decision point.

### Event-triggered monitoring

If the solver reports AMG failure, FPE, a non-finite field, a fatal node/Fluent
failure, unexpected source scope, or a phase/source accounting discontinuity:

1. record the first event native iteration and the last valid monitor row;
2. preserve the last valid paired checkpoint and event transcript/readback;
3. record whether the failure occurred during a ramp update or solve block; and
4. do not silently change pseudo-time, relaxation, outlet, source, or
   initialization settings under the N1 label.

An event is part of the result. Recovery may preserve the endpoint under the
phase-loop authority, but a changed solver setting becomes a separately named
child rather than an unrecorded continuation.

### Decision windows

Compare N1 against N0 over the same native windows: `0–500`, `500–1,000`,
`1,000–1,500`, and `1,500–2,000`. The primary late-window comparison uses
`1,500–2,000` and includes:

- slope and variability of total liquid and lower-zone liquid;
- command-to-applied removal error;
- source-inclusive phase and mixture closure;
- phase-resolved steam-outlet routing and reverse flow;
- residual growth or boundedness and turbulence-viscosity limiting;
- event-free endurance; and
- wall-clock cost per native iteration.

N1 is useful only when these quantities are interpreted together. A lower
residual with growing inventory, worsening closure, increased liquid carryover,
or earlier numerical failure is not an improvement.

## Core figure plan

1. **Numerical trajectory:** native iteration versus continuity, momentum,
   `k`, epsilon, and phase-fraction residuals, with warning/limiter markers and
   the N0 reference on the same loading history.
2. **Absorber and balances:** command, realized source, phase-resolved inlet/
   outlet fluxes, source-inclusive closure, lower-zone availability, total
   liquid inventory, and vapor inventory.
3. **Routing and cost:** phase-resolved `steamoutlet` flux, reverse-flow
   activity, lower-zone liquid development, and wall-clock/iteration cost.

These figures are discovery evidence. Endpoint residuals alone do not decide
the family because the v2 reference already shows finite residuals alongside
inventory growth and reverse flow.

## Decision rule

- **Promote to deeper numerical qualification:** N1 has a clearly improved
  late-window trajectory relative to N0—less residual growth and inventory
  drift or longer bounded endurance—while source tracking, phase-1 source
  exclusion, phase routing, and source-inclusive balances remain auditable.
- **Continue with a smaller tuning probe:** N1 survives longer or is calmer but
  remains nonstationary; use N1 diagnostics to define exactly one N2 control.
- **Reject the solver package:** N1 produces earlier AMG/FPE/non-finite failure,
  materially worse routing, or no useful change after a verified run.
- **Treat as ambiguous:** residuals improve but inventory, reverse flow, or
  phase/source closure cannot be judged; repair instrumentation before any
  interpretation.

## Claim limit

The strongest immediate claim is only whether the verified Coupled + Global
Time Step package improves, worsens, or merely extends the numerical endurance
of the v2 absorber under the declared loading history. It cannot isolate
pseudo-time from coupling within N1, establish a generally converged steady
branch, or validate physical drainage.

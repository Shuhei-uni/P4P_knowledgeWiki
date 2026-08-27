# Intended vs Actual: Setup 07 Live FFF 1-2

## Scope

This report compares:

- the `intended inherited setup` defined by the setup-report chain
- the `actual live Fluent setup` exported from `FFF.1-2.cas.h5` and `FFF.1-2-02541.dat.h5`

Project records used for the intended setup:

1. [Purnanto reference](../../../../Project/experiments/purnanto-00-reference-spiral-boc/setup.md)
2. [Mixed wet-half velocity-inlet record](../../../../Project/experiments/purnanto-03-mixed-wet-half-velocity-inlet/setup.md)
3. [Mixed wet-half actual-area record](../../../../Project/experiments/purnanto-04-mixed-wet-half-actual-area/setup.md)
4. [Pure-phase actual-area record](../../../../Project/experiments/purnanto-07-pure-phase-actual-area/setup.md)

Interpretation rule:

- `Intended` means the setup you likely wanted from the report chain.
- `Actual` means what the exported Fluent case currently contains.
- Where they differ, treat the difference as a likely drift or human-error candidate unless later evidence shows it was an intentional stabilization branch.

## High-Signal Differences

| Topic | Intended inherited setup | Actual live setup | Assessment |
|---|---|---|---|
| Pressure-velocity coupling | `SIMPLE` | `Coupled` | likely drift or temporary numerics branch |
| Momentum / turbulence / multiphase schemes | second-order family, `QUICK` for VF where available | first-order upwind for momentum, `k`, `epsilon`, and multiphase entry | likely drift or temporary stabilization branch |
| Surface tension | expected from parent chain, `0.0411 N/m` | `liquid_surface_tension` exists in model tree but is inactive/unset | important reconstruction gap |
| DPM content | setup `07` report focuses on continuous setup plus later DPM interpretation | live case has active `discrete_phase` branch and multiple injections | actual case is richer than the setup-07 report delta |
| Saved iteration count | loaded data filename suggests `02541` | exported runtime shows `2000` | verify whether Fluent session state or file lineage changed before export |
| Steam inlet turbulence field | intended report uses hydraulic diameter `0.72061 m` | actual BC state shows `Intensity and Viscosity Ratio` with `0.72061` | likely boundary-setting mismatch or Fluent UI interpretation issue |

## Matches

| Topic | Intended | Actual | Assessment |
|---|---|---|---|
| Solver family | pressure-based, steady | pressure-based, steady | matched |
| Multiphase model | `Mixture` | `Mixture` | matched |
| Number of phases | `2` | `2` | matched |
| Energy | `Off` | `Off` | matched |
| Turbulence family | RNG `k-epsilon` | RNG `k-epsilon` | matched |
| Pressure scheme | `PRESTO!` | `PRESTO!` | matched |
| Gravity / operating-pressure convention | gravity on, operating pressure `0 Pa` | gravity on, operating pressure `0 Pa` | matched |
| Boundary roles | split liquid inlet, split steam inlet, steam outlet, walls | `liquidinlet`, `steaminlet`, `steamoutlet`, `wall-fluid`, `bottom` | matched by role |
| Inlet split velocity target | `27.118 m/s` on both inlets | `27.118 m/s` on both inlets | matched |
| Liquid inlet VF | pure liquid | liquid inlet secondary-phase VF `1` | matched |
| Steam inlet VF | pure steam | steam inlet secondary-phase VF `0` | matched |

## Model Detail Notes

### Multiphase

Intended from the chain:

- `Mixture`
- gas primary phase
- liquid secondary phase
- inherited surface tension from earlier split-inlet setup references

Actual live export:

- `models = mixture`
- `number_of_phases = 2`
- children exposed in this build:
  - `vaporization_pressure`
  - `non_condensable_gas`
  - `liquid_surface_tension`
  - `bubble_number_density`
  - `number_of_eulerian_discrete_phases`
- all of the above optional branches are inactive in this case

Interpretation:

- The build supports a surface-tension branch, but this exported case does not currently have it active.
- For reconstruction, surface tension should be treated as an explicit decision point, not assumed from the exported case.

### Viscous

Intended from the chain:

- RNG `k-epsilon`
- standard wall treatment behavior consistent with Purnanto-style baseline
- second-order spatial schemes

Actual live export:

- RNG `k-epsilon`
- differential viscosity `on`
- swirl-dominated flow `on`
- standard wall function
- several other turbulence-family options exist in the Fluent build but are inactive

Interpretation:

- turbulence model family matches well
- numerical-order choice does not

### Discrete Phase

Intended from the report chain:

- setup `07` is primarily defined as a continuous split-inlet branch; DPM is discussed as later evaluation logic

Actual live export:

- active `discrete_phase` branch
- multiple injections present
- active tracking and numerics controls

Interpretation:

- the live case is no longer just a clean setup-07 continuous-flow branch
- if you want a pure reconstruction script, DPM should probably be made an optional second stage

## Practical Reconstruction Guidance

For rebuild automation, do not drive from the exported live case alone and do not drive from setup `07` alone.

Use a merged spec:

1. inherit unchanged physics and numerics from `00` -> `03` -> `04`
2. apply only the intended inlet-specific changes from `07`
3. compare each item against the live export
4. mark each conflict as one of:
   - `intended authority`
   - `actual authority`
   - `needs user choice`

Current items that most clearly need explicit authority choice:

- `SIMPLE` vs `Coupled`
- second-order / `QUICK` vs first-order
- surface tension active at `0.0411 N/m` vs inactive
- whether DPM injections belong in the base reconstruction or only in a later stage

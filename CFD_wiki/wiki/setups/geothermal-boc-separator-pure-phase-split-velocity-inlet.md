# Setup: Geothermal BOC Separator Pure-Phase Split Velocity Inlet

## Purpose
Consolidate the current Purnanto-derived Fluent setup for a spiral-inlet geothermal BOC separator where the inlet is split into:

- `inlet_liquid_outer`: pure liquid water on the outer-wall side;
- `inlet_steam_inner`: pure steam on the inner/core side.

This page merges the stable baseline solver stack from the 2013 reconstruction with the recent project setup-branch calculations for the pure liquid / pure steam velocity-inlet variants.

## Source Basis
- Paper extraction: [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- Baseline reconstruction: [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md)
- Reusable split-inlet rule: [geothermal-boc-separator-two-zone-split-inlet](geothermal-boc-separator-two-zone-split-inlet.md)
- Project experiment records used for the velocity-inlet variants:
  - [mixed wet-half actual-area record](../../../Project/experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-04-mixed-wet-half-actual-area/setup.md)
  - [pure-phase actual-area record](../../../Project/experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-07-pure-phase-actual-area/setup.md)
  - [pure-phase actual-area record](../../../Project/experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-07-pure-phase-actual-area/setup.md)

## Evidence Labels
- `Reported`: directly stated in the 2013 paper.
- `Calculated`: derived from reported phase flows, densities, and current inlet area.
- `Assumed`: selected for a controlled adaptation because the paper did not report this exact inlet form.
- `User-specified`: entered in the recent setup branch by project choice rather than the paper.

## When To Use This
- Use this page when the baseline mist-like inlet is being replaced by a sharp pure-liquid / pure-steam split.
- Use it for the spiral-inlet Purnanto comparison path, not as a generic rule for all separator geometries.
- Keep the rest of the baseline stack frozen if the goal is an A/B inlet comparison.

## A) Geometry and Inlet Split
- Geometry family: spiral-inlet vertical BOC separator (`Reported` for the source geometry family; `Assumed` for this exact project mesh adaptation) ([purnanto-2013], p.2, p.6).
- Current inlet dimensions used by the recent setup branches: `0.724 m x 0.724 m` (`Calculated` from project setup reports).
- Full inlet area:

```text
A_total = 0.724 * 0.724 = 0.524176 m2
```

- Purnanto `1600 kJ/kg` phase targets reused for the split:

```text
m_dot_liquid = 116.92 kg/s
m_dot_steam  = 80.69 kg/s
rho_liquid   = 881.77 kg/m3
rho_steam    = 5.73 kg/m3
```

- Exact-mass equal-velocity split (`Calculated`):

```text
Q_liquid = 116.92 / 881.77 = 0.1325969 m3/s
Q_steam  = 80.69 / 5.73    = 14.0820244 m3/s
Q_total  = 14.2146214 m3/s
V        = Q_total / A_total = 27.1180 m/s

A_liquid = 0.0048896 m2
A_steam  = 0.5192864 m2
```

- If the inlet is split along `x` while keeping full height `0.724 m`:

```text
liquid-side width = 0.006754 m
steam-side width  = 0.717246 m
```

- Mapping rule (`Assumed`, `Low Risk`):
  - liquid side = outer-wall side of the spiral inlet;
  - steam side = inner/core side;
  - do not rely only on screen-left/screen-right naming.

## B) Physics and Models
- Solver family: `Pressure-Based` (`Reported`) ([purnanto-2013], p.6).
- Time formulation: `Steady` (`Reported`) ([purnanto-2013], p.5).
- Flow assumptions: incompressible, isothermal, no flashing (`Reported`) ([purnanto-2013], p.5).
- Multiphase model: `Mixture` (`Reported`) ([purnanto-2013], p.3).
- Primary phase: steam/vapor (`Assumed`, consistent with paper mist-flow description and project reuse path).
- Secondary phase: liquid water (`Assumed`, consistent with paper mist-flow description and project reuse path).
- Turbulence model: `RNG k-epsilon` (`Reported`) ([purnanto-2013], p.1, p.3, p.9).
- Energy equation: `Off` (`Reported` by the isothermal assumption) ([purnanto-2013], p.5).
- Gravity: `On`, downward in `y`, `9.81 m/s2` (`Reported`) ([purnanto-2013], p.5).
- Wall roughness: smooth / `0` (`Reported`) ([purnanto-2013], p.5).

## C) Materials and Operating Conditions
- Use the paper's separator-condition liquid and steam properties from Table 1 (`Reported`) ([purnanto-2013], p.5).
- Separator-condition material values to enter (`Reported` from Table 1, reused in the recent setup branches):
  - liquid density `881.77 kg/m3`;
  - steam density `5.73 kg/m3`;
  - liquid viscosity `145.96e-6 kg/m-s`;
  - steam viscosity `15.188e-6 kg/m-s`.
- Practical Fluent interpretation:
  - use constant density and constant viscosity for this isothermal baseline-style case unless you are deliberately moving away from the Purnanto reconstruction.
- Separation pressure in the source study: `11.2 bara` (`Reported`) ([purnanto-2013], p.5).
- Source boundary pressure package:
  - inlet pressure `11.4 bar`;
  - outlet pressure `11.2 bar`
  (`Reported`) ([purnanto-2013], p.6).
- Practical rule for the velocity-inlet adaptation (`Assumed`, `Medium Risk`):
  - keep the pressure reference convention consistent across inlet, steam outlet, brine outlet, and operating pressure;
  - do not mix absolute and gauge interpretations inside one case.

## D) Boundary Conditions
### Recommended Pure-Phase Split Package
Use two real inlet faces created in CAD/meshing:

| Boundary | Type | Velocity | Liquid VF | Steam VF |
|---|---|---:|---:|---:|
| `inlet_liquid_outer` | `Velocity Inlet` | `27.118 m/s` | `1.0` | `0.0` |
| `inlet_steam_inner` | `Velocity Inlet` | `27.118 m/s` | `0.0` | `1.0` |

- Why `27.118 m/s`:
  - it preserves the Purnanto `1600 kJ/kg` phase mass-flow targets with the current `0.524176 m2` inlet area (`Calculated`).

Expected inlet mass-flow check:

```text
liquid = 881.77 * 27.118 * 0.0048896 = 116.92 kg/s
steam  = 5.73   * 27.118 * 0.5192864 = 80.69 kg/s
total  = 197.61 kg/s
```

### Fixed Reported-Velocity Alternate
Use this only if matching the reported spiral-inlet velocity matters more than exact mass flow:

| Boundary | Type | Velocity | Liquid VF | Steam VF |
|---|---|---:|---:|---:|
| `inlet_liquid_outer` | `Velocity Inlet` | `26.81 m/s` | `1.0` | `0.0` |
| `inlet_steam_inner` | `Velocity Inlet` | `26.81 m/s` | `0.0` | `1.0` |

Expected result at current area (`Calculated`):

```text
liquid = 115.59 kg/s
steam  = 79.77 kg/s
total  = 195.37 kg/s
```

This is `1.14 %` below the exact Purnanto total mass-flow target.

### Outlet Package
- Steam outlet: keep as `Pressure Outlet` (`Reported` BC family from the source; exact active gauge value must follow the current pressure-reference convention) ([purnanto-2013], p.6).
- Brine outlet:
  - if the branch includes liquid drainage, keep the parent case's brine-outlet treatment unchanged;
  - if the branch is the no-brine-outlet diagnostic, the brine face should be absent or set to `Wall`, not left as an unintended pressure outlet (`Assumed`, based on `05` branch logic).
- Backflow phase fractions at pressure outlets (`Assumed`, `Medium Risk`):
  - first controlled default: liquid `0.0`, steam `1.0` at the steam outlet.

## E) Inlet Turbulence Specification
- Reused baseline-style turbulence intensity for split velocity inlets: `2.10999999 %` (`User-specified`, from recent project setup branch).

### Core Comparison Default
For the first controlled inlet A/B test, keep the physical upstream duct hydraulic diameter on both split zones:

| Boundary | Turbulence method | Intensity | Hydraulic diameter |
|---|---|---:|---:|
| `inlet_liquid_outer` | `Intensity and Hydraulic Diameter` | `2.10999999 %` | `0.724 m` |
| `inlet_steam_inner` | `Intensity and Hydraulic Diameter` | `2.10999999 %` | `0.724 m` |

- Why:
  - this changes the phase distribution without also changing the turbulence length scale (`Assumed`, `Medium Risk`).

### Phase-Specific Hydraulic-Diameter Sensitivity
Use this only as a deliberate second case:

| Boundary | Turbulence method | Intensity | Hydraulic diameter |
|---|---|---:|---:|
| `inlet_liquid_outer` | `Intensity and Hydraulic Diameter` | `2.10999999 %` | `0.01338 m` |
| `inlet_steam_inner` | `Intensity and Hydraulic Diameter` | `2.10999999 %` | `0.72061 m` |

Hydraulic-diameter basis (`Calculated`):

```text
Dh = 2ab / (a + b)

liquid zone: a = 0.0067536 m, b = 0.724 m -> Dh = 0.01338 m
steam zone:  a = 0.7172464 m, b = 0.724 m -> Dh = 0.72061 m
```

Risk note:
- the liquid-zone `Dh` is about `54x` smaller than `0.724 m`, so this sensitivity also changes inlet turbulence length scale, not just phase placement.

## F) Solution Methods
- Pressure-velocity coupling: `SIMPLE` (`Reported`) ([purnanto-2013], p.6).
- Gradient: `Green-Gauss Node Based` (`Reported`) ([purnanto-2013], p.6).
- Pressure: `PRESTO!` (`Reported`) ([purnanto-2013], p.6).
- Momentum: `Second Order Upwind` (`Reported`) ([purnanto-2013], p.6).
- Turbulent kinetic energy: `Second Order Upwind` (`Reported`) ([purnanto-2013], p.6).
- Turbulent dissipation rate: `Second Order Upwind` (`Reported`) ([purnanto-2013], p.6).
- Volume fraction: `QUICK` if available (`Reported` in the source baseline; retained in the recent setup branches) ([purnanto-2013], p.6).

## G) Initialization and Run Control
- Initialization method: `Hybrid Initialization` (`Reported`) ([purnanto-2013], p.6).
- Initialization values for pressure, velocity, turbulence variables, and volume fraction: `Missing` in the source ([purnanto-2013], p.6).
- Practical reuse default:
  - initialize with `Hybrid Initialization`;
  - do not patch the inlet boundaries;
  - only patch cell zones if running a separate liquid-pool initialization experiment.
- Iteration budget:
  - the recent no-brine-outlet diagnostic branch planned `5000` steady iterations;
  - otherwise use monitor-based stopping because the paper does not report a fixed iteration count.
- Under-relaxation factors: `Missing` in the source; keep Fluent defaults unless a failure-specific sensitivity is being run (`Assumed`, `Medium Risk`).

## H) Mesh and Resolution Checks
- Mesh family: unstructured tetrahedral (`Reported`) ([purnanto-2013], p.6).
- Reported source resolution guidance:
  - mesh nodes in the order of millions;
  - average element size about `5 cm`;
  - local high-gradient faces down to about `1 cm`
  (`Reported`) ([purnanto-2013], p.6).
- Split-inlet-specific check:
  - confirm the `6.754 mm` liquid strip is represented by real boundary faces and enough cells across the width.

## I) Monitors and Acceptance Checks
- Track scaled residuals for continuity, momentum, `k`, `epsilon`, and volume fraction.
- Run inlet phase flux reports after initialization and early iterations.
- Track total mass imbalance.
- Track steam outlet steam and liquid mass flow separately.
- Inspect liquid volume fraction on the inlet plane and just downstream.
- Inspect velocity vectors around the spiral inlet, vortex core, and steam outlet intake.

First numerical checks:

```text
liquid inlet ~= 116.92 kg/s
steam inlet  ~= 80.69 kg/s
total inlet  ~= 197.61 kg/s
```

or, for the fixed-velocity alternate:

```text
liquid inlet ~= 115.59 kg/s
steam inlet  ~= 79.77 kg/s
total inlet  ~= 195.37 kg/s
```

## J) Common Failure Modes
- A sketch split is created, but Fluent still sees only one inlet boundary.
- The liquid strip is too narrow for the current mesh and diffuses immediately.
- The liquid and steam sides are reversed because the face was named by camera direction, not physical outer-wall/core meaning.
- The hydraulic-diameter sensitivity is interpreted as a phase split result even though turbulence length scale changed at the same time.
- Pressure references are mixed between operating pressure and outlet boundary inputs.

## K) Recommended Build Sequence
1. Start from the closest stable baseline or parent split case.
2. Split the inlet into two real faces in geometry/meshing.
3. Keep solver family, multiphase model, turbulence model, gravity, outlet family, and solution methods unchanged.
4. Enter the exact-mass split package at `27.118 m/s`.
5. First run with `Dh = 0.724 m` on both zones if the goal is a clean inlet-structure comparison.
6. Only then run the phase-specific hydraulic-diameter sensitivity if needed.
7. Keep the `26.81 m/s` package as a separate reported-velocity-matching alternate, not the main exact-mass case.

## Missing Info
- The source paper does not report a pure-phase split inlet; this whole inlet form is an adaptation.
- The source does not report residual targets, URFs, or exact stopping rules.
- The exact active pressure-reference package used in the latest Fluent branch is not fully documented in the reusable CFD setup layer.

## Reproducibility Confidence
- Baseline solver/method stack: `Medium`.
- Exact pure-phase split geometry calculation: `High`.
- Turbulence hydraulic-diameter choice: `Medium-Low` because the branch intent and the controlled-comparison recommendation diverge.

## Cross-Linkage
- `extends` [geothermal-boc-separator-two-zone-split-inlet](geothermal-boc-separator-two-zone-split-inlet.md) by turning the general split rule into a full pure-phase velocity-inlet package.
- `reuses` [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md) for the solver, numerics, gravity, and material basis.
- Project-facing trace is maintained in [the Project inlet-regimes
  interpretation](../../../Project/experiments/phase-02-parity-reset-and-pre-v2-qualification/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md).

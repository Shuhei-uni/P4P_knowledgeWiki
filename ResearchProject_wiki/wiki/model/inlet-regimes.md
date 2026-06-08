# Inlet Regimes

## Objective
Track how inlet representation evolves from simplified baseline toward realistic regime-aware modelling.

## Current Baseline
- Legacy recreation currently assumes mist-like inlet for two-phase feed (based on historical modelling approach).

## Selected Next Inlet Test
- Replace the uniform/mist-like inlet assumption with a **two-zone split inlet**.
- Project intent:
  - outer-wall side of inlet = liquid water
  - inner/core side of inlet = steam
- Preferred implementation route:
  - split the inlet face in geometry/meshing,
  - import two named inlet zones into Fluent,
  - keep the rest of the baseline solver stack unchanged for the first A/B comparison.

## Pure-Phase Equal-Velocity Split Calculation
- Calculation date: 2026-05-28.
- Source values: Purnanto `1600 kJ/kg` phase mass flows from the reusable CFD setup, using liquid `116.92 kg/s`, steam `80.69 kg/s`, liquid density `881.77 kg/m3`, and steam density `5.73 kg/m3`.
- Current inlet area basis: `0.724 m x 0.724 m = 0.524176 m2`.
- Exact-mass result: to keep one shared inlet velocity while assigning one side pure liquid and the other side pure steam, split by volumetric flow:
  - inlet velocity: `27.118 m/s`;
  - liquid-side area: `0.0048896 m2` (`0.9328 %` of inlet);
  - steam-side area: `0.5192864 m2` (`99.0672 %` of inlet);
  - liquid-side width along `x` if full height is `0.724 m`: `0.006754 m`;
  - steam-side width along `x`: `0.717246 m`.
- Active project choice: use the exact-mass/current-area value `27.118 m/s` for the next pure liquid / pure steam split-inlet build.
- Fixed Purnanto-velocity result: using `26.81 m/s` with the current `0.724 m x 0.724 m` area keeps the same split location but gives liquid `115.59 kg/s`, steam `79.77 kg/s`, and total `195.37 kg/s`, about `1.14 %` below the exact Purnanto total mass flow.
- Exact Purnanto mass flow at `26.81 m/s` would require total inlet area `0.5301985 m2`, equivalent to a `0.732318 m` width if height stays `0.724 m`.
- Project interpretation: a center split is not valid for a pure liquid/pure steam velocity-inlet model because it would over-allocate area to liquid and under-allocate area to steam relative to the Purnanto phase mass-flow targets.
- Reusable derivation: `../../../CFD_wiki/wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`.
- Fixed-velocity setup report retained as an alternate/reference: `../../../Setup report/06-pure-phase-split-fixed-velocity.md`.

## Fluent Velocity-Inlet Turbulence Inputs
- Current project answer for the unsplit square inlet: use hydraulic diameter `0.724 m` because `Dh = 4A/P` and a square `0.724 m x 0.724 m` gives `Dh = 0.724 m` (`Inferred`, `Low Risk`).
- Purnanto-style turbulence intensity value `2.109999 %` can be retained as the baseline reproduction value if no new inlet-turbulence evidence is being introduced (`Assumed`, `Medium Risk`).
- If the inlet is split into two Fluent velocity-inlet zones only to assign liquid/steam regions inside the same physical square inlet, keep `Dh = 0.724 m` on both zones for the first controlled comparison so the split does not also introduce a turbulence-length-scale change (`Assumed`, `Medium Risk`).
- If the two zones are instead interpreted as physically separate rectangular ducts, their geometric hydraulic diameters would be approximately:
  - liquid strip `0.006754 m x 0.724 m`: `Dh = 0.01338 m`;
  - steam strip `0.717246 m x 0.724 m`: `Dh = 0.72061 m`.
- Project caution: using `0.01338 m` on the liquid strip would impose a very small turbulence length scale and may add a second change on top of the phase split. Do that only as a sensitivity test, not the first baseline split-inlet run.
- Reusable Fluent guidance: `../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md`.

## Phase-Specific Turbulence Diameter Sensitivity
- User hypothesis on 2026-05-28: because the split inlet represents pure liquid on one side and pure steam on the other, phase-specific turbulence inputs may be more physically appropriate than reusing the same square-inlet hydraulic diameter on both zones.
- Candidate setup for a deliberate two-turbulence sensitivity case (`Assumed`, `Medium Risk`):
  - `inlet_liquid_outer`: turbulence intensity `2.109999 %`, hydraulic diameter `0.01338 m`;
  - `inlet_steam_inner`: turbulence intensity `2.109999 %`, hydraulic diameter `0.72061 m`.
- Interpretation: the hydraulic-diameter change represents each rectangular inlet-zone geometry, not the liquid/steam material property difference by itself. Material density/viscosity differences are already handled through the phase/material definitions.
- Numerical impact to watch: for the same inlet velocity and turbulence intensity, the liquid-side `Dh = 0.01338 m` is about `54.1x` smaller than the full square-inlet `Dh = 0.724 m`, so Fluent will impose a much shorter liquid-side turbulence length scale and much higher dissipation-scale tendency at that boundary (`Inferred`, `Medium Risk`).
- Run-control recommendation: compare this only against a saved same-geometry case using `Dh = 0.724 m` on both split zones; otherwise the inlet phase split and turbulence-length-scale change cannot be separated.
- Diagnostics to check after changing to phase-specific `Dh`:
  - inlet-zone `k`, dissipation rate, and turbulent viscosity ratio immediately after initialization;
  - residual spikes in `k`, `epsilon`, momentum, and volume fraction during the first `100-300` iterations;
  - liquid-strip mesh resolution across the `6.754 mm` width;
  - phase mass-flow reports on both inlets to confirm the turbulence setting did not mask a boundary assignment error;
  - near-inlet volume fraction and velocity vectors to see whether the liquid strip diffuses, jets, or destabilizes too quickly.

## Planned Progression
1. Reproduce and converge baseline model.
2. Introduce one controlled inlet modification only: the two-zone split inlet.
3. Compare internal flow structure, phase distribution, pressure drop, and outlet behavior against the original inlet representation.
4. Only if needed, move later to smoother non-uniform inlet profiles or a UDF/profile approach.

## Current Uncertainties
- The exact physical meaning of `left` and `right` must be confirmed on the actual inlet-face orientation before the two zones are named.
- A 50/50 inlet-area split is now superseded for the pure-phase equal-velocity setup. The new concern is whether the very narrow `6.754 mm` liquid-side strip is physically appropriate and sufficiently mesh-resolved.
- The current attempted setup combines multiple changes at once: two-phase inlet design, brine outlet representation, and water initialized at the bottom. Because several features changed together, the problematic result should first be treated as a diagnostic case rather than proof that the inlet concept is invalid.

## Current Troubleshooting Rule
Before further geometry or physics upgrades, isolate the failure mode with one-change-at-a-time controls:
1. Keep the current inlet and outlets unchanged, but compare bottom-water initialization against a simpler initialization.
2. If the problem remains, inspect brine outlet behavior and reverse-flow/phase settings.
3. If outlet behavior is stable, inspect split-inlet orientation and phase allocation.
4. Only after these checks should the case be compared against partner validation or parameter-sweep results.

## Newest Run Interpretation
- Run reference: `MWH-WP-2026-05-07-A`.
- Setup report: `../../../Setup report/03a-mixed-wet-half-velocity-inlet-water-pool.md`.
- The lower water-pool initialization improved qualitative swirl development and made the brine outlet active.
- The result is not quantitatively usable because the steady solve drained the initialized water inventory: liquid outflow was much larger than liquid inflow.
- The steam outlet carried excessive liquid, making the guessed steam outlet intake geometry a likely sensitivity source.
- Next diagnostic priority: inspect liquid volume fraction, velocity vectors, and streamlines/pathlines near the steam outlet intake before modifying inlet allocation again.

## Confirmed Geometry Context
- User clarification on 2026-04-30: the active baseline geometry for this inlet-change workflow is the **spiral inlet**, not a tangential inlet.

## Evidence Links
- Technical baseline notes: `wiki/technical/sources/purnanto-etal-2013.md`
- Project objective: `wiki/project/objective-and-scope.md`
- Reusable CFD setup: `../../../CFD_wiki/wiki/setups/geothermal-boc-separator-two-zone-split-inlet.md`
- Consolidated pure-phase settings sheet: `../../../CFD_wiki/wiki/setups/geothermal-boc-separator-pure-phase-split-velocity-inlet.md`
- Practical project report: `../../../Setup report/01-split-two-zone-massflow-inlet.md`

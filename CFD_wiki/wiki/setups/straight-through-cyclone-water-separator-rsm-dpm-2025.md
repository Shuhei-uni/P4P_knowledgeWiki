# Setup: Straight-Through Cyclone Water Separator RSM-DPM Benchmark (Chen 2025)

## Purpose
Reusable beginner-oriented setup sheet for an experiment-backed straight-through cyclone separator workflow using Fluent RSM-DPM.

Use this when a future separator case needs:
- a modern RSM-based swirl benchmark;
- DPM droplets with reported size distribution, breakup, coalescence, and rough-wall interaction;
- an experimental pressure-loss and efficiency check before transferring the method to a new separator.

## Source
- Primary: [chen-2025-straight-through-cyclone-water-separator](../sources/chen-2025-straight-through-cyclone-water-separator.md)

## Reported vs Inferred vs Assumed
- `Reported`: directly stated in Chen et al. 2025.
- `Inferred`: practical Fluent sequence assembled from the paper.
- `Assumed`: fallback for controls the paper does not fully report.

## Step-by-Step Build Order
1. Build the straight-through cyclone separator geometry with the retained `15 mm` upstream conditioning section.
2. Create one of the three swirl-generator variants: `20 deg`, `30 deg`, or `40 deg`.
3. Mesh the separator and confirm a production mesh near `4.0M` cells after a three-mesh check.
4. Set air as the continuous phase with ideal-gas density.
5. Enable a transient pressure-based solver with RSM turbulence.
6. Define water droplets through inlet-surface DPM injection using the reported Rosin-Rammler distribution.
7. Activate KHRT breakup, stochastic collision/coalescence, and the rough-wall model.
8. Mark the collector outer wall and collector outlet as DPM `escape` surfaces so collected droplets count as separated.
9. Solve until all scaled residuals are below `1e-4`.
10. Validate first against the low-pressure experimental case before using the model for pressure or geometry sensitivity.

## A) Geometry and Domain
- Separator type: straight-through cyclone water separator (`Reported`) ([chen-2025], p.3-5).
- Included domain: conditioning section, swirl generator, separator body, collector, and collector outlet (`Reported`) ([chen-2025], p.8).
- Characteristic diameter used in reported Reynolds number processing: `38 mm` (`Reported`) ([chen-2025], p.6).
- Swirl-generator geometry (`Reported`) ([chen-2025], p.5-6):
  - outer diameter `38 mm`
  - central shaft diameter `5 mm`
  - axial length `35 mm`
  - vane count `4`
  - pitch `43.5 mm` for `20 deg`
  - pitch `69 mm` for `30 deg`
  - pitch `100 mm` for `40 deg`

## B) Materials and Operating Inputs
- Continuous phase: air (`Reported`) ([chen-2025], p.10).
- Discrete phase: liquid water droplets (`Reported`) ([chen-2025], p.9-10).
- Experimental operating window (`Reported`) ([chen-2025], p.6):
  - air mass flow rate `100-300 kg/h`
  - humidification rate `5-15 g/kg`
- Validation wet case (`Reported`) ([chen-2025], p.14-15):
  - air mass flow rate `200 kg/h`
  - humidification rate `10 g/kg`
  - outlet pressure `93.8 kPa`
- High-pressure sensitivity case: add `600 kPa` back pressure relative to the low-pressure case (`Reported`) ([chen-2025], p.15).

## C) Physics and Models
- Solver mode: transient, pressure-based (`Reported`) ([chen-2025], p.10).
- Turbulence: Reynolds Stress Model (`Reported`) ([chen-2025], p.8-10).
- DPM framework: Euler-Lagrange droplet tracking (`Reported`) ([chen-2025], p.9-10).
- DPM breakup: KHRT default parameters (`Reported`) ([chen-2025], p.9-10).
- DPM coalescence: Stochastic Collision with default parameters (`Reported`) ([chen-2025], p.9-10).
- Rough-wall model: enabled and calibrated to measured roughness values (`Reported`) ([chen-2025], p.10).
- Why this matters: this is a directly experiment-checked RSM-DPM separator workflow, so it is a better method-transfer reference than an unvalidated tutorial-only cyclone setup.

## D) Boundary and Initial Conditions
- Inlet droplet injection type: surface injection from the inlet surface (`Reported`) ([chen-2025], p.10).
- Collector outer wall + collector outlet DPM behavior: `escape`, counted as separated (`Reported`) ([chen-2025], p.8).
- Boundary primitive values: taken from experiment, but a full Fluent BC table is not reported (`Missing`) ([chen-2025], p.8, p.14-15).
- Initialization method: `Missing`.
- Practical first validation route (`Inferred`):
  1. match the low-pressure outlet pressure to `93.8 kPa`;
  2. run the dry validation case and compare simulated inlet pressure;
  3. run the representative wet case and compare pressure loss plus separation efficiency.

## E) Mesh and Numerics
- Grid study meshes (`Reported`) ([chen-2025], p.10-11):
  - `0.42M`
  - `4.0M`
  - `7.26M`
  cells
- Selected production mesh: `4,000,181` cells (`Reported`) ([chen-2025], p.10-11).
- Minimum reported mesh quality: `> 0.2` (`Reported`) ([chen-2025], p.10-11).
- Coupling: SIMPLE (`Reported`) ([chen-2025], p.10).
- Schemes (`Reported`) ([chen-2025], p.10):
  - continuity: Second-Order Upwind
  - all remaining transport equations: First-Order Upwind
- Residual target: all scaled residuals below `1e-4` (`Reported`) ([chen-2025], p.10).

## F) DPM Injection Package
- Material: liquid water (`Reported`) ([chen-2025], p.10).
- Size distribution: Rosin-Rammler (`Reported`) ([chen-2025], p.10).
- Distribution index: `4.5` (`Reported`) ([chen-2025], p.10).
- Main diameter: `1.5e-5 m` (`Reported`) ([chen-2025], p.10).
- Minimum diameter: `6e-6 m` (`Reported`) ([chen-2025], p.10).
- Maximum diameter: `2.5e-5 m` (`Reported`) ([chen-2025], p.10).
- Rough-wall calibration:
  - `Ra = 6.4 um`
  - `Rq = 7.9 um`
  - `Rsm = 75 um`
  (`Reported`) ([chen-2025], p.10)

## G) Validation Targets
- Dry-case inlet-pressure error should stay within the paper's reported `0.01-2.13%` envelope before trusting internal-flow comparisons (`Reported`) ([chen-2025], p.14).
- Representative wet-case target at low pressure (`Reported`) ([chen-2025], p.14-15):
  - pressure loss about `4.5-5.0 kPa`
  - separation efficiency about `28-29.2%`
- High-pressure sensitivity target (`Reported`) ([chen-2025], p.15):
  - pressure loss near `0.7 kPa`
  - separation efficiency near `36.6%`

## Missing Info
- Full separator-body dimensions outside the summarized swirl-generator table.
- Time-step size and iterations per time step.
- Initialization method and patched values.
- Exact parcel count and additional DPM tracking controls.

## Assumptions
- Start with the `30 deg` or `40 deg` swirler if only one benchmark case is needed, because the paper treats `40 deg` as the best overall performer while `30 deg` reaches a stable strongly turbulent regime earlier over part of the flow range (`Assumed`, `Medium Risk`).
- Keep the collector surfaces as the only counted separation route in the first-pass reproduction unless wall-film re-entrainment is being studied (`Assumed`, `Low Risk`).
- Use Fluent defaults for unreported transient marching controls, then run time-step sensitivity before calling the reproduction validated (`Assumed`, `Medium Risk`).

## Sensitivity Plan (Run First)
1. Validate the low-pressure dry and wet cases before any geometry or pressure extrapolation.
2. Check time-step sensitivity because the paper omits transient marching controls.
3. Check mesh sensitivity near the collector and outlet if efficiency shifts more than a few points.
4. If transferred to geothermal work, compare this RSM-DPM stack against the cheaper project baseline before adopting it as the new default.

## Common Failure Modes
- Matching the wet-case efficiency while missing the dry-case inlet-pressure validation.
- Treating air-water operating values as geothermal inputs rather than analogy-only method anchors.
- Changing turbulence model, droplet PSD, and pressure at the same time so the validation error cannot be diagnosed cleanly.

## Quick Diagnostics
- Compare dry-case simulated inlet pressure to the paper before looking at droplet trajectories.
- Plot separator pressure contours to confirm the expected wall-to-core pressure gradient.
- Inspect whether low-pressure cases produce the high-speed core and more dispersed droplets described by Chen.

## Cross-Paper Linkage
- Related source: [pointon-2009-geothermal-separator-sizing-cfd-validation](../sources/pointon-2009-geothermal-separator-sizing-cfd-validation.md), which gives geothermal-scale separator-entry trend support but a less complete Fluent recipe. Relation: `supports`.
- Related source: [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md), which is geothermal-specific but uses an older RNG `k-epsilon` baseline. Relation: `differs`.
- Related synthesis: [fluent-separator-efficiency-methods](../synthesis/fluent-separator-efficiency-methods.md). Relation: `extends`.
- Reuse guidance: use this page as the experiment-backed RSM-DPM benchmark when you need to challenge a simpler separator CFD baseline.

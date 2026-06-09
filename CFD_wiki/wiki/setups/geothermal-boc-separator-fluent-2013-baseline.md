# Setup: Geothermal Vertical BOC Separator (Fluent Baseline from Purnanto 2013)

## Purpose
Beginner-oriented baseline to recreate the 2013 geothermal cyclone separator CFD study for comparison of three inlet designs.

## Source
- Primary: [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)

## Reported vs Inferred vs Assumed
- `Reported`: values and methods explicitly stated in paper.
- `Inferred`: implied workflow assembled from multiple sections.
- `Assumed`: fallback defaults where paper is incomplete.

## Step-by-Step Build Order
1. Build three geometries (Bangma, Lazalde-Crabtree, Spiral-Inlet) using Table 3 dimensions.
2. Generate unstructured tetra mesh with coarse global size and local boundary refinement.
3. Set continuous-phase solver to pressure-based, incompressible, isothermal.
4. Enable RNG k-epsilon turbulence model.
5. Apply boundary conditions (mass-flow inlet, pressure outlet) and pressure settings.
6. Initialize with Hybrid Initialization and iterate to convergence.
7. Run particle injections for separator efficiency evaluation.
8. Post-process velocity, pressure, and outlet steam quality trends across cases.

## A) Geometry and Domain
- Three vertical BOC configurations from legacy and modern designs (`Reported`) ([purnanto-2013], p.2, p.6).
- Heads treated as 2:1 ellipses (`Reported`) ([purnanto-2013], p.6).
- Scope excludes upstream pre-separation and explicit brine-bottom flow dynamics (`Reported`) ([purnanto-2013], p.5).

## B) Materials and Operating Inputs
- Total two-phase inlet mass flow: 197.61 kg/s (`Reported`) ([purnanto-2013], p.5).
- Separation pressure: 11.2 bara (`Reported`) ([purnanto-2013], p.5).
- Enthalpy conditions: 1440, 1520, 1600, 1680, 1760 kJ/kg + one 25% reduced-flow case at 1600 (`Reported`) ([purnanto-2013], p.5).
- Use Table 1 properties for density/viscosity/surface tension at separator condition (`Reported`) ([purnanto-2013], p.5).

## C) Physics and Models
- Continuous phase assumptions: incompressible, isothermal, no flashing (`Reported`) ([purnanto-2013], p.5).
- Turbulence: RNG k-epsilon (`Reported`) ([purnanto-2013], p.1, p.3, p.9).
- Multiphase strategy: mixed wording in paper.
  - Working baseline (`Inferred`): solve continuous field first, then DPM particle tracking for efficiency.

## D) Boundary and Initial Conditions
- Inlet BC: mass flow inlet (`Reported`) ([purnanto-2013], p.6).
- Plain-language interpretation: this baseline uses one inlet boundary carrying both steam and water together, not two separately named inlet zones and not a full-face velocity-inlet reinterpretation (`Inferred`, based on the source BC family plus the live Fluent audit).
- Outlet BC: pressure outlet (`Reported`) ([purnanto-2013], p.6).
- Inlet pressure: 11.4 bar (`Reported`) ([purnanto-2013], p.6).
- Outlet pressure: 11.2 bar (`Reported`) ([purnanto-2013], p.6).
- Initialization method: Hybrid Initialization (`Reported`) ([purnanto-2013], p.6).
- Initialization rationale: chosen because it does not require additional user inputs and may improve convergence robustness (`Reported`) ([purnanto-2013], p.6).
- Initialized field values: not reported for pressure, velocity, turbulence variables, or volume fraction (`Missing`) ([purnanto-2013], p.6).
- Gravity: 9.81 m/s^2 downward in y (`Reported`) ([purnanto-2013], p.5).
- Wall roughness: 0 (smooth) (`Reported`) ([purnanto-2013], p.5).
- Closely related but separate from Fluent field initialization:
  - inlet two-phase state is assumed mist flow with gas as continuous phase and liquid as dispersed phase (`Reported`) ([purnanto-2013], p.5).
  - droplets are initially uniform with average diameter 1e-5 m (`Reported`) ([purnanto-2013], p.5).
  - water level is assumed constant just above the brine outlet (`Reported`) ([purnanto-2013], p.5).

## E) Mesh and Numerics
- Mesh: unstructured tetra volumes (`Reported`) ([purnanto-2013], p.6).
- Resolution: millions of nodes preferred; average 5 cm, local 1 cm near high gradients (`Reported`) ([purnanto-2013], p.6).
- Solver: pressure-based (`Reported`) ([purnanto-2013], p.6).
- Coupling: SIMPLE (`Reported`) ([purnanto-2013], p.6).
- Schemes (`Reported`) ([purnanto-2013], p.6):
  - Gradient: Green-Gauss Node Based
  - Pressure: PRESTO
  - Momentum/k/turbulent dissipation: second-order upwind
  - Volume fraction: QUICK

## F) Particle Tracking for Efficiency
- Inject droplets after converged continuous solution (`Reported`) ([purnanto-2013], p.4).
- Baseline droplet assumption: uniform average diameter 1e-5 m (`Reported`) ([purnanto-2013], p.5).
- Harwell relation for sensitivity setup: `x_med = 1.42 x_sa`; if `10 um` is treated as the Harwell Sauter mean, then the inferred median is `14.2 um` and the standard distribution upper marker is about `41.18 um` (`Reported` relation, `Inferred` envelope) ([purnanto-2013], p.3-4).
- Nine Harwell-derived DPM injections were used for outlet steam quality, but the exact nine diameters and parcel mass allocation are not listed (`Missing`) ([purnanto-2013], p.8).
- Euler time step limit for tracking: 1e5 (tested to 1e6) (`Reported`) ([purnanto-2013], p.8).
- Particle outcomes: trapped, escaped, incomplete (`Reported`) ([purnanto-2013], p.8).

## Live Setup Cross-Check
- The local HDF5 case audit in this repo confirms the saved baseline Fluent setup uses a mass-flow inlet, pressure outlet, pressure-based steady `Mixture`, `RNG k-epsilon`, SIMPLE, PRESTO!, second-order momentum/turbulence, QUICK volume fraction, gravity `(0, -9.81, 0) m/s2`, operating pressure `0 Pa`, and `5000` saved iterations (`Observed`).
- The audit also confirms `2,964,593` cells, `572,556` nodes, minimum orthogonal quality `0.277635`, and maximum aspect ratio `12.8899` (`Observed`).
- The live case carries DPM settings but no active injections; use it as a setup parity anchor, not as a completed particle-efficiency result (`Observed`).

## G) Expected Outputs
- Velocity profiles by geometry and height slices (`Reported`) ([purnanto-2013], p.7).
- Pressure distribution showing lower core pressure and higher wall pressure (`Reported`) ([purnanto-2013], p.8).
- Outlet steam quality vs inlet velocity/enthalpy (`Reported`) ([purnanto-2013], p.9).

## Missing Info
- No initialized field values are given.
- Residual convergence criteria are not given in the paper, but the live HDF5 audit now supplies them for the saved case.
- Iteration count / stopping rules for the paper run itself are still not fully reported beyond the saved live case state.
- Under-relaxation factors are not given in the paper, but the live HDF5 audit now supplies them for the saved case.
- Exact mesh quality thresholds are not given in the paper.
- Exact particle injection count and size-bin allocation details incomplete.
- The exact paper text does not prove the geometry variant by itself, so the saved case still needs visual confirmation if geometry identity matters.

## Assumptions
- Assume convergence when residuals stabilize and key monitors flatten (`Assumed`, `Medium Risk`).
- For the paper-only reconstruction, use the live HDF5 audit values as the practical parity target when the paper does not report a number directly (`Assumed`, `Low Risk`).
- Assume DPM only for post-convergence tracking phase (`Inferred`, `Medium Risk`).

## Sensitivity Plan (Run First)
1. Mesh refinement sensitivity near inlet transition and outlet tube.
2. Hybrid Initialization versus patched/standard initialization sensitivity because initial field values are missing.
3. Residual/monitor stopping sensitivity.
4. Particle tracking settings sensitivity (step cap and injection granularity).

## Common Failure Modes
- Large fraction of incomplete particles makes steam-quality interpretation unstable.
- Swirl structure shifts with mesh or pressure discretization changes.
- Backflow instability at outlet if boundary treatment is inconsistent.

## Quick Diagnostics
- Check mass imbalance at inlet/outlets.
- Track vortex core pressure trend by axial location.
- Compare trapped/escaped/incomplete particle ratios across meshes.

## Cross-Paper Linkage
- Current related papers in wiki:
  - [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)
  - [rivas-cruz-2015-geothermal-separator-state-of-art-review](../sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md)
  - [mubarok-2020-cfd-geothermal-flow-meters](../sources/mubarok-2020-cfd-geothermal-flow-meters.md)
- Live setup reference: [purnanto-live-setup-reference](../../../ResearchProject_wiki/wiki/technical/purnanto-live-setup-reference.md)
- Reuse guidance: keep this as separator-vessel CFD baseline; use 2014/2015 reviews for high-level design screening and use 2020 flow-meter setup when pressure-differential metering performance is the target.
- Reusable extension: for a project-driven non-uniform inlet adaptation that keeps the same baseline numerics but splits the inlet into wall-side liquid and core-side steam zones, see [geothermal-boc-separator-two-zone-split-inlet](geothermal-boc-separator-two-zone-split-inlet.md). Relation: `extends`.

## Reuse Extensions
- Direct rebuild reminder: if the goal is to recreate the Purnanto setup itself, keep one mixed steam-water inlet and preserve the `Mass-Flow Inlet` boundary family before testing any split-inlet alternatives. Relation to later split pages: `contrasts`.
- [geothermal-boc-separator-two-zone-split-inlet](geothermal-boc-separator-two-zone-split-inlet.md): keeps the baseline solver stack but replaces a uniform inlet representation with two separately named inlet zones for a segregated two-phase feed.

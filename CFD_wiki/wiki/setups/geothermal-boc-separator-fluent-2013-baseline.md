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
- Euler time step limit for tracking: 1e5 (tested to 1e6) (`Reported`) ([purnanto-2013], p.8).
- Particle outcomes: trapped, escaped, incomplete (`Reported`) ([purnanto-2013], p.8).

## G) Expected Outputs
- Velocity profiles by geometry and height slices (`Reported`) ([purnanto-2013], p.7).
- Pressure distribution showing lower core pressure and higher wall pressure (`Reported`) ([purnanto-2013], p.8).
- Outlet steam quality vs inlet velocity/enthalpy (`Reported`) ([purnanto-2013], p.9).

## Missing Info
- No initialized field values are given.
- Residual convergence criteria not given.
- Iteration count / stopping rules not given.
- Under-relaxation factors not given.
- Exact mesh quality thresholds not given.
- Exact particle injection count and size-bin allocation details incomplete.

## Assumptions
- Assume convergence when residuals stabilize and key monitors flatten (`Assumed`, `Medium Risk`).
- Assume standard Fluent defaults for unreported under-relaxation factors (`Assumed`, `Medium Risk`).
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
- Reuse guidance: keep this as separator-vessel CFD baseline; use 2014/2015 reviews for high-level design screening and use 2020 flow-meter setup when pressure-differential metering performance is the target.
- Reusable extension: for a project-driven non-uniform inlet adaptation that keeps the same baseline numerics but splits the inlet into wall-side liquid and core-side steam zones, see [geothermal-boc-separator-two-zone-split-inlet](geothermal-boc-separator-two-zone-split-inlet.md). Relation: `extends`.

## Reuse Extensions
- [geothermal-boc-separator-two-zone-split-inlet](geothermal-boc-separator-two-zone-split-inlet.md): keeps the baseline solver stack but replaces a uniform inlet representation with two separately named inlet zones for a segregated two-phase feed.

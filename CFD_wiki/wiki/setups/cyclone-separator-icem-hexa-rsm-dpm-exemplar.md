# Setup: Cyclone Separator ICEM Hexa Mesh + Fluent RSM-DPM Exemplar

## Purpose
Reusable beginner-oriented setup sheet for a generic tangential-inlet cyclone separator workflow based on the `youtube-cyclone-icem-fluent` tutorial notes.

Use this as an exemplar when a future separator case needs:
- ICEM CFD hexahedral blocking for a cyclone body, cone, tangential inlet, and vortex finder.
- Fluent RSM setup for strong swirl.
- DPM post-processing for trapped/escaped/incomplete particle accounting.

## Source
- Primary: [youtube-cyclone-separator-icem-fluent-exemplar](../sources/youtube-cyclone-separator-icem-fluent-exemplar.md)

## Reported vs Inferred vs Assumed
- `Reported`: value or operation appears in the user-provided notes from the video.
- `Inferred`: practical implementation sequence assembled from the notes.
- `Assumed`: fallback for unreported Fluent or ICEM controls.

## Step-by-Step Build Order
1. Import the cyclone CAD model as an IGS file.
2. Clean and organize geometry into meaningful ICEM parts.
3. Create points on circle quadrants and midpoints, then project them to curves.
4. Define seven height planes from the outlet region to the bottom region.
5. Scale planes 6 and 7 by X = 0.45 and Y = 0.45 to represent the cone (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
6. Build a single initial block, add O-grid splits, and split blocks at every plane.
7. Associate vertices/edges to points/curves and snap cone vertices to the scaled planes.
8. Split/extrude the tangential inlet block and assign vortex finder blocks to a solid part.
9. Assign remaining volume blocks to the fluid part.
10. Apply mesh edge counts, wall-layer spacing, and vortex-finder refinements.
11. Check mesh quality with Determinant 2x2x2 and export `.msh`.
12. In Fluent, set gravity, RSM, wall functions, materials, boundary conditions, and DPM wall behavior.
13. Try a steady solve first; switch to staged transient time stepping if RSM residuals fluctuate.
14. Inject limestone particles from the inlet and compute efficiency from trapped/escaped/incomplete counts.

## A) Geometry and Domain
- Geometry family: generic cyclone separator with tangential inlet and vortex finder (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- CAD source: SolidEdge geometry imported into ICEM as IGS (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Included domain: cyclone body, cone, tangential inlet, vortex finder opening, dustbin/wall collection boundary, and fluid zones (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Excluded domain: vortex finder solid blocks assigned to a solid part and excluded from fluid calculation (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## B) Physics and Models
- Continuous phase: air (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Particle phase: inert limestone particles (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Turbulence model: Reynolds Stress Model (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Near-wall treatment: Standard Wall Functions (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Why this matters: the source states that standard RANS models such as k-epsilon cannot accurately capture the combined solid-body rotation and free vortex in the cyclone (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- DPM: surface injection from the inlet for particle collection efficiency (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## C) Materials and Operating Inputs
- Gravity: -9.81 m/s^2 in Z direction (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Air: detailed properties not reported (`Missing`).
- Limestone particle density: 2770 kg/m^3 (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Baseline particle diameter: 1 micrometer (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Visualization particle distribution: Rosin-Rammler with particle diameters 1, 5, and 10 micrometers (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## D) Boundary and Initial Conditions
- Inlet type: Velocity Inlet (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Inlet velocity: 12.69 m/s (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Inlet turbulence input method: Intensity and Hydraulic Diameter; hydraulic diameter = 0.127 m (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Outlet type: Pressure Outlet (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Outlet turbulence input method: Intensity and Hydraulic Diameter; hydraulic diameter = 0.15 m (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Wall material: steel (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Dustbin/wall DPM boundary behavior: Trap (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Initialization: Hybrid Initialization (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## E) ICEM Hexa Mesh Workflow
### Geometry Preparation
1. Create points at circle quadrants and midpoint locations (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
2. Project the points to curves so blocking vertices can be associated accurately (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
3. Define seven planes along cyclone height, with plane 1 near the outlet and plane 7 near the bottom (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
4. Scale planes 6 and 7 by X = 0.45 and Y = 0.45 to match the cone (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
5. Organize parts such as tangential inlet, vortex finder, and planes (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

### Blocking
1. Create one large initial block over the geometry (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
2. Add three O-grid splits where blocks pass through the walls (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
3. Split blocks in Z direction at every defined plane height (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
4. Associate vertices and edges to the corresponding points and curves (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
5. Snap cone-section vertices at planes 6 and 7 into position (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
6. Delete blocks not part of the fluid/solid topology (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
7. Create the inlet block by splitting an existing block and extruding the face to tangential inlet points (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
8. Assign vortex finder blocks to a solid part and all flow-domain blocks to a fluid part (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

### Mesh Parameters
- Surface mesh maximum size: 0.017 (`Reported`; units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Fluid edges: 25 nodes (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Wall layer control: 22 nodes, initial spacing 0.03, growth ratio 1.1 or 1.2 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Vortex finder: 11 nodes, spacing 0.025 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Vortex finder end: 26 nodes, spacing 0.03 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Mesh quality criterion: Determinant 2x2x2 (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Boundary names before export: Pressure Outlet, Velocity Inlet, Wall Dustbin (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Export format: unstructured `.msh` (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## F) Fluent Model Setup
1. Import/check mesh.
2. Set gravity to -9.81 m/s^2 in Z (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
3. Enable Reynolds Stress Model and Standard Wall Functions (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
4. Set air as the continuous fluid and limestone as the particle material (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
5. Set the velocity inlet to 12.69 m/s and hydraulic diameter 0.127 m (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
6. Set the pressure outlet turbulence hydraulic diameter to 0.15 m (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
7. Set the wall dustbin DPM behavior to `Trap` (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## G) Solution Strategy
### Steady Attempt
- Start with steady state, Hybrid Initialization, and up to 5000 iterations (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- If RSM residuals fluctuate without convergence, switch to transient (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

### Transient Fallback
1. Time step 0.01 s, 20 iterations per step, 10 steps (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
2. Time step 0.005 s, 40 iterations per step, 10 steps (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
3. Time step 0.001 s, 50 iterations per step, 5 steps (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
4. Residual target: continuity below 1e-3 (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## H) DPM and Results
- Injection type: surface injection from inlet (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Particle type: inert limestone (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Particle density: 2770 kg/m^3 (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Baseline particle diameter: 1 micrometer (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Trapped: particles reaching dustbin wall (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Escaped: particles leaving through the vortex finder (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Incomplete: particles stuck in infinite-loop-like tracking; subtract from total injected before computing efficiency (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Separation efficiency: trapped / (injected - incomplete) (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Pressure drop: use Volume Integrals for Total Pressure over fluid cell zones (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## Missing Info
- Exact cyclone dimensions and CAD scale.
- Units for ICEM spacing values 0.017, 0.03, and 0.025.
- Inlet and outlet turbulence intensity values.
- Solver coupling, pressure interpolation, gradient, momentum, and RSM discretization schemes.
- Under-relaxation factors.
- Final residual/monitor histories.
- DPM drag law, parcel count, stochastic tracking, step limits, and coupling mode.
- Actual pressure-drop and separation-efficiency results.

## Assumptions
- Use pressure-based incompressible air solver for first-pass reconstruction (`Assumed`, `Medium Risk`).
- Use Fluent defaults for unreported material properties, DPM drag, and particle tracking controls until source detail is recovered (`Assumed`, `Medium Risk`).
- Keep first-pass mesh dimensions in the CAD import units and verify physical scale before trusting velocity/pressure-drop results (`Assumed`, `High Risk`).
- Run DPM after the continuous RSM flow is acceptably stable, unless two-way particle coupling is intentionally being tested (`Assumed`, `Medium Risk`).

## Sensitivity Plan (Run First)
1. Check physical scale by comparing inlet hydraulic diameter to the mesh geometry.
2. Run steady RSM first, then repeat with the staged transient schedule if residuals fluctuate.
3. Compare vortex-finder end refinement because source notes identify it as pressure-drop critical.
4. Compare wall-layer growth ratios 1.1 and 1.2.
5. Vary DPM tracking controls until incomplete particles are a small and stable fraction.

## Common Failure Modes
- RSM does not converge steadily and needs transient stepping.
- Vortex finder under-resolution causes pressure-drop error.
- Dustbin wall is left as `reflect` or default DPM behavior, so collected particles are not counted as trapped.
- Incomplete particle count is large enough to make efficiency unreliable.
- ICEM blocking associations fail near the cone if scaled-plane vertices are not snapped correctly.

## Quick Diagnostics
- Plot swirl velocity and pressure through axial sections.
- Check total pressure at inlet/outlet or volume-integral reporting consistently across runs.
- Report trapped, escaped, and incomplete particle counts together, not only efficiency.
- Inspect mesh determinant quality at the inlet, cone, wall O-grid, and vortex finder end.

## Cross-Paper Linkage
- Related setup: [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md).
- Related cyclone setup: [cyclone-separator-workbench-tetra-rng-dpm-exemplar](cyclone-separator-workbench-tetra-rng-dpm-exemplar.md), which uses Workbench/SpaceClaim volume extraction, tetra meshing, RNG k-epsilon with swirl-dominated option, and DPM source updates. Relation: `differs`.
- Related entities/concepts:
  - [geometry-tangential-inlet-cyclone-separator](../entities/geometry-tangential-inlet-cyclone-separator.md)
  - [turbulence-reynolds-stress-model](../entities/turbulence-reynolds-stress-model.md)
  - [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
  - [mesh-inflation-boundary-layer](../concepts/mesh-inflation-boundary-layer.md)
- Relation to geothermal baseline: `extends` separator workflow knowledge with ICEM hexa blocking and RSM; `differs` because the geothermal baseline used RNG k-epsilon and unstructured tetra mesh.
- Reuse guidance: copy the meshing logic and DPM accounting pattern; adapt material, geometry, and inlet/outlet values for project-specific separator cases.

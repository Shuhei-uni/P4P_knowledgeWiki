# Setup: Cyclone Separator Workbench Tetra Mesh + Fluent RNG-DPM Exemplar

## Purpose
Reusable beginner-oriented setup sheet for a cyclone separator built through ANSYS Workbench, SpaceClaim volume extraction, tetrahedral meshing, Fluent RNG k-epsilon, and DPM particle tracking.

Use this as an exemplar when a future separator case needs:
- Workbench/SpaceClaim internal-flow-volume extraction.
- Simple tetrahedral meshing with named selections.
- RNG k-epsilon with swirl-dominated option as a lower-cost cyclone turbulence setup.
- DPM source-updated particle tracking and CFD-Post particle-track visualization.

## Source
- Primary: [user-cyclone-workbench-rng-dpm-settings-report](../sources/user-cyclone-workbench-rng-dpm-settings-report.md)

## Reported vs Inferred vs Assumed
- `Reported`: value or operation appears in the user-provided settings report.
- `Inferred`: practical implementation sequence assembled from the report.
- `Assumed`: fallback for unreported Fluent, meshing, or DPM controls.

## Step-by-Step Build Order
1. In ANSYS Workbench, add a Fluid Flow (Fluent) system.
2. Import the AutoCAD cyclone geometry into SpaceClaim.
3. Use Prepare > Volume Extract to select inlet/outlet enclosing edges and create the internal fluid volume.
4. Remove the solid body after extracting the flow volume.
5. Save the extracted volume and update the Workbench geometry cell.
6. Open Meshing, generate an initial mesh, then change the method to Tetrahedron.
7. Set mesh element size to 1e-2 (`Reported`; units not specified) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
8. Create named selections for inlet, outlets, and walls.
9. Launch Fluent in double precision.
10. Enable gravity, energy, RNG k-epsilon, swirl-dominated option, and DPM interaction/source updates.
11. Create a surface DPM injection at the inlet using ash solid particles.
12. Set SIMPLE and second-order upwind schemes for k and epsilon.
13. Use Standard Initialization and run 1000 iterations.
14. Export Particle History Data and visualize particle tracks in CFD-Post.

## A) Geometry and Domain
- Geometry family: cyclone separator with inlet, outlets, walls, and internal flow region (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- CAD source: AutoCAD geometry imported into SpaceClaim (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Domain extraction: use Volume Extract under the SpaceClaim Prepare tab and select inlet/outlet edges enclosing the flow region (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Why this matters: the simulation only needs the flow inside the separator, so the solid design is removed after the internal volume is extracted (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## B) Physics and Models
- Precision: double precision (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Gravity: -9.81 m/s^2 on Z axis (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Energy equation: on (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Turbulence model: RNG k-epsilon (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Viscous option: Swirl Dominated Zone (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM interaction: Interaction with Continuous Phase enabled (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM source coupling: Update DPM Sources enabled (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Why this matters: RNG k-epsilon is presented in the report as improving rotating-flow accuracy, while the swirl-dominated option is selected because cyclone flow is governed by swirl (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## C) Materials and Operating Inputs
- Particle material: ash solid, selected as closest available material to dust particles (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Particle diameter: 5e-6 m (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Particle injection temperature: 323.5 K (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Particle mass flow rate: 1e-6 kg/s (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Continuous fluid material, operating pressure, and full thermal condition are not reported (`Missing`).

## D) Boundary and Initial Conditions
- Named selections: inlet, outlets, and walls (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Inlet continuous-phase BC: velocity magnitude, momentum, and thermal properties set to match injection settings (`Reported`; exact fluid values incomplete) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM injection type: Surface injection from inlet (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM particle velocity: -8 m/s on X axis, with the negative sign defining tangential direction (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM diameter distribution: Uniform (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM inlet boundary condition: Reflect (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Initialization: Standard Initialization (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## E) Mesh and Numerics
### Meshing
- Initial mesh covers the whole cyclone separator (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Mesh method changed from Automatic to Tetrahedron (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Element size: 1e-2 (`Reported`; units not specified) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Mesh updated before proceeding to Fluent (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Mesh quality metrics and final cell count are not reported (`Missing`).

### Solver and Schemes
- Pressure-velocity coupling: SIMPLE (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Turbulent kinetic energy: Second Order Upwind (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Turbulent dissipation rate: Second Order Upwind (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Momentum, pressure, gradient, energy, and DPM tracking numerics are not fully reported (`Missing`).
- Iterations: 1000 (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## F) DPM and Results Workflow
1. Enable DPM interaction with continuous phase (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
2. Enable Update DPM Sources (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
3. Create inlet surface injection with ash solid particles (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
4. Use uniform 5e-6 m particles at -8 m/s X velocity, 323.5 K, and 1e-6 kg/s mass flow (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
5. Export Particle History Data for CFD-Post (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
6. In CFD-Post, set wall transparency to 0.643 (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
7. Import the particle track file and color by ash solid particle pipe (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
8. Use 729 animation frames for the final particle-motion video (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## Missing Info
- Exact cyclone dimensions, CAD scale, and extracted volume checks.
- Mesh quality, cell count, and mesh independence evidence.
- Continuous-phase velocity magnitude and turbulence inputs.
- Fluid material, pressure, and thermal boundary values.
- Wall and outlet DPM boundary behavior.
- Particle material density and drag-law settings.
- Residual convergence criteria and monitor definitions.
- Quantitative pressure drop, particle collection, or separation efficiency.

## Assumptions
- Treat element size 1e-2 as geometry-unit dependent and verify physical scale before interpreting results (`Assumed`, `High Risk`).
- Treat Update DPM Sources as intentional two-way coupling, but verify particle mass loading is high enough for source updates to matter (`Inferred`, `Medium Risk`).
- Use this setup as a tutorial/visualization workflow until quantitative validation exists (`Assumed`, `Medium Risk`).
- Inspect DPM inlet `Reflect` behavior because an inlet reflection setting can create confusing particle behavior if the injection boundary is also used for flow entry (`Assumed`, `Medium Risk`).

## Sensitivity Plan (Run First)
1. Mesh element size sensitivity around inlet, cone, and outlet.
2. RNG k-epsilon swirl-dominated option on/off comparison.
3. One-way DPM vs interaction/source-updated DPM comparison.
4. DPM inlet boundary condition check.
5. Particle diameter sensitivity around 5e-6 m.

## Common Failure Modes
- Solid geometry is meshed instead of the extracted internal fluid volume.
- Named selections are missing, causing inlet/outlet/wall BCs to be assigned incorrectly in Fluent.
- Energy equation is enabled but thermal boundary conditions are incomplete.
- DPM source updates are enabled even though the particle mass loading is too low to justify coupled feedback.
- Particle tracks look plausible in CFD-Post but no quantitative collection metric is computed.

## Quick Diagnostics
- Verify the extracted volume is watertight and represents only the flow domain.
- Check mesh quality and element size near tangential inlet and vortex finder.
- Confirm inlet velocity direction matches the intended negative X tangential entry.
- Monitor residuals plus at least one pressure or velocity integral, not only iteration count.
- Inspect particle tracks for artificial reflection at the inlet.

## Cross-Paper Linkage
- Related cyclone setup: [cyclone-separator-icem-hexa-rsm-dpm-exemplar](cyclone-separator-icem-hexa-rsm-dpm-exemplar.md).
- Related geothermal baseline: [geothermal-boc-separator-fluent-2013-baseline](geothermal-boc-separator-fluent-2013-baseline.md).
- Related entities:
  - [geometry-tangential-inlet-cyclone-separator](../entities/geometry-tangential-inlet-cyclone-separator.md)
  - [turbulence-rng-k-epsilon](../entities/turbulence-rng-k-epsilon.md)
  - [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
- Relation to ICEM/RSM exemplar: `differs` by using Workbench tetra meshing and RNG k-epsilon rather than ICEM hexa blocking and RSM.
- Reuse guidance: copy the Workbench volume-extraction flow and named-selection discipline; compare RNG with RSM if final swirl accuracy or pressure drop matters.

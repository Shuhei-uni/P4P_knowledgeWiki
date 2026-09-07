# Setup: Cyclone Separator SolidWorks Flow Simulation + Particle Study Exemplar

## Purpose
Reusable beginner-oriented setup sheet for a cyclone separator study in SolidWorks Flow Simulation, including a post-flow Particle Study to compare how particle diameter affects top escape versus bottom accumulation.

Use this as an exemplar when a future separator case needs:
- A quick SolidWorks-native internal-flow cyclone simulation.
- A fan-assisted rotating region at the top of the separator.
- Particle-size comparison without building a Fluent DPM case.

## Source
- Primary: [user-cyclone-solidworks-flow-particle-study-report](../sources/user-cyclone-solidworks-flow-particle-study-report.md)

## Reported vs Inferred vs Assumed
- `Reported`: value or operation appears in the user-provided settings report.
- `Inferred`: practical implementation sequence assembled from the report.
- `Assumed`: fallback where SolidWorks solver, mesh, or particle settings are incomplete.

## Step-by-Step Build Order
1. Start a SolidWorks Flow Simulation project with the Project Wizard.
2. Name the project `Project 2` (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
3. Use SI units, with temperature in deg C and angular velocity in RPM.
4. Select Internal Analysis and exclude cavities without flow conditions.
5. Enable gravity and set -9.81 m/s^2 along Y.
6. Enable rotation because a top fan is included.
7. Select air as the only fluid.
8. Set thermodynamic parameters to 20 deg C and 101325 Pa.
9. Use a segmented/cut view to apply internal boundary conditions.
10. Add the top rotating fan region at 1000 RPM, using a negative sign for anti-clockwise direction.
11. Set the inlet velocity to 60 m/s.
12. Set top and bottom exits to atmospheric static pressure.
13. Add surface goals for average fluid velocity at both exits.
14. Set global mesh refinement level to 3.
15. Solve the flow case to convergence.
16. Start a Particle Study from the solved flow field.
17. Use 100 iron particles released from the inlet face at 1 kg/s, with Ideal Reflection and accretion/erosion enabled.
18. Compare particle diameters 1e-5 m and 1e-4 m.
19. Post-process with cut plots, surface plots, flow trajectories, and surface parameters.

## A) Geometry and Domain
- Geometry family: cyclone separator with top and bottom exits and a top fan-assisted rotating region (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Analysis type: internal analysis (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Cavities without flow conditions: excluded (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Internal surfaces: selected using a segmented/cut view (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## B) Physics and Models
- Fluid: air only (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Gravity: -9.81 m/s^2 along Y (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Rotation: enabled (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Rotating region: top fan location, 1000 RPM with negative sign for anti-clockwise direction (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Particle Study wall interaction: Ideal Reflection (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Particle Study physical effects: accretion and erosion enabled (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Turbulence model and wall treatment are not exposed in the provided report (`Missing`).

## C) Materials and Operating Inputs
- Unit system: SI (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Temperature unit: deg C (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Angular velocity unit: RPM (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Temperature: 20 deg C (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Pressure: 101325 Pa (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Particle material: iron solid (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Particle mass flow rate: 1 kg/s (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## D) Boundary Conditions and Goals
- Inlet velocity: 60 m/s at entry location (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Top exit static pressure: atmospheric pressure (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Bottom exit static pressure: atmospheric pressure (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Surface goal 1: average fluid velocity at top exit (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Surface goal 2: average fluid velocity at bottom exit (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Why this matters: goals make outlet performance values available during and after the solve (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## E) Mesh and Solve
- Global mesh: manually edited to refinement level 3 (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Why this matters: the report states higher refinement was used for more accurate results (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Solver run: run until mesh is captured and convergence is reached (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Observed velocity result: top exit approximately 218 m/s and bottom exit approximately 70 m/s, with the top fan causing higher top-exit velocity (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Missing: final mesh count, mesh quality, solver residuals, and goal convergence tolerances.

## F) Particle Study Workflow
1. Start Particle Study after the fluid solution is available (`Inferred`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
2. Increase particle count from default 20 to 100 (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
3. Set material to iron solid (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
4. Inject particles from the inlet face (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
5. Set mass flow rate to 1 kg/s (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
6. Set wall interaction to Ideal Reflection because solid iron particles are assumed to bounce off walls (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
7. Enable accretion and erosion effects (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
8. Run particle diameter case 1: 1e-5 m (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
9. Run particle diameter case 2: 1e-4 m (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## G) Particle Study Results
- Small-particle case: diameter 1e-5 m, 11 particles accumulated at the bottom, 89 particles escaped through the top (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Large-particle case: diameter 1e-4 m, 23 particles accumulated at the bottom, with a higher mass accumulation rate than the smaller-particle case (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Trend: larger particles accumulated more at the bottom because cyclone centrifugal forces separated them more effectively (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## H) Post-Processing
- Cut plots: velocity and pressure distribution across the front plane (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Surface plots: confirm exit pressure matches atmospheric pressure (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Flow trajectories: arrows with 0.03 m diameter to show circular motion and separation (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Surface parameters: extract number of particles accumulated and mass erosion/accumulation rates (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Export: surface-parameter data can be exported to Excel for comparison and optimization (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## Missing Info
- Geometry dimensions, fan details, and outlet areas.
- Whether rotating region corresponds to fan geometry, rotating frame, or simplified fan model.
- SolidWorks solver turbulence and wall settings.
- Mesh statistics and local refinement controls.
- Convergence criteria for goals and residuals.
- Full particle release distribution and time/step controls.
- Exact mass accumulation and erosion-rate values.

## Assumptions
- Use this as a qualitative SolidWorks particle-diameter sensitivity workflow, not a validated cyclone efficiency model (`Assumed`, `Medium Risk`).
- Treat the 1000 RPM top rotation as a fan-assisted design-specific feature, not a general cyclone separator default (`Assumed`, `Medium Risk`).
- Keep particle count fixed when comparing diameters, because changing count and diameter together would confound the trend (`Assumed`, `Medium Risk`).

## Sensitivity Plan (Run First)
1. Mesh refinement level 2, 3, and 4 comparison.
2. Rotating region speed/sign comparison.
3. Particle count 100 versus a larger count.
4. Diameter sweep between 1e-5 m and 1e-4 m.
5. Wall interaction model comparison if collection rather than rebound is physically expected.

## Common Failure Modes
- Surface goals are placed on the wrong internal surfaces because the model is not cut/segmented during setup.
- Fan rotation sign is reversed, changing the cyclone flow direction.
- Atmospheric pressure exits are not both assigned, causing unrealistic outlet behavior.
- Particle-count results are overinterpreted as validated efficiency.
- Ideal Reflection prevents realistic sticking/collection if the real separator should trap particles.

## Quick Diagnostics
- Confirm surface goals at top and bottom exits before solving.
- Check that top exit velocity increases when the fan region is active.
- Confirm pressure surface plots show atmospheric pressure at both exits.
- Compare top escape and bottom accumulation counts for each particle diameter.
- Export surface parameters to a spreadsheet only after verifying particle release count and wall interaction settings.

## Cross-Paper Linkage
- Related SolidWorks entity: [solidworks-flow-simulation-particle-study](../entities/solidworks-flow-simulation-particle-study.md).
- Related cyclone geometry: [geometry-tangential-inlet-cyclone-separator](../entities/geometry-tangential-inlet-cyclone-separator.md).
- Related Fluent cyclone setup: [cyclone-separator-workbench-tetra-rng-dpm-exemplar](cyclone-separator-workbench-tetra-rng-dpm-exemplar.md).
- Related Fluent ICEM/RSM setup: [cyclone-separator-icem-hexa-rsm-dpm-exemplar](cyclone-separator-icem-hexa-rsm-dpm-exemplar.md).
- Relation to Fluent exemplars: `differs` because it uses SolidWorks Flow Simulation and Particle Study rather than Fluent DPM.
- Reuse guidance: use this for quick CAD-native qualitative particle-size studies; use Fluent setups for deeper control of turbulence model, wall particle boundary behavior, and solver numerics.

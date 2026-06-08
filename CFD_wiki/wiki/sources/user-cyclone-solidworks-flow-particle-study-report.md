# Source: Cyclone Separator SolidWorks Flow Simulation Particle Study Report

## Source Metadata
- Source ID: `user-cyclone-solidworks-flow-particle`
- Source type: user-provided settings report
- Toolchain: SolidWorks Flow Simulation and SolidWorks Particle Study
- Citation note: this page is based on user-provided setup notes, not an independently verified paper or full transcript. Values below should be cited as `Reported` from `user-cyclone-solidworks-flow-particle` only within that limitation.

## One-Page Summary
This settings report describes a SolidWorks Flow Simulation cyclone separator workflow. The flow simulation is created with the Project Wizard as an internal air analysis with gravity, a rotating top fan region, inlet velocity, atmospheric-pressure exits, manual mesh refinement, and surface goals for outlet velocities. A separate particle study then compares iron particles with diameters 1e-5 m and 1e-4 m to see how many leave through the top exit versus accumulate at the bottom.

The most reusable lessons are:
- SolidWorks Flow Simulation uses a wizard-driven internal-flow setup rather than the Fluent setup tree.
- A rotating top fan region can strongly change outlet velocities.
- Particle Study is run after the solved flow field and can compare particle size effects.
- Larger particles accumulated more at the bottom in the reported comparison, consistent with stronger centrifugal separation.

## A) Study Scope
- Objective: simulate cyclone separator fluid flow and particle separation using SolidWorks Flow Simulation, then compare separation behavior for different particle diameters (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Software scope: SolidWorks Flow Simulation, not ANSYS Fluent (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Analysis type: internal analysis, excluding cavities without flow conditions (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Target outputs: top and bottom exit average fluid velocities, pressure/velocity plots, particle path behavior, particle accumulation count, and erosion/accretion rates (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## B) Physics and Models
- Fluid: air only (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Gravity: enabled, -9.81 m/s^2 along the Y axis (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Rotation: enabled because a fan is included at the top to improve separator performance (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Rotating region: top fan region, 1000 RPM, negative sign for anti-clockwise direction (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Turbulence model, wall treatment, and numerical schemes are not reported because the workflow is described at the SolidWorks Flow Simulation wizard level (`Missing`).

## C) Material and Operating Conditions
- Unit system: SI, with temperature in deg C and angular velocity in RPM (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Thermodynamic state: 20 deg C and 101325 Pa (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Particle material: iron solid (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Particle mass flow rate: 1 kg/s (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## D) Boundary and Initial Conditions
- Inlet velocity: 60 m/s at the entry location (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Static pressure: atmospheric pressure at both top and bottom exits (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Surface goals: average fluid velocity at top and bottom exits (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Segmented/cut view: used to apply conditions to internal surfaces (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Initial field values are not reported (`Missing`).

## E) Mesh and Numerics
- Global mesh: manually edited to refinement level 3 (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Solver execution: run until mesh is captured and convergence is reached (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Final mesh count, mesh quality, stopping criteria, and residual/goal convergence tolerances are not reported (`Missing`).

## F) Validation and Results
- Reported fluid-flow observation: top exit velocity approximately 218 m/s and bottom exit velocity approximately 70 m/s, with the top fan driving the higher top-exit velocity (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Study 1 particle diameter: 1e-5 m (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Study 1 result: 11 particles accumulated at the bottom and 89 particles escaped through the top exit (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Study 2 particle diameter: 1e-4 m (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Study 2 result: 23 particles accumulated at the bottom, with a higher mass accumulation rate than the smaller-particle case (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Interpretation: larger particles accumulated more at the bottom because they are more easily separated by centrifugal forces (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- External validation against experiment is not reported (`Missing`).

## G) Reproducibility Risk
### Missing Parameter List
- Exact cyclone geometry and fan geometry.
- Whether fan rotation is a real rotating region, a local rotating frame, or simplified fan treatment.
- Solver convergence tolerances and goal convergence settings.
- Final mesh statistics and local refinement settings.
- Particle release distribution across the inlet face.
- Wall roughness and detailed rebound/accretion/erosion settings.
- Quantitative mass accumulation/erosion rates, beyond the reported particle counts.

### Assumptions Used in This Wiki
- Treat the 1000 RPM rotating region as a setup feature specific to this fan-assisted cyclone, not a default cyclone separator assumption (`Assumed`, `Medium Risk`).
- Treat the reported top/bottom particle counts as tutorial output, not validated separator efficiency (`Assumed`, `Medium Risk`).
- Convert the particle-count interpretation into a qualitative trend only unless the same particle count, mass flow, and release distribution are used (`Assumed`, `Medium Risk`).

### Confidence Rating
`Medium` for SolidWorks workflow transfer; `Low-Medium` for quantitative reproduction because geometry, mesh statistics, convergence controls, and detailed particle-study settings are incomplete.

### Minimal Sensitivity Tests
1. Global mesh refinement level 3 versus adjacent refinement levels.
2. Fan rotating-region speed and sign sensitivity.
3. Particle count sensitivity: 100 versus larger counts.
4. Particle diameter sweep between 1e-5 m and 1e-4 m.
5. Ideal Reflection versus other available wall-interaction models if physical collection is the target.

## H) Cross-Paper Linkage
- Closest related pages:
  - [cyclone-separator-solidworks-flow-particle-study-exemplar](../setups/cyclone-separator-solidworks-flow-particle-study-exemplar.md)
  - [cyclone-separator-workbench-tetra-rng-dpm-exemplar](../setups/cyclone-separator-workbench-tetra-rng-dpm-exemplar.md)
  - [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md)
  - [solidworks-flow-simulation-particle-study](../entities/solidworks-flow-simulation-particle-study.md)
- Relations:
  - `extends`: adds a non-Fluent cyclone workflow using SolidWorks Flow Simulation.
  - `differs`: uses fan-assisted rotation and SolidWorks Particle Study instead of Fluent DPM.
  - `supports`: reinforces particle diameter as a first-order separator-performance sensitivity.
- Reuse recommendation:
  - Copy the SolidWorks wizard sequence for quick qualitative cyclone studies.
  - Use Fluent exemplars when solver-level turbulence, DPM boundary behavior, or pressure-drop numerics need deeper control.

# Source: Cyclone Separator Workbench Fluent RNG-DPM Settings Report

## Source Metadata
- Source ID: `user-cyclone-workbench-rng-dpm`
- Source type: user-provided settings report
- Toolchain: ANSYS Workbench, SpaceClaim, ANSYS Meshing, Fluent, CFD-Post
- Citation note: this page is based on user-provided setup notes, not an independently verified paper or full tutorial transcript. Values below should be cited as `Reported` from `user-cyclone-workbench-rng-dpm` only within that limitation.

## One-Page Summary
This settings report describes a Workbench-based cyclone separator workflow: import AutoCAD geometry into SpaceClaim, extract the internal fluid volume, generate a tetrahedral mesh, solve in Fluent with double precision, gravity, energy equation, RNG k-epsilon with swirl-dominated option, and DPM particle injections using ash solid particles.

The most reusable lessons are:
- Extract the flow volume first so Fluent receives the internal fluid domain rather than the solid cyclone body.
- Use named selections for inlet, outlet, and walls before entering Fluent.
- Enable RNG k-epsilon with swirl-dominated treatment for a lower-cost cyclone setup than RSM.
- Enable DPM interaction with the continuous phase and update DPM sources when particle-fluid coupling is intended.

## A) Study Scope
- Objective: simulate fluid and particle flow inside a cyclone separator using Workbench, SpaceClaim, Fluent, and CFD-Post (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Geometry source: cyclone separator originally created in AutoCAD and imported into SpaceClaim (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Domain scope: internal extracted fluid volume; solid design body removed after flow-volume extraction (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Target outputs: particle history data and particle-track visualization in CFD-Post (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## B) Physics and Models
- Solver launch precision: double precision (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Gravity: -9.81 m/s^2 on the Z axis (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Energy equation: on, to include temperature effects (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Turbulence model: RNG k-epsilon (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Viscous option: Swirl Dominated Zone (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM: particle injection with interaction with continuous phase enabled and DPM sources updated (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## C) Material and Operating Conditions
- Continuous-phase material and detailed thermophysical properties are not reported (`Missing`).
- Particle material: ash solid, chosen as the closest available material to dust particles (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Particle temperature: 323.5 K (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Fluid operating temperature and inlet thermal condition are not fully reported (`Missing`).

## D) Boundary and Initial Conditions
- Named selections: inlet, outlets, and walls (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Inlet BC: velocity magnitude, momentum, and thermal properties set to match injection settings (`Reported`, exact continuous-phase values incomplete) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM boundary at inlet: Reflect (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM injection type: Surface injection starting at the inlet (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM injection velocity: -8 m/s on the X axis (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM diameter distribution: Uniform (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM particle diameter: 5e-6 m (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- DPM mass flow rate: 1e-6 kg/s (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Initialization: Standard Initialization (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## E) Mesh and Numerics
- Geometry preparation: SpaceClaim Volume Extract from inlet/outlet enclosing edges, then saved back to the Workbench geometry cell (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Mesh method: Tetrahedron, changed from automatic method (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Mesh element size: 1e-2 (`Reported`; units not specified) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Boundary naming: inlet, outlets, and walls named before setup (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Pressure-velocity coupling: SIMPLE (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Turbulent kinetic energy and turbulent dissipation rate schemes: Second Order Upwind (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Momentum, pressure interpolation, gradient, energy, and DPM tracking numerics are not fully reported (`Missing`).
- Run length: 1000 iterations (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## F) Validation and Results
- Particle History Data exported for CFD-Post visualization (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- CFD-Post wall transparency: 0.643 (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Particle track file imported into CFD-Post (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- CFD-Post color variable: ash solid particle pipe (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Animation frames: 729 (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Quantitative validation targets, pressure drop, collection efficiency, and residual convergence evidence are not reported (`Missing`).

## G) Reproducibility Risk
### Missing Parameter List
- Exact cyclone dimensions and CAD scale.
- Mesh element-size units and final mesh quality metrics.
- Continuous-phase inlet velocity, turbulence intensity, hydraulic diameter, and temperature values.
- Wall DPM behavior at collection/outlet surfaces.
- Particle material density and drag law.
- DPM tracking step controls, stochastic tracking, and parcel count.
- Residual target and monitor-based convergence criteria.

### Assumptions Used in This Wiki
- Interpret mesh size 1e-2 in the active Workbench geometry units and verify scale before relying on results (`Assumed`, `High Risk`).
- Treat the DPM source-update settings as intended two-way particle-fluid coupling, but check particle mass loading before assuming coupling is physically important (`Inferred`, `Medium Risk`).
- Treat the DPM inlet `Reflect` note as a reported GUI setting, but verify it does not cause nonphysical particle behavior at the injection boundary (`Assumed`, `Medium Risk`).
- Use this setup for tutorial-style visualization and first-pass cyclone studies, not validated performance prediction (`Assumed`, `Medium Risk`).

### Confidence Rating
`Medium` for Workbench/SpaceClaim/Fluent setup sequence; `Low-Medium` for exact numerical reproduction because geometry, mesh quality, continuous-phase BCs, and DPM controls are incomplete.

### Minimal Sensitivity Tests
1. Mesh element size and tetra quality sensitivity.
2. RNG k-epsilon swirl-dominated option on/off comparison.
3. DPM one-way vs source-updated coupling comparison.
4. Particle diameter 5e-6 m sensitivity against at least one larger and one smaller size.
5. Inlet DPM boundary behavior check, especially if reflected particles appear near the inlet.

## H) Cross-Paper Linkage
- Closest related pages:
  - [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md)
  - [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)
  - [turbulence-rng-k-epsilon](../entities/turbulence-rng-k-epsilon.md)
  - [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
- Relations:
  - `extends`: adds a Workbench/SpaceClaim volume-extraction and tetra-mesh cyclone workflow.
  - `differs`: uses RNG k-epsilon with swirl-dominated option rather than RSM used by the ICEM hexa tutorial.
  - `supports`: reinforces DPM surface injection as a reusable cyclone particle-tracking pattern.
- Reuse recommendation:
  - Copy the Workbench geometry preparation and named-selection flow for beginner setup.
  - Adapt turbulence model choice after comparing against the RSM/hexa exemplar for swirl fidelity and convergence robustness.

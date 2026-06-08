# Source: Cyclone Separator ICEM Hexa Mesh and Fluent RSM-DPM Exemplar

## Source Metadata
- Source ID: `youtube-cyclone-icem-fluent`
- Source type: YouTube tutorial / user-provided extraction notes
- URL: https://youtu.be/ZW6-yBWAhZk
- Toolchain: CAD/IGS geometry, ICEM CFD blocking/meshing, ANSYS Fluent
- Citation note: this page is based on user-provided notes from the video, not a peer-reviewed paper. Values below should be cited as `Reported` from `youtube-cyclone-icem-fluent` only within that limitation.

## One-Page Summary
This tutorial-style source demonstrates a full cyclone separator CFD workflow: import a CAD cyclone as IGS geometry, create plane-and-layer blocking in ICEM CFD for a hexahedral mesh, solve high-swirl air flow in Fluent with the Reynolds Stress Model (RSM), then evaluate limestone particle collection with the Discrete Phase Model (DPM).

The most reusable lessons are:
- Use structured blocking and O-grid splits to control cyclone wall, cone, inlet, and vortex-finder topology.
- Use RSM rather than basic two-equation RANS models for strong solid-body rotation and free-vortex behavior.
- Treat the dustbin wall as `Trap` in DPM so collected particles are counted.
- Switch from steady to transient solution stepping if RSM convergence fluctuates.

## A) Study Scope
- Objective: build a cyclone separator CFD case with geometry preparation, hexahedral meshing, continuous air-flow solution, DPM limestone particle tracking, separation efficiency, and pressure-drop post-processing (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Geometry: 3D cyclone separator imported from SolidEdge as an IGS file; includes 360 degree rotational cyclone body and tangential inlet (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Main modeled features: tangential inlet, vortex finder, conical body, dustbin/wall collection boundary, and fluid cell zones (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Target outputs: particle trapped/escaped/incomplete counts, separation efficiency, total pressure drop, and particle animation (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## B) Physics and Models
- Flow assumption: cyclone air flow with strong swirl; compressibility and heat transfer treatment are not reported (`Missing`).
- Turbulence model: Reynolds Stress Model (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Near-wall treatment: Standard Wall Functions (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Multiphase/particle model: Fluent DPM for inert limestone particles (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Particle density: 2770 kg/m^3 (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Baseline particle diameter: 1 micrometer (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Demonstration particle distribution: Rosin-Rammler with 1, 5, and 10 micrometer diameters for unsteady particle-tracking visualization (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## C) Material and Operating Conditions
- Continuous fluid: air (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Particle material: limestone (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Gravity: -9.81 m/s^2 in the Z direction (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Operating pressure, temperature, and detailed material-property values are not reported (`Missing`).

## D) Boundary and Initial Conditions
- Inlet boundary: velocity inlet (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Inlet velocity: 12.69 m/s (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Inlet turbulence specification: intensity and hydraulic diameter; hydraulic diameter 0.127 m (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Outlet boundary: pressure outlet (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Outlet turbulence specification: intensity and hydraulic diameter; hydraulic diameter 0.15 m (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Wall material: steel (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- DPM wall condition at wall dustbin: `Trap` (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Initialization: Hybrid Initialization (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Initialized primitive-field values are not reported (`Missing`).

## E) Mesh and Numerics
- Mesh approach: hexahedral mesh from ICEM CFD using plane-and-layer blocking (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Geometry preparation:
  - points created on quadrant and midpoint locations of cyclone circles (`Reported`);
  - points projected to curves for blocking accuracy (`Reported`);
  - seven planes defined along cyclone height from outlet to bottom (`Reported`);
  - planes 6 and 7 scaled by X and Y factors of 0.45 for cone dimensions (`Reported`);
  - parts named for tangential inlet, vortex finder, and planes (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Blocking:
  - one initial large block (`Reported`);
  - three O-grid splits through wall-crossing blocks (`Reported`);
  - Z-direction splits at each plane height (`Reported`);
  - vertices/edges associated to points/curves and cone vertices snapped at planes 6 and 7 (`Reported`);
  - inlet block created by splitting an existing block and extruding a face to tangential inlet points (`Reported`);
  - vortex finder blocks assigned to a solid part and excluded from fluid calculation (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Surface mesh max size: 0.017 (`Reported`; units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Fluid edges: 25 nodes (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Wall prism-layer-style edge refinement: 22 nodes, initial spacing 0.03, growth ratio 1.1 or 1.2 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Vortex finder: 11 nodes with spacing 0.025 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Vortex finder end: 26 nodes with spacing 0.03 (`Reported`; spacing units not specified) ([youtube-cyclone-icem-fluent], user-provided notes).
- Mesh quality check: Determinant 2x2x2 criterion (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Mesh export: unstructured `.msh` for Fluent (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Solver family, pressure-velocity coupling, spatial discretization schemes, and under-relaxation factors are not reported (`Missing`).

## F) Validation and Results
- Separation efficiency definition: trapped / (injected - incomplete) (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Pressure-drop post-processing: total pressure via Volume Integrals over fluid cell zones (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Particle outcomes:
  - `Trapped`: particles reaching dustbin wall (`Reported`);
  - `Escaped`: particles exiting vortex finder (`Reported`);
  - `Incomplete`: particles in infinite-loop-like tracking state, subtracted from efficiency denominator (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Experimental validation data are mentioned for inlet velocity but full validation target and comparison error are not reported (`Missing`).

## G) Reproducibility Risk
### Missing Parameter List
- Exact cyclone dimensions and CAD file are missing.
- Units for several ICEM mesh spacing values are missing.
- Residual histories, final monitors, and pressure-drop values are missing.
- Solver coupling and discretization schemes are missing.
- DPM parcel count, drag law, stochastic tracking settings, max tracking steps, and coupling mode are missing.
- Inlet/outlet turbulence intensities are missing.

### Assumptions Used in This Wiki
- Treat the case as incompressible, isothermal air flow unless Mach number or heat-transfer evidence appears (`Assumed`, `Medium Risk`).
- Use Fluent defaults for unreported DPM drag and particle tracking controls for the first reconstruction (`Assumed`, `Medium Risk`).
- Use conservative second-order spatial schemes only after first achieving a stable RSM solution (`Assumed`, `Medium Risk`).
- Interpret unspecified ICEM spacing values as geometry-unit values from the imported CAD scale, not universal SI defaults (`Assumed`, `High Risk`).

### Confidence Rating
`Medium` for workflow structure and model-selection lessons; `Low-Medium` for exact numerical reproduction because the source is a video-derived tutorial summary with missing dimensions and solver numerics.

### Minimal Sensitivity Tests
1. RSM steady vs transient solution schedule.
2. Vortex-finder mesh refinement because the source states it dominates pressure-drop losses.
3. Wall-layer growth ratio 1.1 vs 1.2 and first spacing sensitivity.
4. DPM incomplete-particle sensitivity to tracking step controls and particle diameter.

## H) Cross-Paper Linkage
- Closest related pages:
  - [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)
  - [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
  - [mesh-inflation-boundary-layer](../concepts/mesh-inflation-boundary-layer.md)
- Relations:
  - `extends`: adds a tutorial-style ICEM hexa blocking workflow for tangential-inlet cyclone separators.
  - `contradicts`/`differs`: recommends RSM over simpler two-equation RANS for this cyclone tutorial, while the geothermal Purnanto baseline used RNG k-epsilon.
  - `supports`: reinforces that incomplete particle counts must be tracked explicitly when computing efficiency.
- Reuse recommendation:
  - Copy the ICEM blocking and Fluent RSM-DPM logic for future generic cyclone separator cases.
  - Adapt boundary values only after matching geometry scale and experimental operating conditions.
  - Avoid treating this as a validated geothermal separator setup without additional source evidence.

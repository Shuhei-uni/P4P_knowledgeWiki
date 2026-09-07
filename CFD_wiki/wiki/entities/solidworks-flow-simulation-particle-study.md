# Entity: SolidWorks Flow Simulation Particle Study

## Definition
SolidWorks-native workflow where a solved Flow Simulation case is followed by a Particle Study to trace solid particles through the computed flow field.

This is related to Fluent DPM in purpose, but it is not the same software model or setup interface.

## Usage in Wiki
- Used in the SolidWorks cyclone separator exemplar to compare iron particles with diameters 1e-5 m and 1e-4 m after solving an internal air-flow case with gravity and a rotating top fan (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## Reusable Setup Notes
- Define flow boundary conditions and goals first, solve the fluid case, then run Particle Study.
- Particle count can be increased from the default; the exemplar uses 100 particles (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Wall interaction can be set to Ideal Reflection when particles are assumed to rebound rather than stick (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Accretion and erosion options can be enabled to report accumulation/erosion-related outputs (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).

## Known Risk
- Particle-count results are sensitive to release count and release distribution.
- Ideal Reflection may be inappropriate when the real separator should trap dust at walls or in a collection bin.
- Fan-assisted rotation can dominate separator behavior, so results may not transfer to passive cyclone geometries.

## Linked Sources
- [user-cyclone-solidworks-flow-particle-study-report](../sources/user-cyclone-solidworks-flow-particle-study-report.md)

## Linked Setups
- [cyclone-separator-solidworks-flow-particle-study-exemplar](../setups/cyclone-separator-solidworks-flow-particle-study-exemplar.md)

## Relation to Fluent DPM
- [multiphase-dpm-particle-tracking](multiphase-dpm-particle-tracking.md): similar engineering question, different solver and particle-study controls. Relation: `differs`.

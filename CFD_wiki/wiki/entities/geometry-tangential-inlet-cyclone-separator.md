# Entity: Tangential-Inlet Cyclone Separator Geometry

## Definition
Generic cyclone separator geometry with a tangential inlet, cylindrical/conical body, vortex finder, and lower collection/dustbin region.

## Why It Matters
This geometry family creates a strong swirling flow. Particles or dense phases migrate outward toward walls while cleaner gas exits through the vortex finder.

## Known Variants in Wiki
- Generic air/limestone cyclone tutorial with tangential inlet and vortex finder: [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md) (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Generic Workbench/SpaceClaim cyclone tutorial with extracted internal flow volume, tetra mesh, RNG k-epsilon, and ash particle DPM: [cyclone-separator-workbench-tetra-rng-dpm-exemplar](../setups/cyclone-separator-workbench-tetra-rng-dpm-exemplar.md) (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Generic SolidWorks Flow Simulation cyclone tutorial with top fan rotation and particle-diameter comparison: [cyclone-separator-solidworks-flow-particle-study-exemplar](../setups/cyclone-separator-solidworks-flow-particle-study-exemplar.md) (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- Geothermal vertical BOC cyclone-like separator variants: Bangma tangential inlet, Lazalde-Crabtree tangential inlet, and spiral-inlet design in [geometry-vertical-boc-cyclone-separator](geometry-vertical-boc-cyclone-separator.md).

## Reusable Setup Notes
- Tangential inlet topology needs local blocking/refinement because it drives the incoming swirl.
- Vortex finder resolution is pressure-drop critical in the tutorial source (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- For Workbench workflows, extract the internal fluid volume before meshing so the solid cyclone body does not become the computational domain (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- Fan-assisted SolidWorks cyclone cases should not be treated as passive cyclone defaults because the rotating region can dominate top-exit velocity (`Reported`) ([user-cyclone-solidworks-flow-particle], user-provided settings report).
- The cone and dustbin/collection wall need correct particle boundary behavior when DPM efficiency is the output.

## Linked Sources
- [youtube-cyclone-separator-icem-fluent-exemplar](../sources/youtube-cyclone-separator-icem-fluent-exemplar.md)
- [user-cyclone-workbench-rng-dpm-settings-report](../sources/user-cyclone-workbench-rng-dpm-settings-report.md)
- [user-cyclone-solidworks-flow-particle-study-report](../sources/user-cyclone-solidworks-flow-particle-study-report.md)

## Linked Setups
- [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md)
- [cyclone-separator-workbench-tetra-rng-dpm-exemplar](../setups/cyclone-separator-workbench-tetra-rng-dpm-exemplar.md)
- [cyclone-separator-solidworks-flow-particle-study-exemplar](../setups/cyclone-separator-solidworks-flow-particle-study-exemplar.md)
- [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)

## Open Questions
- How transferable is the tutorial RSM setup to geothermal steam/brine separator cases?
- What vortex-finder mesh resolution is needed before pressure-drop results become mesh independent?

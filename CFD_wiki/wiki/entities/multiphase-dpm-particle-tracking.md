# Entity: DPM Particle Tracking Workflow

## Definition
Post-convergence particle-injection workflow for estimating separator carryover/collection behavior.

## Usage in Wiki
- Particle tracking with DPM is reported after converged flow solution in `purnanto-2013` ([purnanto-2013], p.4, p.8).
- DPM is used in the cyclone separator tutorial to inject inert limestone particles from the inlet, then classify outcomes as trapped, escaped, or incomplete (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- DPM is used in the Workbench cyclone settings report with inlet surface injection, ash solid particles, uniform 5e-6 m diameter, -8 m/s X velocity, 323.5 K, 1e-6 kg/s mass flow, interaction with continuous phase, and Update DPM Sources enabled (`Reported`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).

## Known Risk
- High incomplete-particle counts can contaminate efficiency interpretation and may indicate numerical issues.
- In cyclone tutorials, leaving the dustbin wall with the wrong DPM boundary behavior can undercount collection; the tutorial sets the Wall Dustbin to `Trap` (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- Enabling DPM source updates should be checked against particle mass loading; if loading is tiny, the extra coupling may add cost without changing the continuous phase much (`Inferred`) ([user-cyclone-workbench-rng-dpm], user-provided settings report).
- A DPM `Reflect` setting on an inlet injection boundary should be inspected in particle tracks because it can create confusing near-inlet behavior if applied incorrectly (`Assumed`, `Medium Risk`).
- SolidWorks Particle Study is a related but separate workflow; do not copy Fluent DPM boundary meanings directly into SolidWorks without checking the SolidWorks particle-study controls.

## Linked Sources
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [youtube-cyclone-separator-icem-fluent-exemplar](../sources/youtube-cyclone-separator-icem-fluent-exemplar.md)
- [user-cyclone-workbench-rng-dpm-settings-report](../sources/user-cyclone-workbench-rng-dpm-settings-report.md)

## Linked Setups
- [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md)
- [cyclone-separator-workbench-tetra-rng-dpm-exemplar](../setups/cyclone-separator-workbench-tetra-rng-dpm-exemplar.md)

## Related Non-Fluent Particle Workflow
- [solidworks-flow-simulation-particle-study](solidworks-flow-simulation-particle-study.md): SolidWorks-native particle-study workflow used for particle-diameter sensitivity in a cyclone separator. Relation: `differs`.

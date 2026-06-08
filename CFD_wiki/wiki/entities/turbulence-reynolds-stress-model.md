# Entity: Reynolds Stress Model (RSM)

## Definition
RSM is a Reynolds-averaged turbulence model that solves transport equations for individual Reynolds stresses rather than using a simpler isotropic eddy-viscosity assumption.

In plain terms: RSM is more expensive than common k-epsilon or k-omega models, but it can represent strongly anisotropic swirl better.

## Usage in Wiki
- Used in the cyclone separator tutorial because the source states that standard RANS models such as k-epsilon do not adequately capture solid-body rotation plus free-vortex behavior (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## Why It Matters for Cyclones
- Cyclone separators have strong streamline curvature, anisotropic turbulence, and intense swirl.
- The tutorial warns that model selection is critical for realistic cyclone results (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).
- RSM may require transient stepping when a steady solution fluctuates (`Reported`) ([youtube-cyclone-icem-fluent], user-provided notes).

## Linked Sources
- [youtube-cyclone-separator-icem-fluent-exemplar](../sources/youtube-cyclone-separator-icem-fluent-exemplar.md)

## Linked Setups
- [cyclone-separator-icem-hexa-rsm-dpm-exemplar](../setups/cyclone-separator-icem-hexa-rsm-dpm-exemplar.md)

## Relation to Existing Turbulence Pages
- Differs from [turbulence-rng-k-epsilon](turbulence-rng-k-epsilon.md): RSM is recommended by the tutorial for generic high-swirl cyclone flow, while RNG k-epsilon is the reported turbulence baseline in the Purnanto geothermal separator study.

## Open Questions
- Whether RSM improves geothermal separator reconstruction enough to justify its extra convergence cost.
- Whether LES or scale-resolving methods are needed for final validation-quality cyclone predictions.

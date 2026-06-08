# Concept: Two-Phase Flow Regime vs CFD Representation

## Plain-Language Definition
Two-phase flow means two different states of matter move together in the same system, here steam (gas) + water (liquid).

In geothermal pipelines and separators, those phases can organize in different physical patterns (flow regimes).  
`Assumed` (general multiphase terminology): bubbly, slug/churn, annular/mist, and stratified patterns.

## What "Two-Phase Flow" Means in Purnanto 2013
- `Reported`: The study treats inlet fluid as steam-water two-phase feed for a separator CFD comparison ([purnanto-2013], p.1-2, p.5).
- `Reported`: The continuous CFD field is solved with incompressible, isothermal assumptions and no flashing ([purnanto-2013], p.5).
- `Reported`: Particle tracking (DPM) is used for separator efficiency interpretation ([purnanto-2013], p.3-4, p.8).
- `Inferred`: Practical workflow is continuous-field solution first, then particle injections to estimate carryover behavior.

## Why This Distinction Matters
- `Reported`: The paper focuses on separator design comparison and outlet steam-quality trends, not full transient regime-map prediction ([purnanto-2013], p.7-9).
- `Inferred`: So "two-phase flow" in this paper is an engineering representation for separation performance, not a full resolution of all geothermal flow-regime transitions.
- `Reported`: Authors note additional calibration/validation is needed, reinforcing that this is a practical baseline rather than a complete regime-physics closure ([purnanto-2013], p.7, p.9).

## Reuse Guidance
- Copy this modeling style when you need quick geometry-to-performance comparison in similar separators.
- Adapt or avoid this style when your question depends on transient regime transitions, flashing/condensation dynamics, or detailed interfacial structure.

## Linked Sources and Pages
- [purnanto-2013-cfd-geothermal-separator](../sources/purnanto-2013-cfd-geothermal-separator.md)
- [geothermal-boc-separator-fluent-2013-baseline](../setups/geothermal-boc-separator-fluent-2013-baseline.md)
- [multiphase-dpm-particle-tracking](../entities/multiphase-dpm-particle-tracking.md)
- [governing-equations-and-modeling-levels](../physics-basis/governing-equations-and-modeling-levels.md)
- [operating-pressure-enthalpy-and-phase-split](../physics-basis/operating-pressure-enthalpy-and-phase-split.md)

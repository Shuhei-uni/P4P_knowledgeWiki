# Setup: Geothermal Separator Design Screening Workflow (2014 Review-Based)

## Purpose
Use the `zarrouk-purnanto-2014` review as an early-phase design-screening workflow before detailed CFD.

## Source
- Primary: [zarrouk-purnanto-2014-geothermal-separator-design-overview](../sources/zarrouk-purnanto-2014-geothermal-separator-design-overview.md)

## Step-by-Step Build Order
1. Define plant steam quality and pressure targets.
2. Select separator family (vertical BOC vs horizontal) from deployment and constraints.
3. Size preliminary geometry using reviewed empirical rules.
4. Check inlet velocity band and pressure-drop implications.
5. Evaluate location and drainage strategy against carryover/scaling risks.
6. Move shortlisted geometry to CFD validation.

## Key Design Anchors
- Common effective BOC inlet-velocity design range near 30-40 m/s (`Reported`) ([zarrouk-purnanto-2014], p.253).
- High target separator efficiencies (approximately 99.5-99.99%) are reported for well-designed systems (`Reported`) ([zarrouk-purnanto-2014], p.253).
- Spiral-inlet BOC described as current dominant industrial design (`Reported`) ([zarrouk-purnanto-2014], p.253).

## Missing Info
- No full CFD numerical settings.
- No universally transferable geometry constants for every fluid chemistry.

## Assumptions
- Use this as pre-CFD screening, not final design freeze (`Assumed`, `Low Risk`).

## Sensitivity Plan
1. Inlet velocity around the recommended band.
2. Separator location distance vs carryover risk.
3. Pressure-drop vs steam-quality tradeoff.

## Common Failure Modes
- Oversized centralized separation with insufficient scrubbing/drain strategy.
- Inlet velocity beyond stable separation envelope.
- Underestimated pressure drop causing off-design turbine conditions.

## Quick Diagnostics
- Compare target vs predicted steam purity.
- Track expected carryover mass at full-load and turndown.
- Confirm pressure-drop budget remains within turbine inlet constraints.

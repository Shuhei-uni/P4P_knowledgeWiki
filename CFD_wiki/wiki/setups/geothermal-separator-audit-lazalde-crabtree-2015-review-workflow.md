# Setup: Geothermal Separator Audit Workflow (Lazalde-Crabtree-Centered, 2015 Review)

## Purpose
Audit existing geothermal separator operation against historic design envelopes and known evaluation practices summarized in `rivas-cruz-2015`.

## Source
- Primary: [rivas-cruz-2015-geothermal-separator-state-of-art-review](../sources/rivas-cruz-2015-geothermal-separator-state-of-art-review.md)

## Step-by-Step Build Order
1. Gather historical operating data (mass flow, pressure, steam quality, chemistry).
2. Recompute expected separator performance using Lazalde-Crabtree/Bangma lineage rules.
3. Compare expected vs measured steam quality/purity and pressure-drop behavior.
4. Flag drift cases (fouling, scaling, transients, geometry mismatch).
5. Prioritize retrofit checks or CFD follow-up analysis.

## Key Audit Anchors
- Review consensus: Webre-type separators + Lazalde-Crabtree methods dominate legacy geothermal practice (`Reported`) ([rivas-cruz-2015], p.885-886).
- Steam quality targets around or above 99.95% repeatedly cited in reviewed methods (`Reported`) ([rivas-cruz-2015], p.883, p.886).

## Missing Info
- No single closed-form workflow for all fields.
- No direct CFD re-run dataset.

## Assumptions
- Use this workflow for screening and gap detection before new numerical studies (`Assumed`, `Low Risk`).

## Sensitivity Plan
1. Inlet velocity and dryness sensitivity.
2. Carryover sensitivity to operating transients.
3. Field-chemistry sensitivity to separator/dryer performance.

## Common Failure Modes
- Good nominal steam quality but poor purity due to solids carryover.
- Design-intent drift after long-term field changes.
- Overreliance on historic constants outside their validated operating window.

## Quick Diagnostics
- Trend steam quality/purity against inlet velocity history.
- Compare pressure-drop increase against fouling timeline.
- Verify separator/dryer operating point remains in original design envelope.

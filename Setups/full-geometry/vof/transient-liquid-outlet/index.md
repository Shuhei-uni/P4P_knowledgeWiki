# Full Geometry — VOF Transient Liquid-Outlet Setup Branch

The existing planned VOF setup remains stored at its historical compatibility path:

- [`02d` — transient VOF brine-outlet model-form sensitivity](../../../future/02d-transient-vof-brine-outlet-model-form-sensitivity.md)

This page is the canonical setup-side entry point for that branch.

## Role

Use VOF to test whether explicitly resolved bulk-liquid/free-surface behavior changes the brine-outlet result relative to Mixture.

Before production comparisons, VOF requires its own qualification of initialization, timestep/interface Courant behavior, and local interface resolution. Do not treat a VOF result as another point in the Mixture outlet-family screen.

## Results

VOF numerical evidence belongs in the separate mirrored report folder:

- [VOF transient liquid-outlet reports](../../../reports/full-geometry/vof/transient-liquid-outlet/index.md)

Future VOF setup/stage plans belong here. Future VOF result reports do not.

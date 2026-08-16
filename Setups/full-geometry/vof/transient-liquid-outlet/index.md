# Full Geometry — VOF Transient Liquid-Outlet Branch

The existing planned VOF setup remains stored at its historical compatibility path:

- [`02d` — transient VOF brine-outlet model-form sensitivity](../../../future/02d-transient-vof-brine-outlet-model-form-sensitivity.md)

This page is now the canonical semantic entry point for that branch.

## Role

Use VOF to test whether explicitly resolved bulk-liquid/free-surface behavior changes the brine-outlet result relative to Mixture.

Before production comparisons, VOF requires its own qualification of initialization, timestep/interface Courant behavior, and local interface resolution. Do not treat a VOF result as another point in the Mixture outlet-family screen.

Future VOF plans/results should be added under this campaign folder rather than creating a new global numbered setup/report folder.

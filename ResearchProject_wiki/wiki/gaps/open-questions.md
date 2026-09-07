# Open Questions

## High Priority
1. Can setup `07b`, started from the clean original 900k mesh and fresh Hybrid Initialization, reach stable liquid inventory and close `liquid inlet + liquid steam outlet + integrated sink = 0`?
2. How sensitive are pressure drop, outlet phase flow, velocity/vorticity and sink rate to `tau`, ramp schedule and the one-cell sink-layer thickness?
3. Can the source-CAD/image evidence confirm that Fluent zone `bottom` is exactly the intended constant-water-level plane and establish its elevation?
4. Does the constant-level sink materially alter the carrier field compared with a resolved brine outlet, especially swirl and pressure near the lower vessel?
5. What minimum iteration/monitor-stability rule should decide whether a Fluent run can enter the active evidence set?
6. Which convergence monitors are most reliable for this separator case beyond residual plots?

## Medium Priority
1. Which exact setting mismatch caused non-convergence in the recreated Bangma case, if that reconstruction becomes necessary again?
2. What mesh-quality repair or local refinement is needed before adding inlet-regime realism?
3. Which assumptions from legacy model should be retained versus challenged for this project?

# Turbulence closure path readback

## Read-only live inspection

On 2026-09-11, the reachable Fluent 2025 R2 session was inspected without
changing the case:

| Settings path | Live readback |
| --- | --- |
| settings.setup.models.viscous.model | k-epsilon |
| settings.setup.models.viscous.k_epsilon_model | rng |
| settings.setup.models.viscous.near_wall_treatment.wall_treatment | standard-wall-fn |
| settings.setup.models.viscous.options | curvature correction false; Kato-Launder production false; production limiter false |
| settings.setup.models.viscous.rng | differential viscosity true; swirl-dominated-flow true |

The version-matched Fluent documentation exposes standard, RNG, and realizable
choices under the k-epsilon model branch. The first three queue items therefore
share one known model path:

1. retain viscous model k-epsilon;
2. set only k_epsilon_model to rng, standard, or realizable;
3. reacquire the viscous object;
4. read back the selected closure and all newly exposed closure-specific
   options;
5. verify the shared baseline settings before any iteration.

The alternative closure values themselves have not been set in the live case.
That is intentional: this file proves the path and version-matched option
mapping without mutating the parent. The implementation gate must still reject
the prepared child if the immediate readback does not equal the requested
closure.

## Common implementation rule

The active-1000 absorber pair is loaded as-is. Do not reinitialize, patch,
reset, remesh, resplit, or otherwise alter the restart field before applying
the single closure delta. Each child uses the same parent field so that the
closure comparison does not become an initialization comparison.


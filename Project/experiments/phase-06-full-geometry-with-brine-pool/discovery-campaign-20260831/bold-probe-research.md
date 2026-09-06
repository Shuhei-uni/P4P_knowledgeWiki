# Bold-probe research brief — Phase 06 discovery

## Current scientific tension

The full-geometry steady Mixture/RNG reference and bounded pressure-feedback
surrogate retain positive liquid accumulation. Nearby pressure and gain
changes can show sensitivity, but they cannot distinguish whether the limiting
mechanism is the outlet surrogate or the Mixture model's treatment of a dense
bottom pool. A model-form probe is therefore relevant while the phase remains
steady and surrogate-only.

## Researched candidates

| Candidate | Scientific question | Research basis | Prior collision | Minimal probe and learning |
|---|---|---|---|---|
| Steady Eulerian A/B | Does an Eulerian phase treatment change pool-region phase routing enough to alter boundedness relative to Mixture under the same steady outlet? | The retained project model guidance records Mixture as simpler for dispersed flow but Eulerian as potentially more accurate when phase interaction/volume fraction is stronger: `Project/experiments/phase-01-purnanto-baseline-and-inlet-exploration/purnanto-00-reference-spiral-boc/setup.md` §§3.2, 5. The project explicitly recommends a controlled Mixture-versus-Eulerian A/B after a trusted baseline. | `NEW` for this full-geometry steady pool-control question; earlier VOF was transient and rejected, not an Eulerian A/B. | One lower-pressure fixed-outlet Eulerian child with unchanged geometry, inlet, reports, and 500-iteration attached screen. Positive result supports model-form qualification; negative result bounds the model-form branch. |
| Steady VOF | Can a steady interface-resolving model hold a distinct pool interface? | The retained VOF record reports the prior transient VOF branch as qualitatively invalid; that makes a new steady VOF probe high-risk and potentially confounded by its known interface/steady limitations. | `PARTIAL REPEAT` / high risk; defer. | Do not include in the six-case campaign unless a live/manual capability review proves steady VOF is appropriate and interpretable. |

## D06/D06R outcomes and replacement selection

The original D06 child proved that this Fluent 2025 R2 case can switch to
Eulerian, preserve phase/material mapping, and survive paired save/reopen. It
then stalled during the first 50-iteration smoke without one report coordinate,
so it is a non-counting blocked attempt rather than a negative model-form
result.

`P6-D06R-EC` then proved the Coupled model/coupling/report-path recipe, but
its first smoke exposed a formulation-specific invalid inherited
total-pressure report. It blocked before a countable screen. This means the
Eulerian lane is unavailable under the current predeclared package; do not
remove that report silently after the result.

The selected replacement candidate is `P6-D06C-PR`: a Mixture/RNG prescribed
continuation path through the D01/D02 pressure bracket. It is `NEW` relative
to the mass-error feedback screens because it is open-loop and tests
initialization/path sensitivity rather than a gain or target. It leaves the
model, all 30 valid reports, core figures, and steady numerical-surrogate
boundary unchanged. See [`d06-repair-research.md`](d06-repair-research.md).

This selection is conditional on a new fresh `DISCOVERY_DESIGN` review. If
the prescribed path cannot produce its full evidence contract, record it as
unavailable and repair the campaign again; do not infer a physical conclusion
from numerical failure.

Literature/project guidance motivates this question only. The Phase-06
simulation must decide whether the model-form difference matters for this
geometry and proxy.

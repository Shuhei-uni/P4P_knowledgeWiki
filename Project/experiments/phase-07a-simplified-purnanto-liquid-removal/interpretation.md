# Phase 7A — Interpretation

## Why this phase existed

Phase 7A deliberately simplified the problem after Phase 6.

The lower full-geometry outlet/control system was removed from the immediate research scope. The truncated lower wall was treated as a practical surrogate for the brine-pool surface seen by the separator flow, while the project looked for a separate way to remove continuous liquid.

The key constraint was to remove liquid without introducing another conventional outlet whose pressure or flow condition becomes a new dominant sensitivity problem.

## Main hypothesis

A localized, phase-selective lower-region sink can act as a numerical "virtual liquid outlet": it can remove separated liquid while leaving vapor without a direct sink and preserving the simplified lower boundary.

This was a mechanism-discovery phase. Some deliberately pragmatic methods were acceptable if they helped identify what architecture could work.

## What was run

| Family | What it tested | High-level lesson |
| --- | --- | --- |
| E0 reference | corrected two-phase baseline | valid comparison parent, not a physical result |
| fixed boundary/treatment screens | pressure, resistance, imposed-flow and adaptive treatments | conventional outlet/control choices remained sensitive or numerically problematic |
| fixed-mesh phase sink | remove liquid without a lower outlet | implementation/source-binding limitations |
| E5-CZ native lower cell-zone sink | move the liquid sink into a dedicated lower fluid zone | technically auditable phase-selective absorber became possible |
| absorber-control family | feedback/cap sensitivity | local liquid could be controlled, but inventory drift and divergence remained |
| E6 radial pressure-outlet concept | localized bottom boundary alternative | retained as diagnostic design, not selected direction |

## Representative evidence

The native E5-CZ family separated 3,794 lower cells into a dedicated fluid zone without changing the overall mesh statistics.

The initial gain screen produced positive inventory drift for every tested gain:

- G=0.25: about +0.5046 kg/iteration;
- G=0.50: about +0.3256 kg/iteration;
- G=1.00: about +0.3521 kg/iteration.

The later lower-inventory absorber controller showed that the mechanism could produce a real local phase-2 response, but not yet a stable global state:

- the low-cap 146.15 kg/s case completed but retained about +0.998 kg/native iteration late total-inventory slope;
- the higher-cap 292.30 and 584.60 kg/s cases both diverged before the declared horizon.

This is why no Phase-7A child was a successful final operating point.

## Interpretation

The critical result was architectural rather than numerical: the lower cell-zone phase-2 absorber was the mechanism worth keeping.

It was not selected because the early controller was accurate or converged. It was selected because it satisfied the central modelling requirement better than the alternatives:

- the simplified lower boundary could remain closed;
- vapor did not need a direct mass sink;
- liquid removal could be localized to the bottom region;
- the source could be explicitly audited.

Any conventional outlet reintroduced the same type of pressure/flow sensitivity that Phase 6 had intentionally moved away from.

The remaining problem was therefore no longer "what mechanism should remove liquid?" It became "can this virtual-liquid-outlet idea be redesigned so it actually behaves like a usable outlet and allows a developed separator state?"

## Why this led to Phase 7.1A

Phase 7.1A kept the absorber architecture but moved from mechanism discovery to absorber and solver development.

The old inventory-feedback/cap implementation had not produced a stable global state. The next phase therefore revisited the absorber law itself and the way the flow field was developed.

## Evidence gaps / TODO

- TODO: add one compact comparison figure showing total-liquid inventory for the E5-CZ gain screen if the plot package is retained.
- TODO: in the final report, avoid presenting every E0–E6 branch. The detailed logs remain here, but the report narrative only needs the families that changed the project decision.

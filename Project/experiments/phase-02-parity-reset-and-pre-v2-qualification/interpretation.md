# Phase 2 — Interpretation

## Why this phase existed

Phase 2 was a parity reset. After the exploratory inlet work, the project needed one reproducible Purnanto-based carrier setup that could be used as the parent for later DPM and wall-film work.

The aim was to keep the Purnanto geometry, mesh, and main model settings as close as practical to the reference lineage while making the selected two-phase split inlet the main controlled change.

## Main hypothesis

If the Purnanto setup can be rebuilt with a controlled two-phase split inlet, it can serve as a consistent baseline for later particle and wall-mechanism studies.

## What was run

| Run / family | Main question | High-level outcome |
| --- | --- | --- |
| 08b parity split inlet | can the Purnanto-like carrier be rebuilt around the two-phase inlet? | became the main parity parent, but whole-domain balance remained open |
| 08c inlet-loading sensitivity | how sensitive is the carrier/outlet response to inlet loading? | useful directional sensitivity, not a closed comparison |
| one-inlet recreation | can the earlier one-inlet setup be reconstructed? | retained as smoke/diagnostic evidence only |
| full-geometry 02c pressure sensitivity | how does brine pressure affect the early full-geometry branch? | unstable/non-converged screen |
| transient VOF 02d | does model form change the lower-liquid behaviour? | transient attempts stopped early and remained inconclusive |

## Representative evidence

The saved 08b result at 5000 iterations reported:

- liquid inlet: 116.92 kg/s;
- vapor inlet: 80.69 kg/s;
- liquid through steamoutlet: 0.0821 kg/s;
- vapor through steamoutlet: 81.464 kg/s;
- steam-outlet dryness: 99.899%;
- whole-domain mixture imbalance ratio: 0.587.

The apparently excellent steam-outlet dryness therefore could not be treated as a full separator efficiency result. The domain was not mass closed because the simplified geometry still lacked a credible continuous-liquid removal path.

The active DPM sample was also dominated by incomplete trajectories: 13012 / 13020 tracks were incomplete.

The 08c comparison retained the same split-inlet topology and varied loading, but the available cases had different horizons and no closed phase balance, so it remained a preliminary response study.

## Interpretation

08b matters because it became the project's clean two-phase parity baseline, not because it was a fully validated separator solution.

The important modelling distinction established here was: hold the Purnanto-like carrier model broadly fixed, then build later complexity on top of one repeatable two-phase inlet state.

The phase also exposed a problem that would persist for several later phases: very clean steam-outlet numbers can be misleading when the overall liquid inventory and whole-domain mass balance are still open.

## Why this led to Phase 3

Once a reproducible two-phase carrier existed, the project could follow the Purnanto-style methodology of developing the carrier field first and then injecting droplets to study carryover.

## Evidence gaps / TODO

- TODO: add a compact Phase-2 figure comparing 08b and the two 08c loading cases if the original plot can be recovered.
- TODO: the exact reason the historical one-inlet recreation was retained is weakly documented; keep it out of the final narrative unless needed for provenance.

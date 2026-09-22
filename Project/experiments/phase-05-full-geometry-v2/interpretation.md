# Phase 5 — Interpretation

## Why this phase existed

Up to Phase 4, the project could study separation mechanisms but could not close the continuous-liquid balance because the simplified model had no credible continuous-liquid exit.

Phase 5 therefore moved to the full lower separator geometry so that separated liquid had a physical brine-outlet route.

## Main hypothesis

Adding the real lower geometry and brine outlet should allow separated continuous liquid to leave the domain and make a mass-closed separator state possible.

## What was run

| Family | Main question |
| --- | --- |
| 02e outlet characterization | which built-in brine-outlet formulation can drain liquid without destroying the solution? |
| transient liquid-outlet branch | is the retained-liquid problem easier when accumulation/drainage evolve in physical time? |
| 03A full-geometry parity lineage | can the full geometry preserve the earlier carrier basis while supporting lower-liquid behaviour? |

The 02e campaign was the clearest outlet comparison. It tested Pressure Outlet, Outlet Vent, Mass-Flow Outlet, and Exhaust Fan formulations from a common initialized Y010 lower-liquid state.

## Representative evidence

The Stage-1 02e matrix attempted 12 cases at 500 steady iterations:

- only 4 / 12 completed;
- 8 / 12 terminated with floating-point exceptions.

The complete cases generally over-drained the initialized liquid. For example, PO-P1 had about 116.9 kg/s liquid entering but mean reported liquid discharge of more than 2300 kg/s across the brine and steam outlets in the final window. This was a strongly depleting numerical state, not a physical steady operating point.

The targeted Stage-2 screen then tested:

- Pressure Outlet: 1.175 and 1.190 MPa → both failed before 500 iterations;
- Outlet Vent: K=3 and K=7 → both completed 500 iterations.

Even the surviving Outlet Vent cases still removed far more liquid than entered:

| Case | Liquid inlet | Liquid → brine | Liquid → steam | Liquid balance |
| --- | ---: | ---: | ---: | ---: |
| K=3 | 116.921 | 661.976 | 0.648 | -545.702 kg/s |
| K=7 | 116.921 | 596.647 | 1.224 | -480.950 kg/s |

Useful retained figures:

- [Stage-1 inventory histories](full-geometry-02e-mixture-outlet-characterization/stage-01/figures/02e_stage1_inventory_histories_20260816.png)
- [Stage-1 scaled residuals](full-geometry-02e-mixture-outlet-characterization/stage-01/figures/02e_stage1_scaled_residuals_20260816.png)
- [Stage-2 inventory histories](full-geometry-02e-mixture-outlet-characterization/stage-02/figures/02e_stage2_inventory_histories_20260816.png)
- [Stage-2 scaled residuals](full-geometry-02e-mixture-outlet-characterization/stage-02/figures/02e_stage2_scaled_residuals_20260816.png)

## Interpretation

The full geometry confirmed that simply adding a brine outlet does not automatically solve the liquid-balance problem.

Instead, the lower boundary became extremely sensitive: some conditions aggressively drained the stored liquid; some routed vapor incorrectly; some entered strong reversed flow and numerical failure; and short 500-iteration survivability did not imply a physical operating state.

A later project-level lesson is that many Phase-5 runs were also too short to fully develop the separator inventory. This does not invalidate the observed outlet sensitivity, but it limits any steady-state interpretation.

The most important result was therefore not a selected outlet setting. It was the realization that brine-outlet hydraulics are themselves a major coupled problem.

## Why this led to Phase 6

The physical separator does not operate with an arbitrary fixed brine pressure. It retains a lower liquid inventory and uses downstream hydraulics/level control. Phase 6 therefore reframed the problem from "which fixed outlet condition works?" to "can the CFD establish and control a physically meaningful lower brine-pool state?"

## Evidence gaps / TODO

- TODO: identify the best single full-geometry pressure-sensitivity plot for the final report; the current 02e figures are strong numerically but do not by themselves show the whole physical transition.
- TODO: when discussing Phase-5 short runs, distinguish a later methodological lesson from what was known at the time.

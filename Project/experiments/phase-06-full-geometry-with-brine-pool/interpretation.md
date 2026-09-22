# Phase 6 — Interpretation

## Why this phase existed

Phase 6 followed directly from the Phase-5 outlet sensitivity. The problem was no longer simply to provide a hole for liquid to leave. A real separator retains brine and the downstream system controls that inventory.

The phase therefore asked whether the full-geometry model could reproduce a controlled lower brine-pool operating condition rather than merely responding to a fixed outlet pressure.

## Main hypothesis

If a meaningful lower-liquid observable is coupled to a brine-outlet response, the full-geometry model may settle into a bounded retained-liquid state while maintaining the separator flow field.

## What was run

| Stage | Main purpose |
| --- | --- |
| Stage 1 | define a lower-liquid observable and compare outlet response |
| Stage 2 | map liquid inventory / control data |
| Stage 3 | introduce a simplified level-control surrogate |
| Stage 4 | strengthen feedback and test whether the apparent trend improves |
| Stage 5 | interim phase interpretation |
| Stage 6 | run the surrogate for a much longer horizon to test whether earlier drift was only a long transient |

The control variable was deliberately a numerical lower-region liquid-mass proxy, not a validated physical pool level.

## Representative evidence

The strongest result is the Stage-6 long-horizon test. It completed the full declared 10,000-iteration control horizon, reaching native report coordinate 25,050.

The lower-region phase-2 proxy:

- began at 187.79 kg;
- ended at 284.83 kg;
- had a final-1000 mean of 284.45 kg;
- retained a positive slope of +0.00249 kg/iteration.

The controller reached its pressure lower bound of 1.115 MPa very early and remained saturated for 98 / 100 control endpoints.

The final-1000 mean phase-2 net liquid accumulation remained about +16.10 kg/s, with relative imbalance around 0.081.

Useful figures:

- [F1 — pool proxy and pressure](stage-06-long-horizon-surrogate-hypothesis/figures/P6-S6-H-server2-20260831T004750Z/f1_proxy_and_pressure.png)
- [F2 — phase liquid balance](stage-06-long-horizon-surrogate-hypothesis/figures/P6-S6-H-server2-20260831T004750Z/f2_phase_liquid_balance.png)
- [F3 — storage and closure](stage-06-long-horizon-surrogate-hypothesis/figures/P6-S6-H-server2-20260831T004750Z/f3_storage_and_closure.png)

Residual history was unavailable for this final long run, so no convergence claim should be attached to it.

## Interpretation

The long run weakened the idea that the Phase-6 behaviour was merely a short transient. Even after 10,000 additional control iterations, the numerical pool proxy remained above target and continued to accumulate while the pressure actuator was saturated.

This did not prove that a real separator cannot maintain a brine level. Instead, it showed that the current full-geometry CFD/control abstraction had become a research problem of its own.

The project-level decision was therefore about scope: the CFD should primarily investigate the internal separator flow field and separation mechanisms, not spend most of its complexity reproducing the external brine-level-control system.

The brine pool remains physically important. It can affect vapor deflection, re-entrainment, and carryover. But accurately modelling its downstream control was no longer the highest-value immediate task.

## Why this led to Phase 7A

The project returned to a simplified Purnanto geometry truncated around the brine-pool elevation. The lower wall would act as a reduced representation of the brine-pool surface for the separator flow, while Phase 7A would search for a separate numerical mechanism to remove liquid without reopening the full outlet-control problem.

## Evidence gaps / TODO

- TODO: the final report should clearly distinguish the numerical y≤0.10 m liquid-mass proxy from a measured physical pool level.
- TODO: if plant level-control information becomes available later, revisit whether the Phase-6 conclusion is a scope decision rather than a model-form limitation.

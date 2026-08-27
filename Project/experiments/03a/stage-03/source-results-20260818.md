> **Legacy source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-results-20260818.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# 03A Stage 3 — F08/F10/F12 execution results

## Decision

**Do not proceed with the Stage-3 queue on the basis of this run.** The saved
F08 residual history shows frequent, large spikes in both turbulence transport
residuals, `k` and `epsilon`. This is numerical instability evidence, not a
successful staged convergence result.

Later stages were **not run**. In particular, F08 did not progress through the
40%, 80%, or 100% loading stages or the final-condition run. F10 and F12 did
not complete their first carrier stage.

This report records the user-directed stop decision and the available execution
evidence. It does not promote any branch to a Stage-3 parent or final result.

## Second fixed-block attempt — 2026-08-19

A new attempt was started from the released immutable P0, independently for
F08, F10, and F12. The revised controller used explicit native Fluent journals
with `3000` iterations for each carrier/loading state and no reinitialization at
transitions.

The attempt reached the following confirmed states before the Fluent transport
stream disappeared:

| Branch/state | Confirmed result |
|---|---|
| F08 carrier 10% | Completed exactly at cumulative iteration `3000`; paired checkpoint saved. |
| F08 full Mixture 10% | Completed exactly at cumulative iteration `6000`; paired checkpoint saved. |
| F08 full Mixture 20% | Native block was handed off for `3000` iterations; the gRPC stream was removed before a completed stage checkpoint was confirmed. |
| F10 | Not reached. |
| F12 | Not reached. |

The controller then lost access to Fluent server 1. Repeated reconnect attempts
timed out at `10.104.145.170:54122`. This is classified as
`TRANSPORT_BLOCKED`, not as an FPE or other hard numerical failure. The
uncertain F08 20% block must not be silently repeated; recovery requires
reconnecting to the same Fluent process and checking its actual iteration and
latest autosave/checkpoint first.

## Setup and execution scope

The queue retained its scientific case identities and branch-specific momentum
under-relaxation values:

| Branch | Schedule/state | Momentum URF | Actual execution result |
|---|---|---:|---|
| F08 | Schedule-D, resumed full Mixture at 20% loading | `0.7` | Attempted continuation from iteration `2750`; native journal ended at `4898` instead of the expected `4900`; paired case/data checkpoint was saved, but the branch was stopped. |
| F10 | Schedule-D, independent carrier-first startup | `0.5` | P0/preinit and Hybrid Initialization artifacts were saved; the carrier-stage journal failed with Fluent error `#f` before a valid stage checkpoint and residual export were saved. |
| F12 | Schedule-D, independent carrier-first startup | `0.3` | P0/preinit and Hybrid Initialization artifacts were saved; the carrier-stage journal failed with Fluent error `#f` before a valid stage checkpoint and residual export were saved. |

The Fluent server/session was execution transport only; it was not used as a
scientific case identity. The overnight run used the user-authorized fixed
iteration journal override, so the adaptive `stage3-gate-v1` decision history
was not completed for this run.

## Historical residual evidence

The earlier combined display was retired because it mixed branch evidence and
did not preserve the native iteration progression. The evidence is retained in
this historical report; the evidence-qualified replacement is the
[F08 sampled-residual figure](./figures/03a-stage3/iteration-led/server1/F08/01-scaled-residuals-vs-iteration.png).

The figure overlays the seven residual curves available in the saved F08
export: continuity, the three momentum residuals, `k`, `epsilon`, and the
phase-2 volume-fraction residual. The available history covers plotted samples
from approximately iterations `3939–4898`.

There are no F10 or F12 residual curves to add. Their carrier-stage journals
failed before residual exports were written; the missing histories must not be
interpreted as zero residuals or successful starts.

## Residual evidence

The following statistics are calculated from the plotted samples in the first
and final approximately 250-iteration portions of the saved F08 window. They
are evidence for the stop decision, not a replacement for the exact adaptive
gate history arrays.

| Residual | First-window median | Final-window median | First-window P95 | Final-window P95 |
|---|---:|---:|---:|---:|
| Continuity | `4.01976e-1` | `2.31116e-1` | `4.86967e-1` | `2.86294e-1` |
| x-velocity | `3.49515e-5` | `1.68779e-5` | `3.59734e-5` | `2.14364e-5` |
| y-velocity | `3.37302e-5` | `1.71536e-5` | `3.73381e-5` | `2.32120e-5` |
| z-velocity | `3.72268e-5` | `1.80755e-5` | `3.86633e-5` | `2.30909e-5` |
| `k` | `2.56541e-3` | `2.71312e-3` | `7.46099e-3` | `3.85521e-2` |
| `epsilon` | `1.41451e-2` | `7.10922e-2` | `2.36833e-1` | `1.24913` |
| `vf-phase-2` | `3.13724e-3` | `1.52164e-3` | `3.18836e-3` | `1.79461e-3` |

The momentum and volume-fraction residuals generally decrease, but that does
not offset the turbulence behaviour. The `k` P95 increases by approximately
`416%`, while the `epsilon` median increases by approximately `403%` and its
P95 increases by approximately `427%`. The combined plot also shows repeated
individual spikes, especially in `epsilon`, throughout the later part of the
saved window.

## Result classification

```text
PARTIAL_STAGE3_RUN
F08: stopped during resumed full-Mixture 20% block at actual iteration 4898
F10: carrier-stage journal failed before valid stage output
F12: carrier-stage journal failed before valid stage output
LATER_STAGES: NOT RUN
DECISION: DO NOT PROCEED
```

## Source artifacts

- Overnight execution manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/overnight/20260818T103253Z/overnight-events.jsonl`; not migrated)
- Second fixed-block attempt manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/overnight/20260819T061715Z/overnight-events.jsonl`; not migrated)
- Combined residual data (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/residual-figures/03A-stage3-F08-F10-F12-scaled-residuals.json`; not migrated)
- [Current iteration-led F08 evidence](./figures/03a-stage3/iteration-led/server1/F08/01-scaled-residuals-vs-iteration.png)
- [Stage-3 convergence sweep](setup-source.md)
- [Stage-3 shared parent and seed specification](../../../../Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage3-shared-parent-and-seed-spec.yaml)

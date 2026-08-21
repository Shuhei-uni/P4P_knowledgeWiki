# 03A Stage 3 — Native Queue Final Results

> **Campaign:** 03A Stage 3 — Fluent-Recommended Convergence Sweep
> **Scope:** F02, F04, F05, F06, and F11 only
> **Run stamp:** `20260820T013223Z`
> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](../../../../../full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)
> **Analysis plan:** [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md)
> **Interpretation status:** pending user direction

This report is deliberately branch-by-branch. Each owned branch has the same analysis package: all available residual evidence, mass inlet/outlet with relative imbalance and total liquid inventory, phase routing, Y010/Y030/total liquid distribution, brine-entry pressure and brine flow, branch-local cross-plots, and a ramp-response panel where the branch has a deliberate loading ramp. The cross-branch section appears only after the five individual branch sections and is limited to a compact derived late-window table.

No large multi-branch history overlay is used. Endpoint sequences are labelled as endpoint sequences and are not promoted to continuous convergence histories.

## 1. Evidence model and discovery result

The preserved checkpoint/readback bundle is the lineage authority for the server-2 queue. Continuous residual histories and native Report File histories are required for late-window convergence metrics. A read-only local search was also performed because the Fluent artifacts were expected to exist on the connected computer.

The search root was:

`/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/2026 Sem 2/700`

The search found real local artifacts, but they are not attributable to the server-2 fixed queue:

| Discovery item | Result |
|---|---:|
| Stage-3-named `.out` files | 90 |
| Canonical `.out` report names | 30 |
| Copies per canonical report name | 3 |
| Samples in each discovered `.out` | 25 |
| Case files | 7 |
| Data files | 3 |
| Files carrying `20260820T013223Z` | 0 |
| Files carrying an `F02`/`F04`/`F05`/`F06`/`F11` token | 0 |

The `.out` timestamps are 2026-08-18 UTC, and the case/data names identify P0, preinit, or smoke artifacts rather than the server-2 fixed-3000 queue. They are therefore preserved as discovery evidence but not assigned to any branch or used to calculate a late-window metric. The server-2 remote read-only reachability check also timed out; no Fluent rerun or instrumentation change was performed.

The resulting evidence status is consequently **found locally but lineage-unmapped** rather than “files absent.” Late-window metrics remain unavailable until a positive run/branch mapping or read-only remote recovery is available.

## 2. Package index and execution scope

| Branch | Startup / loading | Momentum URF | Highest valid state | Package |
|---|---|---:|---|---|
| F02 | carrier-first, 100% immediately | 0.7 | carrier stage ended before named endpoint | [F02 package](evidence/03a-stage3-native-queue/branches/F02/branch-analysis.json) |
| F04 | carrier-first, 100% immediately | 0.5 | carrier stage ended before named endpoint | [F04 package](evidence/03a-stage3-native-queue/branches/F04/branch-analysis.json) |
| F05 | full Mixture, 100% immediately | 0.3 | full Mixture, 100%, iteration 3,000 | [F05 package](evidence/03a-stage3-native-queue/branches/F05/branch-analysis.json) |
| F06 | carrier-first, then full Mixture at 100% | 0.3 | full Mixture, 100%, cumulative iteration 6,000 | [F06 package](evidence/03a-stage3-native-queue/branches/F06/branch-analysis.json) |
| F11 | full Mixture, 10 → 20 → 40 → 80 → 100% | 0.3 | full Mixture, 100%, cumulative iteration 15,000 | [F11 package](evidence/03a-stage3-native-queue/branches/F11/branch-analysis.json) |

The machine-readable package index is [`03a-stage3-native-queue-branch-packages.json`](evidence/03a-stage3-native-queue/03a-stage3-native-queue-branch-packages.json). The local artifact inventory is [`03a-stage3-local-artifact-discovery.json`](evidence/03a-stage3-native-queue/03a-stage3-local-artifact-discovery.json), with row-level metadata in [`03a-stage3-local-artifact-discovery.csv`](evidence/03a-stage3-native-queue/03a-stage3-local-artifact-discovery.csv).

## 3. Branch F02 — carrier-first, immediate 100%, momentum URF 0.7

F02 has one submitted carrier-stage record, but it ended before the named full-Mixture endpoint pair. No full-Mixture checkpoint row, endpoint residual point, continuous residual history, or branch-mapped `.out` history is available. The plots below are status-preserving branch-local figures; they do not fill the missing stage with another branch’s data.

Evidence files: [checkpoints](evidence/03a-stage3-native-queue/branches/F02/branch-checkpoints.csv), [residual evidence](evidence/03a-stage3-native-queue/branches/F02/branch-residual-evidence.json), [late-window metrics](evidence/03a-stage3-native-queue/branches/F02/branch-late-window-metrics.json), [report-history evidence](evidence/03a-stage3-native-queue/branches/F02/branch-report-history-evidence.json).

### F02 figure package

1. **All residuals:** [F02 residuals](plots/03a-stage3/native-queue/F02/01-residuals.png)
2. **Mass inlet/outlet, relative imbalance, and total liquid inventory:** [F02 physical package](plots/03a-stage3/native-queue/F02/02-mass-imbalance-inventory.png)
3. **Phase routing:** [F02 phase routing](plots/03a-stage3/native-queue/F02/03-phase-routing.png)
4. **Y010/Y030/total liquid distribution:** [F02 liquid distribution](plots/03a-stage3/native-queue/F02/04-liquid-distribution.png)
5. **Brine-entry pressure and brine flow:** [F02 brine hydraulics](plots/03a-stage3/native-queue/F02/05-brine-pressure-flow.png)
6. **Branch-specific cross-plots:** [F02 cross-plots](plots/03a-stage3/native-queue/F02/06-cross-plots.png)
7. **Ramp-response summary:** [F02 ramp panel](plots/03a-stage3/native-queue/F02/07-ramp-response.png) — not applicable because F02 has no multi-load ramp.

**Branch conclusion:** F02 is partial and cannot be assessed at the requested full-Mixture condition from the preserved server-2 evidence.

## 4. Branch F04 — carrier-first, immediate 100%, momentum URF 0.5

F04 has one submitted carrier-stage record, but it ended before the named full-Mixture endpoint pair. No full-Mixture checkpoint row, endpoint residual point, continuous residual history, or branch-mapped `.out` history is available. Its package is independent of F02 and does not substitute F02 evidence.

Evidence files: [checkpoints](evidence/03a-stage3-native-queue/branches/F04/branch-checkpoints.csv), [residual evidence](evidence/03a-stage3-native-queue/branches/F04/branch-residual-evidence.json), [late-window metrics](evidence/03a-stage3-native-queue/branches/F04/branch-late-window-metrics.json), [report-history evidence](evidence/03a-stage3-native-queue/branches/F04/branch-report-history-evidence.json).

### F04 figure package

1. **All residuals:** [F04 residuals](plots/03a-stage3/native-queue/F04/01-residuals.png)
2. **Mass inlet/outlet, relative imbalance, and total liquid inventory:** [F04 physical package](plots/03a-stage3/native-queue/F04/02-mass-imbalance-inventory.png)
3. **Phase routing:** [F04 phase routing](plots/03a-stage3/native-queue/F04/03-phase-routing.png)
4. **Y010/Y030/total liquid distribution:** [F04 liquid distribution](plots/03a-stage3/native-queue/F04/04-liquid-distribution.png)
5. **Brine-entry pressure and brine flow:** [F04 brine hydraulics](plots/03a-stage3/native-queue/F04/05-brine-pressure-flow.png)
6. **Branch-specific cross-plots:** [F04 cross-plots](plots/03a-stage3/native-queue/F04/06-cross-plots.png)
7. **Ramp-response summary:** [F04 ramp panel](plots/03a-stage3/native-queue/F04/07-ramp-response.png) — not applicable because F04 has no multi-load ramp.

**Branch conclusion:** F04 is partial and cannot be assessed at the requested full-Mixture condition from the preserved server-2 evidence.

## 5. Branch F05 — full Mixture, immediate 100%, momentum URF 0.3

F05 has one paired full-Mixture endpoint at iteration 3,000. It also has one instantaneous seven-equation residual point at that endpoint. That point is retained in the residual package, but it is not a residual history or late-window statistic.

Evidence files: [checkpoints](evidence/03a-stage3-native-queue/branches/F05/branch-checkpoints.csv), [residual evidence](evidence/03a-stage3-native-queue/branches/F05/branch-residual-evidence.json), [residual point CSV](evidence/03a-stage3-native-queue/branches/F05/branch-residual-points.csv), [late-window metrics](evidence/03a-stage3-native-queue/branches/F05/branch-late-window-metrics.json), [report-history evidence](evidence/03a-stage3-native-queue/branches/F05/branch-report-history-evidence.json).

### F05 residuals

[F05 all-residual evidence](plots/03a-stage3/native-queue/F05/01-residuals.png)

| Continuity | X-momentum | Y-momentum | Z-momentum | `k` | `epsilon` | VF phase 2 |
|---:|---:|---:|---:|---:|---:|---:|
| 7.88097e-02 | 1.61021e-05 | 1.76411e-05 | 1.76618e-05 | 5.96102e-04 | 3.27444e-03 | 1.39688e-03 |

These values are one endpoint residual point only. Boundedness, trend, and intermittency cannot be inferred.

### F05 physical and routing package

[Mass inlet/outlet, relative imbalance, and total liquid inventory](plots/03a-stage3/native-queue/F05/02-mass-imbalance-inventory.png) · [Phase routing](plots/03a-stage3/native-queue/F05/03-phase-routing.png) · [Y010/Y030/total liquid distribution](plots/03a-stage3/native-queue/F05/04-liquid-distribution.png) · [Brine-entry pressure and brine flow](plots/03a-stage3/native-queue/F05/05-brine-pressure-flow.png)

| Load | Iteration | Inlet kg/s | Outlet kg/s | Signed imbalance | Total liquid kg | Static margin kPa | Total brine kg/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100% | 3,000 | 198.486 | 170.030 | −14.336% | 317.752 | +1.404 | 116.713 |

| Liquid → brine | Liquid → steam | Vapour → brine | Vapour → steam | Y030 kg | Y010 kg |
|---:|---:|---:|---:|---:|---:|
| 69.655% | 5.907% | 43.267% | 56.854% | 172.354 | 166.299 |

The endpoint does not establish mass closure or stationary inventory. Routing is diagnostic and is not a prescribed separation pass/fail test.

### F05 branch-specific cross-plots and ramp response

[F05 cross-plots](plots/03a-stage3/native-queue/F05/06-cross-plots.png) · [F05 ramp-response summary](plots/03a-stage3/native-queue/F05/07-ramp-response.png)

F05 has one endpoint state and no deliberate loading ramp; both figures preserve that limitation explicitly.

**Branch conclusion:** F05 reaches the requested full-Mixture state, but the available evidence is endpoint-only and the final signed imbalance is −14.336%.

## 6. Branch F06 — carrier-first then full Mixture, immediate 100%, momentum URF 0.3

F06 completed a carrier-first block followed by a no-reinitialization full-Mixture block. The full-Mixture endpoint is at cumulative iteration 6,000, corresponding to 3,000 full-Mixture iterations. The carrier-to-Mixture transition is represented in the branch stage records; no continuous residual history was recovered.

Evidence files: [checkpoints](evidence/03a-stage3-native-queue/branches/F06/branch-checkpoints.csv), [residual evidence](evidence/03a-stage3-native-queue/branches/F06/branch-residual-evidence.json), [late-window metrics](evidence/03a-stage3-native-queue/branches/F06/branch-late-window-metrics.json), [report-history evidence](evidence/03a-stage3-native-queue/branches/F06/branch-report-history-evidence.json).

### F06 figure package

1. **All residuals:** [F06 residuals](plots/03a-stage3/native-queue/F06/01-residuals.png) — two submitted stages, no continuous series.
2. **Mass inlet/outlet, relative imbalance, and total liquid inventory:** [F06 physical package](plots/03a-stage3/native-queue/F06/02-mass-imbalance-inventory.png)
3. **Phase routing:** [F06 phase routing](plots/03a-stage3/native-queue/F06/03-phase-routing.png)
4. **Y010/Y030/total liquid distribution:** [F06 liquid distribution](plots/03a-stage3/native-queue/F06/04-liquid-distribution.png)
5. **Brine-entry pressure and brine flow:** [F06 brine hydraulics](plots/03a-stage3/native-queue/F06/05-brine-pressure-flow.png)
6. **Branch-specific cross-plots:** [F06 cross-plots](plots/03a-stage3/native-queue/F06/06-cross-plots.png)
7. **Ramp-response summary:** [F06 ramp panel](plots/03a-stage3/native-queue/F06/07-ramp-response.png) — not applicable because F06 has no multi-load ramp.

| Load | Cumulative iteration | Inlet kg/s | Outlet kg/s | Signed imbalance | Total liquid kg | Static margin kPa | Total brine kg/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 100% | 6,000 | 198.486 | 169.940 | −14.382% | 376.627 | +1.561 | 120.603 |

| Liquid → brine | Liquid → steam | Vapour → brine | Vapour → steam | Y030 kg | Y010 kg |
|---:|---:|---:|---:|---:|---:|
| 71.393% | 4.171% | 45.545% | 54.463% | 251.880 | 245.693 |

The full-Mixture endpoint remains approximately 14.4% low on signed total outlet relative to inlet. Without continuous residual and report-file histories, the carrier-first transition cannot be credited with convergence.

**Branch conclusion:** F06 reaches full Mixture after carrier-first startup, but the endpoint-only physical evidence does not demonstrate closure or stationary inventory.

## 7. Branch F11 — full Mixture, 10 → 20 → 40 → 80 → 100% ramp, momentum URF 0.3

F11 is the only selected branch with a deliberate multi-load ramp. Five paired full-Mixture endpoints are available. They are separate stage endpoints, not a continuous monitor history; the ramp figure therefore reports response versus imposed load without interpolating between stages.

Evidence files: [checkpoints](evidence/03a-stage3-native-queue/branches/F11/branch-checkpoints.csv), [residual evidence](evidence/03a-stage3-native-queue/branches/F11/branch-residual-evidence.json), [late-window metrics](evidence/03a-stage3-native-queue/branches/F11/branch-late-window-metrics.json), [report-history evidence](evidence/03a-stage3-native-queue/branches/F11/branch-report-history-evidence.json).

### F11 figure package

1. **All residuals:** [F11 residuals](plots/03a-stage3/native-queue/F11/01-residuals.png) — five stage records, no continuous series.
2. **Mass inlet/outlet, relative imbalance, and total liquid inventory:** [F11 physical package](plots/03a-stage3/native-queue/F11/02-mass-imbalance-inventory.png)
3. **Phase routing:** [F11 phase routing](plots/03a-stage3/native-queue/F11/03-phase-routing.png)
4. **Y010/Y030/total liquid distribution:** [F11 liquid distribution](plots/03a-stage3/native-queue/F11/04-liquid-distribution.png)
5. **Brine-entry pressure and brine flow:** [F11 brine hydraulics](plots/03a-stage3/native-queue/F11/05-brine-pressure-flow.png)
6. **Branch-specific cross-plots:** [F11 cross-plots](plots/03a-stage3/native-queue/F11/06-cross-plots.png)
7. **Ramp-response summary:** [F11 ramp response](plots/03a-stage3/native-queue/F11/07-ramp-response.png)

| Load | Cumulative iteration | Inlet kg/s | Outlet kg/s | Signed imbalance | Total liquid kg | Static margin kPa | Total brine kg/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10% | 3,000 | 19.849 | 194.251 | +878.664% | 11,383.447 | −0.022 | 104.741 |
| 20% | 6,000 | 39.697 | 138.001 | +247.634% | 8,067.212 | +0.746 | 49.478 |
| 40% | 9,000 | 79.395 | 83.419 | +5.069% | 815.363 | +0.045 | 55.590 |
| 80% | 12,000 | 158.789 | 157.841 | −0.597% | 471.578 | +1.673 | 116.590 |
| 100% | 15,000 | 198.486 | 173.919 | −12.377% | 345.365 | +1.690 | 120.733 |

The 10% and 20% rows are retained with their large positive imbalance. The 40% and 80% endpoint improvements do not persist at 100%; inventory also changes materially across the ramp.

| Load | Liquid → brine | Liquid → steam | Vapour → brine | Vapour → steam | Y030 kg | Y010 kg |
|---:|---:|---:|---:|---:|---:|---:|
| 10% | 896.396% | 694.092% | 0.000073% | 102.990% | 4,690.476 | 4,179.590 |
| 20% | 211.712% | 311.849% | 0.0128% | 95.827% | 4,714.407 | 4,211.900 |
| 40% | 99.945% | 9.070% | 27.183% | 72.237% | 733.815 | 730.352 |
| 80% | 95.777% | 3.368% | 41.432% | 58.341% | 366.379 | 360.823 |
| 100% | 72.586% | 6.364% | 43.996% | 56.039% | 194.154 | 187.793 |

Values above 100% at the low-load endpoints are diagnostic routing ratios, not a settled phase split. The F11 ramp shows endpoint response, not physical-time causality.

**Branch conclusion:** F11 reaches 100%, and its intermediate endpoints approach small absolute imbalance, but the final 100% endpoint returns to −12.377% with no continuous history to establish sustained closure.

## 8. Compact cross-branch summary from derived late-window metrics

This table is intentionally after the individual packages. It uses the branch-derived late-window fields from [`03a-stage3-native-queue-cross-branch-summary.csv`](evidence/03a-stage3-native-queue/03a-stage3-native-queue-cross-branch-summary.csv). Nulls are evidence states, not zeros: no continuous residual history or server-2-mapped `.out` history is available for calculating the metrics.

| Branch | Residual history | Report-history status | Late abs-imbalance median | Late abs-imbalance P95 | Inventory slope (kg/iteration) | Late-window status |
|---|---|---|---:|---:|---:|---|
| F02 | unavailable | found, unmapped | unavailable | unavailable | unavailable | unavailable; carrier stage incomplete |
| F04 | unavailable | found, unmapped | unavailable | unavailable | unavailable | unavailable; carrier stage incomplete |
| F05 | unavailable | found, unmapped | unavailable | unavailable | unavailable | unavailable; endpoint only |
| F06 | unavailable | found, unmapped | unavailable | unavailable | unavailable | unavailable; endpoint only |
| F11 | unavailable | found, unmapped | unavailable | unavailable | unavailable | unavailable; endpoint ramp only |

Endpoint context is kept separate from the late-window table:

| Branch | Final evidenced load | Endpoint abs. imbalance | Endpoint liquid inventory (kg) | Endpoint basis |
|---|---:|---:|---:|---|
| F02 | — | — | — | no full-Mixture endpoint |
| F04 | — | — | — | no full-Mixture endpoint |
| F05 | 100% | 14.336% | 317.752 | one endpoint row |
| F06 | 100% | 14.382% | 376.627 | one endpoint row |
| F11 | 100% | 12.377% | 345.365 | final ramp endpoint |

This is a compact evidence summary, not a branch ranking or winner selection.

## 9. Checkpoint validation and evidence conflicts

The seven full-Mixture endpoint rows for F05, F06, and F11 agree with their explicit paired readbacks within the declared `0.001` source-unit tolerance. The maximum absolute pressure differences are 0.000367 Pa (F05), 0.000371 Pa (F06), and 0.000407, 0.000051, 0.000484, 0.000250, and 0.000380 Pa for F11 at 10, 20, 40, 80, and 100%, respectively. See [`03a-stage3-native-queue-cross-validation.csv`](evidence/03a-stage3-native-queue/03a-stage3-native-queue-cross-validation.csv).

The F11 10% legacy conflict label is preserved in the source evidence. The current checkpoint row and paired readback agree; the disagreement is with an older compact record. The local `.out` files are not used to resolve that conflict because they lack server-2 branch/run lineage.

## 10. Established and unresolved

Established:

- Five independent branch packages exist with the same figure families and branch-local evidence paths.
- F02 and F04 ended before their full-Mixture endpoint; F05, F06, and F11 have seven paired full-Mixture endpoint readbacks in total.
- The seven checkpoint rows cross-validate against paired readbacks within source rounding.
- The connected computer contains real `.cas`/`.dat`/`.out` artifacts, and their discovery metadata is preserved.
- The discovered local artifacts cannot currently be mapped to the server-2 fixed queue, so they do not support late-window metrics.

Unresolved:

- continuous residual envelopes for F02/F04/F05/F06/F11;
- server-2-queue native `.out` histories and derived late-window mass/inventory metrics;
- sustained total inlet≈outlet mass balance;
- stationary total liquid inventory;
- a preferred branch or operating point.

No branch is selected as a winner. Interpretation and any continuation decision remain pending user direction.

## 11. Evidence and implementation links

- [Branch-package index](evidence/03a-stage3-native-queue/03a-stage3-native-queue-branch-packages.json)
- [Cross-branch late-window summary CSV](evidence/03a-stage3-native-queue/03a-stage3-native-queue-cross-branch-summary.csv)
- [Aggregate checkpoint analysis](evidence/03a-stage3-native-queue/03a-stage3-native-queue-analysis.json)
- [Checkpoint cross-validation](evidence/03a-stage3-native-queue/03a-stage3-native-queue-cross-validation.csv)
- [Residual evidence status](evidence/03a-stage3-native-queue/03a-stage3-native-queue-residual-evidence.json)
- [Report-history evidence status](evidence/03a-stage3-native-queue/03a-stage3-native-queue-report-history-evidence.json)
- [Local case/data/report artifact discovery](evidence/03a-stage3-native-queue/03a-stage3-local-artifact-discovery.json)
- [Artifact discovery row inventory](evidence/03a-stage3-native-queue/03a-stage3-local-artifact-discovery.csv)
- [Branch package builder](../../../../../../PyAnsys/scripts/report/build_03a_stage3_native_queue_branch_packages.py)
- [Artifact discovery script](../../../../../../PyAnsys/scripts/report/discover_03a_stage3_artifacts.py)
- [Report-history extractor](../../../../../../PyAnsys/scripts/inspection/extract_report_plot_histories.py)

## Completion status

- [x] Scope restricted to server-2-owned F02/F04/F05/F06/F11 queue branches.
- [x] Each branch has its own consistent residual, physical, routing, liquid-distribution, brine, cross-plot, and ramp/N/A package.
- [x] Cross-branch comparison is deferred until after the individual branch packages.
- [x] Local `.cas`/`.dat`/`.out` discovery was performed and recorded.
- [x] Unmapped local artifacts are not substituted for server-2 queue histories.
- [x] Checkpoint lineage and paired-readback validation are preserved.
- [ ] Late-window residual/report-file metrics — unavailable pending positive lineage or remote read-only recovery.
- [ ] Branch ranking or winner selection — intentionally not performed.

# 03A Stage 3 — Schedule-D Results: F08/F10/F12

> **Scope:** F08, F10, and F12 only.
> **Evidence quality:** mixed — F12 has continuous native Report File histories through 18,000 iterations; F08 has partial residual and checkpoint evidence; F10 has no valid solve checkpoint or residual history.
> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](../../../../../full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)
> **Checkpoint evidence:** [`03a-stage3-results-20260821-checkpoints.csv`](./03a-stage3-results-20260821-checkpoints.csv)
> **Interpretation status:** pending user direction; this report makes no branch-selection claim.

## 1. Evidence and provenance

The Schedule-D analysis is reproduced from the read-only offline builder and its generated evidence: [`analysis JSON`](../../../../../../PyAnsys/output/03A-stage3/session1-final-analysis/03A-stage3-session1-analysis.json), [`late-window summary`](../../../../../../PyAnsys/output/03A-stage3/session1-final-analysis/03A-stage3-session1-cross-branch-late-window-summary.csv), [`checkpoint validation`](../../../../../../PyAnsys/output/03A-stage3/session1-final-analysis/03A-stage3-session1-checkpoint-validation.csv), and [`remote artifact audit`](../../../../../../PyAnsys/output/03A-stage3/session1-final-analysis/server1-artifact-provenance.json).

The connected Fluent host audit found all 30 configured Report Files (18,000 points each) and recorded the case/data provenance without loading or changing any case. The physical-history checkpoint comparisons give 70 matches, zero mismatches, and one unavailable comparison set: F08 has no branch-specific continuous physical history for comparison. The audit records F08's missing 80% retry pair and F10's missing failed-carrier-stage pair as expected gaps, rather than silently treating them as successful runs.

## 2. Branch packages

Each branch has the same seven figure slots. A panel marked unavailable is an evidence statement, not a zero-valued result.

### F08 — carrier-first ramp, URF 0.7

F08 has a valid 40% full-Mixture checkpoint at iteration 12,000 and a partial residual stream (iterations 3,939–4,898). The subsequent 80% retry has no paired endpoint. The continuous physical Report File series cannot be associated with F08 alone, so no late physical-window values are asserted.

- [Residuals](./plots/03a-stage3/session1/branches/F08/residuals.png)
- [Mass, imbalance, inventory](./plots/03a-stage3/session1/branches/F08/mass-imbalance-inventory.png)
- [Phase routing](./plots/03a-stage3/session1/branches/F08/phase-routing.png)
- [Liquid distribution](./plots/03a-stage3/session1/branches/F08/liquid-distribution.png)
- [Brine pressure and flow](./plots/03a-stage3/session1/branches/F08/brine-pressure-flow.png)
- [Ramp response](./plots/03a-stage3/session1/branches/F08/ramp-response.png)
- [Branch-only cross diagnostics](./plots/03a-stage3/session1/branches/F08/cross-diagnostics.png)

| Last valid checkpoint | Inlet (kg/s) | Path outlet (kg/s) | Absolute imbalance | Total liquid (kg) |
|---|---:|---:|---:|---:|
| 40% / iteration 12,000 | 79.395 | 108.833 | 37.079% | 323.419 |

### F10 — carrier-first ramp, URF 0.5

F10 failed during the carrier stage before a valid solve checkpoint or residual export. The available case/data evidence is an initialized state, not a completed solve. The figure package deliberately displays unavailable evidence rather than extrapolating from F08 or F12.

- [Residual evidence](./plots/03a-stage3/session1/branches/F10/residuals.png)
- [Physical evidence](./plots/03a-stage3/session1/branches/F10/mass-imbalance-inventory.png)
- [Phase-routing evidence](./plots/03a-stage3/session1/branches/F10/phase-routing.png)
- [Liquid-distribution evidence](./plots/03a-stage3/session1/branches/F10/liquid-distribution.png)
- [Brine-hydraulic evidence](./plots/03a-stage3/session1/branches/F10/brine-pressure-flow.png)
- [Ramp-response evidence](./plots/03a-stage3/session1/branches/F10/ramp-response.png)
- [Branch-only cross diagnostics](./plots/03a-stage3/session1/branches/F10/cross-diagnostics.png)

### F12 — carrier-first ramp, URF 0.3

F12 has paired checkpoints at 10%, 20%, 40%, 80%, and 100%, plus continuous native histories through iteration 18,000. Its individual figure package is therefore the strongest Schedule-D evidence set.

- [Residuals](./plots/03a-stage3/session1/branches/F12/residuals.png)
- [Mass, imbalance, inventory](./plots/03a-stage3/session1/branches/F12/mass-imbalance-inventory.png)
- [Phase routing](./plots/03a-stage3/session1/branches/F12/phase-routing.png)
- [Liquid distribution](./plots/03a-stage3/session1/branches/F12/liquid-distribution.png)
- [Brine pressure and flow](./plots/03a-stage3/session1/branches/F12/brine-pressure-flow.png)
- [Ramp response](./plots/03a-stage3/session1/branches/F12/ramp-response.png)
- [Branch-only cross diagnostics](./plots/03a-stage3/session1/branches/F12/cross-diagnostics.png)

| Load | Iteration | Absolute imbalance | Total liquid (kg) | Static pressure margin (kPa) |
|---:|---:|---:|---:|---:|
| 10% | 6,000 | 46.713% | 511.236 | +0.024 |
| 20% | 9,000 | 12.005% | 434.665 | −0.073 |
| 40% | 12,000 | 0.073% | 302.414 | +0.154 |
| 80% | 15,000 | 11.966% | 456.137 | +1.106 |
| 100% | 18,000 | 11.107% | 374.374 | +1.645 |

The final 500-point F12 window (iterations 17,501–18,000) has an absolute path-imbalance median of 12.044% (P95 14.805%) and liquid inventory median of 361.692 kg. Those are descriptive late-window metrics, not proof of a steady operating point.

## 3. Compact Schedule-D summary

| Branch | Residual evidence | Continuous physical history | Last validated state | Main limitation |
|---|---|---|---|---|
| F08 | partial, 212 late points | unavailable by branch | 40% / 12,000 | no 80% paired endpoint; no branch-specific physical history |
| F10 | unavailable | unavailable | none | failed before a valid solve checkpoint |
| F12 | 250 late points | 500-point final window | 100% / 18,000 | full-load late imbalance remains about 12% |

No cross-branch ranking follows from this mixed evidence. The figures and source files preserve the proper branch-level distinction.

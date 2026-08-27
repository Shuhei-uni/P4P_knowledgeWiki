> **Legacy source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-native-queue-final-results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# 03A Stage 3 — F02, F04, F05, F06, and F11 Iteration-Led Results

> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](setup-source.md)  
> **Evidence:** server-2 provenance manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-provenance-manifest.json`; not migrated)

The verified source pair is native `.trn` residual histories in `Documents\FluentRuns` plus 30 physical Report Files per branch in `P4P simulation`. The similarly named `-residuals.out` files were rejected as stale, sampled, or physical-monitor exports.

## Unavailable branches

| Branch | Presentation | Reason |
|---|---|---|
| F02 | no plots | no confirmed native endpoint or branch-linked continuous history |
| F04 | no plots | no confirmed native endpoint or branch-linked continuous history |

Status records: F02 (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/F02/status.json`; not migrated) and F04 (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/F04/status.json`; not migrated).

## F05 — full Mixture, 100%

Residual and physical histories are continuous from 1–3,000.

1. [Scaled residuals](./figures/03a-stage3/iteration-led/server2/F05/01-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server2/F05/02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server2/F05/03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server2/F05/04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server2/F05/05-brine-hydraulics-vs-iteration.png)

## F06 — carrier then full Mixture, 100%

Residual and physical histories are continuous from 1–6,000. The one carried residual row at 3,000 is deduplicated; the phase-fraction residual is absent during the carrier stage and is not zero-filled.

1. [Scaled residuals](./figures/03a-stage3/iteration-led/server2/F06/01-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server2/F06/02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server2/F06/03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server2/F06/04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server2/F06/05-brine-hydraulics-vs-iteration.png)

## F11 — five-stage full-Mixture ramp

Residual and physical histories are continuous from 1–15,000 after only the carried rows at 3k, 6k, 9k, and 12k are removed. The stage labels are 10%, 20%, 40%, 80%, and 100% on the iteration axis.

1. [Scaled residuals](./figures/03a-stage3/iteration-led/server2/F11/01-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server2/F11/02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server2/F11/03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server2/F11/04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server2/F11/05-brine-hydraulics-vs-iteration.png)

The canonical extracted histories are residuals (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-residual-histories.csv`; not migrated), physical monitors (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-physical-histories.csv`; not migrated), and validation (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-validation.csv`; not migrated).

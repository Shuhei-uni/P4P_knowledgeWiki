> **Retired source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-f03-f07-f09-detailed-results.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# 03A Stage 3 — F03, F07, and F09 Iteration-Led Results

> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](setup-source.md)  
> **Evidence:** server-3 iteration-led manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server3/server3-iteration-led-manifest.json`; not migrated)

Every figure below uses native cumulative iteration. Stage changes are annotated on the same coordinate; no cross-plots or load-axis figures are retained.

## F03 — completed 100% run

Physical histories are continuous for iterations 1–5,000. Residual histories retain the observed gap from 982–999; the lines are not bridged.

1. [Scaled residuals](./figures/03a-stage3/iteration-led/server3/f03/figure-01-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server3/f03/figure-02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server3/f03/figure-03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server3/f03/figure-04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server3/f03/figure-05-brine-hydraulics-vs-iteration.png)

## F07 — valid through 40%, failed 80% transition

All histories extend to 9,174. Iterations 9,151–9,174 are visibly marked as the 80% numerical-failure tail, not a successful stage.

1. [Scaled residuals](./figures/03a-stage3/iteration-led/server3/f07/figure-01-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server3/f07/figure-02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server3/f07/figure-03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server3/f07/figure-04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server3/f07/figure-05-brine-hydraulics-vs-iteration.png)

## F09 — completed five-stage ramp

Residual and physical histories are continuous from 1–15,000. The 10%, 20%, 40%, 80%, and 100% stages are annotated at their cumulative iteration boundaries.

1. [Scaled residuals](./figures/03a-stage3/iteration-led/server3/f09/figure-01-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server3/f09/figure-02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server3/f09/figure-03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server3/f09/figure-04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server3/f09/figure-05-brine-hydraulics-vs-iteration.png)

The canonical per-iteration data are F03 (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server3/f03/f03-iteration-led-series.csv`; not migrated), F07 (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server3/f07/f07-iteration-led-series.csv`; not migrated), and F09 (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server3/f09/f09-iteration-led-series.csv`; not migrated).

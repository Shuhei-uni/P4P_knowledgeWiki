> **Legacy source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-schedule-d-final-results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# 03A Stage 3 — F08, F10, and F12 Iteration-Led Results

> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](setup-source.md)  
> **Evidence:** server-1 iteration-led manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server1/server1-iteration-led-manifest.json`; not migrated)

Branch case/data, journals, transcripts, and sampled residual exports are stored beneath `Documents\FluentRuns\03A-stage3`. The F12 physical histories are stored separately in `P4P simulation\brine outlet`; those two locations are complementary evidence sources.

## F08 — qualified partial evidence

The branch-linked physical reports are continuous from 9,000–12,045. Figures plot the validated interval 9,000–12,000; 12,001–12,045 is excluded as the failed next-stage tail. Sampled residuals are connected only within each retained stage window. The older 3,939–4,898 residual fragment is excluded as unjoinable.

1. [Sampled scaled residuals](./figures/03a-stage3/iteration-led/server1/F08/01-scaled-residuals-vs-iteration.png)
2. [Mass convergence, 9,000–12,000](./figures/03a-stage3/iteration-led/server1/F08/02-mass-convergence-vs-iteration.png)
3. [Phase routing, 9,000–12,000](./figures/03a-stage3/iteration-led/server1/F08/03-phase-routing-vs-iteration.png)
4. [Liquid distribution, 9,000–12,000](./figures/03a-stage3/iteration-led/server1/F08/04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics, 9,000–12,000](./figures/03a-stage3/iteration-led/server1/F08/05-brine-hydraulics-vs-iteration.png)

## F10 — unavailable

No valid solve endpoint, residual history, or physical history was recovered. The branch remains a status record, not a figure package: F10 evidence status (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server1/f10-status.json`; not migrated).

## F12 — completed six-stage sequence

Physical histories are continuous from 1–18,000. The six retained residual exports each contain 250 sampled points; each retained window is a line segment at native iterations, with no line across the gaps between windows.

1. [Sampled scaled residuals](./figures/03a-stage3/iteration-led/server1/F12/01-scaled-residuals-vs-iteration.png)
2. [Mass convergence](./figures/03a-stage3/iteration-led/server1/F12/02-mass-convergence-vs-iteration.png)
3. [Phase routing](./figures/03a-stage3/iteration-led/server1/F12/03-phase-routing-vs-iteration.png)
4. [Liquid distribution](./figures/03a-stage3/iteration-led/server1/F12/04-liquid-distribution-vs-iteration.png)
5. [Brine hydraulics](./figures/03a-stage3/iteration-led/server1/F12/05-brine-hydraulics-vs-iteration.png)

See the server-1 history validation (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server1/history-validation.csv`; not migrated) for exact ranges, source paths, and exclusions.

# 03A Stage 3 — Iteration-Led Results

> **Campaign:** Fluent-recommended convergence sweep  
> **Interpretation status:** pending user direction  
> **Plotting rule:** every figure uses native cumulative Fluent iteration on the x-axis.

## Evidence-qualified result map

| Branch | Available presentation | Native range / qualification |
|---|---|---|
| F01 | residual figure only; physical endpoint table | residuals 1–5,500; numerical failure followed at 5,704 |
| F02 | unavailable statement | no valid native endpoint or branch-linked history |
| F03 | five figures | physical 1–5,000; residual gap 982–999 preserved |
| F04 | unavailable statement | no valid native endpoint or branch-linked history |
| F05 | five figures | continuous residual and physical histories 1–3,000 |
| F06 | five figures | continuous joined histories 1–6,000; phase-fraction residual absent during carrier stage |
| F07 | five figures | continuous 1–9,174; 9,151–9,174 is a numerical-failure tail |
| F08 | five qualified partial figures | physical history 9,000–12,000; residuals are sampled windows; next-stage tail excluded |
| F09 | five figures | continuous residual and physical histories 1–15,000 |
| F10 | unavailable statement | initialized case evidence only; no valid solve history |
| F11 | five figures | continuous joined histories 1–15,000 |
| F12 | five figures | physical history 1–18,000; residuals are sampled windows, shown as unconnected markers |

No figure fabricates continuity. Continuous series are lines, sampled residual exports are unconnected markers at their native iterations, and unavailable evidence has no placeholder plot.

## Result packages

- [F01 residual evidence](./plots/03a-stage3/iteration-led/central/f01/figure-01-residuals-vs-iteration.png) · [manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/central/f01/f01-iteration-led-manifest.json)
- [F03/F07/F09 iteration-led figures](./03a-stage3-f03-f07-f09-detailed-results.md)
- [F05/F06/F11 iteration-led figures](./03a-stage3-native-queue-final-results.md)
- [F08/F10/F12 iteration-led figures](./03a-stage3-schedule-d-final-results.md)

## Source and validation records

- [Server-1 manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/server1/server1-iteration-led-manifest.json)
- [Server-2 provenance manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-provenance-manifest.json)
- [Server-3 manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/server3/server3-iteration-led-manifest.json)
- [Stage-3 checkpoint evidence](./03a-stage3-results-20260821-checkpoints.csv)

The prior cross-plots, cross-diagnostics, and load-axis ramp-response figures have been retired from this report. Their underlying evidence remains in the machine-readable packages above.

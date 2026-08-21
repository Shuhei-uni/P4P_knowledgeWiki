# 03A Stage 3 — Iteration-Led Analysis and Plotting Contract

> **Scope:** F01–F12  
> **Evidence rule:** no continuous line may be drawn without a verified continuous native history.

## Canonical figures

Every main figure uses cumulative native Fluent iteration on the x-axis:

1. scaled residuals (logarithmic y-axis);
2. total inlet/outlet flow, relative mass imbalance, and total liquid inventory;
3. liquid/vapour routing to brine and steam;
4. total, Y030, and Y010 liquid inventory;
5. brine-entry static/total pressure margin and brine flow.

Stage boundaries, interventions, and numerical-failure tails are annotations on this coordinate. No cross-plot, pressure-versus-flow plot, inventory-versus-imbalance plot, or load-percentage/ramp-response figure is part of the report.

## Evidence presentation rule

| Evidence | Presentation |
|---|---|
| continuous history | line versus iteration |
| sampled history | unconnected markers at recorded iterations |
| several checkpoints only | markers at actual cumulative iterations |
| one checkpoint | table only |
| unavailable | explicit status statement; no placeholder figure |

All figure data require a provenance manifest recording source path, branch identity proof, iteration range, joins, gaps, stage boundaries, units/sign conventions, and checkpoint validation.

## Current output and source manifests

- [Iteration-led final results](./03a-stage3-final-results.md)
- [Server-1 manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/server1/server1-iteration-led-manifest.json)
- [Server-2 manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-provenance-manifest.json)
- [Server-3 manifest](../../../../../../PyAnsys/output/03a_stage3/iteration-led/server3/server3-iteration-led-manifest.json)

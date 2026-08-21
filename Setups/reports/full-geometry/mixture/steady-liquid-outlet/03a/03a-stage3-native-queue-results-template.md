# 03A Stage 3 — Branch-by-Branch Final Results Template

> **Campaign:** 03A Stage 3 — Fluent-Recommended Convergence Sweep
> **Owned branch scope:** `<F##>, <F##>, ...`
> **Run stamp:** `<run stamp>`
> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](../../../../../full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)
> **Analysis plan:** [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md)
> **Interpretation status:** pending user direction

Use this structure for the final report. Keep each owned branch self-contained before adding any cross-branch comparison. Do not use a multi-branch history overlay as the default figure.

## 1. Evidence model and artifact discovery

State the primary evidence hierarchy:

1. continuous residual histories, with genuine gaps and failure tails preserved;
2. native Fluent Report File `.out` histories, if positively mapped to the run and branch;
3. paired case/data readbacks and checkpoint rows as endpoint/lineage anchors;
4. local artifact-discovery results, including artifacts found but not safely attributable.

Record search roots, file counts, timestamps, run-stamp matches, branch-token matches, and any remote-access limitation. Never call a file “absent” when it was found but its lineage is unresolved. Do not use an unresolved file as a branch history.

## 2. Branch package index

| Branch | Startup / loading | URF | Highest valid state | Analysis JSON | Figure directory |
|---|---|---:|---|---|---|
| `<F##>` | `<strategy>` | `<value>` | `<state>` | [`analysis.json`](evidence/<package>/<branch>/branch-analysis.json) | [`plots/`](plots/<plot-root>/<branch>/) |

Each branch package must contain:

- all available residual equations and evidence-status information;
- mass inlet/outlet, relative imbalance, and total liquid inventory;
- phase routing;
- Y010/Y030/total liquid distribution;
- brine-entry pressure and brine flow;
- branch-specific cross-plots;
- ramp-response summary, or an explicit not-applicable panel;
- branch-local checkpoint, residual, report-history, and late-window metric files.

## 3. Branch `<F##>` — `<strategy>`

### 3.1 Execution and evidence

Describe the branch’s startup, loading, URF, stage boundaries, terminal state, gaps, failures, and evidence completeness. Keep this paragraph branch-local.

### 3.2 All residuals

![`<F##>` residuals](plots/<plot-root>/<branch>/01-residuals.png)

Include every available equation. State whether the figure is a continuous history, a stitched history with preserved gaps, endpoint residual points only, or an evidence-status panel. Do not infer a late-window statistic from a single endpoint point.

### 3.3 Mass inlet/outlet, relative imbalance, and total liquid inventory

![`<F##>` mass and inventory](plots/<plot-root>/<branch>/02-mass-imbalance-inventory.png)

| Load | Iteration | Inlet | Outlet | Signed imbalance | Total liquid inventory | Status |
|---:|---:|---:|---:|---:|---:|---|
| `<load>` | `<iteration>` | `<kg/s>` | `<kg/s>` | `<%>` | `<kg>` | `<endpoint/history>` |

Label endpoint sequences as endpoints. Do not describe a connecting line as a continuous physical history.

### 3.4 Phase routing

![`<F##>` phase routing](plots/<plot-root>/<branch>/03-phase-routing.png)

Report liquid/vapour routing to brine/steam. Explain that routing is diagnostic unless the setup explicitly defines a routing criterion.

### 3.5 Y010/Y030/total liquid distribution

![`<F##>` liquid distribution](plots/<plot-root>/<branch>/04-liquid-distribution.png)

Report total liquid, Y030, Y010, and diagnostic fractions. Do not call Y010/Y030 a validated free-surface or stationary-pool measure without separate support.

### 3.6 Brine-entry pressure and brine flow

![`<F##>` brine hydraulics](plots/<plot-root>/<branch>/05-brine-pressure-flow.png)

Report static/total-pressure margin and brine flow. Treat endpoint associations as solver-state diagnostics, not physical-time causality.

### 3.7 Branch-specific cross-plots

![`<F##>` cross-plots](plots/<plot-root>/<branch>/06-cross-plots.png)

Use only this branch’s states and label plots as associations. If there are fewer than two valid states, show an explicit not-calculable panel.

### 3.8 Ramp-response summary

![`<F##>` ramp response](plots/<plot-root>/<branch>/07-ramp-response.png)

For a ramp, show only confirmed stage endpoints against imposed loading. For an immediate-load branch, retain the panel and mark it not applicable.

### 3.9 Branch conclusion

State what this branch establishes and does not establish. Do not rank it against another branch in this section.

## 4. Repeat sections 3.1–3.9 for every owned branch

Complete every branch package before writing the cross-branch section.

## 5. Compact cross-branch summary

Use derived late-window metrics only after all branch sections are complete. Preserve unavailable values as `unavailable`/null; never encode missing histories as zero.

| Branch | Late residual median/P95 | Late abs-imbalance median/P95 | Inventory slope | Report-history status | Evidence status |
|---|---|---|---:|---|---|
| `<F##>` | `<derived or unavailable>` | `<derived or unavailable>` | `<derived or unavailable>` | `<mapped/unmapped/unavailable>` | `<status>` |

Keep endpoint-only context in a separate compact table. This summary is not a winner-selection mechanism.

## 6. Validation, findings, and handoff

Link checkpoint/readback cross-validation, residual evidence, report-history evidence, artifact discovery, and all branch packages. State remaining uncertainties, unresolved lineage, remote-access limits, and that interpretation or continuation remains pending user direction.

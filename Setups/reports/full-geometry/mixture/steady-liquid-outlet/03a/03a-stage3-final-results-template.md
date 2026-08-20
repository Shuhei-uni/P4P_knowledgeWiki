# 03A Stage 3 — Final Results Report

> **Campaign:** 03A Stage 3 — Fluent-Recommended Convergence Sweep  
> **Branches:** F01–F12  
> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](../../../../../full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)  
> **Analysis/plotting authority:** [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md)  
> **Checkpoint/provenance evidence:** [`03a-stage3-results-20260821.md`](./03a-stage3-results-20260821.md) and [`03a-stage3-results-20260821-checkpoints.csv`](./03a-stage3-results-20260821-checkpoints.csv)  
> **Interpretation status:** pending user direction

> **Template rule:** Fill this report from continuous stitched residual histories and recovered Fluent Report File histories. Checkpoint values are provenance/cross-check anchors, not the main convergence evidence.

---

## 1. Experiment objective

Stage 3 is a **numerical convergence/stabilisation experiment** on the unchanged 03A full-geometry steady Mixture case.

> **Objective:** determine whether any Fluent-recommended startup strategy can calm the previously unstable residual behaviour and allow the solution to approach a steady total mass balance, where total mass entering approaches total mass leaving and total liquid inventory becomes approximately stationary.

The branches vary only:

- Mixture startup: full immediately vs carrier-first;
- inlet loading: 100% immediately vs 10→20→40→80→100% ramp;
- momentum URF: 0.7, 0.5, 0.3.

There is **no Stage-3 requirement for a prescribed outlet phase split**. Phase routing is diagnostic evidence used to explain changes in total mass balance and inventory.

### Primary questions

1. Do all available residuals become bounded/stabilising rather than progressively divergent/intermittent?
2. Do total inlet and total outlet mass flow approach one another and stay close over a meaningful window?
3. Does total liquid inventory become approximately stationary rather than continuing to fill or drain?
4. Which numerical intervention, if any, improves all three behaviours at the common full-Mixture 100% condition?

---

## 2. Evidence completeness

<!-- FILL before interpretation. Use complete / partial / unavailable / blocked. -->

| Branch | Residual history | Report-file histories | 100% full Mixture reached | Valid 100% window | Checkpoint cross-check | Overall evidence |
|---|---|---|---|---|---|---|
| F01 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F02 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F03 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F04 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F05 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F06 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F07 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F08 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F09 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F10 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F11 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F12 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |

### Evidence notes

<!-- FILL with source paths, gaps, aliases/duplicates, run-stamp distinctions, and any history/checkpoint mismatch. -->

---

## 3. Compact execution overview

| Branch | Mixture startup | Inlet loading | Momentum URF | Highest valid state | 100% iterations | Terminal status |
|---|---|---|---:|---|---:|---|
| F01 | full | immediate | 0.7 | `<state>` | `<n>` | `<status>` |
| F02 | carrier-first | immediate | 0.7 | `<state>` | `<n>` | `<status>` |
| F03 | full | immediate | 0.5 | `<state>` | `<n>` | `<status>` |
| F04 | carrier-first | immediate | 0.5 | `<state>` | `<n>` | `<status>` |
| F05 | full | immediate | 0.3 | `<state>` | `<n>` | `<status>` |
| F06 | carrier-first | immediate | 0.3 | `<state>` | `<n>` | `<status>` |
| F07 | full | ramped | 0.7 | `<state>` | `<n>` | `<status>` |
| F08 | carrier-first | ramped | 0.7 | `<state>` | `<n>` | `<status>` |
| F09 | full | ramped | 0.5 | `<state>` | `<n>` | `<status>` |
| F10 | carrier-first | ramped | 0.5 | `<state>` | `<n>` | `<status>` |
| F11 | full | ramped | 0.3 | `<state>` | `<n>` | `<status>` |
| F12 | carrier-first | ramped | 0.3 | `<state>` | `<n>` | `<status>` |

<!-- FILL only interpretation-relevant limitations here. Leave detailed operational provenance in the evidence packet. -->

---

## 4. Residual behaviour

### Figure 1 — all stitched scaled residuals

Requirements:

- plot **every available residual** together on log scale;
- include continuity, x/y/z momentum, `k`, `epsilon`, volume fraction when active, and any other available equation;
- preserve gaps;
- mark carrier→Mixture transitions;
- mark 10/20/40/80/100% inlet stages;
- distinguish failure tails from last valid checkpoints.

`[FIGURE PLACEHOLDER]`

### Observations

<!-- FILL: bounded vs expanding envelopes, late-window trends, intermittent spikes, whether k/epsilon actually calm relative to Stage 1, and whether apparent calming survives later iterations. -->

### Comparable late-window residual summary

| Branch | 100% window | Continuity | X-mom | Y-mom | Z-mom | k | epsilon | VF | Overall envelope |
|---|---|---|---|---|---|---|---|---|---|
| `<F##>` | `<iterations>` | `<median/P95>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<decreasing/bounded/expanding>` |

---

## 5. Primary physical convergence evidence

### Figure 2 — mass-flow convergence + imbalance + liquid inventory

Use aligned x-axes and combine:

1. `|total mixture inlet|` and `|total mixture outlet|`;
2. relative mass imbalance;
3. total liquid inventory;
4. inlet-load shading/markers for ramped cases.

`[FIGURE PLACEHOLDER]`

A promising branch should jointly show:

- inlet/outlet flow approaching one another;
- imbalance approaching and remaining near zero rather than merely crossing it once;
- liquid inventory flattening rather than continuously filling/draining.

### Observations

<!-- FILL from continuous histories, not endpoint values. -->

### Matched 100% summary

| Branch | Window | Mean inlet | Mean outlet | Median abs. imbalance | P95 abs. imbalance | Inventory change | Inventory variability | Physical behaviour |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `<F##>` | `<iterations>` | `<kg/s>` | `<kg/s>` | `<%>` | `<%>` | `<kg or %>` | `<metric>` | `<stationary/filling/draining/oscillatory>` |

---

## 6. Phase-routing explanation

### Figure 3 — phase routing through both outlets

Use two compact aligned panels:

- brine outlet: liquid→brine and vapour→brine;
- steam outlet: liquid→steam and vapour→steam.

Optionally normalize by corresponding phase inlet flow.

`[FIGURE PLACEHOLDER]`

<!-- FILL: explain which phase causes changes in total outlet flow / imbalance. Do not label a split as “correct” for Stage 3. -->

---

## 7. Liquid distribution

### Figure 4 — total / Y030 / Y010 liquid inventory

Plot where available:

- total liquid mass;
- Y030 liquid mass;
- Y010 liquid mass.

Optionally derive:

\[
f_{Y010}=M_{l,Y010}/M_{l,total},
\qquad
f_{Y030}=M_{l,Y030}/M_{l,total}.
\]

Do not plot constant geometric-register volumes in the main report.

`[FIGURE PLACEHOLDER]`

<!-- FILL: distinguish total liquid amount from lower-vessel concentration. -->

---

## 8. Brine-entry hydraulic response

### Figure 5 — pressure margin + brine flow

Combine:

- brine-entry static pressure minus outlet pressure;
- brine-entry total pressure minus outlet pressure where useful;
- total brine-outlet and/or liquid-to-brine flow.

`[FIGURE PLACEHOLDER]`

Optional cross-plot:

\[
P_{entry}-P_{out}
\quad\text{vs}\quad
\dot m_{brine}.
\]

<!-- FILL as solver-state association, not physical-time causality. -->

---

## 9. Progressive-loading response

### Figure 6 — response vs inlet loading

For ramped branches, summarize late-window response at 10/20/40/80/100% for:

- relative mass imbalance;
- total liquid inventory;
- total outlet flow;
- brine-entry pressure margin;
- compact residual-envelope metric.

`[FIGURE PLACEHOLDER]`

<!-- FILL: identify whether low/intermediate-load improvements survive at 100%. -->

---

## 10. Useful cross-variable diagnostics

Only retain cross-plots that materially explain the result. Candidate pairs:

- `|mass imbalance|` vs total liquid inventory;
- brine-entry pressure margin vs brine flow;
- liquid inventory vs liquid-to-brine flow;
- rolling residual-activity metric vs `|mass imbalance|`.

`[OPTIONAL FIGURE PLACEHOLDER(S)]`

Do not present correlation along steady iterations as proof of physical cause.

---

## 11. Main matched 100% cross-branch comparison

### Figure 7 — 100% histories overlaid

Compare valid branches using `iterations since entering full-Mixture 100%` where useful.

Recommended overlays:

- residual histories or compact residual-envelope metric;
- relative mass imbalance;
- total liquid inventory.

`[FIGURE PLACEHOLDER]`

| Branch | Strategy | 100% iterations | Residual envelope | Median abs. imbalance | Imbalance trend | Inventory trend | Failure? | Evidence strength |
|---|---|---:|---|---:|---|---|---|---|
| `<F##>` | `<M/S/U>` | `<n>` | `<summary>` | `<%>` | `<trend>` | `<trend>` | `<yes/no>` | `<complete/partial>` |

### Comparison observations

<!-- FILL:
- branches without useful 100% evidence;
- calmer residuals but poor mass balance;
- better mass balance but continued inventory drift;
- branches showing both bounded residuals and improving/stationary physical behaviour.
Do not choose a winner unless explicitly delegated.
-->

---

## 12. Checkpoint cross-validation

| Branch/checkpoint | History value | Checkpoint readback | Difference | Consistent? | Note |
|---|---:|---:|---:|---|---|
| `<metric @ iteration>` | `<value>` | `<value>` | `<difference>` | `<yes/no>` | `<note>` |

<!-- Preserve conflicts explicitly. -->

---

## 13. Evidence-led findings

### Solver behaviour
- `<finding>`

### Mass/inventory behaviour
- `<finding>`

### Effect of Stage-3 interventions
- `<carrier-first finding>`
- `<progressive-loading finding>`
- `<momentum-URF finding>`

### Diagnostic outlet/phase behaviour
- `<finding>`

---

## 14. What Stage 3 has and has not established

### Established
- `<supported claim>`

### Not established
- prescribed outlet phase-separation performance;
- validated physical operating point;
- mesh independence;
- `<other unresolved point>`.

---

## 15. Interpretation handoff

**Interpretation status:** pending user direction.

The evidence should enable these questions:

1. Which branch, if any, is the most promising continuation state?
2. Does that branch need a longer 100% run before judging steady state?
3. Should the next decision prioritize stable mass closure, residual envelope, or continued improvement at 100%?
4. Should the follow-up be a turbulence-model test, return-to-authority URF continuation, or another numerical intervention?

---

## 16. Evidence links

- Stitched residual JSON/plots: `<path>`
- Report-history JSON/plots: `<path>`
- Composite figures: `<path>`
- Checkpoint CSV: [`03a-stage3-results-20260821-checkpoints.csv`](./03a-stage3-results-20260821-checkpoints.csv)
- Evidence packet: [`03a-stage3-results-20260821.md`](./03a-stage3-results-20260821.md)
- Analysis/plotting plan: [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md)

---

## Agent completion checklist

- [ ] Stitch all available residual histories.
- [ ] Plot every available residual equation.
- [ ] Recover all available Report File `.out` histories.
- [ ] Preserve gaps and missing data; do not interpolate.
- [ ] Map duplicate reports to canonical quantities and verify expected duplicates.
- [ ] Mark carrier/full-Mixture and inlet-load transitions.
- [ ] Build the mass-flow + imbalance + liquid-inventory composite figure.
- [ ] Build diagnostic phase-routing, liquid-distribution, brine-pressure/flow, and ramp-response figures where supported.
- [ ] Compare valid branches at matched full-Mixture 100% condition.
- [ ] Cross-check histories against checkpoint readbacks.
- [ ] Keep operational detail in the evidence packet rather than bloating this report.
- [ ] Distinguish steady-iteration association from physical-time causality.
- [ ] State limitations before interpretation.
- [ ] Leave final branch selection/next-step interpretation to the user unless explicitly delegated.

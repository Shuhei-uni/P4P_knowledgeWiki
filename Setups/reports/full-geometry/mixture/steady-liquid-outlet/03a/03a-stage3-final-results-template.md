# 03A Stage 3 — Final Results Report

> **Campaign:** 03A Stage 3 — Fluent-Recommended Convergence Sweep  
> **Branches:** F01–F12  
> **Setup authority:** [`03a-stage3-fluent-recommended-convergence-sweep.md`](../../../full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)  
> **Analysis/plotting authority:** [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md)  
> **Checkpoint/provenance evidence:** [`03a-stage3-results-20260821.md`](./03a-stage3-results-20260821.md) and [`03a-stage3-results-20260821-checkpoints.csv`](./03a-stage3-results-20260821-checkpoints.csv)  
> **Interpretation status:** pending user direction

> **Template rule:** This report is intended to be filled from the continuous stitched residual histories and recovered Fluent Report File histories. Do not simply copy checkpoint endpoint tables into the narrative. Checkpoints are validation anchors and provenance evidence.

---

## 1. Experiment objective

Stage 3 is a **numerical convergence/stabilisation experiment** on the unchanged 03A full-geometry steady Mixture case.

The practical objective is:

> **Determine whether any Fluent-recommended startup strategy can calm the previously unstable residual behaviour and allow the full-geometry Mixture solution to approach a steady total mass balance, where total mass entering the separator approaches total mass leaving it and the liquid inventory becomes approximately stationary.**

The Stage-3 branches vary only:

- Mixture-equation startup: full Mixture immediately vs carrier-first staging;
- inlet/inertial loading: full speed immediately vs 10→20→40→80→100% ramp;
- momentum URF: 0.7, 0.5, or 0.3.

There is **no Stage-3 requirement** for a prescribed liquid/vapour outlet split. Phase-routing quantities are diagnostic: they help explain changes in total mass balance, inventory, and outlet behaviour, but are not themselves the pass/fail criterion.

### Primary questions

1. **Residual behaviour:** do all available solver residuals become bounded/stabilising rather than progressively more intermittent or divergent?
2. **Mass convergence:** do total inlet and total outlet mass flow approach one another and remain close over a meaningful late-iteration window?
3. **Inventory stationarity:** does total liquid inventory approach a bounded/stationary condition rather than continuing to fill or drain?
4. **Numerical-strategy response:** which Stage-3 intervention, if any, most clearly improves those behaviours when the case reaches the common full-Mixture 100% operating condition?

---

## 2. Evidence recovered

<!-- FILL: Complete this table before interpretation. Use complete / partial / unavailable / not applicable / blocked. -->

| Branch | Stitched residual history | Report-file history | Full-Mixture 100% reached | Valid 100% comparison window | Checkpoint cross-check | Evidence status |
|---|---|---|---|---|---|---|
| F01 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F02 | `<status>` | `<status>` | no/partial | N/A | `<status>` | `<status>` |
| F03 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F04 | `<status>` | `<status>` | no/partial | N/A | `<status>` | `<status>` |
| F05 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F06 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F07 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F08 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F09 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F10 | `<status>` | `<status>` | no | N/A | `<status>` | `<status>` |
| F11 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |
| F12 | `<status>` | `<status>` | yes | `<window>` | `<status>` | `<status>` |

### Evidence notes

<!-- FILL:
- residual source files / stitched JSON paths;
- report-history manifest paths;
- missing/gapped histories;
- duplicate report names mapped to canonical quantities;
- run-stamp distinctions that must not be merged;
- any checkpoint/report-history mismatch.
-->

---

## 3. Execution overview

Keep this section compact. Its purpose is to establish which branches provide useful scientific evidence, not to retell every execution event.

| Branch | Mixture startup | Inlet loading | Momentum URF | Highest valid state | 100% full-Mixture iterations | Terminal status |
|---|---|---|---:|---|---:|---|
| F01 | full immediately | 100% immediately | 0.7 | `<state>` | `<iterations>` | `<status>` |
| F02 | carrier-first | 100% immediately | 0.7 | `<state>` | `<iterations>` | `<status>` |
| F03 | full immediately | 100% immediately | 0.5 | `<state>` | `<iterations>` | `<status>` |
| F04 | carrier-first | 100% immediately | 0.5 | `<state>` | `<iterations>` | `<status>` |
| F05 | full immediately | 100% immediately | 0.3 | `<state>` | `<iterations>` | `<status>` |
| F06 | carrier-first | 100% immediately | 0.3 | `<state>` | `<iterations>` | `<status>` |
| F07 | full immediately | ramped | 0.7 | `<state>` | `<iterations>` | `<status>` |
| F08 | carrier-first | ramped | 0.7 | `<state>` | `<iterations>` | `<status>` |
| F09 | full immediately | ramped | 0.5 | `<state>` | `<iterations>` | `<status>` |
| F10 | carrier-first | ramped | 0.5 | `<state>` | `<iterations>` | `<status>` |
| F11 | full immediately | ramped | 0.3 | `<state>` | `<iterations>` | `<status>` |
| F12 | carrier-first | ramped | 0.3 | `<state>` | `<iterations>` | `<status>` |

### Execution limitations relevant to interpretation

<!-- FILL: only limitations that affect the scientific comparison. Examples: FPE before 100%, transport gap, different 100% iteration counts, incomplete report histories. Leave detailed operational provenance in the evidence packet. -->

---

## 4. Residual behaviour

### Figure 1 — stitched scaled residual histories

**Plot requirements**

- plot every available residual equation together on a logarithmic y-axis;
- include continuity, x/y/z momentum, `k`, `epsilon`, and volume fraction when active;
- preserve missing iterations as gaps;
- mark carrier-only → full-Mixture transitions;
- mark 10%, 20%, 40%, 80%, and 100% inlet-loading transitions for ramped branches;
- annotate numerical-failure tails separately from the last valid checkpoint where applicable.

`[FIGURE PLACEHOLDER — all residual histories / selected branch panels or branch comparison layout]`

### Residual observations

<!-- FILL: describe measured patterns only before interpretation. Suggested structure:
- which branches show expanding/unbounded residual envelopes;
- which show bounded but oscillatory behaviour;
- which show decreasing/stationary late envelopes;
- whether k/epsilon intermittency is materially calmer than the Stage-1 behaviour;
- whether any apparent calm period is followed by later numerical failure.
Do not reduce this section to endpoint residual values alone.
-->

### Late-window residual summary

<!-- FILL: derive comparable statistics over a clearly stated late window at the 100% full-Mixture condition. Suggested metrics: median and P95 for each residual; log-slope or beginning-vs-end envelope ratio. Do not invent a universal convergence threshold. -->

| Branch | 100% window | Continuity | X-mom | Y-mom | Z-mom | k | epsilon | Volume fraction | Envelope assessment |
|---|---|---|---|---|---|---|---|---|---|
| `<F##>` | `<iterations>` | `<median/P95>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<bounded / decreasing / expanding>` |

---

## 5. Primary physical convergence evidence

This is the central physical section of the report.

### Figure 2 — mass-flow convergence and liquid inventory

Use aligned iteration axes and combine:

1. `|total mixture inlet flow|` and `|total mixture outlet flow|`;
2. relative full-domain mass imbalance;
3. total liquid inventory;
4. inlet-loading level/stage shading for ramped branches where useful.

`[FIGURE PLACEHOLDER — composite mass-flow / imbalance / inventory history]`

### What this figure is intended to answer

A branch is more promising if the continuous history jointly shows:

- inlet and outlet mass flow approaching one another;
- relative imbalance decreasing toward and/or remaining near zero;
- total liquid inventory becoming flatter rather than continuously increasing or decreasing.

These conditions should be evaluated together. A low endpoint imbalance is not sufficient if it is one crossing inside a large oscillation. Likewise, calmer residuals are not sufficient if the physical mass balance continues to drift.

### Mass-convergence observations

<!-- FILL:
- identify sustained approach to in≈out versus one-off crossings;
- identify persistent positive/negative imbalance;
- identify oscillation amplitude and whether it shrinks;
- state whether liquid inventory is filling, draining, or becoming stationary;
- note whether behaviour changes materially when the ramp reaches 100%.
-->

### Late-window physical summary at matched 100% condition

<!-- FILL: use a common window length where available. If branches have different history lengths, state the window basis explicitly. -->

| Branch | 100% comparison window | Mean inlet | Mean outlet | Median abs. relative imbalance | P95 abs. imbalance | Liquid-inventory change over window | Inventory variability | Physical-state assessment |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `<F##>` | `<iterations>` | `<kg/s>` | `<kg/s>` | `<%>` | `<%>` | `<kg or %>` | `<metric>` | `<filling / draining / stationary-ish / oscillatory>` |

---

## 6. Phase-routing explanation

Phase routing is **diagnostic**, not the Stage-3 success criterion.

### Figure 3 — phase routing through both outlets

Use two aligned panels or an equivalent compact layout:

**Brine outlet**

- liquid → brine;
- vapour → brine.

**Steam outlet**

- liquid → steam;
- vapour → steam.

Where useful, normalize each outgoing phase flow by its corresponding inlet phase flow.

`[FIGURE PLACEHOLDER — phase-routing histories]`

### Routing observations

<!-- FILL: use routing to explain changes in total outlet flow or mass imbalance. Examples:
- whether an outlet-flow increase is predominantly liquid or vapour;
- whether an apparent closure improvement coincides with a large routing change;
- whether phase routing stabilises or continues to reorganise.
Do not call a particular outlet split "correct" in Stage 3 unless a separate criterion is explicitly introduced.
-->

---

## 7. Liquid distribution within the separator

### Figure 4 — total and lower-vessel liquid inventory

Plot together where available:

- total liquid mass;
- Y030 liquid mass;
- Y010 liquid mass.

Also derive, when numerically meaningful:

\[
f_{Y010}=\frac{M_{l,Y010}}{M_{l,total}},
\qquad
f_{Y030}=\frac{M_{l,Y030}}{M_{l,total}}.
\]

Do not plot constant geometric register volumes as time histories in the main report.

`[FIGURE PLACEHOLDER — total/Y030/Y010 inventory and/or normalized lower-vessel fractions]`

### Liquid-distribution observations

<!-- FILL: distinguish total inventory from where liquid is concentrated. Describe associations with loading or outlet behaviour without treating iteration order as physical-time causality. -->

---

## 8. Brine-entry hydraulic response

### Figure 5 — brine-entry pressure and brine flow

Combine:

- brine-entry static-pressure margin relative to the 1.120 MPa gauge outlet;
- brine-entry total-pressure margin where useful;
- total brine-outlet flow and/or liquid-to-brine flow.

`[FIGURE PLACEHOLDER — brine-entry pressure margin vs brine flow]`

### Hydraulic-response observations

<!-- FILL: describe whether pressure margin and brine flow move through a coherent relationship or whether they remain highly scattered/unstable. This is an association within the steady iteration path, not proof of time-domain causality. -->

### Optional cross-plot

Plot:

\[
P_{entry}-P_{out}
\quad\text{vs}\quad
\dot m_{brine}
\]

`[FIGURE PLACEHOLDER — pressure/flow cross-plot if informative]`

---

## 9. Progressive-loading response

This section applies mainly to F07–F12.

### Figure 6 — response to inlet loading

At each confirmed load level:

\[
10\%,\;20\%,\;40\%,\;80\%,\;100\%
\]

summarize late-window values for:

- relative mass imbalance;
- total liquid inventory;
- brine-entry pressure margin;
- total outlet flow;
- a compact residual-envelope metric.

`[FIGURE PLACEHOLDER — loading-response curves]`

### Loading-response observations

<!-- FILL: because inlet loading is a deliberate intervention, this section can make stronger statements about the numerical response to increasing loading. Identify whether improvements at low/intermediate loading survive the transition to 100%. -->

---

## 10. Cross-variable diagnostic plots

Use only the cross-plots that reveal a meaningful relationship. Do not include every possible pair.

### Candidate A — mass imbalance vs total liquid inventory

\[
M_l
\quad\text{vs}\quad
|\epsilon_m|
\]

`[OPTIONAL FIGURE PLACEHOLDER]`

### Candidate B — liquid inventory vs liquid-to-brine flow

\[
M_l
\quad\text{vs}\quad
\dot m_{l,B}
\]

`[OPTIONAL FIGURE PLACEHOLDER]`

### Candidate C — residual activity vs physical mass imbalance

Define a documented rolling residual-activity metric, for example a median/P95 measure in log residual space, then compare it with absolute relative mass imbalance.

`[OPTIONAL FIGURE PLACEHOLDER]`

### Cross-variable observations

<!-- FILL: select only relationships that materially help explain the run. Do not over-interpret correlation as physical cause. -->

---

## 11. Matched 100% cross-branch comparison

This is the main branch-to-branch comparison. Include only branches with a valid full-Mixture 100% operating-condition history.

### Figure 7 — selected 100% histories overlaid

Recommended overlays for the most informative surviving branches:

- all-residual comparison or compact residual-envelope comparison;
- relative mass imbalance;
- total liquid inventory.

Normalize iteration to `iterations since entering full-Mixture 100% condition` when that improves comparability.

`[FIGURE PLACEHOLDER — cross-branch 100% comparison]`

### Quantitative comparison table

| Branch | Strategy | 100% iterations available | Residual envelope | Median abs. mass imbalance | Imbalance trend | Inventory trend | Numerical failure? | Evidence strength |
|---|---|---:|---|---:|---|---|---|---|
| `<F##>` | `<M/S/U>` | `<n>` | `<summary>` | `<%>` | `<improving/stationary/worsening>` | `<filling/draining/stationary>` | `<yes/no>` | `<complete/partial>` |

### Comparison observations

<!-- FILL:
- Which branches clearly fail to produce useful 100% evidence?
- Which show calmer residuals but poor physical balance?
- Which show better physical balance but continued drift?
- Which, if any, show both bounded residual behaviour and improving/stationary physical balance?
Do not select a final winner here unless interpretation has been explicitly delegated.
-->

---

## 12. Checkpoint cross-validation

Use the checkpoint evidence packet to confirm that continuous histories reproduce the saved-state values at matching iterations within expected extraction/rounding tolerance.

| Branch/checkpoint | History value | Checkpoint readback | Difference | Consistent? | Note |
|---|---:|---:|---:|---|---|
| `<metric @ F## iteration>` | `<value>` | `<value>` | `<difference>` | `<yes/no>` | `<note>` |

### Conflicts

<!-- FILL: preserve any mismatch or old-report conflict explicitly. Do not silently choose one source. -->

---

## 13. Evidence-led findings

Keep these as neutral observations unless interpretation has been explicitly requested.

### Solver behaviour

- `<finding supported by residual history>`
- `<finding>`

### Mass/inventory behaviour

- `<finding supported by continuous report histories>`
- `<finding>`

### Effect of Stage-3 interventions

- `<finding about carrier-first staging>`
- `<finding about progressive loading>`
- `<finding about momentum URF>`

### Diagnostic phase/outlet behaviour

- `<finding, explicitly secondary to primary convergence objective>`

---

## 14. What Stage 3 has and has not established

### Established by the available evidence

- `<fill only supported claims>`

### Not established

- `<e.g. prescribed phase-separation performance>`
- `<e.g. validated physical operating point>`
- `<e.g. mesh independence>`
- `<other unresolved points>`

---

## 15. Interpretation handoff

**Interpretation status:** pending user direction.

The final evidence should support focused questions such as:

1. Which branch, if any, should be treated as the most promising numerical continuation state?
2. Should the next decision prioritize the smallest/stablest mass imbalance, the calmest residual envelope, or the branch showing the clearest continued improvement at 100%?
3. Does a promising branch need a longer 100% continuation before judging steady state?
4. Should the result motivate a follow-up turbulence-model experiment, a return-to-authority URF continuation, or another numerical intervention?

Do not answer these automatically unless interpretation is explicitly delegated.

---

## 16. Evidence links

<!-- FILL with exact repository/local artifact paths. -->

- Stitched residual JSON/plots: `<path>`
- Recovered report-history JSON/plots: `<path>`
- Composite-figure output directory: `<path>`
- Checkpoint CSV: [`03a-stage3-results-20260821-checkpoints.csv`](./03a-stage3-results-20260821-checkpoints.csv)
- Preserved evidence packet: [`03a-stage3-results-20260821.md`](./03a-stage3-results-20260821.md)
- Analysis/plotting plan: [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md)

---

## Agent completion checklist

Before calling this report complete:

- [ ] Recover and stitch all available residual histories.
- [ ] Plot every available residual equation, not only continuity/`k`/`epsilon`.
- [ ] Recover all available native Report File `.out` histories.
- [ ] Record missing/gapped histories explicitly; do not interpolate.
- [ ] Map duplicate report definitions to canonical quantities and verify duplicates agree where expected.
- [ ] Mark all carrier/full-Mixture and inlet-loading stage transitions.
- [ ] Build the mass-flow + relative-imbalance + liquid-inventory composite figure.
- [ ] Build phase-routing, lower-vessel inventory, brine-pressure/flow, and ramp-response figures where supported.
- [ ] Compare valid branches at like-for-like full-Mixture 100% conditions.
- [ ] Cross-check continuous histories against saved checkpoint readbacks.
- [ ] Keep checkpoint provenance in the evidence packet instead of bloating this report with operational detail.
- [ ] Distinguish steady-iteration association from physical-time causality.
- [ ] State evidence limitations before interpretation.
- [ ] Leave branch selection/next-step interpretation to the user unless explicitly delegated.

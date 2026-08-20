# 03A Stage 3 — Results Analysis and Plotting Plan

> **Campaign:** 03A Stage 3 — Fluent-Recommended Convergence Sweep  
> **Scope:** F01–F12  
> **Purpose:** define how the residual histories and Fluent report-monitor histories should be reduced into a detailed but useful scientific results report.  
> **Primary reporting principle:** use continuous histories as the main evidence; use saved checkpoint readbacks as validation, lineage anchors, and endpoint cross-checks.  
> **Interpretation status:** analysis design only — this document does not select a winning branch.

---

## 1. Stage-3 objective to keep central

Stage 3 is primarily a **numerical convergence/stabilisation experiment**, not an outlet-routing optimisation study.

The practical objective is:

> **Determine whether any Fluent-recommended startup strategy can calm the strongly oscillatory turbulence behaviour, especially the previously problematic `k` and `epsilon` response, and allow the unchanged full-geometry Mixture case to approach a steady mass balance where total mass entering the separator approaches total mass leaving it.**

The physical case is deliberately frozen. F01–F12 vary only numerical startup/continuation strategy through:

- Mixture-equation staging;
- progressive inlet/inertial loading;
- momentum under-relaxation.

There is **no Stage-3 requirement** that a prescribed fraction of liquid must leave through the brine outlet or vapour through the steam outlet.

Phase-routing data remains valuable, but in this experiment it is primarily **diagnostic evidence used to explain changes in total mass balance and liquid inventory**, not a pass/fail criterion.

The two main questions are therefore:

1. **Numerical:** do the solver residuals become bounded/stabilising rather than progressively more intermittent or divergent?
2. **Physical steady-state behaviour:** do total inlet and total outlet mass flow approach one another while liquid inventory approaches a bounded/stationary condition?

A numerically completed run is not automatically a useful result, and a visually favourable outlet split at one checkpoint is not sufficient evidence of steady state.

---

## 2. Evidence hierarchy

Stage 3 has two full time-series evidence layers.

### 2.1 Residual histories

Use the stitched native Fluent residual histories across all available execution segments.

Plot **every available residual equation**, not only continuity, `k`, and `epsilon`.

Expected equations include, where active:

- continuity;
- x-velocity;
- y-velocity;
- z-velocity;
- turbulent kinetic energy `k`;
- turbulent dissipation rate `epsilon`;
- phase-2 volume fraction.

The complete history matters because Stage 3 explicitly contains long blocks, staged equation activation, staged inlet loading, transport interruptions, recovery continuations, and in some cases numerical failure tails.

Preserve:

- source-segment boundaries;
- stage boundaries;
- genuine gaps;
- verified duplicate removal only;
- failure tails when they are attributable to the run;
- missing iterations as missing rather than interpolated.

### 2.2 Fluent report-monitor histories

Use the native report-file `.out` histories as the main physical evidence wherever they were successfully captured.

The P0 instrumentation includes roughly thirty-plus reports across:

- mixture and phase mass fluxes at each inlet/outlet;
- total mixture inlet flow;
- total mixture outlet flow;
- individual steam- and brine-outlet total flow;
- full-domain mass imbalance;
- relative mass imbalance;
- phase-routing flows;
- total-domain liquid inventory;
- Y010 liquid inventory;
- Y030 liquid inventory;
- brine-entry static pressure;
- brine-entry total pressure.

Not every raw report deserves its own figure. Several are deliberately overlapping or redundant representations of the same physical quantity. The purpose of the analysis layer is to convert these histories into a small number of scientifically useful composite figures.

### 2.3 Checkpoint readbacks

Saved `.cas.h5/.dat.h5` checkpoint readbacks remain important for:

- identity and lineage verification;
- confirming report-history values at known checkpoints;
- recovering quantities when a continuous report history is unavailable;
- preserving endpoint evidence for interrupted or failed runs;
- checking sign conventions and derived formulas.

However, checkpoint values should not dominate claims about convergence when a full continuous history exists.

For example, an endpoint imbalance of `-12%` can represent either a steadily improving solution or a strongly oscillatory solution that happened to end near `-12%`. The report history distinguishes those cases.

---

## 3. Semantic reduction of the raw monitor set

Before plotting, group the raw report histories by physical meaning and detect aliases/duplicates.

### 3.1 Canonical evidence families

| Evidence family | Typical raw inputs | Main purpose |
|---|---|---|
| Residuals | all active residual equations | numerical settling |
| Total mass closure | total inlet, total outlet, full-domain imbalance, relative imbalance | **primary physical convergence evidence** |
| Liquid inventory | total liquid mass/volume, Y010, Y030 | **primary steady-state support evidence** |
| Phase routing | liquid/vapour to brine/steam outlets | explain total-flow changes |
| Brine hydraulics | brine-entry static/total pressure, brine total flow | explain lower-outlet response |
| Inlet loading | inlet mass flows and known 10/20/40/80/100% schedule | explain controlled ramp response |
| Duplicate/raw fluxes | generic phase/boundary flux reports overlapping dedicated reports | validation / supplementary evidence |

### 3.2 Duplicate and near-duplicate detection

Several reports should represent the same or nearly the same physical quantity, for example a generic phase flux on `brineoutlet` and the dedicated `routing_liquid_to_brine` report.

The analysis should:

1. map reports to a canonical semantic ID;
2. compare overlapping histories over shared iterations;
3. identify exact or near-identical pairs within a declared numerical tolerance;
4. retain one canonical series for figures;
5. keep the duplicate as a validation source rather than plotting it again;
6. flag unexpected disagreement rather than silently choosing one.

Do not discard raw histories from the evidence bundle.

### 3.3 Constant reports

Geometric Y010/Y030 volume reports are useful for definitions and normalisation but are expected to be constant. They generally do not deserve time-history figures.

Use them to derive occupancy/fraction metrics where useful.

---

# 4. Core figure families

The final report should be organised around a small number of composite figures that answer explicit scientific questions.

## Figure family 1 — complete stitched residual history

### Question

> **Did the numerical solution as a whole become more settled, and which equations responded positively or negatively to each Stage-3 intervention?**

### Plot

Plot all available scaled residuals together on a logarithmic y-axis:

\[
R_c,\ R_u,\ R_v,\ R_w,\ R_k,\ R_\varepsilon,\ R_{\alpha_l}
\]

where available.

For staged/ramped branches, annotate or shade:

- carrier-only vs full-Mixture transition;
- 10%, 20%, 40%, 80%, and 100% inlet stages;
- recovery/continuation boundaries where relevant;
- terminal numerical failure if present.

### Interpretation focus

Do not judge the run only by whether residuals cross a conventional threshold.

Characterise whether residual behaviour is:

- decreasing;
- bounded/stationary but oscillatory;
- increasingly intermittent;
- expanding/diverging;
- changed sharply by a deliberate stage transition.

`k` and `epsilon` deserve specific numerical summaries because their intermittent behaviour motivated Stage 3, but the visual residual figure should contain **all equations**.

Useful late-window summaries may include:

- median;
- P95;
- log-range or interquantile spread;
- slope/trend of log residual;
- maximum excursion;
- fraction of points above a declared branch-relative threshold.

These summaries describe the histories; they are not automatic convergence criteria unless explicitly adopted later.

---

## Figure family 2 — primary steady-state/convergence figure

### Question

> **Is the physical solution moving toward a stationary state with total mass in approximately equal to total mass out?**

This should be one of the central figures in the report.

### Recommended aligned panels

#### Panel A — total flow

\[
|\dot m_{in}|,\qquad |\dot m_{out}|
\]

against native iteration.

#### Panel B — relative mass imbalance

Use the native relative imbalance where available, with the definition made explicit:

\[
\epsilon_m=
\frac{|\dot m_{in}+\dot m_{out}|}{|\dot m_{in}|}
\]

under Fluent's signed mass-flow convention.

Also preserve the signed imbalance separately in the data bundle when it helps diagnose filling vs draining direction.

#### Panel C — total liquid inventory

Prefer liquid mass for the main comparison:

\[
M_{l,total}
\]

with liquid volume retained as a supporting quantity.

#### Stage annotation

For ramped cases, annotate the inlet-loading stages on the shared x-axis rather than creating a separate plot unless a dedicated loading-response figure is being shown.

### Why these belong together

Mass closure and inventory must be interpreted together.

If:

\[
|\dot m_{out}|>|\dot m_{in}|
\]

while total liquid inventory is falling, the solver is draining stored/domain liquid rather than representing stationary through-flow.

If:

\[
|\dot m_{out}|<|\dot m_{in}|
\]

while liquid inventory continues increasing, the domain is accumulating liquid and is not steady.

The strongest Stage-3 outcome would be a branch in which:

- inlet and outlet flow converge toward one another;
- relative mass imbalance falls and remains bounded near a small range;
- total liquid inventory approaches a bounded/stationary range;
- residual behaviour also becomes bounded/stabilising.

---

## Figure family 3 — outlet phase-routing explanation

### Question

> **What phase-flow changes explain the total outlet and mass-balance behaviour?**

Phase routing is diagnostic in Stage 3 rather than an acceptance criterion.

### Recommended aligned panels

#### Brine outlet

\[
\dot m_{l,B},\qquad \dot m_{v,B}
\]

#### Steam outlet

\[
\dot m_{l,S},\qquad \dot m_{v,S}
\]

Use a consistent outward-positive plotting convention if the raw Fluent signs are transformed, and preserve the raw sign convention in the evidence bundle.

### Useful derived normalised quantities

Where useful:

\[
f_{l,B}=\frac{|\dot m_{l,B}|}{|\dot m_{l,in}|}
\]

\[
f_{l,S}=\frac{|\dot m_{l,S}|}{|\dot m_{l,in}|}
\]

\[
f_{v,B}=\frac{|\dot m_{v,B}|}{|\dot m_{v,in}|}
\]

\[
f_{v,S}=\frac{|\dot m_{v,S}|}{|\dot m_{v,in}|}
\]

These help answer questions such as:

- did improved total mass closure occur because liquid drainage settled?
- did vapour short-circuit through the brine outlet increase or decrease?
- did liquid carryover to the steam outlet change?
- did both outlets move together after a numerical transition?

Do **not** call a case better or worse solely because of one routing percentage unless a later experiment explicitly adopts an outlet-routing criterion.

---

## Figure family 4 — liquid-distribution / lower-vessel inventory

### Question

> **Is liquid inventory merely changing in total, or is its spatial concentration within the lower vessel also changing?**

### Main histories

Plot together where scales permit:

\[
M_{l,total},\qquad M_{l,Y030},\qquad M_{l,Y010}
\]

or use normalised lower-region fractions:

\[
f_{Y010}=\frac{M_{l,Y010}}{M_{l,total}}
\]

\[
f_{Y030}=\frac{M_{l,Y030}}{M_{l,total}}
\]

### Purpose

Two branches can have similar total liquid inventory but very different lower-vessel distributions.

This figure helps distinguish:

- total-domain accumulation/depletion;
- concentration of liquid near/below the brine outlet region;
- redistribution of liquid through the domain during staged loading.

Y010/Y030 remain **diagnostic regions**, not claims that Mixture produces a sharply defined physical pool/free surface.

---

## Figure family 5 — brine-entry hydraulic response

### Question

> **How does the lower-outlet pressure state relate to the brine-outlet flow response and inventory behaviour?**

### Recommended aligned panels

#### Pressure margin

Plot:

\[
P_{entry,static}-P_{brine,outlet}
\]

and, where useful:

\[
P_{entry,total}-P_{brine,outlet}
\]

#### Brine flow

Plot total brine-outlet mass flow and optionally liquid-to-brine flow.

A third panel may show total liquid inventory when it materially clarifies the response.

### Interpretation language

This figure can support statements such as:

> a higher/lower brine-entry pressure margin was associated with a corresponding change in brine-outlet flow and domain inventory during this solver state.

Do not automatically convert iteration ordering into physical-time causality. This is a steady iterative calculation.

---

## Figure family 6 — controlled inlet-loading response

This is particularly important for the progressive-loading branches.

### Question

> **How did the solution respond as the deliberately controlled inlet loading was increased from 10% to the final 100% operating condition?**

The inlet schedule is an actual controlled intervention:

\[
10\%\rightarrow20\%\rightarrow40\%\rightarrow80\%\rightarrow100\%
\]

For each completed stage, calculate a consistent late-stage window summary for quantities such as:

- relative mass imbalance median and spread;
- total outlet flow;
- total liquid inventory;
- brine-entry pressure margin;
- selected residual envelope statistics;
- phase-routing quantities where informative.

Plot these **against inlet loading**, not only against iteration.

This produces response curves such as:

\[
\text{inlet loading}\rightarrow\epsilon_m
\]

\[
\text{inlet loading}\rightarrow M_l
\]

\[
\text{inlet loading}\rightarrow\Delta P_{brine}
\]

and provides a clearer picture of whether a ramp strategy progressively developed the field or simply moved it between unrelated unstable states.

---

# 5. Cross-variable plots for mechanism/association analysis

Not every useful figure should use iteration on the x-axis.

Cross-plots can exploit the richness of the report histories to identify relationships between numerical and physical quantities.

These should be treated as **association/response diagnostics**, not automatic proof of physical causality.

## 5.1 Mass imbalance vs total liquid inventory

Plot:

\[
M_{l,total}\quad\text{vs}\quad\epsilon_m
\]

This can show whether the branch moves toward low imbalance while liquid inventory approaches a bounded range, or whether apparently improved mass balance occurs only during strong filling/draining states.

For ramped branches, colour/group points by inlet-loading stage if useful.

## 5.2 Brine-entry pressure margin vs brine flow

Plot:

\[
P_{entry}-P_{outlet}\quad\text{vs}\quad\dot m_B
\]

This can reveal whether the lower outlet follows a coherent pressure/flow relationship across the developed solver states.

## 5.3 Total liquid inventory vs liquid-to-brine flow

Plot:

\[
M_{l,total}\quad\text{vs}\quad\dot m_{l,B}
\]

This can help distinguish high-drainage states from high-retention states and clarify how the domain inventory changes across the solver trajectory.

## 5.4 Residual activity vs physical mass balance

Construct a rolling residual-activity metric, for example from the median/spread of the log residual set within a fixed native-iteration window.

Compare it against relative mass imbalance.

The purpose is to distinguish cases where:

- residuals become calmer **and** mass balance improves;
- residuals become calmer but physical closure remains poor;
- mass balance temporarily improves while residual activity worsens.

This is particularly relevant to the Stage-3 objective because solver residual improvement alone is not sufficient.

---

# 6. Cross-branch comparison strategy

The report should not become twelve isolated mini-reports.

Use branch-specific figures only where a branch has a unique event or where the full trajectory itself is scientifically important.

Prefer cross-branch comparisons whenever the operating condition is matched.

## 6.1 Compare like with like

For the main branch ranking/comparison, use only states that are:

- full Mixture active;
- at 100% inlet velocity;
- based on valid histories/checkpoints;
- compared over a declared late-stage native-iteration window.

Do not compare a carrier-only 100% state directly with a full-Mixture 100% state as though they were the same physical model.

Do not treat an 80% ramp stage as directly equivalent to the final 100% operating condition.

## 6.2 Useful matched-condition cross-branch figures

Potential summary plots include:

- relative mass imbalance histories at the 100% stage overlaid across valid branches;
- total liquid inventory histories at the 100% stage overlaid across valid branches;
- final-window residual-envelope summaries by branch;
- late-window mass-imbalance median/spread by branch;
- late-window liquid-inventory slope/spread by branch;
- brine-entry pressure margin by branch;
- paired summary plot of numerical residual activity vs physical mass imbalance.

## 6.3 Do not hide run-length differences

Branches reached different iteration counts and some failed before 100%.

Every cross-branch comparison must state:

- the compared operating state;
- the native-iteration window length;
- whether the branch completed that state;
- whether the final window ends in a numerical failure tail;
- whether the history is complete, partial, or checkpoint-only.

---

# 7. Window statistics and trend summaries

Continuous plots remain the primary evidence, but consistent summary statistics help compare branches.

For each important history, calculate one or more fixed-window summaries such as the final 250, 500, or 1000 native iterations, depending on available branch length and the analysis question.

Potential summaries:

### Residuals

- median;
- P95;
- interquantile range in log space;
- log-slope;
- maximum excursion.

### Relative mass imbalance

- median;
- mean absolute value;
- P95;
- range/interquantile spread;
- slope;
- fraction of window below selected descriptive thresholds.

### Liquid inventory

- median;
- absolute and relative slope;
- P5/P95 or standard deviation;
- change over the window.

### Pressure/flow

- median;
- variability;
- relationship/correlation within a stable solver stage where relevant.

These values should be treated as **descriptive evidence**, not automatically as pass/fail thresholds.

---

# 8. Interpreting iteration histories safely

Stage 3 uses a **steady solver**.

Native iteration is not physical time.

Therefore avoid causal language such as:

> liquid inventory fell because brine flow increased 50 iterations earlier.

A safer evidence statement is:

> the solver moved into a state with higher brine-outlet flow while liquid inventory and mass imbalance changed in the same stage.

Stronger cause/response language is appropriate for deliberate controlled interventions such as:

- increasing inlet loading from one prescribed stage to the next;
- enabling Volume Fraction and Slip Velocity after a carrier-only stage;
- comparing branches whose controlled difference is momentum URF.

Even there, the conclusion is primarily about **numerical response to the controlled strategy**, not physical transient dynamics.

---

# 9. Recommended final Stage-3 report visual structure

The main report should be detailed without becoming an archive dump.

A strong structure is:

## Figure 1 — complete scaled residual history

All active residual equations, with stage transitions and failures annotated.

## Figure 2 — mass-flow convergence + relative imbalance + total liquid inventory

The primary physical steady-state figure.

## Figure 3 — phase routing

Liquid/vapour routing through brine and steam outlets, used to explain total-flow behaviour.

## Figure 4 — lower-vessel liquid distribution

Total/Y030/Y010 inventory or normalised lower-region fractions.

## Figure 5 — brine-entry pressure / brine-flow response

Static/total pressure margin associated with lower-outlet flow and, where useful, inventory.

## Figure 6 — matched 100% cross-branch comparison

Compact comparison of the valid full-Mixture 100% branches using consistent late-window metrics.

## Figure 7 — inlet-loading response

For progressive-loading branches, show how key metrics changed through 10/20/40/80/100% loading.

### Optional mechanism cross-plots

Include only the cross-plots that materially improve interpretation, for example:

- imbalance vs liquid inventory;
- brine pressure margin vs brine flow;
- inventory vs liquid-to-brine flow;
- residual activity vs mass imbalance.

Not every branch needs every figure individually.

---

# 10. Main report questions to answer

The final analysis/report should progressively answer:

1. **Which branches produced enough valid history to analyse?**
2. **Which numerical strategies made the residual system more bounded/stable, including whether the problematic `k` and `epsilon` behaviour calmed down?**
3. **Which strategies moved total inlet and outlet mass flow toward a stationary in≈out condition?**
4. **Did liquid inventory also become bounded, or was an apparent mass-balance improvement simply associated with filling/draining the domain?**
5. **For ramped/staged runs, did improvements survive the transition to the real 100% full-Mixture operating condition?**
6. **What phase-routing and lower-outlet pressure behaviour explains the major changes in total flow and inventory?**
7. **Which branches are credible candidates for further continuation, if any?**

The report should avoid selecting a preferred branch until the evidence has been assembled consistently across these questions.

---

# 11. Suggested data-processing output

The analysis workflow should create a reusable semantic dataset before report plotting.

Suggested structure:

```text
raw residual transcripts
+ raw report .out histories
+ execution/stage metadata
+ checkpoint readback CSV
        ↓
canonicalised time-series dataset
        ↓
derived metrics + stage labels + duplicate map
        ↓
composite branch figures
+ cross-branch figures
+ compact summary tables
        ↓
final Stage-3 results report
```

The canonical dataset should preserve for every series:

- branch;
- run stamp / attempt identity;
- native iteration;
- stage/load label;
- full-Mixture/carrier-only state;
- quantity semantic ID;
- raw report name;
- value;
- units;
- raw Fluent sign convention;
- plotting sign convention if transformed;
- source file/path;
- evidence completeness/status.

Derived data should be generated from this canonical layer rather than repeatedly re-parsing raw files for each plot.

---

# 12. Evidence-quality rules

For every plotted quantity classify source evidence as:

- `complete history`;
- `partial history`;
- `checkpoint-only`;
- `unavailable`;
- `not applicable`.

Do not silently replace a missing monitor history with a checkpoint line or zero series.

Do not interpolate across missing residual/report iterations.

Do not merge separate failed/retry attempts unless lineage proves they are one valid continuation.

If a raw duplicate report conflicts with its canonical counterpart, preserve and investigate the disagreement.

---

# 13. Final interpretation principle

The most useful Stage-3 branch is not simply the one with the smallest residual at its final iteration and not simply the one with the best outlet split at a checkpoint.

The strongest evidence would be a branch showing the combination:

\[
\boxed{
\text{bounded/stabilising residual system}
+
|\dot m_{in}|\approx|\dot m_{out}|
+
\text{bounded liquid inventory}
}
\]

with those behaviours persisting at the final **100% inlet, full-Mixture operating condition**.

Phase routing, Y010/Y030 distribution, and brine-entry pressure should then be used to explain what physical/numerical state produced that behaviour.

That is the central visual and analytical argument the final 03A Stage-3 results report should build.
> **Retired source:** Setups/past/reported/07-pure-phase-split-actual-area.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Pure Liquid / Steam Actual-Area Velocity-Inlet Setup Report

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `07` |
| Lifecycle | `reported` |
| Role | pure-phase split baseline and DPM carryover diagnostic |
| Parent setup | [Phase 1 historical inlet index](../index.md) |
| Evidence-use label | scoped steam-carryover and DPM diagnostic |
| Outcome | needs follow-up |
| Linked report | [07 results](results.md) |

## 1. Purpose

Define the next spiral-inlet setup built from:

- [04-mixed-wet-half-actual-area.md](../purnanto-04-mixed-wet-half-actual-area/setup.md)
- [inlet-regimes interpretation](../../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08c-inlet-loading-sensitivity/inlet-regimes-interpretation.md)
- [Project state and next decision](../../../index.md)

This setup replaces the mixed wet-half inlet with a pure-phase two-zone inlet:

- `inlet_liquid_outer`: pure liquid water;
- `inlet_steam_inner`: pure steam;
- both velocity inlets use the current-area exact-mass velocity `27.118 m/s`.

All other model settings should remain the same as the mixed wet-half actual-area setup unless explicitly stated in this report.

Project linkage:

- setup `07` is the historical split-inlet baseline candidate carried into the
  Project experiment record;
- this setup report defines the concrete branch content;
- the roadmap defines whether setup `07` is only diagnostic, accepted as a baseline candidate, numerically verified, or ready for higher-complexity child branches.

Geometry naming note:

- setup `07` uses the `purnanto` geometry label;
- geometry naming is separate from inlet boundary-condition style, so the split two-phase inlet in setup `07` does not make the geometry `purnantov2`;
- use `purnantov2` only for the later geometry branch with downstream outlet-boundary placement and local spiral-inlet / dish-head cleanup.

Technical companion:

- [07 technical extraction](technical-extraction.md)

Use the technical companion when you need the live Fluent export, the geometry/mesh replay context, and the intended-vs-actual drift log. If the live export and this narrative report disagree, treat the export as the replay authority and record the mismatch explicitly.

## 2. Setup Identity

| Item | Value |
|---|---:|
| Geometry | `purnanto` spiral-inlet BOC separator |
| Parent setup | `04-mixed-wet-half-actual-area.md` |
| Inlet representation | pure liquid / pure steam split inlet |
| Boundary type | two `Velocity Inlet` zones |
| Shared inlet velocity | `27.118 m/s` |
| Full inlet dimensions | `0.724 m x 0.724 m` |
| Full inlet area | `0.524176 m2` |
| Liquid-side area | `0.0048896 m2` |
| Steam-side area | `0.5192864 m2` |
| Liquid-side width along `x` | `0.006754 m` |
| Steam-side width along `x` | `0.717246 m` |
| Purnanto `1600 kJ/kg` liquid target | `116.92 kg/s` |
| Purnanto `1600 kJ/kg` steam target | `80.69 kg/s` |
| Purnanto `1600 kJ/kg` total target | `197.61 kg/s` |

Evidence labels:

- `Reported`: Purnanto baseline phase mass flows and material values inherited through the project setup notes.
- `Calculated`: current-area split, velocity, hydraulic diameters, and mass-flow checks.
- `User-specified`: turbulence intensity and hydraulic-diameter setup change requested for the new velocity-inlet setup.
- `Assumed`: inlet remains a rectangular `0.724 m x 0.724 m` face split along `x`.

## 3. What Changes From Parent Setup

Change only the following items from the mixed wet-half actual-area setup:

1. Replace the mixed wet-half split with pure liquid / pure steam zones.
2. Use the calculated actual-area velocity `27.118 m/s` on both inlet zones.
3. Use phase-zone hydraulic diameters in the velocity-inlet turbulence settings:
   - liquid inlet hydraulic diameter: `0.01338 m`;
   - steam inlet hydraulic diameter: `0.72061 m`.

Do not change the solver stack, material properties, outlet setup, gravity, initialization, discretization schemes, or reporting method unless the case fails and a separate sensitivity run is being defined.

## 4. Inlet Geometry and Split

Full inlet:

```text
W = 0.724 m
H = 0.724 m
A_total = W * H = 0.524176 m2
```

From the current-area exact-mass split:

```text
A_liquid = 0.0048896 m2
A_steam  = 0.5192864 m2
```

If the split is made along the `x` direction while preserving full inlet height:

```text
x_liquid_width = A_liquid / H = 0.0048896 / 0.724 = 0.006754 m
x_steam_width  = A_steam  / H = 0.5192864 / 0.724 = 0.717246 m
```

Place the split line:

```text
0.006754 m from the liquid-side edge
```

or equivalently:

```text
0.717246 m from the steam-side edge
```

Mapping rule:

- liquid side = outer-wall side of the spiral inlet;
- steam side = inner/core side;
- do not name the zones using only screen-left/screen-right wording.

## 5. Boundary Conditions

### Liquid Inlet

| Fluent field | Value |
|---|---:|
| Boundary name | `inlet_liquid_outer` |
| Boundary type | `Velocity Inlet` |
| Velocity specification | normal to boundary |
| Velocity magnitude | `27.118 m/s` |
| Liquid water volume fraction | `1.0` |
| Steam/vapor volume fraction | `0.0` |
| Turbulence intensity | `2.10999999 %` |
| Hydraulic diameter | `0.01338 m` |

### Steam Inlet

| Fluent field | Value |
|---|---:|
| Boundary name | `inlet_steam_inner` |
| Boundary type | `Velocity Inlet` |
| Velocity specification | normal to boundary |
| Velocity magnitude | `27.118 m/s` |
| Liquid water volume fraction | `0.0` |
| Steam/vapor volume fraction | `1.0` |
| Turbulence intensity | `2.10999999 %` |
| Hydraulic diameter | `0.72061 m` |

If Fluent only asks for the secondary phase volume fraction and liquid water is the secondary phase:

```text
inlet_liquid_outer secondary phase VF = 1.0
inlet_steam_inner secondary phase VF  = 0.0
```

## 6. Hydraulic Diameter Calculation

Use:

```text
Dh = 4A / P
Dh = 2ab / (a + b)
```

where:

- `a` = split-zone width;
- `b` = inlet height `0.724 m`.

### Liquid Inlet

```text
a_liquid = 0.0067536 m
b        = 0.724 m

Dh_liquid = 2 * 0.0067536 * 0.724 / (0.0067536 + 0.724)
Dh_liquid = 0.013382 m
```

Fluent input:

```text
Dh_liquid = 0.01338 m
```

### Steam Inlet

```text
a_steam = 0.7172464 m
b       = 0.724 m

Dh_steam = 2 * 0.7172464 * 0.724 / (0.7172464 + 0.724)
Dh_steam = 0.720607 m
```

Fluent input:

```text
Dh_steam = 0.72061 m
```

## 7. Mass-Flow Check

Inputs:

```text
rho_liquid = 881.77 kg/m3
rho_steam  = 5.73 kg/m3
V          = 27.118 m/s
A_liquid   = 0.0048896 m2
A_steam    = 0.5192864 m2
```

Expected inlet mass flows:

```text
m_dot_liquid = 881.77 * 27.118 * 0.0048896 = 116.92 kg/s
m_dot_steam  = 5.73   * 27.118 * 0.5192864 = 80.69 kg/s
m_dot_total  = 197.61 kg/s
```

This preserves the Purnanto `1600 kJ/kg` target mass flow while using the current inlet area.

## 8. Solver and Model Settings to Inherit

Keep the same settings as the parent mixed wet-half actual-area setup:

| Setting | Value |
|---|---:|
| Solver | `Pressure-Based` |
| Time | `Steady` |
| Multiphase model | `Mixture` |
| Primary phase | steam/vapor |
| Secondary phase | liquid water |
| Turbulence model | `RNG k-epsilon` |
| Energy | `Off` |
| Gravity | same as parent setup |
| Operating pressure | same as parent setup |
| Pressure outlets | same as parent setup |
| Pressure-velocity coupling | `SIMPLE` |
| Pressure scheme | `PRESTO!` |
| Momentum scheme | `Second Order Upwind` |
| Turbulence schemes | `Second Order Upwind` |
| Volume fraction scheme | same as parent setup, `QUICK` if available |
| Initialization | `Hybrid Initialization` |

## 8A. Important Model-Family Clarification

Setup `07` should be classified as:

```text
steady Mixture carrier-flow setup
with post-convergence one-way DPM evaluation
```

It should **not** be classified as a primary `DPM` setup by itself.

Reason:

1. the main continuous-field solve for setup `07` is still `Mixture`, not a particle-coupled solve;
2. the DPM injections were added after the continuous solution was already available;
3. baseline DPM interpretation for setup `07` keeps `unsteady particle tracking` off, so particles move through a frozen steady carrier field rather than through a time-evolving transient field;
4. baseline DPM interpretation for setup `07` also keeps continuous-phase source feedback off, so the injected particles do not modify the solved carrier flow.

Practical interpretation:

- setup `07` = `Mixture` baseline with one-way post-processing DPM carryover checks;
- setup `07` is **not** a fully coupled `Mixture + DPM` solve;
- setup `07` is **not** a transient particle-field simulation;
- setup `07` is **not** an `RSM-DPM` or `DPM + Eulerian Wall Film` branch.

This distinction matters because later setup-family branches such as `09a`, `09b`, and `09c` are intended to turn `DPM` into a deliberate next-step modeling direction through smaller staged branches, rather than treating DPM only as an after-the-fact diagnostic on top of the setup `07` carrier field. More complex wall-film and re-entrainment work is now deferred to a later family beyond `09`.

## 9. Checks Before Running

1. Confirm the split creates two real inlet boundary faces.
2. Confirm `inlet_liquid_outer` is the outer-wall side of the spiral inlet.
3. Confirm the `0.006754 m` liquid strip is mesh-resolved.
4. Confirm the velocity is `27.118 m/s` on both inlet zones.
5. Confirm turbulence intensity is `2.10999999 %` on both inlet zones.
6. Confirm hydraulic diameter:

```text
inlet_liquid_outer = 0.01338 m
inlet_steam_inner  = 0.72061 m
```

7. After initialization, run inlet flux reports and check:

```text
liquid inlet ~= 116.92 kg/s
steam inlet  ~= 80.69 kg/s
total inlet  ~= 197.61 kg/s
```

## 10. Result Interpretation Rules

This run can be used to test:

- whether a pure liquid / pure steam split improves inlet realism compared with the mixed wet-half setup;
- whether the very narrow liquid strip remains stable after initialization;
- whether phase-specific hydraulic diameters change near-inlet turbulence behavior.

Do not attribute any difference only to phase segregation unless it is compared against a same-geometry split case with identical hydraulic diameter settings. The hydraulic-diameter change is a deliberate setup change and may affect turbulence quantities near the inlet.

## 11. Evidence to Save

Save at minimum:

```text
case file before run
case/data after initialization
case/data checkpoints during run
residual plot
inlet phase flux report
outlet phase flux report
liquid volume fraction contour near inlet
velocity vectors near inlet and steam outlet
turbulence kinetic energy / epsilon near inlet if available
```

Recommended report label:

```text
PLS-ACTUAL-AREA-HD-2026-05-28
```

## 12. Report-Ready Calculation Block

These equations match the pure liquid / pure steam equal-velocity split used in this setup report and are formatted so they can be copied directly into a rough report.

### 12.1 Inlet Area Sizing From Purnanto `1600 kJ/kg` Mass Flow

```latex
A_{\text{total}} = W H = 0.724 \times 0.724 = 0.524176\ \text{m}^2
```

```latex
Q_{\ell} = \frac{\dot{m}_{\ell}}{\rho_{\ell}} = \frac{116.92}{881.77} = 0.1325969\ \text{m}^3\!/\text{s}
```

```latex
Q_{v} = \frac{\dot{m}_{v}}{\rho_{v}} = \frac{80.69}{5.73} = 14.0820244\ \text{m}^3\!/\text{s}
```

```latex
V = \frac{Q_{\ell} + Q_{v}}{A_{\text{total}}}
= \frac{0.1325969 + 14.0820244}{0.524176}
= 27.1180\ \text{m}/\text{s}
```

```latex
A_{\ell} = \frac{Q_{\ell}}{V} = \frac{0.1325969}{27.1180} = 0.0048896\ \text{m}^2
```

```latex
A_{v} = \frac{Q_{v}}{V} = \frac{14.0820244}{27.1180} = 0.5192864\ \text{m}^2
```

```latex
x_{\ell} = \frac{A_{\ell}}{H} = \frac{0.0048896}{0.724} = 0.0067536\ \text{m}
```

```latex
x_{v} = \frac{A_{v}}{H} = \frac{0.5192864}{0.724} = 0.7172464\ \text{m}
```

### 12.2 Flux-Based Rough Efficiency Equations

For these no-brine-outlet rough checks, use both:

- implied liquid-removal efficiency from steam-line carryover;
- steam-outlet dryness from the outlet phase split.

```latex
\eta_{\text{carryover}} = \left(1 - \frac{\dot{m}_{\ell,\text{steam out}}}{\dot{m}_{\ell,\text{in}}}\right)\times 100
```

```latex
X_{\text{steam out}} = \frac{\dot{m}_{v,\text{steam out}}}{\dot{m}_{v,\text{steam out}} + \dot{m}_{\ell,\text{steam out}}}\times 100
```

## 13. Rough Student-Edition Diagnostic Notes

These results were copied from a rough internal meeting report and should be treated as low-mesh, non-converged diagnostic evidence only.

### Setup 1

Reported fluxes:

```text
steam inlet      = 80.68986325619862 kg/s
steam outlet     = 81.30666537772633 kg/s
liquid inlet     = 116.9264051941613 kg/s
liquid steam out = 10.67444725655621 kg/s
```

Calculated rough carryover-based metrics:

```text
liquid carryover fraction = 10.67444725655621 / 116.9264051941613 = 0.09129 = 9.13 %
implied liquid-removal efficiency = (1 - 10.67444725655621 / 116.9264051941613) * 100 = 90.87 %
steam outlet dryness = 81.30666537772633 / (81.30666537772633 + 10.67444725655621) * 100 = 88.39 %
```

### Setup 2

Reported fluxes:

```text
steam inlet      = 80.68999999999994 kg/s
steam outlet     = 81.38024350979913 kg/s
liquid inlet     = 116.9199999999997 kg/s
liquid steam out = 7.727826968502679 kg/s
```

Calculated rough carryover-based metrics:

```text
liquid carryover fraction = 7.727826968502679 / 116.9199999999997 = 0.06609 = 6.61 %
implied liquid-removal efficiency = (1 - 7.727826968502679 / 116.9199999999997) * 100 = 93.39 %
steam outlet dryness = 81.38024350979913 / (81.38024350979913 + 7.727826968502679) * 100 = 91.33 %
```

Comparative note:

- Setup 2 shows lower liquid carryover and higher implied separation performance than Setup 1 in this rough flux comparison.
- Because both rough runs appear non-converged and were performed under student-edition mesh limits, these values are suitable only as direction-of-change diagnostics, not final separator-performance claims.

## 14. Professional-License Baseline Flux Check

Date recorded: `2026-06-03`

Run context:

- `User-reported`: this setup was run with the professional license.
- `User-reported`: mesh scale was approximately `1.3M` nodes and `7.6M` cells.
- `User-reported`: flux report order was `liquid inlet`, `steam inlet`, `steam outlet`.

Reported phase fluxes:

| Phase report | Liquid inlet | Steam inlet | Steam outlet |
|---|---:|---:|---:|
| Liquid phase mass flow | `116.8522661860914 kg/s` | `-0 kg/s` | `0.03663388722044243 kg/s` |
| Steam phase mass flow | `-0 kg/s` | `81.63946888251938 kg/s` | `-86.29342139251109 kg/s` |

Calculated quick metrics if the steam-outlet liquid value is interpreted as liquid carryover magnitude:

```text
liquid carryover fraction = 0.03663388722044243 / 116.8522661860914
                          = 0.0003135 = 0.03135 %
implied liquid-removal efficiency = 99.96865 %
steam-outlet dryness = 86.29342139251109 / (86.29342139251109 + 0.03663388722044243)
                     = 99.95757 %
```

Scope assumption and balance caution:

- `User-specified`: for this project setup, the cut-off bottom without an active brine outlet or initialized water pool is acceptable and should not be treated as a blocking concern.
- `User-specified`: setup `07` should focus on steam-line liquid carryover and DPM droplet escape/separation, not on modelling the lower liquid pool or brine outlet drainage.
- `Inferred`: because the bottom liquid-handling region is intentionally out of scope, do not use this setup to claim full separator liquid inventory closure or brine-outlet performance.
- `Inferred`: using Fluent's usual sign convention, the reported steam phase has approximately `5.70 %` imbalance between steam inlet magnitude and steam-outlet magnitude before any phase-change or missing-surface interpretation is applied.
- `Inferred`: the liquid-phase balance across the reported surfaces is intentionally not the primary acceptance metric for this branch.

Evidence-use label:

- Use this as a professional-mesh baseline steam-carryover diagnostic.
- Report the efficiency narrowly as steam-outlet liquid-carryover removal for the scoped setup, not as full-vessel brine drainage or water-pool behavior.
- Residual/monitor stability and DPM escaped/trapped/incomplete counts are still needed before this becomes report-quality efficiency evidence.

Immediate baseline efficiency plan:

1. Save this phase-flux result as `E0-steam-carryover`.
2. Record residual/monitor stability for the professional setup `07` run.
3. On the same saved continuous field, run three quick DPM diameter cases: `5 um`, `10 um`, and `40-41 um`.
4. Record `escaped`, `trapped`, and `incomplete` particle counts for each DPM case before attempting any transient wall-film model.

## 15. DPM Settings Audit for Scoped Steam-Carryover Test

Date recorded: `2026-06-03`

Purpose:

- `User-specified`: current DPM objective is to estimate droplet carryover through the steam outlet for setup `07`.
- `User-specified`: droplets are assumed to be carried inside the steam flow, so injection from the steam inlet is intentional.
- `User-specified`: bottom liquid handling, brine drainage, and lower water-pool behaviour are out of scope for this branch.
- `Inferred`: the DPM setup should therefore be judged by steam-outlet `escape`, bottom `trap`, vessel-wall behaviour, incomplete tracks, and droplet-size sensitivity.

### 15.1 Boundary-Condition Audit

| Boundary / zone | Current DPM setting | Keep or change | Assessment |
|---|---|---|---|
| Separator vessel walls | `Reflect` | Keep for baseline | Conservative for steam carryover. A droplet that hits a wall is not automatically counted as separated; it can return to the flow and may still escape. This may underpredict collection compared with real wall drainage, but it avoids overstating efficiency without a wall-film model. |
| Bottom cut / bottom collection boundary | `Trap` | Keep | Acceptable for this scoped branch. Particles reaching the cut bottom are removed from the steam-carryover problem and counted as not escaping through the steam outlet. Do not interpret this as a real brine-outlet drainage model. |
| Steam outlet | `Escape` | Keep | Correct for carryover accounting. Any particle leaving through the steam outlet is treated as carried over. |

Report interpretation:

- `escaped` at steam outlet = droplet carryover.
- `trapped` at bottom = removed from the steam path for this scoped test.
- `reflected` wall interactions = still active particles; not separated unless they later trap at bottom or escape.
- If many particles bounce on walls then eventually escape, the reflected-wall baseline should be reported as a conservative carryover estimate.

### 15.2 Tracking-Control Audit

| DPM tracking setting | Current value | Keep or change | Assessment |
|---|---:|---|---|
| Particle treatment: unsteady particle tracking | `Off` | Keep off for baseline | Correct if the carrier flow field is the steady solved setup `07` field. |
| High-resolution tracking | `On` | Keep | Good for curved/swirl trajectories and near-wall paths. Higher cost is acceptable for the small three-diameter sweep. |
| Maximum number of steps | `50,000` | Accept for first run; increase if needed | Reasonable starting point. If `incomplete` tracks are more than a small fraction or affect efficiency, rerun with `100,000` steps. Purnanto-style DPM work treated incomplete tracks as a known risk, so do not hide this number. |
| Step length factor | `2` | Keep | Reasonable conservative tracking choice. Smaller values make trajectory integration finer but increase step count. Since this has already been reduced from `5` to `2`, keep it unless runtime becomes excessive without reducing incomplete tracks. |

What `unsteady particle tracking` means:

- With unsteady particle tracking `Off`, Fluent tracks particles through the current carrier-flow field as a steady/frozen field. This is the cheap post-processing mode and matches the intent of injecting droplets after the continuous solution is available.
- With unsteady particle tracking `On`, particle motion is advanced with physical time through a transient carrier-flow calculation. Use it when the gas/mixture field itself changes with time, when release timing matters, or when particles interact with a transient wall-film/VOF field.
- For setup `07`, unsteady particle tracking should stay `Off` unless the whole carrier-flow calculation is changed to transient.

### 15.3 Injection Audit

| Injection setting | Current value | Keep or change | Assessment |
|---|---|---|---|
| Injection surface | `steam inlet` | Keep | Consistent with the project assumption that mist droplets are carried with the steam phase, not injected from the liquid strip. |
| Injection type | `Surface` | Keep | Correct for releasing particles from an inlet face. |
| Particle type | `Inert particle` | Keep only as trajectory marker | Acceptable for an isothermal no-evaporation carryover check if the material properties are made water-like. Do not describe this as coal/solid carryover. |
| Diameter distribution | `Uniform` | Keep | Correct because each DPM run is a single diameter case. Change the diameter between tests: `5 um`, `10 um`, and `40-41 um`. |
| Material | `Anthracite` | Change if possible; otherwise keep with limitation note | Not appropriate for steam-water separator mist droplets. Anthracite is a solid-particle material and changes density/inertia. If Fluent does not offer a water-liquid DPM material in the current case, anthracite can be kept only as a temporary surrogate and the result must be labeled as material-limited. |
| Injection velocity | `27.118 m/s`, same as inlet | Keep | Good first assumption because droplets are carried with the steam inlet flow. Use the same direction convention as the steam velocity inlet. |
| Total flow rate | `1e-6 kg/s` | Keep | Good normalized reporting value for one-way DPM post-processing. Keep the same value for each diameter so escaped/trapped fractions remain comparable. |

How DPM total flow rate changes behaviour:

- In one-way DPM tracking with no continuous-phase source updates, injection mass flow does not change the particle trajectories. Diameter, density, injection velocity, drag/lift models, stochastic tracking, and the carrier-flow field control the paths.
- Injection mass flow does change the represented particle mass. It affects DPM mass-flow reports, escaped mass, trapped mass, and any mass-weighted efficiency calculation.
- If `Interaction with Continuous Phase` / `Update DPM Sources` is enabled, injection mass flow can feed momentum and mass source terms back into the continuous phase. Then the value can change the flow solution or convergence.
- For this baseline, keep DPM as one-way post-processing and set all three diameter runs to the same normalized flow rate. Then compare by escaped/trapped/incomplete fractions, not by arbitrary absolute DPM mass.

Recommended baseline injection values:

```text
Injection surface: steam inlet
Type: Surface
Particle type: inert trajectory marker
Diameter cases: 5e-6 m, 1e-5 m, 4.1e-5 m
Velocity magnitude: 27.118 m/s
Velocity direction: same as steam inlet normal/direction
Total flow rate: 1e-6 kg/s for each diameter case
Continuous-phase source update: Off
Material: water-liquid if available; otherwise anthracite with explicit limitation note
```

### 15.4 Physical-Model Audit

| Physical model setting | Current value | Keep or change | Assessment |
|---|---|---|---|
| Momentum exchange / drag law | `Spherical` | Keep | Correct first-pass drag law for small spherical droplets. |
| Particle rotation | `Off` | Keep | Correct baseline simplification for this scoped carryover test. |
| Rotational drag law | `Dennis et al.` inactive | Leave inactive | Only relevant if particle rotation is intentionally modelled. Not used in the current baseline. |
| Magnus lift law | `None` | Keep none | Correct for baseline. If particle rotation is off, Magnus lift should also remain off. |
| Stochastic tracking | `Off` | Keep for baseline | Correct for deterministic baseline. Use Discrete Random Walk later only as a sensitivity if fine-droplet dispersion needs to be tested. |
| Stochastic model | `Discrete Random Walk` | Sensitivity only | Useful if fine droplets are expected to disperse with turbulent eddies. Not the first report value unless repeated or sensitivity checked. |
| Random eddy lifetime | `Off / inactive` | Leave inactive | Not relevant for deterministic baseline because stochastic tracking is off. |
| Number of tries / iterations | `2` inactive | Increase only if stochastic sensitivity is re-enabled | `2` is too low for a robust stochastic conclusion. If DRW is turned back on, use more tries such as `5-10` for at least the `10 um` case and compare against deterministic tracking. |

Recommended baseline physical models:

```text
Drag law: Spherical
Particle rotation: Off
Magnus lift: None
Stochastic tracking: Off for baseline
Random eddy lifetime: Off/not applicable for baseline
Continuous-phase source coupling: Off
```

Recommended optional sensitivity:

```text
Run: DPM-STOCH-10um
Diameter: 10 um
Stochastic tracking: On
Model: Discrete Random Walk
Random eddy lifetime: On
Number of tries: 5-10
Compare against deterministic 10 um escaped/trapped/incomplete fractions.
```

### 15.5 Final Critical Recommendation

For the first report-ready DPM baseline, change the current setup as follows:

1. Keep the currently applied settings: `unsteady particle tracking Off`, high-resolution tracking `On`, max steps `50,000`, step factor `2`, flow rate `1e-6 kg/s`, particle rotation `Off`, and stochastic tracking `Off`.
2. Keep `unsteady particle tracking` off.
3. Keep high-resolution tracking on.
4. Keep `50,000` max steps for the first run, but increase to `100,000` if incomplete tracks are significant.
5. Keep step length factor `2` for the first run.
6. Keep wall `Reflect`, bottom `Trap`, and steam outlet `Escape`.
7. Keep total flow rate at the same normalized nonzero value for each diameter, `1e-6 kg/s`, with source coupling off.
8. Keep particle rotation off for the baseline.
9. Keep Magnus lift off.
10. Keep stochastic tracking off for the baseline; add it later as a sensitivity with more than `2` tries.
11. Treat `anthracite` as the only remaining weak point. If no liquid-water particle material is available, run with anthracite but label the result as a material-limited DPM surrogate.

Acceptance rule:

- The deterministic baseline is acceptable if `escaped`, `trapped`, and `incomplete` counts are stable and incomplete tracks are small.
- If deterministic and stochastic results differ strongly, report both and state that turbulent dispersion controls fine-droplet carryover.
- If a water-like particle material becomes available later, rerun at least the `10 um` case and compare against anthracite before using DPM as a stronger report claim.

## 16. First DPM Sweep Results

Date recorded: `2026-06-04`

Material update:

- `User-reported`: the DPM particle material for these updated runs was changed from anthracite-like density to a water-droplet surrogate with density `881.77 kg/m3`, matching the liquid-water density used elsewhere in setup `07`.
- `Inferred`: these updated results supersede the earlier anthracite-based DPM counts for the main interpretation of setup `07`.

Reported particle-fate counts:

| Diameter | Injected/tracked | Escaped | Trapped | Incomplete |
|---:|---:|---:|---:|---:|
| `5e-6 m` (`5 um`) | `200` | `74` | `63` | `63` |
| `1e-6 m` (`1 um`) | `200` | `23` | `64` | `113` |
| `1e-5 m` (`10 um`) | `200` | `14` | `53` | `133` |
| `4.1e-5 m` (`41 um`) | `200` | `0` | `72` | `128` |
| `1e-4 m` (`100 um`) | `200` | `0` | `86` | `114` |

Calculated interpretations using injected count as denominator:

| Diameter | Escape fraction | User-scoped efficiency `1 - escaped/injected` | Incomplete fraction |
|---:|---:|---:|---:|
| `5 um` | `37.0 %` | `63.0 %` | `31.5 %` |
| `1 um` | `11.5 %` | `88.5 %` | `56.5 %` |
| `10 um` | `7.0 %` | `93.0 %` | `66.5 %` |
| `41 um` | `0.0 %` | `100.0 %` | `64.0 %` |
| `100 um` | `0.0 %` | `100.0 %` | `57.0 %` |

Critical interpretation:

- `User-specified`: for setup `07`, treat `incomplete` particles as effectively trapped when they are interpreted as wall-stuck rather than escaped.
- `User-specified`: if `escaped = 0`, report that size case as `100 %` efficient at removing particles for this scoped DPM metric.
- `Inferred`: under that interpretation, the trend that larger droplets escape less is still physically plausible. In the updated water-density runs, the zero-escape cases are now `41 um` and `100 um`, while `10 um` drops to `93.0 %`.
- `Inferred`: the `1e-6 m` case is `1 um`, not `10 um`. Keep the result exactly as reported, but do not mix `1e-6 m` and `1e-5 m` when discussing the sweep.
- `Inferred`: the `4.1e-5 m` row was reported as `200, 72, 128`; this is interpreted here as `200 tracked`, `0 escaped`, `72 trapped`, `128 incomplete` because that is the only parse that closes the particle count.
- `Inferred`: because the incomplete fraction is still high, this interpretation should be described as a project assumption rather than a general Fluent best-practice rule.

Current decision for setup `07`:

1. Keep these five runs as the first DPM baseline evidence set.
2. Report the scoped DPM efficiency directly as `1 - escaped/injected`, with incomplete treated as trapped for this branch.
3. For the updated water-density runs, this gives `63.0 %` at `5 um`, `88.5 %` at `1 um`, `93.0 %` at `10 um`, and `100 %` at `41 um` and `100 um`.
4. Keep escaped/trapped/incomplete counts alongside the efficiency values so the assumption stays visible.
5. Optionally increase DPM maximum number of steps from `50,000` to `100,000` and rerun at least the `10 um` case first if you want to test whether the same `93.0 %` result survives with fewer incompletes.

### 16.1 `5 um` Sensitivity Checks: DRW and Rotation

Date recorded: `2026-06-04`

Reported particle-fate counts for `5e-6 m`:

| Case | Injected/tracked | Escaped | Trapped | Incomplete |
|---|---:|---:|---:|---:|
| Deterministic baseline | `1000` | `324` | `325` | `351` |
| Discrete Random Walk on, `200 x 5 = 1000` total tracks, eddy lifetime on | `1000` | `288` | `390` | `322` |
| Particle rotation on, `Dennis et al.` drag, `Oesterle-Bui-Dinh` Magnus lift | `1000` | `347` | `360` | `293` |

Scoped efficiencies using `1 - escaped/injected`:

| Case | Escape fraction | User-scoped efficiency | Incomplete fraction |
|---|---:|---:|---:|
| Deterministic baseline | `32.4 %` | `67.6 %` | `35.1 %` |
| DRW sensitivity | `28.8 %` | `71.2 %` | `32.2 %` |
| Rotation sensitivity | `34.7 %` | `65.3 %` | `29.3 %` |

Interpretation:

- `Inferred`: enabling Discrete Random Walk at `5 um` decreases escape by `3.6` percentage points relative to the deterministic baseline.
- `Inferred`: enabling particle rotation with the selected rotational drag and Magnus lift increases escape by `2.3` percentage points relative to the deterministic baseline.
- `Inferred`: both sensitivities preserve the same qualitative result: `5 um` droplets are not fully removed, and incomplete counts remain high.
- `Inferred`: neither sensitivity changes the branch-level conclusion enough to replace the simpler deterministic baseline as the primary report setting.
- `Inferred`: if a single `5 um` value must be quoted for this branch, the deterministic baseline remains the cleanest reference and the DRW/rotation cases should be described as sensitivity bounds.

# Setup 010V2d — Combined EWF-interaction post-simulation results

## 1. Setup link and evidence

- **Setup:** [010V2d — Combined EWF Interaction Confirmation](../../active/010V2d-ewf-combined-interaction.md); comparison scope: the accepted isolated [010V2a splash](../../active/010V2a-ewf-splash.md), [010V2b edge-separation](../../active/010V2b-ewf-edge-separation.md), and [010V2c stripping](../../active/010V2c-ewf-particle-stripping.md) branches.
- **Evidence class:** `partial diagnostic`. Analysis used the case/data already loaded in Fluent and did not load, solve, or intentionally change case physics. The live session did not expose case/data filenames, so checkpoint identity remains unrecoverable from the generated artifacts.
- **Session:** server ID `3`, Ansys Fluent `2024 R2`; captured 2026-07-22 UTC.
- **Raw evidence:** [EWF/DPM audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server3-20260722-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server3-20260722-snapshot/), [completed DPM sweep](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server3-20260722-dpm/), [carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2d-server3-20260722-flux-check.json), and [residual history](../../../PyAnsys/output/post_simulation_analysis/010V2d-server3-20260722-residual-check.json) ([plot](../../../PyAnsys/output/post_simulation_analysis/010V2d-server3-20260722-residual-check.png)).

## 2. Analysis applicability

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed, limiting | 520 points across seven residual curves; the selected-surface carrier balance does not close. |
| DPM fate analysis | completed | All six live `water-liquid-at-psep-*` injections completed the required transcript gates. |
| EWF audit / final-state snapshot | partial | `wall` is confirmed as the film wall; the 2024 R2 Settings API does not expose the top-level EWF branch. |
| EWF history / closure | deferred | Only a final loaded data state is available; there is no defined interval or integrated history. |
| Splash | active at wall / partially measured | `wall` has DPM wall splash enabled with four splashed particles; a splash event count is printed only for the 348.88 µm injection. |
| Edge separation | active at wall / partially measured | `wall` permits film-boundary separation; the 348.88 µm transcript prints a separation event count, but no represented separated mass. |
| Particle stripping | active(user-confirmation)     | The top-level EWF readback is unavailable and no `Film Stripped Mass` result is established. |

The audit also confirms global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`, matching the intended inherited controls. The model adapter cannot read `models.eulerian_wall_film`; this limitation is not evidence that any unavailable root-level mechanism is disabled.

## 3. Carrier-field and numerical state

The residual export spans iterations 4–1520. Its final scaled values are continuity `1.827e-3`, x/y/z velocity `3.197e-5` / `3.037e-5` / `3.533e-5`, k `4.295e-2`, epsilon `1.181e-1`, and phase-2 volume fraction `1.372e-3`. No acceptance threshold or monitor flatness criterion was supplied; these records do not establish convergence.

The phase-flux extractor identified `liquidinlet`, `steaminlet`, and `steamoutlet`; its phase mapping is phase-1 vapor and phase-2 liquid. It reports 111.074 kg/s liquid inlet and 80.690 kg/s vapor inlet, while the selected steam outlet carries 81.421242 kg/s vapor and 0 kg/s liquid. The resulting selected-surface imbalance is 110.342758 kg/s (57.54% of the 191.764 kg/s inlet total). This is a scope/closure limitation, not a full separator result; the apparent phase efficiency and steam-outlet dryness of 1.0 are not interpretable as separator performance.

## 4. DPM results

Every injection produced a `number tracked` line, a Mass Transfer Summary with parsed rows, a raw transcript, and a quiet completion interval of about 1 s. Flows below are terminal fate flows in kg/s. EWF event counters are separate interaction diagnostics and are not added again to mass closure.

| Diameter (µm) | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.038010 | 0.037930 | 0 | 8.759e-5 | 0 | not printed | not printed | -7.590e-6 |
| 28.14 | `water-liquid-at-psep-28um` | 0.156100 | 0.155800 | 1.438e-4 | 1.438e-4 | 0 | not printed | not printed | 1.240e-5 |
| 56.27 | `water-liquid-at-psep-56um` | 0.194100 | 0.181400 | 5.366e-4 | 2.683e-4 | 0.011890 | 133 | not printed | 5.100e-6 |
| 112.54 | `water-liquid-at-psep-112um` | 0.390100 | 0.275100 | 3.056e-3 | 0 | 0.112000 | 623 | not printed | -5.600e-5 |
| 168.81 | `water-liquid-at-psep-168um` | 0.390100 | 0.189700 | 4.495e-3 | 0 | 0.196000 | 1090 | not printed | -9.500e-5 |
| 348.88 | `water-liquid-at-psep-348um` | 4.693000 | 1.004000 | 8.838e-2 | 0 | 3.601000 | 1706 | 20 | -3.800e-4 |

Escaped particles terminate at `steamoutlet`; trapped particles terminate at `bottom`. The largest relative terminal-flow residual is 2.44e-4 (168.81 µm), consistent with printed report precision. The 348.88 µm transcript separately reports `separated = 120`; this is an event/parcel count, not represented mass, and is not a second terminal mass sink. It also reports 1706 EWF absorbed events but 1701 final absorbed particles, so both counters are retained rather than reconciled artificially.

## 5. EWF final-state results

Confirmed final-state film-wall scope: `wall`. These are single-checkpoint measurements, not time-integrated terms.

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum, `wall` | 3.2061953e-3 | dimensionless | final-state numerical diagnostic only |
| Film Mass | sum, `wall` | 5.66845e-2 | kg | current inventory |
| Film Thickness | facet maximum, `wall` | 1.2496226e-4 | m | local maximum |
| Film Thickness | area-weighted average, `wall` | 9.6016164e-7 | m | distributed-film measure |
| Film Outflow Mass | sum, `wall` | 0 | kg | Fluent final-state field; not a rate |
| Film Mass Flow Rate | selected boundaries / net | 0 | kg/s | `liquidinlet`, `steaminlet`, and `steamoutlet` all read -0.0 kg/s |
| Film velocity components | area-weighted, `wall` | x 5.11949e-2; y 6.41079e-4; z 1.4897525e-2 | m/s | direct component measurements |
| Film velocity magnitude | derived from measured components | 5.33223e-2 | m/s | not an independently extracted Fluent magnitude |
| Film DPM Mass Source | sum, `wall` | unavailable | kg/s | runner requested an unsupported alias; Fluent advertises `film-dpm-mass-src` |
| Film Stripped Mass | sum, `wall` | unavailable | kg | root-level stripping state and quantity were not established |
| Film Separated Mass | sum, `wall` | unavailable | kg | event count exists for one injection, but no film-mass quantity was extracted |

## 6. EWF history and bookkeeping

**Status: bookkeeping-only.** A single final data state cannot close the film balance. Missing terms are the initial inventory, time-integrated DPM-to-film source, film inflow/outflow, stripping/separation where active, and an explicit residual over a defined interval. Do not combine the 0.0566845 kg inventory directly with a kg/s boundary flux.

## 7. Interpretation, limitations, and next action

- **Measured:** a finite film inventory and low final film CFL are present on `wall`; all six DPM injections have completed fate records. DPM behavior shifts from steam-outlet escape at the fine end to final absorption at larger diameters. The largest class has direct splash and separation event evidence.
- **Derived:** terminal mass-flow rows close within printed precision. The component-derived area-weighted film speed is 0.0533223 m/s.
- **Unresolved:** carrier selected-surface closure, case/data filenames, represented splash/separation mass, `Film DPM Mass Source`, `Film Stripped Mass`, time-integrated EWF closure, and top-level EWF mechanism readback. None is treated as zero.

**Conclusion — needs follow-up.** Retain `010V2d` as an active diagnostic branch. Before a defined continuation interval, create EWF history files for inventory, DPM source, outflow, CFL, stripping, and separation; then repeat the snapshot with compatible Fluent field tokens and complete carrier outlet coverage. The current result does not support a separator-performance or fully reconciled combined-mechanism claim.

## 8. Results at 5,000 iterations

### 8.1 Evidence and applicability

- **Checkpoint:** the case/data already loaded on Fluent server ID `1`; Ansys Fluent `2024 R2`; captured 2026-07-23 UTC after the user-confirmed 5,000th iteration. The live session did not expose case/data filenames, so their identity remains unrecoverable from these artifacts.
- **Evidence class:** `partial diagnostic`. The analysis did not load a case/data pair, run iterations, or intentionally change physics. Snapshot mode reused only the namespaced `ewfdiag-*` report definitions.
- **Raw evidence:** [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260723-5000-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260723-5000-snapshot/), [completed six-injection DPM sweep](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260723-5000-dpm/), [carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2d-server1-20260723-5000-flux-check.json), and [residual history](../../../PyAnsys/output/post_simulation_analysis/010V2d-server1-20260723-5000-residual-check.json) ([plot](../../../PyAnsys/output/post_simulation_analysis/010V2d-server1-20260723-5000-residual-check.png)).

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed, limiting | Residual history reaches iteration 5000; selected-surface carrier balance remains open. |
| DPM fate analysis | completed | All six live `water-liquid-at-psep-*` injections passed the transcript completion gate; [per-injection raw summaries](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260723-5000-dpm/dpm_raw/) are retained. |
| EWF audit / final-state snapshot | partial | `wall` is confirmed as the film wall. The 2024 R2 Settings API again does not expose the top-level EWF branch. |
| EWF history / closure | deferred | Only a final loaded state was available; no defined interval or integrated histories exist. |
| Splash and separation | active at `wall` / measured | The wall readback has Stanton–Rutland splash and film-boundary separation enabled; DPM transcripts contain splash events for 112.54 µm and above, and separation events for 348.88 µm. |
| Particle stripping | partially measured | The 348.88 µm DPM transcript reports 11 stripped events. The unavailable top-level EWF readback prevents a root-level mechanism assertion or an extracted stripped mass. |

The audit also reads global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`. These match the intended inherited controls. The unavailable `models.eulerian_wall_film` Settings-API path is an adapter limitation, not evidence that EWF is disabled.

### 8.2 Carrier-field and numerical state at iteration 5,000

The residual history contains 1,000 retained points, ending at iteration 5000. Final scaled residuals are continuity `8.209e-3`, x/y/z velocity `1.123e-4` / `1.157e-4` / `1.275e-4`, k `1.133e-1`, epsilon `2.358e-1`, and phase-2 volume fraction `1.401e-3`. No acceptance threshold or monitor-flatness criterion was supplied; this evidence does **not** establish convergence.

The phase mapping remains the live-extractor fallback of phase-1 = vapor and phase-2 = liquid. The selected surfaces report 111.074 kg/s liquid inlet and 80.690 kg/s vapor inlet; `steamoutlet` carries 81.422408 kg/s vapor and 0 kg/s liquid. The selected-surface imbalance is 110.341592 kg/s (57.54% of the 191.764 kg/s inlet total). Therefore, the apparent steam-outlet dryness and phase efficiency of 1.0 remain scoped diagnostics, not separator-performance results.

### 8.3 DPM results at iteration 5,000

Each row has a complete `number tracked` line, mass-transfer section, parsed mass-transfer rows, a quiet interval of at least 1.0 s, and an individual raw transcript. Flows are terminal fate flows in kg/s. EWF event counters are separate interaction diagnostics and are not added a second time to terminal mass closure.

| Diameter (µm) | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Other events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.038010 | 0.037790 | 0 | 1.577e-4 | 7.007e-5 | 4 | not printed | — | -7.770e-6 |
| 28.14 | `water-liquid-at-psep-28um` | 0.156100 | 0.151800 | 7.191e-4 | 5.034e-4 | 3.020e-3 | 42 | not printed | — | 5.750e-5 |
| 56.27 | `water-liquid-at-psep-56um` | 0.194100 | 0.155400 | 1.789e-3 | 3.577e-4 | 3.649e-2 | 408 | not printed | — | 6.330e-5 |
| 112.54 | `water-liquid-at-psep-112um` | 0.395100 | 0.209300 | 9.529e-3 | 0 | 0.176300 | 1052 | 128 | — | -2.900e-5 |
| 168.81 | `water-liquid-at-psep-168um` | 0.395200 | 0.136900 | 1.205e-2 | 0 | 0.246300 | 1427 | 152 | — | -5.000e-5 |
| 348.88 | `water-liquid-at-psep-348um` | 4.781000 | 0.316600 | 0.154100 | 4.269e-11 | 4.310000 | 2194 | 256 | stripped 11; separated 179 | 3.000e-4 |

Escaped particles terminate at `steamoutlet`, and trapped particles at `bottom`. The largest relative closure residual is `3.68e-4` (28.14 µm), consistent with the printed mass-flow precision. The highest diameter class has 2,194 EWF absorbed events but 2,130 final absorbed particles; those different counters are retained separately. Its 256 splash, 11 stripping, and 179 separation events are not extra terminal mass sinks because their represented parcels can subsequently reach a final fate.

### 8.4 EWF final-state results at iteration 5,000

Confirmed final-state film-wall scope: `wall`. Values below are one-checkpoint measurements, not time-integrated terms.

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum, `wall` | 5.0655068e-3 | dimensionless | final-state numerical diagnostic only |
| Film Mass | sum, `wall` | 2.0221152e-1 | kg | current inventory |
| Film Thickness | facet maximum, `wall` | 4.5730619e-4 | m | local maximum |
| Film Thickness | area-weighted average, `wall` | 3.4252e-6 | m | distributed-film measure |
| Film Outflow Mass | sum, `wall` | 0 | kg | Fluent final-state field; not a rate |
| Film Mass Flow Rate | selected boundaries / net | 0 | kg/s | `liquidinlet`, `steaminlet`, and `steamoutlet` all read -0.0 kg/s |
| Film velocity components | area-weighted, `wall` | x 1.2242461e-1; y 1.2739215e-3; z 5.2224306e-2 | m/s | direct component measurements |
| Film velocity magnitude | derived from measured components | 1.3310442e-1 | m/s | not an independently extracted Fluent magnitude |
| Film DPM Mass Source | sum, `wall` | unavailable | kg/s | runner requested an unsupported alias; Fluent advertises `film-dpm-mass-src` |
| Film Stripped Mass | sum, `wall` | unavailable | kg | top-level mechanism readback and report extraction remain unavailable |
| Film Separated Mass | sum, `wall` | unavailable | kg | DPM event count exists, but no film-mass quantity was extracted |

### 8.5 EWF bookkeeping, interpretation, and limitation at iteration 5,000

**Status: bookkeeping-only.** The final data state cannot close the EWF balance. Missing terms are initial inventory, time-integrated DPM-to-film source, film inflow/outflow, stripping and separation where active, and an explicit residual over a defined interval. The 0.20221152 kg inventory must not be combined directly with the kg/s boundary flux.

- **Measured:** the 5,000-iteration state has a finite wall-film inventory, low final CFL, and complete DPM fate records for all six injections. DPM behavior remains increasingly absorption-dominated as diameter increases; splash begins to be printed at 112.54 µm, while the 348.88 µm class also has stripping and separation events.
- **Derived:** all six terminal fate-flow rows close within printed precision. The component-derived area-weighted film speed is 0.13310442 m/s.
- **Unresolved:** full carrier outlet coverage, case/data filenames, represented splash/separation/stripping mass, Film DPM Mass Source, time-integrated EWF closure, and root-level EWF mechanism readback. None is treated as zero.

**Conclusion — diagnostic only.** The additional iterations changed the final-state film inventory and DPM-fate distribution materially, but higher final residuals and the open selected-surface carrier balance prevent a convergence or separator-performance conclusion.

## 9. Results at 10,000 iterations

### 9.1 Evidence and applicability

- **Checkpoint:** the case/data already loaded on Fluent server ID `1`; Ansys Fluent `2024 R2`; captured 2026-07-24 UTC after the user-confirmed 10,000th iteration. The live session did not expose case/data filenames, so their identity remains unrecoverable from the generated artifacts.
- **Evidence class:** `partial diagnostic`. Analysis did not load a case/data pair, run iterations, or intentionally change physics. Snapshot mode reused only the namespaced `ewfdiag-*` report definitions.
- **Raw evidence:** [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260724-10000-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260724-10000-snapshot/), [completed six-injection DPM sweep](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260724-10000-dpm/), [carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2d-server1-20260724-10000-flux-check.json), and [residual history](../../../PyAnsys/output/post_simulation_analysis/010V2d-server1-20260724-10000-residual-check.json) ([plot](../../../PyAnsys/output/post_simulation_analysis/010V2d-server1-20260724-10000-residual-check.png)).

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed, limiting | The residual export covers iterations 5012–10000; the selected-surface carrier balance remains open. |
| DPM fate analysis | completed | All six live `water-liquid-at-psep-*` injections passed the transcript completion gate; [per-injection raw summaries](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-server1-20260724-10000-dpm/dpm_raw/) are retained. |
| EWF audit / final-state snapshot | partial | `wall` is confirmed as the film wall. The 2024 R2 Settings API still does not expose the top-level EWF branch. |
| EWF history / closure | deferred | Only a final loaded state was available; no defined interval or integrated histories exist. |
| Splash and separation | active at `wall` / measured | The wall readback has Stanton–Rutland splash and film-boundary separation enabled. DPM transcripts print splash from 56.27 µm upward and separation for 348.88 µm. |
| Particle stripping | partially measured | The 348.88 µm DPM transcript reports 1,722 stripped events. Root-level EWF readback and stripped mass extraction remain unavailable. |

The audit again reads global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`, matching the inherited controls. The unavailable `models.eulerian_wall_film` Settings-API path is an adapter limitation, not evidence that EWF is disabled.

### 9.2 Carrier-field and numerical state at iteration 10,000

The residual export has 1,000 retained points over iterations 5012–10000. Final scaled residuals are continuity `2.315e-2`, x/y/z velocity `1.761e-4` / `1.829e-4` / `1.976e-4`, k `8.363e-3`, epsilon `1.485e-2`, and phase-2 volume fraction `1.345e-3`. No acceptance threshold or monitor-flatness criterion was supplied; these records do **not** establish convergence.

The phase mapping remains the live-extractor fallback of phase-1 = vapor and phase-2 = liquid. The selected surfaces report 111.074 kg/s liquid inlet and 80.690 kg/s vapor inlet; `steamoutlet` carries 81.415962 kg/s vapor and effectively zero liquid. The selected-surface imbalance is 110.348038 kg/s (57.54% of the 191.764 kg/s inlet total). The apparent steam-outlet dryness and phase efficiency of 1.0 remain scoped diagnostics, not separator-performance results.

### 9.3 DPM results at iteration 10,000

Each row has a complete `number tracked` line, mass-transfer section, parsed mass-transfer rows, a quiet interval of about 1.0 s, and an individual raw transcript. Flows are terminal fate flows in kg/s. EWF event counters are separate interaction diagnostics and are not added a second time to terminal mass closure.

| Diameter (µm) | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Other events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.038010 | 0.037450 | 0 | 1.577e-4 | 4.029e-4 | 23 | not printed | — | -6.000e-7 |
| 28.14 | `water-liquid-at-psep-28um` | 0.156100 | 0.107200 | 3.596e-4 | 1.438e-4 | 4.840e-2 | 673 | not printed | — | -3.400e-6 |
| 56.27 | `water-liquid-at-psep-56um` | 0.194300 | 6.921e-2 | 1.520e-3 | 8.943e-5 | 0.123500 | 1385 | 12 | — | -1.943e-5 |
| 112.54 | `water-liquid-at-psep-112um` | 0.395400 | 8.507e-2 | 1.061e-2 | 0 | 0.299700 | 1891 | 244 | — | 2.000e-5 |
| 168.81 | `water-liquid-at-psep-168um` | 0.416200 | 5.691e-2 | 9.708e-3 | 0 | 0.349500 | 2896 | 976 | — | 8.200e-5 |
| 348.88 | `water-liquid-at-psep-348um` | 6.095000 | 0.188100 | 0.101300 | 7.278e-4 | 5.805000 | 6676 | 3724 | stripped 1722; separated 228 | -1.278e-4 |

Escaped particles terminate at `steamoutlet`, and trapped particles at `bottom`. The largest relative closure residual is `1.97e-4` (168.81 µm), within the printed mass-flow precision. The 348.88 µm transcript has 6,676 EWF absorbed events but 5,745 final absorbed particles; these are distinct counters and are retained separately. Its splash, stripping, and separation counts are not extra terminal mass sinks because generated parcels can subsequently reach a final fate.

### 9.4 EWF final-state results at iteration 10,000

Confirmed final-state film-wall scope: `wall`. Values below are one-checkpoint measurements, not time-integrated terms.

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum, `wall` | 3.0344429 | dimensionless | elevated final-state numerical diagnostic; not a closure result |
| Film Mass | sum, `wall` | 2.8838471e-1 | kg | current inventory |
| Film Thickness | facet maximum, `wall` | 6.1392697e-4 | m | local maximum |
| Film Thickness | area-weighted average, `wall` | 4.8848615e-6 | m | distributed-film measure |
| Film Outflow Mass | sum, `wall` | 0 | kg | Fluent final-state field; not a rate |
| Film Mass Flow Rate | selected boundaries / net | 0 | kg/s | `liquidinlet`, `steaminlet`, and `steamoutlet` all read -0.0 kg/s |
| Film velocity components | area-weighted, `wall` | x 6.148724e-2; y -3.4803981e-3; z 1.7276889e-1 | m/s | direct component measurements |
| Film velocity magnitude | derived from measured components | 1.8341724e-1 | m/s | not an independently extracted Fluent magnitude |
| Film DPM Mass Source | sum, `wall` | unavailable | kg/s | runner requested an unsupported alias; Fluent advertises `film-dpm-mass-src` |
| Film Stripped Mass | sum, `wall` | unavailable | kg | top-level mechanism readback and report extraction remain unavailable |
| Film Separated Mass | sum, `wall` | unavailable | kg | DPM event count exists, but no film-mass quantity was extracted |

### 9.5 EWF bookkeeping, interpretation, and limitation at iteration 10,000

**Status: bookkeeping-only.** The final data state cannot close the EWF balance. Missing terms are initial inventory, time-integrated DPM-to-film source, film inflow/outflow, stripping and separation where active, and an explicit residual over a defined interval. The 0.28838471 kg inventory must not be combined directly with the kg/s boundary flux.

- **Measured:** the wall-film inventory, thickness, and component-derived speed are larger than at 5,000 iterations. DPM final absorption has increased and steam-outlet escape decreased across every reported size class. The 348.88 µm class has markedly more splash and stripping events.
- **Derived:** all six terminal fate-flow rows close within printed precision. The component-derived area-weighted film speed is 0.18341724 m/s.
- **Unresolved:** full carrier outlet coverage, case/data filenames, represented splash/separation/stripping mass, Film DPM Mass Source, time-integrated EWF closure, and root-level EWF mechanism readback. None is treated as zero.

**Conclusion — diagnostic only.** The final-state inventory continues to grow, while the maximum film CFL is now above 1 and the selected-surface carrier balance remains open. Do not use this checkpoint to claim convergence, EWF mass closure, or separator performance.

## 10. Comparison: previous checkpoint vs. 5,000 vs. 10,000 iterations

The initial record above is the 2026-07-22 server-3 checkpoint whose residual export ended at iteration 1520. The latter two checkpoints were captured from server 1. This is a same-setup diagnostic comparison, but it is not a formal controlled convergence study: the live sessions expose no case/data filenames, DPM track summaries are recomputed at each checkpoint, and final-state-only EWF values do not supply a time-integrated balance.

| Carrier / numerical indicator | Previous (through 1520) | At 5000 | At 10000 | 5000 → 10000 |
|---|---:|---:|---:|---:|
| Continuity residual | 1.827e-3 | 8.209e-3 | 2.315e-2 | +182% |
| x / y / z velocity residual | 3.197e-5 / 3.037e-5 / 3.533e-5 | 1.123e-4 / 1.157e-4 / 1.275e-4 | 1.761e-4 / 1.829e-4 / 1.976e-4 | +56.8% / +58.1% / +55.0% |
| k / epsilon residual | 4.295e-2 / 1.181e-1 | 1.133e-1 / 2.358e-1 | 8.363e-3 / 1.485e-2 | -92.6% / -93.7% |
| phase-2 volume-fraction residual | 1.372e-3 | 1.401e-3 | 1.345e-3 | -4.0% |
| steam-outlet vapor flow | 81.421242 kg/s | 81.422408 kg/s | 81.415962 kg/s | -0.006446 kg/s |
| selected-surface imbalance | 110.342758 kg/s | 110.341592 kg/s | 110.348038 kg/s | +0.006446 kg/s; still 57.54% of inlet |

Selected-surface fluxes remain effectively unchanged at the printed scale, while continuity and all velocity residuals increased further between 5,000 and 10,000 iterations. k and epsilon decreased during that same interval. Without a supplied residual acceptance criterion or a demonstrated flatness window, this mixed behavior does not establish numerical convergence.

| EWF final-state quantity on `wall` | Previous | At 5000 | At 10000 | 5000 → 10000 |
|---|---:|---:|---:|---:|
| Maximum film CFL | 3.2061953e-3 | 5.0655068e-3 | 3.0344429 | about 599× higher |
| Film inventory | 5.66845e-2 kg | 2.0221152e-1 kg | 2.8838471e-1 kg | +42.6% |
| Maximum film thickness | 1.2496226e-4 m | 4.5730619e-4 m | 6.1392697e-4 m | +34.2% |
| Area-weighted thickness | 9.6016164e-7 m | 3.4252e-6 m | 4.8848615e-6 m | +42.6% |
| Derived area-weighted film speed | 5.33223e-2 m/s | 1.3310442e-1 m/s | 1.8341724e-1 m/s | +37.8% |
| Boundary-film-flow net | 0 kg/s | 0 kg/s | 0 kg/s | unchanged at printed precision |

The film inventory and thickness continue to grow at 10,000 iterations. Unlike the preceding checkpoints, the maximum Film CFL is now 3.03, so it should be examined before treating the later film state as numerically reliable. All three snapshots remain final-state observations only; none establishes accumulation rate or closure.

| Diameter (µm) | Final absorbed: previous → 5000 → 10000 (kg/s) | Escaped: previous → 5000 → 10000 (kg/s) | Interaction-event change at 10000 | Comparison note |
|---:|---:|---:|---|---|
| 5.63 | 0 → 7.007e-5 → 4.029e-4 | 0.037930 → 0.037790 → 0.037450 | absorbed 4 → 23 | Fine class remains escape-dominated. |
| 28.14 | 0 → 3.020e-3 → 4.840e-2 | 0.155800 → 0.151800 → 0.107200 | absorbed 42 → 673 | Absorption becomes material at 10,000 iterations. |
| 56.27 | 1.189e-2 → 3.649e-2 → 0.123500 | 0.181400 → 0.155400 → 6.921e-2 | absorbed 408 → 1385; splash 12 | Strong shift from escape to absorption. |
| 112.54 | 0.112000 → 0.176300 → 0.299700 | 0.275100 → 0.209300 → 8.507e-2 | absorbed 1052 → 1891; splash 128 → 244 | Greater final absorption, lower escape. |
| 168.81 | 0.196000 → 0.246300 → 0.349500 | 0.189700 → 0.136900 → 5.691e-2 | absorbed 1427 → 2896; splash 152 → 976 | Greater final absorption, sharply lower escape. |
| 348.88 | 3.601000 → 4.310000 → 5.805000 | 1.004000 → 0.316600 → 0.188100 | absorbed 1706 → 6676; splash 256 → 3724; stripping 11 → 1722; separation 179 → 228 | Coarsest class is increasingly absorption-dominated; secondary-interaction activity rises strongly. |

**Comparison interpretation:** from 5,000 to 10,000 iterations, every tracked diameter class has greater final absorption and lower steam-outlet escape. The most pronounced changes occur in the 28.14–348.88 µm classes. Event counts are interaction diagnostics, not additional mass sinks, and changed summary net flows or track counts must not be interpreted as a physical source without a controlled re-run and history-based mass balance. The elevated 10,000-iteration Film CFL and unresolved carrier/EWF closures remain the limiting evidence gaps.

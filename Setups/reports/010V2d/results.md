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


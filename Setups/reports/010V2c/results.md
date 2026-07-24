# Setup 010V2c — EWF particle-stripping sensitivity: post-simulation results

## 1. Setup link and evidence

- **Setup:** [010V2c EWF particle-stripping sensitivity](../../active/010V2c-ewf-particle-stripping.md); parent comparison scope: [010V2 clean deposition control](../../active/010V2-ewf-deposition-film-inventory.md).
- **Evidence class:** `partial diagnostic`. The supplied, already-loaded server-4 session was analysed without loading, solving, or changing physics. The live client did not expose case/data filenames, so the checkpoint identity is not independently recoverable from these artifacts.
- **Session:** server ID `4`, Ansys Fluent `2025 R2`; captured 2026-07-22 UTC.
- **Raw evidence:** [audit bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server4-20260722-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server4-20260722-snapshot/), [DPM sweep bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server4-20260722-dpm/), [carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2c-server4-20260722-flux-check.json), and [residual history](../../../PyAnsys/output/post_simulation_analysis/010V2c-server4-20260722-residual-check.json) ([plot](../../../PyAnsys/output/post_simulation_analysis/010V2c-server4-20260722-residual-check.png)).

## 2. Analysis applicability

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and flux checks | completed, limiting | 946 points across seven residual curves; selected-surface phase balance does not close. |
| DPM fate analysis | completed | All six live `water-liquid-at-psep-*` injections completed their transcript gates. |
| EWF audit / final-state snapshot | partial | `wall` is confirmed as the film wall; the 2025 R2 adapter cannot read the top-level EWF model branch. |
| EWF history / closure | deferred | Only one final data-state snapshot is available; no defined interval or time-integrated terms. |
| Splash | not available | No splash counter was printed by the DPM summaries; do not convert this to zero. |
| Particle stripping | not available | The top-level stripping readback and `Film Stripped Mass` were unavailable through the 2025 R2 adapter, so activity and magnitude cannot be established from this pass. |
| Edge separation | not available | Same top-level EWF adapter limitation; no separated-mass result is claimed. |

Live readback independently confirms `wall` as an Eulerian-film wall, `bottom` as a non-film trapped wall, global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`. These match the intended `010V2`-family controls. The audit also found six active DPM injections, all using `water-liquid-at-psep-dpm` on `steaminlet`.

## 3. Carrier-field and numerical state

The final residual record spans iterations 2–1446. Its last scaled values are continuity `2.029e-3`, x/y/z velocity `3.318e-5` / `3.344e-5` / `4.085e-5`, k `1.322e-1`, epsilon `1.962e-1`, and phase-2 volume fraction `1.424e-3`. No convergence criterion or monitor acceptance gate was supplied, so this record alone does not establish convergence.

The phase-flux extractor identified `liquidinlet`, `steaminlet`, and `steamoutlet`; it used the adapter fallback `phase-1=vapor`, `phase-2=liquid`. It reported 111.074 kg/s liquid inlet and 80.690 kg/s vapor inlet, while the selected steam outlet carried 81.420 kg/s vapor and 0 kg/s liquid. The selected-surface imbalance is 110.344 kg/s (57.54% of the 191.764 kg/s inlet total). This is a scope/closure failure, not a full-separator efficiency result; the reported apparent phase efficiency/dryness of 1.0 is therefore not interpretable.

## 4. DPM results

All rows completed the required `number tracked`, Mass Transfer Summary, parsed mass row, and 1 s quiet-transcript gate. Mass-flow values below are terminal fate flows in kg/s; parenthetical values are parcel counts. The output did not print splash events, so they remain unavailable rather than zero.

| Diameter (µm) | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.038010 | 0.038000 (2169) | 0 (0) | 1.752e-5 (1) | 0 (0) | not printed | not reported | -7.520e-6 |
| 28.14 | `water-liquid-at-psep-28um` | 0.156100 | 0.155800 (2166) | 1.438e-4 (2) | 7.191e-5 (1) | 7.191e-5 (1) | 1 | not reported | 1.238e-5 |
| 56.27 | `water-liquid-at-psep-56um` | 0.194100 | 0.183900 (2056) | 3.577e-4 (4) | 1.789e-4 (2) | 9.659e-3 (108) | 108 | not reported | 4.400e-6 |
| 112.54 | `water-liquid-at-psep-112um` | 0.390100 | 0.276900 (1540) | 1.618e-3 (9) | 0 (0) | 0.111600 (621) | 621 | not reported | -1.800e-5 |
| 168.81 | `water-liquid-at-psep-168um` | 0.390100 | 0.190200 (1058) | 4.674e-3 (26) | 0 (0) | 0.195200 (1086) | 1086 | not reported | 2.600e-5 |
| 348.88 | `water-liquid-at-psep-348um` | 4.678000 | 1.022000 (474) | 8.838e-2 (41) | 0 (0) | 3.567000 (1655) | 1655 | not reported | 6.200e-4 |

All escaped particles exited through `steamoutlet`; trapped particles were on `bottom`. The largest relative closure residual is `1.33e-4` (348.88 µm), consistent with the printed summary precision. No splash term is added to closure because none was reported, and such a counter would be an event diagnostic rather than a second terminal mass sink.

## 5. EWF final-state results

Confirmed film-wall scope: `wall`. These are final-state measurements only, not time-integrated quantities.

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum, `wall` | 2.8549e-3 | dimensionless | final-state numerical diagnostic only |
| Film Mass | sum, `wall` | 5.44018e-2 | kg | current inventory |
| Film Thickness | facet maximum, `wall` | 1.21115e-4 | m | local maximum |
| Film Thickness | area-weighted average, `wall` | 9.21495e-7 | m | distributed-film measure |
| Film Outflow Mass | sum, `wall` | 2.47576e-8 | kg | Fluent final-state field; not a rate |
| Film Mass Flow Rate | `steamoutlet` | -2.21816e-6 | kg/s | preserve Fluent sign; other requested boundaries were -0.0 kg/s |
| Film velocity components | area-weighted, `wall` | x 4.95878e-2; y 6.42438e-4; z 1.43558e-2 | m/s | direct component measurements |
| Film velocity magnitude | derived from the measured components | 5.16280e-2 | m/s | not the unavailable Fluent magnitude report |
| Film DPM Mass Source | sum, `wall` | unavailable | kg/s | 2025 R2 token mismatch (`film-dpm-mass-src` is the live allowed token) |
| Film Stripped Mass | sum, `wall` | unavailable | kg | stripping activity could not be read back; no zero claim |
| Film Separated Mass | sum, `wall` | unavailable | kg | edge-separation activity could not be read back; no zero claim |

## 6. EWF history and bookkeeping

**Status: bookkeeping-only.** A single loaded data state cannot close the EWF balance. Missing terms are initial inventory, time-integrated DPM-to-film source, time-integrated film inflow/outflow, time-integrated stripped/separated mass when active, and an explicit residual over a defined interval. Do not combine the 0.05440 kg inventory directly with the instantaneous -2.218e-6 kg/s outlet flux.

## 7. Interpretation, limitations, and next action

- **Measured:** particle fate shifts strongly from steam-outlet escape at 5.63 µm toward EWF absorption at larger diameters: 1655 of 2170 tracked 348.88 µm parcels were absorbed. The film exists on `wall` with low final film CFL and finite final inventory.
- **Derived:** the DPM terminal mass rows close within the printed precision. The component-derived area-weighted film-speed magnitude is 0.05163 m/s.
- **Unresolved:** this pass cannot demonstrate particle stripping, quantify stripped mass, or close an EWF mass balance. The carrier selected-surface flux imbalance also prevents any separator-performance conclusion.

**Next action:** repair the Fluent-2025-R2 diagnostic token mappings (`film-dpm-mass-src` and `film-velocity-mag`) and add an explicit stripping readback/report; create history files before a defined continuation interval, then repeat the snapshot with complete carrier outlet coverage.

## 8. 5,000-iteration follow-up — server-2 comparison

### Evidence and applicability

- **Checkpoint scope:** the already-loaded server-2 case/data state, reported by the operator as `5000` iterations. The diagnostic client could not expose the case/data filenames, so this iteration label is user-supplied rather than independently read from Fluent.
- **Session:** server ID `2`, Ansys Fluent `2025 R2`; captured 2026-07-23 NZST (artifact timestamp 2026-07-22 UTC). No case/data were loaded, no iterations were run, and no physics settings were changed.
- **Raw evidence:** [audit bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server2-20260723-5000it-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server2-20260723-5000it-snapshot/), and [complete DPM sweep](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server2-20260723-5000it-dpm/), including [per-injection transcripts](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server2-20260723-5000it-dpm/dpm_raw/) and [DPM closure summary](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2c-server2-20260723-5000it-dpm/dpm_injection_summary.csv).

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | incomplete | The read-only carrier client returned before writing its expected residual/flux bundle. It was watched for more than 320 s; no numerical carrier result is inferred. |
| DPM fate analysis | completed | All six live injections passed `number tracked`, Mass Transfer Summary, parsed-mass-row, and 1 s quiet-transcript gates. |
| EWF audit / final-state snapshot | completed with adapter limitation | `wall` is the confirmed sole film wall; `bottom` is non-film/trapping. The Fluent 2025 R2 top-level EWF branch remains unavailable to this adapter. |
| EWF history / closure | deferred | One final state only; no defined interval or integrated source/outflow terms. |
| Splash | not available | No splash counter was printed. This is not a zero result. |
| Particle stripping | not available | The snapshot labels `Film Stripped Mass` as an inactive mechanism because the top-level EWF readback is unavailable. This is not independent proof that stripping is off, nor a stripped-mass measurement. |
| Edge separation | not available | Same top-level EWF adapter limitation; no separated-mass result is claimed. |

The live audit reconfirms `wall` as the EWF wall, `bottom` as a non-film trapped wall, global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`. Six active `water-liquid-at-psep-*` injections use `water-liquid-at-psep-dpm` from `steaminlet`.

### DPM results at 5,000 iterations

All flows are kg/s. `Absorbed` is the final fate mass; the EWF absorbed count is a separate event/parcel diagnostic. Splash is deliberately not added as a terminal sink.

| Diameter (µm) | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.038010 | 0.037930 (2165) | 0 (0) | 7.007e-5 (4) | 1.752e-5 (1) | 1 | -7.590e-6 |
| 28.14 | `water-liquid-at-psep-28um` | 0.156100 | 0.154700 (2151) | 2.157e-4 (3) | 1.438e-4 (2) | 1.007e-3 (14) | 14 | 3.350e-5 |
| 56.27 | `water-liquid-at-psep-56um` | 0.194100 | 0.167000 (1867) | 1.610e-3 (18) | 0 (0) | 2.549e-2 (285) | 285 | 0 |
| 112.54 | `water-liquid-at-psep-112um` | 0.390100 | 0.242500 (1349) | 7.371e-3 (41) | 0 (0) | 0.140200 (780) | 780 | 2.900e-5 |
| 168.81 | `water-liquid-at-psep-168um` | 0.390100 | 0.174400 (970) | 1.187e-2 (66) | 0 (0) | 0.203900 (1134) | 1134 | -7.000e-5 |
| 348.88 | `water-liquid-at-psep-348um` | 4.774000 | 0.357400 (146) | 0.181100 (84) | 0 (0) | 4.236000 (1965) | 1965 | -5.000e-4 |

All escaped parcels exit through `steamoutlet`; all trapped parcels are on `bottom`. The largest relative mass-flow closure residual is `2.15e-4` (28.14 µm), consistent with the printed-summary precision.

Compared with the earlier 1,446-iteration, server-4 checkpoint, final absorbed parcel counts increased from `0 -> 1`, `1 -> 14`, `108 -> 285`, `621 -> 780`, `1086 -> 1134`, and `1655 -> 1965` for the ascending 5.63–348.88 µm bins. The 348.88 µm steam-outlet escape count fell from `474` to `146`. This is a comparison of independently tracked checkpoint states, not proof that the change was caused by particle stripping.

### EWF final-state comparison

Confirmed film-wall scope is `wall`. Values are final-state fields; inventory values in kg and fluxes in kg/s must not be combined as a closure.

| Quantity | Earlier 1,446-iteration checkpoint | 5,000-iteration checkpoint | Change / limit |
|---|---:|---:|---|
| Maximum film Courant number | 2.85490e-3 | 4.92992e-3 | +72.7%; still a final-state numerical indicator only |
| Film mass / inventory (kg) | 5.44018e-2 | 0.20107457 | +269.6% |
| Maximum film thickness (m) | 1.21115e-4 | 4.09844e-4 | +238.4% |
| Area-weighted film thickness (m) | 9.21495e-7 | 3.40594e-6 | +269.6% |
| Film outflow mass field (kg) | 2.47576e-8 | 1.20434e-7 | +386.5%; field is not a rate |
| `steamoutlet` film mass flow (kg/s) | -2.21816e-6 | -1.78286e-6 | outlet-magnitude decreased 19.6%; Fluent sign preserved |
| Component-derived area-weighted film speed (m/s) | 5.16280e-2 | 0.134012 | +159.6%; derived from x/y/z components |
| Film DPM Mass Source | unavailable | unavailable | 2025 R2 token mismatch: live token is `film-dpm-mass-src` |
| Film Stripped Mass | unavailable | unavailable | no validated stripping readback or quantity |
| Film Separated Mass | unavailable | unavailable | no validated edge-separation readback or quantity |

At 5,000 iterations, the area-weighted component measurements are x `0.12186478`, y `0.00205104`, and z `0.05571432` m/s. The snapshot reports a film outflow mass-flow rate of `-1.7828591e-6 kg/s` at `steamoutlet` and `-0.0 kg/s` at both inlet boundaries.

### Interpretation and next action

- **Measured:** compared with the earlier checkpoint, the film inventory and thickness are markedly larger and the DPM sweep reports more EWF-absorbed parcels in every bin, especially 56.27–348.88 µm. The final film CFL remains low in absolute terms (`4.93e-3`).
- **Derived:** the DPM terminal mass rows close within printed precision; the component-derived film speed increased by about 160%. These results show a changed deposition/film state between checkpoints.
- **Unresolved:** no result proves particle stripping was active or measures stripped mass; no EWF history closes the film balance; and residual/phase-flux carrier evidence was not captured at 5,000 iterations because the extractor did not produce an artifact bundle.

**Next action:** first repair the 2025 R2 field-token/readback adapter for `film-dpm-mass-src`, `film-velocity-mag`, and the explicit stripping state/`Film Stripped Mass`; create EWF histories before any further continuation so the next comparison can separate inventory growth, DPM-to-film source, drainage, and stripping over a defined interval.

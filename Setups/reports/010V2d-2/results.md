# Diagnostic Results Report — Setup 010V2d-2

## Setup link and run identity

- Setup definition: [010V2d-2 — Combined EWF with Global DPM Interaction](../../active/010V2d-2-ewf-combined-global-dpm.md)
- Parent setup: [010V2d — Combined EWF Interaction Confirmation](../../active/010V2d-ewf-combined-interaction.md)
- Fluent server and version: server `1`, `Ansys Fluent 2024 R2`
- Analysis date: `2026-07-22`
- Case/data state: analysis used the already-loaded Fluent session. The read-only runners did not expose case/data filenames.
- Evidence class: partial diagnostic. This report does not change the setup lifecycle or satisfy the branch acceptance gate.

## 1. Analysis applicability and live readback

| Analysis | Status | Evidence and limit |
|---|---|---|
| Carrier flux and residual history | completed | Phase-specific fluxes and seven residual curves were exported. |
| DPM Particle Tracks Summary | completed | All six live injections passed the tracked-count, mass-transfer, quiet-transcript, and raw-artifact gates. |
| EWF audit | completed with adapter limitation | `wall` is the confirmed film wall, but the EWF Settings API root is unavailable. |
| EWF final-state snapshot | partial | Several film quantities were captured; DPM mass-source and velocity-magnitude fields failed. |
| EWF history/closure | deferred | Only a final checkpoint was available; no interval histories were created before the run. |

The wall-level readback confirms `wall` as the only EWF film wall. It uses the `stanton-rutland` impingement model and has a configured splashed-particle count of `4`. Global DPM interaction is enabled, with source updates every iteration and interval `1`, matching the intended controlled change for this branch.

The audit could not access `models.eulerian_wall_film` through the Fluent 2024 R2 Settings API adapter. Therefore its root-level EWF mechanism flags, including stripping and edge-separation status, are recorded as unavailable rather than interpreted as off. The final snapshot created or reused only namespaced `ewfdiag-*` report definitions; it did not alter case physics or iterations.

## 2. Carrier-field and numerical state

| Quantity | Value |
|---|---:|
| Liquid inlet flow | `111.074 kg/s` |
| Vapor inlet flow | `80.690 kg/s` |
| Steam-outlet liquid flow | `0 kg/s` |
| Steam-outlet vapor flow | `81.419309 kg/s` |
| Derived phase efficiency | `1.000` |
| Steam-outlet dryness | `1.000` |
| Derived carrier mass imbalance | `110.344691 kg/s` (`57.54%`); informational only under the simplified Purnanto scope |

The mixture mass-flow report was unavailable, so the imbalance is derived from phase-specific fluxes and is only a scoped conservation diagnostic. It is too large to support a carrier-balance, separator-performance, or global-DPM-source claim.

The residual monitor export contains seven curves and `568` points over monitor iterations `8`–`2068`. Final residuals are continuity `2.875e-3`, x/y/z velocity `5.212e-5` / `5.161e-5` / `6.481e-5`, liquid-volume-fraction `1.284e-3`, `k` `2.057e-1`, and epsilon `3.845e-1`. Velocity residuals are low, but continuity, `k`, and epsilon do not establish a converged or physically validated solution.

## 3. DPM Particle Tracks Summary

All six live injections completed in ascending diameter order. Every per-injection transcript includes a tracked-count line, a Mass Transfer Summary with terminal rows, and a quiet completion interval. `Escaped` particles terminate at `steamoutlet`; `Trapped` particles terminate at `bottom` when present. EWF absorbed and splashed counters are separate interaction diagnostics, not additional terminal sinks.

| Diameter (µm) | Injection | Net flow (kg/s) | Escaped | Trapped | Incomplete | Final absorbed fate | EWF absorbed events | Splash events | Closure residual (kg/s) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `5.63` | `water-liquid-at-psep-5um` | `0.03801` | 2157 | 0 | 11 | 2 | 2 | not printed | `-7.74e-6` |
| `28.14` | `water-liquid-at-psep-28um` | `0.1561` | 2161 | 3 | 0 | 6 | 6 | not printed | `5.28e-5` |
| `56.27` | `water-liquid-at-psep-56um` | `0.1941` | 1944 | 6 | 1 | 219 | 219 | not printed | `-1.603e-5` |
| `112.54` | `water-liquid-at-psep-112um` | `0.3901` | 1389 | 17 | 0 | 764 | 764 | not printed | `-5.60e-5` |
| `168.81` | `water-liquid-at-psep-168um` | `0.3909` | 906 | 34 | 0 | 1258 | 1265 | 28 | `-1.30e-5` |
| `348.88` | `water-liquid-at-psep-348um` | `4.713` | 590 | 68 | 5 | 1746 | 1757 | 44 | `-1.35e-4` |

The largest relative terminal-flow closure residual is `3.38e-4` for the `28.14 µm` injection, consistent with the printed-report precision. For `168.81` and `348.88 µm`, the EWF absorbed-event counter exceeds the final absorbed-fate count by `7` and `11`, respectively; both values are preserved as Fluent reported them. A splash field not printed by Fluent is not interpreted as a physical zero.

This completed fate analysis supersedes the earlier incomplete Particle Tracks artifact. Direct DPM-to-carrier mass and momentum source totals remain unavailable from the completed diagnostics.

## 4. EWF final-state snapshot

The final-state snapshot is scoped to `wall`. The diagnostic CSV left unit cells blank; the units below are the requested Fluent report dimensions and should not be treated as a separate unit readback.

| Quantity | Value | Requested dimension | Interpretation limit |
|---|---:|---|---|
| Maximum Film Courant Number | `0.003872775` | dimensionless | final-state numerical diagnostic only |
| Film Mass | `0.0799062` | kg | current film inventory, not an integrated balance |
| Maximum Film Thickness | `1.7669208e-4` | m | local maximum |
| Area-weighted Film Thickness | `1.353507e-6` | m | distributed average |
| Film Outflow Mass | `0` | kg | final reported cumulative/snapshot quantity only |
| Area-weighted Film x velocity | `0.065356183` | m/s | component value only |
| Area-weighted Film y velocity | `4.3707143e-4` | m/s | component value only |
| Area-weighted Film z velocity | `0.020206066` | m/s | component value only |

The mixture film-mass-flow query returned `0 kg/s` on `liquidinlet`, `steaminlet`, and `steamoutlet` (net `0 kg/s`). This is a final-state flux readback, not evidence that no film transport occurred earlier in the run.

The snapshot failed to extract `Film DPM Mass Source`, area-weighted film-velocity magnitude, and maximum film-velocity magnitude because the runner requested aliases that this Fluent session rejects. The report did capture the three velocity components above, so film velocity is only partially missing. Stripped and separated film-mass results were not captured: the adapter could not establish the corresponding root-level mechanism states, and no missing value is treated as zero.

## 5. Interpretation and acceptance gate

**Measured:** a finite film inventory and thickness on `wall`, bounded final Film CFL, zero final reported film mass flow at the selected boundaries, carrier fluxes, residual history, six DPM injection identities, and global DPM interaction enabled.

**Derived:** the phase-specific carrier imbalance is `57.54%` of inlet mixture flow. It is not a closed full-domain mass balance.

**Unresolved:** direct DPM-to-carrier source totals, Film DPM Mass Source, velocity-magnitude reductions, stripped/separated film terms, time-integrated film storage/outflow/source closure, case/data filenames, and a comparison against the accepted `010V2d` parent checkpoint.

**Conclusion — needs follow-up.** Keep `010V2d-2` diagnostic. The available evidence does not show an unbounded final film inventory or floating-point failure, but the large carrier imbalance and missing source/closure terms prevent attribution of any difference to global DPM interaction.

## Machine-readable evidence

- [Carrier flux check JSON](../../../PyAnsys/output/post_simulation_analysis/010V2d-2-ewf-combined-global-dpm-flux-check.json)
- [Residual check JSON](../../../PyAnsys/output/post_simulation_analysis/010V2d-2-ewf-combined-global-dpm-residual-check.json) and [plot](../../../PyAnsys/output/post_simulation_analysis/010V2d-2-ewf-combined-global-dpm-residual-check.png)
- [Completed DPM summary CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-dpm-complete/dpm_injection_summary.csv), [zone summary CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-dpm-complete/dpm_zone_summary.csv), [bookkeeping](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-dpm-complete/bookkeeping.json), and [full transcript](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-dpm-complete/dpm_particle_track_transcript.txt)
- [Per-injection DPM transcripts](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-dpm-complete/dpm_raw/)
- [EWF/DPM audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-audit/model_audit.json) and [manifest](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-audit/run_manifest.json)
- [EWF final-report CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-snapshot/final_reports.csv), [film-flux CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-snapshot/film_flux.csv), [raw results](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-snapshot/raw_results.json), and [bookkeeping snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-20260722-snapshot/bookkeeping.json)

## 6. Results at 4,189 iterations (server 3)

### 6.1 Checkpoint and applicability

- Case/data checkpoint: `010V2-d-2-4189.cas.h5` / `010V2-d-2-4189.dat.h5`, already loaded on Fluent server `3`.
- Fluent version: `Ansys Fluent 2024 R2`.
- Evidence class: **diagnostic, complete for the available carrier, DPM, and final-state EWF outputs**. It does not supply an interval EWF mass closure or direct DPM-to-carrier source totals.

| Analysis | Status | Evidence and limitation |
|---|---|---|
| Carrier flux and residual history | completed | Phase-specific fluxes and seven residual curves, ending at monitor iteration `4189`. |
| DPM Particle Tracks Summary | completed | All six live injections passed tracked-count, mass-transfer, quiet-transcript, and per-injection raw-artifact gates. |
| EWF audit | completed with adapter limitation | `wall` is the confirmed film wall; global DPM interaction is on, updated every iteration with interval `1`. |
| EWF final-state snapshot | partial | The snapshot returned inventory, thickness, CFL, component velocities, and boundary film fluxes; the mass-source and velocity-magnitude aliases remain unavailable. |
| EWF history/closure | deferred | A final checkpoint alone supports bookkeeping-only results, not time integration. |

`wall` remains the only confirmed film wall and retains the `stanton-rutland` impingement model. The root EWF Settings API remains unavailable, so its root-level mechanism flags are not interpreted from the adapter. The wall readback does confirm film-wall splash is enabled with four configured splashed particles. The snapshots only created or reused namespaced `ewfdiag-*` reports; they did not alter physics or iterate the case.

### 6.2 Carrier field and numerical state

| Quantity | Value |
|---|---:|
| Liquid inlet flow | `111.074 kg/s` |
| Vapor inlet flow | `80.690 kg/s` |
| Steam-outlet liquid flow | `0 kg/s` |
| Steam-outlet vapor flow | `81.422109 kg/s` |
| Derived phase efficiency | `1.000` |
| Steam-outlet dryness | `1.000` |
| Derived carrier mass imbalance | `110.341891 kg/s` (`57.5405%`); informational only under the simplified Purnanto scope |

The mixture mass-flow report was unavailable. The imbalance is therefore derived from phase-specific fluxes and remains a scoped diagnostic, not a full-domain mass balance or separator-performance result.

The residual export contains seven curves and `689` points from monitor iteration `128` to `4189`. Final values are continuity `6.043e-3`, x/y/z velocity `8.536e-5` / `8.573e-5` / `9.715e-5`, liquid volume fraction `1.286e-3`, `k` `7.224e-3`, and epsilon `4.552e-2`. The turbulence residuals decreased substantially, but continuity is higher than at the prior checkpoint and the unresolved carrier imbalance prevents a convergence or validation claim.

### 6.3 DPM Particle Tracks Summary

All six injections completed in ascending diameter order. `Escaped` fates terminate at `steamoutlet`; `Trapped` fates terminate at `bottom`. EWF absorbed, splashed, stripped, and separated counters are interaction diagnostics, not extra terminal mass sinks.

| Diameter (µm) | Injection | Net flow (kg/s) | Escaped | Trapped | Incomplete | Final absorbed fate | EWF absorbed events | Splash events | Closure residual (kg/s) |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `5.63` | `water-liquid-at-psep-5um` | `0.03801` | 2156 | 0 | 14 | not printed | not printed | not printed | `-5.20e-6` |
| `28.14` | `water-liquid-at-psep-28um` | `0.1561` | 2160 | 8 | 1 | 1 | 1 | not printed | `8.088e-5` |
| `56.27` | `water-liquid-at-psep-56um` | `0.1941` | 1875 | 21 | 0 | 274 | 274 | not printed | `2.20e-5` |
| `112.54` | `water-liquid-at-psep-112um` | `0.3901` | 1355 | 49 | 2 | 764 | 764 | not printed | `-6.86e-5` |
| `168.81` | `water-liquid-at-psep-168um` | `0.3901` | 895 | 81 | 0 | 1194 | 1194 | not printed | `-6.00e-5` |
| `348.88` | `water-liquid-at-psep-348um` | `4.750` | 357 | 134 | 0 | 1990 | 2011 | 84 | `2.00e-4` |

For the `348.88 µm` injection, Fluent also reports `5` stripped and `222` separated EWF particle events. These are not added to the terminal closure, because the final fates already represent the terminal particle accounting. The largest relative closure residual is `5.18e-4` (`28.14 µm`), consistent with printed-report precision. An unprinted counter is preserved as `not printed`, not changed to zero.

### 6.4 EWF final-state and bookkeeping-only results

The final-state snapshot is scoped to `wall`. Units below are the requested Fluent report dimensions; the diagnostic CSV does not return unit cells as an independent Fluent readback.

| Quantity | Value | Requested dimension | Interpretation limit |
|---|---:|---|---|
| Maximum Film Courant Number | `0.0056902254` | dimensionless | final-state numerical diagnostic only |
| Film Mass | `0.1691669` | kg | current inventory, not an integrated balance |
| Maximum Film Thickness | `5.1177549e-4` | m | local maximum |
| Area-weighted Film Thickness | `2.8654671e-6` | m | distributed average |
| Film Outflow Mass | `0` | kg | final reported cumulative/snapshot quantity only |
| Area-weighted Film x velocity | `0.10379051` | m/s | component value only |
| Area-weighted Film y velocity | `1.3825066e-4` | m/s | component value only |
| Area-weighted Film z velocity | `0.045745551` | m/s | component value only |

The mixture film-mass-flow query returns `0 kg/s` on `liquidinlet`, `steaminlet`, and `steamoutlet` (net `0 kg/s`). This final-state readback is not evidence that no film transport occurred during the solve. `Film DPM Mass Source` and film-velocity-magnitude reports remain unavailable because this Fluent version exposes `film-dpm-mass-src` and `film-velocity-mag` rather than the runner's requested aliases. The root-level adapter classifies stripping and edge separation as unavailable; therefore corresponding film-mass snapshot values are not reported as zero, even though the 348.88 µm track summary prints stripped/separated particle events.

This checkpoint is **bookkeeping-only**: it has no defined interval, initial film inventory, or time-integrated DPM source/inflow/outflow terms. Inventory in `kg` must not be combined with the final flux rates in `kg/s` to claim film conservation.

### 6.5 Interpretation and next action

**Measured:** the exact loaded 4,189-iteration checkpoint; finite `0.1691669 kg` film inventory; bounded final Film CFL; phase-specific carrier fluxes; residual history; global DPM interaction readback; and complete six-injection DPM fate/mass-transfer outputs.

**Derived:** the phase-specific carrier imbalance is `57.5405%` of inlet mixture flow. DPM terminal closures are within the precision of the printed mass-transfer summaries.

**Unresolved:** direct DPM-to-carrier mass/momentum source totals; Film DPM Mass Source; velocity-magnitude reductions; root-level EWF stripping/separation state and film-mass terms; and a time-integrated film closure.

**Conclusion — remains diagnostic.** The 4,189-iteration state has a finite but substantially larger film inventory and no floating-point failure in the captured diagnostics. The carrier imbalance remains far too large to attribute observed changes solely to global DPM interaction or to make a separator-performance claim. Before another run, create interval histories for film inventory, DPM-to-film source, and outflow, then assess carrier continuity together with direct DPM source totals.

### 6.6 Machine-readable evidence at 4,189 iterations

- [Carrier flux check JSON](../../../PyAnsys/output/post_simulation_analysis/010V2d-2-server3-4189it-20260723-flux-check.json)
- [Residual check JSON](../../../PyAnsys/output/post_simulation_analysis/010V2d-2-server3-4189it-20260723-residual-check.json) and [plot](../../../PyAnsys/output/post_simulation_analysis/010V2d-2-server3-4189it-20260723-residual-check.png)
- [EWF/DPM audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-audit/model_audit.json) and [manifest](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-audit/run_manifest.json)
- [EWF final-report CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-snapshot/final_reports.csv), [film-flux CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-snapshot/film_flux.csv), [raw results](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-snapshot/raw_results.json), and [bookkeeping snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-snapshot/bookkeeping.json)
- [DPM summary CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-dpm/dpm_injection_summary.csv), [zone summary CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-dpm/dpm_zone_summary.csv), [bookkeeping](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-dpm/bookkeeping.json), [full transcript](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-dpm/dpm_particle_track_transcript.txt), and [per-injection transcripts](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2d-2-server3-4189it-20260723-dpm/dpm_raw/)

## 7. Previous checkpoint versus 4,189 iterations

The previous evidence section above ends at residual-monitor iteration `2068`; this comparison uses that documented checkpoint rather than the unrelated discarded server-1 capture. Both checkpoints use the same branch, Fluent version, six injection identities, and phase-specific carrier-flux scope.

### 7.1 Carrier and residual comparison

| Quantity | Previous (`2068`) | At `4189` | Change |
|---|---:|---:|---:|
| Steam-outlet vapor flow (kg/s) | `81.419309` | `81.422109` | `+0.002800` |
| Carrier imbalance (kg/s) | `110.344691` | `110.341891` | `-0.002800` |
| Carrier imbalance (% inlet mixture) | `57.54%` | `57.5405%` | effectively unchanged |
| Continuity residual | `2.875e-3` | `6.043e-3` | `+110%` |
| k residual | `2.057e-1` | `7.224e-3` | `-96.5%` |
| Epsilon residual | `3.845e-1` | `4.552e-2` | `-88.2%` |

Velocity and liquid-volume-fraction residuals remain low (`8.54e-5` to `9.72e-5` and `1.286e-3` at 4,189 iterations), but continuity worsened. The outlet flux and derived imbalance are effectively static, so extra iterations have not remedied the scoped carrier-balance limitation.

### 7.2 EWF final-state comparison

| Quantity | Previous (`2068`) | At `4189` | Change |
|---|---:|---:|---:|
| Maximum Film Courant Number | `0.003872775` | `0.005690225` | `+46.9%` |
| Film Mass (kg) | `0.0799062` | `0.1691669` | `+111.7%` |
| Maximum Film Thickness (m) | `1.7669208e-4` | `5.1177549e-4` | `+189.6%` |
| Area-weighted Film Thickness (m) | `1.353507e-6` | `2.8654671e-6` | `+111.7%` |
| Film Outflow Mass (kg) | `0` | `0` | unchanged final-state readback |
| Boundary/net film mass flow (kg/s) | `0` | `0` | unchanged final-state readback |

The film inventory more than doubled and the maximum thickness nearly tripled while the available final-state outflow readbacks remain zero. This is an observation, not a film-closure result: no interval source/outflow histories exist to distinguish genuine accumulation from the unresolved accounting terms.

### 7.3 DPM fate comparison

| Diameter (µm) | Escaped: previous → 4189 | Trapped: previous → 4189 | Final absorbed: previous → 4189 | Key change |
|---:|---:|---:|---:|---|
| `5.63` | `2157 → 2156` | `0 → 0` | `2 → not printed` | incomplete `11 → 14` |
| `28.14` | `2161 → 2160` | `3 → 8` | `6 → 1` | incomplete `0 → 1` |
| `56.27` | `1944 → 1875` | `6 → 21` | `219 → 274` | fewer escapes, more wall absorption/trapping |
| `112.54` | `1389 → 1355` | `17 → 49` | `764 → 764` | incomplete `0 → 2` |
| `168.81` | `906 → 895` | `34 → 81` | `1258 → 1194` | more trapping, fewer final absorbed fates |
| `348.88` | `590 → 357` | `68 → 134` | `1746 → 1990` | EWF events: splash `44 → 84`; current track also prints stripped `5`, separated `222` |

At 4,189 iterations the larger droplets show a stronger redistribution away from `steamoutlet` escape and toward final EWF absorption/trapping, most notably at `348.88 µm`. The comparison is diagnostic only: the different final film inventory, lack of film-history closure, and unresolved carrier imbalance mean it cannot establish a causal global-DPM-interaction effect.

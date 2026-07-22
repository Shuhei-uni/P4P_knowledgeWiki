# Diagnostic Results Report — Setup 010V2d-2

## Setup link and run identity

- Setup definition: [010V2d-2 — Combined EWF with Global DPM Interaction](../../future/010V2d-2-ewf-combined-global-dpm.md)
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
| Derived carrier mass imbalance | `110.344691 kg/s` (`57.54%` of inlet mixture flow) |

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

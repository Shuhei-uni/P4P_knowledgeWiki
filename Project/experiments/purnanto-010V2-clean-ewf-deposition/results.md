> **Legacy source:** Setups/reports/purnanto-reference/010V2/results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Diagnostic Results Report — Setup 010V2

## Setup link and evidence

- Setup definition: [010V2 — EWF Deposition and Film-Inventory Control](setup.md)
- Parent: [09cV2 — Skoog Partition and Injection-Control Branch](../purnanto-09cV2-dpm-partition-control/setup.md)
- Fluent session: server `3`, `Ansys Fluent 2025 R2`; analysis date `2026-07-22`.
- Case/data checkpoint: already loaded in Fluent; filenames were not exposed by the read-only diagnostics.
- Evidence class: **diagnostic**. The checks did not change solver physics, iterations, or case/data; the snapshot only created/reused `ewfdiag-*` report definitions.

## Analysis applicability

| Analysis | Status | Evidence / limitation |
|---|---|---|
| Carrier flux and residual checks | completed | Phase-specific fluxes and seven residual curves were exported. |
| DPM fate analysis | completed | All six live injections passed the transcript completion gate. |
| EWF audit | completed with adapter limitation | `wall` is the only confirmed film wall; the 2025 R2 EWF Settings API root was unavailable. |
| EWF final-state snapshot | partial | Final inventory, thickness, CFL, flux, and velocity components were captured on `wall`; source and velocity-magnitude aliases failed. |
| EWF history / closure | deferred | Only a final checkpoint was available, so this is bookkeeping-only. |
| Splash, stripping, and edge separation | not available as root-level readback | The audit did not expose their EWF root flags. No missing or unprinted value is treated as zero. |

The wall readback confirms initial film-wall state on `wall`, `stanton-rutland` as its impingement model, zero initial film height/velocity, and flow-momentum coupling off. `bottom` is not an EWF wall and has DPM fate `trap`. Global DPM interaction is `Off`; unsteady particle tracking is `Off`; and maximum DPM steps is `10000`. These support the intended `010V2` control scope, but the unavailable root API prevents a full optional-mechanism confirmation.

## Carrier-field and numerical state

| Quantity | Value |
|---|---:|
| Liquid inlet flow | `111.074 kg/s` |
| Vapor inlet flow | `80.690 kg/s` |
| Steam-outlet liquid flow | `0 kg/s` |
| Steam-outlet vapor flow | `81.4226 kg/s` |
| Derived phase efficiency | `1.000` |
| Steam-outlet dryness | `1.000` |
| Derived carrier imbalance | `110.3414 kg/s` (`57.54%` of inlet mixture flow) |

The live state did not reveal a phase/material mapping, so the flux tool used its fallback `phase-1 = vapor`, `phase-2 = liquid`. Fluent did not provide a mixture mass-flow report; the imbalance is therefore a scoped phase-flux diagnostic, not a closed conservation result.

The residual export contains seven curves and `884` points from monitor iteration `4` through `1884`. Final residuals are continuity `2.362e-3`, x/y/z velocity `4.075e-5` / `4.087e-5` / `4.401e-5`, liquid volume fraction `1.252e-3`, `k` `2.335e-2`, and epsilon `2.439e-2`. The velocity residuals decreased substantially, but the remaining continuity level and large flux imbalance do not establish convergence or separator validation.

## DPM Particle Tracks Summary

All original injections completed in diameter-ascending order. `Escaped` particles terminate at `steamoutlet`; `Trapped` particles terminate at `bottom`. The absorbed-fate count below is the final Particle Tracks fate, while the EWF absorbed-event count is a separate Fluent interaction diagnostic. Fluent did not print splash events for this run, so that field is reported as unavailable rather than zero.

| Diameter (µm) | Injection | Net flow (kg/s) | Escaped | Trapped | Incomplete | Final absorbed fate | EWF absorbed events | Splash events | Closure residual (kg/s) |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| `5.63` | `water-liquid-at-psep-5um` | `0.03801` | 2153 | 0 | 16 | 1 | 1 | not printed | `-7.82e-6` |
| `28.14` | `water-liquid-at-psep-28um` | `0.1561` | 2134 | 3 | 13 | 20 | 20 | not printed | `1.14e-5` |
| `56.27` | `water-liquid-at-psep-56um` | `0.1941` | 1944 | 2 | 5 | 219 | 219 | not printed | `-1.61e-5` |
| `112.54` | `water-liquid-at-psep-112um` | `0.3901` | 1479 | 18 | 10 | 663 | 663 | not printed | `-3.40e-5` |
| `168.81` | `water-liquid-at-psep-168um` | `0.3901` | 985 | 30 | 0 | 1155 | 1155 | not printed | `-9.40e-5` |
| `348.88` | `water-liquid-at-psep-348um` | `4.678` | 439 | 52 | 0 | 1679 | 1679 | not printed | `6.00e-4` |

Every transcript contains the required tracked-count line, Mass Transfer Summary, parsed terminal mass-transfer row, and at least `1.0 s` quiet interval. The maximum relative closure residual is `2.41e-4` for the `168.81 µm` injection (the largest absolute residual is `6.00e-4 kg/s` for `348.88 µm`), consistent with the printed mass-flow precision. Fine droplets are predominantly escape fates; absorption becomes the dominant original-particle fate at `168.81 µm` and above. This fate pattern is diagnostic only because the carrier mass balance remains open.

## EWF final-state snapshot

The snapshot is scoped to the confirmed `wall` film wall and is a single final-state readback. The CSV left unit cells blank; dimensions below are the Fluent report dimensions requested by the diagnostic, not an independent unit readback.

| Quantity | Value | Dimension | Interpretation limit |
|---|---:|---|---|
| Maximum Film Courant Number | `0.0032725923` | dimensionless | final-state numerical diagnostic only |
| Film Mass | `0.071499171` | kg | current film inventory, not an integrated balance |
| Maximum Film Thickness | `1.519645e-4` | m | local maximum (`0.152 mm`) |
| Area-weighted Film Thickness | `1.2111029e-6` | m | distributed average (`1.211 µm`) |
| Film Outflow Mass | `1.8709544e-8` | kg | snapshot/cumulative field only |
| `steamoutlet` film mass flow | `-1.7573375e-6` | kg/s | preserve Fluent's report sign |
| Area-weighted Film x velocity | `0.060466394` | m/s | component only |
| Area-weighted Film y velocity | `5.7609767e-4` | m/s | component only |
| Area-weighted Film z velocity | `0.01762499` | m/s | component only |

The flux query returned `0 kg/s` at `liquidinlet` and `steaminlet`; its net equals the signed `steamoutlet` value above. The final CFL is bounded at the captured state, but one point cannot exclude an earlier transient CFL/source spike.

`Film DPM Mass Source`, area-weighted film-velocity magnitude, and maximum film-velocity magnitude were not extracted because Fluent 2025 R2 exposes the aliases `film-dpm-mass-src` and `film-velocity-mag`, while the diagnostic runner requested unsupported aliases. The raw results preserve those failures. Stripped and separated film-mass results were classified inactive by the snapshot adapter, but the root mechanism flags were unavailable; no stripped/separated mass is claimed.

## Bookkeeping, interpretation, and next action

**Measured:** finite film inventory/thickness on `wall`; bounded final CFL; signed final film outlet flux; carrier fluxes/residual history; and complete original-particle fate summaries for all six injections.

**Derived:** absorption increases strongly with diameter and becomes the dominant original-particle fate at `168.81 µm` and `348.88 µm`; the phase-specific carrier imbalance is `57.54%` of inlet mixture flow.

**Unresolved:** case/data filenames; phase/material mapping; mixture mass-flow report; root-level EWF option states; Film DPM Mass Source; velocity-magnitude reductions; splash readback; and any time-integrated film source, outflow, or inventory balance. A final snapshot mixes inventories (`kg`) and rates (`kg/s`), so it is explicitly **bookkeeping-only**, not an EWF closure.

**Conclusion — needs follow-up.** The reported state shows a finite, thin wall film and a low final film CFL, with increasing deposition for larger droplets. It does not meet the `010V2` acceptance gate because the carrier balance is open and no defined-interval EWF history exists. Before continuing or rerunning, create histories for film inventory, film CFL, Film DPM Mass Source, and film boundary mass flow; then resolve the carrier phase/mixture flux balance before making separator-performance or film-conservation claims.

## Machine-readable evidence

- Carrier flux check (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/010V2-20260722-flux-check.json`; not migrated), residual check (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/010V2-20260722-residual-check.json`; not migrated), and residual plot (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/010V2-20260722-residual-check.png`; not migrated)
- EWF/DPM audit (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-audit/model_audit.json`; not migrated) and audit manifest (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-audit/run_manifest.json`; not migrated)
- EWF final-report CSV (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/final_reports.csv`; not migrated), film-flux CSV (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/film_flux.csv`; not migrated), raw snapshot results (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/raw_results.json`; not migrated), and bookkeeping snapshot (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/bookkeeping.json`; not migrated)
- Completed DPM summary CSV (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_injection_summary.csv`; not migrated), zone summary CSV (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_zone_summary.csv`; not migrated), bookkeeping (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/bookkeeping.json`; not migrated), full transcript (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_particle_track_transcript.txt`; not migrated), and per-injection transcripts (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_raw`; not migrated)

## 5,000-iteration results

This is a second read-only evidence checkpoint from the already loaded `010V2` case/data state on server `1`, captured on 2026-07-23 with Ansys Fluent 2025 R2. It does not change the setup or solver physics; the EWF snapshot only reused `ewfdiag-*` diagnostic report definitions. The residual history reaches monitor iteration `4996`, so this section is referred to as the **5,000-iteration checkpoint**.

| Analysis | Status | Evidence / limitation |
|---|---|---|
| Carrier flux and residual checks | completed | Phase-specific fluxes and seven residual curves were exported. |
| DPM fate analysis | completed | All six live injections passed the transcript completion gate. |
| EWF audit | completed with adapter limitation | `wall` remains the only confirmed film wall; the EWF Settings API root was unavailable. |
| EWF final-state snapshot | partial | Final inventory, thickness, CFL, flux, and velocity components were captured on `wall`; source and velocity-magnitude aliases still failed. |
| EWF history / closure | deferred | This remains a single final checkpoint and therefore bookkeeping-only. |
| Splash, stripping, and edge separation | not available as root-level readback | No unavailable or unprinted value is treated as zero; stripping and separation report terms remain inactive. |

The live audit again found `wall` as the film wall with `stanton-rutland` impingement, zero initial film height/velocity, and flow-momentum coupling off. `bottom` remains a non-film wall with DPM fate `trap`. Global DPM interaction and unsteady particle tracking remain `Off`; maximum DPM steps remains `10000`. The EWF root API limitation means that the optional-mechanism flags cannot be fully read back from this adapter.

### Carrier-field and numerical state at the 5,000-iteration checkpoint

| Quantity | Value |
|---|---:|
| Liquid inlet flow | `111.074 kg/s` |
| Vapor inlet flow | `80.690 kg/s` |
| Steam-outlet liquid flow | `0 kg/s` |
| Steam-outlet vapor flow | `81.4212 kg/s` |
| Derived phase efficiency | `1.000` |
| Steam-outlet dryness | `1.000` |
| Derived carrier imbalance | `110.3428 kg/s` (`57.54%` of inlet mixture flow) |

The confirmed phase mapping is `phase-1 = water-vapor-at-psep` and `phase-2 = water-liquid-at-psep`. Fluent still did not provide a mixture mass-flow report, so the imbalance remains a scoped phase-flux diagnostic rather than a closed conservation result.

The residual export contains seven curves and `996` points from monitor iteration `256` through `4996`. Final residuals are continuity `7.157e-3`, x/y/z velocity `1.041e-4` / `1.072e-4` / `1.176e-4`, liquid volume fraction `1.390e-3`, `k` `9.104e-3`, and epsilon `1.898e-2`. The carrier phase-flux imbalance remains open and the final continuity residual is higher than at the earlier checkpoint; this does not establish convergence or separator validation.

### DPM Particle Tracks Summary at the 5,000-iteration checkpoint

All six original injections completed in diameter-ascending order. `Escaped` particles terminate at `steamoutlet` and `Trapped` particles terminate at `bottom`. The absorbed-fate count is a final Particle Tracks fate; the EWF absorbed-event count is a separate interaction diagnostic. Fluent did not print splash events, so splash is **not available**, not zero.

| Diameter (µm) | Injection | Net flow (kg/s) | Escaped | Trapped | Incomplete | Final absorbed fate | EWF absorbed events | Splash events | Closure residual (kg/s) |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| `5.63` | `water-liquid-at-psep-5um` | `0.03801` | 2157 | 0 | 6 | 7 | 7 | not printed | `-7.70e-6` |
| `28.14` | `water-liquid-at-psep-28um` | `0.1561` | 2117 | 9 | 2 | 42 | 42 | not printed | `8.90e-5` |
| `56.27` | `water-liquid-at-psep-56um` | `0.1941` | 1872 | 12 | 0 | 286 | 286 | not printed | `4.70e-5` |
| `112.54` | `water-liquid-at-psep-112um` | `0.3901` | 1338 | 58 | 0 | 774 | 774 | not printed | `-1.30e-4` |
| `168.81` | `water-liquid-at-psep-168um` | `0.3901` | 883 | 79 | 0 | 1208 | 1208 | not printed | `-1.00e-4` |
| `348.88` | `water-liquid-at-psep-348um` | `4.678` | 135 | 82 | 0 | 1953 | 1953 | not printed | `2.00e-4` |

Every injection has a `number tracked` line, Mass Transfer Summary, parsed mass-transfer rows, at least a `1.0 s` quiet transcript interval, an individual raw transcript, and the completed CSV/JSON bundle. The largest relative closure residual is `5.70e-4` (`28.14 µm`), which is consistent with printed mass-flow precision. Larger droplets remain predominantly absorbed by the wall-film interaction, while the smallest droplets remain predominantly escaped.

### EWF final-state results at the 5,000-iteration checkpoint

The snapshot is scoped to the confirmed `wall` film wall. The CSV unit cells are blank; dimensions below are the requested Fluent-report dimensions, not an independent unit readback.

| Quantity | Value | Dimension | Interpretation limit |
|---|---:|---|---|
| Maximum Film Courant Number | `0.0055245073` | dimensionless | final-state numerical diagnostic only |
| Film Mass | `0.20448504` | kg | current inventory, not an integrated balance |
| Maximum Film Thickness | `4.7140205e-4` | m | local maximum (`0.471 mm`) |
| Area-weighted Film Thickness | `3.4637104e-6` | m | distributed average (`3.464 µm`) |
| Film Outflow Mass | `8.1856682e-8` | kg | snapshot/cumulative field only |
| `steamoutlet` film mass flow | `-1.5345366e-6` | kg/s | preserve Fluent's report sign |
| Area-weighted Film x velocity | `0.13980836` | m/s | component only |
| Area-weighted Film y velocity | `-0.0014074416` | m/s | component only |
| Area-weighted Film z velocity | `0.053088067` | m/s | component only |

The film-flux query returned `0 kg/s` at `liquidinlet` and `steaminlet`; the net is the signed `steamoutlet` value above. The final CFL is low at the captured state, but a final snapshot cannot exclude an earlier spike. `Film DPM Mass Source`, area-weighted film-velocity magnitude, and maximum film-velocity magnitude remain unavailable because the 2025 R2 field aliases exposed by Fluent (`film-dpm-mass-src` and `film-velocity-mag`) are not yet resolved by the diagnostic adapter. No stripped or separated mass is claimed.

**Measured:** a finite film on `wall`; final film inventory, thickness, CFL, film flux, and velocity components; phase-specific carrier fluxes/residual history; and complete original-particle DPM fate summaries.

**Derived:** between the two checkpoints the film inventory and film thickness increased materially, while large-droplet escape decreased and large-droplet absorption increased. The phase-specific carrier imbalance remains approximately `57.54%` of inlet mixture flow.

**Unresolved:** case/data filenames; a mixture mass-flow report; EWF root-option readback; Film DPM Mass Source; velocity-magnitude reductions; splash readback; and all history terms needed for a time-integrated film closure. This is explicitly **bookkeeping-only**, not an EWF mass closure.

**Conclusion — needs follow-up.** The 5,000-iteration checkpoint has a larger but still thin local film, a low final film CFL, and stronger deposition of the larger droplets. It still fails the `010V2` interpretation gate because the carrier balance is open, the continuity residual has not converged, and EWF histories are absent. Create histories for film inventory, film CFL, Film DPM Mass Source, and film boundary mass flow before another continued run; resolve the carrier phase/mixture flux balance before making separator-performance or film-conservation claims.

Evidence: carrier flux check (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/010V2-5000it-20260723-flux-check.json`; not migrated), residual check (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/010V2-5000it-20260723-residual-check.json`; not migrated), residual plot (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/010V2-5000it-20260723-residual-check.png`; not migrated), EWF/DPM audit (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-audit/model_audit.json`; not migrated), snapshot CSV (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-snapshot/final_reports.csv`; not migrated), film-flux CSV (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-snapshot/film_flux.csv`; not migrated), snapshot bookkeeping (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-snapshot/bookkeeping.json`; not migrated), DPM summary (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-dpm/dpm_injection_summary.csv`; not migrated), DPM zone summary (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-dpm/dpm_zone_summary.csv`; not migrated), DPM bookkeeping (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-dpm/bookkeeping.json`; not migrated), full DPM transcript (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-dpm/dpm_particle_track_transcript.txt`; not migrated), and per-injection transcripts (historical machine artifact path: `../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-5000it-20260723-dpm/dpm_raw`; not migrated).

## Comparison: previous checkpoint (residual monitor through iteration 1884) vs 5,000-iteration checkpoint

The earlier report did not prove that the loaded case had stopped exactly at iteration `1884`; it records a residual history ending at monitor iteration `1884`. The comparison below therefore uses that evidence checkpoint against the new residual history ending at `4996` (the requested 5,000-iteration state). Values are retained at the reported precision.

### Carrier and residual values

| Quantity | Previous checkpoint | 5,000-iteration checkpoint | Change / reading |
|---|---:|---:|---|
| Liquid inlet flow (kg/s) | `111.074` | `111.074` | unchanged |
| Vapor inlet flow (kg/s) | `80.690` | `80.690` | unchanged |
| Steam-outlet liquid flow (kg/s) | `0` | `0` | unchanged |
| Steam-outlet vapor flow (kg/s) | `81.4226` | `81.4212` | `-0.0014 kg/s` |
| Derived phase efficiency | `1.000` | `1.000` | unchanged scoped metric |
| Steam-outlet dryness | `1.000` | `1.000` | unchanged scoped metric |
| Derived carrier imbalance (kg/s) | `110.3414` | `110.3428` | `+0.0014 kg/s`; still `57.54%` of inlet mixture flow |
| Residual-monitor range | `4–1884` | `256–4996` | later checkpoint contains `996` rather than `884` exported points |
| Final continuity residual | `2.362e-3` | `7.157e-3` | increased by about `3.03×` |
| Final x-velocity residual | `4.075e-5` | `1.041e-4` | increased by about `2.55×` |
| Final y-velocity residual | `4.087e-5` | `1.072e-4` | increased by about `2.62×` |
| Final z-velocity residual | `4.401e-5` | `1.176e-4` | increased by about `2.67×` |
| Final liquid-volume-fraction residual | `1.252e-3` | `1.390e-3` | increased by about `11.1%` |
| Final `k` residual | `2.335e-2` | `9.104e-3` | decreased by about `61.0%` |
| Final epsilon residual | `2.439e-2` | `1.898e-2` | decreased by about `22.2%` |

### DPM fate and closure values

| Diameter (µm) | Net flow (kg/s) previous → 5,000 | Escaped previous → 5,000 | Trapped previous → 5,000 | Incomplete previous → 5,000 | Final absorbed previous → 5,000 | EWF absorbed events previous → 5,000 | Closure residual (kg/s) previous → 5,000 |
|---:|---|---|---|---|---|---|---|
| `5.63` | `0.03801 → 0.03801` | `2153 → 2157` | `0 → 0` | `16 → 6` | `1 → 7` | `1 → 7` | `-7.82e-6 → -7.70e-6` |
| `28.14` | `0.1561 → 0.1561` | `2134 → 2117` | `3 → 9` | `13 → 2` | `20 → 42` | `20 → 42` | `1.14e-5 → 8.90e-5` |
| `56.27` | `0.1941 → 0.1941` | `1944 → 1872` | `2 → 12` | `5 → 0` | `219 → 286` | `219 → 286` | `-1.61e-5 → 4.70e-5` |
| `112.54` | `0.3901 → 0.3901` | `1479 → 1338` | `18 → 58` | `10 → 0` | `663 → 774` | `663 → 774` | `-3.40e-5 → -1.30e-4` |
| `168.81` | `0.3901 → 0.3901` | `985 → 883` | `30 → 79` | `0 → 0` | `1155 → 1208` | `1155 → 1208` | `-9.40e-5 → -1.00e-4` |
| `348.88` | `4.678 → 4.678` | `439 → 135` | `52 → 82` | `0 → 0` | `1679 → 1953` | `1679 → 1953` | `6.00e-4 → 2.00e-4` |

Splash events were not printed at either checkpoint, so no numerical splash comparison is made. All six injection flows are unchanged. The fate shift is consistent with greater wall-film absorption as the continued solution develops, especially for the `112.54–348.88 µm` classes; it is not a separator-performance claim while the carrier balance remains open.

### EWF final-state values

| Quantity | Previous checkpoint | 5,000-iteration checkpoint | Change / reading |
|---|---:|---:|---|
| Maximum Film Courant Number | `0.0032725923` | `0.0055245073` | `+68.8%`; both final values are low |
| Film Mass (kg) | `0.071499171` | `0.20448504` | `+0.132985869 kg` (`2.86×`) |
| Maximum Film Thickness (m) | `1.519645e-4` | `4.7140205e-4` | `+3.1943755e-4 m` (`3.10×`) |
| Area-weighted Film Thickness (m) | `1.2111029e-6` | `3.4637104e-6` | `+2.2526075e-6 m` (`2.86×`) |
| Film Outflow Mass (kg) | `1.8709544e-8` | `8.1856682e-8` | `4.38×`; snapshot/cumulative field only |
| `steamoutlet` film mass flow (kg/s) | `-1.7573375e-6` | `-1.5345366e-6` | magnitude decreased by about `12.7%` |
| Area-weighted Film x velocity (m/s) | `0.060466394` | `0.13980836` | `2.31×` |
| Area-weighted Film y velocity (m/s) | `5.7609767e-4` | `-0.0014074416` | sign reversal; component needs spatial context |
| Area-weighted Film z velocity (m/s) | `0.01762499` | `0.053088067` | `3.01×` |
| Film DPM Mass Source (kg/s) | unavailable | unavailable | Fluent alias unresolved in both snapshots |
| Area-weighted Film Velocity Magnitude (m/s) | unavailable | unavailable | Fluent alias unresolved in both snapshots |
| Maximum Film Velocity Magnitude (m/s) | unavailable | unavailable | Fluent alias unresolved in both snapshots |
| Film Stripped Mass | inactive mechanism | inactive mechanism | no value claimed |
| Film Separated Mass | inactive mechanism | inactive mechanism | no value claimed |

The comparison shows a growing film inventory and stronger large-droplet absorption, without a high final CFL at either sample. It cannot establish bounded inventory, drainage balance, or conservation because neither checkpoint supplies the required defined-interval histories and integrated source/outflow terms.

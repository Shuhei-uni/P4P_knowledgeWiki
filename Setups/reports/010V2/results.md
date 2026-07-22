# Diagnostic Results Report — Setup 010V2

## Setup link and evidence

- Setup definition: [010V2 — EWF Deposition and Film-Inventory Control](../../active/010V2-ewf-deposition-film-inventory.md)
- Parent: [09cV2 — Skoog Partition and Injection-Control Branch](../../active/09cV2-skoog-partition-injection-control.md)
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

- [Carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2-20260722-flux-check.json), [residual check](../../../PyAnsys/output/post_simulation_analysis/010V2-20260722-residual-check.json), and [residual plot](../../../PyAnsys/output/post_simulation_analysis/010V2-20260722-residual-check.png)
- [EWF/DPM audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-audit/model_audit.json) and [audit manifest](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-audit/run_manifest.json)
- [EWF final-report CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/final_reports.csv), [film-flux CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/film_flux.csv), [raw snapshot results](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/raw_results.json), and [bookkeeping snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-snapshot/bookkeeping.json)
- [Completed DPM summary CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_injection_summary.csv), [zone summary CSV](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_zone_summary.csv), [bookkeeping](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/bookkeeping.json), [full transcript](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_particle_track_transcript.txt), and [per-injection transcripts](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2-20260722-dpm/dpm_raw/)

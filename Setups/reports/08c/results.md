# Preliminary Results Report — Setup 08c

## Setup link and evidence

- Setup definition: [08c-purnanto-parity-inlet-velocity-sensitivity.md](../../active/08c-purnanto-parity-inlet-velocity-sensitivity.md)
- Fluent server: `1`
- Fluent version: `Ansys Fluent 2024 R2`
- Evidence class: partial diagnostic; neither run has a closed carrier mass balance or converged residual history.
- DPM: six-injection Particle Tracks Summary analysis completed for both checkpoints; the runs remain partial/nonconverged.

## 1. Highest-iteration carrier results

| Case | Data checkpoint | Liquid inlet | Vapor inlet | Steam-outlet liquid | Steam-outlet vapor | Scoped steam-line liquid removal | Steam-outlet dryness | Derived phase imbalance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `08c-v20p00` | `3088` | `86.18 kg/s` | `60.21 kg/s` | `0.00132696 kg/s` | `60.76847 kg/s` | `99.99846%` | `99.99782%` | `85.6202 kg/s` (`58.49%`) |
| `08c-v32p14` | `5000` | `138.48 kg/s` | `96.76 kg/s` | `0.1132807 kg/s` | `97.659468 kg/s` | `99.91820%` | `99.88414%` | `137.4673 kg/s` (`58.44%`) |

The carryover values are scoped to the steam outlet. They must not be presented as full separator efficiency because the phase balance is not closed.

## 2. Residual and stability findings

- `v20p00`: residual monitor export covered the run to approximately iteration `3088`; continuity remained on the order of `10^-1` rather than approaching a converged level.
- `v32p14`: residual monitor export covered `5000` iterations; continuity also remained on the order of `10^-1`, with intermittent epsilon spikes and a persistent phase-fraction residual plateau.
- Both cases show improving velocity, `k`, and `epsilon` residuals, but continuity and phase-fraction behaviour prevent quantitative acceptance.

Residual plots:

- [v20p00 residual history](../../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-residuals_20260720_131511.png)
- [v32p14 residual history](../../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-residuals_20260720_131754.png)

Machine-readable post-processing:

- [v20p00 summary](../../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-summary.json)
- [v32p14 summary](../../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-summary.json)

## 3. DPM particle-fate analysis

Each injection contained `2170` tracked parcels in the saved checkpoint. The table reports final fate counts as `escaped / trapped / incomplete`; aborted and evaporated counts were zero.

| Diameter | `08c-v20p00` fate counts | `08c-v32p14` fate counts |
|---:|---:|---:|
| `5.63 µm` | `1 / 851 / 1318` | `13 / 0 / 2157` |
| `28.14 µm` | `0 / 1010 / 1160` | `0 / 0 / 2170` |
| `56.27 µm` | `0 / 1160 / 1010` | `0 / 0 / 2170` |
| `112.54 µm` | `0 / 1301 / 869` | `0 / 0 / 2170` |
| `168.81 µm` | `0 / 1415 / 755` | `0 / 0 / 2170` |
| `348.88 µm` | `0 / 1621 / 549` | `0 / 0 / 2170` |

Mass-flow summaries from Fluent, in `kg/s`, are reported as `escaped / trapped / incomplete`:

| Diameter | `08c-v20p00` | `08c-v32p14` |
|---:|---:|---:|
| `5.63 µm` | `0.00008756 / 0.07451 / 0.1154` | `0.001138 / 0 / 0.1889` |
| `28.14 µm` | `0 / 0.3630 / 0.4170` | `0 / 0 / 0.7800` |
| `56.27 µm` | `0 / 0.5185 / 0.4515` | `0 / 0 / 0.9700` |
| `112.54 µm` | `0 / 1.169 / 0.7809` | `0 / 0 / 1.950` |
| `168.81 µm` | `0 / 1.272 / 0.6785` | `0 / 0 / 1.950` |
| `348.88 µm` | `not emitted / not emitted / not emitted` | `not emitted / not emitted / not emitted` |

The `348.88 µm` count summary was emitted, but Fluent did not complete its mass-transfer rows in the captured transcript. The raw audit files are preserved here:

- [v20p00 DPM JSON](../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-summary.json), [CSV](../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-summary.csv), [transcript](../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-transcript.txt)
- [v32p14 DPM JSON](../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-summary.json), [CSV](../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-summary.csv), [transcript](../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-transcript.txt)

Across the six injections, `v20p00` produced `7358` trapped, `5661` incomplete, and `1` escaped parcel out of `13020` tracked. `v32p14` produced `13007` incomplete and `13` escaped parcels, with no trapped parcels in the captured checkpoint. The higher-loading case is therefore not a resolved increase in carryover; it is dominated by incomplete tracks because the saved carrier field is not sufficiently mature for the larger particles to finish tracking.

## 4. Interpretation

The higher-loading case has higher reported steam-outlet liquid carryover and slightly lower scoped removal/dryness. This is directionally consistent with the intended loading-sensitivity question, but the similar approximately `58.4%` derived imbalance ratio means the comparison is still a diagnostic signal, not a reliable efficiency trend.

## 5. Next action

Continue both cases or save additional checkpoints only after confirming that continuity, phase fraction, whole-domain phase balance, and DPM track completion improve. Do not interpret incomplete tracks as trapped or escaped liquid.

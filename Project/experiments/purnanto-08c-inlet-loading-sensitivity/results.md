> **Retired source:** Setups/reports/purnanto-reference/08c/results.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Preliminary Results Report — Setup 08c

## Setup link and evidence

- Setup definition: [08c-purnanto-parity-inlet-velocity-sensitivity.md](setup.md)
- Historical checkpoints: Fluent server `1`; the 20,000-iteration continuation below was analysed on Fluent server `3`.
- Fluent version: `Ansys Fluent 2024 R2`
- Evidence class: partial diagnostic; the reported states do not have a closed carrier mass balance or converged residual history.
- DPM: six-injection Particle Tracks Summary analysis completed for the historical checkpoints and the continuation; the runs remain partial/nonconverged.

## 1. Earlier family carrier results

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

- v20p00 residual history (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-residuals_20260720_131511.png`; not migrated)
- v32p14 residual history (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-residuals_20260720_131754.png`; not migrated)

Machine-readable post-processing:

- v20p00 summary (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v20p00-summary.json`; not migrated)
- v32p14 summary (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260720/08c-v32p14-summary.json`; not migrated)

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

- v20p00 DPM JSON (historical machine artifact path: `../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-summary.json`; not migrated), CSV (historical machine artifact path: `../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-summary.csv`; not migrated), transcript (historical machine artifact path: `../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v20p00-20260720-dpm-particle-track-transcript.txt`; not migrated)
- v32p14 DPM JSON (historical machine artifact path: `../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-summary.json`; not migrated), CSV (historical machine artifact path: `../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-summary.csv`; not migrated), transcript (historical machine artifact path: `../../../PyAnsys/output/dpm_particle_tracks/20260720-dpm-analysis/08c-v32p14-20260720-dpm-particle-track-transcript.txt`; not migrated)

Across the six injections, the sampled records contain observed escapes at `steamoutlet` alongside raw Fluent `trapped`/`incomplete` categories. Under the simplified Purnanto scope, only observed steam-outlet escape is report-facing; the other categories remain raw bookkeeping and are not blockers. The comparison is still diagnostic because the saved carrier field is not sufficiently mature for a strong loading claim.

## 4. Interpretation

The higher-loading case has higher reported steam-outlet liquid carryover and slightly lower scoped removal/dryness. This is directionally consistent with the intended loading-sensitivity question, but the similar approximately `58.4%` derived imbalance ratio means the comparison is still a diagnostic signal, not a reliable efficiency trend.

## 5. Next action

Continue both cases or save additional checkpoints only after confirming that continuity, residual/monitor stability, iteration maturity, and mesh/convergence evidence improve. Do not relabel incomplete tracks as trapped or escaped liquid; report observed `steamoutlet` escape only.

## 6. 20,000-iteration continuation — `08c-v20p00`

### Scope and case identity

- The already-loaded Fluent case/data on server `3` was analysed read-only; no case or data file was loaded by the analysis script.
- The live inlet pair (`86.18 kg/s` liquid and `60.21 kg/s` vapor) identifies the loaded case as `08c-v20p00`, not `08b`.
- EWF was not analysed, as requested.
- The residual artifact contains a retained window from iterations `15012`–`20000` with `1000` points and `7` monitored curves; it is not a complete residual-history export.

### Carrier flux diagnostic

| Metric | 20,000-iteration value |
|---|---:|
| Liquid inlet | `86.18 kg/s` |
| Vapor inlet | `60.21 kg/s` |
| Steam-outlet liquid | `3.2192137 kg/s` |
| Steam-outlet vapor | `60.681912 kg/s` |
| Scoped steam-line liquid removal | `96.26455%` |
| Steam-outlet dryness | `94.96220%` |
| Derived phase imbalance | `82.4889 kg/s` (`56.3487%`) |

These are scoped steam-outlet diagnostics, not a closed separator mass balance. Relative to the earlier `3088`-iteration checkpoint, the reported steam-outlet liquid is higher (`0.00132696` to `3.2192137 kg/s`) and the scoped removal/dryness are lower (`99.99846%`/`99.99782%` to `96.26455%`/`94.96220%`).

### Residual diagnostic

| Residual | Final value at iteration `20000` |
|---|---:|
| Continuity | `1.1682755` |
| X-velocity | `4.3493e-05` |
| Y-velocity | `5.2734e-05` |
| Z-velocity | `4.2661e-05` |
| `k` | `1.2828e-03` |
| `epsilon` | `4.9524e-03` |
| `vf-phase-2` | `1.8213e-03` |

Continuity remains large at the final retained point, so the 20,000-iteration state is not converged for quantitative acceptance.

### DPM particle-fate diagnostic

Each injection had `2170` tracked parcels. The continuation recorded fate counts only; no per-injection mass-transfer rows were available in the captured Fluent output.

| Diameter | Tracked | Escaped | Trapped | Incomplete |
|---:|---:|---:|---:|---:|
| `5.63 µm` | `2170` | `25` | `0` | `2145` |
| `28.14 µm` | `2170` | `0` | `0` | `2170` |
| `56.27 µm` | `2170` | `0` | `0` | `2170` |
| `112.54 µm` | `2170` | `0` | `0` | `2170` |
| `168.81 µm` | `2170` | `0` | `0` | `2170` |
| `348.88 µm` | `2170` | `0` | `0` | `2170` |

Thus, `25` of `13020` tracked parcels were recorded as escaped and `12995` remained incomplete. This is a count-only diagnostic and must not be converted into a DPM mass-removal or separation-efficiency claim.

### Audit artifacts

The files retain the original analysis run label `08b-20000it-20260727`; the live inlet evidence and this report identify the analysed case as `08c-v20p00`.

- 20,000-iteration carrier flux JSON (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-flux-check.json`; not migrated)
- 20,000-iteration residual JSON (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-residual-check.json`; not migrated)
- 20,000-iteration residual plot (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-residual-check.png`; not migrated)
- 20,000-iteration DPM summary (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-dpm-summary.txt`; not migrated)
- 20,000-iteration DPM JSON (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-dpm-particle-track-summary.json`; not migrated)
- 20,000-iteration DPM CSV (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-dpm-particle-track-summary.csv`; not migrated)
- 20,000-iteration DPM transcript (historical machine artifact path: `../../../PyAnsys/output/post_simulation_analysis/08b-20000it-20260727-dpm-particle-track-transcript.txt`; not migrated)

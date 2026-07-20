# Preliminary Results Report — Setup 08c

## Setup link and evidence

- Setup definition: [08c-purnanto-parity-inlet-velocity-sensitivity.md](../../active/08c-purnanto-parity-inlet-velocity-sensitivity.md)
- Fluent server: `1`
- Fluent version: `Ansys Fluent 2024 R2`
- Evidence class: partial diagnostic; neither run has a closed carrier mass balance or converged residual history.
- DPM: inventory was observed, but no DPM fate analysis was performed.

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

## 3. Interpretation

The higher-loading case has higher reported steam-outlet liquid carryover and slightly lower scoped removal/dryness. This is directionally consistent with the intended loading-sensitivity question, but the similar approximately `58.4%` derived imbalance ratio means the comparison is still a diagnostic signal, not a reliable efficiency trend.

## 4. Next action

Continue both cases or save additional checkpoints only after confirming that continuity, phase fraction, and whole-domain phase balance improve. Do not escalate this comparison to DPM interpretation yet.

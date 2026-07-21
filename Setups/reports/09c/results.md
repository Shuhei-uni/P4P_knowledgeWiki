# Preliminary Results Report — Setup 09c

## Setup link and evidence

- Setup definition: [09c-dpm-ewf-wall-film-reentrainment.md](../../past/archived/09c-dpm-ewf-wall-film-reentrainment.md)
- Case: `TwoPhaseInletV2(Purnanto)-09c-two-way-dpm-coupled.cas.h5`
- Data checkpoint: `TwoPhaseInletV2(Purnanto)-09c-two-way-dpm-coupled-25-921.dat.h5`
- Fluent server: `1`
- Fluent version: `Ansys Fluent 2024 R2`
- Evidence class: partial two-way-coupling diagnostic; not a converged comparison.

## 1. Carrier-field result

| Quantity | Value |
|---|---:|
| Liquid inlet | `116.92 kg/s` |
| Vapor inlet | `80.69 kg/s` |
| Steam-outlet liquid | approximately `3.46e-45 kg/s` |
| Steam-outlet vapor | `81.454153 kg/s` |
| Scoped steam-line liquid removal | `100.00000%` |
| Steam-outlet dryness | `100.00000%` |
| Derived phase imbalance | `116.155847 kg/s` (`58.78%` of inlet) |

The apparent perfect steam-line result is not report-quality because the carrier mass balance is strongly open at this partial checkpoint.

## 2. Residual and stability findings

- Residual monitor export covered `921` iterations.
- Continuity remained around the `10^-1` level and did not converge.
- Epsilon began with a very large startup spike and settled only to approximately the `10^-3` to `10^-2` range.
- Velocity residuals became small, but continuity and phase-fraction residuals remain limiting.

Residual plot: [09c residual history](../../../PyAnsys/output/live_postprocess_20260720/09c-residuals_20260720_132009.png)

Machine-readable post-processing: [09c summary](../../../PyAnsys/output/live_postprocess_20260720/09c-summary.json)

## 3. DPM scope

The case contains six active injections and two-way DPM source feedback, but no particle fate analysis was run. This report therefore addresses only the carrier-field and flux response.

## 4. Conclusion

At this checkpoint, `09c` does not yet establish whether two-way DPM coupling changes the physical conclusion. First obtain a more stable carrier field and a closed-enough phase balance, then compare coupled and one-way cases using the same flux surfaces.

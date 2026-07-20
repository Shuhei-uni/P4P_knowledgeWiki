# Preliminary Results Report — Setup 10a

## Setup link and evidence

- Setup definition: [10a-ewf-deposition.md](../../active/10a-ewf-deposition.md)
- Run case: `10a-25-02000.cas.h5`
- Highest data checkpoint: `10a-25-02805.dat.h5`
- Fluent server: `1`
- Fluent version: `Ansys Fluent 2024 R2`
- Evidence class: partial EWF/splash-sensitive diagnostic; not a clean no-splash 10a control.

## 1. Setup-difference audit

The read-only audit compared the 10a case against the base case under `Base Case Data Set`.

- The candidate contains the expected EWF wall-film additions on `wall` and no EWF film wall on `bottom`.
- The wall film is initialized with zero height and zero velocity.
- Flow momentum coupling is off.
- The impingement model reads as `stanton-rutland`.
- The candidate has `DPM Wall Splash = On` with `4` splashed particles.

That last setting conflicts with the documented no-splash 10a control. The supplied run must therefore be treated as a splash-enabled diagnostic, closer to `10a-splash`, until the case is corrected or the branch identity is clarified.

Audit outputs:

- [10a run-case audit](../../../PyAnsys/output/case_setup_diff/10a-base-case-diff.md)
- [10a EWF case-only audit](../../../PyAnsys/output/case_setup_diff_10a_ewf/10a-base-case-diff.md)

Both artifacts showed the same splash-enabled wall-film state.

## 2. Carrier-field result

| Quantity | Value |
|---|---:|
| Liquid inlet | `116.92 kg/s` |
| Vapor inlet | `80.69 kg/s` |
| Steam-outlet liquid | `0.0001959642 kg/s` |
| Steam-outlet vapor | `81.452089 kg/s` |
| Scoped steam-line liquid removal | `99.99983%` |
| Steam-outlet dryness | `99.99976%` |
| Derived phase imbalance | `116.157715 kg/s` (`58.78%` of inlet) |

These values are only a scoped carrier diagnostic. They do not demonstrate bounded film inventory, conserved DPM-to-film transfer, or validated splash behaviour.

## 3. Residual and stability findings

- Residual monitor export covered approximately `2805` iterations.
- Continuity remained around the `10^-1` level and did not converge.
- Epsilon showed intermittent spikes while declining overall.
- Velocity residuals became small, but continuity and phase-fraction residuals remain limiting.

Residual plot: [10a residual history](../../../PyAnsys/output/live_postprocess_20260720/10a-residuals_20260720_132227.png)

Machine-readable post-processing: [10a summary](../../../PyAnsys/output/live_postprocess_20260720/10a-summary.json)

## 4. Deferred analysis

No DPM fate, splashed-mass, or DPM-to-film transfer analysis was performed. Film inventory and wall-zone drainage should be analysed only after the intended no-splash/splash branch identity is resolved.

## 5. Next action

Do not use this run as the no-splash `10a` reference. Either relabel it as a splash-enabled diagnostic or create a corrected 10a case with `DPM Wall Splash = Off` before making a no-splash comparison.

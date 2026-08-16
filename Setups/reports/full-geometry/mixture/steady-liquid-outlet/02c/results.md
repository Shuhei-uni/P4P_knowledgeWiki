# Results Report — Setup 02c, Unprimed Brine-Outlet Pressure Screen (Cases A–H)

## Comparison dashboard (early screening)

This report is arranged for side-by-side comparison first, with the detailed per-case evidence retained below. The A–G points are the earlier directional screen; current scope adds only the single H point at `1.140 MPa`. The former upper-pressure H20–H50 and I20–I160 sweeps are superseded and are not part of the active matrix. Results are not a converged separator-performance study. Values are the recorded endpoint after Hybrid Initialization plus the stated steady-iteration budget; outlet flows are shown as outward-positive magnitudes. Because this simplified geometry intentionally omits the lower-liquid outlet, phase closure and liquid-routing values are diagnostic only.

### Sweep definition

| Case | Brine-outlet gauge pressure [MPa] | Steam-outlet gauge pressure [MPa] | ΔP(brine − steam) [kPa] | Endpoint |
|---|---:|---:|---:|---:|
| A | 1.1150 | 1.1200 | −5.0 | iter 649 |
| B | 1.1200 | 1.1200 | 0.0 | iter 500 |
| D | 1.1225 | 1.1200 | +2.5 | iter 500 |
| C | 1.1250 | 1.1200 | +5.0 | iter 500 |
| E | 1.1275 | 1.1200 | +7.5 | iter 500 |
| F | 1.1300 | 1.1200 | +10.0 | iter 500 |
| G | 1.1350 | 1.1200 | +15.0 | iter 500 |
| H | 1.1400 | 1.1200 | +20.0 | iter 500 |

### Primary phase-routing comparison

| Case | P_brine [MPa] | ΔP [kPa] | Liquid → brine [kg/s] | Liquid → steam [kg/s] | Liquid brine / liquid inlet | Vapour → brine [kg/s] | Vapour → steam [kg/s] | Vapour wrong-outlet fraction (of vapour inlet) | Screening classification |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A | 1.1150 | −5.0 | 45.799 | 0.000020 | 39.20% | 49.294 | 32.794 | 60.38% | early diagnostic |
| B | 1.1200 | 0.0 | 6.921 | 0.000001 | 5.92% | 42.547 | 39.823 | 52.12% | early diagnostic |
| D | 1.1225 | +2.5 | 25.966 | 0.000001 | 22.22% | 38.127 | 44.084 | 46.70% | positive-backpressure direction; unresolved |
| C | 1.1250 | +5.0 | 136.605 | 0.000009 | 116.91%* | 26.744 | 54.828 | 32.76% | inventory-draining / unresolved* |
| E | 1.1275 | +7.5 | 258.323 | 0.000005 | 221.08%* | 19.821 | 60.957 | 24.28% | inventory-draining / unresolved* |
| F | 1.1300 | +10.0 | 440.922 | 0.000391 | 377.35%* | 13.346 | 66.192 | 16.35% | inventory-draining / unresolved* |
| G | 1.1350 | +15.0 | 228.106 | 0.032864 | 195.22%* | 9.211 | 71.647 | 11.28% | inventory-draining / unresolved* |
| H | 1.1400 | +20.0 | 616.795† | 0.281021 | 527.87%† | 0.000 | 86.299 | 0.00% | unstable / indeterminate† |

*Cases C, E, F, and G have liquid outflow above the liquid inlet at the recorded endpoint; this is an open transient/inventory signal, not recovery above 100%.

†For H, Fluent's positive raw brine-outlet liquid flow means reverse flow into the domain. The table shows the absolute magnitude for side-by-side screening, not a positive liquid-recovery result; the endpoint is classified as unstable/indeterminate.

The vapour fractions in this dashboard use the fixed incoming vapour flow (`81.639506 kg/s`) as the denominator, so the two outlet fractions need not sum to exactly 100% while the phase balance is open.

### Numerical-health comparison

| Case | Iterations | Final continuity | Minimum continuity | Residual-history points | Common-window / convergence status |
|---|---:|---:|---:|---:|---|
| A | 649 | 1.265e−1 | 7.966e−2 | 649 | not converged |
| B | 500 | 1.239e−1 | 1.135e−1 | 500 | not converged |
| D | 500 | 1.021e−1 | 9.563e−2 | 500 | not converged |
| C | 500 | 1.194e−1 | 1.121e−1 | 500 | not converged |
| E | 500 | 8.959e−2 | 8.934e−2 | 500 | not converged |
| F | 500 | 1.117e−1 | 1.116e−1 | 500 | not converged |
| G | 500 | 8.243e−2 | 8.241e−2 | 500 | not converged |
| H | 500 | 2.289e−1 | 1.333e−1 | 500 | unstable / indeterminate; severe reverse-flow/viscosity-limit diagnostics |

### Reading the sweep

- **Measured direction:** A → C already shows a strong shift in the recorded endpoint routing: higher brine backpressure coincides with less vapour through the brine outlet and more vapour through the steam outlet.
- **Screening hypothesis:** a small positive brine-over-steam pressure difference is therefore worth testing as a control variable for phase routing and possible liquid drainage.
- **What D–G add:** the +2.5 to +15 kPa points locate whether that directional shift continues, flattens, or crosses into restricted liquid drainage.
- **What H adds:** at `1.140 MPa` (`+20 kPa` relative to the fixed `1.120 MPa` steam outlet), the Student-surrogate endpoint reports zero vapour through the brine outlet but strong reverse liquid flow at that outlet; this is a diagnostic boundary case, not evidence of a usable pressure.
- **Interpretation boundary:** no point is a selected operating pressure or efficiency result until a common stable/converged window, liquid-inventory history, and the agreed visual/pressure diagnostics are available.

Detailed per-case evidence and artifact links follow below. The D–G and H rows above are populated from verified endpoint post-processing; H uses the separate Student-surrogate lineage explicitly identified below.

## 1. Setup link and evidence

- Setup definition: [02c — Mixture brine-outlet pressure sensitivity, unprimed](../../active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md)
- Case: `02c-B`, brine-outlet gauge pressure `1.120 MPa`
- Verified checkpoint: `02c-B-brine-p1120kpa-unprimed-iter500-20260812T045447Z.cas.h5` with matching `.dat.h5`
- Fluent version: Ansys Fluent 2025 R2
- Run state: Hybrid Initialization followed by `500` steady iterations; no liquid patch was applied
- Evidence class: early numerical diagnostic; not converged and not a separator-performance result

Generated evidence:

- [carrier flux extraction](../../../PyAnsys/output/post_simulation_analysis/02c-B-brine-p1120kpa-unprimed-iter500-flux-check.json)
- [residual history](../../../PyAnsys/output/post_simulation_analysis/02c-B-brine-p1120kpa-unprimed-iter500-residual-check.json) and [plot](../../../PyAnsys/output/post_simulation_analysis/02c-B-brine-p1120kpa-unprimed-iter500-residual-check.png)
- [configuration audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-B-iter500-audit/model_audit.json)
- [complete DPM output bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-B-iter500-dpm/raw_results.json), including [per-injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-B-iter500-dpm/dpm_injection_summary.csv) and [zone fate rows](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-B-iter500-dpm/dpm_zone_summary.csv)

## 2. Analysis applicability

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed | explicit Case B checkpoint was reloaded and analysed |
| DPM fate analysis | completed | six active inherited surface injections were present, so the complete required sweep was captured |
| EWF audit / snapshot | EWF not applicable | audit found EWF disabled and no active film wall |
| EWF history / closure | not applicable | no Eulerian Wall Film model was active |
| Splash, stripping, edge separation | not applicable | mechanisms unavailable with EWF inactive |

## 3. Carrier-field result at iteration 500

### Measured phase mass flows

Fluent reported inward flow as positive and outward flow as negative. The table converts the outlet values to outward-positive magnitudes for comparison.

| Quantity | Raw Fluent flow [kg/s] | Outward-positive / inlet value [kg/s] |
|---|---:|---:|
| Liquid at liquid inlet | `116.847094` | `116.847094` in |
| Liquid at brine outlet | `-6.921014` | `6.921014` out |
| Liquid at steam outlet | `-7.779685e-7` | `7.779685e-7` out |
| Vapour at steam inlet | `81.639506` | `81.639506` in |
| Vapour at brine outlet | `-42.547417` | `42.547417` out |
| Vapour at steam outlet | `-39.823439` | `39.823439` out |

### Derived screening metrics

| Metric | Value | Interpretation limit |
|---|---:|---|
| Liquid closure error | `0.940769` (`94.08%`) | liquid drainage is far below inlet flow at this early checkpoint |
| Liquid brine-recovery fraction | `0.059231` (`5.92%`) | not a converged drainage fraction |
| Steam wrong-outlet fraction | `0.521162` (`52.12%`) | more than half of the incoming vapour leaves through the brine outlet at this checkpoint |
| Vapour fraction leaving steam outlet | `0.487796` (`48.78%`) | complement is not exact because the vapour phase remains unclosed by `0.731349 kg/s` |
| Steam-outlet liquid carryover | `7.779685e-7 kg/s` | small only because the field is not yet a valid two-outlet steady state |

The Case B objective was not demonstrated at iteration 500: the brine outlet is not yet carrying most of the incoming liquid, while the vapour short-circuit through it is large. This is an observation from the specified checkpoint, not evidence that the `1.120 MPa` pressure is intrinsically unsuitable after a mature solution.

### Residual state

The residual history contains 500 points, iterations `1–500`.

| Equation | Initial | Final | Minimum over run |
|---|---:|---:|---:|
| Continuity | `1.000000` | `1.239373e-1` | `1.135326e-1` |
| x velocity | `1.080760e-3` | `2.575407e-5` | `2.575407e-5` |
| y velocity | `7.284543e-4` | `2.688511e-5` | `2.688511e-5` |
| z velocity | `1.219977e-3` | `2.499069e-5` | `2.499069e-5` |
| k | `8.270402e-1` | `1.167529e-3` | `1.167529e-3` |
| epsilon | `8.940388e3` | `5.747842e-3` | `4.485275e-3` |
| liquid volume fraction | `1.325983e-1` | `1.795970e-3` | `1.725008e-3` |

Momentum residuals decreased substantially, but continuity remains approximately three orders of magnitude above its configured `1e-4` criterion and the physical phase balances are still open. The carrier result is therefore **not converged**.

## 4. Inherited DPM diagnostic

The audit found six active inherited inert-particle surface injections. DPM coupling was off, so this sweep does not change the carrier field, but it is retained because it was active in the checkpoint.

| Diameter [µm] | Injection | Tracked | Escaped at steam outlet | Incomplete | Reported terminal flow [kg/s] |
|---:|---|---:|---:|---:|---:|
| `5.63` | `injection-5-micron` | 874 | 874 | 0 | `0.1900` |
| `28.14` | `injection-28-micron` | 874 | 874 | 0 | `0.7800` |
| `56.27` | `injection-56-micron` | 874 | 874 | 0 | `0.9700` |
| `112.54` | `injection-112-micron` | 874 | 865 | 9 | `1.95008` |
| `168.81` | `injection-168-micron` | 874 | 859 | 15 | `1.95047` |
| `348.88` | `injection-348-micron` | 874 | 848 | 26 | `23.3755` |

All six transcript-completion gates passed. The injected surfaces read back as `steam-outlet`, which is an inherited configuration fact and an important scope caveat: these trajectories do not test droplet release from the intended steam inlet or liquid inlet. They must not be used as an independent measure of the Case B brine-drainage performance.

## 5. Interpretation and next action

**Measured:** the 500-iteration checkpoint, phase fluxes, residual history, audit, and complete DPM transcript bundle.

**Derived:** Case B has `94.08%` liquid closure error and `52.12%` vapour wrong-outlet fraction at its iteration-500 screen.

**Unresolved:** whether a later stable window changes these values; the tangential-pipe pressure sampling locations, total liquid inventory history, and required contour/vector evidence were not instrumented before this first screen. The inherited DPM payload and its `steam-outlet` release surfaces also require a separate decision before it is interpreted as part of this study.

## 6. Case A lower-pressure screen at 1.115 MPa (iteration 649)

### Setup link and evidence

- Case: `02c-A`, brine-outlet gauge pressure `1.115 MPa`; steam-outlet gauge pressure remained `1.120 MPa`.
- Explicitly loaded checkpoint: `02c-A-brine-p1115kpa-unprimed-iter649-20260812T051900Z.cas.h5` with matching `.dat.h5`.
- Fluent version: Ansys Fluent 2025 R2.
- Evidence class: preliminary numerical diagnostic; the requested 500-iteration milestone was exceeded and the final checkpoint contains `649` residual-history points. It is not converged and is not a separator-performance result.

Generated evidence:

- [carrier flux extraction](../../../PyAnsys/output/post_simulation_analysis/02c-A-brine-p1115kpa-unprimed-iter649-flux-check.json)
- [residual history](../../../PyAnsys/output/post_simulation_analysis/02c-A-brine-p1115kpa-unprimed-iter649-residual-check.json) and [plot](../../../PyAnsys/output/post_simulation_analysis/02c-A-brine-p1115kpa-unprimed-iter649-residual-check.png)
- [configuration audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-A-iter649-audit/model_audit.json)
- [complete DPM output bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-A-iter649-dpm/raw_results.json), including [per-injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-A-iter649-dpm/dpm_injection_summary.csv), [zone fate rows](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-A-iter649-dpm/dpm_zone_summary.csv), and the [full transcript](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-A-iter649-dpm/dpm_particle_track_transcript.txt).

### Analysis applicability

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed | explicitly loaded Case A checkpoint was analysed |
| DPM fate analysis | completed | six active inherited surface injections were present; all transcript-completion gates passed |
| EWF audit / snapshot | EWF not applicable | audit found EWF disabled and no active film walls |
| EWF history / closure | not applicable | no Eulerian Wall Film model was active |
| Splash, stripping, edge separation | not applicable | EWF inactive; no active film mechanism was found |

### Measured phase mass flows

Fluent reported inward flow as positive and outward flow as negative. Outlet values below are converted to outward-positive magnitudes.

| Quantity | Raw Fluent flow [kg/s] | Outward-positive / inlet value [kg/s] |
|---|---:|---:|
| Liquid at liquid inlet | `116.847094` | `116.847094` in |
| Liquid at brine outlet | `-45.799051` | `45.799051` out |
| Liquid at steam outlet | `-2.008474e-5` | `2.008474e-5` out |
| Vapour at steam inlet | `81.639506` | `81.639506` in |
| Vapour at brine outlet | `-49.294436` | `49.294436` out |
| Vapour at steam outlet | `-32.793685` | `32.793685` out |

### Derived screening metrics and comparison with Case B

| Metric | Case A, `1.115 MPa` / iter 649 | Case B, `1.120 MPa` / iter 500 | Interpretation limit |
|---|---:|---:|---|
| Liquid closure error | `0.608043` (`60.80%`) | `0.940769` (`94.08%`) | both liquid balances remain open; values are not steady drainage fractions |
| Liquid brine-recovery fraction | `0.391957` (`39.20%`) | `0.059231` (`5.92%`) | higher for Case A at unequal iteration counts and without a stable window |
| Vapour wrong-outlet fraction (brine outlet) | `0.603806` (`60.38%`) | `0.521162` (`52.12%`) | higher for Case A; not a converged separation metric |
| Vapour fraction leaving steam outlet | `0.401689` (`40.17%`) | `0.487796` (`48.78%`) | the Case A vapour balance closes to within `0.55%`; Case B remained more open |
| Liquid at steam outlet | `2.008474e-5 kg/s` | `7.779685e-7 kg/s` | a scoped outlet value only, not full separator validation |

**Measured:** at this checkpoint, reducing brine pressure from `1.120` to `1.115 MPa` coincides with substantially more liquid leaving through the brine outlet (`45.799051 kg/s` versus `6.921014 kg/s`) and more vapour leaving through the brine outlet (`49.294436 kg/s` versus `42.547417 kg/s`).

**Derived:** the lower-pressure screen improves the observed liquid brine-recovery fraction by `33.27` percentage points relative to Case B, but worsens the observed vapour wrong-outlet fraction by `8.26` percentage points. Neither direction supports selecting a pressure because Case A and B are both non-converged, are at different final iteration counts, and lack a common stable window.

### Residual state

The Case A residual history contains 649 points, iterations `1–649`.

| Equation | Initial | Final | Minimum over run |
|---|---:|---:|---:|
| Continuity | `1.000000` | `1.265345e-1` | `7.966281e-2` |
| x velocity | `1.080760e-3` | `4.771068e-5` | `2.074424e-5` |
| y velocity | `7.284543e-4` | `6.136807e-5` | `2.011115e-5` |
| z velocity | `1.219977e-3` | `5.589449e-5` | `2.080359e-5` |
| k | `8.270402e-1` | `2.094519e-3` | `9.426436e-4` |
| epsilon | `8.940388e3` | `6.148259e-3` | `3.743591e-3` |
| liquid volume fraction | `1.325983e-1` | `1.103022e-2` | `1.551960e-3` |

Momentum residuals fell substantially, but continuity rose from its best value and finished at `1.265345e-1`, far above the configured `1e-4` criterion. The carrier result is therefore **not converged**.

### Inherited DPM diagnostic

The Case A audit found the same six inherited inert-particle surface injections as Case B, with carrier coupling off. All six DPM transcript-completion gates passed. All injected surfaces were `steam-outlet`; consequently, the fates below are retained as inherited-configuration diagnostics, not as droplet-release or brine-drainage evidence.

| Diameter [µm] | Injection | Tracked | Escaped at steam outlet | Incomplete | Net injection flow [kg/s] |
|---:|---|---:|---:|---:|---:|
| `5.63` | `injection-5-micron` | 874 | 873 | 1 | `0.1900` |
| `28.14` | `injection-28-micron` | 874 | 865 | 9 | `0.7800` |
| `56.27` | `injection-56-micron` | 874 | 852 | 22 | `0.9700` |
| `112.54` | `injection-112-micron` | 874 | 847 | 27 | `1.9500` |
| `168.81` | `injection-168-micron` | 874 | 856 | 18 | `1.9500` |
| `348.88` | `injection-348-micron` | 874 | 866 | 8 | `23.3800` |

Reported DPM terminal-flow closure residuals are within the printed-summary precision (absolute values from `1.74e-5` to `4.00e-3 kg/s`; maximum relative magnitude `1.71e-4`). The DPM output bundle is complete, but it must not be used as an independent acceptance metric for this pressure point because its source surface is inherited as `steam-outlet`.

## 7. Interpretation and next action

**Measured:** explicit Case A case/data reload, phase fluxes, 649-point residual history, EWF/DPM audit, and full six-injection DPM bundle.

**Derived:** Case A's preliminary field has more liquid drained to the brine outlet but more vapour short-circuit to that same outlet than Case B. The relative changes are descriptive only.

**Unresolved:** a common converged/stable window, liquid-inventory history, tangential-pipe pressure diagnostics, and visual field diagnostics have not been captured. EWF is inactive. DPM trajectories are inherited from the steam-outlet release surface and therefore do not test the intended phase-inlet release physics.

Smallest justified next action: build and analyse Case C (`1.125 MPa`) from the same frozen pre-initialization parent using an explicitly defined common convergence/stopping gate, then compare A/B/C only as an early-screening matrix unless a stable window is obtained.

## 8. Case C higher-pressure screen at 1.125 MPa (iteration 500)

### Setup link and evidence

- Case: `02c-C`, brine-outlet gauge pressure `1.125 MPa`; steam-outlet gauge pressure remained `1.120 MPa`.
- Case/data identity basis: the paired Case C `iter500` checkpoint was written and verified immediately after the native Fluent TUI run. The user then confirmed that this case/data state remained loaded for direct analysis.
- Fluent version: Ansys Fluent 2025 R2.
- Evidence class: early numerical diagnostic; exactly `500` residual-history points are available. It is not converged and is not a separator-performance result.

Generated evidence:

- [carrier flux extraction](../../../PyAnsys/output/post_simulation_analysis/02c-C-brine-p1125kpa-unprimed-iter500-flux-check.json)
- [residual history](../../../PyAnsys/output/post_simulation_analysis/02c-C-brine-p1125kpa-unprimed-iter500-residual-check.json) and [plot](../../../PyAnsys/output/post_simulation_analysis/02c-C-brine-p1125kpa-unprimed-iter500-residual-check.png)
- [configuration audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-C-iter500-audit/model_audit.json)
- [complete DPM output bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-C-iter500-dpm/raw_results.json), [per-injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-C-iter500-dpm/dpm_injection_summary.csv), [zone fate rows](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-C-iter500-dpm/dpm_zone_summary.csv), and [full transcript](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-C-iter500-dpm/dpm_particle_track_transcript.txt).

### Analysis applicability

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed | direct analysis of the user-confirmed retained Case C session |
| DPM fate analysis | completed | six active inherited surface injections were present; all transcript-completion gates passed |
| EWF audit / snapshot | EWF not applicable | audit found EWF disabled and no active film wall |
| EWF history / closure | not applicable | no Eulerian Wall Film model was active |
| Splash, stripping, edge separation | not applicable | EWF inactive; no active film mechanism was found |

### Measured phase mass flows

Fluent reported inward flow as positive and outward flow as negative. Outlet values below are converted to outward-positive magnitudes.

| Quantity | Raw Fluent flow [kg/s] | Outward-positive / inlet value [kg/s] |
|---|---:|---:|
| Liquid at liquid inlet | `116.847094` | `116.847094` in |
| Liquid at brine outlet | `-136.604543` | `136.604543` out |
| Liquid at steam outlet | `-8.928871e-6` | `8.928871e-6` out |
| Vapour at steam inlet | `81.639506` | `81.639506` in |
| Vapour at brine outlet | `-26.743944` | `26.743944` out |
| Vapour at steam outlet | `-54.827687` | `54.827687` out |

### Derived screening metrics and A/B/C comparison

| Metric | Case A, `1.115 MPa` / iter 649 | Case B, `1.120 MPa` / iter 500 | Case C, `1.125 MPa` / iter 500 | Interpretation limit |
|---|---:|---:|---:|---|
| Liquid closure error | `60.80%` | `94.08%` | `16.91%` | all are early, unsteady/non-converged screens; Case C has liquid outflow exceeding inlet |
| Liquid brine-recovery fraction | `39.20%` | `5.92%` | `116.91%` | Case C is physically unclosed at this checkpoint; do not read this as recovery above 100% |
| Vapour wrong-outlet fraction (brine outlet) | `60.38%` | `52.12%` | `32.76%` | lower for Case C at the recorded early screen |
| Vapour fraction leaving steam outlet | `40.17%` | `48.78%` | `67.16%` | Case C vapour balance closes to within `0.083%` |
| Liquid at steam outlet | `2.008474e-5 kg/s` | `7.779685e-7 kg/s` | `8.928871e-6 kg/s` | scoped outlet value only, not full separator validation |

**Measured:** at this Case C checkpoint, `136.604543 kg/s` liquid leaves the brine outlet while only `116.847094 kg/s` enters through the liquid inlet; `54.827687 kg/s` vapour leaves the steam outlet and `26.743944 kg/s` leaves the brine outlet.

**Derived:** compared with the A/B early screens, the higher-pressure Case C has the lowest observed vapour wrong-outlet fraction and the highest observed vapour steam-outlet fraction. It also has a liquid brine-outlet flow greater than liquid inlet, so its smaller liquid closure error (`16.91%`) is still an open balance—not a valid high recovery result. Therefore A/B/C may not be pressure-ranked from these checkpoints.

### Residual state

The Case C residual history contains 500 points, iterations `1–500`.

| Equation | Initial | Final | Minimum over run |
|---|---:|---:|---:|
| Continuity | `1.000000` | `1.194315e-1` | `1.120839e-1` |
| x velocity | `1.080760e-3` | `5.868121e-5` | `5.671169e-5` |
| y velocity | `7.284543e-4` | `5.996074e-5` | `5.373275e-5` |
| z velocity | `1.219977e-3` | `6.325916e-5` | `5.657353e-5` |
| k | `8.270402e-1` | `2.530846e-3` | `2.021561e-3` |
| epsilon | `8.940388e3` | `8.728362e-3` | `6.562048e-3` |
| liquid volume fraction | `1.325983e-1` | `9.264018e-3` | `8.077433e-3` |

Momentum residuals decreased substantially, but continuity remains about three orders of magnitude above the configured `1e-4` criterion and rose from its minimum before the endpoint. The Case C carrier result is therefore **not converged**.

### Inherited DPM diagnostic

The audit found the same six inherited inert-particle surface injections, with carrier coupling off. All six DPM transcript-completion gates passed. The source surface for every injection was `steam-outlet`; therefore these results are retained as inherited configuration diagnostics, not as droplet-release or brine-drainage evidence.

| Diameter [µm] | Injection | Tracked | Escaped at steam outlet | Incomplete | Net injection flow [kg/s] |
|---:|---|---:|---:|---:|---:|
| `5.63` | `injection-5-micron` | 874 | 874 | 0 | `0.1900` |
| `28.14` | `injection-28-micron` | 874 | 874 | 0 | `0.7800` |
| `56.27` | `injection-56-micron` | 874 | 874 | 0 | `0.9700` |
| `112.54` | `injection-112-micron` | 874 | 848 | 26 | `1.9500` |
| `168.81` | `injection-168-micron` | 874 | 836 | 38 | `1.9500` |
| `348.88` | `injection-348-micron` | 874 | 817 | 57 | `23.3800` |

For the three small injections, Fluent printed only a single escaped mass-transfer row; a separate terminal-flow closure residual is therefore not available from that printed summary. For the remaining injections, reported closure residual magnitudes are within printed-summary precision (`1.0e-5` to `5.0e-3 kg/s`, with maximum relative magnitude `2.14e-4`). This operationally complete DPM bundle must not be used as an independent pressure-selection metric because of the inherited `steam-outlet` source surface.

## 9. Matrix interpretation and next action

**Measured:** direct Case C live-session carrier/residual extraction, model audit, and full six-injection DPM output; complete A/B/C/D/E/F/G phase-flux screens now exist.

**Derived:** at their respective early checkpoints, the brine-pressure increase from A to C coincides with lower observed vapour wrong-outlet fraction (`60.38%` → `32.76%`) and higher observed vapour steam-outlet fraction (`40.17%` → `67.16%`). The liquid metrics are not comparable recovery outcomes because all fields remain open and Case C liquid outflow exceeds inlet.

**Unresolved:** none of the three checkpoints supplies a common converged/stable window, liquid-inventory history, tangential-pipe pressure diagnostics, or visual field evidence. Case A also has a different final iteration count. The active inherited DPM branch releases from the steam outlet, not an intended inlet.

Smallest justified next action: define a common convergence/stability gate with total liquid-inventory and outlet-flow monitors, then continue only the bracket-adjacent points (starting with D) from their frozen pre-initialization parents. Use the full A–G matrix as directional evidence only until a common stable window is obtained.

## 10. Cases D–G higher-pressure post-processing

Cases D–G were explicitly reloaded from their paired remote `.cas.h5`/`.dat.h5` endpoints and processed with the same carrier-flux, residual-history, EWF/DPM audit, and six-injection DPM transcript workflow used for A–C. Each has 500 residual-history points. The inherited DPM branch is unchanged across the sweep: six inert surface injections, carrier coupling off, and every injection source reported as `steam-outlet`. These trajectories are therefore configuration diagnostics, not pressure-selection evidence.

### Case D — 1.1225 MPa brine outlet, +2.5 kPa relative to steam

Measured endpoint phase flows: liquid brine `25.965839 kg/s`, liquid steam `1.072079e-6 kg/s`, vapour brine `38.126893 kg/s`, and vapour steam `44.084141 kg/s`. Relative to the liquid inlet, the observed brine liquid fraction is `22.22%`; relative to the vapour inlet, the observed brine-outlet vapour fraction is `46.70%` and steam-outlet vapour fraction is `54.00%`. Continuity finished at `1.021147e-1` (minimum `9.563220e-2`), so the field is not converged. D is the first positive-backpressure point and shows the expected directional shift versus B, but the liquid-routing state remains unresolved.

Post-processing artifacts: [flux JSON](../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-flux-check.json), [residual JSON](../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-residual-check.json), [residual plot](../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-residual-check.png), [model audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-D-iter500-dpm/model_audit.json), and [DPM bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-D-iter500-dpm/raw_results.json) with [injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-D-iter500-dpm/dpm_injection_summary.csv) and [zone summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-D-iter500-dpm/dpm_zone_summary.csv).

### Case E — 1.1275 MPa brine outlet, +7.5 kPa relative to steam

Measured endpoint phase flows: liquid brine `258.322717 kg/s`, liquid steam `4.557397e-6 kg/s`, vapour brine `19.821113 kg/s`, and vapour steam `60.957303 kg/s`. The liquid brine flow is `221.08%` of the liquid inlet, which is an open inventory signal rather than recovery. Vapour routing is `24.28%` to the brine outlet and `74.67%` to the steam outlet relative to the vapour inlet. Continuity finished at `8.959052e-2` (minimum `8.933988e-2`), still far above the configured convergence criterion. Classify E as inventory-draining / unresolved; do not call it liquid-drainage restriction without liquid-inventory history.

Post-processing artifacts: [flux JSON](../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-flux-check.json), [residual JSON](../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-residual-check.json), [residual plot](../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-residual-check.png), [model audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-E-iter500-dpm/model_audit.json), and [DPM bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-E-iter500-dpm/raw_results.json) with [injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-E-iter500-dpm/dpm_injection_summary.csv) and [zone summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-E-iter500-dpm/dpm_zone_summary.csv).

### Case F — 1.1300 MPa brine outlet, +10.0 kPa relative to steam

Measured endpoint phase flows: liquid brine `440.922326 kg/s`, liquid steam `3.911503e-4 kg/s`, vapour brine `13.346016 kg/s`, and vapour steam `66.191977 kg/s`. The liquid brine flow is `377.35%` of the liquid inlet and therefore indicates a strongly open, inventory-dominated endpoint. Vapour routing is `16.35%` to the brine outlet and `81.08%` to the steam outlet relative to the vapour inlet. Continuity finished at `1.117432e-1` (minimum `1.115639e-1`), not converged; Fluent also reported turbulent-viscosity limiting in `1115` cells during reload. Classify F as inventory-draining / unresolved and retain the reload warning as a numerical-health caveat.

Post-processing artifacts: [flux JSON](../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-flux-check.json), [residual JSON](../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-residual-check.json), [residual plot](../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-residual-check.png), [model audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-F-iter500-dpm/model_audit.json), and [DPM bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-F-iter500-dpm/raw_results.json) with [injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-F-iter500-dpm/dpm_injection_summary.csv) and [zone summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-F-iter500-dpm/dpm_zone_summary.csv).

### Case G — 1.1350 MPa brine outlet, +15.0 kPa relative to steam

Measured endpoint phase flows: liquid brine `228.105695 kg/s`, liquid steam `3.286418e-2 kg/s`, vapour brine `9.211118 kg/s`, and vapour steam `71.646923 kg/s`. The liquid brine flow is `195.22%` of the liquid inlet. Vapour routing is `11.28%` to the brine outlet and `87.76%` to the steam outlet relative to the vapour inlet. Continuity finished at `8.242718e-2` (minimum `8.240676e-2`), not converged; Fluent reported turbulent-viscosity limiting in `53` cells during reload. Classify G as inventory-draining / unresolved. The vapour-routing direction continues to strengthen, but no claim about a useful operating point follows from this open endpoint.

Post-processing artifacts: [flux JSON](../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-flux-check.json), [residual JSON](../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-residual-check.json), [residual plot](../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-residual-check.png), [model audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-G-iter500-dpm/model_audit.json), and [DPM bundle](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-G-iter500-dpm/raw_results.json) with [injection summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-G-iter500-dpm/dpm_injection_summary.csv) and [zone summary](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-G-iter500-dpm/dpm_zone_summary.csv).

### D–G matrix interpretation

**Measured:** increasing brine backpressure from `+2.5` to `+15 kPa` reduces the recorded vapour flow through the brine outlet (`38.127` → `9.211 kg/s`, `46.70%` → `11.28%` of vapour inlet) and increases the recorded vapour flow through the steam outlet (`44.084` → `71.647 kg/s`, `54.00%` → `87.76%`). This is a clear directional screening signal.

**Derived:** the positive-backpressure hypothesis is supported directionally across D–G for vapour routing. D is the most useful bracket-adjacent candidate because it shows the shift while its liquid brine flow remains below the liquid inlet. E–G show increasingly large liquid-outlet excesses at the recorded endpoint, so they are inventory-draining / unresolved rather than demonstrated drainage-restricted equilibria.

**Unresolved:** no D–G case has a common stable/converged window, total liquid-inventory history, lower-vessel/pipe-entry pressure history, or the agreed contour/vector evidence. The pressure scan locates a promising routing direction and suggests that the liquid-drainage limit lies somewhere between D and the higher points, but it does not identify the limit numerically.

## 11. Case H — 1.1400 MPa brine outlet, Student surrogate (iteration 500)

### Setup and execution evidence

- Setup link: [02c active setup](../../../../../active/02c-mixture-brine-outlet-pressure-sensitivity-unprimed.md).
- Case ID: `02c-H`.
- Brine outlet gauge pressure: `1.140 MPa` (`1,140,000 Pa`).
- Steam outlet gauge pressure: `1.120 MPa` (`1,120,000 Pa`).
- Explicit Student parent: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\02c-C-brine-p1125kpa-unprimed-preinit-20260815T231711Z.cas.h5`.
- Verified pre-initialization child: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\02c-H-brine-p1140kpa-unprimed-student-preinit-20260816T091723Z.cas.h5`.
- Verified endpoint pair: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Test case\02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z.cas.h5` and matching `.dat.h5`.
- Fluent version: Ansys Fluent 2025 R2 Student.
- Mesh readback: `661,558` mixed cells and `1,648,866` nodes.
- Boundary/model readback: split velocity inlets at `27.118 m/s` with `1.140 MPa` initial gauge reference; Mixture; RNG k-epsilon; Energy off; steam outlet pressure outlet at `1.120 MPa`; brine outlet pressure outlet at `1.140 MPa`; liquid backflow volume fraction `1.0`.
- Run protocol: Fluent-native Hybrid Initialization without a liquid patch, followed by one native `500`-iteration solve and paired case/data write. No Python iteration loop was used.
- Evidence class: Student mesh-derived surrogate diagnostic. The Student mesh is not certified as exact server-2/production 02c mesh parity, so this result must not be merged into a professional/server-2 pressure ranking.

### Measured phase mass flows

The read-only endpoint extraction used Fluent phase-1 as vapour and phase-2 as liquid, with outward-positive magnitudes at outlets.

| Quantity | Raw Fluent flow [kg/s] | Outward-positive / inlet value [kg/s] |
|---|---:|---:|
| Liquid at liquid inlet | `116.846776` | `116.846776` in |
| Liquid at brine outlet | `+616.795402` | `-616.795402` outward-positive signed flow (reverse flow into domain) |
| Liquid at steam outlet | `-0.281021` | `0.281021` out |
| Vapour at steam inlet | `81.639504` | `81.639504` in |
| Vapour at brine outlet | `-0.000000` | `0.000000` out |
| Vapour at steam outlet | `-86.298717` | `86.298717` out |

The positive Fluent brine-outlet liquid value is reverse flow into the domain, not liquid leaving through the brine outlet. The absolute magnitude is retained for comparison only; it is not a physical recovery fraction. The reported phase-specific net values also show a whole-domain mixture imbalance of `111.906543 kg/s` (`56.38%` of the extracted mixture inlet basis), retained as informational only because this simplified geometry has no modelled lower-liquid outlet.

### Derived screening metrics

| Metric | H endpoint value | Interpretation limit |
|---|---:|---|
| Absolute brine liquid flux / liquid inlet | `527.87%` | reverse-flow magnitude; not recovery above 100% |
| Liquid closure error | `428.11%` | phase closure is not acceptable for a steady result |
| Vapour wrong-outlet fraction | `0.00%` | endpoint routing signal only; not a converged separation result |
| Vapour leaving steam outlet / vapour inlet | `105.71%` | open vapour balance; not recovery |
| Final continuity residual | `2.288839e-1` | not converged; configured criterion is `1e-4` |
| Minimum continuity residual | `1.332997e-1` at iteration `37` | no stable low-residual window |

### Residual and numerical-health evidence

The endpoint residual history contains exactly `500` points, iterations `1–500`.

| Equation | Initial | Final | Minimum over run |
|---|---:|---:|---:|
| Continuity | `1.000000` | `2.288839e-1` | `1.332997e-1` |
| x velocity | `3.566766e-3` | `1.079818e-3` | `6.085548e-4` |
| y velocity | `3.712990e-3` | `1.212693e-3` | `5.317855e-4` |
| z velocity | `4.148917e-3` | `1.117975e-3` | `5.339696e-4` |
| k | `5.966393e-1` | `1.129812e-2` | `7.865774e-3` |
| epsilon | `1.609200e3` | `2.851939e-1` | `1.731018e-2` |
| liquid volume fraction | `1.325980e-1` | `1.489275e-2` | `5.815662e-3` |

The native transcript recorded persistent reverse flow on both pressure outlets and turbulent-viscosity limiting, reaching approximately `27,030` limited cells on explicit endpoint reload. Classify H as **unstable / indeterminate and numerically unhealthy**, not converged and not a pressure-selection result.

Post-processing artifacts: [Student build manifest](../../../../../../PyAnsys/output/02c-student-h1140-build-20260816T091723Z.json), [carrier flux JSON](../../../../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-flux-check.json), [residual JSON](../../../../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-residual-check.json), [residual plot](../../../../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-residual-check.png), [native journal](../../../../../../PyAnsys/output/02c-student-h1140-run-20260816T091812Z.jou).

**Interpretation status: pending user direction.**

### Artifact index

| Case | Remote endpoint | Carrier flux | Residual history | EWF/DPM audit | DPM bundle |
|---|---|---|---|---|---|
| D | `02c-D-...-iter500-20260813T205605Z.cas.h5/.dat.h5` | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-flux-check.json) | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-D-brine-p1122p5kpa-unprimed-iter500-residual-check.json) | [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-D-iter500-dpm/model_audit.json) | [raw](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-D-iter500-dpm/raw_results.json) |
| E | `02c-E-...-iter500-20260813T205605Z.cas.h5/.dat.h5` | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-flux-check.json) | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-E-brine-p1127p5kpa-unprimed-iter500-residual-check.json) | [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-E-iter500-dpm/model_audit.json) | [raw](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-E-iter500-dpm/raw_results.json) |
| F | `02c-F-...-iter500-20260813T205605Z.cas.h5/.dat.h5` | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-flux-check.json) | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-F-brine-p1130kpa-unprimed-iter500-residual-check.json) | [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-F-iter500-dpm/model_audit.json) | [raw](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-F-iter500-dpm/raw_results.json) |
| G | `02c-G-...-iter500-20260813T205605Z.cas.h5/.dat.h5` | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-flux-check.json) | [JSON](../../../PyAnsys/output/post_simulation_analysis/02c-G-brine-p1135kpa-unprimed-iter500-residual-check.json) | [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-G-iter500-dpm/model_audit.json) | [raw](../../../PyAnsys/output/ewf_dpm_diagnostics/02c-G-iter500-dpm/raw_results.json) |
| H | `02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z.cas.h5/.dat.h5` | [JSON](../../../../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-flux-check.json) | [JSON](../../../../../../PyAnsys/output/post_simulation_analysis/02c-H-brine-p1140kpa-unprimed-student-iter500-20260816T091812Z-residual-check.json) | Student endpoint reload: viscosity limiting; no DPM/EWF claim | — |

For all four cases, the audit reports EWF disabled, no active film wall, and no UDF body-force/scalar-update match. DPM transcripts completed for all six inherited injections per case. These inherited particle results are kept for reproducibility but excluded from the primary pressure comparison.

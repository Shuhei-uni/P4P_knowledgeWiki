# Results Report — Setup 02c, Unprimed Brine-Pressure Screens (Cases A and B)

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

**Measured:** direct Case C live-session carrier/residual extraction, model audit, and full six-injection DPM output; complete A/B/C phase-flux screens now exist.

**Derived:** at their respective early checkpoints, the brine-pressure increase from A to C coincides with lower observed vapour wrong-outlet fraction (`60.38%` → `32.76%`) and higher observed vapour steam-outlet fraction (`40.17%` → `67.16%`). The liquid metrics are not comparable recovery outcomes because all fields remain open and Case C liquid outflow exceeds inlet.

**Unresolved:** none of the three checkpoints supplies a common converged/stable window, liquid-inventory history, tangential-pipe pressure diagnostics, or visual field evidence. Case A also has a different final iteration count. The active inherited DPM branch releases from the steam outlet, not an intended inlet.

Smallest justified next action: define a common convergence/stability gate (including outlet-flow and liquid-inventory monitors), rerun or continue all three pressure points to that same gate from their frozen pre-initialization parent, and only then evaluate brine-pressure selection.

# Diagnostic Results Report — Setup 010V2a

## Setup link and run identity

- Setup definition: [010V2a — EWF Splash Sensitivity](../../active/010V2a-ewf-splash.md)
- Parent setup: [010V2 — EWF deposition and film-inventory control](../../active/010V2-ewf-deposition-film-inventory.md)
- Fluent server and version: server `2`, `Ansys Fluent 2024 R2`
- Analysis date: `2026-07-22`
- Case/data state: the analysis used the already-loaded session; Fluent did not expose case/data filenames through this read-only workflow. The residual history spans monitor iterations `4`–`1963`.
- Checks run: carrier flux, residual history, Particle Tracks Summary for all six live DPM injections, EWF/DPM configuration audit, and final-state EWF snapshot on `wall`.
- Evidence class: diagnostic only.

## 1. Run scope

This is the splash-only `010V2a` branch: EWF DPM coupling is intended to remain on while global DPM interaction with the continuous phase remains off. The audit readback confirms global DPM interaction is `Off`, `wall` is the only active film wall, `DPM Wall Splash` is enabled on that wall, the impingement model is `stanton-rutland`, and its configured number of splashed particles is `4`.

The checks did not modify case/data, physics, or iterations. The final-state snapshot created or reused namespaced `ewfdiag-*` report definitions only.

## 2. Carrier flux and residual evidence

| Quantity | Value |
|---|---:|
| Liquid inlet flow | `111.074 kg/s` |
| Vapor inlet flow | `80.690 kg/s` |
| Steam-outlet liquid flow | `0 kg/s` |
| Steam-outlet vapor flow | `81.4218 kg/s` |
| Derived phase efficiency | `1.000` |
| Steam-outlet dryness | `1.000` |
| Derived carrier mass imbalance | `110.3422 kg/s` (`57.54%`); informational only because the simplified Purnanto geometry has no lower-liquid outlet |

The phase mapping fell back to `phase-1 = vapor` and `phase-2 = liquid` because the live state did not disclose the material-to-phase mapping. The mixture mass-flow report was unavailable, so the imbalance is a phase-specific derived diagnostic, not a closed conservation result.

The residual export contains seven curves and `963` points. At the last recorded monitor iteration (`1963`), continuity is `2.29e-3`, liquid volume fraction is `1.34e-3`, `k` is `2.13e-1`, and epsilon is `4.76e-1`. Continuity fell from `3.41e-1`, but this history alone does not establish convergence or physical validity.

## 3. DPM Particle Tracks Summary

The original injected DPM allocation totals `5.846 kg/s`. Fluent completed a summary track for each live injection. The table contains original-particle fates; EWF absorption and splash events are reported separately and must not be added to the tracked original-particle total as though they were independent injections.

| Diameter (µm) | Injection flow (kg/s) | Tracked | Escaped | Trapped | Incomplete | EWF absorbed events | Splash events |
|---:|---:|---:|---:|---:|---:|---:|---:|
| `5.63` | `0.0380130` | 2170 | 2162 | 0 | 7 | 1 | not printed |
| `28.14` | `0.1560534` | 2170 | 2158 | 2 | 4 | 6 | not printed |
| `56.27` | `0.1940664` | 2174 | 2007 | 5 | 4 | 159* | 4 |
| `112.54` | `0.3901335` | 2174 | 1510 | 20 | 3 | 642* | 4 |
| `168.81` | `0.3901335` | 2174 | 1008 | 33 | 3 | 1131* | 4 |
| `348.88` | `4.6776003` | 2170 | 435 | 54 | 0 | 1681 | not printed |

`*` The EWF header count is one greater than the fate-table absorbed count for the `56.27`, `112.54`, and `168.81 µm` injections. This discrepancy is preserved as reported by Fluent.

The transcript explicitly reports `12` splashed EWF events: four for each of the `56.27`, `112.54`, and `168.81 µm` injections. It does **not** provide represented splashed mass. Therefore no splashed-mass balance is claimed, and omitted splash text for the other injections is not converted into an asserted physical zero.

Fluent's per-injection mass-transfer tables do report absorbed original-particle flow, including `1.752e-05`, `4.315e-04`, `1.413e-02`, `1.152e-01`, `2.032e-01`, and `3.624 kg/s` from smallest to largest injection. See the transcript for the corresponding escaped, trapped, and incomplete mass flows.

## 4. EWF final-state snapshot

The final-state snapshot is scoped to the confirmed `wall` film wall and the `steamoutlet` film-flux boundary. It is a final-state bookkeeping snapshot, not a time-integrated mass balance.

| EWF quantity | Final value |
|---|---:|
| Maximum film Courant number | `0.010627651` |
| Film inventory on `wall` | `0.074310961 kg` |
| Maximum film thickness | `1.6408537e-4 m` (`0.164 mm`) |
| Area-weighted film thickness | `1.2587309e-6 m` (`1.259 µm`) |
| Snapshot film outflow mass | `9.2668918e-8 kg` |
| Instantaneous `steamoutlet` film mass flow | `-6.5910833e-6 kg/s` |
| Area-weighted film x velocity | `0.063969943 m/s` |
| Area-weighted film y velocity | `4.1049182e-4 m/s` |
| Area-weighted film z velocity | `0.018198265 m/s` |

The negative outlet flux follows Fluent's report orientation and is not independently interpreted here as a physical flow direction. The maximum film Courant number is bounded in this final snapshot, but this single value does not rule out an earlier transient spike.

The snapshot could not extract `Film DPM Mass Source`, area-weighted film-velocity magnitude, or maximum film-velocity magnitude because this Fluent session rejects the runner's requested aliases. Stripped and separated film mass are correctly reported as inactive mechanisms. The EWF settings root is also unavailable through this Fluent Settings API adapter; the wall-level EWF readback above is the authoritative live evidence for this run.

## 5. Interpretation and acceptance gate

The completed tracks demonstrate that EWF absorption occurs across all six original injections and that Fluent reported splash events for the middle three diameter classes. The largest (`348.88 µm`) class is absorption-dominant by event count, while the fine classes are escape-dominant.

This does not yet close the `010V2a` splash claim. The reported splash events are secondary-particle events, not original-particle fates, and their represented mass is unavailable. The final film inventory, thickness, outlet flux, and CFL have now been captured, but Film DPM Mass Source, history-based inventory change, and a closed carrier/DPM/film balance remain unavailable. The `57.54%` derived carrier imbalance is also too large for a conservation claim.

## 6. Conclusion

**Needs follow-up.** Retain `010V2a` as an active diagnostic branch. The next analysis must obtain time histories for film inventory, film outflow, CFL, and Film DPM Mass Source; represented splashed mass; and a reconciliation with direct escape, absorption, and storage. Resolve the phase-flux imbalance before interpreting splash as a quantified physical mechanism.

## Machine-readable evidence

- [Flux check JSON](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-flux-check.json)
- [Residual check JSON](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-residual-check.json)
- [Residual history plot](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-residual-check.png)
- [DPM Particle Tracks Summary JSON](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-dpm-particle-track-summary.json)
- [DPM Particle Tracks Summary CSV](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-dpm-particle-track-summary.csv)
- [DPM Particle Tracks transcript](../../../PyAnsys/output/post_simulation_analysis/010V2a-ewf-splash-dpm-particle-track-transcript.txt)
- [EWF/DPM model audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-ewf-splash/model_audit.json)
- [EWF final-state raw results](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-ewf-splash-snapshot/raw_results.json)
- [EWF bookkeeping snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-ewf-splash-snapshot/bookkeeping.json)

## 7. Results at 5,000 iterations

### 7.1 Evidence and applicability

- **Checkpoint:** the case/data already loaded on Fluent server ID `2`; Ansys Fluent `2025 R2`; captured 2026-07-24 after the user-confirmed 5,000th iteration. The live session did not expose case/data filenames, so their identity remains unrecoverable from the generated artifacts.
- **Evidence class:** `partial diagnostic`. The analysis did not load a case/data pair, run iterations, or intentionally change physics. Snapshot mode reused only the namespaced `ewfdiag-*` report definitions.
- **Raw evidence:** [audit](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-server2-20260724-5000-audit/), [EWF final-state snapshot](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-server2-20260724-5000-snapshot/), [completed six-injection DPM sweep](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-server2-20260724-5000-dpm/), [carrier flux check](../../../PyAnsys/output/post_simulation_analysis/010V2a-server2-20260724-5000-flux-check.json), and [residual history](../../../PyAnsys/output/post_simulation_analysis/010V2a-server2-20260724-5000-residual-check.json) ([plot](../../../PyAnsys/output/post_simulation_analysis/010V2a-server2-20260724-5000-residual-check.png)).

| Analysis | Status | Evidence / reason |
|---|---|---|
| Carrier residual and phase-flux checks | completed, limiting | Residual history reaches iteration 5000; the selected-surface carrier balance remains open. |
| DPM fate analysis | completed | All six live `water-liquid-at-psep-*` injections passed the transcript completion gate; [per-injection raw summaries](../../../PyAnsys/output/ewf_dpm_diagnostics/010V2a-server2-20260724-5000-dpm/dpm_raw/) are retained. |
| EWF audit / final-state snapshot | partial | `wall` is confirmed as the film wall. The 2025 R2 Settings API still does not expose the top-level EWF branch. |
| EWF history / closure | deferred | Only a final loaded state is available; no defined interval or integrated histories exist. |
| Splash | active at `wall` / measured | The wall readback has Stanton–Rutland splash with four configured splashed particles. DPM transcripts print splash events for the 112.54, 168.81, and 348.88 µm injections. |
| Edge separation / particle stripping | not applicable to reported result | This is the splash-only branch; no current DPM transcript prints separation or stripping events. The unavailable root EWF readback is not treated as proof of a physical zero. |

The audit reads global DPM interaction `Off`, unsteady tracking `Off`, and maximum DPM steps `10000`, consistent with the setup's intended controls. The unavailable `models.eulerian_wall_film` Settings-API path is an adapter limitation, not evidence that EWF is disabled.

### 7.2 Carrier-field and numerical state at iteration 5,000

The residual export has 1,000 retained points from iterations 256–5000. Final scaled residuals are continuity `7.475e-3`, x/y/z velocity `1.927e-4` / `1.932e-4` / `2.160e-4`, k `4.001e-3`, epsilon `2.592e-2`, and phase-2 volume fraction `1.337e-3`. No acceptance threshold or monitor-flatness criterion was supplied; this evidence does **not** establish convergence.

The phase mapping remains the live-extractor fallback of phase-1 = vapor and phase-2 = liquid. The selected surfaces report 111.074 kg/s liquid inlet and 80.690 kg/s vapor inlet; `steamoutlet` carries 81.418420 kg/s vapor and 0 kg/s liquid. The selected-surface imbalance is 110.345580 kg/s (57.54% of the 191.764 kg/s inlet total). Therefore, the apparent steam-outlet dryness and phase efficiency of 1.0 remain scoped diagnostics, not separator-performance results.

### 7.3 DPM results at iteration 5,000

Each row has a complete `number tracked` line, mass-transfer section, parsed mass-transfer rows, a quiet interval of about 1.0 s, and an individual raw transcript. Flows are terminal fate flows in kg/s. EWF event counters are separate interaction diagnostics and are not added a second time to terminal mass closure.

| Diameter (µm) | Injection | Net flow | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Closure residual |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.038010 | 0.037730 | 0 | 2.452e-4 | 3.504e-5 | 2 | not printed | -2.400e-7 |
| 28.14 | `water-liquid-at-psep-28um` | 0.156100 | 0.153400 | 1.151e-3 | 8.630e-4 | 6.472e-4 | 9 | not printed | 3.880e-5 |
| 56.27 | `water-liquid-at-psep-56um` | 0.194100 | 0.163500 | 4.650e-3 | 6.260e-4 | 2.531e-2 | 283 | not printed | 1.400e-5 |
| 112.54 | `water-liquid-at-psep-112um` | 0.390300 | 0.210100 | 1.618e-2 | 1.798e-4 | 0.163800 | 912 | 4 | 4.020e-5 |
| 168.81 | `water-liquid-at-psep-168um` | 0.390400 | 0.144900 | 1.510e-2 | 0 | 0.230400 | 1284 | 8 | 5.551e-17 |
| 348.88 | `water-liquid-at-psep-348um` | 4.724000 | 0.232100 | 0.215800 | 0 | 4.276000 | 2019 | 104 | 1.000e-4 |

Escaped particles terminate at `steamoutlet`, and trapped particles at `bottom`. The largest relative closure residual is `2.49e-4` (28.14 µm), consistent with printed mass-flow precision. The 348.88 µm transcript has 2,019 EWF absorbed events but 1,993 final absorbed particles; these are distinct counters and are retained separately. The reported splash events are secondary-parcel/event diagnostics, not additional terminal mass sinks.

### 7.4 EWF final-state results at iteration 5,000

Confirmed final-state film-wall scope: `wall`. Values below are one-checkpoint measurements, not time-integrated terms.

| Quantity | Reduction / scope | Value | Unit | Interpretation limit |
|---|---|---:|---|---|
| Film Courant Number | facet maximum, `wall` | 1.0759366e-2 | dimensionless | final-state numerical diagnostic only |
| Film Mass | sum, `wall` | 2.0655528e-1 | kg | current inventory |
| Film Thickness | facet maximum, `wall` | 3.9866607e-4 | m | local maximum |
| Film Thickness | area-weighted average, `wall` | 3.4987776e-6 | m | distributed-film measure |
| Film Outflow Mass | sum, `wall` | 2.7735934e-7 | kg | Fluent final-state field; not a rate |
| Film Mass Flow Rate | selected boundaries / net | -2.9794671e-6 | kg/s | `steamoutlet`; preserve Fluent report sign |
| Film velocity components | area-weighted, `wall` | x 1.7180708e-1; y -5.5620131e-3; z 5.3621321e-2 | m/s | direct component measurements |
| Film velocity magnitude | derived from measured components | 1.8006625e-1 | m/s | not an independently extracted Fluent magnitude |
| Film DPM Mass Source | sum, `wall` | unavailable | kg/s | runner requested an unsupported alias; Fluent advertises `film-dpm-mass-src` |
| Film Stripped Mass | sum, `wall` | not applicable | kg | splash-only result; no stripping event is printed |
| Film Separated Mass | sum, `wall` | not applicable | kg | splash-only result; no separation event is printed |

### 7.5 EWF bookkeeping, interpretation, and limitation at iteration 5,000

**Status: bookkeeping-only.** The final data state cannot close the EWF balance. Missing terms are initial inventory, time-integrated DPM-to-film source, film inflow/outflow, represented splash mass, and an explicit residual over a defined interval. The 0.20655528 kg inventory must not be combined directly with the kg/s boundary flux.

- **Measured:** the final-state film inventory is finite, the final CFL is bounded, and all six DPM injections have completed fate records. Fine classes remain escape-dominated; larger droplets have increasingly more final absorption. Splash is directly printed for 112.54, 168.81, and 348.88 µm.
- **Derived:** all six terminal fate-flow rows close within printed precision. The component-derived area-weighted film speed is 0.18006625 m/s.
- **Unresolved:** case/data filenames, full carrier outlet coverage, represented splash mass, Film DPM Mass Source, time-integrated EWF closure, and top-level EWF mechanism readback. None is treated as zero.

**Conclusion — diagnostic only.** This checkpoint continues to demonstrate EWF absorption and secondary splash events, but does not close the splash-mass, carrier, or film balance. It is not evidence of separator performance or a quantified splash mechanism.

## 8. Comparison: previous record vs. 5,000 iterations

The preceding record is from server 2 running Fluent 2024 R2 through monitor iteration 1963; this new record is server 2 running Fluent 2025 R2 through iteration 5000. The different Fluent release, unavailable case/data filenames, and independently recomputed DPM tracks mean this is a diagnostic trend comparison, not a controlled convergence study.

| Indicator | Previous record | At 5000 | Comparison |
|---|---:|---:|---|
| Carrier steam-outlet vapor flow | 81.4218 kg/s | 81.418420 kg/s | -0.00338 kg/s; effectively unchanged at the selected-surface scale |
| Selected-surface carrier imbalance | 110.3422 kg/s | 110.345580 kg/s | +0.00338 kg/s; remains 57.54% of inlet |
| Continuity residual | 2.29e-3 | 7.475e-3 | higher; no convergence conclusion |
| k / epsilon residual | 2.13e-1 / 4.76e-1 | 4.001e-3 / 2.592e-2 | lower, but no supplied acceptance or flatness criterion |
| Maximum film CFL | 1.0627651e-2 | 1.0759366e-2 | +1.2%; both final snapshots are bounded |
| Film inventory | 7.4310961e-2 kg | 2.0655528e-1 kg | +178% (2.78×) |
| Maximum film thickness | 1.6408537e-4 m | 3.9866607e-4 m | +143% (2.43×) |
| Area-weighted film thickness | 1.2587309e-6 m | 3.4987776e-6 m | +178% (2.78×) |
| `steamoutlet` film mass flow | -6.5910833e-6 kg/s | -2.9794671e-6 kg/s | lower magnitude; sign remains Fluent-report oriented |

| Diameter (µm) | Previous absorbed flow → at 5000 | Previous EWF absorbed events → at 5000 | Splash-event comparison | Interpretation limit |
|---:|---:|---:|---|---|
| 5.63 | 1.752e-5 → 3.504e-5 kg/s | 1 → 2 | not printed → not printed | Fine class remains escape-dominated. |
| 28.14 | 4.315e-4 → 6.472e-4 kg/s | 6 → 9 | not printed → not printed | Fine class remains escape-dominated. |
| 56.27 | 1.413e-2 → 2.531e-2 kg/s | 159 → 283 | 4 → not printed | Missing text is not treated as zero. |
| 112.54 | 0.1152 → 0.1638 kg/s | 642 → 912 | 4 → 4 | Greater final absorption; event count is unchanged. |
| 168.81 | 0.2032 → 0.2304 kg/s | 1131 → 1284 | 4 → 8 | Greater absorption and more printed splash events. |
| 348.88 | 3.624 → 4.276 kg/s | 1681 → 2019 | not printed → 104 | Greater final absorption; splash is now explicitly printed. |

**Comparison interpretation:** the later checkpoint has a substantially larger final film inventory and higher absorbed terminal flow across every injection. However, the splash metric remains an event count without represented mass, and the carrier balance remains open. The release change from Fluent 2024 R2 to 2025 R2 further limits causal interpretation of the differences.

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
| Derived carrier mass imbalance | `110.3422 kg/s` (`57.54%` of inlet mixture flow) |

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

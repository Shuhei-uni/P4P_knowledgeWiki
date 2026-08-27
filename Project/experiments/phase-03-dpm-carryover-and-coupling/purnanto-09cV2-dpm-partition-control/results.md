> **Retired source:** Setups/reports/purnanto-reference/09cV2/results.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Post-Simulation Results — Setup 09cV2

## Setup link and evidence

- Setup definition: [09cV2 — Skoog partition and injection-control](setup.md)
- Parent/comparison scope: `09c` two-way-DPM branch. This live state uses the `5%` allocation point: `111.074 kg/s` Eulerian liquid plus `5.846 kg/s` represented DPM liquid.
- Fluent session: server `2`, `Ansys Fluent 2025 R2`, case/data already loaded. The audit did not receive source filenames, so exact checkpoint filenames are **not available** in the captured evidence.
- Evidence class: `diagnostic; not converged`. These results do not validate separator efficiency, steam purity, or a physical geothermal inlet-droplet fraction.
- Evidence bundle: model audit (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-audit/model_audit.json`; not migrated), carrier fluxes (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-flux-check.json`; not migrated), residual history (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-residual-check.json`; not migrated), residual plot (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-residual-check.png`; not migrated), DPM injection summary (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-dpm/dpm_injection_summary.csv`; not migrated), DPM zone/fate rows (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-dpm/dpm_zone_summary.csv`; not migrated), and live DPM transcript (historical machine artifact path: `../../../PyAnsys/output/live_postprocess_20260722/09cV2-server2-dpm/dpm_live_transcript.txt`; not migrated).

## Analysis applicability

| Analysis | Status | Evidence/reason |
|---|---|---|
| Carrier residual and phase-flux checks | Completed | Flux and 909-iteration residual capture from the already-loaded session. |
| DPM fate analysis | Completed | Complete Particle Tracks Summary sweep for all six active injections. |
| EWF audit | Completed — not applicable | Audit reports `ewf_enabled = false` and no confirmed film walls. |
| EWF final-state snapshot and history/closure | Not applicable | No active Eulerian Wall Film model; no film quantities were created or inferred. |
| Splash, stripping, and edge separation | Not applicable | EWF is disabled. The 2025 R2 adapter could not expose its EWF branch, so optional-mechanism state is not represented as a measured zero. |

## Carrier-field and numerical state

The live carrier report identifies `phase-1` as vapor and `phase-2` as liquid (the mapping is a documented fallback in the artifact). Reported phase fluxes are:

| Scope | Vapor, `kg/s` | Liquid, `kg/s` |
|---|---:|---:|
| `steaminlet` | `80.690` | `0` |
| `liquidinlet` | `0` | `111.074` |
| `steamoutlet` | `81.412` | approximately `2.28e-57` |

The carrier-only inlet total is `191.764 kg/s`, versus `81.412 kg/s` at the reported outlet. The derived phase-flow imbalance is therefore `110.352 kg/s` (`57.55%` of inlet). This open balance prevents a separator-performance or steam-purity claim, even though the scoped outlet liquid flow is numerically near zero.

The residual record spans iterations `1`–`909`. Velocity residuals finish near `3.0e-5`, and liquid volume fraction finishes at `7.14e-4`; however, continuity remains `2.86e-1` (minimum `2.52e-1`). The result is not converged. The epsilon history also contains a startup maximum of `4.54e3`, with final epsilon `2.70e-3`.

## DPM results

All six active surface injections use `water-liquid-at-psep-dpm` on `steaminlet`; their read-back total is `5.846 kg/s`, consistent with the setup's `5%` allocation point. Each summary tracked `2,170` parcels. `Incomplete` is retained as unresolved particle mass, not treated as captured or escaped mass.

| Diameter, µm | Injection | Net flow, kg/s | Escaped | Trapped | Incomplete | Final absorbed | EWF absorbed events | Splash events | Closure residual, kg/s |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 5.63 | `water-liquid-at-psep-5um` | 0.03801 | 776 | 380 | 1,014 | — | — | — | `3.0e-6` |
| 28.14 | `water-liquid-at-psep-28um` | 0.15610 | 29 | 506 | 1,635 | — | — | — | `2.4e-5` |
| 56.27 | `water-liquid-at-psep-56um` | 0.19410 | 0 | 591 | 1,579 | — | — | — | `5.0e-5` |
| 112.54 | `water-liquid-at-psep-112um` | 0.39010 | 0 | 713 | 1,457 | — | — | — | `0` |
| 168.81 | `water-liquid-at-psep-168um` | 0.39010 | 0 | 813 | 1,357 | — | — | — | `-1.0e-4` |
| 348.88 | `water-liquid-at-psep-348um` | 4.67800 | 0 | 1,129 | 1,041 | — | — | — | approximately `0` |

Terminal zones are `steamoutlet` for the escaped 5.63 and 28.14 µm parcels, and `bottom` for trapped parcels. No final absorbed fate or EWF splash counter was reported, which is consistent with EWF being inactive; these fields are shown as not applicable rather than zero-valued mechanisms.

The printed mass-flow closures are within `2.6e-4` relative residual per injection. Across the rounded fate rows, approximately `0.0157 kg/s` escapes, `2.8043 kg/s` traps at `bottom`, and `3.0265 kg/s` remains incomplete. Thus, DPM accounting is internally closed to output precision, but more than half of the represented DPM mass remains unresolved and cannot support a carryover or capture-performance conclusion.

## Interpretation, limitations, and next action

- **Measured:** six complete DPM summary transcripts, their fate/mass-transfer rows, the active injection payload, carrier phase fluxes, and residual history.
- **Derived:** the `5%` DPM allocation read-back is consistent with `111.074 + 5.846 = 116.920 kg/s` at inlet accounting level; DPM terminal rows close to printed precision.
- **Unresolved:** the carrier field is strongly mass-imbalanced and continuity is not converged; many particle paths are incomplete; exact loaded checkpoint filenames were not returned; EWF and its optional mechanisms are absent from this branch.

Next action: preserve this diagnostic checkpoint, then continue or rerun the carrier solution until phase-flow balance and continuity are acceptably closed before comparing allocation points or creating the `010V2` EWF branch. Do not enable EWF, splash, stripping, or edge separation merely to extend this analysis.

> **Legacy source:** Setups/reports/purnanto-reference/09cV3/results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Post-Simulation Results — Setup 09cV3

## Scope and evidence

- Setup definition: [09cV3 — Fine-Mist 5% DPM PSD Rerun](setup.md).
- Fluent version: `Ansys Fluent 2025 R2`. Server `2` was used only as the connection route; it is not case identity.
- **Reported** values below are Fluent phase-flux and Particle Tracks outputs. Percentages are **Derived** from those values.
- The 10% case/data was supplied by the operator as the active Fluent session. Its captured residual history ends at iteration `5000`; the local artifact records this as an already-loaded session rather than as a saved, immutable checkpoint.
- The 5% analysis explicitly loaded `09cV3-fDPM-05pct-finemist-5to100um.cas.h5` with `09cV3-fDPM-05pct-finemist-5to100um-5000.dat.h5`. This is an **Assumed, non-canonical pair**: the filenames do not form a matching saved `-5000` case/data checkpoint, although the loaded residual history ends at iteration `5000`.

The tables intentionally report only phase fluxes, residual endpoints, and observed DPM escape. They do not present a full-separator mass balance or use DPM track outcomes as an efficiency claim.

## Carrier phase-flux results

| Metric | 5% loading @ 5,000 | 10% loading @ 5,000 |
|---|---:|---:|
| Eulerian liquid at `liquidinlet`, kg/s | `111.074000` | `105.228000` |
| Vapour at `steaminlet`, kg/s | `80.690000` | `80.690000` |
| Vapour at `steamoutlet`, kg/s | `81.425470` | `81.373933` |
| Eulerian liquid at `steamoutlet`, kg/s | `0.0309432` | `0.00778785` |
| Outlet carrier vapour fraction, % | `99.962013%` | `99.990430%` |
| Eulerian-liquid removal from `liquidinlet`, % | `99.972142%` | `99.992599%` |
| Residual-history endpoint, iteration | `5000` | `5000` |
| Continuity residual at endpoint | `1.64399e-1` | `1.58984e-1` |

The two derived percentages are limited to the reported carrier-phase fluxes on the named boundaries; they are not a separator-efficiency or convergence conclusion.

## DPM Particle Tracks — observed escape

All seven named injections completed a `2,170`-parcel Particle Tracks summary. The table contains the reported escape at `steamoutlet` only. A blank/zero escape entry means Fluent did not report an escaped terminal row for that injection in this analysis.

| Diameter, µm | 5%: escaped parcels / tracked | 5%: escaped DPM mass flow, kg/s | 10%: escaped parcels / tracked | 10%: escaped DPM mass flow, kg/s |
|---:|---:|---:|---:|---:|
| 7.07 | `10 / 2170` | `0.001885` | `20 / 2170` | `0.007542` |
| 14.14 | `0 / 2170` | `0` | `0 / 2170` | `0` |
| 24.49 | `0 / 2170` | `0` | `0 / 2170` | `0` |
| 34.64 | `0 / 2170` | `0` | `0 / 2170` | `0` |
| 48.99 | `0 / 2170` | `0` | `0 / 2170` | `0` |
| 69.28 | `0 / 2170` | `0` | `0 / 2170` | `0` |
| 89.44 | `0 / 2170` | `0` | `0 / 2170` | `0` |
| **Reported escaped total** | **`10 / 15190`** | **`0.001885`** | **`20 / 15190`** | **`0.007542`** |

## Evidence files

### 5% loading

- Carrier phase-flux output (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000/09cV3-05pct-base-plus-5000data-flux-check.json`; not migrated)
- Residual history JSON (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000/09cV3-05pct-base-plus-5000data-residual-check.json`; not migrated) and plot (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000/09cV3-05pct-base-plus-5000data-residual-check.png`; not migrated)
- DPM Particle Tracks summary CSV (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000_dpm/09cV3-05pct-iter5000-dpm-summary-particle-track-summary.csv`; not migrated) and raw transcript (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000_dpm/09cV3-05pct-iter5000-dpm-summary-particle-track-transcript.txt`; not migrated)

### 10% loading

- Carrier phase-flux output (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000/09cV3-10pct-iter5000-assumed-live-flux-check.json`; not migrated)
- Residual history JSON (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000/09cV3-10pct-iter5000-assumed-live-residual-check.json`; not migrated) and plot (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000/09cV3-10pct-iter5000-assumed-live-residual-check.png`; not migrated)
- DPM injection summary CSV (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000_massfates/09cV3-10pct-iter5000-massfates/dpm_injection_summary.csv`; not migrated), zone summary CSV (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000_massfates/09cV3-10pct-iter5000-massfates/dpm_zone_summary.csv`; not migrated), and raw per-injection transcripts (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000_massfates/09cV3-10pct-iter5000-massfates/dpm_raw`; not migrated)

## Handoff note

The 5% and 10% data sets are now analyzed and retained locally. A matched `-5000.cas.h5` plus `.dat.h5` pair should be saved for 5% before treating that row as a canonical checkpoint in later comparison work.

> **Retired source:** Setups/reports/purnanto-reference/09cV3/dpm-mass-allocation-quick-report.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# 09cV3 DPM-Mass Allocation — Quick Results Report

Setup: [09cV3 — Fine-Mist 5% DPM PSD Rerun](setup.md)

## Quick-report plan

1. State the DPM allocation point and completed iteration count.
2. Compare the carrier liquid-removal percentage.
3. Compare DPM mass reaching `steamoutlet` and DPM mass trapped at `bottom`.

## 1. Comparison points

| DPM allocation | DPM mass injected, kg/s | Eulerian liquid at `liquidinlet`, kg/s | Result checkpoint |
|---:|---:|---:|---:|
| `2%` | `2.338400` | `114.581600` | `5,000` iterations |
| `3%` | `3.507600` | `113.412400` | `2,000` iterations |
| `5%` | `5.846000` | `111.074000` | `5,000` iterations |
| `10%` | `11.692000` | `105.228000` | `5,000` iterations |

## 2. Carrier liquid-removal result

Carrier liquid-removal percentage = `(1 − |Eulerian liquid at steamoutlet| / Eulerian liquid at liquidinlet) × 100`.

| DPM allocation | Eulerian liquid at `steamoutlet`, kg/s | Carrier liquid-removal, % |
|---:|---:|---:|
| `2%` | `0.0966121` | `99.915683%` |
| `3%` | `0.000000742` | `99.999999%` |
| `5%` | `0.0309432` | `99.972142%` |
| `10%` | `0.00778785` | `99.992599%` |

## 3. DPM mass-fate result

DPM steam-outlet fraction = `(DPM mass escaped at steamoutlet / DPM mass injected) × 100`.

| DPM allocation | DPM mass escaped at `steamoutlet`, kg/s | DPM steam-outlet fraction, % | DPM mass trapped at `bottom`, kg/s | DPM bottom-trapped fraction, % |
|---:|---:|---:|---:|---:|
| `2%` | `0.0015080` | `0.064489%` | `0.532370` | `22.766421%` |
| | `5%` | `0.0018850` | `0.032244%` | — | — |
| `10%` | `0.0075420` | `0.064506%` | `1.908670` | `16.324581%` |

## Evidence

| DPM allocation | Carrier flux result | DPM mass-fate result |
|---:|---|---|
| `2%` | phase fluxes (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/02pct_iter5000/09cV3-02pct-iter5000-flux-check.json`; not migrated) | mass fates (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/02pct_iter5000_massfates/09cV3-02pct-iter5000-massfates/dpm_zone_summary.csv`; not migrated) |
| `3%` | phase fluxes (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/03pct_iter2000/09cV3-03pct-iter2000-flux-check.json`; not migrated) | mass fates (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/03pct_iter2000_massfates/09cV3-03pct-iter2000-massfates/dpm_zone_summary.csv`; not migrated) |
| `5%` | phase fluxes (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000/09cV3-05pct-base-plus-5000data-flux-check.json`; not migrated) | [reported escape result](results.md#dpm-particle-tracks--observed-escape) and particle-track summary (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/05pct_iter5000_dpm/09cV3-05pct-iter5000-dpm-summary-particle-track-summary.csv`; not migrated) |
| `10%` | phase fluxes (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000/09cV3-10pct-iter5000-assumed-live-flux-check.json`; not migrated) | mass fates (historical machine artifact path: `../../../PyAnsys/output/09cV3_results/10pct_iter5000_massfates/09cV3-10pct-iter5000-massfates/dpm_zone_summary.csv`; not migrated) |

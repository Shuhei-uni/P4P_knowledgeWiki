> **Legacy source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-fixed3000-results-20260820.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# 03A Stage 3 — fixed-3,000 execution results (2026-08-20)

> **Campaign:** 03A Stage 3 — Fluent-recommended convergence sweep  
> **Run stamp:** `20260820T013223Z`  
> **Branches covered:** F02, F04, F05, F06, F11  
> **Status:** execution record complete; endpoint physical post-processing complete; residual-window statistics pending

This report records the five branches executed in the fixed-3,000-iteration campaign. It is an execution and checkpoint inventory, not a convergence or physics interpretation. Every named case/data pair listed as **verified** below was checked as a complete remote pair after the run.

The source state was the immutable monitor-ready P0 case:

```text
C:\Users\syok443\OneDrive - The University of Auckland\2026 Sem 2\700\Full geom\03A-stage3\03A-stage3-P0-monitor-ready-preinit.cas.h5
```

## 1. Result status at a glance

| Branch | Schedule | Completed native stages | Total completed iterations | Full-mixture 100% iterations | Final usable checkpoint | Result status |
|---|---|---:|---:|---:|---|---|
| F02 | Carrier-first, 100% | 0 / 1 | Not confirmed | 0 | Hybrid-initialized pair only | **PARTIAL** — terminal native-stage error; not classified as a numerical failure |
| F04 | Carrier-first, 100% | 0 / 1 | Not confirmed | 0 | Hybrid-initialized pair only | **PARTIAL** — terminal native-stage error; not classified as a numerical failure |
| F05 | Full mixture, 100% | 1 / 1 | 3,000 | 3,000 | `full-mixture-100pct-end` | **COMPLETED** |
| F06 | Carrier-first, then full mixture; 100% | 2 / 2 | 6,000 | 3,000 | `full-mixture-100pct-end` | **COMPLETED** |
| F11 | Full mixture progressive: 10 → 20 → 40 → 80 → 100% | 5 / 5 | 15,000 | 3,000 | `full-mixture-100pct-end` | **COMPLETED** |

There are 23 verified plot-ready case/data pairs: five hybrid-initialized pairs, eight native-stage endpoint pairs, and ten transition pairs. F02 and F04 have no named native endpoint pair because their submitted carrier stages ended with terminal Fluent-native errors.

## 2. Evidence and post-processing boundary

The campaign ledger and event log establish submission, completion, transition, and file-pair verification. A subsequent explicit paired case/data readback captured phase-resolved boundary mass flow for the seven completed full-mixture native endpoints: F05 at 100%, F06 at 100%, and F11 at 10%, 20%, 40%, 80%, and 100%.

Therefore:

- `NOT EXTRACTED` means the quantity has not yet been read from the named checkpoint; it does not mean zero.
- The extracted outlet-path flows below use Fluent's outward-positive convention. A negative nominal outlet flow therefore means backflow through that boundary and is retained as a negative value.
- At the seven full-mixture native endpoints, total liquid inventory, Y010/Y030 liquid mass, and brine-entry static/total pressure were recomputed from the report definitions embedded in the paired checkpoints.
- The Y010/Y030 volume-integral definitions did not return a scalar through this Fluent wrapper. Their liquid masses are reported directly; volumes can be derived with the documented liquid density of `881.77 kg/m³` if required.
- This report makes no claim that a completed branch is physically converged or settled.
- Each of the seven completed full-mixture endpoint pairs was explicitly loaded and inspected. Each retained 30 report-definition monitor sets, but none retained Fluent's `residual` monitor set. Consequently, 500-iteration residual-window statistics cannot be reconstructed from the case/data pairs; they require the native residual-export files.

## 3. Branch records

### F02 — carrier-first, 100%

**Intent.** Test a carrier-first start at full velocity using the F02 under-relaxation setup from the [Stage 3 sweep plan](setup-source.md).

**Execution record.** The carrier 100% stage was submitted after hybrid initialization. Fluent returned a terminal native-stage error before the planned named endpoint pair was written. The ledger records `numerical_failure: false`; this is retained as a terminal execution error, not relabelled as an FPE/numerical failure.

| Checkpoint | Cumulative iterations | State | Pair status | Physical results |
|---|---:|---|---|---|
| `03A-stage3-F02-hybrid-initialized-iter000000-20260820T013223Z` | 0 | Carrier, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F02-carrier-100pct-end-20260820T013223Z` | — | Carrier, 100% | **Missing** — terminal stage did not reach named endpoint | Unavailable |

No full-mixture transition was applied. The native residual export is unavailable for the failed stage; the native transcript exists.

### F04 — carrier-first, 100%

**Intent.** Test a carrier-first start at full velocity using the F04 under-relaxation setup from the [Stage 3 sweep plan](setup-source.md).

**Execution record.** The carrier 100% stage was submitted after hybrid initialization and ended with the same terminal Fluent-native error form as F02, before the named endpoint pair was written. The ledger records `numerical_failure: false`.

| Checkpoint | Cumulative iterations | State | Pair status | Physical results |
|---|---:|---|---|---|
| `03A-stage3-F04-hybrid-initialized-iter000000-20260820T013223Z` | 0 | Carrier, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F04-carrier-100pct-end-20260820T013223Z` | — | Carrier, 100% | **Missing** — terminal stage did not reach named endpoint | Unavailable |

No full-mixture transition was applied. The native residual export is unavailable for the failed stage; the native transcript exists.

### F05 — full mixture, 100%

**Intent.** Test immediate full-mixture solving at 100% velocity with the F05 under-relaxation setup.

**Execution record.** One native 3,000-iteration full-mixture stage completed and its endpoint pair was verified.

| Checkpoint | Cumulative iterations | State | Pair status | Physical results |
|---|---:|---|---|---|
| `03A-stage3-F05-hybrid-initialized-iter000000-20260820T013223Z` | 0 | Full mixture, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F05-full-mixture-100pct-end-20260820T013223Z` | 3,000 | Full mixture, 100% | Verified | Phase-resolved mass flow extracted; inventory and pressure pending |

| Iteration | Total inlet kg/s | Total outlet kg/s | Signed mass imbalance | L→B kg/s | L→S kg/s | V→B kg/s | V→S kg/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3,000 | 198.486 | 170.030 | -14.336% | 81.390 | 6.902 | 35.323 | 46.416 |

Derived routing fractions are L→B `69.655%`, L→S `5.907%`, V→B `43.267%`, and V→S `56.854%`. The phase signed closures are liquid `-24.438%` and vapour `+0.122%`; the absolute whole-domain imbalance is `14.336%`.

| Total liquid m³ | Total liquid kg | Y030 liquid kg | Y010 liquid kg | Entry static pressure | Entry total pressure | Static margin to 1.120 MPa gauge |
|---:|---:|---:|---:|---:|---:|---:|
| 0.360585 | 317.752 | 172.354 | 166.299 | 1.121404 MPa gauge | 1.130056 MPa gauge | +1.404 kPa |

The endpoint event records these final instantaneous residual values at iteration 3,000: continuity `7.88097e-02`, x-velocity `1.61021e-05`, y-velocity `1.76411e-05`, z-velocity `1.76618e-05`, k `5.96102e-04`, epsilon `3.27444e-03`, and phase-2 volume fraction `1.39688e-03`. These are point values only; no final-window residual statistic has been calculated.

### F06 — carrier-first then full mixture, 100%

**Intent.** Test a carrier-first 100% solve followed by a no-reinitialization transition to full mixture at the same velocity.

**Execution record.** The carrier 100% endpoint completed at 3,000 iterations. The no-reinitialization transition was saved, then the full-mixture 100% endpoint completed at 6,000 cumulative branch iterations. The carrier endpoint was reconciled from its verified pair on resume; no duplicate carrier solve was submitted.

| Checkpoint | Cumulative iterations | State | Pair status | Physical results |
|---|---:|---|---|---|
| `03A-stage3-F06-hybrid-initialized-iter000000-20260820T013223Z` | 0 | Carrier, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F06-carrier-100pct-end-20260820T013223Z` | 3,000 | Carrier, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F06-carrier-100pct-pre-transition-20260820T013223Z` | 3,000 | Carrier, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F06-full-mixture-100pct-transition-20260820T013223Z` | 3,000 | Full mixture, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F06-full-mixture-100pct-end-20260820T013223Z` | 6,000 | Full mixture, 100% | Verified | Phase-resolved mass flow extracted; inventory and pressure pending |

| Cumulative iteration | Total inlet kg/s | Total outlet kg/s | Signed mass imbalance | L→B kg/s | L→S kg/s | V→B kg/s | V→S kg/s |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 6,000 | 198.486 | 169.940 | -14.382% | 83.421 | 4.873 | 37.183 | 44.463 |

Derived routing fractions are L→B `71.393%`, L→S `4.171%`, V→B `45.545%`, and V→S `54.463%`. The phase signed closures are liquid `-24.436%` and vapour `+0.007%`; the absolute whole-domain imbalance is `14.382%`.

| Total liquid m³ | Total liquid kg | Y030 liquid kg | Y010 liquid kg | Entry static pressure | Entry total pressure | Static margin to 1.120 MPa gauge |
|---:|---:|---:|---:|---:|---:|---:|
| 0.427397 | 376.627 | 251.880 | 245.693 | 1.121561 MPa gauge | 1.130960 MPa gauge | +1.561 kPa |

Residual exports exist for both native stages. Final residual values and residual-window statistics remain to be extracted.

### F11 — progressive full mixture, 10 → 20 → 40 → 80 → 100%

**Intent.** Test progressive velocity loading while full mixture is active throughout.

**Execution record.** All five native stages completed at exactly 3,000 iterations each. Each velocity transition was applied without reinitialization and saved both immediately before and immediately after the transition.

| Checkpoint | Cumulative iterations | State | Pair status | Physical results |
|---|---:|---|---|---|
| `03A-stage3-F11-hybrid-initialized-iter000000-20260820T013223Z` | 0 | Full mixture, 10% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-10pct-end-20260820T013223Z` | 3,000 | Full mixture, 10% | Verified | Phase-resolved mass flow extracted |
| `03A-stage3-F11-full-mixture-10pct-pre-transition-20260820T013223Z` | 3,000 | Full mixture, 10% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-20pct-transition-20260820T013223Z` | 3,000 | Full mixture, 20% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-20pct-end-20260820T013223Z` | 6,000 | Full mixture, 20% | Verified | Phase-resolved mass flow extracted |
| `03A-stage3-F11-full-mixture-20pct-pre-transition-20260820T013223Z` | 6,000 | Full mixture, 20% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-40pct-transition-20260820T013223Z` | 6,000 | Full mixture, 40% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-40pct-end-20260820T013223Z` | 9,000 | Full mixture, 40% | Verified | Phase-resolved mass flow extracted |
| `03A-stage3-F11-full-mixture-40pct-pre-transition-20260820T013223Z` | 9,000 | Full mixture, 40% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-80pct-transition-20260820T013223Z` | 9,000 | Full mixture, 80% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-80pct-end-20260820T013223Z` | 12,000 | Full mixture, 80% | Verified | Phase-resolved mass flow extracted |
| `03A-stage3-F11-full-mixture-80pct-pre-transition-20260820T013223Z` | 12,000 | Full mixture, 80% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-100pct-transition-20260820T013223Z` | 12,000 | Full mixture, 100% | Verified | NOT EXTRACTED |
| `03A-stage3-F11-full-mixture-100pct-end-20260820T013223Z` | 15,000 | Full mixture, 100% | Verified | Phase-resolved mass flow extracted |

At the final 100% endpoint, total inlet and outlet mass flows are `198.486 kg/s` and `173.919 kg/s`, respectively. The signed mass imbalance is `-12.377%` (absolute `12.377%`); L→B, L→S, V→B, and V→S are `84.814`, `7.436`, `35.918`, and `45.750 kg/s`. The corresponding routing fractions are `72.586%`, `6.364%`, `43.996%`, and `56.039%`. Liquid and vapour signed closures are `-21.050%` and `+0.036%`.

| Total liquid m³ | Total liquid kg | Y030 liquid kg | Y010 liquid kg | Entry static pressure | Entry total pressure | Static margin to 1.120 MPa gauge |
|---:|---:|---:|---:|---:|---:|---:|
| 0.391921 | 345.365 | 194.154 | 187.793 | 1.121690 MPa gauge | 1.130555 MPa gauge | +1.690 kPa |

Residual exports exist for all five native stages. Final residual values and residual-window statistics remain to be extracted.

## 4. Progressive-loading checkpoint map — F11

| Load | Cumulative iteration | Signed mass imbalance | L→B fraction | L→S fraction | V→B fraction | V→S fraction | Total liquid m³ | ΔP brine static |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10% | 3,000 | -176.734% | -896.396% | 694.092% | 0.000069% | 102.990% | 12.917960 | -0.022 kPa |
| 20% | 6,000 | +247.634% | 211.712% | 311.849% | 0.012766% | 95.827% | 9.154690 | +0.746 kPa |
| 40% | 9,000 | +5.069% | 99.945% | 9.070% | 27.183% | 72.237% | 0.925276 | +0.045 kPa |
| 80% | 12,000 | -0.597% | 95.777% | 3.368% | 41.432% | 58.341% | 0.535148 | +1.673 kPa |
| 100% | 15,000 | -12.377% | 72.586% | 6.364% | 43.996% | 56.039% | 0.391921 | +1.690 kPa |

The 10% L→B value is negative because the nominal brine outlet had liquid backflow at that checkpoint. The 20% routing fractions exceed 100% and are shown without capping, as required by the evidence model. Transition and hybrid checkpoints remain unextracted; lines between the five endpoint values, if plotted, are guides to the eye only.

| Load | Total liquid kg | Y030 liquid kg | Y010 liquid kg | Entry static pressure | Entry total pressure | Dynamic margin |
|---:|---:|---:|---:|---:|---:|---:|
| 10% | 11,383.447 | 4,690.476 | 4,179.590 | 1.119978 MPa gauge | 1.120393 MPa gauge | 0.415 kPa |
| 20% | 8,067.212 | 4,714.407 | 4,211.900 | 1.120746 MPa gauge | 1.120878 MPa gauge | 0.132 kPa |
| 40% | 815.363 | 733.815 | 730.352 | 1.120045 MPa gauge | 1.121139 MPa gauge | 1.094 kPa |
| 80% | 471.578 | 366.379 | 360.823 | 1.121673 MPa gauge | 1.126769 MPa gauge | 5.096 kPa |
| 100% | 345.365 | 194.154 | 187.793 | 1.121690 MPa gauge | 1.130555 MPa gauge | 8.864 kPa |

## 5. Matched full-mixture 100% comparison set

| Branch | Full-mixture 100% checkpoint | Iterations at full mixture 100% | Signed mass imbalance | L→B | L→S | V→B | V→S | Total liquid m³ | ΔP brine static |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| F02 | — | 0 | — | — | — | — | — | — | — |
| F04 | — | 0 | — | — | — | — | — | — | — |
| F05 | `full-mixture-100pct-end` | 3,000 | -14.336% | 69.655% | 5.907% | 43.267% | 56.854% | 0.360585 | +1.404 kPa |
| F06 | `full-mixture-100pct-end` | 3,000 | -14.382% | 71.393% | 4.171% | 45.545% | 54.463% | 0.427397 | +1.561 kPa |
| F11 | `full-mixture-100pct-end` | 3,000 | -12.377% | 72.586% | 6.364% | 43.996% | 56.039% | 0.391921 | +1.690 kPa |

The three completed endpoints form the valid matched set for a full-mixture, 100%, fixed-3,000-iteration comparison. Mass-flow routing and closure have been calculated from the paired data files. Inventory and brine-entry pressure remain pending, and no scientific conclusion should be drawn from these incomplete physical metrics alone.

## 6. File locations and reproducibility record

Remote branch roots:

```text
C:\Users\syok443\Documents\FluentRuns\03A-stage3\F02\run-20260820T013223Z\
C:\Users\syok443\Documents\FluentRuns\03A-stage3\F04\run-20260820T013223Z\
C:\Users\syok443\Documents\FluentRuns\03A-stage3\F05\run-20260820T013223Z\
C:\Users\syok443\Documents\FluentRuns\03A-stage3\F06\run-20260820T013223Z\
C:\Users\syok443\Documents\FluentRuns\03A-stage3\F11\run-20260820T013223Z\
```

Local orchestration evidence:

- Event log: `native-fixed-3000-events.jsonl` in the local campaign artifact directory for run stamp `20260820T013223Z`
- Resume-state ledger: `native-fixed-3000-resume-state.json` in the same campaign artifact directory
- Endpoint readback records: one `*-readback.json` per extracted full-mixture endpoint in the campaign post-processing artifact directory
- [Stage 3 sweep plan](setup-source.md)

## 7. Required next analysis

1. Retrieve the eight native residual exports through a supported remote file-transfer route, then calculate final 500-iteration residual statistics.
2. Extend the endpoint readback to transition checkpoints if a physically discrete transition plot is required.
3. Plot F11 loading history and the matched 100% branch comparison, marking actual endpoint locations and all stage transitions.

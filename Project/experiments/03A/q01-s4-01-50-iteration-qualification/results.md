# 03A-Q01 — S4-01 50-iteration qualification results

## What ran

Status: completed successfully as one Fluent-native continuation on
`2026-08-27` UTC (`run-stamp=20260827T121534Z`). The exact named S4-01 parent
was loaded explicitly on Fluent Server 2, a case-only prepared child was
written, the prepared case was reloaded with the exact parent data, and one
native journal issued `/solve/iterate 50`. There was no reinitialization, no
Python iteration loop, no journal replay, and no scientific setup delta.

The preflight verified Fluent `2025 R2`, the 18-compute-node route, no other
connected client, and a quiescent session. The endpoint pair is complete and
was reloaded after the run. The native evidence coordinates are cumulative
iteration `33,000` for the inherited parent row followed by exactly 50 new
rows, `33,001` through `33,050`.

The PyFluent connection used the configured Server-2 endpoint with
`FLUENT_INSECURE_MODE=true` because no TLS certificate was configured for that
endpoint. This is a transport/security limitation of the implementation
environment, not a scientific setup change; it is retained here for
reproducibility.

Remote run root:

```text
C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-q01-50iter-20260827T121534Z
```

Endpoint:

```text
Case: C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-q01-50iter-20260827T121534Z\03A-Q01-S4-01-50iter-end-20260827T121534Z.cas.h5
Data: C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-q01-50iter-20260827T121534Z\03A-Q01-S4-01-50iter-end-20260827T121534Z.dat.h5
```

## Evidence / plots / measurements

The local reconciliation directory is the historical machine artifact path
`PyAnsys/output/03a_q01/s4-01-50iter-20260827T121534Z/` (not migrated). The
machine-readable completion manifest is the historical machine artifact path
`PyAnsys/output/03a_q01/s4-01-50iter-20260827T121534Z/completed_50_iteration_native_run.json`
(not migrated); it records the exact paths, hashes, readbacks, native return,
and endpoint reconciliation while the local execution packet is available.

| Evidence | Result |
|---|---|
| Parent case/data | Explicitly loaded; parent SHA-256 matched the contract: case `dfbc0109e910f11f71d9c15956f49a3ab81a015e2d5d7a43f7d366e75aec1126`, data `f52a7f91cbadaa276eab851bde16a0f1c2a92dfa39c7c005517d28f2f8706249` |
| Prepared case | Written and reloaded; SHA-256 `07a7dcd6bf24b1656b95b6410bce82bcb62715bf34c3becf9c409cfe40157384` |
| Endpoint case/data | Both present and reloaded; case SHA-256 `74b1f6746860df7182591c77cc8856dc92da3a28dea0624ecaaed3392522a962`, data SHA-256 `0775e2e40fc4547f4012a80d84b6d8c82ccf57bedd36336d97fed18fd38c0d93` |
| Native transcript | Present; residual table contains 51 rows spanning `33,000` to `33,050` |
| Native residual export | Present; seven equation series with 600 retained points each, spanning `31,902` to `33,050`; the Q01 tail is the 50-point `33,001`–`33,050` window |
| Physical report histories | `30/30` configured report files recovered, each with 51 points at `33,000`–`33,050`; JSON history packet (historical machine artifact path: `PyAnsys/output/03a_q01/s4-01-50iter-20260827T121534Z/report-histories/q01-report-history_20260828_001920.json`; not migrated) and overview plot (historical machine artifact path: `PyAnsys/output/03a_q01/s4-01-50iter-20260827T121534Z/report-histories/q01-report-history_20260828_001920.png`; not migrated) |
| Native autosave | No paired `checkpoint-*` case/data pair was found in the post-run remote directory listing, despite the configured 50-iteration data frequency; the endpoint pair is the retained run output |
| Endpoint flux extraction | Flux check (historical machine artifact path: `PyAnsys/output/03a_q01/s4-01-50iter-20260827T121534Z/analysis/q01-s4-01-50iter-flux-check.json`; not migrated) explicitly reloaded the endpoint case/data and recorded verified identity. It is still a single diagnostic snapshot, not a time-window check; the physical-history extractor was the separate read-only pass that did not load case/data. |

The endpoint scientific readback matched the parent and prepared-case
readbacks: steady pressure-based Mixture, RNG `k-epsilon`, SIMPLE, momentum
under-relaxation `0.3`, active mixture and drift equations, and no DPM
injections. The controlled-delta audit passed. The endpoint reload also passed
the three-sample quiescence check; Fluent's session RP value
`current-iteration=1556` is stale after case/data load and is not used as the
cumulative coordinate.

### Residual evidence

The following values are from the 50 new native residual-export rows only
(`33,001`–`33,050`). They are reported as observed residual values, not as
convergence criteria.

| Equation | First → last | Q01 minimum → maximum |
|---|---:|---:|
| continuity | `0.157492 → 0.164332` | `0.150002 → 0.221104` |
| x-velocity | `2.96850e-05 → 3.04353e-05` | `2.96850e-05 → 3.39069e-05` |
| y-velocity | `2.88707e-05 → 2.99948e-05` | `2.88707e-05 → 3.34546e-05` |
| z-velocity | `3.21265e-05 → 3.20265e-05` | `3.20265e-05 → 3.53980e-05` |
| k | `1.28986e-03 → 1.29431e-03` | `1.28986e-03 → 6.57987e-02` |
| epsilon | `1.95159e-01 → 9.22544e-02` | `8.22696e-02 → 4.83937e+01` |
| vf-phase-2 | `2.22924e-03 → 2.21187e-03` | `2.21187e-03 → 2.24383e-03` |

The `k` and `epsilon` ranges include large within-window excursions. The
residual export is therefore evidence of a completed 50-iteration native
continuation, not evidence of a settled residual state.

### Physical-history measurements

All 30 report histories contain the inherited parent point at `33,000` and
the 50 new points. The tables below show the parent-to-endpoint change; the
range column is the min/max over only the 50 new points. Flux and routing
values retain Fluent's signed orientation.

| Signal | `33,000 → 33,050` | Q01 min–max |
|---|---:|---:|
| Relative mass imbalance | `0.086061 → 0.070222` | `0.069929 → 0.086718` |
| Full-domain mass imbalance [kg/s] | `17.0819 → 13.9381` | `13.8800 → 17.2124` |
| Total liquid mass [kg] | `463.958 → 463.503` | `462.956 → 463.897` |
| Total liquid volume [m³] | `0.526500 → 0.525984` | `0.525363 → 0.526432` |
| Y010 liquid mass [kg] | `302.091 → 301.332` | `300.919 → 302.023` |
| Y030 liquid mass [kg] | `308.965 → 308.224` | `307.826 → 308.899` |
| Brine-entry static pressure [Pa] | `1,121,801 → 1,121,976` | `1,121,782 → 1,122,060` |
| Brine-entry total pressure [Pa] | `1,130,875 → 1,130,663` | `1,130,532 → 1,130,854` |
| Brine-outlet total report [Pa] | `-126.060 → -129.536` | `-129.586 → -126.102` |

The inlet histories are constant over this window at liquid `116.8468 kg/s`,
vapour `81.6395 kg/s`, and total mixture `198.4863 kg/s`. The routing histories
change as follows:

| Signed routing signal [kg/s] | `33,000 → 33,050` |
|---|---:|
| Liquid to brine | `-91.2419 → -94.5862` |
| Liquid to steam | `-8.58912 → -8.52902` |
| Vapour to brine | `-34.8189 → -34.9497` |
| Vapour to steam | `-46.7556 → -46.4841` |

The endpoint live flux snapshot derived `phase-flux efficiency=0.927007`,
steam-outlet vapour fraction `0.844964`, mass imbalance `13.9373 kg/s`, and
mass-imbalance ratio `0.0702177`. The extractor could not discover the
phase-material mapping and used the fallback phase-1=vapour,
phase-2=liquid mapping. That fallback agrees with the endpoint readback
(`water-vapor-at-psep` and `water-liquid-at-psep`), but the extractor warning
means these derived metrics remain diagnostic rather than independently
qualified performance results.

## Numerical state and limitations

Q01 proves that the exact parent can be loaded, continued natively for the
requested 50 iterations, and written as a paired endpoint without changing
the audited scientific state. It does not prove physical convergence or
stationarity. The residual excursions, changing mass imbalance, and movement
in liquid inventories and routing signals are material over this short window.

The parent remains diagnostic/model-development evidence, not a validated or
report-ready separator baseline. This run cannot establish mesh independence,
plant validation, turbulence-model correctness, separator performance, or
that a longer continuation is sufficient. The absence of a paired native
autosave checkpoint and the insecure transport mode are also implementation or
evidence limitations. The current results are not a basis for promoting the
endpoint to a new parent.

## Observations

- The endpoint pair, endpoint hashes, scientific readback, and quiescence
  check are complete.
- The native residual transcript confirms exactly 50 new iterations, while
  the residual export retains a longer history from the loaded session; the
  two coordinate scopes are kept distinct above.
- Relative mass imbalance decreased from `0.086061` to `0.070222`, but the
  Q01 window spans `0.069929`–`0.086718`; this is a bounded observation, not a
  convergence claim.
- Total liquid mass decreased by about `0.455 kg` from the inherited point to
  the endpoint, with a wider within-window range, and both Y010 and Y030
  inventories moved by about `0.76 kg`.
- The pressure histories remain in a narrow band over 50 iterations, but the
  pressure and routing movement is not sufficient to establish stationarity.
- The flux check is partial because the live extractor used a fallback
  phase-material mapping and derived the balance from phase-specific outlet
  fluxes after the mixture mass-flow report was unavailable.

## Findings / interpretation

Interpretation status: diagnostic evidence complete; user-led scientific
review remains required.

The exact S4-01 endpoint is reproducible as a controlled, unchanged
50-iteration continuation and is suitable for evidence review. The observed
residual excursions and physical-history drift do not support calling the
state converged, stationary, report-ready, or qualified as a new parent.
Q01 therefore answers the execution/readback question positively but leaves
the Stage-4 numerical and physical qualification gate open.

## What this implies for the next review

Review the linked transcript, residual export, physical-history packet, and
endpoint manifest as one evidence unit. Keep this run in the diagnostic
03A/S4-01 lineage and do not promote the endpoint or make separator
performance claims from it. Any further continuation or comparison should be
selected explicitly and should retain the same no-delta, native-coordinate,
paired-endpoint evidence requirements.

## Source

[Q01 setup contract](setup.md)

<!-- BEGIN CODEX GENERATED EVIDENCE: post-simulation-analysis -->
## Automated evidence handoff

### What ran
- Run label: `q01-s4-01-50iter`
- Selected checks: `flux`
- Case/data action: `explicit-read_case-then-read_data`

### Run identity / horizon
- Case/data identity: `verified`
  - Basis: explicit case/data load performed by this workflow
  - Case: `C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-q01-50iter-20260827T121534Z\03A-Q01-S4-01-50iter-end-20260827T121534Z.cas.h5`
  - Data: `C:\Users\syok443\Documents\FluentRuns\03A-stage4\S4-01\run-q01-50iter-20260827T121534Z\03A-Q01-S4-01-50iter-end-20260827T121534Z.dat.h5`
- Fluent version: `Ansys Fluent 2025 R2`
- `flux` coordinate: `single live snapshot; Fluent iteration/time unavailable`; horizon: `single live snapshot; no iteration/time window`

### Plots and measured values
| Check | Extraction status | Scope / coordinate | Measured values | Artifacts |
|---|---|---|---|---|
| `flux` | `partial` | zones liquidinlet, steaminlet, steamoutlet, brineoutlet; domains phase-1, phase-2; single live snapshot; Fluent iteration/time unavailable | liquid inlet mass flow=116.847 kg/s; vapor inlet mass flow=81.6395 kg/s; steam-outlet liquid mass flow=8.52902 kg/s; steam-outlet vapor mass flow=46.4841 kg/s; phase-flux efficiency=0.927007 dimensionless; steam-outlet vapor fraction=0.844964 dimensionless; mass imbalance=13.9373 kg/s; mass imbalance ratio=0.0702177 dimensionless; signed Fluent fluxes: phase-1/Net=0.205708 kg/s, phase-1/brineoutlet=-34.9497 kg/s, phase-1/liquidinlet=-0 kg/s, phase-1/steaminlet=81.6395 kg/s, phase-1/steamoutlet=-46.4841 kg/s, phase-2/Net=13.7315 kg/s, phase-2/brineoutlet=-94.5862 kg/s, phase-2/liquidinlet=116.847 kg/s, phase-2/steaminlet=-0 kg/s, phase-2/steamoutlet=-8.52902 kg/s | Flux check (historical machine artifact path: `PyAnsys/output/03a_q01/s4-01-50iter-20260827T121534Z/analysis/q01-s4-01-50iter-flux-check.json`; not migrated) explicitly reloaded the endpoint case/data and recorded verified identity. It is still a single diagnostic snapshot, not a time-window check; the physical-history extractor was the separate read-only pass that did not load case/data. |
- `flux` evidence note: The by-domain values retain Fluent's signed zone orientation; carrier metrics above use absolute mass-flow magnitudes.
- `flux` evidence note: Mass-balance scope recorded by the extractor: all_discovered_pressure_outlets; Computed from both discovered pressure outlets, including the physical brine outlet; use as a diagnostic balance check, not as the sole convergence criterion..
- `flux` evidence note: Mass-balance note: Derived from phase-specific fluxes across both pressure outlets because the mixture mass-flow report was unavailable.

### Numerical state
- Extraction status is separate from scientific adequacy; this packet does not declare convergence, validation, or parent eligibility.
- `flux`: Instantaneous signed mass-flow evidence was captured; no iteration or physical-time history was available for a stability assessment.

### Missing/incomplete evidence
- `flux`: Could not discover phase-material mapping from the live state; using fallback phase-1=vapor, phase-2=liquid.

### Neutral observations
- `flux`: The captured report scope contains 4 zone(s) and 2 domain(s).
- `flux`: Derived metrics and signed source values are reported separately; no ranking or acceptance decision is made.
- This generated block records evidence only. It does not choose a preferred case or model, assign a scientific finding, or select the next experiment.
<!-- END CODEX GENERATED EVIDENCE: post-simulation-analysis -->

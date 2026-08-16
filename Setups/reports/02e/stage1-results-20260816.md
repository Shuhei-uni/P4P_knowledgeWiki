# Setup 02e Stage-1 results — 2026-08-16

Status: **Stage 1 complete; Stage 2 not generated.**

Interpretation status: **execution and evidence-quality results are recorded;
physical interpretation and outlet selection remain pending user direction.**

This report covers the original `Full-geomV2-231kcells.msh.h5` campaign. The
four-case 275k-mesh retry is a short, separate note near the end and is not
mixed into the original 12-case comparison.

## Executive Stage-1 outcome

Twelve Stage-1 pilot calculations were attempted from independently built
children of the common Y010 initialization. Four reached the planned 500
iterations and eight terminated with floating-point exceptions. The recovered
native report histories also correct an earlier provisional status: `MF-P3`
terminated at iteration 254 rather than completing 500. No outlet family
produced three complete pilot histories suitable for the prescribed
three-point adaptive Stage-2 rule.

Stage 1 therefore provides useful evidence about build lineage,
parameter-dependent numerical survivability, and the evolution of the Y010 and
Y030 liquid inventories. It still does **not** provide a complete four-family
liquid-balance response characterization: the total-domain liquid history was
not configured as a native report, and the original `EF-P1` report history was
not preserved. The recovered values for the other 11 original cases are
reported below with their exact measurement basis.

## 1. Purpose and experimental matrix

Setup 02e was intended to compare four built-in brine-outlet formulations while
holding the Mixture model, inlet conditions, steam outlet, numerical settings,
mesh, and initialized lower liquid state fixed. Each family had three pilot
controls:

| Family | Pilot controls |
|---|---|
| Pressure Outlet (`PO`) | `1.160`, `1.200`, `1.240 MPa` gauge |
| Outlet Vent (`OV`) | `K=0`, `K=10`, `K=100` |
| Mass-Flow Outlet (`MF`) | `58.4235`, `116.847`, `233.694 kg/s` liquid; vapour target `0 kg/s` |
| Exhaust Fan (`EF`) | `-50`, `0`, `+50 kPa` pressure jump |

Every child was intended to receive one Fluent-native `/solve/iterate 500`
command. A failed case remains a failed numerical experiment; it was not
rescued by changing relaxation factors, discretization, turbulence settings,
materials, inlet conditions, or steam-outlet conditions.

## 2. Common initialized state

All 12 original children were built independently from the saved Y010 parent.
The parent readback recorded:

| Quantity | Measured value |
|---|---:|
| Mesh cells | `231,376` |
| Y010 selected cells | `33,315` |
| Y010 geometric selected-cell volume | `4.829410214 m³` |
| Initial Y010 liquid volume, `V_l,Y010(0)` | `4.790652590 m³` |
| Initial Y010 liquid mass | `4224.253734 kg` |

The official initial liquid reference for the campaign is therefore:

\[
V_{l,Y010}(0)=4.790652590\ \mathrm{m^3}.
\]

The geometric register volume is not the same as the liquid volume because the
patched field does not fill every selected cell completely. The initialized
parent snapshot contains the Y030 report definition. It does not contain a
total-domain liquid report definition or a numeric initial total-domain liquid
value. The native history files recovered from the Student host are
liquid-mass reports; the liquid volumes below are derived as `mass / 881.77
kg·m⁻³`.

The inventory measurements have three different meanings and must not be
collapsed into one “drainage” number:

```text
Y010 liquid inventory change
    → movement out of the originally patched lower region

Y030 liquid inventory change
    → movement out of the broader y ≤ 0.30 m lower-region monitor

total-domain liquid inventory change
    → net liquid accumulation or depletion in the computational domain

phase outlet fluxes
    → measured liquid/vapour routing through the boundaries
```

A decrease in Y010 alone cannot establish that liquid left the domain; it may
only indicate redistribution above the Y010 cutoff. Y030, total liquid, and
phase-separated outlet fluxes are required to distinguish those possibilities.

## 3. Execution outcome and evidence quality

The statuses below are the native Stage-1 run outcomes established from the
queue continuation records and preserved Fluent-side execution evidence.

`COMPLETE_500` means that the native 500-iteration command reached its planned
iteration count. `FAILED_FPE` means that Fluent terminated with a
floating-point exception before iteration 500. The recovered report history
and transcript establish `OV-P2` at iteration 448 and `MF-P3` at iteration 254.

| Case | Control | Run status | Iterations reached | Local endpoint / monitor evidence | Formal Stage-2 use |
|---|---:|---|---:|---|---|
| `PO-P1` | `1.160 MPa` | `COMPLETE_500` | 500 | Endpoint plus Y010/Y030/phase-flux histories recovered | No — family incomplete |
| `PO-P2` | `1.200 MPa` | `FAILED_FPE` | 335 | Transcript/failure evidence; no valid final-100 endpoint | No |
| `PO-P3` | `1.240 MPa` | `FAILED_FPE` | 226 | Transcript/failure evidence; no valid final-100 endpoint | No |
| `OV-P1` | `K=0` | `COMPLETE_500` | 500 | Endpoint plus Y010/Y030/phase-flux histories recovered | No — family incomplete |
| `OV-P2` | `K=10` | `FAILED_FPE` | 448 | Transcript plus Y010/Y030/phase-flux histories recovered; no valid final-100 endpoint | No |
| `OV-P3` | `K=100` | `FAILED_FPE` | 457 | Transcript/failure evidence; no valid final-100 endpoint | No |
| `MF-P1` | `58.4235 kg/s` | `FAILED_FPE` | 33 | Transcript/failure evidence; no valid final-100 endpoint | No |
| `MF-P2` | `116.847 kg/s` | `FAILED_FPE` | 9 | Transcript/failure evidence; no valid final-100 endpoint | No |
| `MF-P3` | `233.694 kg/s` | `FAILED_FPE` | 254 | Transcript plus Y010/Y030/phase-flux histories recovered; no valid final-100 endpoint | No |
| `EF-P1` | `-50 kPa` | `FAILED_FPE` | 254 | FPE outcome recorded; original inventory/flux report history not preserved | No |
| `EF-P2` | `0 kPa` | `COMPLETE_500` | 500 | Endpoint plus Y010/Y030/phase-flux histories recovered | No — family incomplete |
| `EF-P3` | `+50 kPa` | `COMPLETE_500` | 500 | Endpoint plus Y010/Y030/phase-flux histories recovered | No — family incomplete |

Overall: **4/12 cases completed 500 iterations; 8/12 ended in FPEs.** The
completed cases were `PO-P1`, `OV-P1`, `EF-P2`, and `EF-P3`.

The recovered native report files now provide machine-readable Y010/Y030 and
phase-separated flux histories for 11 original cases. `EF-P1` has no preserved
original report-history file. The total-domain liquid report is unavailable for
all cases because that report was not present in the saved monitor package.

## 4. Numerical survivability across the pilot matrix

The following are numerical observations only. They are not physical outlet
performance rankings and do not establish a causal pressure/control law.

| Family | Low/first pilot | Middle pilot | High/third pilot | Observed survivability pattern |
|---|---|---|---|---|
| `PO` | `P1`: 500 | `P2`: FPE at 335 | `P3`: FPE at 226 | The two higher-pressure pilots terminated earlier than `P1` in this screen. |
| `OV` | `P1`: 500 | `P2`: FPE at 448 | `P3`: FPE at 457 | `P1` completed; the two loss-coefficient pilots did not. |
| `MF` | `P1`: FPE at 33 | `P2`: FPE at 9 | `P3`: FPE at 254 | All three mass-flow pilots terminated before 500; `P3` survived longer than `P1` and `P2` but did not complete. |
| `EF` | `P1`: FPE at 254 | `P2`: 500 | `P3`: 500 | The negative pressure-jump pilot failed; zero and positive jumps completed. |

The patterns are valuable for diagnosing the numerical operating envelope, but
they are not substitutes for the required liquid-balance values
`L₁`, `L₂`, and `L₃`. A three-point response direction cannot be inferred from
survival status alone.

## 5. Liquid inventory and phase-flux results

### 5.1 Recovered native histories and measurement basis

The Student-host report-history files were recovered without loading or
altering the active Fluent session. The histories contain liquid mass in the
Y010 and Y030 registers and phase-separated mass-flow reports. The liquid
volume values below are derived using the frozen liquid density
`881.77 kg/m³`:

\[
V_l = \frac{M_l}{881.77\ \mathrm{kg/m^3}}.
\]

For complete cases, inventory-window statistics use iterations `401–500`.
For FPE cases, the endpoint is the last valid report point and the displayed
window statistics use the last 20 valid points, or the complete available
history when fewer than 20 points exist. These two bases are not treated as
equivalent convergence statistics.

Native Fluent outlet fluxes are negative for outward flow in these reports. The
tables use the Setup 02e outward-positive convention:

\[
\dot m_{outward-positive}=-\dot m_{native,outlet}.
\]

The total-domain liquid history remains unavailable because no total-domain
liquid report file was created. The original `EF-P1` report history is also not
preserved, so that case remains explicitly unavailable in the tables.

### 5.2 Recovered inventory values and trends

The table reports the last valid inventory, its change from the common parent
baseline, and the statistics over the appropriate window. Values are derived
liquid volumes; the machine-readable summary also retains the source liquid
masses.

| Case | Basis | Y010 last m³ | ΔY010 m³ (%) | Y010 window mean [min, max] m³ | Y010 final-window trend | Y030 last m³ | ΔY030 m³ (%) | Y030 window mean [min, max] m³ | Y030 final-window trend | Total liquid |
|---|---|---:|---:|---|---|---:|---:|---|---|---|
| `PO-P1` | 401–500 | 3.184082 | −1.606571 (−33.54%) | 3.222853 [3.184082, 3.247247] | bounded; slope −2.955e−4 m³/iter | 3.519948 | −1.270705 (−26.52%) | 3.567507 [3.519948, 3.596514] | bounded; slope −5.239e−4 | unavailable |
| `PO-P2` | last 20, 316–335 | 3.504458 | −1.286195 (−26.85%) | 3.752816 [3.504458, 3.876120] | decreasing; slope −1.505e−2 | 3.910319 | −0.880333 (−18.38%) | 4.152270 [3.910319, 4.273223] | decreasing; slope −1.420e−2 | unavailable |
| `PO-P3` | last 20, 207–226 | 4.021516 | −0.769136 (−16.05%) | 4.107872 [3.928760, 4.421028] | increasing before FPE; slope +1.802e−2 | 4.439510 | −0.351143 (−7.33%) | 4.533391 [4.347701, 4.881701] | increasing before FPE; slope +1.838e−2 | unavailable |
| `OV-P1` | 401–500 | 1.048469 | −3.742183 (−78.11%) | 1.222061 [1.048469, 1.316526] | decreasing; slope −2.792e−3 | 1.120053 | −3.670600 (−76.62%) | 1.285422 [1.120053, 1.372972] | decreasing; slope −2.453e−3 | unavailable |
| `OV-P2` | last 20, 429–448 | 3.268832 | −1.521821 (−31.77%) | 3.077519 [2.974019, 3.268832] | decreasing; slope −2.471e−3 | 3.540378 | −1.250274 (−26.10%) | 3.324396 [3.197002, 3.540378] | decreasing; slope −2.705e−3 | unavailable |
| `OV-P3` | last 20, 438–457 | 3.836424 | −0.954228 (−19.92%) | 3.809061 [3.625820, 3.836424] | bounded/oscillatory; slope −2.185e−3 | 4.234491 | −0.556162 (−11.61%) | 4.199134 [4.003533, 4.234491] | bounded/oscillatory; slope −1.966e−3 | unavailable |
| `MF-P1` | last 20, 14–33 | 4.359627 | −0.431026 (−9.00%) | 4.714324 [4.359627, 4.792079] | decreasing; slope −1.137e−2 | 4.831079 | +0.040427 (+0.84%) | 5.206038 [4.831079, 5.288516] | decreasing before FPE; slope −1.170e−2 | unavailable |
| `MF-P2` | last 9, 1–9 | 4.072051 | −0.718602 (−15.00%) | 4.535037 [4.072051, 4.679685] | decreasing; slope −4.581e−2 | 4.203286 | −0.587367 (−12.26%) | 4.626683 [4.203286, 4.867417] | decreasing; slope −2.714e−2 | unavailable |
| `MF-P3` | last 20, 235–254 | 2.815726 | −1.974926 (−41.22%) | 2.734901 [2.602452, 2.853737] | bounded/oscillatory before FPE; slope −1.166e−2 | 3.093426 | −1.697226 (−35.43%) | 2.989507 [2.849283, 3.115099] | bounded/oscillatory before FPE; slope −1.193e−2 | unavailable |
| `EF-P1` | no preserved history | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable |
| `EF-P2` | 401–500 | 1.032552 | −3.758101 (−78.45%) | 1.212185 [1.032552, 1.305604] | decreasing; slope −2.858e−3 | 1.103924 | −3.686728 (−76.96%) | 1.275465 [1.103924, 1.361666] | decreasing; slope −2.512e−3 | unavailable |
| `EF-P3` | 401–500 | 0.492739 | −4.297914 (−89.71%) | 0.575353 [0.492739, 0.740206] | decreasing; slope −1.805e−3 | 0.521181 | −4.269471 (−89.12%) | 0.603807 [0.521181, 0.772233] | decreasing; slope −1.821e−3 | unavailable |

The plot below shows the recovered Y010 and Y030 histories. Solid lines are
500-iteration cases; dashed lines are pre-FPE histories. Circle and square
markers identify the last Y010 and Y030 values, respectively. The horizontal
line is the common Y010 parent baseline.

![Recovered Setup 02e Stage-1 Y010 and Y030 liquid inventory histories](../../../PyAnsys/output/02e_stage1_recovered_reports_20260816/02e_stage1_inventory_histories_20260816.png)

### 5.3 Recovered phase fluxes and liquid balance

For complete cases, flux values are arithmetic means over iterations `401–500`.
For failed cases, the table shows the last valid point only. The failed-case
flux values that have grown to `10²⁷–10⁵⁸ kg/s` are numerical blow-up
diagnostics, not physical flow estimates and must not be used as endpoint
physics.

The branching quantity is:

\[
L=\bar{\dot m}_{l,in}-\bar{\dot m}_{l,brine}-\bar{\dot m}_{l,steam}.
\]

| Case | Flux basis | Liquid in kg/s | Liquid → brine kg/s | Liquid → steam kg/s | `L` kg/s | Vapour → brine kg/s | Vapour → steam kg/s | Flux interpretation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `PO-P1` | 401–500 | 116.921 | 2063.635 | 271.604 | −2218.318 | 8.027 | 57.922 | Finite complete-run balance; `L<0` indicates measured liquid depletion for branch navigation |
| `PO-P2` | last valid point, 335 | 116.921 | −5.837e54 | 0 | +5.837e54 | 5.240e54 | −1.447e41 | Numerical blow-up immediately before FPE; not physical |
| `PO-P3` | last valid point, 226 | 116.921 | −2.550e31 | 4.921e52 | −4.921e52 | 0 | −8.813e52 | Numerical blow-up immediately before FPE; not physical |
| `OV-P1` | 401–500 | 116.921 | 696.923 | 1.024 | −581.026 | 12.446 | 64.315 | Finite complete-run balance; `L<0` |
| `OV-P2` | last valid point, 448 | 116.921 | −1.448e41 | 8.110e54 | −8.110e54 | 0 | −1.022e55 | Numerical blow-up immediately before FPE; not physical |
| `OV-P3` | last valid point, 457 | 116.921 | −4.204e58 | 0 | +4.204e58 | 0 | −5.918e57 | Numerical blow-up immediately before FPE; not physical |
| `MF-P1` | last valid point, 33 | 116.921 | 31.648 | 3.386e41 | −3.386e41 | 0.174 | 7.866e56 | Numerical blow-up immediately before FPE; not physical |
| `MF-P2` | last valid point, 9 | 116.921 | 0 | 1.121e21 | −1.121e21 | 0 | 1.035e45 | Numerical blow-up immediately before FPE; not physical |
| `MF-P3` | last valid point, 254 | 116.921 | 155.640 | 0 | −38.719 | 0.507 | −9.293e45 | Liquid fluxes remain finite at the last report point, but the case still fails at 254 and vapour-to-steam is already corrupted |
| `EF-P1` | no preserved history | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | FPE outcome known; phase-flux history unavailable |
| `EF-P2` | 401–500 | 116.921 | 694.980 | 1.082 | −579.141 | 12.427 | 64.343 | Finite complete-run balance; `L<0` |
| `EF-P3` | 401–500 | 116.921 | 683.589 | 1.195 | −567.863 | 30.353 | 46.665 | Finite complete-run balance; `L<0` |

The finite complete cases all have strongly negative measured `L` values and
simultaneously declining Y010/Y030 inventories. That is internally consistent
with net liquid depletion of the monitored lower region and measured liquid
outflow exceeding liquid inflow. It is still an experimental numerical
observation, not a claim that the formulation is physically correct or
converged.

The failed cases show why their pre-FPE histories must be retained but not
treated as endpoints. Their inventory values remain finite and interpretable as
last-valid/pre-FPE evidence, while several phase-flux reports diverge by many
orders of magnitude immediately before the exception.

### 5.4 Reproducible recovered-data artifacts

- Machine-readable summary:
  [`02e_stage1_inventory_flux_summary_20260816.json`](../../../PyAnsys/output/02e_stage1_recovered_reports_20260816/02e_stage1_inventory_flux_summary_20260816.json)
- Compact comparison CSV:
  [`02e_stage1_inventory_flux_summary_20260816.csv`](../../../PyAnsys/output/02e_stage1_recovered_reports_20260816/02e_stage1_inventory_flux_summary_20260816.csv)
- Offline extraction script:
  [`analyze_02e_stage1_histories.py`](../../../PyAnsys/scripts/inspection/analyze_02e_stage1_histories.py)

The raw recovered `.out` report histories remain in the linked output bundle.
They were copied read-only from the Student host and were not regenerated by
running Fluent.

## 6. Failure diagnostics

The FPEs are a material Stage-1 result. The preserved native evidence includes
floating-point exceptions and, in the available failure diagnostics,
reversed-flow and turbulent-viscosity-limiting warnings before terminal
failure. The observed residual behavior is consistent with difficult or
unstable numerical evolution immediately before some failures.

These diagnostics support statements such as:

- higher-pressure `PO` pilots terminated earlier than `PO-P1`;
- the lower-flow `MF` pilots failed at iterations 33 and 9, while `MF-P3`
  survived to iteration 254 before also failing;
- `EF-P1` failed while `EF-P2` and `EF-P3` completed; and
- failure occurred before the prescribed 500-iteration endpoint for eight
  pilots.

They do **not** support statements that a case physically drained, retained,
or accumulated liquid. Those claims require the inventory and phase-flux
histories.

## 7. What went well

- The frozen 231k production mesh and common Y010 parent were established before
  the children were built. The parent readback preserved the selected-cell
  count, geometric volume, liquid volume, and liquid mass.
- All 12 requested Stage-1 children passed build/readback and were written as
  paired pre-run case/data artifacts from the same initialized parent. This
  preserves the intended same-initial-state comparison.
- The native-run contract was respected: each child was intended to run one
  Fluent-native 500-iteration command, and later queue continuations used
  untouched pre-run children rather than solved cases.
- Four pilots reached the planned 500-iteration endpoint, giving one complete
  run in `PO`, one in `OV`, none in `MF`, and two in `EF`.
- Failure evidence was retained rather than converted into fabricated physical
  results. The queue journals, local build records, monitor read-only snapshots,
  Student-host transcript references, and the recovered native report histories
  remain available.
- The Stage-2 gate was applied conservatively. No family was assigned a
  response direction from only one or two surviving points, and no Stage-2
  case was generated or submitted.

## 8. What did not go well / evidence limitations

- Eight of the twelve pilots terminated with floating-point exceptions before
  the required endpoint.
- No family has three complete 500-iteration pilots. This alone prevents the
  required three-point Stage-2 classification.
- The total-domain liquid history was not configured as a native report, and
  the original `EF-P1` Y010/Y030/phase-flux report history was not preserved.
  Those two evidence gaps prevent a complete all-12-case inventory comparison,
  but the other 11 cases are now populated from recovered native histories.
- The native queue required several cautious continuations after failures. An
  earlier launcher also encountered a post-Fluent manifest-serialization error
  after an endpoint write; the endpoint evidence was retained, but the handoff
  was not clean for that queue.
- The available live monitor snapshot is a read-only residual/progress record;
  the report now uses the separate native `.out` history exports for the
  inventory and flux values.

## 9. Stage-2 eligibility decision

Setup 02e permits automatic Stage 2 only when all three pilots in a family
provide usable histories and final-100 phase-flux averages. The eligibility
result is:

| Family | P1 complete 500? | P2 complete 500? | P3 complete 500? | Complete three-point family? | Stage-2 decision |
|---|---|---|---|---|---|
| `PO` | Yes | No | No | No | `STAGE2_NOT_GENERATED` |
| `OV` | Yes | No | No | No | `STAGE2_NOT_GENERATED` |
| `MF` | No | No | No | No | `STAGE2_NOT_GENERATED` |
| `EF` | No | Yes | Yes | No | `STAGE2_NOT_GENERATED` |

Therefore:

\[
\boxed{\text{No outlet family satisfied the formal Stage-2 gate.}}
\]

No Stage-2 controls, Stage-2 child artifacts, or Stage-2 queue were generated
from this Stage-1 campaign. This is a data-quality decision, not a physical
ranking of the outlet formulations.

## 10. Brief 275k-mesh retry note

Four selected cases—`PO-P2`, `OV-P2`, `MF-P2`, and `EF-P1`—were retried on
`brine-outlet-275kcells.msh.h5` with 275,448 cells. All four again terminated
with native floating-point exceptions and produced no usable complete
endpoint. The retry therefore did not establish improved endpoint robustness.
It remains a separate recovery experiment and does not alter the original
231k-mesh Stage-1 matrix or its Stage-2 decision. See
[mesh-275k-retry-20260816.md](mesh-275k-retry-20260816.md) for its detailed
record.

## 11. Evidence and lineage

- Governing setup:
  [`02e-mixture-y010-brine-outlet-boundary-characterization.md`](../../active/02e-mixture-y010-brine-outlet-boundary-characterization.md)
- Initialized 231k parent snapshot:
  [`02e_y010_parent_20260816T063000Z.json`](../../../PyAnsys/output/02e_y010_parent_20260816T063000Z.json)
- Complete Stage-1 child-build snapshot:
  [`02e_stage1_all_build_20260816T064500Z.json`](../../../PyAnsys/output/02e_stage1_all_build_20260816T064500Z.json)
- Stage-1 read-only monitor snapshot:
  [`02e_stage1_monitor_state.json`](../../../PyAnsys/output/02e_stage1_monitor_state.json)
- Initial native queue journal:
  [`02e_stage1_native_queue_20260816T071500Z.jou`](../../../PyAnsys/output/02e_stage1_native_queue_20260816T071500Z.jou)
- Existing execution/continuation record:
  [`stage1-execution-20260816.md`](stage1-execution-20260816.md)
- Recovered native report-history summary:
  [`02e_stage1_inventory_flux_summary_20260816.json`](../../../PyAnsys/output/02e_stage1_recovered_reports_20260816/02e_stage1_inventory_flux_summary_20260816.json)
- Separate 275k retry record:
  [`mesh-275k-retry-20260816.md`](mesh-275k-retry-20260816.md)

The native queue journals reference Student-host transcripts and endpoint
case/data paths. The small native report-history files used for the populated
tables were copied read-only into the linked recovery bundle. The original
`EF-P1` report history and the total-domain liquid report remain unavailable.

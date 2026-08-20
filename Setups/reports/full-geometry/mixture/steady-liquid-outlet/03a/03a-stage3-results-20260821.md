# 03A Stage-3 Results — F01–F12 evidence report

> **Campaign:** 03A Stage-3 — Fluent-Recommended Convergence Sweep  
> **Branches:** F01–F12  
> **Physical case:** unchanged 03A full-geometry steady Mixture case  
> **Evidence model:** residual histories plus discrete physical measurements from paired `.cas.h5`/`.dat.h5` checkpoints  
> **Interpretation status:** pending user direction

This report is an evidence packet. It records execution validity, checkpoint lineage, physical readback, and residual-window evidence. It does not select a best branch, claim physical settlement, or call a branch converged.

> **Final-report handoff (2026-08-21):** keep this document as the Stage-3 checkpoint/provenance evidence layer. Build the final scientific results report from the continuous stitched residual histories and recovered Fluent Report File histories using [`03a-stage3-results-analysis-and-plotting-plan.md`](./03a-stage3-results-analysis-and-plotting-plan.md) and [`03a-stage3-final-results-template.md`](./03a-stage3-final-results-template.md). Checkpoint values remain cross-check anchors and must not be treated as sufficient evidence of steady state on their own.

## 1. Evidence conventions

- Attempts remain separate by run stamp. Earlier F02/F04 floating-point-error attempts are not merged into the later `20260820T013223Z` partial attempts.
- The signed total mass imbalance in this report is exactly

  `100 × (total outlet − total inlet) / total inlet`.

- Values above `100%` are retained. They are not capped.
- Carrier-only checkpoints have phase-routing and liquid-inventory fields recorded as `N/A`.
- Physical values are checkpoint measurements. Any connecting line in a future plot is a guide to the eye only.
- The pressure margin is `entry static pressure − 1,120,000 Pa`.
- The physical-readback checkpoint table is [03a-stage3-results-20260821-checkpoints.csv](03a-stage3-results-20260821-checkpoints.csv). It contains the 23 full-Mixture checkpoints read back in this pass; carrier-only and hybrid pairs remain in the execution inventory with physical fields `N/A`. Values in the CSV are rounded to six decimal places; the paired checkpoint and execution artifacts remain the lineage authority.

The immutable monitor-ready P0 identity used by the independent branches was recorded as SHA-256:

```text
8b9489d745a9539bfa36ffdca0fe224331fce749c331f08f6b0fc1ad6f386301
```

## 2. Overall execution summary

| Branch | Run stamp | Stages reached | Highest load | Total iterations | Iterations at 100% | Last valid checkpoint | Terminal status |
|---|---|---|---:|---:|---:|---|---|
| F01 | legacy supervised record | 100% final stage; failure after 5,704 logged | 100% | 5,500 valid; 5,704 logged before FPE | 5,500 | `F01-autosave-2-05500.dat.h5` | `NUMERICAL_FAILURE` |
| F02 | `20260820T013223Z` | hybrid initialization; carrier-100% attempt | carrier 100% | 0 native iterations confirmed | 0 full Mixture | hybrid-initialized pair | `PARTIAL` |
| F03 | `20260820T054645Z` | full Mixture at 100% | 100% | 5,000 | 5,000 | `F03-100pct-final-5000...dat.h5` | `COMPLETED` |
| F04 | `20260820T013223Z` | hybrid initialization; carrier-100% attempt | carrier 100% | 0 native iterations confirmed | 0 full Mixture | hybrid-initialized pair | `PARTIAL` |
| F05 | `20260820T013223Z` | full Mixture at 100% | 100% | 3,000 | 3,000 | `F05-full-mixture-100pct-end...dat.h5` | `COMPLETED` |
| F06 | `20260820T013223Z` | carrier 100%; full Mixture 100% | 100% | 6,000 | 3,000 | `F06-full-mixture-100pct-end...dat.h5` | `COMPLETED` |
| F07 | `20260820T002135Z` | confirmed 10%, 20%; 40% pair present but stage unconfirmed | 40% attempted | 6,150 confirmed; 9,150 pair present | 0 | `F07-20pct-end-iter006150...dat.h5` | `TRANSPORT_BLOCKED` |
| F08 | `20260820T044148Z`; retry `20260820T054146Z` | verified 20% source; 40% continuation | 40% | 12,000 | 0 | `F08-full-mixture-40pct-iter012000...dat.h5` | `NUMERICAL_FAILURE` |
| F09 | `20260820T082047Z` | 10%, 20%, 40%, 80%, 100% | 100% | 15,000 | 3,000 | `F09-100pct-end-iter015000...dat.h5` | `COMPLETED` |
| F10 | `20260820T055022Z`; prep `20260820T054449Z` | hybrid initialization; carrier-10% attempt | carrier 10% | 0 native iterations confirmed | 0 full Mixture | hybrid-initialized pair | `NUMERICAL_FAILURE` |
| F11 | `20260820T013223Z` | 10%, 20%, 40%, 80%, 100% | 100% | 15,000 | 3,000 | `F11-full-mixture-100pct-end...dat.h5` | `COMPLETED` |
| F12 | `20260820T073316Z` | carrier 10%; full Mixture 10%, 20%, 40%, 80%, 100% | 100% | 18,000 | 3,000 | `F12-full-mixture-100pct-iter018000...dat.h5` | `COMPLETED` |

The fixed-block branches end after 3,000 iterations at 100%. They are fixed-block results and do not satisfy the separate authority request for at least 5,000 iterations at 100%.

## 3. Branch records

### F01 — full Mixture immediately, 100% immediately, URF 0.7

- **Role:** canonical long-run control; Schedule A.
- **Execution:** valid full-Mixture 100% checkpoint at iteration 5,500. The reassessment then showed AMG divergence, catastrophic residual escalation, extensive viscosity limiting, and an explicit floating-point exception after logged iteration 5,704.
- **Last valid pair:** `C:\Temp\03A-stage3-F01\F01-autosave-2.cas.h5` and `F01-autosave-2-05500.dat.h5`.
- **Factual checkpoint observation:** total outlet flow was `385.264 kg/s` against `198.486 kg/s` inlet, giving `+94.101%` under the signed convention used here. Liquid-to-brine routing was `239.378%` of liquid inlet and liquid closure was `+161.194%`.
- **Residual evidence:** full residual history to 5,500 is available. In the final 500-iteration window, continuity was approximately stationary while `k` and epsilon trended downward; this did not prevent the later numerical failure.

### F02 — carrier-first, 100% immediately, URF 0.7

- **Role:** isolate carrier-first Mixture staging against F01.
- **Execution:** the later fixed-block attempt completed hybrid initialization, then returned a terminal Fluent-native `Error Object: #f` during the carrier-100% stage before the named endpoint pair was written.
- **Status:** `PARTIAL`, not `NUMERICAL_FAILURE`; the ledger records no FPE for this attempt. A separate earlier F02 attempt has an FPE, but it is a different run and is not combined here.
- **Physical evidence:** no full-Mixture checkpoint; phase-routing and inventory quantities are `N/A`.

### F03 — full Mixture immediately, 100% immediately, URF 0.5

- **Role:** immediate full-Mixture comparison at moderate momentum damping; Schedule A.
- **Execution:** 5,000 native iterations completed. A transport/client interruption occurred around cumulative iteration 1,000 and was recovered by continuation without reinitialization or duplicate solving.
- **Last valid pair:** `C:\Temp\03A-stage3-F03\F03-100pct-final-5000-end-iter005000-supervised-20260820T054645Z.{cas,dat}.h5`.
- **Factual checkpoint observation:** the final outlet flow was `866.164 kg/s` against `198.486 kg/s` inlet, or `+336.385%` signed imbalance. The entry static pressure margin was `−19.415 kPa`.
- **Residual evidence:** the endpoint retained 500 residual points spanning iterations 2,312–5,000. Continuity and `k` trended upward; epsilon trended downward. These statistics are not a convergence claim.

### F04 — carrier-first, 100% immediately, URF 0.5

- **Role:** isolate carrier-first staging at URF 0.5.
- **Execution:** the later fixed-block attempt reached hybrid initialization, then returned terminal Fluent-native `Error Object: #f` during the carrier-100% stage before a named endpoint pair.
- **Status:** `PARTIAL`, not `NUMERICAL_FAILURE`; the ledger records no FPE for this attempt. A separate earlier F04 attempt has an FPE and remains separate.
- **Physical evidence:** no full-Mixture checkpoint; phase-routing and inventory quantities are `N/A`.

### F05 — full Mixture immediately, 100% immediately, URF 0.3

- **Role:** immediate full-Mixture comparison at strong momentum damping; Schedule A.
- **Execution:** one native 3,000-iteration full-Mixture 100% block completed.
- **Checkpoint:** `F05-full-mixture-100pct-end-20260820T013223Z.{cas,dat}.h5`.
- **Factual checkpoint observation:** signed total imbalance was `−14.336%`; liquid closure was `−24.438%`; entry static pressure margin was `+1.404 kPa`.
- **Residual evidence:** the native residual export is present remotely, but its final 500-iteration window has not yet been transferred and reduced.

### F06 — carrier-first, 100% immediately, URF 0.3

- **Role:** carrier-first comparison at strong momentum damping.
- **Execution:** the carrier 100% block completed at 3,000 iterations, followed by a no-reinitialization full-Mixture 100% block completing at cumulative iteration 6,000.
- **Checkpoint:** `F06-full-mixture-100pct-end-20260820T013223Z.{cas,dat}.h5`.
- **Factual checkpoint observation:** signed total imbalance was `−14.382%`; liquid closure was `−24.436%`; entry static pressure margin was `+1.561 kPa`.
- **Residual evidence:** native residual exports are present; final 500-iteration statistics remain to be extracted.

### F07 — full Mixture progressive loading, URF 0.7

- **Role:** progressive-loading comparison without carrier-first staging.
- **Execution:** 10% and 20% stages are confirmed complete at cumulative iterations 3,150 and 6,150. The 40% pair at iteration 9,150 exists and was read back, but the event log lost its transport stream before recording stage completion and reconciliation could be completed.
- **Status:** `TRANSPORT_BLOCKED`, not `NUMERICAL_FAILURE`.
- **Factual checkpoint observations:** the confirmed 20% checkpoint had `+1.212%` signed imbalance; the unconfirmed 40% pair had `+21.054%`. Both values are retained with their evidence-status distinction.
- **Residual evidence:** final-window statistics are available for the 10%, 20%, and pair-present 40% checkpoints. The 40% statistics are not evidence that the 40% stage completed.

### F08 — carrier-first progressive loading, URF 0.7

- **Role:** combined principal staging strategy; recovery continuation from the verified 20% endpoint.
- **Execution:** the verified 20%/9,000 checkpoint was continued to a valid 40%/12,000 checkpoint. The 80% native block failed with `Error Object: #f`; a retry from the same valid 40% state failed in the same way. No 80% pair exists.
- **Source pair:** `C:\Users\syok443\Documents\FluentRuns\03A-stage3\F08\F08-full-mixture-20pct-iter009000-20260819T061715Z.{cas,dat}.h5`.
- **Status:** `NUMERICAL_FAILURE` for queue purposes after the reproducible terminal failure. The evidence is not labelled an FPE unless the native transcript explicitly contains one.
- **Factual checkpoint observation:** the last valid 40% checkpoint had `+37.079%` signed imbalance, `+63.501%` liquid closure, and entry static pressure margin `−0.078 kPa`.
- **Residual evidence:** the retained 40% final window had increasing continuity and epsilon envelopes while `k` and volume fraction trended downward.

### F09 — full Mixture progressive loading, URF 0.5

- **Role:** progressive loading at moderate momentum damping.
- **Execution:** all five 3,000-iteration stages completed, for 15,000 iterations total and 3,000 iterations at 100%.
- **Factual checkpoint observations:** signed imbalance was positive at every saved load, ranging from `+25.856%` at 40% to `+1,764.907%` at 10%; the 100% endpoint was `+650.794%`. The 100% liquid inventory was `2,959.919 kg` and entry static pressure margin was `−34.045 kPa`.
- **Residual evidence:** final-window statistics are available at all five stage endpoints. The 80% and 100% continuity medians were `9.609` and `9.257`, respectively.

### F10 — carrier-first progressive loading, URF 0.5

- **Role:** combined staging strategy at moderate momentum damping.
- **Execution:** hybrid initialization completed. The carrier 10% native attempt then produced an explicit floating-point exception in the post-failure transcript; no native iteration or full-Mixture checkpoint was confirmed.
- **Status:** `NUMERICAL_FAILURE`.
- **Physical evidence:** no full-Mixture checkpoint; phase-routing and inventory quantities are `N/A`.

### F11 — full Mixture progressive loading, URF 0.3

- **Role:** progressive loading at strong momentum damping.
- **Execution:** all five 3,000-iteration stages completed, for 15,000 iterations total and 3,000 iterations at 100%.
- **Factual checkpoint observation:** the raw 10% readback has extreme liquid accumulation and conflicts with the older compact report's signed 10% value. This report uses the raw paired-readback flows and the stated signed formula: `+878.664%` total imbalance and `+1,490.488%` liquid closure. The conflict is retained rather than silently resolved.
- **100% observation:** signed total imbalance `−12.377%`, liquid closure `−21.050%`, and entry static pressure margin `+1.690 kPa`.
- **Residual evidence:** native residual exports are present for all five stages; final-window reduction remains pending.

### F12 — carrier-first progressive loading, URF 0.3

- **Role:** most conservative combined staging strategy.
- **Execution:** carrier 10% completed, followed by full-Mixture 10%, 20%, 40%, 80%, and 100% blocks. Total iterations were 18,000, with 3,000 at 100%.
- **Factual checkpoint observations:** signed imbalance was `−46.713%`, `+12.005%`, `+0.073%`, `−11.966%`, and `−11.107%` at the 10%, 20%, 40%, 80%, and 100% checkpoints, respectively. The 40% checkpoint had the smallest absolute total imbalance in this sequence, while the 100% checkpoint retained `−18.664%` liquid closure.
- **Residual evidence:** all five full-Mixture endpoint windows are available. The final 100% window showed decreasing continuity, `k`, epsilon, and volume-fraction trends, but this is not sufficient to claim physical settlement.

## 4. Checkpoint physical evidence

### 4.1 Matched full-Mixture 100% condition

Only branches with full Mixture active, 100% inlet velocity, and a valid `.dat.h5` checkpoint are included. F07, F08, and F10 have no valid full-Mixture 100% checkpoint in the selected attempts.

| Branch | 100% iterations | Total inlet kg/s | Total outlet kg/s | Signed imbalance | L→B | L→S | V→B | V→S | Total liquid kg | ΔP brine |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F01 | 5,500 valid | 198.486 | 385.264 | +94.101% | 239.378% | 21.816% | 37.342% | 60.732% | 901.399 | +0.233 kPa |
| F03 | 5,000 | 198.486 | 866.164 | +336.385% | 662.091% | 13.536% | 37.739% | 56.230% | 2,821.069 | −19.415 kPa |
| F05 | 3,000 | 198.486 | 170.031 | −14.336% | 65.159% | 10.403% | 9.434% | 90.787% | 4,457.055 | +1.404 kPa |
| F06 | 3,000 | 198.486 | 169.941 | −14.382% | 65.153% | 10.411% | 9.424% | 90.782% | 4,461.249 | +1.561 kPa |
| F09 | 3,000 | 198.486 | 1,490.350 | +650.794% | 1,243.654% | 45.129% | 43.537% | 85.528% | 2,959.919 | −34.045 kPa |
| F11 | 3,000 | 198.486 | 173.918 | −12.377% | 66.815% | 12.136% | 10.447% | 89.217% | 4,686.969 | +1.690 kPa |
| F12 | 3,000 | 198.486 | 176.437 | −11.107% | 68.420% | 12.916% | 10.183% | 89.160% | 4,681.935 | +1.367 kPa |

### 4.2 F12 staged full-Mixture checkpoints

| Load | Cumulative iterations | Signed imbalance | Liquid closure | Total liquid kg | ΔP brine |
|---:|---:|---:|---:|---:|---:|
| 10% | 6,000 | −46.713% | −78.911% | 5,486.152 | −0.623 kPa |
| 20% | 9,000 | +12.005% | +20.501% | 5,612.346 | −0.027 kPa |
| 40% | 12,000 | +0.073% | +0.109% | 5,464.289 | +0.128 kPa |
| 80% | 15,000 | −11.966% | −20.203% | 4,919.994 | +1.232 kPa |
| 100% | 18,000 | −11.107% | −18.664% | 4,681.935 | +1.367 kPa |

## 5. Final-report requirements added after continuous-history recovery work

The final Stage-3 report should not be a longer version of this checkpoint packet. It should use the continuous histories to answer the experiment question directly.

Required changes for the final report:

- plot **all** available residual equations, not only continuity/`k`/`epsilon`;
- recover and use native Report File `.out` histories;
- make total inlet/outlet mass flow, relative mass imbalance, and total liquid inventory the main physical convergence evidence;
- explicitly show inlet-loading transitions for ramped branches;
- use phase routing, Y010/Y030 inventories, and brine-entry static/total pressure as diagnostic evidence;
- collapse duplicate/alias report histories into canonical plotted quantities with duplicate consistency checks;
- compare branches at like-for-like full-Mixture 100% conditions where possible;
- use checkpoints from this packet only as validation/provenance anchors;
- preserve transport/failure gaps rather than interpolating them;
- distinguish associations across steady iterations from physical-time causality.

The fillable target structure is [`03a-stage3-final-results-template.md`](./03a-stage3-final-results-template.md).

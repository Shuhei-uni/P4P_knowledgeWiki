# 03A Stage-3 Results — F01–F12 evidence report

> **Campaign:** 03A Stage-3 — Fluent-Recommended Convergence Sweep  
> **Branches:** F01–F12  
> **Physical case:** unchanged 03A full-geometry steady Mixture case  
> **Evidence model:** residual histories plus discrete physical measurements from paired `.cas.h5`/`.dat.h5` checkpoints  
> **Interpretation status:** pending user direction

This report is an evidence packet. It records execution validity, checkpoint lineage, physical readback, and residual-window evidence. It does not select a best branch, claim physical settlement, or call a branch converged.

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
| F05 | 3,000 | 198.486 | 170.030 | −14.336% | 69.655% | 5.907% | 43.267% | 56.854% | 317.752 | +1.404 kPa |
| F06 | 3,000 | 198.486 | 169.940 | −14.382% | 71.393% | 4.171% | 45.545% | 54.463% | 376.627 | +1.561 kPa |
| F09 | 3,000 | 198.486 | 1,490.223 | +650.794% | 1,189.211% | 24.000% | 29.212% | 59.745% | 2,959.919 | −34.045 kPa |
| F11 | 3,000 | 198.486 | 173.919 | −12.377% | 72.586% | 6.364% | 43.996% | 56.039% | 345.365 | +1.690 kPa |
| F12 | 3,000 | 198.486 | 176.439 | −11.107% | 75.025% | 6.311% | 43.286% | 56.422% | 374.374 | +1.645 kPa |

Routing percentages are normalized by the corresponding phase inlet. Values above 100% are intentionally visible.

### 4.2 Progressive-loading checkpoint map

The complete physical fields for the read-back full-Mixture endpoints, including raw phase mass flows, phase closures, Y030/Y010 inventories, and pressure values, are in the [physical-readback checkpoint CSV](03a-stage3-results-20260821-checkpoints.csv). Carrier-only and hybrid checkpoints are intentionally not represented as zero-valued physical rows.

| Branch | Load | Iteration | Signed imbalance | L→B | L→S | V→B | V→S | Total liquid kg | ΔP brine |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F07 | 10% | 3,150 | +59.399% | 199.974% | 2.060% | 14.292% | 84.087% | 353.443 | +0.029 kPa |
| F07 | 20% | 6,150 | +1.212% | 96.179% | 6.075% | 37.628% | 62.094% | 192.386 | −0.054 kPa |
| F07 | 40%* | 9,150 | +21.054% | 132.206% | 3.788% | 42.518% | 57.153% | 324.162 | +0.085 kPa |
| F09 | 10% | 3,000 | +1,764.907% | 3,071.684% | 5.231% | 0.000% | 130.216% | 3,095.118 | −2.250 kPa |
| F09 | 20% | 6,000 | +616.838% | 996.785% | 158.065% | 36.271% | 53.660% | 2,108.039 | +0.137 kPa |
| F09 | 40% | 9,000 | +25.856% | 119.702% | 24.475% | 43.885% | 55.748% | 398.452 | +0.543 kPa |
| F09 | 80% | 12,000 | +506.705% | 948.532% | 17.836% | 35.415% | 56.522% | 2,449.258 | −20.200 kPa |
| F09 | 100% | 15,000 | +650.794% | 1,189.211% | 24.000% | 29.212% | 59.745% | 2,959.919 | −34.045 kPa |
| F11 | 10% | 3,000 | +878.664% | 896.396% | 694.092% | 0.000% | 102.990% | 11,383.447 | −0.022 kPa |
| F11 | 20% | 6,000 | +247.634% | 211.712% | 311.849% | 0.013% | 95.827% | 8,067.212 | +0.746 kPa |
| F11 | 40% | 9,000 | +5.069% | 99.945% | 9.070% | 27.183% | 72.237% | 815.363 | +0.045 kPa |
| F11 | 80% | 12,000 | −0.597% | 95.777% | 3.368% | 41.432% | 58.341% | 471.578 | +1.673 kPa |
| F11 | 100% | 15,000 | −12.377% | 72.586% | 6.364% | 43.996% | 56.039% | 345.365 | +1.690 kPa |
| F12 | 10% | 6,000 | −46.713% | 18.565% | 1.386% | 1.110% | 99.890% | 511.236 | +0.024 kPa |
| F12 | 20% | 9,000 | +12.005% | 114.660% | 6.376% | 21.551% | 77.527% | 434.665 | −0.073 kPa |
| F12 | 40% | 12,000 | +0.073% | 96.594% | 3.714% | 41.342% | 58.394% | 302.414 | +0.154 kPa |
| F12 | 80% | 15,000 | −11.966% | 75.618% | 4.054% | 43.631% | 56.371% | 456.137 | +1.106 kPa |
| F12 | 100% | 18,000 | −11.107% | 75.025% | 6.311% | 43.286% | 56.422% | 374.374 | +1.645 kPa |

`*` The F07 40% pair is present and readable, but stage completion is not execution-confirmed because the supervising transport stream was lost.

## 5. Residual statistics

The default final window is 500 iterations, or the available endpoint window where fewer points were retained. Entries use `median [P05, P95]; trend`. “Final point” was not retained in the remote endpoint readback unless separately stated.

| Branch / stage | Window | Continuity | k | epsilon | Volume fraction |
|---|---:|---|---|---|---|
| F01 / 100% | 5,001–5,500 | 0.395 [0.340, 0.591]; stationary | 0.00945 [0.00736, 0.0179]; decreasing | 0.0446 [0.0221, 1.010]; decreasing | 0.0103 [0.00848, 0.0133]; stationary |
| F03 / 100% | 500 retained points; 2,312–5,000 | 1.166 [1.039, 1.232]; increasing | 0.0102 [0.00790, 0.0132]; increasing | 0.0376 [0.0246, 0.132]; decreasing | 0.0128 [0.0112, 0.0145]; decreasing |
| F07 / 10% | final retained 500 | 0.264 [0.233, 0.317]; increasing | 0.00488 [0.00178, 0.0588]; increasing | 0.163 [0.0174, 4.324]; increasing | 0.00197 [0.00142, 0.00313]; increasing |
| F07 / 20% | final retained 500 | 0.295 [0.189, 0.385]; decreasing | 0.00445 [0.00148, 0.0849]; increasing | 0.111 [0.0148, 1.873]; increasing | 0.00117 [0.000829, 0.00153]; decreasing |
| F07 / 40%* | final retained 500 | 1.353 [1.105, 1.567]; stationary | 0.00377 [0.00294, 0.00784]; decreasing | 0.0308 [0.00915, 0.634]; increasing | 0.00696 [0.00575, 0.00858]; decreasing |
| F08 / 40% | final retained 250 | 1.384 [1.143, 1.469]; increasing | 0.00350 [0.00302, 0.00596]; decreasing | 0.0271 [0.00975, 0.495]; increasing | 0.00684 [0.00604, 0.00754]; decreasing |
| F09 / 10% | final retained 500 | 0.601 [0.380, 0.717]; increasing | 0.00502 [0.00233, 0.0166]; increasing | 0.158 [0.0282, 1.159]; decreasing | 0.00363 [0.00285, 0.00429]; increasing |
| F09 / 20% | final retained 500 | 1.544 [1.399, 1.777]; stationary | 0.00387 [0.00274, 0.0455]; decreasing | 0.182 [0.0200, 4.254]; decreasing | 0.00579 [0.00558, 0.00596]; stationary |
| F09 / 40% | final retained 500 | 1.749 [1.499, 2.145]; decreasing | 0.00272 [0.00234, 0.00923]; stationary | 0.0467 [0.00932, 0.727]; increasing | 0.00695 [0.00655, 0.00794]; stationary |
| F09 / 80% | final retained 500 | 9.609 [8.849, 10.263]; increasing | 0.0110 [0.00772, 0.0131]; decreasing | 0.0367 [0.0259, 0.133]; stationary | 0.0141 [0.0131, 0.0158]; decreasing |
| F09 / 100% | final retained 500 | 9.257 [8.348, 10.028]; stationary | 0.00924 [0.00731, 0.0108]; stationary | 0.0321 [0.0224, 0.0947]; increasing | 0.0111 [0.0103, 0.0117]; stationary |
| F12 / 10% | final retained 250 | 0.244 [0.175, 0.292]; increasing | 0.000905 [0.000625, 0.00123]; increasing | 0.00708 [0.00205, 0.0744]; increasing | 0.00292 [0.00184, 0.00328]; increasing |
| F12 / 20% | final retained 250 | 0.340 [0.247, 0.430]; increasing | 0.000833 [0.000478, 0.00276]; decreasing | 0.203 [0.0673, 0.602]; decreasing | 0.000864 [0.000473, 0.000998]; increasing |
| F12 / 40% | final retained 250 | 0.610 [0.517, 0.699]; increasing | 0.000792 [0.000616, 0.00214]; increasing | 0.0736 [0.0107, 0.368]; increasing | 0.00154 [0.00143, 0.00198]; increasing |
| F12 / 80% | final retained 250 | 1.224 [0.987, 1.460]; increasing | 0.00152 [0.000817, 0.00774]; increasing | 0.219 [0.0391, 0.670]; increasing | 0.00212 [0.00198, 0.00243]; increasing |
| F12 / 100% | final retained 250 | 1.051 [0.667, 1.496]; decreasing | 0.000926 [0.000544, 0.00254]; decreasing | 0.141 [0.0279, 0.411]; decreasing | 0.00106 [0.000935, 0.00121]; decreasing |

Residual-window statistics for F05, F06, and F11 are not yet reduced from their native residual-export files. The exports exist remotely. F02, F04, and F10 have no usable full-Mixture native residual window in the selected attempts.

## 6. Factual observations only

- F01 and F10 have explicit floating-point-exception evidence. F01 also has AMG-divergence and residual-escalation evidence before the FPE.
- F02 and F04 later fixed-block attempts ended with terminal Fluent-native errors without ledger evidence of an FPE; they remain `PARTIAL`.
- F03 experienced a recoverable transport/client interruption and still completed its planned 5,000 iterations.
- F07 is transport-blocked after confirmed 20%; a readable 40% pair exists, but its stage completion is unconfirmed.
- F08 has a valid 40% continuation checkpoint and no 80% checkpoint after two reproducible native-stage failures.
- F05, F06, F09, F11, and F12 completed their fixed-block schedules. Only F01 and F03 have at least 5,000 valid iterations at 100% in the selected records.
- Checkpoint routing fractions above 100% and large signed mass imbalances occur in several stages. They are retained in the evidence table.

## 7. Interpretation and campaign conclusion

**Interpretation status remains pending user direction.** The following fields are intentionally not filled with a scientific ranking:

- numerically useful branch;
- physically settled branch;
- converged branch;
- most promising numerical strategy;
- final strategy recommendation.

The immediate evidence-completion action is to transfer and reduce the remaining native residual exports for F05, F06, and F11, then generate the checkpoint-marker plots from the master CSV. The F11 10% raw-readback conflict should be reconciled against the native report definitions before cross-branch interpretation.

## 8. Evidence sources

Local execution and readback records include:

- F01: `PyAnsys/output/03a_stage3/F01/F01-summary.json`, `F01-failure-histories.json`, and `F01-monitor-histories.json`.
- F02/F04/F05/F06/F11 fixed-block ledger, journals, and readbacks under `PyAnsys/output/03A-stage3/override-fixed3000-native-server2/20260820T013223Z/`.
- F03: `PyAnsys/output/03a_stage3/supervised/20260820T054645Z/supervised-events.jsonl`.
- F07: `PyAnsys/output/03a_stage3/overnight/20260820T002135Z/overnight-events.jsonl`.
- F08: `PyAnsys/output/03A-stage3/recovery-safe/20260820T044148Z/recovery-safe-events.jsonl` and `PyAnsys/output/03A-stage3/recovery-retry80/20260820T054146Z/recovery-retry80-events.jsonl`.
- F09: `PyAnsys/output/03a_stage3/supervised/20260820T082047Z/supervised-events.jsonl`.
- F10: `PyAnsys/output/03A-stage3/resume-f10-f12/20260820T055022Z/resume-events.jsonl` and `resume-f12-after-f10-fpe/20260820T055715Z/resume-events.jsonl`.
- F12: `PyAnsys/output/03A-stage3/f12-from-verified-preinit/20260820T073316Z/f12-events.jsonl`.

Remote Windows case/data roots are retained in the event logs and in the checkpoint CSV. No new Fluent iterations or solver-setting changes were made during readback.

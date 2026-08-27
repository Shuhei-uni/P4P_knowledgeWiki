# 03A Stage 3 — results

## What ran

The twelve-branch Fluent-recommended sweep used independent branches from the shared pre-initialization parent. The source evidence distinguishes continuous histories, checkpoint-only evidence, transport gaps, and numerical failures; no missing interval is interpolated.

| Branch | Highest confirmed state | Horizon | Status |
|---|---|---:|---|
| F01 | 100% final stage | 5,500 valid iterations | numerical failure after the last valid checkpoint |
| F02 | carrier 100% attempt | 0 confirmed native iterations | partial / no valid branch history |
| F03 | full Mixture at 100% | 5,000 | completed diagnostic |
| F04 | carrier 100% attempt | 0 confirmed native iterations | partial / no valid branch history |
| F05 | full Mixture at 100% | 3,000 | completed diagnostic |
| F06 | carrier then full Mixture at 100% | 6,000 | completed diagnostic |
| F07 | confirmed through 20%; 40% attempt | 6,150 confirmed | transport-blocked |
| F08 | ramp through 40%; 80% transition | 12,000 | numerical failure |
| F09 | 10/20/40/80/100% ramp | 15,000 | completed diagnostic |
| F10 | carrier 10% attempt | 0 confirmed native iterations | numerical failure / no valid solve history |
| F11 | 10/20/40/80/100% ramp | 15,000 | completed diagnostic |
| F12 | carrier then 10/20/40/80/100% ramp | 18,000 | completed diagnostic |

## Evidence / plots / measurements

The full source package contains native residual histories and per-iteration physical histories for the qualified branches, plus checkpoint measurements for all branches where a paired state exists:

- [final iteration-led interpretation and branch plots](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-final-results.md);
- [checkpoint evidence packet](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-results-20260821.md);
- [F05/F06/F11 native-history package](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-native-queue-final-results.md);
- [F03/F07/F09 native-history package](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-f03-f07-f09-detailed-results.md).

At the matched 100% checkpoint, the best-developed mass-balance compromises were still open:

| Branch | 100% iterations | Signed total imbalance | Total liquid inventory | Brine pressure margin |
|---|---:|---:|---:|---:|
| F05 | 3,000 | `−14.336%` | `4,457.055 kg` | `+1.404 kPa` |
| F06 | 3,000 | `−14.382%` | `4,461.249 kg` | `+1.561 kPa` |
| F09 | 3,000 | `+650.794%` | `2,959.919 kg` | `−34.045 kPa` |
| F11 | 3,000 | `−12.377%` | `4,686.969 kg` | `+1.690 kPa` |
| F12 | 3,000 | `−11.107%` | `4,681.935 kg` | `+1.367 kPa` |

These are checkpoint anchors, not steady-state claims. The source histories retain total and phase flow routing, mass imbalance, liquid inventories, residuals, and brine hydraulics versus cumulative Fluent iteration.

F12 illustrates why the loading path must remain visible: at its 10/20/40/80/100% checkpoints, signed imbalance was `−46.713%`, `+12.005%`, `+0.073%`, `−11.966%`, and `−11.107%`, while total liquid inventory was `5,486.152`, `5,612.346`, `5,464.289`, `4,919.994`, and `4,681.935 kg`. The apparently favourable 40% state did not prove a stationary full-load solution.

## Numerical state and limitations

- Residual evidence is strongest when it is continuous, but several branches have native-history gaps or only sampled windows. Those gaps are preserved.
- Low or moderate residuals alone do not qualify a branch: total/phase flow, mass balance, liquid inventory, and brine-pressure histories must also become bounded.
- F01 failed numerically after iteration `5,704` with `5,500` as the last valid checkpoint; F07 was transport-blocked before its intended ramp completed; F08 failed at the higher-load transition.
- F02, F04, and F10 do not provide confirmed native solve histories and cannot support branch ranking.
- No Stage-3 branch is a converged, report-ready, or externally validated baseline. The checkpoint packet explicitly treats endpoint values as validation anchors only, never as proof of stationarity.

## Observations

- **F05/F06:** the cleanest tests of whether more iteration alone could flatten the promising full-load inventory behaviour; both still require a longer continuation.
- **F11/F12:** the strongest full-load physical histories, with better balance than most branches despite intermittent `k`/`epsilon`; both require sustained continuation.
- **F09:** residual behaviour improved through the ramp and the 40% state was promising, but the 80% transition drove mass and liquid behaviour away from that state.
- **F07/F08:** reduced loading can improve an intermediate residual regime, but a high momentum URF did not robustly reach full load.
- **F02/F04/F10:** missing or failed histories prevent a scientific comparison rather than proving the associated strategy ineffective.

## Findings / interpretation

Stage 3 did not identify a qualified winner. It did identify a bounded follow-up set: long unchanged continuations from F05, F06, and F11; a separate standard-`k-epsilon` sensitivity from F11; and a gated return to the F09 40% state if its exact parent can be recovered. The project remains diagnostic, and no efficiency, carryover, pressure-drop, or inlet-improvement claim is promoted from these results.

## What this implies for the next review

Stage 4 is needed to distinguish temporary checkpoint improvement from a sustained state. It holds the Stage-3 candidates for a common `+30,000`-iteration continuation, keeps evidence packages comparable, and changes only one model-form variable in the standard-`k-epsilon` branch. Its setup and actual execution are recorded separately in [Stage-4 setup](../stage-04/setup.md) and [Stage-4 results](../stage-04/results.md).

## Source

[Original Stage-3 results authority](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-final-results.md)

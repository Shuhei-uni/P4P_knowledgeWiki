> **Retired source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-results-20260821.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# 03A Stage-3 Results — F01–F12 evidence report

> **Campaign:** 03A Stage-3 — Fluent-Recommended Convergence Sweep  
> **Branches:** F01–F12  
> **Physical case:** unchanged 03A full-geometry steady Mixture case  
> **Evidence model:** residual histories plus discrete physical measurements from paired `.cas.h5`/`.dat.h5` checkpoints  
> **Interpretation status:** pending user direction

This file remains the Stage-3 **checkpoint/provenance evidence packet**, not the
final scientific report. The final report should be rebuilt from continuous
stitched residual histories plus recovered Fluent Report File histories using
the [migrated analysis and plotting plan](source-analysis-and-plotting-plan.md).

The existing checkpoint CSV was the structured endpoint authority for the
source run; its interpreted contents are retained in this Project packet.

## 1. Evidence conventions

- Attempts remain separate by run stamp.
- Signed total mass imbalance is `100 × (total outlet − total inlet) / total inlet`.
- Values above `100%` are retained.
- Carrier-only checkpoints have phase-routing and liquid-inventory fields recorded as `N/A`.
- Physical values are checkpoint measurements, not continuous-history claims.
- Pressure margin is `entry static pressure − 1,120,000 Pa`.
- Endpoint values are validation anchors only; they must not be used alone to establish steady state.

## 2. Overall execution summary

| Branch | Stages reached | Highest load | Total iterations | Iterations at 100% | Terminal status |
|---|---|---:|---:|---:|---|
| F01 | 100% final stage; later FPE | 100% | 5,500 valid | 5,500 | `NUMERICAL_FAILURE` |
| F02 | hybrid initialization; carrier-100% attempt | carrier 100% | 0 native confirmed | 0 | `PARTIAL` |
| F03 | full Mixture at 100% | 100% | 5,000 | 5,000 | `COMPLETED` |
| F04 | hybrid initialization; carrier-100% attempt | carrier 100% | 0 native confirmed | 0 | `PARTIAL` |
| F05 | full Mixture at 100% | 100% | 3,000 | 3,000 | `COMPLETED` |
| F06 | carrier 100%; full Mixture 100% | 100% | 6,000 | 3,000 | `COMPLETED` |
| F07 | confirmed 10%, 20%; 40% pair unconfirmed | 40% attempted | 6,150 confirmed | 0 | `TRANSPORT_BLOCKED` |
| F08 | verified through 40%; failed at 80% | 40% valid | 12,000 | 0 | `NUMERICAL_FAILURE` |
| F09 | 10%, 20%, 40%, 80%, 100% | 100% | 15,000 | 3,000 | `COMPLETED` |
| F10 | hybrid initialization; carrier-10% attempt | carrier 10% | 0 native confirmed | 0 | `NUMERICAL_FAILURE` |
| F11 | 10%, 20%, 40%, 80%, 100% | 100% | 15,000 | 3,000 | `COMPLETED` |
| F12 | carrier 10%; full Mixture 10%, 20%, 40%, 80%, 100% | 100% | 18,000 | 3,000 | `COMPLETED` |

## 3. Matched full-Mixture 100% checkpoint evidence

| Branch | 100% iterations | Total inlet kg/s | Total outlet kg/s | Signed imbalance | L→B | L→S | V→B | V→S | Total liquid kg | ΔP brine |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F01 | 5,500 valid | 198.486 | 385.264 | +94.101% | 239.378% | 21.816% | 37.342% | 60.732% | 901.399 | +0.233 kPa |
| F03 | 5,000 | 198.486 | 866.164 | +336.385% | 662.091% | 13.536% | 37.739% | 56.230% | 2,821.069 | −19.415 kPa |
| F05 | 3,000 | 198.486 | 170.031 | −14.336% | 65.159% | 10.403% | 9.434% | 90.787% | 4,457.055 | +1.404 kPa |
| F06 | 3,000 | 198.486 | 169.941 | −14.382% | 65.153% | 10.411% | 9.424% | 90.782% | 4,461.249 | +1.561 kPa |
| F09 | 3,000 | 198.486 | 1,490.350 | +650.794% | 1,243.654% | 45.129% | 43.537% | 85.528% | 2,959.919 | −34.045 kPa |
| F11 | 3,000 | 198.486 | 173.918 | −12.377% | 66.815% | 12.136% | 10.447% | 89.217% | 4,686.969 | +1.690 kPa |
| F12 | 3,000 | 198.486 | 176.437 | −11.107% | 68.420% | 12.916% | 10.183% | 89.160% | 4,681.935 | +1.367 kPa |

These are checkpoint anchors only. The final report must use the continuous histories to determine whether apparent endpoint improvements are persistent, transient, oscillatory, or still drifting.

## 4. F12 staged checkpoint evidence

| Load | Cumulative iterations | Signed imbalance | Liquid closure | Total liquid kg | ΔP brine |
|---:|---:|---:|---:|---:|---:|
| 10% | 6,000 | −46.713% | −78.911% | 5,486.152 | −0.623 kPa |
| 20% | 9,000 | +12.005% | +20.501% | 5,612.346 | −0.027 kPa |
| 40% | 12,000 | +0.073% | +0.109% | 5,464.289 | +0.128 kPa |
| 80% | 15,000 | −11.966% | −20.203% | 4,919.994 | +1.232 kPa |
| 100% | 18,000 | −11.107% | −18.664% | 4,681.935 | +1.367 kPa |

## 5. What the final report must add

The final Stage-3 scientific report must be history-led rather than checkpoint-led.

Required additions:

1. stitch and plot **all** available residual equations;
2. recover native Report File `.out` histories;
3. use total inlet/outlet mass flow, relative mass imbalance, and total liquid inventory as the primary physical convergence evidence;
4. show inlet-loading transitions for ramped branches;
5. use phase routing, Y010/Y030 inventory, and brine-entry static/total pressure as diagnostic evidence explaining the main behaviour;
6. collapse duplicate/alias report histories into canonical plotted quantities and retain duplicates as consistency checks;
7. compare branches at like-for-like full-Mixture 100% conditions where possible;
8. cross-check history values against this packet/CSV at matching checkpoints;
9. preserve failure/transport gaps rather than interpolating them;
10. distinguish associations along steady iterations from physical-time causality.

There is no Stage-3 requirement for a prescribed outlet phase split. The primary success question is whether a strategy produces bounded/stabilising residual behaviour **and** a steady total mass balance with stationary liquid inventory.

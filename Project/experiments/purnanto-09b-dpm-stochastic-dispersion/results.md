> **Legacy source:** Setups/reports/purnanto-reference/09b/results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Results Report — Setup 09b

## Setup link

- Setup definition: [09b-rsm-dpm-split-inlet-accuracy.md](setup.md)
- Comparison parent: [09a/results.md](../purnanto-09a-dpm-deterministic-carryover/results.md)
- Evidence basis: stochastic DPM fate tables

## 1. DPM trajectory/fate results

| Diameter | Random eddy lifetime | Injected | Escaped | Trapped | Incomplete | Escape fraction |
|---:|---|---:|---:|---:|---:|---:|
| `5.63 um` | off | `21700` | `2722` | `15` | `18963` | `12.54%` |
| `10 um` | off | `21700` | `3370` | `106` | `18224` | `15.53%` |
| `5.63 um` | on | `21700` | `2312` | `19` | `19369` | `10.65%` |
| `10 um` | on | `21700` | `2943` | `85` | `18672` | `13.56%` |
| `28.14 um` | off | `21700` | `0` | `6` | `21694` | `0%` |
| `28.14 um` | on | `21700` | `0` | `9` | `21691` | `0%` |
| `40 um` | off/on | `21700` | `0` | `0` | `21700` | `0%` |

## 2. Findings

- Stochastic dispersion materially changes completed escape counts for the fine-droplet cases.
- Random eddy lifetime reduces escape for both tested fine-droplet cases.
- The `10 um` point escapes more than the `5.63 um` point in both stochastic settings.
- The result is dominated by incomplete trajectories and should not be presented as a final physical grade-efficiency curve.

## 3. Conclusion

`Needs follow-up` — retain as a stochastic DPM sensitivity report and carry dispersion and unresolved-fate uncertainty into later interpretation.

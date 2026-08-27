> **Legacy source:** Setups/reports/purnanto-reference/09a/results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Results Report — Setup 09a

## Setup link

- Setup definition: [09a-dpm-split-inlet-carryover.md](setup.md)
- Parent evidence: setup `08b` deterministic DPM sample
- Evidence provenance: inherited parent data plus preliminary manual diagnostic

## 1. DPM trajectory/fate results

Inherited six-bin deterministic sample:

| Quantity | Value |
|---|---:|
| Total tracked | `13020` |
| Escaped | `8` |
| Trapped | `0` |
| Incomplete | `13012` |
| Aggregate escaped fraction | `0.061%` |
| Aggregate incomplete fraction | `99.94%` |

The only recovered bin with completed escape was `5.63 um`, with `8 / 2170` escaped. Bins from `28.14 um` through `348.88 um` had no completed escape or trap in the sampled pass.

Separate manual diagnostic:

| Diameter | Injected | Escaped | Trapped | Incomplete |
|---:|---:|---:|---:|---:|
| `10 um` | `2170` | `1` | `TBD` | `2169` |

## 2. Interpretation and limitations

The result establishes a deterministic comparison point, but almost all trajectories remain unresolved. Incomplete particles must remain a separate unresolved category rather than being silently counted as trapped or escaped.

## 3. Conclusion

`Needs follow-up` — retain as the deterministic DPM baseline for comparison with `09b` stochastic dispersion.

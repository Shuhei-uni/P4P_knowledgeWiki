> **Legacy source:** Setups/reports/purnanto-reference/04/results.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

# Results Report — Setup 04

## Setup link

- Setup definition: [04-mixed-wet-half-actual-area.md](setup.md)
- Evidence basis: own setup calculation and DPM sensitivity checks
- Evidence-use label: `DPM diagnostic only`; low-confidence flux diagnostic

## 1. Run scope

Setup 04 tested the mixed wet-half velocity-inlet branch using the measured actual inlet area. The report includes phase-flux calculations and one-way DPM tracking sensitivity.

## 2. Numerical results

### Phase flux and efficiency

| Quantity | Value |
|---|---:|
| Liquid inlet | `115.5160538 kg/s` |
| Liquid outlet | `2.4986160 kg/s` |
| Steam inlet total | `80.7122860 kg/s` |
| Steam outlet | `81.4523789 kg/s` |
| Liquid separation efficiency | `2.16%` |
| Outlet steam dryness | `97.02%` |

The liquid efficiency is calculated as `liquid outlet / liquid inlet`. The report also records a large retained-liquid amount, so this is not full separator mass-balance evidence.

### DPM trajectory/fate sensitivity

For the tested injection, the numerical fate counts were:

| Max steps | Step factor | Interval | Trapped | Incomplete | Escaped |
|---:|---:|---:|---:|---:|---:|
| `50,000` | `5` | `10` | `158` | `342` | `0` |
| `500,000` | `5` | `10` | `158` | `342` | `0` |
| `50,000` | `2` | `2` | `159` | `341` | `0` |
| `50,000` | `1` | `1` | `157` | `343` | `0` |

The stream-count sweep also kept incomplete tracks dominant at approximately `65.8–68.4%`.

## 3. Interpretation and limitations

Increasing tracking steps did not resolve the incomplete-track problem. The flux result is useful for branch comparison, but residual stability, outlet closure, and unresolved DPM trajectories limit its claim strength.

## 4. Conclusion

`Needs follow-up` — retain as a reported diagnostic branch and historical comparison, not as a final efficiency baseline.

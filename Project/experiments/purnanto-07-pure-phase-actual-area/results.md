> **Retired source:** Setups/reports/purnanto-reference/07/results.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# Results Report — Setup 07

## Setup link

- Setup definition: [07-pure-phase-split-actual-area.md](setup.md)
- Technical extraction: [technical-extraction.md](technical-extraction.md)
- Evidence basis: professional-mesh phase fluxes and DPM sweep

## 1. Flux-based carryover result

The professional-mesh report recorded:

| Quantity | Value |
|---|---:|
| Liquid inlet | `116.8522662 kg/s` |
| Steam inlet | `81.6394689 kg/s` |
| Steam-outlet liquid carryover | `0.0366339 kg/s` |
| Implied steam-line liquid-removal efficiency | `99.96865%` |
| Steam-outlet dryness | `99.95757%` |

This is a scoped steam-line carryover metric. It is not a full-vessel brine-drainage or liquid-inventory closure claim.

## 2. DPM injection trajectory/fate results

| Diameter | Injected | Escaped | Trapped | Incomplete | Scoped efficiency |
|---:|---:|---:|---:|---:|---:|
| `5 um` | `200` | `74` | `63` | `63` | `63.0%` |
| `1 um` | `200` | `23` | `64` | `113` | `88.5%` |
| `10 um` | `200` | `14` | `53` | `133` | `93.0%` |
| `41 um` | `200` | `0` | `72` | `128` | `100%`* |
| `100 um` | `200` | `0` | `86` | `114` | `100%`* |

`*` The source report treats incomplete particles as effectively trapped for this scoped project metric. Keep that assumption visible whenever quoting these values.

## 3. Sensitivity findings

At `5 um`, deterministic, DRW, and rotation cases gave scoped efficiencies of `67.6%`, `71.2%`, and `65.3%`, respectively. The qualitative conclusion was unchanged, but incomplete tracks remained substantial.

## 4. Conclusion

`Needs follow-up` — this is a numerically reported steam-carryover and DPM diagnostic branch. Do not promote it to full separator validation without stronger residual, balance, and trajectory-completion evidence.

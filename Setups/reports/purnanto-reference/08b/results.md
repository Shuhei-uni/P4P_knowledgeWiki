# Results Report — Setup 08b

## Setup link

- Setup definition: [08b-purnanto-parity-split-inlet-rebuild.md](../../past/reported/08b-purnanto-parity-split-inlet-rebuild.md)
- Additional raw phase result: [phase-flux-result.md](phase-flux-result.md)
- Evidence basis: saved `5000`-iteration carrier field, phase flux, and active DPM sample

## 1. Flux-based result

| Quantity | Value |
|---|---:|
| Liquid inlet | `116.92 kg/s` |
| Steam/vapor inlet | `80.69 kg/s` |
| Steam-outlet liquid flow | `0.082132007 kg/s` |
| Steam-outlet vapor flow | `81.464165 kg/s` |
| Scoped steam-line liquid-removal efficiency | `99.92975367%` |
| Steam-outlet dryness | `99.89928175%` |
| Whole-domain mixture imbalance ratio | `0.5873372754` |

The efficiency is explicitly scoped to steam-line liquid carryover. The large whole-domain imbalance prevents treating it as full separator mass-balance validation.

## 2. DPM injection trajectory/fate result

The active six-bin sample recorded:

| Quantity | Value |
|---|---:|
| Total tracked | `13020` |
| Escaped at `steamoutlet` | `8` |
| Trapped | `0` reported rows |
| Incomplete | `13012` |
| Escaped represented mass flow | `7.005e-04 kg/s` |

The one-injection-at-a-time sample identified the completed escapes only in the `5.63 um` injection: `8 escaped`, `2162 incomplete`, and `0 trapped` out of `2170` tracks. The remaining sampled bins were fully incomplete.

## 3. Interpretation and limitations

This is a split-inlet and steam-carryover screening result, not report-quality DPM efficiency evidence. The DPM result is dominated by incomplete trajectories, and the current active sample omits three larger recovered injection bins.

## 4. Conclusion

`Needs follow-up` — retain as the past reported parity-reset result and numerical parent evidence for later DPM branches.

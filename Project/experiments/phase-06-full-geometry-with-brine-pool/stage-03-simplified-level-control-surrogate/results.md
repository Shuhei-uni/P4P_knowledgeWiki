# Phase 06 / Stage 03 — simplified level-control surrogate — results

## Status

**Completed discovery run `P6-S3-C`.** Five 100-iteration steady chunks were
run from F11. After each chunk the Python controller read the retained
`y≤0.10 m` liquid-mass history, updated only brine pressure, read the change
back, and saved a verified final case/data pair.

## Research interpretation

**Reported, generic geothermal practice.** A brine-line level-control valve
can prevent separator draining and steam passage by changing brine discharge.

**Assumed for this model.** The existing `y≤0.10 m` phase-2 liquid-mass proxy,
a 200 kg target, and pressure-based quasi-steady action stand in for unknown
plant measurement and valve dynamics.

**Claim limit.** Any success can establish only that this CFD model can or
cannot support the stated *numerical surrogate*. It cannot validate a real
separator controller or select the real plant level.

## Observed controller response

| Chunk endpoint | Proxy mass [kg] | Brine pressure for next chunk [MPa gauge] |
|---:|---:|---:|
| 15,100 | 194.10 | 1.122000 |
| 15,200 | 199.35 | 1.122327 |
| 15,300 | 205.80 | 1.120327 |
| 15,400 | 211.02 | 1.118327 |
| 15,500 | 214.50 | 1.116327 |

**Observed.** The controller changed direction correctly at the 200 kg
target, but the proxy continued upward. Over the full screen it increased by
26.70 kg. Its late mean was 212.78 kg, with late slope +0.0337 kg/iteration.
The late derived net liquid rate was still +19.96 kg/s; relative mass
imbalance averaged 0.1018. The controller did not create a controlled state.

**Interpretation.** A discrete outer pressure-feedback rule is technically
implementable and its action survives live readback, but this initial gain and
five-chunk horizon are insufficient. The next stage must test a materially
stronger, longer bounded feedback response—not another fixed pressure or an
arbitrary outlet resistance.

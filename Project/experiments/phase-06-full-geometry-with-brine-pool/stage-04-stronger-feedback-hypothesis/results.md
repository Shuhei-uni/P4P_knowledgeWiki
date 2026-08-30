# Phase 06 / Stage 04 — stronger-feedback hypothesis — results

## Status

**Completed `P6-S4-C`.** Ten 100-iteration chunks (1,000 retained samples)
ran from F11 with the declared stronger controller. The final paired case/data
artifact and nine file-backed physical histories were verified.

## Observed result

The controller reached its lower pressure bound, 1.115 MPa gauge, during
chunk 5 and remained there. The lower-region proxy ended at 225.57 kg; its
last-100-sample mean was 225.74 kg, not the assumed 200 kg target. Its late
slope was still positive (+0.00620 kg/iteration), although much lower than the
Stage-03 short-controller late slope (+0.0337 kg/iteration).

The stronger rule improved liquid drainage and numerical direction: late
liquid-to-brine flow averaged −100.01 kg/s, late net liquid accumulation was
+10.02 kg/s, and late relative mass imbalance averaged 0.0511. These are
improvements over Stage 3, but they are still non-zero accumulation and
material imbalance. Scaled residual history remains unavailable after
reconnection.

## Hypothesis decision

**Weakened.** More aggressive bounded pressure feedback reduces the drift but
does not hold the numerical level proxy before the actuator hits its bound.
It cannot establish a controlled operating condition in the current steady
Mixture/RNG model.

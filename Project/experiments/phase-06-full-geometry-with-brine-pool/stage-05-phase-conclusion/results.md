# Phase 06 / Stage 05 — phase conclusion

## Phase conclusion

**Within the tested F11 steady Mixture/RNG model, a simple quasi-steady
brine-pressure feedback surrogate cannot establish a credible controlled
bottom brine-pool operating condition.**

The evidence is progressive:

1. Fixed pressure accumulated lower-region liquid mass and retained material
   mass imbalance.
2. The generic outlet-vent `K=10` case made drainage, accumulation, and
   imbalance worse.
3. The initial five-chunk numerical controller responded in the intended
   direction but did not hold the 200 kg proxy.
4. The stronger 1,000-iteration controller improved drainage and reduced
   accumulation, but saturated at its lowest allowed pressure while the proxy
   remained about 26 kg above target and continued to rise slightly.

## What is supported

- A file-backed lower-region phase-2 liquid-mass proxy can drive an external
  Python/PyFluent quasi-steady feedback loop.
- Lower brine backpressure increases liquid brine drainage in this model.
- Stronger feedback moves the solution in a better numerical direction.
- Within the Stage-5/Phase-6 tested pressure bracket, pressure feedback alone
  cannot close the liquid balance or hold the assumed proxy target.

## What is not supported

- A real separator level-control claim.
- A real pool-level elevation or plant setpoint.
- Numerical convergence: scaled residual histories were not recoverable.
- A conclusion that all valve laws, pressure ranges, turbulence models, or
  multiphase models fail.

## Next phase-level implication

The next phase should challenge the retained model/control architecture rather
than extend this pressure-feedback rule: for example, an independently
specified valve/line model, a different multiphase formulation, or a
time-dependent controlled model. That choice is outside the completed Phase-6
surrogate conclusion.

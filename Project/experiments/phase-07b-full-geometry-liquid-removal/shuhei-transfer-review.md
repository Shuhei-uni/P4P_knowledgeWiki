# Shuhei evidence relevant to Phase 7b E2

**Superseded for new R0 evidence:** see the [22 September audit](convergence-investigation/shuhei-audit.md). This earlier review retains its historical evidence boundary.

The strongest transferable lessons concern source accounting, liquid delivery,
and startup-path sensitivity. The reviewed records do not identify a proven
converged configuration to import. Phase 7b's approved tau-only comparison
continues unchanged; this review supplies interpretation for G2.

## Evidence boundary

The current Shuhei baseline is the [60k v2 virtual outlet](../phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/setup.md),
superseding the earlier uniform/inventory-controlled absorber. Its
[inlet-ramp result](../phase-07-1a-absorber-convergence/v2-inlet-loading-ramp/results.md)
includes a user continuation to native N4002, supported by the saved
[native endpoint readback](../phase-07-1a-absorber-convergence/v2-inlet-loading-ramp/live-4002-readback.json).
Those Project records and the v2 build manifest were inspected locally.
The referenced full v2 run-history directory is absent from this Mac, so this
review does not independently audit every history sample or establish new
late-window statistics. No Shuhei solver was contacted or changed.

His v2 uses 60,964 cells, a 715-cell lower zone and mass-flow inlets. Phase 7b
uses the full 620,431-cell geometry, the 41,258-cell S40 region and split
equal-velocity inlets. The build recipe also retains first-order k, whereas
Phase 7b uses second-order k; material properties differ. Absolute residuals,
inventory levels and iteration counts are therefore not matched comparisons.

## What transfers

| Recorded finding | Implication for Phase 7b |
| --- | --- |
| V2 weights local removal by liquid volume fraction and removes matching liquid momentum and shared k/epsilon; direct vapor source is off. | These useful implementation features are already present in Phase 7b. They do not require a new source-law change during E2. |
| V2 applied removal eventually tracks its inlet-derived command. At N4002, command and removal are both 116.92 kg/s. | This verifies source realization. Because the normalized law enforces the integrated command above its volume floor, command agreement alone cannot establish convergence or collector performance. |
| N2000 to N4002 total liquid mass rises from 183.595 to 318.661 kg; all seven endpoint residuals increase and reverse flow persists. | Reaching the requested removal does not establish bounded inventory. Retain the joint inventory, applied-source closure, routing and residual criteria. |
| Both feeds were ramped from 25% toward full loading over 2,000 iterations. Lower liquid subsequently develops. | A matched ramp-versus-immediate-full-feed experiment is a plausible later startup-path test. No same-v2 full-feed control was identified, so the ramp's causal benefit is unproven. A ramp must be followed by a declared full-feed hold. |
| Earlier standard and realizable k-epsilon children changed the residual and inventory trajectories but retained drift, reverse flow and viscosity limiting. | There is no demonstrated turbulence replacement to adopt as a fix. The old absorber also differs materially from both v2 and Phase 7b. |

The turbulence observations are recorded in the
[family comparison](../phase-07-1a-absorber-convergence/turbulence-family/family-analysis-summary.json).
The [production-limiter child](../phase-07-1a-absorber-convergence/turbulence-family/t2-rng-production-limiter/results.md)
saved active 250 but failed during the following block; it provides no successful
stabilization setting. The recorded
[Coupled/global-pseudo-time packet](../phase-07-1a-absorber-convergence/solver-path-family/c3c4-coupled-global-pseudo-time/results.md)
was not run, and the later physical-transient comparison was withdrawn in the
current Phase 7.1A context. Neither supports a claimed successful solver switch.
The superseded C8 ring case is partial and lacks a completed conservation
assessment, so its large liquid flux is not a qualified drainage result.

## Conservation implication of the v2 command

**Calculated from the saved N4002 readback:** the listed liquid inlet, native
applied sink and liquid steam-outlet flux give

\[
116.92-116.92-22.116498=-22.116498\ {\rm kg/s},
\]

or an 18.9159% deficit relative to liquid feed. This is an endpoint calculation
from the listed terms, assuming the declared pure-phase inlets, closed bottom
and no additional liquid transfer; it is not a complete-history closure audit.
The mixture outlet differs from the sum of its two phase reports by about
0.009984 kg/s, a small additional accounting/readback discrepancy to retain.

**Inferred:** commanding removal equal to all liquid feed presupposes zero net
liquid carryover at a balanced steady state. Positive liquid carryover must
share the feed with collector removal. A throughput-controlled law would need
that balance constraint considered explicitly; merely matching a prescribed
source is not an independent mass-closure success criterion. Inventory change
per steady iteration is not a physical storage term that can repair this sum.

V2 is also not simply a weaker fixed-tau sink. Above its normalization floor,
and for constant density and physically bounded alpha, its law has effective
`tau = lower liquid mass / commanded removal`. The reported values give about
0.000882 s at N2000 and 0.02136 s at N4002. Its effective coefficient changes
with inventory, whereas E2 holds tau fixed. Similarity to the current 0.02 s
point at one endpoint does not establish equivalence or an optimal tau.

## Use at G2

Finish the authorized fixed-tau contrast before introducing another factor.
Use the existing histories to distinguish: liquid reaching the collector,
actual removal, net liquid carryover, and total source-inclusive balance. Low
collector inventory alone cannot diagnose starvation; Phase 7b's exact-face
delivery/escape records provide the necessary transport evidence.

If E2 does not produce acceptable behaviour, the next decision can compare a
matched inlet-ramp experiment against a separately designed source-treatment
experiment. Shuhei's evidence motivates these hypotheses but selects neither
as a proven remedy. No new physics, numerical setting, inlet ramp, source law,
case or horizon is authorized by this review.

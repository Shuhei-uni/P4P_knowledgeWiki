# Phase 06 discovery campaign — steady numerical pool-control substitutes

## Lifecycle and question

Lifecycle mode: `discovery`. This campaign is permitted only after
`PHASE_CONTRACT == PASS` and a fresh `DISCOVERY_DESIGN` gate review.

Question:

> Which deliberately simple steady outlet-response substitute, if any,
> deserves an expensive qualification run for keeping the lower-region liquid
> pool proxy bounded in the full-geometry separator model?

The human-authorized boundary is full geometry and steady state. Mixture/RNG is
the verified reference, not a required final model. The campaign makes no
physical plant-controller, plant setpoint, or validation claim.

## Discovery basis and collision check

Prior Phase-06 evidence shows fixed pressure accumulation, an uncalibrated
outlet-vent `K=10` deterioration, and one short bounded pressure-feedback
screen. The previous long run is not reused as a gate pass because its
residual history and named final pair were missing. The six cases below are
explicitly classified against prior work. D01 and D02 are `REPLICATION`
screens, retained because their earlier evidence lacked durable residual
histories and cannot support a numerical comparison. D03 and D04 are
`PARTIAL REPEAT` cases because the earlier screens lacked durable residual
evidence (and D03 also changes the loss coefficient). D05 is a nonredundant
control-update probe. The original D06 `NEW` Eulerian bold lane proved its
model-switch capability but stalled before one smoke report coordinate, so it
is a blocked non-counting attempt. The selected sixth case is
`P6-D06R-EC`, a `PARTIAL REPEAT` whose concrete delta was the verified steady
Eulerian `Coupled` pressure–velocity scheme. D06R then exposed an invalid
inherited total-pressure report during smoke and is also non-counting. The
selected sixth case is `P6-D06C-PR`, a `NEW` open-loop prescribed continuation
path across the existing pressure bracket. It retains Mixture/RNG and all 30
currently valid reports; see [`bold-probe-research.md`](bold-probe-research.md)
and [`d06-repair-research.md`](d06-repair-research.md).

## Planned six-case campaign

All cases use the canonical paired F11 parent, the same lower-region liquid
mass reports, phase-resolved flow reports, full/pool-region balance reports,
and a 50-iteration smoke followed by the declared attached discovery horizon.
Each run must redirect every report to its own run root, configure and read
back scaled residual history before solving, save/reopen the prepared pair,
and retain a matching final pair.

| Case | Delta from F11 parent | Discovery purpose | Novelty / collision class | Horizon |
|---|---|---|---|---:|
| `P6-D01-R` | fixed brine pressure at 1.115 MPa gauge | lower-pressure reference against the prior long-run bracket | `REPLICATION`; earlier residual history was unavailable, so this creates a complete numerical baseline | 500 |
| `P6-D02-R` | fixed brine pressure at 1.1375 MPa gauge | upper-pressure reference; checks pressure-direction sensitivity | `REPLICATION`; earlier residual history was unavailable, so comparison remains informative | 500 |
| `P6-D03-V` | outlet-vent at retained ambient pressure, `K=1` | milder pressure-loss outlet representation; tests whether `K=10` was overstrong | `PARTIAL REPEAT`; changes K and repairs residual capture | 500 |
| `P6-D04-F` | pressure feedback, target 200 kg, gain 500 Pa/kg, max step 2 kPa, 5×100-iteration chunks | reproduce the existing low-gain surrogate with complete numerical evidence | `PARTIAL REPEAT`; prior low-gain run lacked durable residual history | 500 |
| `P6-D05-F` | pressure feedback, target 200 kg, gain 2 kPa/kg, max step 5 kPa, 10×50-iteration chunks | test stronger/faster correction as a distinct architecture | `NEW` relative to the short campaign; not a substitute for the blocked long run | 500 |
| `P6-D06C-PR` | **redesign-gated** steady Mixture/RNG prescribed continuation path: start at 1.115 MPa gauge and, after each successive 100-iteration chunk, read back and set 1.120, 1.125, 1.13125, then 1.1375 MPa gauge; unchanged F11 geometry, materials, report package, residual path, and final upper-bracket endpoint | bold numerical-path probe: determine whether a cold fixed-pressure endpoint is enough, or whether the lower-pool response depends on the open-loop route through the same pressure bracket | `NEW`; unlike D04/D05 feedback, this has no mass target or gain and tests continuation/initialization-path sensitivity. Unlike D01/D02, it is not a cold fixed endpoint. | 500 |

Cases are screened, not ranked by endpoint alone. The useful candidate must
show a bounded proxy history, directionally consistent outlet response, phase
liquid balance and full-domain closure that do not materially worsen, and
complete residual/report evidence. If all six remain poor, discovery has still
earned a hypothesis about the common limiting mechanism.

## Required evidence before a case counts

- exact parent case/data identity and parent readback;
- intended outlet/model state readback;
- prepared paired save and full-path reload readback;
- 50-iteration smoke success;
- durable scaled residual capture with native iteration coordinates;
- lower-region `y≤0.10 m` and `y≤0.30 m` phase-2 liquid-mass histories;
- phase-2 liquid inlet, brine-outlet, and steam-outlet histories;
- full-domain and pool-region liquid-balance/imbalance histories;
- outlet condition and, for feedback cases, every command/readback update;
- requested 500 discovery iterations after smoke;
- matching final case/data pair and terminal attached-run manifest.

Missing residual or report evidence makes the case invalid for the discovery
gate. It is not replaced by a post-run prose statement. D06 stalled before a
single smoke coordinate and is retained as a non-counting blocked attempt.
D06R did not pass its smoke evidence contract: the inherited total-pressure
report is invalid for Eulerian and did not write. It is retained as a
non-counting blocked attempt and is not rescued by post-hoc monitor deletion.
D06C must instead pass a deterministic continuation-path sub-gate: load the
same verified Mixture/RNG parent, read back every declared pressure command at
the planned chunk boundary, retain all 30 report histories, and prove the same
prepared/final save/reopen, residual, autosave, and native-coordinate horizon
contract. No physical controller, gain, target, phase/material, model,
pseudo-time, or transient change is authorized. A fresh independent
`DISCOVERY_DESIGN` review is mandatory before mutation.

## Core discovery figures

1. `F1_pool_proxy_histories`: native iteration versus both lower-region liquid
   mass proxies for all six cases, preserving raw histories and a declared
   final-window reduction. It asks whether the outlet delta changes inventory
   direction or boundedness.
2. `F2_phase_liquid_balance`: phase-2 inlet, brine-outlet, steam-outlet, and
   derived net-liquid rate versus native iteration. It asks whether apparent
   pool control agrees with phase-resolved conservation.
3. `F3_numerical_adequacy`: scaled residual histories and full/pool-region
   imbalance for each case. It asks whether comparisons are numerically
   credible and whether any outlet response worsens closure.

## Selection rule for the next lifecycle state

After all six execution-gated cases are analysed, formulate one falsifiable
hypothesis only if discovery materially narrows the uncertainty. State the
strongest competing explanation and why a long qualification can distinguish
them. If uncertainty remains broad, extend discovery only within the maximum
12-case ceiling and do not promote a weak hypothesis.

## Claim limits

All targets, gains, pressure bounds, loss coefficients, and deadband values
are numerical assumptions. The Eulerian case, if capability verification
passes, is a model-form probe rather than a claim that Eulerian is physically
correct. Results apply only to the tested full-geometry steady surrogate
cases. They do not identify the physical sensor, valve, controller, or real
separator operating target.

# Phase 06 / Stage 01 — level observable and outlet response discovery — results

## Status

**One bounded reference discovery result is complete; the outlet-response
comparison remains to run.** `P6-S1-R` was run from the canonical paired F11
parent on Server 2 under the inherited fixed `brineoutlet` pressure boundary.
The solver wrote 551 retained report samples over native report coordinates
15,000–15,550, and paired final case/data files were verified at the declared
run root. This is a repeatable fixed-pressure reference, not a controlled
brine-pool state or a converged solution.

## Capability evidence before execution

**Observed from live F11-derived cases.** The retained model is steady,
pressure-based Mixture with vapor `phase-1`, liquid `phase-2`, and the three
already-loaded turbulence variants (RNG, Standard, and Realizable
`k-epsilon`). `brineoutlet` is presently a pressure outlet. Existing reports
already resolve phase-1, phase-2, and mixture boundary fluxes, full-domain
imbalance, and liquid volume/mass in geometry-specific registers bounded at
`y≤0.10 m` and `y≤0.30 m`.

**Interpretation limit.** The two lower-region integrals are inventory proxies,
not a demonstrated physical level instrument or a calibrated height. They can
answer whether the model distinguishes changes inside the bottom region, but
cannot be reported as plant pool elevation until a geometry/instrument mapping
is supplied.

**Reported by the Fluent 2025 R2 User's Guide.** A mass-flow outlet pumps a
prescribed flow and is designed for strictly outward flow; it should not be
used for mixed or direction-changing flow. The pressure-outlet target-mass-flow
option is unavailable with multiphase flows. An outlet vent instead represents
ambient pressure plus an empirically supplied loss coefficient. These facts
justify the Stage-01 representation screen but do not validate any candidate
as the separator's real valve/controller.

## Completed reference discovery — `P6-S1-R`

**Observed.** The reference used the retained steady pressure-based Mixture /
RNG `k-epsilon` F11 configuration and the inherited phase-aware histories.
The native report-file coordinate is the authoritative iteration coordinate:
the operational Fluent RP variable remained at its inherited value and must
not be interpreted as evidence of zero progress. The run completed a
50-iteration smoke then 500-iteration discovery continuation; report files
contain 551 samples from 15,000 through 15,550.

| Quantity | Start → final | Last-100-sample mean | Late slope | Interpretation boundary |
|---|---:|---:|---:|---|
| `y≤0.10 m` phase-2 liquid mass | 187.79 → 215.48 kg | 213.43 kg | +0.0412 kg/iteration | lower-region inventory proxy, **not level** |
| `y≤0.30 m` phase-2 liquid mass | 194.15 → 222.09 kg | 219.98 kg | +0.0421 kg/iteration | lower-region inventory proxy, **not level** |
| total phase-2 liquid mass | 345.37 → 378.46 kg | 375.81 kg | +0.0530 kg/iteration | no stationary liquid inventory in this window |
| liquid inlet − liquid brine outlet − liquid steam outlet | +24.60 → +18.78 kg/s | +21.42 kg/s | −0.0494 kg/s/iteration | phase-flow basis remains net accumulating |
| full-domain mass imbalance | +24.57 → +18.74 kg/s | +21.42 kg/s | −0.0498 kg/s/iteration | material and not closed |
| relative mass imbalance | 0.1238 → 0.0944 | 0.1079 | −0.000251/iteration | improving direction, not an adequate plateau |

The completed core figures are retained beside this record:
[F1 lower-region inventory response](figures/reference-server2-20260830T030000Z/f1_lower_region_inventory.png),
[F2 phase-resolved liquid balance](figures/reference-server2-20260830T030000Z/f2_phase_resolved_liquid_balance.png), and
[F3 numerical/output behaviour](figures/reference-server2-20260830T030000Z/f3_numerical_output_behavior.png).
The corresponding machine summary is
[summary.json](figures/reference-server2-20260830T030000Z/summary.json).

**Interpretation.** All three retained liquid-mass inventories grow over the
screen; the two lower-region series track the same direction as total liquid
mass. They therefore provide a useful *response proxy*, but do not identify a
pool elevation, a measurement plane, or a controlled setpoint. The fixed
pressure boundary has not established a controlled lower-region state.

**Numerical adequacy limit.** Physical report histories survived, but the
live residual buffer was unavailable after reconnection; scaled residual
history cannot be reconstructed for this result. The reference is not called
converged and may only be used as a matched short-screen comparator.

**Observable capability boundary.** Attempted custom phase-2 volume-integral
reports and explicit report files survived settings definition/readback but
did not produce usable histories across save/reopen. The Stage-01 evidence is
therefore deliberately framed as lower-region liquid-*mass* inventory, with
level/elevation mapping deferred to a later stage.

## Completed outlet-vent comparison — `P6-S1-O`

**Observed.** The matched F11 child converted only `brineoutlet` from a
pressure outlet to an outlet vent at the retained 1.120 MPa gauge ambient
pressure, with constant loss coefficient `K=10`. The save/reopen readback
retained both the outlet-vent type and `K=10`. The 50-iteration smoke and
500-iteration discovery continuation completed; final paired case/data files
and nine relevant report histories were verified. The native history window
again spans 15,000–15,550 (551 samples).

| Matched metric | Fixed-pressure `P6-S1-R` | Outlet-vent `P6-S1-O` | Bounded comparison |
|---|---:|---:|---|
| `y≤0.10 m` phase-2 mass increase | +27.68 kg | +68.41 kg | 2.47× larger with vent |
| `y≤0.30 m` phase-2 mass increase | +27.94 kg | +68.57 kg | 2.45× larger with vent |
| total phase-2 mass increase | +33.10 kg | +84.98 kg | 2.57× larger with vent |
| late derived net liquid rate | +21.42 kg/s | +44.82 kg/s | materially more net accumulation |
| late relative mass imbalance | 0.1079 | 0.2249 | materially worse closure indicator |
| late liquid-to-brine flow | −87.97 kg/s | −59.00 kg/s | substantially less liquid drainage |
| late liquid-to-steam flow | −7.46 kg/s | −13.03 kg/s | greater liquid carryover to steam outlet |

The outlet-vent core figures are
[F1 lower-region inventory response](figures/vent-server2-20260830T235000Z/f1_lower_region_inventory.png),
[F2 phase-resolved liquid balance](figures/vent-server2-20260830T235000Z/f2_phase_resolved_liquid_balance.png), and
[F3 numerical/output behaviour](figures/vent-server2-20260830T235000Z/f3_numerical_output_behavior.png), with the
[machine summary](figures/vent-server2-20260830T235000Z/summary.json).

**Interpretation.** This deliberately uncalibrated `K=10` outlet-vent form
is a *negative capability result* for this exact steady F11 screen: it
reduces liquid brine drainage, increases lower-region liquid inventory growth,
increases liquid carryover, and worsens the retained closure indicators.
It is not a plant-valve test and does not rule out a different resistance
coefficient, an identified line/valve characteristic, or a genuine feedback
controller. It does rule out advancing this particular `K=10` vent condition
as a credible controlled-pool candidate.

**Numerical adequacy limit.** As for the reference, scaled residual history
could not be recovered after reconnecting. The matched comparison is reliable
for its retained physical Report Files and exact boundary readback, but neither
branch is a converged steady solution.

## Stage-01 decision

**Decision: advance, with a narrowed question.** Stage 01 has established
that existing lower-region liquid-mass reports are repeatable *inventory*
response measures and that changing to a simple outlet-vent loss relation can
be decisively screened. Neither branch supplies a level/elevation observable
or controlled state. A generic `K=10` resistance worsened the behaviour, so
the next Stage-01/Stage-02 work must not sweep arbitrary resistance values.
It must first construct the geometry-to-level mapping and seek a physically
specified outlet/feedback relation (or document that this information is
missing). The strictly outward-flow mass-flow outlet remains deferred: the
reference already demonstrates outward *net* liquid flow but does not prove
all boundary flow is outward at all faces/phases.

## Execution reconciliation

**Observed.** Three early Phase-06 runner attempts established the child-case
configuration/readback path but did not create a valid numerical endpoint.
The first outlet-vent child (`K=10`) saved a paired final case/data record but
its requested iteration values were below F11's existing iteration coordinate;
Fluent therefore advanced zero additional iterations. It is configuration-only
evidence. Direct PyFluent API inspection subsequently established that
`iterate(iter_count=…)` accepts an **incremental** iteration count. The runner
now calls `50` then `500`, records the start/end coordinates, and fails unless
each coordinate advances by the requested increment.

**Observed.** The corrected resistance and reference attempts on Servers 2 and
3 each wrote their declared `prepared.cas.h5`, proving parent loading,
outlet readback, monitor-path redirection, and save/reopen. Neither exposed a
final `.cas.h5`/`.dat.h5` pair or a terminal manifest before its local runner
ended. They are therefore `PREPARED_ONLY`, not CFD results. The Server-1
attempt used the superseded iteration logic and its client was cancelled after
a non-returning Fluent RPC; it is excluded from all analysis.

**Current execution boundary.** Prepared-only artifacts listed below remain
non-results. They are superseded operational attempts; no conclusion relies on
them. The later attached `P6-S1-R` run above is the first valid Stage-01
numerical reference and has a terminal `COMPLETE` manifest.

**Observed 2026-08-30 — strengthened implementation proof, then a remote-run
blocker.** A Server-3 reference child under
`reference-api-validated-20260830T015000Z` passed the following gates before
the solve command: F11 parent load/data readback, the two new lower-region
phase-2 liquid-volume report definitions, explicit report-file objects for
those definitions, report-path redirection, paired prepared case/data save,
and save/reopen readback. The subsequent 50-iteration smoke command was not
issued: Fluent reported `iterating=true` and exposed no active
`run_calculation.iterate` or `calculate` command. The native iteration
coordinate remained `1556` across a 20-second read-only observation.

**Observed on Server 2.** The same `iterating=true`, coordinate-`1556` state
persisted across a 12-second observation while the earlier local attached
runner remained present. Its terminal manifest is absent. These are stalled or
otherwise unreconciled remote calculations, not proof that either case ran to
the planned horizon. The runner now fails before any child mutation when this
state is detected. Recovering or stopping an existing remote calculation is a
separate execution decision; no interrupt was sent.

## Carried numerical basis

**Observed from the completed Stage-5 Realizable-low native report history.**
The liquid-inlet phase flux was `+116.85 kg/s`; liquid routing was
`-91.25 kg/s` to the brine outlet and `-8.90 kg/s` to the steam outlet over
the last 50 samples. The total mixture brine-outlet flux was instead
`-128.79 kg/s`.

**Interpretation limit.** The flow values above document why the later outlet
experiments must state phase and surface scope. A rough flow value mentioned in
phase discussion is not a fixed target, total separator outflow, or proof of
only slight liquid accumulation. The pool-level metric and actual control
condition remain missing.

## Current fleet boundary

| Server reference | Preflight result |
|---|---|
| `server-1@10.104.145.170` | network reachable; gRPC call timed out |
| `server-2@10.104.145.174` | reachable, Fluent connected, quiescent after `P6-S1-R`; selected for the matched outlet-vent comparison |
| `server-3@10.104.145.176` | reachable, Fluent connected, quiescent during the latest read-only check; no alteration made |

The next action is controlled child construction, save/reopen readback, and
the selected `P6-S1-O` outlet-vent discovery screen under new explicit paths.

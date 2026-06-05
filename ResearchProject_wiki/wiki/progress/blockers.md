# Blockers

## Active Blockers

### BLK-001 | Baseline run not converging
- Status: Downgraded to setup/debug history
- First observed: 2026-04-22
- Related run(s): `BGM-2026-04-22-A`
- Symptom: no satisfactory convergence after 1000 iterations.
- Current interpretation: this run is no longer part of the active quantitative evidence base because it did not exceed the current `1000`-iteration evidence threshold and did not converge. Retain it only as a setup-history warning unless the Bangma-based reconstruction becomes necessary again.

### BLK-002 | No interpretation framework for simulation outputs
- Status: Active
- First observed: 2026-04-22
- Related run(s): `BGM-2026-04-22-A` and follow-up runs
- Symptom: uncertainty about which outputs indicate separator performance and what model change should follow from results.

### BLK-003 | Split-inlet orientation and allocation not yet frozen
- Status: Active
- First observed: 2026-04-30
- Related run(s): next split-inlet A/B case
- Symptom: `left/right` wording is not precise enough to guarantee the correct wall-side vs inner-side phase placement on the spiral-inlet face.

### BLK-004 | Current split-inlet/brine-outlet result has unclassified problems
- Status: Historical / not blocking setup `07`
- First observed: 2026-05-18
- Related run(s): `FFF-2`, `MWH-WP-2026-05-07-A`
- Symptom: the parent `FFF-2` case is already not converged and not liquid-mass-balanced after approximately `1020` iterations without water-pool initialization; the water-pool child case then develops additional liquid inventory depletion and extreme steam-outlet liquid carryover.
- Current interpretation: this remains historical troubleshooting context for older mixed wet-half/brine-outlet cases. For setup `07`, bottom truncation without an active brine outlet or water pool is accepted as out of scope, so this blocker should not delay steam-carryover/DPM efficiency checks.

### BLK-005 | Steam outlet geometry/intake may be entraining liquid
- Status: Historical / not blocking setup `07`
- First observed: 2026-05-18 from review of newest setup report
- Related run(s): `MWH-WP-2026-05-07-A`
- Symptom: guessed steam outlet geometry appears likely to create turbulence or suction near the intake, with reported liquid through steam outlet of `1044.35 kg/s`.
- Current interpretation: retain as a warning from the older water-pool branch only. The professional setup `07` run currently shows low apparent steam-line carryover, so this should not block the baseline DPM sweep.

## Ranked Hypotheses
1. Parent `FFF-2` has an unresolved convergence/mass-balance problem even without initialized water, but this is historical context rather than an active setup `07` blocker.
2. Brine outlet pressure, backflow settings, or outlet type may be over-driving liquid removal in older parent cases; this is not part of the setup `07` acceptance scope.
3. Missing stabilization tuning in numerics may be preventing the mixed wet-half velocity-inlet case from settling.
4. Mesh quality may still be insufficient in the inlet, swirl, steam-outlet, or brine-outlet regions.
5. Inlet phase allocation may be too sharp or incorrectly oriented, creating an artificial steam jet or liquid blockage.
6. Steam outlet geometry/intake behavior may be entraining liquid and causing excessive carryover.
7. The steady solver is depleting the initialized lower water pool in the child case, producing transient-like liquid drainage inside a steady calculation; this is now out of scope for setup `07`.
8. The project still needs residual/monitor stability and DPM fate counts before setup `07` can become report-quality efficiency evidence.

## Recovery Plan
1. For setup `07`, proceed with steam-carryover/DPM efficiency checks without reopening bottom/brine-outlet troubleshooting.
2. Record residual/monitor stability for `PLS-PRO-2026-06-03-A`.
3. Run DPM diameter checks at `5 um`, `10 um`, and `40-41 um`.
4. Keep `FFF-2` and `MWH-WP-2026-05-07-A` as historical troubleshooting references only unless the project scope later returns to brine-drainage or water-pool modelling.

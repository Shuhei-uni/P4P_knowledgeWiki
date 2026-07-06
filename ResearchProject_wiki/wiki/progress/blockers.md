# Blockers

## Active Blockers

### BLK-008 | Setup 08b DPM result is dominated by incomplete tracks
- Status: Active
- First observed: 2026-07-02
- Related run(s): `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Symptom: the refreshed live `08b` aggregate DPM summary reports `13012` incomplete particles and only `8` escaped particles for the current active 6-bin subset, with no trapped row printed in the summary output. The follow-up one-injection-at-a-time `dpm-sample` pass reproduces the same aggregate split and shows the completed sampled escape only in `injection-5-micron`, while the other active sampled bins remain fully incomplete.
- Current interpretation: this is now the main DPM-quality blocker for setup `08b`. The current result suggests very low completed escaped mass and no sampled trapped mass, but tracking completion is still too poor to treat the DPM outcome as strong removal-efficiency evidence.

### BLK-009 | Setup 08b steam-line carryover result is not backed by a closed whole-domain mass balance
- Status: Active
- First observed: 2026-07-02
- Related run(s): `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Symptom: the live `08b` phase-flux post-processing gives steam-outlet liquid carryover `0.082132007 kg/s`, but the same report also shows a mixture imbalance of `116.063719 kg/s`, much larger than the steam-line carryover signal.
- Current interpretation: this keeps the current `08b` flux result in the `scoped steam-line carryover diagnostic` category rather than allowing it to stand as a closed whole-separator efficiency result.

### BLK-007 | Fluent-exported split-inlet mesh does not yet preserve the exact required zone contract
- Status: Active
- First observed: 2026-06-10
- Related run(s): `MESH-TRIAL1-SPLIT-CONTRACT-AUDIT-2026-06-10`
- Symptom: the corrected `mesh-trial1.msh` now reopens with two separate velocity-inlet boundaries, but Fluent currently exposes them as `liquidinlet` and `steaminlet`, and the exported boundary list does not include `wall-smooth_spiral_separator`.
- Current interpretation: this is a mesh-export / naming-preservation blocker for the semi-automated split-inlet workflow, not a geometry-change request. Conservative mesh-control trials should not be accepted until the exported baseline itself satisfies the exact required-zone contract.

### BLK-006 | PyFluent baseline script still has version-specific API gaps
- Status: Active
- First observed: 2026-06-09
- Related run(s): `PYFLUENT-TRIAL3-SMOKE-2026-06-09`
- Symptom: the local one-inlet reconstruction can launch, initialize, and iterate, but the high-level operating-pressure setter still fails and several intended solution-method setters do not match the current Fluent 2026 R1 PyFluent object paths.
- Current interpretation: this is now a narrow automation-parity blocker, not a full environment blocker. The important result is that the case is already runnable; the remaining task is to make the script cleaner and less ambiguous.
- Update after `PYFLUENT-TRIAL4-HARDENED-2026-06-09`: operating-pressure control and numerics-path discovery are now resolved; the remaining issue is smaller and mostly limited to pressure-outlet subsetting inactivity cleanup.
- Update after `PYFLUENT-TRIAL4-500-2026-06-09`: the longer controlled diagnostic run completed, so this is no longer a stability blocker for the one-inlet branch. The remaining issue is mostly tooling/polish: pressure-outlet subsetting inactivity and the empty direct residual-write export.

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
8. Setup `08b` currently shows low steam-line liquid carryover on the saved field, but the whole-domain mixture imbalance is still much larger than the carryover signal.
9. Setup `08b` DPM tracking currently finishes with overwhelmingly incomplete particles, so tracking completion rather than escaped mass is the main uncertainty.
10. The direct PyFluent rebuild path is now proven runnable, significantly hardened, and stable enough for a controlled `500`-iteration diagnostic, but pressure-outlet setting inactivity and residual-export behavior still need cleanup before treating it as a polished baseline automation workflow.

## Recovery Plan
1. For setup `08b`, keep the current flux result as a scoped steam-line carryover diagnostic unless a later pass closes the whole-domain mass balance more convincingly.
2. Increase DPM tracking budget for the active 6-bin `08b` subset before trying to interpret DPM as stronger evidence.
3. Keep the current one-injection sampled attribution as a diagnostic aid, but improve tracking completion or export stronger per-injection fate summaries before turning it into a report-facing claim.
4. Keep `FFF-2` and `MWH-WP-2026-05-07-A` as historical troubleshooting references only unless the project scope later returns to brine-drainage or water-pool modelling.
5. For the new one-inlet PyFluent path, keep `trial4` plus the completed `500`-iteration diagnostic as the active local baseline and clean up pressure-outlet setting order plus residual export before extending much further.

# Blockers

## Active Blockers

### BLK-011 | Frozen 02c parent is not visible from the currently idle Fluent endpoint
- Status: Active — case-only build blocked
- First observed: 2026-08-16
- Related run(s): `02c-I20-I160-PREPARATION-2026-08-16`
- Symptom: the active 02c I20–I160 builder correctly refused to proceed because the required frozen `02c-B` pre-initialization parent path was not visible to the accessible idle Fluent session.
- Current interpretation: this is a remote-file/session-availability constraint, not evidence that the documented parent, H artifacts, or the intended I settings are invalid. The build was stopped before any case mutation, initialization, iteration, data write, or journal submission.
- Recovery action: reconnect to an idle Fluent session with access to the documented frozen parent; verify the parent boundary/model contract; then build and reload-verify every independent I child before submitting the separate native journal.
- Scope note (2026-08-16): a Student-only I20/I40/I60 50-iteration surrogate smoke completed successfully at the execution-integrity level. It does not clear this blocker because its saved source, mesh, and DPM state are not the verified server-2 frozen-parent lineage.

### BLK-010 | IC1 brine-pipe VOF patch has no unambiguous cell-volume selection
- Status: Active — human selection required
- First observed: 2026-08-14
- Related run(s): `VOF-IC1-PATCH-PLATFORM-2026-08-14`
- Symptom: the coarse patch-test mesh has one combined fluid cell zone (`simple-spiral-separator--brine-outlet-`) and no pre-existing brine-pipe-only cell register. `brine-outlet` is a pressure-outlet face zone, so it cannot itself serve as a volume-fraction patch target for the complete pipe volume.
- Current interpretation: IC1 and independent IC2 plane-pool checkpoints at `+0.00 m` and visually approved `+0.30 m` have been patched and saved as coarse platform artifacts. IC2 now has a reproducible planned height matrix (`+0.00`, `+0.15`, `+0.30`, `+0.45`, `+0.60 m`). The unbuilt sensitivity levels still require marked-volume and initialized-liquid-mass recording before any transient interpretation.
- Recovery action: create each planned global-coordinate register, report its marked volume/cell count and corresponding initial liquid mass, then preserve the same timestep/monitor/averaging gates as IC0 before authorizing a solve.

### BLK-008 | Setup 08b DPM result is dominated by incomplete tracks
- Status: Accepted scope limitation; not blocking
- First observed: 2026-07-02
- Related run(s): `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Symptom: the refreshed live `08b` aggregate DPM summary reports `13012` incomplete particles and only `8` escaped particles for the current active 6-bin subset, with no trapped row printed in the summary output. The follow-up one-injection-at-a-time `dpm-sample` pass reproduces the same aggregate split and shows the completed sampled escape only in `injection-5-micron`, while the other active sampled bins remain fully incomplete.
- Current interpretation: incomplete tracks remain raw diagnostic context, but are not a project blocker or acceptance gate. Report-facing interpretation is limited to observed escape through `steamoutlet`.

### BLK-009 | Setup 08b steam-line carryover result is not backed by a closed whole-domain mass balance
- Status: Accepted scope limitation; not blocking
- First observed: 2026-07-02
- Related run(s): `PURNANTO-08B-POSTPROCESS-2026-07-02`
- Symptom: the live `08b` phase-flux post-processing gives steam-outlet liquid carryover `0.082132007 kg/s`, but the same report also shows a mixture imbalance of `116.063719 kg/s`, much larger than the steam-line carryover signal.
- Current interpretation: the simplified Purnanto geometry has no modelled lower-liquid discharge path, so whole-domain liquid/mixture imbalance is expected within scope and is informational only. Steam-outlet carryover remains a scoped outlet measure, not a closed whole-separator balance claim.

## Accepted Scope Limitations

### SCOPE-001 | Open lower-liquid inventory in the simplified Purnanto geometry
The current geometry does not model the brine/liquid outlet required for whole-domain liquid closure. The resulting liquid or mixture imbalance is out of scope and is not an active numerical blocker.

### SCOPE-002 | DPM incomplete trajectories
DPM incomplete counts are retained in raw outputs but are not an acceptance gate or active blocker. Report-facing DPM interpretation is limited to observed escape through `steamoutlet`.

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
1. Setup `02c` now has complete A–G early screens but no stable two-outlet carrier state. D–G confirm the directional vapour-routing signal as brine pressure rises (brine-outlet vapour `46.70%` → `11.28%` of vapour inlet), while E–G liquid brine outflow exceeds inlet and all four continuity endpoints remain `8.24e-2`–`1.12e-1`. The active blocker is evidence maturity: add total liquid-inventory and local pressure/visual monitors before attributing steady behaviour, calling a drainage limit, or selecting pressure.
2. Parent `FFF-2` has an unresolved convergence/mass-balance problem even without initialized water, but this is historical context rather than an active setup `07` blocker.
3. Brine outlet pressure, backflow settings, or outlet type may be over-driving liquid removal in older parent cases; this is not part of the setup `07` acceptance scope.
4. Missing stabilization tuning in numerics may be preventing the mixed wet-half velocity-inlet case from settling.
5. Mesh quality may still be insufficient in the inlet, swirl, steam-outlet, or brine-outlet regions.
6. Inlet phase allocation may be too sharp or incorrectly oriented, creating an artificial steam jet or liquid blockage.
7. Steam outlet geometry/intake behavior may be entraining liquid and causing excessive carryover.
8. The steady solver is depleting the initialized lower water pool in the child case, producing transient-like liquid drainage inside a steady calculation; this is now out of scope for setup `07`.
9. Setup `08b` residual and monitor histories may still be insufficiently mature for a strong numerical claim.
10. Mesh quality and mesh convergence remain unresolved in the inlet, swirl, and steam-outlet regions.
11. The direct PyFluent rebuild path still has narrow pressure-outlet and residual-export cleanup work.

## Recovery Plan
1. For setup `08b`, assess residuals, iteration maturity, monitor stability, and mesh convergence before strengthening the carrier interpretation.
2. Keep the current one-injection sampled attribution as raw/scoped escape evidence; do not create a recovery branch solely to eliminate incomplete tracks.
4. Keep `FFF-2` and `MWH-WP-2026-05-07-A` as historical troubleshooting references only unless the project scope later returns to brine-drainage or water-pool modelling.
5. For the new one-inlet PyFluent path, keep `trial4` plus the completed `500`-iteration diagnostic as the active local baseline and clean up pressure-outlet setting order plus residual export before extending much further.

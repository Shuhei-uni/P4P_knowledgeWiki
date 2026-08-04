# Blockers

## Active Blockers

### BLK-011 | Split-inlet mesh study cannot pass preflight
- Status: Active.
- First observed: 2026-07-29.
- Related run(s): `SPLIT-MESH-PREFLIGHT-2026-07-29`.
- Symptom: the configured Fluent endpoint timed out, the active processor count is unknown, no systematic three-mesh binaries are local, and the actual split-inlet archive conflicts with intended setup-07 numerics.
- Current interpretation: `FFF.1-2.cas.h5` is the authoritative actual split-inlet case record, but its active DPM and `Coupled`/first-order state cannot be silently used as the carrier-only `SIMPLE`/second-order intended study. Geometry orientation and boundary areas also require live verification.
- Next action: restore the remote connection; inspect version, processor count, geometry/zone areas/normals, phase/material mapping, and full settings; choose and qualify one numerics authority; then generate a systematic coarse/medium/fine ladder with identical topology controls.

### BLK-009 | Fixed 1500-iteration completion is not convergence proof
- Status: Active
- First observed: 2026-07-21.
- Related run(s): `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`, `PURNANTO-SPIRAL-ENTHALPY-DPM-SWEEP-2026-07`.
- Symptom: all 12 runs completed 1500 carrier iterations, but final continuity residuals remained approximately `0.193-0.343` for the baseline cases and `0.145-0.229` for the spiral cases. Baseline incomplete DPM mass ranges from `36.06` to `58.01 kg/s`.
- Current interpretation: the steam-quality values are provisional DPM outputs, not converged validation results. The full residual/physical-monitor trend and incomplete-particle locations must be assessed before claiming replication.
- Next action: run a controlled continuation on representative cases with residual and outlet-flow stopping criteria, then decide whether all six cases require extension.

### BLK-010 | Historical sweep manifests do not preserve the complete DPM contract
- Status: Active for evidence qualification; mitigated for future runs by automation preflight.
- First observed: 2026-07-29 compliance audit.
- Related run(s): `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`, `PURNANTO-SPIRAL-ENTHALPY-DPM-SWEEP-2026-07`.
- Symptom: historical manifests do not preserve all tracking controls, wall fates, face-normal geometry orientation, and interaction readbacks. The baseline branch also lacks a standalone residual CSV for Case 1.
- Current interpretation: the accepted reports provide consistent `Final` DPM mass flows and passing injection mass balances, but they cannot prove full setup parity independently. Particle-count weighting is not a defensible substitute for fate mass flow.
- Next action: use the hardened preflight/report path for any rerun, capture full DPM state plus zone normals, and require fresh per-injection reports before accepting outputs.

### BLK-008 | Remote PyFluent sweep is vulnerable to sleep and VPN loss
- Status: Active / mitigated by checkpoints and recovery manifests.
- First observed: 2026-07-21.
- Related run(s): `PURNANTO-ENTHALPY-DPM-SWEEP-2026-07`.
- Symptom: closing the Mac lid or losing VPN/Wi-Fi removes the gRPC stream while Fluent may continue the already-issued iteration block remotely.
- Current interpretation: `caffeinate` prevents idle sleep but cannot override lid sleep. Short chunks, explicit checkpoints, and first-residual recovery verification limit lost work, but continuous connectivity is still required for unattended sequencing.
- Next action: keep the Mac lid open and VPN connected; prefer an on-PC controller or persistent remote host for future long sweeps.

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
8. The project still needs residual/monitor stability and DPM fate counts before setup `07` can become report-quality efficiency evidence.
9. The direct PyFluent rebuild path is now proven runnable, significantly hardened, and stable enough for a controlled `500`-iteration diagnostic, but pressure-outlet setting inactivity and residual-export behavior still need cleanup before treating it as a polished baseline automation workflow.

## Recovery Plan
1. For setup `07`, proceed with steam-carryover/DPM efficiency checks without reopening bottom/brine-outlet troubleshooting.
2. Record residual/monitor stability for `PLS-PRO-2026-06-03-A`.
3. Run DPM diameter checks at `5 um`, `10 um`, and `40-41 um`.
4. Keep `FFF-2` and `MWH-WP-2026-05-07-A` as historical troubleshooting references only unless the project scope later returns to brine-drainage or water-pool modelling.
5. For the new one-inlet PyFluent path, keep `trial4` plus the completed `500`-iteration diagnostic as the active local baseline and clean up pressure-outlet setting order plus residual export before extending much further.

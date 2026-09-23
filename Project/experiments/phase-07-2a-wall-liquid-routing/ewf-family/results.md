# Phase 7.2A Family E — Execution result

## Native phase-2 volume-fraction contours — 2026-09-23

The three Fluent-native contours use the preserved final native-8586
case/data pairs, X–Y centre cut at Z = 0 m, `phase-2-vof`, fixed 0–1 scale,
and matching orthographic camera and 2400 × 1800 export. Source identities
and settings are in the [E0 export manifest](../../../../PyAnsys/output/phase72a_e0_native_vof_contour_20260923/export-manifest.json)
and [E1/E3 export manifest](../../../../PyAnsys/output/phase72a_e1_e3_native_vof_contours_20260923_v2/export-manifest.json).

E0 — smooth, EWF off:

![E0 phase-2 volume fraction on the X–Y centre cut at native 8586](../../../../PyAnsys/output/phase72a_e0_native_vof_contour_20260923/P72A-E0-phase2-vof-xy-z0-final8586.png)

E1 — smooth, basic EWF:

![E1 phase-2 volume fraction on the X–Y centre cut at native 8586](../../../../PyAnsys/output/phase72a_e1_e3_native_vof_contours_20260923_v2/P72A-E1-phase2-vof-xy-z0-final8586.png)

E3 — basic EWF plus R3 roughness:

![E3 phase-2 volume fraction on the X–Y centre cut at native 8586](../../../../PyAnsys/output/phase72a_e1_e3_native_vof_contours_20260923_v2/P72A-E3-phase2-vof-xy-z0-final8586.png)

At this scale E0 and E1 look similar; all three cuts are mostly low phase-2
volume fraction with a narrow wall-adjacent cyan region and no distinct thick
liquid layer. These are bulk-liquid contours, not EWF film-thickness contours.
The independent E1/E3 film-thickness reports remain zero, so film cannot be
inferred from these colours alone. The first E1/E3 export attempt had an
off-centre crop and was not used for interpretation.

## E1/E3 film thickness and steamoutlet liquid escape — 2026-09-23

The [paired history figure](../../../../PyAnsys/output/phase72a_family_e_e1_e3_film_escape_20260923/film-thickness-and-steamoutlet-escape.png)
uses the 300 file-backed samples at native 5590–8580 (10-iteration cadence).
On the active `wall` film surface, both maximum and area-weighted EWF film
thickness were exactly zero at every sample for E1 and E3. This is a measured
zero signal, not a missing report. The [aligned values](../../../../PyAnsys/output/phase72a_family_e_e1_e3_film_escape_20260923/aligned-film-escape.csv)
and [source/summary record](../../../../PyAnsys/output/phase72a_family_e_e1_e3_film_escape_20260923/summary.json)
preserve report identities and original Fluent flux signs.

The phase-2 `steamoutlet` signed flux is negative for outflow. Shown as
positive escape magnitude, its native 7590–8580 mean was 24.3617 kg/s for
E1 and 24.6178 kg/s for E3 (+0.2561 kg/s, +1.05%). E3 also had a strong
early transient, peaking at 37.06 kg/s, before its later narrower range.
Neither run demonstrates nonzero film formation; the escape contrast should
not be attributed to film drainage. E3's roughness is the controlled physical
delta relative to E1, but this history alone does not prove a steady response.

## Liquid-inventory comparison — 2026-09-23

The [inventory figure](../../../../PyAnsys/output/phase72a_family_e_liquid_inventory_comparison_20260923/liquid-inventory-comparison.png)
compares total and lower-zone continuous-liquid mass for E0, E1, and E3 on
the shared native 5590–8580 coordinates (300 points, every 10 iterations).
E2 is excluded because its FPE prevented a comparable continuation. E0's
per-iteration file was sampled only at E1/E3's coordinates; the [aligned
values](../../../../PyAnsys/output/phase72a_family_e_liquid_inventory_comparison_20260923/aligned-inventory.csv)
and [summary](../../../../PyAnsys/output/phase72a_family_e_liquid_inventory_comparison_20260923/summary.json)
retain exact source paths and statistics.

| Case | Mean total liquid mass, 7590–8580 (kg) | Mean lower-zone liquid mass (kg) | Final shared total / lower (kg) |
| --- | ---: | ---: | ---: |
| E0 | 295.936 | 0.08376 | 295.915 / 0.04573 |
| E1 | 295.936 | 0.08376 | 295.915 / 0.04573 |
| E3 | 297.890 | 0.17549 | 298.101 / 0.35701 |

E0 and E1's four liquid-inventory histories are exactly identical at all 300
shared coordinates. E3 has 1.953 kg (+0.660%) more total liquid and 0.09173 kg
(+109.5%) more lower-zone liquid on the final-window mean. Its total inventory
has a large early transient before approaching a higher level; the lower-zone
signal remains intermittent. These are solver-history comparisons, not proof
of steady storage or drainage. Film mass is zero in E1/E3, so the E3 contrast
is consistent with the roughness delta rather than demonstrated film capture.

## Updated result — 2026-09-23 (supersedes the recovery block below)

E0, basic-EWF E1, and the human-selected E1-plus-R3-roughness E3 each
completed an independent 3,000-native-iteration continuation from the verified
native-5586 parent. Their final native coordinate is 8586, and their local and
durable final case/data pairs, 12 paired Fluent-local autosaves, and required
report histories were verified. E1 and E3 recorded zero film mass, thickness,
velocity, outflow, and Courant throughout; neither demonstrates film capture
or drainage. Reverse flow and turbulent-viscosity limiting persisted without
AMG/FPE/nonfinite/fatal events in these completed cases.

| Case | Treatment | Result | Phase-2 `steamoutlet` mean, native 7590–8580 (kg/s) |
| --- | --- | --- | ---: |
| E0 | EWF off, `k_s=0` | complete to 8586 | `-24.3686` |
| E1 | basic EWF, accretion off, `k_s=0` | complete to 8586; film reports zero | `-24.3617` |
| E2 | EWF plus phase accretion, `k_s=0` | FPE at 5653; no final pair | unavailable |
| E3 | E1 basic EWF plus R3 roughness, `k_s=5e-4 m`, `C_s=0.5` | complete to 8586; film reports zero | `-24.6178` |

Fluent signs are retained (negative means outflow). The E0 mean uses 991
per-iteration points; E1 and E3 use 100 points at 10-iteration cadence over
the same native window. E1 differs from E0 by less than 0.1%; E3's carryover
magnitude is about 1.05% greater than E1's. Solver completion is not a steady
or physical validation claim.

E2 was built, saved/reopened, and instrumented with the live phase-accretion
fields `film-phase2-mass` and `film-phase2-mass-collection`. Film mass rose
from about `0.059 kg` at 5590 to `0.170 kg` at 5640. At 5650 maximum film
thickness hit its configured `0.01 m` limit and maximum film Courant jumped
to about `5.1e5`; film/bulk residuals then diverged with AMG and FPE events.
No 250-iteration checkpoint was reached. A separately labelled technical
recovery, changing only the initial film time step from `1e-4` to `1e-6 s`,
reproduced a floating-point exception near 5652. Its Python client remained
unresponsive after the FPE and was terminated without terminating Fluent;
therefore its manifest is stale at `RUNNING_FLUENT_NATIVE_SOLVE`. The clean
pre-solve pair was preserved. A bounded MCP status probe then found the
student Fluent endpoint unresponsive. An additional proposed recovery that
changes only film sub-iterations from 5 to 20 remains unrun.

Evidence: [E0 manifest](../../../../PyAnsys/output/phase72a_ewf_family_e_student_20260922T115500Z/E0/run-manifest.json),
[E1 manifest](../../../../PyAnsys/output/phase72a_ewf_student_e1_run_20260923T024000Z/E1/run-manifest.json),
[E2 manifest](../../../../PyAnsys/output/phase72a_ewf_student_e2_run_20260923T031600Z/E2/run-manifest.json),
[E3 manifest](../../../../PyAnsys/output/phase72a_ewf_student_e3_run_20260923T032500Z/E3/run-manifest.json),
[E2 time-step recovery receipt](../../../../PyAnsys/output/phase72a_ewf_student_e2_dt_recovery_build_20260923T035600Z/probe-receipt.json),
and [recovery run manifest](../../../../PyAnsys/output/phase72a_ewf_student_e2_dt_recovery_run_20260923T040000Z/E2/run-manifest.json).

The supported conclusion is a negative basic-EWF and EWF-plus-R3 screen in
this model. E2's intended 3,000-iteration accreting-film comparison is not
available; its early numerical failure does not falsify phase accretion as a
physical mechanism. No steady, wall-film-closure, or plant-performance claim
is supported. The historical block text below describes the superseded
Server-3 preflight state, not the current student result.

## Status

**RECOVERY BLOCKED after pre-solve capability probing — 2026-09-22.** The
assigned Server 3 endpoint became reachable at `10.104.145.176:62530` after
the environment was refreshed. The exact 5586 parent and its terminal state
were verified. No `/solve/iterate` command was issued for E0, E1, or E2.

A generated Fluent 2025 R2 TUI wrapper passed the hyphenated film material
`water-liquid-at-psep` as an unquoted Scheme symbol during a disposable E1
build probe. Fluent rejected the material input and then its owned solver ranks
terminated with `SIGSEGV`. This is an implementation failure before a valid
child build, not a numerical failure or scientific result. Server 3 is now
offline at the configured endpoint and the repository is attach-only, so the
queue requires a restarted Fluent endpoint before recovery can continue.

The superseded initial preflight receipt is
[`connectivity-receipt-20260922.json`](../../../../PyAnsys/output/phase72a_ewf_server3_preflight/connectivity-receipt-20260922.json).

The preserved no-solve capability receipts are
[`phase72a_ewf_capability_probe_20260922T103703Z.json`](../../../../PyAnsys/output/phase72a_ewf_capability_probe_20260922T103703Z.json),
[`phase72a_ewf_wall_probe_20260922T103703Z.json`](../../../../PyAnsys/output/phase72a_ewf_wall_probe_20260922T103703Z.json), and
[`phase72a_ewf_basic_build_probe_20260922T104950Z.json`](../../../../PyAnsys/output/phase72a_ewf_basic_build_probe_20260922T104950Z.json).

## Required queue and what was tested

| Case | Requested delta | Result |
|---|---|---|
| E0 | EWF off, `k_s = 0`, independent 5586 control copy | Pre-solve setup attempted; inherited roughness helper rejected an invalid field; no solve |
| E1 | Basic EWF on, `k_s = 0` | Independent capability copies saved; model and `wall` film-zone controls exposed; material configuration probe invalid; no solve |
| E2 | EWF on + phase accretion, `k_s = 0` | Not built or solved; official 2025 R2 semantics verified, live mutation still pending |

The authoritative parent was loaded read-only and remains untouched. All
written case/data artifacts are independent Fluent-local probe copies under
`C:\Users\syok443\Documents\FluentRuns\Phase72A\FamilyE`. None was accepted as
a valid scientific child and none was iterated.

## Preflight evidence

The refreshed endpoint attached to Fluent 2025 R2 and loaded the exact parent
pair. SHA-256 verification matched the phase handoff:

- case: `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`;
- data: `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`.

The authoritative `P71V2Iteration` report read `5586`. The terminal absorber,
inventory, and phase-resolved outlet reports matched the handoff. The parent
also read back as Mixture/RNG k-epsilon, smooth-wall, EWF-off, with the v2
absorber/source scaffold intact.

The live EWF probe established that the film wall control is exposed at
`wall.phase[mixture].wall_film`, and zone `wall` is Fluent film-wall ID 33.
`bottom` remained a non-film wall. EWF field availability included film mass,
thickness, velocity components/magnitude, Courant number, coverage, and film
outflow mass. Fluent's separate DPM erosion/accretion model remained off and
must not be substituted for EWF secondary-phase accretion.

## Scientific evidence status

There are no E0/E1/E2 solve histories, active-horizon checkpoints, valid film
transfer histories, outlet comparisons, residual histories, plots, or results
to interpret. In particular, no claim can be made about EWF carryover
reduction, film accretion, film drainage, or numerical health.

Historical repository code contains EWF diagnostic scaffolding and prior
Fluent 2025 R2 naming candidates, but those records were not used as live
readback and cannot substitute for the mandatory current-session audit of:

- EWF enabled state and active film walls;
- basic EWF versus phase-accretion controls;
- film mass/inventory and film velocity/flow toward the lower region;
- bulk-to-film accretion and film-to-bulk transfer; and
- native report definitions and incremental output paths.

## Recovery condition

Resume only after Server 3 exposes a restarted Fluent session and the refreshed
endpoint is recorded in `PyAnsys/.env`. Reload and reverify the authoritative
parent rather than any invalid probe child. Use a quoted native film-material
command, reject any Fluent transcript error, and require the exact material,
model-parameter, film-wall, roughness-zero, DPM-erosion-off, instrumentation,
and save/reopen readbacks before solving. Then execute E0, E1, and E2 in order,
with one native `/solve/iterate 3000` command per valid child as explicitly
requested for this run.

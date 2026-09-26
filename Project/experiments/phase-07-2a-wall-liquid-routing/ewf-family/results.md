# Phase 7.2A Family E — Execution result

## E4 — direct EWF film feed attempt — 2026-09-25

This exploratory branch started from the verified native-5586 baseline pair
and localized the intended `116.92 kg/s` liquid feed to a `0.00331036 m²`
wall patch. However, the executed patch used the EWF Initial Condition User
Source Terms, not the proposed EWF Boundary Condition Film Mass Flux. The
saved start pair round-tripped the requested adaptive settings
(`Co_max=0.5`, initial film step `1e-4 s`, increase/decrease `2`, three film
sub-iterations, stop residual `1e-3`, first-order implicit, EWF Coupled
Solution ON, Flow Momentum Coupling OFF). Pressure-gradient driving was OFF
in the case, although the direct-film proposal called for it ON.

The run stopped at native 5871 after 285 iterations (last report row 5870).
Film elapsed time reached only `2e-4 s` before adaptive steps collapsed to
sub-picosecond scale. The `0.3 m` thickness cap was hit; peak film Courant
was about `6.7e3`, and peak velocity about `5.49e10 m/s`. At the last monitor
row, reported film mass was `13.948 kg`, cumulative outflow `69.009 kg`, and
total liquid mass `128.110 kg`. Phase-2 steamoutlet flux was `-11.657 kg/s`
(negative is outflow). `P71V2Command` remained `116.92 kg/s`, while removal
was only `6.944 kg/s` and command error `-109.976 kg/s`. The command targeted
the original bulk inlet despite that inlet being set to zero; it is invalid
for a direct-film branch and must be disabled/redefined before retry.

Only one paired autosave was created, at native 5750 (164 iterations beyond
the parent), and the local Fluent transcript was preserved. The machine
receipt and raw monitor streams are in
[`PyAnsys/output/phase72a_ewf_e4_direct_film_fast_20260925T104504Z`](../../../../PyAnsys/output/phase72a_ewf_e4_direct_film_fast_20260925T104504Z);
the exact parent/start/checkpoint hashes and process outcome are recorded in
`run_receipt.json`. No Fluent process remains open.

**Interpretation:** this is a failed setup/solver screen, not evidence against
the direct EWF boundary condition and not a physical film or carryover result.
The next attempt needs the native Boundary Condition film mass/momentum flux
fields, zero bulk phase-2 absorber command/source, and pressure-gradient
driving ON. E2.7 remains the strongest successful wall-film development
evidence in this family, with its existing limits.

## Native phase-2 volume-fraction contours — 2026-09-23

The four Fluent-native contours use the preserved final native-8586
case/data pairs, X–Y centre cut at Z = 0 m, `phase-2-vof`, fixed 0–1 scale,
and matching orthographic camera and 2400 × 1800 export. Source identities
and settings are in the [E0 export manifest](../../../../PyAnsys/output/phase72a_e0_native_vof_contour_20260923/export-manifest.json),
[E1/E3 export manifest](../../../../PyAnsys/output/phase72a_e1_e3_native_vof_contours_20260923_v2/export-manifest.json),
and [E2.7 export manifest](../../../../PyAnsys/output/phase72a_e27_native_vof_contour_20260923/export-manifest.json).

E0 — smooth, EWF off:

![E0 phase-2 volume fraction on the X–Y centre cut at native 8586](figures/E0-phase2-vof-xy-z0-final8586.png)

E1 — smooth, basic EWF:

![E1 phase-2 volume fraction on the X–Y centre cut at native 8586](figures/E1-phase2-vof-xy-z0-final8586.png)

E3 — basic EWF plus R3 roughness:

![E3 phase-2 volume fraction on the X–Y centre cut at native 8586](figures/E3-phase2-vof-xy-z0-final8586.png)

E2.7 — phase accretion enabled, Flow Momentum Coupling off:

![E2.7 phase-2 volume fraction on the X–Y centre cut at native 8586](figures/E2.7-phase2-vof-xy-z0-final8586.png)

At this scale E0 and E1 look similar; all four cuts are mostly low phase-2
volume fraction with a narrow wall-adjacent cyan region and no distinct thick
liquid layer. These are bulk-liquid contours, not EWF film-thickness contours.
The independent E1/E3 film-thickness reports remain zero, while E2.7 has a
measured nonzero but thin wall film. Film thickness cannot be inferred from
these bulk-volume-fraction colours alone. The first E1/E3 export attempt had an
off-centre crop and was not used for interpretation.

## E1/E3 film thickness and steamoutlet liquid escape — 2026-09-23

The [paired history figure](figures/E1-E3-film-thickness-and-steamoutlet-escape.png)
uses the 300 file-backed samples at native 5590–8580 (10-iteration cadence).
On the active `wall` film surface, both maximum and area-weighted EWF film
thickness were exactly zero at every sample for E1 and E3. This is a measured
zero signal, not a missing report. The [aligned values](../../../../PyAnsys/output/phase72a_family_e_e1_e3_film_escape_20260923/aligned-film-escape.csv)
and [source/summary record](../../../../PyAnsys/output/phase72a_family_e_e1_e3_film_escape_20260923/summary.json)
preserve report identities and original Fluent flux signs.

### Interpretation of the zero-thickness histories

The zero is consistent with the E1/E3 configuration. EWF was enabled and
solved on `wall`, but both cases used `secondary_phase_mode=0` (phase
accretion off); the wall film began with zero film height. DPM coupling,
phase change, and an imposed film source were also off. Thus these runs had no
configured source to transfer the continuous phase-2 liquid into the wall
film. Fluent documents Eulerian secondary-phase capture as the separate
Phase Accretion interaction, with the collected secondary-phase material
matching the film material ([2025 R2 model options](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html),
[2025 R2 theory guide](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html)).
The E1 transcript shows the film solver advancing, and the thickness histories
are populated at every sample, so the recorded zero is consistent with a dry
film state rather than a missing report. E3 kept the same no-accretion EWF
settings while changing roughness; its zero film history therefore does not
test whether phase-2 liquid would accrete under active Phase Accretion. The
recorded settings are preserved in the [E1 manifest](../../../../PyAnsys/output/phase72a_ewf_student_e1_run_20260923T024000Z/E1/run-manifest.json),
[E3 manifest](../../../../PyAnsys/output/phase72a_ewf_student_e3_run_20260923T032500Z/E3/run-manifest.json),
and [EWF configuration probe](../../../../PyAnsys/output/phase72a_ewf_student_e1_build_20260923T022700Z/probe-receipt.json).

The phase-2 `steamoutlet` signed flux is negative for outflow. Shown as
positive escape magnitude, its native 7590–8580 mean was 24.3617 kg/s for
E1 and 24.6178 kg/s for E3 (+0.2561 kg/s, +1.05%). E3 also had a strong
early transient, peaking at 37.06 kg/s, before its later narrower range.
Neither run demonstrates nonzero film formation; the escape contrast should
not be attributed to film drainage. E3's roughness is the controlled physical
delta relative to E1, but this history alone does not prove a steady response.

## Liquid-inventory comparison — 2026-09-23

The [inventory figure](figures/E0-E1-E3-liquid-inventory-comparison.png)
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
| E2.1 | E2 plus `0.3 m` maximum film thickness | reached cap at 5650; FPE at 5653; no final pair | unavailable |
| E2.2 | E2.1 plus 20 film sub-iterations | reached cap at 5650; FPE at 5653; no final pair | unavailable |
| E2.3 | E2.2 plus `1e-6 s` initial film time step | reached cap at 5647; FPE at 5653; no final pair | unavailable |
| E2.4 | E2.1 with adaptive film Courant `0.05` | reached cap at 5737; FPE at 5742; no final pair | unavailable |
| E2.5 | E2.1 with fixed `1e-6 s` film time step | reached cap at 6018; FPE at 6022; no final pair | unavailable |
| E2.6 | E2.1 with 10 sub-iterations, fixed `1e-5 s`, Courant `0.05`, Coupled Solution ON | cap at 5760; FPE at 5765; 26 native reports recovered through 5764 | unavailable |
| E2.7 | E2.6 settings with film-wall Flow Momentum Coupling OFF; Phase Accretion and Coupled Solution ON | complete to 8586; no cap or FPE; 26 native reports recovered | `-1.7361` |
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
This initial mass increase is direct evidence that the phase-accretion setup
did create film before the numerical failure; it does not provide a completed
carryover or drainage comparison.
No 250-iteration checkpoint was reached. A separately labelled technical
recovery, changing only the initial film time step from `1e-4` to `1e-6 s`,
reproduced a floating-point exception near 5652. Its Python client remained
unresponsive after the FPE and was terminated without terminating Fluent;
therefore its manifest is stale at `RUNNING_FLUENT_NATIVE_SOLVE`. The clean
pre-solve pair was preserved. A bounded MCP status probe then found the
student Fluent endpoint unresponsive. An additional proposed recovery that
changes only film sub-iterations from 5 to 20 remains unrun.

## E2.1 — maximum-thickness sensitivity — 2026-09-23

E2.1 repeated E2 from the verified native-5586 parent, changing only Fluent's
maximum film thickness from `0.01 m` to `0.3 m`. The saved/reopened build
read back `0.3 m`, with phase accretion active. Fluent native Report Files
were configured at frequency `1` and recovered for all 26 active reports;
each contains 67 samples at every native iteration from 5586 through 5652.
The maximum and area-weighted thickness, film mass, phase-2 film
mass/collection, film outflow/velocity, maximum film Courant, phase-resolved
outlet flux, inventory, absorber, and closure definitions are in the
[recovered native histories](../../../../PyAnsys/output/phase72a_ewf_student_e21_run_20260923T052000Z/E2.1/e21-native-report-histories_20260923_173131.json).

The maximum film thickness first reached the configured `0.3 m` cap at native
5650, the same iteration at which E2 reached its `0.01 m` cap. One iteration
earlier, at 5649, maximum thickness was `0.007735 m`, area-weighted thickness
was `4.51e-6 m`, total film mass was `0.212 kg`, and maximum film Courant was
already `24.6`. At 5650 the capped maximum was `0.30000001 m`, film mass
jumped to `7.03 kg`, and maximum film Courant to `5.09e5`. The last report
sample at 5652 shows area-weighted thickness `0.154 m`, film mass `7256 kg`,
and infinite maximum film Courant. Those terminal film values are part of
numerical divergence and are not physically meaningful predictions. The
transcript records very large residuals, AMG divergence, and a floating-point
exception at native 5653. See the [iteration figure](figures/E2.1-native-iteration-monitoring.png)
and machine-readable [summary](../../../../PyAnsys/output/phase72a_ewf_student_e21_run_20260923T052000Z/E2.1/e21-summary.json).

Raising the cap moved the clipping value from `0.01 m` to `0.3 m` but did not
prevent the early instability. The event still reaches the active thickness
limit at 5650, so this run cannot tell us whether an unconstrained film would
have remained stable beyond that value. There is no valid post-parent
checkpoint: the first scheduled 250-iteration checkpoint was not reached.
The prepared native-5586 pair and all per-iteration reports are preserved.
E2.1 is a numerical block, not a completed carryover or drainage comparison.

## E2.2 — sub-iteration recovery — 2026-09-23

E2.2 repeated E2.1 from the verified native-5586 parent and changed only the
EWF film sub-iterations from 5 to 20. The `0.3 m` thickness cap, phase
accretion, `1e-4 s` initial film time step, and other settings were preserved
and verified after save/reopen. Native Report Files were configured at
frequency `1`; all 26 active files were recovered with 67 samples each from
5586 to 5652. The [native histories](../../../../PyAnsys/output/phase72a_ewf_student_e22_run_20260923T053831Z/E2.2/e22-native-report-histories_20260923_174911.json),
[aligned E2.1/E2.2 history](../../../../PyAnsys/output/phase72a_ewf_student_e22_run_20260923T053831Z/E2.2/e21-e22-aligned-film-history.csv),
and [summary](../../../../PyAnsys/output/phase72a_ewf_student_e22_run_20260923T053831Z/E2.2/e22-summary.json) preserve the samples.

E2.2 also first hit the `0.3 m` cap at 5650 and failed with AMG divergence and
FPE at 5653. At 5649, one iteration before the cap, its maximum thickness
(`0.02165 m`) and maximum Courant (`342`) were already above E2.1's
`0.007735 m` and `24.6`. By 5652 the reported film mass had risen to
`10070 kg` and maximum Courant was infinite; these are numerical-divergence
artifacts, not physical predictions. Raising sub-iterations did not prevent
or delay the cap/FPE event and the run produced no valid post-parent
checkpoint. The [paired figure](figures/E2.1-E2.2-iteration-monitoring.png)
shows the two histories on the same native-iteration axis.

## E2.3 — reduced initial film time step — 2026-09-23

E2.3 repeated E2.2 from the verified native-5586 parent, changing only the
initial film time step from `1e-4 s` to `1e-6 s`; the `0.3 m` cap and 20 film
sub-iterations were retained. The saved/reopened readback confirmed all three
settings. Native Report Files were configured at frequency `1`; all 26 active
files were recovered with 67 samples each from native 5586–5652. Evidence is
preserved in the [native histories](../../../../PyAnsys/output/phase72a_ewf_student_e23_run_20260923T055258Z/E2.3/e23-native-report-histories_20260923_180234.json),
[aligned E2.1–E2.3 histories](../../../../PyAnsys/output/phase72a_ewf_student_e23_run_20260923T055258Z/E2.3/e21-e23-aligned-film-history.csv),
[summary](../../../../PyAnsys/output/phase72a_ewf_student_e23_run_20260923T055258Z/E2.3/e23-summary.json), and [comparison figure](figures/E2.1-E2.3-iteration-monitoring.png).

The smaller initial step did not postpone the instability. Maximum thickness
first hit `0.3 m` at native 5647, three iterations earlier than E2.1/E2.2;
maximum film Courant was `21661` at 5647, `12894` at 5649, and `5.18e13` at
5650. Film mass rose from `0.114 kg` at 5646 to `12.61 kg` at 5647, then to
`10219 kg` by the last sample at 5652 as maximum Courant became infinite.
These post-onset values are numerical divergence artifacts. The transcript
records AMG divergence and FPE at 5653. No 250-iteration checkpoint was
reached, and no valid post-parent case/data pair exists.

Across E2.1–E2.3, changing the cap, film sub-iterations, and initial film
time step did not prevent the early FPE. All three reached the `0.3 m` cap
before failure. The evidence shows numerical instability in this setup; it
does not establish that phase accretion itself is physically invalid. No
carryover, drainage, steady-state, or physical-thickness claim is supported.

## E2.4 — lower adaptive film Courant number — 2026-09-23

E2.4 repeated the E2.1 phase-accretion case independently from the verified
native-5586 parent, retaining its `0.3 m` thickness cap, five film
sub-iterations, and `1e-4 s` initial film step. The only scientific control
change was adaptive EWF maximum Courant `0.25 -> 0.05`. Fluent-native surface
report definitions for maximum/area-average film thickness, total film mass,
film Courant, and phase-accretion quantities were linked to Report Files at
every iteration. The native flow residual monitor was retained, and the
native EWF sub-iteration residuals (`h`, `u`, `v`) were printed to the solve
transcript every film sub-iteration.

E2.4 reached the `0.3 m` maximum film-thickness cap at native `5737` and then
failed with FPE at `5742`; the last complete report sample is `5741`. Compared
with E2.1 (cap at `5650`, FPE at `5653`), the lower adaptive Courant delayed
the cap by 87 iterations and the FPE by 89. It did not prevent cap-reaching or
numerical failure. During terminal divergence, maximum film Courant and the
`h/u/v` residuals became astronomically large or infinite; terminal film mass
and thickness after the cap are not physically interpretable.

Evidence is in the [E2.4 setup and result](e2.4/setup.md), the [E2.1/E2.4/E2.5
cap-hit comparison figure](figures/E2.1-E2.5-film-thickness-monitoring.png), [native
every-iteration report histories](../../../../PyAnsys/output/phase72a_ewf_student_e24_run_20260923T060500Z/E2.4/e24-native-report-histories_20260923_182121.json),
[summary](../../../../PyAnsys/output/phase72a_ewf_student_e24_run_20260923T060500Z/E2.4/e24-summary.json),
and [failure transcript](../../../../PyAnsys/output/phase72a_ewf_student_e24_run_20260923T060500Z/E2.4/transcript-failure-tail.txt).
This supports only that the Courant change delayed the instability in the
observed run; it does not establish stable film transport or reduced carryover.

## E2.5 — fixed EWF film time step — 2026-09-23

E2.5 independently repeated E2.1 from the verified native-5586 parent, with
the `0.3 m` thickness cap and five film sub-iterations retained. The adaptive
film-step flag was OFF and Fluent's fixed EWF `Time-Step` read back as
`1e-6 s` before and after save/reopen. Fluent-native definitions for maximum
and area-average thickness, total film mass, Courant, and the phase-accretion
reports were linked to native Report Files at every iteration. All 26 active
report files were recovered. Flow residuals were retained with Fluent's
residual history; EWF `h/u/v` residuals were present in the native solve
transcript at each film sub-iteration.

Maximum thickness reached the `0.3 m` cap at native `6018`, then Fluent raised
an FPE at `6022`; the last complete report sample is `6021`. This delayed the
E2.1 cap/FPE coordinates (`5650`/`5653`) by 368/369 iterations, and extended
the E2.4 cap/FPE coordinates (`5737`/`5742`) by 281/280 iterations. It did not
avoid cap-reaching or numerical failure. In the divergence tail the EWF
residuals reached `1e210`–`1e215`; maximum Courant also exploded. Film mass
and thickness values after the cap are not interpretable as physical results.

See the [E2.5 setup and result](e2.5/setup.md), [native every-iteration
reports](../../../../PyAnsys/output/phase72a_ewf_student_e25_run_20260923T062200Z/E2.5/e25-native-report-histories_20260923_183617.json),
[summary](../../../../PyAnsys/output/phase72a_ewf_student_e25_run_20260923T062200Z/E2.5/e25-summary.json),
and [native solve transcript](../../../../PyAnsys/output/phase72a_ewf_student_e25_run_20260923T062200Z/E2.5/transcript-native-solve.txt).

E2.5's fixed step prolonged the observed response in that separate setup, but
did not establish stable film growth, drainage, or reduced carryover. The user
later selected the combined E2.6 controls; its outcome is reported below.

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


## E2.6 — combined EWF controls — 2026-09-23

E2.6 was built independently from the verified native-5586 parent. The saved
and reopened model read back 10 film sub-iterations, Courant `0.05`, adaptive
stepping OFF, fixed EWF timestep `1e-5 s`, EWF Coupled Solution ON, and the
exploratory `0.3 m` thickness cap. The Courant value is inactive for timestep
selection with adaptive stepping OFF. The fixed film timestep stayed at
`1e-5 s`; the film solver typically stopped at 6–8 sub-iterations while
residuals met its tolerance, then used all 10 in the unstable tail.

Fluent reached the thickness cap at native `5760` and raised an FPE at native
`5765`; the last complete native report sample is `5764`. All 26 configured
Fluent Report Files were recovered, each containing 179 samples from 5586
through 5764. Maximum film Courant first exceeded `0.05` at 5673 despite the
fixed timestep, which confirms why the stored Courant control should not be
read as a timestep limiter in this run.

At the cap-hit iteration, maximum thickness was `0.300000012 m`, while
area-weighted thickness was `0.000658 m`. It remained capped through the last
report point, when area-weighted thickness had risen to `0.1825 m`. Reported
film mass rose from `0.00232 kg` at 5587 to `30.96 kg` at the cap, then to
`8593.59 kg` at 5764. Maximum film Courant escalated from `0.0876` at 5757 to
`2596.6` at 5759, `7.56e5` at 5760, and infinity at the last point. EWF `h/u/v`
residuals reached about `2.43e175`, `3.46e175`, and `1.73e172`; Fluent also
flagged AMG divergence in `k` and `epsilon` before the FPE. The cap and
post-cap values describe numerical runaway and cannot be interpreted as
physical film thickness, mass, or transport.

Relative to E2.1, the combined E2.6 run delayed cap/FPE by 110/112 iterations.
It delayed them 23/23 iterations relative to E2.4 and reached them 258/257
iterations earlier than E2.5. Since E2.6 changed several settings together,
these timings do not isolate any one control's effect. No completed outlet,
drainage, or carryover comparison is available.

The [E2.6 setup](e2.6/setup.md), [monitoring figure](figures/E2.6-combined-film-monitoring.png),
[native every-iteration report histories](../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/e26-native-report-histories_20260923_190209.json),
[summary](../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/e26-summary.json),
[run manifest](../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/run-manifest.json),
and [native solve transcript](../../../../PyAnsys/output/phase72a_ewf_student_e26_run_20260923T065114Z/E2.6/transcript-native-solve.txt)
preserve the result.


## E2.7 — Flow Momentum Coupling off — 2026-09-23

E2.7 repeated E2.6 from the verified native-5586 parent with the same
exploratory `0.3 m` film-thickness cap, 10 maximum film sub-iterations, fixed
film timestep `1e-5 s`, Courant setting `0.05`, adaptive stepping OFF, and EWF
Coupled Solution ON. The sole intended setting change was disabling Flow
Momentum Coupling on film wall `wall`; Phase Accretion remained ON. Saved and
reopened readback confirmed both switches independently. With Flow Momentum
Coupling OFF, gas-to-film momentum influence remains one-way and the film does
not feed momentum back to the bulk flow; this is distinct from both Phase
Accretion and the EWF Coupled Solution algorithm ([Fluent boundary control
documentation](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_boundary_conditions_task_page.html),
[Fluent EWF model controls](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_models_task_page.html)).

The full 3,000-iteration continuation completed at native 8586. Fluent
recovered all 26 native Report Files, each with 3,001 per-iteration samples
from 5586 through 8586. There was no cap hit, FPE, AMG divergence, nonfinite
report, or fatal event. Reverse flow and turbulent-viscosity limiting were
still flagged. The maximum reported film thickness was `0.0003310 m`
(0.331 mm), versus the `0.3 m` cap; the terminal area-weighted thickness was
`0.00006607 m` (0.0661 mm). Film mass reached `3.111 kg` at the final report
point. In the final native 7590–8580 window it rose from `2.149` to `3.106 kg`,
while maximum thickness varied from `0.297` to `0.328 mm`. The film remained
small relative to the configured cap, but its upward trend means this window
does not establish a stationary film state.

At the shared native coordinate 5760, E2.7 reported maximum thickness
`0.0000703 m` and film mass `0.235 kg`; E2.6 was already at the cap
(`0.300000 m`) with `30.96 kg` reported film mass and then failed at 5765.
This is a clear difference in numerical response for these runs, but it is
not a matched stable comparison beyond E2.6's failure point. The comparison is visualized below; the successful-run
phase-2 outlet history is in the [flux comparison](#successful-e-family-phase-2-steamoutlet-flux-comparison--2026-09-23).

![E2.6 and E2.7 maximum film thickness and total film mass](figures/E2.6-E2.7-flow-momentum-coupling-comparison.png)

[Open the thickness and film-mass comparison](figures/E2.6-E2.7-flow-momentum-coupling-comparison.png).
 In the later
7590–8580 window, phase-2 `steamoutlet` signed flux averaged `-1.7361 kg/s`
(negative is outflow), total liquid inventory averaged `63.03 kg`, and absorber
removal averaged `98.23 kg/s` against a `116.92 kg/s` command. The inventory
and absorber signals were moving or off-command, so this continuation does
not establish source-inclusive closure, steady carryover, improved drainage,
or a physical carryover benefit. EWF residuals remained finite overall, but
their early transient maxima were large (`h=1.83e3`, `u=2.75e4`, `v=105`);
completion alone does not demonstrate convergence.

The Courant setting `0.05` was retained and verified but is inactive for
timestep selection because adaptive stepping was OFF. The actual reported
maximum film Courant reached `0.225` and ended at `0.143`. Thus, within this
particular numerical setup, turning Flow Momentum Coupling off prevented the
cap/FPE sequence seen in E2.6 over the tested 3,000 iterations. It does not
isolate a general physical effect, prove the film solution is converged, or
qualify Phase Accretion as a predictive carryover mechanism.

See the [E2.7 setup and readback](e2.7/setup.md), [E2.6/E2.7 film
comparison](figures/E2.6-E2.7-flow-momentum-coupling-comparison.png),
[native report histories](../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/report-histories.json),
[summary](../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/e27-summary.json),
[run manifest](../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/run-manifest.json),
and [native solve transcript](../../../../PyAnsys/output/phase72a_ewf_student_e27_run_20260923T071523Z/E2.7/transcript-native-solve.txt).

## Successful E-family phase-2 `steamoutlet` flux comparison — 2026-09-23

![Successful E-family phase-2 steamoutlet flux comparison](figures/e-family-phase2-steamoutlet-flux.png)

This simple linear-scale plot compares only E0, E1, E3, and E2.7, the four
successful E-family runs, over their shared native window 5590–8580. All
series use the same 10-iteration coordinates; per-iteration E0/E2.7 histories
were sampled at those existing coordinates without interpolation. Negative
Fluent flux is outflow. E0 and E1 stay near `-24.4 kg/s`; E3 has a strong early
transient before returning near that range. E2.7 trends upward from the same
starting range to about `-1.74 kg/s` by the end. This is
a history comparison only and does not establish that E2.7's change is a
physical carryover reduction.

The [aligned values](figures/e-family-phase2-steamoutlet-flux.csv) and
[Matplotlib script](../../../../PyAnsys/scripts/inspection/plot_phase72a_ewf_family_steamoutlet.py)
preserve the source and plotting method.

## E2.7 continuation — another 5,000 iterations on Server 1 — 2026-09-23

![E2.7 continuation liquid inventory, phase-2 outlet flux, EWF film mass and wetted area, average film speed, and maximum film thickness](figures/E2.7-CONT5000-requested-histories.png)

The completed TUI continuation covered native iterations 8586–13586. All 26
Fluent-native Report Files were active at every iteration and each history has
5,001 points including the starting coordinate. The solver returned normally;
the run manifest records no FPE, AMG, nonfinite, or fatal event. EWF residuals
were captured in the transcript (49,972 residual rows). The [run manifest](../../../../PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z/run-manifest.json),
[report histories](../../../../PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z/report-histories.json),
[figure values and statistics](figures/E2.7-CONT5000-requested-histories-manifest.json),
and [plotted CSV](figures/E2.7-CONT5000-requested-histories.csv) retain the
measurements.

Total liquid inventory fluctuated between `62.894` and `63.086 kg` and ended
at `62.989 kg`, only `0.034 kg` below its starting value. Phase-2
`steamoutlet` signed mass flux remained negative (outflow): it ranged from
`-1.746` to `-1.719 kg/s` and ended at `-1.735 kg/s`. These outlet and
inventory histories were comparatively level over the extension, but they do
not establish source-inclusive closure.

The EWF signals continued to change: reported film mass rose throughout the
extension from `3.111` to `5.842 kg` (about 88%); area-weighted average speed
rose from `46.34` to `82.41 m/s`. Maximum film thickness varied between
`0.275` and `0.531 mm` and ended at `0.310 mm`. The latter stayed far below
the configured `0.3 m` cap, with no cap event, but the film-mass and speed
trends mean this horizon still does not show a stationary film response.

At iteration 13586, the EWF wetted area was `50.690 m²` (`94.86%` of the
active EWF wall). Fluent defines Film Coverage as 1 when film thickness is
above its critical value and 0 when below; for EWF the critical thickness is
`1e-10 m`, and the surface integral of Film Coverage gives wetted area
([Fluent Theory Guide, Partial Wetting Effect](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_wet.html),
[Fluent field-variable definition](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_fvdefs.html)).
The value was reconstructed from terminal per-face EWF thicknesses and mesh
face areas in the hash-verified final Fluent HDF5 pair. The 3,463-face mesh
area sum (`53.4369523 m²`) matches the earlier Fluent-native wall-area report
to `1.4e-14 m²`; 2,529 faces exceed the wetness threshold. Another 282 faces
have positive thickness below the threshold and are counted dry by Fluent's
coverage definition. The [wetted-area evidence record](../../../../PyAnsys/output/phase72a_e27_cont5000_wetted_area/wetted-area.json)
preserves this calculation. Server 1 became unreachable when I attempted a
live Film Coverage report, so the result is reconstructed from the exact
Fluent-documented coverage threshold and the preserved terminal mesh/data
instead of a newly computed native report definition. The wetted area is
measured only at the final iteration; the run did not retain its full time
history.

The final-state Fluent-native [phase-2 volume-fraction contour](figures/E2.7-CONT5000-phase2-vof-xy-z0-final13586-v3.png)
uses the X–Y centre cut at Z = 0 m and a fixed physical 0–1 scale. The cut
appears predominantly near zero phase-2 volume fraction at this full scale;
the image does not provide a useful resolution of small local values, and it
cannot be used to infer EWF film thickness. Its [native export manifest](../../../../PyAnsys/output/phase72a_e27_cont5000_native_vof_v3/export-manifest.json)
records the field, range, source-pair hashes, and Fluent view settings.

This was a continuation, not a new physics contrast. The copied OneDrive
starting pair was verified loaded at native 8586 with E2.7 settings, but its
hashes differ from those in the earlier E2.7 run manifest. That source-identity
limitation remains attached to the extension. Completion and relatively level
outlet/inventory signals do not establish convergence, stable film behaviour,
drainage, source-inclusive closure, or a physical carryover benefit. The
[continuation setup](e2.7-continuation-5000/setup.md) and [native contour export
script](../../../../PyAnsys/scripts/inspection/export_phase72a_e27_cont5000_vof_v3.py)
record the analysis path.

## E2.8 — adaptive speed screen with fixed-step recovery — 2026-09-26

E2.8 started independently from the exact native-5586 baseline pair used by
E2.7 (case SHA-256
`4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`; data
SHA-256 `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`).
It retained E2.7's EWF Coupled Solution, Phase Accretion, Flow Momentum
Coupling OFF, mesh, flow, and `0.3 m` exploratory thickness cap, and applied
the combined fast controls recorded in the [E2.8 setup](e2.8/setup.md).

The aggressive adaptive branch reached a close match to E2.7 at native 7000
after 1,414 additional iterations. It then developed nonphysical film values.
The paired native-7000 state was preserved; the subsequent 318 divergent
iterations were excluded from the selected trajectory. Recovery used E2.7's
fixed `1e-5 s` film step, ten maximum film sub-iterations, and `1e-5` stop to
continue the saved state through native 8586. Thus the selected trajectory has
3,000 additional iterations (1,414 adaptive plus 1,586 fixed-step recovery),
while total solver work was 3,318 iterations. The native-8586 pair is a
recovered hybrid result, not a successful 3,000-iteration run of the
aggressive adaptive profile.

The final case/data pair was saved locally and copied to OneDrive with matching
hashes: case SHA-256 `eec5e1a319bb23be81f85edfb49171fe2d262159eaabbb4dba09999e6f197fcc`;
data SHA-256 `b9d1b70f4a34fa9570a9b8ac67e1c686fc142c563d5d80a3a63a1e6edf0b67b0`.

### Early adaptive match

The native-7000 comparison below uses E2.7's native-8586 endpoint as the
reference. The area-threshold values use the same saved-pair face geometry
reconstruction for both runs.

| Measure | E2.7 at 8586 | E2.8 at 7000 | Difference |
| --- | ---: | ---: | ---: |
| Film mass | 3.1112 kg | 3.2007 kg | +2.9% |
| Maximum thickness | 0.3310 mm | 0.3078 mm | -7.0% |
| Area-weighted thickness | 0.06607 mm | 0.06797 mm | +2.9% |
| Area-weighted film speed | 46.34 m/s | 45.36 m/s | -2.1% |
| Maximum film speed | 222.07 m/s | 221.25 m/s | -0.4% |
| Reconstructed Film Coverage | 50.1453 m² | 50.2027 m² | +0.11% |
| Wall area with thickness ≥ 0.01 mm | 45.3449 m² | 46.3220 m² | +2.15% |
| Wall area with thickness ≥ 0.05 mm | 21.3569 m² | 22.2961 m² | +4.40% |
| Wall area with thickness ≥ 0.10 mm | 13.9070 m² | 13.9150 m² | +0.06% |
| Wall area with thickness ≥ 0.25 mm | 1.5479 m² | 1.6730 m² | +8.08% |
| Wall area with thickness ≥ 0.50 mm | 0 m² | 0 m² | 0 m² |

E2.8 had advanced `0.02930 s` of EWF time by native 7000, compared with
`0.03000 s` after E2.7's 3,000 fixed steps. The adaptive trajectory therefore
reached a similar reported film state in 47.1% of the iteration count, but
this state was not numerically converged and the fast profile did not remain
stable.

### Thickness-distribution areas

Area values are reconstructed from EWF film height on 3,463 faces of `wall`.
The reconstructed total wall area is `53.436952299276584 m²`; Fluent reports
`53.4369522992766 m²`, an absolute difference of `1.42e-14 m²`. The 250-step
checkpoint CSV covers 12 paired snapshots plus the native-5586 start and
native-8586 final pairs.

| Thickness area | E2.7 at 8586 | E2.8 at 7000 | E2.8 at 8586 |
| --- | ---: | ---: | ---: |
| Film Coverage, height > 1e-10 m | 50.1453 m² | 50.2027 m² | 50.3946 m² |
| ≥ 0.01 mm | 45.3449 m² | 46.3220 m² | 48.1630 m² |
| ≥ 0.05 mm | 21.3569 m² | 22.2961 m² | 27.3846 m² |
| ≥ 0.10 mm | 13.9070 m² | 13.9150 m² | 21.2575 m² |
| ≥ 0.25 mm | 1.5479 m² | 1.6730 m² | 1.3059 m² |
| ≥ 0.50 mm | 0 m² | 0 m² | 0 m² |
| 0–0.01 mm | 8.0921 m² | 7.1149 m² | 5.2739 m² |
| 0.01–0.05 mm | 23.9879 m² | 24.0259 m² | 20.7785 m² |
| 0.05–0.10 mm | 7.4500 m² | 8.3811 m² | 6.1270 m² |
| 0.10–0.25 mm | 12.3591 m² | 12.2421 m² | 19.9516 m² |
| 0.25–0.50 mm | 1.5479 m² | 1.6730 m² | 1.3059 m² |
| ≥ 0.50 mm | 0 m² | 0 m² | 0 m² |

Fluent's native per-iteration Film Coverage integral is retained separately
from this checkpoint reconstruction. At E2.8 native 8586 the native monitor
is `50.2051 m²`, versus `50.3946 m²` from reconstructed face areas. The two
values are not substituted for each other; the same reconstruction method is
used for the E2.7/E2.8 thickness-distribution comparison.

### Recovered endpoint and numerical limits

At native 8586 the selected hybrid path reports `4.2484 kg` film mass,
`0.3026 mm` maximum thickness, `0.09022 mm` area-weighted thickness,
`63.14 m/s` area-weighted film speed, `230.19 m/s` maximum film speed,
`50.3946 m²` reconstructed Film Coverage, and maximum film Courant `0.1366`.
Compared with E2.7 at native 8586, this endpoint has 36.6% greater film mass,
36.6% greater area-weighted thickness, and 36.3% greater area-weighted speed;
maximum thickness is 8.6% lower and reconstructed coverage is 0.50% higher.
The adaptive branch's film elapsed time was `0.02930 s` at native 7000; the
hybrid endpoint reached `0.04516 s`, compared with `0.03000 s` for E2.7's
3,000 fixed steps.

The adaptive segment hit its three-sub-iteration limit in all 1,414 selected
updates, and none ended with the last captured `h/u/v` residuals all at or
below the configured `1e-3` stop. At native 7195, maximum thickness reached
`0.11091 m` and area-weighted speed reached `73,395 m/s`. Maximum film CFL
reached `4.3616` at 7197 and the adaptive timestep collapsed to about
`9.54e-11 s`; the divergent branch was stopped at 7318.

In fixed-step recovery, 230 of 1,586 updates ended with all three last-captured
EWF residuals at or below `1e-5`, while 1,551 updates reached the 10-substep
cap. The largest selected-path residuals occurred at native 7395
(`h=2.01e5`, `u=2.23e5`, `v=1.71e3`). The selected recovery manifest records
no FPE, AMG divergence, nonfinite, or fatal-event flags, but these facts do not
establish EWF convergence. The combined fast-control package also cannot
attribute the early match or later instability to any single setting.

The run captured 37 native reports at all 3,001 selected coordinates. EWF
fields include mass, maximum and area-weighted thickness, film Courant,
cumulative outflow, phase-accretion mass and collection coefficient, film and
free-surface speed/velocity components, effective pressure, film and
stripping Weber numbers, and per-iteration Film Coverage. DPM-to-film source
mass, stripped mass, and separated mass were unavailable in the allowed
surface-report field list.

![E2.8 per-iteration film response](e2.8/figures/film-response.svg)

![E2.8 reconstructed wall area by thickness](e2.8/figures/wet-area-by-thickness.svg)

![E2.8 EWF numerical health and transfer](e2.8/figures/ewf-numerical-health.svg)

See the [setup and execution record](e2.8/setup.md), [all 3,001 per-iteration
report rows](../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/e28-per-iteration-history.csv),
[checkpoint thickness-area table](../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/checkpoint-area/checkpoint-thickness-area.csv),
[response analysis summary](../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/e28-response-summary.json),
[recovery manifest](../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/recovery-run-manifest.json),
[initial fast-run manifest](../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/run-manifest.json),
[analysis manifest](../../../../PyAnsys/output/phase72a_ewf_direct_e28_20260926T010700Z/analysis-manifest.json),
and [run paths](e2.8/run-paths.yaml).

**Interpretation:** E2.8 demonstrates that the aggressive adaptive controls
can approach E2.7's observed film response in fewer iterations, but the same
profile becomes unstable soon afterward. The recovered native-8586 endpoint
is a different hybrid trajectory with elevated film mass, mean thickness,
speed, and film physical time. This is numerical response evidence only; it
does not establish a stationary film, drainage, source-inclusive closure, or
improved physical carryover.

## E2.81 — slightly tightened adaptive EWF — 2026-09-26

E2.81 repeated the fast adaptive phase-accretion run from the same exact
native-5586 parent as E2.7/E2.8 and completed all 3,000 requested iterations
to native 8586. It used maximum film Courant `0.4`, timestep increase `1.5`,
four maximum film sub-iterations, and stop `5e-4`; adaptive stepping remained
on from `1e-4 s`, with decrease factor `2`. EWF Coupled Solution and Phase
Accretion remained on, film-wall Flow Momentum Coupling remained off, the
maximum thickness cap remained `0.3 m`, and the film wall remained `wall`.
The exact setup and per-run paths are in the [E2.81 setup](e2.81/setup.md)
and [run-path record](e2.81/run-paths.yaml).

The run reached an E2.7-like observed film state by native 7196, after 1,610
additional iterations (46.3% fewer than E2.7's 3,000 iterations to native
8586). At that point mass, thickness, speed, and reconstructed wet area were
all close to the E2.7 endpoint:

| Measure | E2.7 at 8586 | E2.81 at 7196 | Difference |
| --- | ---: | ---: | ---: |
| Film mass | 3.1112 kg | 2.9093 kg | -6.5% |
| Maximum thickness | 0.3310 mm | 0.3249 mm | -1.8% |
| Area-weighted thickness | 0.06607 mm | 0.06178 mm | -6.5% |
| Area-weighted film speed | 46.34 m/s | 40.92 m/s | -11.7% |
| Maximum film speed | 222.07 m/s | 219.53 m/s | -1.1% |
| Reconstructed Film Coverage area | 50.1453 m² | 50.0237 m² | -0.24% |
| Wall area with thickness ≥ 0.01 mm | 45.3449 m² | 45.5518 m² | +0.46% |
| Wall area with thickness ≥ 0.05 mm | 21.3569 m² | 20.6108 m² | -3.5% |
| Wall area with thickness ≥ 0.10 mm | 13.9070 m² | 11.9549 m² | -14.0% |
| Wall area with thickness ≥ 0.25 mm | 1.5479 m² | 1.4952 m² | -3.4% |
| Wall area with thickness ≥ 0.50 mm | 0 m² | 0 m² | 0 m² |

This is a close intermediate match and it survived E2.8's known divergence
window: at native 7196 E2.81 reported maximum CFL `0.2976`, not the E2.8
runaway CFL/thickness/velocity pattern. Its film-time increment then was
`0.02647 s`; by native 8586 it had advanced `0.03582832 s`, 19.4% more film
time than E2.7's `0.03000 s` over the same iteration horizon.

The terminal distribution had drifted from the early E2.7-like state. At
native 8586 E2.81 reported `3.1610 kg` film mass, `1.4068 mm` maximum
thickness, `0.06713 mm` area-weighted thickness, `216.13 m/s` area-weighted
speed, and `1204.65 m/s` maximum speed. Relative to E2.7 at the same endpoint,
mass is 1.6% higher and area-weighted thickness is 1.6% higher, while maximum
thickness is 4.25 times higher, area-weighted speed is 4.66 times higher, and
maximum speed is 5.42 times higher. Fluent's native Film Coverage integral is
`51.7618 m²`; independent face-area reconstruction gives `51.8122 m²`.
Against E2.7's reconstructed `50.1453 m²`, E2.81 has 3.3% more covered area,
but less area at or above `0.05 mm` (`14.0482` vs `21.3569 m²`) and `0.10 mm`
(`9.4663` vs `13.9070 m²`), with more area at or above `0.25 mm` (`4.1391`
vs `1.5479 m²`) and `0.50 mm` (`0.7213` vs `0 m²`). The wet-area measure
and height-threshold reconstruction are distinct diagnostics.

All 37 Report Files contain 3,001 native coordinates. They cover film mass,
maximum and area-weighted thickness, film Courant, cumulative outflow,
phase-accretion mass and collection, film and free-surface velocity, pressure,
Weber/stripping indicators, Film Coverage, and inherited phase-2 outlet,
absorber, and closure signals. DPM-to-film source, stripped mass, and separated
mass were unavailable in the Fluent surface-report field list. Film height
was reconstructed over all 3,463 `wall` faces at 12 250-step checkpoint pairs
plus the named start, native-7196 review, and final pairs. Reconstructed wall
area `53.436952299276584 m²` matches Fluent's `53.4369522992766 m²` within
`1.42e-14 m²`; tables include cumulative areas at five thickness thresholds
and six disjoint thickness bands.

The selected trajectory completed without FPE, AMG-divergence, nonfinite, or
fatal-event flags, and without discarded iterations. However, it is not
numerically qualified as a stable/converged film solution: 2,998 of 3,000
updates reached the four-sub-iteration cap, only 10 ended with all last
captured `h/u/v` residuals at or below `5e-4`, and the largest per-step
residual maxima occurred at native 7764 (`h=2.08e10`, `u=2.31e11`,
`v=2.58e8`). Late film speeds and maximum thickness were also elevated. The
combined control changes do not identify which setting enabled survival of
the earlier risk window or drove later response. This remains an exploratory
numerical screen; it does not establish steady convergence, drainage,
source-inclusive closure, or physical carryover benefit. The sum of per-batch
solve timers was about 2 h 23 min despite reaching the E2.7-like state in
fewer iterations.

The final local and OneDrive case/data pairs have matching SHA-256 hashes:
case `affb844234e602f829f2ee42817329df573c13390e52b698c4012ace44a7a6e3`,
data `7168fb166294d9a253916bb6e0caabb675da3599716728c101e133d6cb992dd9`.
The [E2.81 response figure](e2.81/figures/film-response.svg), [wet-area
figure](e2.81/figures/wet-area-by-thickness.svg), and [numerical-health
figure](e2.81/figures/ewf-numerical-health.svg) summarize the full trajectory.
The [all-iteration history](../../../../PyAnsys/output/phase72a_ewf_direct_e281_20260926T052048Z/e281-per-iteration-history.csv),
[checkpoint thickness-area table](../../../../PyAnsys/output/phase72a_ewf_direct_e281_20260926T052048Z/checkpoint-area/checkpoint-thickness-area.csv),
[response summary](../../../../PyAnsys/output/phase72a_ewf_direct_e281_20260926T052048Z/e281-response-summary.json),
[run manifest](../../../../PyAnsys/output/phase72a_ewf_direct_e281_20260926T052048Z/run-manifest.json),
and [checkpoint-area result](../../../../PyAnsys/output/phase72a_ewf_direct_e281_20260926T052048Z/checkpoint-area/checkpoint-thickness-area.json)
retain the underlying evidence.

## E2.82–E2.84 — fixed EWF timestep screen — 2026-09-27

### Question and controlled comparison

Test fixed film timesteps of `1.25e-5`, `1.50e-5`, and `1.75e-5 s` against
E2.7's `1e-5 s`, seeking faster film buildup without E2.81's large excursions.
Each case was loaded independently from the verified common native-5586 parent
(case SHA-256 `4fd493972839929f1f0922ad42679456d1f4aea294da86e4b13d6b7c32f754fc`;
data SHA-256 `b2261fac8626b2e338c3a9c80c334c8a910d1bfb536f782ef9234623f00e1a72`).
All three completed exactly 3,000 added iterations to native 8586. Adaptive
stepping was OFF; EWF Coupled Solution was ON; wall Flow Momentum Coupling was
OFF; Phase Accretion was ON; each used 10 maximum film sub-iterations and a
`1e-5` residual stop. The stored Courant setting `0.05` was inactive in fixed
mode. Start-pair reopen and one-step report-write gates passed for each run;
final local and OneDrive case/data SHA-256 pairs match.

### Film response at matched physical time

Compare E2.7 at 0.030000 s with each candidate at the closest attainable
0.030000 s (`0.029995 s` for E2.84). This removes the extra film-time advance
that would otherwise make equal-iteration endpoints misleading.

| Case | Native iteration at ~0.03 s | Film mass (kg) | Max thickness (mm) | Area-weighted thickness (mm) | Area-weighted speed (m/s) | EWF max CFL |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E2.7, `1e-5 s` | 8586 | 3.1112 | 0.3310 | 0.06607 | 46.339 | 0.1427 |
| E2.82, `1.25e-5 s` | 7986 | 3.1442 | 0.3296 | 0.06677 | 46.451 | 0.1781 |
| E2.83, `1.50e-5 s` | 7586 | 3.1770 | 0.3280 | 0.06752 | 46.573 | 0.2137 |
| E2.84, `1.75e-5 s` | 7300 | 3.2092 | 0.3260 | 0.06820 | 46.701 | 0.2498 |

At matched film time, E2.82 adds only 1.1% film mass and 0.24% area-weighted
speed over E2.7. E2.83 and E2.84 show 2.1% and 3.1% more mass at this early
coordinate, but both later enter grossly nonphysical states. These small early
differences do not establish a sustained increase in buildup rate.

At equal iteration 8586, E2.82 reports `3.6650 kg` film mass versus E2.7's
`3.1112 kg` (+17.8%), but it has also advanced to 0.0375 s rather than 0.0300 s.
The time-normalized endpoint film accumulation is about 5.8% lower for E2.82
(97.7 versus 103.7 kg/s from the common zero report origin). Thus the apparent
same-iteration gain is explained by its 25% longer film-time interval; it is
not evidence of faster average buildup.

### Numerical health and full-horizon endpoints

| Case | Film time at 8586 (s) | Endpoint film mass (kg) | Endpoint max thickness (mm) | Peak CFL (native iteration) | Peak max film speed (native iteration) | EWF residual maxima `h / u / v` | Steps ending with all `h/u/v <= 1e-5` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E2.7 | 0.0300 | 3.1112 | 0.3310 | 0.2248 (6268) | 262.2 m/s (6268) | baseline residual transcript not available in this comparison set | — |
| E2.81 adaptive | 0.03583 | 3.1610 | 1.4068 | 58.60 | 4.733e9 m/s | `2.083e10 / 2.314e11 / 2.580e8` | 10 / 3000 ended below its looser `5e-4` stop |
| E2.82, `1.25e-5 s` | 0.03750 | 3.6650 | 0.3577 | 3.314 (8537) | 4,169.5 m/s (8537) | `6.852e7 / 2.440e8 / 5.973e5` (8246) | 262 / 3000 |
| E2.83, `1.50e-5 s` | 0.04500 | 4,543.9 | 300 (cap) | 2.032e8 (7965) | 1.435e11 m/s (8094) | `1.536e11 / 1.606e11 / 2.779e9` | 56 / 3000 |
| E2.84, `1.75e-5 s` | 0.05250 | 4,902.8 | 300 (cap) | 2.600e8 (8227) | 1.508e11 m/s (8571) | `1.250e11 / 1.892e11 / 2.078e9` | 44 / 3000 |

E2.82 is the best of these three numerical responses. Relative to E2.81 its
peak CFL is about 18 times lower, its peak speed is over six orders of
magnitude lower, its maximum `h/u/v` residuals are roughly 300–950 times
lower, and its endpoint maximum thickness is about four times lower. It still
is not stable or converged: its CFL and maximum-speed peaks are still about
15 and 16 times E2.7's respective maxima over the same native interval. It
has a late CFL/speed burst at native 8537, and only 262 of 3,000 updates ended
with all last captured EWF residuals below the stricter `1e-5` stop. The run
completed without FPE, AMG divergence, nonfinite, or fatal-event flags, but
these flags do not certify a valid film solution.

E2.83 first reached the `0.3 m` exploratory thickness cap at native 7800;
E2.84 reached it at 7473. Their later mass, thickness, velocity, CFL, and
residual values are nonphysical. Both are rejected as fixed-step candidates.
The growth excursions begin near 0.033 s in both runs. E2.82 remains far more
bounded but develops a residual spike near 0.0333 s and its largest speed/CFL
spike near 0.0369 s.

### Decision and evidence

Do not adopt E2.83 or E2.84. E2.82 is substantially less pathological than
E2.81, but this screen does not show a meaningful sustained buildup-rate gain
at matched physical time, and its late spike leaves stability unproven. Keep
E2.7 as the reference; if the timestep study continues, the next useful range
is closer to `1e-5 s` than the failed `1.5–1.75e-5 s` settings, with any new
comparison judged at matched film time and with the same per-iteration residual
and velocity checks.

The trajectories are available as [film mass](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/film-mass-total.svg),
[area-weighted speed](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/velocity-mag-awavg.svg),
[maximum thickness](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/thickness-max.svg),
and [maximum CFL](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/courant-max.svg), plotted against film elapsed time. The [3,001-point matched history CSV](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/ewf-timestep-screen.csv)
and [machine-readable summary](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/ewf-timestep-screen-summary.json)
retain the numerical values. Per-case manifests and histories are under the
[E2.82 output](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_e2.82_20260926T134145Z),
[E2.83 output](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_e2.83_20260926T144249Z),
and [E2.84 output](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_e2.84_20260926T154347Z)
folders; their paired final Fluent files are indexed in each case's `run-paths.yaml`.

### Phase-2 `steamoutlet` flux overlay across E2.7–E2.84

The signed phase-2 `steamoutlet` flux is negative for outflow. The plot compares
all 3,001 native-iteration points from 5586 to 8586 for E2.7, E2.8, and E2.81–E2.84.
E2.8 uses its selected trajectory: the adaptive prefix followed by the recorded
fixed-step recovery from native 7000 after the adaptive branch diverged.

E2.82, E2.83, and E2.84 exactly overlay E2.7 at every recorded native iteration.
Their terminal-window mean (`7590–8580`) is `-1.736142505 kg/s`, and their native-8586
endpoint is `-1.736546967 kg/s`, the same as E2.7. E2.8 and E2.81 have small
transient departures, with maximum absolute difference `0.126516 kg/s` at native
5736; their terminal-window means are `-1.739938826` and `-1.740602294 kg/s`,
respectively. By native 8586 their endpoint differences from E2.7 are only
`-0.004075` kg/s (E2.8) and `-0.006989 kg/s` (E2.81).

This confirms that the fixed-timestep E2.82–E2.84 changes did not alter this
bulk phase-2 outlet history in the recorded trajectory, consistent with film
Flow Momentum Coupling OFF. The flux overlay alone does not measure liquid
captured by the wall film or establish a carryover mechanism.

[Open the six-case flux plot](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/phase2-steamoutlet-flux-e2.7-to-e2.84.svg)
or its [native-iteration CSV](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/phase2-steamoutlet-flux-e2.7-to-e2.84.csv)
and [summary](../../../../PyAnsys/output/phase72a_ewf_fixed_dt_comparison_20260927/phase2-steamoutlet-flux-e2.7-to-e2.84-summary.json).

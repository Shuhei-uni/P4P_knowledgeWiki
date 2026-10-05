# Audit and current decision

## Verified from preserved machine evidence

Offline audit checked all620431 saved N0 cells from the guarded hydrostatic reference. Pressure equals1120000+876.04*9.81*max(0.10−y,0)Pa exactly (maximum error0Pa); phase patch has zero mismatched cells and initial maximum speed is0. The saved settings show gravity(0,−9.81,0), operatingdensity5.73, implicitbodyforce enabled, SIMPLE/pseudo-off, PRESTO!, least-square-cell gradients and the intended K9 outletvent/head expression. Evidence: ../../../PyAnsys/output/hydrostatic-startup-audit/offline-audit.json.

The velocity inlets retain a Supersonic/Initial Gauge Pressure of1140000Pa versus base1120000Pa. Fluent2025R2 UG §8.4.4.1.7 states this is ignored for subsonic flow; it is not evidence of an imposed20kPa pressure boundary. Initializing from a selected inlet could use it, but this builder supplies explicit standard-initialization defaults and then the audited pressurefield. Source: https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_bcs_sec_bound_cond.html .

Two current bounded connection attempts to the owned server1 endpoint timed out. No new solver connection, mutation or solved iteration occurred. The last verified N1/idle/preserved pair is historical; current live state remains unknown. Evidence: ../../../PyAnsys/output/hydrostatic-startup-audit/connectivity.json. The same failure does not imply solver failure or permit use of another owner's session.

## Interpretation and next controlled step

The intended analytic cellpressure/VOF field was installed correctly in the saved starting state. This rules out a simple array/formula mismatch, but not inconsistent face/gradient state or an incompatible discrete hydrostatic balance. The next preferred contrast is the same fresh zero-feed state produced through Fluent's native pressure-patch workflow instead of direct SV_P assignment, holding cell arrays and all physical/numerical settings equal within stated numeric tolerance. This tests initialization-route sensitivity; native patch success alone does not prove every internal auxiliary field was refreshed.

Fluent2025R2 UG §37.9.2 supports native patching with expressions/custom field functions. Installed v252 settings expose calculate_patch with domain/cell_zones/variable and custom-field-function controls; the Real value accepts strings in the generic API, but exact expression/token support requires live verification. A direct expression route is preferred; documented CFF fallback needs live coordinate token discovery. No guessed command is eligible to solve. Documentation does not establish a generic face/gradient-refresh command. Source: https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_solve_initialize.html .

## Operational disposition

Current status is an external connectivity block, with zero new solves spent. The existing30-minute monitor is active, scoped to this new campaign. It should verify connectivity/ownership, notify this planner once connectivity returns, then monitor exact selected run receipts. The planner has human authority to execute subsequent evidence-directed steps inside CONTEXT.md without routine approval. No run is claimed active. Deadline and budget remain fixed; elapsed disconnection does not silently extend them.

## Connectivity recheck, 2 October2026 NZDT

At12:13 NZDT the configured Fluent endpoint10.104.145.174:63084 and the same host's RDP port3389 both timed out after5seconds. The local route uses en0. This does not establish whether the remote host or Fluent process is running; it establishes that these connections are unavailable from this Mac. The configured automation is now PAUSED and the campaign wall deadline10:59 NZDT has passed. No new calculation was launched. Exact probe receipt is PyAnsys/output/hydrostatic-startup-audit/connectivity-recheck.json.

## Connectivity recovered and live audit completed

At12:39 NZDT on2 October, connection to the unchanged server1 endpoint succeeded. Verified nativeN1 idle, expected zero-feed configuration and preserved case/data pair. The read-only audit completed without field mutations or solves; it captured native patch arguments, boundary centroid geometry and pressure samples in PyAnsys/output/hydrostatic-startup-audit. All brine boundary centroids are below the specified+0.10m head (y range−0.502536 to−0.005994m), supporting the submerged linear reservoir-pressure expression. Samples belong to the already-disturbedN1 endpoint and cannot prove N0 face/gradient consistency. Surface pressure sample precision/interpolation also limits pointwise comparisons. The expired execution deadline remains unchanged; monitoring remains paused and no new job was launched.

## Native-patch setup preparation

Human renewed execution after recovery. The first build stopped before any solve because calculate_patch.variable.allowed_values() returned an empty list without argument context. A bounded live query confirmed domains mixture/phase-2 and the correctly dimensioned named expression. The context-free list was not evidence that pressure patching is unsupported; the repaired builder lets the explicit native mixture/pressure command validate the pair and requires full array readback. This is an implementation repair, not a scientific result.

## Verified native pressure build and first launch

The explicit mixture/pressure patch accepted the named expression. Analytic pressure array agreement within1e−8Pa, exact alpha/geometry, physical/numerical settings invariants and saved/reopened settings passed. Native N0 reports zero velocity and zero flow on every phase/mixture boundary, with4096.769804kg liquid. Build receipt is PyAnsys/output/hydrostatic-startup-recovery/build-receipt.json. First job hsr-native-pressure-n500 is launched with its exact receipt/state paths; execution outcome remains pending.

## First contrast result and decision

Native pressure patch stopped atN1 by the unchanged2m/s guard: speed30.891001m/s, liquid mass4111.353916kg (+0.355991% from4096.769804kg), net liquid/vapor/mixture inward flux33.937701/−0.234381/33.703320kg/s. The saved pair, native reports, callback, fullfields/sections and deterministic verifier passed; live idleN1 and lockfree verified. Exactly1 new solve and53.940575 controller-seconds spent. Compared with directSV_P N1 speed10.942883m/s and mass4077.559874kg, the initialization route materially changes the response but does not cure it. This supports route dependence, not a unique auxiliary-field cause. Proceed autonomously to the documented one-change Modified BFW contrast in setup.md; preserve both failed endpoints.

## Second contrast outcome

Modified BFW N1 reproduced the same reported maximumspeed30.891001m/s, inventory4111.353916kg and liquid/vapor/mixture net rates as the native-patched PRESTO! N1 run. It triggered the unchanged speedguard. The setting change was proved by native readback/save-reopen and the runner's complete methods comparison; the outcome is not inferred from a requested setter alone. Fullfield comparison is preserved in native-versus-modified-audit.json. Both exacthorizon/guard artifacts verified and paired endpoints are preserved. Campaign spend2 solved iterations,111.966179 controller-seconds. This does not establish that pressure interpolation never matters; only that this first-iteration guarded response was insensitive to the selected contrast. Proceed to the last permitted unsuccessful mechanism contrast, brine-boundary isolation, with its claim limits in setup.md.

Third-control setup repairs used zero solves: under specified shear, Fluent makes wall_motion inactive; checking that inactive child was corrected without altering the physical setup. Boundary comparison then differed only because the now-empty outlet_vent group was omitted from the native tree, not because another boundary changed. Normalizing empty groups resolves that representation difference while retaining all nonempty boundary comparisons. These are setup repairs, not additional mechanism trials.

## Terminal campaign disposition

Third sealed-brine test stoppedN1 with speed30.938888m/s, liquid inventory4110.242176kg (+0.328854%) and exactly zero native liquid boundary net flow. Pair, fullfields/sections, nativehistory/residuals/callback and deterministic audits verified. Live solver idleN1, controller/worker exited, lockfree. Brinepressure/vent forcing is not necessary for this startup motion; remaining cause is unresolved. The third unsuccessful contrast reaches the predeclared decisionlimit. Campaign closed unqualified; see [closure](closure.md) for comparison, claimlimits and next recommendation. Monitoring paused; no more solves selected.

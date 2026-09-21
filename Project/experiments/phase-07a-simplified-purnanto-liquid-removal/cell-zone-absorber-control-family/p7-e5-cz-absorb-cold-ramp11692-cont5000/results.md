# P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000 results

## Status

`BLOCKED_VERIFIED` — the exact continuation executed on `student` from the
verified active-1,000 parent, passed its preparation/reopen and smoke checks,
then diverged in the block ending at total active iteration `1,970`. The last
valid reported iteration is `1,960`; the requested total-active-5,000 horizon
was not reached. This is a valid partial continuation result, not a failed
setup identity or a qualification result.

Run manifest: continuation manifest (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000-student-20260910T211158Z-manifest.json`

The exact parent was:

```text
Case: C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.cas.h5
Data: C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberCold\20260910T135421Z\P7-E5-CZ-ABSORB-COLD-RAMP11692\P7-E5-CZ-ABSORB-COLD-RAMP11692-active1000.dat.h5
```

The case retained two fluid zones, including the 3,794-cell
`p7-e5-lower-y010` zone. No outlet, patch/reset, remesh, resplit, or absorber
retuning was introduced. The fixed lower-zone phase-2 source command remained
`−116.92 kg/s` and was re-audited every 10 additional iterations.

## Evidence package

| Evidence | Result | Record |
| --- | --- | --- |
| Parent identity and two-zone topology | PASS | Manifest `parent_readback` and `prepared_reopen` |
| Source readback and invariants | PASS | Manifest source tree/invariant records |
| Smoke | PASS at total active 1,050 | Paired active-1,050 case/data |
| Valid continuation histories | PASS through active 1,960 | 18 stitched report histories, 1,960 points each |
| Residual history | PASS through active 1,960 | 7 residual curves, 1,960 points |
| Requested 5,000 horizon | BLOCKED | Solver divergence/fatal diagnostic in block ending at 1,970 |
| Final active-5,000 save/reopen | NOT AVAILABLE | No active-5,000 pair exists |
| F1 inventory figure | COMPLETE through active 1,960 | [F1](figures/F1-stitched-inventory-response.png) |
| F2 source realization figure | COMPLETE through active 1,960 | [F2](figures/F2-source-realization-and-lower-inventory.png) |
| F3 routing/numerical figure | PARTIAL | [F3](figures/F3-routing-and-numerical-credibility.png) |

The last durable case/data pair is the configured autosave at total active
`1,900`:

```text
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberColdContinuation\20260910T211158Z\P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000\checkpoint-1900-1-01900.cas.h5
C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase07\CellZoneAbsorberColdContinuation\20260910T211158Z\P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000\checkpoint-1900-1-01900.dat.h5
```

## Results

The stitched analysis uses the original active-1–1,000 history plus the
continuation’s valid active-1,001–1,960 interval. The invalid report tail after
active 1,960 was excluded. The full machine-readable summary is
analysis.json (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000-student-20260910T211158Z-analysis.json`, with the paired residual artifact at
residuals.json (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-CONT5000-student-20260910T211158Z-residuals.json`.

| Quantity | Parent late window, active 700–1,000 | Valid continuation, active 1,001–1,960 | Interpretation |
| --- | ---: | ---: | --- |
| Total liquid mass slope | `+0.943 kg/iteration` | `+1.066 kg/iteration` | Positive buildup persists and is slightly steeper over the valid continuation window. |
| Total liquid mass at endpoint | `651.30 kg` at 1,000 | `1,655.14 kg` at 1,960 | No bounded total-inventory response is visible before divergence. |
| Lower-zone phase-2 mass | max `~1.0×10⁻⁶ kg` | max `0.0787 kg` | Liquid occasionally reaches the lower zone, but remains negligible relative to total inventory and is not sustained. |
| Lower-zone phase-2 volume | max `~1.14×10⁻⁹ m³` | max `8.93×10⁻⁵ m³` | Same conclusion in volume terms. |
| Integrated phase-2 source | not applicable to parent comparison | `116.9200000000002 kg/s` at all 97 audits | Source realization is numerically exact to max absolute error `1.99×10⁻¹³ kg/s`. |
| Direct phase-1 mass source | OFF | OFF at all audits | No direct vapor mass sink was enabled. |
| Residual endpoint | finite at active 1,000 | divergence trajectory; no valid data after 1,960 | The long continuation exposed numerical deterioration rather than a steady branch. |

The lower-zone inventory is transient and very small. The absorber source is
therefore commanded and accounted for, but the simulation does not show a
substantial liquid pool entering that zone before numerical failure. In
parallel, the total liquid inventory continues to grow. Within the tested
valid interval, this unchanged fixed-rate cold-start absorber does not provide
evidence of a bounded removal state.

The solver diagnostics include frequent reversed-flow and turbulent-viscosity
limiting warnings, followed by divergence/fatal diagnostics in the final
block. These are retained in the manifest and analysis summary; they are not
silently treated as harmless convergence noise.

## Exact-settings recovery attempts

Three recovery attempts were made from the last durable active-1,900 case/data
pair. Neither the first two nor the post-relaunch third attempt introduced an
outlet, patch/reset, remesh, resplit, source-law change, numerical retuning, or
other scientific setting delta. They were performed to distinguish a
transient first-run interruption from a repeatable continuation failure.

| Attempt | Outcome | Evidence |
| --- | --- | --- |
| Recovery 1 | `BLOCKED_REPORT_FILE_SCHEME_QUERY` at active 1,900 | manifest (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-student-20260910T220409Z-manifest.json` and transcript (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-student-20260910T220409Z-residuals-transcript.txt` |
| Recovery 2 | `BLOCKED_REPEATABLE_SOLVER_FAILURE`; observed through active 1,975, with the failure block ending at active 1,970 | manifest (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-R2-student-20260910T221403Z-manifest.json` and transcript (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-R2-student-20260910T221403Z-residuals-transcript.txt` |
| Recovery 3 after Fluent relaunch | `BLOCKED_REPEATABLE_SOLVER_FAILURE`; observed through active 1,975, with the failure block ending at active 1,970 | manifest (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-R3-student-20260910T224003Z-manifest.json` and transcript (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-R3-student-20260910T224003Z-residuals-transcript.txt` |

Recovery 1 passed parent preparation and source readback but the wrapper
stopped on a non-scientific report-file Scheme query immediately after saving
the restarted state. It did not advance the solution and is not treated as
independent solver evidence.

Recovery 2 removed that query and restarted from the same durable active-1,900
pair. It reproduced the primary run's deterioration: epsilon and the flow
field escalated over the same active-1,900-to-1,970 interval, after which
Fluent reported node `SIGSEGV` and the run terminated. This makes the
fixed-rate, frozen-settings continuation a repeatable numerical blocker. It
does not establish behaviour beyond the valid primary active-1,960 history,
and it does not create the requested active-5,000 pair.

After the human relaunched Fluent, Recovery 3 connected to the new endpoint
`10.0.0.5:49468` and repeated the same exact active-1,900 restart. The residual
trajectory, active-1,970 blow-up, and node `SIGSEGV` again matched the earlier
recoveries. This confirms that restarting the Fluent session does not remove
the unchanged-settings solver blocker. Only the active-1,900 paired start
state was durable in this attempt; no active-5,000 pair was written. The
recovery transcript was parsed into R3 residual evidence (local generated artifact): `PyAnsys/output/phase07_cz_absorb_cold_cont5000/P7-E5-CZ-ABSORB-COLD-RAMP11692-RECOVER1900-CONT5000-R3-student-20260910T224003Z-residuals.json`: 76 raw points were captured, of which the active-1,900--1,960 interval is retained as valid and the active-1,970 onward tail is explicitly excluded as numerical-failure evidence.

Because the scientific question was specifically the unchanged continuation,
no further autonomous retry under the same settings is warranted. Any next
attempt that changes numerical stabilization, absorber control/source law,
instrumentation, or the lower-zone definition must be a separately authorized
setup and must preserve the bottom-only, no-outlet boundary intent.

At the final local status check, `student` still responded to ICMP ping but
the configured Fluent endpoint `10.0.0.5:60949` timed out and the gRPC/activity
check reported no live calculation. This is consistent with the Fluent node
failure terminating the session; it is an operational state check, not an
additional scientific result.

## Interpretation and claim limits

The result is evidence against the specific unchanged continuation reaching a
stable 5,000-iteration branch, not evidence that every possible lower-zone
absorber design is impossible. It is also not evidence against the conceptual
brine-pool abstraction itself: the lower-zone volume can still be a legitimate
phase-selective absorption concept, but this fixed-rate/source implementation
did not attract enough liquid into the zone and then became numerically
unstable.

The following limits apply:

- The requested active-5,000 horizon was not achieved; no claim is made about
  behaviour beyond active 1,960.
- The result is a finite-horizon numerical discovery result, not a converged
  or physically qualified separator prediction.
- No vapor-inventory report history was configured in the parent or this
  continuation. Vapor compatibility is therefore assessed only from recorded
  phase-1 boundary fluxes and residual behaviour, and F3 remains partial.
- The 1,900 autosave is the last durable case/data pair. The active-1,960
  state is supported by report/residual histories and the terminal manifest,
  but not by a separately saved 1,960 pair.
- No outlet, field patch/reset, mesh change, source-cap change, or numerical
  retuning was used as an autonomous recovery. Any altered recovery requires
  a separately authorized setup.

## Planned next step

There is no automatic next experiment from this blocked continuation. Preserve
the valid evidence and return the decision to the human. If further work is
authorized, it should be a separately formalized stabilization or absorber
control setup that explicitly addresses the divergence mechanism and the
missing vapor-inventory instrumentation while retaining the bottom-only,
no-outlet scientific boundary. Do not infer a 5,000-iteration result from the
partial run and do not silently change the absorber law.

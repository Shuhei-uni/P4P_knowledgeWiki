# Phase 7b technical diagnostics — 2026-09-10

These are preparation checks on the 620,431-cell full-geometry case, not collector-screen results. All PC operations used Python/PyFluent. The latest source diagnostic completed 50 collector-enabled iterations.

**Current recovery (2026-09-21 NZ):** authenticated health and normal Settings
calls respond again. The loaded S20 case was verified at N0 with unchanged
collector source slots. `P7bMaximumSpeed` was corrected to use
`VelocityMagnitude(phase="mixture")`, saved as a new matching pair and reopened.
The corrected report returns 372.5669852 m/s in the initialized field, and all
screen report definitions compute successfully. No solve was issued by this
repair. The first retry stopped at N0 because the section exporter treated the modern
`SurfaceData` object as a dictionary. The adapter now uses its documented
`vertices`, `face_centroids` and `connectivity` attributes. This was a local
Python error, not a Fluent solver failure. The corrected runner exported four sections with ten finite fields each,
advanced 50 iterations with complete scalar/collector-flux histories, and
saved a matching N50 checkpoint before continuing.
Evidence: `PyAnsys/output/p7b-s020-20260920T221831Z/manifest.json`.
Evidence: `PyAnsys/output/phase07b_preparation/speed-report-repair-20260920T221216Z/result.json`.

**Previous operational block (2026-09-18; access now recovered):** all direct API probes timed
out: health, build-information, Settings and Scheme (8 s deadlines). The
fully instrumented S20 attempt stayed at N0 because `P7bMaximumSpeed` needed
`VelocityMagnitude(phase="mixture")`. At that time the correction was in the runner but
had not reached the saved prepared case. During recovery, the last successful
operation closed the previous native transcript; the next call timed out in
`Settings.GetAttrs` while resolving activity, **before read_case_data was
sent**. No additional solve was issued and no client job remains active.
The timing does not prove transcript closure caused the session stall.

Evidence: `PyAnsys/output/p7b-s020-20260918T065338Z/manifest.json`,
`PyAnsys/output/p7b-s020-20260918T070215Z/{manifest.json,error.txt}`, and
`PyAnsys/output/phase07b_preparation/post-transcript-{api-probe,settings-scheme}-20260918.json`.
The first probe's Settings request had a local schema error; the second used
the correct schema and independently timed out, as did Scheme.

**Recovery action:** regain a responsive PC Fluent API; verify live process,
case and global iteration before any reload or solve. The preserved clean N0
reference and split initial/prepared pairs allow in-scope recovery. Correct the
speed report before use, verify small fixed-section extraction, then execute
the full approved screen. There is no scientific reapproval gate.

**Current recovery:** clean N3 reload and client-exit preservation passed on
2026-09-18. The velocity-expression fault is now reproducible and avoidable:
`Velocity(phase="phase-2").x` emits a Cortex segmentation violation, whereas
`Velocity.x(phase="phase-2")` passes in the clean case. Corrected x/y/z volume
integrals match the native liquid-velocity reports at nonzero slip, with no
recorded Cortex faults. This establishes the phase accessor for the source;
it does not by itself prove pointwise equality or source coupling. Evidence:
`PyAnsys/output/phase07b_preparation/corrected-velocity-validation.json`.

The first source-enabled solve request stayed at N0: Fluent rejected the
explicit phase context on shared k/epsilon expressions. Its API call returned
without raising, so iteration progress must be checked independently before
claiming completion. No history file was expected from that unadvanced solve.
The corrected diagnostic uses unqualified shared turbulence fields and passed
50 iterations from the clean N0 parent with complete scalar/residual histories
and no Cortex fault. At N50 total liquid was 0.00379968 m³ (3.35045 kg), while
collector liquid was effectively zero; this does not demonstrate practical
liquid removal. Evidence: `p7b-source-proof-s20-20260918T063831Z/validation.json`
under the preparation evidence directory. Native applied source at N50 matched
the recomputed N49 source, so both quantities must be retained.

The exact S20 cell-zone split preserves 620,431 cells, 2,852,567 faces and
1,724,499 solver nodes, selects 21,516 cells / 0.56124364 m³, and has zero
mask-membership mismatch. Its two interface face sets contain 7,076 unique
faces. Geometry reconstruction proves c0 inside / c1 outside and area vectors
directed outward; discrete phase-2 flux sums match native phase reports with
the documented opposite sign. Native interior report Net is zero even when
the individual interface contribution is nonzero; it must not be used.
A synchronous callback smoke captured N54–56 and verified every PC-side row.
Evidence: `interface-adjacency-20260918/` and
`callback-smoke-20260918T065246Z/` under the preparation evidence directory. Historical restart/access locks
below are superseded by these in-scope recovery checks.

| Check | Observed result |
| --- | --- |
| Native case/data save and same-session reload | Passed; critical source settings and expression definitions persisted. Liquid-volume reduction differed only by floating-point roundoff. |
| Small pressure and nine-field velocity/UDM exports | Passed on the 827-row liquid inlet. The earlier whole-domain CSV remains incomplete/unverified; its exact write-error cause is unknown. |
| Direct Python cell-volume transfer | Passed: 620,431 finite positive values, about 5 MB; sum agrees with native volume. |
| Five native-expression collector masks | Counts and volumes agree with the prior independent geometry probe. |
| Native-expression liquid volume and inlet mass flow | Evaluated successfully; liquid volume agrees with the native volume report. |
| Six source-expression attachments | Liquid mass and mixture momentum/k/epsilon attached and persisted through save/reload. Sources were then disabled; nonzero source coupling remains untested. |
| Expression metadata | `get_info()` raises a Fluent Scheme type error; `get_state()` and scalar `get_value()` work. |
| Expression report API | Legacy `expression.define` silently stayed blank. Modern `single_valued_expression.definition` readback passed. |
| Report-file setup | Windows path normalization repaired. A subsequent source-free diagnostic wrote both water-volume histories and all active residual rows at N10–13; the volume reports agree exactly. This attempt also reported fatal Cortex errors, so it is not a passed execution smoke. |
| Intermittent client connection stall | Interrupted traceback located the wait in PyFluent API-version discovery via gRPC reflection, before report mutation. Separate health and Settings clients responded. A subsequent bounded connection succeeded; the underlying intermittent fault remains unresolved. |

The reflection wait and historical CSV write error are distinct observations; no causal link is established. The installed reflection request has no explicit deadline. The diagnostic runner now bounds local connection construction and prints its stage; it does not terminate Fluent.

## Evidence and recovery

Generated evidence resides in `PyAnsys/output/phase07b_preparation/`: `diagnostic-recovery.json`, `diagnostic-expressions.json`, `diagnostic-source-persistence.json`, `diagnostic-direct-data.json`, `diagnostic-small-export.json`, `diagnostic-small-velocity.json`, `diagnostic-report-expression-readback.json`, and `diagnostic-report-recording.json`.

PC root: `C:/Users/qtra338/P4P/experiments/phase-07b-full-geometry-liquid-removal`.

The source-free recovery pair is `case-data/p7b-diagnostic-recovery-20260910T065159Z.cas.h5` and `.dat.h5` beneath that root. The expression persistence fixture is `case-data/p7b-expression-diagnostic-20260910T070215Z.cas.h5` and `.dat.h5`; that saved fixture contains enabled source settings and must not be mistaken for the source-free parent. Artifacts are PC-local; replication is unverified.

## Remaining readiness work

Reconcile report-file path normalization, prove file-backed histories and residual capture, verify source coupling and momentum/phase-velocity semantics with nonzero liquid in the collector, and complete mass-flux accounting and initialized smoke checks. Save/reload configuration success is not numerical-stability evidence. The scientific execution gate remains blocked; no 5,000-iteration screen has begun.

**Earlier wrap-up state (superseded by the resumption below):** restored the source-free recovery case/data pair above, steady solver at iteration 10, with mixture and both phase source enables off. No additional diagnostic iterations ran. The local diagnostic clients have exited.

## Historical execution lock after requested resumption

**Observed:** the source-free three-iteration attempt produced two `Cortex received a fatal signal (SEGMENTATION VIOLATION)` messages. Report and residual files contain N10–13, while fresh API iteration readback remained N10. Native and expression water-volume reports match exactly at all four samples. All collector sources were disabled; this is not evidence of collector instability.

**Independent disposition:** `/root/phase7b_cortex_failure_gate` returned `DISCOVERY_EXECUTION: HUMAN_REQUIRED`. Restart Fluent on the PC and expose the API endpoint. No verified remote PC launcher is available under the API-only access constraint. The need for a fresh process is a recovery/trust judgement, not proof of permanent corruption or a diagnosed root cause. No further solves are permitted in this process. A restart must be followed by recovery-identity, progress and clean-recording checks; remaining collector readiness requirements still apply.

Evidence: `diagnostic-recording.trn`, `diagnostic-recording.out`, `diagnostic-recording-validation.json`, `diagnostic-report-recording.json` and `cortex-failure-recovery.json` in the generated evidence directory. A new diagnostic pair was saved and both files verified present at `case-data/p7b-cortex-diagnostic-20260910T104659Z.cas.h5` and `.dat.h5` beneath the PC root; its numerical iteration identity is unresolved, so it is not a screen parent.

**Final recovery verified:** original source-free pair reloaded successfully; Settings readback is steady, N10, mixture/phase sources all off. The recovery client exited successfully. No active job remains. This restores the saved setup but does not clear the fatal-process readiness lock.

## Human-requested fault retest — 2026-09-12

**Observed:** the fault recurred before any solve. The separated setup transcript records five Cortex segmentation-violation messages; the first follows reading the saved expression diagnostic case, before its data-read section. No iteration command was issued. Both direct RP-variable and solver-routed iteration readbacks were 10.

**Observed inherited dependency:** case loading automatically attempted to compile/load historical C probe libraries. `libp7b_velocity_20260908T102329Z` failed compilation and lacked the required parallel host/node DLLs. Other historical probe libraries were also loaded. This was Fluent's automatic case-load behaviour, not a newly requested C build. These dependencies need removal from the Python-only preparation route before reuse. The retest script itself contains no C compilation call.

**Inferred:** stale probe-library dependencies are a concrete candidate explanation, not a proven root cause. The evidence contradicts attributing the fault specifically to starting the solve. Restarting alone has not been shown sufficient if the same saved case reloads the failing dependencies.

**Recovery:** the pre-test matching pair was saved as `case-data/p7b-before-fault-retest-20260912T062151Z.cas.h5` and `.dat.h5` beneath the PC phase root, then reloaded. Both iteration queries returned 10 and all phase/mixture source enables were off. This verifies restored settings, not a fault-free process. No active client or solve remains; the scientific execution lock is unchanged.

Evidence: `PyAnsys/output/phase07b_preparation/fault-retest-20260912T062151Z/result.json`, `setup.trn`, and `error.txt`. Runtime identity was Cortex PID11168 and solver-host PID12200 on EN432647; no earlier PID comparison establishes whether the process was restarted. Next technical recovery must address the saved case's stale library references using the authorized Python API and verify a clean load before another solve.

## Restart and clean mesh recovery — 2026-09-12

**Observed:** user restarted Fluent and enabled the API. Cortex PID11724 and solver-host PID21008 differ from the failed session's PID11168/12200; API port is now59433. Before recovery, cell-zone settings were inactive, consistent with the requested empty session. The original input mesh was accessible.

**Observed clean recovery:** disabled `setup.user_defined.auto_compile_compiled_functions` and verified false, then loaded only `inputs/brine-outlet-620kcells.msh.h5`. The full 620,431-cell mesh loaded in16seconds; the captured transcript contains no Cortex segmentation violation or C compilation attempt. Current UDF state has zero user-defined memory locations and no user scalars. No prior diagnostic case was loaded, and no initialization or iteration was issued.

This demonstrates a clean original-mesh loading route in a new process. It does not prove the stale libraries caused the earlier fault, nor establish reference/source setup, expression-reporting smoke, or scientific run readiness. The live session now contains the original mesh with mesh/default conditions; rebuild the approved reference and native-expression collector through Python rather than importing the old probe-bearing case. The old N10 restoration description is historical, not the current live state.

Evidence: `PyAnsys/output/phase07b_preparation/restarted-session-20260912.json`, `clean-mesh-recovery-20260912.json`, and `clean-mesh-recovery-20260912.trn`. Fluent-side transcript: `logs/p7b-clean-mesh-load-20260912T080009Z.trn` beneath the PC phase root.

## Clean reference proof and current expression failure — 2026-09-12

**Observed successful rebuild:** the new process loaded only the original mesh;
Python applied the approved reference physics and boundary conditions with
C auto-compilation off. Settings matched across case save/reopen. Whole-snapshot
equality did not pass because `domains` metadata populated only after reload;
this is separated from configuration equality. No Cortex error or compiler
attempt appears in the rebuild transcript.

**Observed source-free solve:** the clean initialized pair saved and reloaded,
then three steady iterations completed without recorded Cortex errors. Native
and expression water-volume reports agree exactly at N1–3:
`1.309584994374274e-5`, `2.682039083659162e-5`, and
`4.190719535637436e-5 m3`. All seven active residual histories contain N1–3.
All sources remained off. This is execution smoke evidence, not convergence
or a collector result.

**Counter correction:** the earlier use of `sol/iterations` as physical solve
progress was incorrect: it remained 10 after Hybrid Initialization and after
three main iterations. The documented `Iteration` expression was 0 after
initialized-pair reload and 3 after the solve, consistent with native histories.
Historical RP-counter-based N10/N13 inconsistency interpretations are withdrawn;
this correction does not invalidate the separately recorded Cortex errors.

**Observed subsequent failure:** 30 approved unhooked diagnostic expressions
were staged. During the first x-component phase-velocity comparison, Cortex
reported `SEGMENTATION VIOLATION`. The exception surfaced at expression
`get_value()` / `GetAttrs`, requesting the absolute liquid-minus-mixture
velocity integral. Earlier native-report and liquid-velocity evaluations were
in the same compound statement, and their return values were not persisted.
The exact trigger is therefore unresolved. No collector source was attached
and no additional iteration was issued. Old C dependencies cannot explain all
faults because this new process was rebuilt without loading old cases.

**Independent disposition:** `/root/phase7b_clean_expression_failure_review`
returned `DISCOVERY_EXECUTION: HUMAN_REQUIRED`. Stop further solves in this
process. A human Fluent restart is needed because no remote relaunch route has
been verified under the API-only constraint. After fresh-process verification,
use the saved clean N3 pair and isolate native phase reports, liquid-velocity
expressions and slip expressions one operation at a time, persisting each
stage and capturing its transcript. Source coupling, persistence and smoke,
mask-boundary flux accounting, full instrumentation and all five runs remain
uncompleted. No active job remains.

**Preserved artifacts under the PC root:**

- Clean uninitialized case: `case-data/p7b-clean-reference-20260912T080340Z.cas.h5`.
- Clean initialized N0 pair: `case-data/p7b-clean-initial-20260912T080713Z.cas.h5` and `.dat.h5`; same-process reload passed.
- Clean N3 pair: `case-data/p7b-clean-smoke-20260912T080713Z.cas.h5` and `.dat.h5`; both saved and existence verified before the later diagnostic fault.
- History: `reports/p7b-clean-smoke-20260912T080713Z.out`.
- Transcripts: `logs/p7b-clean-reference-20260912T080340Z.trn`, `logs/p7b-clean-smoke-20260912T080713Z.trn`, and `logs/p7b-clean-smoke-solve-20260912T080713Z.trn`.

These artifacts are `LOCAL_ONLY`; replication and a fresh-process N3 reload
are not yet verified. Do not substitute unsaved post-fault diagnostic state or
old probe-bearing cases for this recovery pair.

Generated evidence in `PyAnsys/output/phase07b_preparation/`:
`clean-reference-rebuild.json/.trn`, `clean-reference-smoke.json`,
`clean-reference-smoke-setup.trn`, `clean-reference-smoke-solve.trn`,
`clean-reference-smoke.out`, `clean-expression-validation.json`, and
`clean-expression-failure.json`. The last JSON preserves the observed exception
and its attribution limit; no separate native transcript of that final probe
was captured.

## Explicitly requested clean-pair reload — 2026-09-12

**Observed:** after the human explicitly requested loading the case, PyFluent
connected to the same Cortex11724/solver21008 process and confirmed both clean
N3 files exist. Automatic C compilation was disabled and verified. The
`read_case_data` request failed with `Stream removed (recvmsg:Connection reset
by peer)` before readback. Transcript-stop recovery did not respond within its
20-second bound. A subsequent five-second TCP probe timed out.

**Current access/state:** the configured endpoint is now unreachable in that
bounded check; loading completion and live case identity are unverified. No
iterations, initialization or save/overwrite were requested. The clean saved
pair was only read. This evidence does not distinguish process termination
from a service/network failure. The previous execution lock remains in force.

Evidence: `PyAnsys/output/phase07b_preparation/requested-clean-reload-20260912T100856Z/`
contains `result.json`, `error.txt` and `post-load-connectivity.json`. The remote
transcript was started but could not be retrieved after the connection reset.

## Shutdown-code attribution review

**Reported:** Shuhei identified scripts shutting down Fluent and pushed fixes.
**Observed at repository HEAD `79dd78a`:** commit `b0ea02f` removed the local
launch helper's `atexit` handler, which called `process.terminate()` for
processes registered by that helper. It also detached the local launch from
the Python client's terminal. Commit `7a3532c` replaced the helper with an
attach-only connection route and added an MCP backend whose cleanup is a
no-op and whose generated-code policy rejects solver lifecycle calls.

**Phase 7b attribution:** the inspected Phase 7b scripts attach to the remote
PC through the common connection helper, contain no explicit solver shutdown
call, and already used `cleanup_on_exit=False` before these commits. The old
local-process registry is populated only by local launches; a mock check
confirmed that an empty registry does nothing and a registered local child is
terminated. Therefore this specific local cleanup defect is not established
as the cause of Phase 7b's recorded Cortex faults or connection reset. Other
PC-side clients/launchers were not observed and cannot be excluded. The newer
MCP backend was not used by the September 12 diagnostics.

**Verification:** 14 connection tests and six native monitor tests passed
without contacting Fluent. The local environment has PyFluent `0.39.0` and
neither `ansys-fluent-mcp` nor `pytest`; the optional MCP integration suite
could not run. The new MCP requirements pin PyFluent `0.42.0`; pulling source
alone does not install that runtime. No dependency changes or live-server
operations were performed during this review. Existing API availability and
crash-cause uncertainty remain unchanged.

Machine evidence: `PyAnsys/output/phase07b_preparation/shutdown-change-audit.json`.

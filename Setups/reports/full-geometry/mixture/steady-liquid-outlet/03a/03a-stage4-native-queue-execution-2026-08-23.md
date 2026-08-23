---
record_type: result-report
programme: full-geometry
geometry: Full-geomV2-231kcells
physics_family: mixture
campaign: steady-liquid-outlet
record_id: 03A-stage4-native-queue-20260822T123011Z
lifecycle: active
---

# 03A Stage 4 — Native-Queue Execution Evidence

## Status

The original non-overwriting queue
`03A-stage4-S4-01-through-S4-04-native-20260822T123011Z` is no longer active.
Its Fluent-owned journal reached S4-02 cumulative iteration `36,000`, the exact
`+30,000` iteration budget from the F06 iteration-6,000 parent, and then
reported a journal-read error before the named endpoint write, residual export
or S4-03 transition.  No NaN, infinity, floating-point exception or explicit
fatal divergence preceded the interruption.

The bounded recovery queue
`03A-stage4-S4-02-forensic-S4-03-S4-04-recovery-20260823T125548Z` is also
stopped.  It preserved the post-interruption S4-02 live field under a unique
forensic name, independently prepared S4-03 and S4-04 from the exact F11
iteration-15,000 case/data pair, and submitted S4-03 as a Fluent-owned native
branch.  S4-03 reached cumulative iteration `42,547` (`+27,547`) before the
owner received `Stream removed (recvmsg:Operation timed out)`.  The target
cumulative-45,000 autosave and named endpoint were absent at reconciliation,
so the owner stopped without replay and S4-04 was not submitted.

## Verified execution evidence

| Branch | Verified state | Classification |
|---|---|---|
| S4-01 | Native journal reached cumulative iteration 33,000 (`+30,000`); the named final case and data both exist | completed diagnostic / unresolved pending checksums, readback and physical-history analysis |
| S4-02 | Native console reached cumulative iteration 36,000 (`+30,000`), then the journal stopped before endpoint write. A unique case/data pair was subsequently saved and hash-verified, but Fluent's post-interruption RP iteration value was `1,556` and cannot be reconciled with the console count | completed iteration budget / forensic live-field preservation / diagnostic-unresolved; not parent-eligible |
| S4-03 | Exact F11 parent hashes and RNG readback passed. Complete paired autosaves were written at 20,000, 25,000, 30,000, 35,000 and 40,000. Transport failed at cumulative iteration 42,547 (`+27,547`), before the 45,000 target and named endpoint | interrupted diagnostic / unresolved; latest complete pair is cumulative 40,000 (`+25,000`), not parent-eligible |
| S4-04 | Exact same F11 parent hashes and standard `k-epsilon` readback passed; prepared under a separate output root and native journal, but never submitted | prepared independent diagnostic / unresolved; not executed |

The final observed S4-02 residual row at cumulative iteration `36,000` was
continuity `0.15066`, `x/y/z` momentum `3.0047e-05`, `2.7322e-05`, and
`3.1789e-05`, `k` `1.4070e-03`, epsilon `0.10394`, and phase-volume-fraction
residual `2.1425e-03`.  This proves completion of the iteration budget, not a
valid saved endpoint or physical convergence.

The last observed S4-03 residual row at cumulative iteration `42,547` was
continuity `1.5239`, `x/y/z` momentum `2.9694e-05`, `2.8665e-05`, and
`3.0068e-05`, `k` `1.6928e-03`, epsilon `0.13969`, and
phase-volume-fraction residual `2.1828e-03`.  Reversed flow on pressure outlet
30 and turbulent-viscosity limiting persisted.  No NaN, infinity,
floating-point exception or explicit fatal numerical divergence was recorded;
the terminal signature is transport/journal failure, not demonstrated solver
divergence.  These residual values do not establish convergence.

## Recovery controls and lineage

- The original queue, observer evidence and failure manifest remain unchanged.
- The first recovery attempt stopped safely during preparation because Fluent
  persisted report paths relative to the prepared-case working directory.  It
  performed no iteration.  The second attempt validates that relative-path
  behaviour against the unique per-branch monitor directory before submission.
- The S4-02 forensic pair has SHA-256 values
  `8b49aff7d5a522f04a952eae640e81fb6d24f7052783496b8b09886c16ecab1c`
  (case) and
  `887c0cff41ddd823b6d6eecdcba3efc78c3bea21de19bdbc59729772be302bd3`
  (data).  Its settings/readback are self-consistent, but the iteration identity
  is not; it is evidence only.
- S4-03 and S4-04 use the exact F11 parent case SHA-256
  `f82125f5d4f17e3c161cfc9f17c2158698eea5132154deef53b16fa6a3b994a5`
  and data SHA-256
  `cb1a2b2b3f6c7bb2d607dd9a8e45c7c161e30a457a5cabe7eb799b1768b78919`.
  The prepared S4-03 case reads back RNG `k-epsilon`; the independently
  prepared S4-04 case reads back standard `k-epsilon`.
- Each branch has a separate journal, transcript, residual file, 30 physical
  report histories, 5,000-iteration paired autosaves and named endpoint.  The
  final cumulative-45,000 autosave is also an endpoint-recovery candidate if a
  post-iteration journal command fails.
- The recovery owner released the writer lock after recording the transport
  failure.  No second Fluent observer was connected and no automatic replay
  occurred.

## Evidence limitations

- Fluent's monitor-stream manager does not expose the residual set to the
  reconnecting client, so cumulative iteration is parsed from the native
  console stream rather than the monitor API.
- Thirty S4-03 physical report histories remain remote and have not yet been
  recovered.  Mass balance, phase routing, liquid inventory and pressure
  stationarity are therefore not adjudicated.
- The S4-02 named endpoint and residual export were never written.  Its
  cumulative-35,000 autosave is only `+29,000`; it is not the common-budget
  endpoint.  The forensic pair cannot repair that scientific identity gap.
- No checkpoint is parent-eligible until paired-file completeness, remote
  checksums, exact case/data readback and final physical-history analysis are
  complete.

## Local evidence

- Original submission/failure packet:
  `PyAnsys/output/03a_stage4/native_queue/20260822T123011Z/`
- Preserved read-only observer evidence:
  `PyAnsys/output/03a_stage4/native_queue/20260822T123011Z/observer-20260823T012500Z-attempt2/`
- Machine-readable reconciliation record:
  `PyAnsys/output/03a_stage4/native_queue/20260822T123011Z/reconciliation-20260823T012500Z.json`
- First bounded recovery attempt and S4-02 forensic save:
  `PyAnsys/output/03a_stage4/native_queue_recovery/20260823T125149Z/`
- Stopped S4-03/S4-04 recovery owner, manifests, failure record, journals and
  local console:
  `PyAnsys/output/03a_stage4/native_queue_recovery/20260823T125548Z/`
- Recovery implementation:
  `PyAnsys/scripts/setup/recover_resume_03a_stage4.py`

Interpretation status: interrupted diagnostic / unresolved.  S4-03 did not
complete the common budget, S4-04 did not run, and no recovery checkpoint is
promoted.

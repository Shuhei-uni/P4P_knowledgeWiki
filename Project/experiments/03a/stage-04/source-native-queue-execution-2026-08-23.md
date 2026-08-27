> **Legacy source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage4-native-queue-execution-2026-08-23.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

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

The current Server 2 tree is the authoritative artifact source for this report:
`C:\Users\syok443\Documents\FluentRuns\03A-stage4`.  It contains the
completed S4-01 native branch, the completed-budget S4-02 native branch, and a
later S4-03 recovery branch that reached its named cumulative-45,000 endpoint.
This section supersedes the earlier 2026-08-23 reconciliation snapshot, which
was written before the later endpoint/checkpoint files were visible in the
remote tree.

The native Stage 4 branches are related to the Stage 3 cases as follows:

- S4-01 continues the F05 parent at cumulative iteration 3,000 for `+30,000`,
  ending at cumulative 33,000.
- S4-02 continues the F06 parent at cumulative iteration 6,000 for `+30,000`,
  reaching cumulative 36,000 in the console.  Its six paired checkpoints stop
  at 35,000 and no named endpoint or native residual export was written.
- S4-03 continues the F11 parent at cumulative iteration 15,000 for `+30,000`
  in the recovery run, ending at cumulative 45,000.
- S4-04 uses the same F11 parent with standard `k-epsilon`, but remains a
  prepared-only branch and was never submitted.

No NaN, infinity, floating-point exception or explicit fatal numerical
divergence is indicated by the recovered execution evidence.  These files are
execution and diagnostic evidence; they do not by themselves establish
physical convergence or parent eligibility.

## Verified execution evidence

| Branch | Verified state | Classification |
|---|---|---|
| S4-01 | Native journal and remote tree show cumulative iteration 33,000 (`+30,000`), six paired checkpoints from 5,000 through 30,000, a named final case/data pair, residual export, transcript, and 30 physical report histories | completed diagnostic / unresolved pending binary checksums, readback and physical-history analysis |
| S4-02 | Native console reached cumulative iteration 36,000 (`+30,000`); six paired checkpoints exist from 10,000 through 35,000. A separate recovery tree contains the ambiguous live-field forensic case/data pair; the native branch has no named endpoint or residual export, but its complete per-iteration residual table is present in the transcript | completed iteration budget / forensic live-field preservation / diagnostic-unresolved; not parent-eligible |
| S4-03 | Recovery branch contains six paired checkpoints from 20,000 through 45,000, a named final case/data pair, residual export, transcript, and 30 physical report histories | completed diagnostic / unresolved pending binary checksums, readback and physical-history analysis |
| S4-04 | Native and recovery prepared cases exist for the standard `k-epsilon` branch; no data, checkpoints, transcript, or report histories exist | prepared independent diagnostic / unresolved; not executed |

The S4-02 transcript residual table runs continuously from cumulative
iteration `6,000` through `36,000`; the Stage 3 F06 parent history supplies
iterations `1–6,000`, with the shared boundary row deduplicated.  At
iteration `36,000`, the residuals are continuity `0.15066`, `x/y/z` momentum
`3.0047e-05`, `2.7322e-05`, and `3.1789e-05`, `k` `1.4070e-03`, epsilon
`0.10394`, and phase-volume-fraction `2.1425e-03`.  There is no separate
native `-residuals.out` export for S4-02, but its full residual history is now
available from the transcript and is included in the cumulative CSV/JSON
package.  The phase-volume-fraction series correctly starts at iteration
3,001 because the F06 carrier parent did not record that equation earlier.

The S4-01 residual export ends at cumulative iteration `33,000` with
continuity `0.155722`, `x/y/z` momentum `2.96232e-05`, `2.90554e-05`, and
`3.20977e-05`, `k` `1.23642e-03`, epsilon `0.133098`, and phase-volume-fraction
residual `2.22671e-03`.  The S4-03 recovery residual export ends at cumulative
iteration `45,000` with continuity `1.37284`, `x/y/z` momentum
`2.92493e-05`, `2.86139e-05`, and `3.16722e-05`, `k` `1.04189e-03`, epsilon
`0.0489749`, and phase-volume-fraction residual `2.19014e-03`.  These values
do not establish convergence.

## Server 2 artifact relocation and analysis package

The source report described a complete relocation map and portable analysis
package on Server 2. Those machine-generated files, native case/data files,
and the remote relocation manifests are intentionally not copied into the
written Project memory. The report-facing PNGs that were present locally are
retained in the [Stage-4 figure folder](figures/03a-stage4/server2/) and
indexed in the [Project Stage-4 figure index](figures/README.md); the
missing package files remain identified by their source report and are not
recreated here.

The portable package contains one CSV per physical report history (30 per
branch), cumulative residual CSVs for all three executed branches, the raw
Stage 4 transcript residual segments, and the source remote path in each JSON
record.  The native H5 case/data files remain on Server 2:
the configured PyFluent endpoint did not expose its file-transfer service, so
they could not be copied into the repository during this read-only inspection.
No case was loaded, no solve was started, and no remote Fluent file was
written during extraction.

The scaled-residual figures and cumulative residual CSVs are assembled from
the complete Stage 3 parent history plus the complete Stage 4 transcript
history.  Their x-axes are anchored at `0`; the first recorded Fluent residual
row is at iteration `1`, so no artificial iteration-0 residual is inserted.

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
- S4-01 has a separate journal, transcript, residual export, 30 physical
  report histories, six 5,000-iteration paired autosaves and a named endpoint.
- S4-02 has a separate journal, transcript, 30 physical report histories and
  six paired autosaves.  It has no native residual export or named endpoint;
  its later forensic case/data pair is retained only as ambiguous live-field
  evidence.
- S4-03's recovery branch has a separate journal, transcript, residual export,
  30 physical report histories, six paired autosaves and a named endpoint at
  cumulative 45,000.  This completed endpoint supersedes the earlier
  42,547-iteration recovery snapshot.
- S4-04 has prepared case files under separate native and recovery roots, but
  no submitted solve artifacts.
- The recovery owner released the writer lock after recording the transport
  failure.  No second Fluent observer was connected and no automatic replay
  occurred.

## Evidence limitations

- Fluent's monitor-stream manager does not expose the residual set to the
  reconnecting client, so cumulative iteration is parsed from the native
  console stream rather than the monitor API.
- The extracted physical histories are now local, but the native H5 case/data
  files remain remote-only pending a usable file-transfer route.
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
- Server 2 extraction implementation:
  `PyAnsys/scripts/report/extract_03a_stage4_server2_evidence.py`
- Offline plotting implementation:
  `PyAnsys/scripts/report/plot_03a_stage4_server2.py`

Interpretation status: completed diagnostic evidence recovered for S4-01 and
S4-03, completed-budget but endpoint-incomplete evidence for S4-02, and
prepared-only evidence for S4-04.  All branches remain unresolved for
scientific parent promotion pending binary checksums, exact readback and
physical-history analysis.  S4-03's recovery checkpoint now reaches the common
`+30,000` budget; S4-04 did not run.

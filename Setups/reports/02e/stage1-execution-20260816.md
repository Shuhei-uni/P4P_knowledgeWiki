# Setup 02e Stage-1 execution record — 2026-08-16

Status: **blocked pending recovery of the existing Student Fluent server**.

This is an intermediate execution record, not a results report. It records the
native-run evidence available before the Student Fluent gRPC endpoint became
unresponsive after a floating-point exception. It does not select an outlet
family, claim convergence, or generate Stage 2. The governing experiment is
[`Setup 02e`](../../active/02e-mixture-y010-brine-outlet-boundary-characterization.md).

## Frozen inputs and build evidence

- Fluent server: `student`, Ansys Fluent 2025 R2.
- Production mesh: `C:\Users\Shuhei Yokkaichi\Documents\CFD\Brine outlet\Full-geomV2-231kcells.msh.h5`.
- Mesh readback: 231,376 cells, one fluid cell zone, with bounds matching the
  Setup 02e contract.
- Initialized parent: `02e-Y010-parent-initialized-20260816T063000Z.cas.h5` and
  matching `.dat.h5` on the Student host.
- Y010 readback: 33,315 selected cells, geometric volume
  `4.829410214052421 m3`, liquid volume `4.790652589965104 m3`, and liquid
  mass `4224.25373425353 kg`.
- The parent contains the native report-definition package: phase-separated
  mass-flow reports for all four boundaries and Y010/Y030 inventory reports.
- All 12 Stage-1 children were independently reloaded from that parent and
  written as paired pre-run case/data artifacts. The build manifest is
  [`02e_stage1_all_build_20260816T064500Z.json`](../../../PyAnsys/output/02e_stage1_all_build_20260816T064500Z.json).

## Native queue evidence

The first queue was written and submitted as a Fluent-native journal:
[`02e_stage1_native_queue_20260816T071500Z.jou`](../../../PyAnsys/output/02e_stage1_native_queue_20260816T071500Z.jou).
Each child was intended to execute one native `/solve/iterate 500`, then write
its own endpoint case/data pair and transcript.

| Case | Native status | Evidence |
|---|---|---|
| `02e-PO-P1` | Endpoint pair written after the native 500-iteration command | Student-host endpoint pair named `...PO-P1...stage1-iter500-20260816T071500Z.cas.h5/.dat.h5` |
| `02e-PO-P2` | **Unusable: floating-point exception at iteration 335** | Student-host transcript `...PO-P2...stage1-iter500-20260816T071500Z.trn`; residuals grew to approximately `4.95e43` continuity, `4.60e38` k, and `2.71e56` epsilon before Fluent reported AMG divergence and floating-point exceptions |
| `02e-PO-P3` | Not reached by the interrupted queue | Paired pre-run artifact remains available |
| `02e-OV-P1..P3` | Not reached | Paired pre-run artifacts remain available |
| `02e-MF-P1..P3` | Not reached | Paired pre-run artifacts remain available |
| `02e-EF-P1..P3` | Not reached | Paired pre-run artifacts remain available |

The read-only monitor observed Fluent `Status.SERVING` and the PO-P2 history
through iteration 335. After the floating-point exception, the endpoint stayed
TCP-reachable but failed the PyFluent/gRPC handoff repeatedly, including
15–20-second read-only connection checks. No restart, overwrite, solver
iteration, initialization, or Stage-2 submission was attempted after that
failure.

## Continuation point

After the existing `student` Fluent service is restarted or otherwise made
responsive, resume with a fresh native queue built from the untouched paired
children in the build manifest. Exclude only `02e-PO-P2` because its native
transcript records the floating-point exception. The continuation must run the
remaining ten pilots, collect the final-100 phase flux means and inventory
histories, and apply the exact adaptive rules in Setup 02e before any Stage-2
case is created.

Until that continuation occurs, the Stage-1 data-quality gate is incomplete and
there is no valid Stage-2 decision manifest.

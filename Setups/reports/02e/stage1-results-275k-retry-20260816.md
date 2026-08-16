# Setup 02e Stage-1 results — 275k-mesh retry — 2026-08-16

Interpretation status: **operational mesh-sensitivity conclusion recorded;
broader scientific interpretation pending user direction**.

This report is the results companion to the
[275k-mesh retry record](mesh-275k-retry-20260816.md). It covers only the four
requested retry points and does not replace the original 231k-mesh Stage-1
report. The user labels `P0-P2` and `0V-P2` were interpreted as `PO-P2` and
`OV-P2`.

## Investigation question and controlled change

The question was whether changing the mesh from the original 231,376-cell
production mesh to `brine-outlet-275kcells.msh.h5` would make selected unstable
Stage-1 pilots usable under the same frozen Setup 02e procedure.

The controlled change was the mesh only. The parent was rebuilt and initialized
on the 275k mesh, then four independent children were created:

| Case | Boundary control |
|---|---|
| `02e-PO-P2` | Pressure outlet, `1,200,000 Pa` |
| `02e-OV-P2` | Outlet-velocity control, `K=10` |
| `02e-MF-P2` | Liquid mass flow, `116.847 kg/s`; vapour `0` |
| `02e-EF-P1` | Pressure jump, `-50,000 Pa` |

Each child was intended to execute exactly one Fluent-native
`/solve/iterate 500` command. No adaptive continuation, solver-setting change,
Stage-2 construction, or Stage-2 submission was included.

## Results and evidence

| Case | Native result | Usable endpoint? | Evidence state |
|---|---|---:|---|
| `PO-P2` | Floating-point exception during the native solve | No | Student-host transcript present; paired endpoint case/data absent |
| `OV-P2` | Floating-point exception during the native solve | No | Student-host transcript present; paired endpoint case/data absent |
| `MF-P2` | Floating-point exception during the native solve | No | Student-host transcript present; paired endpoint case/data absent |
| `EF-P1` | Floating-point exception during the native solve | No | Student-host transcript present; paired endpoint case/data absent |

The first retry, `PO-P2`, remained finite through the observed portion of the
run and reached iteration 347 before Fluent reported the floating-point
exception. This is a trajectory observation, not a convergence result. The
exact terminal details for every case are retained in the Student-host native
transcripts.

Because no case reached its endpoint write, this retry set provides no valid
phase-flux means, inventory histories, final-100 statistics, or converged field
data. Residual traces and reversed-flow/turbulent-viscosity warnings in the
transcripts are diagnostic evidence only.

## What went well

- The 275k mesh was read back successfully at 275,448 cells with one fluid cell
  zone and seven face zones.
- A fresh Y010 parent was built and initialized before the retry children were
  created. The readback recorded 35,193 selected cells, geometric selected
  volume `4.621318904116535 m3`, liquid volume `4.601173779458446 m3`, and
  liquid mass `4057.1770035130744 kg`.
- The live hyphenated boundary names on the new mesh were verified and used in
  the monitor package. This avoided relying on the earlier non-hyphenated
  boundary-name assumption.
- All four children were independently written as paired pre-run case/data
  artifacts from the fresh 275k parent. Their build inventory is preserved in
  [`02e_y010_275k_retry_build_20260816T131500Z.json`](../../../PyAnsys/output/02e_y010_275k_retry_build_20260816T131500Z.json).
- The native queues used one Fluent-native solve command per child. When a
  floating-point exception interrupted a queue, the continuation queue skipped
  only the recorded failed child and did not overwrite or re-run it.
- The endpoint check was conservative: every retry transcript exists, but none
  of the four `.cas.h5/.dat.h5` endpoint pairs was counted as usable.
- The original 231k-mesh report and its evidence were left unchanged. No
  Stage-2 case or Stage-2 decision manifest was created.

## What did not go well

- None of the four requested retry cases completed the native 500-iteration
  command and wrote a paired endpoint.
- `PO-P2`, `OV-P2`, `MF-P2`, and `EF-P1` all terminated with native floating-
  point exceptions. The mesh change therefore did not remove the numerical
  failure mode for this selected retry set.
- The runs continued to show reversed-flow and turbulent-viscosity-limiting
  warnings before the terminal failures. These warnings are consistent with
  unstable or difficult flow behavior, but they do not by themselves identify
  the root cause.
- The first queue launcher encountered Fluent's floating-point-exception
  handoff, so its Python process ended at the native error rather than writing
  a normal completion manifest. The continuation procedure still preserved the
  native transcripts and completed the remaining requested attempts one at a
  time.
- Since no endpoint was written, the mesh comparison cannot assess outlet
  fluxes, inventory conservation, or final-100 iteration behavior. It can only
  compare endpoint usability and observed failure trajectories.

## Mesh-sensitivity assessment

**Evidence-backed operational result:** the 275k mesh did not make any of the
four selected retry points usable under the unchanged frozen setup. It may have
altered the iteration path—for example, `PO-P2` remained finite beyond the
original failure neighborhood—but no successful endpoint was produced.

The appropriate classification for this limited retry is therefore:

- endpoint usability: **negative**;
- evidence of mesh improvement: **inconclusive**;
- convergence or physical-result comparison: **not available**;
- Stage-2 readiness: **not established**.

This report does not recommend accepting or rejecting the mesh for the broader
project. That interpretation requires a decision about whether additional
numerical-stability diagnostics, a different mesh-quality comparison, or a
revised solver procedure is in scope.

## Lineage and preserved artifacts

- Fresh parent snapshot:
  [`02e_y010_275k_parent_20260816T130500Z.json`](../../../PyAnsys/output/02e_y010_275k_parent_20260816T130500Z.json)
- Child-build snapshot:
  [`02e_y010_275k_retry_build_20260816T131500Z.json`](../../../PyAnsys/output/02e_y010_275k_retry_build_20260816T131500Z.json)
- Detailed retry record: [mesh-275k-retry-20260816.md](mesh-275k-retry-20260816.md)
- Native queue journals and Student-host transcripts are listed in the detailed
  retry record. The original 231k-mesh results remain in the existing Setup 02e
  execution record and are not superseded by this report.

# 03A Stage 4 — results

## What ran

The recovered execution evidence distinguishes the native queue from its later recovery branch. It does not infer a successful endpoint from a console iteration count or from a file that lacks the required paired evidence.

| Branch | Actual evidence | Status |
|---|---|---|
| S4-01 | native continuation from F05 reached cumulative iteration `33,000`; paired checkpoints, named endpoint, residual export, transcript, and physical histories exist | completed diagnostic; pending final checksum/readback/history review |
| S4-02 | native console reached cumulative iteration `36,000`; paired checkpoints exist through `35,000`; no named endpoint or native residual export, but the transcript contains the cumulative residual table | completed-budget but endpoint-incomplete; forensic evidence only, not parent-eligible |
| S4-03 | recovery continuation from F11 reached cumulative iteration `45,000`; paired checkpoints, named endpoint, residual export, transcript, and physical histories exist | completed diagnostic; pending final checksum/readback/history review |
| S4-04 | standard-`k-epsilon` case was prepared from the F11 parent; no solve, data, checkpoint, transcript, or report histories | prepared-only; not executed |
| S4-05 / S4-06 | exact F09 40% parent was not proved accessible for this queue | gated; not submitted |

## Evidence / plots / measurements

The [source execution report](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage4-native-queue-execution-2026-08-23.md) records the portable Server-2 evidence package, including residual CSV/JSON histories, 30 physical report histories per executed branch, checkpoint relocation manifests, plots, and the authoritative remote case/data locations. The locally retained report-facing PNGs are indexed in the [Stage-4 figure index](figures/README.md).

The recovered endpoint residuals illustrate why the continuation is still diagnostic:

| Branch | Cumulative iteration | Continuity | `k` | `epsilon` | Volume-fraction residual |
|---|---:|---:|---:|---:|---:|
| S4-01 | `33,000` | `0.155722` | `1.23642e-03` | `0.133098` | `2.22671e-03` |
| S4-02 | `36,000` | `0.15066` | `1.4070e-03` | `0.10394` | `2.1425e-03` |
| S4-03 | `45,000` | `1.37284` | `1.04189e-03` | `0.0489749` | `2.19014e-03` |

These residual snapshots are not enough to establish stationarity. The physical histories must still be evaluated over the prescribed windows for mass imbalance, phase routing, liquid inventory, and brine pressure.

## Numerical state and limitations

- No recovered Stage-4 execution file indicates NaN, infinity, floating-point exception, or explicit fatal numerical divergence. That is an execution fact, not a convergence result.
- S4-02 has a scientific identity gap: its native continuation reached the budget in the console, but its named endpoint and native residual export were not written. The forensic pair cannot repair that gap.
- Native H5 case/data files remain on the authoritative remote host; the portable evidence package is local, while file-transfer limitations prevent treating local extraction as a replacement for exact binary readback.
- No checkpoint is parent-eligible until paired-file completeness, remote checksums, exact case/data readback, and final physical-history analysis are complete.
- S4-04 did not test the turbulence-model hypothesis because it was prepared but never submitted; S4-05/S4-06 did not test the loading-path hypothesis because their exact parent remained gated.

## Observations

- S4-01 and S4-03 show that long continuation evidence can be recovered without a recorded fatal solver signature, but their endpoint residuals and physical histories still require qualification.
- S4-02 demonstrates why iteration count and an ambiguous saved field must not be substituted for a named paired endpoint.
- The executed branches do not yet discriminate “more iteration is enough” from “model form or continuation path is important.”

## Findings / interpretation

Stage 4 remains completed diagnostic evidence, not a qualified baseline. It does not establish physical convergence, mesh independence, plant validation, turbulence-model correctness, or separator performance. The immediate scientific decision is therefore still gated on checksum/readback and physical-history review, with S4-05/S4-06 held until the F09 parent is defensible.

## What this implies for the next review

Review the portable histories against the remote case/data identity, compute the common continuation-window statistics, and decide whether any branch is eligible to become a 03A parent. Keep all branches diagnostic until that review is complete; do not infer a winner from the endpoint residual table.

## Source

[Original Stage-4 execution authority](../../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage4-native-queue-execution-2026-08-23.md)

The linked execution report is the superseding status source for the retained Stage-4 setup plan; its recovered S4-03 `45,000` endpoint supersedes the earlier `42,547` execution snapshot in that setup-plan file.

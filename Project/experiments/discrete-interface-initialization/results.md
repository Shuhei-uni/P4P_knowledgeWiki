# Reconstructed-interface diagnostic — terminal review

## Verified observations

The original open-vent Modified BFW N0 was loaded as a configuration parent; the previous sealed-brine N1 remains preserved. Fluent's native reconstructed region patch produced **3382 fractional cells**, with centroid y=0.066088–0.132382m, at fixed surface y=.10m. All exterior mesh vertices are inside the other patch-box faces. Smoothing stayed off. N0 pressure/geometry arrays matched the binary reference, velocities and native flows were zero, and alpha/pressure plus scientific settings survived save/reopen. Initial mass changed from4096.769804 to4082.887808kg because geometric fill replaced binary centroid fill; no height tuning was used.

The requested500-iteration block stopped at the first iteration at the existing2m/s speed guard. This is one solved iteration, not a completed500-iteration convergence test.

| Quantity | Binary reference N1 | Reconstructed N1 |
| --- | ---: | ---: |
| Maximum speed (m/s) |30.891001|30.929505|
| Liquid inventory change (% own N0) |+0.355991|+0.443079|
| Liquid net inward flow (kg/s) |33.937701|38.758840|
|Largest gross phase/boundary flow (kg/s)|37.2835|41.4675|
|Volume-weighted RMS pressure change (Pa)|237.48|260.429|

All active residuals are available; these first-iteration values do not describe a converged residual window.

| Residual | Binary N1 | Reconstructed N1 |
| --- | ---: | ---: |
|continuity|1|1|
|x-velocity|967.18|967.18|
|y-velocity|2.4583|2.4585|
|z-velocity|0.0010777|0.0010777|
|k|1.0406|0.98385|
|epsilon|95.758|87.297|
|vf-phase-2|0.006974|0.0061796|

The speed maximum remains in the same cell at(0.766235,0.140942,0.408113)m. The reconstructed/reference speed ratio is1.001246, so the predeclared90% suppression criterion fails. Inventory departure also worsened and exceeds the throughout .1% limit. Final100-window conditions are **unavailable**, not measured failures, because only one iteration was solved. Full initial/final fields, native x0/z0 sections, histories, all seven residuals, and the N1 face callback are present. Face/native ledger mismatch is1.11e-16kg/s; phase-sum/native mismatch7.11e-15kg/s. This agreement validates accounting extraction, not mass conservation. Terminal maximum gross phase flow is41.46748kg/s. The stored field comparison was visually checked for axes, normalization, raw points and source identity.

## Interpretation

Geometric fractional filling alone does not suppress the startup motion in this setup. The initial interface representation changed substantially, but the large velocity response and its maximum location persisted. Combined with the preceding brine-sealed test, neither brine forcing nor binary filling is a sufficient single explanation for the failure. This does not prove they have zero influence. The remaining priority is the discrete pressure–gravity/auxiliary field consistency around the interface, including how the pressure gradient and density used by the momentum equation are initialized. More blind iterations of this endpoint are not justified.

## Unresolved assumptions and limits

The native geometric patch is documented and its effects are measured; exact cell clipping has not been independently reconstructed. Equality of cell pressure arrays does not establish face/gradient or density consistency. Analytic hydrostatic pressure and fractional cell density are not guaranteed to be discretely balanced. The open steam pressure boundary, turbulence seeds, mesh/discretization interaction and auxiliary initialization state remain possible contributors. Steady iteration inventory changes are not physical storage rates. No conclusion about physical transient necessity, steady-solution existence, drainage calibration or operating separator performance follows.

## Disposition and evidence

Close this single-contrast diagnostic unqualified. Do not extend the N1 endpoint or select a full-feed run. A useful next investigation is a no-solve audit of the actual pressure gradients/density/body-force fields used by Fluent, followed only by a specifically supported contrast. The present contract selects no further solves.

Evidence: [comparison](../../../PyAnsys/output/discrete-interface-initialization/comparison.json), [figure](../../../PyAnsys/output/discrete-interface-initialization/interface-comparison.png), [live terminal proof](../../../PyAnsys/output/discrete-interface-initialization/terminal-live-proof.json), [exact receipt](../../../PyAnsys/output/discrete-interface-initialization/n500-receipt.json). The job completed deterministic artifact verification; controllers exited, lock is free, Fluent is idleN1 and the final Fluent-local case/data pair is present. No evidence gap in the single-iteration contract; the deliberately unobserved late window remains explicit.

Spend:1 solved iteration, 56.918783 controller-seconds, no solve retries. Unused499-iteration ceiling is not continuation authority. Existing monitor paused after terminal review.

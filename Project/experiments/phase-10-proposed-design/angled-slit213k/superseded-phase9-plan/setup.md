# Angle slit — selected Phase 9 procedure

| Archive status | Value |
| --- | --- |
| Status | Superseded; this queued Phase 9 plan was not executed |
| Authority | Historical 11 October plan only; no active run authority |
| Current case | [Phase 10 angle contract](../CONTEXT.md); completed 50 ms under basic Stage 3 settings |

| Input / gate | Requirement |
| --- | --- |
| Mesh | `Separator-angle-slit-213k.msh.h5`; SHA-256 `9b68ea200ed4e8bf53785834e380b6b26490b36e4d7271b1b375478f7f410df9` |
| Offline cell count | 213,232 |
| Existing angle case/data pair | None found in the checked OneDrive inventories; mesh is available |
| Build basis | Verify the archived early-EWF prepared-A parent used for the vertical slit; native Replace Mesh with verified zone mapping and interpolation; reproduce the vertical slit bulk startup before Phase 9 film preparation |
| Coordinate scale | Offline bounds extend to Y = 6993.9083 input units; prove intended metre scale through native inspection before transfer or solving |
| Topology | Inspect `bottom`, `wall`, the angled slit solid wall, two inlets, outlet and extra boundary; prove the lower collector split and physical mapping rather than copying generated zone names |
| Preservation gate | Preserve vertical final pair and readback before any angle mesh load |

| Stage | Selected procedure |
| --- | --- |
| Build | Native mesh check; inlet, solid-wall, interface and collector mapping; UDF identity; replace mesh; recover injection definitions if needed; preserve interpolated bulk lineage; save/reopen |
| Bulk startup | Reproduce verified vertical slit startup, including scheduled inlet ramp and full-feed hold; record exact film age and native coordinate |
| Phase 9 settings | Approved Mixture/RNG/Coupled bulk contract; full feed 116.92 kg/s liquid and 80.69 kg/s vapor; corresponding walls 0.045 mm / Cs 0.5, physical bottom smooth; film controls as in [vertical setup](../../vertical-slit154k/setup.md) |
| Film preparation | Preserve original film fields and bulk state; allocate mapped lower collector dry; full film forces and particle mechanisms; direct mass and XYZ drain with 1.5 ms capture time and 1% limiter; no flow momentum feedback |
| Drain proof | Matched seeded-film OFF/ON test with frozen bulk; verify native removal and ≤1% matched ledger error; restore production pair and exclude probe time |
| Film development | Active-bulk adjustment, separate bulk freeze, initial0.1 µs startup and qualification, then selected1 µs fixed development with Courant operating ceiling0.8 under the11 October human revision; retain independent inner-stop checks; fixed commands ≥1000 updates except scheduled input changes; native clocks, inner stops, Courant and finite fields required |
| Numerical recovery | Preserve failed attempt; restore last healthy pair; reduce planned step, update cadence/drain span, save/reopen and verify before continuation |
| Final interval | Bulk active from 95 to 100 ms; derive counts from actual accepted film age and selected step |
| Completion | Verify 100 ms clock, final bulk state, paired local artifacts and reopen readback; preserve selected final pair on OneDrive |

| Numerical acceptance revision — human, 11 October 2026 | Selected rule |
| --- | --- |
| Authority | Remove any gates other than Courant; this supersedes earlier numerical qualification gates in this record |
| Sole numerical acceptance gate | Film Courant ≤0.8 |
| Selected step | Fixed 1 µs; apply at the next reconciled native command boundary with save/reopen |
| Inner solver | Keep 100 maximum subiterations and 1e-5 stop. Record pass counts and residuals as diagnostics; no minimum pass fraction or inner-convergence gate |
| Film ledger | Record as a diagnostic; no numerical acceptance gate |
| Evidence and completion | Preserve paired checkpoints and Fluent; verify native iteration/film clock, intended settings, final 95–100 ms bulk-active interval and saved/reopened 100 ms endpoint before the next case |

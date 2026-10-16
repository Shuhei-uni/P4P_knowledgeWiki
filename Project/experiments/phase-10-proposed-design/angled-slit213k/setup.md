# Phase 10 — Angled slit setup

| Current continuation — 13 October 2026 | Selected value |
| --- | --- |
| Authority | Human: angled slit another 100 ms at 10 µs, reaching 150 ms; same settings; preserve 50 ms pair |
| Parent | Hash-verified N33492 / 50.000 ms paired endpoint |
| Target | N43492 / 150.000 ms; 10,000 new fixed 10 µs updates |
| Controlled delta | Restore fixed EWF step from final 5 µs endpoint update to 10 µs; no other physics change |
| Invariants | Original angle model parameters, all boundary conditions and solution methods; bulk remains frozen |
| Preservation | Existing angle 50 ms OneDrive pair kept; loaded vertical 150 ms endpoint saved before replacement |
| Preparation | Load selected angle pair, preserve a separate 50 ms pair, set 10 µs, save/hash/reopen and read back |
| Numerical thresholds | None; diagnostic histories retained |
| Run control | One native 10,000-update command; local autosaves every 1000 updates; final paired reopen and unique OneDrive pair |
| Session | Server 6 only; leave Fluent open; no updates beyond 150 ms or another case |
| Evidence | [Angle 150 ms continuation](../../../../PyAnsys/output/phase10-proposed-design/20261013/angle213k-to150ms/) |

## Earlier preparation and 50 ms run

| Record ownership | Value |
| --- | --- |
| Phase | Phase 10 proposed design; human reassignment, 12 October 2026 |
| Phase navigation | [Both proposed designs](../index.md) |

| Input / setting | Basis |
| --- | --- |
| Mesh | `Separator-angle-slit-213k.msh.h5`; 213,232 cells |
| Mesh SHA-256 | `9b68ea200ed4e8bf53785834e380b6b26490b36e4d7271b1b375478f7f410df9` |
| Parent | Stage 3 basic-EWF prepared-A-N1580; 25% feed; dry film |
| Case SHA-256 | `5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72` |
| Data SHA-256 | `72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af` |
| Controlled change | Supplied angled-slit geometry and discretization |
| Transfer | Native Replace Mesh; retain mapped bulk fields and dry-film clock |
| Scale | Verify native metre extents before scaling; raw file coordinates alone do not establish units |
| Wall mapping | Prove slit and lower-collector roles from geometry and adjacency; record full transferred boundary conditions |
| Basic EWF | Read back inherited Stage 3 film equations, forces, sources, roughness, walls, feedback and DPM |
| Preparation method | Phase 9 hold/ramp procedure; do not substitute later Stage 4 EWF physics |
| Low feed | Liquid 29.23 kg/s; vapor 20.1725 kg/s |
| Full feed | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Hold allowance | 1,000 low-feed updates; 2,000 full-feed updates minimum |
| Ramp | 25% → 100% in 2,000 updates; inlet changes every 10 updates |
| Preparation screen | Two final-1,000 windows: pressure-drop range ≤5% of mean; bulk-mass range ≤10% of mean; outlet-liquid range ≤5% of full liquid inlet |
| Film horizon | 0.050 s total film age; start from the saved23.705ms pair |
| Freeze prerequisite | Prove direct film removal, accepted film-time advancement and preserved bulk fields |
| Film numerics | Human:10 µs for2629updates, then one5 µs endpoint adjustment; total2630updates toN33492/50ms |
| Revised-step evidence | Record numerical diagnostics; no Courant/residual/thickness/ledger/qualification gates. No new matched-time qualification required |
| Fixed solve | At least 1,000 updates between required decisions; short smoke, ramp and numerical contrasts only |
| Checkpoints | Local Fluent disk; paired saves at decision boundaries; final paired reopen |

| Evidence ID | Quantity / artifact | Purpose |
| --- | --- | --- |
| P10-1 | Native mesh check, zone map, mapped fields and paired reopen | Prove the proposed-design child |
| P10-2 | Matplotlib film mass and accretion/removal/storage versus actual film time | Assess development and film accounting |
| P10-3 | Final wall-film thickness with declared scope and scale | Locate retained film at the retained endpoint |
| Supporting | Bulk pressure drop, inventory, signed outlet flux; residuals, accepted steps and Courant | Retain startup and numerical limits |

| Accounting / interpretation | Requirement |
| --- | --- |
| Film ledger | Δfilm mass + integrated removal − integrated input; actual accepted film-time increments |
| Extra terms | Include every active deposition, stripping, separation, evaporation and user source |
| Frozen-bulk limit | Held inventory does not prove bulk stationarity or whole-separator conservation |
| Geometry limit | New geometry is not a pure mesh-resolution contrast |
| Endpoint limit | 50 ms is finite development, not evidence of steady film |


| Current resume | Exact identity / command |
| --- | --- |
| Selected parent | OneDrive Phase10/proposed-design-213k/paused-23p705ms-N30862; nativeN30862 /23.705ms |
| Case SHA-256 | 9e378d5e08bc9724e4b93e8bed06be1f1c60c7ebbae08254dbffa5180d3b605d |
| Data SHA-256 | 3605f9e736c48803f3a9f0141813bc42595ba97e075bf77c03a9ca9fc0d3abb1 |
| Controlled change | Only EWF timestep-max:10 µs; one last5 µs update. Model, boundary and equation controls retained |
| Run | Server6;2629fixedupdates toN33491 /49.995ms; finalscheduledupdate toN33492 /50ms |
| Acceptance thresholds | None; no extra qualification batch |
| Storage | Server-local transcripts and paired autosaves; finalpaired reopen and selectedOneDrivecopy |
| Implementation | [Reviewed runner and prepared controls](../../../../PyAnsys/output/phase10-proposed-design/20261012/angle213k-to50ms/prepared.json) |

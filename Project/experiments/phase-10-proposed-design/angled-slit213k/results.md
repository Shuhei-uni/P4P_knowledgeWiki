# Phase 10 — Angled slit results

| Record ownership | Value |
| --- | --- |
| Phase | Phase 10 proposed design; human reassignment, 12 October 2026 |
| Phase navigation | [Both proposed designs](../index.md) |

| Check | Verified observation | Limit |
| --- | --- | --- |
| Supplied mesh | 213,232 cells; 741,601 file nodes | Fluent reads 715,755 active nodes; file nodes include additional node zones |
| Native mesh | Positive cell volumes; 213,232 cells; physical extents checked in metres | No mesh-convergence claim |
| Lower collector | 1,825 cells; two lower/upper entry interfaces proved from saved topology | Same centroid-selection rule; not a fitted plane |
| Prior session | Paired case/data preserved before replacement | Separate Phase 9 result; not continued |
| Parent | Local dry-film A pair matches recorded case/data hashes | Bulk fields transferred by native interpolation |
| Transfer recovery | Per-zone source repartition crashed; fresh-session native transfer without that repartition succeeded | Across-zone interpolation may occur |
| Bulk liquid inventory | Parent 31.357136 kg; mapped/reopened child 31.963552 kg | Interpolation changed inventory by about 1.93%; not global conservation proof |
| New slit wall | Complete reference non-film rough-wall condition | Film domain remains the traced parent wall scope |
| Basic EWF | Film momentum on; film pressure, surface tension, stripping and edge separation off | Stage 4 enhanced EWF settings not substituted |
| Roughness | Inherited Stage 3 R3: 0.5 mm; coefficient 0.5 | Different from later Phase 9 Stage 4 roughness |
| Child persistence | Paired reopen verified; dry-film clock retained | First reopen refreshed face fluxes; second pair reproduced required readback |
| Smoke | N1580 → N1600; 20 updates; 31 report histories | Counted once |
| Smoke film | 20 µs; peak Courant 8.622832e-6 | Small startup probe only |
| Clock recovery | Data save synchronized host film state with printed native clock | No repeated solve |
| Current run | Complete onServer6: N33492 /50.000ms;2629updates at10 µs plus one5 µs endpoint update; finalpair saved/reopened and OneDrivehashes verified | Finite frozen-bulk basicEWF endpoint; no numericalqualification thresholds applied |
| Paused pair transfer | Both files copied to OneDrive: `P4P-Fluent-Artifacts/Phase10/proposed-design-213k/paused-23p705ms-N30862`; sizes and SHA-256 match local originals | Local OneDrive folder copy verified; cloud sync not independently confirmed |
| History recovery | All 31 native report histories recovered from Fluent-renamed files after reopen; 1 µs block counted once | Controller had stopped on stale file routes; no numerical failure found |
| 1 µs block | Film-ledger error 0.00142%; maximum thickness 0.23944 mm at 18 ms | Faster timestep is human-selected; no matched-time accuracy claim |

| Supporting reference | Transferred evidence | Limit |
| --- | --- | --- |
| Vertical-slit reference | [Separate vertical design results](../vertical-slit154k/results.md) and [phase comparison](../results.md) | Different mesh and EWF controls; export QA limit retained with the vertical record |

| Record | Owner |
| --- | --- |
| [Run manifest](../../../../PyAnsys/output/phase10-proposed-design/20261011/run-manifest.json) | Live execution progress |
| [Prepared reopen](../../../../PyAnsys/output/phase10-proposed-design/20261011/prepared-reopen.json) | Transferred settings, fields and pair |
| [Smoke evidence](../../../../PyAnsys/output/phase10-proposed-design/20261011/startup-smoke-metrics.json) | Exact completed smoke horizon |
| [Setup](setup.md) | Intended run and evidence |


| Current 50 ms continuation | Verified observation / limit |
| --- | --- |
| Parent and controls | Source hashes match; paused pair reopened at23.705ms;10 µs control saved/reopened; existingbulk equations remain frozen |
| Native startup | [Transcript prefix](../../../../PyAnsys/output/phase10-proposed-design/20261012/angle213k-to50ms/native-startup.json):226film rows at10 µs,23.715–25.965ms; prefixCourant0.1931458–0.1987588 |
| Scheduled endpoint | 2629updates at10 µs to49.995ms, one5 µs update to50ms/N33492 |
| Numerical decision | Diagnostics only; no numerical stop thresholds or qualification batch |
| Execution | [Host launch](../../../../PyAnsys/output/phase10-proposed-design/20261012/angle213k-to50ms/host-launch.json); Server6 controller runs independently oflaptop; histories redirected tothe Fluent host |
| Scope | Prefix establishes startup, not the latestlive clock or a completed endpoint.50ms completion nowverified in the completionrecord |


| 50 ms endpoint | Verified result / limit |
| --- | --- |
| Native clock and iteration | N33492;50.000ms after finalpaired reopen |
| Count and step | 2629updates at10 µs, one at5 µs;2630nativefilm rows andupdates fromN30862/23.705ms |
| Paired source and sharing | Finalcase/data saved onServer6, reopened, then copied toOneDrive. MacOneDrivecopies match bothserver SHA-256 hashes |
| Shared folder | Phase10/proposed-design-213k/final-50ms-N33492-1791790200415874900 |
| Diagnostics | PeakCourant0.2196081 on10 µs block,0.1098041 onlast5 µs update; recordedwithout stopthresholds |
| Connection event | Nativehost job completed; laterdesktopconnectiongap reconciled without a solve replay |
| Session | Fluent left open; watcher stopped; no update beyond50ms or newcase |
| Evidence | [Completion and OneDrive hashes](../../../../PyAnsys/output/phase10-proposed-design/20261012/angle213k-to50ms/completion-reconciliation.json) |
| Claim limit | Finite filmdevelopment; no steadyfilm, meshconvergence, timestepaccuracy or physicalvalidation claim |

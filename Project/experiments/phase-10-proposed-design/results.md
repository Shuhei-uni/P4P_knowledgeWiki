# Phase 10 — Proposed design results

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
| Current run | Human paused at the furthest preserved endpoint: 23.705 ms, N30862; case/data reopened and clock verified | Continuation is not authorized; 100 ms not reached |
| Paused pair transfer | Both files copied to OneDrive: `P4P-Fluent-Artifacts/Phase10/proposed-design-213k/paused-23p705ms-N30862`; sizes and SHA-256 match local originals | Local OneDrive folder copy verified; cloud sync not independently confirmed |
| History recovery | All 31 native report histories recovered from Fluent-renamed files after reopen; 1 µs block counted once | Controller had stopped on stale file routes; no numerical failure found |
| 1 µs block | Film-ledger error 0.00142%; maximum thickness 0.23944 mm at 18 ms | Faster timestep is human-selected; no matched-time accuracy claim |

| Record | Owner |
| --- | --- |
| [Run manifest](../../../PyAnsys/output/phase10-proposed-design/20261011/run-manifest.json) | Live execution progress |
| [Prepared reopen](../../../PyAnsys/output/phase10-proposed-design/20261011/prepared-reopen.json) | Transferred settings, fields and pair |
| [Smoke evidence](../../../PyAnsys/output/phase10-proposed-design/20261011/startup-smoke-metrics.json) | Exact completed smoke horizon |
| [Setup](setup.md) | Intended run and evidence |

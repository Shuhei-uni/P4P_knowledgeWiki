# Stage 2 — original 08b mesh transfer

| Item | Verified result |
| --- | --- |
| Status | Original 08b settings on supplied 997,604-cell mesh; paired save/reopen verified; loaded on Server 2 |
| Parent | Exact `08b/TwoPhaseInletV2(Purnanto).cas.h5` and `TwoPhaseInletV2(Purnanto)-25-10000.dat.h5`; local/remote hashes match |
| Target | Same supplied 997k input used in failed Stage 2 trials; no geometry scaling |
| Mesh | 997,604 cells; 4,808,306 faces; one fluid zone and six face zones |
| Zone grouping | Original 08b wall/bottom/inlet/outlet roles retained; no lower absorber partition |
| Settings | Exact match of loaded setup, methods, controls, native interaction and report definitions |
| Numerics | SIMPLE, pseudo time OFF; first-order k; other loaded schemes preserved |
| Carrier feed | Liquid 116.92 kg/s; vapor 80.69 kg/s; source values retained |
| DPM | Six original definitions and full states match; feedback OFF as in original 08b |
| Absorber | None added; original 08b cell-source flags OFF |
| Solve coordinate | Native N10000 retained; zero new carrier iterations |
| Initialization | None; native transfer of archived fields |
| Reopen | Inventory and extrema reproduced within verification tolerance |
| Output paths | Report files and autosaves redirected to local Windows run folder |
| Previous failure | N518 failed pair preserved and hash-verified before replacement |

| Field | Archived 08b | After mesh transfer | Final reopened pair |
| --- | ---: | ---: | ---: |
| Liquid mass, kg | 327.184405932 | 325.830149680 | 325.830149680 |
| Vapor mass, kg | 129.209520447 | 129.999648533 | 129.999648533 |
| Minimum liquid volume fraction | 0.000000 | 0.000000 | 0.000000 |
| Maximum liquid volume fraction | 1.000000 | 0.159342 | 0.159342 |
| Maximum mixture speed, m/s | 94.205956 | 66.441254 | 66.441254 |
| Native iteration | 10000 | 10000 | 10000 |

| Transfer effect / repair | Evidence and limit |
| --- | --- |
| Inventory interpolation | Liquid mass changed -0.4139%; native interpolation does not enforce global conservation |
| Spatial interpolation | Maximum liquid fraction changed 1 to 0.159342; maximum speed changed 94.206 to 66.441 m/s; mapped fields are a starting point, not the original resolved distribution |
| Injection inventory | Settings initially returned no injection objects after replacement; native import refreshed the original six and created six collision copies; only those verified copies were deleted |
| Mesh-check setting | Native check enabled DPM quadrilateral-face centroid tracking; original OFF value restored before final pair |
| Native DPM update | Replace Mesh triggered tracking on the original mesh; no carrier iteration increment; 13,020 tracked, 12,762 incomplete; no DPM separation claim |
| Stability | No solve on the transferred mesh; numerical stability and convergence remain untested |
| Failure causality | Different startup, parent settings and saved fields prevent a single-setting explanation of prior failures |

| Evidence / artifact | Location |
| --- | --- |
| Transfer contract | [Setup](setup.md) |
| Parent readback | [Source state](../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/source-live.json) |
| Full transfer and hashes | [Receipt](../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/transfer-receipt.json) |
| Final readback | [Verification](../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/final-verification.json) |
| Saved mesh topology | [Topology](../../../../../PyAnsys/output/phase8-stage2/20261007/08b-native997k/ready-topology.json) |
| Final case | `C:\Users\syok443\Documents\FluentRuns\Phase8\Stage2\20261007\08b-native997k\08b-on-997604-ready-no-solve.cas.h5` |
| Final data | `C:\Users\syok443\Documents\FluentRuns\Phase8\Stage2\20261007\08b-native997k\08b-on-997604-ready-no-solve.dat.h5` |
| Next action | Leave Server 2 loaded; no further carrier solve selected |

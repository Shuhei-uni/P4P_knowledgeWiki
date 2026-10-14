# R1600 — recovered spiral settings audit

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Recovered parent | Loaded in owned Fluent 2025 R2 session | SSD copy and PC mirror share SHA-256 `b59ffb1a287699e1fd5839294f74258f706d7729e86166e0f17343bf212185e1` |
| Mesh identity | 2,964,593 cells | Matches the historical spiral mesh; M04 remains 946,967 cells |
| Recorded parent injections | All nine match | Historical subset checked; stationary global frame checked in archived RP variables |
| Recorded parent boundaries | Match | Old API names translated explicitly; no value substitutions |
| M04 carrier physics | Match recovered source | Solver, gravity/pressure datum, energy, mixture phases, turbulence and fluid materials |
| M04 numerics | Match recovered source | Methods, controls and residual equation settings |
| M04 carrier boundaries | Match by geometric role | `inlet` → `inlet`; `outlet` → `steamoutlet`; `bottom` → `bottom`; `wall-fluid` → vessel wall patches |
| Carrier endpoint | N1500 restored and verified after source audit | Zero initialization, carrier updates or DPM updates during audit |
| Manual baseline on entry | Preserved before replacement | Loaded case had 5,578,299 cells and no valid data; native case-only preservation and hash recorded |
| Particle material | `liquid-water`, 881.2109 kg/m³ | Recovered source readback; no baseline-family density substitution |
| Global tracking | Maximum 10000 steps; step-length factor 5 | Full recovered controls preserved in machine comparison |
| Particle forces | Pressure force and virtual mass on; virtual-mass factor 0.5 | Saffman lift off; one-way interaction |
| Particle boundaries | Inlet/top escape; bottom trap; vessel reflect | Normal/tangential restitution 0.3 / 0.8 |
| Exact Case 4 delta | 24 numeric fields differ from rounded parent | Nine diameters, nine positive face-normal speeds of 26.865069 m/s, six mass flows; apply direct Case 4 objects |
| Version limit | Historical 2024 R2; current 2025 R2 | Matching settings do not remove solver-version effects |
| Source limit | Exact July binary and full July settings export remain unlocated | Matching recovered h1600 parent plus direct Case 4 overrides supports a documented reconstruction, not byte-identical historical provenance |
| Scientific limit | Carrier remains numerically unqualified | Settings parity does not establish convergence, mesh independence or improved accuracy |

| Machine evidence | Purpose |
| --- | --- |
| [Live audit receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-recovered-parent/live-audit-receipt.json) | Source load, preserved manual baseline and restored M04 |
| [Live source settings](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-recovered-parent/live-source-settings.json) | Full current-version readback of recovered source |
| [Settings comparison](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-recovered-parent/settings-comparison.json) | Explicit API translations, exact matches and Case 4 overrides |
| [Exact Case 4 injections](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-reference/exact-injection-readbacks.json) | Full-precision historical injection authority |
| [Carrier result](replication1600-carrier-results.md) | N1500 paired fields, histories, budget and numerical limits |

| M04 DPM preparation | Verified result |
| --- | --- |
| Current loaded state | Post-tracking M04 N1500 pair with nine exact Case 4 injections; [DPM result](replication1600-dpm-results.md) |
| Verification | Complete particle/global/boundary readback; unchanged carrier settings; saved/reopened case and data; paired SHA-256; serialized global frame for all nine |
| Tracking status | One fresh DPM update complete and mass-audited; zero new carrier updates |
| [Preparation receipt](../../../PyAnsys/output/phase10-single-inlet-mesh-convergence/replication1600-M04/spiral-recovered-parent/DPM-preparation-receipt.json) | Native pair paths, hashes, settings and repair evidence |
| Native manifest | `C:/Users/qtra338/Documents/FluentRuns/Phase10/20261009/replication1600-M04-9717fb9b/DPM-ready-5a9cc9bc/manifest.json`; saved and read back |
| Next selected operation | Tracking complete; review Case 4 results before conditional enthalpies |

# Phase 9 — Full-load mesh startup

| Setting / invariant | Selected preparation basis |
| --- | --- |
| Parent | Prepared Stage 3 A, N1580, 25% feed; native paired parent hashes in source receipt |
| Stage 4 provisional physics | Selected pressure/spreading/surface-tension, feedback, DPM collection/splash, stripping and edge separation settings |
| Stage 4 source | recovery1-prepared.json; common configuration, not a final EWF selection |
| Roughness | 0.045 mm; Cs 0.5; bottom smooth; original physical wall scope |
| Film domain | Same original physical wall scope across meshes; merge newly named component walls before transfer |
| Bulk model | Retain verified steady Coupled Mixture/RNG model, materials, contact collector and diagnostic DPM |
| 08b corrections | Bulk surface tension enabled at 0.04041000083088875 N/m; restore turbulence compressibility and drag-modification flags; human approved stored `none` interaction as an inactive Mixture legacy exception |
| Human-retained controls | Two tension smoothing passes, current reporting reference values and current DPM tracking controls; no separate tracking pass |
| Audit record | [Native 08b comparison and traced exceptions](settings-audit-08b.md); corrected paired readback required before solve |
| Bulk equations | drift, flow, ke, mp active throughout |
| Low feed | Liquid 29.23 kg/s; vapor 20.1725 kg/s |
| Full feed | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Ramp | 25% to 100% over 2000 updates; reference 10-update command spacing |
| Film numerics | Stage 4 recovery: fixed 0.1 microsecond, original implicit solver, 100 allowed subiterations |
| Bulk numerical start | Stage 4 recovery pseudo scale 0.01 and recorded relaxation settings |
| Mesh transfer | Original verified E2.7 A for native Replace Mesh; apply Stage 4 settings after interpolation |
| Collector selection | Same physical cell-centroid region at y <= 0.10 m on each mesh |
| Transfer recovery | Stage 4-active replacement crashed at 342k; revised ordering passed replacement after restart; child paired verification is required before solve |
| Scaling | Confirm native metre extents; file coordinate scale alone does not authorize another scaling operation |
| Boundary proof | Name, type, physical bounds and cell-zone adjacency; preserve film/non-film and collector roles |
| 60k reuse proof | Same physical boundary face counts, scaled areas, enclosed volume and 60,964 cells; [native input comparison](../../../PyAnsys/output/phase9-mesh-convergence/20261007/60k-physical-reuse-proof.json) |
| Initialization | No bulk reinitialization; no film reset after startup begins |
| Checkpoints | Server-local FluentRuns/Phase9 disk; source, prepared children, hold/ramp checkpoints, full-feed endpoints |

| Solve stage | Native command size | Reason for this boundary |
| --- | --- | --- |
| Initial instrumentation smoke | 20 updates once per mesh | Prove report coverage and accepted film time before the longer holds |
| Fixed low-feed hold | Entire remaining low-feed allowance in one command | No inlet change or intermediate decision is required |
| Feed ramp | 10 updates between inlet changes | Preserve the traced 2000-update ramp and its feed schedule; paired checkpoints every 500 updates |
| Fixed full-feed hold | `/solve/iterate 1000` per block | One uninterrupted solve between the 1000-update stability decisions and paired checkpoints |
| Observation | Separate watcher reads the live transcript every 30 s | Observation does not split the solve into short commands |
| Storage | Native autosaves every 500 updates; paired verification at scheduled boundaries | All native checkpoints and transcripts stay on the Fluent machine; OneDrive is reserved for shared start/final pairs |
| OneDrive | Immutable supplied inputs; selected final pairs only |

| Mesh label | Actual fluid cells | File nodes | Low-feed hold updates | Ramp updates | Minimum full-feed hold updates |
| --- | ---: | ---: | ---: | ---: | ---: |
| 60k | 60,964 | 233,698 | 500 | 2000 | 1000 |
| 342k | 342,609 | 1,077,053 | 1000 | 2000 | 2000 |
| 680k | 679,970 | 1,764,797 | 1500 | 2000 | 3000 |
| 997k | 997,604 | 3,177,646 | 1500 | 2000 | 3000 |
| 2_6M | 2,596,657 | 6,195,886 | 2000 | 2000 | 4000 |

| Iteration policy | Rule |
| --- | --- |
| Minimum hold scaling | Base hold multiplied by cube root of cell-count ratio; round upward to 500/1000 updates |
| Purpose | Initial scheduling allowance; not a mathematical convergence law |
| Full-feed extension | Additional 1000-update batches if bulk monitors still drift |
| Stability screen | Human revised limits, 7 October 2026: two consecutive final-1000 windows with pressure-drop range <= 5% of mean; bulk inventory range <= 10% of mean; outlet-liquid range <= 5% of full liquid inlet flow |
| Earliest stability acceptance | 2000 full-feed updates; larger mesh minima still apply |
| Interpretation | Preparation maturity screen; does not establish full conservation or film stationarity |
| Bounded preparation budget | At most 20,000 full-feed updates per mesh; preserve a nonstationary endpoint if the budget is exhausted |
| Film-time comparison | Record actual clock; mesh-dependent holds give different film ages; do not infer final EWF convergence from those endpoints |
| Recovery | Preserve solved children; adjust numerical controls only with recorded reason and readback; keep physical settings consistent |

| Evidence ID | Quantity and source | Decision use |
| --- | --- | --- |
| P9-1 | Exact cells, physical bounds, boundary areas, volume and native mesh quality | Prove comparable geometry and meshing scope |
| P9-2 | Pressure drop, bulk liquid inventory and signed steamoutlet liquid flux versus native iteration | Decide full-feed extensions; separate iteration drift from mesh differences |
| P9-3 | Film mass, accretion, drainage, thickness, Courant and native time | Record provisional film development and unequal film age |
| P9-4 | Source hooks, active bulk equations, complete histories and paired reopen | Prove usable full-feed endpoints |
| Supporting | Residuals, vapor routing, source-inclusive balance and collector tracking | Retain numerical/accounting claim limits |

# Stage 3 early EWF startup — vertical-slit 154k mesh

| Question / authority | Contract |
| --- | --- |
| Human instruction | Repeat the completed early-EWF startup on the supplied vertical-slit mesh |
| Session authority | Full ownership of Server 3; replacement explicitly authorized on 5 October 2026 |
| Reference | [Completed 60k startup](../setup.md), N1580–N5080 |
| Source of exact settings | Hash-verified prepared A case/data; [reference runner](../../../../../../PyAnsys/scripts/setup/run_phase72a_stage3_early_ewf.py) |
| Chat access | Linked chat tool unavailable; human supplied its final answer and local record links; reference recovered from repository evidence |
| Previous Server 3 work | Preserved N46806 pair before replacement; no further continuation of that lane selected here |
| Requested physical change | Supplied vertical-slit geometry and mesh; 154,063 cells |
| Comparison limit | Geometry and mesh change together; this is not a mesh-convergence study |

| Parent / invariant | Required value / treatment |
| --- | --- |
| Prepared A case SHA-256 | `5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72` |
| Prepared A data SHA-256 | `72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af` |
| Target source | Server 3 OneDrive: `2026 Sem 1/700/P4PCFD/CAD PurnantoV2/Design improvement/Separator-vertical-slit-154k.msh.h5` |
| Target source SHA-256 | `42f548aaabafc79e7af26829ac1d2613372e07ad4004fffbfd49ee9a15b8964d` |
| Native transfer | Fluent 2025 R2 Replace Mesh; retain source settings and map saved A bulk data |
| Legacy conversion | Local mesh-bearing `.cas` copy; required by native replacement; supplied `.msh.h5` unchanged |
| Scaling | Native target mesh check: height 6.991387 m; Fluent reads stored mm metadata correctly |
| Collector | Same reference centroid selection box: x −2.067034…1.066950 m, y 0…0.10 m, z −1.469893…1.066889 m |
| Collector extent limit | Cell-centroid selection; boundary is not an exact fitted y=0.10 m plane |
| Collector topology | 837 lower cells; 153,226 upper cells; same two transparent entry face groups and DPM escape treatment |
| Boundary correspondence | Native matching names; mapping receipt retains the supplied physical names |
| Added slit solid | Complete reference non-film rough-wall BC copied onto the additional slit wall |
| R3 roughness | 0.5 mm height; Cs 0.5; all corresponding non-bottom solid walls |
| Bulk absorber | Exact `libcontactv2` hooks; 10 µs liquid depletion; phase-velocity momentum removal; inherited turbulence sources |
| Carrier | Exact reference steady Mixture/RNG, Coupled, Global Time Step and numerical controls |
| Film | Exact reference E2.7 phase accretion; coupled film solve; Flow Momentum Coupling off; upper vessel `wall` only |
| Film startup | Dry mapped A film; 1 µs fixed step; 10 subiterations; 1 m diagnostic thickness cap |
| Bulk startup | Native interpolated historical A; no bulk reinitialization; report mapped inventory change explicitly |
| DPM | Exact inherited one-way diagnostics; collector escape boundaries; no new injection loading |
| Native coordinate | Record actual mapped starting coordinate; solve exactly 3,500 additional updates |

| Step | Updates | Feed / action |
| --- | ---: | --- |
| Low-feed hold | 500 | Liquid 29.23 kg/s; vapor 20.1725 kg/s |
| Loading ramp | 2,000 | Both inlet commands updated every 10 updates, matching the reference schedule |
| Ramp formula | r=0,10,…,1990 | f=0.25+0.75r/2000; liquid=116.92f; vapor=80.69f |
| Target hold | 1,000 | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Smoke evidence | First 20 hold updates | Included in the 500-update low-feed hold; no extra updates |
| Checkpoints | Stage boundaries / every 500 ramp updates | Paired local Fluent disk saves; reopen verified |
| Shared outputs | Prepared/final inputs and endpoints | OneDrive copies hash-verified; ordinary checkpoints remain local |

| Evidence / acceptance | Requirement |
| --- | --- |
| Transfer proof | Source/target settings readback; new-wall mapping; saved/reopened prepared pair |
| Reports | All reference native reports at frequency 1; server-local absolute destinations |
| Residuals | All seven carrier residuals; every printed film inner iteration and accepted film clock |
| Schedule | Persist each boundary write/readback; compare 200 ramp blocks with reference |
| Completion | Exact horizon; paired final endpoint; final reopen; complete report coverage |
| Recovery limits | Reference nonfinite-field, thickness >3 mm, Courant >1 and film-ledger error >1% conditions |
| Interpretation | Startup response, bulk+film storage, carryover, source tracking and film numerical adequacy |
| Claim limit | No steady-film, physical-validation, developed-film or mesh-convergence claim |

| Owner | Evidence |
| --- | --- |
| Native implementation | [Runner](../../../../../../PyAnsys/scripts/setup/run_phase72a_stage3_slit154k.py) |
| Machine state / exact paths | [Run manifest](../../../../../../PyAnsys/output/phase72a-stage3-slit154k-server3/20261005/run-manifest.json) |
| Results | [Current status](results.md) |
| Native transfer mechanics | [Fluent 2025 R2 manual, section 7.12.12](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_GridModify.html) |

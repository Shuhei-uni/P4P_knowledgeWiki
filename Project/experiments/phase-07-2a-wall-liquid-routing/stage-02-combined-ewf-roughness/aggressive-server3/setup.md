# Stage 2 — aggressive adaptive continuation on Server 3

| Item | Selected contract |
| --- | --- |
| Human direction | Continue N45606 on Server 3; use more aggressive EWF stepping to seek a steady film |
| Human target confirmed | Steady film; nonzero film mass is allowed, inventory growth should approach zero |
| Authority | Full ownership of Server 3; 5 October 2026 |
| Owning workflow | `phase-loop` |
| Parent | [Verified N45606 history](../case-history-N45606.md) |
| Field lineage | Corrected original-E2.7 restart → independent local four-rank N33586 → Server 1 adaptive N45606 |
| Separate branch | Server 1 N23586 fields are not a parent |
| Preservation | Save and reopen Server 3 Stage 3 N8000 before replacement |
| Initialization | None; retain developed carrier and film fields |
| Film clock at parent | 0.1207690160000985 s |
| Time added since corrected restart | 0.0407690160000985 s; restart clock 0.08 s |
| Parent film inventory | 6.360049592 kg |
| Parent maximum thickness | 0.307209964 mm |

| Numerical setting | Parent | First aggressive test |
| --- | ---: | ---: |
| Adaptive stepping | On | On |
| Courant target | 0.05 | 0.15 |
| Increase factor | 1.2 | 1.3 |
| Decrease factor | 2.0 | 2.0 |
| Initial-step setting | 1 µs | 2 µs |
| Inherited accepted step | 1.728 µs | Retain; verify subsequent adaptation |
| `timestep-max` | 1 µs | Unchanged; not a verified adaptive ceiling |
| Film subiterations | 10 | 10 for the controlled test |

| Fixed scientific setting | Requirement |
| --- | --- |
| Mesh, materials and feeds | Exact N45606 model |
| Roughness | R3 |
| Absorber | Corrected contact absorber; verify UDF library hash and applied source |
| Film walls and coupling | Exact parent scope; momentum feedback remains off |
| DPM and bulk controls | Exact parent settings |
| Diagnostic thickness cap | Retain 1 m; never use cap clipping as convergence evidence |
| R5 | Cancelled |

| Run plan / evidence | Requirement |
| --- | --- |
| Preparation | Verify transferred case/data hashes, settings, inventory, boundary fluxes and film clock; save/reopen prepared child |
| First probe | 100 updates; includes native film subiteration residuals |
| Continuation | 1,000-update native TUI batches |
| Bounded horizon | Up to 0.2 s total film time added since corrected restart; maximum 80,000 updates for the moderate restart |
| Review points | Batch endpoints; inspect passage through 0.05 and 0.1 s before 0.2 s |
| Checkpoints | Local FluentRuns disk; retain paired native autosaves and explicit batch endpoints |
| Transcript | Native server transcript plus client transcript for every batch |
| Histories | All inherited reports each update; carrier residuals and all EWF subiterations |
| Film ledger | Δfilm inventory + Δcumulative drain − Σ(accretion × actual film-time increment) |
| Numerical recovery bounds | CFL > 1; thickness > 3 mm; film inventory > 12.3 kg; film ledger error > 1% |
| Inner-film recovery condition | More than 20% of a 1,000-update batch has final h/u/v residual above 1; preserve endpoint and repair before a longer continuation |
| Stationarity screen | Three consecutive 1,000-update windows: absolute drainage deficit < 1%, film ledger error < 0.1%, no final EWF residual above 1, at least 99% of updates meet the 1e-5 film stop value |
| Stronger qualification | Check raw inventory slopes, accretion/drainage trends and inner-solve tolerance; screen alone is insufficient |
| Core figure | Film inventory; accretion/drainage/storage; accepted timestep and CFL; final inner-film residuals |
| Claim limits | Film-side accounting only; no whole-separator closure, timestep independence or physical validation |
| Exact implementation | [Continuation runner](../../../../../PyAnsys/scripts/setup/continue_phase72a_stage2_server3.py) |
| Machine evidence | [Run manifest](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/run-manifest.json) |

| Assessed numerical test | Observation / selected repair |
| --- | --- |
| Target 0.15, 10 subiterations; N45606–N45706 | Accepted 6.415943 µs; 30/100 final film residuals above 1; no update met the 1e-5 stop value |
| First repair at N45706 | Increase allowed film subiterations to 30; preserve fields and timestep controls |
| Target 0.15, 30 subiterations; N45706–N45806 | No final residual above 1, but no update met the 1e-5 stop value; maximum final h residual 0.545342 |
| Target 0.08, 30 subiterations; N45806–N45906 | Accepted 3.207972 µs; 69/100 updates met the stop value; 29/100 had a final residual above 1 |
| Excluded branch | Preserve N45906; not selected for long compute or as a field parent |
| Selected moderate restart | Return directly to verified original N45606; target 0.06, growth 1.3, reduction 2, initial setting 2 µs, 30 allowed subiterations |
| Moderate 100-update probe | Accepted 2.2464 µs; all 100 film solves met 1e-5; endpoint reopened exactly |
| First 1,000-update batch | Running N45706–N46706; later inner-film bursts observed; sustained qualification pending |
| Moderate restart evidence | [Separate manifest](../../../../../PyAnsys/output/phase72a-stage2-server3/20261005/moderate-restart/run-manifest.json) |
| Control meaning | [Fluent 2025 R2 §30.4](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_eqns.html) documents implicit-film subiterations and stop value |
| Interpretation | Faster accepted steps require an inner-solve check; smooth inventory alone does not qualify the aggressive route |

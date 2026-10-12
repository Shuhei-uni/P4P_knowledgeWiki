# Vertical slit / N5080 — Phase 9 continuation

| Parent | Selected identity |
| --- | --- |
| Case | `final-N5080.cas.h5` |
| Case SHA-256 | `9cde787ac71219f1d54dde53c1b57d41afacb75595b085b7b29e2630c980cb60` |
| Data | `final-N5080.dat.h5` |
| Data SHA-256 | `22535f056edba6ea75a96b63db0b1bb7c665fc8516647372571dbc42d595ffab` |
| Recorded directory | OneDrive: `P4P-Fluent-Artifacts/Phase72A/Stage3/slit154k-20261005/final-N5080` |
| Native iteration / film age | N5080 / 3.5 ms |
| Preservation | No bulk reinitialization; preserve original upper film facets and clock |
| Execution server | Server 6 only; preserve loaded N45606 before replacement |
| Prerequisite | Both files accessible and hash verified; verified; child reopened and functional drain proof passed |

| Setting group | Selected target |
| --- | --- |
| Common settings owner | [EWF Plan v1](../ewf-plan-v1.md) |
| Bulk physics | Mixture / RNG / Coupled; audit nested interaction settings against the Phase 9 approved contract |
| Feed | Liquid 116.92 kg/s; vapor 80.69 kg/s |
| Bulk collector | Retain verified contact-absorber mass, momentum and turbulence hooks |
| Roughness | 0.045 mm; Cs 0.5 on corresponding non-bottom solid walls; bottom smooth |
| Film physics | Full film momentum, gravity, gas shear, wall viscosity, momentum advection, pressure and spreading; phase accretion ON |
| Surface tension | Bulk and film 0.04041 N/m |
| Film solution | Sequential; first-order implicit; new implicit scheme OFF; first-order mass and momentum |
| Inner solver | 100 maximum subiterations; stop value 1e-5 |
| Smoothing | ON; level 2; factor 0.5 |
| Momentum feedback | Flow Momentum Coupling OFF |
| Particle options | DPM collection, splash, stripping and edge separation ON |
| Film walls | Preserve original upper wall; map and allocate lower collector with zero initial height, then restore saved parent data and verify original fields |
| Direct film drain | Lower wall mass and XYZ momentum removal; 1.5 ms capture time; 1% depletion limiter |
| Cadence | One film update per iteration; profile interval 1; particle update span 20 µs |
| Selected film step | Human revision: fixed 2.5 µs from N80580 / 42.35 ms; adaptive OFF; drain refresh span 2.5 µs; DPM every 8 iterations retains 20 µs physical interval |
| Recovery ladder | Lane adds selected1 µs level to0.1/2.5/5 µs; technical recovery retains recorded model settings, preserves failed endpoint and save/reopen controls |
| Film Courant diagnostic reference | 0.8; recorded excursions do not stop or roll back the run under the 12 October human revision |
| Pre-run proof | Save/reopen child; verify parent clock, bulk fields and original film facets; prove direct drainage with frozen bulk |
| Evidence | Native transcripts; per-iteration bulk/film reports; server-local paired checkpoints; selected final pair on OneDrive |

| Selected stage | Bulk | Step | Updates | Expected film age / native iteration |
| --- | --- | ---: | ---: | --- |
| Human-selected saved parent | Frozen | Inherited 2.5 µs | — | 42.350 ms / N80580 |
| Growth 1 | Frozen | 2.5 µs | 10000 | 67.350 ms / N90580 |
| Growth 2 | Frozen | 2.5 µs | 10000 | 92.350 ms / N100580 |
| Reach final bulk stage | Frozen | 2.5 µs | 1060 | 95.000 ms / N101640 |
| Final bulk adjustment | Active | 2.5 µs | 2000 | 100.000 ms / N103640 |
| Total new continuation | — | 2.5 µs | 23060 | Numerical diagnostics only; no automatic rollback |

| Parent acceptance scope | Limit |
| --- | --- |
| Explicitly adopted N80580 pair | Historical peak Courant 4.292395 retained in evidence; human selection authorizes loading this endpoint without claiming its earlier block passed |
| Continuation accounting | New run accounting starts at N80580 / 42.35 ms; earlier branch manifests and N5080 OneDrive provenance remain preserved separately |

| Decision / limit | Requirement |
| --- | --- |
| Step increase | Verified healthy checkpoint; complete clocks and finite fields; film Courant and inner-solver evidence reviewed |
| Step recovery | Follow Plan v1; preserve failed evidence, reload last healthy pair, lower the step and recalculate remaining counts from accepted film age |
| Fixed-input commands | At least 1000 updates; the 1060-update block ends at the required 95 ms equation switch |
| Probe accounting | Restore prepared production pair after a drain probe; exclude probe updates from production film age |
| Claim limit | Changed geometry and mesh; run does not establish mesh independence, steady film or physical validation |
| Current execution | Cancel the superseded owned waiter, interrupt the native 1 µs solve once, preserve and reopen its stable partial pair, then reopen N80580 / 42.35 ms and save/reopen fixed 2.5 µs controls before continuation. No stop or rollback due to Courant/inner/ledger values |

| Recovery decision | Gate |
| --- | --- |
| Courant acceptance | No numerical gate; record peak and excursions diagnostically |
| Inner and ledger diagnostics | Record residuals, pass counts and mass ledgers without blocking continuation on their thresholds |
| Courant exceedance | Record and continue to100 ms; no automatic numerical rollback |

| Numerical acceptance revision — human, 11 October 2026 | Selected rule |
| --- | --- |
| Authority | Remove any gates other than Courant; this supersedes earlier numerical qualification gates in this record |
| Sole numerical acceptance gate | None; Courant, residuals and ledger values are diagnostics under the 12 October revision |
| Selected step | Fixed 2.5 µs from N80580 / 42.35 ms; save/reopen controls before solve |
| Inner solver | Keep 100 maximum subiterations and 1e-5 stop. Record pass counts and residuals as diagnostics; no minimum pass fraction or inner-convergence gate |
| Film ledger | Record as a diagnostic; no numerical acceptance gate |
| Evidence and completion | Preserve paired checkpoints and Fluent; verify native iteration/film clock, intended settings, final 95–100 ms bulk-active interval and saved/reopened 100 ms endpoint before the next case |

| Technical recovery implementation | Evidence / limit |
| --- | --- |
| Hash output | Lane-only PowerShell Get-FileHash with durable ASCII output and finite polling; known case and data hashes match the independent host Python SHA-256 calculation |
| Host evidence reads | Controller reads native transcript and histories from local files inside Server 6 WORK; desktop reads retain the Fluent transport route. No replay for file or RPC failures |
| Selected vs recovery step | Human selected 2.5 µs from 42.35 ms; numerical exceedances are diagnostics and do not authorize automatic rollback. Physics and 100 max / 1e-5 remain fixed |

| Continue-to-100 ms policy | Requirement / limit |
| --- | --- |
| Human authority | No, keep running to100ms — 12 October2026; supersedes earlier numerical acceptance gates |
| Active control | Use 2.5 µs / DPM8 / drain refresh2.5 µs; physics and inner100max/1e-5 fixed |
| Numerical decision | Record Courant and inner/ledger diagnostics without stop or rollback; no new qualification block |
| Boundary handoff | Superseded by explicit 42.35 ms selection: preserve interrupted partial, then reopen the saved N80580 pair and run 23060 updates to100ms |
| Final stage | Bulk active95–100ms, verified saved/reopened100ms endpoint. Completion and artifact checks remain |

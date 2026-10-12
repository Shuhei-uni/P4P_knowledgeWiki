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

| Current retained-case procedure | Requirement |
| --- | --- |
| Human revision | Pause this case; keep the saved 50.9 ms pair; supersedes 100 ms continuation and angle transition |
| Selected saved pair | N84000 / 50.9 ms; fixed 2.5 µs film step, frozen bulk |
| Preserve before load | Archive interrupted later N90695 / 67.6375 ms pair with both SHA-256 hashes |
| Reopen | Hash selected case/data, load pair, verify N84000 / 50.9 ms / 2.5 µs and idle state |
| Shared artifact | Copy selected pair to unique Server 6 OneDrive folder; verify source/copy hashes; cloud upload remains a separate claim |
| Further updates | None; no final bulk-active stage and no angle launch |
| Session | Leave Fluent open; watcher stopped |
| Evidence | [Retained pair receipt](../../../../PyAnsys/output/phase9-server6-slit154k/20261010/retained-50p9ms.json) |
| Claim limit | Retained checkpoint does not establish mesh independence, steady film or physical validation |

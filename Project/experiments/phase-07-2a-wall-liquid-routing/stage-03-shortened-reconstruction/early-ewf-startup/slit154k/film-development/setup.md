# Vertical-slit wall-film development — Server 3

| Contract | Selected work |
| --- | --- |
| Human goal | Develop the wall film as far as numerical evidence supports; supervise the continuation continuously |
| Authority | Overwrite and operate Server 3, confirmed 6 October 2026 |
| Mesh | `Separator-vertical-slit-154k.msh.h5`; 154,063 cells |
| Exact parent | [Completed vertical-slit startup](../results.md), N5080; native film time 3.5 ms |
| Parent case SHA256 | `9cde787ac71219f1d54dde53c1b57d41afacb75595b085b7b29e2630c980cb60` |
| Parent data SHA256 | `22535f056edba6ea75a96b63db0b1bb7c665fc8516647372571dbc42d595ffab` |
| Reference method | [Original film-development setup](../../film-development/setup.md) and [results](../../film-development/results.md); numerical settings require qualification on this mesh |
| Fixed physical model | Parent R3 roughness, contact absorber, phase accretion, wall scope, DPM, full inlet loading and bulk methods |
| Initial controlled delta | Increase allowed film subiterations from 10 to 30; retain 1 µs step and all bulk equations |
| First numerical probe | 100 native updates; save/reopen, complete native clocks and inner residuals, mass ledger, facet fields |
| Continuation | Prefer 1,000-update native TUI batches; shorter batches for numerical contrasts and recovery |
| Acceleration | Test equal film-time contrasts before accepting larger steps; recheck as film develops |
| Bulk freeze | May be used for a matched forcing comparison and provisional film development; restore original bulk equations before any steady-film claim |
| Checkpoints | Paired case/data on Server 3 local `Documents/FluentRuns/Phase72A/Stage3/slit154k-film-development-20261006`; unique files, hashes and reopen |
| Native evidence | Server-local transcript for each batch; all report histories, accepted film steps and native film clock |
| Film solver screen | Recorded h/u/v terminal residuals ≤1e-5 in ≥99% of updates; zero terminal residuals >1; unavailable residuals are not passes |
| Field and accounting screen | Finite, nonnegative film fields; peak film CFL ≤1; thickness ≤3 mm; film ledger error ≤0.1% for qualification |
| Recovery | Preserve failed endpoints; restore a passing pair and reduce the step or change solver numerics within this model |
| Review horizons | 10, 50, 100, 200 and 500 ms of actual film time; these are evidence reviews, not proof of stationarity |
| Steady-film criterion | Three consecutive 1,000-update full-bulk windows: drainage deficit and storage/accretion ≤1%, film ledger ≤0.1%, persistent facet mass and velocity |
| Claim limits | Film development alone does not establish whole-separator conservation, mesh convergence, or improved separation |
| Machine owner | [Continuation runner](../../../../../../../PyAnsys/scripts/setup/continue_phase72a_slit154k_film.py) |

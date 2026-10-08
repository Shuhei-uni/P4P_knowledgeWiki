# Stage 4 — DPM cadence and film accounting

| Contract | Selected diagnostic |
| --- | --- |
| Authority / scope | Human: keep running; owned Server 1; film-method accuracy and development cost |
| Question | Does the reported-rate balance discrepancy follow the number of film updates between particle tracking events? |
| Classification | NEW numerical-cadence contrast; hypothesis test, not a proposed ledger correction |
| Baseline | [Core17 report-cost arm](../report-cost/results.md): N41503 → N42503; 10 ms; 50 tracking events; 1.6721% reported-rate discrepancy |
| Exact parent | Full-momentum N41503 case/data pair; no initialization; prepared save/reopen span 10 µs; geometry-matched film fields must remain exact |
| Controlled delta | `iters-per-dpm-step`: 20 → 40; nominal physical tracking interval 200 → 400 µs |
| Fixed controls | Full film momentum; 10 µs film step; 17 essential per-update report files; frozen bulk; drain τ=1.5 ms / 666.667 per second; same relaxation and source refresh |
| Mandatory models | EWF and Phase Accretion remain enabled |
| Other physical models | Collection, splash, stripping, edge separation, gravity, shear, pressure gradient, spreading, surface tension and film coupled solution retained; Flow Momentum Coupling OFF |
| Horizon | One native 1,000-update solve, N41503 → N42503 / +10 ms; determine actual tracking positions from the native transcript |
| Safety | Existing native all-sample Courant <1 and thickness <0.3 m guards; finite face fields; local paired endpoint and transcript; no active-run Scheme monitoring |
| Preparation proof | Only the cadence parameter changes; bulk/wall state and film clock unchanged; saved child reopens with identical geometry-matched mass, thickness and XYZ velocity |
| Decision | Compare residual divided by reported DPM input against 1/20 and 1/40; also compare film storage, drainage, DPM input and whole-command cost |
| Claim boundary | A lower discrepancy or inverse-cadence trend does not prove mass conservation. The native deposited mass and its normalization interval still require independent reconciliation. |
| Accuracy tradeoff | Less frequent tracking can alter particle/film coupling; a favourable cost or balance result does not authorize this cadence for mesh convergence |

| Evidence item | Purpose |
| --- | --- |
| C1 — cadence/accounting figure | Cumulative original ledger discrepancy and film mass gain at matched accepted time |
| C2 — native tracking record | Number and update positions of DPM events; distinguish nominal control from actual event timing |
| C3 — endpoint and cost table | Finite fields, invariants, Courant, thickness, drain, storage, timing and uncorrected balance |

| Primary source / existing evidence | Use |
| --- | --- |
| [Fluent 2025 R2 solution controls](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_eqns.html) | Film Steps per DPM Step specifies how often the DPM phase is calculated; available with continuous-phase interaction disabled |
| [Fluent film submodels](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_submodels.html) | Particle/film exchange and event-based creation of stripped/separated particle streams |
| [Field definitions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_fvdefs.html) | Film DPM mass source describes absorbed particle mass; this definition does not establish an N+1 time-normalization rule |
| [Previous accepted long-run ledger](../ewf-only-drain/long-development/results.md) | Residual / reported DPM input ≈0.0500207 at nominal 20-step cadence; hypothesis only |

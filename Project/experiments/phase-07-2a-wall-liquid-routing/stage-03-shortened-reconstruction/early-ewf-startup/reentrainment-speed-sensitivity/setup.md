# Stage 3 — Local re-entrainment speed sensitivity

| Contract | Selected value |
| --- | --- |
| Human authority | 6 October 2026; three local direct-Fluent cases |
| Question | How does inlet speed change film development with splash, stripping and edge separation active? |
| Classification | Partial repeat of early startup and accelerated film development |
| Owning workflow | `phase-loop`; local start/close through `direct-fluent-use` |
| Runtime | HOME-DESKTOP-SH; Fluent 2025 R2 Student; 3D double; four ranks |
| Parent | Prepared historical A, N1580; original bulk fields; dry film |
| Parent case SHA-256 | `5907e357654ebe5437c64f4e6abea19cbbc66b1edd2312f6b2eb63fe408c2b72` |
| Parent data SHA-256 | `72a7134f6358ea68615907f336e71d6e518c713418674477703fc638e41816af` |
| Historical A data SHA-256 | `ff64317d4e6e77661d7faf13d26d4c04ac3d5db2ea78eed461762a3b3531c187` |
| Mesh | Existing 60,964 cells; no topology change |
| Fixed science | Materials, R3 0.5 mm / Cs 0.5, corrected contact absorber, Coupled carrier, film wall scope and phase accretion |
| Selected mechanical change | DPM film coupling prerequisite; Particle Splashing, Edge Separation and Particle Stripping on |
| Source Smoothing | Retain inherited off setting |
| Other physical settings | Retain parent; no added pressure, spreading, surface-tension force, energy, scalar or reciprocal flow momentum coupling |
| TUI proof | Version-matched guide Figures 30.1 and 30.9; explicit TUI responses; native readback and paired save/reopen |
| Droplet feed | Retain negligible diagnostic feed; no extra physical liquid injection |
| Stop | Native EWF elapsed time near 0.250 s from dry activation, separately for each case |
| Stationarity | Not a completion gate; report continued accumulation and numerical limits |
| Other sessions | No remote-server access or changes |

| Case | Nominal speed (m/s) | Both phase feed multipliers |
| --- | ---: | ---: |
| Slow | 20.11 | 20.11 / 26.81 |
| Middle | 26.81 | 1 |
| Fast | 32.14 | 32.14 / 26.81 |

| Run segment | Operation |
| --- | --- |
| Parent proof | Hash files; compare stored A bulk field arrays; retain original fields for every speed |
| Startup | 500 updates at 25% of each speed's target feed; original 2000-update ramp in 10-update blocks; 1000-update target hold |
| Startup film step | Fixed 1 microsecond; actual clock/readback required |
| Development | Reference film-development strategy; matched-time timestep screen, then qualified large batches |
| Bulk freezing | Temporary film-development stage after each speed's startup; label evidence as fixed bulk forcing |
| Numerical recovery | Preserve endpoints; reduce step or repair film controls from a verified parent; do not change physical scope |
| Endpoint | Paired local checkpoint and reopen audit; actual time near 250 ms; final wall-face fields |
| Local checkpoint policy | Approximately 1000 updates; shorter qualification and final batches; no OneDrive intermediate saves |

| Evidence ID | Required evidence | Comparison |
| --- | --- | --- |
| RE-1 | Film inventory, accretion, drainage, separated/stripped mass and DPM source versus actual film time | Three speeds; finite-time sensitivity |
| RE-2 | Native wall thickness and velocity fields | Shared wall facets and colour scale at the endpoint |
| RE-3 | Accepted steps, film Courant, residual evidence, complete native report coverage and mass ledger | Numerical limits; timestep-screen receipt |
| RE-4 | Bulk inventory, phase outlet flux and absorber removal | Startup response; frozen-stage values are not evidence of bulk stationarity |

| Claim limit | Consequence |
| --- | --- |
| Common historical A fields at different target speeds | Startup adaptation is part of the comparison |
| Frozen bulk development | Film response to each saved carrier field; no fully coupled separator or physical transient-time claim |
| New film transfer routes | Extend the film ledger; do not treat film-to-droplet transfer as external removal |
| Alternative implicit solver if used | Missing inner residuals remain a limitation; matched-time agreement is local evidence |
| 250 ms endpoint | Bounded observation; no steady-film, mesh-convergence or physical-validation claim |

| Reference | Link |
| --- | --- |
| Startup | [Existing setup](../setup.md) |
| Film development | [Setup](../film-development/setup.md), [results](../film-development/results.md) |
| Inlet-speed inspiration | [Phase 8 context](../../../../phase-08-storyline-reconstruction/stage-01-60k-storyline/CONTEXT.md) |
| Re-entrainment rationale | [CFD wiki](../../../../../../CFD_wiki/wiki/physics-basis/droplets-carryover-and-re-entrainment.md) |
| Official model options and Figure 30.1 | [Fluent 2025 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html) |
| Official wall options and Figure 30.9 | [Fluent 2025 R2](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html) |

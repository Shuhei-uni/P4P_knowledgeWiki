# Stage 4 — Flow Momentum Coupling OFF retry

| Contract | Value |
| --- | --- |
| Human authority | 7 October 2026: turn off Flow Momentum Coupling and retry; then add 2000 more bulk updates |
| Question | Does removing reciprocal film-to-bulk momentum feedback permit the selected settings to run? |
| Parent | Original verified selected-settings N29815 prepared pair; exact original bulk/film fields and clock |
| Controlled physical delta | Flow Momentum Coupling OFF on active film wall wall |
| Retained physics | Pressure Gradient, Spreading, Surface Tension, EWF DPM coupling, Splashing, Edge Separation, Stripping, Phase Accretion, film Momentum Equation, Gravity, Surface Shear and EWF Coupled Solution ON |
| Retained model | Mesh, feeds, collector, material compatibility, commercial-steel roughness and film wall scope |
| Initial numerics | Original first-probe controls: 1 microsecond fixed film step, alternative implicit film solver, 30 film subiterations, bulk pseudo scale 1.0 and original relaxation |
| Initialization | None; retain bulk and film fields and clock |
| Parent film time | 0.2691843386355824 s |
| Bulk and film horizon | 4000 additional iterations in total: N29815 → N33815; first 20 are instrumentation probe; all four bulk equation groups ON |
| Film-only horizon | Then freeze bulk and add 50 ms native EWF time; aim for 15 microseconds, subject to numerical recovery |
| Checkpoints | Paired local Fluent disk; preserve both feedback-ON failures before replacement |
| Required evidence | Five requested diagnostics; particle transfers; native step/clock/Courant; paired reopen; numerical failure tails |
| Interpretation | Initial matched probe isolates feedback switch; longer trajectories remain finite-time numerical evidence |
| Claim limit | One-way bulk-to-film response; no reciprocal flow response or full-system stationarity claim |
| General contract | [Selected-mechanism setup](../setup.md) |

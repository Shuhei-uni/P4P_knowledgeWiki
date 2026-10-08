# Stage 4 — Film development with selected diagnostics

| Contract | Selected continuation |
| --- | --- |
| Authority | Human: keep running; full ownership of Server 1 |
| Question | How does the developed full-momentum film evolve over another 50 ms using the measured lower-cost report plan? |
| Classification | Diagnostic film development; unresolved source accounting prevents physical-accuracy qualification |
| Parent | Furthest verified 10 µs full-momentum endpoint N43483; native film clock 0.4081843386354826 s; original paired hashes must match before reopen |
| Preserved sibling | Complete and capture the cadence40 comparison before replacement; retain its paired endpoint |
| Selected change | [17-report plan](../report-cost/results.md): 29.52% lower solve time and exactly equal shared histories / film fields in the +10 ms comparison |
| Fixed physics | All accepted full-momentum wall physics, including EWF and Phase Accretion; Flow Momentum Coupling OFF; frozen bulk |
| Fixed numerics | 10 µs; DPM every 20 film updates; same relaxation, implicit/coupled controls and source/profile cadence |
| Direct drain | τ=1.5 ms; 666.667 per second; matched mass and XYZ momentum sinks; 1% per-refresh bound unchanged |
| Restart proof | No initialization; exact geometry-matched mass/thickness/XYZ velocity; fixed bulk/wall/parameter state after save/reopen. Prepared-pair elapsed injection span resets to 10 µs; record the observed parent span. |
| Horizon | +5,000 updates / +50 ms to N48483; expected native film clock 0.4581843386354826 s |
| Native control | Existing Fluent-owned journal; 1,000-update guard intervals; all-sample Courant <1 and maximum thickness <0.3 m; native autosave at 5,000 updates; paired endpoint on horizon or guard rejection |
| Files | Local paired checkpoints, transcript and essential per-update ledger/guard histories on Server 1; no laptop-controlled solve |
| Observation | Passive transcript; bounded Settings idle query only if completion cannot be resolved; no active-run Scheme queries |
| End decision | Capture endpoint and all histories; assess actual clock/count, finite fields, stability, upper/lower mass, direct drain, original uncorrected ledger and timing before further extension |
| Claim boundary | Positive storage is development, not steady film. Frozen-bulk film behaviour does not establish fully coupled separator behaviour. Missing achieved inner residuals remain a gap. |

| Evidence item | Quantity / use |
| --- | --- |
| F1 — development history | Total/upper/lower film inventory, maximum speed, Courant and thickness; inspect filling, routing and numerical behaviour |
| F2 — original film ledger | Phase/DPM rates, direct drain and cumulative removal stocks; no inverse-cadence correction |
| F3 — computational cost | Whole-command solve time; distinguish parallel timer, save/reopen and retrieval |

| Implementation owner | Link |
| --- | --- |
| Preparation, native submission and terminal recovery | [Server 1 continuation runner](../../../../../PyAnsys/scripts/setup/run_phase72a_stage4_core_development.py) |

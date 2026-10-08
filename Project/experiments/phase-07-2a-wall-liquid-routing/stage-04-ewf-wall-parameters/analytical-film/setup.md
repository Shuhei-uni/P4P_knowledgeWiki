# Stage 4 — Analytical film velocity

| Contract | Selected test |
| --- | --- |
| Authority | Human, 8 October 2026: start the approved analytical-film direction; full ownership of Server 1 |
| Question | Can analytical velocity develop a balanced, stable film with practical cost while retaining EWF and Phase Accretion? |
| Classification | NEW momentum closure; previous force/stripping screens used the momentum equation |
| Parent | Verified drain-ON N41483 / film clock 0.3881843386354626 s; exact pair and hashes in the [long-run manifest](../../../../../PyAnsys/output/phase72a-stage4-ewf-long-native/20261007/run-manifest.json) |
| Recovery | Preserve the current N68483 diagnostic endpoint before replacement; no bulk or film initialization |
| Physics delta | Analytical Solution instead of Momentum Equation; Solve Momentum remains ON |
| Numerical screen | Fixed 10 µs; compare analytical 5 µs and full momentum 10 µs at matching accepted film times |
| Invariants | Mesh, feed, materials, roughness, film walls, accretion, collection, stripping, separation, splash, drain τ=1.5 ms, Flow Momentum Coupling OFF |
| Bulk mode | Frozen initially; later refresh comparison remains in scope after analytical functional proof |
| Short proof | One 20-update smoke check; count it in the arm horizon. Require positive collection/removal, accepted time, finite fields and frozen bulk. Probe ledger limit 5%; qualification limit 1%. |
| First screen | Total +20 ms per arm; analytical10: 2000 updates; analytical5: 4000 updates; momentum10: 2000 updates |
| Conditional extension | Continue an acceptable analytical route in ≥1000-update native blocks, initially toward +500 ms; stop on declared numerical/evidence failure and analyse before further extension |
| Numerical guards | Every recorded Courant sample <1 and thickness <0.3 m; all relevant fields finite. Native guard assesses all samples at each block return. |
| Solve ownership | Fluent-native Scheme/TUI journals; local paired checkpoints and transcript; Python prepares/submits/retrieves and does not control a running solve |
| Evidence route | Proven direct Fluent file read; selected files recovered without archive. Connection required for remote retrieval; server-local evidence persists after laptop closure. |
| Runtime comparison | Separate solve, save, reopen and retrieval time; total time to qualified endpoint remains the final cost metric |
| Claim boundary | A stable analytical result tests this reduced closure under recorded forcing; it does not validate pressure/inertia omission or a fully coupled separator |

| Primary configuration evidence | Use |
| --- | --- |
| [Fluent v252 UG 30.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_options.html), Figures 30.1 and 30.2 visually checked | Solve Momentum prerequisite; distinct Analytical Solution and Momentum Equation selectors; independent Phase Accretion |
| Live native `wall-film/model-parameters` | Exact `solve-momentum?` and `mom-equation?` values; change the latter only for the physical comparison; save/reopen and smoke proof |
| Generated v252 TUI menu | `model-options` exists but does not expose a dedicated one-setting analytical command or verified prompt sequence. Use the established native RP API rather than guess prompts. |
| [Analytical theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_ewf_sec_film_vel.html) | Shear/gravity equilibrium velocity; mass stays transient |
| [Wiki annular-flow precedent](../../../../../CFD_wiki/wiki/sources/mondal-sharma-2024-air-water-annular-flow-cfd.md) | Validated precedent uses broader momentum physics in a straight air–water pipe; no validation of analytical velocity in this separator |

| Core artifact | Quantity / source / decision |
| --- | --- |
| A1 — matched development | Native upper/lower mass, drain rate, thickness and Courant versus accepted film time; compare methods and timestep |
| A2 — film ledger and cost | Collection rates × accepted steps; cumulative outflow/stripping/separation differences; direct sink counted once; native solve timing separate from artifact handling |
| A3 — wall distribution | Saved face mass/thickness/XYZ velocity and face centres; transport versus wall height and extreme-speed locations |

| Accounting / timing constraint | Treatment |
| --- | --- |
| Instantaneous phase source clears on reload | Integrate solved native histories; reopened zero is not zero input |
| DPM cadence | Retain configured controls for the first method contrast; record actual native injection span. A timestep contrast also changes step-indexed cadence unless independently preserved. Label that limitation. |
| Drain refresh | Profile interval 1; declare step-sized refresh bound without changing 666.667 /s physical coefficient |
| Inactive force flags | Analytical velocity does not solve general pressure/curvature response; retained flags do not imply active momentum forces |

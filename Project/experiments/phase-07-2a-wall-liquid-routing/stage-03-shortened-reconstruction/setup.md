# Stage 3 — Shortened model reconstruction

| Item | Selected contract |
| --- | --- |
| Human authority | 5 October 2026 handoff; full ownership of Server 3 |
| Question | Can a short startup reproduce the current Phase 7.2A model on its existing mesh? |
| Classification | New startup contrast; no physical-model change |
| Reference | Corrected R3/contact-absorber N33586; independent four-rank replay from original E2.7 |
| Reference case SHA-256 | `1dedd5e01fca7b694c7af4c9da23f823c328931b6ee64a7aa717a63b25e0fe11` |
| Reference data SHA-256 | `5810d6049a6862d04e2c55791eee75de9a471d349ab73052366ca69f3c87c25e` |
| Reference evidence | [Stage 2 results](../stage-02-combined-ewf-roughness/results.md); [native reference state](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/reference-state.json) |
| Reference limit | Developed film; no stationary-film or complete-separator qualification |
| Native source reconciliation | Older load receipt cached zero UDF source; Server 3 evaluates `64.6792 kg/s`, matching independent depletion expression |
| Preparation | Load verified model settings; reset bulk and film fields; retain native film model and wall assignments with film equations off |
| Mesh | Existing approximately 60k mesh; no remeshing in this screen |
| Fixed physics | Materials, phases, turbulence, DPM, collector extent, boundary assignments, accretion, feedback flags and source hooks from exact reference |
| Absorber | Corrected `libcontactv2`; phase-liquid velocity in momentum removal; depletion time `1e-5 s` |
| Roughness | R3; physical height `5e-4 m`, constant `0.5`; exact reference walls |
| Bulk controls | Coupled from startup; inherited controls; fraction relaxation `0.1` |
| Target feed | Split mass-flow inlets; liquid `116.92 kg/s`, vapor `80.69 kg/s` |
| Low feed assumption | 25% of each target; uses [parent startup precedent](../../phase-07-1a-absorber-convergence/v2-inlet-loading-ramp/results.md) |
| Feed interpretation | Ramp the verified mass flows; do not substitute Phase 8 velocity settings |
| DPM loading | Retain inherited diagnostic one-way injections; verify active definitions and fates; no added two-way source |
| Reference preservation | Unique paired local save before resetting fields |
| Cost | Wall-clock duration for each solve block and each film arm; include solver process/rank identity when available |

| Startup updates | Feed and action | Batch size |
| --- | --- | --- |
| 0–1500 | 25% target; film equations off | 1000 then 500 |
| 1500–2500 | Ten loading steps: 32.5%, 40%, …, 100%; hold each step | 100 |
| 2500–3000 | 100% target; film equations off | 500 |
| At 3000 | Enable and initialize dry EWF; preserve paired common parent | No solve |
| Fixed arm | 3000 film updates at `1e-6 s` | 1000 |
| Adaptive arm | Restore common dry-film parent; 3000 film updates | 1000 |
| Adaptive controls | Initial `1e-6 s`; Courant target `0.1`; increase `1.2`; decrease `2.0` | Native accepted steps required |

| Required evidence | Source and reduction | Decision use |
| --- | --- | --- |
| Routing and bulk state | Native per-update pressure-drop, vapor and liquid outlet flux, source integral and inventories; final 500-update window | Compare short reconstruction with developed reference |
| Film development | Native clock, accepted step, inventory, thickness, accretion and cumulative drainage | Compare timestep arms at matched elapsed film time |
| Accounting | Applied UDF source; boundary-only phase fluxes; native film ledger integrated on actual film clock | Detect false apparent reproduction |
| Numerical behaviour | Native residual transcript; warning/failure events | Explain numerical limits |
| Spatial response | Same surfaces and scales for velocity, bulk liquid fraction and film thickness | Test whether similar scalar values hide different distributions |
| Durability | Paired checkpoints every 1000 updates; final paired reopen | Verify a reusable reconstruction endpoint |

| Predeclared screen tolerance | Value and interpretation |
| --- | --- |
| Vapor outlet and pressure drop | Reconstructed final-window mean difference ≤5% from preserved reference snapshot; numerical screen only |
| Liquid carryover and bulk/film inventory | Reconstructed final-window mean difference ≤10% from preserved reference snapshot; numerical screen only |
| Film maximum/mean thickness and drainage/accretion rates | Difference ≤10% at stated time/window; distribution evidence also required |
| Low-reference fallback | State absolute difference where division by a small reference is unstable; no automatic pass |
| Film ledger | Absolute error ≤1% of integrated accretion for each arm |
| Bulk ledger | Source-inclusive boundary mismatch reported separately; no physical `dM/dt` inferred from steady pseudo-time |
| Stable reproduction | Scalar tolerances, source/film accounting, consistent spatial response and sustained windows all required |
| Reference limitation | A drifting reference permits a development-state comparison; it cannot certify steady reconstruction |
| Reference window gap | No matching stationary reference window is available; snapshot agreement cannot support a stronger reproduction claim |
| Film recovery limits | Nonfinite state or film thickness >3 mm; preserve endpoint and investigate |
| Diagnostic film cap | Retain reference 1 m cap; no cap-based success claim |
| Matched-time rule | Use native clock increments; never infer adaptive elapsed time from iteration count or an upper bound |
| Startup horizon | 3000 film updates are a screen; do not automatically run the earlier rough 0.2–0.5 s estimate |
| Later mesh family | Start only after existing-mesh evidence supports reproduction; preserve physical roughness, film boundaries and collector extent |

| Machine owner | Link |
| --- | --- |
| Runner | [Server 3 reconstruction runner](../../../../PyAnsys/scripts/setup/run_phase72a_stage3_server3.py) |
| Artifact and progress map | [Run manifest](../../../../PyAnsys/output/phase72a-stage3-server3/20261005/run-manifest.json) |
| Deliverable | Tested recipe, measured cost, evidence and claim limits |

# Phase 7.2A Stage 2 — E2.7 EWF plus R3–R5 roughness

| Item | Phase 7.2A Stage 2 — E2.7 EWF plus R3–R5 roughness |
| --- | --- |
| three requested runs | are complete to native 16586 |
| — | See the [matched results and claim limits](results.md) |

## Selected follow-up — 3 October 2026

The Server 1 continuation completed another 6,000 updates at 1 microsecond,
reaching N23586 and 10,000 restart updates. Maximum film thickness is
0.291141 mm and inventory is 6.013528 kg, still gaining approximately
16.19 g per 1,000 updates. Film is bounded but not stationary. Final paired
checkpoints are saved and hashed; a service stall blocks the final full
settings readback and shared transfer. Server 1 was not terminated.
See the [longer-film result](results.md#contact-absorber-10000-updates-at-1-microsecond).

| Item | Selected follow-up — 3 October 2026 |
| --- | --- |
| Latest timestep match | the separate R3/contact arm using E2.7's fixed 1e-5 s film step completed N13586–17586 and reopened exactly |
|  | Film runaway returned: the 1 m diagnostic cap was reached at N13776, final film inventory was 6305.274 kg and film-side closure failed |
|  | This arm is scientifically rejected; the earlier 1e-6 s thin-film response does not isolate an absorber benefit |
|  | Owned local sessions are closed |
|  | See the [timestep-matched evidence](results.md#contact-absorber-with-e27-timestep) |

<details>
<summary>Supporting detail — Selected follow-up — 3 October 2026</summary>

| Item | Selected follow-up — 3 October 2026 |
| --- | --- |
| Latest original-parent restart | the human then requested 4,000 iterations directly from the original E2.7 N13586 solution, before the old R3 film grew to 0.3 m |
|  | This separate corrected R3/contact child completed N17586 with original-array verification, four checkpoints and exact final reopen |
|  | Film maximum decreased from 0.30979 to 0.298108 mm; steady convergence remains unqualified |
|  | All owned local sessions are closed |
|  | See the [restart result](results.md#contact-absorber-restart-from-original-e27) |
| Latest execution instruction | use local `direct-fluent-use` from now and do not access Server 1 |
|  | R3 + E2.7 with the new shared absorber completed the requested N13586–16586 continuation with the matched 1 m cap |
|  | See the [old/new comparison](results.md#r3-new-absorber-direct-comparison) |
|  | Earlier fleet execution instructions below describe the completed cap-test contract and are superseded for further execution |
| Latest human correction | omit R5 from the 1 m cap test |
|  | Finish R3 and R4 only; the historical R5 0.3 m result remains comparison evidence |
| Latest selected mechanism | independently remove bulk liquid, EWF and liquid DPM on contact with the existing lower collector |
|  | The [contact collector setup](ewf-absorber/setup.md) supersedes the shared-throughput budget |
|  | Its corrected local R3+E2.7 prototype completed a 1,000-iteration bounded screen and exact saved-endpoint readback |
|  | Collector liquid is nearly zero and film remains thin, but bulk steady convergence and joint mass closure are unqualified |
|  | See the [contact trial](results.md#all-liquid-contact-absorber-trial) |
|  | Retain the earlier shared-budget and metre-cap endpoints as separate evidence |
| — | The unchanged contact-absorber continuation then completed all 4,000 additional iterations from N14686 to N18686, including four paired local checkpoints and exact endpoint reopen verification |
|  | Film maximum decreased to 0.29443 mm; collector inventory remained below 1 g |
| owned local sessions | are closed |
| — | See the [continuation evidence and limits](results.md#contact-absorber-4000-iteration-continuation) |
| Film removal preference | the human prefers liquid to leave EWF through drainage or release into the flow while other liquid continues to accrete |
|  | A hard film-thickness limit is a last resort |
|  | After preserving the matched cap tests, audit existing film-edge drainage and design separate shear-stripping and edge-separation contrasts within the authorized DPM work |
|  | Account for accretion, film storage, edge outflow, released droplets and their subsequent fate without adding released film mass a second time as inlet loading |
|  | Native film-edge outflow is not automatically proof of transfer to the bulk liquid or absorber |
|  | Require a numerically credible starting film before interpreting release rates physically; metre-scale cap-seeking children are diagnostics |
| — | The human authorized a Phase-8-style speed/DPM sequence for Stage 2, with ownership of servers 1 and 3 and no `direct-fluent-use` workflow |
|  | Before that sequence, the human selected a maximum-film-thickness sensitivity: raise the exploratory limit from 0.3 m to 1 m to measure growth beyond the old cap |
|  | Repeat E2.7+R3 and E2.7+R4 independently from the same hash-verified N13586 parent above, retaining the respective roughness and all other physics and numerical controls |
|  | Change only `thickness-limit` to 1.0 m relative to each original Stage 2 child |
|  | Run 3,000 additional steady iterations in three 1,000-iteration Settings/API blocks; retain server-local paired checkpoints |
|  | Save/reopen and verify the cap and roughness before compute |
|  | Preserve loaded valuable endpoints before replacement |
|  | Keep OneDrive for selected start/final pairs |
|  | Compare every-iteration maximum/mean thickness, film mass, film speed, wetted area, bulk liquid inventory, phase outlet fluxes, absorber diagnostic, and continuity against the 0.3 m histories at matched native offsets |
| Reaching 1 m | remains a censored thickness result; growth or a plateau does not alone establish physical accumulation, drainage, or convergence |
| The speed/DPM sequence remains authorized after this sensitivity | five speeds 20.11, 23.46, 26.81, 29.48 and 32.14 m/s, first carrier-only, then one-way DPM, then two-way DPM with continuity histories |
|  | Retain the Stage 2 absorber/EWF lineage and roughness contrasts |
|  | Carry over the seven-bin Phase 8 PSD and the 2.5%, 5%, 7.5%, 10% and 20% liquid-allocation sensitivity, complemented by tracking-cap, integration-step, release-count, diameter-bin, stochastic dispersion and source-update sensitivities |
|  | Fix matched allocation controls before attributing a change to interaction |
|  | The exact execution matrix and accounting must be compiled from verified cap-test endpoints before compute; this selected follow-up does not resume the separate paused Phase 8 jobs |

</details>

## Question and comparison

| Item | Question and comparison |
| --- | --- |
| — | From the completed E2.7 continuation, how do three previously tested outer-wall roughness levels affect phase-2 liquid outflow through `steamoutlet`, EWF film response, and bulk liquid inventory? |
| This | is a combined-mechanism screen, not a replay of the earlier no-EWF R3–R5 results |
| — | Compare the three children with one another and with the E2.7 continuation's terminal behaviour |
|  | Historical R3–R5 results began from a different parent and cannot serve as matched controls |

## Common parent

| Item | Common parent |
| --- | --- |
| — | Each child loads the same final E2.7 continuation case/data pair at native iteration `13586`, saved under the local OneDrive sync folder `P4P-Fluent-Artifacts/Phase72A/FamilyE/E2.7-continuation-5000/20260923T102912Z/`: |
|  | `P72A-E2.7-CONT5000-final-N13586.cas.h5` — SHA-256 `bc9eeac09adfeca77ebe467c03e6425f3f9bb7069aa5b1eaa9a839ee44f92990` |
|  | `P72A-E2.7-CONT5000-final-N13586.dat.h5` — SHA-256 `57e8b1a97f9d9db8665eb0ab1a211c08065e1a0befc4570a90b89ab18fe61af5` |
| These | are the durable final pair hashes in the [continuation run manifest](../../../../PyAnsys/output/phase72a_ewf_server1_e27_cont5000_20260923T102912Z/run-manifest.json), confirmed against files on this machine |
| They differ from the server-local final pair hashes | recorded in that manifest |
| — | Use and verify the durable pair as one matched parent; do not mix pair sources |
|  | Confirm native iteration and E2.7 settings after load |
| earlier native-8586 source-identity limitation | remains part of this parent provenance; see the [continuation result](../ewf-family/results.md#e27-continuation--another-5000-iterations-on-server-1--2026-09-23) |

## Controlled children

| Stage 2 case | Roughness setting inherited from | `k_s` (m) | `C_s` | Setup |
| --- | --- | ---: | ---: | --- |
| `E2.7+R3` | R3 | `5e-4` | `0.5` | [setup](e27-r3/setup.md) |
| `E2.7+R4` | R4 | `1e-3` | `0.5` | [setup](e27-r4/setup.md) |
| `E2.7+R5` | R5 | `2e-3` | `0.5` | [setup](e27-r5/setup.md) |

| Controlled children |
| --- |
| Apply roughness only to `separator-purnanto:1`, `separator-purnanto:1:001`, `wall`, and `wall:004`, as in the [R4/R5 setup](../roughness-family/extension-r4-r5-setup.md) |
| Preserve the parent mesh, steady Mixture/RNG physics, inlets, phase-2 absorber, outlet, bottom walls, solver controls, and E2.7 phase-accretion EWF settings |
| In particular preserve maximum film thickness `0.3 m`, ten film subiterations, fixed film timestep `1e-5 s`, EWF Coupled Solution ON, and film-wall Flow Momentum Coupling OFF |
| Do not reinitialize, patch, or replay the inlet ramp |

## Run and evidence contract

| Item | Run and evidence contract |
| --- | --- |
| — | For each independently prepared child, verify pair hashes and native iteration, apply and read back the wall-only roughness delta, save/reopen the prepared pair, then run one native `/solve/iterate 3000` from `13586` to expected `16586` |
|  | Keep Fluent-native reports at every iteration and preserve server-local paired checkpoints (including start and final) |
|  | Keep only the shareable start and final pairs in OneDrive |
|  | Record the full solver transcript, residuals, warnings, and report files |
| A failure preserves the last valid state and | is reported at its actual native coordinate |

<details>
<summary>Supporting detail — Run and evidence contract</summary>

| Item | Run and evidence contract |
| --- | --- |
| — | Plot the following against native iteration, with the three children on matched axes and the parent terminal value indicated where available: |
|  | signed phase-2 `steamoutlet` mass flux (`kg/s`; negative means outflow); |
|  | EWF total film mass (`kg`), maximum film thickness (`mm`), and area-weighted average film speed (`m/s`); |
|  | EWF wetted area (`m²` and fraction of active EWF wall area); |
|  | total bulk liquid inventory (`kg`) |
|  | The continuation already has native reports for outlet flux, film mass, thickness, speed, and liquid inventory |
|  | Check their definitions/readback in each prepared child |
|  | Wetted area had only a terminal reconstruction in the parent, not a full history |
|  | Before solving a child, establish an every-iteration Fluent-native Film Coverage area report on the active EWF wall and verify its value/zone scope |
|  | If Fluent cannot provide that report, preserve enough per-face film-thickness and face-area evidence at declared checkpoints to reconstruct wetted area using the documented `1e-10 m` critical-thickness threshold; state the resulting sampling cadence explicitly |
|  | Do not label an endpoint value as a time history |
|  | For interpretation, also retain absorber command/applied removal, phase-1 and mixture outlet fluxes, source-inclusive closure/storage, and solver-health evidence from the existing native reports |
|  | Compare raw traces and a common late 500-iteration window when complete; report trends and variability as well as endpoints |
| A lower outlet-flux magnitude alone | is insufficient if bulk inventory is depleted, film response keeps moving, closure deteriorates, or the solution fails |
| — | This screen does not establish physical drainage, convergence, or plant separation efficiency |

</details>

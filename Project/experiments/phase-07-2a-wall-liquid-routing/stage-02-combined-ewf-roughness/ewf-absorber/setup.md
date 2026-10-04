# Lower liquid absorber

## Current local replay and extension

| Run setting | Verified value or requirement |
| --- | --- |
| Human instruction | Run through `direct-fluent-use` locally |
| Parent | Verified local N17586 pair; hashes and paths in [local manifest](../../../../../PyAnsys/output/phase72a-contact-absorber-local-20000/20261004T081120Z/run-manifest.json) |
| Remote gap | Server 1 N23586 files were not synced |
| Replay command | `/solve/iterate 6000` from N17586 to local N23586 |
| Extension command | Then `/solve/iterate 10000` to N33586 |
| Full horizon | 20,000 updates from original E2.7 N13586 |
| Model invariants | All parent fields, hooks, film wall, entry faces, DPM, film parameters and controls verified |
| Film timestep | Fixed 1 microsecond |
| Checkpoints | Native paired autosaves every 1,000 updates on local disk; retain all |
| Endpoint saves | Explicit paired files at local N23586 and N33586 |
| Supervision | One four-hour check; no continuous status queries |
| Lineage | Independent 4-rank local replay; compare with Server 1's 18-rank result as separate evidence |
| Server 1 | No changes or further commands during local execution |

## Active contact-capture trial

The latest human request continues the completed 1 microsecond thin-film
N17586 endpoint on Server 1 for **6,000 more iterations to N23586**. This
gives 10,000 updates and 0.01 s added film time from original E2.7 N13586.
Restore the exact saved contact settings and solution fields; retain the
1e-6 s film timestep, R3, libcontactv2, bulk tau=1e-5 s, fraction relaxation
0.1, native EWF edge drainage and inherited one-way DPM. Host transfer is
not a new numerical package. Verify parent hashes, loaded fields/hooks and
save/reopen before compute. Keep checkpoints and reports on Server 1 local
disk; stage only input and final artifacts through shared OneDrive.

Record all 6,001 native coordinates and six paired 1,000-update checkpoints.
Combine with the earlier 4,001-coordinate arm, removing only the verified
N17586 overlap. Plot maximum thickness and film inventory over the full
10,000 updates, plus native accretion/drainage and film CFL. Assess the
final three consecutive 1,000-update windows for continued inventory and
thickness drift, and evaluate the integrated film mass ledger. Report a
steady-film state only if thickness and inventory flatten together and
accretion balances drainage; a flat maximum alone is insufficient. Preserve
finite instability evidence to the requested horizon; native fatal/nonfinite
failure ends this exact-settings arm without hidden timestep reduction.
Server 1 is explicitly authorized for this continuation and stays open
after endpoint verification. R5 remains cancelled.

| Item | Active contact-capture trial |
| --- | --- |
| — | The latest human instruction sets the film timestep to E2.7's fixed 1e-5 s for a separate 4,000-iteration child from original N13586 fields |
|  | Only `timestep-max` changes relative to the prepared corrected contact restart; other controls, R3, libcontactv2 and collector boundaries remain unchanged |
|  | Verify prepared fields/settings and fresh-session reopen before compute |
|  | Save after 100 updates, then at N14586/15586/16586/17586 |
| Target film-time advance | is 0.04 s |

<details>
<summary>Supporting detail — Active contact-capture trial</summary>

| Item | Active contact-capture trial |
| --- | --- |
| — | Retain finite cap-seeking behaviour as failure evidence while attempting the requested horizon; a native fatal/nonfinite failure ends this exact-settings trial |
|  | Do not silently reduce the timestep or introduce recovery controls into this comparison |
|  | The requested arm completed N17586 with exact endpoint reopen and closed owned sessions |
| It | is rejected for runaway film and failed film-side mass accounting; see [the timestep-matched result](../results.md#contact-absorber-with-e27-timestep) |
| — | The latest human request restarts a separate 4,000-iteration R3/contact child directly from the original E2.7 N13586 solution fields (maximum film thickness 0.30979 mm), targeting N17586 |
|  | Use the corrected contact case as a settings template, then load the hash-verified original E2.7 data, restore selected film/solver controls after data read, and save/reopen the prepared N13586 pair before solving |
|  | Retain libcontactv2/tau=1e-5 s, film step=1e-6 s, explicit fraction relaxation=0.1, native EWF edge drainage and DPM escape |
|  | Save paired checkpoints at N14586, N15586, N16586 and N17586 |
|  | Preserve the completed N14686–18686 continuation as separate evidence |
| Film-clock and bulk-convergence limits | remain as stated below |
| — | The human subsequently authorized a 4,000-iteration unchanged continuation from the verified corrected contact endpoint N14686 to N18686 |
|  | Retain libcontactv2, tau=1e-5 s, film timestep=1e-6 s, explicit volume-fraction relaxation=0.1 and all saved boundary/DPM settings |
|  | Save local paired checkpoints at N15686, N16686, N17686 and N18686; verify the final saved endpoint by reopening |
|  | Assess late residuals, collector inventory/removal, film thickness and film mass accounting without treating execution completion as steady convergence |
|  | The latest human instruction on 3 October 2026 supersedes the shared throughput budget below: remove inlet liquid on entry to the existing lower collector, regardless of whether it is phase-2 liquid, EWF or liquid DPM |
| Run locally with `direct-fluent-use`; Server 1 | remains prohibited, R5 cancelled |
| prior shared-budget endpoint | remains a preserved comparison |
| — | Start each discovery child from the hash-verified E2.7 N13586 parent |
|  | Retain R3 roughness, E2.7 models and the diagnostic 1 m cap |
| Bulk removal | uses `S_l=-rho_l*alpha_l/tau` with its negative implicit derivative and matching Mixture momentum removal `S_l*u_l` using liquid velocity; its implicit momentum derivative holds slip fixed |
| — | It has no prescribed throughput, removes no vapor, and does not overwrite alpha |
|  | Screen tau=1e-3, 1e-4 and 1e-5 s independently; compare lower inventory/max alpha, actual integrated source, boundary fluxes, source-inclusive balance, residuals and film response |
| Finite tau | is an approximation to perfect bulk capture, not a literal zero-alpha constraint |
| If the 10 microsecond branch | remains sensitive, compare 1 microsecond under the same controls |
| — | Reduce volume-fraction relaxation if the fast source oscillates |
|  | Preserve the initial mixture-velocity prototype as rejected implementation evidence; only the corrected liquid-velocity library can support an accepted collector result |
|  | The first fast-source trial destabilized EWF at its inherited 1e-5 s film step |
|  | A 1e-6 s film step recovered a thin film in the short screen |
|  | Parameter RP readback alone did not activate the changed film step: verify the printed native step after saved-case load and equation activation |
|  | Film-step changes alter elapsed physical time per iteration, so these trials are not matched physical-time comparisons with the preserved 3,000-iteration run |
|  | For film, terminate the EWF domain at its existing lower edge and keep `wall:004` outside EWF |
|  | Verify native film outflow and retain upstream film inventory on preparation |
|  | This drain removes film through transport flux, without a source coefficient or droplet release |
|  | For DPM, test native escape on the collector-entry faces with zero carrier resistance, and on lower walls |
|  | Prove fate/mass accounting in frozen-field tracking before coupling |
|  | Do not use evaporating-particle trap or zero particle mass as removal |
|  | The existing lower zone contains 715 cells selected by y<=0.10 m centroids |
| Its separating faces | are stepped (vertex y=0.03211–0.18477 m), not a fitted y=0.10 m plane |
| — | Capture refers to entry to that existing collector |
| Exact geometric-plane capture would | require a fitted mesh and is not claimed |
| — | Use short discovery runs to detect immediate failure, then a 1,000-iteration qualification screen and save/reopen continuation if the model passes |
| Success | requires near-dry lower bulk liquid insensitive to further tau reduction, independently accounted film/DPM removal and bounded numerical behaviour |
| — | A running solver alone does not qualify separator performance |

</details>

## Preserved shared-budget comparison

| Item | Preserved shared-budget comparison |
| --- | --- |
| — | The human authorized the existing lower absorber to remove EWF liquid on 3 October 2026 |
| This | is a new numerical collector contrast, not a physical evaporation or stripping model |
| — | Preserve completed R3/R4 cap-test endpoints |
|  | Start implementation checks from the hash-verified E2.7 N13586 parent, rather than the numerically unphysical metre-thick endpoints |

## Controlled change

| Item | Controlled change |
| --- | --- |
| — | The active upper film wall has no face centres in the existing y <= 0.10 m collector |
|  | Extend EWF to `wall:004`, the 34-face lower outer-wall segment whose centres are at y=0.044–0.047 m, retaining the upper film data and bulk flow |
|  | Keep the bottom and inner walls outside EWF |
|  | Use Initial Condition and User Source Terms on this lower film wall |
|  | Apply negative film mass flux and matching mean-film-velocity momentum removal; no direct vapor source |

<details>
<summary>Supporting detail — Controlled change</summary>

| Item | Controlled change |
| --- | --- |
| — | Share the existing inlet-throughput command between bulk liquid in `p71a-v2-virtual-outlet` and EWF on `wall:004` |
|  | With the common verified constant liquid density, use their combined liquid volume, floored at 1e-6 m³, to select the film share |
| Its removal coefficient | is the smaller of command/(density*combined volume) and 0.1/profile-update film-time span |
| film sink | is -coefficient*density*height |
| — | Give the remaining command to the existing bulk sink, retaining its original bulk-only 1e-6 m³ denominator floor |
|  | Dry film therefore leaves the original bulk removal unchanged |
|  | Bound film depletion to at most 10% over a conservative ten-film-step span from the inherited `film-per-flow-iters` setting |
|  | The isolated native clock demonstrated one physical film step per bulk iteration; the retained bound is therefore 1% per observed update |
|  | Implicit subiterations do not add film time |
|  | A limited combined rate may fall below the command and must be reported; never silently compensate by removing unavailable liquid |
|  | Keep the inherited fixed 1e-5 s film step and profile update interval 1 |
|  | Retain the authorized 1 m thickness safeguard as diagnostic clipping only |
| R5 | remains cancelled |
| — | Establish source operation first with a smooth-wall implementation check, then retain R3/R4 as separate roughness contrasts |

</details>

## Evidence before scientific continuation

| Item | Evidence before scientific continuation |
| --- | --- |
| — | The latest human instruction selects R3 + E2.7 with this collector for exactly 3,000 additional iterations, executed locally through the explicitly invoked `direct-fluent-use` workflow |
|  | Do not access or work on Server 1 |
|  | Copy the hash-verified E2.7 N13586 parent from the local OneDrive input into the dedicated Fluent runtime, build the same collector and R3 roughness, and retain the 1 m cap to match the completed old-absorber R3 cap test |
|  | Keep 1,000-iteration paired checkpoints and every-iteration native reports on the local machine |
| Compare the old/new upper-wall histories directly, and | include lower and combined film storage/thickness so extending EWF area cannot hide accumulation |

<details>
<summary>Supporting detail — Evidence before scientific continuation</summary>

| Item | Evidence before scientific continuation |
| --- | --- |
| — | Read back source hooks, lower-wall extent, density, combined removal budget, and invariants; prove unchanged upper-film inventory during configuration |
|  | Save/reopen a local case/data pair |
|  | Demonstrate negative-source operation in an isolated film-inventory check and report film/source update cadence |
| first scientific screen | uses 1,000-iteration blocks and local checkpoints |
| — | Record bulk removal, film removal, their sum and command error separately; lower film storage, upper film storage, native film-edge outflow, thickness, film velocity/Courant and subiteration residuals; existing bulk inventory, phase outlet fluxes and continuity |
|  | Do not double count user film sources in Fluent's source-inclusive film flux reports |
|  | A nonzero sink or successful run does not establish stable film transport or physical separator performance |
| Implementation | `PyAnsys/src/pyansys_fluent/ewf_absorber.py` and `PyAnsys/scripts/setup/run_phase72a_ewf_absorber.py` |
|  | Version-matched source controls and variables are described in [Fluent 2025 R2 §30.5](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_ewf_sec_bound.html) and [supported expression variables §5.5](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_expressions_Appendix_fieldvars.html) |

</details>

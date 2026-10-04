# Phase 7.2A throughout-run monitoring contract

| Item | Phase 7.2A throughout-run monitoring contract |
| --- | --- |
| — | This contract applies to the R and E children and the matched R0/E0 control copy |
|  | Reports must be created and verified before solving, written during the solve, and read incrementally from native iteration coordinates |
| Endpoint-only reconstruction | is not sufficient |

## Every 10 native iterations or finer

| Item | Every 10 native iterations or finer |
| --- | --- |
| — | Record the following in durable report files: |
|  | liquid and steam inlet commands and realized phase-resolved inlet fluxes; |
|  | `P71V2Command`, native applied phase-2 absorber removal, command error, and direct phase-1 source audit; |
|  | total liquid mass and volume, vapor inventory where available, and lower- zone liquid mass, volume, and available-liquid diagnostic; |
|  | phase-1, phase-2, and mixture flux through `steamoutlet`, with the sign convention stated explicitly; |

<details>
<summary>Supporting detail — Every 10 native iterations or finer</summary>

| Item | Every 10 native iterations or finer |
| --- | --- |
| — | source-inclusive phase and mixture closure, including finite-difference storage while the field is moving; |
|  | continuity, momentum, volume-fraction, `k`, and `epsilon` residuals; |
|  | reverse-flow face counts, turbulent-viscosity limiting, AMG/FPE/nonfinite/ fatal warnings, and other solver-health events; and |
|  | elapsed block time and report-readback status |
| Family-specific | records are mandatory in the same stream: |
| R | wall-zone roughness settings/readback, outer-wall liquid vertical velocity with fixed sign convention, wall-adjacent phase fraction/velocity evidence, and any lower-region delivery/discharge measure exposed by Fluent |
| E | EWF enabled state/readback, film mass/inventory, film flow toward the lower region, bulk-to-film accretion, film-to-bulk transfer, and wall-film phase/velocity evidence wherever Fluent exposes them |
|  | Missing film transfer evidence is an evidence gap, not permission to infer drainage |

</details>

## Checkpoints

| Checkpoints |
| --- |
| At active offsets `0`, `250`, `500`, `750`, and `1,000`, preserve: |
| paired case/data checkpoint on the Fluent-local run disk; |
| current native monitor snapshot and residual snapshot; |
| settings and family-delta readback; |
| transcript tail and solver-event ledger; and |
| the current plot bundle |
| At the first discontinuity or failure, preserve the first event iteration, last valid monitor row, last valid checkpoint, transcript, and readback |
| Do not hide an event by changing the family delta or restarting from an unrecorded state |

## Live figures

| Live figures |
| --- |
| Refresh plots throughout the run, at least every `50–100` native iterations, from the report files themselves |
| The minimum figure set is: |
| liquid carryover through `steamoutlet` (phase 2) against the R0 control; |
| total and lower-zone liquid inventory; |
| absorber command versus native applied removal and command error; |

<details>
<summary>Supporting detail — Live figures</summary>

| Live figures |
| --- |
| phase-resolved outlet fluxes and source-inclusive closure/storage; |
| residuals with reverse-flow and viscosity-limit/event markers; and |
| a compact run-health panel |
| For EWF, add film inventory and film transfer/flow figures |
| For roughness, add outer-wall liquid vertical velocity and the wall-setting readback |
| Use matched native windows and do not pool warm-up or parent history into the child statistics |

</details>

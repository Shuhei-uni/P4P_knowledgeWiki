| Item | Record |
| --- | --- |
| Retired source | Setups/past/reported/010V2d-2-ewf-combined-global-dpm.md |

# Setup 010V2d-2 — Combined EWF with Global DPM Interaction

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2d-2` |
| Lifecycle | `reported` |
| Role | global-DPM coupling sensitivity after combined EWF mechanisms |
| Parent setup | accepted [010V2d](../purnanto-010V2d-ewf-combined-mechanisms/setup.md) |
| Controlled change | global `DPM Interaction with Continuous Phase` only |
| DPM allocation | historical `5%` total DPM mass with the inherited six-bin PSD |
| Future PSD basis | [project fine-mist DPM size and mass distribution](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md) |
| Evidence-use label | diagnostic until carrier-source and film mass balances close |
| Outcome | needs follow-up |
| Linked report | [diagnostic results](results.md) |

## Objective

| Objective |
| --- |
| Determine how enabling global DPM source interaction changes the accepted combined EWF case |
| This branch must be created from a stable, mass-reconciled `010V2d` case and must not be used to rescue an unstable isolated mechanism |

## Inherited setup

| Item | Inherited setup |
| --- | --- |
| — | Keep identical to the accepted `010V2d` case: |
|  | EWF wall, film material, wall condition, fixed transient controls, and film solution settings; |
|  | accepted subset of splash, edge separation, and particle stripping; |
|  | six original legacy-distribution injections and any Fluent-generated separation/stripping injection; |
| corrected DPM tracking controls | unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000`; |
| — | all inlet, outlet, phase, material, mesh, and wall settings |

## Controlled change

| Controlled change |
| --- |
| Change only: |

| Setting | `010V2d-2` value |
|---|---|
| Global `DPM Interaction with Continuous Phase` | `On` |
| Update DPM sources every flow iteration | retain parent value (`On`) |
| DPM iteration interval | retain parent value (`1`) |

| Controlled change |
| --- |
| Do not change the EWF mechanism settings, fixed flow timestep, DPM tracking correction, or wall-film settings in this branch |

## Droplet-distribution applicability

| Droplet-distribution applicability |
| --- |
| The existing `010V2d-2` case and its linked results use the historical `09cV2` allocation: |

```text
f_DPM = 5%
m_DPM = 5.846 kg/s
m_Eulerian_liquid = 111.074 kg/s
```

| Item | Droplet-distribution applicability |
| --- | --- |
| — | with the inherited six-bin PSD dominated by the `348.88 µm` class |
| These results | remain valid as a legacy-distribution global-interaction diagnostic |
| — | They must not be re-labelled as using the new fine-mist distribution |
|  | For the future PSD comparison: |
|  | create a new child case from the same accepted/matured carrier and EWF state; |

<details>
<summary>Supporting detail — Droplet-distribution applicability</summary>

| Item | Droplet-distribution applicability |
| --- | --- |
| — | keep `f_DPM = 5%`, `m_DPM = 5.846 kg/s`, and `m_Eulerian_liquid = 111.074 kg/s`; |
|  | keep global DPM interaction, source-update interval, EWF mechanisms, materials, wall conditions, tracking controls, mesh, and numerics unchanged; |
|  | replace only the original injection diameters and relative mass weights with the seven-class `5-100 µm` project baseline; |
|  | record the PSD identity in the case name and report |
|  | The resulting comparison isolates whether the historical film loading and removal efficiency were strongly affected by assigning most DPM mass to a coarse `348.88 µm` class |
|  | See: |
|  | [Project fine-mist DPM size and mass distribution](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md) |
|  | [Detailed geothermal fine-mist cutoff evidence](../../../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md) |
|  | [09cV2 partition and historical PSD definition](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV2-dpm-partition-control/setup.md) |

</details>

## Click-by-click procedure

| Item | Click-by-click procedure |
| --- | --- |
| — | Open the accepted/read-back-verified `010V2d` case/data pair |
|  | Save as `010V2d-2-ewf-combined-global-dpm.cas.h5` and its corresponding data checkpoint |
|  | Go to `Models > Discrete Phase > Interaction` |
|  | Enable `Interaction with Continuous Phase` |
|  | Retain source updates every flow iteration and iteration interval `1` |

<details>
<summary>Supporting detail — Click-by-click procedure</summary>

| Item | Click-by-click procedure |
| --- | --- |
| — | Reopen the panel and read back all three interaction settings |
| Confirm the EWF mechanism flags and generated injection identities | are unchanged from `010V2d` |
| Confirm the case | records its active PSD identity as `legacy-six-bin` for the historical branch |
| — | Save the case/data checkpoint before running |
|  | Run only after the parent combined case has passed its stability and mass-closure gate |

</details>

## Required comparison outputs

| Required comparison outputs |
| --- |
| carrier phase source terms and continuity imbalance versus `010V2d`; |
| direct DPM-to-carrier mass and momentum source totals; |
| film storage, film outflow, splash mass, separated mass, and stripped mass; |
| original and generated-particle fates; |
| film CFL, residuals, maximum film thickness, and total liquid closure; |
| active PSD identity and per-size injected mass flow |

## Acceptance gate

| Acceptance gate |
| --- |
| Keep `010V2d-2` diagnostic unless the difference from `010V2d` can be attributed to global DPM source interaction without an unbounded film inventory, unexplained carrier imbalance, or floating-point failure |
| Do not combine conclusions from a future fine-mist child case with the historical six-bin result unless the PSD change is explicitly identified as an additional controlled variable |

## Linked evidence

| Linked evidence |
| --- |
| [Project fine-mist DPM size and mass distribution](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV3-fine-mist-psd/fine-mist-interpretation.md) |
| [Detailed geothermal fine-mist cutoff evidence](../../../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md) |
| [09cV2 partition setup](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV2-dpm-partition-control/setup.md) |
| [010V2d parent](../purnanto-010V2d-ewf-combined-mechanisms/setup.md) |
| [010V2 control](../purnanto-010V2-clean-ewf-deposition/setup.md) |

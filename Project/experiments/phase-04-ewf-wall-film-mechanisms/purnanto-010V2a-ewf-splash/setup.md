| Item | Record |
| --- | --- |
| Retired source | Setups/past/reported/010V2a-ewf-splash.md |

# Setup 010V2a — EWF Splash Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2a` |
| Lifecycle | `reported` |
| Role | splash-only EWF sensitivity |
| Parent setup | [010V2 clean deposition control](../purnanto-010V2-clean-ewf-deposition/setup.md) |
| Controlled change | particle splashing only |
| Evidence-use label | diagnostic until splashed-mass balance closes |
| Outcome | needs follow-up |
| Linked report | [010V2a diagnostic results](results.md) |

## Objective

| Objective |
| --- |
| Test whether DPM impacts on the `010V2` wall film create secondary splashed parcels, without enabling edge separation or particle stripping |
| This branch may only start from a stable, read-back-verified `010V2` film baseline |
| It must not start from the failed `10a` checkpoint or from a zero-film initialization with splash enabled |
| Retain the `010V2` intentional fixed transient controls and global DPM interaction `Off` |
| Before execution, apply the parent DPM correction: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000` |

## Click-by-click procedure

| Item | Click-by-click procedure |
| --- | --- |
| — | Open the accepted/read-back-verified `010V2` case/data pair |
|  | Save as `010V2a-ewf-splash.cas.h5` and `010V2a-ewf-splash.dat.h5` |
|  | Go to `Models > Eulerian Wall Film > Edit` |
|  | In the DPM Interaction section, change `Particle Splashing` from `Off` to `On` |
|  | Keep `DPM Coupling = On` and all film momentum settings unchanged |

<details>
<summary>Supporting detail — Click-by-click procedure</summary>

| Item | Click-by-click procedure |
| --- | --- |
| — | Go to `Models > Discrete Phase > Interaction` and confirm global `DPM Interaction with Continuous Phase = Off` |
|  | Go to `Boundary Conditions` and select each confirmed EWF wall |
|  | Open the `Wall Film` tab |
|  | Enable `DPM Wall Splash` |
|  | Leave the Fluent default number of splashed particles for the first run; record the actual readback |
|  | Leave `Edge Separation`, `Particle Stripping`, and `Source Smoothing` off |
|  | Confirm the impingement model and record it; do not change it in this branch |
|  | Reopen the EWF and wall panels and verify the splash state |
| Initialize only if the EWF variables | were invalidated by the setting change; preserve the parent carrier field where possible |
| — | Run a `5-10` step smoke test with the inherited fixed `010V2` transient controls |
|  | If film CFL, source terms, or residuals spike, stop and return to the clean `010V2` parent; do not classify the floating-point failure as splash physics |
|  | If stable, run the same transient budget and averaging window as `010V2` |
|  | Save a new checkpoint |

</details>

## Required outputs

| Required outputs |
| --- |
| original injected DPM mass; |
| absorbed mass; |
| splashed parcel count and represented splashed mass; |
| escaped, trapped, and incomplete original-particle fates; |
| film inventory, film outflow, and film thickness; |
| residuals, film CFL history, global DPM interaction state, and phase-flux imbalance |
| Do not combine Fluent splash event counts with original injected-particle counts without accounting for secondary parcels |

## Acceptance gate

| Acceptance gate |
| --- |
| Keep this branch diagnostic unless splashed mass can be distinguished from direct escape, film storage, film outflow, and original DPM absorption, with no unbounded film-CFL/source spike |

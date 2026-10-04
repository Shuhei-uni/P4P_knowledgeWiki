| Item | Record |
| --- | --- |
| Retired source | Setups/past/reported/010V2c-ewf-particle-stripping.md |

# Setup 010V2c — EWF Particle-Stripping Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2c` |
| Lifecycle | `reported` |
| Role | particle-stripping-only EWF sensitivity |
| Parent setup | [010V2 clean deposition control](../purnanto-010V2-clean-ewf-deposition/setup.md) |
| Controlled change | particle stripping only |
| Evidence-use label | diagnostic until stripped-mass balance closes |
| Outcome | needs follow-up |
| Linked report | [010V2c diagnostic results](results.md) |

## Objective

| Item | Objective |
| --- | --- |
| — | Test whether carrier shear strips droplets from an existing EWF film under the separator flow conditions |
| Stripping | is a post-formation mechanism in this project |
| It must not be enabled while the film | is still zero, while the film inventory is unbounded, or on the failed `10a` checkpoint |
| — | Start from a stable `010V2` film field, retain the parent intentional fixed transient controls, and keep global DPM interaction `Off` |
|  | Before execution, apply the parent DPM correction: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000` |

## Click-by-click procedure

| Click-by-click procedure |
| --- |
| Open the accepted/read-back-verified `010V2` case/data pair |
| Save as `010V2c-ewf-particle-stripping.cas.h5` and `010V2c-ewf-particle-stripping.dat.h5` |
| Go to `Models > Eulerian Wall Film > Edit` |
| Confirm `Particle Splashing = Off` |
| Confirm `Edge Separation = Off` |

<details>
<summary>Supporting detail — Click-by-click procedure</summary>

| Click-by-click procedure |
| --- |
| Enable `Particle Stripping` |
| Leave `Critical Shear Stress`, `Diameter Coefficient`, and `Mass Coefficient` at Fluent defaults for the first diagnostic; record their readback |
| Keep `DPM Coupling = On`, `Surface Shear Force = On`, and `Flow Momentum Coupling = Off` as inherited from `010V2` |
| Confirm global `DPM Interaction with Continuous Phase = Off` as inherited from the intentional `010V2` configuration |
| Go to `Boundary Conditions` and verify that every selected EWF wall has the intended wall-film condition |
| Confirm a finite, bounded film inventory exists in the parent before enabling stripping; do not judge stripping from a zero-film initialization |
| Check `Models > Discrete Phase > Injections` for the automatically created stripping injection |
| Verify the generated injection material matches the film material and record its name, diameter, and source |
| Reopen the EWF panel and record all stripping parameters |
| Initialize only if required by the setting change; preserve the parent film field |
| Run a `5-10` step smoke test with the inherited fixed `010V2` transient controls |
| If film CFL, source terms, or residuals spike, stop and return to the clean `010V2` parent; do not classify the floating-point failure as stripping physics |
| If stable, run the same transient budget as `010V2` |
| Save a separate case/data checkpoint |

</details>

## Required outputs

| Item | Required outputs |
| --- | --- |
| — | film inventory and film shear-related variables; |
|  | `Film Stripped Mass`; |
|  | generated stripping injection flow and particle count; |
|  | direct DPM escape, generated-particle escape, film outflow, and film storage; |
|  | residuals, film Courant behavior, global DPM interaction state, and phase-flux balance |
| If stripping | remains zero, report whether the cause is insufficient film, insufficient shear, or the default threshold—not simply “stripping failed.” If the run diverges, report the film CFL/source history and return to `010V2` before changing stripping thresholds |

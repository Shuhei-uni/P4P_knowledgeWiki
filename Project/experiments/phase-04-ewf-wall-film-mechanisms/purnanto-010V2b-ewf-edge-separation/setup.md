| Item | Record |
| --- | --- |
| Retired source | Setups/past/reported/010V2b-ewf-edge-separation.md |

# Setup 010V2b — EWF Edge-Separation Sensitivity

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2b` |
| Lifecycle | `reported` |
| Role | edge-separation-only EWF sensitivity |
| Parent setup | [010V2 clean deposition control](../purnanto-010V2-clean-ewf-deposition/setup.md) |
| Controlled change | edge separation only |
| Evidence-use label | diagnostic until generated-particle mass is reported |
| Outcome | needs follow-up |
| Linked report | [010V2b partial diagnostic results](results.md) |

## Objective

| Objective |
| --- |
| Test whether the wall film separates at confirmed geometric film-wall edges and generates DPM parcels |
| This branch may only start after the clean `010V2` parent has developed a finite, bounded film at the intended edge |
| Retain the parent intentional fixed transient controls and global DPM interaction `Off` |
| Before execution, apply the parent DPM correction: unsteady tracking off, no `0.001 s` particle-time-step override, and maximum particle steps `10000` |
| Do not enable edge separation on the failed `10a` state or during the initial zero-film transient |

## Click-by-click procedure

| Item | Click-by-click procedure |
| --- | --- |
| — | Open the accepted/read-back-verified `010V2` case/data pair |
|  | Save as `010V2b-ewf-edge-separation.cas.h5` and `010V2b-ewf-edge-separation.dat.h5` |
|  | Go to `Models > Eulerian Wall Film > Edit` |
|  | Confirm `Particle Splashing = Off` |
|  | Confirm `Particle Stripping = Off` |

<details>
<summary>Supporting detail — Click-by-click procedure</summary>

| Item | Click-by-click procedure |
| --- | --- |
| — | Enable `Edge Separation` |
|  | Leave `Critical Weber Number`, `Critical Angle`, and `Separation Model` at Fluent defaults for the first diagnostic, unless a project-specified value is already documented |
| Keep `Random Separation = Off` initially so the first result | is deterministic |
| — | Go to `Models > Discrete Phase > Interaction` and confirm global `DPM Interaction with Continuous Phase = Off` |
|  | Go to `Boundary Conditions` and inspect every EWF wall edge |
| Confirm the intended edge | is a real film-wall edge and is not an accidental mesh/domain boundary |
| — | Confirm the film reaches that edge in the `010V2` parent result |
|  | Reopen the EWF panel and record every separation parameter after Fluent applies defaults |
|  | Check `Models > Discrete Phase > Injections` for an automatically created separation injection, typically named with an EWF strip/separation identity |
|  | Verify its material, diameter, source surface, and flow-rate readback; do not manually add a duplicate injection |
|  | Initialize only if required by the setting change; preserve the finite parent film field |
|  | Run a `5-10` step smoke test with the inherited fixed `010V2` transient controls |
|  | If film CFL, source terms, or residuals spike, stop and return to the clean `010V2` parent before interpreting separation |
|  | If stable, run the same transient budget as `010V2` |
|  | Save a separate case/data checkpoint |

</details>

## Required outputs

| Item | Required outputs |
| --- | --- |
| — | film mass arriving at the edge; |
|  | separated DPM parcel count and represented mass; |
|  | separation injection identity and material; |
|  | film outflow and remaining inventory; |
|  | direct DPM escape versus generated-particle escape; |
|  | residuals, film CFL history, global DPM interaction state, and phase-flux balance |
| If no particles | are generated, first check film presence, edge connectivity, and local Weber/impact conditions |
| — | Do not tune thresholds until those checks pass |

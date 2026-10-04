| Item | Record |
| --- | --- |
| Retired source | Setups/past/reported/010V2-ewf-deposition-film-inventory.md |

# Setup 010V2 — EWF Deposition and Film-Inventory Control

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `010V2` |
| Lifecycle | `reported` |
| Role | clean EWF deposition/drainage stability control |
| Parent setup | [09cV2](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV2-dpm-partition-control/setup.md) |
| Child setups | [010V2a splash](../purnanto-010V2a-ewf-splash/setup.md), [010V2b edge separation](../purnanto-010V2b-ewf-edge-separation/setup.md), [010V2c stripping](../purnanto-010V2c-ewf-particle-stripping/setup.md), [010V2d combined](../purnanto-010V2d-ewf-combined-mechanisms/setup.md), [010V2d-2 coupled combined](../purnanto-010V2d-2-ewf-global-dpm/setup.md) |
| Controlled changes | EWF model, EWF wall coupling, transient film solution, wall-film boundary condition, staged global-DPM source coupling |
| Evidence-use label | diagnostic until film mass balance and carrier gates pass |
| Outcome | needs follow-up |
| Linked report | [010V2 diagnostic results](results.md) |

## 1. Objective

| Item | Objective |
| --- | --- |
| — | Determine whether the Skoog-style allocated DPM population deposits into a bounded Eulerian wall film and drains without enabling splash, edge separation, or particle stripping |
| This | is the clean control for all later `010V2` interaction branches |
| The first execution is an EWF stability baseline | EWF-DPM coupling is enabled so injected droplets can deposit into the film, while global `DPM Interaction with Continuous Phase` is disabled |
|  | The resulting film behavior is the uncoupled global-DPM control; `010V2d-2` is reserved for the corresponding combined case with global DPM interaction enabled |

## 2. Inherited setup

| Inherited setup |
| --- |
| Start from a saved, read-back-verified `09cV2` case/data pair |
| Do not start from the existing `10a` artifact because it is splash-enabled and uses the old branch identity |
| Keep unchanged: |
| geometry, mesh, split inlet topology, outlet boundaries, gravity, operating pressure; |
| `Mixture`, phase definitions, carrier materials, `RNG k-epsilon`, Energy off; |

<details>
<summary>Supporting detail — Inherited setup</summary>

| Inherited setup |
| --- |
| the `09cV2` liquid/DPM allocation and EWF-compatible DPM material names; |
| injection diameters, flows, velocities, particle count, drag, rotation, and stochastic settings; |
| DPM outlet and ordinary-wall fates unless the wall must be changed to `wall-film` for coupling |
| Do not inherit the failed `10a` data field, its `water-liquid` DPM material, or its splash/stripping state |

</details>

### Intentional live-case controls and the single DPM correction

| Item | Intentional live-case controls and the single DPM correction |
| --- | --- |
| — | The server-4 readback confirmed that the other deviations from the provisional plan are intentional for this execution |
|  | Preserve the configured EWF options, fixed transient controls, `water-liquid-at-psep` / `water-liquid-at-psep-dpm` material identities and properties, global-DPM state, and `reflect` wall fate as currently set |
| global-DPM branch rule | is explicit: `010V2` and `010V2a`–`010V2d` use `Off`; only `010V2d-2` turns it `On` |
| — | The only DPM tracking items requiring correction before execution are: |
|  | disable `Unsteady Particle Tracking`; |

<details>
<summary>Supporting detail — Intentional live-case controls and the single DPM correction</summary>

| Item | Intentional live-case controls and the single DPM correction |
| --- | --- |
| — | remove the `0.001 s` particle-time-step override and return to the inherited parent tracking mode; |
|  | restore `Maximum Number of Steps` from `500` to `10000` |
| These three items | are the exception to the otherwise intentional live-case configuration |
| same correction | is inherited by `010V2a`–`010V2d` |

</details>

## 3. EWF model settings

| Fluent setting | First `010V2` value |
|---|---|
| Eulerian Wall Film | `On` |
| Solve Momentum | `On` |
| Momentum method | `Momentum Equation` |
| Gravity Force | `On` |
| Surface Shear Force | `On` |
| Pressure Gradient | `On` if available; record readback |
| Spreading Term | `Off` |
| Surface Tension | `Off` initially |
| Solve Energy | `Off` |
| Solve Scalar | `Off` |
| Film Material | existing `water-liquid-at-psep` or verified project film material |
| DPM Coupling | `On` |
| Global DPM Interaction with Continuous Phase | `Off` for `010V2` and `010V2a`–`010V2d` |
| Phase Coupling / VOF Coupling | `Off` for this first control |
| Treat Sharp Edge | `Off` |
| Particle Splashing | `Off` |
| Edge Separation | `Off` |
| Particle Stripping | `Off` |
| Flow Momentum Coupling at wall | `Off` initially |
| EWF time stepping | retain the intentional fixed transient control |
| Flow time-step control | `1.0e-5 s`, `40` configured steps, `1` iteration per step |
| Max Courant Number | `0.5` (`Assumed` conservative starting value if exposed; record readback) |
| Film step increase/decrease factors | Fluent defaults; record readback and confirm both are greater than `1` |
| Per Flow Iterations | `1` in the intentional live-case configuration |
| DPM per Film Steps | `20` initial readback; retain for the first control |
| EWF DPM Relaxation Factor | `0.5` (`Assumed` conservative starting value) |

| Item | EWF model settings |
| --- | --- |
| — | The referenced server-2 `10a` failure analysis reported a film CFL of approximately `679` at the second film step with a `0.01 s` film time step |
| That run | is not a calibration of a required physical film timestep |
| — | For this configured branch, retain the intentional fixed `1.0e-5 s` flow timestep and monitor film CFL/source spikes |
|  | Do not change the global DPM interaction state or increase the flow timestep after a divergence without creating a separately documented sensitivity |

## 4. Click-by-click build procedure

### A. Save the `09cV2` parent

| A. Save the `09cV2` parent |
| --- |
| Open the read-back-verified `09cV2` case/data pair |
| Go to `File > Save Case/Data As` |
| Save as `010V2-ewf-deposition-control.cas.h5` and `010V2-ewf-deposition-control.dat.h5` |
| Preserve the `09cV2` case/data pair separately |

### B. Enable and configure EWF

| Item | B. Enable and configure EWF |
| --- | --- |
| — | Go to `Models > Eulerian Wall Film > Edit` |
|  | Enable `Eulerian Wall Film` |
|  | Set `Solve Momentum = On` |
|  | Select `Momentum Equation` |
|  | Enable `Gravity Force` |

<details>
<summary>Supporting detail — B. Enable and configure EWF</summary>

| Item | B. Enable and configure EWF |
| --- | --- |
| — | Enable `Surface Shear Force` |
|  | Enable `Pressure Gradient` if the active Fluent panel exposes it; record whether it was available |
|  | Leave `Spreading Term` and `Surface Tension` off |
|  | Leave `Solve Energy` and `Solve Scalar` off |
|  | Select the verified project film material |
|  | Enable `DPM Coupling` |
|  | Leave `Phase Coupling`, `VOF Coupling`, and `Treat Sharp Edge` off |
| Confirm `Particle Splashing`, `Edge Separation`, and `Particle Stripping` | are off |
| — | Click `Apply`/`OK` |

</details>

### C. Assign the EWF wall

| Item | C. Assign the EWF wall |
| --- | --- |
| — | Go to `Boundary Conditions` |
|  | Select the confirmed physical liquid-impact wall zone, initially `wall` only |
|  | Open the `Wall Film` tab |
|  | Select the Eulerian wall-film condition |
|  | Set initial film height to `0 m` |

<details>
<summary>Supporting detail — C. Assign the EWF wall</summary>

| Item | C. Assign the EWF wall |
| --- | --- |
| — | Set initial film velocity to `0 m/s` in every component |
|  | Set `Flow Momentum Coupling = Off` |
|  | Set the DPM wall interaction to the standard `wall-film`/impingement path, not `trap` or ordinary `reflect` |
|  | Leave wall splash off |
| Confirm `bottom` | is not accidentally assigned as an EWF wall unless its role is intentionally part of the film path |
| — | Inspect every film-wall edge |
|  | Confirm it connects to another film wall or to an intentional drain/outflow edge |
|  | Click `Apply` and reopen the wall panel to verify the readback |

</details>

### D. Check material/injection compatibility

| D. Check material/injection compatibility |
| --- |
| Go to `Models > Eulerian Wall Film` and record the exact film-material name |
| Go to `Models > Discrete Phase > Injections` |
| Confirm every EWF-coupled injection material has the same relevant properties as the film material |
| Confirm the injection names contain the film-material name |
| Confirm all six flows sum to the selected `09cV2` DPM total for the case being built; do not assume `5.846 kg/s` unless the selected fraction is explicitly `5%` |
| If any material/name check fails, stop before initializing |
| Correct the material identity and record the change |

### E. Set transient film solution controls

| Item | E. Set transient film solution controls |
| --- | --- |
| — | Go to `General` and change `Time` from `Steady` to `Transient` |
|  | Go to `Solution Methods` |
|  | Set transient time discretization to `First Order Implicit` |
|  | Keep the carrier equations at the accepted parent schemes |
|  | In the EWF `Solution Method and Control` tab, set the wall-film continuity and momentum schemes to the most conservative first-order option exposed by the active Fluent release |

<details>
<summary>Supporting detail — E. Set transient film solution controls</summary>

| Item | E. Set transient film solution controls |
| --- | --- |
| — | Keep `Coupled Solution` off for this first control |
| Under `Time Marching and Time Step Control`, retain the intentional fixed transient control | `1.0e-5 s`, `40` steps, and `1` iteration per step |
| — | Do not enable adaptive time stepping for this configured branch unless it is created as a separate sensitivity |
|  | Set `Max Courant Number = 0.5` as the `Assumed` conservative starting value if the field is exposed |
|  | Leave the film-step increase/decrease factors at their Fluent defaults, confirm both are greater than `1`, and record all readbacks |
|  | Retain `Per Flow Iterations = 1`, `Reporting Interval = 1`, `Sub-Iteration Stop = 1e-8`, `Sub-Iterations = 10`, and sub-iteration `Reporting Interval = 1` unless a separate numerical sensitivity is documented |
|  | In `DPM Control`, set `Relaxation Factor = 0.5` as the `Assumed` conservative starting value and retain `DPM per Film Steps = 20` for the first control |
|  | Do not search the general `Solution Controls` panel for a film-specific relaxation factor; the relevant EWF controls are in `Solution Method and Control` |
|  | Keep global `DPM Interaction with Continuous Phase = Off` for `010V2` and `010V2a`–`010V2d`; enable it only in the separately named `010V2d-2` branch |
|  | Do not copy Skoog's BWR time step as a project default |
|  | If film CFL or source terms spike, preserve the checkpoint before changing the fixed flow timestep |

</details>

### F. Initialize the film and run

| Item | F. Initialize the film and run |
| --- | --- |
| — | Save the case before initialization |
|  | Go to `Solution > Initialization` |
|  | Initialize the carrier field using the inherited parent data if valid; otherwise use `Hybrid Initialization` and record the fallback |
|  | Go to `Models > Eulerian Wall Film` and click `Initialize` for wall-film variables |
| Confirm the initial film height and velocity | are zero on the selected wall |

<details>
<summary>Supporting detail — F. Initialize the film and run</summary>

| Item | F. Initialize the film and run |
| --- | --- |
| — | Run `5-10` transient time steps as a first smoke test |
|  | Monitor continuity, phase fraction, `k`, epsilon, film Courant number, film mass, film source terms, and DPM-to-film mass transfer after every step |
|  | If film CFL or source terms spike, stop and preserve the checkpoint before changing the fixed flow timestep; do not interpret a floating-point exception as a mechanism result |
|  | If stable, continue to `20-50` transient time steps and then to a documented averaging window after film inventory has developed |
|  | Save case/data checkpoints without overwriting `09cV2` |

</details>

## 5. Required monitors and reports

| Item | Required monitors and reports |
| --- | --- |
| — | Create or record, where available: |
|  | area-weighted film thickness on each EWF wall; |
|  | film mass/inventory versus time; |
|  | film velocity and drainage direction; |
|  | `Film DPM Mass Source`; |

<details>
<summary>Supporting detail — Required monitors and reports</summary>

| Item | Required monitors and reports |
| --- | --- |
| — | `Film Outflow Mass`; |
| `Film Stripped Mass` and `Film Separated Mass`—both should | remain zero in this control; |
| — | steam-outlet liquid phase flux; |
|  | actual global DPM interaction state and EWF-DPM coupling state; |
|  | original DPM escaped, trapped, and incomplete counts; |
|  | residual history, film CFL history, maximum film thickness, and complete phase-flux imbalance |

</details>

## 6. Acceptance gate

| Item | Acceptance gate |
| --- | --- |
| `010V2` | is interpretable only if: |
| — | the film forms on the intended wall; |
|  | no unintended film-edge outlet removes unexplained mass; |
| film inventory | is bounded or its growth is explicitly explained by the inlet allocation; |
| DPM-to-film transfer, film outflow, storage, and remaining particle fates | are reported together; |

<details>
<summary>Supporting detail — Acceptance gate</summary>

| Item | Acceptance gate |
| --- | --- |
| splash, edge separation, and stripping | remain off; |
| — | no floating-point exception or unbounded film-CFL/source spike occurs during the smoke test; |
| the configured global DPM interaction state | is recorded as `Off` for `010V2` and `010V2a`–`010V2d`, with `On` reserved for `010V2d-2`; |
| the carrier phase balance and continuity limitations | are visible in the report |

</details>

## Linked evidence

| Item | Linked evidence |
| --- | --- |
| — | [09cV2 parent](../../phase-03-dpm-carryover-and-coupling/purnanto-09cV2-dpm-partition-control/setup.md) |
|  | [Project Skoog guardrails](../../../technical/skoog-application-guardrails.md) |
|  | [Fluent EWF guidance](../../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md) |
| 10a server-2 live failure readback (historical machine artifact path | `../../../PyAnsys/output/live_postprocess_20260721/10a-server2-stripping-live-report.md`; not migrated) |
| — | [Existing 10a splash-enabled diagnostic](../purnanto-10a-splash-ewf-preliminary/setup.md) |

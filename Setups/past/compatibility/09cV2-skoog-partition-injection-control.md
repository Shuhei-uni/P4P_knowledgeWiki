# Setup 09cV2 — Skoog Partition and Injection-Control Branch

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `09cV2` |
| Lifecycle | `reported` |
| Role | Skoog-aligned allocation and injection-control experiment |
| Parent setup | [09c — two-way DPM coupling](09c-dpm-ewf-wall-film-reentrainment.md) |
| Child setups | [09cV3 — fine-mist 5% DPM PSD rerun](../../active/09cV3-fine-mist-5pct-psd-rerun.md); [010V2](010V2-ewf-deposition-film-inventory.md) |
| Controlled changes | liquid/DPM mass partition, EWF-ready DPM material identity, scaled DPM loading, failure-informed source-balance checks |
| Droplet-size basis | historical six-bin distribution for completed cases; future PSD reruns use the [project fine-mist baseline](../../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md) |
| Evidence-use label | setup calculation only until carrier and liquid balance gates pass |
| Outcome | needs follow-up |
| Linked report | [09cV2 diagnostic results](../../reports/purnanto-reference/09cV2/results.md) |

## 1. Objective

Create a mass-consistent Skoog-style inlet partition before adding Eulerian Wall Film physics.

The branch tests whether the two-way DPM calculation can run with DPM representing a declared fraction of the total liquid feed rather than an additional copy of the full Purnanto liquid flow.

This is not yet a full Skoog three-field model. The existing project `Mixture` carrier model is retained so that the first comparison changes injection bookkeeping without also changing the global multiphase formulation.

## 2. Inherited setup

Start from a fresh copy of the best available `09c` case/data pair. Do not use the existing `10a` artifact as the parent because it was read back with splash enabled.

Inherit unchanged:

- Purnanto/purnantov2 geometry and inherited `08b`-family mesh;
- split `liquidinlet` / `steaminlet` topology;
- `steamoutlet` pressure outlet and existing DPM wall fates;
- `Mixture` model, phase definitions, `RNG k-epsilon`, Energy off, gravity, operating pressure, and accepted solver numerics;
- DPM `Interaction with Continuous Phase = On`;
- `Update DPM Sources Every Flow Iteration = On`;
- `DPM Iteration Interval = 1`;
- deterministic tracking, spherical drag, rotation off, stochastic dispersion off;
- the six existing diameter classes as the historical controlled-comparison basis.

The `09c` parent is not a converged reference. Preserve that limitation in the case name and run notes.

## 2A. Failure-informed starting rule

Do not use the failed server-2 `10a` case/data checkpoint as the parent for any `V2` branch. The live readback is `Debug only`: it had the full `116.920 kg/s` Eulerian liquid inlet, an active DPM total of `1.940 kg/s`, and a derived mass imbalance of approximately `2.61 × 10^65 kg/s`. The failure is evidence of a divergent coupled setup, not evidence that stripping or another EWF mechanism produced a physical result.

Build `09cV2` from a fresh, read-back-verified `09c` case/data pair or a clean carrier checkpoint. Before moving to EWF, verify that the selected DPM fraction reduces the Eulerian liquid contribution and that the DPM material is not still the unmatched `water-liquid` material from the failed `10a` run.

## 3. DPM-fraction evidence and selection rule

The project reference is `116.92 kg/s` liquid and `80.69 kg/s` vapor. The DPM fraction must be treated as a parameter, not as a known property of the geothermal separator inlet.

The earlier `5%` value is not a project default and is not literature-derived. It was only a numerical screening point. It must not be described as the measured or expected geothermal mist fraction.

| Evidence item | Status | Consequence for `09cV2` |
|---|---|---|
| Purnanto's `116.92 kg/s` | `Reported` total liquid/brine feed | It is the liquid accounting reference, not a DPM fraction. |
| Purnanto's approximately `10 µm` inlet droplet basis | `Reported` CFD input; not measured upstream truth | Retain the parent size basis only as a controlled comparison. |
| Harwell's approximately `5% <= 0.3 x_med` statement | `Reported` size-distribution fraction | Do not reinterpret it as 5% of liquid mass. |
| Skoog's `d_frac` scan and deposition/entrainment balance | `Reported` method | Prefer a calculated fraction where the required inputs and correlations are available. |
| Geothermal separator inlet droplet PSD and concentration | `Missing` from the current evidence set | A single physical DPM fraction cannot be claimed. |
| Takahashi's `20-30 µm` minimum trapped droplet size | `Reported` capture-performance result; no inlet mass fraction | It is not a basis for choosing `f_DPM`. |
| Rivera-Diaz and Koorey's statement that droplet distribution is unknown | `Reported` | Use sensitivity analysis until an inlet distribution is measured or defensibly inferred. |

### Required selection rule before simulation

1. Define `f_DPM` explicitly for every case and calculate:

   ```text
   m_DPM = f_DPM × 116.92 kg/s
   m_Eulerian_liquid = (1 − f_DPM) × 116.92 kg/s
   ```

2. If a Skoog/1-D calculation is available, scan the candidate droplet/film split, calculate deposition and entrainment for each point, and select the point where the two rates are acceptably balanced. Label the resulting fraction `Inferred`, record the inputs/correlation, and still retain a nearby sensitivity case.
3. If the Skoog/1-D calculation cannot be closed because onset, film, or property inputs are missing, run the sensitivity matrix below. The matrix is a bracketing experiment, not a claim that any row is physically correct.
4. Keep the six-bin relative weights from `09c` unchanged during the historical fraction study so that fraction and size-distribution effects are not changed simultaneously.
5. For the next PSD comparison, keep the chosen `f_DPM`, total DPM mass, complementary Eulerian-liquid flow, mesh, carrier checkpoint, coupling, and numerics fixed; change only the injection diameters and relative mass weights according to the [fine-mist DPM decision](../../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md).

### Pre-simulation fraction matrix

| Case point | `f_DPM` | DPM total | Eulerian liquid | Use |
|---|---:|---:|---:|---|
| Control | `0%` | `0.000 kg/s` | `116.920 kg/s` | Carrier/EWF baseline; no DPM loading claim |
| Low | `1%` | `1.169 kg/s` | `115.751 kg/s` | Low-loading sensitivity |
| Earlier screen | `5%` | `5.846 kg/s` | `111.074 kg/s` | Retain only as a mid-range sensitivity point |
| Upper sensitivity | `10%` | `11.692 kg/s` | `105.228 kg/s` | Loading sensitivity |
| Parent-loading comparison | `25%` | `29.230 kg/s` | `87.690 kg/s` | Approximately matches the existing `09c` DPM total of `29.22 kg/s`; diagnostic only |

The first recommended execution set is `0%`, `1%`, `5%`, `10%`, and `25%`. A Skoog-calculated point can be added after the one-dimensional balance is closed. These are parameter points under `09cV2`, not new stable setup IDs.

### Historical 5% sensitivity point

For traceability, the earlier 5% point is retained below. It is an `Assumed`, medium-risk sensitivity case only:

```text
f_DPM = 0.05
m_DPM = 0.05 × 116.92 = 5.846 kg/s
m_Eulerian_liquid = 116.92 − 5.846 = 111.074 kg/s
```

Scale the six active `09c` injections while preserving their existing relative weights:

| Diameter | `09c` flow | `09cV2` historical 5% flow |
|---:|---:|---:|
| `5.63 µm` | `0.19 kg/s` | `0.038013 kg/s` |
| `28.14 µm` | `0.78 kg/s` | `0.156053 kg/s` |
| `56.27 µm` | `0.97 kg/s` | `0.194066 kg/s` |
| `112.54 µm` | `1.95 kg/s` | `0.390133 kg/s` |
| `168.81 µm` | `1.95 kg/s` | `0.390133 kg/s` |
| `348.88 µm` | `23.38 kg/s` | `4.677600 kg/s` |
| **Total** | **`29.22 kg/s`** | **`5.846000 kg/s`** |

Do not call the six-bin distribution measured. This branch tested the mass-allocation correction while retaining the parent size basis.

### Droplet-size distribution status and future rerun

The completed `09cV2` and downstream EWF cases use the historical table above. Those results remain valid only as **legacy-distribution diagnostics**.

The recommended project baseline now represents steam-carried fine mist with seven classes from `5-100 µm`:

```text
7.07, 14.14, 24.49, 34.64, 48.99, 69.28, 89.44 µm
```

At the same `5%` total DPM loading, the recommended flows are:

| Diameter [µm] | Recommended 5% DPM flow [kg/s] |
|---:|---:|
| `7.07` | `0.409128` |
| `14.14` | `1.165149` |
| `24.49` | `1.267410` |
| `34.64` | `1.092501` |
| `48.99` | `1.329262` |
| `69.28` | `0.468606` |
| `89.44` | `0.113944` |
| **Total** | **`5.846000`** |

Do not silently modify an existing historical case. Create a new child/rerun, keep `m_DPM = 5.846 kg/s` and `m_Eulerian_liquid = 111.074 kg/s`, and change only the PSD for the first direct comparison. See:

- [Project fine-mist DPM size and mass distribution](../../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md)
- [Detailed geothermal fine-mist cutoff evidence](../../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md)

## 4. Click-by-click build procedure

### A. Save the parent safely

1. Open the `09c` case/data pair in Fluent.
2. Confirm the loaded case is the two-way DPM parent, not the splash-enabled `10a` artifact.
3. Go to `File > Save Case/Data As`.
4. Save a new pair using a name that records the selected fraction, for example:
   `09cV2-fDPM-05pct.cas.h5` and `09cV2-fDPM-05pct.dat.h5`.
5. Record the source case/data filenames, Fluent version, server, and iteration checkpoint.

### B. Audit the inherited carrier state

1. Go to `Boundary Conditions > liquidinlet`.
2. Open the phase-specific flow panel and record the current liquid flow.
3. Go to `Boundary Conditions > steaminlet` and record the vapor flow.
4. Confirm the starting values are approximately `116.92 kg/s` liquid and `80.69 kg/s` vapor.
5. Go to `Models > Multiphase` and confirm `Mixture` and the existing phase/material mapping.
6. Go to `Models > Discrete Phase` and record the interaction, update-source, iteration-interval, tracking, and injection settings before changing anything.

### C. Apply the liquid/DPM partition

1. Go to `Boundary Conditions > liquidinlet`.
2. Keep the boundary type, phase fractions, turbulence values, and direction unchanged.
3. Select the fraction row being executed and calculate `m_Eulerian_liquid` from the rule in Section 3. For the illustrative 5% point, change the liquid phase mass flow from `116.92 kg/s` to `111.074 kg/s`.
4. Leave the vapor flow at `80.69 kg/s`.
5. Click `Apply` and read back the actual boundary flux if the panel provides it.

This step prevents the DPM loading from being added to a full duplicate `116.92 kg/s` Eulerian liquid feed.

### D. Rebuild the historical DPM injection payload

The following procedure documents the existing six-injection case. Use the project fine-mist decision when creating a new PSD child case.

Repeat the following for each of the six existing injections:

1. Go to `Models > Discrete Phase > Injections`.
2. Select the injection by name and click `Edit`.
3. Keep the injection type `Surface` and the `steaminlet` surface for this first allocation-control branch.
4. Keep the diameter unchanged.
5. Keep the velocity direction and magnitude unchanged from `09c` so that mass allocation is the isolated change.
6. Change `Total Flow Rate` to the selected fraction's DPM total multiplied by the existing `09c` relative weight. For the historical 5% point, use the six values in the table above.
7. Keep particle count/streams, deterministic tracking, spherical drag, and stochastic settings unchanged.
8. Click `Change`/`Apply`, then reopen the injection and read the value back.
9. Repeat for all six injections.
10. Sum the read-back flow rates and confirm the DPM total for the selected fraction. For the historical 5% point, confirm `5.846 kg/s`.

### E. Prepare EWF-compatible material identity

This material preparation is required before `010V2`, even though EWF remains off in `09cV2`.

1. Go to `Materials` and identify the existing film material planned for EWF, expected to be `water-liquid-at-psep`.
2. Create a copied DPM material named `water-liquid-at-psep-dpm`.
3. Copy density, viscosity, surface-tension-relevant properties, and all other active particle properties from the intended film material.
4. Do not change the carrier phase material in this branch.
5. In each DPM injection, change the particle material to `water-liquid-at-psep-dpm`.
6. Rename each injection so the film material name is contained in the injection name, for example:
   - `water-liquid-at-psep-5um`
   - `water-liquid-at-psep-28um`
   - `water-liquid-at-psep-56um`
   - `water-liquid-at-psep-112um`
   - `water-liquid-at-psep-168um`
   - `water-liquid-at-psep-348um`
7. Reopen each injection and verify the name, material, diameter, surface, and flow rate.

Fluent requires matching film/injection properties and a material-name relationship when DPM coupling is used with EWF. Verify the exact 2024 R2 readback before relying on this branch ([Fluent EWF model options](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_ewf_sec_options.html)).

### F. Keep the parent coupling state for the first comparison

1. Go to `Models > Discrete Phase > Interaction`.
2. Confirm `Interaction with Continuous Phase = On`.
3. Confirm `Update DPM Sources Every Flow Iteration = On`.
4. Confirm `DPM Iteration Interval = 1`.
5. Do not enable EWF, particle splashing, edge separation, stripping, custom laws, or phase-change coupling in this branch.

### G. Initialize and run

1. Save the case/data pair.
2. If the parent data field is being reused, first preserve a copy of the original parent data.
3. Use `Solution > Initialization` and retain the parent initialization method unless the case is case-only.
4. If case-only, use `Hybrid Initialization` and record that the parent field was not reused.
5. Run a short smoke test of `20-50` iterations.
6. Check continuity, phase fraction, `k`, epsilon, inlet/outlet fluxes, and DPM source monitors.
7. If the smoke test is stable, continue using the parent run budget or a documented transient/steady budget.
8. Save a new checkpoint; never overwrite the `09c` parent.
9. Stop and preserve a debug checkpoint if the DPM source terms spike, the carrier mass balance opens, or the selected Eulerian-liquid plus DPM total no longer closes to the project liquid reference. Do not proceed to EWF to work around that failure.

## 5. Acceptance checks

Do not promote `09cV2` unless:

- actual Eulerian liquid plus the selected DPM flow is approximately `116.92 kg/s` at the inlet accounting level;
- vapor flow remains approximately `80.69 kg/s`;
- the selected `f_DPM` is recorded in the case name, setup notes, and run log;
- the active PSD identity is recorded as either `legacy-six-bin` or `fine-mist-5-100um`;
- DPM source terms do not create a new unexplained mass imbalance;
- continuity and phase-fraction residuals are reported;
- every active injection setting reads back correctly;
- the DPM material and selected fraction read back correctly and are not inherited from the failed `10a` material/loading state;
- escaped, trapped, and incomplete counts are recorded per injection;
- the result is labelled diagnostic if the carrier phase balance remains open.

## 6. Next branch

Use the accepted `09cV2` case/data pair and its selected fraction point to create [010V2 — EWF deposition and film inventory](010V2-ewf-deposition-film-inventory.md). Do not promote the 5% point to a physical default without a closed Skoog/1-D balance or new measurement evidence.

Create a separate child case for the fine-mist PSD comparison rather than overwriting the historical `09cV2` artifacts.

## 7. Live Student velocity-inlet adaptation — 2026-08-04

The requested build was performed from the case already loaded in the Windows Student Edition session. The loaded source did **not** expose a verified filename and did not satisfy the documented mass-flow-parent requirements, so the saved artifact is a labelled diagnostic derivative rather than an exact historical `09cV2` recreation.

| Item | Read-back value |
|---|---|
| Artifact | `09cV2-fDPM-05pct-velocity-inlet-adaptation.cas.h5` |
| Fluent version | `Ansys Fluent 2025 R2` |
| Inlet topology | `velocity_inlet.liquidinlet` + `velocity_inlet.steaminlet` |
| Liquid allocation implementation | `liquidinlet` water-liquid velocity `27.118 -> 25.7621 m/s` |
| Steam-side velocity | `steaminlet` water-vapor `27.118 m/s` |
| DPM fraction | `Assumed 5%` screening point |
| DPM total | `5.846 kg/s` |
| Eulerian-liquid target | `111.074 kg/s` reference target; exact mass flow not independently verified because the live flux-report branch was inactive |
| DPM coupling | interaction `On`; source update every flow iteration `On`; interval `1` |
| DPM payload | six historical bins on `steaminlet`, `5.63–348.88 µm`, total `5.846 kg/s` |
| DPM material | `water-liquid-at-psep-dpm` |
| Material basis | `Fallback`: `water-liquid-at-psep` was copied from the live `water-liquid`; not provenance-verified historical EWF material data |
| Wall fates | `bottom = trap`, `wall-fluid = reflect`, inlets/outlet = `escape` |
| EWF / Energy | `Off / Off` |
| Run state | case-only; no initialization, iterations, or `.dat.h5` write |
| Verification | [strict post-save readback](../../../PyAnsys/output/09cV2_student_velocity_inlet_adaptation_verification_20260804.json) |

The six-bin relative weights were normalized to close exactly to `5.846 kg/s`; this preserves the documented parent ratio but does not add evidence that the 5% fraction is physically measured. The velocity scaling assumes fixed inlet area and density, so this artifact must remain labelled a velocity-inlet adaptation until a mass-flow parent or an independently verified flux closure is available.

## Linked evidence

- [Project fine-mist DPM size and mass distribution](../../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md)
- [Detailed geothermal fine-mist cutoff evidence](../../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md)
- [Project Skoog guardrails](../../../ResearchProject_wiki/wiki/model/skoog-application-guardrails.md)
- [Droplets, carryover, and re-entrainment evidence](../../../CFD_wiki/wiki/physics-basis/droplets-carryover-and-re-entrainment.md)
- [Geothermal separator inlet droplet synthesis](../../../CFD_wiki/wiki/synthesis/geothermal-separator-inlet-droplets-and-carryover.md)
- [Skoog source extraction](../../../CFD_wiki/wiki/sources/skoog-2020-annular-flow-three-field-cfd-thesis.md)
- [Fluent click-by-click guidance](../../../CFD_wiki/wiki/guidance/fluent-general-click-by-click.md)
- [10a server-2 live failure readback](../../../PyAnsys/output/live_postprocess_20260721/10a-server2-stripping-live-report.md)
- [09c parent setup](09c-dpm-ewf-wall-film-reentrainment.md)

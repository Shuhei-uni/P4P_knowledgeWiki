# Setup 09cV3 — Fine-Mist 5% DPM PSD Rerun

## Setup metadata

| Field | Value |
|---|---|
| Setup ID | `09cV3` |
| Lifecycle | `active` |
| Role | controlled fine-mist particle-size-distribution (PSD) rerun |
| Parent setup | [09cV2 — Skoog partition and injection control](../past/reported/09cV2-skoog-partition-injection-control.md) |
| Child setups | none yet |
| Controlled changes | replace the active legacy six-bin DPM injection diameters and relative mass weights with the seven-bin `5–100 µm` fine-mist PSD; retain the total 5% DPM allocation |
| Evidence-use label | setup calculation / diagnostic only until the inherited carrier state, DPM source terms, and run monitors are read back and assessed |
| Outcome | case-only child built and read-back verified; diagnostic 2%/3% run post-processing is recorded separately |
| Linked report | [09cV3 fine-mist allocation diagnostic results](../reports/purnanto-reference/09cV3/results.md) |

## 1. Objective

Recreate the `09cV2` **5% DPM** point with a DPM population intended to represent steam-carried fine mist, rather than the historical six-bin distribution dominated by the `348.88 µm` injection.

The single experimental question is:

> At the same 5% tracked-liquid allocation, how do the revised fine-mist injection sizes and mass weights affect DPM fate and coupled carrier response?

This is a controlled PSD comparison, not a claim that the new mass distribution is a measured geothermal separator-inlet PSD. The `5–100 µm` range and mass weights are an **Assumed, medium-risk engineering prior** based on the project decision record and the 2026-08-04 meeting report ([fine-mist decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md), §§3–7; [meeting report](../../Meeting%20report/mesh-conversion-and-dpm-mass-sensitivity-meeting-report.md), §3).

## 2. Inherited setup

Copy the selected, read-back-verified `09cV2` **5% partitioned** case/data checkpoint. The parent checkpoint remains diagnostic, not a converged physical baseline; preserve that limitation in the case name, run notes, and any results report.

Inherit without intentional change:

- geometry, mesh, split `liquidinlet` / `steaminlet` topology, outlets, walls, phase materials, and carrier solver settings;
- liquid accounting at the parent 5% point: total liquid `116.920 kg/s`, DPM allocation `5.846000 kg/s`, and Eulerian-liquid allocation `111.074000 kg/s` (**Reported** project accounting; [09cV2](../past/reported/09cV2-skoog-partition-injection-control.md), §3; [fine-mist decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md), §7);
- vapor inlet flow, DPM injection surface (`steaminlet`), injection velocity, particle material, parcel/stream settings, deterministic tracking, drag law, and DPM source-update controls;
- global `DPM Interaction with Continuous Phase = On`, source update every flow iteration, and DPM iteration interval `1` ([09cV2](../past/reported/09cV2-skoog-partition-injection-control.md), §§2 and 4F);
- EWF and its splash, edge-separation, stripping, custom-law, and phase-change mechanisms **Off**, as in the parent allocation-control branch.

Do not inherit a failed `10a` checkpoint or any unpartitioned DPM payload. `09cV3` must begin from a case whose readback confirms the complementary Eulerian-liquid allocation and a total active DPM flow of `5.846000 kg/s`.

## 3. Controlled change: seven-injection fine-mist PSD

Deactivate the six legacy injections in the **copied `09cV3` case** and create seven active `Surface` injections on `steaminlet`. Keep all non-PSD injection settings inherited. The values below are **Assumed engineering-prior inputs**, not measured inlet data ([fine-mist decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md), §§5–7; [meeting report](../../Meeting%20report/mesh-conversion-and-dpm-mass-sensitivity-meeting-report.md), §3).

| Suggested injection identity | Diameter interval [µm] | Representative diameter [µm] | DPM mass share | Total flow rate [kg/s] |
|---|---:|---:|---:|---:|
| `09cV3-finemist-07um` | `5–10` | `7.07` | `6.998%` | `0.409128` |
| `09cV3-finemist-14um` | `10–20` | `14.14` | `19.931%` | `1.165149` |
| `09cV3-finemist-24um` | `20–30` | `24.49` | `21.680%` | `1.267410` |
| `09cV3-finemist-35um` | `30–40` | `34.64` | `18.688%` | `1.092501` |
| `09cV3-finemist-49um` | `40–60` | `48.99` | `22.738%` | `1.329262` |
| `09cV3-finemist-69um` | `60–80` | `69.28` | `8.016%` | `0.468606` |
| `09cV3-finemist-89um` | `80–100` | `89.44` | `1.949%` | `0.113944` |
| **Total active DPM payload** | `5–100` | — | **`100.000%`** | **`5.846000`** |

The mass shares come from the truncated and renormalised Rosin–Rammler prior with `F(30 µm) = 0.50`, `F(60 µm) = 0.90`, `n = 1.7320`, and `d_c = 37.070 µm`. These two cumulative constraints are project assumptions, so this setup must retain the uncertainty label even if the Fluent run is numerically stable ([fine-mist decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md), §5).

The removed coarse legacy payload is not deleted from the overall liquid accounting: it remains represented by the inherited Eulerian-liquid allocation. Do not change `111.074000 kg/s` while making this first PSD-only comparison.

## 4. Geometry and mesh

Use the same geometry and selected mesh checkpoint as the copied `09cV2` parent. Mesh independence is unresolved, so any `09cV3` comparison is conditional on the exact mesh/checkpoint being recorded; do not attribute a difference to PSD if the mesh, carrier maturity, or checkpoint changes at the same time ([meeting report](../../Meeting%20report/mesh-conversion-and-dpm-mass-sensitivity-meeting-report.md), §§1 and 3).

## 5. Fluent setup and build procedure

1. Open the selected `09cV2` 5% case/data pair and read back the carrier settings, active injection list, DPM interaction controls, material identity, and inlet phase flows.
2. Save a child copy before editing, for example `09cV3-fDPM-05pct-finemist-5to100um.cas.h5` and its matching data file. Never overwrite the `09cV2` artifact.
3. Confirm the Eulerian-liquid flow is `111.074000 kg/s`, the vapor flow is inherited unchanged, and the sum of active DPM injection flows is `5.846000 kg/s` before replacing the PSD.
4. In the child copy, deactivate each active legacy six-bin injection so none can contribute DPM mass or source terms. Retain their names and settings in the copied setup notes/readback for comparison traceability.
5. Create the seven `Surface` injections listed in Section 3 on `steaminlet`. Set each representative diameter and total flow rate exactly as tabulated; retain inherited material, velocity, tracking, and parcel settings.
6. Reopen every injection and record the name, surface, material, diameter, total flow rate, and active state. Sum the seven read-back flow rates; the total must be `5.846000 kg/s` within displayed precision.
7. Confirm that no legacy injection remains active and that the project liquid accounting still closes at the **input definition** level: `111.074000 + 5.846000 = 116.920000 kg/s`.
8. Confirm that global DPM interaction remains `On`, source update every flow iteration remains `On`, and DPM iteration interval remains `1`. Keep EWF and optional DPM/EWF mechanisms off for this direct `09cV2` child comparison.
9. Save the pre-run `09cV3` checkpoint. Run a short `20–50`-iteration smoke test, preserving a debug checkpoint if DPM source terms, continuity, or phase fluxes deteriorate sharply.
10. If the smoke test is stable, continue only to a documented checkpoint and record the exact case/data names, Fluent version, mesh identity, initial-field source, iteration count, residuals, phase fluxes, DPM source monitors, and per-injection fates.

## 6. Boundary conditions

| Boundary / setting | `09cV3` value | Evidence / label |
|---|---|---|
| Total inlet liquid reference | `116.920 kg/s` | **Reported** project accounting ([09cV2](../past/reported/09cV2-skoog-partition-injection-control.md), §3) |
| Eulerian liquid at `liquidinlet` | `111.074000 kg/s` | **Assumed** 5% allocation point retained from parent ([fine-mist decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md), §7) |
| DPM injection surface | `steaminlet` | **Inherited** from `09cV2`; read back before run |
| Total DPM flow | `5.846000 kg/s` | **Assumed** 5% allocation point; seven-bin sum in Section 3 |
| DPM size range | `5–100 µm` | **Assumed** provisional fine-mist representation ([fine-mist decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md), §§3–6) |
| Vapor inlet, outlets, walls, backflow, turbulence, and injection velocity | unchanged from selected parent checkpoint | **Inherited**; record readback because no new value is introduced by this setup |

## 7. Acceptance checks

Before interpreting a `09cV3` result:

- record the exact parent and child case/data files, Fluent version, mesh identity, initial-field source, and iteration checkpoint;
- verify there are exactly seven active original DPM injections, no legacy six-bin injection is active, and the seven read-back flows sum to `5.846000 kg/s`;
- verify the Eulerian liquid plus active DPM total remains `116.920000 kg/s` at the inlet-accounting level;
- verify every injection uses the inherited material and `steaminlet` surface, unless a separately named sensitivity documents a different setting;
- capture continuity, phase-fraction, momentum/turbulence residuals, phase-flux reports, and DPM source-term monitors before and after the PSD substitution;
- report per-injection injected mass, parcel count, escaped, trapped, incomplete, and—if applicable—EWF-absorbed fractions; report both mass-weighted and number-weighted aggregates only when their definitions are recorded;
- retain `diagnostic only` if the inherited carrier imbalance, residual drift, or DPM source response remains unresolved. The meeting record explicitly identifies the existing 5% case as diagnostic rather than converged ([meeting report](../../Meeting%20report/mesh-conversion-and-dpm-mass-sensitivity-meeting-report.md), §2).

## 8. Linked evidence

- [09cV2 parent setup](../past/reported/09cV2-skoog-partition-injection-control.md)
- [Fine-mist DPM size and mass-distribution decision](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md)
- [Mesh, droplet-loading, and wall-film meeting report](../../Meeting%20report/mesh-conversion-and-dpm-mass-sensitivity-meeting-report.md)
- [Detailed geothermal fine-mist cutoff evidence](../../CFD_wiki/wiki/synthesis/geothermal-fine-mist-size-cutoff-evidence.md)
- [09cV2 diagnostic results](../reports/purnanto-reference/09cV2/results.md)

## 8a. Server-2 10% fine-mist loading sensitivity — 2026-08-07

The separately saved `10%` child changes the **liquid/DPM allocation**, so it is not a replacement for the fixed-`5%` PSD comparison defined above. It remains an **Assumed, medium-risk diagnostic sensitivity**, not a measured geothermal inlet mist fraction. The seven fine-mist diameters, `steaminlet` surface, DPM material, injection velocity, DPM interaction controls, carrier settings other than the liquid allocation, and wall fates were retained from the explicit `5%` child.

| Item | Read-back value |
|---|---:|
| Parent case | `C:\Users\syok443\P4P simulation\09cV3-fDPM-05pct-finemist-5to100um.cas.h5` |
| Child case | `C:\Users\syok443\P4P simulation\09cV3-fDPM-10pct-finemist-5to100um.cas.h5` |
| Eulerian liquid at `liquidinlet` | `105.228000 kg/s` |
| Seven-bin DPM total | `11.692000 kg/s` |
| Input liquid accounting | `105.228000 + 11.692000 = 116.920000 kg/s` |
| Vapor inlet | `80.690000 kg/s`, inherited unchanged |
| Verification | [strict explicit-reload readback](../../PyAnsys/output/09cV3_server2_10pct_verification_20260807.json) |

The seven-bin flow values are the project’s tabulated `10%` values from the [fine-mist allocation sweep](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md#8-scaling-across-the-dpm-fraction-sweep); they sum to `11.692000 kg/s`. The planned `5,000`-iteration run must still be reported separately from this case-only verification, including its actual completed iteration count and any numerical/DPM monitoring evidence.

## 8b. Server-1 2% fine-mist loading sensitivity — 2026-08-07

This is a controlled **Assumed, medium-risk** tracked-liquid DPM-allocation sensitivity, derived from the explicitly loaded server-1 `09cV3` 5% fine-mist case. It is not a generic DPM-to-carrier mass-ratio claim and it does not replace the 5% PSD comparison branch.

| Item | Read-back / configured value |
|---|---|
| Parent case | `C:\Users\syok443\P4P simulation\09cV3-fDPM-05pct-finemist-5to100um.cas.h5` |
| Recovery case | `C:\Users\syok443\P4P simulation\09cV3-fDPM-05pct-prebuild-02pct-20260807.cas.h5` |
| Child case | `C:\Users\syok443\P4P simulation\09cV3-fDPM-02pct-finemist-5to100um.cas.h5` |
| Eulerian liquid at `liquidinlet`, phase `phase-2` | `114.581600 kg/s` |
| Seven-bin DPM total | `2.338400 kg/s` |
| Input liquid accounting | `114.581600 + 2.338400 = 116.920000 kg/s` |
| Vapor inlet | `80.690000 kg/s`, inherited unchanged |
| DPM controls | interaction `On`; source update every flow iteration `On`; interval `1` |
| Initialization | hybrid initialization requested and Fluent returned to `SERVING` before calculation launch |
| Native recovery settings | paired case/data every `500` iterations; unique `09cV3-fDPM-02pct-finemist-5to100um-autosave` root; retain two most recent files |
| Calculation request | Fluent Run Calculation configured for `5,000` additional iterations; launch observed through first coupled DPM tracking output |
| Verification | [strict explicit-reload readback](../../PyAnsys/output/09cV3_mass_flow_02pct_from_05pct_20260807.json) |

The seven surface injections remain on `steaminlet`, retain the documented diameters and all inherited non-loading settings, and use the tabulated 2% flow scaling in the [fine-mist allocation sweep](../../ResearchProject_wiki/wiki/model/fine-mist-dpm-size-and-mass-distribution.md#8-scaling-across-the-dpm-fraction-sweep). A later explicit reload of the paired `...-iter5000.cas.h5`/`.dat.h5` checkpoint established an available 5,000-iteration result checkpoint and produced the scoped phase-flux and DPM terminal-fate reports in the [09cV3 results record](../reports/purnanto-reference/09cV3/results.md). The result remains diagnostic because carrier closure, residual maturity, and the substantial incomplete-DPM fraction are unresolved.

## 8c. Server-1 3% fine-mist loading sensitivity — 2026-08-10

The 3% sensitivity was built from the explicitly loaded 2% iteration-5000 checkpoint, with a distinct paired recovery copy written before mutation. This is an **Assumed, medium-risk** tracked-liquid DPM allocation sensitivity and remains diagnostic only.

| Item | Read-back / configured value |
|---|---|
| Source checkpoint | `09cV3-fDPM-02pct-finemist-5to100um-iter5000.cas.h5` + matching `.dat.h5` |
| Pre-mutation recovery pair | `09cV3-fDPM-02pct-iter5000-prebuild-03pct-20260810.cas.h5` + matching `.dat.h5` |
| 3% child case | `09cV3-fDPM-03pct-finemist-5to100um.cas.h5` |
| Eulerian liquid at `liquidinlet`, phase `phase-2` | `113.412400 kg/s` |
| Seven-bin DPM total | `3.507600 kg/s` |
| Input liquid accounting | `113.412400 + 3.507600 = 116.920000 kg/s` |
| Vapor inlet | `80.690000 kg/s`, unchanged |
| DPM controls | interaction `On`; source update every flow iteration `On`; interval `1` |
| Initialisation | hybrid initialization completed and Fluent returned `SERVING` |
| Initialized recovery pair | `09cV3-fDPM-03pct-finemist-5to100um-initialized.cas.h5` + matching `.dat.h5` |
| Native autosave | paired case/data every `500` iterations; unique 3% root; two newest files retained |
| Calculation request | Fluent Calculate started for `2,000` additional iterations; first coupled iteration was observed |

The child was explicitly reloaded before hybrid initialization. Its readback preserved the seven inert `Surface` injections on `steaminlet`, their diameters and non-loading settings, the Mixture/RNG `k-ε` carrier setup, Energy off, and global two-way DPM controls. The run is recorded as **launched**, not as a verified 2,000-iteration completion; establish final count and numerical/DPM state from later native autosave or read-only monitor evidence.

## 9. Live Student case-only build — 2026-08-04

The `09cV3` child was built from the explicitly named, read-back-verified Student velocity-inlet adaptation of `09cV2`. The parent artifact was loaded by its full Windows path; the transport alias `student` was not treated as case identity.

| Item | Read-back value |
|---|---|
| Fluent / PyFluent | Ansys Fluent `2025 R2` / PyFluent `0.39.0` |
| Parent case | `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV2-fDPM-05pct-velocity-inlet-adaptation.cas.h5` |
| Child case | `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation.cas.h5` |
| Recovery copy | `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-student-prebuild-from-09cV2-20260804.cas.h5` |
| Inlet topology | split `velocity_inlet.liquidinlet` + `velocity_inlet.steaminlet`; `mass_flow_inlet` branch inactive |
| Inherited liquid-side velocity | `liquidinlet` water-liquid `25.7621 m/s` |
| Inherited steam-side velocity | `steaminlet` water-vapor `27.118 m/s` |
| DPM interaction | `On`; source update every flow iteration `On`; interval `1` |
| Active DPM payload | exactly seven surface injections on `steaminlet`; read-back total `5.846000 kg/s` |
| Legacy payload | all six legacy injections absent from the copied child branch; no legacy injection remains active |
| Input liquid accounting | `111.074000 + 5.846000 = 116.920000 kg/s` at the setup-definition level |
| Wall fates | `bottom = trap`; `wall-fluid = reflect`; inlets and `steamoutlet = escape` |
| EWF / data / iterations | EWF not activated in the parent branch; no data file read or written; `0` flow iterations performed |

The requested identities in Section 3 were entered with uppercase `V`, but Fluent 2025 R2 canonicalized them to lowercase when serializing the case. The saved-case names are therefore `09cv3-finemist-07um`, `09cv3-finemist-14um`, `09cv3-finemist-24um`, `09cv3-finemist-35um`, `09cv3-finemist-49um`, `09cv3-finemist-69um`, and `09cv3-finemist-89um`; the verification compares the identities case-insensitively and records both spellings.

This remains a **diagnostic, velocity-inlet adaptation**, not an exact historical mass-flow `09cV3` recreation. The `111.074000 kg/s` Eulerian-liquid value is the inherited 5% allocation reference represented by the parent velocity scaling; the live session did not expose an independent mass-flow report to verify that flux. The seven-bin PSD remains an **Assumed, medium-risk engineering prior**, not measured inlet data. No 20–50-iteration smoke test was run as part of this build.

The strict read-back snapshot is [09cV3_student_finemist_verification_20260804.json](../../PyAnsys/output/09cV3_student_finemist_verification_20260804.json), and the case-only builder is [build_09cV3_student_finemist_from_09cV2.py](../../PyAnsys/scripts/setup/build_09cV3_student_finemist_from_09cV2.py).

## 11. Student 50-iteration checkpoint and stopped continuation — 2026-08-04

The verified Student velocity-inlet child was hybrid-initialized and run for the requested first `50` flow iterations. It was then saved as a paired case/data checkpoint, explicitly resumed from that pair, and advanced into the second `50`-iteration block. The user stopped the run during the chunk covering iterations `51–60`; the Fluent transcript had reached iterations `51–59`, but the exact in-memory state at the interrupt is not claimed.

| Item | Read-back value |
|---|---|
| Initial field | hybrid initialization performed once before iteration 1 |
| Iteration-50 case | `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation-iter50.cas.h5` |
| Iteration-50 data | `C:\Users\Shuhei Yokkaichi\Documents\CFD\base files\09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation-iter50.dat.h5` |
| Iteration-100 case/data | not created |
| First stage | completed and saved at `50` iterations |
| Resume stage | explicitly loaded the iteration-50 case/data pair; no reinitialization was performed |
| Stop point | user interruption during the `51–60` chunk; transcript reached `51–59` |
| Restored live state | explicitly reloaded from the saved iteration-50 case/data pair |
| Iteration-50 monitor snapshot | continuity `6.4197e-1`; x/y/z velocity `7.1907e-4 / 6.6254e-4 / 6.6994e-4`; `k = 7.5132e-3`; epsilon `1.5149e-2`; water-liquid VF residual `1.2477e-2` |
| DPM monitor snapshot at iteration 50 | `21,581` tracked; `20,928` escaped; `650` trapped; `3` incomplete |
| Numerical warnings at iteration 50 | reversed flow on `35` pressure-outlet faces; turbulent-viscosity ratio limited to `1.0e5` in `26` cells |

The first checkpoint is valid for resumption and the original case-only child remains untouched. The iteration-50 DPM counts are live diagnostic monitor output from the coupled flow iteration, not a completed per-injection fate or separator-efficiency result. The residuals and outlet reverse-flow warnings keep this run **diagnostic only**; no convergence or performance claim is promoted.

The stopped-run record is [09cV3_student_50_then_100_run_20260804.json](../../PyAnsys/output/09cV3_student_50_then_100_run_20260804.json), the run-state record is [09cV3_student_50_then_100_run_state_20260804.json](../../PyAnsys/output/09cV3_student_50_then_100_run_state_20260804.json), and the reusable runner is [run_09cV3_student_50_then_100.py](../../PyAnsys/scripts/setup/run_09cV3_student_50_then_100.py).

## 10. Live server-1 mass-flow build — 2026-08-04

The same PSD-only child was then built from the explicitly named server-1 mass-flow parent. This is a separate artifact from the Student velocity-inlet adaptation above; the boundary topology and wall-zone names were read back rather than assumed to match.

| Item | Read-back value |
|---|---|
| Parent case | `C:\Users\syok443\P4P simulation\09cV2-fDPM-05pct-10678.cas.h5` |
| Child case | `C:\Users\syok443\P4P simulation\09cV3-fDPM-05pct-finemist-5to100um.cas.h5` |
| Recovery copy | `C:\Users\syok443\P4P simulation\09cV3-server1-prebuild-from-09cV2-20260804.cas.h5` |
| Inlet topology | `mass_flow_inlet.liquidinlet` + `mass_flow_inlet.steaminlet`; no active velocity-inlet zones |
| Liquid flow | `111.074 kg/s` on `liquidinlet` phase `phase-2` |
| Vapor flow | `80.690 kg/s` on `steaminlet` phase `phase-1` |
| DPM interaction | `On`; source update every flow iteration `On`; interval `1` |
| Active DPM payload | exactly seven surface injections on `steaminlet`; read-back total `5.846000 kg/s` |
| Parent wall-zone names | `bottom` and `wall` |
| Wall fates | `bottom = trap`; `wall = reflect`; inlets and `steamoutlet = escape` |
| Input liquid accounting | `111.074000 + 5.846000 = 116.920000 kg/s` |
| Run state | case-only; no initialization, iterations, data read, or `.dat.h5` write |
| Verification | [strict server-1 readback](../../PyAnsys/output/09cV3_mass_flow_verification_20260804.json) |

The reusable mass-flow builder is [build_09cV3_mass_flow_from_09cV2.py](../../PyAnsys/scripts/setup/build_09cV3_mass_flow_from_09cV2.py). Fluent 2025 R2 serializes the requested fine-mist injection names as lowercase `09cv3-finemist-*` in the saved case; the verification compares these names case-insensitively. The source `09cV2` case was not overwritten.

## 12. Detached 5,000-iteration connection-resilience test — 2026-08-04

The long-run worker was launched from the verified Student iteration-50 case/data pair and deliberately detached from the terminal that launched it. The first ordinary background launch was reaped when its shell ended; the worker was then submitted as a user-level `launchd` job, which survived the launcher shell ending. A fresh terminal-side client subsequently connected to the same Fluent endpoint and read both the worker state/log and Fluent health without taking over the worker's run client.

| Item | Read-back / requested value |
|---|---|
| Starting case/data pair | `09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation-iter50.cas.h5` + matching `.dat.h5` |
| Starting orchestration count | `50` total iterations |
| Target | `5,000` total iterations (`4,950` additional) |
| Chunk size | `10` iterations between local state updates |
| Checkpoint interval | every `500` total iterations |
| Checkpoint policy | two alternating paired case/data slots; each new save overwrites one slot after the other slot has been verified |
| Checkpoint slot A | `09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation-checkpoint-a.cas.h5` + `.dat.h5` |
| Checkpoint slot B | `09cV3-fDPM-05pct-finemist-5to100um-velocity-inlet-adaptation-checkpoint-b.cas.h5` + `.dat.h5` |
| Fluent health after launcher terminal ended | new client: `Ansys Fluent 2025 R2`, health `SERVING` |
| Worker state at initial verification | `running`, persisted count `50`, target `5,000`; Fluent had begun iteration `51` |
| Stop result | user-requested stop; worker reached the chunk through `60`, entered `61`, and was then removed from `launchd` |
| Last verified paired checkpoint | iteration `50`; no `500`-iteration checkpoint was written |
| Live state after stop | explicitly restored from the iteration-50 case/data pair; fresh health `SERVING`; no calculation remained active |
| Starting-pair audit | liquid velocity `25.7621 m/s`; steam velocity `27.118 m/s`; seven active injections; DPM total `5.846 kg/s`; two-way interaction `enabled`; source update interval `1`; legacy injections absent |
| Local worker state | [09cV3_student_5000_resilient_state_20260804.json](../../PyAnsys/output/09cV3_student_5000_resilient_state_20260804.json) |
| Local worker log | [09cV3_student_5000_resilient_20260804.log](../../PyAnsys/output/09cV3_student_5000_resilient_20260804.log) |
| Worker | [run_09cV3_student_5000_resilient.py](../../PyAnsys/scripts/setup/run_09cV3_student_5000_resilient.py) |

The user subsequently requested that the simulation end. The worker was removed from `launchd` after it had completed the local chunk through iteration `60`; a transcript line shows iteration `61` had begun, but that iteration is not claimed complete. No rolling checkpoint slot was written because the run never reached total iteration `500`. The live Fluent session was then explicitly restored from the verified iteration-50 case/data pair; a fresh readback confirmed the expected seven-injection, `5.846 kg/s` DPM setup and Fluent health `SERVING`. The `run_calculation.interrupt` command was inactive after restoration, confirming that no calculation remained active. `completed_iterations` in the state file records the last worker chunk observed (`60`), while `last_checkpoint.iteration` remains the last verified paired save (`50`). This remains a **diagnostic** run, and the inherited velocity-inlet adaptation plus assumed medium-risk fine-mist PSD limitations continue to apply.

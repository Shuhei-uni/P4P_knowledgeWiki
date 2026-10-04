# Phase 8 F2 — split feed results

| Item | Phase 8 F2 — split feed results |
| --- | --- |
| Splitting the inlet phases changes | retained liquid mass and the inlet flow representation, but the Coupled sweep still routes almost all Eulerian liquid to the steam outlet |
| — | It supplies the next historical stage rather than demonstrating successful separation |

## Comparison basis

| Item | Comparison basis |
| --- | --- |
| — | Five nominal speeds on the same 60,964-cell partition, full Eulerian liquid feed, closed bottom, absorber/EWF off, and matched Coupled/Global Time Step/first-order-k numerics |
|  | Each speed starts with fresh Hybrid initialization and reaches N10,000 |
| Routing and pressure summaries use N9,500–10,000; inventories | are final snapshots |
| These Coupled cases | are numerical adaptations of the SIMPLE recreation |

## Higher speed changes inventory and pressure, with little change in outlet routing

| Item | Higher speed changes inventory and pressure, with little change in outlet routing |
| --- | --- |
| — | Across 20.11–32.14 m/s, F2's outlet fraction stays within 99.38–99.43% |
|  | Its inventory first decreases slightly and then rises to 1,911.1 kg; the pressure difference increases from 45.67 to 102.26 kPa |
| inventory response | is therefore not monotonic across the whole sweep, although pressure rises at every speed |
| Compared with F1, the split inlet | retains more liquid at all five matched endpoints |

![F2 speed response](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/speed-response.png>)

| Speed (m/s) | Outlet liquid / feed, last-500 mean (%) | Final liquid inventory (kg) | Steam-face–outlet pressure difference (kPa) | Unresolved diagnostic DPM weight (%) |
| ---: | ---: | ---: | ---: | ---: |
| 20.11 | 99.384 | 1743.0 | 45.67 | 78.70 |
| 23.46 | 99.422 | 1719.2 | 58.75 | 74.30 |
| 26.81 | 99.404 | 1734.5 | 73.39 | 80.76 |
| 29.48 | 99.425 | 1806.3 | 86.89 | 77.33 |
| 32.14 | 99.423 | 1911.1 | 102.26 | 79.62 |

![F2 routing and inventory histories](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/routing-inventory-history.png>)

| Item | Higher speed changes inventory and pressure, with little change in outlet routing |
| --- | --- |
| — | The raw histories distinguish the evolving carrier from its final checkpoint |
| Inventory | is Eulerian liquid mass, not removed liquid |
| pressure metric | uses the recorded area-weighted `steaminlet` and `steamoutlet` reports; it is not a mass-weighted pressure loss |

## Retained liquid occupies the lower region and outer wall

| Reference snapshot | Vertical liquid distribution | Inlet-plane circulation |
| --- | --- | --- |
| F2-26.81-n10000 | ![F2-26.81-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-liquid.png>) | ![F2-26.81-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-inlet-vectors.png>) |

| Item | Retained liquid occupies the lower region and outer wall |
| --- | --- |
| The centre cut and inlet slice answer different questions | the first shows vertical liquid distribution; the second retains the offset inlet and shows circumferential flow |
|  | Compare speed cases within the same numerical branch and horizon |
|  | The SIMPLE snapshots document an earlier stage and are not matched N10,000 speed controls |
| — | Reference-speed gauge pressure: |

![F2-26.81-n10000 pressure](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-pressure.png>)

*Figure F2.3. Reference-speed F2 carrier at N10,000, with a separate gauge-pressure view above. The centre cut identifies lower-region and wall enrichment; inlet-plane vectors show circumferential circulation. These local views support the inventory interpretation without measuring removal.*

| Retained liquid occupies the lower region and outer wall |
| --- |
| The split-feed centre cut has a deeper liquid-enriched lower region than the mixed-feed reference at 26.81 m/s, consistent with its larger inventory |
| Both show an outer-wall liquid band and low-volume-fraction central bulk; the inlet slice shows enrichment around the outer circumference and a locally stronger band near the inlet junction |
| The inlet-plane vectors retain the same circulation direction |
| Use the inventory report to quantify the difference; a centre-plane colour footprint alone does not measure the 3D liquid mass |

## Diagnostic droplets reveal unresolved transport rather than a complete separation result

| Item | Diagnostic droplets reveal unresolved transport rather than a complete separation result |
| --- | --- |
| F2 | retains 74.30–80.76% unresolved injection weight, without a monotonic trend across the speeds |
| At 26.81 m/s, 80.76% | is unresolved, compared with 77.30% in F1 |
| — | This small cross-family difference does not establish a droplet-separation ranking |

![F2 seven-bin fates at every speed](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/droplet-bin-fates.png>)

![F2 droplet speed response](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/droplet-speed-response.png>)

| Item | Diagnostic droplets reveal unresolved transport rather than a complete separation result |
| --- | --- |
| left plot | uses injection-weighted fate fractions; the right gives the incomplete trajectory fraction in each size bin |
| — | Both retain incomplete tracks |
|  | Diagnostic parcel weights do not add physical inlet mass to these full-Eulerian-feed carriers |
|  | High unresolved fractions prevent converting escaped weight into separator efficiency |
|  | F2 reference one-way DPM — inlet stream 0: |

| 7.07 µm | 34.64 µm | 89.44 µm |
| --- | --- | --- |
| ![F2-26.81-diagnostic stream 0 07](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-diagnostic-track-07um-stream0.png>) | ![F2-26.81-diagnostic stream 0 35](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-diagnostic-track-35um-stream0.png>) | ![F2-26.81-diagnostic stream 0 89](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-diagnostic-track-89um-stream0.png>) |

| Item | Diagnostic droplets reveal unresolved transport rather than a complete separation result |
| --- | --- |
| Each row | shows three deterministic illustrative paths, not a statistical sample |
| — | Native zone outlines provide vessel/inlet/outlet context; path colour represents diameter on the shared 5–100 µm range |
| line endpoint alone | is not a fate classification |
| saved tracking controls | were retained; no carrier iterations or source-case saves were issued |
| — | Diameter-resolved fate plots, rather than these selected paths, describe the full tracked ensemble |

## Numerical context

![F2 numerical context](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/numerical-context.png>)

| Item | Numerical context |
| --- | --- |
| reported boundary gap and continuity | are supporting diagnostics |
| Reverse outlet flow and viscosity limiting | were recorded in these runs; a low residual or bounded inventory does not validate the closed-bottom separator |
| — | See the [phase result](../results.md) for the matched F1/F2 comparison |

## What this stage establishes

| Item | What this stage establishes |
| --- | --- |
| F2 supplies the split-inlet stage | the internal liquid state differs from F1, but almost all Eulerian liquid still reaches the steam outlet |
|  | Separating the inlet phases alone does not establish a satisfactory removal path in the closed-bottom model; F3 adds explicit droplet transport and feedback to investigate another part of that history |
|  | The five-speed SIMPLE snapshots preserve an earlier method branch; the quantitative F2 sweep remains the declared Coupled adaptation |

## Supporting spatial atlas

<details>
<summary>All saved case contours and vectors</summary>
| Saved snapshot | Liquid, vertical cut | Liquid, inlet slice | Vertical vectors | Inlet vectors |
| --- | --- | --- | --- | --- |
| F2 20.11 m/s N10000 | ![F2-20.11-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-20.11-n10000-liquid.png>) | ![F2-20.11-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-20.11-n10000-inlet-liquid.png>) | ![F2-20.11-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-20.11-n10000-vertical-vectors.png>) | ![F2-20.11-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-20.11-n10000-inlet-vectors.png>) |
| F2 23.46 m/s N10000 | ![F2-23.46-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-23.46-n10000-liquid.png>) | ![F2-23.46-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-23.46-n10000-inlet-liquid.png>) | ![F2-23.46-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-23.46-n10000-vertical-vectors.png>) | ![F2-23.46-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-23.46-n10000-inlet-vectors.png>) |
| F2 26.81 m/s N10000 | ![F2-26.81-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-liquid.png>) | ![F2-26.81-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-inlet-liquid.png>) | ![F2-26.81-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-vertical-vectors.png>) | ![F2-26.81-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-26.81-n10000-inlet-vectors.png>) |
| F2 29.48 m/s N10000 | ![F2-29.48-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-29.48-n10000-liquid.png>) | ![F2-29.48-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-29.48-n10000-inlet-liquid.png>) | ![F2-29.48-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-29.48-n10000-vertical-vectors.png>) | ![F2-29.48-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-29.48-n10000-inlet-vectors.png>) |
| F2 32.14 m/s N10000 | ![F2-32.14-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-32.14-n10000-liquid.png>) | ![F2-32.14-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-32.14-n10000-inlet-liquid.png>) | ![F2-32.14-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-32.14-n10000-vertical-vectors.png>) | ![F2-32.14-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-32.14-n10000-inlet-vectors.png>) |
| F2 SIMPLE original faces N2000 | ![F2-simple-mixed liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-simple-mixed-liquid.png>) | ![F2-simple-mixed inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-simple-mixed-inlet-liquid.png>) | ![F2-simple-mixed vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-simple-mixed-vertical-vectors.png>) | ![F2-simple-mixed inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f2-split-inlet/figures/F2-simple-mixed-inlet-vectors.png>) |

| Item | Supporting spatial atlas |
| --- | --- |
| — | Columns show separate native liquid contours and mixture-vector views |
| Shared planes, scales and source identities | are specified below |
| SIMPLE and continuation snapshots have their own horizons and | are not substitutes for matched pilot controls |

</details>

## Figure provenance and claim limits

| Item | Figure provenance and claim limits |
| --- | --- |
| Spatial images | are native Fluent 2025 R2 exports from verified case/data pairs |
| vertical cut | is `z = 0`; the horizontal cut is `y = 2.065999985 m`, the midpoint of the measured steam-inlet elevation bounds |
| Vertical axis | is `y` |
| Liquid volume fraction | uses `0–1`; mixture velocity colours use `0–100 m/s` |
| Bulk slice vectors | are in-plane, fixed-length, use shared scale `0.1`, and show every available vector (`skip = 0`) |

<details>
<summary>Supporting detail — Figure provenance and claim limits</summary>

| Item | Figure provenance and claim limits |
| --- | --- |
| — | They show projected direction; colour represents full mixture speed |
|  | Pressure contours use a shared gauge-pressure range `1110–1220 kPa` |
| Evidence | [hash-verified case catalog](../../../../PyAnsys/output/phase8-storyline-20260930/catalog.json), [native export receipt](../../../../PyAnsys/output/phase8-storyline-20260930/export-receipt.json), [surface/range receipt](../../../../PyAnsys/output/phase8-storyline-20260930/range-receipt.json) and [plot summary](../../../../PyAnsys/output/phase8-storyline-20260930/summary.json) |
| — | Phase 8 reconstructs the simulation storyline |
| Numerical shortcomings | are observations and interpretation limits, not progression gates |
| Steady native iterations | are not physical time; inventory slopes must not be called physical storage rates |
| No new flow solves | were performed for these results |

</details>

## Retained detailed execution evidence

<details>
<summary>Earlier receipts, numerical assessments and setup detail</summary>

| Item | Retained detailed execution evidence |
| --- | --- |
| Earlier pass/fail terminology below | records the previous numerical screening rule |
| It | is superseded as a Phase 8 progression/completion requirement by the [2026-09-30 clarification](../CONTEXT.md) |

# F2 26.81 m/s base preparation

| Item | F2 26.81 m/s base preparation |
| --- | --- |
| F2 | was derived from the verified F1 26.81 m/s case/data pair by changing the four phase mass-flow inlet commands only |
| It | was then freshly Hybrid initialized, saved, and reopened on `student` |
| Case | `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F2\F2-split-26p81-base.cas.h5` (SHA-256 `a38ab50038551124b5e22ec501f94dbc03ca306cde0c601225c7d6967b4d63d5`) |
| Data | `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F2\F2-split-26p81-base.dat.h5` (SHA-256 `a3acc8e538f8b33937c65831d82f93d0f29074e039b99725308ea55d5d01e4e3`) |
| Machine builder | [`build_phase8_f2_from_f1.py`](../../../../PyAnsys/scripts/setup/build_phase8_f2_from_f1.py). [Readback receipt](../../../../PyAnsys/output/phase8_f2_base_20260926.json) |

<details>
<summary>Supporting detail — F2 26.81 m/s base preparation</summary>

| Item | F2 26.81 m/s base preparation |
| --- | --- |
| Readback after reopening | `liquidinlet` supplies `116.93872650 kg/s` phase-2 liquid and zero vapor; `steaminlet` supplies `80.70292372 kg/s` phase-1 vapor and zero liquid |
|  | The shared materials, other boundaries, cell sources, DPM/EWF state, solver methods, and controls matched F1 in the builder's before/after comparison |
|  | Mesh check passed |
|  | This is an initialized setup base, not a developed carrier; common Phase 8 report definitions and post-development 09cV3 diagnostic injections remain to be installed before any F1/F2 comparison run |
| — | F2 inherits F1's Mixture model and therefore has no active bulk interfacial surface-tension coefficient or force. `0.0411 N/m` is recorded as the Purnanto reference property, not as an active Fluent setting; see the F1 surface-tension audit |

</details>

## Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29)

| Item | Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29) |
| --- | --- |
| — | The [parity builder](../../../../PyAnsys/scripts/setup/build_phase8_purnanto_parity_pilots.py) saved/reopened a new split-inlet child matching F1's SIMPLE/no pseudo-time/second-order `k` numerical setup and `0.724 m` inlet/backflow turbulence scale |
|  | The split phase commands remained liquid only at `liquidinlet` and vapor only at `steaminlet` |
|  | The [builder receipt](../../../../PyAnsys/output/phase8_purnanto_parity_pilots_20260928T110152Z.json) contains exact child hashes and setting readback |
| common 17-report package | recorded all 10-iteration coordinates through the 2,000-iteration carrier pilot; the final pair reopened. [Run manifest](../../../../PyAnsys/output/phase8-carrier/F2-26p81-20260928T113527Z/manifest.json), [paired numerical summary](../../../../PyAnsys/output/phase8-analysis/26p81-purnanto-parity/summary.json), and [trajectory figure](../../../../PyAnsys/output/phase8-analysis/26p81-purnanto-parity/f1-f2-carrier-26p81.png) carry the machine evidence |
| At N=2,000, mixture inlet flow | was `197.642 kg/s`, outlet flow `117.956 kg/s`, and boundary imbalance `79.685 kg/s` (40.32% of feed) |

<details>
<summary>Supporting detail — Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29)</summary>

| Item | Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29) |
| --- | --- |
| Steam-outlet liquid | was `36.693 kg/s`, 31.38% of liquid feed |
| — | Whole-domain liquid inventory rose from `689.94` to `979.04 kg` over N=1,500–2,000, with fitted slope `0.542 kg/steady iteration` |
| Continuity residual | was `0.1059`; reversed outlet flow and turbulence-viscosity limiting occurred repeatedly |
| slope | is not a physical storage rate |
| — | This endpoint fails the steady carrier qualification gate; an apparent outlet routing difference from F1 is not an accepted separator result |
| A bounded continuation to N=5,000 | is the next development step before F3/F4 can use F2 as a parent |

</details>

### N=2,000–5,000 continuation

| Item | N=2,000–5,000 continuation |
| --- | --- |
| — | The [continuation manifest](../../../../PyAnsys/output/phase8-carrier/F2-26p81-extension-20260928T114507Z/manifest.json) verifies the N=3,000, 4,000, and 5,000 checkpoints and the reopened final pair |
|  | The last 500 iterations still do not qualify: liquid inventory rose `2,896.70 → 3,616.56 kg` (`1.393 kg/steady iteration` fitted slope), while the N=5,000 steam outlet carried `255.324 kg/s` mixture against `197.642 kg/s` inlet, a signed boundary excess of `57.682 kg/s` |
| Steam-outlet liquid | was `175.289 kg/s`, exceeding the `116.939 kg/s` liquid feed |
| Continuity residual | was `0.2649`; reversed flow and viscosity limiting persisted |
| changing inventory and outlet flux | are a numerical/field-development failure, not evidence of useful separation or a physical storage rate |
| — | F2 therefore cannot yet parent the allocated coupled-DPM F3/F4 matrix |

### Coupled/Global Time Step numerical recovery child

| Item | Coupled/Global Time Step numerical recovery child |
| --- | --- |
| [recovery builder receipt](../../../../PyAnsys/output/phase8_numerical_recovery_f2_20260928T120003Z.json) verifies a new case/data pair that | retains the corrected `0.724 m` inlet/backflow scale and split feed, but restores Phase 7.2A's Coupled/Global Time Step and first-order `k` numerical settings |
| This | is a separately labelled numerical recovery branch, not Purnanto SIMPLE parity |
| It | was freshly Hybrid initialized and reopened |
| The [N=2,000 recovery manifest](../../../../PyAnsys/output/phase8-carrier/F2-26p81-coupled-gts-20260928T120152Z/manifest.json) and [numerical summary](../../../../PyAnsys/output/phase8-analysis/26p81-coupled-recovery/summary.json) show improvement but not qualification | terminal mixture boundary imbalance `14.618 kg/s` (7.40% of feed), outlet liquid `102.359 kg/s`, and continuity residual `0.0157` |
|  | Whole-domain liquid inventory still rose `1,295.67 → 1,421.33 kg` over N=1,500–2,000 (`0.250 kg/steady iteration` fitted slope) |

<details>
<summary>Supporting detail — Coupled/Global Time Step numerical recovery child</summary>

| Item | Coupled/Global Time Step numerical recovery child |
| --- | --- |
| The [N=2,000 recovery manifest](../../../../PyAnsys/output/phase8-carrier/F2-26p81-coupled-gts-20260928T120152Z/manifest.json) and [numerical summary](../../../../PyAnsys/output/phase8-analysis/26p81-coupled-recovery/summary.json) show improvement but not qualification | This state was continued to N=5,000 to test whether the trend settled |
| — | The [N=5,000 recovery continuation](../../../../PyAnsys/output/phase8-carrier/F2-26p81-coupled-gts-extension-20260928T121641Z/manifest.json) and [SIMPLE-versus-Coupled comparison](../../../../PyAnsys/output/phase8-analysis/26p81-f2-numerics/summary.json) show a monotonic improvement unlike the oscillating SIMPLE branch |
| At N=5,000 the mixture boundary gap | is `2.408 kg/s` (1.22% of feed), outlet liquid is `114.558 kg/s` (97.96% of liquid feed), and continuity residual is `0.0149` |
| — | Liquid inventory still rose `1,690.36 → 1,707.23 kg` in N=4,500–5,000 (`0.0336 kg/steady iteration` fitted slope) |
|  | Reversed outlet flow and turbulent-viscosity limiting continued |
| same state | was continued to N=10,000 |

</details>

### N=10,000 carrier gate

| Item | N=10,000 carrier gate |
| --- | --- |
| — | The [continuation manifest](../../../../PyAnsys/output/phase8-carrier/F2-26p81-coupled-gts-extension-to10000-20260928T123834Z/manifest.json) verifies local N=6,000–9,000 checkpoints and a saved/reopened shared N=10,000 case/data pair |
|  | The predeclared [last-500-window assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f2-coupled-n10000/assessment.json) passes all four operational checks: mean absolute mixture boundary gap `0.8550 kg/s` (`0.433%` of feed), liquid inventory `1,734.430 → 1,734.476 kg` with fitted slope `0.000101 kg/steady iteration`, continuity residual range `0.01329–0.01711`, and no fatal solver event |
| terminal mixture gap | is `0.9753 kg/s`; liquid through `steamoutlet` is `116.175 kg/s`, approximately `99.35%` of the liquid feed |
| extension transcript | retains reversed outlet flow and turbulent-viscosity limiting throughout |
| Thus this | is a developed diagnostic DPM parent under the operational rule, but a poor separator and not evidence of Purnanto numerical parity |
| — | The F1 Coupled child must use the same numerical package for a matched inlet-topology comparison |

### Seven-bin one-way diagnostic DPM

| Item | Seven-bin one-way diagnostic DPM |
| --- | --- |
| — | The [F2 diagnostic DPM child receipt](../../../../PyAnsys/output/phase8-dpm/F2-diagnostic-050permil-26p81-20260928T133307Z/build.json) verifies seven 09cV3 diameter bins, `5.846936325 kg/s` total *diagnostic* parcel weight, inert-particle density `881.210876 kg/m³` matching the carrier liquid, `steaminlet` release, interaction off, main-wall reflect, bottom trap, and saved/reopened case/data |
| full `116.93872650 kg/s` Eulerian liquid feed remains; parcel weights | are not additional physical inlet liquid |
| historical `27.118 m/s` axial release velocity and tracking controls | are in the readback |
| — | Fluent's per-injection Particle Tracks Summary tracked `613` trajectories per bin (`4,291` total): `175` escaped, `1,266` trapped, and `2,850` incomplete |
|  | The [size-resolved summary](../../../../PyAnsys/output/phase8-analysis/26p81-f2-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/26p81-f2-diagnostic-dpm/f2-diagnostic-dpm-fates-26p81.png) weight the fates by configured bin flow: `2.00%` escaped, `17.24%` trapped, and `80.76%` incomplete |

<details>
<summary>Supporting detail — Seven-bin one-way diagnostic DPM</summary>

| Item | Seven-bin one-way diagnostic DPM |
| --- | --- |
| small-bin incompleteness | is severe: the 14.14 and 24.49 µm bins had no completed tracks |
| These | are diagnostic fate outputs, not a resolved carryover estimate; a bounded tracking-step probe is needed before interpreting the fractions |
| — | The [matched F1/F2 Coupled comparison](../../../../PyAnsys/output/phase8-analysis/26p81-f1-f2-coupled-n10000/summary.json) confirms that both carrier histories have the common report and residual coordinates through N=10,000 |
|  | At the endpoint, F2 routed `99.35%` of Eulerian liquid feed to `steamoutlet` versus F1's `99.73%`; their last-500 mean fractions were `99.40%` and `99.67%` |
|  | F2 had about `1,734 kg` domain liquid inventory versus F1's `1,263 kg` |
| [trajectory figure](../../../../PyAnsys/output/phase8-analysis/26p81-f1-f2-coupled-n10000/f1-f2-coupled-26p81-n10000.png) | shows early transient differences that largely vanish in the outlet fraction by N=10,000 |
| — | This supports a controlled inlet-representation comparison under the Coupled recovery branch, not a meaningful separator-efficiency advantage |
|  | A [non-destructive 200,000-step tracking probe](../../../../PyAnsys/output/phase8-dpm/F2-26p81-dpm-maxsteps-200000-20260928T143334Z/probe.json) on the 14.14 µm bin changed its fates from `613 incomplete` at the original 50,000-step cap to `1 escaped at steamoutlet` and `612 incomplete` |
|  | The per-zone mass summary gives `0.001901 kg/s` escaped and `1.163 kg/s` still incomplete for that bin's diagnostic weights |
|  | Raising this cap fourfold therefore does not resolve its carryover fraction; the saved seven-bin reference child remains unchanged |

</details>

## Coupled speed sweep — 20.11 m/s

| Item | Coupled speed sweep — 20.11 m/s |
| --- | --- |
| — | The [fresh-Hybrid 20.11 m/s F2 pilot](../../../../PyAnsys/output/phase8-carrier/F2-20p11-coupled-gts-20260928T171916Z/manifest.json) applies `87.71494927 kg/s` liquid only to the outer strip and `60.53471824 kg/s` vapor only to the steam face, with the selected Coupled/Global Time Step recovery settings and common reports |
|  | It saved/reopened at N2,000 |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f2-coupled-n2000/assessment.json) fails the carrier gate: mean absolute boundary gap `16.242 kg/s` (`10.96%` of feed) and liquid-inventory slope `+0.29445 kg/steady iteration` (`1,245.792 → 1,393.434 kg`) |
|  | Continuity `0.01003–0.01512` and no-fatal-event checks pass |
| Terminal liquid steam-outlet flow | is `73.729 kg/s` versus `87.715 kg/s` commanded liquid feed |

<details>
<summary>Supporting detail — Coupled speed sweep — 20.11 m/s</summary>

| Item | Coupled speed sweep — 20.11 m/s |
| --- | --- |
| matched F1 pilot also fails, so neither | is ready for one-way DPM at this speed; both need a deeper, matched development horizon |
| — | The [F2 N=5,000 continuation](../../../../PyAnsys/output/phase8-carrier/F2-20p11-coupled-gts-extension-to5000-20260928T175649Z/manifest.json) saved local N3,000/N4,000 checkpoints and reopened its final pair |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f2-coupled-n5000/assessment.json) still fails: mean absolute boundary gap `1.715 kg/s` (`1.16%` of feed) and liquid-inventory slope `+0.01908 kg/steady iteration` (`1,732.720 → 1,742.421 kg`) |
|  | Continuity `0.01328–0.01818` and no-fatal-event checks pass |
| Terminal phase-2 steam-outlet flow | is `86.807 kg/s` (`98.97%` of liquid feed) |
| F2 | is not yet a one-way DPM parent |
| — | The [matched 20.11 m/s trajectory](../../../../PyAnsys/output/phase8-analysis/20p11-f1-f2-coupled-n5000/f1-f2-coupled-20p11-n5000.png) and [summary](../../../../PyAnsys/output/phase8-analysis/20p11-f1-f2-coupled-n5000/summary.json) compare both families on continuous common report coordinates |
|  | Outlet liquid fractions nearly meet by N5,000 (`98.90%` F1, `98.97%` F2), while F2 holds about `1,742 kg` liquid inventory versus F1's `1,002 kg` |
| Neither passes the complete gate, and both | remain poor-separation carriers in this closed-bottom geometry |
| — | The [F2 N=10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F2-20p11-coupled-gts-extension-to10000-20260928T185808Z/manifest.json) saved local N6,000–N9,000 checkpoints and reopened the shared final pair |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f2-coupled-n10000/assessment.json) passes all operational checks: mean absolute boundary gap `0.659 kg/s` (`0.445%` of feed), liquid inventory `1,743.028 → 1,742.983 kg` with slope `−0.0000774 kg/steady iteration`, continuity `0.01392–0.01936`, and no fatal event |
| It | is eligible as a diagnostic DPM parent |
| terminal phase-2 steam-outlet flow | is `87.126 kg/s`, about `99.33%` of commanded liquid feed |
| — | The [matched N=10,000 trajectory](../../../../PyAnsys/output/phase8-analysis/20p11-f1-f2-coupled-n10000/f1-f2-coupled-20p11-n10000.png) and [summary](../../../../PyAnsys/output/phase8-analysis/20p11-f1-f2-coupled-n10000/summary.json) show that both carrier gates pass, yet both route almost all Eulerian liquid feed to the steam outlet: `99.75%` for F1 and `99.33%` for F2 at the endpoint |
| F2's domain liquid inventory | remains about `1,743 kg` versus F1's `1,022 kg` |
| These | are operationally developed, poor-separation carriers; the small outlet-fraction difference is not a credible separator-efficiency benefit |
| — | The [20.11 m/s F2 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F2-diagnostic-050permil-20p11-20260928T194026Z/build.json) saved/reopened the matched seven inert bins with the full Eulerian liquid feed retained, `4.385747463 kg/s` total diagnostic parcel weight, interaction off, the same `steaminlet` release face, and axial release velocity `20.34103 m/s` |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/20p11-f2-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/20p11-f2-diagnostic-dpm/f2-diagnostic-dpm-fates-20p11.png) show `2.12%` escaped, `19.18%` trapped, and `78.70%` incomplete |
|  | The F1/F2 diagnostic escape fractions cannot establish a carryover advantage while most represented weight has no resolved fate |

</details>

## Coupled speed sweep — 23.46 m/s

| Item | Coupled speed sweep — 23.46 m/s |
| --- | --- |
| — | The [F2 Coupled pilot](../../../../PyAnsys/output/phase8-carrier/F2-23p46-coupled-gts-20260928T211344Z/manifest.json) starts independently from the verified numerical-recovery parent, scales the split-phase feeds to 23.46 m/s, fresh-Hybrid initializes, and saves/reopens at N2,000 |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/23p46-f2-coupled-n2000/assessment.json) fails the operational gate: mean absolute boundary gap `16.514 kg/s` (`9.55%` of feed) and liquid-inventory slope `+0.26260 kg/steady iteration` (`1,255.773 → 1,387.622 kg`) |
|  | Continuity `0.01362–0.01872` and no-fatal-event checks pass |
| terminal phase-2 steam-outlet flow | is `88.409 kg/s` versus `102.327 kg/s` commanded liquid feed |
| This | is a preserved development checkpoint, not a diagnostic DPM parent |

<details>
<summary>Supporting detail — Coupled speed sweep — 23.46 m/s</summary>

| Item | Coupled speed sweep — 23.46 m/s |
| --- | --- |
| — | The [N=10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F2-23p46-coupled-gts-extension-to10000-20260928T212957Z/manifest.json) saved local N3,000–N9,000 checkpoints and reopened its final shared pair |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/23p46-f2-coupled-n10000/assessment.json) passes all operational checks: mean absolute boundary gap `0.705 kg/s` (`0.408%` of feed), liquid inventory `1,719.046 → 1,719.234 kg` with slope `+0.000368 kg/steady iteration`, continuity `0.01242–0.01672`, and no fatal event |
| Terminal phase-2 steam-outlet flow | is `101.703 kg/s`, about `99.39%` of commanded liquid feed |
| It | is eligible as a diagnostic DPM parent but does not establish effective separation |
| — | The [matched N=10,000 comparison](../../../../PyAnsys/output/phase8-analysis/23p46-f1-f2-coupled-n10000/summary.json) and [trajectory figure](../../../../PyAnsys/output/phase8-analysis/23p46-f1-f2-coupled-n10000/f1-f2-coupled-23p46-n10000.png) show `99.66%` (F1) and `99.39%` (F2) of inlet liquid leaving through the steam outlet at the endpoint |
| F2 | retains about `1,719 kg` domain liquid versus F1's `1,111 kg` |
| — | Both carriers pass the operational gate; the small outlet-fraction difference is not a credible separator-efficiency benefit in this closed-bottom geometry |
|  | The [23.46 m/s F2 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F2-diagnostic-050permil-23p46-20260928T223330Z/build.json) saved/reopened the matched seven inert bins from its qualified carrier with full Eulerian liquid feed retained, interaction off, the shared `steaminlet` release face, and the declared speed-scaled axial release velocity |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/23p46-f2-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/23p46-f2-diagnostic-dpm/f2-diagnostic-dpm-fates-23p46.png) show `2.10%` escaped, `23.60%` trapped, and `74.30%` incomplete |
|  | The matched F1 diagnostic likewise leaves `71.45%` incomplete; neither escape fraction qualifies as physical carryover efficiency |

</details>

## Coupled speed sweep — 29.48 m/s

| Item | Coupled speed sweep — 29.48 m/s |
| --- | --- |
| — | The [F2 Coupled pilot](../../../../PyAnsys/output/phase8-carrier/F2-29p48-coupled-gts-20260929T001706Z/manifest.json) independently scales the split-phase feeds to `128.584620 kg/s` liquid through the outer strip and `88.740104 kg/s` vapor through the steam face, with fresh Hybrid initialization and common reports |
|  | It saved/reopened its N2,000 endpoint |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/29p48-f2-coupled-n2000/assessment.json) fails the operational carrier gate: mean absolute mixture boundary gap `19.088 kg/s` (`8.783%` of feed) and liquid inventory `1,354.978 → 1,481.704 kg`, slope `+0.25225 kg/steady iteration` |
|  | Continuity `0.01366–0.01878` and no-fatal-event checks pass |
| saved state | is the parent for a [declared N10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F2-29p48-coupled-gts-extension-to10000-20260929T011807Z/manifest.json); it is not yet a diagnostic DPM parent |

<details>
<summary>Supporting detail — Coupled speed sweep — 29.48 m/s</summary>

| Item | Coupled speed sweep — 29.48 m/s |
| --- | --- |
| — | The N10,000 continuation completed, saved local N3,000–N9,000 checkpoints, and reopened its shared final pair |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/29p48-f2-coupled-n10000/assessment.json) passes the operational carrier gate: mean absolute boundary gap `0.911 kg/s` (`0.419%` of feed), liquid inventory `1,806.270 → 1,806.328 kg` with slope `+0.000103 kg/steady iteration`, continuity `0.01293–0.01741`, and no fatal event |
| Terminal liquid through `steamoutlet` | was `127.982 kg/s`, about `99.53%` of inlet liquid |
| It | is eligible for diagnostic DPM, while effective separation remains unproven |
| — | The [matched F1/F2 trajectory](../../../../PyAnsys/output/phase8-analysis/29p48-f1-f2-coupled-n10000/f1-f2-coupled-29p48-n10000.png) and [summary](../../../../PyAnsys/output/phase8-analysis/29p48-f1-f2-coupled-n10000/summary.json) show outlet liquid fractions of `99.66%` (F1) and `99.53%` (F2) at the endpoint, with about `1,429 kg` and `1,806 kg` domain liquid inventory respectively |
|  | Both carriers pass the operational gate, but their outlet routing does not support a meaningful separator-efficiency distinction in this closed-bottom geometry |
|  | The [29.48 m/s F2 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F2-diagnostic-050permil-29p48-20260929T022325Z/build.json) saved/reopened the seven-bin one-way setup from its qualified carrier |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/29p48-f2-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/29p48-f2-diagnostic-dpm/f2-diagnostic-dpm-fates-29p48.png) show `1.85%` escaped, `20.82%` trapped, and `77.33%` incomplete |
| Matched F1 | retains `78.00%` incomplete; the escape fractions are unresolved diagnostics, not physical carryover efficiencies |

</details>

## Coupled speed sweep — 32.14 m/s

| Item | Coupled speed sweep — 32.14 m/s |
| --- | --- |
| — | The [F2 Coupled pilot](../../../../PyAnsys/output/phase8-carrier/F2-32p14-coupled-gts-20260929T042043Z/manifest.json) scaled the verified split-feed recovery parent to 32.14 m/s, fresh-Hybrid initialized, and saved/reopened at N2,000 |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f2-coupled-n2000/assessment.json) fails the carrier gate: mean absolute mixture boundary gap `21.851 kg/s` (`9.222%` of feed) and liquid inventory `1,435.091 → 1,569.345 kg`, slope `+0.26711 kg/steady iteration` |
|  | Continuity `0.01324–0.01971` and no-fatal-event checks pass |
|  | The saved endpoint became the parent for a [declared N10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F2-32p14-coupled-gts-extension-to10000-20260929T043627Z/manifest.json) |
|  | The N10,000 continuation completed, saved local N3,000–N9,000 checkpoints, and reopened its shared final pair |

<details>
<summary>Supporting detail — Coupled speed sweep — 32.14 m/s</summary>

| Item | Coupled speed sweep — 32.14 m/s |
| --- | --- |
| — | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f2-coupled-n10000/assessment.json) passes the operational carrier gate: mean absolute boundary gap `0.974 kg/s` (`0.411%` of feed), liquid inventory `1,910.874 → 1,911.056 kg` with slope `+0.000362 kg/steady iteration`, continuity `0.01264–0.01764`, and no fatal event |
| Terminal phase-2 steam-outlet flow | was `139.410 kg/s`, `99.45%` of commanded liquid feed |
| carrier | is eligible for diagnostic DPM tracking, while effective separation remains unproven |
| — | The [matched F1/F2 trajectory](../../../../PyAnsys/output/phase8-analysis/32p14-f1-f2-coupled-n10000/f1-f2-coupled-32p14-n10000.png) and [summary](../../../../PyAnsys/output/phase8-analysis/32p14-f1-f2-coupled-n10000/summary.json) show endpoint outlet-liquid fractions `99.69%` (F1) and `99.45%` (F2), with domain liquid inventory about `1,630 kg` and `1,911 kg` respectively |
|  | Both carriers pass the operational gate, but their outlet routing does not support a separator-efficiency distinction in this closed-bottom geometry |
|  | The [32.14 m/s F2 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F2-diagnostic-050permil-32p14-20260929T062610Z/build.json) saved/reopened seven one-way inert bins from its qualified carrier |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/32p14-f2-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/32p14-f2-diagnostic-dpm/f2-diagnostic-dpm-fates-32p14.png) show `1.56%` escaped, `18.81%` trapped, and `79.62%` incomplete |
| Matched F1 | retains `82.75%` incomplete; neither escape fraction qualifies as physical carryover efficiency |

</details>

</details>

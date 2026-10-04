# Phase 8 F1 — mixed feed results

| Phase 8 F1 — mixed feed results |
| --- |
| The mixed-feed Coupled sweep has almost unchanged high liquid routing to the steam outlet across speed, while retained liquid mass and pressure difference increase |
| This supplies the mixed-inlet stage of the storyline, including its closed-bottom limitation |

## Comparison basis

| Item | Comparison basis |
| --- | --- |
| — | Five nominal speeds on the same 60,964-cell partition, full Eulerian liquid feed, closed bottom, absorber/EWF off, and matched Coupled/Global Time Step/first-order-k numerics |
|  | Each speed starts with fresh Hybrid initialization and reaches N10,000 |
| Routing and pressure summaries use N9,500–10,000; inventories | are final snapshots |
| These Coupled cases | are numerical adaptations of the SIMPLE recreation |
| — | The main sweep assigns mixed-phase feed to both original inlet faces |
| separately recreated merged single-inlet SIMPLE case | is shown below and must not be conflated with this two-face sweep |

## Higher speed changes inventory and pressure, with little change in outlet routing

| Higher speed changes inventory and pressure, with little change in outlet routing |
| --- |
| Across 20.11–32.14 m/s, F1's outlet fraction stays within 99.65–99.73%, but its final liquid inventory rises from 1,021.5 to 1,629.6 kg, an increase of about 60% |
| The inlet-to-outlet pressure difference rises from 43.29 to 100.88 kPa |
| Thus, the speed sweep changes the internal state and pressure requirement much more than the fraction of liquid reaching the steam outlet |

![F1 speed response](figures/speed-response.png)

| Speed (m/s) | Outlet liquid / feed, last-500 mean (%) | Final liquid inventory (kg) | Steam-face–outlet pressure difference (kPa) | Unresolved diagnostic DPM weight (%) |
| ---: | ---: | ---: | ---: | ---: |
| 20.11 | 99.728 | 1021.5 | 43.29 | 59.93 |
| 23.46 | 99.651 | 1110.8 | 56.18 | 71.45 |
| 26.81 | 99.671 | 1262.6 | 71.09 | 77.30 |
| 29.48 | 99.653 | 1428.9 | 84.97 | 78.00 |
| 32.14 | 99.664 | 1629.6 | 100.88 | 82.75 |

![F1 routing and inventory histories](figures/routing-inventory-history.png)

| Item | Higher speed changes inventory and pressure, with little change in outlet routing |
| --- | --- |
| — | The raw histories distinguish the evolving carrier from its final checkpoint |
| Inventory | is Eulerian liquid mass, not removed liquid |
| pressure metric | uses the recorded area-weighted `steaminlet` and `steamoutlet` reports; it is not a mass-weighted pressure loss |

## Retained liquid occupies the lower region and outer wall

| Reference snapshot | Vertical liquid distribution | Inlet-plane circulation |
| --- | --- | --- |
| F1-26.81-n10000 | ![F1-26.81-n10000 liquid](figures/F1-26.81-n10000-liquid.png) | ![F1-26.81-n10000 inlet-vectors](figures/F1-26.81-n10000-inlet-vectors.png) |

| Item | Retained liquid occupies the lower region and outer wall |
| --- | --- |
| The centre cut and inlet slice answer different questions | the first shows vertical liquid distribution; the second retains the offset inlet and shows circumferential flow |
|  | Compare speed cases within the same numerical branch and horizon |
|  | The SIMPLE reconstruction is reported separately in F0, including its matched N10,000 series and earlier topology variants |
| — | Reference-speed gauge pressure: |

![F1-26.81-n10000 pressure](figures/F1-26.81-n10000-pressure.png)

*Figure F1.3. Reference-speed F1 carrier at N10,000, with a separate gauge-pressure view above. The centre cut identifies lower-region and wall enrichment; inlet-plane vectors show circumferential circulation. These local views support the inventory interpretation without measuring removal.*

| Item | Retained liquid occupies the lower region and outer wall |
| --- | --- |
| — | The mixed-feed centre cuts retain liquid enrichment at the bottom and along the outer walls |
|  | The wall band becomes more pronounced at the higher speeds, consistent with the increasing domain inventory |
| Most of the central annular bulk | remains at low liquid volume fraction on the shared 0–1 scale |
| — | The inlet-plane arrows turn around the central exclusion and show circulation rather than a direct inlet-to-outlet path |
| These | are local field observations, not a liquid removal measurement |

## Diagnostic droplets reveal unresolved transport rather than a complete separation result

| Diagnostic droplets reveal unresolved transport rather than a complete separation result |
| --- |
| F1's unresolved injection-weighted fraction rises from 59.93% at 20.11 m/s to 82.75% at 32.14 m/s |
| The apparent decline in completed fates with speed must therefore be read alongside a growing unresolved category |

![F1 seven-bin fates at every speed](figures/droplet-bin-fates.png)

![F1 droplet speed response](figures/droplet-speed-response.png)

| Item | Diagnostic droplets reveal unresolved transport rather than a complete separation result |
| --- | --- |
| left plot | uses injection-weighted fate fractions; the right gives the incomplete trajectory fraction in each size bin |
| — | Both retain incomplete tracks |
|  | Diagnostic parcel weights do not add physical inlet mass to these full-Eulerian-feed carriers |
|  | High unresolved fractions prevent converting escaped weight into separator efficiency |
|  | F1 reference one-way DPM — inlet stream 0: |

| 7.07 µm | 34.64 µm | 89.44 µm |
| --- | --- | --- |
| ![F1-26.81-diagnostic stream 0 07](figures/F1-26.81-diagnostic-track-07um-stream0.png) | ![F1-26.81-diagnostic stream 0 35](figures/F1-26.81-diagnostic-track-35um-stream0.png) | ![F1-26.81-diagnostic stream 0 89](figures/F1-26.81-diagnostic-track-89um-stream0.png) |

| Item | Diagnostic droplets reveal unresolved transport rather than a complete separation result |
| --- | --- |
| Each row | shows three deterministic illustrative paths, not a statistical sample |
| — | Native zone outlines provide vessel/inlet/outlet context; path colour represents diameter on the shared 5–100 µm range |
| line endpoint alone | is not a fate classification |
| saved tracking controls | were retained; no carrier iterations or source-case saves were issued |
| — | Diameter-resolved fate plots, rather than these selected paths, describe the full tracked ensemble |

## Numerical context

![F1 numerical context](figures/numerical-context.png)

| Item | Numerical context |
| --- | --- |
| reported boundary gap and continuity | are supporting diagnostics |
| Reverse outlet flow and viscosity limiting | were recorded in these runs; a low residual or bounded inventory does not validate the closed-bottom separator |
| — | See the [phase result](../results.md) for the matched F1/F2 comparison |

## F0 comparison

| Item | F0 comparison |
| --- | --- |
| mixed-inlet SIMPLE reconstruction and its diagnostic DPM | are now [F0](../f0-simple/results.md) |
| — | F1 contains the Coupled series |
|  | Compare the two numerical packages at N10,000 with N9,500–10,000 windows; retain original artifact IDs |

The reported boundary gap and continuity are supporting diagnostics. Reverse outlet flow and viscosity limiting were recorded in these runs; a low residual or bounded inventory does not validate the closed-bottom separator. See the [phase result](../results.md) for the matched F1/F2 comparison.

## SIMPLE versus Coupled: matched outcomes, different numerical packages

![F1 SIMPLE versus Coupled carrier comparison](figures/f1-simple-vs-coupled-n10000.png)

*Replotted from the rounded values in the table below; original machine-generated plot unavailable in this checkout.*

| Speed (m/s) | Steam-outlet liquid / feed, Coupled → SIMPLE (%) | Final liquid inventory, Coupled → SIMPLE (kg) | Pressure difference, Coupled → SIMPLE (kPa) |
| ---: | ---: | ---: | ---: |
| 20.11 | 99.728 → 214.437 | 1021.5 → 3802.5 | 43.29 → 107.80 |
| 23.46 | 99.651 → 258.911 | 1110.8 → 5274.2 | 56.18 → 198.18 |
| 26.81 | 99.671 → 360.424 | 1262.6 → 6576.7 | 71.09 → 406.52 |
| 29.48 | 99.653 → 455.273 | 1428.9 → 7339.8 | 84.97 → 546.56 |
| 32.14 | 99.664 → 673.023 | 1629.6 → 8160.3 | 100.88 → 843.23 |

SIMPLE numerical diagnostics over N9,500–10,000:

| Speed (m/s) | SIMPLE mixture boundary gap (% feed) | SIMPLE inventory slope (kg/iteration) | SIMPLE max continuity residual | Reverse-flow messages | Viscosity-limit messages |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20.11 | 67.27 | 0.486 | 0.256 | 9998 | 9740 |
| 23.46 | 93.42 | 0.582 | 0.389 | 9998 | 9768 |
| 26.81 | 153.14 | 0.741 | 0.680 | 9998 | 9760 |
| 29.48 | 208.93 | 1.111 | 1.086 | 9998 | 9770 |
| 32.14 | 336.85 | 0.047 | 1.162 | 9998 | 9783 |

Both series use the same two-face F1 topology, five total-feed targets, 60,964-cell mesh and fresh initialized parent, with N10,000 endpoints and N9,500–10,000 response windows. The SIMPLE branch uses segregated pseudo-time off and second-order `k`; the comparison branch uses Coupled/Global Time Step and first-order `k`. This is a numerical-package comparison. It does not isolate the pressure-coupling algorithm from the discretization and time-stepping changes. These diagnostics describe numerical limitations; they are not Phase 8 progression gates.

Reference-speed native liquid contours and inlet vectors at the same N10,000 horizon:

| SIMPLE package | Coupled recovery package |
| --- | --- |
| ![F1-26.81-simple-n10000 liquid](figures/F1-26.81-simple-n10000-liquid.png) | ![F1-26.81-n10000 liquid](figures/F1-26.81-n10000-liquid.png) |
| ![F1-26.81-simple-n10000 inlet-vectors](figures/F1-26.81-simple-n10000-inlet-vectors.png) | ![F1-26.81-n10000 inlet-vectors](figures/F1-26.81-n10000-inlet-vectors.png) |

Historical [08b setup](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md) and [results](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/results.md) remain separate comparison anchors: the documented run used split `liquidinlet`/`steaminlet` mass-flow boundaries on 7,601,261 cells and its N5,000 carrier report showed a 58.73% mixture imbalance ratio. F1 SIMPLE shares the audited 00a SIMPLE/second-order/QUICK numerical-method family, but F1 applies mixed-phase feed to both inlet faces on 60,964 cells. SIMPLE alone therefore does not make this a topology-, mesh-, or result-identical 08b replication.
### One-way DPM diagnostics on the SIMPLE carriers

![F1 SIMPLE carrier one-way DPM diagnostic fates](figures/f1-simple-diagnostic-dpm-fates.png)

*Replotted from the rounded values in the table below; original machine-generated plot unavailable in this checkout.*

| Speed (m/s) | Escaped represented weight (%) | Trapped represented weight (%) | Incomplete represented weight (%) |
| ---: | ---: | ---: | ---: |
| 20.11 | 0.08 | 0.01 | 99.91 |
| 23.46 | 5.12 | 1.24 | 93.65 |
| 26.81 | 0.18 | 11.79 | 88.03 |
| 29.48 | 4.72 | 0.23 | 95.05 |
| 32.14 | 6.19 | 1.32 | 92.49 |

These seven-bin cases use 5% inert, one-way DPM weight, a 50,000-step tracking cap, and the same full-feed Eulerian SIMPLE carriers. The large incomplete share is unresolved trajectory weight. The fates are diagnostic outcomes on numerically poor carriers, not separator efficiency or validated separation.


## What this stage establishes

F1 supplies the mixed-feed reference: more speed produces more retained liquid and a larger pressure difference, without resolving the high steam-outlet liquid routing. This motivates comparing the inlet representation in F2 and following droplets separately in F3. The five-speed SIMPLE reconstruction is reported separately from the selected Coupled adaptation: it exposes large mixture-boundary gaps and inventory drift, so its outlet ratios and diagnostic DPM fates cannot be read as separation performance. Its connection to historical 08b is numerical-method lineage, not exact topology or mesh parity.

## Supporting spatial atlas

<details>
<summary>All saved case contours and vectors</summary>
| Saved snapshot | Liquid, vertical cut | Liquid, inlet slice | Vertical vectors | Inlet vectors |
| --- | --- | --- | --- | --- |
| F1 20.11 m/s N10000 | ![F1-20.11-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-20.11-n10000-liquid.png>) | ![F1-20.11-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-20.11-n10000-inlet-liquid.png>) | ![F1-20.11-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-20.11-n10000-vertical-vectors.png>) | ![F1-20.11-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-20.11-n10000-inlet-vectors.png>) |
| F1 23.46 m/s N10000 | ![F1-23.46-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-23.46-n10000-liquid.png>) | ![F1-23.46-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-23.46-n10000-inlet-liquid.png>) | ![F1-23.46-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-23.46-n10000-vertical-vectors.png>) | ![F1-23.46-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-23.46-n10000-inlet-vectors.png>) |
| F1 26.81 m/s N10000 | ![F1-26.81-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-liquid.png>) | ![F1-26.81-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-inlet-liquid.png>) | ![F1-26.81-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-vertical-vectors.png>) | ![F1-26.81-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-26.81-n10000-inlet-vectors.png>) |
| F1 29.48 m/s N10000 | ![F1-29.48-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-29.48-n10000-liquid.png>) | ![F1-29.48-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-29.48-n10000-inlet-liquid.png>) | ![F1-29.48-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-29.48-n10000-vertical-vectors.png>) | ![F1-29.48-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-29.48-n10000-inlet-vectors.png>) |
| F1 32.14 m/s N10000 | ![F1-32.14-n10000 liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-32.14-n10000-liquid.png>) | ![F1-32.14-n10000 inlet-liquid](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-32.14-n10000-inlet-liquid.png>) | ![F1-32.14-n10000 vertical-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-32.14-n10000-vertical-vectors.png>) | ![F1-32.14-n10000 inlet-vectors](<C:/Users/Shuhei Yokkaichi/Documents/CFD/P4P_knowledgeWiki/Project/experiments/phase-08-storyline-reconstruction/f1-one-inlet/figures/F1-32.14-n10000-inlet-vectors.png>) |

| F1 20.11 m/s N10000 | ![F1-20.11-n10000 liquid](figures/F1-20.11-n10000-liquid.png) | ![F1-20.11-n10000 inlet-liquid](figures/F1-20.11-n10000-inlet-liquid.png) | ![F1-20.11-n10000 vertical-vectors](figures/F1-20.11-n10000-vertical-vectors.png) | ![F1-20.11-n10000 inlet-vectors](figures/F1-20.11-n10000-inlet-vectors.png) |
| F1 23.46 m/s N10000 | ![F1-23.46-n10000 liquid](figures/F1-23.46-n10000-liquid.png) | ![F1-23.46-n10000 inlet-liquid](figures/F1-23.46-n10000-inlet-liquid.png) | ![F1-23.46-n10000 vertical-vectors](figures/F1-23.46-n10000-vertical-vectors.png) | ![F1-23.46-n10000 inlet-vectors](figures/F1-23.46-n10000-inlet-vectors.png) |
| F1 26.81 m/s N10000 | ![F1-26.81-n10000 liquid](figures/F1-26.81-n10000-liquid.png) | ![F1-26.81-n10000 inlet-liquid](figures/F1-26.81-n10000-inlet-liquid.png) | ![F1-26.81-n10000 vertical-vectors](figures/F1-26.81-n10000-vertical-vectors.png) | ![F1-26.81-n10000 inlet-vectors](figures/F1-26.81-n10000-inlet-vectors.png) |
| F1 29.48 m/s N10000 | ![F1-29.48-n10000 liquid](figures/F1-29.48-n10000-liquid.png) | ![F1-29.48-n10000 inlet-liquid](figures/F1-29.48-n10000-inlet-liquid.png) | ![F1-29.48-n10000 vertical-vectors](figures/F1-29.48-n10000-vertical-vectors.png) | ![F1-29.48-n10000 inlet-vectors](figures/F1-29.48-n10000-inlet-vectors.png) |
| F1 32.14 m/s N10000 | ![F1-32.14-n10000 liquid](figures/F1-32.14-n10000-liquid.png) | ![F1-32.14-n10000 inlet-liquid](figures/F1-32.14-n10000-inlet-liquid.png) | ![F1-32.14-n10000 vertical-vectors](figures/F1-32.14-n10000-vertical-vectors.png) | ![F1-32.14-n10000 inlet-vectors](figures/F1-32.14-n10000-inlet-vectors.png) |
| F1 SIMPLE original faces N2000 | ![F1-simple-mixed liquid](figures/F1-simple-mixed-liquid.png) | ![F1-simple-mixed inlet-liquid](figures/F1-simple-mixed-inlet-liquid.png) | ![F1-simple-mixed vertical-vectors](figures/F1-simple-mixed-vertical-vectors.png) | ![F1-simple-mixed inlet-vectors](figures/F1-simple-mixed-inlet-vectors.png) |
| F1 SIMPLE merged single inlet N2000 | ![F1-simple-single liquid](figures/F1-simple-single-liquid.png) | ![F1-simple-single inlet-liquid](figures/F1-simple-single-inlet-liquid.png) | ![F1-simple-single vertical-vectors](figures/F1-simple-single-vertical-vectors.png) | ![F1-simple-single inlet-vectors](figures/F1-simple-single-inlet-vectors.png) |
| F1 20.11 m/s SIMPLE original two faces N10000 | ![F1-20.11-simple-n10000 liquid](figures/F1-20.11-simple-n10000-liquid.png) | ![F1-20.11-simple-n10000 inlet-liquid](figures/F1-20.11-simple-n10000-inlet-liquid.png) | ![F1-20.11-simple-n10000 vertical-vectors](figures/F1-20.11-simple-n10000-vertical-vectors.png) | ![F1-20.11-simple-n10000 inlet-vectors](figures/F1-20.11-simple-n10000-inlet-vectors.png) |
| F1 23.46 m/s SIMPLE original two faces N10000 | ![F1-23.46-simple-n10000 liquid](figures/F1-23.46-simple-n10000-liquid.png) | ![F1-23.46-simple-n10000 inlet-liquid](figures/F1-23.46-simple-n10000-inlet-liquid.png) | ![F1-23.46-simple-n10000 vertical-vectors](figures/F1-23.46-simple-n10000-vertical-vectors.png) | ![F1-23.46-simple-n10000 inlet-vectors](figures/F1-23.46-simple-n10000-inlet-vectors.png) |
| F1 26.81 m/s SIMPLE original two faces N10000 | ![F1-26.81-simple-n10000 liquid](figures/F1-26.81-simple-n10000-liquid.png) | ![F1-26.81-simple-n10000 inlet-liquid](figures/F1-26.81-simple-n10000-inlet-liquid.png) | ![F1-26.81-simple-n10000 vertical-vectors](figures/F1-26.81-simple-n10000-vertical-vectors.png) | ![F1-26.81-simple-n10000 inlet-vectors](figures/F1-26.81-simple-n10000-inlet-vectors.png) |
| F1 29.48 m/s SIMPLE original two faces N10000 | ![F1-29.48-simple-n10000 liquid](figures/F1-29.48-simple-n10000-liquid.png) | ![F1-29.48-simple-n10000 inlet-liquid](figures/F1-29.48-simple-n10000-inlet-liquid.png) | ![F1-29.48-simple-n10000 vertical-vectors](figures/F1-29.48-simple-n10000-vertical-vectors.png) | ![F1-29.48-simple-n10000 inlet-vectors](figures/F1-29.48-simple-n10000-inlet-vectors.png) |
| F1 32.14 m/s SIMPLE original two faces N10000 | ![F1-32.14-simple-n10000 liquid](figures/F1-32.14-simple-n10000-liquid.png) | ![F1-32.14-simple-n10000 inlet-liquid](figures/F1-32.14-simple-n10000-inlet-liquid.png) | ![F1-32.14-simple-n10000 vertical-vectors](figures/F1-32.14-simple-n10000-vertical-vectors.png) | ![F1-32.14-simple-n10000 inlet-vectors](figures/F1-32.14-simple-n10000-inlet-vectors.png) |

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

# F1 26.81 m/s base preparation

## Artifact and provenance

| Item | Artifact and provenance |
| --- | --- |
| — | On `student`, Fluent 2025 R2 Student Edition loaded the Phase 7.2A Family E0 prepared case `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase72A\FamilyE\E0\20260922T115500Z\P72A-E0-prepared.cas.h5` (SHA-256 `1c5b1a5f5e68fcc6ff7248b50f6df83e788363faf7492315da42960fbce3e9f5`) |
|  | The saved F1 pair is: |
| Case | `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F1\F1-mixed-26p81-base.cas.h5` (SHA-256 `653b5e9d0f95886ab6a1ee20787b4e97d25f8c63027c375969ef6073460d770c`) |
| Data | `C:\Users\Shuhei Yokkaichi\Documents\FluentRuns\Phase8\F1\F1-mixed-26p81-base.dat.h5` (SHA-256 `e8c12cedd721b56143077ffa3ecb11965538f5d494fa4c991bda5a7533d8be6f`) |
| Machine builder | [`build_phase8_f1_from_p72a_e0.py`](../../../../PyAnsys/scripts/setup/build_phase8_f1_from_p72a_e0.py). [Readback receipt](../../../../PyAnsys/output/phase8_f1_base_20260926.json) |

## Verified F1 setup

| Item | Verified F1 setup |
| --- | --- |
| child | retained the Phase 7.2A `60,964`-cell geometry and its two fluid zones, but sources are disabled in both zones for all phases |
| absorber partition | is geometrically present; it removes no mass or momentum |
| — | The mesh check passed |
| `bottom` | remains a wall, `steamoutlet` a pressure outlet, EWF off, roughness zero, DPM interaction off, and all six inherited injections removed |
| Phase 7 report definitions, report files, and absorber expressions | were removed |

<details>
<summary>Supporting detail — Verified F1 setup</summary>

| Item | Verified F1 setup |
| --- | --- |
| live inlet areas | were `0.0048899165 m²` (`liquidinlet`) and `0.51928608 m²` (`steaminlet`) |
| With the | retained phase densities (`5.79743385` and `881.21087646 kg/m³`) and 1600 kJ/kg mass proportion, the read-back total feeds are `80.70292372 kg/s` vapor and `116.93872650 kg/s` liquid, giving the nominal combined volumetric speed `26.81 m/s` |
| Both phases | were apportioned to each face by its area |
| — | Coupled pressure–velocity with steady Global Time Step remained from the Phase 7.2A parent |
| A fresh Hybrid field | was initialized; the parent data field was not carried over |
| — | Case and data reopened with the same critical readbacks |
| This | is a prepared base, not a developed carrier or a DPM result |
| — | Phase 8 report definitions and file destinations, the carrier development window, and the seven-bin 09cV3 post-development injection still need to be installed/verified before the F1 run |

</details>

### Surface-tension audit (2026-09-26)

| Item | Surface-tension audit (2026-09-26) |
| --- | --- |
| prepared model | is Fluent 2025 R2 Mixture |
| Its `setup.models.multiphase.phase_interaction` and `liquid_surface_tension` branches | are inactive, so no bulk interfacial surface-tension force or coefficient is active in F1 |
| — | The source paper reports `0.0411 N/m` at the separator condition, but that number is a reference property here, not a saved solver setting |
|  | The official Fluent 2025 R2 model documentation lists surface-tension force modeling for VOF and Eulerian, while the current Mixture branch exposes no active setting |
|  | A carrier-model change would alter the Phase 8 family contract and is awaiting a scientific decision |

## Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29)

| Item | Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29) |
| --- | --- |
| — | The [parity builder](../../../../PyAnsys/scripts/setup/build_phase8_purnanto_parity_pilots.py) saved/reopened a new F1 child with SIMPLE, steady pseudo-time off, second-order `k`, and `0.724 m` turbulence hydraulic diameter on both inlet faces and the outlet backflow |
| Its | retained two-face geometry is still an approximation to Purnanto's single inlet |
| child case/data hashes and full setting readback | are in the [builder receipt](../../../../PyAnsys/output/phase8_purnanto_parity_pilots_20260928T110152Z.json) |
| No active Mixture surface-tension force | was introduced |
| common 17-report package | recorded all 10-iteration coordinates through the 2,000-iteration carrier pilot; the final pair reopened. [Run manifest](../../../../PyAnsys/output/phase8-carrier/F1-26p81-20260928T112326Z/manifest.json) records checkpoint hashes, settings, and local monitor/transcript paths |

<details>
<summary>Supporting detail — Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29)</summary>

| Item | Purnanto-parity child: 26.81 m/s carrier pilot (2026-09-29) |
| --- | --- |
| — | The [paired numerical summary](../../../../PyAnsys/output/phase8-analysis/26p81-purnanto-parity/summary.json) and [trajectory figure](../../../../PyAnsys/output/phase8-analysis/26p81-purnanto-parity/f1-f2-carrier-26p81.png) compare F1 with matched F2 |
| At N=2,000, mixture inlet flow | was `197.642 kg/s`, outlet flow `119.867 kg/s`, and boundary imbalance `77.775 kg/s` (39.35% of feed) |
| Steam-outlet liquid | was `38.687 kg/s`, 33.08% of liquid feed |
| — | Whole-domain liquid inventory rose from `562.80` to `824.92 kg` over N=1,500–2,000, with fitted slope `0.519 kg/steady iteration` |
| Continuity residual | was `0.0970`; reversed outlet flow and turbulence-viscosity limiting occurred repeatedly |
| slope | is not a physical storage rate |
| — | This endpoint fails the steady carrier qualification gate and cannot support a separation-efficiency claim |

</details>

## Matched Coupled numerical-recovery carrier

| Item | Matched Coupled numerical-recovery carrier |
| --- | --- |
| — | The [F1 recovery builder](../../../../PyAnsys/output/phase8_numerical_recovery_f1_20260928T131400Z.json) saved/reopened a fresh-Hybrid child retaining the corrected mixed two-face feed and turbulence inputs while restoring the same Coupled/Global Time Step/first-order-`k` methods as F2's recovery child |
|  | Direct method and turbulence readbacks match F2 |
| This | is not Purnanto SIMPLE parity |
| — | The [N=2,000 pilot](../../../../PyAnsys/output/phase8-carrier/F1-26p81-coupled-gts-20260928T131505Z/manifest.json) saved/reopened its final pair |
|  | The declared [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f1-coupled-n2000/assessment.json) fails two operational checks: mean absolute mixture boundary gap `10.097 kg/s` (`5.11%` of feed) and liquid-inventory slope `0.1400 kg/steady iteration` (`1,059.858 → 1,130.201 kg`) |

<details>
<summary>Supporting detail — Matched Coupled numerical-recovery carrier</summary>

| Item | Matched Coupled numerical-recovery carrier |
| --- | --- |
| — | Continuity stayed within `0.01045–0.01554`, without a fatal event, but reversed outlet flow and viscosity limiting persisted |
| endpoint remained a development checkpoint and | was continued without F1 DPM activation |
| — | The [N=5,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-26p81-coupled-gts-extension-to5000-20260928T133645Z/manifest.json) saved/reopened its final pair |
| Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f1-coupled-n5000/assessment.json) | shows mean absolute boundary gap `1.324 kg/s` (`0.670%` of feed), terminal liquid outlet `115.863 kg/s`, and continuity `0.01018–0.01418` |
| — | Liquid inventory still rose `1,235.785 → 1,242.380 kg`, fitted slope `0.01314 kg/steady iteration`, just outside the `0.01` operational limit |
|  | Reversed outlet flow and viscosity limiting persisted |
| This | is not yet a DPM parent; the same state is being continued to N=10,000 for qualification and a matched F2 horizon |
| — | The [N=10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-26p81-coupled-gts-extension-to10000-20260928T135803Z/manifest.json) completed, saved, and reopened its final case/data pair |
|  | Its [declared last-500 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f1-coupled-n10000/assessment.json) passes all four operational checks: mean absolute mixture boundary gap `0.4700 kg/s` (`0.2378%` of feed), fitted liquid-inventory slope `0.0008653 kg/steady iteration` (`1,262.167 → 1,262.612 kg`), continuity `0.009412–0.014028`, and no fatal event |
| terminal liquid outlet | is `116.623 kg/s`, `99.73%` of the liquid feed |
| — | Reverse outlet flow and turbulence-viscosity limiting persisted throughout the continuation |
| F1 | is now a qualified *diagnostic-DPM parent* under the declared operational gate, not a validated separator or a Purnanto reproduction |
| — | The [matched F1/F2 Coupled comparison](../../../../PyAnsys/output/phase8-analysis/26p81-f1-f2-coupled-n10000/summary.json) and [trajectory figure](../../../../PyAnsys/output/phase8-analysis/26p81-f1-f2-coupled-n10000/f1-f2-coupled-26p81-n10000.png) verify continuous report and residual coordinates through N=10,000 |
|  | At the endpoint, F1 routed `99.73%` and F2 `99.35%` of Eulerian liquid feed to `steamoutlet`; the last-500 means were `99.67%` and `99.40%` |
| F1 | retained about `1,263 kg` liquid inventory versus F2's `1,734 kg` |
| This | is a reproducible inlet-representation contrast under the Coupled recovery numerics, with poor liquid separation in both cases |

</details>

## Seven-bin one-way diagnostic DPM

| Item | Seven-bin one-way diagnostic DPM |
| --- | --- |
| [F1 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-26p81-20260928T143528Z/build.json) | was saved/reopened from the qualified N=10,000 carrier with the same seven-bin 09cV3 particle specification and `5.846936325 kg/s` *diagnostic* parcel-weight scale as F2 |
| full Eulerian liquid feed | remains in the carrier; one-way tracking adds no carrier source feedback |
| — | Fluent tracked `613` trajectories per bin with per-zone summaries |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/26p81-f1-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/26p81-f1-diagnostic-dpm/f1-diagnostic-dpm-fates-26p81.png) report `1.63%` escaped, `21.07%` trapped, and `77.30%` incomplete |
|  | The 14.14 µm bin had all `613` tracks incomplete; the 24.49 µm bin had `608` incomplete |
|  | These unresolved fates preclude a physical F1/F2 DPM carryover comparison |

## Separately named true single-face Purnanto-style child

| Separately named true single-face Purnanto-style child |
| --- |
| The [single-face builder](../../../../PyAnsys/scripts/setup/build_phase8_f1_single_face_parity.py) merged the two identically conditioned mass-flow-inlet face zones in a copy of the saved F1 SIMPLE parity child |
| It then reapplied the combined `80.70292372 kg/s` vapor and `116.93872650 kg/s` liquid feeds, performed fresh Hybrid initialization, checked the mesh, and saved/reopened a new pair |
| The [build receipt](../../../../PyAnsys/output/phase8-single-face/F1-single-face-parity-26p81-20260928T162910Z/build.json) reads back one `liquidinlet` face zone of `0.524176 m²`, `0.724 m` turbulence hydraulic diameter, `2.11%` turbulence intensity, SIMPLE, pseudo-time off, and second-order `k` |
| This addresses the original two-face approximation as a separate Purnanto-style carrier setup |
| The initialized build has no DPM result, and it cannot use the matched two-face `steaminlet` release footprint without a separately defined injection surface |

<details>
<summary>Supporting detail — Separately named true single-face Purnanto-style child</summary>

| Separately named true single-face Purnanto-style child |
| --- |
| The separate [2,000-iteration single-face pilot](../../../../PyAnsys/output/phase8-single-face/F1-single-face-SIMPLE-26p81-20260928T165448Z/manifest.json) saved a local N1,000 checkpoint and reopened its selected final pair |
| Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/26p81-f1-single-face-simple-n2000/assessment.json) fails the carrier gate: mean absolute boundary gap `84.262 kg/s` (`42.63%` of feed), liquid inventory `562.665 → 824.682 kg` (`+0.51861 kg/steady iteration`), and continuity `0.09366–0.19237` |
| Its terminal boundary gap `77.667 kg/s`, phase-2 outlet `38.754 kg/s`, and inventory `824.682 kg` are close to the earlier two-face SIMPLE F1 terminal `77.775 kg/s`, `38.687 kg/s`, and `824.92 kg` |
| The face merge resolved the inlet-zone lineage distinction, but did not cure the open balance or establish a usable separator carrier |

</details>

## Coupled speed sweep — 20.11 m/s

| Item | Coupled speed sweep — 20.11 m/s |
| --- | --- |
| — | The [fresh-Hybrid 20.11 m/s F1 pilot](../../../../PyAnsys/output/phase8-carrier/F1-20p11-coupled-gts-20260928T170440Z/manifest.json) scaled both inlet-face phase feeds by `20.11/26.81`, kept the selected Coupled/Global Time Step recovery numerics, and saved/reopened at N2,000 |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f1-coupled-n2000/assessment.json) fails the operational carrier gate: mean absolute mixture boundary gap `5.928 kg/s` (`4.00%` of feed) and liquid-inventory slope `+0.1027 kg/steady iteration` (`853.488 → 905.129 kg`) |
|  | Continuity `0.00916–0.01319` and no-fatal-event checks pass |
| Terminal phase-2 steam-outlet flow | is `83.187 kg/s` versus `87.715 kg/s` commanded liquid feed |
| This | is a development checkpoint, not a DPM parent |

<details>
<summary>Supporting detail — Coupled speed sweep — 20.11 m/s</summary>

| Item | Coupled speed sweep — 20.11 m/s |
| --- | --- |
| — | The [N=5,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-20p11-coupled-gts-extension-to5000-20260928T173433Z/manifest.json) saved local N3,000/N4,000 checkpoints and reopened its final pair |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f1-coupled-n5000/assessment.json) passes mixture boundary balance at `1.014 kg/s` (`0.684%` of feed), continuity `0.00819–0.01151`, and no fatal event |
|  | Liquid inventory still rose `994.571 → 1,001.721 kg`, fitted `+0.01431 kg/steady iteration`, just beyond the `0.01` operational threshold |
| terminal phase-2 steam-outlet flow | was `86.749 kg/s` (`98.90%` of liquid feed) |
| This | is still a development checkpoint, not a DPM parent |
| — | The [N=10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-20p11-coupled-gts-extension-to10000-20260928T182041Z/manifest.json) saved local N6,000–N9,000 checkpoints and reopened the shared final pair |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/20p11-f1-coupled-n10000/assessment.json) passes all operational checks: mean absolute boundary gap `0.291 kg/s` (`0.196%` of feed), liquid inventory `1,021.187 → 1,021.502 kg` with slope `+0.000616 kg/steady iteration`, continuity `0.00754–0.01232`, and no fatal event |
| It | is eligible as a diagnostic DPM parent |
| terminal phase-2 steam-outlet flow | is `87.499 kg/s`, about `99.75%` of commanded liquid feed; carrier development does not establish effective separation |
| — | The [20.11 m/s F1 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-20p11-20260928T193646Z/build.json) saved/reopened seven inert bins with the full Eulerian liquid feed retained, `4.385747463 kg/s` total diagnostic parcel weight, interaction off, the shared `steaminlet` release face, and speed-scaled axial release velocity `20.34103 m/s` |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/20p11-f1-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/20p11-f1-diagnostic-dpm/f1-diagnostic-dpm-fates-20p11.png) show `3.90%` escaped, `36.16%` trapped, and `59.93%` incomplete |
| Diagnostic parcel weight | is not additional physical feed, and incomplete tracks remain unresolved |

</details>

## Coupled speed sweep — 23.46 m/s

| Item | Coupled speed sweep — 23.46 m/s |
| --- | --- |
| An accidental [SIMPLE start manifest](../../../../PyAnsys/output/phase8-carrier/F1-23p46-20260928T194516Z/manifest.json) | was identified before carrier iteration, interrupted, and excluded from this Coupled comparison |
| Its initialized start pair | is preserved and no Fluent process from that attempt remains active |
| — | The corrected [F1 Coupled pilot](../../../../PyAnsys/output/phase8-carrier/F1-23p46-coupled-gts-20260928T194751Z/manifest.json) starts independently from the verified numerical-recovery parent, scales the phase feeds to 23.46 m/s, fresh-Hybrid initializes, and saves/reopens at N2,000 |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/23p46-f1-coupled-n2000/assessment.json) fails the operational carrier gate: mean absolute mixture boundary gap `7.129 kg/s` (`4.12%` of feed) and liquid-inventory slope `+0.10821 kg/steady iteration` (`946.992 → 1,001.519 kg`) |
|  | Continuity `0.01023–0.01446` and no-fatal-event checks pass |

<details>
<summary>Supporting detail — Coupled speed sweep — 23.46 m/s</summary>

| Item | Coupled speed sweep — 23.46 m/s |
| --- | --- |
| saved state | is being continued to a declared N10,000 horizon before DPM eligibility is reconsidered |
| — | The [N=10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-23p46-coupled-gts-extension-to10000-20260928T200321Z/manifest.json) saved local N3,000–N9,000 checkpoints, saved and reopened the final shared pair, and passed its [last-500 operational assessment](../../../../PyAnsys/output/phase8-analysis/23p46-f1-coupled-n10000/assessment.json): mean absolute boundary gap `0.426 kg/s` (`0.246%` of feed), liquid inventory `1,110.235 → 1,110.796 kg` with slope `+0.001133 kg/steady iteration`, continuity `0.00927–0.01323`, and no fatal event |
| Terminal phase-2 steam-outlet flow | is `101.980 kg/s`; carrier development still does not establish effective separation |
| — | The [23.46 m/s F1 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-23p46-20260928T222919Z/build.json) saved/reopened seven inert bins from this qualified carrier with the full Eulerian liquid feed retained, one-way interaction off, the shared `steaminlet` release face, and the declared speed-scaled axial release velocity |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/23p46-f1-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/23p46-f1-diagnostic-dpm/f1-diagnostic-dpm-fates-23p46.png) show `2.10%` escaped, `26.45%` trapped, and `71.45%` incomplete |
| Diagnostic parcel weight | is not an additional physical inlet source, and incomplete tracks remain unresolved |

</details>

## Coupled speed sweep — 29.48 m/s

| Item | Coupled speed sweep — 29.48 m/s |
| --- | --- |
| — | The [F1 Coupled pilot](../../../../PyAnsys/output/phase8-carrier/F1-29p48-coupled-gts-20260928T223744Z/manifest.json) independently scaled the verified recovery parent to 29.48 m/s, used fresh Hybrid initialization, saved local checkpoints, and saved/reopened its N2,000 endpoint |
|  | The [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/29p48-f1-coupled-n2000/assessment.json) fails the operational gate: mean absolute mixture boundary gap `13.551 kg/s` (`6.235%` of feed) and liquid inventory `1,165.215 → 1,253.387 kg`, slope `+0.17563 kg/steady iteration` |
|  | Continuity `0.01169–0.01572` and no-fatal-event checks pass |
|  | The saved endpoint became the parent for a [declared N10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-29p48-coupled-gts-extension-to10000-20260928T225313Z/manifest.json) |
|  | The N10,000 continuation completed and reopened its shared final pair |

<details>
<summary>Supporting detail — Coupled speed sweep — 29.48 m/s</summary>

| Item | Coupled speed sweep — 29.48 m/s |
| --- | --- |
| — | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/29p48-f1-coupled-n10000/assessment.json) passes the operational carrier gate: mean absolute mixture boundary gap `0.562 kg/s` (`0.259%` of feed), liquid inventory `1,428.597 → 1,428.896 kg` with slope `+0.000609 kg/steady iteration`, continuity `0.01036–0.01396`, and no fatal event |
| It | is eligible for diagnostic DPM tracking |
| Terminal phase-2 steam-outlet flow | was `128.152 kg/s`, or `99.66%` of commanded liquid feed, so this is not evidence of effective separation |
| — | The [29.48 m/s F1 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-29p48-20260929T021944Z/build.json) saved/reopened seven inert bins from the qualified carrier, retaining the full Eulerian liquid feed and one-way interaction-off tracking from `steaminlet` |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/29p48-f1-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/29p48-f1-diagnostic-dpm/f1-diagnostic-dpm-fates-29p48.png) show `1.40%` escaped, `20.59%` trapped, and `78.00%` incomplete |
| diagnostic parcel weight | is not additional physical liquid feed; the unresolved fates prevent a carryover-efficiency claim |

</details>

## Coupled speed sweep — 32.14 m/s

| Item | Coupled speed sweep — 32.14 m/s |
| --- | --- |
| — | The [F1 Coupled pilot](../../../../PyAnsys/output/phase8-carrier/F1-32p14-coupled-gts-20260929T022741Z/manifest.json) scaled the verified recovery parent to 32.14 m/s, fresh-Hybrid initialized, and saved/reopened its N2,000 endpoint |
|  | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f1-coupled-n2000/assessment.json) fails the operational carrier gate: mean absolute mixture boundary gap `18.556 kg/s` (`7.832%` of feed) and liquid inventory `1,284.456 → 1,396.714 kg`, slope `+0.22357 kg/steady iteration` |
|  | Continuity `0.01174–0.01613` and no-fatal-event checks pass |
|  | The saved development checkpoint became the parent for a [declared N10,000 continuation](../../../../PyAnsys/output/phase8-carrier/F1-32p14-coupled-gts-extension-to10000-20260929T031916Z/manifest.json) |
|  | The N10,000 continuation completed, saved local N3,000–N9,000 checkpoints, and reopened its shared final pair |

<details>
<summary>Supporting detail — Coupled speed sweep — 32.14 m/s</summary>

| Item | Coupled speed sweep — 32.14 m/s |
| --- | --- |
| — | Its [last-500 assessment](../../../../PyAnsys/output/phase8-analysis/32p14-f1-coupled-n10000/assessment.json) passes the operational carrier gate: mean absolute mixture boundary gap `0.555 kg/s` (`0.234%` of feed), liquid inventory `1,629.557 → 1,629.575 kg` with slope `+0.0000484 kg/steady iteration`, continuity `0.00936–0.01282`, and no fatal event |
| Terminal phase-2 steam-outlet flow | was `139.752 kg/s`, `99.69%` of commanded liquid feed |
| carrier | is eligible for diagnostic DPM tracking, while effective separation remains unproven |
| — | The [32.14 m/s F1 diagnostic child](../../../../PyAnsys/output/phase8-dpm/F1-diagnostic-050permil-32p14-20260929T062233Z/build.json) saved/reopened seven inert bins from this qualified carrier, retaining full Eulerian liquid feed and one-way interaction-off tracking from `steaminlet` |
|  | All seven native track reports completed at 613 trajectories per bin |
|  | The [weighted fate summary](../../../../PyAnsys/output/phase8-analysis/32p14-f1-diagnostic-dpm/summary.json) and [figure](../../../../PyAnsys/output/phase8-analysis/32p14-f1-diagnostic-dpm/f1-diagnostic-dpm-fates-32p14.png) show `1.69%` escaped, `15.57%` trapped, and `82.75%` incomplete |
| diagnostic parcel weight | is not additional physical liquid feed; unresolved fates prevent a carryover-efficiency claim |

</details>

</details>

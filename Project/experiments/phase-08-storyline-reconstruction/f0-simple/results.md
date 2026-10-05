# Phase 8 F0 — SIMPLE reconstruction results

| Item | Phase 8 F0 — SIMPLE reconstruction results |
| --- | --- |
| F0 | is the former F1 SIMPLE series, separated by human direction on 3 October 2026 |
| Original artifact names | remain unchanged |
| — | F1 now denotes the mixed-inlet Coupled series |

## F0 versus F1: matched outcomes, different numerical packages

![F1 SIMPLE versus Coupled carrier comparison](../f1-one-inlet/figures/f1-simple-vs-coupled-n10000.png)

*Replotted from the rounded values in the table below; original machine-generated plot unavailable in this checkout.*

| Speed (m/s) | Steam-outlet liquid / feed, Coupled → SIMPLE (%) | Final liquid inventory, Coupled → SIMPLE (kg) | Pressure difference, Coupled → SIMPLE (kPa) |
| ---: | ---: | ---: | ---: |
| 20.11 | 99.728 → 214.437 | 1021.5 → 3802.5 | 43.29 → 107.80 |
| 23.46 | 99.651 → 258.911 | 1110.8 → 5274.2 | 56.18 → 198.18 |
| 26.81 | 99.671 → 360.424 | 1262.6 → 6576.7 | 71.09 → 406.52 |
| 29.48 | 99.653 → 455.273 | 1428.9 → 7339.8 | 84.97 → 546.56 |
| 32.14 | 99.664 → 673.023 | 1629.6 → 8160.3 | 100.88 → 843.23 |

| F0 versus F1: matched outcomes, different numerical packages |
| --- |
| SIMPLE numerical diagnostics over N9,500–10,000: |

| Speed (m/s) | SIMPLE mixture boundary gap (% feed) | SIMPLE inventory slope (kg/iteration) | SIMPLE max continuity residual | Reverse-flow messages | Viscosity-limit messages |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20.11 | 67.27 | 0.486 | 0.256 | 9998 | 9740 |
| 23.46 | 93.42 | 0.582 | 0.389 | 9998 | 9768 |
| 26.81 | 153.14 | 0.741 | 0.680 | 9998 | 9760 |
| 29.48 | 208.93 | 1.111 | 1.086 | 9998 | 9770 |
| 32.14 | 336.85 | 0.047 | 1.162 | 9998 | 9783 |

| Item | F0 versus F1: matched outcomes, different numerical packages |
| --- | --- |
| — | Both series use the same two-face F1 topology, five total-feed targets, 60,964-cell mesh and fresh initialized parent, with N10,000 endpoints and N9,500–10,000 response windows |
| SIMPLE branch | uses segregated pseudo-time off and second-order `k`; the comparison branch uses Coupled/Global Time Step and first-order `k` |
| This | is a numerical-package comparison |
| — | It does not isolate the pressure-coupling algorithm from the discretization and time-stepping changes |
| These diagnostics describe numerical limitations; they | are not Phase 8 progression gates |
| — | Reference-speed native liquid contours and inlet vectors at the same N10,000 horizon: |

| SIMPLE package | Coupled recovery package |
| --- | --- |
| ![F1-26.81-simple-n10000 liquid](../f1-one-inlet/figures/F1-26.81-simple-n10000-liquid.png) <br>  <br> ![F1-26.81-simple-n10000 inlet-vectors](../f1-one-inlet/figures/F1-26.81-simple-n10000-inlet-vectors.png) | ![F1-26.81-n10000 liquid](../f1-one-inlet/figures/F1-26.81-n10000-liquid.png) <br>  <br> ![F1-26.81-n10000 inlet-vectors](../f1-one-inlet/figures/F1-26.81-n10000-inlet-vectors.png) |

| Item | F0 versus F1: matched outcomes, different numerical packages |
| --- | --- |
| Historical [08b setup](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/setup.md) and [results](../phase-02-parity-reset-and-pre-v2-qualification/purnanto-08b-parity-split-inlet/results.md) remain separate comparison anchors | the documented run used split `liquidinlet`/`steaminlet` mass-flow boundaries on 7,601,261 cells and its N5,000 carrier report showed a 58.73% mixture imbalance ratio |
|  | F1 SIMPLE shares the audited 00a SIMPLE/second-order/QUICK numerical-method family, but F1 applies mixed-phase feed to both inlet faces on 60,964 cells |
|  | SIMPLE alone therefore does not make this a topology-, mesh-, or result-identical 08b replication |

### One-way DPM diagnostics on the SIMPLE carriers

![F1 SIMPLE carrier one-way DPM diagnostic fates](../f1-one-inlet/figures/f1-simple-diagnostic-dpm-fates.png)

*Replotted from the rounded values in the table below; original machine-generated plot unavailable in this checkout.*

| Speed (m/s) | Escaped represented weight (%) | Trapped represented weight (%) | Incomplete represented weight (%) |
| ---: | ---: | ---: | ---: |
| 20.11 | 0.08 | 0.01 | 99.91 |
| 23.46 | 5.12 | 1.24 | 93.65 |
| 26.81 | 0.18 | 11.79 | 88.03 |
| 29.48 | 4.72 | 0.23 | 95.05 |
| 32.14 | 6.19 | 1.32 | 92.49 |

| Item | One-way DPM diagnostics on the SIMPLE carriers |
| --- | --- |
| — | These seven-bin cases use 5% inert, one-way DPM weight, a 50,000-step tracking cap, and the same full-feed Eulerian SIMPLE carriers |
| large incomplete share | is unresolved trajectory weight |
| fates | are diagnostic outcomes on numerically poor carriers, not separator efficiency or validated separation |

## What this stage establishes

| Item | What this stage establishes |
| --- | --- |
| F1 supplies the mixed-feed reference | more speed produces more retained liquid and a larger pressure difference, without resolving the high steam-outlet liquid routing |
|  | This motivates comparing the inlet representation in F2 and following droplets separately in F3 |
|  | The five-speed SIMPLE reconstruction is reported separately from the selected Coupled adaptation: it exposes large mixture-boundary gaps and inventory drift, so its outlet ratios and diagnostic DPM fates cannot be read as separation performance |
|  | Its connection to historical 08b is numerical-method lineage, not exact topology or mesh parity |

## SIMPLE native views and supporting topology variants

| Snapshot | Liquid | Inlet liquid | Vertical vectors | Inlet vectors |
| --- | --- | --- | --- | --- |
| F1 SIMPLE original faces N2000 | ![F1-simple-mixed liquid](../f1-one-inlet/figures/F1-simple-mixed-liquid.png) | ![F1-simple-mixed inlet-liquid](../f1-one-inlet/figures/F1-simple-mixed-inlet-liquid.png) | ![F1-simple-mixed vertical-vectors](../f1-one-inlet/figures/F1-simple-mixed-vertical-vectors.png) | ![F1-simple-mixed inlet-vectors](../f1-one-inlet/figures/F1-simple-mixed-inlet-vectors.png) |
| F1 SIMPLE merged single inlet N2000 | ![F1-simple-single liquid](../f1-one-inlet/figures/F1-simple-single-liquid.png) | ![F1-simple-single inlet-liquid](../f1-one-inlet/figures/F1-simple-single-inlet-liquid.png) | ![F1-simple-single vertical-vectors](../f1-one-inlet/figures/F1-simple-single-vertical-vectors.png) | ![F1-simple-single inlet-vectors](../f1-one-inlet/figures/F1-simple-single-inlet-vectors.png) |
| F1 20.11 m/s SIMPLE original two faces N10000 | ![F1-20.11-simple-n10000 liquid](../f1-one-inlet/figures/F1-20.11-simple-n10000-liquid.png) | ![F1-20.11-simple-n10000 inlet-liquid](../f1-one-inlet/figures/F1-20.11-simple-n10000-inlet-liquid.png) | ![F1-20.11-simple-n10000 vertical-vectors](../f1-one-inlet/figures/F1-20.11-simple-n10000-vertical-vectors.png) | ![F1-20.11-simple-n10000 inlet-vectors](../f1-one-inlet/figures/F1-20.11-simple-n10000-inlet-vectors.png) |
| F1 23.46 m/s SIMPLE original two faces N10000 | ![F1-23.46-simple-n10000 liquid](../f1-one-inlet/figures/F1-23.46-simple-n10000-liquid.png) | ![F1-23.46-simple-n10000 inlet-liquid](../f1-one-inlet/figures/F1-23.46-simple-n10000-inlet-liquid.png) | ![F1-23.46-simple-n10000 vertical-vectors](../f1-one-inlet/figures/F1-23.46-simple-n10000-vertical-vectors.png) | ![F1-23.46-simple-n10000 inlet-vectors](../f1-one-inlet/figures/F1-23.46-simple-n10000-inlet-vectors.png) |
| F1 26.81 m/s SIMPLE original two faces N10000 | ![F1-26.81-simple-n10000 liquid](../f1-one-inlet/figures/F1-26.81-simple-n10000-liquid.png) | ![F1-26.81-simple-n10000 inlet-liquid](../f1-one-inlet/figures/F1-26.81-simple-n10000-inlet-liquid.png) | ![F1-26.81-simple-n10000 vertical-vectors](../f1-one-inlet/figures/F1-26.81-simple-n10000-vertical-vectors.png) | ![F1-26.81-simple-n10000 inlet-vectors](../f1-one-inlet/figures/F1-26.81-simple-n10000-inlet-vectors.png) |
| F1 29.48 m/s SIMPLE original two faces N10000 | ![F1-29.48-simple-n10000 liquid](../f1-one-inlet/figures/F1-29.48-simple-n10000-liquid.png) | ![F1-29.48-simple-n10000 inlet-liquid](../f1-one-inlet/figures/F1-29.48-simple-n10000-inlet-liquid.png) | ![F1-29.48-simple-n10000 vertical-vectors](../f1-one-inlet/figures/F1-29.48-simple-n10000-vertical-vectors.png) | ![F1-29.48-simple-n10000 inlet-vectors](../f1-one-inlet/figures/F1-29.48-simple-n10000-inlet-vectors.png) |
| F1 32.14 m/s SIMPLE original two faces N10000 | ![F1-32.14-simple-n10000 liquid](../f1-one-inlet/figures/F1-32.14-simple-n10000-liquid.png) | ![F1-32.14-simple-n10000 inlet-liquid](../f1-one-inlet/figures/F1-32.14-simple-n10000-inlet-liquid.png) | ![F1-32.14-simple-n10000 vertical-vectors](../f1-one-inlet/figures/F1-32.14-simple-n10000-vertical-vectors.png) | ![F1-32.14-simple-n10000 inlet-vectors](../f1-one-inlet/figures/F1-32.14-simple-n10000-inlet-vectors.png) |

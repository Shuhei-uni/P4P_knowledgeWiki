# G7 — weaker sink with Coupled/N-phase

| Item | G7 — weaker sink with Coupled/N-phase |
| --- | --- |
| — | E7 completed absolute N5000 and its recording, regional-budget and native spatial audits |
|  | Weakening the sink from tau 0.02 to 0.10 s did not produce a credible steady solution |
| G7 | is complete; E7 is numerically inadequate and is not a qualified parent |
| No E7 extension | is selected |

## Controlled comparison and terminal evidence

| Item | Controlled comparison and terminal evidence |
| --- | --- |
| [setup](setup.md) | retains E6's full geometry, full split feed, closed brine wall, Mixture/slip/RNG model, N-phase, segregated VF, Coupled/pseudo-time Off/CFL20, pressure and momentum relaxation0.5, source law and update interval1 |
| — | Only tau and the consequent source coefficients change |
|  | Both start from the common clean N0 physical field |
|  | The final controller exited successfully at N5000 |
|  | Native scalar, exact-face flux, speed and all eight residual histories cover N1–5000; 4999 source-lag pairs have zero error |

<details>
<summary>Supporting detail — Controlled comparison and terminal evidence</summary>

| Item | Controlled comparison and terminal evidence |
| --- | --- |
| — | All21 scheduled/recovery whole-cell snapshots pass independently normalized/native inventory parity |
|  | Initial/final horizontal and full-height axial fields and the final local-PC case/data pair are preserved |
|  | See [run paths](run-paths.md), machine `PyAnsys/output/phase07b-g7/completion-audit.json`, `comparison.json`, `diagnostic-comparison.json`, `regional-budget.json` and `native-spatial/manifest.json` |
| The original job wrapper's BLOCKED receipt is retained | its sole defect was a missing local copy of historical N2500 smoke evidence |
|  | The byte-identical file was recovered from two agreeing preserved parents, and all required-file checks passed in `resume-n3227/terminal-file-reconciliation.json` |
|  | Solver and terminal verifier both returned0 |
|  | This evidence-copy defect is separate from numerical inadequacy |

</details>

## Declared late-window result

| Item | Declared late-window result |
| --- | --- |
| — | Statistics use N4501–5000 |
|  | Inventory change compares means N4001–4500 versus N4501–5000, divided by the larger mean |
| Closure | includes the independently measured applied removal source and uses each phase's measured feed; native mixture uses total feed |

| Quantity | E6 tau0.02 | E7 tau0.10 |
| --- | ---: | ---: |
| Mean absolute liquid closure, % feed | 144.369 | 148.213 |
| Mean absolute vapor closure, % feed | 1.520 | 1.776 |
| Signed mean vapor closure, % feed | +1.418 | +1.700 |
| Mean absolute native mixture closure, % feed | 84.841 | 87.000 |
| Inventory mean increase, % | 18.451 | 15.195 |
| Mean total native liquid volume, m³ | 0.475630 | 0.515893 |
| Mean collector liquid volume, m³ | 0.006259 | 0.030844 |
| Mean applied removal, kg/s | 275.962 | 272.028 |
| Liquid carryover, % liquid feed | 8.346 | 15.554 |
| Vapor outlet recovery, % vapor feed | 98.582 | 98.300 |
| Outlet vapor mass fraction | 0.890889 | 0.814549 |
| Late maximum speed, m/s | 82.285 | 81.144 |

| Declared late-window result |
| --- |
| Measured liquid/vapor feed is116.921232/80.689902kg/s |
| The fivefold weaker coefficient leaves nearly the same removal because the mean collector inventory rises about4.93-fold |
| E7 has more total inventory and more liquid carryover; its smaller relative inventory growth still greatly exceeds the1% criterion |
| This supports rejecting this coefficient change as a steady-state remedy at the tested horizon; it does not establish that no steady solution can exist |
| All eight late residual maxima: |

| Residual | E6 | E7 |
| --- | ---: | ---: |
| continuity | 1.3259 | 1.3222 |
| x velocity | 0.00010281 | 0.00012179 |
| y velocity | 0.000080592 | 0.00011675 |
| z velocity | 0.00011706 | 0.00011949 |
| k | 0.0095616 | 0.010212 |
| epsilon | 0.023795 | 0.031379 |
| vf-phase-1 | 0.00018085 | 0.00018437 |
| vf-phase-2 | 0.012148 | 0.012194 |

| Item | Declared late-window result |
| --- | --- |
| Only the three momentum curves and VF1 | remain below1e-3 throughout the window |
| — | Necessary closure, inventory and residual criteria fail |
|  | Neither case has an iterated speed event≥500m/s; both peak283.091m/s atN1 |
|  | Absence of extreme bursts does not establish conservation |

## Independent regional budgets and spatial interpretation

| Item | Independent regional budgets and spatial interpretation |
| --- | --- |
| regional audit | uses exact native phase face fluxes and the source integral; collector and above-collector budgets sum to the whole-vessel budget within1e-10kg/s at every late iteration |
| These | are steady numerical budgets, not a physical-time storage derivative |

| Signed mean / mean absolute budget, kg/s | E6 | E7 |
| --- | ---: | ---: |
| Collector | −6.136 / 21.014 | −10.809 / 64.986 |
| Above collector | −162.662 / 162.662 | −162.483 / 164.417 |
| Whole liquid | −168.798 / 168.798 | −173.292 / 173.292 |

| Item | Independent regional budgets and spatial interpretation |
| --- | --- |
| Most signed deficit | remains above the collector |
| — | E7 mean inward delivery/outward escape across the collector interface is425.558/164.339kg/s, versus316.007/46.182kg/s forE6 |
| native brine-wall phase flux | is zero and the mass source is confined to the collector |
| — | This spatial ledger does not prove that the source causes the upstream deficit |
|  | Six native figures passed direct visual QA, using shared VF0–1 and speed0–60m/s scales, matched planes and cameras, and unchanged PNGs |

<details>
<summary>Supporting detail — Independent regional budgets and spatial interpretation</summary>

| Item | Independent regional budgets and spatial interpretation |
| --- | --- |
| inlet-height horizontal views | are deliberately local zooms; E7 has a narrower liquid band and higher local core speed in that particular view |
| — | Full-height axial cuts retain boundary liquid bands and lower pockets within a predominantly vapor interior |
|  | A plane cannot replace volume-integrated inventory |
|  | The raw closure/inventory and residual/speed figures preserve oscillation and drift |
| Figure identities and settings | are in `native-spatial/manifest.json`; QA observations are in `visual-qa.json` |
| — | E7 sampled N2600/2700/2800 maxima are86.829/86.303/86.326m/s, near the upper outlet at y≈6.265m |
|  | Its final maximum is76.393m/s at(−0.238654,6.265104,0.068375)m, not in the collector |
|  | Both transcripts contain4825 viscosity-limiting messages; maximum limited cells are2810(E6) and3399(E7) |
| Reverse-flow messages occur4998times each; message counts | are not unique-iteration counts |

</details>

## Raw fraction semantics and limits

| Item | Raw fraction semantics and limits |
| --- | --- |
| native reported liquid VF | is normalized |
| — | At E7 N5000, raw alpha1+alpha2 ranges0.923461–1.184119 above the collector and0.970334–1.105978 in it |
|  | Raw liquid volume totals0.546833m³, versus independently verified normalized/native0.527307m³ |
| Both raw fractions, raw inventory and phase-sum defects | are preserved |
| — | Cellwise normalization agrees with native volume within rtol1e-9/atol1e-12m³ at every snapshot; it does not repair or establish conservation |

<details>
<summary>Supporting detail — Raw fraction semantics and limits</summary>

| Item | Raw fraction semantics and limits |
| --- | --- |
| Raw SV_MASS_IMBALANCE | remains uncalibrated |
| — | Exact source-command lag parity does not establish the expression Jacobian or implicitness |
| Retained history | is originalN1–500, first replayN501–2500 and second replayN2501–5000 |
| N500/N2500 case-data restarts | were independently verified; later unchanged-state recorder recoveries atN687/N1631/N2185/N3227 added no replay |
| — | Repeated native boundary rows agree exactly and immutable retired tails remain excluded |
|  | The cumulative attempted ceiling was6000 |
| No uninterrupted or bitwise-equivalent trajectory | is claimed |

</details>

## Decision

| Item | Decision |
| --- | --- |
| Final disposition,29 September2026 | Andy subsequently stopped E8 atN128 and closed Phase7b |
|  | The selection below is historical and is superseded by [phase closure](../../closure.md); no further simulation is authorized |
| — | The completed [source audit](../source-treatment-audit.md) found no concrete source assignment/sign/transported-term defect |
|  | Together with G7, it supports using the last permitted contrast for the separately documented Mixture startup sequence, not another sink coefficient or horizon. [E8 setup](../mixture-startup/setup.md) freezes VF/slip together during bounded flow conditioning and restores both only if its prospectively declared gate passes |
| This | is the final discovery contrast under the accepted bounded finish; an unsuccessful bounded attempt closes the tested route, while passing indicators require separate persistence/restart qualification |

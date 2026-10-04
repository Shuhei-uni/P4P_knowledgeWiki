# Conclusions from completed Phase 7b results and partial E7

| Item | Conclusions from completed Phase 7b results and partial E7 |
| --- | --- |
| — | The tested full-geometry steady ideal-collector route has not established a numerically credible, conservative solution within the completed discovery budgets |
|  | The investigation has established reproducible numerical problems, verified source bookkeeping, and sensitivity to solver treatment |
|  | It has not established separator performance, physical nonexistence of a steady state, or a unique failure mechanism |
| E7 | remains incomplete after an external interruption; this review makes no new solve, phase selection, qualification or terminal G7 disposition |

## What the completed experiments establish

| Item | What the completed experiments establish |
| --- | --- |
| Collector extent alone did not resolve the problem. | G1's four completed N5000 cases have mean absolute liquid closure errors of 253–503% of feed and inventory changes of 10–16%; the full-extent S100 case failed numerically at attempted N4183 |
|  | Lower inventory or carryover is not sufficient to select a thickness. [G1](../results.md) |
| A weaker coefficient is not necessarily a smaller realized sink. | The SIMPLE coefficient contrasts remained nonconservative and retained substantial inventory drift |
|  | Liquid accumulation in the collector offsets coefficient reduction |
|  | This rules out claiming a monotonic rescue from the tested tau values; it does not prove that every possible removal law fails. [G2](../lower-sink-rate/results.md) |

<details>
<summary>Supporting detail — What the completed experiments establish</summary>

| Item | What the completed experiments establish |
| --- | --- |
| The severe original excursions are reproducible and algorithm-sensitive. | G3 reproduces every recorded scalar, collector-flux and residual value at stored precision |
|  | Sampled extreme-speed locations are near inlet-top elevation, well above the collector |
|  | Coupled treatment suppresses recorded speeds at or above 500 m/s, but does not close the independent mass budgets. [G3](../spike-diagnostic/results.md), [G4](coupled-off/results.md) |
| Numerical damping and phase-equation changes improve some indicators without producing convergence. | E5's lower Courant number reduces late liquid imbalance; E6's all-phase equations yield only a small further reduction, from 148.115% to 144.369% |
|  | E6 still has 84.841% native-mixture imbalance, 18.451% inventory change and maximum continuity residual 1.3259 in its declared late windows |
|  | Momentum and primary-VF residuals pass; continuity, turbulence and secondary-VF do not. [G5](coupled-cfl20/results.md), [G6](coupled-nphase/results.md) |
| These budget errors | include the native applied source exactly once |
| 1% budget/inventory and 0.001 all-equation residual criteria | are the declared discovery screens, not physical-validation guarantees |

</details>

## What the current E7 prefix adds

| Item | What the current E7 prefix adds |
| --- | --- |
| — | The new offline reduction compares both E6 and E7 at N2001–2500 |
|  | Inventory compares their own N1501–2000 and N2001–2500 means, normalized by the larger mean |
| This | is a retrospective matched-prefix diagnostic, not the predeclared terminal N4501–5000 comparison |
| E7 | includes the verified N500 restart and unchanged-state recorder recoveries; uninterrupted bitwise replication is not claimed |

| Matched partial indicator | E6, tau 0.02 s | E7, tau 0.10 s |
| --- | ---: | ---: |
| Mean absolute liquid closure / feed | 17.840% | 40.284% |
| Mean absolute vapor closure / feed | 0.321% | 0.474% |
| Mean absolute native-mixture closure / feed | 10.467% | 23.722% |
| Inventory window-mean change | +5.984% | +7.780% |
| Maximum continuity residual | 0.47977 | 0.74490 |
| Mean collector liquid mass | 2.633 kg | 15.992 kg |
| Mean native applied removal | 131.694 kg/s | 159.942 kg/s |

| Item | What the current E7 prefix adds |
| --- | --- |
| E7 | is worse on all the listed numerical adequacy metrics in this window |
| — | Its roughly sixfold collector mass increase more than offsets the fivefold coefficient reduction |
| Liquid carryover | is also higher, 3.489% versus 1.612% of feed, but neither ratio is qualified performance |
| — | Only momentum and primary-VF residuals pass the threshold in both cases |

![Matched raw partial histories](../../../../PyAnsys/output/phase07b-review-20260928/e7-partial/matched-partial-histories.png)

| Item | What the current E7 prefix adds |
| --- | --- |
| Raw histories, N1–2500 | E7 has more liquid inventory and generally larger continuity residual after the trajectories separate |
|  | Signed liquid imbalance changes sign and develops large deficits |
|  | The shaded interval is the retrospective table window; the dashed line marks E7's N500 restart |
|  | Neither apparent early balance nor a short improving segment establishes persistence |
|  | E7's mean absolute liquid error is 9.842% at N1001–1500, then 40.411% at N1501–2000 and 40.284% at N2001–2500 |
|  | E6 itself later deteriorates from 17.840% in this partial window to 144.369% at N4501–5000, illustrating why comparing E7's middle to E6's end would be misleading |
| — | The comparison verifies exact saved methods/controls/source-slot equality and the tau-only expression delta, consecutive finite scalar/flux/all-eight-residual prefixes, 2499 zero-error source-lag pairs per case, and regional-to-whole liquid-budget agreement |
|  | The E7 numbers exactly reproduce its previously preserved partial diagnostic. [Machine reduction and source hashes](../../../../PyAnsys/output/phase07b-review-20260928/e7-partial/comparison.json), [reproducible offline script](../../../../PyAnsys/output/phase07b-review-20260928/e7-partial/analyze_partial.py), [visual and machine QA](../../../../PyAnsys/output/phase07b-review-20260928/e7-partial/qa.json) |

## Mechanism and claim limits

| Item | Mechanism and claim limits |
| --- | --- |
| — | The [source audit](source-treatment-audit.md) found no concrete assignment, sign, unit or missing transported-property source defect |
|  | Exact source tracking proves evaluation timing; it does not establish implicit linearization or conservation |
| actual expression Jacobian | remains unverified |
| — | Thus a numerical interaction between removal, phase transport and the evolving flow remains plausible, without evidence for a particular undocumented derivative fix |
|  | E6's completed regional audit assigns most late liquid deficit above the collector: -162.662 kg/s above versus -6.136 kg/s inside in signed means |

<details>
<summary>Supporting detail — Mechanism and claim limits</summary>

| Item | Mechanism and claim limits |
| --- | --- |
| Collector mean absolute error | is still 21.014 kg/s |
| — | The new partial E7 ledger has signed means -31.031 kg/s above and -16.069 kg/s inside; neither region closes |
| These | are discrete flux/source budgets, not calibrated cellwise residuals or physical accumulation rates |
| — | They weaken an explanation confined solely to a local collector defect but do not exclude upstream feedback from that source |
|  | Raw phase sums depart from one in E6; native-normalized fraction/inventory parity is a reporting check, not a repair of conservation |
| Raw `SV_MASS_IMBALANCE` | remains uncalibrated |
| — | Attractive liquid-location contours, reduced carryover, a quiet velocity history or a low primary residual cannot overcome independent budget and stationarity failures |

</details>

## Practical implication

| Item | Practical implication |
| --- | --- |
| There | is enough evidence to write the phase's present scientific discussion now: the tested combinations have not produced credible steady removal, and broad further thickness/tau/Courant/relaxation sweeps are not justified by the completed evidence |
| — | E7's partial evidence provides no matched-window support for the hoped-for weaker-sink improvement, while its terminal outcome remains unknown |
| The accepted bounded finish remains unchanged | reconcile and finish E7 if access is restored, then consider at most the already-authorized isolated startup contrast if justified |
|  | Its remaining value is testing the unresolved startup hypothesis, not repeating parameter tuning |
|  | If the bounded work still fails, close the tested route with these limitations |
|  | A different physical collection/drainage model would require separate phase framing; this analysis neither selects it nor proves it will solve the problem |
|  | Existing Shuhei film growth and low bulk carryover are not evidence of stationary conservative drainage, as recorded in the [cross-branch review](phase-review-2026-09-26.md) |

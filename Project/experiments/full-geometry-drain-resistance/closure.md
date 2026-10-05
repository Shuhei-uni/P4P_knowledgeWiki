# Closure — full-geometry fixed drain resistance

Closed unqualified on 1 October 2026 (Pacific/Auckland). The two predeclared fresh starts each completed1000 steady iterations. Both meet the depletion/imbalance/routing stopping predicate; no further solves are selected. Unused budget is not authorization to continue this closed route.

## Verified evidence

| Initial level | Liquid inventory loss | Late500 mean absolute liquid imbalance | Final continuity |
| --- | ---: | ---: | ---: |
| +0.10m | 4.149% | 159.315% of feed | 0.17799 |
| +0.30m | 5.147% | 193.974% of feed | 0.17688 |

Both starts continued losing inventory in the final200 iterations and failed conservation, inventory, routing, residual and clipping requirements. Independent phase/native-mixture face reductions and full-cell inventory agree with native reports; that confirms the accounting, not conservation. Native histories and callback evidence cover N1–1000, both endpoint case/data pairs and spatial fields are preserved, and execution verifiers passed. The latest monitor live receipt verified the high endpoint idle at N1000 with no controller/worker and a free lock. See [results and evidence links](results.md).

## Interpretation

Adding the tested passive K9 resistance did not produce an acceptable steady solution from either initial level under fixed downstream head +0.10m. Greater initial submergence did not avoid the observed failure pattern; the high start lost a larger fraction of inventory and had greater imbalance. Neither endpoint is a qualified parent. The single-liquid benchmark remains a valid limited implementation test; its success did not transfer to qualification of the coupled separator.

These nonconverged outcomes do not identify the root cause. They cannot distinguish inadequate physical boundary assumptions from shortcomings in numerical solution of this multiphase setup. Steady iteration inventory changes are not a physical transient storage rate. Low carryover, final momentum residuals below0.001 and exact ledger parity do not establish steady drainage.

## Budget and claim limits

2000 total solved iterations and16273.657s (4.5205 recorded controller wall-hours) used; no retries added solves. The6000-iteration/14-hour ceilings were not exhausted because the scientific stop criterion was reached. Connected-interface stationarity, two passing independent starts, save/reopen persistence, mesh independence and physical validation remain unestablished. No claim that all resistances, steady models or the physical separator lack a solution.

## Disposition and next decision

Preserve both native pairs, source histories, fields, audits and manifests. Monitoring ends; no endpoint is restored or replaced by closure. Phase9 and7b remain closed. Do not automatically run a K/head sweep, change solver settings or start a transient calculation. Before framing another compute phase, review the pressure-to-flow behavior and spatial conservation defects in these saved fields and identify which missing downstream boundary evidence could constrain the model. Any new physical/numerical contrast needs a separately agreed scope.

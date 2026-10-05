# Phase 9 closure — unqualified bounded steady-pool test

**Current disposition after the authorized extension:** closed unqualified at N2000 on 30 September 2026. The endpoint is preserved and Fluent is idle. No further solves are selected; supervision ends after this review. See [results](results.md#completed-n10002000-extension-unqualified) for the combined evidence, interruption limits and next scope recommendation. Earlier authorization and closure text below is historical.

**Human-authorized continuation on 30 September 2026:** Andy requested resumption. Continue the preserved h_i=0.30 m, scale-0.1 endpoint from native N1000 to N2000, with unchanged physics and numerical settings. This explicitly extends the prior stopping allowance by one 1000-iteration block, within the original 12000-iteration/48-hour total budget. A four-hour execution guard bounds this block; earlier stop gates remain active. No endpoint is qualified. Phase 9 supervision was subsequently resumed by Andy for this bounded extension and terminal review; see CONTEXT.md and phase-state.yaml. Compare conservation, inventory drift, routing, all active residuals and spatial changes with N1000 before selecting further work. This single-start continuation cannot establish initial-condition independence or physical validity.


**Closed unqualified on 30 September 2026.** No conservative stationary solution
or qualified parent was obtained. This stopped calculations at the original cutoff; the later bounded human extension above supersedes that stop only.
The final higher-pool endpoint is preserved; live Fluent was idle at N1000,
its controller had exited and the server1 lock was free. Phase 7b remains
closed, its old automations remain paused, and Shuhei's sessions were not used.

## Evidence and comparison

The existing 620431-cell full geometry was rebuilt as steady implicit VOF with
separate full-feed inlets and the existing brine pressure outlet. The assumed
external liquid reservoir level was fixed at +0.10 m. No CAD change, sink,
film model, level controller or physical transient was used.

The initial scale-0.3, h_i=0.10 m run reached N1050 but drained severely. The
single allowed scale reduction to 0.1 was then tested with two independently
initialized pools. Both scale-0.1 runs completed N1000 with saved case/data,
native seven-equation residuals, phase/native-mixture ledgers, gross reverse
flux histories, inventory reports, full-cell fields and axial section fields.
The N1–1000 comparisons exclude duplicated initial-state callbacks and verify
agreement where the two report blocks overlap. Independent endpoint face-flux
and liquid-volume reductions agree with the native reports. That agreement
verifies accounting, not conservation.

| Scale 0.1, N1000 | Initial pool 0.10 m | Initial pool 0.30 m | Required |
|---|---:|---:|---|
| Initial → final liquid inventory (kg) | 4096.77 → 3619.56 | 4652.24 → 3990.82 | Stationary window |
| Inventory change from N0 | −11.65% | −14.22% | Not a standalone qualification test |
| N1–1000 inventory range / mean | 12.28% | 15.21% | ≤1% |
| Inventory half-window mean change | −6.12% | −7.64% | ≤0.25% magnitude |
| Mean absolute liquid imbalance / feed | 265.90% | 369.35% | ≤0.5% |
| Final absolute liquid imbalance / feed | 334.43% | 511.09% | ≤1% throughout window |
| Final vapor imbalance / feed | 3.14% | 4.60% | ≤1% throughout window |
| Final native-mixture imbalance / feed | 196.59% | 300.52% | ≤1% throughout window |
| Final continuity residual | 0.16942 | 0.17394 | ≤0.001 throughout window |

Both runs also failed routing/reverse-flow and other active residual criteria.
Momentum residuals alone were small. The last 200 iterations still lost
125.36 and 158.88 kg of liquid respectively. Thus neither trace supports a
stationary tail. The spatial stationarity, common-equilibrium and qualification
save/reopen continuation were not established; persistence of saved diagnostic
files must not be described as persistence of a qualified steady solution.

![Two initial levels, unchanged numerical treatment](../../../PyAnsys/output/phase09/comparison/two-start-comparison.png)

[Audited two-start metrics and source hashes](../../../PyAnsys/output/phase09/comparison/two-start-comparison.json)
· [Compute ledger](../../../PyAnsys/output/phase09/comparison/budget-ledger.json)
· [Detailed results](results.md)
· [Original gates and subsequent predeclared contrasts](setup.md)

## Interpretation and claim limits

The lower-pool case developed vapor leakage at the drain. Greater initial
submergence reduced final vapor leakage (7.65→1.41 kg/s), but produced a larger
liquid imbalance. Therefore loss of the liquid seal alone does not explain
all the failure. The higher-pool drain-height band remained about 90% liquid
by volume, versus 75% for the lower-pool case, while neither conserved mass.
These band occupancies are not connected-interface measurements.

Reducing the numerical step lowered continuity residuals and slowed inventory
loss, but did not produce conservative steady drainage. Matched iteration
counts do not represent matched physical time or equal progress toward steady
state; no exact pseudo-time conversion is available. Verbosity was enabled,
but explicit automatic step values were not found in the archived transcript,
so no cumulative pseudo-time comparison is claimed.

The fixed external reservoir pressure and absent calibrated drain resistance
remain important physical assumptions. Pressure-convention review found no
specific formula error, but the unconverged results cannot identify an exact
cause, prove the physical boundary wrong, or rule out all steady pool models.
There is no mesh-independence, dynamic-stability, fine-mist or plant-validation
claim. Changing the downstream model or using physical transient VOF requires
a newly agreed scientific scope; neither was done overnight.

## Disposition

Use every endpoint only as **unqualified diagnostic evidence**. No endpoint is
an eligible qualified parent. No further numerical sweep or unchanged
continuation is justified by these results. The declared 2000-iteration
smaller-step allowance is exhausted, including the higher-level comparison;
the larger overall budget is a ceiling, not a reason to keep iterating.

Total: **3102 solved iterations**, including both rest diagnostics, and **7.057
recorded controller wall-hours**, including setup/output overhead within those
runs. Separate build/review time is not included in that ledger. The initial
rest run had a cached-flux initialization defect and the zero-feed Global Time
Step diagnostic has a documented applicability limitation; neither establishes
full-feed physical feasibility. All failed and completed evidence is retained.

The most useful next scope discussion is to constrain the downstream pressure,
liquid level and drain/valve resistance from the actual apparatus, then decide
whether a revised steady boundary model is justified. This is a proposed future
decision, not authority to tune outlet pressure until a balance appears.

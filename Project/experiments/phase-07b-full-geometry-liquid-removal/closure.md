# Phase 7b closure — 29 September 2026

| Item | Phase 7b closure — 29 September 2026 |
| --- | --- |
| **Closed by Andy's direction | “okay stop E8. and conclude Phase 7b.” No qualified steady solution was established |
|  | This closes the tested numerical route and supersedes all earlier automatic continuation, experiment-selection and qualification authority |
|  | No further Phase 7b solve, restart or new contrast is selected |
|  | Both supervision automations are paused |
|  | A different physical model or a new phase requires separate framing and selection |

## What the completed evidence establishes

| Item | What the completed evidence establishes |
| --- | --- |
| question | was whether a lower-region ideal liquid collector could support credible steady full-feed Mixture flow in the full separator, with useful separation above it |
| mesh, split full-feed inlets and closed physical brine outlet | were retained; the collector was a numerical removal mechanism rather than a resolved pool or drain |
| — | The completed G1–G7 campaign did not establish simultaneous source-inclusive phase/native-mixture conservation, stationary inventory and acceptable residuals |
|  | Liquid reached the collector and the prescribed source acted, but that did not make the flow a credible steady solution |
|  | The evidence supports concluding that the tested configurations and finite iteration horizons did not meet the phase objective |
|  | It does not establish that the physical separator cannot work, that an ideal collector can never converge, or that no steady solution exists |

| Completed evidence | Supported finding |
| --- | --- |
| [G1: five collector thicknesses](results.md) | Four cases reached N5000 with inadequate closure/inventory/residuals; S100 diverged at attempted N4183. No thickness qualified. |
| [G2: weaker sink](lower-sink-rate/results.md) | The tested removal-time changes did not establish balanced steady collection. |
| [G3: unchanged diagnostic repeat](spike-diagnostic/results.md) | Replication and sampled hotspot evidence strengthen confidence that the observed behaviour is numerical evidence rather than merely a plotting artifact; they do not isolate its cause. |
| [G4: Coupled treatment](convergence-investigation/coupled-off/results.md), [G5: CFL20](convergence-investigation/coupled-cfl20/results.md) | Numerical controls affected extreme bursts and residual behaviour without restoring the required conservation and inventory behaviour. |
| [G6: N-phase equations](convergence-investigation/coupled-nphase/results.md), [G7: weaker sink under that treatment](convergence-investigation/coupled-nphase-weaker-sink/results.md) | Lower continuity and absence of ≥500 m/s events still did not yield a credible steady solution. Weakening the sink further did not remedy the late budgets. |

| Item | What the completed evidence establishes |
| --- | --- |
| most recent controlled E6/E7 comparison | uses N4501–5000; inventory change compares means N4001–4500 and N4501–5000, divided by the larger mean |
| Each phase closure | uses its measured feed; native mixture uses total feed |
| Removal | is counted once |

| Necessary indicator | E6, tau 0.02 s | E7, tau 0.10 s | Criterion |
| --- | ---: | ---: | ---: |
| Mean absolute liquid closure, % feed | 144.369 | 148.213 | ≤1 |
| Mean absolute vapor closure, % feed | 1.520 | 1.776 | ≤1 |
| Mean absolute native-mixture closure, % feed | 84.841 | 87.000 | ≤1 |
| Inventory mean increase, % | 18.451 | 15.195 | ≤1 |
| Maximum continuity residual in late window | 1.3259 | 1.3222 | <0.001 throughout |

| Item | What the completed evidence establishes |
| --- | --- |
| — | E7's mean applied removal was272.028 kg/s against liquid feed116.921232 kg/s while inventory continued to grow |
|  | Its liquid carryover was15.554% of feed versus8.346% for E6; neither ratio is a validated separator efficiency |
|  | Only three momentum residuals and VF1 met the residual threshold throughout the late window; continuity, k, epsilon and VF2 did not |
|  | The [G7 record](convergence-investigation/coupled-nphase-weaker-sink/results.md) owns all eight residuals, vapor signed/absolute errors, regional budgets and spatial interpretation |
|  | E7's complete N1–5000 scalar/flux/speed/eight-residual histories,4999 zero-error source-lag pairs,21 whole-cell snapshots, final pair and six native spatial figures passed their audits |
| Machine evidence | is `PyAnsys/output/phase07b-g7/completion-audit.json`; the raw history and native figures are retained there |
| final endpoint | remains preserved, but is not a qualified physical or converged parent |

## E8 disposition and preserved endpoint

| Item | E8 disposition and preserved endpoint |
| --- | --- |
| — | E8 tested a documented joint Volume Fraction/Slip Velocity freeze during initial flow conditioning, retaining E6's full-feed final treatment |
|  | Exact original N0 fields/geometry, zero-step freeze/restore, pair reopen and recovered N50 recording passed |
|  | Andy stopped the test at native N128, before its first prospective conditioning gate at N200 |
|  | No full-equation restoration occurred |
| N1000 conditioning cap and N5000 full-stage horizon | were not completed |

<details>
<summary>Supporting detail — E8 disposition and preserved endpoint</summary>

| Item | E8 disposition and preserved endpoint |
| --- | --- |
| This | is USER_STOPPED_PARTIAL_CONDITIONING, not conditioning-gate failure, numerical divergence or a completed G8 comparison |
| — | No conclusion about the effectiveness of the startup contrast follows from this short frozen-stage prefix |
|  | Its zero/bounded liquid inventory or source behaviour cannot qualify the full Mixture model while the phase equations are frozen |
| owned local controller | was retired, the exact owned pause4 interrupted/unregistered/released, and Fluent was verified idle at the same N128 without advancing or terminating Fluent |
| A unique local-PC case/data pair | was saved |
| stop receipt and partial native histories/whole-cell fields/section exports | are in `PyAnsys/output/phase07b-convergence-investigation/e8/user-stop-20260929/preserved/`; `receipt.json` owns exact paths and verification status |
| — | The independent `user-stop-20260929/partial-evidence-audit.json` passes: complete N1–128 scalar/six-residual/flux/speed records,127 zero-error source-lag pairs, frozen raw/slip parity, normalized-native inventory parity, final sections, and a free controller lock |
| Earlier raw partial runs | remain unchanged. [E8 results](convergence-investigation/mixture-startup/results.md) and [machine state](phase-state.yaml) identify the final disposition |

</details>

## Claim limits and unresolved explanations

| Item | Claim limits and unresolved explanations |
| --- | --- |
| — | No case passed the necessary indicators, so persistence/restart qualification and physical validation were not achieved |
| Closing the campaign | is a user-directed scope decision, not a successful qualification claim |
| — | The [source-treatment audit](convergence-investigation/source-treatment-audit.md) found no concrete source ownership, sign or transported-term assignment defect |
| actual expression Jacobian | remains unverified |
| Exact source tracking | is not conservation or proof of source implicitness |

<details>
<summary>Supporting detail — Claim limits and unresolved explanations</summary>

| Item | Claim limits and unresolved explanations |
| --- | --- |
| — | N-phase raw fractions do not necessarily sum to1 |
| Raw fractions/inventory and phase-sum defects | remain preserved; cellwise normalization matches native reported VF/inventory, but does not repair mass balance |
| Raw SV_MASS_IMBALANCE | is uncalibrated |
| — | Regional liquid budgets place most late signed deficit above the collector |
|  | They do not isolate a local source, mesh, transport or startup mechanism as the cause |
|  | E8's early termination leaves the staged-startup explanation unresolved |
| E7's | retained trajectory includes case/data restarts at N500 and N2500 and later unchanged-state recorder recoveries |
| Lost raw tails | remain excluded and immutable |
| No uninterrupted or bitwise-equivalent execution | is claimed; connectivity/sleep failures are distinct from numerical inadequacy |
| These | are steady solver iterations, not physical time |
| — | Inventory slope cannot be substituted for a physical storage term |
| Mesh independence, physical transient evolution and experimental agreement | were not established |
| Shuhei's different geometry/source/startup campaign | is not an isolated comparison |
| — | Film growth and low bulk carryover do not by themselves establish drainage or combined conservation |
| His sessions and other phases | remain untouched |
| practical outcome | is a documented negative result for the tested route and a reusable audited evidence/recording system |
| — | A subsequent phase should start from its own scientific question and qualified evidence requirements; it should not silently promote an unconverged Phase 7b endpoint or continue this tuning series |

</details>

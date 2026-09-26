# E4 — Coupled/Off suppresses extreme bursts but does not establish convergence

E4 completed the declared 5,000 iterations with intact recording and preserved
final case/data. Relative to original T020 and its exact E3 replication,
Coupled with pseudo time Off removes the observed >500 m/s excursions but
leaves severe source-inclusive mass errors, drifting liquid inventory and
failed continuity, turbulence and volume-fraction residual indicators. This
specific treatment is not a credible steady solution. G4 is complete with native spatial comparison and visual QA. No case is qualified.

## Core comparison

![Raw source-inclusive phase and independent native mixture errors with liquid inventory](../../../../../PyAnsys/output/phase07b-g4/E4-F1-closure-inventory.png)

The native applied liquid source is counted once in liquid and mixture budgets.
Positive values mean net inflow after sources; negative values mean excess
outflow/removal. Both methods develop large negative liquid errors while liquid
inventory continues evolving. Iteration is not physical time, so an inventory
slope here is not a physical storage-rate correction. The Coupled vapor error
oscillates rapidly about near-zero signed mean; cancellation does not satisfy
the declared mean-absolute closure criterion.

![All seven residuals and maximum speed](../../../../../PyAnsys/output/phase07b-g4/E4-F2-residual-speed.png)

Raw residual options are unchanged, with no normalization or restart during
E4. Algorithm-dependent residual scales can still differ: a residual ratio
between SIMPLE and Coupled is not a ratio of physical mass errors. Momentum
passes the declared late-window residual threshold; the other four equations
fail in both cases.

| Indicator | SIMPLE T020 / E3 | Coupled/Off E4 |
| --- | ---: | ---: |
| Liquid mean absolute closure, % feed | 354.843 | 263.677 |
| Vapor mean absolute closure, % feed | 3.329 | 5.223 |
| Independent mixture mean absolute closure, % feed | 208.591 | 155.961 |
| Inventory mean change, % larger mean | 18.370 | 11.526 |
| Continuity residual maximum | 1.2497 | 2.3959 |
| k residual maximum | 0.16321 | 0.037306 |
| Epsilon residual maximum | 32.2 | 0.088281 |
| Volume-fraction residual maximum | 0.014231 | 0.014106 |
| Maximum speed in late window, m/s | 2477.048 | 149.569 |
| Mean liquid inventory, m³ | 0.892680 | 0.584739 |
| Mean applied liquid removal, kg/s | 512.526 | 388.292 |
| Mean liquid carryover, % feed | 16.491 | 31.581 |
| Mean vapor recovery, % feed | 96.671 | 99.859 |

All late metrics use N4501–5000; inventory change compares that mean with
N4001–4500. Screening limits remain 1% for each mean absolute closure and
inventory change, and every residual below 0.001 throughout the late window.
Routing figures are unqualified solver outputs, not credible separation
performance. In E4 the signed mean vapor error is only 0.141% while its mean
absolute error is 5.223%; this difference exposes oscillatory cancellation.

## Diagnostic evidence and limits

All 5,000 scalar, exact-face-flux, every-iteration speed and seven-residual
records are complete. Applied source at N matches the current expression at
N−1 in all 4,999 pairs, with zero recorded difference. Source lag is verified,
not proven harmless or causal. All 15 scheduled cell snapshots pass hash,
iteration, finite-field and independent native-report checks; replaying the
capture schedule finds no omitted events. No speed-triggered capture occurred
because E4 never reached 500 m/s. Whole-run N1–5000 maximum is 267.664 m/s;
the common initialized N0 maximum is separately 372.622 m/s.

Around the original N2700 onset, E4 epsilon p95 rises from 0.02361 in
N2201–2700 to 0.03239 in N2701–3200, with speed maxima 59.27 and 77.08 m/s.
The dramatic later SIMPLE bursts are absent. This supports sensitivity of
those excursions to the pressure/momentum algorithm treatment, including its
required controls; it does not isolate one internal solver operation.

Scheduled E4 maxima move between locations: N4000 reaches 77.52 m/s at
(-0.20470, 6.26497, -0.00165) m; N4500 reaches 123.68 m/s at
(0.37704, 1.70602, -0.89198) m; N5000 reaches 56.24 m/s at
(-0.04093, 1.71321, -1.05891) m. These sampled maxima are not a complete
trajectory of the maximum-speed cell. The historical inlet-upper plane is
retained for a controlled spatial comparison, not assumed to contain every
new maximum.

E4 reports 598 turbulent-viscosity limiting messages (maximum 2,088 cells),
versus 4,679 (maximum 11,518) in SIMPLE. Reverse-flow messages persist in
4,998 and 4,999 iterations respectively. These are transcript message counts,
not distinct-cell or physical-time statistics. Raw SV_MASS_IMBALANCE remains
uncalibrated and is excluded from physical budgets and residual claims.

## Interpretation and next decision

The coupling hypothesis is partly supported for extreme excursions, but not
for acceptable closure or a bounded steady inventory. Large liquid source
rates relative to incoming feed, verified one-iteration update lag, segregated phase
transport and startup history remain competing explanations. E4's changed
vapor oscillations also leave numerical step aggressiveness plausible. The selected next contrast is [E5, Flow Courant 20](../coupled-cfl20/setup.md), with every other E4 setting fixed. This tests stronger implicit flow damping; source linearization is not established by the inspected documentation.

This result does not reject every Coupled setting, every source treatment or
the full-geometry steady objective. No extension or qualification of E4 is
justified merely by smoother epsilon and speed histories.

## Evidence

- [Setup](setup.md), [execution map](run-paths.md), [spatial comparison](spatial-comparison.md).
- [History comparison and raw CSVs](../../../../../PyAnsys/output/phase07b-g4/comparison.json).
- [Terminal recording audit](../../../../../PyAnsys/output/phase07b-g4/terminal-recording-audit.json).
- [Onset, schedule, snapshot locations and field audit](../../../../../PyAnsys/output/phase07b-g4/diagnostic-comparison.json).
- [Original wrapper receipt retained; corrected-path completion proof](../../../../../PyAnsys/output/phase07b-convergence-investigation/e4/completion-reconciliation.json). Its BLOCKED status concerned two mistaken filenames, repaired without Fluent calls or a rerun.

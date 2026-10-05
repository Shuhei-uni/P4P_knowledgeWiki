# Results — fixed drain resistance

Fresh h=+0.10 m K=9 setup passed native field initialization and save/reopen configuration checks. The N0–1000 block completed; terminal verification and observations are recorded below. No qualification is claimed. Prior unqualified separator endpoint remains preserved.

The dedicated monitoring schedule prompt was updated and its existing PAUSED status preserved under configure-run-monitor. Controller numerical guards and terminal verification operate independently of that schedule. Runtime model/effort is not exposed by the chat tools; intended monitor is GPT-6.1 Sol high.

## Low-start N0–1000 terminal observations

The exact `drain-k9-low-start-n1000` job completed 1000 solves and passed its deterministic artifact verifier. Independent live reconciliation found idle N1000, exited controller/worker, a free server1 lock, unchanged K=9 contract and saved local case/data pair. Native reports, seven residual histories and gross/net face-flux callbacks cover N1–1000 without gaps; N0/N1000 full fields and both axial sections are preserved. [Analysis](../../../PyAnsys/output/full-geometry-drain-resistance/drain-k9-h0p1-scale0p1-20260930T064024Z/drain-k9-h0p1-scale0p1-20260930T064024Z-flow-n00000-20260930T064324Z/analysis.json), [independent terminal audit](../../../PyAnsys/output/full-geometry-drain-resistance/drain-k9-h0p1-scale0p1-20260930T064024Z/drain-k9-h0p1-scale0p1-20260930T064024Z-flow-n00000-20260930T064324Z/monitor-terminal-audit.json), [live receipt](../../../PyAnsys/output/full-geometry-drain-resistance/low-start-n1000-terminal-live-receipt.json).

Liquid inventory fell 4096.770→3926.783 kg (−4.149%); first/second 500-iteration endpoint changes were −1.130/−3.054%. Mean absolute liquid imbalance worsened from 51.120% to 159.315% of feed between those halves. Across N1–1000 mean absolute liquid/vapor/mixture imbalance was 105.217/1.442/61.821%; terminal values were 165.412/1.157/97.398%. Whole/lower inventory ranges were 4.230/7.250% of window mean, with half-window mean changes −2.130/−3.406%. Upper inventory reached 116.750 kg. These fail the declared conservation and inventory thresholds.

Terminal brine discharge was 309.838 kg/s liquid and 0.561 kg/s vapor; liquid leaving steam was 0.485 kg/s. Maximum reverse liquid brine inflow/vapor steam inflow across the block was 44.782/17.105% of feed; routing gates fail. Terminal continuity/k/epsilon/VOF residuals were 0.17799/0.0047304/0.0083889/0.003937; terminal momentum residuals were below 0.001, but every residual failed its required throughout-window test. The transcript includes 1709 turbulent-viscosity limiting lines (ratio 1e5); there were no divergence/FPE matches. Execution finite/speed/phase guards passed; no sustained 10× flux stop occurred.

Independent full-cell liquid inventory agrees with the native report. Per-face flux/native report disagreement is ≤2.85e−13 kg/s; phase-sum/native-mixture disagreement is ≤1.14e−13 kg/s. This is accounting consistency, not mass closure. Volume-weighted absolute phase-fraction change is 0.02504, with liquid-volume loss 0.19278 m³. Connected-interface stationarity, the independent high start and persistence remain unestablished. Steady iteration changes do not define physical storage rates.

Spend: 1000/6000 new campaign solves and 2.2646/14 recorded controller-hours; 5000 solves and 11.7354 hours remain, subject to the existing deadline. No additional calculation was selected by the monitor. Scientific interpretation and the next in-scope decision are referred to the designated planner. K=9/head remain idealized assumptions; this single-start block cannot qualify the model or establish physical impossibility.

## Scientific decision after low-start N1000

The low trajectory meets the predeclared stop predicate: both half-window endpoint inventory losses exceed1%, last-half liquid mean absolute imbalance exceeds1% by a large margin, and routing fails. Do not extend it. Verified ledger parity excludes a simple report-summing discrepancy as the explanation; it does not identify the physical/numerical cause of the failed balance. The fixed resistance has not established steady drainage for this start.

Select the predeclared independent fresh +0.30m start for one N0–1000 block with K9, downstream +0.10m, full feed and scale0.1 unchanged. Its narrow value is to determine whether the same failure persists under greater initial submergence or is strongly initialization-sensitive. This is not a parameter tune or continuation of the depleted endpoint. If the same depletion/imbalance/routing stop pattern recurs, close this tested route without consuming remaining budget. A better high-start result remains diagnostic and cannot qualify the failed two-start hypothesis. Existing campaign deadline and caps are unchanged.

## High-start N0–1000 terminal observations

The exact `drain-k9-high-start-n1000` block completed 1000 solves and passed the deterministic artifact verifier. Live reconciliation independently confirmed idle N1000, exited controller/worker, free server1 lock, matching K=9 setup contract and preserved Fluent-local case/data pair. Reports, all seven active residuals and gross/net phase/mixture flux callbacks cover N1–1000 without gaps. N0/N1000 full-cell fields and x0/z0 terminal sections are preserved. [Analysis](../../../PyAnsys/output/full-geometry-drain-resistance/drain-k9-h0p3-scale0p1-20260930T092319Z/drain-k9-h0p3-scale0p1-20260930T092319Z-flow-n00000-20260930T092609Z/analysis.json), [independent audit](../../../PyAnsys/output/full-geometry-drain-resistance/drain-k9-h0p3-scale0p1-20260930T092319Z/drain-k9-h0p3-scale0p1-20260930T092319Z-flow-n00000-20260930T092609Z/monitor-terminal-audit.json), [terminal live receipt](../../../PyAnsys/output/full-geometry-drain-resistance/high-start-n1000-terminal-live-receipt.json).

| Observed N0–1000 metric | Low +0.10 m | High +0.30 m |
| --- | ---: | ---: |
| Liquid inventory loss | 4.149% | 5.147% |
| First/second half endpoint loss | 1.130/3.054% | 1.956/3.255% |
| First/second half mean absolute liquid imbalance | 51.120/159.315% feed | 88.943/193.974% feed |
| Whole/lower half-window mean change | −2.130/−3.406% | −2.688/−3.858% |
| Whole/lower inventory range | 4.230/7.250% mean | 5.266/8.104% mean |
| Mean absolute liquid/vapor/mixture imbalance | 105.217/1.442/61.821% | 141.459/1.751/83.109% |

High-start liquid inventory declined 4652.236→4412.769 kg; the last 200 solves lost another 60.989 kg. Upper-region inventory reached 122.419 kg. Terminal absolute liquid/vapor/mixture imbalance was 186.434/1.566/109.668% of feed. Final brine liquid/vapor discharge was 334.401/0.260 kg/s, with 0.501 kg/s liquid leaving steam. Maximum reverse liquid brine/vapor steam inflow was 59.301/17.934% of feed across the block; the late 500 vapor reverse remains 17.934% while late liquid reverse is zero. Conservation, inventory and routing thresholds fail.

Final continuity/k/epsilon/VOF residuals were 0.17688/0.0042925/0.006755/0.0034304; terminal momentum residuals were 0.00012353/0.00012192/0.00012947. Every active residual failed the required throughout-window test. There were 1709 turbulent-viscosity limit lines at ratio 1e5, still affecting 160 cells at the end, and no divergence/FPE matches. Finite, speed and phase-bound execution guards passed, with no sustained 10× net-flux event.

Independent inventory reduction agrees with the native report; all per-face native/flux sums agree within 2.85e−13 kg/s and summed phases/native mixture within 1.14e−13 kg/s. Ledger parity does not establish conservation. Volume-weighted absolute liquid-fraction change was 0.02513 and liquid-volume loss 0.27158 m³. Connected-interface stationarity, two passing independent starts and persistence remain unestablished. Steady iterations supply no physical storage time.

The high-start observations repeat the declared depletion/imbalance/routing stop pattern. This monitor selected no further solve and referred the outcome to the planner for scientific interpretation and the campaign decision. Both endpoints remain unqualified; no global physical-impossibility claim follows. Total new campaign spend is 2000/6000 solves and 16273.657 seconds (4.5205/14 recorded controller-hours); remaining caps are 4000 solves/9.4795 hours, subject to the existing deadline.

## Final scientific disposition

Both starts meet the predeclared stopping predicate; close this fixed K9/head route unqualified. Higher initial submergence did not remove the failure pattern. Stop further iteration on both trajectories and do not use unused budget to start another treatment. The root cause remains unresolved; no physical impossibility or universal steady-model conclusion follows. [Closure and claim limits](closure.md).

# Results — steady VOF solver-method diagnostic

## Verified observations

The fresh N0 alpha/pressure/mesh fields match the previous K9 low-start reference exactly; zero velocity and initial liquid mass 4096.7698038261215 kg were verified. The SIMPLE/pseudo-time inactive/all-standard-URF0.3 settings passed native readback and save/reopen verification. Build evidence is linked in phase-state.yaml.

The single N0–1000 job completed; launch observations below are historical. The deliberate N1 instrumentation interruption passed native iteration/idle, callback and native report checks, then continued the same fields. Launch reconciliation verified native N5, Fluent iterating, controller PID47660 alive and the server1 lock held; callback evidence advanced through N5 with no capture error or stop reason. This is a timestamped launch observation, not a promise of continued activity. Exact receipt and live run manifest are in phase-state.yaml; launch-live-proof.json is under PyAnsys/output/steady-vof-solver-method.

## Interpretation and claim limits

The diagnostic is closed unqualified: substantial method sensitivity, but the combined improvement criterion fails. [Scientific disposition and next recommendation](closure.md). This compares a numerical-method package on unchanged physics; it cannot separately attribute effects to coupling, pseudo-time or relaxation. Compare conservation, inventory, routing, residual/clipping and spatial evidence together at the bounded horizon. A single-start improvement cannot establish initial-condition independence, physical validity or a qualified separator. Equal iteration counts do not imply equal numerical progress.

## Monitoring

The existing schedule andy-cfd-monitor-sol-6-1-high is PAUSED after terminal review and handoff. Its monitoring destination remains Monitor phase 9. Runtime model/effort is not exposed by the configuration API; the intended monitor configuration remains GPT-6.1 Sol/high. No automatic continuation beyond1000 solves is authorized.

## N1000 terminal observations and matched comparison

The exact job `steady-vof-simple-low-n1000` completed all 1000 solves, including the N1 instrumentation interrupt followed by 999 unchanged-state solves. The deterministic artifact verifier passed. Independent live reconciliation confirmed idle N1000, exited controller/worker, a free server1 lock, the SIMPLE/pseudo-time-inactive/eight-URF-0.3 contract and a saved Fluent-local case/data pair. Native reports and gross/net face callbacks cover N1–1000 without gaps. The residual transcript contains one identical duplicate N1 row from the instrumentation restart; its unique seven-equation history covers N1–1000 without conflicts. Raw evidence remains intact. Initial/final full fields and both terminal axial sections are present. [Analysis](../../../PyAnsys/output/steady-vof-solver-method/simple-k9-h0p1-urf0p3-20260930T155922Z/simple-k9-h0p1-urf0p3-20260930T155922Z-flow-n00000-20260930T160344Z/analysis.json), [independent comparison audit](../../../PyAnsys/output/steady-vof-solver-method/simple-k9-h0p1-urf0p3-20260930T155922Z/simple-k9-h0p1-urf0p3-20260930T155922Z-flow-n00000-20260930T160344Z/monitor-terminal-audit.json), [live proof](../../../PyAnsys/output/steady-vof-solver-method/terminal-live-receipt.json).

| Observed metric | Matched Coupled | SIMPLE package |
| --- | ---: | ---: |
| First500 mean absolute liquid/vapor/mixture imbalance, % feed | 51.120/1.206/30.066 | 68.724/0.694/40.393 |
| Last500 mean absolute liquid/vapor/mixture imbalance, % feed | 159.315/1.678/93.577 | 63.809/0.570/37.522 |
| Total liquid inventory loss | 4.149% | 32.905% |
| First/second half endpoint inventory loss | 1.130/3.054% | 28.963/5.550% |
| Last200 inventory change | −53.871 kg | −16.659 kg |
| Last500 reverse liquid brine/vapor steam maxima, % feed | 0/17.105 | 4.149/9.606 |

The late500 liquid/mixture mean absolute errors reduce by 59.948/59.903%, meeting the two ≥50% arithmetic thresholds. The simultaneous inventory-not-worse condition fails: mass falls 4096.770→2748.719 kg and both half-window endpoint losses exceed the Coupled reference. Routing metrics are mixed; late liquid reverse inflow is worse, vapor reverse inflow is smaller, and terminal vapor discharge through brine rises from 0.561 to 6.948 kg/s. These observations do not meet the combined predeclared material-improvement condition; they are referred to the planner without promoting this endpoint. Equal iteration counts do not imply equal numerical progress, and this package cannot isolate coupling, pseudo-time or URF effects.

Absolute gates remain failed: full-window mean absolute liquid/vapor/mixture imbalance is 66.267/0.632/38.957%, terminal 10.462/0.070/6.162%. Whole/lower inventory ranges are 48.993/52.562% of window mean and half-mean changes −13.214/−14.927%; upper inventory ends at 84.541 kg. Terminal liquid brine discharge is 104.688 kg/s, liquid steam discharge zero, and vapor steam discharge 73.799 kg/s. Across the complete block reverse liquid brine/vapor steam maxima are 434.523/9.606% feed. Neither an isolated final vapor balance nor zero final liquid carryover rescues failed closure, inventory and routing.

All seven residual histories fail their throughout-window threshold. Final continuity/k/epsilon/VOF residuals are 0.07664/0.0051723/0.0073929/0.0044131; final x/y/z momentum residuals are 5.958e−5/5.7515e−5/6.2455e−5. There are 1879 turbulent-viscosity limiting lines at ratio 1e5, continuing in 38 cells at the endpoint; no divergence/FPE matches. Execution finite/speed/phase guards passed, with no recorded numerical stop or capture error.

Independent initial-field comparison is exact. Terminal cell inventory matches the native report; every per-face native/flux sum agrees within 2.56e−13 kg/s and phase/native-mixture face sums within 2.85e−14 kg/s. This checks the ledger, not conservation. Volume-weighted absolute phase-fraction change is 0.06439 and liquid-volume loss 1.52880 m³. Connected-interface stationarity, initial-condition independence and save/reopen persistence remain unestablished. No physical storage rate is inferred from steady iteration changes.

Spend is exactly 1000/1000 diagnostic solves and 6239.363 seconds (1.7332/6 controller-hours). The iteration budget is exhausted: zero additional solves are authorized, despite unused wall-hour allowance. No follow-on run was launched by this monitor. The single-start diagnostic is closed unqualified; see closure.md for the scientific disposition.

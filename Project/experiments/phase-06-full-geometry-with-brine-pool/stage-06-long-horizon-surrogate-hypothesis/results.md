# Phase 06 / Stage 06 — long-horizon surrogate hypothesis — results

## Status

**COMPLETED CALCULATION; NUMERICAL-ADEQUACY LIMIT RECORDED.** The clean
successor `P6-S6-H-server2-20260831T004750Z` completed all 100 declared
100-iteration control intervals after a 50-iteration smoke, reaching the
authoritative native report coordinate 25,050. It retained 10,051 points for
every required report history and a paired chunk-100 endpoint checkpoint. The
checkpoint pair was independently verified as readable on server 2.

The runner blocked only after the calculation, when its PyFluent residual
monitor capture did not populate within 20 seconds. No named `final.cas.h5`
pair was written because that capture preceded final-save logic. This is a
numerical-adequacy/evidence gap, not a solver-advance failure: the chunk-100
checkpoint is the proven endpoint pair and all report histories span the
declared run. F4 is therefore **unavailable**, not replaced by another
diagnostic.

## Pre-run claim boundary

This run tests only the Stage-03/04 **numerical pressure-feedback surrogate**.
It cannot identify the real separator level, setpoint, valve characteristic,
downstream condition, or controller response.

## Reconciled pre-smoke execution attempt

`P6-S6-H-server2-20260831T120000Z` is **BLOCKED_PRE_SMOKE**, not a CFD result.
The runner saved/reloaded the prepared child before its 50-iteration smoke test,
then detected that Fluent had reduced report-file destinations to relative
names. Because no explicit working directory had been declared for those
relative paths, the runner stopped before any solve rather than risking output
in the wrong location. No long-horizon iteration, residual capture, final pair,
or scientific observation is attributed to this attempt. The successor run
uses a fresh path and fixes Fluent's working directory to the declared monitor
directory before save/reopen verification.

`P6-S6-H-server2-20260831T003300Z` is also
**BLOCKED_BEFORE_LONG_HORIZON**. It passed the report-path save/reopen gate and
issued its 50-iteration smoke, but the runner incorrectly used Fluent's
inherited RP iteration value as the progress coordinate. That value remained
`1556`, a known non-authoritative quantity for this F11 lineage. No
10,000-iteration result or phase conclusion uses this attempt. The next fresh
attempt validates every chunk from native coordinates in the redirected report
files, which are the same coordinate used by the retained Phase-06 discovery
evidence.

`P6-S6-H-server2-20260831T004100Z` is
**BLOCKED_DURING_FIRST_CONTROL_CHUNK**. It completed the 50-iteration smoke,
with the authoritative redirected report coordinate reaching 15,050, then
recorded the start of control chunk 1 and did not return from its one
100-iteration PyFluent call. A later read-only live-session inspection found
Fluent serving and quiescent, with no connected clients; no final pair or
residual capture existed. This is an execution blocker, not evidence for or
against H6. The clean server-3 successor keeps the scientific contract fixed,
but divides each 100-iteration control interval into two independently
report-verified 50-iteration calls before the single unchanged feedback update.

`P6-S6-H-server3-20260831T004552Z` is **BLOCKED_OWNERSHIP_PREFLIGHT**. Its
direct Fluent state gate reported `iterating=true`, so it made no case change
and no solver call. The activity-window probe alone had been insufficient to
prove ownership. The active server-2 successor has since passed the direct
three-sample quiescence check; this ownership event is not scientific evidence.

## Run evidence and planned figure completeness

| Planned evidence | Status | Result / limit |
|---|---|---|
| F1 — numerical-pool proxy and pressure | Complete | [F1](figures/P6-S6-H-server2-20260831T004750Z/f1_proxy_and_pressure.png) shows the proxy does not return to the assumed 200 kg target after the pressure actuator reaches its lower bound. |
| F2 — phase liquid balance | Complete | [F2](figures/P6-S6-H-server2-20260831T004750Z/f2_phase_liquid_balance.png) retains the physical-sign phase-2 balance; its derived late net rate remains positive. |
| F3 — storage and closure | Complete | [F3](figures/P6-S6-H-server2-20260831T004750Z/f3_storage_and_closure.png) shows continuing lower-region and global phase-2 storage with retained imbalance. |
| F4 — residual histories | Unavailable | PyFluent residual monitor set did not populate after the completed run. No residual-convergence assertion is made. |

The portable raw histories and exact reductions are in
[report histories](figures/P6-S6-H-server2-20260831T004750Z/raw/report_histories_20260831_145202.json)
and the [analysis summary](figures/P6-S6-H-server2-20260831T004750Z/summary.json).

## Observed numerical behaviour

**Observed.** The lower-region phase-2 proxy began at 187.79 kg and ended at
284.83 kg. In the final 1,000 native iterations (24,051–25,050), its mean was
284.45 kg, range 281.61–287.58 kg, and linear slope
+0.00249 kg/iteration. It therefore remained about 84 kg above the deliberately
non-plant 200 kg target and continued to rise slightly rather than forming a
bounded target-centred state.

**Observed.** The controller initially moved the pressure from 1.120 to
1.125 MPa gauge, then reached its declared lower bound of 1.115 MPa gauge by
the third control endpoint. It remained there for 98 of 100 recorded control
endpoints. The pressure cannot be reduced further within this numerical setup.

**Observed.** The final-1,000-iteration mean derived phase-2 net liquid rate
was +16.10 kg/s (range +12.06 to +20.02 kg/s); full-domain imbalance averaged
+16.11 kg/s and relative imbalance averaged 0.08115. Total phase-2 mass also
continued to rise, with a late slope +0.00494 kg/iteration. These are report
sign-convention-aware quantities: physical outlet discharge is the negative of
the raw Fluent outward report, so the plotted net is inlet minus physical
brine and steam discharge.

## Interpretation and conclusion

**Hypothesis H6.** The Stage-04 lower proxy slope was a long transient toward
a bounded numerical-surrogate state after pressure saturation.

**Result.** H6 is weakened. At the full 10,000-iteration horizon the bounded
surrogate is still materially above its assumed target, has a positive proxy
slope, and retains a positive phase-liquid accumulation/imbalance signal.
The long calculation strengthens the Stage-04 finding: this F11 steady
Mixture/RNG bracket cannot establish a controlled state even for the explicitly
nonphysical bounded pressure-feedback surrogate.

**Claim boundary.** This does not establish that a real separator cannot be
level-controlled. The proxy/target/actuator are numerical stand-ins, and the
plant sensor datum, target/band, valve/line characteristic, downstream
condition, and controller dynamics remain missing. The unavailable residual
history further means this is a bounded failure-to-establish result, not a
convergence-certified physical conclusion.

## Working-assumption update and handoff

| Assumption | Status after Stage 06 |
|---|---|
| `y≤0.10 m` phase-2 mass is a useful numerical control input | **Questioned**: it responds, but did not yield a target-centred state. It is still not a physical level measurement. |
| Bounded brine pressure can represent a real level-control actuator | **Materially challenged** for this F11 steady bracket: it saturated without arresting the numerical accumulation. |
| A steady Mixture/RNG surrogate can establish the requested physical controlled pool | **Materially challenged**: this completed long test did not establish it. |
| Missing plant control data can be bypassed by a numerical surrogate | **Materially challenged** for the physical Phase-06 question. It bounds a numerical result only. |

The verified endpoint checkpoint is
`C:\\Users\\syok443\\Documents\\FluentRuns\\P6\\S6\\long-hypothesis-server2-20260831T004750Z\\checkpoints\\checkpoint-chunk-100.cas.h5`
with paired `.dat.h5`; it is not silently relabelled as the missing named final
pair. Further progress toward a physical controlled-pool claim requires the
human/phase-planner to choose a new model/control scope and supply the missing
plant control information.

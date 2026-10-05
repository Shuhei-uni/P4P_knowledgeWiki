# Phase 9 — Steady VOF pool feasibility (Andy)

**Current disposition after the authorized extension:** closed unqualified at N2000 on 30 September 2026. The endpoint is preserved and Fluent is idle. No further solves are selected; supervision ends after this review. See [results](results.md#completed-n10002000-extension-unqualified) for the combined evidence, interruption limits and next scope recommendation. Earlier authorization and closure text below is historical.

**Human-authorized continuation on 30 September 2026:** Andy requested resumption. Continue the preserved h_i=0.30 m, scale-0.1 endpoint from native N1000 to N2000, with unchanged physics and numerical settings. This explicitly extends the prior stopping allowance by one 1000-iteration block, within the original 12000-iteration/48-hour total budget. A four-hour execution guard bounds this block; earlier stop gates remain active. No endpoint is qualified. Andy subsequently authorized resuming supervision: the updated Phase 9 heartbeat checks every 30 minutes, reviews this bounded extension and pauses after terminal review. The obsolete overnight cutoff is superseded by the current execution deadline in phase-state.yaml. Compare conservation, inventory drift, routing, all active residuals and spatial changes with N1000 before selecting further work. This single-start continuation cannot establish initial-condition independence or physical validity.


## Previous closure (superseded only by the bounded extension above)

**Closed unqualified on 30 September 2026.** Both scale-0.1 initial-level
comparisons completed N1000 and failed conservation, inventory, routing and
convergence criteria. The allowed numerical recovery is exhausted. Fluent is
idle and endpoints are preserved. No further solves are selected. See
[closure.md](closure.md) for the bounded conclusion and claim limits.

Selected and execution authorized by Andy on 29 September 2026: “Sounds good.
do any additional planning and execute the plan.” This follows agreement to
try a standing pool while retaining **steady state**. Phase 7b remains closed;
its endpoints are not qualified parents and its automations remain paused.
Shuhei's phases and Fluent sessions are outside this phase's authority.

## Evidence anchors

**Verified project evidence:** [Phase 7b closure](../phase-07b-full-geometry-liquid-removal/closure.md)
found no qualified steady ideal-collector case. E8 is incomplete at N128,
not a failed startup test. [Historical resolved-outlet studies](../parallel-andy-studies/resolved-brine-outlet.md)
show excessive initial drainage, a very short bounded hydrostatic-rest test,
and later failure of low-feed long holds despite small residuals. They did not
test this steady implicit VOF comparison. [Phase 6](../phase-06-full-geometry-with-brine-pool/conclusion.md)
used a different mesh and steady Mixture with pressure feedback, and did not
establish a stationary pool. Neither history proves physical impossibility.

The existing 620,431-cell full geometry includes the brine boundary. Its lower
edge is about 0.978 m above the vessel floor. Reopening that boundary requires
no CAD change. Initial pool levels and downstream conditions are numerical
assumptions, not measured plant levels or validated drain conditions.

**Reported method evidence:** Fluent 2025 R2 supports steady implicit VOF,
Coupled pressure–velocity and Global Time Step pseudo-time. Steady VOF requires
a result independent of initial conditions and distinct phase inflows:
[VOF steady/transient restrictions](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_vof_ss_td.html),
[VOF setup](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_mphase_using_steps_vof.html).
The split pure-phase inlets satisfy the distinct-inflow premise. Initial-state
independence must be tested, not assumed.

**Interpretation:** explicitly representing the pool interface and a spatially
consistent downstream pressure is a scientifically different test from
adjusting Phase 7b's sink or repeating steady Mixture pressure feedback.
Shuhei's source tracking, film growth and low carryover do not establish
combined conservation and cannot supply a qualified parent for this phase.

## Phase contract

Question: can the existing full geometry, with separate full-feed inlets and
a declared hydrostatic downstream reservoir condition, support a stationary,
conservative implicit-VOF pool solution independent of two initial pool levels?

Hypothesis: with an interface-aware representation, no volumetric sink and a
hydrostatically consistent open brine exit, liquid discharge can balance feed
without progressive pool accumulation or vapor short-circuiting.

Retain the 620k geometry, full-feed material/inlet basis, gravity and RNG k–ε.
Replace Mixture/slip and the artificial collector by implicit VOF and the
existing pressure outlet. Energy, phase change, DPM and EWF remain off.
No sink, imposed brine mass-flow, level controller or physical transient run.
Pseudo-time is only a numerical steady-solution aid. Use fresh mesh/setup
initialization, never an unconverged Phase 7b flow field as a qualified parent.

The accepted departure from the previous no-pool preference is explicit: the
pool now provides the liquid head and resolved interface needed to test the
actual elevated drain. It is a feasibility model, not a fine-droplet separator
model. This phase does not claim mesh independence, dynamic stability, plant
level-control performance or validated mist carryover.

## Candidate experiment families

1. **Selected: steady implicit VOF, fixed downstream hydrostatic head.** Highest
   direct value for the agreed steady-pool question; moderate setup cost and
   bounded compute. Test two initial levels with the same boundary condition.
2. **Deferred: physical transient VOF.** Can test storage and dynamic stability,
   but substantially greater compute and explicitly outside current authority.
3. **Deferred: EWF with an ideal drain.** Cheaper film representation, but the
   elevated existing drain lacks a justified gravity-film-only route; it cannot
   settle standing-pool balance and is not the selected phase.

The selected experiment is a PARTIAL REPEAT of the resolved-outlet family with
material deltas: steady implicit VOF, consistent pressure profile, fresh native
model and a predeclared initialization-independence contrast.

## Decision conditions

[setup.md](setup.md) specifies numerical gates before results are known.
Success requires simultaneous phase/native-mixture closure, inventory and
interface stationarity, correct routing, all active residuals, two-start
agreement and a save/reopen continuation. Low residuals alone do not qualify.

Budget: at most 48 solver wall-hours and 12,000 total iterations, whichever
comes first, including diagnostics and any numerical recovery. Discovery up
to 4,000 per initial level; reserve 2,000 for save/reopen persistence and 2,000
for implementation verification or one justified solver-aid contrast. All
retries count. No open-ended pressure or relaxation sweep.

One supported smaller pseudo-time scale may be tested if startup is stiff,
with the same physical model and boundary conditions. Configuration failures
remain untested until repaired. Persistent drift, imbalance, initial-condition
dependence or budget exhaustion closes the bounded route as unqualified or
inconclusive; it does not prove that no steady physical solution exists.

## Overnight supervision authorization

Andy requested automatic checks and in-scope scientific decisions until
07:30 on 30 September 2026, Pacific/Auckland (29 September 18:30 UTC).
Use a thread heartbeat every 30 minutes. Do not use the failed CLI thread-resume
hook. Review the N1050 drift before choosing further compute; preserve the
existing scientific envelope and total budget. No blind continuation.
At the cutoff, issue no new calculations; stop any owned running batch at an
iteration boundary, preserve its endpoint and record partial status. The
Phase 9 runner enforces this deadline from phase-state.yaml. Endpoint saving
and a final evidence summary may finish after the cutoff. A newer human pause
always takes precedence. Phase 7b automations remain paused.

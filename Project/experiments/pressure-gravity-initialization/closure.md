# Pressure/gravity initialization campaign — closed unqualified

Closed at the recorded six-unsuccessful-contrast limit on 3 October 2026. Seven contrasts used **85 new solved iterations** and **21.45 minutes of tracked run-controller time**, including run preparation and evidence collection. Separate setup and idle time are not mislabelled solver time: the entire elapsed campaign was 3.14 hours, a conservative upper bound on all controller activity that remains below the eight-hour limit. No time or iteration extension was used.

Fluent server1 is idle at G N1; its controller and wrapper are absent, the writer lock is available, and all seven saved case/data pairs remain on Fluent's local disk. [Current closure verification](../../../PyAnsys/output/pressure-gravity-initialization/campaign-final-live-review.json). No endpoint is a qualified operating parent. Phase 7b and Phase 9 remain closed; Shuhei's sessions were not used.

## What the experiments established

| Contrast | Solved/requested iterations | Peak speed (m/s) | Liquid inventory change | Outcome |
| --- | ---: | ---: | ---: | --- |
| A: Body-force update 1, two-phase | 1/500 | 25.72918 | -0.806245% | Speed guard |
| B: Low-order face interpolation | 1/500 | 30.92951 | +0.443079% | Speed guard |
| C: Zero gravity, gauge pressure 1.12 MPa | 40/500 | 2.808803e-06 | -2.063075% | Inventory guard |
| D: Zero gravity, equivalent zero gauge | 40/40 | 0 | ~0 | Matched datum predicates passed; diagnostic only |
| E: Gravity restored, equivalent datum | 1/500 | 30.92951 | +0.443079% | Speed guard |
| F: Homogeneous liquid, matched hydrostatic outlets | 1/500 | 4.393725 | ~0 | Speed guard |
| G: Homogeneous liquid, body-force update 1 | 1/500 | 31.84725 | ~0 | Speed guard |

A, B, E, F and G are guarded one-iteration startup tests, not completed 500-iteration convergence studies. C stopped at 40; D deliberately requested only 40. Missing final-100 windows are unavailable evidence, not measured failure. The original reconstructed-interface reference is a separate historical comparison and is not counted in this campaign's 85 iterations.

**Verified observations.** Equivalent pressure representation removed the tiny-flow/interface drift in the zero-gravity C/D comparison. Applying that same representation to the original gravity-on case did not reduce its approximately 31 m/s first-iteration motion. Homogeneous liquid also lost hydrostatic rest, so a liquid–vapour interface is not necessary for this startup failure. Setting body-force relaxation to one worsened that homogeneous response and reversed net routing. Uniform liquid inventory in F/G did not imply continuity: substantial net and gross boundary flows remained.

**Interpretation.** These tests reveal pressure-representation sensitivity in the zero-force control and a separate unresolved gravity-on startup problem. They do not isolate a unique internal algorithmic cause. A quiet exact-zero state does not establish a unique steady liquid inventory. Native pressure-gradient/body-force arrays were zero before saving as well as after reopening; reopening alone cannot explain those initial values. Exact patched cell pressure is not proof of a balanced first assembled momentum and face-flux system. The meaning and timing of BF/BFP storage remain unresolved.

**Claim limits.** The predeclared gate tested whether initialization preserves rest from its first iteration. It did not test whether a disturbed startup could eventually converge. There is no evidence here that a steady separator solution is impossible. Steady iterations are not physical time, so iteration-to-iteration inventory change cannot be integrated against flux as a physical transient balance. No drainage, carryover, separator performance, initial-condition independence or sustained two-phase convergence has been qualified.

Fluent's steady VOF applicability guidance requires independence from initialization and distinct phase inflows; a zero-feed pool specified by its starting inventory does not satisfy that guidance. The static controls were useful diagnostics, but their inventory-retention checks cannot be promoted into physical pool validation. [Fluent 2025 R2 Theory §14.3.3](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_th/flu_th_vof_ss_td.html). The pressure-datum convention and constant-density invariance are documented in [UG §9.15](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/flu_ug/flu_ug_sec_op_press.html). These sources motivate interpretation without identifying the native failure mechanism.

## Recommended next scope

Use a small, analytically checkable **homogeneous hydrostatic column benchmark plus an initialization-sequence audit**, retaining steady operation. The scientific question is whether the same startup disturbance survives after removing separator geometry and boundary complexity. Verify the supported initialization/pressure-patching sequence, matching pointwise pressure boundaries, first assembled-field evidence where documented, and spatial pressure/velocity/flux errors. Do not invent gradient-refresh commands or tune another sequence of relaxation factors.

If the column fails similarly, preserve it as a compact reproducer for Ansys to clarify supported hydrostatic initialization and gradient/body-force assembly. If it preserves rest, focus subsequent work on separator boundary and mesh discretization. A revised startup criterion must distinguish first-iteration preservation from eventual steady convergence, without relaxing operating conservation/inventory/routing evidence.

This requires a new recorded scope because the current campaign fixes full geometry and has reached its failure limit. No new geometry, benchmark calculation, phase number, physical transient, external support message or full-feed run was launched. The monitor is to be paused after terminal review; the user can review this recommendation on return.

## Evidence

The per-contrast sections in [results.md](results.md) link exact run, analysis and review receipts. [setup.md](setup.md) records pre-run hypotheses and criteria. [phase-state.yaml](phase-state.yaml) owns closure, budget and monitor state. Raw/native evidence is preserved; no failed trajectory was extended or promoted.

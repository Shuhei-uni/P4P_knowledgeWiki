# Phase 7.1A Meeting Report — 22 September 2026

**Status:** Discussion draft
**Scope:** Historical V1 absorber reference, Server-3 bottom-pressure-outlet diagnostic, and V2 inlet-loading ramp
**Purpose:** Clarify what has improved, what remains open, and the next numerical decision. This is a report of the tested model states, not a separator-performance or physical-validation claim.

## The story in one minute

The original Phase 7.1A reference (V1) showed the core problem clearly: liquid inventory continued to grow, continuity did not settle, and the lower absorber had almost no liquid available to remove. The absorber source itself was correctly realized, but it could not cure a field that did not supply it with liquid.

The Server-3 bottom-pressure-outlet test is a promising separate routing diagnostic, but it is incomplete. Once the thin outer bottom ring was opened, a large flux passed through it and most of that flux was phase 2 under Fluent's stored sign convention. However, vapour also escapes through the ring, so it is not yet an acceptable liquid-only drain. It needs an artificial bottom pressure-control treatment or other boundary constraint before it can be judged as a viable route.

V2 replaces the V1 uniform inventory-driven absorber with a phase-2-only virtual outlet commanded by the instantaneous liquid-inlet throughput. The ramped V2 run demonstrates the important implementation result: once liquid reaches the lower virtual-outlet zone, the applied source follows the inlet-derived command. Its residual magnitudes, including continuity, are much lower than the historical V1 reference at the stated endpoints, but the V2 inventory is still increasing and the residuals rise again during the continuation. It is therefore more promising discovery evidence, not yet a converged or mass-closed solution.

## Position at this meeting

| Route | What was changed | Decisive observation | What can be concluded now |
|---|---|---|---|
| **V1 reference** | Lower, phase-2-only uniform absorber; steady Mixture/RNG reference on the historical parent. | Over native iterations 1,250–1,500, total liquid mass increased from **943.23 to 1,227.86 kg**. Continuity remained about **0.65–0.95**; every solved iteration reported pressure-outlet reverse flow and turbulent-viscosity limiting. | The V1 state is not stationary. Its source was correctly applied, but it was not receiving useful liquid in the lower zone and did not close the numerical problem. |
| **C8 bottom pressure outlet (Server 3)** | The outermost thin bottom ring was changed from a wall to a **1.120 MPa gauge** pressure outlet after an all-wall liquid-development run. The remaining four bottom bands stayed walls. | In the observed partial history at native 7,800 (C8-P0 active 2,800), ring flux was overwhelmingly phase 2 in magnitude, but phase 1 also crossed the ring. Total liquid mass was still **6,477.04 kg** at the last row. | This is an informative routing diagnostic, not a selected boundary condition: its horizon, mass accounting, residual evidence, and terminal checkpoint are incomplete, and steam escape must be controlled. |
| **V2 inlet-loading ramp** | New 60k-mesh, alpha-weighted virtual liquid outlet: its phase-2 sink command is the instantaneous liquid-inlet throughput. Both inlets ramp from 25% to 100% over 2,000 iterations. | At iteration 4,002 the applied phase-2 source and named removal are both **116.920 kg/s**, matching the final liquid-inlet command. Lower-zone liquid mass reached **2.497 kg**, but total liquid mass increased to **318.661 kg**. | The V2 outlet is demonstrably active once supplied with liquid. It has not established bounded inventory, source-inclusive mass closure, acceptable outlet routing, or steady convergence. |

## 1. V1 baseline: why the original absorber did not solve the problem

The V1 finite reference completed its planned 500-iteration discovery horizon, so it is useful as a diagnostic baseline. It did not, however, approach a usable steady state. The total liquid inventory rose by **284.63 kg** across the late 250-iteration window, while continuity stayed of order one rather than settling.

The key interpretation is not that the lower absorber was absent or incorrectly configured. Its integrated phase-2 source readback was **−116.92 kg/s**, matching its command. Instead, the lower-zone liquid-mass report stayed zero while liquid accumulated elsewhere. In practical terms, liquid was not being driven into the absorber region strongly enough for that implementation to provide a meaningful removal path.

This separates two questions that should not be conflated:

1. **Source realization:** the V1 phase-2 absorber was present and auditable.
2. **Field and balance response:** the solution still accumulated liquid, retained reverse flow, and did not converge.

## 2. Bottom pressure outlet: useful routing signal, but vapour leakage is a design constraint

The independent Server-3 C8 family developed the all-wall field for 5,000 active iterations, then changed only the thin outer bottom ring after the predeclared lower-liquid trigger was met. This is deliberately a local artificial-boundary test; it is not a claim that the physical separator has an equivalent open bottom outlet.

At the last observed C8-P0 row, the ring reports approximately **−1,720.11 kg/s** phase 2 and **−8.32 kg/s** phase 1. The signs have not yet been independently normalized in this partial package; the useful observation is the phase composition and relative magnitude. The ring is strongly liquid-dominated, but it is not phase-exclusive. The regular steam outlet also continues to carry a substantial phase-1 component.

That makes the next technical issue concrete: the bottom boundary needs a controlled artificial pressure treatment that prevents or sharply limits unwanted steam escape while preserving the useful liquid-routing signal. The present partial run cannot tell us whether such a treatment will close the source-inclusive balance or bound inventory.

The requested native **pressure** and **phase-2 volume-fraction** contours have verified live sources on Server 3 (the Y–Z `x = 0 m` plane in the stopped C8-P0 state), but their Fluent hardcopy export stalled before files were created. They are intentionally not replaced by substitute images here. The final report should add those two native exports plus the continuity history when the Server-3 post-processing endpoint is responsive.

## 3. V2 ramped inlet loading: the virtual outlet begins to work once liquid arrives

V2 changes the removal law rather than simply increasing a source strength. The 715-cell lower virtual-outlet zone removes phase 2 in proportion to the liquid volume fraction available locally, and its commanded removal follows the liquid inlet. It does not directly delete phase 1.

The ramped run reached its planned 2,000-iteration horizon and was subsequently continued to iteration 4,002. The initial lower zone was essentially all vapour, so its removal was initially zero; this was expected starvation behaviour. As the ramp developed liquid into the lower region, the source began to realize its command. From iteration 501 onward, the recorded difference between the named removal and the native applied phase-2 source was at most approximately `3e-13 kg/s`.

| V2 monitor | Iteration 2,000 | Iteration 4,002 | Reading |
|---|---:|---:|---|
| Liquid-inlet flux | 116.482 kg/s | 116.920 kg/s | The schedule reached its declared 116.92 kg/s liquid target. |
| V2 named removal | 116.482 kg/s | 116.920 kg/s | The virtual outlet follows the inlet-derived command once liquid is available. |
| Total liquid mass | 183.595 kg | 318.661 kg | Liquid inventory is still increasing, not bounded. |
| Lower-zone liquid mass | 0.103 kg | 2.497 kg | The lower virtual-outlet zone is no longer effectively starved. |
| Phase-2 flux at steam outlet (outward-positive) | 9.156 kg/s | 22.116 kg/s | Phase routing is still changing materially in the continuation. |
| Continuity residual | 9.62e-3 | 1.73e-2 | Finite, but higher at 4,002 than at 2,000; it does not demonstrate convergence. |

The V2 continuity magnitude is substantially below the historical V1 reference endpoint (about `8.09e-1` at V1 native iteration 1,500). That comparison is encouraging but limited: the configurations, mesh, initialization, and iteration windows differ. It should therefore be used as a direction-of-travel observation, not as a like-for-like convergence ranking.

### Existing V2 native figures

<div class="figure-grid two">
<figure>
<img src="/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase71A/V2InletLoading/finals/P71A-V2-INLET-LOADING-RAMP/20260922T031500Z/P71A-V2-INLET-LOADING-RAMP-active4002-residual.png" alt="V2 scaled residual histories through iteration 4,002" />
<figcaption><strong>V2 scaled residuals through iteration 4,002.</strong> All residuals remain finite, but the late histories oscillate and rise after the earlier low levels. Continuity ends at 1.73 × 10<sup>−2</sup>; this is not a steady-convergence signature.</figcaption>
</figure>
<figure>
<img src="/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase71A/V2InletLoading/finals/P71A-V2-INLET-LOADING-RAMP/20260922T031500Z/P71A-V2-INLET-LOADING-RAMP-active4002-densityContour.png" alt="V2 mixture-density contour at iteration 4,002" />
<figcaption><strong>V2 mixture-density contour at iteration 4,002.</strong> Native Fluent contour from the continued V2 state. It shows the spatial state at one iteration only; it is not, on its own, evidence of a bounded inventory or preferred phase routing.</figcaption>
</figure>
</div>

![V2 lower virtual-outlet cell register at iteration 4,002](/Users/shuheiyokkaichi/Library/CloudStorage/OneDrive-TheUniversityofAuckland/P4P-Fluent-Artifacts/Phase71A/V2InletLoading/finals/P71A-V2-INLET-LOADING-RAMP/20260922T031500Z/P71A-V2-INLET-LOADING-RAMP-active4002-BottomCellRegister.png)

*V2 lower virtual-outlet cell register. The 715-cell lower source region is shown as a mesh/register view. This confirms the controlled region used by the virtual outlet; it is not a liquid-volume-fraction contour.*

## Meeting conclusion and proposed next decision

The work has moved from an absorber that was correctly applied but effectively inaccessible (V1) to a V2 virtual outlet that demonstrably realizes its inlet-following phase-2 removal command after liquid develops in the lower zone. This is a real implementation and numerical-development improvement.

The system is not yet solved. V2 liquid inventory continues to increase, continuity worsens between iterations 2,000 and 4,002, pressure-outlet reverse flow persists, and phase-2 carryover at the steam outlet grows. The C8 bottom-pressure route adds a potentially useful liquid-routing mechanism, but it also reveals vapour escape through the artificial boundary and has not yet been tested to a complete accounting horizon.

The next decision should therefore be based on a **source-inclusive, phase-resolved balance** and a **late-window inventory slope**, while testing an artificial bottom pressure-control condition that constrains steam leakage. A successful next run must demonstrate all of the following together: bounded or clearly improving liquid inventory, credible phase routing, controlled bottom-boundary vapour flux, finite and improving residual behaviour, and closure that includes the virtual-outlet source and storage term.

## Evidence basis

- [Phase 7.1A context](../../experiments/phase-07-1a-absorber-convergence/CONTEXT.md)
- [V1 RNG reference result](../../experiments/phase-07-1a-absorber-convergence/turbulence-family/t0-rng-reference/results.md)
- [V2 virtual-outlet baseline build](../../experiments/phase-07-1a-absorber-convergence/baseline-v2-virtual-liquid-outlet/results.md)
- [V2 inlet-loading-ramp result](../../experiments/phase-07-1a-absorber-convergence/v2-inlet-loading-ramp/results.md)
- [Server-3 C8 dynamic thin-outer-ring result](../../experiments/phase-07-1a-absorber-convergence/dynamic-thin-outer-ring/results.md)
- [Authoritative V2 run evidence](../../../PyAnsys/output/phase71a_v2_inlet_loading/20260922T031500Z/)

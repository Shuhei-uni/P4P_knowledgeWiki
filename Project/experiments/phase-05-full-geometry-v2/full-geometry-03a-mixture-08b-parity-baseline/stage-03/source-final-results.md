> **Retired source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-final-results.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# 03A Stage 3 — Iteration-Led Results

> **Campaign:** Fluent-recommended convergence sweep  
> **Interpretation status:** user-reviewed branch interpretation added  
> **Plotting rule:** every figure uses native cumulative Fluent iteration on the x-axis.

## Evidence-qualified result map

| Branch | Available presentation | Native range / qualification |
|---|---|---|
| F01 | residual figure only; physical endpoint table | residuals 1–5,500; numerical failure followed at 5,704 |
| F02 | unavailable statement | no valid native endpoint or branch-linked history |
| F03 | five figures | physical 1–5,000; residual gap 982–999 preserved |
| F04 | unavailable statement | no valid native endpoint or branch-linked history |
| F05 | five figures | continuous residual and physical histories 1–3,000 |
| F06 | five figures | continuous joined histories 1–6,000; phase-fraction residual absent during carrier stage |
| F07 | five figures | continuous 1–9,174; 9,151–9,174 is a numerical-failure tail |
| F08 | five qualified partial figures | physical history 9,000–12,000; sampled residual windows are line segments; next-stage tail excluded |
| F09 | five figures | continuous residual and physical histories 1–15,000 |
| F10 | unavailable statement | initialized case evidence only; no valid solve history |
| F11 | five figures | continuous joined histories 1–15,000 |
| F12 | five figures | physical history 1–18,000; residuals are sampled windows, shown as separate line segments |

No figure fabricates continuity. Continuous series are lines; sampled residual exports are separate lines within each retained window and never bridge an unrecorded gap; unavailable evidence has no placeholder plot.

## Result packages

- [F01 residual evidence](figures/03a-stage3/iteration-led/central/f01/figure-01-residuals-vs-iteration.png) · manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/central/f01/f01-iteration-led-manifest.json`; not migrated)
- [F03/F07/F09 iteration-led figures](source-f03-f07-f09-detailed-results.md)
- [F05/F06/F11 iteration-led figures](source-native-queue-final-results.md)
- [F08/F10/F12 iteration-led figures](source-schedule-d-final-results.md)

## Interpretation of plotted branches

The interpretation below is intentionally driven mainly by two figure families:

1. scaled residual behaviour, especially the development of `k` and `epsilon`; and
2. mass convergence, especially relative mass imbalance and total liquid inventory.

The purpose is not to declare a branch converged from residuals alone. The main question is whether each branch shows evidence that additional iteration or a modified continuation strategy could move it toward a more developed and physically useful state.

### F03 — full Mixture, 100%, momentum URF 0.5

`k` and `epsilon` remain jumpy, but the large excursions appear to become less frequent with iteration. The residual history therefore gives some reason to test a longer continuation.

The physical history is much less encouraging. Relative mass imbalance grows strongly and the total liquid inventory continues to rise rather than approaching a clearly bounded level. Additional iterations could still be useful diagnostically, but F03 is a lower-priority continuation because the physical monitors are moving in the wrong direction even while the turbulence residual behaviour appears to improve.

### F05 — full Mixture, 100%, momentum URF 0.3

`epsilon` remains intermittent, but the residual behaviour is not severely unstable and the overall residual envelope is considerably more usable than the more aggressive-URF branches.

The mass-convergence plot is encouraging. The run contains only 3,000 iterations, the total-flow behaviour is comparatively well controlled, and the liquid inventory rises rapidly early in the run before becoming much flatter toward the end. The key unresolved question is whether that apparent liquid-inventory plateau persists or whether the inventory begins drifting again over a longer run.

F05 is therefore a strong candidate for a simple long continuation at the same settings.

### F06 — carrier-first then full Mixture, 100%, momentum URF 0.3

The `epsilon` history is reasonably controlled and `k` remains imperfect but not severely unstable. The physical monitor behaviour is also comparatively good.

As with F05, the main unresolved question is the liquid inventory. The branch is worth continuing for several thousand more iterations to determine whether the inventory approaches a bounded level or continues to grow slowly. Because F06 uses the Fluent-recommended carrier-first startup, it also provides a useful direct comparison against F05 once both have longer full-Mixture histories.

### F07 — full Mixture, progressive inlet loading, momentum URF 0.7

The successful part of the residual history is interesting. `epsilon` appears to improve with iteration, and the relatively calm `k`/`epsilon` behaviour around the earlier low-load portion shows that the branch can enter a much better residual regime under reduced inlet loading.

However, the mass-imbalance behaviour is poor overall, and the branch ultimately fails during the transition toward 80% loading. F07 therefore suggests that gradual loading can create a better-behaved intermediate state, but progressive loading alone is not sufficient to carry the canonical momentum URF of 0.7 to the full operating condition.

### F08 — carrier-first, progressive inlet loading, momentum URF 0.7

The available evidence is too limited for a strong residual interpretation. The sampled `k` and `epsilon` evidence remains jumpy and the available mass-convergence history is poor.

Because the branch is only qualified through the partial 40% state and the next-stage attempt fails, F08 should mainly be treated as supporting evidence that carrier-first startup does not by itself rescue the high-URF ramp strategy. It is not a priority branch for further interpretation until better evidence exists.

### F09 — full Mixture, progressive inlet loading, momentum URF 0.5

F09 is one of the most interesting continuation cases. `k` and `epsilon` show a clear overall decrease through much of the ramp, giving better residual behaviour than several other branches.

The mass behaviour is not good at the final operating condition, but the 40% stage is important. Around the end of the 40% stage the branch approaches a much better mass-balance state, after which the 80% transition drives the mass imbalance and liquid behaviour strongly away from that state again.

This suggests that the useful experiment is not simply to continue the existing 100% endpoint. A better follow-up is to:

- restart from the validated 40% state;
- hold 40% for substantially longer to test whether mass imbalance and liquid inventory continue to settle; and
- if the 40% state remains promising, replace the large 40→80% jump with a gentler continuation such as 40→50→60→70→80% before progressing to 100%.

This would test whether F09's deterioration is caused mainly by the final physical state or by moving through the loading transition too aggressively.

### F11 — full Mixture, progressive inlet loading, momentum URF 0.3

`k` and `epsilon` remain visibly jumpy, so the residual history is not textbook convergence. Despite that, the mass behaviour is strong relative to the rest of the campaign.

The branch reaches very low mass imbalance at intermediate loading and remains comparatively well behaved after reaching 100%. This makes F11 one of the strongest overall Stage-3 branches. A longer full-load continuation is worthwhile to determine whether the physical monitors remain bounded and whether the turbulence residual envelope eventually settles after the mass behaviour has already become reasonably controlled.

### F12 — carrier-first, progressive inlet loading, momentum URF 0.3

F12 also produces good mass behaviour, although its `k` and `epsilon` residuals remain jumpier than desired. Its physical response is somewhat similar to F09 in that an intermediate loading state becomes particularly well balanced, but F12 carries that favourable mass behaviour through the later loading stages much more successfully.

The branch is therefore a strong result overall, though less convincing than F11 from the turbulence-residual perspective. It is worth continuing at full load to see whether the residual intermittency decreases while the relatively good mass behaviour is preserved.

## Follow-up implications

The current plots suggest four distinct follow-up categories rather than one single "best" branch:

- **F05 and F06:** extend the existing full-load runs with no setup change. Their short histories and flattening liquid-inventory behaviour make them the cleanest tests of whether more iteration alone is sufficient.
- **F11 and F12:** extend the existing 100% stages. These are the strongest full-load physical histories and test whether `k`/`epsilon` become more bounded after the mass behaviour has already improved.
- **F09:** return to the promising 40% checkpoint, hold it longer, then investigate a gentler inlet-loading transition.
- **F03:** optional lower-priority extension. Its residual behaviour may be improving, but the worsening mass imbalance and liquid inventory make it less promising than the branches above.

F07 and F08 are primarily useful as evidence that the `0.7` momentum-URF family can enter better low-load states but does not transition robustly toward the full operating condition.

A broader Stage-3 lesson is that the most useful branches do not necessarily show textbook turbulence-residual convergence at the same time as good physical monitors. F11 and F12 in particular show that relative mass imbalance can become strong while `k` and `epsilon` remain intermittent. Future branch decisions should therefore continue to evaluate residual development and physical-monitor behaviour together rather than rejecting a branch solely because the turbulence residuals remain jumpy.

## Source and validation records

- Server-1 manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server1/server1-iteration-led-manifest.json`; not migrated)
- Server-2 provenance manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server2/server2-provenance-manifest.json`; not migrated)
- Server-3 manifest (historical machine artifact path: `../../../../PyAnsys/output/03a_stage3/iteration-led/server3/server3-iteration-led-manifest.json`; not migrated)
- [Stage-3 checkpoint evidence](source-results-20260821.md)

The prior cross-plots, cross-diagnostics, and load-axis ramp-response figures have been retired from this report. Their underlying evidence remains in the machine-readable packages above.

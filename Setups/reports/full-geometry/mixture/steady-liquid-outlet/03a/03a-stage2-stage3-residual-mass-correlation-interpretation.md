# 03A — Stage 2 / Stage 3 Residual, Mass-Balance, and Physical-Convergence Interpretation

## Purpose

The next convergence stage should not reduce the problem to one residual target or one mass-balance number. The evidence from Stage 2 and Stage 3 is better interpreted through four separate questions:

1. **Numerical stability:** are the residual envelopes bounded, or are they growing, broadening, and producing repeated large excursions or solver failure?
2. **Global conservation and stationarity:** is mass imbalance small and stable over a sustained window, and is total liquid inventory approaching a bounded state rather than drifting?
3. **Physical separator behaviour:** are liquid and vapour being routed through physically sensible outlets, without unacceptable carryover, vapour short-circuit, or persistent outlet reversal?
4. **Robustness to numerical/model strategy:** does a favourable state survive changes in continuation history, loading strategy, under-relaxation, and turbulence model?

Stage 3 produced several branches with good mass behaviour while the turbulence residuals—especially `k` and `epsilon`—remain less convincing. Stage 2 N5 is important because its temporary switch from RNG `k-epsilon` to standard `k-epsilon` produced a substantially tighter residual envelope **at the same time as** a large improvement in the diagnostic mass imbalance.

That N5 observation is a strong lead, but it should not yet be described as a general residual–mass correlation or as proof that standard `k-epsilon` is the correct final turbulence model. It is one controlled model intervention in which two diagnostics improved together.

## Stage 3 — residual quality versus mass behaviour

| Branch | `k` / `epsilon` interpretation | Mass / inventory behaviour | Combined interpretation |
|---|---|---|---|
| **F03** | Jumpy, but large `k`/`epsilon` excursions appear to become less frequent | Very poor: endpoint mass imbalance ~336%; liquid inventory continues growing | Residual trend has some promise, but the physical monitors are moving strongly in the wrong direction |
| **F05** | `epsilon` remains jumpy but is not severely unstable | Reasonably good relative to the campaign: endpoint imbalance ~14.3%; liquid inventory rises rapidly then appears much flatter near the end | **One of the best Stage-3 compromises**; only 3,000 iterations, so a longer continuation is justified |
| **F06** | `epsilon` is reasonably controlled; `k` is imperfect but not severely unstable | Reasonably good relative to the campaign: endpoint imbalance ~14.4%; inventory remains controlled enough to justify continuation | **One of the best Stage-3 compromises**; longer continuation should test whether inventory actually becomes stationary |
| **F07** | `epsilon` improves and there is a relatively calm low-load `k`/`epsilon` region | Good only briefly at reduced loading: ~1.2% imbalance at 20%, ~21% at 40%, then failure during the 80% transition | Reduced loading can produce a better-behaved intermediate state, but this branch does not transition robustly toward full load |
| **F08** | Limited and jumpy sampled `k`/`epsilon` evidence | Poor: ~37% imbalance at the validated 40% state; later transition fails | No convincing overlap between good residual and mass behaviour |
| **F09** | **Clear overall decrease in `k` and `epsilon`; probably the strongest Stage-3 turbulence-residual trend** | Poor overall. The 40% history passes close to zero imbalance temporarily, but the actual 40% checkpoint remains ~25.9%; 80% and 100% deteriorate dramatically | **Residual-improving / mass-poor.** The interesting experiment is the 40% state and the transition away from it, not the final endpoint |
| **F11** | `k` and `epsilon` remain visibly jumpy | **Very good relative mass behaviour:** ~5.1% at 40%, ~0.60% at 80%, ~12.4% at 100% | **Mass-strong / residual-intermittent.** One of the strongest physical-monitor branches, but turbulence convergence remains unresolved |
| **F12** | `k` and `epsilon` remain jumpy and are less convincing than F09 | **Very good relative mass behaviour:** ~0.073% at 40%, ~12.0% at 80%, ~11.1% at 100% | **Mass-strong / residual-intermittent.** Strong mass behaviour survives later ramp stages much better than F09 |

Source data: [Stage-3 checkpoint evidence](./03a-stage3-results-20260821-checkpoints.csv) and [Stage-3 final results](./03a-stage3-final-results.md).

## What Stage 3 actually shows

There is **not** a simple Stage-3 relationship of:

```text
better k/epsilon residuals -> better mass balance
```

The strongest examples separate into different groups:

- **Strongest Stage-3 mass behaviour:** F11 and F12.
- **Strongest Stage-3 `k` / `epsilon` trend:** F09.
- **Best Stage-3 compromise between both criteria:** F05 and F06.

F11/F12 show that strong mass behaviour can exist while turbulence residuals remain intermittent. F09 shows almost the reverse: turbulence residuals can improve while the mass behaviour becomes unacceptable. F05/F06 are currently the closest Stage-3 cases to improving both dimensions simultaneously, although neither dimension is yet strong enough to call the solution converged.

### What should remain only a hypothesis

The Stage-3 families are not a clean one-variable experiment. Across the branches, combinations of the following change:

- momentum URF;
- direct versus progressive inlet loading;
- full-Mixture versus carrier-first startup;
- total iteration budget;
- time spent at intermediate loading states;
- inherited starting field.

For example, F05 contains only 3,000 iterations, while F11 and F12 extend to much longer histories. The strongest Stage-3 branches are disproportionately associated with `momentum URF = 0.3`, but that does **not** isolate URF as the cause of better mass behaviour.

The defensible statement is therefore:

> Lower momentum URF and progressive-loading strategies are associated with several of the strongest mass-behaviour branches, but loading history, startup strategy, and iteration budget remain confounded.

That is a useful design signal, not yet a demonstrated mechanism.

## A low endpoint imbalance is not enough

Several branches demonstrate why a single low mass-imbalance value should not be treated as convergence.

F09 passes close to zero imbalance temporarily during its 40% stage, yet the actual 40% checkpoint remains approximately 25.9% and the later stages deteriorate strongly. F11 and F12 also move substantially between loading checkpoints.

The next stage should therefore evaluate mass convergence over a sustained final window rather than ranking branches by the minimum or endpoint alone. Where the recorded histories permit it, the useful quantities are:

```text
final-window mean |mass imbalance|
final-window variability of mass imbalance
liquid-inventory slope with iteration
liquid-inventory variability
```

A branch that crosses zero once is qualitatively different from a branch that remains close to zero while its liquid inventory is stationary.

## Residual intermittency also needs a more careful interpretation

The target should not simply be "make `k` and `epsilon` perfectly flat."

There is an important distinction between:

- a **deteriorating residual envelope**: excursions grow, become more frequent, couple to worsening physical monitors, or lead toward AMG/FPE failure; and
- a **bounded residual envelope**: residuals remain intermittent but their statistical envelope stops broadening while the physical monitors become stationary.

Stage 3 already suggests that these two ideas should not be collapsed into one pass/fail criterion. F11/F12 in particular show that mass behaviour can become comparatively strong while `k` and `epsilon` remain jumpy.

If a future long continuation reaches stable mean fluxes, bounded inventory, acceptable phase routing, and a stationary residual envelope that still oscillates, that would need to be distinguished from simple non-convergence. The present evidence is not yet sufficient to decide whether any branch has reached that condition.

## Stage 2 N5 — the strongest simultaneous improvement

Stage 2 N5 tested:

```text
Stage-1 parent
-> standard k-epsilon for 500 iterations
-> restore RNG k-epsilon for 300 iterations
```

During the **standard `k-epsilon`** portion, the final 100-iteration residual statistics were:

| Quantity | Median | P95 |
|---|---:|---:|
| Continuity | `7.8155e-2` | `1.0090e-1` |
| `k` | `2.2840e-3` | `3.4441e-3` |
| `epsilon` | `5.0056e-3` | `1.3436e-2` |
| Volume fraction | `7.2313e-3` | `1.1464e-2` |

At the same time, the diagnostic mass imbalance improved from the Stage-1 value of **17.17%** to **5.24%**.

When RNG `k-epsilon` was restored, both diagnostics deteriorated together:

| State | Mass imbalance | `k` median | `epsilon` median | `epsilon` P95 |
|---|---:|---:|---:|---:|
| Standard `k-epsilon` bootstrap | **5.24%** | `2.2840e-3` | `5.0056e-3` | `1.3436e-2` |
| Restored RNG `k-epsilon` | **37.57%** | `8.7831e-3` | `6.5010e-2` | `1.3728e+0` |

The RNG return also increased continuity substantially and broadened the turbulence-residual envelope again.

Source: [Stage 2 N5 results](./03a-08b-stage2-N5-results.md).

## What N5 supports — and what it does not

The strongest N5 statement is:

> **The N5 standard-`k-epsilon` state is currently the clearest observed case where the turbulence-residual envelope and diagnostic mass imbalance improved at the same time.**

This is stronger evidence than saying only that the standard-model residual plot looked cleaner. During N5-standard:

- `k` and `epsilon` became much more tightly bounded;
- diagnostic mass imbalance simultaneously improved to ~5.24%; and
- restoring RNG caused both the residual and mass metrics to worsen together.

However, three limitations are important.

### 1. This is not yet a general residual–mass correlation

N5 is one intervention in which two diagnostics moved together. Stage 3 explicitly shows that those diagnostics can also move independently. The current evidence therefore supports **coincident improvement under the standard-model intervention**, not a general claim that better turbulence residuals cause better mass balance.

### 2. Standard `k-epsilon` changes the turbulence closure, not just the numerics

The N5 result does not isolate a purely numerical stabilisation mechanism. Switching RNG to standard `k-epsilon` changes the solved turbulence model and therefore can change the velocity, turbulence, phase-distribution, and outlet-flow fields.

The N5 endpoint evidence confirms that phase routing changes materially across the model transition. Liquid flow to the steam outlet increases from approximately `1.75 kg/s` during the standard bootstrap to approximately `6.72 kg/s` after RNG is restored, while total liquid outlet flow also changes strongly.

The defensible interpretation is therefore:

> Standard `k-epsilon` produces a substantially different and numerically better-behaved coupled state during N5. It is unresolved whether the improvement is primarily a numerical-stability benefit, a consequence of different turbulence physics, or both.

### 3. N5-standard is improved, not yet converged

A diagnostic mass imbalance of **5.24%** is a large improvement over the Stage-1 and restored-RNG states, but it should not yet be labelled a satisfactorily converged mass balance. Likewise, a continuity median of approximately `7.8e-2` is improved but not by itself evidence of a converged solution.

The correct language is therefore **strongest simultaneous improvement**, not **good residuals plus good mass balance**.

## The most important missing N5 evidence: liquid-inventory history

The original N5 result record explicitly states that its standard-bootstrap and RNG-return monitor artifacts contain no usable temporal liquid-inventory history. The flux and inventory monitor sets contain zero recorded points, so no inventory trend can be inferred from N5.

That matters because the intended combined convergence target contains three distinct pieces:

```text
bounded residual behaviour
+
stable low mass imbalance
+
bounded liquid inventory
```

N5 currently provides evidence for improvement in the first two only.

A long standard-`k-epsilon` run is therefore valuable not just to see whether the residual and mass improvements persist, but also to collect the missing inventory history and determine whether the solution is actually approaching a stationary liquid state.

## Mass balance is necessary but not sufficient physical evidence

The present note has deliberately focused on residuals, mass imbalance, and inventory because they are the clearest convergence diagnostics available across the campaign. They should not, however, be treated as a complete definition of a physically useful separator solution.

A case could achieve a low total mass imbalance while still having unacceptable phase routing. The broader separator-level assessment should therefore include, where evidence is available:

- liquid flow to the brine outlet;
- vapour flow to the brine outlet;
- liquid carryover to the steam outlet;
- vapour flow to the steam outlet;
- outlet reversal behaviour;
- key pressure-monitor behaviour;
- total liquid inventory and its trend.

For this project, the more complete physical target is:

```text
global conservation
+
liquid-inventory stationarity
+
physically sensible phase routing
```

A low mass-imbalance number alone does not demonstrate that the separator is doing the right thing.

## Broader interpretation framework for the next stage

The next stage should evaluate candidate branches on four dimensions rather than collapsing everything into residuals versus mass balance.

| Dimension | Main evidence | Question |
|---|---|---|
| **1. Numerical stability** | all residual histories, residual envelope, AMG/FPE behaviour | Is the solver approaching a bounded numerical state? |
| **2. Conservation / stationarity** | mass imbalance history, phase balances, liquid-inventory trend | Is the global solution becoming stationary rather than merely passing through a favourable endpoint? |
| **3. Physical separator behaviour** | phase-specific outlet fluxes, carryover, wrong-outlet vapour, pressure and reversal histories | Is the separator routing the phases plausibly? |
| **4. Strategy robustness** | URF, startup, ramping, turbulence-model and continuation comparisons | Does the favourable behaviour survive changes in how the solution is obtained? |

A branch should become a serious parent candidate only when dimensions 1–3 are simultaneously reasonable. Dimension 4 determines how much confidence should be placed in that candidate and which mechanism should be investigated next.

## Implication for the next stage

The current evidence supports several targeted follow-ups rather than one declared best branch.

- **F05/F06-type damping (`momentum URF = 0.3`)** remains worth extending because these are the cleanest Stage-3 compromises. The main test is whether the apparent mass/inventory behaviour becomes genuinely stationary over a longer interval.
- **F11/F12-type ramping at URF 0.3** remains worth extending because these branches demonstrate very strong relative mass behaviour. The next question is whether the physical monitors remain bounded while the `k`/`epsilon` envelope becomes stationary or continues to deteriorate.
- **F09** remains useful for studying how a promising residual state is lost during the loading transition. The 40% state should be held longer before concluding that its near-zero imbalance interval represents a useful operating state, and a gentler loading transition can then test whether the later deterioration is transition-driven.
- **A long standard-`k-epsilon` run is strongly justified.** It should no longer be treated only as a 500-iteration bootstrap back to RNG. The experiment should test whether the N5-standard simultaneous improvement persists for several thousand iterations while recording liquid inventory and phase-specific outlet histories.

The long standard-model experiment should be interpreted as a **turbulence-model sensitivity / coupled-solution experiment**, not merely as a convergence trick. If it remains favourable, the next question is whether it is numerically easier because it is a more forgiving closure, physically different because it predicts a different strongly swirling flow field, or both.

## Current confidence in the main interpretations

| Interpretation | Confidence |
|---|---|
| Residual quality and mass behaviour are not simply correlated in Stage 3 | **High** |
| N5-standard simultaneously improves turbulence residuals and diagnostic mass imbalance | **High** |
| F05/F06 are worthwhile long-continuation candidates | **High** |
| F11/F12 contain unusually strong relative mass behaviour | **High** |
| A long standard-`k-epsilon` experiment is justified | **High** |
| `momentum URF = 0.3` itself causes the improved Stage-3 mass behaviour | **Unresolved / confounded** |
| Progressive loading itself causes the improved Stage-3 mass behaviour | **Unresolved / confounded** |
| Standard `k-epsilon` directly fixes the turbulence instability | **Plausible hypothesis, not demonstrated** |
| Standard `k-epsilon` is the correct final physical turbulence model | **Weak evidence at present** |

## Central next-stage question

The next stage should therefore not ask only:

```text
Can the run survive?
```

or:

```text
Can k and epsilon be made cleaner?
```

The stronger question is:

> **Can one strategy produce a numerically bounded, globally stationary, and physically sensible separator state at the same time — and does that state persist long enough to distinguish a real solution trend from a favourable transient or continuation artifact?**

N5-standard is currently one of the most interesting clues toward that objective, but it should be treated as a hypothesis-generating result rather than the answer.
# 03A — Stage 2 / Stage 3 Residual and Mass-Balance Interpretation

## Purpose

The next convergence stage should aim for a solution that satisfies **both** of the following at the end of the run:

1. `k` and `epsilon` residuals are stable and reasonably bounded rather than repeatedly jumping; and
2. mass imbalance is stable and acceptably small, with liquid inventory also approaching a bounded state.

Stage 3 produced several runs with very good mass behaviour, but the turbulence residuals—especially `k` and `epsilon`—remain less convincing. Stage 2 N5 is therefore important because its temporary switch from RNG `k-epsilon` to standard `k-epsilon` produced a noticeably better residual envelope **at the same time as** improved mass balance.

This note separates those two criteria before looking for correlation.

## Stage 3 — residual quality versus mass behaviour

| Branch | `k` / `epsilon` interpretation | Mass behaviour | Combined interpretation |
|---|---|---|---|
| **F03** | Jumpy, but large `k`/`epsilon` excursions appear to become less frequent | Very poor: endpoint mass imbalance ~336%; liquid inventory continues growing | Residual trend has some promise, but physical monitors are moving strongly in the wrong direction |
| **F05** | `epsilon` remains jumpy but is not severely unstable | Reasonably good: endpoint imbalance ~14.3%; liquid inventory rises rapidly then appears much flatter near the end | **One of the best Stage-3 compromises between residual and mass behaviour**; only 3,000 iterations, so a longer continuation is justified |
| **F06** | `epsilon` is reasonably controlled; `k` is not good but not severely unstable | Reasonably good: endpoint imbalance ~14.4%; liquid inventory remains controlled enough to justify continuation | **One of the best Stage-3 compromises between residual and mass behaviour**; longer continuation should test whether inventory stabilises |
| **F07** | `epsilon` improves and there is a relatively calm low-load `k`/`epsilon` region | Good only briefly at reduced loading: ~1.2% imbalance at 20%, ~21% at 40%, then failure during the 80% transition | Reduced loading can produce a good residual/mass state, but URF 0.7 cannot carry it robustly toward full load |
| **F08** | Limited and jumpy sampled `k`/`epsilon` evidence | Poor: ~37% imbalance at the validated 40% state; later transition fails | No convincing overlap between good residual and mass behaviour |
| **F09** | **Clear overall decrease in `k` and `epsilon`; probably the strongest Stage-3 turbulence-residual trend** | Poor overall. The 40% history passes close to zero imbalance temporarily, but the actual 40% checkpoint remains ~25.9%; 80% and 100% deteriorate dramatically | **Residual-good / mass-bad.** The interesting experiment is the 40% state and the transition away from it, not the final endpoint |
| **F11** | `k` and `epsilon` remain visibly jumpy | **Very good relative mass behaviour:** ~5.1% at 40%, ~0.60% at 80%, ~12.4% at 100% | **Mass-good / residual-bad.** One of the strongest physical Stage-3 branches, but turbulence convergence remains unsatisfactory |
| **F12** | `k` and `epsilon` remain jumpy and are less convincing than F09 | **Very good mass behaviour:** ~0.073% at 40%, ~12.0% at 80%, ~11.1% at 100% | **Mass-good / residual-bad.** Strong physical behaviour survives later ramp stages much better than F09 |

Source data: [Stage-3 checkpoint evidence](./03a-stage3-results-20260821-checkpoints.csv) and [Stage-3 final results](./03a-stage3-final-results.md).

## What Stage 3 actually shows

There is **not** a simple correlation in Stage 3 of:

```text
better k/epsilon residuals -> better mass balance
```

The strongest examples instead separate into different groups:

- **Best Stage-3 mass behaviour:** F11 and F12.
- **Best Stage-3 `k` / `epsilon` trend:** F09.
- **Best Stage-3 compromise between both criteria:** F05 and F06.

F11/F12 show that strong mass behaviour can exist while turbulence residuals remain jumpy. F09 shows almost the reverse: turbulence residuals can improve while the physical mass behaviour becomes unacceptable. F05/F06 are currently the closest Stage-3 cases to meeting both objectives simultaneously, even though neither criterion is yet excellent.

This means momentum damping and progressive inlet loading appear to help the **physical stability / mass behaviour** of the solution, but they do not automatically solve the `k`/`epsilon` residual problem.

## Stage 2 N5 — the important exception

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

When RNG `k-epsilon` was restored, **both diagnostics deteriorated together**:

| State | Mass imbalance | `k` median | `epsilon` median | `epsilon` P95 |
|---|---:|---:|---:|---:|
| Standard `k-epsilon` bootstrap | **5.24%** | `2.2840e-3` | `5.0056e-3` | `1.3436e-2` |
| Restored RNG `k-epsilon` | **37.57%** | `8.7831e-3` | `6.5010e-2` | `1.3728e+0` |

The RNG return also increased continuity substantially and broadened the turbulence-residual envelope again.

Source: [Stage 2 N5 results](./03a-08b-stage2-N5-results.md).

## Correlation and current interpretation

The most important observation across Stage 2 and Stage 3 is therefore:

> **The N5 standard-`k-epsilon` state is currently the clearest observed case where good `k`/`epsilon` behaviour and good mass balance occurred at the same time.**

This is stronger evidence than saying only that the standard-model residual plot looked cleaner. During N5-standard:

- `k` and `epsilon` became much more tightly bounded;
- mass imbalance simultaneously improved to ~5.24%; and
- restoring RNG caused both the residual and mass metrics to worsen together.

That suggests two somewhat different numerical effects may be present:

1. **Momentum damping / gradual loading** in Stage 3 mainly improves the physical stability and mass behaviour of the flow field. This is most obvious in F11/F12.
2. **Standard `k-epsilon`** may be addressing the turbulence-solution instability more directly, while also producing a favourable mass response in N5.

This does **not yet prove** that standard `k-epsilon` is the correct final turbulence model. N5-standard was only held for 500 iterations, and the experiment was originally designed as a bootstrap rather than a long-run final solution. The key missing evidence is whether the simultaneous residual and mass improvement survives for several thousand iterations.

## Implication for the next stage

The next stage should explicitly target the combined objective:

```text
stable k and epsilon
+
stable low mass imbalance
+
bounded liquid inventory
```

Based on the evidence so far, the most useful starting hypotheses are:

- **F05/F06-type damping (`momentum URF = 0.3`)** gives the best Stage-3 compromise and should be extended to test whether the apparent inventory behaviour actually settles.
- **F11/F12-type ramping at URF 0.3** demonstrates that very strong mass behaviour is achievable, but another change is needed to improve turbulence residual stability.
- **F09** is useful for studying how a promising residual state is lost during the loading transition, but its final mass behaviour makes it a poor direct parent without modifying the continuation.
- **A long standard-`k-epsilon` run is now strongly justified.** It should no longer be treated only as a 500-iteration bootstrap back to RNG. The experiment should test whether the N5-standard combination of bounded `k`/`epsilon` and low mass imbalance persists over a much longer interval.

The central next-stage question is therefore not simply whether a run survives, nor whether the residuals look better in isolation. It is whether a numerical strategy can preserve **both turbulence-residual stability and physical mass convergence at the same time**.
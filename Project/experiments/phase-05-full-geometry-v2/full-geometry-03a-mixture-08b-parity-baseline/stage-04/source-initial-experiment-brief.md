> **Retired source:** Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage4-initial-experiment-brief.md
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Machine-generated artifacts remain with their original external owners; the retired written source is recoverable from Git history.

# 03A Stage 4 — Initial Experiment Brief

## Historical execution status — superseded by the updated result report

> The execution narrative below is the original 2026-08-23 snapshot.  The
> authoritative Server 2 tree was rechecked on 2026-08-27 and contains later
> S4-01/S4-02/S4-03 artifacts, including a complete S4-03 recovery endpoint.
> Use the [updated execution evidence report](source-native-queue-execution-2026-08-23.md)
> for current run status and interpretation. The associated Server 2 evidence
> package was machine-generated and is not part of this written-memory
> migration; the locally retained report-facing plots are under
> [Stage-4 figures](figures/03a-stage4/server2).

## Execution status — S4-03 recovery interrupted (historical snapshot)

The first authoritative native queue was submitted at `2026-08-22T12:30:11Z`
under the non-overwriting label
`03A-stage4-S4-01-through-S4-04-native-20260822T123011Z`.  It was designed to
cold-load the exact F05, F06, and F11 Stage-3 case/data parents for S4-01
through S4-04 and run them sequentially for `+30,000` Fluent iterations each.
S4-04 changes only RNG to standard `k-epsilon`; the preparation readback found
no scientific delta for S4-01 through S4-03.

At submission, the selected friend host was healthy on Fluent 2025 R2 with 18
contiguous solver ranks and approximately 694 GB free.  Fluent owns the solve,
5,000-iteration paired autosaves, transcripts, residual history, physical
monitor histories, and final case/data writes.

A client transport failure at `2026-08-22T20:35:52Z` ended the original local
owner after S4-01 had completed and while S4-02 was running.  Fluent's native
journal continued to the exact S4-02 target at cumulative iteration `36,000`,
then reported a journal-read error before writing the named endpoint, exporting
residuals or transitioning to S4-03.  The only complete native S4-02 autosave is
at cumulative iteration `35,000` (`+29,000`).  A later uniquely named live-field
save is preserved only as forensic evidence because its RP iteration readback
cannot be reconciled with the native-console count.

Recovery attempt `20260823T125548Z` independently cold-prepared S4-03 and S4-04
from the exact same checksum-verified F11 iteration-15,000 case/data pair.
S4-03 retained RNG `k-epsilon`; S4-04 changed only to standard `k-epsilon` and
was prepared to cold-load the F11 parent rather than the S4-03 result.  S4-03
reached cumulative iteration 42,547 (`+27,547`) before a transport timeout
stopped the owner.  Complete paired autosaves exist through cumulative
iteration 40,000 (`+25,000`), but the 45,000 target and named endpoint are
absent.  S4-04 was not submitted.  No numerical fatal signature was recorded,
and no block was replayed.  Every current result remains diagnostic/unresolved
pending checksum, cold-readback and physical-history analysis.  See the
[execution evidence report](source-native-queue-execution-2026-08-23.md).

The exact execution contract and parent-gating rules are recorded in the
[canonical Stage-4 setup plan](setup-source.md).

S4-05 and S4-06 remain gated because the exact F09 40% pair has not yet been
proved accessible on an authenticated available host.  They were not part of
the stopped S4-01-through-S4-04 or recovery queues.

## Overall objective

Develop the most promising **Stage-3 states** rather than restarting the search.

Stage 4 should determine which continuation strategy can produce a sustained state with:

- bounded residual behaviour;
- low and stable mass imbalance;
- bounded liquid inventory;
- sensible liquid/vapour outlet routing.

The main philosophy is:

```text
promising Stage-3 checkpoint
        ↓
continue unchanged OR change one thing
        ↓
determine what actually improves the solution
```

## Standard iteration budget

Use a common Stage-4 budget of:

\[
\boxed{+30{,}000\text{ additional Fluent iterations per experiment}}
\]

The `+30,000` is measured from each experiment's own Stage-3 or Stage-4 parent checkpoint, rather than running every branch to the same absolute native iteration. This keeps **continuation length** from becoming another major changing variable between cases.

Do not stop a branch early simply because it appears converged. The purpose of the long budget is to determine whether apparently good behaviour is genuinely sustained rather than temporary. Early termination is appropriate only for genuine numerical failure such as an FPE, unrecoverable divergence, or equivalent solver breakdown.

For interpretation, inspect the full history but also compare consistent continuation windows such as:

- `0–5k`: immediate response to the Stage-4 continuation/intervention;
- `5–10k`: early developed behaviour;
- `10–20k`: intermediate behaviour;
- `20–30k`: primary final stationarity window.

The final `20–30k` window should receive particular weight when judging residual envelopes, mass imbalance, liquid-inventory slope, phase routing, and pressure/outlet stability.

## Initial six experiments

| Case | Parent | Change | Stage-4 budget | Clear objective |
|---|---|---|---:|---|
| **S4-01** | **F05 100%** | None — long continuation | `+30,000` | Determine whether F05's apparent inventory flattening becomes a genuinely stationary full-load solution with more iteration alone. |
| **S4-02** | **F06 100%** | None — long continuation | `+30,000` | Same test as S4-01, but from the carrier-first branch. Compare against F05 to determine whether startup history still matters after long development. |
| **S4-03** | **F11 100%** | None — long continuation | `+30,000` | Test whether F11's strong mass behaviour persists and whether its jumpy `k`/`epsilon` becomes bounded without any further intervention. |
| **S4-04** | **F11 100%** | Switch RNG → standard `k-epsilon` | `+30,000` | Test the most interesting combined hypothesis: can standard `k-epsilon` calm turbulence behaviour **without destroying F11's already-good mass behaviour?** |
| **S4-05** | **F09 40% checkpoint** | Hold 40% unchanged | `+30,000` | Determine whether F09's promising intermediate state is genuinely stationary or merely passes temporarily through good mass balance. |
| **S4-06** | **S4-05 developed 40% state** | Gentle loading: 50→60→70→80→90→100% | `30,000 total` | Determine whether F09's Stage-3 deterioration came from the aggressive loading transition rather than the final 100% operating condition itself. |

S4-06 should logically follow S4-05 rather than starting from the original short 40% checkpoint. Its `30,000`-iteration budget should be structured as:

```text
50% load  → 5,000 iterations
60% load  → 5,000 iterations
70% load  → 5,000 iterations
80% load  → 5,000 iterations
90% load  → 5,000 iterations
100% load → 5,000 iterations
```

This gives the loading-path experiment the same total Stage-4 iteration budget as the other cases while deliberately giving each intermediate load enough development time to reveal whether the transition remains controlled.

The existing evidence makes these useful contrasts: F05/F06 were among the better residual–mass compromises, F11 had particularly strong mass behaviour despite jumpy turbulence residuals, and F09 had the strongest residual trend but deteriorated badly as loading increased.

## Common monitor/report package

Every Stage-4 case should record the **same data every iteration** wherever Fluent permits it.

### Residuals

Record **all scaled residuals**, not only `k` and `epsilon`:

- continuity;
- velocity/momentum components;
- `k`;
- `epsilon`;
- mixture/volume-fraction equation;
- any other active solved residual.

### Conservation and inventory

Record:

- total mixture mass imbalance;
- total liquid-phase imbalance;
- total vapour-phase imbalance;
- total liquid inventory in the domain;
- Y010 liquid inventory;
- Y030 liquid inventory.

The important result is not just the endpoint value. We want to determine whether:

\[
\frac{dM_l}{dN}\rightarrow0
\]

over the final iteration window.

### Phase routing

Record separately:

- liquid → brine outlet;
- vapour → brine outlet;
- liquid → steam outlet;
- vapour → steam outlet;
- liquid inlet;
- vapour inlet.

This prevents a low total imbalance from hiding incorrect phase routing.

### Pressure / outlet behaviour

Where practical, record:

- brine-outlet pressure;
- steam-outlet pressure;
- representative inlet pressure;
- reversed-flow behaviour or an equivalent outlet-flow indicator.

## Plots for every case

Keep these **branch-by-branch with cumulative Fluent iteration on the x-axis**.

1. **All scaled residuals vs iteration**
2. **`k` and `epsilon` focused residual plot**
3. **Total + phase mass imbalance vs iteration**
4. **Total / Y010 / Y030 liquid inventory vs iteration**
5. **Liquid phase routing vs iteration**
6. **Vapour phase routing vs iteration**
7. **Key pressure/outlet behaviour vs iteration**, if the monitor data is reliable

Then calculate final-window statistics rather than judging plots only by eye:

- mean;
- median;
- P95 / spread;
- slope with iteration;
- min/max where useful.

For the long continuation cases, report these statistics both for the complete `+30,000` continuation and for the final `20–30k` window. This helps distinguish a branch that only improves overall because of its early transient from one that is genuinely stationary near the end.

## What Stage 4 should answer

By the end of these six cases we should be able to distinguish three possibilities:

### A. More iteration is enough

S4-01/02/03 progressively settle and sustain that behaviour over the long continuation without another numerical change.

### B. Turbulence-model choice is important

S4-04 materially improves F11's residual behaviour while preserving or improving its physical monitors over a sustained long-run window.

### C. Continuation path is important

S4-05/06 demonstrate that F09 can retain its promising intermediate state and reach full load through a gentler trajectory.

If none of those produces a convincing sustained state after a common `+30,000`-iteration budget, then Stage 4 should expand into more fundamental changes rather than immediately adding another broad sweep. At that point, insufficient iteration count is a much weaker explanation for the remaining behaviour.

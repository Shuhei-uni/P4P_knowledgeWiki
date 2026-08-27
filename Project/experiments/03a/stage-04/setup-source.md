> **Legacy source:** Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage4-promising-state-development.md  
> **Migration note:** Historical wording, evidence status, and uncertainty labels are preserved; this Project copy is not a reinterpretation. Raw and machine-generated artifacts remain at their legacy paths.

---
record_type: stage-plan
programme: full-geometry
geometry: Full-geomV2-231kcells
physics_family: mixture
campaign: steady-liquid-outlet
record_id: 03A-stage4
lifecycle: active
---

# 03A Stage 4 — Promising-State Development

## Active execution status

The original S4-01-through-S4-04 native queue completed S4-01 and reached the
exact S4-02 iteration budget, but its journal stopped before writing the S4-02
endpoint or starting S4-03.  The S4-02 post-interruption field is preserved as
forensic, diagnostic/unresolved evidence only because Fluent's RP iteration
readback does not reconcile with the final native-console iteration.

Recovery `20260823T125548Z` cold-prepared S4-03 and S4-04 independently from
the checksum-verified F11 iteration-15,000 parent.  S4-03 reached cumulative
iteration 42,547 (`+27,547`) before a transport timeout stopped the owner.  Its
latest complete paired autosave is cumulative iteration 40,000 (`+25,000`);
the target 45,000 pair and named endpoint are absent.  S4-04 remains prepared
from the same F11 parent but was not submitted.  No recovery checkpoint is
parent-eligible.  See the [execution evidence report](source-native-queue-execution-2026-08-23.md).

## Question

Can any promising Stage-3 state sustain bounded residuals, low and stable mass imbalance, bounded liquid inventory, and sensible phase routing over a common `+30,000`-iteration continuation?

## Frozen comparison contract

- Fluent 2025 R2, 3D double precision, steady pressure-based Mixture model.
- Exact Stage-3 parent case/data pairs are cold-loaded independently.
- Each experiment receives exactly `+30,000` Fluent iterations unless a genuine numerical failure stops Fluent.
- Every inherited physical and numerical setting is read back before preparation.
- S4-01, S4-02, and S4-03 have no scientific delta.
- S4-04 changes only RNG to standard `k-epsilon`; it is a model-form sensitivity, not an authority promotion.
- Fluent owns iteration, 5,000-iteration paired autosaves, transcripts, residual export, and endpoint writes through one native journal.
- Python may prepare and audit case-only start artifacts, then submit the native journal once. It must not loop over iterations.

## Initial experiment matrix

| ID | Exact parent | Delta | Budget |
|---|---|---|---:|
| S4-01 | F05 100% endpoint, Stage-3 iteration 3,000 | none | +30,000 |
| S4-02 | F06 100% endpoint, Stage-3 iteration 6,000 | none | +30,000 |
| S4-03 | F11 100% endpoint, Stage-3 iteration 15,000 | none | +30,000 |
| S4-04 | same F11 endpoint | RNG to standard `k-epsilon` | +30,000 |
| S4-05 | F09 40% endpoint, Stage-3 iteration 9,000 | none | +30,000 |
| S4-06 | developed S4-05 endpoint | 50/60/70/80/90/100%, 5,000 each | 30,000 total |

S4-05 and S4-06 remain gated until the exact F09 pair is accessible on an authenticated Fluent host or is transferred and checksum-verified. S4-06 cannot start from the short Stage-3 F09 checkpoint.

## Evidence package

Each experiment records every iteration where Fluent permits:

- all scaled residuals;
- mixture and phase inlet/outlet fluxes;
- total, Y010, and Y030 liquid inventory;
- total mass imbalance and phase-balance inputs;
- brine-entry static/total pressure and outlet-flow reversal indicators.

Interpret using `0–5k`, `5–10k`, `10–20k`, and especially `20–30k` continuation windows. Report complete-history and final-window mean, median, P95/spread, slope, and useful extrema. No endpoint alone can establish stationarity.

## Interpretation boundary

Stage 4 is diagnostic/model-development evidence. It does not establish turbulence-model correctness, mesh independence, plant validation, or separator performance. The initial experiment rationale remains documented in the [Stage-4 brief](source-initial-experiment-brief.md).

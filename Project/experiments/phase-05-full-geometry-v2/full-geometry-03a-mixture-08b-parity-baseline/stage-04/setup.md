# 03A Stage 4 — setup

## Question

Can a promising Stage-3 state sustain bounded residuals, low and stable mass imbalance, bounded liquid inventory, and sensible phase routing over a common long continuation?

Stage 4 tests whether more iteration, turbulence-model form, or loading path is the main remaining limitation. It is diagnostic/model-development work, not a convergence or validation declaration.

## Parent states and controlled deltas

S4-01 through S4-05 each cold-load an exact Stage-3 case/data parent independently. S4-06 is intentionally different: it is a dependent continuation from a successfully verified, developed S4-05 40% state and must not be treated as an independent Stage-3-parent branch.

| Branch | Exact parent | Controlled delta | Budget |
|---|---|---|---:|
| S4-01 | F05 100% endpoint at cumulative 3,000 | none; long continuation | `+30,000` |
| S4-02 | F06 100% endpoint at cumulative 6,000 | none; long continuation | `+30,000` |
| S4-03 | F11 100% endpoint at cumulative 15,000 | none; long continuation | `+30,000` |
| S4-04 | F11 100% endpoint at cumulative 15,000 | RNG → standard `k-epsilon` only | `+30,000` |
| S4-05 | exact F09 40% endpoint | hold 40% unchanged | `+30,000` |
| S4-06 | developed S4-05 40% state | 50 → 60 → 70 → 80 → 90 → 100% loading | `30,000 total` |

S4-05 and S4-06 are gated until the exact F09 40% parent is accessible and checksum/readback verified. S4-06 cannot start from the short Stage-3 40% checkpoint.

S4-04 remains the unexecuted Stage-4 model-form branch. Its parent is the same hashed F11 100% endpoint at cumulative 15,000 used by S4-03, not an S4-03 45,000 continuation. Reported F11 parent SHA-256 from the [execution report](source-native-queue-execution-2026-08-23.md): case `f82125f5d4f17e3c161cfc9f17c2158698eea5132154deef53b16fa6a3b994a5`, data `cb1a2b2b3f6c7bb2d607dd9a8e45c7c161e30a457a5cabe7eb799b1768b78919`. Live re-readback from this checkout is Missing Info.

## Frozen comparison context

- Fluent 2025 R2, 3D double precision, steady pressure-based Mixture model;
- exact Stage-3 parent case/data identity read back before preparation;
- all inherited physical and numerical settings held fixed for S4-01/02/03;
- S4-04 changes only the turbulence-model form to standard `k-epsilon`;
- no reinitialization between parent load and the continuation;
- mesh identity `Full-geomV2-231kcells.msh.h5`.

The common `+30,000` budget is measured from each branch's own parent, not from a shared absolute iteration. This makes continuation length comparable without making absolute cumulative iteration another factor.

## Execution mechanism

The historical S4-01 through S4-03 solves used Fluent native journals for iteration, autosave, residual export, monitors, transcript, and endpoint writes. That journal path is a **human-gated exception**. Any new Stage-4 solve, including S4-04, must use Python/PyFluent (`connect_to_fluent`) unless Shuhei explicitly approves a journal/TUI/batch for that specific run. Do not improvise a journal because the historical queue used one.

## Evidence package

Each branch must record, wherever Fluent permits, the same cumulative histories:

- all scaled residuals;
- total, liquid-phase, and vapour-phase inlet/outlet fluxes;
- total, Y010, and Y030 liquid inventory;
- total mass imbalance and phase-balance inputs;
- brine-entry static/total pressure and outlet-flow reversal indicators.

Interpret full history and consistent windows (`0–5k`, `5–10k`, `10–20k`, and especially `20–30k`), measured from each branch's own parent. Report mean/median, P95 or spread, slope, and useful extrema. No endpoint alone establishes stationarity. Visual PNG envelopes are not a substitute for those window statistics.

## Core figure plan

The planned core figures are the existing Stage-4 report-facing set. Analysis must execute these first; a residual dashboard is supporting evidence unless residual behaviour is itself the sub-question.

| Figure | Question | Plot | X-axis | Y-axis / field | Series / cases | Comparison basis | Reduction | Data source | Instrumentation | Interpretation use |
|---|---|---|---|---|---|---|---|---|---|---|
| F0 cross-branch | Do S4-01/02/03 occupy the same late-window physical envelope? | 2×2 history overlay | continuation iterations from parent, 0–30k | relative mass imbalance; total liquid inventory; liquid→brine flux; brine-entry static pressure | S4-01, S4-02, S4-03 | common continuation length, not shared absolute iteration | raw | portable CSV/JSON package; PNG is the committed report face | per-iteration report files | Distinguish shared limit-cycle vs parent-specific drift. S4-02 is diagnostic-only for parent decisions. |
| F1 residuals | Do scaled residuals decay, bound, or persist as a spike envelope? | log history | cumulative Fluent iteration | scaled continuity, momentum, `k`, `epsilon`, vf-phase-2 | one branch | that branch's parent residual export / transcript | raw | native residual export or S4-02 transcript table | residual export or transcript | Support A only if the late envelope shrinks. Bounded intermittency is not automatic parent failure, but continuity remaining `O(10^{-1})`–`O(1)` is. |
| F2 k/epsilon | Is the turbulence-residual envelope deteriorating or merely ugly? | log history | cumulative Fluent iteration | scaled `k`, `epsilon` | one branch | Stage-3 parent envelope; PR #7 bounded-vs-deteriorating distinction | raw | same as F1 | same as F1 | Weaken A if late spikes grow; do not reject A solely because `k`/`epsilon` stay jumpy. |
| F3 mass | Is mass imbalance low and stable in the 20–30k continuation window? | history | cumulative Fluent iteration | absolute and relative mass imbalance | one branch | Stage-3 100% checkpoint imbalance | raw plus later window mean/median/P95/slope from CSV | physical report histories | report definitions | Support A if late relative imbalance is small and non-oscillatory. A persistent 5–11% limit cycle weakens A. |
| F4 inventory | Does liquid holdup bound, with \(dM_l/dN \to 0\) in the 20–30k window? | history | cumulative Fluent iteration | total / Y010 / Y030 liquid mass and total liquid volume | one branch | 2026-08-20 volume-integral family, not the unreconciliation 2026-08-21 kg column | raw plus window slope from CSV | physical report histories | report definitions | Visual plateau is not stationarity. Use the 2026-08-20 family (~318 kg at F05 3,000) when comparing Stage-4 PNGs. |
| F5 routing | Is liquid routed to brine and vapour to steam without hiding carryover? | history | cumulative Fluent iteration | liquid/vapour → brine/steam fluxes; sign as configured Fluent units (outflow negative on Stage-4 PNGs) | one branch | Stage-3 phase routing | raw | physical report histories | report definitions | Sensible routing can coexist with oscillating liquid→brine. Do not quote PNG flux as kg/s until the sign convention is read back. |
| F6 brine | Do brine-entry pressure and outlet totals remain bounded? | history | cumulative Fluent iteration | brine-entry static/total pressure; brine/steam outlet totals | one branch | Stage-3 brine pressure margin | raw | physical report histories | report definitions | Bounded pressure does not prove mass closure. |
| F7 boundary fluxes | Do inlet/outlet mixture fluxes stay prescribed and consistent with F3/F5? | history | cumulative Fluent iteration | mixture/phase inlet and outlet fluxes | one branch | prescribed inlet ~198.5 kg/s (Reported, Stage-3) | raw | physical report histories | report definitions | Flat inlets with oscillating outlets are the mass-imbalance mechanism, not a separate mystery. |

## Execution boundary

The setup defines intent and required evidence only. Live execution status belongs in [Stage-4 results](results.md). Placement and absolute paths belong in [run-paths.yaml](run-paths.yaml). A branch is not parent-eligible until paired-file completeness, checksum/readback, and prescribed-window physical-history analysis are complete.

## Source

[Migrated Stage-4 setup authority](setup-source.md)

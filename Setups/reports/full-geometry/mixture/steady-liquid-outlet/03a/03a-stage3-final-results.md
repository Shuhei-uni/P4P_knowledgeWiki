# 03A Stage 3 — Final Results

> **Campaign:** 03A Stage 3 — Fluent-Recommended Convergence Sweep
> **Purpose:** canonical entry point for the independently produced Stage-3 result packages.
> **Interpretation status:** pending user direction. No branch is selected here.

## What was reconciled

The prior collision was editorial, not a contradiction in the underlying data: three agents analysed disjoint branch sets but two wrote to the same shared report path. The detailed evidence is now retained in separate scope-owned reports. This page is the only cross-scope summary and avoids combining unequal evidence types into one convergence plot or ranking.

| Result package | Branches | Evidence position | Detailed report |
|---|---|---|---|
| Native queue | F02, F04, F05, F06, F11 | checkpoint-backed endpoints; discovered local histories are present but not yet mapped to the queue lineage | [`native-queue final results`](./03a-stage3-native-queue-final-results.md) |
| Owned native-history branches | F03, F07, F09 | 30 native Report Files per branch; checkpoint-validated continuous histories | [`F03/F07/F09 detailed results`](./03a-stage3-f03-f07-f09-detailed-results.md) |
| Schedule D | F08, F10, F12 | F12 complete through 100%; F08 partial; F10 no valid solve checkpoint | [`F08/F10/F12 Schedule-D results`](./03a-stage3-schedule-d-final-results.md) |

F01 is not represented by the three delegated packages. Its pre-failure checkpoint remains in the shared [`2026-08-21 checkpoint table`](./03a-stage3-results-20260821-checkpoints.csv); this canonical report makes no new claim about F01.

## Cross-package evidence boundary

- Checkpoint endpoints and continuous histories are not interchangeable. The native-queue report therefore does not state late-window convergence metrics.
- F03/F07/F09 and F12 retain branch-first figures and their own late-window descriptions. Do not merge their history lines just because their branch identifiers share the Stage-3 campaign.
- F08's partial history and F10's unavailable solve evidence remain explicit. They are not omitted to make the campaign look more complete.
- Source and setup context are linked from the [`Stage-3 evidence packet`](./03a-stage3-results-20260821.md) and [`analysis/plotting plan`](./03a-stage3-results-analysis-and-plotting-plan.md).

## Reading order

1. Read the detailed report for the branch set relevant to the question.
2. Check that report's evidence-quality and provenance section before comparing values across packages.
3. Use the source checkpoint table only as a cross-check anchor where the detailed report says continuous history is available.

This separation resolves the write conflict without discarding any package or inventing a unified convergence conclusion.

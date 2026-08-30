# 03A tracer

This is the Project-layer tracer for the full-geometry Mixture `03A` campaign. It preserves the scientific handoff between the Fluent-recommended Stage-3 sweep and the Stage-4 long-continuation/model-form test without recreating the old progress or report tree.

## What this tracer must explain

- what Stage 3 tested and what evidence it produced;
- why Stage 4 followed from those findings;
- what Stage 4 was intended to test;
- which execution evidence is complete, partial, prepared-only, or still gated;
- what remains unresolved before a state can become a parent or support a stronger claim.

## Navigation

- [Stage-3 setup](stage-03/setup.md)
- [Stage-3 results](stage-03/results.md)
- [Stage-4 setup](stage-04/setup.md)
- [Stage-4 results](stage-04/results.md)
- [Stage-5 setup](stage-05/setup.md)
- [Stage-5 results](stage-05/results.md)
- [Phase 06 — Full Geometry with Brine Pool](../../phase-06-full-geometry-with-brine-pool/index.md)
- [Historical Stage-2 screening report](stage-02/source-screening-report.md)

## Source and artifact authorities

The original setup and report records remain available as frozen provenance:

- [Stage-3 setup authority](stage-03/setup-source.md)
- [Stage-3 checkpoint evidence](stage-03/source-results-20260821.md)
- [Stage-3 interpretation report](stage-03/source-final-results.md)
- [Stage-4 setup authority](stage-04/setup-source.md)
- [Stage-4 execution evidence](stage-04/source-native-queue-execution-2026-08-23.md)

The detailed Fluent artifacts, histories, plots, case/data files, and
machine-readable manifests remain in their original external or generated
locations. This tracer links to the migrated source reports and Project
evidence rather than copying binary run output.

## Current status

- Stage 3 is a completed diagnostic sweep. Its branches reached different horizons and several have missing, transport-blocked, or numerical-failure evidence; no branch is a validated or report-ready baseline.
- Stage 4 has completed diagnostic continuation evidence for S4-01 and S4-03, completed-budget but endpoint-incomplete evidence for S4-02, a completed F11/RNG-to-standard-`k-epsilon` sensitivity test (S4-04), and a completed F12 carrier-first/progressive-loading full-load test (S4-07). Its results did not establish a mass-closed, report-ready baseline.
- Stage 5 completed two discovery → focused-hypothesis cycles. Higher fixed brine-outlet pressure was worse for both tested practical `k-epsilon` closures, and Realizable `k-epsilon` did not improve on RNG at the preferred low pressure. RSM and SST did not produce practical full-screen comparisons at the tested full-geometry horizon.
- Phase 06 — Full Geometry with Brine Pool is the human-selected next
  top-level scientific phase. It investigates the reported real brine-pool
  level-control mechanism before treating the fixed-pressure Stage-5 result as
  a pure Mixture model-form failure. No Phase-06 case has yet been built or
  run.

## Cutover gate

**Status:** passed for this tracer on `2026-08-27` after source cross-check, structural review, and the fresh-agent comprehension test. The records below are the canonical current interpretation route for 03A; the linked setup/report files remain frozen provenance.

The Project tracer becomes the canonical current interpretation authority for 03A when all of the following are true:

1. both stages have a reviewed `setup.md` and `results.md` pair;
2. every carried conclusion is traceable to an existing setup/report or machine-evidence source;
3. actual, partial, failed/interrupted, missing, and usable evidence are distinguished explicitly;
4. the Project index points to this tracer as the shortest current route;
5. the fresh-agent test can explain Stage 3, the Stage-4 rationale, the Stage-4 experiment, and the unresolved gate from the Project records alone.

After this gate passes, new 03A scientific updates go to these Project records
only. The old 03A setup/report records are recoverable from Git history; the
current Project packet owns the scientific interpretation and PyAnsys owns
machine evidence. There is no dual-write period after cutover.

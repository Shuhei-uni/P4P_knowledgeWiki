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
- [Historical Stage-2 screening report](stage-02/source-screening-report.md)

## Source and artifact authorities

The original setup and report records remain available as frozen provenance:

- [Stage-3 setup authority](../../../Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage3-fluent-recommended-convergence-sweep.md)
- [Stage-3 checkpoint evidence](../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-results-20260821.md)
- [Stage-3 interpretation report](../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage3-final-results.md)
- [Stage-4 setup authority](../../../Setups/full-geometry/mixture/steady-liquid-outlet/03a-stage4-promising-state-development.md)
- [Stage-4 execution evidence](../../../Setups/reports/full-geometry/mixture/steady-liquid-outlet/03a/03a-stage4-native-queue-execution-2026-08-23.md)

The detailed Fluent artifacts, histories, plots, case/data files, and machine-readable manifests remain in their existing `Setups/reports/` and `PyAnsys/` locations. This tracer links to them through the source reports rather than copying them.

## Current status

- Stage 3 is a completed diagnostic sweep. Its branches reached different horizons and several have missing, transport-blocked, or numerical-failure evidence; no branch is a validated or report-ready baseline.
- Stage 4 has completed diagnostic continuation evidence for S4-01 and S4-03, completed-budget but endpoint-incomplete evidence for S4-02, and prepared-only evidence for S4-04. S4-05 and S4-06 remain gated on an exact F09 40% parent.
- The current 03A state is therefore still diagnostic and unresolved for scientific parent promotion.

## Cutover gate

**Status:** passed for this tracer on `2026-08-27` after source cross-check, structural review, and the fresh-agent comprehension test. The records below are the canonical current interpretation route for 03A; the linked setup/report files remain frozen provenance.

The Project tracer becomes the canonical current interpretation authority for 03A when all of the following are true:

1. both stages have a reviewed `setup.md` and `results.md` pair;
2. every carried conclusion is traceable to an existing setup/report or machine-evidence source;
3. actual, partial, failed/interrupted, missing, and usable evidence are distinguished explicitly;
4. the Project index points to this tracer as the shortest current route;
5. the fresh-agent test can explain Stage 3, the Stage-4 rationale, the Stage-4 experiment, and the unresolved gate from the Project records alone.

After this gate passes, new 03A scientific updates go to these Project records only. The old 03A setup/report records remain available as frozen historical/provenance sources; `Setups/` and `PyAnsys/` retain concrete lineage and machine artifacts, respectively. There is no dual-write period after cutover.

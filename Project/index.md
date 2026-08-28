# Project

This is the default entry point for the project's current scientific truth.
`Project/` owns the question being pursued, stable model assumptions, selected
experiments, evidence interpretation, and claim limits. Reusable CFD knowledge
belongs in `CFD_wiki/`; executable implementation and machine evidence belong
in `PyAnsys/`.

## What are we trying to answer now?

Can a controlled, sufficiently iterated reference case for the vertical BOC
separator be established before comparing more realistic two-phase inlet
regimes or making report-facing performance claims?

The immediate technical question is whether the extraction-first 08b-parity
full-geometry branch can separate setup-fidelity uncertainty from the intended
inlet change while producing interpretable residual, phase-flux, pressure, and
liquid-carryover evidence.

## Active/latest experiment

The current execution lane is the canonical full-geometry Mixture `03A`
Stage-4 promising-state development campaign. Its Project tracer is the
shortest route through the selected record:

- [03A tracer index](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/index.md)
- [Stage-4 setup contract](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/setup.md)
- [Stage-4 execution evidence](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-04/results.md)
- [Stage-3 results](experiments/phase-05-full-geometry-v2/full-geometry-03a-mixture-08b-parity-baseline/stage-03/results.md)

The earlier Project experiment records preserve the migrated setup and result
memory for the Purnanto, full-geometry, DPM, EWF, VOF, and reconstruction
families. Their historical status is part of the evidence; they are not
silently upgraded to current conclusions.

## What did the latest experiment show?

Stage 4 produced completed diagnostic continuation evidence for S4-01 and
S4-03, completed-budget but endpoint-incomplete evidence for S4-02, and
prepared-only evidence for S4-04. S4-05 and S4-06 remain gated because the
exact F09 40% parent was not proved accessible.

The available Stage-4 records do not establish physical convergence, a
report-ready baseline, or eligibility for a new parent branch. The executed
branches remain diagnostic until their binary identity, readback, and full
physical-history evidence are reviewed together.

## What remains unresolved?

- whether any 03A state has stable residuals, phase routing, pressure behaviour,
  and liquid-inventory behaviour over the required continuation window;
- whether the completed S4-01 and S4-03 continuations contain a stable,
  parent-eligible window;
- whether the rebuilt case is truly at parity with the audited Purnanto carrier
  settings apart from its declared project change;
- which external, analytical, or measured targets are appropriate for a
  validation claim;
- whether later DPM evidence is complete enough to support more than a bounded
  carryover diagnostic.

## What happens next?

Review the Stage-4 execution package together with the 03A tracer's remaining
readback and physical-history gaps. Promote only a state that passes those
checks, then record the next explicitly selected experiment with the
[setup/results contract](experiments/README.md). Keep each new experiment to a
concise delta from a verified parent and make its evidence and interpretation
explicit.

## Project map

- [experiment phase structure](experiments/README.md)
- [scope](scope.md)
- [stable model assumptions](model.md)
- [V&V and claim limits](vnv.md)
- [selected-experiment contract](experiments/README.md)
- [cross-experiment observations](observations/index.md)
- [technical project records](technical)

## Supporting source input

The original project source inputs and retired written project wiki were
removed from the current checkout at the user's request. Their exact history
is recoverable from Git; they are not active authorities.

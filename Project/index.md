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

- [03A tracer index](experiments/03a/index.md)
- [03A-Q01 setup — S4-01 50-iteration qualification](experiments/03a/q01-s4-01-50-iteration-qualification/setup.md)
- [03A-Q01 results — S4-01 50-iteration qualification](experiments/03a/q01-s4-01-50-iteration-qualification/results.md)
- [Stage-4 setup contract](experiments/03a/stage-04/setup.md)
- [Stage-4 execution evidence](experiments/03a/stage-04/results.md)
- [Stage-3 results](experiments/03a/stage-03/results.md)

The earlier Project experiment records preserve the migrated setup and result
memory for the Purnanto, full-geometry, DPM, EWF, VOF, and reconstruction
families. Their historical status is part of the evidence; they are not
silently upgraded to current conclusions.

## What did the latest experiment show?

Stage 4 produced completed diagnostic continuation evidence for S4-01 and
S4-03, completed-budget but endpoint-incomplete evidence for S4-02, and
prepared-only evidence for S4-04. The selected Q01 qualification then
completed exactly 50 native steady iterations from the verified `33,000`
parent endpoint, reaching native coordinate `33,050` with a paired endpoint,
hashes, scientific readback, residual/transcript evidence, and all 30
configured physical histories.

The short window still contains residual excursions and movement in mass
imbalance, liquid inventory, and routing; no paired native autosave checkpoint
was recovered. The available records do not establish physical convergence, a
report-ready baseline, or eligibility for a new parent branch. The Q01 packet
is diagnostic execution evidence, not a performance or validation claim.

## What remains unresolved?

- whether any 03A state has stable residuals, phase routing, pressure behaviour,
  and liquid-inventory behaviour over the required continuation window;
- whether the Q01 short-window movement can be qualified over a longer
  explicitly selected continuation with complete checkpoint evidence;
- whether the rebuilt case is truly at parity with the audited Purnanto carrier
  settings apart from its declared project change;
- which external, analytical, or measured targets are appropriate for a
  validation claim;
- whether later DPM evidence is complete enough to support more than a bounded
  carryover diagnostic.

## What happens next?

Review the Q01 packet together with the 03A tracer's remaining readback and
physical-history gaps. Promote only a state that passes those checks, then
record the next explicitly selected experiment with the
[setup/results contract](experiments/README.md). Keep each new experiment to a
concise delta from a verified parent and make its evidence and interpretation
explicit.

## Project map

- [scope](scope.md)
- [stable model assumptions](model.md)
- [V&V and claim limits](vnv.md)
- [selected-experiment contract](experiments/README.md)
- [cross-experiment observations](observations/index.md)
- [technical project records](technical/)

## Supporting source input

The two tracked files under `ResearchProject_wiki/raw/` are immutable source
inputs for the project-specific extraction. The retired written project wiki
and its progress/meeting navigation are recoverable from Git history; they are
not active authorities.

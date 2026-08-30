# Phase 06 — Full Geometry with Brine Pool

This is a new top-level Project experiment phase. It follows the `03A`
full-geometry fixed-pressure work and is not another Stage-5 pressure or
turbulence variation.

## Fixed phase-level question

> **Can a full-geometry CFD model reproduce a physically credible, controlled
> bottom brine-pool operating condition for the separator, rather than merely
> a response to a fixed brine-outlet pressure?**

This is the fixed question for Phase 6. It deliberately does not presume the
answer is Mixture, Eulerian, steady, transient, a particular valve law, or a
particular controller. Those are possible means of answering the question and
must be tested or justified by later stage-level questions.

For this phase, a controlled operating condition means: a meaningful pool-level
observable at the real measurement location; a specified level target/band;
brine-outlet behaviour physically connected to that target; phase-resolved
conservation consistent with the level behaviour; and numerically credible
equation and output histories.

## How later stages use this question

Each later stage must answer a narrower question that reduces uncertainty
about the fixed Phase-6 question. It may ask, for example, what the real
control mechanism is, how to measure pool level in the mesh, whether a
controlled quasi-steady outlet can reach the target, or whether a literal
time-dependent controller/model is required. A stage must not silently replace
the phase question with a convenient pressure, turbulence, or numerical sweep.

- [setup and phase contract](setup.md)
- [results and current evidence](results.md)
- [Stage 01 — level observable and outlet-response discovery](stage-01-level-observable-and-outlet-response/setup.md)
- [Stage 02 — level mapping and control-data gate](stage-02-level-mapping-and-control-data-gate/setup.md)
- [Stage 03 — simplified level-control surrogate](stage-03-simplified-level-control-surrogate/setup.md)
- [Stage 04 — stronger-feedback hypothesis](stage-04-stronger-feedback-hypothesis/setup.md)
- [Stage 05 — phase conclusion](stage-05-phase-conclusion/results.md)

## Relationship to the prior work

03A Stage 5 established that a fixed brine-outlet pressure plus the practical
steady `k-epsilon` variants does not produce a mass-closed, stationary-liquid
inventory state in the F11-derived model. That result is retained. This phase
asks the separate boundary-condition question exposed by that evidence: a real
separator controls liquid holdup through its brine outlet, whereas the tested
cases fixed an outlet pressure without representing that feedback mechanism.

# Phase 8 — Storyline reconstruction on the new mesh

Phase 8 recreates selected earlier setups on the existing Phase 7.2A 60k mesh to explain how the project reached its current model. Its primary deliverable is a reproducible run and comparison pipeline with common report definitions. Historical results guide case selection but are not quantitative baselines.

The [phase context](CONTEXT.md) records the four-family scientific envelope and remaining matrix choices. The [common run and report contract](report-contract.md) defines measurements and provenance required of every selected case. The [26.81 m/s F1/F2 baseline lineage audit](baseline-lineage-audit.md) compares the saved initialized cases against the historical records and identifies the remaining run gates. Families 1–4 have no absorber; an absorber comparison follows only after Phase 7.2A is finalized.

The source narrative is the [Phase 1](../phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md) through [Phase 7.2A](../phase-07-2a-wall-liquid-routing/interpretation.md) interpretation chain. Phase 8 results and interpretation belong here once executed.

## Family setups

- [F1 — mixed one-inlet carrier and one-way DPM](f1-one-inlet/setup.md)
- [F2 — split two-phase carrier and one-way DPM](f2-split-inlet/setup.md)
- [F3 — split inlet with two-way DPM fraction screen](f3-coupled-dpm/setup.md)
- [F4 — coupled DPM plus EWF](f4-coupled-dpm-ewf/setup.md)

F1/F2 have five speed cases each; F3/F4 each have a five-speed by five-DPM-fraction matrix, for 60 intended core cases. The `26.81 m/s` [F1](f1-one-inlet/results.md) and [F2](f2-split-inlet/results.md) **initialized base pairs** now exist on `student`; no Phase 8 carrier development or DPM run has been executed. Install and verify the common reports, develop the matched carrier pilots, then build the `5%` F3 pilot before expanding the matrix. F4 waits for finalized Phase 7.2A EWF settings. A five-speed, 5% one-way allocated bridge is optional.

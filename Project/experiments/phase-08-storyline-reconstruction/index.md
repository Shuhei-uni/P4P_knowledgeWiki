# Phase 8 — Storyline reconstruction on the new mesh

Phase 8 recreates selected earlier setups on the existing Phase 7.2A 60k mesh to explain how the project reached its current model. Its primary deliverable is a reproducible run and comparison pipeline with common report definitions. Historical results guide case selection but are not quantitative baselines.

The [phase context](CONTEXT.md) records the four-family scientific envelope and remaining matrix choices. The [common run and report contract](report-contract.md) defines measurements and provenance required of every selected case. The [26.81 m/s F1/F2 baseline lineage audit](baseline-lineage-audit.md) compares the saved initialized cases against the historical records and identifies the remaining run gates. Families 1–4 have no absorber; an absorber comparison follows only after Phase 7.2A is finalized.

The source narrative is the [Phase 1](../phase-01-purnanto-baseline-and-inlet-exploration/interpretation.md) through [Phase 7.2A](../phase-07-2a-wall-liquid-routing/interpretation.md) interpretation chain. Phase 8 results and interpretation belong here once executed.

## Family setups

- [F1 — mixed one-inlet carrier and one-way DPM](f1-one-inlet/setup.md)
- [F2 — split two-phase carrier and one-way DPM](f2-split-inlet/setup.md)
- [F3 — split inlet with two-way DPM fraction screen](f3-coupled-dpm/setup.md)
- [F4 — coupled DPM plus EWF](f4-coupled-dpm-ewf/setup.md)

F1/F2 have five speed cases each; F3/F4 each have a five-speed by five-DPM-fraction matrix, for 60 intended core cases. The original `26.81 m/s` [F1](f1-one-inlet/results.md) and [F2](f2-split-inlet/results.md) initialized base pairs remain available. The selected Purnanto-parity F1/F2 children were saved and reopened on 2026-09-29, but their SIMPLE carrier pilots failed the balance/inventory gate. Separately named matched Coupled recoveries reached the operational carrier gate at N=10,000 for both 26.81 and 20.11 m/s; their seven-bin one-way diagnostics retain large unresolved track fractions. The [5% F3 pilot](f3-coupled-dpm/results.md) has a verified two-way DPM child, but its N=15,000 update-100 continuation remains outside the inventory and continuity gates. The [F4 E2.7-based exploratory build and N=11,000 pilot](f4-coupled-dpm-ewf/results.md) likewise remain unqualified; the EWF matrix basis is provisional because Phase 7.2A has not closed. The 23.46 m/s F1/F2 Coupled carrier sweep is in progress. A five-speed, 5% one-way allocated bridge is optional.

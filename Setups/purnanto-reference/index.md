# Purnanto / Reference Programme

This is the canonical setup-definition home for the Purnanto/reference geometry lineage and its DPM/EWF development branches.

## 09c family

The complete `09c` lineage now has canonical setup records in this programme:

- [09c — Two-Way DPM Coupling](09c-dpm-ewf-wall-film-reentrainment.md)
- [09cV2 — Skoog Partition and Injection Control](09cV2-skoog-partition-injection-control.md)
- [09cV3 — Fine-Mist 5% DPM PSD Rerun](09cV3-fine-mist-5pct-psd-rerun.md)

Numerical evidence:

- [09c results](../reports/purnanto-reference/09c/results.md)
- [09cV2 results](../reports/purnanto-reference/09cV2/results.md)
- [09cV3 results](../reports/purnanto-reference/09cV3/results.md)

The original full-text `09c` and `09cV2` records are preserved under `Setups/past/compatibility/` because their relative links depended on the old directory depth. Their former `past/reported/` paths are now redirect stubs. `09cV3` was moved directly from `active/` because its relative-link depth is compatible with this programme.

## Legacy numbered views

- [Archived numbered setups](../past/archived/index.md)
- [Reported numbered compatibility view](../past/reported/index.md)
- [Historical order dictionary](../order-dictionary.md)

## Archived former future plans

The previously planned `10`, `11`, and `12` branches are no longer in the future queue:

- [10 archived plan](../archived/10-wall-film-reentrainment-and-dpm-interaction-plan.md)
- [11 archived plan](../archived/11-combined-wallfilm-dpm-plan.md)
- [12 archived plan](../archived/12-carrier-mesh-convergence-plan.md)

## Classification rule

Do not classify geometry from the setup number alone. Some historical notes use phrases such as “full geometry” while still belonging to the older Purnanto/reference lineage. Require explicit mesh/case provenance before promoting a setup into the current `Full-geomV2` programme.

New `Full-geomV2` campaigns belong under [`Setups/full-geometry/`](../full-geometry/index.md), not here.

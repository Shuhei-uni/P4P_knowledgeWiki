# Setup 09cV2 — Skoog Partition and Injection-Control Branch

## Canonical metadata

| Field | Value |
|---|---|
| Programme | `purnanto-reference` |
| Legacy setup ID | `09cV2` |
| Lifecycle | `reported` |
| Role | Skoog-aligned allocation and injection-control experiment |
| Parent | [09c — two-way DPM coupling](09c-dpm-ewf-wall-film-reentrainment.md) |
| Active child | [09cV3 — fine-mist 5% DPM PSD rerun](09cV3-fine-mist-5pct-psd-rerun.md) |
| Other historical child | [010V2 — EWF deposition/film inventory](../past/reported/010V2-ewf-deposition-film-inventory.md) |
| Controlled changes | liquid/DPM mass partition, DPM material identity, scaled DPM loading, and source-balance checks |
| Geometry basis | inherited Purnanto/purnantov2 `08b`-family geometry/mesh lineage |
| Detailed frozen source | [09cV2 compatibility snapshot](../past/compatibility/09cV2-skoog-partition-injection-control.md) |
| Numerical evidence | [09cV2 results](../reports/purnanto-reference/09cV2/results.md) |

## Intent

Create a mass-consistent Skoog-style inlet partition before adding Eulerian Wall Film physics, with DPM representing a declared fraction of total liquid feed rather than an additional copy of the full Purnanto liquid flow.

The existing Mixture carrier model is retained so the first comparison changes injection bookkeeping without simultaneously changing the global multiphase formulation.

The detailed compatibility snapshot remains the authority for exact partition values, injection controls, readback requirements, case artifacts, and diagnostic limitations. This canonical record places the branch explicitly inside the Purnanto/reference programme.

## Descendant

`09cV3` keeps the partitioned 5% DPM concept but replaces the historical six-bin droplet population with the project fine-mist PSD. Its canonical record is stored alongside this file.

# Setups

> **LEGACY FOR NEW WORK**
> New selected experiments belong in [`Project/experiments/`](../Project/experiments/).
> Do not create new mirrored setup/report records here.
> Historical files remain available for provenance.

`Setups/` stores retained concrete Fluent experiment definitions, setup-linked evidence, and historical lineage. Existing setup definitions and result reports remain intentionally separated for compatibility; new selected experiments keep `setup.md` and `results.md` together under `Project/experiments/`.

The retained programme navigation is geometry-first because the `Full-geomV2` records are a different experimental generation from the older Purnanto/reference work.

## Primary programme entry points

- [Full-geometry setup definitions](full-geometry/index.md)
- [Purnanto/reference programme](purnanto-reference/index.md)
- [Setup reports](reports/index.md)
- [Archived setup plans](archived/index.md)

## Retained full-geometry separation rule

For retained production-work records, the existing mirror separates setup and result ownership:

```text
Setups/full-geometry/<physics>/<campaign>/
Setups/reports/full-geometry/<physics>/<campaign>/
```

Use the first path for what was intended to be built/run and the second for what actually happened. Do not start a new selected experiment in either path.

## Retained layout reference (do not use for new work)

The campaign directory is the historical unit for existing Setups work. Use the smallest shape that fits a retained campaign:

```text
Setups/full-geometry/<physics>/<campaign>/
├── index.md
├── setup.md or setup-<id>-<slug>.md
└── stage-<nn>-<slug>.md

Setups/reports/full-geometry/<physics>/<campaign>/
├── index.md
└── <experiment-id>/
    ├── index.md
    ├── result reports
    ├── plots/                        # only for local figures
    └── evidence/                     # only for companion artifacts
```

Use [`campaign-index-template.md`](templates/campaign-index-template.md) when repairing a retained campaign, and keep one canonical copy of each record. Each setup/experiment gets one report folder; plots belong inside that folder, never in a shared campaign-level `plots/` directory. Lifecycle is metadata, not a new status directory. Retained paths use lowercase kebab-case and stable campaign-scoped IDs; do not start another global numbered sequence.

Existing exceptions are retained for link compatibility. Do not move or rename them solely for style. If a record is intentionally migrated, leave a redirect stub or an explicitly labelled compatibility snapshot at the old path and link it to the canonical record.

Do not keep operating-system metadata such as `.DS_Store` in this tree.

## Compatibility paths

- [active](active/index.md) now contains redirect stubs only for records that were moved to programme-owned locations;
- [future](future/index.md) contains redirect stubs only — all previously planned setups there were archived on 2026-08-17;
- [archived](archived/index.md) retains setup-only plans that are no longer in a working queue;
- [past](past/) retains the historical numbered setup corpus;
- [compatibility snapshots](compatibility-snapshots/index.md) preserve detailed pre-migration records whose relative links depended on their old directory depth;
- [templates](templates/) contains the setup, result, technical readback, and campaign-index templates.

Do not create new setup definitions or result reports anywhere in `Setups/` for a selected experiment. Use the [Project experiment contract](../Project/experiments/README.md), where the setup and result records are co-located.

## Historical ordering

- [Setup order dictionary](order-dictionary.md) remains the historical numbered-lineage reference. It is not the naming authority for new full-geometry campaigns.

## Geometry identity rule

Do not infer geometry from a setup number or a phrase such as “full geometry.” Require explicit mesh/case provenance. `Full-geomV2-231kcells.msh.h5` is an explicit full-geometry production-mesh identity used by the 02e steady Mixture work.

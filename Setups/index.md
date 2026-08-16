# Setups

`Setups/` stores concrete Fluent experiment definitions and their setup-linked evidence. The primary navigation is now **geometry-first**, because the current `Full-geomV2` programme is a different experimental generation from the older numbered Purnanto/reference work.

## Primary programmes

- [Full geometry](full-geometry/index.md) — canonical home for `Full-geomV2` and its descendants. New production work belongs here.
- [Purnanto/reference programme](purnanto-reference/index.md) — navigation layer for the historical numbered/reference corpus and its DPM/EWF development branches.

## Shared resources

- [Setup order dictionary](order-dictionary.md) — historical numbered-lineage reference. Continue using it when editing legacy numbered records; it is **not** the naming authority for new full-geometry campaigns.
- [Templates](templates/) — flexible setup/result templates shared by both programmes.

## Legacy compatibility views

The following directories are retained because many existing Markdown files cross-link to them:

- [active](active/index.md)
- [future](future/index.md)
- [past](past/)
- [reports](reports/index.md)

These paths are now a **compatibility layer for the numbered corpus**. Do not create new `Full-geomV2` campaigns there. Current full-geometry records that still physically reside in those paths are linked from the canonical full-geometry campaign pages until a future link-safe physical migration is justified.

## New full-geometry filing rule

Use:

```text
Setups/full-geometry/
└── <physics-family>/
    └── <scientific-campaign>/
        ├── index.md
        ├── setup.md
        ├── results.md            # when one report is enough
        └── <stage-or-study>/      # when the campaign has multiple stages
            ├── plan.md
            └── results.md
```

The folder name should communicate the scientific question. Do not make a new top-level numbered folder simply because the next integer is available.

Stable IDs may still exist in metadata and Fluent artifact names, for example `FG-MIX-T01`, but the ID is secondary to the geometry/physics/campaign path.

## Setup/report contract

A setup record should make clear:

- geometry and mesh identity;
- scientific question and investigation mode;
- reference/predecessor and controlled changes;
- frozen comparison context;
- exact Fluent build/readback requirements;
- pre-run evidence that must be instrumented;
- interpretation ownership, defaulting to user-led.

Results should normally live with the scientific campaign and remain an evidence packet until interpretation is explicitly supplied or delegated.

## Geometry-lineage rule

Do not infer geometry from a setup number or a title such as “full geometry.” A historical file can describe a full-domain vessel while still using the older `purnanto` geometry label. Geometry classification must come from explicit case/mesh provenance.

For the current programme, `Full-geomV2-231kcells.msh.h5` is an explicit full-geometry production-mesh identity used by the active Mixture liquid-outlet work.

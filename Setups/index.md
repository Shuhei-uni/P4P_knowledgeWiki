# Setups

`Setups/` stores concrete Fluent experiment definitions and their setup-linked evidence, but **setup definitions and result reports are intentionally kept in separate trees**.

The primary navigation is geometry-first because the current `Full-geomV2` programme is a different experimental generation from the older numbered Purnanto/reference work.

## Primary programmes

- [Full-geometry setup definitions](full-geometry/index.md) — canonical home for `Full-geomV2` setup plans, build contracts, stage plans, and controlled experiment definitions.
- [Setup reports](reports/index.md) — canonical home for numerical result reports and evidence packets.
- [Purnanto/reference programme](purnanto-reference/index.md) — navigation layer for the historical numbered/reference setup corpus and its DPM/EWF development branches.

## Separation rule

For new full-geometry work, the setup and report trees mirror one another:

```text
Setups/full-geometry/<physics>/<campaign>/
Setups/reports/full-geometry/<physics>/<campaign>/
```

Use the first path for **what is intended to be built/run** and the second for **what actually happened**.

Do not place `results.md`, execution-result reports, post-analysis reports, or interpretation reports inside `Setups/full-geometry/...`.

Do not place setup plans, stage plans, or Fluent build contracts inside `Setups/reports/...`.

Example:

```text
Setups/
├── full-geometry/
│   └── mixture/
│       └── transient-liquid-outlet/
│           ├── index.md
│           ├── setup.md
│           ├── stage-03-initialization-comparison.md
│           └── stage-06-six-case-screen.md
└── reports/
    └── full-geometry/
        └── mixture/
            └── transient-liquid-outlet/
                ├── index.md
                ├── stage-03-initialization-comparison-results.md
                └── stage-06-six-case-screen-results.md
```

## Shared resources

- [Setup order dictionary](order-dictionary.md) — historical numbered-lineage reference. Continue using it when editing legacy numbered records; it is **not** the naming authority for new full-geometry campaigns.
- [Templates](templates/) — flexible setup/result templates shared by both programmes.

## Legacy compatibility views

The following directories are retained because many existing Markdown files cross-link to them:

- [active](active/index.md)
- [future](future/index.md)
- [past](past/)
- numbered report folders directly under [reports](reports/index.md)

These paths are a compatibility layer for the numbered corpus. Do not create new `Full-geomV2` campaigns there.

## Geometry-lineage rule

Do not infer geometry from a setup number or a title such as “full geometry.” A historical file can describe a full-domain vessel while still using the older `purnanto` geometry label. Geometry classification must come from explicit case/mesh provenance.

For the current programme, `Full-geomV2-231kcells.msh.h5` is an explicit full-geometry production-mesh identity used by the active Mixture liquid-outlet work.

# Full-Geometry Programme

This is the canonical setup area for the current production separator geometry (`Full-geomV2` and verified descendants).

The purpose of this split is to prevent the new production-geometry work from being treated as one more numbered child of the older Purnanto/reference development sequence.

## Current programme map

```text
Full geometry
├── Mixture
│   ├── steady liquid-outlet characterization
│   └── transient liquid-outlet characterization   ← next major campaign
└── VOF
    └── transient liquid-outlet model-form branch
```

- [Mixture](mixture/index.md)
- [VOF](vof/index.md)

## Authoring rule

New work should be organized as:

```text
geometry → physics family → scientific campaign → setup/evidence
```

rather than:

```text
next number → next number → global reports folder
```

A campaign may use a stable machine/reference ID such as `FG-MIX-T01`, but the descriptive campaign path is the primary human-facing identity.

## Relationship to the numbered corpus

The current steady Mixture work was originally recorded as numbered Setup `02c` and `02e`. Those source files and their report folders remain at their historical paths for link stability, but their **scientific ownership is now this full-geometry programme**.

The older numbered corpus remains accessible through [Purnanto/reference programme](../purnanto-reference/index.md). A legacy setup can be a methodological predecessor without being a geometry parent. Do not claim case/mesh inheritance unless the artifact lineage is explicitly verified.

## Geometry identity gate

Before adding a campaign here, record the exact geometry/mesh evidence. A name containing “full geometry” is not sufficient. At minimum capture one of:

- exact mesh filename and readback;
- exact parent `.cas.h5` with verified mesh identity;
- explicit geometry revision/provenance record.

If that evidence is missing, keep the setup in the legacy/reference programme until the geometry is resolved.

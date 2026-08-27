# Full-Geometry Setup Programme

> **RETAINED SETUP SOURCE — NOT FOR NEW SELECTED EXPERIMENTS**
> New selected experiments belong in [`Project/experiments/`](../../Project/experiments/), with `setup.md` and `results.md` co-located. The records below remain readable as setup/provenance sources for existing Full-geomV2 work.

This is the retained **setup-definition tree** for the production separator geometry (`Full-geomV2` and verified descendants).

Numerical result reports do **not** live in this tree. The mirrored report tree is [Setups/reports/full-geometry](../reports/full-geometry/index.md).

## Retained programme map

```text
Full-geometry setups
├── Mixture
│   ├── steady liquid-outlet characterization
│   │   ├── 02c unprimed pressure sensitivity
│   │   └── 02e Y010 outlet-family characterization
│   └── transient liquid-outlet characterization
└── VOF
    └── transient liquid-outlet branch (02d plan archived)
```

- [Mixture setup campaigns](mixture/index.md)
- [VOF setup campaigns](vof/index.md)
- [Full-geometry result reports](../reports/full-geometry/index.md)

## Retained layout rule

Existing setup records are organized as:

```text
geometry → physics family → scientific campaign → setup/stage plans
```

The matching numerical evidence is organized separately as:

```text
reports → geometry → physics family → scientific campaign → result reports
```

A campaign may use a stable machine/reference ID such as `FG-MIX-T01`, but the descriptive campaign path is the primary human-facing identity.

## Relationship to the numbered corpus

The steady Mixture records originally known as `02c` and `02e` now live canonically under [Mixture steady liquid outlet](mixture/steady-liquid-outlet/index.md). Their pre-migration detailed records are retained as compatibility snapshots, while the old `Setups/active/02c` and `02e` paths are redirect stubs only.

The older numbered corpus remains accessible through [Purnanto/reference programme](../purnanto-reference/index.md). A legacy setup can be a methodological predecessor without being a geometry parent. Do not claim case/mesh inheritance unless artifact lineage is explicitly verified.

## Geometry identity gate for retained records

When reviewing or explicitly repairing a retained campaign, record the exact geometry/mesh evidence. A name containing “full geometry” is not sufficient. At minimum capture an exact mesh filename/readback, an exact parent `.cas.h5` with verified mesh identity, or an explicit geometry revision/provenance record.

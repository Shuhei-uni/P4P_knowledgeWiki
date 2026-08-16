# Full-Geometry Result Reports

This is the canonical report tree for completed simulations on the current `Full-geomV2` programme.

The corresponding setup-definition tree is [Setups/full-geometry](../../full-geometry/index.md).

## Report map

```text
reports/full-geometry/
├── mixture/
│   ├── steady-liquid-outlet/
│   └── transient-liquid-outlet/
└── vof/
    └── transient-liquid-outlet/
```

- [Mixture reports](mixture/index.md)
- [VOF reports](vof/index.md)

## Mirroring rule

For every full-geometry campaign:

```text
Setups/full-geometry/<physics>/<campaign>/
Setups/reports/full-geometry/<physics>/<campaign>/
```

The setup side defines what should be run. The report side records what actually happened.

Do not place setup plans in this report tree.

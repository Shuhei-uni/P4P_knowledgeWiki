# Full Geometry — Mixture Transient Liquid-Outlet Campaign

**Status:** next major full-geometry campaign / active planning

**Investigation mode:** exploratory sensitivity screen with numerical-method qualification

**Interpretation owner:** user-led

This is the first campaign authored natively under the geometry-first setup structure.

- [Setup and transient protocol](setup.md)
- [Steady predecessor campaign](../steady-liquid-outlet/index.md)

## Campaign question

Can the promising liquid-retaining regimes observed during the steady Mixture screens become bounded, interpretable **unsteady** solutions when integrated with a qualified transient method?

The question is not merely whether Fluent avoids a floating-point error. Evidence must distinguish physical storage/oscillation/drainage from numerical survival.

## Filing rule for results

Do not create `Setups/reports/<new-number>/` for this campaign. Add evidence here, for example:

```text
transient-liquid-outlet/
├── index.md
├── setup.md
├── numerical-qualification/
│   ├── plan.md
│   └── results.md
└── aggressive-retention-screen/
    ├── plan.md
    └── results.md
```
